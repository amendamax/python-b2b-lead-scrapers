import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth

async def run_stealth_scraper(target_url: str):
    print("[*] Starting Stealth Playwright Scraper...")
    
    # Initialize playwright-stealth asynchronous wrapper
    async with Stealth().use_async(async_playwright()) as p:
        print("[*] Launching Chromium browser (Stealth)...")
        # Launch browser. Set headless=False to watch the browser execution visually during local debugging.
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # Create browser context with customized user agent and screen viewport size
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        page = await context.new_page()
        
        try:
            print(f"[*] Navigating to: {target_url}")
            response = await page.goto(target_url, wait_until="domcontentloaded", timeout=30000)
            
            print(f"[+] Response Status: {response.status if response else 'No Response'}")
            title = await page.title()
            print(f"[+] Page Title: {title}")
            
            # Check if we were flagged by WAF controls like Cloudflare
            if "Challenge" in title or "Just a moment" in title or "Attention Required!" in title:
                print("[-] Blocked by Cloudflare/Akamai or a CAPTCHA shield!")
                print("[*] Saving screenshot to 'cloudflare_block.png' for verification...")
                await page.screenshot(path="cloudflare_block.png")
            else:
                print("[+] Successfully bypassed security controls and loaded target page!")
                # Optional: Extract some page text to verify data loading
                h1_elements = await page.query_selector_all("h1")
                print(f"[+] Found {len(h1_elements)} H1 headers on the page:")
                for i, h1 in enumerate(h1_elements[:3]):
                    text = await h1.inner_text()
                    print(f"   {i+1}. {text.strip()}")
                    
        except Exception as e:
            print(f"[!] An execution error occurred: {e}")
            await page.screenshot(path="error_screenshot.png")
            
        finally:
            print("[*] Closing browser instance.")
            await browser.close()

if __name__ == "__main__":
    # Target URL can be set to any public website, or verification tools like bot.sannysoft.com
    target = "https://bot.sannysoft.com/"
    asyncio.run(run_stealth_scraper(target))
