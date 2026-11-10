import sqlite3
import os
import shutil

if os.path.exists('d1_chunks'):
    shutil.rmtree('d1_chunks')
os.makedirs('d1_chunks', exist_ok=True)

def escape_sql(val):
    if val is None:
        return ""
    return str(val).replace("'", "''")

def write_chunk_files(prefix, records, rows_per_stmt=250, stmts_per_file=40):
    # rows_per_file = 250 * 40 = 10,000 rows per file (~500 KB)
    rows_per_file = rows_per_stmt * stmts_per_file
    file_idx = 1
    total_files = (len(records) + rows_per_file - 1) // rows_per_file
    
    for f_start in range(0, len(records), rows_per_file):
        file_chunk = records[f_start:f_start + rows_per_file]
        stmts = []
        for s_start in range(0, len(file_chunk), rows_per_stmt):
            stmt_chunk = file_chunk[s_start:s_start + rows_per_stmt]
            vals = [f"('{escape_sql(s)}', '{escape_sql(u)}', {idx})" for s, u, idx in stmt_chunk]
            sql = "INSERT OR IGNORE INTO urls_queue (site_id, url, is_indexed) VALUES\n  " + ",\n  ".join(vals) + ";"
            stmts.append(sql)
            
        file_path = f"d1_chunks/{prefix}_{file_idx}.sql"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(stmts))
        print(f"Generated {file_path} ({len(file_chunk)} records)")
        file_idx += 1
    return file_idx - 1

# 1. PillScam (20,647 records)
print("\n--- Exporting PillScam ---")
records_pill = []
conn = sqlite3.connect('pill-scam-radar/scams.db')
c = conn.cursor()
for slug, is_idx in c.execute("SELECT slug, is_indexed FROM regulatory_scam_reports WHERE slug IS NOT NULL"):
    records_pill.append(('pillscam', f"https://pillscamradar.com/scam/{slug}", 1 if is_idx else 0))
conn.close()
count_pill_files = write_chunk_files('pill', records_pill)

# 2. Broker (34,671 records)
print("\n--- Exporting Broker ---")
records_broker = []
conn = sqlite3.connect('dating-photo-checker/database.db')
c = conn.cursor()
for row_id, slug in c.execute("SELECT id, slug FROM regulatory_scam_reports WHERE slug IS NOT NULL"):
    is_idx = 1 if row_id <= 10 else 0
    records_broker.append(('broker', f"https://isbrokersafe.com/scam-reports/{slug}", is_idx))
conn.close()
count_broker_files = write_chunk_files('broker', records_broker)

# 3. Dating (35,347 records)
print("\n--- Exporting Dating ---")
records_dating = []
conn = sqlite3.connect('dating-photo-checker/database.db')
c = conn.cursor()
for slug, in c.execute("SELECT slug FROM dating_scam_profiles WHERE slug IS NOT NULL"):
    records_dating.append(('dating', f"https://verifydating.net/scammer/{slug}", 0))
conn.close()
count_dating_files = write_chunk_files('dating', records_dating)

print(f"\nAll chunks ready! Pill: {count_pill_files}, Broker: {count_broker_files}, Dating: {count_dating_files}")
