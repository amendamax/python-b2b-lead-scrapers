import json
import requests
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('fresh_europe_scan.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total processed in scan: {len(data)}")

# Filter top candidates
top_matches = [d for d in data if d.get('score', 0) >= 6]

print(f"Total High-Score Matches (Score >= 6): {len(top_matches)}")

for d in top_matches:
    u = d.get('url')
    try:
        r = requests.get(u, headers={'User-Agent': 'Mozilla/5.0'})
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        d_item = json.loads(script.string)
        props = d_item.get('props', {}).get('pageProps', {}).get('listingDetails', {})
        t = props.get('tracking', {})
        p = props.get('prices', {}).get('public', {})
        seller = props.get('seller', {})
        desc = bs4.BeautifulSoup(props.get('description', ''), 'html.parser').get_text()
        
        print("==================================================")
        print(f"[{d.get('country')}][{d.get('color')}] {props.get('location', {}).get('city')} | {p.get('priceFormatted')} | {t.get('mileage')} km | {t.get('firstRegistration')}")
        print(f"  Score: {d.get('score')} | 360Cam: {d.get('has_360')} | BlindSpot: {d.get('has_blind')} | Pano: {d.get('has_pano')} | Lane: {d.get('has_lane')} | Air: {d.get('has_air')} | Bose: {d.get('has_bose')}")
        print(f"  Seller: {seller.get('companyName') or seller.get('type')} | Phones: {seller.get('phones')}")
        print(f"  URL: {u}")
        print(f"  Desc: {desc[:280].replace(chr(10), ' ')}")
    except Exception as e:
        print("Error:", e)
