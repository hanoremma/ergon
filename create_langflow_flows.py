"""
create_langflow_flows.py
Builds all 6 Ergon flows using Langflow's native node format.
Each flow connects to real MCP servers (ports 8001-8007) via MCPTools nodes.

Usage:
    python create_langflow_flows.py

Requirements:
    pip install httpx
"""
import copy
import json
import os
import sqlite3
import sys
import uuid

MCP_BASE = "http://localhost"
MCP_PORTS = {
    "job-scraper-mcp":       8001,
    "company-intel-mcp":     8002,
    "resume-parser-mcp":     8003,
    "portfolio-analyzer-mcp":8004,
    "scoring-engine-mcp":    8005,
    "cv-generator-mcp":      8006,
    "payment-mcp":           8007,
}

DB_PATH = os.path.join(
    os.environ.get("APPDATA", ""),
    "com.LangflowDesktop", "data", "database.db",
)

# ─── Load native node templates from DB (Simple Agent flow) ──────────────────

def _load_native_templates() -> dict:
    """Clone ChatInput, ChatOutput, Agent nodes from the working Simple Agent flow."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT data FROM flow WHERE name = 'Simple Agent'")
    row = cur.fetchone()
    conn.close()
    if not row:
        raise RuntimeError("Simple Agent flow not found in database — cannot load node templates.")
    data = json.loads(row[0])
    templates = {}
    for n in data["nodes"]:
        t = n["data"].get("type")
        if t in ("Agent", "ChatInput", "ChatOutput"):
            templates[t] = n
    return templates

_TEMPLATES = _load_native_templates()

# ─── Node builders ────────────────────────────────────────────────────────────

def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:5].upper()}"


def make_chat_input(node_id: str, x: int, y: int) -> dict:
    n = copy.deepcopy(_TEMPLATES["ChatInput"])
    n["id"] = node_id
    n["position"] = {"x": x, "y": y}
    n["data"]["id"] = node_id
    n["selected"] = False
    return n


def make_chat_output(node_id: str, x: int, y: int) -> dict:
    n = copy.deepcopy(_TEMPLATES["ChatOutput"])
    n["id"] = node_id
    n["position"] = {"x": x, "y": y}
    n["data"]["id"] = node_id
    n["selected"] = False
    return n


def make_mcp_tools(node_id: str, server_name: str, display_name: str, x: int, y: int) -> dict:
    """Build an MCPTools node pointing to one of our MCP servers."""
    port = MCP_PORTS[server_name]
    url = f"{MCP_BASE}:{port}/mcp"
    return {
        "id": node_id, "type": "genericNode",
        "position": {"x": x, "y": y},
        "measured": {"width": 320, "height": 300},
        "selected": False,
        "data": {
            "type": "MCPTools", "id": node_id,
            "display_name": display_name,
            "node": {
                "base_classes": ["Tool"],
                "beta": False,
                "conditional_paths": [],
                "custom_fields": {},
                "description": f"MCP tools from {server_name}",
                "display_name": display_name,
                "documentation": "",
                "edited": False,
                "field_order": ["mcp_server", "use_cache", "verify_ssl", "headers", "tool_execution_timeout"],
                "frozen": False,
                "icon": "wrench",
                "key": "MCPTools",
                "legacy": False,
                "minimized": False,
                "output_types": [],
                "outputs": [
                    {
                        "allows_loop": False,
                        "cache": False,
                        "display_name": "Toolset",
                        "group_outputs": False,
                        "method": "to_toolkit",
                        "name": "component_as_tool",
                        "selected": "Tool",
                        "tool_mode": False,
                        "types": ["Tool"],
                        "value": "__UNDEFINED__",
                    }
                ],
                "pinned": False,
                "template": {
                    "_type": "Component",
                    "mcp_server": {
                        "_input_type": "McpInput",
                        "advanced": False,
                        "display_name": "MCP Server",
                        "dynamic": False,
                        "info": "Select or configure an MCP server.",
                        "name": "mcp_server",
                        "placeholder": "",
                        "required": False,
                        "show": True,
                        "title_case": False,
                        "tool_mode": False,
                        "type": "mcp",
                        "value": {
                            "name": server_name,
                            "url": url,
                            "transport": "streamable_http",
                        },
                    },
                    "use_cache": {
                        "_input_type": "BoolInput",
                        "advanced": True,
                        "display_name": "Use Cached Server",
                        "dynamic": False,
                        "info": "Reuse the existing MCP server connection.",
                        "list": False,
                        "name": "use_cache",
                        "required": False,
                        "show": True,
                        "title_case": False,
                        "type": "bool",
                        "value": True,
                    },
                    "verify_ssl": {
                        "_input_type": "BoolInput",
                        "advanced": True,
                        "display_name": "Verify SSL",
                        "dynamic": False,
                        "info": "Verify SSL certificates.",
                        "list": False,
                        "name": "verify_ssl",
                        "required": False,
                        "show": True,
                        "title_case": False,
                        "type": "bool",
                        "value": True,
                    },
                    "headers": {
                        "_input_type": "DictInput",
                        "advanced": True,
                        "display_name": "Headers",
                        "dynamic": False,
                        "info": "Additional headers for the MCP server requests.",
                        "list": False,
                        "name": "headers",
                        "required": False,
                        "show": True,
                        "title_case": False,
                        "type": "dict",
                        "value": {},
                    },
                    "tool_execution_timeout": {
                        "_input_type": "FloatInput",
                        "advanced": True,
                        "display_name": "Tool Execution Timeout",
                        "dynamic": False,
                        "info": "Timeout in seconds for tool execution.",
                        "list": False,
                        "name": "tool_execution_timeout",
                        "required": False,
                        "show": True,
                        "title_case": False,
                        "type": "float",
                        "value": 60.0,
                    },
                },
            },
        },
    }


def make_agent(node_id: str, display_name: str, system_prompt: str, x: int, y: int) -> dict:
    """Clone the native Agent node from Simple Agent, only override id/position/display_name/system_prompt."""
    n = copy.deepcopy(_TEMPLATES["Agent"])
    n["id"] = node_id
    n["position"] = {"x": x, "y": y}
    n["selected"] = False
    n["data"]["id"] = node_id
    n["data"]["display_name"] = display_name
    n["data"]["node"]["display_name"] = display_name
    n["data"]["node"]["template"]["system_prompt"]["value"] = system_prompt
    return n


# Handle metadata for sourceHandle and targetHandle (native Langflow JSON string format)
_SOURCE_META = {
    # (dataType, outputName) -> output_types list
    ("ChatInput",  "message"):           ["Message"],
    ("Agent",      "response"):          ["Message"],
    ("MCPTools",   "component_as_tool"): ["Tool"],
}

_TARGET_META = {
    # (dataType, fieldName) -> (inputTypes list, type str)
    ("Agent",      "input_value"): (["Message"],                                       "str"),
    ("Agent",      "tools"):       (["Tool"],                                           "other"),
    ("ChatOutput", "input_value"): (["Data", "JSON", "DataFrame", "Table", "Message"], "other"),
}


def make_edge(source_id: str, source_output: str, source_type: str,
              target_id: str, target_input: str, target_type: str) -> dict:
    """Build a Langflow edge using the native JSON-string handle format."""
    import json as _json
    src_output_types = _SOURCE_META.get((source_type, source_output), ["Message"])
    tgt_input_types, tgt_type = _TARGET_META.get((target_type, target_input), (["Message"], "other"))

    source_handle = _json.dumps({
        "dataType": source_type,
        "id": source_id,
        "name": source_output,
        "output_types": src_output_types,
    }, separators=(",", ":"))

    target_handle = _json.dumps({
        "fieldName": target_input,
        "id": target_id,
        "inputTypes": tgt_input_types,
        "type": tgt_type,
    }, separators=(",", ":"))

    return {
        "id": f"reactflow__edge-{source_id}{source_output}-{target_id}{target_input}",
        "source": source_id,
        "sourceHandle": source_handle,
        "target": target_id,
        "targetHandle": target_handle,
        "className": "",
        "selected": False,
    }


# ─── Flow Definitions ─────────────────────────────────────────────────────────

def build_job_extraction_flow(folder_id: str) -> dict:
    cin = _uid("ChatInput");  agent = _uid("Agent");  cout = _uid("ChatOutput")
    mcp_url   = _uid("MCPTools"); mcp_pdf = _uid("MCPTools"); mcp_img = _uid("MCPTools")

    nodes = [
        make_chat_input(cin, 100, 400),
        make_mcp_tools(mcp_url,  "job-scraper-mcp", "Job Scraper — URL",   400, 100),
        make_mcp_tools(mcp_pdf,  "job-scraper-mcp", "Job Scraper — PDF",   400, 380),
        make_mcp_tools(mcp_img,  "job-scraper-mcp", "Job Scraper — Image", 400, 660),
        make_agent(agent, "Job Extraction Agent", """\
