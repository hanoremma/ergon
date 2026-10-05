# Ergon — AI CV-Fit Scorer & Enhancer

> Tahu dulu seberapa cocok CV-mu sebelum kirim lamaran. Ergon membaca loker dan CV-mu, menghitung skor kecocokan per kategori, dan memberikan saran perbaikan yang konkret — bukan template generik.

Dibangun untuk IBM Hackathon menggunakan IBM Langflow, OpenAI-compatible LLM endpoint, FastMCP, FastAPI, dan Next.js.

---

## Arsitektur

```
Browser (Next.js :3000)
    │
    ▼ POST /api/analyze  (multipart: job_url / job_file + cv_file)
Backend FastAPI (:8000)
    ├── job-scraper-mcp     (:8001)  ← ekstraksi loker dari URL / PDF / gambar
    ├── resume-parser-mcp   (:8003)  ← parsing CV dari PDF / DOCX / teks
    ├── scoring-engine-mcp  (:8005)  ← hitung skor + domain relevance LLM + saran
    ├── company-intel-mcp   (:8002)  ← riset perusahaan (via Langflow, opsional)
    ├── portfolio-analyzer-mcp (:8004)
    ├── cv-generator-mcp    (:8006)
    └── payment-mcp         (:8007)  ← Midtrans sandbox

Langflow Desktop (:7860)   ← orchestrator flow opsional (company_intel, dll.)
```

---

## Prasyarat

| Komponen | Versi minimum | Keterangan |
|----------|--------------|------------|
| Python   | 3.10+        | Global (untuk MCP servers) |
| Node.js  | 18+          | Untuk frontend Next.js |
| npm      | 9+           | |
| Langflow Desktop | terbaru | Download dari [langflow.org](https://langflow.org) — opsional, untuk flow company_intel |

---

## 1. Klon & Siapkan Environment

```powershell
# Klon repo
git clone <repo-url>
cd Hackathon
```

### Backend `.env`

```powershell
# Salin template
Copy-Item backend\env.example backend\.env
```

Buka `backend\.env` dan isi nilai berikut:

```env
# ── LLM (OpenAI-compatible endpoint) ─────────────────────────────────────────
# Ganti dengan URL tunnel LLM yang aktif (Cloudflare Tunnel / abc-tunnel, dll.)
OPENAI_COMPATIBLE_BASE_URL=https://<tunnel-url>/v1
OPENAI_COMPATIBLE_API_KEY=sk-xxxxxxxxxxxxxxxx

# Model default per fungsi (opsional, default: gemini/gemini-3.5-flash-lite)
OPENAI_COMPAT_CV_MODEL=gemini/gemini-3.5-flash-lite
OPENAI_COMPAT_SCORING_MODEL=gemini/gemini-3.5-flash-lite
OPENAI_COMPAT_JOB_MODEL=gemini/gemini-3.5-flash-lite

# ── Langflow ──────────────────────────────────────────────────────────────────
LANGFLOW_BASE_URL=http://localhost:7860
LANGFLOW_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx   # Settings → API Keys di Langflow Desktop

# Flow IDs (diisi otomatis oleh create_langflow_flows.py, atau salin dari flow_ids.json)
FLOW_ID_JOB_EXTRACTION=
FLOW_ID_COMPANY_INTEL=
FLOW_ID_CV_PORTFOLIO_PARSING=
FLOW_ID_SCORING_AND_SUGGESTIONS=
FLOW_ID_CV_ENHANCEMENT=
FLOW_ID_INTERVIEW_PRACTICE=

# ── Midtrans (sandbox) ────────────────────────────────────────────────────────
MIDTRANS_SERVER_KEY=Mid-server-xxxxxxxxxxxxxxxxxxxx
MIDTRANS_CLIENT_KEY=Mid-client-xxxxxxxxxxxxxxxxxxxx
MIDTRANS_IS_PRODUCTION=false
UNLOCK_PRICE_IDR=25000

# ── App ───────────────────────────────────────────────────────────────────────
FRONTEND_URL=http://localhost:3000
```

> **Catatan:** `OPENAI_COMPATIBLE_BASE_URL` adalah satu-satunya kunci yang **wajib** diisi agar scoring dan parsing berjalan. Sisanya opsional untuk fitur tertentu.

### Root `.env` (untuk MCP servers)

MCP servers membaca env dari `.env` di root workspace. Salin dari backend:

```powershell
Copy-Item backend\.env .env
```

Lakukan ini setiap kali memperbarui `backend\.env`.

---

## 2. Setup Backend

```powershell
cd backend

# Buat virtual environment
python -m venv venv

# Aktifkan
.\venv\Scripts\Activate.ps1

# Install dependensi
pip install -r requirements.txt
```

---

## 3. Setup MCP Servers

MCP servers menggunakan Python **global** (bukan venv backend):

```powershell
# Dari root workspace (bukan dalam backend/)
pip install fastmcp httpx python-dotenv pydantic beautifulsoup4 lxml `
    PyMuPDF pytesseract Pillow reportlab python-docx requests
```

---

## 4. Setup Frontend

```powershell
cd frontend
npm install
```

---

## Menjalankan Semua Layanan

### Cara Cepat (Recommended)

Buka **3 terminal PowerShell** dari root workspace:

**Terminal 1 — MCP Servers (semua 7 sekaligus):**
```powershell
.\start-mcp-servers.ps1
```
Script ini otomatis membaca `backend\.env`, install dependensi, dan menjalankan semua 7 MCP server di background.

**Terminal 2 — Backend:**
```powershell
# Muat env vars ke sesi ini
$envContent = Get-Content backend\.env
foreach ($line in $envContent) {
    if ($line -match "^([^#=\s][^=]*?)=(.*)$") {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), ($matches[2].Trim() -replace '^"(.*)"$','$1'), "Process")
    }
}

