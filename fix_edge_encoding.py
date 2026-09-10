"""
Fix encoding corruption in Langflow flow edges stored in SQLite DB.
The character œ (\u0153) was incorrectly substituted for " (double-quote)
inside JSON handle strings, causing Langflow to fail parsing the graph.
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


def fix_handle(handle: str) -> str:
    """Replace œ back to " in handle JSON strings."""
    if handle is None:
        return handle
    # \u0153 is œ — replace with double-quote
    return handle.replace("\u0153", '"')


def fix_edge(edge: dict) -> dict:
    edge = dict(edge)
    edge["sourceHandle"] = fix_handle(edge.get("sourceHandle"))
    edge["targetHandle"] = fix_handle(edge.get("targetHandle"))
    # Also fix the edge id which contains the handles
    if "id" in edge:
        edge["id"] = edge["id"].replace("\u0153", '"')
    return edge


def fix_flow_data(data: dict) -> dict:
    edges = data.get("edges", [])
    fixed_edges = [fix_edge(e) for e in edges]
    data["edges"] = fixed_edges
    return data


conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

fixed_count = 0
for flow_name in ERGON_FLOWS:
    cur.execute("SELECT id, data FROM flow WHERE name = ?", (flow_name,))
    row = cur.fetchone()
    if not row:
        print(f"[SKIP] Flow not found: {flow_name}")
        continue

    flow_id, raw_data = row
    data = json.loads(raw_data)
    fixed_data = fix_flow_data(data)

    # Verify fix
    edges_after = fixed_data.get("edges", [])
    has_corruption = any("\u0153" in json.dumps(e) for e in edges_after)
    if has_corruption:
        print(f"[ERROR] Still has corruption in {flow_name}")
        continue

    new_raw = json.dumps(fixed_data, ensure_ascii=False)
    cur.execute("UPDATE flow SET data = ? WHERE id = ?", (new_raw, flow_id))
    print(f"[OK] Fixed {flow_name}  ({len(edges_after)} edges)")
    fixed_count += 1

conn.commit()
conn.close()
print(f"\nDone - fixed {fixed_count}/{len(ERGON_FLOWS)} flows.")
