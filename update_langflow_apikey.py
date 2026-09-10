import sqlite3
import sys
import base64

SECRET_FILE = sys.argv[1]
DB_PATH = sys.argv[2]
NEW_API_KEY = sys.argv[3]

with open(SECRET_FILE, "rb") as f:
    raw = f.read().strip()

# Langflow stores the key as raw base64 — pad it to proper Fernet key (44 chars)
key_str = raw.decode("utf-8")
# Add padding if needed
padding = 4 - (len(key_str) % 4)
if padding != 4:
    key_str += "=" * padding
key_bytes = key_str.encode("utf-8")

print(f"Key (padded): {key_str[:20]}... ({len(key_bytes)} bytes)")

from cryptography.fernet import Fernet
fernet = Fernet(key_bytes)
encrypted = fernet.encrypt(NEW_API_KEY.encode()).decode()
print(f"Encrypted OK: {encrypted[:50]}...")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute(
    "UPDATE variable SET value = ? WHERE name = 'OPENAI_COMPATIBLE_API_KEY' AND type = 'Credential'",
    (encrypted,)
)
print(f"Updated OPENAI_COMPATIBLE_API_KEY: {cur.rowcount} row(s)")
conn.commit()
conn.close()
print("Done!")
