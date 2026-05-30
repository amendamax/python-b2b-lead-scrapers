import asyncio
import os
import sqlite3
import requests
import re
import html
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

# =====================================================================
# ⚙️ CONFIGURARE DATE TELEGRAM & URL CĂUTARE
# =====================================================================
TELEGRAM_TOKEN = "8677428441:AAEKsz-dfn_zlF7asRXEy1qtutCYPQOdLdE"
TELEGRAM_CHAT_ID = "1367224738"

# Listează aici căutările tale de pe Upwork cu filtrele dorite, sortate după cele mai noi (recency)
UPWORK_SEARCH_QUERIES = [
    {
        "nume": "Data Scraping",
        "url": "https://www.upwork.com/nx/search/jobs/?amount=100-&contractor_tier=2,3&hourly_rate=20-&payment_verified=1&q=data+scraping&sort=recency"
    },
    {
        "nume": "Web Scraping",
        "url": "https://www.upwork.com/nx/search/jobs/?amount=100-&contractor_tier=2,3&hourly_rate=20-&payment_verified=1&q=web+scraping&sort=recency"
    },
    {
        "nume": "Python Developer",
        "url": "https://www.upwork.com/nx/search/jobs/?amount=100-&contractor_tier=2,3&hourly_rate=20-&payment_verified=1&q=python&sort=recency"
    },
    {
        "nume": "Data Extraction",
        "url": "https://www.upwork.com/nx/search/jobs/?amount=100-&contractor_tier=2,3&hourly_rate=20-&payment_verified=1&q=data+extraction&sort=recency"
    }
]

# Calea exactă de pe Windows VPS-ul tău
COOKIES_FILE = r"C:\homeupwork-bot\upwork_cookies.txt"

DB_FILE = "upwork_jobs.db"
CHECK_INTERVAL_SECONDS = 120  # Scanează o dată la 2 minute

# =====================================================================
# 🛠️ FUNCȚII DE BAZĂ (DATABASE)
# =====================================================================

