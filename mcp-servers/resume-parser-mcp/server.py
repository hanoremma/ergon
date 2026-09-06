"""
resume-parser-mcp — MCP Server for CV/Resume Parsing
Tools:
  - parse_cv_from_pdf: Extract structured data from CV PDF
  - parse_cv_from_url: Extract structured data from CV at a URL (Google Docs, etc.)
  - parse_cv_from_text: Extract structured data from raw CV text
"""
import os
import re
import json
import base64
import httpx
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(
    name="resume-parser-mcp",
    instructions="MCP server untuk parsing CV/resume menjadi data terstruktur: riwayat kerja, pendidikan, skill, achievement.",
)

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")


async def call_granite(prompt: str) -> str:
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    async with httpx.AsyncClient(timeout=45) as client:
        try:
            token_resp = await client.post(
                iam_url,
                data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": WATSONX_API_KEY},
            )
            token_resp.raise_for_status()
            iam_token = token_resp.json()["access_token"]
            resp = await client.post(
                f"{WATSONX_URL}/ml/v1/text/generation?version=2024-05-31",
                headers={"Authorization": f"Bearer {iam_token}", "Content-Type": "application/json"},
                json={
                    "model_id": "ibm/granite-13b-instruct-v2",
                    "project_id": WATSONX_PROJECT_ID,
                    "input": prompt,
                    "parameters": {"max_new_tokens": 1500, "temperature": 0.1},
                },
            )
            resp.raise_for_status()
            return resp.json()["results"][0]["generated_text"]
        except Exception as e:
            return json.dumps({"error": str(e)})


def build_cv_extraction_prompt(raw_text: str) -> str:
    return f"""Kamu adalah AI parser CV/resume. Ekstrak semua informasi dari CV berikut ke format JSON terstruktur.

Teks CV:
```
{raw_text[:4000]}
```

Kembalikan JSON dengan format ini (gunakan array kosong jika tidak ada data):
{{
  "personal_info": {{
    "name": "",
    "email": "",
    "phone": "",
    "location": "",
    "linkedin": "",
    "github": "",
    "portfolio_url": ""
  }},
  "summary": "ringkasan/objective jika ada",
  "work_experience": [
    {{
      "company": "",
      "position": "",
      "duration": "",
      "start_date": "",
      "end_date": "",
      "responsibilities": ["..."],
      "achievements": ["..."],
      "achievements_quantified": true/false,
      "flags": ["belum terkuantifikasi jika achievement tidak punya angka"]
    }}
  ],
  "education": [
    {{
      "institution": "",
      "degree": "",
      "field": "",
      "year": "",
      "gpa": ""
    }}
  ],
  "skills": {{
    "technical": ["skill1", "skill2"],
    "soft": ["skill1", "skill2"],
    "tools": ["tool1", "tool2"],
    "languages": ["bahasa1"]
  }},
  "certifications": ["cert1"],
  "total_years_experience": 0,
  "seniority_estimate": "junior/mid/senior",
  "parsing_notes": []
}}

JSON:
```"""


async def extract_cv_data(raw_text: str) -> dict:
    """Parse CV text using Granite LLM."""
    prompt = build_cv_extraction_prompt(raw_text)
    llm_output = await call_granite(prompt)

    # Try JSON parse
    try:
        json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass

    # Fallback: basic regex extraction
    return {
        "personal_info": {},
        "summary": "",
        "work_experience": [],
        "education": [],
        "skills": {"technical": [], "soft": [], "tools": [], "languages": []},
        "certifications": [],
        "total_years_experience": 0,
        "seniority_estimate": "unknown",
        "parsing_notes": ["Parsing otomatis gagal — data mungkin tidak lengkap"],
        "raw_text_preview": raw_text[:300],
    }


@mcp.tool()
async def parse_cv_from_pdf(pdf_base64: str, filename: str = "cv.pdf") -> dict:
    """
    Parse CV/resume dari file PDF (base64 encoded).

    Args:
        pdf_base64: Konten PDF dalam base64 encoding
        filename: Nama file original

    Returns:
        Structured CV data: personal info, work history, education, skills, achievements
    """
    import fitz  # PyMuPDF
    notes = []

    try:
        pdf_bytes = base64.b64decode(pdf_base64)
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        raw_text = ""
        for page in doc:
            raw_text += page.get_text()
        doc.close()
    except Exception as e:
        return {
            "error": f"Gagal membaca PDF: {str(e)}",
            "parsing_notes": [f"Gagal membaca PDF '{filename}'"],
        }

    if not raw_text.strip():
        return {
            "error": "PDF tidak mengandung teks yang bisa dibaca (mungkin scan image)",
            "parsing_notes": ["Coba konversi ke teks atau gunakan file PDF dengan teks selectable"],
        }

    return await extract_cv_data(raw_text)


@mcp.tool()
async def parse_cv_from_url(url: str) -> dict:
    """
    Parse CV/resume dari URL (Google Docs, personal website, LinkedIn, dll.).

    Args:
        url: URL halaman CV (Google Docs export, personal site, dll.)

    Returns:
        Structured CV data
    """
    from bs4 import BeautifulSoup

    # Handle Google Docs — convert to export URL
    if "docs.google.com" in url and "/edit" in url:
        doc_id = re.search(r"/d/([a-zA-Z0-9_-]+)", url)
        if doc_id:
            url = f"https://docs.google.com/document/d/{doc_id.group(1)}/export?format=txt"

    try:
        async with httpx.AsyncClient(
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ErgonBot/1.0)"},
            follow_redirects=True,
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()

            content_type = resp.headers.get("content-type", "")
            if "text/plain" in content_type:
                raw_text = resp.text
            else:
                soup = BeautifulSoup(resp.text, "lxml")
                for tag in soup(["script", "style", "nav", "footer"]):
                    tag.decompose()
                raw_text = soup.get_text(separator="\n", strip=True)
    except Exception as e:
        return {
            "error": f"Gagal mengambil URL: {str(e)}",
            "parsing_notes": [f"URL '{url}' tidak bisa diakses"],
        }

    return await extract_cv_data(raw_text)


@mcp.tool()
async def parse_cv_from_text(raw_text: str) -> dict:
    """
    Parse CV/resume dari teks mentah (paste langsung).

    Args:
        raw_text: Teks CV yang dipaste langsung

    Returns:
        Structured CV data
    """
    if not raw_text or len(raw_text.strip()) < 50:
        return {
            "error": "Teks CV terlalu pendek atau kosong",
            "parsing_notes": ["Teks CV minimal harus berisi 50 karakter"],
        }

    return await extract_cv_data(raw_text)


if __name__ == "__main__":
    port = int(os.getenv("RESUME_PARSER_MCP_PORT", "8003"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
