import requests
import json
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

all_italy_listings = []

# Fetch up to 10 pages on AutoScout24 Italy
for page in range(1, 10):
    url = f'https://www.autoscout24.it/lst/porsche/macan/ve_diesel?sort=standard&desc=0&ustate=N%2CU&cy=I&fregfrom=2016&fregto=2018&page={page}'
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
            all_italy_listings.append(item)
    except Exception as e:
        print(f"Error page {page}: {e}")
        break

print(f"Total Italian listings collected: {len(all_italy_listings)}")

# Deduplicate
unique_urls = {}
for it in all_italy_listings:
    u = 'https://www.autoscout24.it' + it.get('url', '')
    unique_urls[u] = it

print(f"Unique Italian listings: {len(unique_urls)}")

italy_perfect_matches = []

for u, it in unique_urls.items():
    try:
        r_item = requests.get(u, headers=headers, timeout=10)
        soup_item = bs4.BeautifulSoup(r_item.text, 'html.parser')
        script_item = soup_item.find('script', id='__NEXT_DATA__')
        if not script_item:
            continue
        d_item = json.loads(script_item.string)
        details = d_item.get('props', {}).get('pageProps', {}).get('listingDetails', {})
        veh = details.get('vehicle', {})
        tracking = details.get('tracking', {})
        location = details.get('location', {})
        prices = details.get('prices', {})
        seller = details.get('seller', {})
        
        kw = veh.get('rawPowerInKw')
        hp = veh.get('powerInHp')
        color = veh.get('bodyColor', '') or details.get('vehicle', {}).get('specifics', {}).get('bodyColor', '')
        desc = bs4.BeautifulSoup(details.get('description', ''), 'html.parser').get_text()
        eq_list = [e.get('name', '') for e in details.get('equipment', [])]
        eq_text = ' '.join(eq_list)
        all_text = (desc + ' ' + eq_text).lower()
        
        # Color check (exclude white and red)
        if any(bad in str(color).lower() for bad in ['bianco', 'rosso', 'white', 'red']):
            continue
            
        city = location.get('city', '')
        km = tracking.get('mileage')
        reg = tracking.get('firstRegistration')
        cost = prices.get('public', {}).get('priceFormatted') or prices.get('public', {}).get('priceRaw')
        
        has_tetto = any(w in all_text for w in ['tetto', 'panoramico', 'apribile', 'sunroof'])
        has_360 = any(w in all_text for w in ['surround view', '360', '360°', 'telecamera 360', 'top view'])
        has_blind_spot = any(w in all_text for w in ['angolo cieco', 'cieco', 'blind spot', 'lca', 'cambio corsia', 'spurwechsel', 'totwinkel'])
        has_lane = any(w in all_text for w in ['corsia', 'lane', 'mantenimento', 'superamento', 'lka'])
        has_camera = any(w in all_text for w in ['telecamera', 'camera', 'retrocamera', 'surround view', '360'])
        
        match_record = {
            'url': u,
            'price': cost,
            'km': km,
            'reg': reg,
            'city': city,
            'color': color,
            'kw': kw,
            'hp': hp,
            'has_tetto': has_tetto,
            'has_360': has_360,
            'has_blind_spot': has_blind_spot,
            'has_lane': has_lane,
            'has_camera': has_camera,
            'seller': seller.get('companyName') or seller.get('type'),
            'phones': seller.get('phones', []),
            'desc': desc[:300].replace('\n', ' ')
        }
        italy_perfect_matches.append(match_record)
        print(f"[{color}] {city} | {cost} | {km} km | {reg} | {kw} kW | Tetto:{has_tetto} | BlindSpot:{has_blind_spot} | Lane:{has_lane} | Cam:{has_camera}")
    except Exception as e:
        print(f"Error {u}: {e}")

with open(r'C:\Users\bratu\Documents\antigravity\amazing-borg\italy_perfect_matches.json', 'w', encoding='utf-8') as f:
    json.dump(italy_perfect_matches, f, indent=2, ensure_ascii=False)
print("Saved all Italian matches!")
