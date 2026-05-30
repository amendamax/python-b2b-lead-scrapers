from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Navigating to BES Home...")
        page.goto("https://secure.utah.gov/bes/")
        
        print("Clicking 'Search Business Entity Records'...")
        # Select link containing text
        page.click("text=Search Business Entity Records")
        
        page.wait_for_timeout(5000)
        
        print(f"URL after click: {page.url}")
        title = page.title()
        print(f"Title: {title}")
        
        html = page.content()
        soup = BeautifulSoup(html, 'html.parser')
        
        forms = soup.find_all('form')
        print(f"Found {len(forms)} forms:")
        for idx, f in enumerate(forms):
            print(f"Form {idx}: action={f.get('action')}, method={f.get('method')}")
            for inp in f.find_all(['input', 'button', 'select']):
                print(f"  {inp.name}: name={inp.get('name')}, type={inp.get('type')}, value={inp.get('value')}")
                
        # Check if there is an input for search
        search_input = soup.find('input', {'id': lambda x: x and 'search' in x.lower() or 'name' in x.lower()})
        print("Search input found by lambda:", search_input is not None)
        
        browser.close()

if __name__ == "__main__":
    main()
