"""
create_langflow_flows.py
Builds all 6 Ergon flows directly in the running Langflow instance via REST API.
Each flow is defined as a full JSON graph and POSTed to /api/v1/flows/

Usage:
    python create_langflow_flows.py

Requirements:
    pip install httpx python-dotenv
"""
import asyncio
import json
import os
import sys
import httpx

LANGFLOW_BASE_URL = os.getenv("LANGFLOW_BASE_URL", "http://localhost:7860")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "sk-ZXzWNdZqieHFGRTHN_AplG5JHVybs6umO0hYvlpZN5s")
LANGFLOW_PROJECT_ID = os.getenv("LANGFLOW_PROJECT_ID", "38b35903-4c72-42ca-815a-05ea28ee4d9e")

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY", "wJSd7vpF05bjDHxYrwl0SykOn9ViJ2ZHh3oCfKtPZDjd")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID", "ergon-hackathon")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

HEADERS = {
    "x-api-key": LANGFLOW_API_KEY,
    "Content-Type": "application/json",
}

# ─── Helper to build standard node ──────────────────────────────────────────────

def node(node_id: str, node_type: str, display_name: str, x: int, y: int, data: dict = {}) -> dict:
    """Build a Langflow node dict."""
    return {
        "id": node_id,
        "type": "genericNode",
        "position": {"x": x, "y": y},
        "data": {
            "type": node_type,
            "node": {
                "display_name": display_name,
                "description": "",
                **data,
            },
            "id": node_id,
        },
    }


def edge(source: str, target: str, source_handle: str = "text", target_handle: str = "input_value") -> dict:
    """Build a Langflow edge."""
    return {
        "source": source,
        "target": target,
        "id": f"{source}-{target}",
        "sourceHandle": f"{source}|{source_handle}|0",
        "targetHandle": f"{target}|{target_handle}|0",
    }


def watsonx_llm_node(node_id: str, x: int, y: int) -> dict:
    """Build a watsonx.ai / IBM Granite LLM node."""
    return {
        "id": node_id,
        "type": "genericNode",
        "position": {"x": x, "y": y},
        "data": {
            "type": "WatsonxLLM",
            "node": {
                "display_name": "IBM Granite (watsonx.ai)",
                "description": "IBM watsonx.ai Granite model for text generation",
                "template": {
                    "model_id": {
                        "value": "ibm/granite-13b-instruct-v2",
                        "type": "str",
                        "display_name": "Model ID",
                    },
                    "project_id": {
                        "value": WATSONX_PROJECT_ID,
                        "type": "str",
                        "display_name": "Project ID",
                    },
                    "url": {
                        "value": WATSONX_URL,
                        "type": "str",
                        "display_name": "watsonx URL",
                    },
                    "apikey": {
                        "value": WATSONX_API_KEY,
                        "type": "str",
                        "password": True,
                        "display_name": "API Key",
                    },
                    "max_new_tokens": {"value": 1024, "type": "int"},
                    "temperature": {"value": 0.1, "type": "float"},
                },
            },
            "id": node_id,
        },
    }


def mcp_tool_node(node_id: str, server_name: str, tool_name: str, x: int, y: int, mcp_url: str) -> dict:
    """Build an MCP Tool node that connects to one of our MCP servers."""
    return {
        "id": node_id,
        "type": "genericNode",
        "position": {"x": x, "y": y},
        "data": {
            "type": "MCPTool",
            "node": {
                "display_name": f"MCP: {tool_name}",
                "description": f"Tool from {server_name}",
                "template": {
                    "mcp_server_url": {
                        "value": mcp_url,
                        "type": "str",
                        "display_name": "MCP Server URL",
                    },
                    "tool_name": {
                        "value": tool_name,
                        "type": "str",
                        "display_name": "Tool Name",
                    },
                },
            },
            "id": node_id,
        },
    }


def agent_node(node_id: str, display_name: str, system_prompt: str, x: int, y: int) -> dict:
    """Build an Agent node."""
    return {
        "id": node_id,
        "type": "genericNode",
        "position": {"x": x, "y": y},
        "data": {
            "type": "Agent",
            "node": {
                "display_name": display_name,
                "description": system_prompt[:200],
                "template": {
                    "system_prompt": {
                        "value": system_prompt,
                        "type": "str",
                        "display_name": "System Prompt",
                    },
                    "max_iterations": {"value": 5, "type": "int"},
                    "verbose": {"value": True, "type": "bool"},
                },
            },
            "id": node_id,
        },
    }


