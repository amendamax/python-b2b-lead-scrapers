import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def main():
    # Asigura aplicarea automata a metodelor de stealth peste contextul asincron Playwright
    async with Stealth().use_async(async_playwright()) as p:
        print("[*] Lansez browser-ul Chromium (Stealth)...")
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        try:
            print("[*] Navighez la Upwork...")
            response = await page.goto('https://www.upwork.com/nx/search/jobs/?q=data+scraping&sort=recency', timeout=30000)
            print("Status:", response.status)
            title = await page.title()
            print("Page Title:", title)
            
            # Verificam daca am trecut
            if "Challenge" in title or "Just a moment" in title:
                print("[-] Blocat de Cloudflare. Incercam screenshot...")
                await page.screenshot(path="cloudflare_block.png")
            else:
                print("[+] Am trecut de Cloudflare!")
                await page.wait_for_selector('article, [data-test="job-tile-list"]', timeout=10000)
                print("[+] Job tiles incarcate cu succes!")
                
                # Extragem titlurile primelor joburi pentru confirmare
                jobs = await page.query_selector_all('article h2, [data-test="job-tile-list"] h2')
                print(f"[+] Am gasit {len(jobs)} joburi pe prima pagina:")
                for i, job in enumerate(jobs[:3]):
                    text = await job.inner_text()
                    print(f"   {i+1}. {text}")
                    
        except Exception as e:
            print("[-] Eroare:", e)
            await page.screenshot(path="error.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
