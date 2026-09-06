"""
scoring-engine-mcp — MCP Server for CV-Job Matching & Scoring
Tools:
  - calculate_match_score: Calculate composite fit score with breakdown
  - generate_suggestions: Generate ranked improvement suggestions
  - get_embedding_similarity: Calculate semantic similarity between texts
"""
import os
import re
import json
import httpx
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP(
    name="scoring-engine-mcp",
    instructions="MCP server untuk scoring kecocokan CV-loker dengan breakdown per kategori dan generasi saran perbaikan.",
)

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "")


async def get_iam_token() -> str:
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            "https://iam.cloud.ibm.com/identity/token",
            data={"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": WATSONX_API_KEY},
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


async def call_granite(prompt: str, max_tokens: int = 1500) -> str:
    try:
        token = await get_iam_token()
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                f"{WATSONX_URL}/ml/v1/text/generation?version=2024-05-31",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={
                    "model_id": "ibm/granite-13b-instruct-v2",
                    "project_id": WATSONX_PROJECT_ID,
                    "input": prompt,
                    "parameters": {"max_new_tokens": max_tokens, "temperature": 0.15},
                },
            )
            resp.raise_for_status()
            return resp.json()["results"][0]["generated_text"]
    except Exception as e:
        return json.dumps({"error": str(e)})


async def get_watsonx_embedding(text: str) -> list[float]:
    """Get text embedding from watsonx.ai."""
    try:
        token = await get_iam_token()
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{WATSONX_URL}/ml/v1/text/embeddings?version=2024-05-31",
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json={
                    "model_id": "ibm/slate-125m-english-rtrvr",
                    "project_id": WATSONX_PROJECT_ID,
                    "inputs": [text[:512]],
                },
            )
            resp.raise_for_status()
            return resp.json()["results"][0]["embedding"]
    except Exception:
        return []


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.5
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = sum(x ** 2 for x in a) ** 0.5
    mag_b = sum(x ** 2 for x in b) ** 0.5
    if mag_a == 0 or mag_b == 0:
        return 0.5
    return dot / (mag_a * mag_b)


def keyword_overlap_score(cv_skills: list[str], job_requirements: list[str]) -> tuple[float, list[str], list[str]]:
    """Calculate keyword overlap between CV skills and job requirements."""
    if not job_requirements:
        return 0.5, [], []
    cv_lower = {s.lower().strip() for s in cv_skills}
    matched = []
    missing = []
    for req in job_requirements:
        req_lower = req.lower().strip()
        # Fuzzy match: check if any CV skill contains the requirement word or vice versa
        found = any(
            req_lower in cv_skill or cv_skill in req_lower or
            any(word in cv_lower for word in req_lower.split())
            for cv_skill in cv_lower
        )
        if found:
            matched.append(req)
        else:
            missing.append(req)
    score = len(matched) / len(job_requirements) if job_requirements else 0.5
    return score, matched, missing


def estimate_seniority_match(cv_years: int, job_seniority: str) -> float:
    """Rule-based seniority matching."""
    seniority_lower = (job_seniority or "").lower()
    if "junior" in seniority_lower or "fresh" in seniority_lower or "entry" in seniority_lower:
        target_range = (0, 2)
    elif "mid" in seniority_lower or "intermediate" in seniority_lower:
        target_range = (2, 5)
    elif "senior" in seniority_lower or "lead" in seniority_lower:
        target_range = (5, 15)
    elif "manager" in seniority_lower or "head" in seniority_lower:
        target_range = (7, 20)
    else:
        return 0.75  # No info, assume reasonable match

    if target_range[0] <= cv_years <= target_range[1]:
        return 1.0
    elif cv_years < target_range[0]:
        gap = target_range[0] - cv_years
        return max(0.2, 1.0 - gap * 0.2)
    else:  # Overqualified
        gap = cv_years - target_range[1]
        return max(0.5, 1.0 - gap * 0.1)


