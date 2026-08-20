import json
import requests
import bs4

with open('italy_perfect_matches.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=== 190 kW Matches in Italy (Nero/Grigio/Blu with Tetto) ===")

for d in data:
    if d.get('kw') and d.get('kw') >= 188:
        u = d.get('url')
        try:
            r = requests.get(u, headers={'User-Agent': 'Mozilla/5.0'})
            soup = bs4.BeautifulSoup(r.text, 'html.parser')
            script = soup.find('script', id='__NEXT_DATA__')
            d_item = json.loads(script.string)
            props = d_item.get('props', {}).get('pageProps', {}).get('listingDetails', {})
            tracking = props.get('tracking', {})
            prices = props.get('prices', {}).get('public', {})
            desc = bs4.BeautifulSoup(props.get('description', ''), 'html.parser').get_text()
            eq = str([e.get('name') for e in props.get('equipment', [])])
            all_text = (desc + ' ' + eq).lower()
            
            has_blind = any(k in all_text for k in ['angolo cieco', 'cieco', 'blind spot', 'lca', 'cambio corsia', 'spurwechsel', 'totwinkel'])
            has_pano = any(k in all_text for k in ['tetto', 'panoramico', 'apribile', 'sunroof'])
            has_lane = any(k in all_text for k in ['corsia', 'lane', 'mantenimento', 'superamento', 'lka'])
            has_360 = any(k in all_text for k in ['surround view', '360', '360°', 'telecamera 360', 'top view'])
            has_cam = any(k in all_text for k in ['telecamera', 'camera', 'retrocamera', 'surround'])
            
            city = props.get('location', {}).get('city')
            cost = prices.get('priceFormatted')
            km = tracking.get('mileage')
            reg = tracking.get('firstRegistration')
            col = d.get('color')
            
            print("========================================")
            print(f"[{col}] {city} | {cost} | {km} km | {reg} | 190 kW")
            print(f"  Pano: {has_pano} | BlindSpot: {has_blind} | Lane: {has_lane} | 360Cam: {has_360} | Cam: {has_cam}")
            print(f"  URL: {u}")
            print(f"  Desc: {desc[:280].replace(chr(10), ' ')}")
        except Exception as e:
            print("Error:", e)
