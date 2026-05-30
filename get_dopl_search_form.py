import requests
from bs4 import BeautifulSoup

url = "https://secure.utah.gov/llv/search/index.html"
try:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    r = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Content length: {len(r.text)}")
    soup = BeautifulSoup(r.text, 'html.parser')
    forms = soup.find_all('form')
    print(f"Found {len(forms)} forms:")
    for i, form in enumerate(forms):
        print(f"Form {i}: action={form.get('action')}, method={form.get('method')}")
        for tag in form.find_all(['input', 'select', 'textarea']):
            print(f"  {tag.name}: name={tag.get('name')}, type={tag.get('type')}, value={tag.get('value')}")
            if tag.name == 'select':
                options = tag.find_all('option')
                print(f"    Options count: {len(options)}")
                for opt in options[:10]:
                    print(f"      Option: value={opt.get('value')}, text={opt.text.strip()}")
except Exception as e:
    print(f"Error: {e}")
