"""
Fix edges in Ergon flows: add the 'data' field containing
{sourceHandle: {...}, targetHandle: {...}} as objects.
Langflow v1.5+ graph builder reads e["data"]["sourceHandle"]["id"]
so the 'data' sub-object is required alongside the string handles.
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
    "interview_practice",
]


def parse_handle_string(s: str) -> dict:
    """Parse a handle that is already a clean JSON string."""
    if not s:
        return {}
    # handles are stored as JSON strings (after our encoding fix)
    try:
        return json.loads(s)
    except Exception:
        return {}


def fix_edge(edge: dict) -> dict:
    edge = dict(edge)
    # If 'data' already has both sourceHandle and targetHandle as dicts, skip
    existing_data = edge.get("data", {})
    if (
        isinstance(existing_data.get("sourceHandle"), dict)
        and isinstance(existing_data.get("targetHandle"), dict)
    ):
        return edge

    sh = parse_handle_string(edge.get("sourceHandle", ""))
    th = parse_handle_string(edge.get("targetHandle", ""))

    edge["data"] = {
        "sourceHandle": sh,
        "targetHandle": th,
    }
    return edge


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
    edges = data.get("edges", [])
    fixed_edges = [fix_edge(e) for e in edges]
    data["edges"] = fixed_edges

    # Verify
    ok = all(
        isinstance(e.get("data", {}).get("sourceHandle"), dict)
        and isinstance(e.get("data", {}).get("targetHandle"), dict)
        for e in fixed_edges
    )
    if not ok:
        print(f"[ERROR] {flow_name} - data field not set correctly")
        continue

    new_raw = json.dumps(data, ensure_ascii=False)
    cur.execute("UPDATE flow SET data = ? WHERE id = ?", (new_raw, flow_id))
    print(f"[OK] {flow_name} - {len(fixed_edges)} edges fixed")

conn.commit()
conn.close()
print("Done.")
