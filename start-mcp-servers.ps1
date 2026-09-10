#!/usr/bin/env pwsh
# start-mcp-servers.ps1
# Install deps sekali, lalu jalankan semua 7 MCP server di background

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Ergon MCP Servers ===" -ForegroundColor Cyan
Write-Host ""

# ── 1. Install semua deps sekali ─────────────────────────────────────────────
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install fastmcp httpx python-dotenv pydantic beautifulsoup4 lxml `
    PyMuPDF pytesseract Pillow reportlab python-docx requests `
    -q --disable-pip-version-check

Write-Host "  Dependencies installed." -ForegroundColor Green
Write-Host ""

# ── 2. Set env vars dari env.example ─────────────────────────────────────────
$envFile = Join-Path $root "backend\.env"
if (-not (Test-Path $envFile)) { $envFile = Join-Path $root "backend\env.example" }
if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $key   = $matches[1].Trim()
            $value = $matches[2].Trim()
            if (-not [System.Environment]::GetEnvironmentVariable($key)) {
                [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }
    Write-Host "Environment variables loaded from env.example" -ForegroundColor DarkGray
}

# ── 3. Jalankan tiap server ───────────────────────────────────────────────────
$servers = @(
    @{ name = "job-scraper-mcp";        script = "mcp-servers\job-scraper-mcp\server.py";        port = 8001 },
    @{ name = "company-intel-mcp";      script = "mcp-servers\company-intel-mcp\server.py";      port = 8002 },
    @{ name = "resume-parser-mcp";      script = "mcp-servers\resume-parser-mcp\server.py";      port = 8003 },
    @{ name = "portfolio-analyzer-mcp"; script = "mcp-servers\portfolio-analyzer-mcp\server.py"; port = 8004 },
    @{ name = "scoring-engine-mcp";     script = "mcp-servers\scoring-engine-mcp\server.py";     port = 8005 },
    @{ name = "cv-generator-mcp";       script = "mcp-servers\cv-generator-mcp\server.py";       port = 8006 },
    @{ name = "payment-mcp";            script = "mcp-servers\payment-mcp\server.py";            port = 8007 }
)

$logDir = Join-Path $root "logs"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }

foreach ($s in $servers) {
    $scriptPath = Join-Path $root $s.script
    $logFile    = Join-Path $logDir "$($s.name).log"

    $proc = Start-Process -FilePath "python" -ArgumentList "`"$scriptPath`"" `
                -WindowStyle Hidden -PassThru

    Write-Host "  Started $($s.name)  ->  http://localhost:$($s.port)/mcp  (PID $($proc.Id))" -ForegroundColor Green
}

Write-Host ""
Write-Host "All 7 MCP servers started." -ForegroundColor Cyan
Write-Host "Logs: $logDir\" -ForegroundColor DarkGray
Write-Host ""
Write-Host "To stop all: Stop-Process -Name python -ErrorAction SilentlyContinue"
