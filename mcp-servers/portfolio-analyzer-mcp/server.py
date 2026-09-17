"""
portfolio-analyzer-mcp — MCP Server for Portfolio Analysis
Tools:
  - analyze_github_portfolio: Analyze a GitHub profile/repo for skill signals
  - analyze_portfolio_url: Analyze a portfolio URL (Behance, personal site, etc.)
  - analyze_portfolio_file: Analyze a portfolio file (PDF case study, image)
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
    name="portfolio-analyzer-mcp",
    instructions="MCP server untuk analisis portofolio: GitHub, Behance, situs personal, PDF case study.",
)

# OpenAI-compatible endpoint (same as resume-parser & scoring-engine)
OPENAI_COMPAT_BASE_URL = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "").rstrip("/")
OPENAI_COMPAT_API_KEY  = os.getenv("OPENAI_COMPATIBLE_API_KEY", "")
OPENAI_COMPAT_MODEL    = os.getenv("OPENAI_COMPAT_PORTFOLIO_MODEL", os.getenv("OPENAI_COMPAT_CV_MODEL", "gemini/gemini-3.5-flash-lite"))
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


def _parse_openai_response(raw: str) -> str:
    """Parse both non-streaming JSON and SSE streaming responses."""
    raw = raw.strip()
    if not raw:
        return ""
    stripped = raw.lstrip()
    if stripped.startswith("{"):
        try:
            import json as _json
            decoder = _json.JSONDecoder()
            data, _ = decoder.raw_decode(stripped)
            msg = data["choices"][0]["message"]
            return msg.get("content", "") or ""
        except Exception:
            pass
    # SSE streaming fallback
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
    """Call LLM via OpenAI-compatible endpoint."""
    if not OPENAI_COMPAT_BASE_URL or not OPENAI_COMPAT_API_KEY:
        return ""
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                f"{OPENAI_COMPAT_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENAI_COMPAT_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENAI_COMPAT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 800,
                    "temperature": 0.1,
                    "stream": False,
                },
            )
            resp.raise_for_status()
            return _parse_openai_response(resp.text)
    except Exception as e:
        import sys
        print(f"[portfolio-analyzer] call_granite error: {e}", file=sys.stderr)
        return ""


@mcp.tool()
async def analyze_github_portfolio(
    github_url: str,
    job_requirements: list[str] = [],
) -> dict:
    """
    Analisis profil/repo GitHub untuk sinyal skill, aktivitas, dan relevansi ke loker.

    Args:
        github_url: URL profil atau repo GitHub (https://github.com/username)
        job_requirements: List skill requirement dari loker untuk scoring relevansi

    Returns:
        Dict dengan language stats, top repos, skill signals, relevance score
    """
    # Extract username from URL
    username_match = re.search(r"github\.com/([^/\?#]+)", github_url)
    if not username_match:
        return {"error": "URL GitHub tidak valid", "available": False}
    username = username_match.group(1)

    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    try:
        async with httpx.AsyncClient(timeout=15, headers=headers) as client:
            # Get user profile
            user_resp = await client.get(f"https://api.github.com/users/{username}")
            user_data = user_resp.json() if user_resp.status_code == 200 else {}

            # Get repos
            repos_resp = await client.get(
                f"https://api.github.com/users/{username}/repos",
                params={"sort": "updated", "per_page": 10, "type": "owner"},
            )
            repos = repos_resp.json() if repos_resp.status_code == 200 else []
    except Exception as e:
        return {"error": f"Gagal mengakses GitHub API: {str(e)}", "available": False}

    if not isinstance(repos, list):
        return {"error": "GitHub API rate limit atau profil tidak publik", "available": False}

    # Aggregate languages
    lang_count: dict = {}
    top_repos = []
    for repo in repos[:8]:
        if isinstance(repo, dict) and not repo.get("fork"):
            lang = repo.get("language")
            if lang:
                lang_count[lang] = lang_count.get(lang, 0) + 1
            top_repos.append({
                "name": repo.get("name", ""),
                "description": repo.get("description", ""),
                "language": lang,
                "stars": repo.get("stargazers_count", 0),
                "updated_at": repo.get("updated_at", ""),
            })

    top_languages = sorted(lang_count.items(), key=lambda x: x[1], reverse=True)

    # Score relevance using LLM — always attempt if repos exist
    relevance_score = 50  # default
    relevance_notes = []
    if top_repos:
        repos_summary = "\n".join([
            f"- {r['name']}: {r['description'] or 'No description'} ({r['language'] or 'unknown'})"
            for r in top_repos[:5]
        ])
        req_text = (
            f"Requirement loker: {', '.join(job_requirements[:10])}"
            if job_requirements
            else f"Bahasa utama: {', '.join([l for l, _ in top_languages[:3]])}"
        )
        prompt = f"""Berdasarkan repo GitHub berikut:
{repos_summary}

{req_text}

Berikan:
1. Skor relevansi 0-100 (seberapa kuat portofolio ini secara teknis)
2. 2-3 catatan spesifik tentang kekuatan atau kelemahan

Format JSON:
{{"relevance_score": 75, "notes": ["catatan 1", "catatan 2"]}}

JSON:"""
        try:
            llm_output = await call_granite(prompt)
            if llm_output:
                json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                    relevance_score = parsed.get("relevance_score", 50)
                    relevance_notes = parsed.get("notes", [])
        except Exception:
            pass

    return {
        "available": True,
        "username": username,
        "profile": {
            "bio": user_data.get("bio", ""),
            "public_repos": user_data.get("public_repos", 0),
            "followers": user_data.get("followers", 0),
        },
        "top_languages": [{"language": l, "repo_count": c} for l, c in top_languages[:5]],
        "top_repos": top_repos[:5],
        "relevance_score": relevance_score,
        "relevance_notes": relevance_notes,
    }


@mcp.tool()
async def analyze_portfolio_url(
    portfolio_url: str,
    job_requirements: list[str] = [],
) -> dict:
    """
    Analisis portofolio dari URL (Behance, Dribbble, situs personal, Notion, dll.).

    Args:
        portfolio_url: URL portofolio
        job_requirements: Skill requirements dari loker

    Returns:
        Dict dengan proyek yang terdeteksi, skill signals, dan relevance assessment
    """
    from bs4 import BeautifulSoup

    try:
        async with httpx.AsyncClient(
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ErgonBot/1.0)"},
            follow_redirects=True,
        ) as client:
            resp = await client.get(portfolio_url)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            for tag in soup(["script", "style", "nav", "footer"]):
                tag.decompose()
            raw_text = soup.get_text(separator="\n", strip=True)[:3000]
    except Exception as e:
        return {"error": f"Gagal mengakses URL: {str(e)}", "available": False}

    prompt = f"""Analisis konten portofolio berikut dan evaluasi relevansinya dengan requirement:

Konten portofolio:
{raw_text[:2000]}

Requirement loker: {', '.join(job_requirements[:8]) if job_requirements else 'tidak tersedia'}

Format JSON:
{{
  "detected_projects": ["proyek 1", "proyek 2"],
  "skill_signals": ["skill 1", "skill 2"],
  "portfolio_type": "design/engineering/marketing/dll",
  "relevance_score": 65,
  "relevance_notes": ["catatan 1", "catatan 2"],
  "strengths": ["kekuatan 1"],
  "missing_for_job": ["yang kurang 1"]
}}

JSON:"""

    try:
        llm_output = await call_granite(prompt)
        if llm_output:
            json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                data["available"] = True
                data["source_url"] = portfolio_url
                return data
    except Exception as e:
        import sys
        print(f"[portfolio-analyzer] analyze_portfolio_url LLM error: {e}", file=sys.stderr)

    return {
        "available": True,
        "source_url": portfolio_url,
        "detected_projects": [],
        "skill_signals": [],
        "relevance_score": 50,
        "relevance_notes": ["LLM tidak dapat menghasilkan analisis — pastikan OPENAI_COMPATIBLE_BASE_URL dan OPENAI_COMPATIBLE_API_KEY dikonfigurasi"],
    }


@mcp.tool()
async def analyze_portfolio_file(
    file_base64: str,
    filename: str = "portfolio.pdf",
    job_requirements: list[str] = [],
) -> dict:
    """
    Analisis portofolio dari file (PDF case study, gambar).

    Args:
        file_base64: Konten file dalam base64
        filename: Nama file (ekstensi menentukan cara parse)
        job_requirements: Skill requirements dari loker

    Returns:
        Dict dengan analisis proyek dan relevansi
    """
    import fitz

    raw_text = ""
    ext = filename.rsplit(".", 1)[-1].lower()

    if ext == "pdf":
        try:
            pdf_bytes = base64.b64decode(file_base64)
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            for page in doc:
                raw_text += page.get_text()
            doc.close()
        except Exception as e:
            return {"error": f"Gagal membaca PDF: {str(e)}", "available": False}
    elif ext in ("png", "jpg", "jpeg", "webp"):
        try:
            import pytesseract
            from PIL import Image
            from io import BytesIO
            img = Image.open(BytesIO(base64.b64decode(file_base64)))
            raw_text = pytesseract.image_to_string(img, lang="ind+eng")
        except Exception as e:
            return {"error": f"Gagal OCR gambar: {str(e)}", "available": False}
    else:
        return {"error": f"Format file '{ext}' tidak didukung", "available": False}

    if not raw_text.strip():
        return {"error": "Tidak ada teks yang bisa diekstrak dari file", "available": False}

    prompt = f"""Analisis konten portofolio berikut:

{raw_text[:2000]}

Requirement loker: {', '.join(job_requirements[:8]) if job_requirements else 'tidak tersedia'}

Format JSON:
{{
  "detected_projects": ["proyek 1"],
  "skill_signals": ["skill 1"],
  "relevance_score": 70,
  "relevance_notes": ["catatan relevansi"],
  "strengths": ["kekuatan"],
  "missing_for_job": ["yang kurang"]
}}

JSON:"""

    try:
        llm_output = await call_granite(prompt)
        if llm_output:
            json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                data["available"] = True
                return data
    except Exception as e:
        import sys
        print(f"[portfolio-analyzer] analyze_portfolio_file LLM error: {e}", file=sys.stderr)

    return {
        "available": True,
        "detected_projects": [],
        "skill_signals": [],
        "relevance_score": 50,
        "relevance_notes": ["LLM tidak dapat menghasilkan analisis — pastikan OPENAI_COMPATIBLE_BASE_URL dan OPENAI_COMPATIBLE_API_KEY dikonfigurasi"],
    }


if __name__ == "__main__":
    port = int(os.getenv("PORTFOLIO_ANALYZER_MCP_PORT", "8004"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