# Jalankan backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level warning
```

**Terminal 3 — Frontend:**
```powershell
cd frontend
npm run dev
```

**Terminal 4 (opsional) — Langflow Desktop:**

Buka aplikasi Langflow Desktop, pastikan berjalan di port `7860`.

---

### Verifikasi Semua Layanan Berjalan

```powershell
# Cek port yang aktif
netstat -ano | Select-String "800[0-9].*LISTEN"

# Health check backend
(Invoke-WebRequest "http://localhost:8000/api/health" -UseBasicParsing).Content
# Output: {"status":"ok","service":"ergon-api-gateway"}

# Cek frontend
# Buka browser: http://localhost:3000
```

Port yang harus aktif:

| Port | Layanan |
|------|---------|
| 3000 | Frontend (Next.js) |
| 7860 | Langflow Desktop (opsional) |
| 8000 | Backend (FastAPI) |
| 8001 | job-scraper-mcp |
| 8002 | company-intel-mcp |
| 8003 | resume-parser-mcp |
| 8004 | portfolio-analyzer-mcp |
| 8005 | scoring-engine-mcp |
| 8006 | cv-generator-mcp |
| 8007 | payment-mcp |

---

### Cara Manual (per layanan)

Kalau ingin jalankan MCP servers satu per satu di terminal terpisah:

```powershell
# Muat env dulu di setiap terminal baru
$envContent = Get-Content .env
foreach ($line in $envContent) {
    if ($line -match "^([^#=\s][^=]*?)=(.*)$") {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), ($matches[2].Trim() -replace '^"(.*)"$','$1'), "Process")
    }
}

# Kemudian jalankan server yang diinginkan:
python mcp-servers/job-scraper-mcp/server.py        # :8001
python mcp-servers/company-intel-mcp/server.py      # :8002
python mcp-servers/resume-parser-mcp/server.py      # :8003
python mcp-servers/portfolio-analyzer-mcp/server.py # :8004
python mcp-servers/scoring-engine-mcp/server.py     # :8005
python mcp-servers/cv-generator-mcp/server.py       # :8006
python mcp-servers/payment-mcp/server.py            # :8007
```

> ⚠️ **Penting:** Env vars `OPENAI_COMPATIBLE_BASE_URL` dan `OPENAI_COMPATIBLE_API_KEY` **harus** sudah di-set di sesi PowerShell yang sama sebelum menjalankan MCP server. `load_dotenv(override=True)` di setiap server akan membaca dari `.env` di root workspace dan menimpa nilai lama.

---

## Mematikan Semua Layanan

```powershell
# Hentikan semua proses python (MCP servers)
Stop-Process -Name python -ErrorAction SilentlyContinue

