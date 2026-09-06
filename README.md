# Ergon — AI CV-Fit Scorer & Enhancer

> Dibangun dengan IBM Bob (dev agent), IBM Langflow (orchestrator), IBM watsonx.ai / Granite (LLM), dan MCP (integrasi).

## Arsitektur

```
Frontend (Next.js :3000)
  └─► API Gateway (FastAPI :8000)
        └─► Langflow Orchestrator (:7860) [via REST API]
              └─► 7 MCP Servers (:8001–8007) [via MCP protocol]
                    └─► IBM watsonx.ai (LLM + Embedding)
```

## Cara Jalankan

### 1. Backend API Gateway
```powershell
cd backend
pip install -r requirements.txt
# Copy env.example ke .env dan isi nilai-nilainya
uvicorn main:app --reload --port 8000
```

### 2. MCP Servers (semua 7 sekaligus)
```powershell
# Install deps tiap server
pip install fastmcp httpx python-dotenv beautifulsoup4 PyMuPDF pytesseract Pillow reportlab python-docx

# Jalankan tiap server (buka terminal terpisah atau pakai script)
.\start-mcp-servers.ps1
```

Atau jalankan manual satu per satu:
```powershell
# Terminal 1
$env:JOB_SCRAPER_MCP_PORT=8001; python mcp-servers/job-scraper-mcp/server.py

# Terminal 2
$env:COMPANY_INTEL_MCP_PORT=8002; python mcp-servers/company-intel-mcp/server.py

# Terminal 3
$env:RESUME_PARSER_MCP_PORT=8003; python mcp-servers/resume-parser-mcp/server.py

# Terminal 4
$env:PORTFOLIO_ANALYZER_MCP_PORT=8004; python mcp-servers/portfolio-analyzer-mcp/server.py

# Terminal 5
$env:SCORING_ENGINE_MCP_PORT=8005; python mcp-servers/scoring-engine-mcp/server.py

# Terminal 6
$env:CV_GENERATOR_MCP_PORT=8006; python mcp-servers/cv-generator-mcp/server.py

# Terminal 7
$env:PAYMENT_MCP_PORT=8007; python mcp-servers/payment-mcp/server.py
```

### 3. Frontend
```powershell
cd frontend
npm install
npm run dev     # development di :3000
# atau
npm run build && npm run start  # production
```

### 4. Langflow Flows (sudah dibuat otomatis)
6 flow sudah dibuat di Langflow via script `create_langflow_flows.py`:
- `job_extraction` (id: d5c0538f-...)
- `company_intel` (id: 84185523-...)
- `cv_portfolio_parsing` (id: f3cebfa7-...)
- `scoring_and_suggestions` (id: 2c3ab612-...)
- `cv_enhancement` (id: e8c8de4b-...)
- `interview_practice` (id: 99256bdb-...) ← Coming Soon

Untuk rebuild flows:
```powershell
$env:PYTHONIOENCODING="utf-8"
$env:LANGFLOW_API_KEY="sk-ZXzWNdZqieHFGRTHN_AplG5JHVybs6umO0hYvlpZN5s"
python create_langflow_flows.py
```

### 5. Register MCP Servers di Langflow
Buka Langflow → Settings → MCP Servers → tambahkan:
| Server | URL |
|--------|-----|
| job-scraper-mcp | http://localhost:8001/mcp |
| company-intel-mcp | http://localhost:8002/mcp |
| resume-parser-mcp | http://localhost:8003/mcp |
| portfolio-analyzer-mcp | http://localhost:8004/mcp |
| scoring-engine-mcp | http://localhost:8005/mcp |
| cv-generator-mcp | http://localhost:8006/mcp |
| payment-mcp | http://localhost:8007/mcp |

## Halaman Frontend

| Halaman | URL | Deskripsi |
|---------|-----|-----------|
| Landing | `/` | Halaman utama, reuse design ergon-landing.html |
| Upload | `/upload` | Form upload loker + CV + portofolio |
| Result | `/result/[sessionId]` | Dashboard skor, breakdown, saran (gratis/terkunci) |
| Unlock | `/unlock/[sessionId]` | Paywall + Midtrans payment |
| Confirm | `/unlock/confirm` | Redirect handler setelah Midtrans callback |