@mcp.tool()
async def calculate_match_score(
    job_data: dict,
    cv_data: dict,
    portfolio_data: dict = {},
    company_data: dict = {},
) -> dict:
    """
    Hitung skor kecocokan komposit antara CV dan lowongan kerja.

    Args:
        job_data: Output dari job-scraper-mcp (company, position, requirements, dll.)
        cv_data: Output dari resume-parser-mcp (skills, experience, dll.)
        portfolio_data: Output dari portfolio-analyzer-mcp (optional)
        company_data: Output dari company-intel-mcp (optional)

    Returns:
        Dict dengan overall_score, label, breakdown per kategori, dan matched/missing skills
    """
    # ─── 1. Keyword/Skill Coverage (30%) ──────────────────────────────────────
    cv_skills = []
    cv_skills_data = cv_data.get("skills", {})
    if isinstance(cv_skills_data, dict):
        cv_skills = (
            cv_skills_data.get("technical", []) +
            cv_skills_data.get("tools", []) +
            cv_skills_data.get("soft", [])
        )
    elif isinstance(cv_skills_data, list):
        cv_skills = cv_skills_data

    job_hard = job_data.get("requirements_hard_skill", [])
    job_soft = job_data.get("requirements_soft_skill", [])
    all_job_reqs = job_hard + job_soft

    keyword_score, matched_skills, missing_skills = keyword_overlap_score(cv_skills, all_job_reqs)

    # ─── 2. Semantic Fit (25%) ─────────────────────────────────────────────────
    cv_experience_text = " ".join([
        f"{exp.get('position', '')} at {exp.get('company', '')}: {' '.join(exp.get('responsibilities', [])[:3])}"
        for exp in (cv_data.get("work_experience", []) or [])[:3]
    ])
    job_responsibilities_text = " ".join(job_data.get("responsibilities", [])[:5])

    semantic_score = 0.6  # default
    if cv_experience_text and job_responsibilities_text:
        emb_cv = await get_watsonx_embedding(cv_experience_text)
        emb_job = await get_watsonx_embedding(job_responsibilities_text)
        if emb_cv and emb_job:
            semantic_score = cosine_similarity(emb_cv, emb_job)

    # ─── 3. Seniority Match (15%) ──────────────────────────────────────────────
    cv_years = int(cv_data.get("total_years_experience", 0) or 0)
    job_seniority = job_data.get("seniority", "")
    seniority_score = estimate_seniority_match(cv_years, job_seniority)

    # ─── 4. Portfolio Relevance (15%) ─────────────────────────────────────────
    portfolio_score = 0.6  # default if no portfolio
    if portfolio_data and portfolio_data.get("available"):
        portfolio_score = (portfolio_data.get("relevance_score", 60)) / 100

    # ─── 5. CV Quality (5%) ───────────────────────────────────────────────────
    cv_quality_score = 0.65
    work_exp = cv_data.get("work_experience", [])
    if work_exp:
        quantified_count = sum(
            1 for exp in work_exp
            for ach in (exp.get("achievements", []) or [])
            if any(char.isdigit() for char in str(ach))
        )
        has_summary = bool(cv_data.get("summary", ""))
        has_linkedin = bool((cv_data.get("personal_info") or {}).get("linkedin"))
        cv_quality_score = min(1.0, 0.5 + quantified_count * 0.1 + (0.1 if has_summary else 0) + (0.05 if has_linkedin else 0))

    # ─── 6. Competition Signal (10%) ──────────────────────────────────────────
    competition_score = None  # Optional
    competition_note = "Data tidak tersedia"
    applicants = job_data.get("applicants_count", "")
    quota = job_data.get("quota", "")
    if applicants and quota:
        try:
            ratio = int(re.sub(r"\D", "", str(applicants))) / int(re.sub(r"\D", "", str(quota)))
            competition_score = max(0.1, min(1.0, 10 / ratio))
            competition_note = f"{applicants} pelamar untuk {quota} posisi"
        except Exception:
            pass

    # ─── Composite Score ───────────────────────────────────────────────────────
    weights = {
        "keyword": 0.30,
        "semantic": 0.25,
        "seniority": 0.15,
        "portfolio": 0.15,
        "quality": 0.05,
        "competition": 0.10,
    }

    if competition_score is None:
        # Redistribute competition weight
        adj_weights = {k: v / 0.90 for k, v in weights.items() if k != "competition"}
        scores = {
            "keyword": keyword_score,
            "semantic": semantic_score,
            "seniority": seniority_score,
            "portfolio": portfolio_score,
            "quality": cv_quality_score,
        }
        overall = sum(adj_weights[k] * scores[k] for k in adj_weights)
    else:
        overall = (
            weights["keyword"] * keyword_score +
            weights["semantic"] * semantic_score +
            weights["seniority"] * seniority_score +
            weights["portfolio"] * portfolio_score +
            weights["quality"] * cv_quality_score +
            weights["competition"] * competition_score
        )

    overall_pct = round(overall * 100)

    # Label
    if overall_pct >= 80:
        label, label_class = "Tinggi", "high"
    elif overall_pct >= 60:
        label, label_class = "Sedang–Tinggi", "medium-high"
    elif overall_pct >= 40:
        label, label_class = "Sedang", "medium"
    else:
        label, label_class = "Rendah–Sedang", "low-medium"

    # Score range (±8%)
    score_range = f"{max(0, overall_pct - 8)}–{min(100, overall_pct + 8)}%"

    return {
        "overall_score": overall_pct,
        "label": label,
        "label_class": label_class,
        "range": score_range,
        "disclaimer": "Estimasi berbasis kecocokan CV & loker, bukan jaminan hasil rekrutmen.",
        "breakdown": [
            {
                "category": "Keyword & Skill Coverage",
                "score": round(keyword_score * 100),
                "weight": "30%",
                "detail": f"Cocok: {len(matched_skills)} dari {len(all_job_reqs)} skill yang dibutuhkan",
            },
            {
                "category": "Kecocokan Semantik Pengalaman",
                "score": round(semantic_score * 100),
                "weight": "25%",
                "detail": "Kemiripan semantik antara pengalaman CV dan tanggung jawab loker",
            },
            {
                "category": "Kesesuaian Level (Seniority)",
                "score": round(seniority_score * 100),
                "weight": "15%",
                "detail": f"CV: {cv_years} tahun pengalaman | Loker: {job_seniority or 'tidak spesifik'}",
            },
            {
                "category": "Relevansi Portofolio",
                "score": round(portfolio_score * 100),
                "weight": "15%",
                "detail": "Berdasarkan analisis portofolio yang diunggah" if portfolio_data.get("available") else "Portofolio tidak disertakan",
            },
            {
                "category": "Kelengkapan & Kualitas CV",
                "score": round(cv_quality_score * 100),
                "weight": "5%",
                "detail": "Kelengkapan data, achievement terukur, dan format CV",
            },
            {
                "category": "Sinyal Kompetisi",
                "score": round(competition_score * 100) if competition_score is not None else None,
                "weight": "10%",
                "detail": competition_note,
            },
        ],
        "matched_skills": matched_skills,
        "missing_skills": missing_skills[:10],
        "cv_years_experience": cv_years,
    }


