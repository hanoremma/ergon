"""
job-scraper-mcp — MCP Server for Job Posting Extraction
Tools:
  - extract_job_from_url: Scrape and extract structured job data from a URL
  - extract_job_from_pdf: Extract structured job data from PDF bytes (base64)
  - extract_job_from_image: OCR + extract structured job data from image (base64)
"""
import os
import re
import json
import base64
import httpx
from typing import Optional
from pydantic import BaseModel
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv(override=True)

mcp = FastMCP(
    name="job-scraper-mcp",
    instructions="MCP server untuk ekstraksi data lowongan kerja dari URL, PDF, atau gambar.",
)

OPENAI_COMPAT_BASE_URL = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "").rstrip("/")
OPENAI_COMPAT_API_KEY  = os.getenv("OPENAI_COMPATIBLE_API_KEY", "")
OPENAI_COMPAT_MODEL    = os.getenv("OPENAI_COMPAT_JOB_MODEL", "gemini/gemini-3.5-flash-lite")


# ─── Schema ─────────────────────────────────────────────────────────────────────

class JobData(BaseModel):
    company: str = ""
    position: str = ""
    seniority: str = ""
    requirements_hard_skill: list[str] = []
    requirements_soft_skill: list[str] = []
    responsibilities: list[str] = []
    location: str = ""
    salary_range: str = ""
    applicants_count: str = ""
    quota: str = ""
    deadline: str = ""
    raw_text: str = ""
    extraction_notes: list[str] = []


# ─── LLM Helper (OpenAI-compatible endpoint) ────────────────────────────────────

def _parse_openai_response(raw: str) -> str:
    """Parse both non-streaming JSON and SSE streaming responses, including thinking models."""
    raw = raw.strip()
    if not raw:
        return ""
    # Non-streaming: starts with { (possibly after leading whitespace)
    stripped = raw.lstrip()
    if stripped.startswith("{"):
        try:
            import json as _json
            decoder = _json.JSONDecoder()
            data, _ = decoder.raw_decode(stripped)
            msg = data["choices"][0]["message"]
            # Some thinking models put answer in content; reasoning is separate
            return msg.get("content", "") or ""
        except Exception:
            pass
    # SSE streaming: collect all delta content chunks
    content = ""
    for line in raw.splitlines():
        if line.startswith("data:"):
            chunk = line[5:].strip()
            if chunk == "[DONE]":
                break
            try:
                import json as _json
                obj = _json.loads(chunk)
                delta = obj.get("choices", [{}])[0].get("delta", {})
                content += delta.get("content", "") or ""
            except Exception:
                pass
    return content


async def call_granite(prompt: str, max_tokens: int = 1024) -> str:
    """Call LLM via OpenAI-compatible endpoint for structured text extraction."""
    if not OPENAI_COMPAT_BASE_URL or not OPENAI_COMPAT_API_KEY:
        return json.dumps({"error": "LLM not configured"})

    url = f"{OPENAI_COMPAT_BASE_URL}/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_COMPAT_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": OPENAI_COMPAT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.1,
        "stream": False,
    }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, headers=headers, json=body)
            resp.raise_for_status()
            return _parse_openai_response(resp.text)
    except Exception as e:
        return json.dumps({"error": str(e)})


def build_extraction_prompt(raw_text: str) -> str:
    return f"""Kamu adalah AI ekstractor lowongan kerja. Ekstrak informasi berikut dari teks lowongan dan kembalikan sebagai JSON valid.

Teks lowongan:
```
{raw_text[:3000]}
```

Kembalikan JSON dengan format PERSIS ini (isi string kosong "" jika tidak ditemukan):
{{
  "company": "nama perusahaan",
  "position": "nama posisi/jabatan",
  "seniority": "junior/mid/senior/lead/manager",
  "requirements_hard_skill": ["skill1", "skill2"],
  "requirements_soft_skill": ["skill1", "skill2"],
  "responsibilities": ["tanggung jawab 1", "tanggung jawab 2"],
  "location": "lokasi kerja",
  "salary_range": "rentang gaji atau kosong",
  "applicants_count": "jumlah pelamar atau kosong",
  "quota": "kuota lowongan atau kosong",
  "deadline": "deadline atau kosong"
}}

JSON:
```"""


# ─── Tool: Extract from URL ──────────────────────────────────────────────────────