def chat_input_node(node_id: str, x: int, y: int) -> dict:
    return {
        "id": node_id,
        "type": "genericNode",
        "position": {"x": x, "y": y},
        "data": {
            "type": "ChatInput",
            "node": {
                "display_name": "Input",
                "template": {
                    "input_value": {"value": "", "type": "str", "display_name": "Message"},
                    "sender": {"value": "User", "type": "str"},
                },
            },
            "id": node_id,
        },
    }


def chat_output_node(node_id: str, x: int, y: int) -> dict:
    return {
        "id": node_id,
        "type": "genericNode",
        "position": {"x": x, "y": y},
        "data": {
            "type": "ChatOutput",
            "node": {
                "display_name": "Output",
                "template": {
                    "input_value": {"value": "", "type": "str"},
                    "sender_name": {"value": "Ergon", "type": "str"},
                },
            },
            "id": node_id,
        },
    }


def prompt_node(node_id: str, display_name: str, template: str, x: int, y: int) -> dict:
    return {
        "id": node_id,
        "type": "genericNode",
        "position": {"x": x, "y": y},
        "data": {
            "type": "Prompt",
            "node": {
                "display_name": display_name,
                "template": {
                    "template": {"value": template, "type": "str", "display_name": "Template"},
                },
            },
            "id": node_id,
        },
    }


# ─── Flow Definitions ────────────────────────────────────────────────────────────

def build_job_extraction_flow() -> dict:
    """Flow 1: job_extraction — extracts structured data from job postings."""
    nodes = [
        chat_input_node("input-1", 100, 300),
        mcp_tool_node("mcp-job-url", "job-scraper-mcp", "extract_job_from_url", 400, 100, "http://localhost:8001/mcp"),
        mcp_tool_node("mcp-job-pdf", "job-scraper-mcp", "extract_job_from_pdf", 400, 300, "http://localhost:8001/mcp"),
        mcp_tool_node("mcp-job-img", "job-scraper-mcp", "extract_job_from_image", 400, 500, "http://localhost:8001/mcp"),
        agent_node(
            "agent-job-extractor",
            "Job Extraction Agent",
            """Kamu adalah agen ekstraksi lowongan kerja untuk Ergon.

Tugasmu: menerima input dari pengguna (bisa berupa URL, base64 PDF, atau base64 gambar) dan mengekstrak data lowongan terstruktur.

Cara kerja:
1. Jika input adalah URL (dimulai dengan http), gunakan tool extract_job_from_url
2. Jika input adalah base64 PDF (dimulai dengan JVBERi), gunakan extract_job_from_pdf
3. Jika input adalah base64 gambar, gunakan extract_job_from_image
4. Jika input adalah JSON dengan field "url", "pdf_base64", atau "image_base64", route ke tool yang sesuai

Selalu kembalikan JSON terstruktur dengan semua field yang berhasil diekstrak.
Jika ada field yang tidak ditemukan, isi dengan string kosong — jangan gagalkan seluruh proses.""",
            700, 300,
        ),
        watsonx_llm_node("llm-1", 700, 100),
        chat_output_node("output-1", 1000, 300),
    ]
    edges = [
        edge("input-1", "agent-job-extractor", "message", "input_value"),
        edge("mcp-job-url", "agent-job-extractor", "text", "tools"),
        edge("mcp-job-pdf", "agent-job-extractor", "text", "tools"),
        edge("mcp-job-img", "agent-job-extractor", "text", "tools"),
        edge("llm-1", "agent-job-extractor", "text", "llm"),
        edge("agent-job-extractor", "output-1", "message", "input_value"),
    ]
    return {
        "name": "job_extraction",
        "description": "Ergon Flow 1: Ekstraksi data lowongan kerja dari URL, PDF, atau gambar/screenshot",
        "data": {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.8}},
    }


