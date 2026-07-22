from curl_cffi import requests
from bs4 import BeautifulSoup
import urllib.parse

def extract_all():
    print("Scanning entire page for external links...")
    session = requests.Session(impersonate="chrome")
    url = "https://www.paginegialle.it/ricerca/dentisti/Milano"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # We want to print all links that do not contain paginegialle.it and are not javascript or whatsapp
        a_tags = soup.find_all('a')
        print(f"Total links on page: {len(a_tags)}")
        
        external_count = 0
        for a in a_tags:
            href = a.get('href', '')
            text = a.text.strip().replace('\n', ' ')
            cls = a.get('class', [])
            
            # Filter out internal, javascript, and standard social links
            if href and not href.startswith('#') and not href.startswith('javascript'):
                parsed = urllib.parse.urlparse(href)
                domain = parsed.netloc
                
                if domain and 'paginegialle.it' not in domain and 'italiaonline' not in domain and 'iubenda' not in domain and 'whatsapp' not in href and 'wa.me' not in href:
                    print(f"  Domain: {domain} | Link: {href[:60]} | Text: '{text[:20]}' | Class: {cls}")
                    external_count += 1
                    
        print(f"\nFound {external_count} total external links.")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    extract_all()
