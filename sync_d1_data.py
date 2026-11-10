import sqlite3
import os

os.makedirs('d1_chunks', exist_ok=True)

def escape_sql(val):
    if val is None:
        return ""
    return str(val).replace("'", "''")

def create_insert_statements(records, chunk_size=400):
    statements = []
    for i in range(0, len(records), chunk_size):
        chunk = records[i:i + chunk_size]
        vals = []
        for site_id, url, is_indexed in chunk:
            vals.append(f"('{escape_sql(site_id)}', '{escape_sql(url)}', {is_indexed})")
        sql = f"INSERT OR IGNORE INTO urls_queue (site_id, url, is_indexed) VALUES\n  " + ",\n  ".join(vals) + ";"
        statements.append(sql)
    return "\n\n".join(statements)

# 1. JobScam
records_job = []
conn = sqlite3.connect('job-scam-radar/database.db')
c = conn.cursor()
for row_id, slug in c.execute("SELECT id, slug FROM job_scam_reports WHERE slug IS NOT NULL"):
    is_idx = 1 if row_id <= 156 else 0
    records_job.append(('jobscam', f"https://jobscamradar.com/scammer/{slug}", is_idx))
conn.close()
print(f"JobScam records: {len(records_job)}")

# 2. AppScam
records_app = []
conn = sqlite3.connect('app-scam-radar/app_scams.db')
c = conn.cursor()
for slug, is_idx in c.execute("SELECT slug, is_indexed FROM malicious_apps WHERE slug IS NOT NULL"):
    records_app.append(('appscam', f"https://appscamradar.com/report/{slug}", 1 if is_idx else 0))
conn.close()
print(f"AppScam records: {len(records_app)}")

# Save initial test chunk
with open('d1_chunks/chunk_small_sites.sql', 'w', encoding='utf-8') as f:
    f.write(create_insert_statements(records_job + records_app))
print("Saved d1_chunks/chunk_small_sites.sql")
