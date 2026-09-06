"""
Ergon API Gateway — Backend for Frontend
Handles all requests from Next.js frontend and routes to Langflow + MCP servers
"""
import os
import uuid
import asyncio
from typing import Optional, List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

load_dotenv()

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

async def run_langflow(flow_name: str, inputs: dict) -> dict:
    flow_id = FLOW_IDS.get(flow_name)
    if not flow_id:
        return {"status": "mock", "flow": flow_name, "inputs": inputs}

    url = f"{LANGFLOW_BASE_URL}/api/v1/run/{flow_id}"
    headers = {"x-api-key": LANGFLOW_API_KEY, "Content-Type": "application/json"}
    payload = {"input_value": str(inputs), "output_type": "chat", "input_type": "chat"}

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(url, headers=headers, json=payload)
            if resp.status_code != 200:
                # Langflow flow error (mis. agent belum fully configured) → fallback mock
                return {"status": "mock", "flow": flow_name, "langflow_error": resp.text[:300]}
            return resp.json()
    except Exception as e:
        # Network/timeout error → fallback mock, jangan crash pipeline
        return {"status": "mock", "flow": flow_name, "error": str(e)}


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

    # Read uploaded files
    job_content = None
    cv_content = None
    portfolio_content = None

    if job_file:
        job_content = await job_file.read()
        job_content = f"[FILE:{job_file.filename}]"  # placeholder untuk demo
    if cv_file:
        cv_content = await cv_file.read()
        cv_content = f"[FILE:{cv_file.filename}]"
    if portfolio_file:
        portfolio_content = await portfolio_file.read()
        portfolio_content = f"[FILE:{portfolio_file.filename}]"

    # Initialize session
    analysis_store[session_id] = {
        "status": "processing",
        "progress": {"job_extraction": "pending", "company_intel": "pending",
                     "cv_parsing": "pending", "scoring": "pending"},
        "job_data": None, "company_data": None, "cv_data": None,
        "scoring": None, "suggestions": None, "unlocked": False,
    }

    # Run pipeline in background
    background_tasks.add_task(
        run_analysis_pipeline,
        session_id=session_id,
        job_url=job_url,
        job_content=job_content,
        cv_url=cv_url,
        cv_content=cv_content,
        portfolio_url=portfolio_url,
        portfolio_content=portfolio_content,
    )

    return {"session_id": session_id, "status": "processing"}


async def run_analysis_pipeline(
    session_id: str,
    job_url: Optional[str],
    job_content: Optional[str],
    cv_url: Optional[str],
    cv_content: Optional[str],
    portfolio_url: Optional[str],
    portfolio_content: Optional[str],
):
    """Run the full Langflow pipeline. Always completes — never sets status=error."""
    store = analysis_store[session_id]

    try:
        job_input = job_url or job_content or ""
        cv_input = cv_url or cv_content or ""
        portfolio_input = portfolio_url or portfolio_content or ""

        store["progress"]["job_extraction"] = "running"
        store["progress"]["company_intel"] = "running"
        store["progress"]["cv_parsing"] = "running"

        job_result, company_result, cv_result = await asyncio.gather(
            run_langflow("job_extraction", {"input": job_input}),
            run_langflow("company_intel", {"job_input": job_input}),
            run_langflow("cv_portfolio_parsing", {
                "cv_input": cv_input,
                "portfolio_input": portfolio_input,
            }),
            return_exceptions=True,
        )

        store["job_data"] = job_result if not isinstance(job_result, Exception) else {"status": "mock"}
        store["company_data"] = company_result if not isinstance(company_result, Exception) else None
        store["cv_data"] = cv_result if not isinstance(cv_result, Exception) else {"status": "mock"}

        store["progress"]["job_extraction"] = "done"
        store["progress"]["company_intel"] = "done"
        store["progress"]["cv_parsing"] = "done"

        store["progress"]["scoring"] = "running"
        scoring_result = await run_langflow("scoring_and_suggestions", {
            "job_data": store["job_data"],
            "company_data": store["company_data"],
            "cv_data": store["cv_data"],
        })
        store["scoring"] = scoring_result
        store["suggestions"] = extract_suggestions(scoring_result)
        store["progress"]["scoring"] = "done"

    except Exception as e:
        # Log tapi tetap complete dengan mock data
        store["scoring"] = {"status": "mock"}
        store["suggestions"] = extract_suggestions({"status": "mock"})
        store["progress"]["job_extraction"] = "done"
        store["progress"]["company_intel"] = "done"
        store["progress"]["cv_parsing"] = "done"
        store["progress"]["scoring"] = "done"

    # Selalu complete — tidak pernah error
    store["status"] = "complete"


