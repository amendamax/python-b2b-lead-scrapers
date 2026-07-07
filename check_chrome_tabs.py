import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://127.0.0.1:9222")
            print("Connected to Chrome via CDP")
            contexts = browser.contexts
            print(f"Number of contexts: {len(contexts)}")
            for idx, context in enumerate(contexts):
                pages = context.pages
                print(f"Context {idx} has {len(pages)} pages:")
                for p_idx, page in enumerate(pages):
                    try:
                        title = await page.title()
                        url = page.url
                        print(f"  Page {p_idx}: Title='{title}', URL='{url}'")
                    except Exception as pe:
                        print(f"  Page {p_idx}: Error getting details: {pe}")
            await browser.close()
        except Exception as e:
            print(f"Error connecting to CDP: {e}")

if __name__ == "__main__":
    asyncio.run(main())