@mcp.tool()
async def generate_suggestions(
    job_data: dict,
    cv_data: dict,
    scoring_result: dict,
    portfolio_data: dict = {},
) -> dict:
    """
    Generate daftar saran perbaikan CV yang diranking berdasarkan dampak estimasi.

    Args:
        job_data: Output dari job-scraper-mcp
        cv_data: Output dari resume-parser-mcp
        scoring_result: Output dari calculate_match_score
        portfolio_data: Output dari portfolio-analyzer-mcp (optional)

    Returns:
        Dict dengan suggestions list, masing-masing berisi rank, title, detail, impact, free (bool)
    """
    missing_skills = scoring_result.get("missing_skills", [])
    breakdown = scoring_result.get("breakdown", [])
    overall = scoring_result.get("overall_score", 70)

    # Build context for Granite
    low_categories = [
        b for b in breakdown
        if b.get("score") is not None and b.get("score", 100) < 70
    ]

    prompt = f"""Kamu adalah konsultan CV yang membantu jobseeker meningkatkan kecocokan CV mereka dengan lowongan kerja.

Data analisis:
- Posisi: {job_data.get('position', '')} di {job_data.get('company', '')}
- Skor kecocokan saat ini: {overall}%
- Skill yang kurang di CV: {', '.join(missing_skills[:8])}
- Kategori yang perlu ditingkatkan: {', '.join([b['category'] for b in low_categories])}

Informasi CV:
- Pengalaman: {cv_data.get('total_years_experience', 0)} tahun
- Skills saat ini: {', '.join((cv_data.get('skills') or {}).get('technical', [])[:8])}

Buat TEPAT 6 saran perbaikan CV yang konkret dan actionable, diranking dari dampak terbesar.
Saran harus spesifik (sebut apa yang perlu diubah/ditambah), bukan generik.

Format JSON (array dengan tepat 6 item):
[
  {{
    "rank": 1,
    "title": "Judul saran singkat (max 60 karakter)",
    "detail": "Penjelasan detail konkret apa yang harus dilakukan (1-3 kalimat)",
    "impact": "+X% estimasi kenaikan skor",
    "category": "skill/experience/format/portfolio",
    "effort": "rendah/sedang/tinggi"
  }}
]

Array JSON:"""

    try:
        llm_output = await call_granite(prompt, max_tokens=1200)
        # Find JSON array
        json_match = re.search(r"\[.*\]", llm_output, re.DOTALL)
        if json_match:
            suggestions = json.loads(json_match.group())
            # Mark first 3 as free
            for i, s in enumerate(suggestions):
                s["free"] = i < 3
                s["rank"] = i + 1
            return {"suggestions": suggestions, "total_count": len(suggestions)}
    except Exception as e:
        pass

    # Fallback suggestions based on scoring
    fallback = []
    if missing_skills:
        fallback.append({
            "rank": 1, "title": f"Tambahkan skill yang kurang: {', '.join(missing_skills[:3])}",
            "detail": f"Loker meminta skill berikut yang tidak ditemukan di CV kamu: {', '.join(missing_skills[:5])}. Jika kamu memilikinya, tambahkan ke bagian Skills.",
            "impact": "+8%", "category": "skill", "effort": "rendah", "free": True,
        })

    # Check for unquantified achievements
    for exp in (cv_data.get("work_experience") or []):
        if exp.get("flags") and "belum terkuantifikasi" in str(exp.get("flags", [])):
            fallback.append({
                "rank": len(fallback) + 1,
                "title": "Tambahkan angka/metrik ke pencapaian",
                "detail": "Ubah kalimat pencapaian generik menjadi konkret dengan angka. Contoh: 'meningkatkan penjualan' → 'meningkatkan penjualan 35% dalam Q1 2025'.",
                "impact": "+6%", "category": "experience", "effort": "rendah", "free": True,
            })
            break

    # Pad with generic but useful suggestions
    generic = [
        {"title": "Perkuat professional summary", "detail": "Tulis 2-3 kalimat pembuka yang secara langsung menyebutkan posisi yang dilamar dan nilai tambah utama kamu.", "impact": "+5%", "category": "format", "effort": "sedang"},
        {"title": "Sesuaikan urutan skill", "detail": "Pindahkan skill yang paling relevan dengan loker ke posisi pertama di bagian Skills.", "impact": "+4%", "category": "skill", "effort": "rendah"},
        {"title": "Tambahkan proyek portofolio relevan", "detail": "Sertakan 2-3 proyek yang paling relevan dengan posisi yang dilamar, lengkap dengan hasil yang terukur.", "impact": "+4%", "category": "portfolio", "effort": "sedang"},
        {"title": "Perbarui LinkedIn & GitHub di header", "detail": "Pastikan URL LinkedIn dan GitHub aktif ada di bagian header CV untuk memudahkan rekruter memverifikasi.", "impact": "+3%", "category": "format", "effort": "rendah"},
    ]
    for i, g in enumerate(generic):
        if len(fallback) >= 6:
            break
        fallback.append({
            "rank": len(fallback) + 1,
            "free": len(fallback) < 3,
            **g,
        })

    while len(fallback) < 6:
        fallback.append({
            "rank": len(fallback) + 1,
            "title": f"Saran perbaikan #{len(fallback) + 1}",
            "detail": "Analisis detail tersedia setelah unlock.",
            "impact": "+2%", "category": "format", "effort": "rendah",
            "free": len(fallback) < 3,
        })

    return {"suggestions": fallback[:6], "total_count": 6}


