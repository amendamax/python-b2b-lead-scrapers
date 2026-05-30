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
        
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            print(f"Found {len(rows)} rows.")
            for idx, r in enumerate(rows[:4]):
                print(f"\nRow {idx} HTML:")
                print(r.prettify())
        else:
            print("No table found")
            
        browser.close()

if __name__ == "__main__":
    main()
