import sqlite3
import os

DB_PATH = "database.db"

try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, created_at, payment_status, scam_probability, matches_count, image_path, email 
        FROM scans 
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    total_scans = len(rows)
    total_paid = sum(1 for r in rows if r[2] == 'paid')
    revenue = total_paid * 4.99
    
    cards_html = ""
    for row in rows:
        scan_id, created_at, payment_status, scam_prob, matches, img_path, email = row
        img_name = os.path.basename(img_path) if img_path else ""
        img_url = f"/uploads/{img_name}" if img_name else "#"
        
        status_badge = '<span style="background:#10B981;color:#fff;padding:4px 10px;border-radius:12px;font-size:12px;font-weight:700;">PAID ($4.99)</span>' if payment_status == "paid" else '<span style="background:#EF4444;color:#fff;padding:4px 10px;border-radius:12px;font-size:12px;font-weight:700;">UNPAID</span>'
        
        prob_color = "#EF4444" if scam_prob >= 70 else "#F59E0B" if scam_prob >= 40 else "#10B981"
        
        formatted_date = created_at.replace("T", " ")[:19] if created_at else "N/A"
        
        unlock_btn = ""
        if payment_status != "paid":
            unlock_btn = f"""
            <button onclick="markPaid('{scan_id}')" style="background:#10B981;color:#fff;border:none;padding:8px 12px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;margin-top:8px;transition:background 0.2s;width:100%;" onmouseover="this.style.background='#059669'" onmouseout="this.style.background='#10B981'">🔓 Unlock Scan</button>
            """
        
        cards_html += f"""
        <div style="background:#1E293B;border-radius:16px;overflow:hidden;border:1px solid #334155;display:flex;flex-direction:column;box-shadow:0 4px 6px -1px rgba(0,0,0,0.3);">
            <div style="height:220px;background:#0F172A;display:flex;align-align:center;justify-content:center;overflow:hidden;position:relative;padding:10px;">
                <a href="{img_url}" target="_blank" style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;">
                    <img src="{img_url}" style="max-width:100%;max-height:100%;object-fit:contain;border-radius:8px;" alt="Uploaded Scan"/>
                </a>
            </div>
            <div style="padding:16px;flex:1;display:flex;flex-direction:column;gap:10px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    {status_badge}
                    <span style="font-size:12px;color:#94A3B8;">{formatted_date}</span>
                </div>
                <div style="font-size:13px;color:#CBD5E1;font-weight:600;word-break:break-all;">
                    ID: <code style="background:#0F172A;padding:2px 6px;border-radius:4px;color:#38BDF8;">{scan_id[:13]}...</code>
                </div>
                <div style="display:flex;gap:10px;margin-top:4px;">
                    <div style="background:#0F172A;padding:6px 12px;border-radius:8px;font-size:13px;color:#F8FAFC;flex:1;text-align:center;border:1px solid #334155;">
                        Risk: <strong style="color:{prob_color};">{scam_prob}%</strong>
                    </div>
                    <div style="background:#0F172A;padding:6px 12px;border-radius:8px;font-size:13px;color:#F8FAFC;flex:1;text-align:center;border:1px solid #334155;">
                        Matches: <strong style="color:#38BDF8;">{matches}</strong>
                    </div>
                </div>
                {f'<div style="font-size:12px;color:#10B981;margin-top:4px;word-break:break-all;">📧 {email}</div>' if email else ''}
                {unlock_btn}
            </div>
        </div>
        """
    print("SUCCESS: Code executed fine.")
    print(f"Total scans: {total_scans}")
except Exception as e:
    print(f"ERROR: {e}")