def build_company_intel_flow() -> dict:
    """Flow 2: company_intel — researches company context."""
    nodes = [
        chat_input_node("input-1", 100, 300),
        mcp_tool_node("mcp-company-research", "company-intel-mcp", "research_company", 400, 200, "http://localhost:8002/mcp"),
        mcp_tool_node("mcp-interview-ctx", "company-intel-mcp", "get_interview_context", 400, 400, "http://localhost:8002/mcp"),
        agent_node(
            "agent-company-intel",
            "Company Intelligence Agent",
            """Kamu adalah agen riset perusahaan untuk Ergon.

Tugasmu: menerima nama perusahaan dan posisi yang dilamar, kemudian:
1. Gunakan research_company untuk mendapatkan berita terbaru, produk, dan konteks rekrutmen
2. Gunakan get_interview_context untuk membangun pertanyaan wawancara berbasis konteks nyata

Jika tidak ada informasi relevan tentang perusahaan, kembalikan {"available": false} — jangan buat data fiktif.
Prioritaskan informasi yang konkret dan actionable untuk membantu pelamar menyesuaikan CV dan persiapan wawancara.""",
            700, 300,
        ),
        watsonx_llm_node("llm-1", 700, 100),
        chat_output_node("output-1", 1000, 300),
    ]
    edges = [
        edge("input-1", "agent-company-intel", "message", "input_value"),
        edge("mcp-company-research", "agent-company-intel", "text", "tools"),
        edge("mcp-interview-ctx", "agent-company-intel", "text", "tools"),
        edge("llm-1", "agent-company-intel", "text", "llm"),
        edge("agent-company-intel", "output-1", "message", "input_value"),
    ]
    return {
        "name": "company_intel",
        "description": "Ergon Flow 2: Riset kontekstual perusahaan untuk memperkaya analisis CV dan saran perbaikan",
        "data": {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.8}},
    }


def build_cv_portfolio_parsing_flow() -> dict:
    """Flow 3: cv_portfolio_parsing — parses CV and portfolio."""
    nodes = [
        chat_input_node("input-1", 100, 400),
        mcp_tool_node("mcp-cv-pdf", "resume-parser-mcp", "parse_cv_from_pdf", 400, 100, "http://localhost:8003/mcp"),
        mcp_tool_node("mcp-cv-url", "resume-parser-mcp", "parse_cv_from_url", 400, 250, "http://localhost:8003/mcp"),
        mcp_tool_node("mcp-cv-text", "resume-parser-mcp", "parse_cv_from_text", 400, 400, "http://localhost:8003/mcp"),
        mcp_tool_node("mcp-portfolio-github", "portfolio-analyzer-mcp", "analyze_github_portfolio", 400, 550, "http://localhost:8004/mcp"),
        mcp_tool_node("mcp-portfolio-url", "portfolio-analyzer-mcp", "analyze_portfolio_url", 400, 700, "http://localhost:8004/mcp"),
        mcp_tool_node("mcp-portfolio-file", "portfolio-analyzer-mcp", "analyze_portfolio_file", 400, 850, "http://localhost:8004/mcp"),
        agent_node(
            "agent-cv-parser",
            "CV & Portfolio Parsing Agent",
            """Kamu adalah agen parsing CV dan portofolio untuk Ergon.

Tugasmu: menerima input CV (PDF/URL/teks) dan portofolio (GitHub/URL/file) lalu mengekstrak struktur lengkap.

Urutan kerja:
1. Parse CV: 
   - Jika ada pdf_base64 di input → parse_cv_from_pdf
   - Jika ada url CV → parse_cv_from_url  
   - Jika ada teks langsung → parse_cv_from_text
2. Parse Portofolio (jika ada):
   - GitHub URL → analyze_github_portfolio (gunakan job_requirements dari job_data jika tersedia)
   - URL lain (Behance, personal site) → analyze_portfolio_url
   - File base64 → analyze_portfolio_file
3. Gabungkan hasil dan kembalikan JSON terstruktur dengan cv_data dan portfolio_data

Tandai field yang tidak bisa diekstrak dengan catatan di parsing_notes, jangan block seluruh proses.""",
            750, 450,
        ),
        watsonx_llm_node("llm-1", 750, 100),
        chat_output_node("output-1", 1050, 450),
    ]
    edges = [
        edge("input-1", "agent-cv-parser", "message", "input_value"),
        edge("mcp-cv-pdf", "agent-cv-parser", "text", "tools"),
        edge("mcp-cv-url", "agent-cv-parser", "text", "tools"),
        edge("mcp-cv-text", "agent-cv-parser", "text", "tools"),
        edge("mcp-portfolio-github", "agent-cv-parser", "text", "tools"),
        edge("mcp-portfolio-url", "agent-cv-parser", "text", "tools"),
        edge("mcp-portfolio-file", "agent-cv-parser", "text", "tools"),
        edge("llm-1", "agent-cv-parser", "text", "llm"),
        edge("agent-cv-parser", "output-1", "message", "input_value"),
    ]
    return {
        "name": "cv_portfolio_parsing",
        "description": "Ergon Flow 3: Parsing CV (PDF/URL/teks) dan portofolio (GitHub/Behance/file) menjadi data terstruktur",
        "data": {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.7}},
    }


