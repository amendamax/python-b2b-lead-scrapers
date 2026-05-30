from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        page.goto("https://secure.utah.gov/bes/")
        page.click("text=Search Business Entity Records")
        page.wait_for_timeout(3000)
        page.fill("input[name='BusinessSearch_Index_txtEntityName']", "GENERAL-PLUMBING CONTRACTORS, INC.")
        page.click("input[name='btnSearch']")
        page.wait_for_timeout(5000)
        
        # Click the link
        print("Clicking result link...")
        page.click("text=GENERAL-PLUMBING CONTRACTORS, INC.")
        
        page.wait_for_timeout(5000)
        
        print(f"Detail URL: {page.url}")
        
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables on detail page.")
        for idx, t in enumerate(tables):
            print(f"\nTable {idx}:")
            for r_idx, row in enumerate(t.find_all('tr')):
                cols = [td.text.strip() for td in row.find_all(['td', 'th'])]
                print(f"  Row {r_idx}: {cols}")
                
        # Also print any text blocks with address labels
        text = soup.text
        for line in text.split('\n'):
            line = line.strip()
            if any(x in line.lower() for x in ['address', 'office', 'agent', 'street']):
                print(f"Address line: {line}")
                
        browser.close()

if __name__ == "__main__":
    main()
