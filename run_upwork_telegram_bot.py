import asyncio
import os
import sqlite3
import requests
import re
import html
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

TELEGRAM_TOKEN = "8677428441:AAEKsz-dfn_zlF7asRXEy1qtutCYPQOdLdE"
TELEGRAM_CHAT_ID = "1367224738"

UPWORK_SEARCH_QUERIES = [
    {
        "nume": "Python & Scraping / Anti-Bot",
        "url": "https://www.upwork.com/nx/search/jobs/?amount=300-&contractor_tier=2,3&hourly_rate=40-&payment_verified=1&q=python+scraping&sort=recency"
    },
    {
        "nume": "Playwright & Browser Automation",
        "url": "https://www.upwork.com/nx/search/jobs/?amount=300-&contractor_tier=2,3&hourly_rate=40-&payment_verified=1&q=playwright+selenium&sort=recency"
    },
    {
        "nume": "Data Extraction & Lead Generation",
        "url": "https://www.upwork.com/nx/search/jobs/?amount=300-&contractor_tier=2,3&hourly_rate=40-&payment_verified=1&q=data+extraction+leads&sort=recency"
    },
    {
        "nume": "FastAPI & Python Backend",
        "url": "https://www.upwork.com/nx/search/jobs/?amount=300-&contractor_tier=2,3&hourly_rate=40-&payment_verified=1&q=fastapi+python&sort=recency"
    },
    {
        "nume": "MQL5 & Algorithmic Trading Bots",
        "url": "https://www.upwork.com/nx/search/jobs/?amount=300-&contractor_tier=2,3&hourly_rate=40-&payment_verified=1&q=mql5+trading&sort=recency"
    }
]

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "upwork_jobs.db")
CHECK_INTERVAL_SECONDS = 180

total_alerts_sent = 0
last_scan_time = "Niciodată"
current_status = "Inițializare..."
recent_alerts_log = []

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sent_jobs (
            guid TEXT PRIMARY KEY,
            title TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def is_job_sent(guid):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM sent_jobs WHERE guid = ?", (guid,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_job_as_sent(guid, title):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO sent_jobs (guid, title) VALUES (?, ?)", (guid, title))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def trimite_telegram(mesaj):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        res = requests.post(url, json=payload, timeout=10)
        return res.status_code == 200
    except Exception as e:
        return False

def render_dashboard(active_category=None, countdown=None):
    """Curăță ecranul și desenează un panou de control elegant, fără spam de text."""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print(" 🚀 UPWORK ELITE RADAR BOT  |  MINIM $300 FIX / $40+/ORĂ")
    print("=" * 70)
    print(f" 🟢 Stare Sistem:      {current_status}")
    print(f" ⏰ Ultima Scanare:    {last_scan_time}")
    print(f" 📬 Alerte Trimise:    {total_alerts_sent} pe Telegram")
    print("-" * 70)
    print(" 🎯 Categorii Monitorizate:")
    for q in UPWORK_SEARCH_QUERIES:
        if active_category and q['nume'] == active_category:
            print(f"   ▶️ [SCANARE ACTIVĂ] {q['nume']}")
        else:
            print(f"   ✓  {q['nume']}")
    print("-" * 70)
    if recent_alerts_log:
        print(" 🔔 Ultimele Alerte Identificate:")
        for log in recent_alerts_log[-3:]:
            print(f"   🔥 {log}")
        print("-" * 70)
    if countdown is not None:
        print(f" ⏳ Următoarea verificare automată în: {countdown} secunde...")
    print("=" * 70)

