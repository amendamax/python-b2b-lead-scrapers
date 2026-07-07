import sqlite3
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

db_files = [
    r"C:\Users\bratu\.gemini\antigravity\conversations\15cef107-4d50-470f-99e0-0223d674ea99.db",
    r"C:\Users\bratu\.gemini\antigravity\conversations\01129faf-8373-4162-96a0-0ca6ad2410af.db"
]

pattern = re.compile(rb'[a-zA-Z0-9\s.,!?:;\-_/\\\'"\(\)=+*&%#@\x80-\xff]{15,}')

for db in db_files:
    if not os.path.exists(db):
        continue
    
    print(f"\n==================== DIALOGUE FROM {os.path.basename(db)} ====================")
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute("SELECT idx, step_payload FROM steps ORDER BY idx;")
    rows = cursor.fetchall()
    for idx, payload in rows:
        if payload:
            matches = pattern.findall(payload)
            for m in matches:
                try:
                    s = m.decode('utf-8', errors='ignore').strip()
                    # Filter out system prompt parts, tool lists, and IDE feedback
                    if "write_file(" in s or "read_file(" in s or "run_command(" in s:
                        continue
                    if "web_application_development" in s or "System Prompt" in s or "identity" in s or "user_information" in s:
                        continue
                    if "As IDE feedback, the following lint errors" in s or "toolAction" in s or "toolSummary" in s:
                        continue
                    # Keep strings that have spaces and lowercase letters (real language)
                    words = s.split()
                    if len(words) >= 4 and any(c.islower() for c in s):
                        # Filter out common binary structures
                        if not s.startswith("sessionID") and not s.startswith("cascade_id"):
                            print(f"  [Step {idx}]: {s}")
                except Exception:
                    pass
    conn.close()