@mcp.tool()
async def extract_job_from_url(url: str) -> dict:
    """
    Ekstrak data lowongan kerja terstruktur dari sebuah URL.

    Args:
        url: URL halaman lowongan kerja (job board, LinkedIn, Glints, dll.)

    Returns:
        JobData terstruktur dengan semua field yang berhasil diekstrak
    """
    notes = []
    raw_text = ""

    # ── Jobstreet: try their GraphQL/API endpoint first ──────────────────────────
    if "jobstreet.co.id" in url or "jobstreet.com" in url:
        import re as _re
        job_id_match = _re.search(r"-(\d{6,12})(?:[/?#]|$)", url)
        if job_id_match:
            job_id = job_id_match.group(1)
            api_url = f"https://xapi.supercharge-srp.co/job-search/graphql?country=id&isSmartSearch=true"
            gql_query = {
                "query": "query GetJobDetail($jobId: String!) { jobDetail(jobId: $jobId, locale: \"id\") { id title companyDetail { name } jobDetail { jobDescription jobRequirement } } }",
                "variables": {"jobId": job_id}
            }
            try:
                async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
                    gql_resp = await client.post(api_url,
                        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
                        json=gql_query)
                    if gql_resp.status_code == 200:
                        gql_data = gql_resp.json()
                        jd = gql_data.get("data", {}).get("jobDetail", {})
                        if jd and jd.get("title"):
                            detail = jd.get("jobDetail", {})
                            raw_text = (
                                f"Position: {jd.get('title', '')}\n"
                                f"Company: {jd.get('companyDetail', {}).get('name', '')}\n"
                                f"Description:\n{detail.get('jobDescription', '')}\n"
                                f"Requirements:\n{detail.get('jobRequirement', '')}"
                            )
                            notes.append(f"Scraped via Jobstreet GraphQL API (job_id={job_id})")
            except Exception as gql_err:
                notes.append(f"Jobstreet API failed: {str(gql_err)}")

    try:
        if not raw_text:
            async with httpx.AsyncClient(
                timeout=20,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/124.0.0.0 Safari/537.36"
                    ),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Referer": "https://www.google.com/",
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                },
                follow_redirects=True,
            ) as client:
                resp = await client.get(url)
                resp.raise_for_status()
                html = resp.text

            # LinkedIn redirect ke halaman search/login jika URL tidak langsung ke job
            if "linkedin.com" in url and "/jobs/view/" not in str(resp.url):
                notes.append(f"LinkedIn redirect ke {resp.url} — mungkin perlu login.")

            from bs4 import BeautifulSoup as _BS
            soup = _BS(html, "lxml")
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
            raw_text = soup.get_text(separator="\n", strip=True)
            raw_text = re.sub(r"\n{3,}", "\n\n", raw_text)

    except Exception as e:
        notes.append(f"Gagal mengambil URL: {str(e)}")
        if not raw_text:
            return JobData(extraction_notes=notes, raw_text="").model_dump()

    # Parse with LLM
    try:
        prompt = build_extraction_prompt(raw_text)
        llm_output = await call_granite(prompt)
        # Strip markdown code fences if present (```json ... ``` or ``` ... ```)
        llm_clean = re.sub(r"```(?:json)?\s*", "", llm_output).strip()
        json_match = re.search(r"\{.*\}", llm_clean, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            parsed["raw_text"] = raw_text[:500]
            parsed["extraction_notes"] = notes
            return parsed
    except Exception as e:
        notes.append(f"LLM parsing gagal, menggunakan regex fallback: {str(e)}")

    # Regex fallback
    job_data = JobData(raw_text=raw_text[:500], extraction_notes=notes)
    return job_data.model_dump()


# ─── Tool: Extract from PDF ──────────────────────────────────────────────────────

@mcp.tool()
async def extract_job_from_pdf(pdf_base64: str, filename: str = "job.pdf") -> dict:
    """
    Ekstrak data lowongan kerja dari file PDF (diencoding sebagai base64).

    Args:
        pdf_base64: Konten PDF dalam base64 encoding
        filename: Nama file original untuk referensi

    Returns:
        JobData terstruktur
    """
    import fitz  # PyMuPDF
    notes = []
    raw_text = ""

    try:
        pdf_bytes = base64.b64decode(pdf_base64)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            raw_text += page.get_text()
        doc.close()
    except Exception as e:
        notes.append(f"Gagal membaca PDF: {str(e)}")
        return JobData(extraction_notes=notes).model_dump()

    # Parse with Granite
    try:
        prompt = build_extraction_prompt(raw_text)
        llm_output = await call_granite(prompt)
        json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            parsed["raw_text"] = raw_text[:500]
            parsed["extraction_notes"] = notes
            return parsed
    except Exception as e:
        notes.append(f"LLM parsing gagal: {str(e)}")

    return JobData(raw_text=raw_text[:500], extraction_notes=notes).model_dump()


# ─── Tool: Extract from Image (OCR) ─────────────────────────────────────────────

@mcp.tool()
async def extract_job_from_image(image_base64: str, filename: str = "job.png") -> dict:
    """
    Ekstrak data lowongan kerja dari gambar/screenshot via OCR.

    Args:
        image_base64: Konten gambar dalam base64 encoding (PNG/JPG/WEBP)
        filename: Nama file original

    Returns:
        JobData terstruktur
    """
    import pytesseract
    from PIL import Image
    from io import BytesIO
    notes = []
    raw_text = ""

    try:
        img_bytes = base64.b64decode(image_base64)
        img = Image.open(BytesIO(img_bytes))
        raw_text = pytesseract.image_to_string(img, lang="ind+eng")
    except Exception as e:
        notes.append(f"OCR gagal: {str(e)}. Coba gunakan gambar resolusi lebih tinggi.")
        return JobData(extraction_notes=notes).model_dump()

    if not raw_text.strip():
        notes.append("OCR tidak menemukan teks. Gambar mungkin terlalu blur atau bukan dokumen teks.")
        return JobData(extraction_notes=notes).model_dump()

    try:
        prompt = build_extraction_prompt(raw_text)
        llm_output = await call_granite(prompt)
        json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())
            parsed["raw_text"] = raw_text[:500]
            parsed["extraction_notes"] = notes
            return parsed
    except Exception as e:
        notes.append(f"LLM parsing gagal: {str(e)}")

    return JobData(raw_text=raw_text[:500], extraction_notes=notes).model_dump()


if __name__ == "__main__":
    port = int(os.getenv("JOB_SCRAPER_MCP_PORT", "8001"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")

