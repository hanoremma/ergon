"""
Inject the 'code' field and metadata into all MCPTools nodes
in Ergon flows. Without the 'code' field, Langflow raises KeyError: 'code'
when building the graph.

This script:
1. Fetches the canonical MCPTools component template from Langflow /api/v1/all
2. Extracts the 'code' value and metadata.code_hash
3. Injects them into every MCPTools node template in each Ergon flow
"""
import sqlite3
import json
import os
import httpx

DB_PATH = os.path.join(os.environ["APPDATA"], "com.LangflowDesktop", "data", "database.db")
LANGFLOW_URL = "http://127.0.0.1:7860"

ERGON_FLOWS = [
    "job_extraction",
    "company_intel",
    "cv_portfolio_parsing",
    "scoring_and_suggestions",
    "cv_enhancement",
    "interview_practice",
]


def get_mcp_tools_template():
    r = httpx.get(f"{LANGFLOW_URL}/api/v1/all", timeout=15)
    all_data = r.json()
    for cat_name, cat in all_data.items():
        if isinstance(cat, dict):
            for comp_name, comp in cat.items():
                if comp_name == "MCPTools":
                    return comp
    return None


def inject_code_into_node(node: dict, canonical_template: dict) -> dict:
    """Inject code + metadata into a MCPTools node if missing."""
    node_data = node.get("data", {})
    node_type = node_data.get("type", "")
    if node_type != "MCPTools":
        return node

    node_inner = node_data.get("node", {})
    template = node_inner.get("template", {})

    # Inject code field
    if "code" not in template:
        code_field = canonical_template.get("template", {}).get("code")
        if code_field:
            template["code"] = code_field
            print(f"  + injected code field into node {node_data.get('id','?')}")

    # Inject metadata.code_hash if missing
    metadata = node_inner.get("metadata", {})
    if not metadata.get("code_hash"):
        canonical_meta = canonical_template.get("metadata", {})
        if canonical_meta.get("code_hash"):
            metadata["code_hash"] = canonical_meta["code_hash"]
            node_inner["metadata"] = metadata
            print(f"  + injected code_hash into node {node_data.get('id','?')}")

    # Also copy any missing top-level node fields from canonical
    canonical_node_keys = ["base_classes", "output_types", "outputs"]
    for key in canonical_node_keys:
        if key not in node_inner and key in canonical_template:
            node_inner[key] = canonical_template[key]

    node_inner["template"] = template
    node_data["node"] = node_inner
    node["data"] = node_data
    return node


print("Fetching MCPTools template from Langflow...")
canonical = get_mcp_tools_template()
if not canonical:
    print("[ERROR] Could not fetch MCPTools template from /api/v1/all")
    exit(1)

code_len = len(canonical.get("template", {}).get("code", {}).get("value", ""))
print(f"MCPTools template fetched ({code_len} chars of code)")

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

    mcp_count = sum(1 for n in nodes if n.get("data", {}).get("type") == "MCPTools")
    print(f"\nFlow: {flow_name} ({mcp_count} MCPTools nodes)")

    fixed_nodes = [inject_code_into_node(n, canonical) for n in nodes]
    data["nodes"] = fixed_nodes

    new_raw = json.dumps(data, ensure_ascii=False)
    cur.execute("UPDATE flow SET data = ? WHERE id = ?", (new_raw, flow_id))
    print(f"  [OK] Saved {flow_name}")

conn.commit()
conn.close()
print("\nAll flows updated.")