# Hentikan backend (jika berjalan di background)
$pid8000 = (netstat -ano | Select-String "8000.*LISTEN" | ForEach-Object { ($_ -split "\s+")[-1] }) | Select-Object -First 1
if ($pid8000) { Stop-Process -Id $pid8000 -Force }
```

---

## Test Analisis End-to-End

```powershell
# Muat env
$envContent = Get-Content backend\.env
foreach ($line in $envContent) {
    if ($line -match "^([^#=\s][^=]*?)=(.*)$") {
        [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), ($matches[2].Trim() -replace '^"(.*)"$','$1'), "Process")
    }
}

# Submit analisis (tanpa CV — hanya job URL)
$r = Invoke-WebRequest "http://localhost:8000/api/analyze" -Method POST `
    -ContentType "application/x-www-form-urlencoded" `
    -Body "job_url=https://glints.com/id/jobs/ai-engineer-test-unique" -UseBasicParsing
$sid = ($r.Content | ConvertFrom-Json).session_id
Write-Host "Session: $sid"

# Tunggu ~45 detik lalu ambil hasil
Start-Sleep -Seconds 45
(Invoke-WebRequest "http://localhost:8000/api/analyze/$sid/result" -UseBasicParsing).Content `
    | ConvertFrom-Json | Select-Object -ExpandProperty scoring
```

---

## Langflow Flows (Opsional)

6 flow tersimpan di Langflow Desktop. Untuk setup dari awal (buat flows + daftarkan MCP servers sekaligus):

```powershell
python setup_langflow.py
```

Script ini akan:
1. Membuat 6 flow Ergon di Langflow (skip jika sudah ada)
2. Mendaftarkan 7 MCP servers
3. Menulis Flow IDs ke `backend\.env` dan snapshot ke `flow_ids.json`

Atau manual: Langflow Desktop → **Settings → MCP Servers → Add** dengan URL berikut:

| Server | URL |
|--------|-----|
| job-scraper-mcp | `http://localhost:8001/mcp` |
| company-intel-mcp | `http://localhost:8002/mcp` |
| resume-parser-mcp | `http://localhost:8003/mcp` |
| portfolio-analyzer-mcp | `http://localhost:8004/mcp` |
| scoring-engine-mcp | `http://localhost:8005/mcp` |
| cv-generator-mcp | `http://localhost:8006/mcp` |
| payment-mcp | `http://localhost:8007/mcp` |

---

## Struktur Direktori

```
Hackathon/
├── backend/
│   ├── main.py              # FastAPI gateway — pipeline utama
│   ├── requirements.txt
│   ├── env.example          # Template environment variables
│   └── venv/                # Virtual environment (tidak di-commit)
├── frontend/
│   └── app/
│       ├── page.tsx          # Landing page
│       ├── upload/           # Form upload loker + CV
│       ├── result/[sessionId]/ # Dashboard skor & saran
│       └── unlock/[sessionId]/ # Paywall Midtrans
├── mcp-servers/
│   ├── job-scraper-mcp/     # Ekstraksi loker (:8001)
│   ├── company-intel-mcp/   # Riset perusahaan (:8002)
│   ├── resume-parser-mcp/   # Parsing CV (:8003)
│   ├── portfolio-analyzer-mcp/ # Analisis portofolio (:8004)
│   ├── scoring-engine-mcp/  # Scoring + domain relevance + saran (:8005)
│   ├── cv-generator-mcp/    # Generate CV revisi (:8006)
│   └── payment-mcp/         # Midtrans payment (:8007)
├── .env                     # Root env (sinkron dengan backend/.env)
├── start-mcp-servers.ps1    # Script starter semua MCP servers
├── setup_langflow.py        # Buat flows + daftarkan MCP servers ke Langflow
├── update_env.py            # Update base URL / API key di .env
└── flow_ids.json            # Flow IDs (di-generate oleh setup_langflow.py)
```

---

## Halaman Frontend

