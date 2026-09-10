"""
Hardcode base_url and api_key directly into Agent node template in all Ergon flows.

When Langflow builds the Agent component, it calls get_llm() which calls
_apply_registered_provider_connection() to resolve OPENAI_COMPATIBLE_BASE_URL
from the variable service. If that lookup fails or returns stale data,
the base_url is missing and ChatOpenAI hits the wrong endpoint.

This script injects base_url and api_key values directly into the
'openai_compatible_base_url' and 'api_key' fields of each Agent node template,
so the component uses them without needing to look up global variables.
"""
import sqlite3
import json
import os

DB_PATH = os.path.join(os.environ["APPDATA"], "com.LangflowDesktop", "data", "database.db")

ERGON_FLOWS = [
    "job_extraction",
    "company_intel",
    "cv_portfolio_parsing",
    "scoring_and_suggestions",
    "cv_enhancement",
]

BASE_URL = "https://campaigns-limitation-ownership-bid.trycloudflare.com"
API_KEY  = "sk-d8b4bf780a10a8fd-3l1iek-c890de0e"


def patch_agent_node(node: dict) -> dict:
    if node.get("data", {}).get("type") != "Agent":
        return node

    template = node["data"]["node"]["template"]

    # 1. Set openai_compatible_base_url field (shown as advanced field in Agent)
    if "openai_compatible_base_url" in template:
        template["openai_compatible_base_url"]["value"] = BASE_URL
        print(f"  + set openai_compatible_base_url = {BASE_URL}")

    # 2. Set api_key field
    if "api_key" in template:
        template["api_key"]["value"] = API_KEY
        print(f"  + set api_key = {API_KEY[:20]}...")

    # 3. Also check for base_url field (some versions use different names)
    for field_name in ["base_url", "openai_api_base"]:
        if field_name in template and not template[field_name].get("value"):
            template[field_name]["value"] = BASE_URL
            print(f"  + set {field_name} = {BASE_URL}")

    node["data"]["node"]["template"] = template
    return node


conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

for flow_name in ERGON_FLOWS:
    cur.execute("SELECT id, data FROM flow WHERE name = ?", (flow_name,))
    row = cur.fetchone()
    if not row:
        print(f"[SKIP] {flow_name} not found")
        continue

    flow_id, raw_data = row
    data = json.loads(raw_data)
    nodes = data.get("nodes", [])

    agent_count = sum(1 for n in nodes if n.get("data", {}).get("type") == "Agent")
    print(f"\nFlow: {flow_name} ({agent_count} Agent nodes)")

    data["nodes"] = [patch_agent_node(n) for n in nodes]

    new_raw = json.dumps(data, ensure_ascii=False)
    cur.execute("UPDATE flow SET data = ? WHERE id = ?", (new_raw, flow_id))
    print(f"  [OK] Saved {flow_name}")

conn.commit()
conn.close()
print("\nAll done.")
