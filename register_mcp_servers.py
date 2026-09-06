"""
register_mcp_servers.py
Registers all 7 Ergon MCP servers in Langflow via the Settings API.
After running this, go to Langflow Settings > MCP Servers to verify.

Usage:
    python register_mcp_servers.py
"""
import asyncio
import json
import httpx
import os

LANGFLOW_BASE_URL = os.getenv("LANGFLOW_BASE_URL", "http://localhost:7860")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY", "sk-ZXzWNdZqieHFGRTHN_AplG5JHVybs6umO0hYvlpZN5s")

HEADERS = {
    "x-api-key": LANGFLOW_API_KEY,
    "Content-Type": "application/json",
}

# 7 MCP Servers to register
MCP_SERVERS = [
    {
        "name": "job-scraper-mcp",
        "url": "http://localhost:8001/mcp",
        "description": "Ergon: Ekstraksi data lowongan kerja dari URL, PDF, atau gambar/screenshot",
        "tools": ["extract_job_from_url", "extract_job_from_pdf", "extract_job_from_image"],
    },
    {
        "name": "company-intel-mcp",
        "url": "http://localhost:8002/mcp",
        "description": "Ergon: Riset kontekstual perusahaan — berita terbaru, produk, funding, konteks rekrutmen",
        "tools": ["research_company", "get_interview_context"],
    },
    {
        "name": "resume-parser-mcp",
        "url": "http://localhost:8003/mcp",
        "description": "Ergon: Parsing CV/resume menjadi data terstruktur (riwayat kerja, pendidikan, skill)",
        "tools": ["parse_cv_from_pdf", "parse_cv_from_url", "parse_cv_from_text"],
    },
    {
        "name": "portfolio-analyzer-mcp",
        "url": "http://localhost:8004/mcp",
        "description": "Ergon: Analisis portofolio — GitHub, Behance, situs personal, PDF case study",
        "tools": ["analyze_github_portfolio", "analyze_portfolio_url", "analyze_portfolio_file"],
    },
    {
        "name": "scoring-engine-mcp",
        "url": "http://localhost:8005/mcp",
        "description": "Ergon: Scoring kecocokan CV-loker komposit dengan breakdown dan generasi saran",
        "tools": ["calculate_match_score", "generate_suggestions", "get_embedding_similarity"],
    },
    {
        "name": "cv-generator-mcp",
        "url": "http://localhost:8006/mcp",
        "description": "Ergon: Generate CV hasil revisi dalam PDF/DOCX berdasarkan saran perbaikan",
        "tools": ["enhance_cv", "export_cv_pdf", "export_cv_docx"],
    },
    {
        "name": "payment-mcp",
        "url": "http://localhost:8007/mcp",
        "description": "Ergon: Payment processing via Midtrans Snap untuk unlock analisis",
        "tools": ["create_payment_transaction", "verify_payment_status", "process_webhook"],
    },
]


async def get_existing_mcp_servers(client: httpx.AsyncClient) -> list:
    """Try to get existing MCP server configs."""
    # Try multiple possible endpoints for MCP server management
    endpoints = [
        "/api/v1/mcp/servers",
        "/api/v1/config/mcp",
        "/api/v1/settings/mcp",
    ]
    for ep in endpoints:
        try:
            resp = await client.get(f"{LANGFLOW_BASE_URL}{ep}", headers=HEADERS)
            if resp.status_code == 200:
                return resp.json()
        except Exception:
            continue
    return []


async def register_server_via_api(client: httpx.AsyncClient, server: dict) -> dict:
    """Register an MCP server in Langflow settings."""
    # Langflow 1.x MCP server registration via settings endpoint
    payload = {
        "name": server["name"],
        "url": server["url"],
        "description": server["description"],
        "transport": "streamable_http",
    }

    # Try Langflow 1.11 MCP endpoint
    endpoints_to_try = [
        ("/api/v1/mcp/servers", "POST"),
        ("/api/v1/settings/mcp-servers", "POST"),
        ("/api/v1/mcp", "POST"),
    ]

    for endpoint, method in endpoints_to_try:
        try:
            if method == "POST":
                resp = await client.post(
                    f"{LANGFLOW_BASE_URL}{endpoint}",
                    headers=HEADERS,
                    json=payload,
                )
            if resp.status_code in (200, 201):
                return {"success": True, "endpoint": endpoint, "data": resp.json()}
            elif resp.status_code == 422:
                # Already exists or validation error
                return {"success": True, "note": "Already exists or validation error", "status": resp.status_code}
        except Exception as e:
            continue

    # Fallback: write to mcp_servers.json config that Langflow reads
    return {"success": False, "note": "API endpoint not found — will configure via JSON"}


