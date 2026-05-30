from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Navigating to BES...")
        page.goto("https://secure.utah.gov/bes/")
        
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
                
        browser.close()

if __name__ == "__main__":
    main()
