import sqlite3
import os

dbs = [
    ('JobScam', 'job-scam-radar/database.db'),
    ('PillScam', 'pill-scam-radar/scams.db'),
    ('Broker', 'broker-verifier/database.db'),
    ('Dating', 'dating-photo-checker/database.db'),
    ('AppScam', 'app-scam-radar/app_scams.db')
]

for name, path in dbs:
    if not os.path.exists(path):
        print(f"[-] {name}: {path} not found")
        continue
    conn = sqlite3.connect(path)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [r[0] for r in c.fetchall()]
    print(f"\n[+] {name} ({path}):")
    for t in tables:
        try:
            cnt = conn.execute(f"SELECT COUNT(*) FROM \"{t}\"").fetchone()[0]
            # Check for columns
            c.execute(f"PRAGMA table_info(\"{t}\")")
            cols = [col[1] for col in c.fetchall()]
            print(f"    - Table '{t}': {cnt} rows | Cols: {', '.join(cols[:8])}...")
        except Exception as e:
            print(f"    - Table '{t}': error {e}")
    conn.close()