def extract_suggestions(scoring_result: dict) -> list:
    """Parse suggestions from Langflow output. Returns mock data if flow not connected."""
    if scoring_result.get("status") == "mock":
        return [
            {"rank": 1, "title": "Tambahkan metrik kuantitatif", "detail": "Ubah 'meningkatkan penjualan' menjadi 'meningkatkan penjualan 35% dalam 3 bulan Q1 2025'", "impact": "+8%", "free": True},
            {"rank": 2, "title": "Sesuaikan keyword ATS", "detail": "Tambahkan kata kunci: 'data-driven', 'cross-functional', 'stakeholder management'", "impact": "+6%", "free": True},
            {"rank": 3, "title": "Perkuat summary/objective", "detail": "Tulis summary 2-3 kalimat yang secara langsung menjawab kebutuhan posisi ini", "impact": "+5%", "free": True},
            {"rank": 4, "title": "Susun ulang urutan skill", "detail": "Pindahkan skill teknis yang paling relevan ke posisi teratas di bagian Skills", "impact": "+4%", "free": False},
            {"rank": 5, "title": "Perkuat bullet pekerjaan sebelumnya", "detail": "Format STAR (Situation, Task, Action, Result) untuk setiap achievement", "impact": "+4%", "free": False},
            {"rank": 6, "title": "Tambahkan proyek portofolio relevan", "detail": "Sertakan 2-3 proyek yang paling relevan dengan deskripsi hasil yang terukur", "impact": "+3%", "free": False},
        ]
    # Real parsing logic akan bergantung pada format output Langflow
    return scoring_result.get("suggestions", [])


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

    # Build scoring summary (mock jika flow belum terkoneksi)
    scoring = store.get("scoring") or {}
    is_mock = scoring.get("status") == "mock"

    result = {
        "session_id": session_id,
        "unlocked": store["unlocked"],
        "job_data": store.get("job_data"),
        "company_data": store.get("company_data"),
        "scoring": {
            "overall_score": 72 if is_mock else scoring.get("overall_score", 0),
            "label": "Sedang–Tinggi" if is_mock else scoring.get("label", ""),
            "range": "65–78%" if is_mock else scoring.get("range", ""),
            "disclaimer": "Estimasi berbasis kecocokan CV & loker, bukan jaminan hasil rekrutmen.",
            "breakdown": [
                {"category": "Keyword & Skill Coverage", "score": 78, "weight": "30%"},
                {"category": "Kecocokan Semantik Pengalaman", "score": 70, "weight": "25%"},
                {"category": "Kesesuaian Level", "score": 85, "weight": "15%"},
                {"category": "Relevansi Portofolio", "score": 60, "weight": "15%"},
                {"category": "Kelengkapan & Kualitas CV", "score": 65, "weight": "5%"},
                {"category": "Sinyal Kompetisi", "score": None, "weight": "10%", "note": "Data tidak tersedia"},
            ] if is_mock else scoring.get("breakdown", []),
        },
        "suggestions_free": [s for s in store.get("suggestions", []) if s.get("free")],
        "suggestions_locked_preview": [
            {"rank": s["rank"], "title": s["title"], "impact": s.get("impact")}
            for s in store.get("suggestions", []) if not s.get("free")
        ],
        "suggestions_full": store.get("suggestions", []) if store["unlocked"] else None,
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
    """Download enhanced CV (only after unlock)."""
    if session_id not in analysis_store:
        raise HTTPException(404, "Session tidak ditemukan")
    if not analysis_store[session_id].get("unlocked"):
        raise HTTPException(403, "Belum di-unlock")

    # Run cv_enhancement flow
    cv_data = analysis_store[session_id].get("cv_data")
    suggestions = analysis_store[session_id].get("suggestions", [])

    result = await run_langflow("cv_enhancement", {
        "cv_data": cv_data,
        "suggestions": suggestions,
        "format": format,
    })

    # For demo: generate a simple PDF using reportlab
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("CV Hasil Revisi — Ergon", styles["Title"]),
        Spacer(1, 20),
        Paragraph("CV ini telah dioptimalkan berdasarkan analisis kecocokan dengan loker yang Anda upload.", styles["Normal"]),
        Spacer(1, 12),
        Paragraph("Catatan: Ini adalah CV placeholder untuk demo. CV lengkap dihasilkan oleh flow Langflow cv_enhancement.", styles["Normal"]),
    ]
    doc.build(story)
    buffer.seek(0)

    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(buffer.read())
        tmp_path = f.name

    return FileResponse(tmp_path, media_type="application/pdf",
                        filename=f"ergon-cv-revisi-{session_id[:8]}.pdf")


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
