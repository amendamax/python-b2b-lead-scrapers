import requests
import json
import bs4
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Search mobile.de / autoscout for Surround View
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

url = 'https://www.autoscout24.de/lst/porsche/macan/ve_diesel?sort=standard&desc=0&ustate=N%2CU&fregfrom=2016&fregto=2018&powerfrom=188&kmto=130000'
r = requests.get(url, headers=headers, timeout=10)
soup = bs4.BeautifulSoup(r.text, 'html.parser')
script = soup.find('script', id='__NEXT_DATA__')

if script:
    data = json.loads(script.string)
    listings = data.get('props', {}).get('pageProps', {}).get('listings', [])
    print(f"Checking {len(listings)} listings:")
    for item in listings:
        u = 'https://www.autoscout24.de' + item.get('url', '')
        try:
            r_item = requests.get(u, headers=headers, timeout=10)
            soup_item = bs4.BeautifulSoup(r_item.text, 'html.parser')
            script_item = soup_item.find('script', id='__NEXT_DATA__')
            d_item = json.loads(script_item.string)
            details = d_item.get('props', {}).get('pageProps', {}).get('listingDetails', {})
            desc = bs4.BeautifulSoup(details.get('description', ''), 'html.parser').get_text().lower()
            eq = str(details.get('equipment', [])).lower()
            all_t = desc + ' ' + eq
            
            city = details.get('location', {}).get('city', '')
            price = details.get('prices', {}).get('public', {}).get('priceRaw')
            km = details.get('tracking', {}).get('mileage')
            reg = details.get('tracking', {}).get('firstRegistration')
            
            has_360 = any(k in all_t for k in ['surround view', '360', 'rundumsicht', 'area view'])
            has_blind = any(k in all_t for k in ['spurwechselassistent', 'totwinkel', 'blind spot', 'angolo cieco'])
            has_pano = any(k in all_t for k in ['panoramadach', 'schiebedach', 'tetto', 'toit'])
            has_lane = any(k in all_t for k in ['spurhalteassistent', 'lane assist', 'mantenimento corsia'])
            
            print(f"-> {city} ({reg}) | {price} € | {km} km | 360:{has_360} | BlindSpot:{has_blind} | Pano:{has_pano} | Lane:{has_lane}")
            if has_360 and has_blind:
                print(f"   *** MATCH BOTH 360 & BLIND SPOT ***: {u}")
        except Exception as e:
            pass