def init_db():
    """Inițializează baza de date SQLite locală pentru a reține joburile trimise."""
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
    """Trimite mesaje HTML formatate pe canalul tău de Telegram."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mesaj,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            print(f"[-] Eroare Telegram (Status {response.status_code}): {response.text}")
    except Exception as e:
        print(f"[-] Eroare de rețea Telegram: {e}")

# =====================================================================
# 🔄 MONITORUL PRINCIPAL PLAYWRIGHT (CONECTARE CDP DIRECT ÎN CHROME)
# =====================================================================

async def monitor_upwork():
    print("[*] Robotul de Monitorizare Upwork (Bypass CDP Chrome) porneste...")
    init_db()
    
    # Trimite mesaj de pornire pe Telegram
    trimite_telegram("<b>🚀 Robotul de Monitorizare Upwork (Bypass CDP Chrome) este ONLINE pe VPS!</b>\n\n<i>Folosesc browserul tău real Google Chrome pentru a monitoriza cele 4 categorii setate!</i>")

    async with Stealth().use_async(async_playwright()) as p:
        # Ne conectăm direct la Chrome-ul tău real folosind IP-ul IPv4 explicit 127.0.0.1
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            context = browser.contexts[0]
            page = context.pages[0] if context.pages else await context.new_page()
            print("[+] Conectat cu succes la instanta activa de Google Chrome!")
        except Exception as e:
            print(f"[-] EROARE: Nu s-a putut conecta la Google Chrome pe portul 9222: {e}")
            print("[-] Asigura-te ca ai pornit Chrome cu optiunea --remote-debugging-port=9222 si ca toate celelalte ferestre normale de Chrome sunt inchise.")
            return

        while True:
            try:
                print(f"\n[*] Scanare noua la data/ora curenta pentru toate cele {len(UPWORK_SEARCH_QUERIES)} cautari...")
                
                for query in UPWORK_SEARCH_QUERIES:
                    nume_cautare = query["nume"]
                    url_cautare = query["url"]
                    
                    print(f"[*] Scanez categoria: {nume_cautare}...")
                    
                    # Navigăm pe pagina de căutare
                    response = await page.goto(url_cautare, timeout=45000, wait_until="load")
                    
                    title = await page.title()
                    print(f"    [*] Pagina incarcata. Titlu: {title} (Status: {response.status if response else 'Nespecificat'})")
                    
                    if "Challenge" in title or "Just a moment" in title:
                        print("    [-] Blocat de ecranul Cloudstile/Challenge. Incercam sa asteptam 10s...")
                        await page.wait_for_timeout(10000)
                        title = await page.title()
                        
                    if "Challenge" in title or "Just a moment" in title:
                        print("    [-] Tot blocat de Cloudflare. Trecem la urmatoarea cautare...")
                        await page.screenshot(path="blocked.png")
                        await page.wait_for_timeout(5000)
                        continue

                    # Așteptăm să apară lista de joburi pe ecran
                    try:
                        await page.wait_for_selector('article, [data-test="job-tile-list"]', timeout=15000)
                    except Exception:
                        print("    [-] Nu s-au putut gasi cardurile de joburi in pagina.")
                        await page.screenshot(path="no_jobs_found.png")
                        await page.wait_for_timeout(5000)
                        continue
                    
                    # Obținem codul sursă al paginii încărcate complet
                    content = await page.content()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Căutăm cardurile de joburi
                    job_tiles = soup.find_all(['article', 'section'], attrs={"data-test": "job-tile-list"})
                    if not job_tiles:
                        job_tiles = soup.find_all('article')
                        
                    print(f"    [+] Am gasit {len(job_tiles)} joburi in categoria {nume_cautare}.")
                    
                    new_jobs_count = 0
                    
                    # Parcurgem în ordine inversă (de la cel mai vechi la cel mai nou în listă)
                    for tile in reversed(job_tiles):
                        # Extrage link-ul și titlul
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
                        
                        # Verificăm dacă a fost deja trimis
                        if not is_job_sent(guid):
                            desc_elem = tile.find('p', attrs={"data-test": "job-description"}) or tile.find('span', attrs={"data-test": "job-description-text"})
                            desc_text = desc_elem.get_text(strip=True) if desc_elem else "Fara descriere disponibila in previzualizare."
                            
                            # Căutăm detaliile despre plată și aplicăm filtre stricte în memorie
                            details_text = tile.get_text(" | ")
                            
                            # 1. Filtrare după Plata Verificată
                            if "Payment verified" not in details_text:
                                print(f"    [-] Sarit (Plata neverificata): {title_text}")
                                continue
                                
                            # 2. Filtrare după Nivel Experiență (Fără Entry level)
                            if "Entry level" in details_text:
                                print(f"    [-] Sarit (Entry level): {title_text}")
                                continue

                            budget_text = "Nespecificat"
                            hourly_text = "Nespecificat"
                            
                            # 3. Filtrare după Buget Fix (Minim $100)
                            budget_match = re.search(r'Est\.\s*Budget:\s*\$([\d,]+)|Fixed-price\s*-\s*Est\.\s*budget:\s*\$([\d,]+)', details_text, re.IGNORECASE)
                            if budget_match:
                                budget_val = budget_match.group(1) or budget_match.group(2)
                                budget_val_clean = int(budget_val.replace(',', ''))
                                if budget_val_clean < 100:
                                    print(f"    [-] Sarit (Buget fix prea mic: ${budget_val_clean}): {title_text}")
                                    continue
                                budget_text = f"${budget_val}"
                                
                            # 4. Filtrare după Tarif Orar (Minim $20/h)
                            hourly_match = re.search(r'Hourly:\s*(\$[\d\.-]+)|Hourly\s*Range:\s*(\$[\d\.-]+)', details_text, re.IGNORECASE)
                            if hourly_match:
                                hourly_val = hourly_match.group(1) or hourly_match.group(2)
                                hourly_text = hourly_val
                                
                                # Extrage toate cifrele din intervalul orar (ex: "$15-$30" -> [15.0, 30.0])
                                rates = re.findall(r'\$?([\d\.]+)', hourly_val)
                                if rates:
                                    rates_float = [float(r) for r in rates]
                                    max_rate = max(rates_float)
                                    if max_rate < 20:
                                        print(f"    [-] Sarit (Tarif orar prea mic: {hourly_val}): {title_text}")
                                        continue
                            
                            # Formatăm mesajul premium de alertă cu eticheta căutării
                            mesaj = (
                                f"<b>🔥 JOB NOU - {nume_cautare.upper()}!</b>\n\n"
                                f"<b>📌 Titlu:</b> {html.escape(title_text)}\n"
                                f"<b>💰 Buget Fix:</b> {budget_text}\n"
                                f"<b>⏱️ Tarif Orar:</b> {hourly_text}\n\n"
                                f"<b>📝 Descriere:</b>\n<i>{html.escape(desc_text[:600])}...</i>\n\n"
                                f"<b>🔗 Link direct pentru aplicare:</b>\n<a href='{job_url}'>Click aici pentru a deschide jobul</a>"
                            )
                            
                            # Trimitem pe Telegram și salvăm în DB
                            trimite_telegram(mesaj)
                            mark_job_as_sent(guid, title_text)
                            new_jobs_count += 1
                            print(f"    [+] Alerta trimisa pentru: {title_text}")
                            
                    if new_jobs_count > 0:
                        print(f"    [+] S-au trimis {new_jobs_count} joburi noi din categoria {nume_cautare}.")
                    
                    # Pauză mică între categoriile căutate pentru a fi cât mai stealthy
                    await page.wait_for_timeout(5000)
                    
            except Exception as e:
                print(f"[-] Eroare in bucla de rulare: {e}")
                
            # Așteptăm durata setată
            print(f"[*] Runda finalizata. Asteptam {CHECK_INTERVAL_SECONDS} secunde pana la urmatoarea verificare...")
            await page.wait_for_timeout(CHECK_INTERVAL_SECONDS * 1000)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(monitor_upwork())
