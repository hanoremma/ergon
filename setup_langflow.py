"""
setup_langflow.py
=================
One-shot setup script untuk Ergon di Langflow Desktop.

Yang dilakukan:
  1. Cek koneksi ke Langflow
  2. Buat 6 flow Ergon (skip jika sudah ada)
  3. Daftarkan 7 MCP servers ke Langflow
  4. Tulis Flow IDs ke backend/.env

Usage:
    python setup_langflow.py

Requirements:
    pip install httpx python-dotenv
"""

import json
import os
import sys
import httpx
from dotenv import dotenv_values

# ─── Config ───────────────────────────────────────────────────────────────────

ENV_FILE   = "backend/.env"
FLOW_IDS_FILE = "flow_ids.json"   # backup snapshot

env = dotenv_values(ENV_FILE)
LANGFLOW_BASE = env.get("LANGFLOW_BASE_URL", "http://localhost:7860").rstrip("/")
API_KEY       = env.get("LANGFLOW_API_KEY", "")

HEADERS = {
    "Content-Type": "application/json",
    **({"x-api-key": API_KEY} if API_KEY else {}),
}

# MCP servers: name → port
MCP_SERVERS = {
    "job-scraper-mcp":        8001,
    "company-intel-mcp":      8002,
    "resume-parser-mcp":      8003,
    "portfolio-analyzer-mcp": 8004,
    "scoring-engine-mcp":     8005,
    "cv-generator-mcp":       8006,
    "payment-mcp":            8007,
}

