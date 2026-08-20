import requests
import json
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Search Europe on AutoScout24 for 2017-2018 Macan Diesel with 190kW, <= 100k km
url = 'https://www.autoscout24.de/lst/porsche/macan/ve_diesel?sort=price&desc=0&ustate=N%2CU&fregfrom=2017&fregto=2018&powerfrom=188&kmto=100000'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

r = requests.get(url, headers=headers, timeout=10)
soup = bs4.BeautifulSoup(r.text, 'html.parser')
script = soup.find('script', id='__NEXT_DATA__')

results = []

if script:
    data = json.loads(script.string)
    listings = data.get('props', {}).get('pageProps', {}).get('listings', [])
    print(f"Total 2017-2018 European listings found: {len(listings)}")
    
    for i, item in enumerate(listings):
        vehicle = item.get('vehicle', {})
        tracking = item.get('tracking', {})
        location = item.get('location', {})
        price = item.get('price', {})
        u = 'https://www.autoscout24.de' + item.get('url', '')
        
        try:
            r_item = requests.get(u, headers=headers, timeout=10)
            soup_item = bs4.BeautifulSoup(r_item.text, 'html.parser')
            script_item = soup_item.find('script', id='__NEXT_DATA__')
            d_item = json.loads(script_item.string)
            details = d_item.get('props', {}).get('pageProps', {}).get('listingDetails', {})
            veh_det = details.get('vehicle', {})
            desc = bs4.BeautifulSoup(details.get('description', ''), 'html.parser').get_text()
            eq = str(details.get('equipment', []))
            
            all_text = (desc + ' ' + eq).lower()
            has_tetto = any(w in all_text for w in ['panoramadach', 'schiebedach', 'glasdach', 'tetto', 'toit'])
            has_vetri = any(w in all_text for w in ['privacy', 'abgedunkelt', 'verglasung', 'sonnenschutzverglasung', 'oscurati', 'surteint'])
            has_corsia = any(w in all_text for w in ['spurhalteassistent', 'spurwechselassistent', 'lane assist', 'lane keep', 'corsia', 'voie'])
            has_360 = any(w in all_text for w in ['surround view', '360', '360°', '360-grad', '360 grad', 'top view', 'area view', 'telecamera 360', 'kamera 360', 'rundumsicht', 'caméra 360'])
            
            city = location.get('city', '')
            country = location.get('countryCode', '')
            km = tracking.get('mileage')
            reg = tracking.get('firstRegistration')
            cost = price.get('priceFormatted')
            kw = veh_det.get('rawPowerInKw')
            hp = veh_det.get('powerInHp')
            
            res_obj = {
                'price': cost,
                'km': km,
                'reg': reg,
                'city': city,
                'country': country,
                'kw': kw,
                'hp': hp,
                'has_tetto': has_tetto,
                'has_vetri': has_vetri,
                'has_corsia': has_corsia,
                'has_360': has_360,
                'url': u,
                'desc_snippet': desc[:300].replace('\n', ' ')
            }
            results.append(res_obj)
            print(f"[{i+1}] {cost} | {km} km | {reg} | {city} ({country}) | {kw} kW")
            print(f"    Tetto: {has_tetto} | Privacy: {has_vetri} | Lane: {has_corsia} | 360 Cam: {has_360}")
        except Exception as e:
            print(f"Error {u}: {e}")

with open(r'C:\Users\bratu\Documents\antigravity\amazing-borg\strict_2017_2018_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print("Saved strict 2017-2018 results.")
