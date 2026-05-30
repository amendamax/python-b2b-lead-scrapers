from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Navigating to BES Home...")
        page.goto("https://secure.utah.gov/bes/")
        
        print("Clicking 'Search Business Entity Records'...")
        page.click("text=Search Business Entity Records")
        page.wait_for_timeout(3000)
        
        print(f"Current URL: {page.url}")
        
        # Fill the business entity name input
        print("Filling company name...")
        page.fill("input[name='BusinessSearch_Index_txtEntityName']", "GENERAL-PLUMBING CONTRACTORS, INC.")
        
        # Click search
        print("Clicking Search button...")
        page.click("input[name='btnSearch']")
        
        page.wait_for_timeout(5000)
        
        print(f"URL after search: {page.url}")
        
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables on page.")
        for idx, t in enumerate(tables):
            print(f"\nTable {idx}:")
            for r_idx, row in enumerate(t.find_all('tr')[:10]):
                cols = [td.text.strip() for td in row.find_all(['td', 'th'])]
                print(f"  Row {r_idx}: {cols}")
                for a in row.find_all('a'):
                    print(f"    Link: {a.text.strip()} -> {a.get('href')}")
                    
        browser.close()

if __name__ == "__main__":
    main()
