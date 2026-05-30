import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://secure.utah.gov/llv/search/index.html")
        title = await page.title()
        print(f"Title: {title}")
        
        # Check if the form is loaded
        full_name_input = await page.query_selector("input[name='fullName']")
        print("fullName input found:", full_name_input is not None)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