Kamu adalah agen ekstraksi lowongan kerja untuk Ergon.

Tugasmu: menerima input dari pengguna dan mengekstrak data lowongan terstruktur.

Routing berdasarkan input:
- Input berupa URL (dimulai http/https) → gunakan extract_job_from_url
- Input berupa base64 PDF (dimulai JVBERi) → gunakan extract_job_from_pdf
- Input berupa base64 gambar / screenshot → gunakan extract_job_from_image
- Input berupa JSON dengan field "url", "pdf_base64", atau "image_base64" → route ke tool yang sesuai
- Input berupa teks deskripsi lowongan langsung → ekstrak langsung tanpa tool

Kembalikan JSON terstruktur:
{
  "title": "", "company": "", "location": "", "employment_type": "",
  "requirements": [], "responsibilities": [], "salary_range": "",
  "benefits": [], "deadline": "", "source_url": ""
}

Isi field yang tidak ditemukan dengan string kosong — jangan gagalkan seluruh proses.""", 750, 380),
        make_chat_output(cout, 1100, 400),
    ]
    edges = [
        make_edge(cin,     "message",          "ChatInput", agent, "input_value", "Agent"),
        make_edge(mcp_url, "component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(mcp_pdf, "component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(mcp_img, "component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(agent,   "response",         "Agent",     cout,  "input_value", "ChatOutput"),
    ]
    return {
        "name": "job_extraction", "folder_id": folder_id,
        "description": "Ergon Flow 1: Ekstraksi data lowongan kerja dari URL, PDF, atau gambar/screenshot",
        "data": {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.75}},
    }


def build_company_intel_flow(folder_id: str) -> dict:
    cin = _uid("ChatInput");  agent = _uid("Agent");  cout = _uid("ChatOutput")
    mcp_research = _uid("MCPTools"); mcp_interview = _uid("MCPTools")

    nodes = [
        make_chat_input(cin, 100, 350),
        make_mcp_tools(mcp_research,   "company-intel-mcp", "Company Research",   400, 150),
        make_mcp_tools(mcp_interview,  "company-intel-mcp", "Interview Context",  400, 450),
        make_agent(agent, "Company Intelligence Agent", """\
