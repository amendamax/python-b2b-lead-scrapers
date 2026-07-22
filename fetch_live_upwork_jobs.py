import asyncio
import re
import html
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

SEARCH_CATEGORIES = [
    {
        "nume": "Web & Data Scraping",
        "url": "https://www.upwork.com/nx/search/jobs/?amount=50-&contractor_tier=2,3&payment_verified=1&q=web+scraping&sort=recency"
    },
    {
        "nume": "Python & Automation",
        "url": "https://www.upwork.com/nx/search/jobs/?amount=50-&contractor_tier=2,3&payment_verified=1&q=python+automation&sort=recency"
    },
    {
        "nume": "B2B Lead Generation / Extraction",
        "url": "https://www.upwork.com/nx/search/jobs/?amount=50-&contractor_tier=2,3&payment_verified=1&q=lead+scraping&sort=recency"
    },
    {
        "nume": "FastAPI & AI Integration",
        "url": "https://www.upwork.com/nx/search/jobs/?amount=50-&contractor_tier=2,3&payment_verified=1&q=fastapi&sort=recency"
    }
]

async def fetch_jobs():
    print("[*] Lansam Playwright Chromium (stealth mode) pentru scanare live Upwork...\n")
    
    async with Stealth().use_async(async_playwright()) as p:
        # Launch browser in headless mode with user-agent
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()

        all_results = []

        for category in SEARCH_CATEGORIES:
            nume = category["nume"]
            url = category["url"]
            print(f"=== Scanam categoria: {nume} ===")
            
            try:
                response = await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(3000) # asteptam incarcare elemente dinamice
                
                title = await page.title()
                print(f"-> Titlu pagina: {title}")
                
                if "Challenge" in title or "Just a moment" in title:
                    print("   [-] Cloudflare Challenge detectat. Asteptam 5 secunde...")
                    await page.wait_for_timeout(5000)
                    title = await page.title()

                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                # Gasim cardurile de joburi
                job_tiles = soup.find_all(['article', 'section'], attrs={"data-test": "job-tile-list"})
                if not job_tiles:
                    job_tiles = soup.find_all('article')
                    
                print(f"   [+] Am gasit {len(job_tiles)} carduri brute de joburi.\n")

                for tile in job_tiles[:5]: # Primele 5 cele mai noi per categorie
                    title_elem = tile.find('h2') or tile.find('a', attrs={"data-test": "job-title-link"})
                    if not title_elem:
                        continue
                    title_text = title_elem.get_text(strip=True)

                    link_elem = tile.find('a', href=re.compile(r'/jobs/~'))
                    if not link_elem:
                        continue
                    job_url = "https://www.upwork.com" + link_elem['href']

                    desc_elem = tile.find('p', attrs={"data-test": "job-description"}) or tile.find('span', attrs={"data-test": "job-description-text"})
                    desc_text = desc_elem.get_text(strip=True) if desc_elem else "Fara descriere in previzualizare."

                    details_text = tile.get_text(" | ")
                    
                    # Extrage Buget / Hourly
                    budget_text = "Nespecificat"
                    budget_match = re.search(r'Est\.\s*Budget:\s*\$([\d,]+)|Fixed-price\s*-\s*Est\.\s*budget:\s*\$([\d,]+)', details_text, re.IGNORECASE)
                    if budget_match:
                        budget_text = f"${budget_match.group(1) or budget_match.group(2)}"

                    hourly_text = "Nespecificat"
                    hourly_match = re.search(r'Hourly:\s*(\$[\d\.-]+)|Hourly\s*Range:\s*(\$[\d\.-]+)', details_text, re.IGNORECASE)
                    if hourly_match:
                        hourly_text = hourly_match.group(1) or hourly_match.group(2)

                    all_results.append({
                        "categoria": nume,
                        "titlu": title_text,
                        "url": job_url,
                        "buget": budget_text,
                        "tarif_orar": hourly_text,
                        "descriere": desc_text[:350]
                    })

            except Exception as e:
                print(f"   [-] Eroare la scanarea categoriei {nume}: {e}")

        await browser.close()

        print("\n=======================================================")
        print(f"🎉 REZULTATE FINALE: Am colectat {len(all_results)} joburi!")
        print("=======================================================\n")
        
        for idx, job in enumerate(all_results, 1):
            print(f"[{idx}] [{job['categoria']}] {job['titlu']}")
            print(f"    💰 Buget: {job['buget']} | ⏱️ Orar: {job['tarif_orar']}")
            print(f"    📝 Descriere: {job['descriere']}...")
            print(f"    🔗 Link: {job['url']}")
            print("-" * 60)

if __name__ == "__main__":
    asyncio.run(fetch_jobs())
