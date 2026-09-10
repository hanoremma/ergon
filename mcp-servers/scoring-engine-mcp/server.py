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

load_dotenv(override=True)

mcp = FastMCP(
    name="scoring-engine-mcp",
    instructions="MCP server untuk scoring kecocokan CV-loker dengan breakdown per kategori dan generasi saran perbaikan.",
)

OPENAI_COMPAT_BASE_URL = os.getenv("OPENAI_COMPATIBLE_BASE_URL", "").rstrip("/")
OPENAI_COMPAT_API_KEY  = os.getenv("OPENAI_COMPATIBLE_API_KEY", "")
# ergon-scoring-engine may be a heavy model — use fast model for suggestions generation
OPENAI_COMPAT_MODEL    = os.getenv("OPENAI_COMPAT_SCORING_MODEL", "gemini/gemini-3.5-flash-lite")


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


async def call_granite(prompt: str, max_tokens: int = 1500) -> str:
    """Call LLM via OpenAI-compatible endpoint."""
    if not OPENAI_COMPAT_BASE_URL or not OPENAI_COMPAT_API_KEY:
        return json.dumps({"error": "LLM not configured"})
    try:
        async with httpx.AsyncClient(timeout=35) as client:
            resp = await client.post(
                f"{OPENAI_COMPAT_BASE_URL}/chat/completions",
                headers={"Authorization": f"Bearer {OPENAI_COMPAT_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": OPENAI_COMPAT_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.15,
                    "stream": False,
                },
            )
            resp.raise_for_status()
            return _parse_openai_response(resp.text)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def get_watsonx_embedding(text: str) -> list[float]:
    """Embedding — returns empty list (no embedding service configured)."""
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
        return None, [], []   # None = no data, caller decides fallback
    cv_lower = {s.lower().strip() for s in cv_skills}
    matched = []
    missing = []
    for req in job_requirements:
        req_lower = req.lower().strip()
        found = any(
            req_lower in cv_skill or cv_skill in req_lower or
            any(word in cv_lower for word in req_lower.split())
            for cv_skill in cv_lower
        )
        if found:
            matched.append(req)
        else:
            missing.append(req)
    score = len(matched) / len(job_requirements) if job_requirements else 0.0
    return score, matched, missing