def build_scoring_and_suggestions_flow() -> dict:
    """Flow 4: scoring_and_suggestions — scores CV against job and generates suggestions."""
    nodes = [
        chat_input_node("input-1", 100, 400),
        mcp_tool_node("mcp-score", "scoring-engine-mcp", "calculate_match_score", 400, 200, "http://localhost:8005/mcp"),
        mcp_tool_node("mcp-suggest", "scoring-engine-mcp", "generate_suggestions", 400, 400, "http://localhost:8005/mcp"),
        mcp_tool_node("mcp-embedding", "scoring-engine-mcp", "get_embedding_similarity", 400, 600, "http://localhost:8005/mcp"),
        agent_node(
            "agent-scorer",
            "Scoring & Suggestions Agent",
            """Kamu adalah agen scoring kecocokan CV-loker untuk Ergon.

Tugasmu: menerima job_data, cv_data, dan (opsional) portfolio_data + company_data, lalu:
1. Hitung skor kecocokan komposit dengan calculate_match_score
2. Gunakan get_embedding_similarity untuk memperhalus skor semantic fit jika diperlukan
3. Generate daftar 6 saran perbaikan yang diranking dengan generate_suggestions

Output yang harus dikembalikan:
{
  "scoring": { ... hasil calculate_match_score ... },
  "suggestions": [ ... 6 saran terurut ... ],
  "summary": "ringkasan 1-2 kalimat tentang kecocokan keseluruhan"
}

PENTING: Framing skor harus sebagai estimasi kecocokan, BUKAN jaminan diterima.
Gunakan framing: "Kecocokan CV-mu dengan loker ini: Sedang–Tinggi (65–78%) — estimasi, bukan jaminan rekrutmen." """,
            700, 400,
        ),
        watsonx_llm_node("llm-1", 700, 100),
        chat_output_node("output-1", 1000, 400),
    ]
    edges = [
        edge("input-1", "agent-scorer", "message", "input_value"),
        edge("mcp-score", "agent-scorer", "text", "tools"),
        edge("mcp-suggest", "agent-scorer", "text", "tools"),
        edge("mcp-embedding", "agent-scorer", "text", "tools"),
        edge("llm-1", "agent-scorer", "text", "llm"),
        edge("agent-scorer", "output-1", "message", "input_value"),
    ]
    return {
        "name": "scoring_and_suggestions",
        "description": "Ergon Flow 4: Scoring kecocokan CV-loker dengan breakdown per kategori + generasi 6 saran perbaikan",
        "data": {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.8}},
    }


