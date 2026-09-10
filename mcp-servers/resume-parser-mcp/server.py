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

load_dotenv(override=True)

mcp = FastMCP(
    name="resume-parser-mcp",
    instructions="MCP server untuk parsing CV/resume menjadi data terstruktur: riwayat kerja, pendidikan, skill, achievement.",
)

# Use the same OpenAI-compatible endpoint as job-scraper and scoring-engine
OPENAI_COMPAT_BASE_URL = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "").rstrip("/")
OPENAI_COMPAT_API_KEY  = os.getenv("OPENAI_COMPATIBLE_API_KEY", "")
# ergon-resume-parser maps to a heavy thinking model — use a fast model for CV parsing
OPENAI_COMPAT_MODEL    = os.getenv("OPENAI_COMPAT_CV_MODEL", "gemini/gemini-3.5-flash-lite")


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


async def call_granite(prompt: str) -> str:
    """Call LLM via OpenAI-compatible endpoint for CV extraction."""
    if not OPENAI_COMPAT_BASE_URL or not OPENAI_COMPAT_API_KEY:
        return json.dumps({"error": "LLM not configured"})
    try:
        async with httpx.AsyncClient(timeout=90) as client:
            resp = await client.post(
                f"{OPENAI_COMPAT_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_COMPAT_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENAI_COMPAT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 3000,
                    "temperature": 0.1,
                    "stream": False,
                },
            )
            resp.raise_for_status()
            return _parse_openai_response(resp.text)
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
    """Parse CV text using LLM."""
    prompt = build_cv_extraction_prompt(raw_text)
    llm_output = await call_granite(prompt)

    if llm_output:
        # If LLM returned an error dict, don't use it
        try:
            _err = json.loads(llm_output)
            if isinstance(_err, dict) and "error" in _err and not any(
                k in _err for k in ("personal_info", "skills", "work_experience", "education")
            ):
                llm_output = ""  # treat as failed
        except Exception:
            pass

    if llm_output:
        # Strip markdown fences and thinking tags if present
        cleaned = re.sub(r"<think>.*?</think>", "", llm_output, flags=re.DOTALL).strip()
        cleaned = re.sub(r"```(?:json)?\s*", "", cleaned).strip()

        # Try direct parse first (skip if it's just an error dict)
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict) and any(
                k in parsed for k in ("personal_info", "skills", "work_experience", "education")
            ):
                return parsed
        except Exception:
            pass

        # Find the last (outermost) JSON object — use decoder to find first valid one
        try:
            decoder = json.JSONDecoder()
            # Scan forward until we find a valid JSON object
            idx = cleaned.find("{")
            while idx != -1:
                try:
                    obj, _ = decoder.raw_decode(cleaned[idx:])
                    if isinstance(obj, dict) and (
                        obj.get("personal_info") or obj.get("skills") or obj.get("work_experience")
                    ):
                        return obj
                except Exception:
                    pass
                idx = cleaned.find("{", idx + 1)
        except Exception:
            pass

    # Fallback
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

