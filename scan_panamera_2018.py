import requests
import json
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {'User-Agent': 'Mozilla/5.0'}

# Search all Panamera 4S Diesel 2018 across Europe
all_panameras = []
for page in range(1, 6):
    url = f'https://www.autoscout24.de/lst/porsche/panamera/ve_diesel?sort=standard&desc=0&ustate=N%2CU&fregfrom=2017&fregto=2019&powerfrom=300&page={page}'
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
        for it in listings:
            all_panameras.append(it)
    except Exception as e:
        break

print(f"Total collected: {len(all_panameras)}")

unique_map = {}
for it in all_panameras:
    u = 'https://www.autoscout24.de' + it.get('url', '')
    unique_map[u] = it

print(f"Unique Panameras to inspect: {len(unique_map)}")

for u, it in unique_map.items():
    try:
        r = requests.get(u, headers=headers, timeout=10)
        soup = bs4.BeautifulSoup(r.text, 'html.parser')
        script = soup.find('script', id='__NEXT_DATA__')
        d = json.loads(script.string)
        props = d.get('props', {}).get('pageProps', {}).get('listingDetails', {})
        veh = props.get('vehicle', {})
        tracking = props.get('tracking', {})
        prices = props.get('prices', {}).get('public', {})
        location = props.get('location', {})
        seller = props.get('seller', {})
        
        reg = str(tracking.get('firstRegistration', ''))
        km = tracking.get('mileage')
        cost = prices.get('priceFormatted') or prices.get('priceRaw')
        city = location.get('city')
        country = location.get('countryCode')
        color = veh.get('bodyColor')
        
        desc = bs4.BeautifulSoup(props.get('description', ''), 'html.parser').get_text()
        eq = [e.get('name') for e in props.get('equipment', [])]
        all_text = (desc + ' ' + ' '.join(eq)).lower()
        
        has_rear_steer = any(k in all_text for k in ['hinterachslenkung', 'allradlenkung', 'rear axle steering', 'asse posteriore sterzante', '4-rad-lenkung'])
        has_soft_close = any(k in all_text for k in ['soft-close', 'softclose', 'servoschließung', 'chiusura ammortizzata', 'fermeture assistée'])
        has_360 = any(k in all_text for k in ['surround view', '360', '360°', '360-grad', 'rundumsicht', 'telecamera 360', 'top view'])
        has_blind = any(k in all_text for k in ['spurwechselassistent', 'totwinkel', 'blind spot', 'angolo cieco', 'angle mort'])
        has_pano = any(k in all_text for k in ['panoramadach', 'schiebedach', 'tetto', 'toit'])
        has_chrono = any(k in all_text for k in ['sport chrono', 'chrono'])
        has_night = any(k in all_text for k in ['nachtsicht', 'night vision', 'termocamera', 'vision nocturne'])
        has_massage = any(k in all_text for k in ['massage', 'massaggio'])
        has_ventilation = any(k in all_text for k in ['sitzbelüftung', 'belüftung', 'ventilazione', 'ventilés'])
        has_bose_burm = any(k in all_text for k in ['bose', 'burmester'])
        
        score = sum([has_rear_steer, has_soft_close, has_360, has_blind, has_pano, has_chrono, has_night, has_massage, has_ventilation, has_bose_burm])
        
        print("==================================================")
        print(f"[{country}][{color}] {city} | {cost} | {km} km | Reg: {reg} | Score: {score}/10")
        print(f"  RearSteer:{has_rear_steer} | SoftClose:{has_soft_close} | 360Cam:{has_360} | BlindSpot:{has_blind} | Pano:{has_pano}")
        print(f"  SportChrono:{has_chrono} | NightVision:{has_night} | Massage:{has_massage} | Ventil:{has_ventilation} | Sound:{has_bose_burm}")
        print(f"  URL: {u}")
        print(f"  Desc: {desc[:280].replace(chr(10), ' ')}")
    except Exception as e:
        pass
