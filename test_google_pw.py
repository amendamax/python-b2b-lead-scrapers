import urllib.parse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Set Romanian locale and timezone to get Romanian results
        context = browser.new_context(
            locale="ro-RO",
            timezone_id="Europe/Bucharest",
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        url = 'https://www.google.com/search?q=agentie+imobiliara+Bucuresti'
        print(f"Navigating to {url}...")
        page.goto(url)
        page.wait_for_timeout(2000)
        
        print("Page URL:", page.url)
        print("Page Title:", page.title())
        
        # Check if consent page is shown (title contains "Prima di continuare" or "Înainte de a continua")
        if "consent" in page.url or "consent" in page.title().lower() or "înainte de a continua" in page.content().lower() or "prima di continuare" in page.content().lower():
            print("Consent page detected. Trying to click accept button...")
            try:
                # Click the accept button. Google uses buttons inside a form or specific selectors.
                buttons = page.locator('button')
                count = buttons.count()
                print(f"Found {count} buttons on consent page.")
                for i in range(count):
                    txt = buttons.nth(i).text_content()
                    print(f"  Button {i}: '{txt}'")
                    if any(x in txt.lower() for x in ["acceptă tot", "accetta tutto", "accept all", "de acord", "agree"]):
                        print(f"-> Clicking button {i} ('{txt}')")
                        buttons.nth(i).click()
                        page.wait_for_timeout(3000)
                        break
            except Exception as e:
                print("Error clicking consent button:", e)
                
        # Re-check page content after consent
        print("After consent - Page URL:", page.url)
        print("After consent - Page Title:", page.title())
        
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract Google organic result links
        links = []
        for a in soup.select('a'):
            href = a.get('href', '')
            if href.startswith('http') and 'google.com' not in href:
                links.append(href)
                
        print(f"Found {len(links)} links:")
        for idx, l in enumerate(links[:15]):
            print(f"{idx+1}: {l}")
            
        browser.close()

if __name__ == "__main__":
    main()
