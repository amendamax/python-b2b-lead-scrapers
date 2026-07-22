from curl_cffi import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

def scan_multiple():
    print("Fetching search results...")
    session = requests.Session(impersonate="chrome")
    url = "https://www.paginegialle.it/ricerca/dentisti/Milano"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        items = soup.select('.search-itm')
        
        print(f"Scanning first 5 detail pages...")
        for idx, item in enumerate(items[:5]):
            name_el = item.select_one('.search-itm__rag')
            name = name_el.text.strip() if name_el else f"Item {idx+1}"
            
            # Yellowpages details page link
            detail_link_el = item.select_one('.search-itm__dx a')
            if not detail_link_el:
                detail_link_el = item.select_one('a')
                
            detail_url = detail_link_el.get('href', '')
            if not detail_url.startswith('http'):
                detail_url = urllib.parse.urljoin("https://www.paginegialle.it", detail_url)
                
            print(f"\n[{idx+1}] Business: {name[:50]}")
            print(f"      Detail URL: {detail_url}")
            
            # Fetch detail page
            time.sleep(1.0)
            res = session.get(detail_url, headers=headers, timeout=15)
            detail_soup = BeautifulSoup(res.text, 'lxml')
            
            # Look for external website links
            external_links = []
            a_tags = detail_soup.find_all('a')
            for a in a_tags:
                href = a.get('href', '')
                text = a.text.strip().replace('\n', ' ')
                cls = a.get('class', [])
                
                if href and not href.startswith('#') and not href.startswith('javascript'):
                    parsed = urllib.parse.urlparse(href)
                    domain = parsed.netloc
                    
                    if domain and 'paginegialle.it' not in domain and 'italiaonline' not in domain and 'iubenda' not in domain and 'whatsapp' not in href and 'wa.me' not in href and 'tuttocitta.it' not in domain and 'google' not in domain and 'apple' not in domain:
                        external_links.append((href, text, cls))
                        
            if external_links:
                print(f"      [+] Found {len(external_links)} external websites:")
                for href, text, cls in external_links:
                    print(f"        -> {href} | Text: '{text[:20]}' | Class: {cls}")
            else:
                print("      [-] No external website found.")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    scan_multiple()
