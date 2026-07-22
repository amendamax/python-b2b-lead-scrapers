from curl_cffi import requests
from bs4 import BeautifulSoup

def extract_links():
    print("Extracting all link tags from Pagine Gialle...")
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
        
        for idx, item in enumerate(items[:3]):
            name = item.select_one('.search-itm__rag').text.strip() if item.select_one('.search-itm__rag') else f"Item {idx+1}"
            print(f"\n--- Listing {idx+1}: {name[:60]} ---")
            
            # Print ALL anchor tags in the item
            anchors = item.find_all('a')
            for a in anchors:
                href = a.get('href', '')
                text = a.text.strip().replace('\n', ' ')
                cls = a.get('class', [])
                print(f"  Link: '{text[:30]}' | href: {href[:70]} | Class: {cls}")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_links()
