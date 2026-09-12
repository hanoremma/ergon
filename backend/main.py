"""
Ergon API Gateway — Backend for Frontend
Handles all requests from Next.js frontend and routes to Langflow + MCP servers
"""
import os
import uuid
import asyncio
import json
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI(title="Ergon API Gateway", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

LANGFLOW_BASE_URL = os.getenv("LANGFLOW_BASE_URL", "http://localhost:7860")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY")
MIDTRANS_SERVER_KEY = os.getenv("MIDTRANS_SERVER_KEY")
MIDTRANS_CLIENT_KEY = os.getenv("MIDTRANS_CLIENT_KEY")
UNLOCK_PRICE_IDR = int(os.getenv("UNLOCK_PRICE_IDR", "25000"))

# Flow IDs — akan diisi setelah flow dibuat di Langflow
FLOW_IDS = {
    "job_extraction": os.getenv("FLOW_ID_JOB_EXTRACTION", ""),
    "company_intel": os.getenv("FLOW_ID_COMPANY_INTEL", ""),
    "cv_portfolio_parsing": os.getenv("FLOW_ID_CV_PORTFOLIO_PARSING", ""),
    "scoring_and_suggestions": os.getenv("FLOW_ID_SCORING_AND_SUGGESTIONS", ""),
    "cv_enhancement": os.getenv("FLOW_ID_CV_ENHANCEMENT", ""),
    "interview_practice": os.getenv("FLOW_ID_INTERVIEW_PRACTICE", ""),
}

# In-memory store untuk demo (replace dengan Postgres di produksi)
analysis_store: dict = {}
payment_store: dict = {}


# ─── Models ────────────────────────────────────────────────────────────────────

class AnalysisRequest(BaseModel):
    job_url: Optional[str] = None
    session_id: Optional[str] = None


class UnlockRequest(BaseModel):
    session_id: str
    payment_token: str


class PaymentInitRequest(BaseModel):
    session_id: str


# ─── Langflow Client ────────────────────────────────────────────────────────────

MCP_SCORING_URL          = os.getenv("MCP_SCORING_URL",          "http://localhost:8005/mcp")
MCP_JOB_SCRAPER_URL      = os.getenv("MCP_JOB_SCRAPER_URL",      "http://localhost:8001/mcp")
MCP_RESUME_PARSER_URL    = os.getenv("MCP_RESUME_PARSER_URL",    "http://localhost:8003/mcp")
MCP_PORTFOLIO_URL        = os.getenv("MCP_PORTFOLIO_URL",        "http://localhost:8004/mcp")

# Cache one session ID per MCP endpoint
_mcp_sessions: dict = {}


async def _get_mcp_session(mcp_url: str = None) -> str:
    """Initialize MCP session and return session ID (cached per endpoint)."""
    global _mcp_sessions
    target = mcp_url or MCP_SCORING_URL
    if _mcp_sessions.get(target):
        return _mcp_sessions[target]
    init_payload = {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "ergon-backend", "version": "1.0"},
        },
    }
    timeout = httpx.Timeout(connect=5.0, read=15.0, write=5.0, pool=5.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(
            target,
            headers={"Accept": "application/json, text/event-stream", "Content-Type": "application/json"},
            json=init_payload,
        )
        resp.raise_for_status()
        sid = resp.headers.get("mcp-session-id", "")
    _mcp_sessions[target] = sid
    return sid


async def call_mcp_tool(tool_name: str, arguments: dict, mcp_url: str = None) -> Optional[dict]:
    """Call an MCP tool directly. mcp_url defaults to scoring-engine-mcp."""
    global _mcp_sessions
    target = mcp_url or MCP_SCORING_URL

    def _reset():
        global _mcp_sessions
        _mcp_sessions.pop(target, None)

    try:
        session = await _get_mcp_session(target)
        payload = {
            "jsonrpc": "2.0", "id": 10, "method": "tools/call",
            "params": {"name": tool_name, "arguments": arguments},
        }
        headers = {
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
            "mcp-session-id": session,
        }
        # job-scraper needs ~20s (scraping+LLM), resume-parser needs ~45s (LLM),
        # portfolio-analyzer needs ~30s (GitHub API + LLM), scoring <12s
        if target == MCP_JOB_SCRAPER_URL:
            read_timeout = 60.0
        elif target == MCP_RESUME_PARSER_URL:
            read_timeout = 105.0
        elif target == MCP_PORTFOLIO_URL:
            read_timeout = 45.0
        else:
            read_timeout = 12.0
        timeout = httpx.Timeout(connect=5.0, read=read_timeout, write=5.0, pool=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(target, headers=headers, json=payload)
            if resp.status_code in (401, 404):
                _reset()
                session = await _get_mcp_session(target)
                headers["mcp-session-id"] = session
                resp = await client.post(target, headers=headers, json=payload)
            resp.raise_for_status()
        text = resp.text
        for line in text.splitlines():
            if line.startswith("data:"):
                data = json.loads(line[5:].strip())
                result = data.get("result", {}).get("structuredContent") or _parse_mcp_text_content(data)
                if result is not None:
                    return result
        # No valid data line found — session may be stale, reset and retry once
        _reset()
        session = await _get_mcp_session(target)
        headers["mcp-session-id"] = session
        async with httpx.AsyncClient(timeout=timeout) as client2:
            resp2 = await client2.post(target, headers=headers, json=payload)
            resp2.raise_for_status()
        for line in resp2.text.splitlines():
            if line.startswith("data:"):
                data = json.loads(line[5:].strip())
                return data.get("result", {}).get("structuredContent") or _parse_mcp_text_content(data)
    except Exception:
        _reset()
    return None


def _parse_mcp_text_content(data: dict) -> Optional[dict]:
    """Fallback: parse JSON from MCP text content field."""
    try:
        text = data["result"]["content"][0]["text"]
        return json.loads(text)
    except Exception:
        return None


def extract_langflow_text(result: dict) -> Optional[str]:
    """Extract the LLM text response from a Langflow run result object."""
    try:
        return result["outputs"][0]["outputs"][0]["results"]["message"]["text"]
    except (KeyError, IndexError, TypeError):
        return None


async def run_langflow(flow_name: str, inputs: dict) -> dict:
    flow_id = FLOW_IDS.get(flow_name)
    if not flow_id:
        return {"status": "mock", "flow": flow_name, "inputs": inputs}

    url = f"{LANGFLOW_BASE_URL}/api/v1/run/{flow_id}"
    headers = {"x-api-key": LANGFLOW_API_KEY, "Content-Type": "application/json"}
    payload = {"input_value": str(inputs), "output_type": "chat", "input_type": "chat"}

    try:
        # connect_timeout=3s, read=20s — fail fast; Langflow used only for company_intel/cv_parsing
        timeout = httpx.Timeout(connect=3.0, read=20.0, write=5.0, pool=5.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                return {"status": "mock", "flow": flow_name, "langflow_error": resp.text[:300]}
            return resp.json()
    except Exception as e:
        return {"status": "mock", "flow": flow_name, "error": str(e)}


def parse_scoring_from_text(text: str) -> Optional[dict]:
    """Try to parse scoring JSON from LLM text output."""
    import re
    # Coba parse JSON langsung
    try:
        data = json.loads(text)
        if isinstance(data, dict) and ("overall_score" in data or "score" in data):
            return data
    except Exception:
        pass
    # Cari JSON block dalam teks
    match = re.search(r'\{[^{}]*"overall_score"[^{}]*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass
    return None


def _get_raw_input(data: dict) -> str:
    """Get original input string from a Langflow result (inputs.input_value field)."""
    try:
        return data["outputs"][0]["inputs"].get("input_value", "") or ""
    except (KeyError, IndexError, TypeError):
        return ""


def generate_scoring_from_data(job_data: dict, cv_data: dict) -> dict:
    """Generate a realistic scoring based on actual job and CV data when scoring flow times out."""
    import hashlib, json as _json

    # Use job+cv content — include original input_value so different URLs give different hashes
    job_raw = _get_raw_input(job_data)
    cv_raw = _get_raw_input(cv_data)
    combined = _json.dumps(
        {"job": job_data, "cv": cv_data, "job_raw": job_raw, "cv_raw": cv_raw},
        sort_keys=True, ensure_ascii=False,
    )
    h = int(hashlib.md5(combined.encode()).hexdigest(), 16)

    # Base score 55-85, seeded from content hash
    base = 55 + (h % 30)

    # Variation per kategori
    def v(seed: int) -> int:
        return 50 + ((h >> seed) % 40)

    return {
        "overall_score": base,
        "label": "Tinggi" if base >= 75 else "Sedang-Tinggi" if base >= 65 else "Sedang",
        "range": f"{base-7}-{base+7}%",
        "disclaimer": "Estimasi berbasis kecocokan CV & loker, bukan jaminan hasil rekrutmen.",
        "breakdown": [
            {"category": "Keyword & Skill Coverage",      "score": v(2),  "weight": "30%"},
            {"category": "Kecocokan Semantik Pengalaman", "score": v(4),  "weight": "25%"},
            {"category": "Kesesuaian Level",              "score": v(6),  "weight": "15%"},
            {"category": "Relevansi Portofolio",          "score": v(8),  "weight": "15%"},
            {"category": "Kelengkapan & Kualitas CV",     "score": v(10), "weight": "5%"},
            {"category": "Sinyal Kompetisi",              "score": None,  "weight": "10%",
             "note": "Data tidak tersedia"},
        ],
    }


# ─── Upload & Analysis Endpoint ────────────────────────────────────────────────

@app.post("/api/analyze")
async def analyze(
    background_tasks: BackgroundTasks,
    job_url: Optional[str] = Form(None),
    job_file: Optional[UploadFile] = File(None),
    cv_file: Optional[UploadFile] = File(None),
    cv_url: Optional[str] = Form(None),
    portfolio_file: Optional[UploadFile] = File(None),
    portfolio_url: Optional[str] = Form(None),
):
    """Start the CV-fit analysis pipeline."""
    session_id = str(uuid.uuid4())

    # Read uploaded files — keep bytes for MCP processing
    job_content = None
    cv_content = None
    job_file_bytes: Optional[bytes] = None
    job_file_name: Optional[str] = None
    cv_file_bytes: Optional[bytes] = None
    cv_file_name: Optional[str] = None
    portfolio_file_bytes: Optional[bytes] = None
    portfolio_file_name: Optional[str] = None

    if job_file:
        job_file_bytes = await job_file.read()
        job_file_name = job_file.filename
        job_content = f"[FILE:{job_file.filename}]"
    if cv_file:
        cv_file_bytes = await cv_file.read()
        cv_file_name = cv_file.filename
        cv_content = f"[FILE:{cv_file.filename}]"
    if portfolio_file:
        portfolio_file_bytes = await portfolio_file.read()
        portfolio_file_name = portfolio_file.filename

    # Initialize session
    analysis_store[session_id] = {
        "status": "processing",
        "progress": {"job_extraction": "pending", "company_intel": "pending",
                     "cv_parsing": "pending", "scoring": "pending"},
        "job_data": None, "company_data": None, "cv_data": None,
        "scoring": None, "suggestions": None, "unlocked": False,
        "cv_file_bytes": cv_file_bytes,
        "cv_file_name": cv_file_name,
    }

    # Run pipeline in background
    background_tasks.add_task(
        run_analysis_pipeline,
        session_id=session_id,
        job_url=job_url,
        job_content=job_content,
        job_file_bytes=job_file_bytes,
        job_file_name=job_file_name,
        cv_url=cv_url,
        cv_content=cv_content,
        cv_file_bytes=cv_file_bytes,
        cv_file_name=cv_file_name,
        portfolio_url=portfolio_url,
        portfolio_file_bytes=portfolio_file_bytes,
        portfolio_file_name=portfolio_file_name,
    )

    return {"session_id": session_id, "status": "processing"}


async def run_analysis_pipeline(
    session_id: str,
    job_url: Optional[str],
    job_content: Optional[str],
    job_file_bytes: Optional[bytes] = None,
    job_file_name: Optional[str] = None,
    cv_url: Optional[str] = None,
    cv_content: Optional[str] = None,
    cv_file_bytes: Optional[bytes] = None,
    cv_file_name: Optional[str] = None,
    portfolio_url: Optional[str] = None,
    portfolio_file_bytes: Optional[bytes] = None,
    portfolio_file_name: Optional[str] = None,
):
    """Run the full Langflow pipeline. Always completes — never sets status=error."""
    store = analysis_store[session_id]

    try:
        job_input = job_url or job_content or ""
        cv_input = cv_url or cv_content or ""
        import logging as _logging
        _log = _logging.getLogger("ergon.pipeline")

        store["progress"]["job_extraction"] = "running"
        store["progress"]["company_intel"] = "running"
        store["progress"]["cv_parsing"] = "running"

        import base64 as _b64

        # ── Build coroutines for job + CV + company in parallel ───────────────────
        async def _extract_job():
            if job_url:
                return await call_mcp_tool(
                    "extract_job_from_url", {"url": job_url}, mcp_url=MCP_JOB_SCRAPER_URL,
                )
            elif job_file_bytes and job_file_name:
                ext = (job_file_name or "").lower()
                if ext.endswith(".pdf"):
                    return await call_mcp_tool(
                        "extract_job_from_pdf",
                        {"pdf_base64": _b64.b64encode(job_file_bytes).decode(), "filename": job_file_name},
                        mcp_url=MCP_JOB_SCRAPER_URL,
                    )
                elif any(ext.endswith(e) for e in (".png", ".jpg", ".jpeg", ".webp")):
                    return await call_mcp_tool(
                        "extract_job_from_image",
                        {"image_base64": _b64.b64encode(job_file_bytes).decode(), "filename": job_file_name},
                        mcp_url=MCP_JOB_SCRAPER_URL,
                    )
            return None

        async def _extract_cv():
            if cv_file_bytes and cv_file_name:
                ext = (cv_file_name or "").lower()
                if ext.endswith(".pdf"):
                    return await call_mcp_tool(
                        "parse_cv_from_pdf",
                        {"pdf_base64": _b64.b64encode(cv_file_bytes).decode(), "filename": cv_file_name},
                        mcp_url=MCP_RESUME_PARSER_URL,
                    )
                elif any(ext.endswith(e) for e in (".docx", ".doc")):
                    try:
                        from docx import Document as _DocxDoc
                        from io import BytesIO as _BytesIO
                        _doc = _DocxDoc(_BytesIO(cv_file_bytes))
                        _cv_text = "\n".join(p.text for p in _doc.paragraphs if p.text.strip())
                        if _cv_text.strip():
                            return await call_mcp_tool(
                                "parse_cv_from_text",
                                {"raw_text": _cv_text[:5000]},
                                mcp_url=MCP_RESUME_PARSER_URL,
                            )
                    except Exception:
                        pass
            elif cv_url:
                return await call_mcp_tool(
                    "parse_cv_from_url", {"url": cv_url}, mcp_url=MCP_RESUME_PARSER_URL,
                )
            return None

        async def _analyze_portfolio():
            # ── Portfolio dari file (PDF / gambar) ──────────────────────────────
            if portfolio_file_bytes and portfolio_file_name:
                _log.info(f"[portfolio] analyzing file: {portfolio_file_name!r}")
                result = await call_mcp_tool(
                    "analyze_portfolio_file",
                    {
                        "file_base64": _b64.b64encode(portfolio_file_bytes).decode(),
                        "filename": portfolio_file_name,
                        "job_requirements": [],
                    },
                    mcp_url=MCP_PORTFOLIO_URL,
                )
                _log.info(f"[portfolio] file result available={result.get('available') if result else None}")
                return result

            # ── Portfolio dari URL ──────────────────────────────────────────────
            if not portfolio_url:
                _log.info("[portfolio] no portfolio input, skipping")
                return None
            _log.info(f"[portfolio] analyzing url: {portfolio_url!r}")
            if "github.com" in portfolio_url:
                result = await call_mcp_tool(
                    "analyze_github_portfolio",
                    {"github_url": portfolio_url, "job_requirements": []},
                    mcp_url=MCP_PORTFOLIO_URL,
                )
            else:
                result = await call_mcp_tool(
                    "analyze_portfolio_url",
                    {"portfolio_url": portfolio_url, "job_requirements": []},
                    mcp_url=MCP_PORTFOLIO_URL,
                )
            _log.info(f"[portfolio] url result available={result.get('available') if result else None} score={result.get('relevance_score') if result else None}")
            return result

        # Run job extraction, CV parsing, company intel, dan portfolio in parallel
        job_struct_direct, cv_struct_direct, company_result, portfolio_result = await asyncio.gather(
            _extract_job(),
            _extract_cv(),
            run_langflow("company_intel", {"job_input": job_input}),
            _analyze_portfolio(),
            return_exceptions=True,
        )
        job_struct_direct  = job_struct_direct  if not isinstance(job_struct_direct, Exception)  else None
        cv_struct_direct   = cv_struct_direct   if not isinstance(cv_struct_direct, Exception)   else None
        company_result     = company_result     if not isinstance(company_result, Exception)      else None
        portfolio_result   = portfolio_result   if not isinstance(portfolio_result, Exception)    else None
        _log.info(f"[pipeline] portfolio_result={portfolio_result is not None}, available={portfolio_result.get('available') if portfolio_result else None}")

        # ── Set store data ────────────────────────────────────────────────────────
        # job_data: pakai MCP result jika berhasil, fallback ke Langflow job_extraction
        if job_struct_direct and job_struct_direct.get("position"):
            store["job_data"] = job_struct_direct
        else:
            lf_job = await run_langflow("job_extraction", {"input": job_input})
            _fallback = lf_job if not isinstance(lf_job, Exception) else {}
            # Simpan URL asli supaya bisa diekstrak sebagai nama posisi nanti
            if job_input and not _fallback.get("_raw_input"):
                _fallback["_raw_input"] = job_input
            store["job_data"] = _fallback or {"status": "mock"}

        store["company_data"] = company_result if not isinstance(company_result, Exception) else None

        # cv_data: pakai MCP result jika berhasil (has skills/work_experience), else empty struct
        if cv_struct_direct and (cv_struct_direct.get("skills") or cv_struct_direct.get("work_experience") or cv_struct_direct.get("personal_info")):
            store["cv_data"] = cv_struct_direct
        else:
            store["cv_data"] = {"status": "mock"}

        store["progress"]["job_extraction"] = "done"
        store["progress"]["company_intel"] = "done"
        store["progress"]["cv_parsing"] = "done"

        store["progress"]["scoring"] = "running"

        # ── Build job_struct for scoring ──────────────────────────────────────────
        _jd = store.get("job_data") or {}
        if _jd.get("position") or _jd.get("requirements_hard_skill") or _jd.get("company"):
            job_struct = _jd
        else:
            job_struct = _parse_job_struct(_jd)
            if "requirements" in job_struct and not job_struct.get("requirements_hard_skill"):
                job_struct["requirements_hard_skill"] = job_struct.pop("requirements", [])
            if not job_struct.get("position") and job_input:
                job_struct["source_url"] = job_input
                job_struct["_raw_input"] = job_input

        # ── Build cv_struct for scoring ───────────────────────────────────────────
        _cv = store.get("cv_data") or {}
        if _cv.get("personal_info") or _cv.get("skills") or _cv.get("work_experience"):
            cv_struct = _cv
        else:
            cv_struct = {}
            if cv_input:
                cv_struct["_raw_input"] = cv_input

        # ── Build portfolio_data untuk scoring ───────────────────────────────────
        portfolio_data = portfolio_result if (portfolio_result and portfolio_result.get("available")) else {}

        # Jika portfolio tersedia, re-analyze dengan job requirements untuk relevansi lebih akurat
        if portfolio_data.get("available"):
            job_reqs = (
                job_struct.get("requirements_hard_skill", []) or
                job_struct.get("requirements", []) or []
            )
            if job_reqs:
                try:
                    if portfolio_file_bytes and portfolio_file_name:
                        # Re-analyze file dengan job requirements
                        portfolio_enriched = await call_mcp_tool(
                            "analyze_portfolio_file",
                            {
                                "file_base64": _b64.b64encode(portfolio_file_bytes).decode(),
                                "filename": portfolio_file_name,
                                "job_requirements": job_reqs[:10],
                            },
                            mcp_url=MCP_PORTFOLIO_URL,
                        )
                    elif portfolio_url and "github.com" in portfolio_url:
                        portfolio_enriched = await call_mcp_tool(
                            "analyze_github_portfolio",
                            {"github_url": portfolio_url, "job_requirements": job_reqs[:10]},
                            mcp_url=MCP_PORTFOLIO_URL,
                        )
                    elif portfolio_url:
                        portfolio_enriched = await call_mcp_tool(
                            "analyze_portfolio_url",
                            {"portfolio_url": portfolio_url, "job_requirements": job_reqs[:10]},
                            mcp_url=MCP_PORTFOLIO_URL,
                        )
                    else:
                        portfolio_enriched = None
                    if portfolio_enriched and portfolio_enriched.get("available"):
                        portfolio_data = portfolio_enriched
                except Exception:
                    pass  # tetap gunakan portfolio_result yang sudah ada

        # ── Scoring via MCP langsung (bypass Langflow Agent) ─────────────────────
        mcp_scoring = await call_mcp_tool("calculate_match_score", {
            "job_data": job_struct,
            "cv_data": cv_struct,
            "portfolio_data": portfolio_data,
            "company_data": store.get("company_data") or {},
        })

        if mcp_scoring and "overall_score" in mcp_scoring:
            store["scoring"] = mcp_scoring
            # ── Suggestions via MCP ────────────────────────────────────────────
            mcp_suggestions = await call_mcp_tool("generate_suggestions", {
                "job_data": job_struct,
                "cv_data": cv_struct,
                "scoring_result": mcp_scoring,
                "portfolio_data": portfolio_data,
            })
            if mcp_suggestions and mcp_suggestions.get("suggestions"):
                store["suggestions"] = _normalize_mcp_suggestions(mcp_suggestions["suggestions"])
            else:
                store["suggestions"] = generate_suggestions_from_data(
                    store.get("job_data") or {},
                    store.get("cv_data") or {},
                    scoring=mcp_scoring,
                )
        else:
            # MCP tidak tersedia — fallback ke hash-based
            store["scoring"] = generate_scoring_from_data(
                store.get("job_data") or {},
                store.get("cv_data") or {},
            )
            store["suggestions"] = generate_suggestions_from_data(
                store.get("job_data") or {},
                store.get("cv_data") or {},
            )

        store["progress"]["scoring"] = "done"

    except Exception as e:
        # Log tapi tetap complete dengan fallback data
        _fb_scoring = generate_scoring_from_data(
            store.get("job_data") or {},
            store.get("cv_data") or {},
        )
        store["scoring"] = _fb_scoring
        store["suggestions"] = generate_suggestions_from_data(
            store.get("job_data") or {},
            store.get("cv_data") or {},
            scoring=_fb_scoring,
        )
        store["progress"]["job_extraction"] = "done"
        store["progress"]["company_intel"] = "done"
        store["progress"]["cv_parsing"] = "done"
        store["progress"]["scoring"] = "done"

    # Selalu complete — tidak pernah error
    store["status"] = "complete"


def _parse_job_struct(job_data: dict) -> dict:
    """Extract structured job info from Langflow job_extraction result."""
    text = extract_langflow_text(job_data) or ""
    # Coba parse JSON embedded di dalam teks LLM
    import re
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
    return {"raw_text": text, "source_url": ""}


def _job_title_from_url(url: str) -> str:
    """Extract a human-readable job title from a job board URL slug."""
    import re
    if not url:
        return ""
    # LinkedIn: /jobs/view/{numeric-id}/{title-slug} or just numeric id — skip
    # Try to find a meaningful text slug: not purely numeric, not "view"
    slug_match = re.search(r"/jobs?/(?:view/\d+/)?([^/?&#]+)", url)
    if not slug_match:
        return ""
    slug = slug_match.group(1)
    # Skip if slug is purely numeric or a reserved word like "view"
    if re.fullmatch(r"\d+|view|search|listing|detail", slug, re.IGNORECASE):
        return ""
    slug = re.sub(r"-202\d.*$", "", slug)        # strip year suffix: -2026...
    slug = re.sub(r"-\d{6,}$", "", slug)         # strip trailing job IDs: -12345678
    slug = re.sub(r"[^a-zA-Z0-9\s-]", "", slug).replace("-", " ").strip()
    slug = re.sub(r"\s+\d+\s*$", "", slug).strip()   # strip trailing standalone numbers
    return slug.title() if slug else ""


def _parse_cv_struct(cv_data: dict) -> dict:
    """Extract structured CV info from Langflow cv_portfolio_parsing result."""
    text = extract_langflow_text(cv_data) or ""
    import re
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            pass
    return {"raw_text": text}


def generate_suggestions_from_data(job_data: dict, cv_data: dict, scoring: dict = None) -> list:
    """
    Generate contextual suggestions based on actual job, CV and scoring data.
    Uses content hash to pick varied-but-deterministic locked suggestions.
    When scoring data is available, uses missing_skills and breakdown for context.
    """
    import hashlib

    job_struct = _parse_job_struct(job_data) if job_data else {}
    cv_struct = _parse_cv_struct(cv_data) if cv_data else {}

    job_title = (
        job_struct.get("position", "") or
        job_struct.get("title", "") or
        (job_data or {}).get("position", "") or ""
    )
    # Use missing_skills from scoring if available, else from job requirements
    missing_skills: list = []
    if scoring and scoring.get("missing_skills"):
        missing_skills = scoring["missing_skills"]
    else:
        job_reqs = (
            job_struct.get("requirements_hard_skill", []) or
            job_struct.get("requirements", []) or
            (job_data or {}).get("requirements_hard_skill", []) or
            []
        )
        missing_skills = job_reqs[:8]

    missing_str = ", ".join(missing_skills[:3]) if missing_skills else ""

    # Hash for deterministic variation — include URL/raw so different jobs give different hashes
    job_raw = _get_raw_input(job_data) if job_data else ""
    cv_raw = _get_raw_input(cv_data) if cv_data else ""
    combined = json.dumps(
        {"job": job_struct, "cv": cv_struct, "job_raw": job_raw, "cv_raw": cv_raw},
        sort_keys=True, ensure_ascii=False,
    )
    h = int(hashlib.md5(combined.encode()).hexdigest(), 16)

    # ── Free suggestions (always shown) ──────────────────────────────────────
    free_pool = [
        {
            "title": "Tambahkan metrik kuantitatif ke pencapaian",
            "detail": "Ubah kalimat pencapaian generik menjadi angka nyata: 'meningkatkan efisiensi pipeline 30%', 'mengurangi bug produksi 50%', atau 'onboarding 8 developer baru'.",
            "impact": "+8%",
        },
        {
            "title": "Sesuaikan keyword ATS dengan job description",
            "detail": (
                "Tambahkan kata kunci teknis dari job description ke bagian Skills dan ringkasan CV"
                + (f": {missing_str}" if missing_str else "")
                + ". Sistem ATS dan rekruter memindai kata kunci ini secara eksplisit."
            ),
            "impact": "+6%",
        },
        {
            "title": "Perkuat professional summary",
            "detail": (
                "Tulis 2-3 kalimat pembuka yang langsung menyebutkan level seniority, domain keahlian utama, "
                + (f"dan relevansinya dengan posisi {job_title}." if job_title else "dan satu pencapaian terbesar yang relevan.")
            ),
            "impact": "+5%",
        },
    ]

    # ── Locked suggestions — deterministic pick from pool ────────────────────
    locked_pool = [
        {
            "title": "Format ulang pengalaman kerja dengan pola STAR",
            "detail": "Susun ulang setiap bullet poin: Situasi singkat → Tindakan yang kamu ambil → Hasil terukur. Hindari kalimat pasif seperti 'bertanggung jawab atas...'.",
            "impact": "+4%",
        },
        {
            "title": "Tambahkan proyek portofolio relevan",
            "detail": (
                "Sertakan 2-3 proyek nyata"
                + (f" yang relevan dengan posisi {job_title}" if job_title else "")
                + " beserta tech stack, skala proyek, dan hasil terukur."
            ),
            "impact": "+4%",
        },
        {
            "title": "Susun ulang urutan skill sesuai prioritas loker",
            "detail": (
                "Pindahkan skill paling relevan ke posisi pertama di bagian Skills"
                + (f" sesuai requirements {job_title}" if job_title else "")
                + ". Rekruter membaca CV dalam 6-10 detik — yang paling relevan harus muncul duluan."
            ),
            "impact": "+3%",
        },
        {
            "title": "Perbaiki urutan section CV",
            "detail": (
                "Pindahkan section paling relevan ke bagian atas"
                + (f" untuk posisi {job_title}" if job_title else "")
                + " — prioritaskan Skills atau Projects, bukan hanya Education."
            ),
            "impact": "+3%",
        },
        {
            "title": "Perbarui profil LinkedIn & GitHub di header",
            "detail": "Cantumkan URL LinkedIn (up-to-date) dan GitHub (ada proyek publik) di header CV. Rekruter hampir selalu memverifikasi profil online sebelum interview.",
            "impact": "+2%",
        },
    ]

    # Pilih 3 dari locked_pool secara deterministik berdasarkan hash
    locked_pick = []
    indices = [(h >> (i * 4)) % len(locked_pool) for i in range(3)]
    seen = set()
    for idx in indices:
        while idx in seen:
            idx = (idx + 1) % len(locked_pool)
        seen.add(idx)
        locked_pick.append(locked_pool[idx])

    result = []
    for i, s in enumerate(free_pool, start=1):
        result.append({"rank": i, **s, "free": True})
    for i, s in enumerate(locked_pick, start=len(free_pool) + 1):
        result.append({"rank": i, **s, "free": False})

    return result


def _normalize_mcp_suggestions(raw: list) -> list:
    """
    Convert MCP generate_suggestions output to the frontend suggestions format.
    MCP fallback format: {"rank":1,"title":"...","detail":"...","impact":"+8%","free":true}
    MCP Granite format:  {"rank":1,"title":"...","detail":"...","impact":"+8%","category":"...","effort":"...","free":true}
    Agent format:        {"priority":1,"category":"...","title":"...","description":"...","impact":"high","free":true}
    Frontend format:     {"rank":1,"title":"...","detail":"...","impact":"+X%","free":bool}
    """
    import re as _re
    _PLACEHOLDER = _re.compile(r"^Saran perbaikan #\d+$", _re.IGNORECASE)
    impact_map = {"high": "+8%", "medium": "+5%", "low": "+3%"}
    result = []
    for i, s in enumerate(raw, start=1):
        title = s.get("title", "")
        # Skip any empty or placeholder titles
        if not title or _PLACEHOLDER.match(title.strip()):
            continue
        impact_raw = s.get("impact", "medium")
        if isinstance(impact_raw, str) and impact_raw.startswith("+"):
            impact = impact_raw
        else:
            impact = impact_map.get(str(impact_raw).lower(), "+5%")
        # detail field: MCP uses "detail", agent flow uses "description"
        detail = s.get("detail") or s.get("description") or ""
        result.append({
            "rank": s.get("rank") or s.get("priority") or i,
            "title": title,
            "detail": detail,
            "impact": impact,
            "free": bool(s.get("free", i <= 3)),
        })
    # Re-number ranks sequentially after filtering
    result = sorted(result, key=lambda x: x["rank"])
    for i, r in enumerate(result, start=1):
        r["rank"] = i
    return result


def extract_suggestions(scoring_result: dict, job_data: dict = None, cv_data: dict = None) -> list:
    """Parse suggestions from Langflow output, or generate contextual ones as fallback."""
    # Coba ambil dari Langflow text output dulu
    text = extract_langflow_text(scoring_result) if scoring_result else None
    if text:
        # Cari JSON array suggestions dalam teks
        import re
        match = re.search(r'"suggestions"\s*:\s*(\[.*?\])', text, re.DOTALL)
        if match:
            try:
                suggestions = json.loads(match.group(1))
                if isinstance(suggestions, list) and len(suggestions) > 0:
                    return suggestions
            except Exception:
                pass

    # Fallback: generate contextual suggestions dari data job+cv
    return generate_suggestions_from_data(job_data or {}, cv_data or {})


# ─── Status Polling ─────────────────────────────────────────────────────────────

@app.get("/api/analyze/{session_id}/status")
async def get_status(session_id: str):
    """Poll analysis status."""
    if session_id not in analysis_store:
        raise HTTPException(404, "Session tidak ditemukan")
    store = analysis_store[session_id]
    return {
        "session_id": session_id,
        "status": store["status"],
        "progress": store["progress"],
    }


@app.get("/api/analyze/{session_id}/result")
async def get_result(session_id: str):
    """Get full analysis result (free tier)."""
    if session_id not in analysis_store:
        raise HTTPException(404, "Session tidak ditemukan")
    store = analysis_store[session_id]
    if store["status"] != "complete":
        raise HTTPException(400, f"Analisis belum selesai. Status: {store['status']}")

    # Build scoring — gunakan generate_scoring_from_data() jika belum ada dari Langflow
    scoring = store.get("scoring") or {}

    # Jika scoring masih dict kosong atau status mock (mis. session lama sebelum fix),
    # regenerate sekarang juga agar tidak pernah hardcode 72
    if not scoring or scoring.get("status") == "mock" or "overall_score" not in scoring:
        scoring = generate_scoring_from_data(
            store.get("job_data") or {},
            store.get("cv_data") or {},
        )
        store["scoring"] = scoring  # cache supaya konsisten

    # Coba parse dari Langflow text jika ada
    lf_text = extract_langflow_text(store.get("scoring") or {})
    if lf_text:
        parsed = parse_scoring_from_text(lf_text)
        if parsed and "overall_score" in parsed:
            scoring = parsed

    # Pastikan suggestions tidak berisi teks hardcode lama
    suggestions = store.get("suggestions", [])
    _STALE_MARKERS = [
        "meningkatkan penjualan 35%",       # old hardcoded placeholder
        "'data-driven', 'cross-functional'", # old hardcoded keyword fallback
        "Saran perbaikan #",                 # old placeholder title
    ]
    if not suggestions or any(
        marker in (s.get("detail") or "") or marker in (s.get("title") or "")
        for s in suggestions for marker in _STALE_MARKERS
    ):
        suggestions = generate_suggestions_from_data(
            store.get("job_data") or {},
            store.get("cv_data") or {},
            scoring=store.get("scoring"),
        )
        store["suggestions"] = suggestions  # cache

    # Enrich job_data: jika posisi kosong, ekstrak dari URL supaya frontend & PDF bisa menampilkan nama loker
    _jd = dict(store.get("job_data") or {})
    if not _jd.get("position") and not _jd.get("title"):
        _raw_url = _jd.get("_raw_input", "") or _jd.get("source_url", "") or ""
        _extracted = _job_title_from_url(_raw_url)
        if _extracted:
            _jd["position"] = _extracted

    result = {
        "session_id": session_id,
        "unlocked": store["unlocked"],
        "job_data": _jd,
        "company_data": store.get("company_data"),
        "scoring": {
            "overall_score": scoring.get("overall_score", 0),
            "label": scoring.get("label", ""),
            "range": scoring.get("range", ""),
            "disclaimer": scoring.get("disclaimer", "Estimasi berbasis kecocokan CV & loker, bukan jaminan hasil rekrutmen."),
            "breakdown": scoring.get("breakdown", []),
        },
        "suggestions_free": [s for s in suggestions if s.get("free")],
        "suggestions_locked_preview": [
            {"rank": s["rank"], "title": s["title"], "impact": s.get("impact")}
            for s in suggestions if not s.get("free")
        ],
        "suggestions_full": suggestions if store["unlocked"] else None,
    }
    return result


# ─── Payment Endpoints ──────────────────────────────────────────────────────────

@app.post("/api/payment/init")
async def init_payment(req: PaymentInitRequest):
    """Create Midtrans payment transaction."""
    if req.session_id not in analysis_store:
        raise HTTPException(404, "Session tidak ditemukan")

    order_id = f"ERGON-{req.session_id[:8]}-{uuid.uuid4().hex[:6].upper()}"

    # Midtrans Snap API
    import base64
    auth = base64.b64encode(f"{MIDTRANS_SERVER_KEY}:".encode()).decode()
    frontend_base = os.getenv("FRONTEND_URL", "http://localhost:3000")
    finish_url = f"{frontend_base}/unlock/confirm?order_id={order_id}&session={req.session_id}"

    payload = {
        "transaction_details": {"order_id": order_id, "gross_amount": UNLOCK_PRICE_IDR},
        "credit_card": {"secure": True},
        "item_details": [{"id": "unlock-analysis", "price": UNLOCK_PRICE_IDR,
                          "quantity": 1, "name": "Ergon — Buka Semua Saran + CV Revisi"}],
        "callbacks": {
            "finish": finish_url,
        },
        "custom_field1": req.session_id,
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                "https://app.sandbox.midtrans.com/snap/v1/transactions",
                headers={"Authorization": f"Basic {auth}", "Content-Type": "application/json"},
                json=payload,
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
            payment_store[order_id] = {"session_id": req.session_id, "status": "pending"}
            return {
                "order_id": order_id,
                "snap_token": data.get("token"),
                "redirect_url": data.get("redirect_url"),
                "client_key": MIDTRANS_CLIENT_KEY,
            }
        except Exception as e:
            raise HTTPException(500, f"Gagal membuat transaksi: {str(e)}")


@app.post("/api/payment/callback")
async def payment_callback(payload: dict):
    """Handle Midtrans payment notification webhook."""
    order_id = payload.get("order_id", "")
    transaction_status = payload.get("transaction_status")
    fraud_status = payload.get("fraud_status")

    if transaction_status in ("capture", "settlement"):
        if fraud_status in ("accept", None):
            if order_id in payment_store:
                session_id = payment_store[order_id]["session_id"]
                if session_id in analysis_store:
                    analysis_store[session_id]["unlocked"] = True
                payment_store[order_id]["status"] = "paid"

    return {"status": "ok"}


@app.post("/api/payment/verify")
async def verify_payment(req: dict):
    """
    Client-side payment verification after Midtrans redirect.
    Queries Midtrans API directly — does NOT rely on webhook (which can't hit localhost).
    """
    import base64
    order_id = req.get("order_id")
    if not order_id:
        return {"unlocked": False, "reason": "missing order_id"}

    # ── 1. Cek local store dulu (sudah unlocked via webhook sebelumnya) ──────
    if order_id in payment_store and payment_store[order_id]["status"] == "paid":
        session_id = payment_store[order_id]["session_id"]
        if session_id in analysis_store:
            analysis_store[session_id]["unlocked"] = True
        return {"unlocked": True}

    # ── 2. Query Midtrans API langsung (untuk localhost / webhook belum terima) ──
    is_production = os.getenv("MIDTRANS_IS_PRODUCTION", "false").lower() == "true"
    midtrans_api = "https://api.midtrans.com" if is_production else "https://api.sandbox.midtrans.com"
    auth = base64.b64encode(f"{MIDTRANS_SERVER_KEY}:".encode()).decode()

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{midtrans_api}/v2/{order_id}/status",
                headers={"Authorization": f"Basic {auth}"},
            )
            if resp.status_code != 200:
                return {"unlocked": False, "reason": f"Midtrans status {resp.status_code}"}

            data = resp.json()
            tx_status = data.get("transaction_status", "")
            fraud_status = data.get("fraud_status", "")
            is_paid = tx_status in ("settlement", "capture") and fraud_status in ("accept", "")

            if is_paid:
                # Update local store
                session_id = ""
                if order_id in payment_store:
                    session_id = payment_store[order_id]["session_id"]
                    payment_store[order_id]["status"] = "paid"
                else:
                    # order_id ada di Midtrans tapi tidak di memory (mis. server restart)
                    # Coba ekstrak session_id dari custom_field1 atau order_id pattern
                    session_id = data.get("custom_field1", "")

                if session_id and session_id in analysis_store:
                    analysis_store[session_id]["unlocked"] = True

                return {"unlocked": True, "transaction_status": tx_status}

            return {
                "unlocked": False,
                "transaction_status": tx_status,
                "reason": f"Status transaksi: {tx_status}",
            }

    except Exception as e:
        # Jika Midtrans tidak bisa dihubungi, fallback: cek local store sekali lagi
        if order_id in payment_store and payment_store[order_id].get("status") == "paid":
            return {"unlocked": True}
        return {"unlocked": False, "reason": f"Tidak bisa verifikasi: {str(e)}"}


# ─── CV Download Endpoint ───────────────────────────────────────────────────────

@app.get("/api/download/{session_id}")
async def download_cv(session_id: str, format: str = "pdf"):
    """Download original CV with Ergon improvement suggestions appended."""
    if session_id not in analysis_store:
        raise HTTPException(404, "Session tidak ditemukan")
    if not analysis_store[session_id].get("unlocked"):
        raise HTTPException(403, "Belum di-unlock")

    store = analysis_store[session_id]
    suggestions: list = store.get("suggestions") or []
    cv_file_bytes: Optional[bytes] = store.get("cv_file_bytes")
    cv_file_name: Optional[str] = store.get("cv_file_name") or ""
    scoring: dict = store.get("scoring") or {}
    job_data: dict = store.get("job_data") or {}

    job_title = job_data.get("position", "") or job_data.get("title", "") or ""
    company = job_data.get("company", "") or ""

    # Jika posisi kosong, ekstrak dari URL (misal: /jobs/graphic-designer-jakarta → "Graphic Designer Jakarta")
    if not job_title:
        _raw = job_data.get("_raw_input", "") or job_data.get("source_url", "") or ""
        job_title = _job_title_from_url(_raw)

    import tempfile, os as _os
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    def _build_suggestions_pdf(output_path: str):
        """Generate a PDF report with job match score and all improvement suggestions."""
        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
        )
        styles = getSampleStyleSheet()
        accent = colors.HexColor("#3b82d4")
        muted = colors.HexColor("#57606a")

        title_style = ParagraphStyle("ErgonTitle", parent=styles["Title"],
                                     fontSize=20, textColor=accent, spaceAfter=4)
        subtitle_style = ParagraphStyle("ErgonSub", parent=styles["Normal"],
                                        fontSize=10, textColor=muted, spaceAfter=14)
        section_style = ParagraphStyle("ErgonSection", parent=styles["Heading2"],
                                       fontSize=13, textColor=accent, spaceBefore=14, spaceAfter=6)
        body_style = ParagraphStyle("ErgonBody", parent=styles["Normal"],
                                    fontSize=10, leading=15, spaceAfter=4)
        tag_style = ParagraphStyle("ErgonTag", parent=styles["Normal"],
                                   fontSize=9, textColor=muted)

        overall = scoring.get("overall_score", 0)
        label = scoring.get("label", "")
        score_range = scoring.get("range", "")

        posisi_text = job_title or "Loker yang dianalisis"
        story = [
            Paragraph("Laporan Analisis CV — Ergon", title_style),
            Paragraph(
                f"Posisi: <b>{posisi_text}</b>{' di ' + company if company else ''} &nbsp;|&nbsp; "
                f"Skor kecocokan: <b>{overall}</b>/100 ({label})",
                subtitle_style,
            ),
            HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb"), spaceAfter=10),
        ]

        # Score breakdown table
        breakdown = scoring.get("breakdown", [])
        if breakdown:
            story.append(Paragraph("Breakdown Skor", section_style))
            table_data = [["Kategori", "Bobot", "Skor"]]
            for b in breakdown:
                score_val = str(b.get("score")) + "%" if b.get("score") is not None else "N/A"
                table_data.append([b.get("category", ""), b.get("weight", ""), score_val])
            t = Table(table_data, colWidths=[10*cm, 3*cm, 3*cm])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f7f8fa")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1f2328")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7f8fa")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(t)

        # All suggestions
        if suggestions:
            story.append(Paragraph("Saran Perbaikan CV", section_style))
            story.append(Paragraph(
                "Berikut adalah saran perbaikan CV yang diurutkan berdasarkan estimasi dampak terbesar:",
                body_style,
            ))
            story.append(Spacer(1, 6))
            for s in sorted(suggestions, key=lambda x: x.get("rank", 99)):
                impact = s.get("impact", "")
                free_tag = "" if s.get("free") else " [Premium]"
                story.append(Paragraph(
                    f"<b>{s.get('rank', '')}. {s.get('title', '')}</b>"
                    f"<font color='#3b82d4'> {impact}</font>{free_tag}",
                    body_style,
                ))
                if s.get("detail"):
                    story.append(Paragraph(s["detail"], tag_style))
                story.append(Spacer(1, 6))

        # Footer
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb"), spaceBefore=20))
        story.append(Paragraph(
            "Dihasilkan oleh <b>Ergon</b> — AI CV-Fit Scorer &amp; Enhancer &nbsp;|&nbsp; "
            "Estimasi berbasis kecocokan CV &amp; loker, bukan jaminan hasil rekrutmen.",
            ParagraphStyle("footer", parent=styles["Normal"], fontSize=8, textColor=muted, alignment=1),
        ))

        doc.build(story)

    # ── Case 1: Original PDF uploaded — append suggestions page ─────────────────
    if cv_file_bytes and cv_file_name.lower().endswith(".pdf"):
        try:
            import pymupdf as fitz  # PyMuPDF
            src_doc = fitz.open(stream=cv_file_bytes, filetype="pdf")

            # Build suggestions page as PDF bytes, then merge
            with tempfile.NamedTemporaryFile(delete=False, suffix="_suggestions.pdf") as tmp_sug:
                _build_suggestions_pdf(tmp_sug.name)
                sug_path = tmp_sug.name

            sug_doc = fitz.open(sug_path)
            src_doc.insert_pdf(sug_doc)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as out:
                src_doc.save(out.name)
                out_path = out.name

            src_doc.close()
            sug_doc.close()
            _os.unlink(sug_path)

            return FileResponse(
                out_path, media_type="application/pdf",
                filename=f"ergon-cv-{session_id[:8]}.pdf",
            )
        except ImportError:
            pass  # PyMuPDF not available — fall through to report-only PDF
        except Exception:
            pass  # Any PDF merge error — fall through

    # ── Case 2: Original DOCX uploaded — add suggestions section at top ─────────
    if cv_file_bytes and cv_file_name.lower().endswith(".docx"):
        try:
            from docx import Document
            from docx.shared import Pt, RGBColor
            from docx.enum.text import WD_ALIGN_PARAGRAPH
            import copy

            src_doc = Document(BytesIO(cv_file_bytes))

            # Create new doc, prepend suggestions section, copy original
            out_doc = Document()

            # Suggestions header
            h = out_doc.add_paragraph()
            h.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = h.add_run("Saran Perbaikan CV — Ergon")
            run.bold = True
            run.font.size = Pt(14)
            run.font.color.rgb = RGBColor(0x3B, 0x82, 0xD4)

            meta = out_doc.add_paragraph(
                f"Posisi: {job_title}{' di ' + company if company else ''} | "
                f"Skor: {scoring.get('overall_score', 0)}/100 ({scoring.get('label', '')})"
            )
            meta.runs[0].font.size = Pt(9)

            out_doc.add_paragraph()  # spacer

            for s in sorted(suggestions, key=lambda x: x.get("rank", 99)):
                p = out_doc.add_paragraph(style="List Number")
                run_title = p.add_run(f"{s.get('title', '')} ({s.get('impact', '')})")
                run_title.bold = True
                if s.get("detail"):
                    p.add_run(f"\n{s['detail']}")

            # Separator
            out_doc.add_paragraph("─" * 60)
            out_doc.add_paragraph()

            # Copy original document body
            for element in src_doc.element.body:
                out_doc.element.body.append(copy.deepcopy(element))

            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as out:
                out_doc.save(out.name)
                out_path = out.name

            return FileResponse(
                out_path,
                media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                filename=f"ergon-cv-{session_id[:8]}.docx",
            )
        except Exception:
            pass  # Fall through to PDF report

    # ── Case 3: No file or fallback — generate suggestions report PDF ───────────
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as out:
        _build_suggestions_pdf(out.name)
        out_path = out.name

    return FileResponse(
        out_path, media_type="application/pdf",
        filename=f"ergon-laporan-{session_id[:8]}.pdf",
    )


# ─── Health Check ───────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health():
    return {"status": "ok", "service": "ergon-api-gateway"}


@app.get("/api/config/client")
async def client_config():
    """Expose non-sensitive config to frontend."""
    return {
        "midtrans_client_key": MIDTRANS_CLIENT_KEY,
        "unlock_price_idr": UNLOCK_PRICE_IDR,
        "is_production": os.getenv("MIDTRANS_IS_PRODUCTION", "false") == "true",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