Kamu adalah agen riset perusahaan untuk Ergon.

Tugasmu: menerima nama perusahaan dan posisi yang dilamar, kemudian:
1. Gunakan research_company untuk mendapatkan berita terbaru, produk, budaya, dan konteks rekrutmen
2. Gunakan get_interview_context untuk membangun pertanyaan wawancara berbasis konteks nyata perusahaan

Format input yang diterima:
- Teks: "Nama Perusahaan, Posisi Target"
- JSON: {"company": "...", "position": "...", "job_data": {...}}

Kembalikan JSON:
{
  "company_name": "", "industry": "", "size": "", "culture": "",
  "recent_news": [], "products_services": [], "tech_stack": [],
  "interview_tips": [], "interview_questions": [], "available": true
}

Jika tidak ada informasi relevan, kembalikan {"available": false} — jangan buat data fiktif.""", 750, 300),
        make_chat_output(cout, 1100, 350),
    ]
    edges = [
        make_edge(cin,          "message",          "ChatInput", agent, "input_value", "Agent"),
        make_edge(mcp_research, "component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(mcp_interview,"component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(agent,        "response",         "Agent",     cout,  "input_value", "ChatOutput"),
    ]
    return {
        "name": "company_intel", "folder_id": folder_id,
        "description": "Ergon Flow 2: Riset kontekstual perusahaan — berita, produk, budaya, dan konteks rekrutmen",
        "data": {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.8}},
    }


def build_cv_parsing_flow(folder_id: str) -> dict:
    cin = _uid("ChatInput");  agent = _uid("Agent");  cout = _uid("ChatOutput")
    mcp_pdf       = _uid("MCPTools"); mcp_url_cv  = _uid("MCPTools")
    mcp_text      = _uid("MCPTools"); mcp_gh      = _uid("MCPTools")
    mcp_portfolio = _uid("MCPTools")

    nodes = [
        make_chat_input(cin, 100, 500),
        make_mcp_tools(mcp_pdf,       "resume-parser-mcp",     "CV Parser — PDF",       400, 100),
        make_mcp_tools(mcp_url_cv,    "resume-parser-mcp",     "CV Parser — URL",       400, 330),
        make_mcp_tools(mcp_text,      "resume-parser-mcp",     "CV Parser — Text",      400, 560),
        make_mcp_tools(mcp_gh,        "portfolio-analyzer-mcp","Portfolio — GitHub",    400, 790),
        make_mcp_tools(mcp_portfolio, "portfolio-analyzer-mcp","Portfolio — URL/File",  400, 1020),
        make_agent(agent, "CV & Portfolio Parsing Agent", """\
