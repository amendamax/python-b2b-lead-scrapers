import requests
import json
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Search Germany on AutoScout24
url = 'https://www.autoscout24.de/lst/porsche/macan/ve_diesel?sort=price&desc=0&ustate=N%2CU&cy=D&fregfrom=2016&fregto=2018&powerfrom=188&kmto=100000'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

r = requests.get(url, headers=headers, timeout=10)
soup = bs4.BeautifulSoup(r.text, 'html.parser')
script = soup.find('script', id='__NEXT_DATA__')

if script:
    data = json.loads(script.string)
    listings = data.get('props', {}).get('pageProps', {}).get('listings', [])
    print(f"Total German listings found: {len(listings)}")
    
    for i, item in enumerate(listings[:15]):
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
            has_tetto = any(w in all_text for w in ['panoramadach', 'schiebedach', 'glasdach', 'panoramaglasdach', 'tetto'])
            has_vetri = any(w in all_text for w in ['privacy', 'abgedunkelt', 'verglasung', 'sonnenschutzverglasung', 'oscurati'])
            has_corsia = any(w in all_text for w in ['spurhalteassistent', 'spurwechselassistent', 'lane assist', 'lane keep', 'totwinkel'])
            
            city = location.get('city', '')
            km = tracking.get('mileage')
            reg = tracking.get('firstRegistration')
            cost = price.get('priceFormatted')
            kw = veh_det.get('rawPowerInKw')
            hp = veh_det.get('powerInHp')
            
            print(f"[{i+1}] {cost} | {km} km | {reg} | {city} (DE) | {kw} kW ({hp} PS)")
            print(f"    Panoramadach: {has_tetto} | Privacy Glass: {has_vetri} | Spurhalteassistent: {has_corsia}")
            print(f"    URL: {u}")
            print("--------------------------------------------------")
        except Exception as e:
            print(f"Error {u}: {e}")
