import requests
import json
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Search all Diesel Macans 2017-2018 up to 130.000 km across Europe
all_listings = []

for page in range(1, 10):
    url = f'https://www.autoscout24.de/lst/porsche/macan/ve_diesel?sort=standard&desc=0&ustate=N%2CU&fregfrom=2017&fregto=2018&kmto=130000&page={page}'
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
            all_listings.append(item)
    except Exception as e:
        print(f"Error page {page}: {e}")
        break

print(f"Total collected: {len(all_listings)}")

unique_urls = {}
for it in all_listings:
    u = 'https://www.autoscout24.de' + it.get('url', '')
    unique_urls[u] = it

print(f"Unique listings to inspect: {len(unique_urls)}")

target_matches = []

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
        desc = bs4.BeautifulSoup(details.get('description', ''), 'html.parser').get_text()
        eq_list = [e.get('name', '') for e in details.get('equipment', [])]
        eq_text = ' '.join(eq_list)
        all_text = (desc + ' ' + eq_text).lower()
        
        city = location.get('city', '')
        country = location.get('countryCode', '')
        km = tracking.get('mileage')
        reg = tracking.get('firstRegistration')
        cost = prices.get('public', {}).get('priceFormatted') or prices.get('public', {}).get('priceRaw')
        
        has_tetto = any(w in all_text for w in ['panoramadach', 'schiebedach', 'glasdach', 'tetto', 'toit'])
        has_360 = any(w in all_text for w in ['surround view', '360', '360°', '360-grad', '360 grad', 'top view', 'area view', 'telecamera 360', 'kamera 360', 'rundumsicht', 'caméra 360'])
        has_blind_spot = any(w in all_text for w in ['totwinkel', 'spurwechselassistent', 'blind spot', 'angolo cieco', 'angle mort'])
        has_lane = any(w in all_text for w in ['spurhalteassistent', 'lane assist', 'lane keep', 'mantenimento corsia', 'franchissement'])
        has_privacy = any(w in all_text for w in ['privacy', 'abgedunkelt', 'verglasung', 'sonnenschutzverglasung', 'oscurati', 'surteint'])
        
        # Check if matching 190kW (or if 190kW is present)
        if kw and kw >= 188:
            match_obj = {
                'url': u,
                'price': cost,
                'km': km,
                'reg': reg,
                'city': city,
                'country': country,
                'kw': kw,
                'hp': hp,
                'has_tetto': has_tetto,
                'has_360': has_360,
                'has_blind_spot': has_blind_spot,
                'has_lane': has_lane,
                'has_privacy': has_privacy,
                'seller': seller.get('companyName') or seller.get('type'),
                'phones': seller.get('phones', []),
                'desc_snippet': desc[:300].replace('\n', ' ')
            }
            target_matches.append(match_obj)
            print(f"[{country}] {city} | {cost} | {km} km | {reg} | 360:{has_360} | BlindSpot:{has_blind_spot} | Tetto:{has_tetto} | Lane:{has_lane}")
    except Exception as e:
        print(f"Error on {u}: {e}")

with open(r'C:\Users\bratu\Documents\antigravity\amazing-borg\matches_360_blindspot.json', 'w', encoding='utf-8') as f:
    json.dump(target_matches, f, indent=2, ensure_ascii=False)
print("Done scraping!")
