import sqlite3
import os

db_path = "upwork_jobs.db"
if not os.path.exists(db_path):
    print("Database does not exist")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("Tables:", tables)
    for table in tables:
        tname = table[0]
        cursor.execute(f"PRAGMA table_info({tname})")
        print(f"Columns in {tname}:", cursor.fetchall())
        cursor.execute(f"SELECT COUNT(*) FROM {tname}")
        print(f"Row count in {tname}:", cursor.fetchone()[0])
        cursor.execute(f"SELECT * FROM {tname} LIMIT 5")
        print(f"First 5 rows in {tname}:", cursor.fetchall())
