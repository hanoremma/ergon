"""
register_mcp_v2.py  —  Register all 7 Ergon MCP servers via Langflow v2 API
POST /api/v2/mcp/servers/{server_name}  with {"url": "http://localhost:PORT/mcp"}
"""
import asyncio, json
import httpx

LANGFLOW_BASE = "http://localhost:7860"
API_KEY = "sk-ZXzWNdZqieHFGRTHN_AplG5JHVybs6umO0hYvlpZN5s"
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

SERVERS = [
    {"name": "job-scraper-mcp",        "url": "http://localhost:8001/mcp"},
    {"name": "company-intel-mcp",      "url": "http://localhost:8002/mcp"},
    {"name": "resume-parser-mcp",      "url": "http://localhost:8003/mcp"},
    {"name": "portfolio-analyzer-mcp", "url": "http://localhost:8004/mcp"},
    {"name": "scoring-engine-mcp",     "url": "http://localhost:8005/mcp"},
    {"name": "cv-generator-mcp",       "url": "http://localhost:8006/mcp"},
    {"name": "payment-mcp",            "url": "http://localhost:8007/mcp"},
]

async def main():
    print("Registering 7 MCP servers via /api/v2/mcp/servers/")
    async with httpx.AsyncClient(timeout=15) as c:
        # Get existing servers first
        r = await c.get(f"{LANGFLOW_BASE}/api/v2/mcp/servers", headers=HEADERS)
        existing = {s["name"] for s in r.json()}
        print(f"Existing servers: {existing}")
        print()

        for s in SERVERS:
            name, url = s["name"], s["url"]
            if name in existing:
                # Update with PATCH
                resp = await c.patch(
                    f"{LANGFLOW_BASE}/api/v2/mcp/servers/{name}",
                    headers=HEADERS, json={"url": url},
                )
                verb = "UPDATED"
            else:
                # Create with POST
                resp = await c.post(
                    f"{LANGFLOW_BASE}/api/v2/mcp/servers/{name}",
                    headers=HEADERS, json={"url": url},
                )
                verb = "CREATED"

            if resp.status_code in (200, 201):
                print(f"  [OK] {verb}: {name}  ({url})")
            else:
                print(f"  [!!] {name}  HTTP {resp.status_code}: {resp.text[:200]}")

        # Verify final list
        print()
        r2 = await c.get(f"{LANGFLOW_BASE}/api/v2/mcp/servers", headers=HEADERS)
        all_servers = r2.json()
        print("All registered MCP servers now:")
        for s in all_servers:
            print(f"  {s['name']}")

asyncio.run(main())
