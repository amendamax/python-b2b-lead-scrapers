import sqlite3
import subprocess
import os

print("[*] Verificam inregistrari noi din bazele de date locale pentru Cloudflare D1...")

def escape_sql(val):
    if val is None:
        return ""
    return str(val).replace("'", "''")

def sync_site(name, db_path, query, url_template, site_id):
    if not os.path.exists(db_path):
        print(f"[-] {name}: Nu s-a gasit baza de date {db_path}")
        return
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    rows = c.execute(query).fetchall()
    conn.close()
    
    if not rows:
        print(f"[*] {name}: 0 inregistrari.")
        return
        
    vals = [f"('{site_id}', '{escape_sql(url_template.format(slug=r[0]))}', 0)" for r in rows if r[0]]
    if not vals:
        return

    # Inseram in batch-uri de 400
    for i in range(0, len(vals), 400):
        chunk = vals[i:i+400]
        sql = "INSERT OR IGNORE INTO urls_queue (site_id, url, is_indexed) VALUES\n  " + ",\n  ".join(chunk) + ";"
        tmp_file = f"tmp_sync_{site_id}.sql"
        with open(tmp_file, "w", encoding="utf-8") as f:
            f.write(sql)
        subprocess.run(["npx.cmd", "wrangler", "d1", "execute", "radar-network-db", f"--file={tmp_file}", "--remote", "-y"], capture_output=True)
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
            
    print(f"[+] {name}: Sincronizate {len(vals)} URL-uri potential noi in Cloudflare D1.")

sync_site("JobScamRadar", "job-scam-radar/database.db", "SELECT slug FROM job_scam_reports", "https://jobscamradar.com/scammer/{slug}", "jobscam")
sync_site("PillScamRadar", "pill-scam-radar/scams.db", "SELECT slug FROM regulatory_scam_reports", "https://pillscamradar.com/scam/{slug}", "pillscam")
sync_site("IsBrokerSafe", "dating-photo-checker/database.db", "SELECT slug FROM regulatory_scam_reports", "https://isbrokersafe.com/scam-reports/{slug}", "broker")
sync_site("VerifyDating", "dating-photo-checker/database.db", "SELECT slug FROM dating_scam_profiles", "https://verifydating.net/scammer/{slug}", "dating")
sync_site("AppScamRadar", "app-scam-radar/app_scams.db", "SELECT slug FROM malicious_apps", "https://appscamradar.com/report/{slug}", "appscam")

print("[*] Sincronizare Cloudflare D1 finalizata cu succes!")
