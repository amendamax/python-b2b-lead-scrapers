from curl_cffi import requests
from bs4 import BeautifulSoup
import re

def parse_full():
    print("Fetching full page...")
    session = requests.Session(impersonate="chrome")
    url = "https://www.paginegialle.it/ricerca/dentisti/Milano"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Let's search for elements by class name that might represent a card or listing
        class_counts = {}
        for tag in soup.find_all(True):
            classes = tag.get('class', [])
            for c in classes:
                class_counts[c] = class_counts.get(c, 0) + 1
                
        # Sort and print top classes
        sorted_classes = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)
        print("\nTop class names in page:")
        for c, count in sorted_classes[:30]:
            print(f"  .{c}: {count} occurrences")
            
        # Let's search for text containing "Telefono" or "Tel" or phone numbers
        phone_matches = soup.find_all(text=re.compile(r'\d{2,4}\s?\d{6,8}'))
        print(f"\nFound {len(phone_matches)} text blocks matching phone patterns.")
        for m in phone_matches[:5]:
            print(f"  Phone text: '{m.strip()}' | Parent tag: {m.parent.name} | parent classes: {m.parent.get('class')}")
            
        # Let's search for tags that might be headers/names (h2, h3, h4)
        headings = soup.find_all(['h2', 'h3'])
        print(f"\nFound {len(headings)} heading elements (h2, h3).")
        for h in headings[:10]:
            print(f"  <{h.name}> classes: {h.get('class')} | Text: '{h.text.strip()}'")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parse_full()