Kamu adalah agen parsing CV dan portofolio untuk Ergon.

Tugasmu: menerima input CV dan (opsional) portofolio, lalu mengekstrak struktur lengkap.

Urutan kerja:
1. Parse CV:
   - Field "pdf_base64" tersedia → parse_cv_from_pdf
   - Field "cv_url" tersedia → parse_cv_from_url (support Google Docs, direct URL)
   - Teks CV langsung → parse_cv_from_text
2. Parse Portofolio (jika tersedia):
   - GitHub URL → analyze_github_portfolio
   - URL lain (Behance, personal site) atau base64 file → analyze_portfolio_url / analyze_portfolio_file

Format input yang diterima:
- JSON: {"cv_url": "...", "portfolio_url": "...", "job_requirements": [...]}
- JSON: {"pdf_base64": "...", "github_url": "..."}
- Teks CV langsung

Kembalikan JSON:
{
  "cv_data": {
    "personal_info": {"name":"","email":"","phone":"","location":"","linkedin":"","github":""},
    "summary": "", "experience": [], "education": [], "skills": {}, "certifications": [], "projects": []
  },
  "portfolio_data": {"github_stats": {}, "top_skills": [], "projects": [], "relevance_score": 0},
  "parsing_notes": []
}""", 800, 500),
        make_chat_output(cout, 1150, 500),
    ]
    edges = [
        make_edge(cin,          "message",          "ChatInput", agent, "input_value", "Agent"),
        make_edge(mcp_pdf,      "component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(mcp_url_cv,   "component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(mcp_text,     "component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(mcp_gh,       "component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(mcp_portfolio,"component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(agent,        "response",         "Agent",     cout,  "input_value", "ChatOutput"),
    ]
    return {
        "name": "cv_portfolio_parsing", "folder_id": folder_id,
        "description": "Ergon Flow 3: Parsing CV (PDF/URL/teks) dan portofolio (GitHub/Behance/file) menjadi data terstruktur",
        "data": {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.65}},
    }


def build_scoring_flow(folder_id: str) -> dict:
    cin = _uid("ChatInput");  agent = _uid("Agent");  cout = _uid("ChatOutput")
    mcp_score     = _uid("MCPTools")
    mcp_suggest   = _uid("MCPTools")
    mcp_embed     = _uid("MCPTools")

    nodes = [
        make_chat_input(cin, 100, 400),
        make_mcp_tools(mcp_score,   "scoring-engine-mcp", "Match Scorer",         400, 150),
        make_mcp_tools(mcp_suggest, "scoring-engine-mcp", "Suggestion Generator", 400, 430),
        make_mcp_tools(mcp_embed,   "scoring-engine-mcp", "Embedding Similarity", 400, 710),
        make_agent(agent, "Scoring & Suggestions Agent", """\
