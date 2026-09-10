"""
company-intel-mcp — MCP Server for Company Intelligence
Tools:
  - research_company: Search for recent news, products, funding, and context about a company
  - get_interview_context: Build interview-relevant context from company data
"""
import os
import json
import httpx
import re
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv(override=True)

mcp = FastMCP(
    name="company-intel-mcp",
    instructions="MCP server untuk riset kontekstual perusahaan: berita terbaru, produk, funding, dan konteks rekrutmen.",
)

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")


async def call_granite(prompt: str) -> str:
    iam_url = "https://iam.cloud.ibm.com/identity/token"
    async with httpx.AsyncClient(timeout=30) as client:
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
                    "parameters": {"max_new_tokens": 800, "temperature": 0.2},
                },
            )
            resp.raise_for_status()
            return resp.json()["results"][0]["generated_text"]
        except Exception:
            return ""


async def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Simple web search via DuckDuckGo HTML (no API key needed, best-effort)."""
    results = []
    try:
        url = f"https://html.duckduckgo.com/html/?q={query.replace(' ', '+')}"
        async with httpx.AsyncClient(
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; ErgonBot/1.0)"},
        ) as client:
            resp = await client.get(url)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(resp.text, "lxml")
            for result in soup.select(".result__body")[:max_results]:
                title_el = result.select_one(".result__title")
                snippet_el = result.select_one(".result__snippet")
                link_el = result.select_one(".result__url")
                results.append({
                    "title": title_el.get_text(strip=True) if title_el else "",
                    "snippet": snippet_el.get_text(strip=True) if snippet_el else "",
                    "url": link_el.get_text(strip=True) if link_el else "",
                })
    except Exception as e:
        results.append({"error": str(e)})
    return results


@mcp.tool()
async def research_company(
    company_name: str,
    position: str = "",
    max_results: int = 5,
) -> dict:
    """
    Riset kontekstual perusahaan untuk memperkaya analisis CV dan saran perbaikan.

    Args:
        company_name: Nama perusahaan yang akan diriset
        position: Posisi yang dilamar (untuk konteks pencarian)
        max_results: Jumlah maksimum hasil pencarian

    Returns:
        Dict berisi berita terbaru, produk, funding, dan insight rekrutmen
    """
    if not company_name or company_name in ("", "Tidak dapat diekstrak"):
        return {"available": False, "reason": "Nama perusahaan tidak tersedia"}

    # Search queries
    queries = [
        f"{company_name} berita terbaru 2025 2026",
        f"{company_name} produk baru funding rekrutmen",
    ]
    if position:
        queries.append(f"{company_name} {position} lowongan kebutuhan")

    all_results = []
    for q in queries[:2]:  # Batasi 2 query
        results = await web_search(q, max_results=3)
        all_results.extend(results)

    if not all_results or all(r.get("error") for r in all_results):
        return {"available": False, "reason": "Tidak ada hasil pencarian relevan"}

    # Synthesize with Granite
    snippets = "\n".join([
        f"- {r.get('title', '')}: {r.get('snippet', '')}"
        for r in all_results if not r.get("error")
    ])

    prompt = f"""Berdasarkan hasil pencarian berikut tentang perusahaan "{company_name}":

{snippets}

Buat ringkasan singkat (3-5 poin) tentang:
1. Apa yang sedang terjadi di perusahaan ini (produk baru, expansion, dll)
2. Kenapa mereka mungkin sedang merekrut posisi "{position}"
3. Hal spesifik yang sebaiknya disorot pelamar di CV-nya

Format sebagai JSON:
{{
  "company_context": "ringkasan 2-3 kalimat",
  "why_hiring": "perkiraan alasan merekrut",
  "cv_recommendations": ["poin 1", "poin 2", "poin 3"],
  "recent_highlights": ["highlight 1", "highlight 2"]
}}

JSON:"""

    try:
        llm_output = await call_granite(prompt)
        json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            data["available"] = True
            data["sources"] = [r.get("url", "") for r in all_results[:3] if not r.get("error")]
            return data
    except Exception:
        pass

    return {
        "available": True,
        "company_context": snippets[:500],
        "cv_recommendations": [],
        "recent_highlights": [],
        "sources": [],
    }


@mcp.tool()
async def get_interview_context(
    company_name: str,
    position: str,
    company_research: dict,
) -> dict:
    """
    Generate konteks untuk pertanyaan wawancara berdasarkan riset perusahaan.

    Args:
        company_name: Nama perusahaan
        position: Posisi yang dilamar
        company_research: Output dari research_company tool

    Returns:
        Dict berisi pertanyaan wawancara berbasis konteks perusahaan
    """
    context = company_research.get("company_context", "")
    highlights = company_research.get("recent_highlights", [])

    prompt = f"""Buat 5 pertanyaan wawancara spesifik untuk posisi "{position}" di perusahaan "{company_name}".

Konteks perusahaan: {context}
Highlights terbaru: {', '.join(highlights[:3])}

Pertanyaan harus mencerminkan kondisi nyata perusahaan, bukan pertanyaan generik.
Format JSON:
{{
  "behavioral_questions": ["pertanyaan 1", "pertanyaan 2"],
  "technical_questions": ["pertanyaan 1", "pertanyaan 2"],
  "company_specific_questions": ["pertanyaan 1"]
}}

JSON:"""

    try:
        llm_output = await call_granite(prompt)
        json_match = re.search(r"\{.*\}", llm_output, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
    except Exception:
        pass

    return {
        "behavioral_questions": [
            f"Ceritakan pengalaman kamu yang paling relevan untuk posisi {position}.",
            "Bagaimana kamu menangani situasi tekanan tinggi di pekerjaan sebelumnya?",
        ],
        "technical_questions": [
            f"Apa skill teknis terkuat kamu yang relevan untuk {position}?",
        ],
        "company_specific_questions": [
            f"Mengapa kamu tertarik bergabung dengan {company_name}?",
        ],
    }


if __name__ == "__main__":
    port = int(os.getenv("COMPANY_INTEL_MCP_PORT", "8002"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
