import requests
import json
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

all_listings = []

# Fetch up to 5 pages
for page in range(1, 6):
    url = f'https://www.autoscout24.it/lst/porsche/macan/ve_diesel?sort=standard&desc=0&ustate=N%2CU&cy=I&fregfrom=2015&fregto=2018&kmto=115000&page={page}'
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
        print(f"Page {page}: found {len(listings)} items")
        for item in listings:
            all_listings.append(item)
    except Exception as e:
        print(f"Error page {page}: {e}")
        break

print(f"Total collected across pages: {len(all_listings)}")

# Deduplicate by url
unique_urls = {}
for it in all_listings:
    u = 'https://www.autoscout24.it' + it.get('url', '')
    unique_urls[u] = it

print(f"Unique listings to inspect: {len(unique_urls)}")

detailed_matches = []

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
        km = tracking.get('mileage')
        reg = tracking.get('firstRegistration')
        cost = prices.get('public', {}).get('priceFormatted') or prices.get('public', {}).get('priceRaw')
        
        has_tetto = any(w in all_text for w in ['tetto', 'panoramico', 'apribile', 'sunroof'])
        has_vetri = any(w in all_text for w in ['vetri oscurati', 'privacy', 'vetri scuri', 'cristalli privacy', 'oscurati', 'vetri neri'])
        has_corsia = any(w in all_text for w in ['corsia', 'lane', 'mantenimento', 'superamento', 'angolo cieco', 'blind spot', 'lka', 'ldw'])
        
        detailed_matches.append({
            'url': u,
            'price': cost,
            'km': km,
            'reg': reg,
            'city': city,
            'kw': kw,
            'hp': hp,
            'has_tetto': has_tetto,
            'has_vetri': has_vetri,
            'has_corsia': has_corsia,
            'seller': seller.get('companyName') or seller.get('type'),
            'phones': seller.get('phones', []),
            'desc': desc[:400].replace('\n', ' ')
        })
        print(f"-> {city} | {cost} | {km} km | {reg} | {kw} kW ({hp} CP) | Tetto:{has_tetto} | Privacy:{has_vetri} | Corsia:{has_corsia}")
    except Exception as e:
        print(f"Error on {u}: {e}")

with open(r'C:\Users\bratu\Documents\antigravity\amazing-borg\all_detailed_macan_italy.json', 'w', encoding='utf-8') as f:
    json.dump(detailed_matches, f, indent=2, ensure_ascii=False)
print("Saved all detailed matches.")