Kamu adalah agen scoring kecocokan CV-loker untuk Ergon.

Tugasmu: menerima job_data dan cv_data, menghitung skor kecocokan, dan menghasilkan 6 saran perbaikan.

Urutan kerja:
1. Panggil calculate_match_score dengan job_data dan cv_data
2. Panggil get_embedding_similarity untuk menguatkan skor semantic jika ada mismatch
3. Panggil generate_suggestions untuk menghasilkan 6 saran terurut berdasarkan scoring

Format input:
{
  "job_data": { ... output dari flow job_extraction ... },
  "cv_data":  { ... output dari flow cv_portfolio_parsing ... },
  "portfolio_data": { ... opsional ... },
  "company_data":   { ... opsional ... }
}

Kembalikan JSON:
{
  "scoring": {
    "overall_score": 75,
    "framing": "Kecocokan CV-mu: Sedang–Tinggi (75%) — estimasi, bukan jaminan rekrutmen.",
    "breakdown": {"keyword_match":80, "semantic_similarity":72, "seniority_match":70,
                  "portfolio_relevance":65, "cv_quality":60, "competition_signal":50}
  },
  "suggestions": [
    {"priority":1, "category":"skills", "title":"", "description":"", "impact":"high", "free":true},
    {"priority":2, "category":"keywords", "title":"", "description":"", "impact":"high", "free":true},
    {"priority":3, "category":"experience", "title":"", "description":"", "impact":"medium", "free":true},
    {"priority":4, "category":"format", "title":"", "description":"", "impact":"medium", "free":false},
    {"priority":5, "category":"summary", "title":"", "description":"", "impact":"medium", "free":false},
    {"priority":6, "category":"projects", "title":"", "description":"", "impact":"low", "free":false}
  ],
  "free_suggestions": 3,
  "locked_suggestions": 3
}

PENTING: Selalu framing skor sebagai estimasi, BUKAN jaminan diterima.""", 750, 380),
        make_chat_output(cout, 1100, 400),
    ]
    edges = [
        make_edge(cin,       "message",          "ChatInput", agent, "input_value", "Agent"),
        make_edge(mcp_score, "component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(mcp_suggest,"component_as_tool","MCPTools", agent, "tools",       "Agent"),
        make_edge(mcp_embed, "component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(agent,     "response",         "Agent",     cout,  "input_value", "ChatOutput"),
    ]
    return {
        "name": "scoring_and_suggestions", "folder_id": folder_id,
        "description": "Ergon Flow 4: Scoring CV-loker komposit + 6 saran perbaikan (3 gratis, 3 premium)",
        "data": {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.75}},
    }


def build_cv_enhancement_flow(folder_id: str) -> dict:
    cin = _uid("ChatInput");  agent = _uid("Agent");  cout = _uid("ChatOutput")
    mcp_enhance = _uid("MCPTools")
    mcp_pdf_exp = _uid("MCPTools")
    mcp_docx    = _uid("MCPTools")

    nodes = [
        make_chat_input(cin, 100, 350),
        make_mcp_tools(mcp_enhance, "cv-generator-mcp", "CV Enhancer",     400, 100),
        make_mcp_tools(mcp_pdf_exp, "cv-generator-mcp", "Export PDF",      400, 380),
        make_mcp_tools(mcp_docx,    "cv-generator-mcp", "Export DOCX",     400, 660),
        make_agent(agent, "CV Enhancement Agent", """\
Kamu adalah agen peningkatan CV untuk Ergon — fitur berbayar yang aktif setelah unlock.

