from curl_cffi import requests
from bs4 import BeautifulSoup

def test():
    print("Testing paginegialle.it request...")
    session = requests.Session(impersonate="chrome")
    url = "https://www.paginegialle.it/ricerca/dentisti/Milano"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        soup = BeautifulSoup(response.text, 'lxml')
        # Let's see some search results
        listings = soup.select('.item, article, .card, .search-results .result')
        print(f"Found {len(listings)} elements matching selectors.")
        
        # Print a snippet of the response text to inspect elements
        print("\nPage text length:", len(response.text))
        
        # Save a snippet of the HTML to a file so we can view its structure
        with open("pg_sample.html", "w", encoding="utf-8") as f:
            f.write(response.text[:20000])
        print("Wrote pg_sample.html for inspection.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