def build_cv_enhancement_flow() -> dict:
    """Flow 5: cv_enhancement — applies suggestions and generates downloadable CV."""
    nodes = [
        chat_input_node("input-1", 100, 300),
        mcp_tool_node("mcp-enhance", "cv-generator-mcp", "enhance_cv", 400, 200, "http://localhost:8006/mcp"),
        mcp_tool_node("mcp-export-pdf", "cv-generator-mcp", "export_cv_pdf", 400, 400, "http://localhost:8006/mcp"),
        mcp_tool_node("mcp-export-docx", "cv-generator-mcp", "export_cv_docx", 400, 600, "http://localhost:8006/mcp"),
        agent_node(
            "agent-cv-enhancer",
            "CV Enhancement Agent",
            """Kamu adalah agen peningkatan CV untuk Ergon (fitur berbayar setelah unlock).

Tugasmu: menerima cv_data, suggestions, dan job_data, kemudian:
1. Gunakan enhance_cv untuk menerapkan saran perbaikan ke CV (hanya saran yang dipilih jika selected_suggestions ada)
2. Export hasil sebagai PDF dengan export_cv_pdf
3. Jika format "docx" diminta, gunakan export_cv_docx

Output:
{
  "enhanced_cv": { ... struktur CV yang sudah direvisi ... },
  "pdf_base64": "...",
  "docx_base64": "..." (opsional),
  "filename": "ergon-nama-revisi.pdf",
  "changes_applied": [ "daftar perubahan yang dilakukan" ]
}

PENTING: Jangan pernah menambahkan pengalaman, skill, atau pencapaian yang tidak ada di CV asli.
Hanya perbaiki framing, urutan, dan kuantifikasi yang masuk akal.""",
            700, 300,
        ),
        watsonx_llm_node("llm-1", 700, 100),
        chat_output_node("output-1", 1000, 300),
    ]
    edges = [
        edge("input-1", "agent-cv-enhancer", "message", "input_value"),
        edge("mcp-enhance", "agent-cv-enhancer", "text", "tools"),
        edge("mcp-export-pdf", "agent-cv-enhancer", "text", "tools"),
        edge("mcp-export-docx", "agent-cv-enhancer", "text", "tools"),
        edge("llm-1", "agent-cv-enhancer", "text", "llm"),
        edge("agent-cv-enhancer", "output-1", "message", "input_value"),
    ]
    return {
        "name": "cv_enhancement",
        "description": "Ergon Flow 5: Terapkan saran perbaikan ke CV dan generate file siap download (PDF/DOCX) — fitur berbayar",
        "data": {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.8}},
    }


def build_interview_practice_flow() -> dict:
    """Flow 6: interview_practice — Coming Soon, scaffold only."""
    nodes = [
        chat_input_node("input-1", 100, 400),
        mcp_tool_node("mcp-company-intel", "company-intel-mcp", "research_company", 400, 200, "http://localhost:8002/mcp"),
        mcp_tool_node("mcp-interview-ctx", "company-intel-mcp", "get_interview_context", 400, 400, "http://localhost:8002/mcp"),
        agent_node(
            "agent-interview",
            "Interview Practice Agent (Coming Soon)",
            """Kamu adalah agen latihan wawancara AI untuk Ergon (fitur Premium — Coming Soon).

Status: SCAFFOLDED — belum diaktifkan di produksi.

Saat aktif, tugasmu akan:
1. Gunakan company_intel dan job_data untuk membangun konteks perusahaan
2. Generate pertanyaan wawancara personal: behavioral + teknis + spesifik perusahaan
3. Evaluasi jawaban pengguna dan berikan feedback terstruktur
4. Hasilkan laporan akhir: kekuatan, kelemahan, saran, skor kesiapan

Input yang dibutuhkan:
- job_data: output dari job_extraction flow
- cv_data: output dari cv_portfolio_parsing flow  
- scoring_result: output dari scoring_and_suggestions flow
- company_data: output dari company_intel flow

[PLACEHOLDER — Implementasi penuh akan ditambahkan saat fitur voice real-time siap]""",
            700, 400,
        ),
        watsonx_llm_node("llm-1", 700, 100),
        prompt_node(
            "prompt-coming-soon",
            "Coming Soon Notice",
            "⚠️ Fitur Latihan Wawancara AI sedang dalam pengembangan dan belum tersedia untuk pengguna. Flow ini sudah disiapkan dan akan diaktifkan saat implementasi voice real-time (VAD + STT + TTS) selesai. Context: {job_context}",
            700, 700,
        ),
        chat_output_node("output-1", 1000, 400),
    ]
    edges = [
        edge("input-1", "agent-interview", "message", "input_value"),
        edge("mcp-company-intel", "agent-interview", "text", "tools"),
        edge("mcp-interview-ctx", "agent-interview", "text", "tools"),
        edge("llm-1", "agent-interview", "text", "llm"),
        edge("agent-interview", "output-1", "message", "input_value"),
    ]
    return {
        "name": "interview_practice",
        "description": "Ergon Flow 6: Latihan wawancara AI dengan konteks loker & CV — COMING SOON (scaffolded, belum aktif di UI)",
        "data": {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.8}},
    }


