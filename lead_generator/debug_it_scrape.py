from curl_cffi import requests
from bs4 import BeautifulSoup
import urllib.parse

def debug_scrape():
    print("Debugging Italian scraper...")
    session = requests.Session(impersonate="chrome")
    url = "https://www.paginegialle.it/ricerca/dentisti/Milano"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        items = soup.select('.search-itm')
        
        if items:
            item = items[0]
            name = item.select_one('.search-itm__rag').text.strip()
            detail_link_el = item.select_one('.search-itm__dx a') or item.select_one('a')
            detail_url = detail_link_el.get('href', '')
            if not detail_url.startswith('http'):
                detail_url = urllib.parse.urljoin("https://www.paginegialle.it", detail_url)
                
            print(f"Name: {name}")
            print(f"Detail URL: {detail_url}")
            
            res = session.get(detail_url, headers=headers, timeout=15)
            print(f"Detail Status Code: {res.status_code}")
            
            detail_soup = BeautifulSoup(res.text, 'lxml')
            phone_el = detail_soup.select_one('.search-itm__phone-item')
            phone = phone_el.text.strip() if phone_el else "N/A"
            print(f"Phone: {phone}")
            
            # Check for website link
            has_website = False
            a_tags = detail_soup.find_all('a')
            print(f"Total links on detail page: {len(a_tags)}")
            for a in a_tags:
                text = a.text.strip().lower()
                if 'sito web' in text or 'sito' == text:
                    has_website = True
                    print(f"Found website: {a.get('href')} | text: {a.text.strip()}")
            print(f"Has website: {has_website}")
            
        else:
            print("No items found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_scrape()
