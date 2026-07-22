from curl_cffi import requests
from bs4 import BeautifulSoup
import urllib.parse

def test_detail():
    print("Fetching detail page...")
    session = requests.Session(impersonate="chrome")
    url = "https://www.paginegialle.it/studio-dentistico-ausonio-19-stp-milano"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Look for all links on this detail page
        a_tags = soup.find_all('a')
        print(f"Total links on detail page: {len(a_tags)}")
        
        for a in a_tags:
            href = a.get('href', '')
            text = a.text.strip().replace('\n', ' ')
            cls = a.get('class', [])
            
            # Look for external website links
            if href and not href.startswith('#') and not href.startswith('javascript'):
                parsed = urllib.parse.urlparse(href)
                domain = parsed.netloc
                
                if domain and 'paginegialle.it' not in domain and 'italiaonline' not in domain and 'iubenda' not in domain and 'whatsapp' not in href and 'wa.me' not in href:
                    print(f"  External Link: {href} | Text: '{text[:30]}' | Class: {cls}")
                    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_detail()