# Flow name → env key yang akan ditulis ke backend/.env
FLOW_ENV_KEYS = {
    "Ergon — Job Extraction":           "FLOW_ID_JOB_EXTRACTION",
    "Ergon — Company Intel":            "FLOW_ID_COMPANY_INTEL",
    "Ergon — CV & Portfolio Parsing":   "FLOW_ID_CV_PORTFOLIO_PARSING",
    "Ergon — Scoring & Suggestions":    "FLOW_ID_SCORING_AND_SUGGESTIONS",
    "Ergon — CV Enhancement":           "FLOW_ID_CV_ENHANCEMENT",
    "Ergon — Interview Practice":       "FLOW_ID_INTERVIEW_PRACTICE",
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def log(msg: str) -> None:
    print(msg, flush=True)


def check_connection(client: httpx.Client) -> bool:
    """Verifikasi Langflow bisa dijangkau dan API key valid."""
    try:
        r = client.get(f"{LANGFLOW_BASE}/api/v1/flows", timeout=10)
        if r.status_code == 401:
            log("✗ API key tidak valid. Set LANGFLOW_API_KEY di backend/.env")
            return False
        if r.status_code == 200:
            log(f"✓ Terhubung ke Langflow ({LANGFLOW_BASE})")
            return True
        log(f"✗ Unexpected status {r.status_code} dari Langflow")
        return False
    except httpx.ConnectError:
        log(f"✗ Tidak bisa terhubung ke {LANGFLOW_BASE} — pastikan Langflow Desktop berjalan")
        return False


def get_existing_flows(client: httpx.Client) -> dict[str, str]:
    """Return mapping {name: id} untuk flow yang sudah ada."""
    r = client.get(f"{LANGFLOW_BASE}/api/v1/flows", timeout=10)
    r.raise_for_status()
    return {f["name"]: f["id"] for f in r.json()}


# ─── Flow Definitions ─────────────────────────────────────────────────────────

def _agent_node(node_id: str, display_name: str, system_prompt: str,
                mcp_server_name: str, x: int = 200, y: int = 200) -> dict:
    """Helper untuk membuat Agent node yang terhubung ke satu MCP server."""
    return {
        "id": node_id,
        "type": "genericNode",
        "position": {"x": x, "y": y},
        "data": {
            "id": node_id,
            "type": "Agent",
            "node": {
                "display_name": display_name,
                "description": "",
                "template": {
                    "system_prompt": {
                        "value": system_prompt,
                        "type": "str",
                    },
                    "openai_compatible_base_url": {
                        "value": env.get("OPENAI_COMPATIBLE_BASE_URL", ""),
                        "type": "str",
                    },
                    "api_key": {
                        "value": env.get("OPENAI_COMPATIBLE_API_KEY", ""),
                        "type": "str",
                        "password": True,
                    },
                    "model_name": {
                        "value": "gemini/gemini-3.5-flash-lite",
                        "type": "str",
                    },
                    "mcp_servers": {
                        "value": [mcp_server_name],
                        "type": "list",
                    },
                },
            },
        },
    }


def _chat_input_node(node_id: str = "chat_input", x: int = -200, y: int = 200) -> dict:
    return {
        "id": node_id,
        "type": "genericNode",
        "position": {"x": x, "y": y},
        "data": {
            "id": node_id,
            "type": "ChatInput",
            "node": {
                "display_name": "Chat Input",
                "template": {"input_value": {"value": "", "type": "str"}},
            },
        },
    }


def _chat_output_node(node_id: str = "chat_output", x: int = 600, y: int = 200) -> dict:
    return {
        "id": node_id,
        "type": "genericNode",
        "position": {"x": x, "y": y},
        "data": {
            "id": node_id,
            "type": "ChatOutput",
            "node": {
                "display_name": "Chat Output",
                "template": {"input_value": {"value": "", "type": "str"}},
            },
        },
    }


def _edge(src_id: str, tgt_id: str,
          src_handle: str = "message", tgt_handle: str = "input_value") -> dict:
    return {
        "source": src_id,
        "target": tgt_id,
        "data": {
            "sourceHandle": {"id": src_id, "name": src_handle, "output_types": ["Message"]},
            "targetHandle": {"id": tgt_id, "name": tgt_handle, "input_types": ["Message"]},
        },
    }


def build_flows() -> list[dict]:
    """Return list of flow payloads siap di-POST ke Langflow."""

    flows = []

    # ── 1. Job Extraction ─────────────────────────────────────────────────────
    agent = _agent_node(
        "agent_job", "Job Extractor",
        "Kamu adalah spesialis ekstraksi data lowongan kerja. Gunakan tool yang tersedia "
        "untuk mengekstrak informasi terstruktur dari URL, PDF, atau teks lowongan.",
        "job-scraper-mcp", x=200, y=200,
    )
    flows.append({
        "name": "Ergon — Job Extraction",
        "description": "Ekstrak data lowongan dari URL / PDF / gambar via job-scraper-mcp",
        "data": {
            "nodes": [_chat_input_node(), agent, _chat_output_node()],
            "edges": [
                _edge("chat_input", "agent_job"),
                _edge("agent_job", "chat_output"),
            ],
        },
    })

    # ── 2. Company Intel ──────────────────────────────────────────────────────
    agent = _agent_node(
        "agent_company", "Company Intel Agent",
        "Kamu adalah analis bisnis. Gunakan tool yang tersedia untuk meneliti perusahaan "
        "dan memberikan konteks relevan bagi pencari kerja.",
        "company-intel-mcp", x=200, y=200,
    )
    flows.append({
        "name": "Ergon — Company Intel",
        "description": "Riset kontekstual perusahaan via company-intel-mcp",
        "data": {
            "nodes": [_chat_input_node(), agent, _chat_output_node()],
            "edges": [
                _edge("chat_input", "agent_company"),
                _edge("agent_company", "chat_output"),
            ],
        },
    })

    # ── 3. CV & Portfolio Parsing ─────────────────────────────────────────────
    agent = _agent_node(
        "agent_cv", "CV Parser Agent",
        "Kamu adalah spesialis parsing CV dan portofolio. Gunakan tool yang tersedia "
        "untuk mengekstrak data terstruktur dari dokumen CV dan portofolio.",
        "resume-parser-mcp", x=200, y=200,
    )
    flows.append({
        "name": "Ergon — CV & Portfolio Parsing",
        "description": "Parse CV dan portofolio via resume-parser-mcp",
        "data": {
            "nodes": [_chat_input_node(), agent, _chat_output_node()],
            "edges": [
                _edge("chat_input", "agent_cv"),
                _edge("agent_cv", "chat_output"),
            ],
        },
    })

    # ── 4. Scoring & Suggestions ──────────────────────────────────────────────
    agent = _agent_node(
        "agent_scoring", "Scoring Agent",
        "Kamu adalah evaluator kecocokan CV-loker. Hitung skor komposit dan berikan saran "
        "perbaikan yang konkret dan actionable menggunakan tool yang tersedia.",
        "scoring-engine-mcp", x=200, y=200,
    )
    flows.append({
        "name": "Ergon — Scoring & Suggestions",
        "description": "Hitung skor kecocokan CV-loker dan generate saran via scoring-engine-mcp",
        "data": {
            "nodes": [_chat_input_node(), agent, _chat_output_node()],
            "edges": [
                _edge("chat_input", "agent_scoring"),
                _edge("agent_scoring", "chat_output"),
            ],
        },
    })

    # ── 5. CV Enhancement ─────────────────────────────────────────────────────
    agent = _agent_node(
        "agent_cvgen", "CV Enhancement Agent",
        "Kamu adalah penulis CV profesional. Gunakan tool yang tersedia untuk membuat "
        "revisi CV yang dioptimalkan untuk loker target, dalam format PDF.",
        "cv-generator-mcp", x=200, y=200,
    )
    flows.append({
        "name": "Ergon — CV Enhancement",
        "description": "Generate revisi CV yang dioptimalkan via cv-generator-mcp",
        "data": {
            "nodes": [_chat_input_node(), agent, _chat_output_node()],
            "edges": [
                _edge("chat_input", "agent_cvgen"),
                _edge("agent_cvgen", "chat_output"),
            ],
        },
    })

    # ── 6. Interview Practice ─────────────────────────────────────────────────
    agent = _agent_node(
        "agent_interview", "Interview Coach",
        "Kamu adalah interview coach berpengalaman. Berikan pertanyaan interview yang "
        "relevan dengan posisi dan CV kandidat, lalu evaluasi jawaban mereka.",
        "scoring-engine-mcp", x=200, y=200,
    )
    flows.append({
        "name": "Ergon — Interview Practice",
        "description": "Simulasi dan evaluasi interview berbasis CV + loker",
        "data": {
            "nodes": [_chat_input_node(), agent, _chat_output_node()],
            "edges": [
                _edge("chat_input", "agent_interview"),
                _edge("agent_interview", "chat_output"),
            ],
        },
    })

    return flows


# ─── Create Flows ─────────────────────────────────────────────────────────────

def create_flows(client: httpx.Client) -> dict[str, str]:
    """Buat semua flow. Skip jika sudah ada. Return mapping {flow_name: flow_id}."""
    existing = get_existing_flows(client)
    flow_ids: dict[str, str] = {}

    for flow_def in build_flows():
        name = flow_def["name"]
        if name in existing:
            fid = existing[name]
            log(f"  ↩  '{name}' sudah ada — skip (id: {fid[:8]}…)")
            flow_ids[name] = fid
            continue

        r = client.post(
            f"{LANGFLOW_BASE}/api/v1/flows",
            json=flow_def,
            timeout=30,
        )
        if r.status_code in (200, 201):
            fid = r.json()["id"]
            flow_ids[name] = fid
            log(f"  ✓  '{name}' dibuat (id: {fid[:8]}…)")
        else:
            log(f"  ✗  Gagal buat '{name}': {r.status_code} — {r.text[:120]}")

    return flow_ids


# ─── Register MCP Servers ─────────────────────────────────────────────────────

def register_mcp_servers(client: httpx.Client) -> None:
    """Daftarkan semua MCP server ke Langflow via v2 API."""
    for name, port in MCP_SERVERS.items():
        url = f"http://localhost:{port}/mcp"
        # Coba v2 dulu, fallback ke v1
        for api_path in (f"/api/v2/mcp/servers/{name}", f"/api/v1/mcp/servers/{name}"):
            r = client.post(
                f"{LANGFLOW_BASE}{api_path}",
                json={"url": url},
                timeout=10,
            )
            if r.status_code in (200, 201):
                log(f"  ✓  {name} → {url}")
                break
            if r.status_code == 404:
                continue  # coba path berikutnya
            log(f"  ✗  {name}: {r.status_code} — {r.text[:100]}")
            break
        else:
            log(f"  ✗  {name}: endpoint MCP tidak ditemukan di Langflow ini")


# ─── Write Flow IDs to .env ───────────────────────────────────────────────────

def write_flow_ids_to_env(flow_ids: dict[str, str]) -> None:
    """Tulis / update FLOW_ID_* di backend/.env dan simpan snapshot ke flow_ids.json."""
    if not os.path.exists(ENV_FILE):
        log(f"⚠  {ENV_FILE} tidak ditemukan — lewati penulisan env")
        return

    with open(ENV_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Bangun map env_key → flow_id berdasarkan nama flow
    updates: dict[str, str] = {}
    for flow_name, env_key in FLOW_ENV_KEYS.items():
        if flow_name in flow_ids:
            updates[env_key] = flow_ids[flow_name]

    # Update baris yang sudah ada
    updated_keys: set[str] = set()
    new_lines = []
    for line in lines:
        key = line.split("=")[0].strip()
        if key in updates:
            new_lines.append(f"{key}={updates[key]}\n")
            updated_keys.add(key)
        else:
            new_lines.append(line)

    # Tambahkan key yang belum ada
    for key, val in updates.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={val}\n")

    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    log(f"\n✓ Flow IDs ditulis ke {ENV_FILE}")

    # Snapshot JSON
    snapshot = {FLOW_ENV_KEYS[n]: fid for n, fid in flow_ids.items() if n in FLOW_ENV_KEYS}
    with open(FLOW_IDS_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
    log(f"✓ Snapshot disimpan ke {FLOW_IDS_FILE}")


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    if not API_KEY:
        log("⚠  LANGFLOW_API_KEY tidak di-set di backend/.env — mencoba tanpa auth")

    with httpx.Client(headers=HEADERS) as client:
        # 1. Cek koneksi
        if not check_connection(client):
            sys.exit(1)

        # 2. Buat flows
        log("\n── Membuat Flows ────────────────────────────────────────")
        flow_ids = create_flows(client)

        # 3. Daftarkan MCP servers
        log("\n── Registrasi MCP Servers ───────────────────────────────")
        register_mcp_servers(client)

        # 4. Tulis IDs ke .env
        log("\n── Menulis Flow IDs ke .env ─────────────────────────────")
        write_flow_ids_to_env(flow_ids)

    log("\n✓ Setup selesai.")
    log("  Jalankan ulang: Copy-Item backend\\.env .env  (untuk sinkronisasi root .env)")


if __name__ == "__main__":
    main()