## MCP Servers & Tools

### job-scraper-mcp (:8001)
- `extract_job_from_url(url)` — scrape loker dari URL
- `extract_job_from_pdf(pdf_base64, filename)` — ekstrak dari PDF
- `extract_job_from_image(image_base64, filename)` — OCR dari gambar

### company-intel-mcp (:8002)
- `research_company(company_name, position)` — riset perusahaan
- `get_interview_context(company_name, position, company_research)` — konteks wawancara

### resume-parser-mcp (:8003)
- `parse_cv_from_pdf(pdf_base64, filename)` — parse CV dari PDF
- `parse_cv_from_url(url)` — parse CV dari URL (Google Docs, dll)
- `parse_cv_from_text(raw_text)` — parse CV dari teks

### portfolio-analyzer-mcp (:8004)
- `analyze_github_portfolio(github_url, job_requirements)` — analisis GitHub
- `analyze_portfolio_url(portfolio_url, job_requirements)` — analisis URL portofolio
- `analyze_portfolio_file(file_base64, filename, job_requirements)` — analisis file

### scoring-engine-mcp (:8005)
- `calculate_match_score(job_data, cv_data, portfolio_data, company_data)` — hitung skor
- `generate_suggestions(job_data, cv_data, scoring_result, portfolio_data)` — generate saran
- `get_embedding_similarity(text_a, text_b)` — semantic similarity via watsonx

### cv-generator-mcp (:8006)
- `enhance_cv(cv_data, suggestions, job_data, selected_suggestions)` — revisi CV
- `export_cv_pdf(enhanced_cv, job_data)` — export ke PDF
- `export_cv_docx(enhanced_cv, job_data)` — export ke DOCX

### payment-mcp (:8007)
- `create_payment_transaction(order_id, session_id, amount, ...)` — buat transaksi Midtrans
- `verify_payment_status(order_id)` — cek status pembayaran
- `process_webhook(notification_payload)` — proses Midtrans webhook

## Langflow Flows

| Flow | Deskripsi | Status |
|------|-----------|--------|
| job_extraction | Ekstraksi data loker dari URL/PDF/gambar | ✅ Aktif |
| company_intel | Riset kontekstual perusahaan | ✅ Aktif |
| cv_portfolio_parsing | Parse CV & portofolio | ✅ Aktif |
| scoring_and_suggestions | Scoring + 6 saran perbaikan | ✅ Aktif |
| cv_enhancement | Revisi CV + export PDF/DOCX | ✅ Aktif (berbayar) |
| interview_practice | Latihan wawancara AI | 🔜 Scaffolded, Coming Soon |

## Environment Variables (backend/env.example)

```
LANGFLOW_BASE_URL=http://localhost:7860
LANGFLOW_API_KEY=...
WATSONX_API_KEY=...
WATSONX_PROJECT_ID=...
MIDTRANS_SERVER_KEY=Mid-server-...
MIDTRANS_CLIENT_KEY=Mid-client-...
MIDTRANS_IS_PRODUCTION=false
UNLOCK_PRICE_IDR=25000
FLOW_ID_JOB_EXTRACTION=d5c0538f-...
FLOW_ID_COMPANY_INTEL=84185523-...
FLOW_ID_CV_PORTFOLIO_PARSING=f3cebfa7-...
FLOW_ID_SCORING_AND_SUGGESTIONS=2c3ab612-...
FLOW_ID_CV_ENHANCEMENT=e8c8de4b-...
FLOW_ID_INTERVIEW_PRACTICE=99256bdb-...
```

## Design System

Design tokens dari `ergon-landing.html`, konsisten di semua halaman:
- **Font:** Space Grotesk (heading) + Inter (body)
- **Warna:** `#E7E3FC` (bg-hero), `#FBFAFF` (bg-page), `#5B4FE5` (accent)
- **Paywall:** panel terbuka (putih, dashed border) vs panel berbayar (dark/ink)
- **Coming Soon:** border putus-putus, badge "Segera hadir", non-interaktif
