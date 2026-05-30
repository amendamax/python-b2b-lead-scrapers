import requests
from bs4 import BeautifulSoup

url = "https://secure.utah.gov/llv/search/index.html"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}
try:
    r = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    recaptcha_divs = soup.find_all(class_=lambda x: x and 'recaptcha' in x.lower())
    print(f"Found recaptcha elements: {len(recaptcha_divs)}")
    for d in recaptcha_divs:
        print(d)
        
    scripts = soup.find_all('script')
    print(f"Found {len(scripts)} scripts:")
    for s in scripts:
        src = s.get('src', '')
        if 'recaptcha' in src.lower():
            print(f"  Recaptcha script: {src}")
except Exception as e:
    print(f"Error: {e}")