Tugasmu: menerima cv_data, suggestions, dan job_data, lalu menghasilkan CV yang sudah direvisi dalam format file.

Urutan kerja:
1. Panggil enhance_cv dengan cv_data, suggestions, dan job_data
   - Jika selected_suggestions disertakan, hanya terapkan saran tersebut
2. Panggil export_cv_pdf untuk menghasilkan PDF siap download
3. Jika format "docx" diminta, panggil export_cv_docx

Format input:
{
  "cv_data": { ... output dari cv_portfolio_parsing ... },
  "suggestions": [ ... output dari scoring_and_suggestions (semua 6 saran) ... ],
  "job_data": { ... output dari job_extraction ... },
  "selected_suggestions": [1,2,3],  // opsional, jika null terapkan semua
  "export_format": "pdf"  // atau "docx", default "pdf"
}

Kembalikan JSON:
{
  "enhanced_cv": { ... struktur CV yang sudah direvisi ... },
  "pdf_base64": "...",
  "docx_base64": "...",  // null jika tidak diminta
  "filename": "ergon-nama-revisi.pdf",
  "changes_applied": [],
  "changes_skipped": []
}

PENTING: Jangan pernah menambahkan pengalaman, skill, atau pencapaian yang tidak ada di CV asli.
Hanya perbaiki framing, urutan, dan kuantifikasi yang masuk akal dari data yang ada.""", 750, 350),
        make_chat_output(cout, 1100, 350),
    ]
    edges = [
        make_edge(cin,        "message",          "ChatInput", agent, "input_value", "Agent"),
        make_edge(mcp_enhance,"component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(mcp_pdf_exp,"component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(mcp_docx,   "component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(agent,      "response",         "Agent",     cout,  "input_value", "ChatOutput"),
    ]
    return {
        "name": "cv_enhancement", "folder_id": folder_id,
        "description": "Ergon Flow 5: Terapkan saran perbaikan ke CV dan generate PDF/DOCX siap download — fitur premium",
        "data": {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.75}},
    }


def build_interview_practice_flow(folder_id: str) -> dict:
    cin = _uid("ChatInput");  agent = _uid("Agent");  cout = _uid("ChatOutput")
    mcp_research  = _uid("MCPTools")
    mcp_interview = _uid("MCPTools")

    nodes = [
        make_chat_input(cin, 100, 350),
        make_mcp_tools(mcp_research,  "company-intel-mcp", "Company Research",  400, 150),
        make_mcp_tools(mcp_interview, "company-intel-mcp", "Interview Context", 400, 450),
        make_agent(agent, "Interview Practice Agent", """\
Kamu adalah agen latihan wawancara AI untuk Ergon.

Tugasmu: menerima job_data, cv_data, dan company_data, lalu menghasilkan sesi latihan wawancara yang personal.

Urutan kerja:
1. Gunakan research_company untuk memperkaya konteks perusahaan (jika company_data belum tersedia)
2. Gunakan get_interview_context untuk generate pertanyaan wawancara berbasis konteks nyata
3. Generate pertanyaan behavioral, teknis, dan spesifik-perusahaan berdasarkan seluruh konteks

Format input:
{
  "job_data": { ... output dari job_extraction ... },
  "cv_data": { ... output dari cv_portfolio_parsing ... },
  "scoring_result": { ... output dari scoring_and_suggestions ... },
  "company_data": { ... output dari company_intel, opsional ... },
  "mode": "generate_questions"  // atau "evaluate_answer" jika ada field "question" dan "answer"
}

Untuk mode "generate_questions", kembalikan:
{
  "interview_questions": [
    {"id":1, "type":"behavioral", "question":"", "why_asked":"", "tips":""},
    {"id":2, "type":"technical",  "question":"", "why_asked":"", "tips":""},
    {"id":3, "type":"company",    "question":"", "why_asked":"", "tips":""},
    ... total 10 pertanyaan ...
  ],
  "preparation_tips": [],
  "estimated_readiness": "medium",
  "focus_areas": []
}