@mcp.tool()
async def get_embedding_similarity(text_a: str, text_b: str) -> dict:
    """
    Hitung cosine similarity antara dua teks menggunakan watsonx embedding.

    Args:
        text_a: Teks pertama (misal deskripsi pengalaman dari CV)
        text_b: Teks kedua (misal tanggung jawab dari job posting)

    Returns:
        Dict dengan similarity score (0-1) dan interpretasi
    """
    emb_a = await get_watsonx_embedding(text_a[:512])
    emb_b = await get_watsonx_embedding(text_b[:512])

    if not emb_a or not emb_b:
        return {"similarity": 0.5, "note": "Embedding tidak tersedia, menggunakan nilai default"}

    sim = cosine_similarity(emb_a, emb_b)
    return {
        "similarity": round(sim, 4),
        "percentage": round(sim * 100, 1),
        "interpretation": (
            "Sangat mirip" if sim >= 0.85 else
            "Cukup mirip" if sim >= 0.70 else
            "Agak mirip" if sim >= 0.55 else
            "Kurang mirip"
        ),
    }


if __name__ == "__main__":
    port = int(os.getenv("SCORING_ENGINE_MCP_PORT", "8005"))
    mcp.run(transport="streamable-http", host="0.0.0.0", port=port, path="/mcp")
