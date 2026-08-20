import requests
import json
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

green_listings = []

# Search green Macan Diesel across AutoScout24 Europe
for page in range(1, 5):
    url = f'https://www.autoscout24.de/lst/porsche/macan/ve_diesel?sort=standard&desc=0&ustate=N%2CU&fregfrom=2016&fregto=2018&powerfrom=188&bodycolors=gruen&page={page}'
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        if not script:
            break
        data = json.loads(script.string)
        listings = data.get('props', {}).get('pageProps', {}).get('listings', [])
        if not listings:
            break
        for item in listings:
            green_listings.append(item)
    except Exception as e:
        print(f"Error page {page}: {e}")
        break

print(f"Total Green listings: {len(green_listings)}")

for it in green_listings:
    u = 'https://www.autoscout24.de' + it.get('url', '')
    print("Green Macan URL:", u)
    try:
        r_item = requests.get(u, headers=headers, timeout=10)
        soup_item = bs4.BeautifulSoup(r_item.text, 'html.parser')
        script_item = soup_item.find('script', id='__NEXT_DATA__')
        d_item = json.loads(script_item.string)
        details = d_item.get('props', {}).get('pageProps', {}).get('listingDetails', {})
        desc = bs4.BeautifulSoup(details.get('description', ''), 'html.parser').get_text()
        print("City:", details.get('location', {}).get('city'))
        print("Price:", details.get('prices', {}).get('public', {}).get('priceFormatted'))
        print("Desc:", desc[:300])
    except Exception as e:
        print(e)
