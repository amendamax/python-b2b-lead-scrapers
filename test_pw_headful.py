import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        print("[*] Lansez browser-ul Chromium in mod HEADFUL (vizibil)...")
        # headless=False face ca browserul sa apara ca o fereastra reala pe desktopul tau
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        try:
            print("[*] Navighez la Upwork...")
            response = await page.goto('https://www.upwork.com/nx/search/jobs/?q=data+scraping&sort=recency', timeout=30000)
            print("Status:", response.status)
            title = await page.title()
            print("Page Title:", title)
            
            # Asteptam cateva secunde pentru eventualele provocari automate
            await page.wait_for_timeout(5000)
            
            title = await page.title()
            print("Page Title dupa asteptare:", title)
            
            # Incercam sa gasim joburile
            await page.wait_for_selector('article, [data-test="job-tile-list"]', timeout=15000)
            print("[+] Succes! Am gasit joburile in mod HEADFUL!")
            
            jobs = await page.query_selector_all('article h2, [data-test="job-tile-list"] h2')
            print(f"[+] Am gasit {len(jobs)} joburi pe prima pagina:")
            for i, job in enumerate(jobs[:3]):
                text = await job.inner_text()
                print(f"   {i+1}. {text}")
                
        except Exception as e:
            print("[-] Eroare:", e)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
