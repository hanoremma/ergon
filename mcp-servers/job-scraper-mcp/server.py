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
import asyncio
from pathlib import Path
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
JINA_API_KEY = os.getenv("JINA_API_KEY", "").strip()

# Hosts that often require a real browser render before text/markdown tiers help.
CSR_HEAVY_JOB_HOSTS = (
    "linkedin.com",
    "glints.com",
    "glints.id",
    "indeed.com",
    "jobsdb.com",
    "jobstreet.com",
    "jobstreet.co.id",
    "karir.com",
)


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


async def _run_cheerio_helper(mode: str, value: str) -> str:
    """Run the Node.js Cheerio helper to extract readable job-page content."""
    helper_path = Path(__file__).with_name("scraper.cjs")
    command = ["node", str(helper_path), mode]
    payload = value.encode("utf-8") if mode == "html" else None
    if mode == "render":
        command.append(value)
    process = await asyncio.create_subprocess_exec(
        *command,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            process.communicate(payload),
            timeout=45 if mode == "render" else 10,
        )
    except asyncio.TimeoutError:
        process.kill()
        await process.wait()
        raise RuntimeError(f"Cheerio helper timed out in {mode} mode")
    if process.returncode != 0:
        error = stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(error or f"Cheerio helper exited with status {process.returncode}")
    try:
        result = json.loads(stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Cheerio helper returned invalid JSON") from exc
    if not isinstance(result, dict) or not isinstance(result.get("text"), str):
        raise RuntimeError("Cheerio helper returned an invalid response")
    return result["text"]


def _host_matches(host: str, domains: tuple[str, ...]) -> bool:
    normalized = (host or "").lower()
    return any(
        normalized == domain or normalized.endswith(f".{domain}")
        for domain in domains
    )


def _usable_job_text(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) < 200:
        return False
    blocked_page_markers = (
        "verify you are human",
        "checking your browser",
        "access denied",
        "enable javascript and cookies",
        "enable javascript and cookies to continue",
        "sign in to view",
        "just a moment",
        "attention required",
        "are you a robot",
        "are you a human",
        "please complete the security check",
        "pardon our interruption",
        "cf-browser-verification",
        "cf_chl_opt",
        "unusual traffic from your computer network",
        "access to this page has been denied",
    )
    lowered = normalized.lower()
    return not any(marker in lowered for marker in blocked_page_markers)


_PARTIAL_FIELD_PATTERNS = {
    "position": re.compile(
        r"(?im)^\s*(?:position|title|job title|role|posisi|jabatan|lowongan)\s*[:\-–]\s*(.+)$"
    ),
    "company": re.compile(
        r"(?im)^\s*(?:company|perusahaan|employer|nama perusahaan|company name)\s*[:\-–]\s*(.+)$"
    ),
    "location": re.compile(
        r"(?im)^\s*(?:location|lokasi|workplace|work location|lokasi kerja)\s*[:\-–]\s*(.+)$"
    ),
    "salary_range": re.compile(
        r"(?im)^\s*(?:salary|gaji|compensation|upah|rentang gaji)\s*[:\-–]\s*(.+)$"
    ),
}


def _partial_job_data_from_text(raw_text: str, notes: list[str]) -> JobData:
    """Best-effort labeled-field extraction when LLM parsing is unavailable."""
    local_notes = list(notes)
    data = JobData(raw_text=raw_text[:500], extraction_notes=local_notes)
    matched = False
    for field, pattern in _PARTIAL_FIELD_PATTERNS.items():
        match = pattern.search(raw_text)
        if not match:
            continue
        value = match.group(1).strip().strip("\"'")
        if value:
            setattr(data, field, value[:200])
            matched = True
    if matched:
        local_notes.append(
            "LLM parsing gagal; memakai regex parsial untuk field lowongan berlabel."
        )
    else:
        local_notes.append(
            "LLM parsing gagal dan regex parsial tidak menemukan field berlabel."
        )
    data.extraction_notes = local_notes
    return data


async def _fetch_jina_reader_text(url: str) -> str:
    headers = {
        "Accept": "text/plain",
        "X-Return-Format": "markdown",
    }
    if JINA_API_KEY:
        headers["Authorization"] = f"Bearer {JINA_API_KEY}"
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        response = await client.get(
            f"https://r.jina.ai/{url}",
            headers=headers,
        )
        response.raise_for_status()
        return response.text.strip()


async def _fetch_jobstreet_job_text(url: str) -> Optional[str]:
    """Use Jobstreet's job-detail endpoint when its public page is not readable."""
    host = httpx.URL(url).host.lower()
    if not (host == "jobstreet.com" or host.endswith(".jobstreet.com")
            or host == "jobstreet.co.id" or host.endswith(".jobstreet.co.id")):
        return None
    job_id_match = re.search(r"-(\d{6,12})(?:[/?#]|$)", url)
    if not job_id_match:
        return None

    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        response = await client.post(
            "https://xapi.supercharge-srp.co/job-search/graphql?country=id&isSmartSearch=true",
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
            json={
                "query": (
                    'query GetJobDetail($jobId: String!) { jobDetail(jobId: $jobId, '
                    'locale: "id") { id title companyDetail { name } '
                    'jobDetail { jobDescription jobRequirement } } }'
                ),
                "variables": {"jobId": job_id_match.group(1)},
            },
        )
        response.raise_for_status()
        job = response.json().get("data", {}).get("jobDetail", {})
    if not job or not job.get("title"):
        return None
    detail = job.get("jobDetail", {})
    company = job.get("companyDetail", {})
    return (
        f"Position: {job.get('title', '')}\n"
        f"Company: {company.get('name', '')}\n"
        f"Description:\n{detail.get('jobDescription', '')}\n"
        f"Requirements:\n{detail.get('jobRequirement', '')}"
    )


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

    try:
        parsed_url = httpx.URL(url)
    except (TypeError, httpx.InvalidURL) as exc:
        return JobData(extraction_notes=[f"URL tidak valid: {exc}"]).model_dump()
    if parsed_url.scheme not in ("http", "https") or not parsed_url.host:
        return JobData(
            extraction_notes=["URL harus menggunakan skema http atau https."],
        ).model_dump()

    request_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    host = parsed_url.host.lower()
    use_csr_priority = _host_matches(host, CSR_HEAVY_JOB_HOSTS)

    # Tier 1: fetch the original page and parse its HTML with Cheerio.
    try:
        async with httpx.AsyncClient(
            timeout=20,
            headers=request_headers,
            follow_redirects=True,
        ) as client:
            response = await client.get(url)
            response.raise_for_status()
            direct_text = await _run_cheerio_helper("html", response.text)
        if _usable_job_text(direct_text):
            raw_text = direct_text
            notes.append("Scraped via direct fetch + Cheerio.")
        else:
            notes.append("Direct fetch tidak menghasilkan konten lowongan yang cukup; mencoba fallback.")
    except Exception as exc:
        notes.append(f"Direct fetch + Cheerio gagal: {exc}")

    # Preserve Jobstreet's site-specific extraction when its page/API is available.
    if not raw_text:
        try:
            jobstreet_text = await _fetch_jobstreet_job_text(url)
            if jobstreet_text and _usable_job_text(jobstreet_text):
                raw_text = jobstreet_text
                notes.append("Scraped via Jobstreet job-detail API.")
        except Exception as exc:
            notes.append(f"Jobstreet API gagal: {exc}")

    async def _try_jina_reader() -> None:
        nonlocal raw_text
        if raw_text:
            return
        try:
            jina_text = await _fetch_jina_reader_text(url)
            if _usable_job_text(jina_text):
                raw_text = jina_text
                notes.append("Scraped via Jina Reader API.")
            else:
                notes.append("Jina Reader tidak menghasilkan konten lowongan yang cukup.")
        except Exception as exc:
            notes.append(f"Jina Reader gagal: {exc}")

    async def _try_puppeteer() -> None:
        nonlocal raw_text
        if raw_text:
            return
        try:
            rendered_text = await _run_cheerio_helper("render", url)
            if _usable_job_text(rendered_text):
                raw_text = rendered_text
                notes.append("Scraped via Puppeteer headless + Cheerio.")
            else:
                notes.append("Puppeteer tidak menghasilkan konten lowongan yang cukup.")
        except Exception as exc:
            notes.append(f"Puppeteer headless gagal: {exc}")

    # Tier 2/3: Jina Reader then Puppeteer (CSR-heavy hosts try Puppeteer first).
    if use_csr_priority:
        await _try_puppeteer()
        await _try_jina_reader()
    else:
        await _try_jina_reader()
        await _try_puppeteer()

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
            if isinstance(parsed, dict) and "error" not in parsed:
                parsed["raw_text"] = raw_text[:500]
                parsed["extraction_notes"] = notes
                return parsed
            notes.append("LLM mengembalikan error; mencoba parse parsial.")
    except Exception as e:
        notes.append(f"LLM parsing gagal: {str(e)}")

    return _partial_job_data_from_text(raw_text, notes).model_dump()


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
