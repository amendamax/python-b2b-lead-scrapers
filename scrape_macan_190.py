import requests
import json
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Search for all Macan Diesel with power >= 189 kW in Italy, 2015-2018, km <= 105.000
url = 'https://www.autoscout24.it/lst/porsche/macan/ve_diesel?sort=standard&desc=0&ustate=N%2CU&cy=I&fregfrom=2015&fregto=2018&powerfrom=188&kmto=105000'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

r = requests.get(url, headers=headers, timeout=10)
soup = bs4.BeautifulSoup(r.text, 'html.parser')
script = soup.find('script', id='__NEXT_DATA__')

if script:
    data = json.loads(script.string)
    listings = data.get('props', {}).get('pageProps', {}).get('listings', [])
    print(f"Total 190kW found: {len(listings)}")
    
    for i, item in enumerate(listings):
        vehicle = item.get('vehicle', {})
        tracking = item.get('tracking', {})
        location = item.get('location', {})
        price = item.get('price', {})
        u = 'https://www.autoscout24.it' + item.get('url', '')
        
        try:
            r_item = requests.get(u, headers=headers, timeout=10)
            soup_item = bs4.BeautifulSoup(r_item.text, 'html.parser')
            script_item = soup_item.find('script', id='__NEXT_DATA__')
            d_item = json.loads(script_item.string)
            details = d_item.get('props', {}).get('pageProps', {}).get('listingDetails', {})
            veh_det = details.get('vehicle', {})
            raw_power = veh_det.get('rawPowerInKw')
            hp = veh_det.get('powerInHp')
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
            
            print(f"--- LISTING #{i+1} ---")
            print(f"Pret: {cost} | Km: {km} | Data: {reg} | Oras: {city} | Putere: {raw_power} kW ({hp} CP)")
            print(f"Tetto: {has_tetto} | Privacy: {has_vetri} | Lane Assist: {has_corsia}")
            print(f"URL: {u}")
            print("Descriere scurta:", desc[:250].replace('\n', ' '))
        except Exception as e:
            print(f"Error {u}: {e}")
