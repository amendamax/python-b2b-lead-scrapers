import requests
import json
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

countries = ['D', 'I', 'F', 'MC', 'A', 'CH', 'NL', 'B', 'L']
all_collected = []

# Fetch pages across all target countries
for c in countries:
    for page in range(1, 10):
        url = f'https://www.autoscout24.de/lst/porsche/macan/ve_diesel?sort=standard&desc=0&ustate=N%2CU&cy={c}&fregfrom=2016&fregto=2018&powerfrom=188&page={page}'
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
                all_collected.append(item)
        except Exception as e:
            break

print(f"Total raw collected across Europe: {len(all_collected)}")

unique_dict = {}
for it in all_collected:
    u = 'https://www.autoscout24.de' + it.get('url', '')
    unique_dict[u] = it

print(f"Unique vehicles to inspect: {len(unique_dict)}")

ranked_cars = []

for u, it in unique_dict.items():
    try:
        r_item = requests.get(u, headers=headers, timeout=10)
        soup_item = bs4.BeautifulSoup(r_item.text, 'html.parser')
        script_item = soup_item.find('script', id='__NEXT_DATA__')
        if not script_item:
            continue
        d_item = json.loads(script_item.string)
        props = d_item.get('props', {}).get('pageProps', {}).get('listingDetails', {})
        veh = props.get('vehicle', {})
        tracking = props.get('tracking', {})
        location = props.get('location', {})
        prices = props.get('prices', {})
        seller = props.get('seller', {})
        
        kw = veh.get('rawPowerInKw')
        hp = veh.get('powerInHp')
        color = str(veh.get('bodyColor', '') or props.get('vehicle', {}).get('specifics', {}).get('bodyColor', ''))
        
        # Color exclusion
        if any(bad in color.lower() for bad in ['weiß', 'weiss', 'white', 'bianco', 'rot', 'red', 'rosso']):
            continue
            
        desc = bs4.BeautifulSoup(props.get('description', ''), 'html.parser').get_text()
        eq_list = [e.get('name', '') for e in props.get('equipment', [])]
        eq_text = ' '.join(eq_list)
        all_text = (desc + ' ' + eq_text).lower()
        
        city = location.get('city', '')
        country = location.get('countryCode', '')
        km = tracking.get('mileage')
        reg = tracking.get('firstRegistration')
        cost = prices.get('public', {}).get('priceFormatted') or prices.get('public', {}).get('priceRaw')
        
        # Specific equipment checks
        has_360 = any(w in all_text for w in ['surround view', '360', '360°', '360-grad', '360 grad', 'top view', 'area view', 'rundumsicht', 'telecamera 360'])
        has_blind = any(w in all_text for w in ['spurwechselassistent', 'totwinkel', 'blind spot', 'angolo cieco', 'angle mort', 'lca'])
        has_pano = any(w in all_text for w in ['panoramadach', 'schiebedach', 'glasdach', 'tetto', 'toit', 'sunroof'])
        has_lane = any(w in all_text for w in ['spurhalteassistent', 'lane assist', 'lane keep', 'mantenimento corsia', 'franchissement', 'lka'])
        has_air = any(w in all_text for w in ['luftfederung', 'sospensioni pneumatiche', 'suspension pneumatique', 'air suspension', 'pasm'])
        has_chrono = any(w in all_text for w in ['sport chrono', 'chrono'])
        has_bose = any(w in all_text for w in ['bose', 'burmester'])
        
        # Score calculation
        score = (3 if has_360 else 0) + (3 if has_blind else 0) + (3 if has_pano else 0) + (2 if has_lane else 0) + (1 if has_air else 0) + (1 if has_bose else 0)
        
        car_data = {
            'url': u,
            'price': cost,
            'km': km,
            'reg': reg,
            'city': city,
            'country': country,
            'color': color,
            'kw': kw,
            'hp': hp,
            'score': score,
            'has_360': has_360,
            'has_blind': has_blind,
            'has_pano': has_pano,
            'has_lane': has_lane,
            'has_air': has_air,
            'has_chrono': has_chrono,
            'has_bose': has_bose,
            'seller_name': seller.get('companyName') or seller.get('type'),
            'phones': seller.get('phones', []),
            'desc': desc[:350].replace('\n', ' ')
        }
        ranked_cars.append(car_data)
        print(f"[{country}][{color}] {city} | {cost} | {km} km | {reg} | Score:{score} (360:{has_360}, Blind:{has_blind}, Pano:{has_pano}, Lane:{has_lane}, Air:{has_air})")
    except Exception as e:
        pass

ranked_cars.sort(key=lambda x: x['score'], reverse=True)

with open(r'C:\Users\bratu\Documents\antigravity\amazing-borg\fresh_europe_scan.json', 'w', encoding='utf-8') as f:
    json.dump(ranked_cars, f, indent=2, ensure_ascii=False)

print("Scan Complete and saved to fresh_europe_scan.json!")
