from curl_cffi import requests
from bs4 import BeautifulSoup

def find_websites():
    print("Fetching and scanning Pagine Gialle page for website links...")
    session = requests.Session(impersonate="chrome")
    url = "https://www.paginegialle.it/ricerca/dentisti/Milano"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        items = soup.select('.search-itm')
        print(f"Found {len(items)} search items.")
        
        for idx, item in enumerate(items[:5]):
            # Business Name
            name_el = item.select_one('.search-itm__rag')
            name = name_el.text.strip() if name_el else "N/A"
            
            # Find all links (a tags) in the card
            links = item.find_all('a')
            print(f"\n[{idx+1}] Business: {name[:50]}")
            
            # Let's inspect all links in this card
            for a in links:
                href = a.get('href', '')
                text = a.text.strip().replace('\n', ' ')
                cls = a.get('class', [])
                id_attr = a.get('id', '')
                
                # We want to identify links that go to external websites (not paginegialle.it)
                if href and not href.startswith('#') and not href.startswith('javascript') and 'paginegialle.it' not in href:
                    print(f"  -> External link: {href} | Text: '{text[:20]}' | Class: {cls} | ID: {id_attr}")
                elif href and 'sito' in href.lower() or 'website' in href.lower():
                    print(f"  -> Potential website link: {href} | Text: '{text[:20]}' | Class: {cls}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    find_websites();
