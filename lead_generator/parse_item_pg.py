from curl_cffi import requests
from bs4 import BeautifulSoup

def parse_item():
    print("Fetching single search item card from Pagine Gialle...")
    session = requests.Session(impersonate="chrome")
    url = "https://www.paginegialle.it/ricerca/dentisti/Milano"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        
        item = soup.select_one('.search-itm')
        if item:
            print("Found .search-itm card!")
            with open("item_sample.html", "w", encoding="utf-8") as f:
                f.write(item.prettify())
            print("Saved card HTML to item_sample.html.")
        else:
            print("Did not find .search-itm card.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    parse_item()
