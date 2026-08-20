import requests
import json
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

url = 'https://www.autoscout24.it/lst/porsche/macan/ve_diesel?sort=standard&desc=0&ustate=N%2CU&cy=I&fregfrom=2016&fregto=2018&kmto=100000'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

r = requests.get(url, headers=headers, timeout=10)
soup = bs4.BeautifulSoup(r.text, 'html.parser')
script = soup.find('script', id='__NEXT_DATA__')

if script:
    data = json.loads(script.string)
    listings = data.get('props', {}).get('pageProps', {}).get('listings', [])
    print(f"Total found: {len(listings)}")
    
    for i, item in enumerate(listings):
        vehicle = item.get('vehicle', {})
        tracking = item.get('tracking', {})
        location = item.get('location', {})
        price = item.get('price', {})
        u = 'https://www.autoscout24.it' + item.get('url', '')
        
        # Scrape item details
        try:
            r_item = requests.get(u, headers=headers, timeout=10)
            soup_item = bs4.BeautifulSoup(r_item.text, 'html.parser')
            script_item = soup_item.find('script', id='__NEXT_DATA__')
            d_item = json.loads(script_item.string)
            details = d_item.get('props', {}).get('pageProps', {}).get('listingDetails', {})
            veh_det = details.get('vehicle', {})
            raw_power = veh_det.get('rawPowerInKw')
            desc = bs4.BeautifulSoup(details.get('description', ''), 'html.parser').get_text()
            eq = str(details.get('equipment', []))
            
            all_text = (desc + ' ' + eq).lower()
            has_tetto = any(w in all_text for w in ['tetto', 'panoramico', 'apribile', 'sunroof'])
            has_vetri = any(w in all_text for w in ['vetri oscurati', 'privacy', 'vetri scuri', 'cristalli privacy', 'oscurati'])
            has_corsia = any(w in all_text for w in ['corsia', 'lane', 'mantenimento', 'superamento', 'angolo cieco'])
            
            city = location.get('city', '')
            km = tracking.get('mileage')
            reg = tracking.get('firstRegistration')
            cost = price.get('priceFormatted')
            
            print(f"[{i+1}] {cost} | {km} km | {reg} | {city} | {raw_power} kW ({veh_det.get('powerInHp')} CV)")
            print(f"    Tetto: {has_tetto} | Privacy Glass: {has_vetri} | Lane/Corsia: {has_corsia}")
            print(f"    URL: {u}")
            print("--------------------------------------------------")
        except Exception as e:
            print(f"[{i+1}] Error reading {u}: {e}")
