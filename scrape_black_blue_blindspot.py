import requests
import json
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Search all black and blue Macan Diesels on AutoScout24 (2016-2018)
listings_to_check = []

for page in range(1, 15):
    url = f'https://www.autoscout24.de/lst/porsche/macan/ve_diesel?sort=standard&desc=0&ustate=N%2CU&fregfrom=2016&fregto=2018&powerfrom=188&bodycolors=schwarz&bodycolors=blau&page={page}'
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        if not script:
            break
        data = json.loads(script.string)
        page_items = data.get('props', {}).get('pageProps', {}).get('listings', [])
        if not page_items:
            break
        for it in page_items:
            listings_to_check.append(it)
    except Exception as e:
        print(f"Error page {page}: {e}")
        break

print(f"Total Black/Blue listings: {len(listings_to_check)}")

# Deduplicate
unique_map = {}
for it in listings_to_check:
    u = 'https://www.autoscout24.de' + it.get('url', '')
    unique_map[u] = it

blind_spot_results = []

for u, it in unique_map.items():
    try:
        r = requests.get(u, headers=headers, timeout=10)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        if not script:
            continue
        d = json.loads(script.string)
        details = d.get('props', {}).get('pageProps', {}).get('listingDetails', {})
        veh = details.get('vehicle', {})
        tracking = details.get('tracking', {})
        location = details.get('location', {})
        prices = details.get('prices', {})
        seller = details.get('seller', {})
        
        desc = bs4.BeautifulSoup(details.get('description', ''), 'html.parser').get_text().lower()
        eq = str([e.get('name', '') for e in details.get('equipment', [])]).lower()
        all_text = desc + ' ' + eq
        
        has_blind_spot = any(k in all_text for k in ['spurwechselassistent', 'totwinkel', 'blind spot', 'lca', 'angolo cieco', 'angle mort'])
        has_pano = any(k in all_text for k in ['panoramadach', 'schiebedach', 'tetto', 'toit', 'glasdach'])
        has_lane = any(k in all_text for k in ['spurhalteassistent', 'lane assist', 'mantenimento corsia', 'lka'])
        has_360 = any(k in all_text for k in ['surround view', '360', 'rundumsicht', 'area view'])
        
        color = veh.get('bodyColor', '') or details.get('vehicle', {}).get('specifics', {}).get('bodyColor', '')
        city = location.get('city', '')
        country = location.get('countryCode', '')
        km = tracking.get('mileage')
        reg = tracking.get('firstRegistration')
        cost = prices.get('public', {}).get('priceFormatted') or prices.get('public', {}).get('priceRaw')
        kw = veh.get('rawPowerInKw')
        
        if has_blind_spot:
            item_data = {
                'url': u,
                'price': cost,
                'km': km,
                'reg': reg,
                'city': city,
                'country': country,
                'color': color,
                'kw': kw,
                'has_pano': has_pano,
                'has_blind_spot': has_blind_spot,
                'has_lane': has_lane,
                'has_360': has_360,
                'seller': seller.get('companyName') or seller.get('type'),
                'phones': seller.get('phones', []),
                'desc_snippet': desc[:300].replace('\n', ' ')
            }
            blind_spot_results.append(item_data)
            print(f"*** HIT: [{color}] {city} | {cost} | {km} km | {reg} | BlindSpot:{has_blind_spot} | Pano:{has_pano} | Lane:{has_lane} | 360:{has_360}")
    except Exception as e:
        print(f"Error {u}: {e}")

with open(r'C:\Users\bratu\Documents\antigravity\amazing-borg\black_blue_with_blindspot.json', 'w', encoding='utf-8') as f:
    json.dump(blind_spot_results, f, indent=2, ensure_ascii=False)
print("Saved black & blue with blind spot!")
