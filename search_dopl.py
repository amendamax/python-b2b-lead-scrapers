import requests
from bs4 import BeautifulSoup
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = "https://secure.utah.gov/llv/search/index.html"

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

try:
    r = session.get(url, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    csrf_tag = soup.find('input', {'name': '_csrf'})
    csrf_token = csrf_tag.get('value') if csrf_tag else ""
    
    payload = {
        "_csrf": csrf_token,
        "type": "by_name",
        "action": "search",
        "fullName": "GENERAL-PLUMBING",
        "startsWith": "true",
        "item38": "207",
        "count": ""
    }
    
    r_post = session.post(url, data=payload, timeout=15)
    soup_post = BeautifulSoup(r_post.text, 'html.parser')
    
    # Print the page main content area to see if there is an error message
    main_content = soup_post.find('div', {'id': 'content'}) or soup_post.find('div', {'class': 'content'})
    if not main_content:
        main_content = soup_post.body
        
    print("Page Content Snippet:")
    text_content = main_content.text.strip() if main_content else "No content"
    lines = [l.strip() for l in text_content.split('\n') if l.strip()]
    for line in lines[:50]:
        print(f"  {line}")
            
except Exception as e:
    print(f"Error: {e}")