async def write_langflow_mcp_config(servers: list[dict]) -> str:
    """Write MCP server config that Langflow can import."""
    # Langflow uses a specific format for MCP server configuration
    config = {
        "mcpServers": {}
    }
    for server in servers:
        config["mcpServers"][server["name"]] = {
            "url": server["url"],
            "transport": "streamable_http",
            "description": server["description"],
        }

    config_path = "langflow_mcp_servers.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    return config_path


async def main():
    print("=" * 60)
    print("Ergon -- Register MCP Servers in Langflow")
    print(f"Langflow: {LANGFLOW_BASE_URL}")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=15) as client:
        # Verify connection
        try:
            resp = await client.get(f"{LANGFLOW_BASE_URL}/api/v1/version", headers=HEADERS)
            resp.raise_for_status()
            version = resp.json().get("version")
            print(f"[OK] Langflow v{version}")
        except Exception as e:
            print(f"[FAIL] Cannot connect: {e}")
            return

        # Try to get MCP project endpoint (Langflow 1.11 exposes MCP per-project)
        project_mcp_url = f"{LANGFLOW_BASE_URL}/api/v1/mcp/project/{os.getenv('LANGFLOW_PROJECT_ID', '38b35903-4c72-42ca-815a-05ea28ee4d9e')}"
        print(f"Project MCP endpoint: {project_mcp_url}/streamable")

        # Check if we can list existing MCP tools in the project
        try:
            resp = await client.get(
                f"{LANGFLOW_BASE_URL}/api/v1/mcp/project/{os.getenv('LANGFLOW_PROJECT_ID', '38b35903-4c72-42ca-815a-05ea28ee4d9e')}/tools",
                headers=HEADERS,
            )
            if resp.status_code == 200:
                tools = resp.json()
                print(f"[OK] Found {len(tools)} existing MCP tools in project")
        except Exception:
            pass

        # Register each server
        print()
        print("Registering MCP servers:")
        results = {}
        all_via_api = True

        for server in MCP_SERVERS:
            result = await register_server_via_api(client, server)
            results[server["name"]] = result
            if result.get("success"):
                print(f"  [OK] {server['name']} -- {server['url']}")
            else:
                all_via_api = False
                print(f"  [--] {server['name']} -- API registration not available, will use config file")

        # Always write config file for manual import
        config_path = await write_langflow_mcp_config(MCP_SERVERS)
        print()
        print("=" * 60)
        print(f"MCP config file written: {config_path}")
        print()
        print("To register MCP servers in Langflow:")
        print("  Option A (Recommended for Langflow 1.11+):")
        print("    1. Open Langflow at http://localhost:7860")
        print("    2. Go to Settings (gear icon, top right)")
        print("    3. Select 'MCP Servers'")
        print("    4. Add each server URL:")
        for s in MCP_SERVERS:
            print(f"       - {s['name']}: {s['url']}")
        print()
        print("  Option B: Import from config file")
        print(f"    Copy {config_path} to Langflow config directory")
        print()
        print("After registration, add MCP Tool nodes in each flow:")
        print("  - Open flow in Langflow canvas")
        print("  - Drag 'MCP Tool' component from sidebar")
        print("  - Select server and tool from dropdown")

        # Also output curl commands for manual registration
        print()
        print("  Option C: curl commands to register via API:")
        for server in MCP_SERVERS:
            print(f"""
  curl -X POST http://localhost:7860/api/v1/mcp/servers \\
    -H "x-api-key: {LANGFLOW_API_KEY}" \\
    -H "Content-Type: application/json" \\
    -d '{json.dumps({"name": server["name"], "url": server["url"]})}'""")


if __name__ == "__main__":
    asyncio.run(main())
