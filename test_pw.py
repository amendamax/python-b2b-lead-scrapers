import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        # Set a standard User-Agent to look like a real desktop Chrome browser
        await page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9"
        })
        try:
            print("Navigating to Upwork...")
            response = await page.goto('https://www.upwork.com/nx/search/jobs/?q=data+scraping&sort=recency', timeout=30000)
            print("Status:", response.status)
            title = await page.title()
            print("Page Title:", title)
            
            # Wait for job tiles to load
            await page.wait_for_selector('article, [data-test="job-tile-list"]', timeout=10000)
            print("Job tiles loaded successfully!")
            
            # Get the page source or count job elements
            job_elements = await page.query_selector_all('article, [data-test="job-tile-list"]')
            print("Found", len(job_elements), "job elements.")
            
        except Exception as e:
            print("Error during navigation/extraction:", e)
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