# ─── Main: Create all flows via Langflow API ──────────────────────────────────────

FLOWS = [
    build_job_extraction_flow,
    build_company_intel_flow,
    build_cv_portfolio_parsing_flow,
    build_scoring_and_suggestions_flow,
    build_cv_enhancement_flow,
    build_interview_practice_flow,
]


async def get_existing_flows(client: httpx.AsyncClient) -> dict:
    """Get existing flows by name."""
    resp = await client.get(
        f"{LANGFLOW_BASE_URL}/api/v1/flows/",
        headers=HEADERS,
    )
    resp.raise_for_status()
    flows = resp.json()
    return {f["name"]: f["id"] for f in flows}


async def create_or_update_flow(client: httpx.AsyncClient, flow_def: dict, existing: dict) -> dict:
    """Create new flow or update existing one."""
    name = flow_def["name"]

    if name in existing:
        flow_id = existing[name]
        print(f"  Updating existing flow '{name}' (id: {flow_id})...")
        resp = await client.patch(
            f"{LANGFLOW_BASE_URL}/api/v1/flows/{flow_id}",
            headers=HEADERS,
            json=flow_def,
        )
    else:
        print(f"  Creating new flow '{name}'...")
        resp = await client.post(
            f"{LANGFLOW_BASE_URL}/api/v1/flows/",
            headers=HEADERS,
            json=flow_def,
        )

    resp.raise_for_status()
    result = resp.json()
    return result


async def main():
    print("=" * 60)
    print("Ergon — Creating Langflow Flows")
    print(f"Langflow URL: {LANGFLOW_BASE_URL}")
    print(f"Project ID: {LANGFLOW_PROJECT_ID}")
    print("=" * 60)
    print()

    # Verify Langflow connection
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            health_resp = await client.get(
                f"{LANGFLOW_BASE_URL}/api/v1/version",
                headers=HEADERS,
            )
            health_data = health_resp.json()
            print(f"[OK] Connected to Langflow v{health_data.get('version', 'unknown')}")
        except Exception as e:
            print(f"[FAIL] Cannot connect to Langflow at {LANGFLOW_BASE_URL}")
            print(f"  Error: {e}")
            print(f"  Make sure Langflow is running: langflow run")
            sys.exit(1)

        print()

        # Get existing flows
        try:
            existing = await get_existing_flows(client)
            print(f"Found {len(existing)} existing flows: {list(existing.keys())}")
        except Exception as e:
            print(f"Warning: Could not fetch existing flows: {e}")
            existing = {}

        print()

        # Create/update all flows
        created_flows = {}
        for flow_builder in FLOWS:
            flow_def = flow_builder()
            try:
                result = await create_or_update_flow(client, flow_def, existing)
                flow_id = result.get("id", "")
                created_flows[flow_def["name"]] = flow_id
                print(f"  [OK] '{flow_def['name']}' -- id: {flow_id}")
            except Exception as e:
                print(f"  [FAIL] Failed to create '{flow_def['name']}': {e}")
                if hasattr(e, "response") and e.response is not None:
                    print(f"    Response: {e.response.text[:500]}")

        print()
        print("=" * 60)
        print("Flow IDs (add these to backend/env.example):")
        for name, fid in created_flows.items():
            env_key = f"FLOW_ID_{name.upper()}"
            print(f"  {env_key}={fid}")

        print()
        print("All flows created! View them at:")
        print(f"  {LANGFLOW_BASE_URL}")
        print()
        print("Next step: Register MCP servers in Langflow")
        print("  Settings > MCP Servers > Add each server URL")

        # Save flow IDs to file
        with open("flow_ids.json", "w") as f:
            json.dump(created_flows, f, indent=2)
        print()
        print("Flow IDs saved to flow_ids.json")


if __name__ == "__main__":
    asyncio.run(main())