| URL | Halaman |
|-----|---------|
| `/` | Landing page |
| `/upload` | Form upload loker + CV + portofolio |
| `/result/[sessionId]` | Dashboard: skor, breakdown kategori, saran (3 gratis / terkunci) |
| `/unlock/[sessionId]` | Paywall — bayar Rp 25.000 via Midtrans untuk buka semua saran |
| `/unlock/confirm` | Handler redirect setelah payment Midtrans |

---

## MCP Server Tools

### job-scraper-mcp (:8001)
- `extract_job_from_url(url)` — scrape loker dari Glints/Jobstreet/LinkedIn
- `extract_job_from_pdf(pdf_base64, filename)` — ekstrak dari PDF job description
- `extract_job_from_image(image_base64, filename)` — OCR dari screenshot loker

### resume-parser-mcp (:8003)
- `parse_cv_from_pdf(pdf_base64, filename)` — parse CV dari PDF
- `parse_cv_from_url(url)` — parse CV dari Google Docs / URL
- `parse_cv_from_text(raw_text)` — parse dari teks yang di-paste

### scoring-engine-mcp (:8005)
- `calculate_match_score(job_data, cv_data, ...)` — hitung skor komposit (keyword overlap + domain LLM + seniority + kualitas CV)
- `generate_suggestions(job_data, cv_data, scoring_result, ...)` — generate 6 saran perbaikan via LLM

### company-intel-mcp (:8002)
- `research_company(company_name, position)` — riset kontekstual perusahaan

### payment-mcp (:8007)
- Wrapper Midtrans Snap untuk transaksi unlock Rp 25.000

---

## Mengganti Base URL LLM (OpenAI-Compatible Endpoint)

LLM endpoint yang digunakan Ergon berjalan di balik **tunnel sementara** (misalnya Cloudflare Tunnel, ngrok, atau sejenisnya). URL tunnel ini akan **expired** secara berkala dan perlu diperbarui.

Tandanya endpoint sudah expired: error `getaddrinfo failed`, `Connection refused`, `ERR_NAME_NOT_RESOLVED`, atau semua skor keluar `0` / analisis tidak selesai.

### Cara Cepat — Pakai `update_env.py`

```powershell
python update_env.py --base-url https://<tunnel-baru>.trycloudflare.com/v1
```

Script ini otomatis update `backend\.env` **dan** sinkronisasi ke root `.env`.

Untuk lihat nilai yang tersimpan saat ini:

```powershell
python update_env.py --show
```

Setelah update, restart layanan:

```powershell
Stop-Process -Name python -ErrorAction SilentlyContinue
.\start-mcp-servers.ps1
# Restart backend di Terminal 2 (Ctrl+C → jalankan ulang uvicorn)
```

### Cara Manual

**1.** Update `OPENAI_COMPATIBLE_BASE_URL` di `backend\.env`

**2.** Sinkronisasi ke root `.env`:
```powershell
Copy-Item backend\.env .env
```

**3.** Restart MCP servers dan backend.

---

## Troubleshooting

**MCP server tidak terhubung / LLM error `getaddrinfo failed`**

URL tunnel LLM sudah expired. Ikuti panduan **Mengganti Base URL LLM** di atas.

**Skor selalu sama untuk semua loker**

Pastikan `resume-parser-mcp` (:8003) berjalan dan dapat menjangkau LLM endpoint. Tanpa CV data, semua loker akan mendapat skor yang sama. Dengan CV di-upload, scoring engine menggunakan domain relevance LLM untuk membedakan skor.

**`status: mock` di job_data**

Job scraping dari Glints/Jobstreet sering di-blokir (HTTP 403). Ini normal — pipeline fallback ke LLM domain relevance menggunakan nama posisi dari URL slug. Upload job description sebagai PDF untuk hasil terbaik.

**Backend crash saat start**

Pastikan virtual environment sudah diaktifkan dan semua dependensi di `requirements.txt` sudah terinstall:
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Port sudah dipakai**

```powershell
# Cari dan kill proses di port tertentu (contoh: 8000)
$pid_ = (netstat -ano | Select-String "8000.*LISTEN" | ForEach-Object { ($_ -split "\s+")[-1] }) | Select-Object -First 1
Stop-Process -Id $pid_ -Force
```
