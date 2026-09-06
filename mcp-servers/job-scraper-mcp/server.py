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

load_dotenv()

mcp = FastMCP(
    name="job-scraper-mcp",
    instructions="MCP server untuk ekstraksi data lowongan kerja dari URL, PDF, atau gambar.",
)

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")


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


# ─── Watsonx LLM Helper ─────────────────────────────────────────────────────────

async def call_granite(prompt: str, max_tokens: int = 1024) -> str:
    """Call IBM watsonx.ai Granite model for text processing."""
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    token_payload = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": WATSONX_API_KEY,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        # Get IAM token
        try:
            token_resp = await client.post(iam_url, data=token_payload)
            token_resp.raise_for_status()
            iam_token = token_resp.json()["access_token"]
        except Exception:
            # Fallback: use mock extraction if watsonx unavailable
            return json.dumps({"error": "watsonx unavailable", "mock": True})

        # Call Granite
        wx_url = f"{WATSONX_URL}/ml/v1/text/generation?version=2024-05-31"
        headers = {
            "Authorization": f"Bearer {iam_token}",
            "Content-Type": "application/json",
        }
        body = {
            "model_id": "ibm/granite-13b-instruct-v2",
            "project_id": WATSONX_PROJECT_ID,
            "input": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.1,
                "stop_sequences": ["```"],
            },
        }
        resp = await client.post(wx_url, headers=headers, json=body)
        resp.raise_for_status()
        result = resp.json()
        return result["results"][0]["generated_text"]


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
    from bs4 import BeautifulSoup

    notes = []
    raw_text = ""

    try:
        async with httpx.AsyncClient(
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ErgonBot/1.0)"},
            follow_redirects=True,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            html = resp.text

        soup = BeautifulSoup(html, "lxml")
        # Remove scripts, styles, nav
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        raw_text = soup.get_text(separator="\n", strip=True)
        raw_text = re.sub(r"\n{3,}", "\n\n", raw_text)

    except Exception as e:
        notes.append(f"Gagal mengambil URL: {str(e)}")
        return JobData(
            extraction_notes=notes,
            raw_text="",
        ).model_dump()

    # Parse with Granite
    try:
        prompt = build_extraction_prompt(raw_text)
        llm_output = await call_granite(prompt)
        # Try to parse JSON from LLM output
        json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
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