async def start_monitor():
    global last_scan_time, current_status, total_alerts_sent
    
    init_db()
    current_status = "Lansare browser invizibil..."
    render_dashboard()
    
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )
        page = await context.new_page()

        while True:
            last_scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            current_status = "Scanare în curs..."
            
            for query in UPWORK_SEARCH_QUERIES:
                nume_cautare = query["nume"]
                url_cautare = query["url"]
                
                render_dashboard(active_category=nume_cautare)
                
                try:
                    await page.goto(url_cautare, timeout=35000, wait_until="domcontentloaded")
                    await page.wait_for_timeout(3500)
                    
                    title = await page.title()
                    if "Challenge" in title or "Just a moment" in title:
                        await page.wait_for_timeout(7000)
                        
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    job_tiles = soup.find_all(['article', 'section'], attrs={"data-test": "job-tile-list"})
                    if not job_tiles:
                        job_tiles = soup.find_all('article')
                    
                    for tile in reversed(job_tiles):
                        title_elem = tile.find('h2') or tile.find('a', attrs={"data-test": "job-title-link"})
                        if not title_elem:
                            continue
                        title_text = title_elem.get_text(strip=True)
                        
                        link_elem = tile.find('a', href=re.compile(r'/jobs/~'))
                        if not link_elem:
                            continue
                        
                        job_url = "https://www.upwork.com" + link_elem['href']
                        guid_match = re.search(r'/jobs/(~[\w\d]+)', job_url)
                        guid = guid_match.group(1) if guid_match else job_url
                        
                        if is_job_sent(guid):
                            continue
                            
                        desc_elem = tile.find('p', attrs={"data-test": "job-description"}) or tile.find('span', attrs={"data-test": "job-description-text"})
                        desc_text = desc_elem.get_text(strip=True) if desc_elem else "Descriere disponibilă pe Upwork."
                        
                        details_text = tile.get_text(" | ")
                        
                        if "Payment verified" not in details_text:
                            continue
                        if "Entry level" in details_text:
                            continue
                            
                        budget_text = "Nespecificat"
                        hourly_text = "Nespecificat"
                        is_valid = False
                        
                        budget_match = re.search(r'Est\.\s*Budget:\s*\$([\d,]+)|Fixed-price\s*-\s*Est\.\s*budget:\s*\$([\d,]+)', details_text, re.IGNORECASE)
                        if budget_match:
                            budget_val = budget_match.group(1) or budget_match.group(2)
                            budget_val_clean = int(budget_val.replace(',', ''))
                            if budget_val_clean >= 300:
                                budget_text = f"${budget_val_clean}"
                                is_valid = True
                                
                        hourly_match = re.search(r'Hourly:\s*(\$[\d\.-]+)|Hourly\s*Range:\s*(\$[\d\.-]+)', details_text, re.IGNORECASE)
                        if hourly_match:
                            hourly_val = hourly_match.group(1) or hourly_match.group(2)
                            rates = re.findall(r'\$?([\d\.]+)', hourly_val)
                            if rates:
                                max_rate = max([float(r) for r in rates])
                                if max_rate >= 40.0:
                                    hourly_text = hourly_val
                                    is_valid = True
                                    
                        if not is_valid:
                            continue
                            
                        mesaj = (
                            f"<b>🔥 JOB DE ELITĂ NOU - {nume_cautare.upper()}!</b>\n\n"
                            f"<b>📌 Titlu:</b> {html.escape(title_text)}\n"
                            f"<b>💰 Buget Fix:</b> {budget_text}\n"
                            f"<b>⏱️ Tarif Orar:</b> {hourly_text}\n\n"
                            f"<b>📝 Descriere:</b>\n<i>{html.escape(desc_text[:500])}...</i>\n\n"
                            f"<b>🔗 Link direct de aplicare:</b>\n<a href='{job_url}'>Deschide Jobul pe Upwork</a>"
                        )
                        
                        trimite_telegram(mesaj)
                        mark_job_as_sent(guid, title_text)
                        total_alerts_sent += 1
                        recent_alerts_log.append(f"{title_text[:40]}... ({budget_text} | {hourly_text})")
                        render_dashboard(active_category=nume_cautare)
                        
                except Exception as e:
                    pass
                    
                await page.wait_for_timeout(2000)
                
            current_status = "🟢 În așteptare (Sistem activ)"
            
            # Numărătoare inversă curată
            for rem in range(CHECK_INTERVAL_SECONDS, 0, -10):
                render_dashboard(countdown=rem)
                await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(start_monitor())