Untuk mode "evaluate_answer" (field "question" dan "answer" tersedia), kembalikan:
{
  "score": 75,
  "feedback": "",
  "strengths": [],
  "improvements": [],
  "model_answer_hint": ""
}""", 750, 300),
        make_chat_output(cout, 1100, 350),
    ]
    edges = [
        make_edge(cin,          "message",          "ChatInput", agent, "input_value", "Agent"),
        make_edge(mcp_research, "component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(mcp_interview,"component_as_tool","MCPTools",  agent, "tools",       "Agent"),
        make_edge(agent,        "response",         "Agent",     cout,  "input_value", "ChatOutput"),
    ]
    return {
        "name": "interview_practice", "folder_id": folder_id,
        "description": "Ergon Flow 6: Latihan wawancara AI personal — generate pertanyaan & evaluasi jawaban",
        "data": {"nodes": nodes, "edges": edges, "viewport": {"x": 0, "y": 0, "zoom": 0.8}},
    }


FLOW_BUILDERS = [
    build_job_extraction_flow,
    build_company_intel_flow,
    build_cv_parsing_flow,
    build_scoring_flow,
    build_cv_enhancement_flow,
    build_interview_practice_flow,
]


# ─── Inject directly into SQLite (bypasses auth) ─────────────────────────────

def inject_to_db(flows: list[dict], db_path: str) -> dict:
    import sqlite3
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    USER_ID = "d886394153cc47169c5bc76515aaff08"

    cur.execute("SELECT id, name FROM flow WHERE user_id = ?", (USER_ID,))
    existing = {r[1]: r[0] for r in cur.fetchall()}

    created = {}
    for flow in flows:
        name = flow["name"]
        data_str = json.dumps(flow["data"])
        if name in existing:
            fid = existing[name]
            cur.execute("UPDATE flow SET data=?, description=?, updated_at=? WHERE id=?",
                        (data_str, flow["description"], now, fid))
            print(f"  [updated] {name} ({fid[:8]})")
        else:
            fid = uuid.uuid4().hex
            cur.execute(
                "INSERT INTO flow (id, name, description, data, folder_id, user_id, is_component, updated_at) "
                "VALUES (?,?,?,?,?,?,0,?)",
                (fid, name, flow["description"], data_str, flow["folder_id"], USER_ID, now),
            )
            print(f"  [created] {name} ({fid[:8]})")
        created[name] = fid

    conn.commit()
    conn.close()
    return created


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    import platform
    print("=" * 60)
    print("Ergon — Building Full Langflow Flows (with MCP nodes)")
    print("=" * 60)

    FOLDER_ID = "38b359034c7242ca815a05ea28ee4d9e"
    db_path = os.path.join(
        os.environ.get("APPDATA", ""),
        "com.LangflowDesktop", "data", "database.db"
    )

    if not os.path.exists(db_path):
        print(f"[FAIL] Database not found: {db_path}")
        sys.exit(1)

    print(f"\nDatabase: {db_path}")
    print(f"Folder:   {FOLDER_ID}\n")

    flows = [builder(FOLDER_ID) for builder in FLOW_BUILDERS]
    print(f"Building {len(flows)} flows...")
    for f in flows:
        n = len(f["data"]["nodes"]); e = len(f["data"]["edges"])
        print(f"  {f['name']}: {n} nodes, {e} edges")

    print()
    created = inject_to_db(flows, db_path)

    # Save flow IDs
    ids_path = os.path.join(os.path.dirname(__file__), "flow_ids.json")
    existing_ids = {}
    if os.path.exists(ids_path):
        with open(ids_path) as f:
            existing_ids = json.load(f)
    existing_ids.update(created)
    with open(ids_path, "w") as f:
        json.dump(existing_ids, f, indent=2)

    print(f"\n{'=' * 60}")
    print(f"Done! {len(created)} flows saved.")
    print("Flow IDs saved to flow_ids.json")
    print("\nRestart Langflow Desktop to reload flows from database.")


if __name__ == "__main__":
    main()