async def llm_domain_relevance(cv_skills: list[str], cv_experience: list[dict], job_title: str, job_url: str) -> float:
    """
    Use LLM to estimate domain relevance between CV and job when no requirements data available.
    Returns 0.0–1.0. Fast call with small token budget.
    """
    if not cv_skills and not cv_experience:
        return 0.5  # No CV data — can't judge

    # Build CV domain summary
    exp_titles = [f"{e.get('position','')} at {e.get('company','')}" for e in (cv_experience or [])[:3] if e.get('position')]
    cv_summary = ", ".join(cv_skills[:8])
    if exp_titles:
        cv_summary += " | Pengalaman: " + "; ".join(exp_titles)

    job_context = job_title or job_url or "tidak diketahui"

    prompt = (
        f"Nilai relevansi antara profil CV dan loker dari 0.0 sampai 1.0.\n"
        f"CV domain: {cv_summary}\n"
        f"Loker: {job_context}\n\n"
        f"Aturan:\n"
        f"- 0.0-0.2: Domain sangat berbeda (misal AI Engineer melamar desain grafis/akuntan/hukum)\n"
        f"- 0.2-0.4: Domain cukup berbeda (misal AI Engineer melamar marketing/sales)\n"
        f"- 0.4-0.6: Ada sedikit relevansi (misal AI Engineer melamar IT generalis)\n"
        f"- 0.6-0.8: Domain relevan (misal AI Engineer melamar software engineer)\n"
        f"- 0.8-1.0: Domain sangat cocok (misal AI Engineer melamar AI/ML/NLP Engineer)\n\n"
        f"Jawab HANYA satu angka desimal, contoh: 0.75\nNilai:"
    )

    try:
        llm_output = await call_granite(prompt, max_tokens=10)
        # Extract first float from response
        match = re.search(r"0?\.\d+|[01]\.?\d*", llm_output.strip())
        if match:
            val = float(match.group())
            return max(0.0, min(1.0, val))
    except Exception:
        pass
    return 0.5


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
    # ─── Extract CV skills & job context ──────────────────────────────────────
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

    cv_work_exp = cv_data.get("work_experience", []) or []

    job_hard = (
        job_data.get("requirements_hard_skill") or
        job_data.get("requirements") or
        []
    )
    job_soft = job_data.get("requirements_soft_skill") or []
    all_job_reqs = job_hard + job_soft

    job_title = job_data.get("position", "") or job_data.get("title", "") or ""
    job_url   = job_data.get("source_url", "") or job_data.get("_raw_input", "") or ""

    # Detect whether we have real job data or just a URL (scraping failed)
    job_has_content = bool(all_job_reqs or job_data.get("responsibilities") or job_title)

    # ─── 1. Keyword/Skill Coverage (30%) ──────────────────────────────────────
    keyword_score_raw, matched_skills, missing_skills = keyword_overlap_score(cv_skills, all_job_reqs)

    if keyword_score_raw is None:
        # No job requirements — use LLM domain relevance as proxy for keyword match
        domain_score = await llm_domain_relevance(cv_skills, cv_work_exp, job_title, job_url)
        keyword_score = domain_score
        keyword_detail = f"Estimasi relevansi domain CV vs loker (job scraping tidak tersedia)"
    else:
        keyword_score = keyword_score_raw
        keyword_detail = f"Cocok: {len(matched_skills)} dari {len(all_job_reqs)} skill yang dibutuhkan"

    # ─── 2. Semantic Fit (25%) ─────────────────────────────────────────────────
    cv_experience_text = " ".join([
        f"{exp.get('position', '')} at {exp.get('company', '')}: {' '.join(exp.get('responsibilities', [])[:3])}"
        for exp in cv_work_exp[:3]
    ])
    job_responsibilities_text = " ".join(job_data.get("responsibilities", [])[:5])

    # If no job responsibilities AND we already computed domain_score, reuse it for semantic
    if not job_responsibilities_text and not job_has_content:
        # domain_score already computed above — use it with slight variation
        domain_score_for_semantic = (
            domain_score if keyword_score_raw is None
            else await llm_domain_relevance(cv_skills, cv_work_exp, job_title, job_url)
        )
        semantic_score = domain_score_for_semantic * 0.9  # slightly lower than domain (no detail)
    else:
        semantic_score = 0.6  # default when no embedding
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
    portfolio_score = 0.5  # lower default — no data means uncertain
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
        label, label_class = "Sedang-Tinggi", "medium-high"
    elif overall_pct >= 40:
        label, label_class = "Sedang", "medium"
    else:
        label, label_class = "Rendah-Sedang", "low-medium"

    # Score range (+-8%) — use ASCII hyphen to avoid encoding issues
    score_range = f"{max(0, overall_pct - 8)}-{min(100, overall_pct + 8)}%"

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
                "detail": keyword_detail,
            },
            {
                "category": "Kecocokan Semantik Pengalaman",
                "score": round(semantic_score * 100),
                "weight": "25%",
                "detail": (
                    "Relevansi pengalaman CV terhadap domain loker (estimasi LLM)"
                    if not job_has_content
                    else "Kemiripan semantik antara pengalaman CV dan tanggung jawab loker"
                ),
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

    position = job_data.get("position", "") or job_data.get("title", "") or ""
    company = job_data.get("company", "") or ""
    # Try to extract job context from raw_input URL if position is unknown
    raw_input = job_data.get("_raw_input", "") or job_data.get("source_url", "") or ""
    job_context = f"{position} di {company}" if position else (f"dari {raw_input}" if raw_input else "yang dilamar")

    cv_skills_list = []
    cv_skills_data = cv_data.get("skills", {})
    if isinstance(cv_skills_data, dict):
        cv_skills_list = (
            cv_skills_data.get("technical", []) +
            cv_skills_data.get("tools", [])
        )[:8]
    elif isinstance(cv_skills_data, list):
        cv_skills_list = cv_skills_data[:8]

    cv_years = cv_data.get("total_years_experience", 0) or 0

    # Build score context sentence
    score_context = f"Skor kecocokan: {overall}%"
    if low_categories:
        score_context += f". Kategori lemah: {', '.join([b['category'] for b in low_categories])}"
    if missing_skills:
        score_context += f". Skill yang kurang: {', '.join(missing_skills[:6])}"

    prompt = f"""Kamu adalah konsultan CV profesional. Bantu jobseeker meningkatkan CV mereka untuk posisi {job_context}.

Konteks analisis:
- {score_context}
- Pengalaman CV: {cv_years} tahun
- Skills di CV: {', '.join(cv_skills_list) if cv_skills_list else 'tidak terdeteksi'}

Berikan TEPAT 6 saran perbaikan CV yang KONKRET dan ACTIONABLE, diranking dari dampak terbesar ke terkecil.
Saran harus menyebut tindakan spesifik yang bisa langsung dilakukan. JANGAN generik seperti "perbaiki CV kamu".
Fokus pada: menambahkan angka/metrik, keyword ATS, professional summary, urutan skill, format pengalaman, portofolio.

Format JSON (array tepat 6 item, tidak ada teks lain di luar array):
[
  {{
    "rank": 1,
    "title": "Judul saran singkat (max 60 karakter)",
    "detail": "Penjelasan konkret 1-2 kalimat: apa yang diubah/ditambah dan contoh spesifiknya",
    "impact": "+X%",
    "category": "skill/experience/format/portfolio",
    "effort": "rendah/sedang/tinggi"
  }}
]

Array JSON:"""

    try:
        llm_output = await call_granite(prompt, max_tokens=1200)
        # Strip markdown code fences if present
        llm_clean = re.sub(r"```(?:json)?\s*", "", llm_output).strip()
        json_match = re.search(r"\[.*\]", llm_clean, re.DOTALL)
        if json_match:
            suggestions = json.loads(json_match.group())
            # Mark first 3 as free
            for i, s in enumerate(suggestions):
                s["free"] = i < 3
                s["rank"] = i + 1
            return {"suggestions": suggestions, "total_count": len(suggestions)}
    except Exception as e:
        pass

    # Fallback suggestions based on scoring — no placeholder entries
    fallback = []

    job_title = position  # already extracted above
    missing_str = ", ".join(missing_skills[:3]) if missing_skills else ""

    # Identify which categories score low to make fallback smarter
    low_cat_names = {b["category"].lower() for b in low_categories}
    has_low_keyword = any("keyword" in c or "skill" in c for c in low_cat_names)
    has_low_semantic = any("semantik" in c or "pengalaman" in c for c in low_cat_names)
    has_low_portfolio = any("portofolio" in c for c in low_cat_names)
    has_low_quality = any("kualitas" in c or "kelengkapan" in c for c in low_cat_names)

    # Dynamic entry based on missing skills (highest priority)
    if missing_skills:
        fallback.append({
            "rank": 1,
            "title": f"Tambahkan skill yang hilang: {', '.join(missing_skills[:3])}",
            "detail": (
                f"Skill berikut ada di job description tapi tidak ditemukan di CV kamu: {', '.join(missing_skills[:5])}. "
                "Jika kamu menguasainya, tambahkan eksplisit di bagian Skills atau di deskripsi pengalaman."
            ),
            "impact": "+8%", "category": "skill", "effort": "rendah", "free": True,
        })

    # Meaningful pool — ordered by relevance to low-scoring categories
    generic_pool = [
        {
            "title": "Tambahkan angka/metrik ke setiap pencapaian",
            "detail": "Ubah pencapaian generik menjadi konkret dengan angka nyata, misal: 'meningkatkan efisiensi proses 30%' atau 'mengelola tim 5 engineer dalam 2 sprint'.",
            "impact": "+8%", "category": "experience", "effort": "rendah",
            "_priority": 10 if has_low_semantic else 5,
        },
        {
            "title": "Perkuat professional summary",
            "detail": (
                f"Tulis 2-3 kalimat pembuka yang langsung menyebutkan posisi"
                f"{' ' + job_title if job_title else ' yang dilamar'}, level seniority, dan satu pencapaian terbesar yang relevan."
            ),
            "impact": "+5%", "category": "format", "effort": "sedang",
            "_priority": 9 if has_low_quality else 4,
        },
        {
            "title": "Sesuaikan keyword ATS dengan job description",
            "detail": (
                f"Tambahkan kata kunci teknis dari job description ke bagian Skills dan ringkasan CV"
                f"{(': ' + missing_str) if missing_str else ''}. "
                "Rekruter dan sistem ATS memindai kata kunci ini secara eksplisit."
            ),
            "impact": "+6%", "category": "skill", "effort": "rendah",
            "_priority": 10 if has_low_keyword else 6,
        },
        {
            "title": "Tambahkan proyek portofolio relevan",
            "detail": (
                f"Sertakan 2-3 proyek yang paling relevan{' dengan posisi ' + job_title if job_title else ''},"
                " lengkap dengan tech stack yang dipakai dan hasil terukur (misal: 'akurasi model 92%', '10k DAU')."
            ),
            "impact": "+4%", "category": "portfolio", "effort": "sedang",
            "_priority": 10 if has_low_portfolio else 3,
        },
        {
            "title": "Format ulang pengalaman kerja dengan pola STAR",
            "detail": "Susun ulang setiap bullet poin pengalaman dengan format: Situasi singkat → Tindakan yang kamu ambil → Hasil konkret. Hindari bullet pasif seperti 'bertanggung jawab atas...'.",
            "impact": "+4%", "category": "experience", "effort": "sedang",
            "_priority": 8 if has_low_semantic else 4,
        },
        {
            "title": "Susun ulang urutan skill sesuai prioritas loker",
            "detail": (
                f"Pindahkan skill teknis paling relevan ke posisi pertama di bagian Skills"
                f"{' untuk posisi ' + job_title if job_title else ''}. "
                "Rekruter membaca CV dalam 6-10 detik — letakkan yang paling relevan di atas."
            ),
            "impact": "+3%", "category": "skill", "effort": "rendah",
            "_priority": 7 if has_low_keyword else 3,
        },
        {
            "title": "Perbarui profil LinkedIn & GitHub di header",
            "detail": "Pastikan URL LinkedIn (aktif, up-to-date) dan GitHub (berisi proyek publik) tercantum di header CV. Rekruter hampir selalu memverifikasi profil online.",
            "impact": "+3%", "category": "format", "effort": "rendah",
            "_priority": 5,
        },
    ]

    # Sort generic_pool by priority descending, then add to fallback
    generic_pool_sorted = sorted(generic_pool, key=lambda x: x.pop("_priority", 0), reverse=True)
    existing_titles = {f.get("title") for f in fallback}
    for g in generic_pool_sorted:
        if len(fallback) >= 6:
            break
        if g["title"] in existing_titles:
            continue
        fallback.append({
            "rank": len(fallback) + 1,
            "free": len(fallback) < 3,
            **g,
        })
        existing_titles.add(g["title"])

    return {"suggestions": fallback, "total_count": len(fallback)}


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

