import asyncio
import json
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def get_upwork_jobs():
    print("[*] Lansam browser-ul pentru a colecta joburi reale de pe Upwork...\n")
    
    async with Stealth().use_async(async_playwright()) as p:
        # Launching Chromium in headful mode with realistic parameters to bypass Cloudflare
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--start-maximized"
            ]
        )
        context = await browser.new_context(
            no_viewport=True,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        urls_to_search = [
            ("Python & Web Scraping", "https://www.upwork.com/nx/search/jobs/?q=web+scraping+python&sort=recency"),
            ("Data Extraction & Lead Gen", "https://www.upwork.com/nx/search/jobs/?q=data+extraction+lead&sort=recency"),
            ("FastAPI & Automation", "https://www.upwork.com/nx/search/jobs/?q=fastapi+python&sort=recency")
        ]

        found_jobs = []

        for category, url in urls_to_search:
            print(f"[*] Navigam pe: {category} ({url})")
            try:
                await page.goto(url, timeout=30000, wait_until="domcontentloaded")
                await page.wait_for_timeout(4000)

                # Solve or wait if cloudflare challenge appears
                title = await page.title()
                if "Challenge" in title or "Just a moment" in title:
                    print("    [-] Asteptam 8 secunde pentru Cloudflare...")
                    await page.wait_for_timeout(8000)

                # Wait for job tiles
                try:
                    await page.wait_for_selector('article', timeout=10000)
                except Exception:
                    pass

                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')
                
                job_tiles = soup.find_all('article')
                print(f"    [+] Am gasit {len(job_tiles)} joburi pe pagina.")

                for tile in job_tiles[:3]:
                    title_elem = tile.find('h2') or tile.find('a', attrs={"data-test": "job-title-link"})
                    if not title_elem:
                        continue
                    title_text = title_elem.get_text(strip=True)

                    link_elem = tile.find('a', href=re.compile(r'/jobs/~'))
                    if not link_elem:
                        continue
                    job_url = "https://www.upwork.com" + link_elem['href']

                    desc_elem = tile.find('p', attrs={"data-test": "job-description"}) or tile.find('span', attrs={"data-test": "job-description-text"})
                    desc_text = desc_elem.get_text(strip=True) if desc_elem else "Fara descriere"

                    details_text = tile.get_text(" | ")

                    found_jobs.append({
                        "category": category,
                        "title": title_text,
                        "url": job_url,
                        "details": details_text[:200],
                        "desc": desc_text[:400]
                    })

            except Exception as e:
                print(f"    [-] Eroare: {e}")

        await browser.close()

        with open("real_upwork_jobs.json", "w", encoding="utf-8") as f:
            json.dump(found_jobs, f, indent=2, ensure_ascii=False)

        print(f"\n[+] Salvat {len(found_jobs)} joburi reale in real_upwork_jobs.json")

if __name__ == "__main__":
    asyncio.run(get_upwork_jobs())
