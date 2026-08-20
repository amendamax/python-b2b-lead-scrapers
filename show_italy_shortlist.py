import requests
import bs4
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

urls = [
    ('Imperia (Liguria - 110 km)', 'https://www.autoscout24.it/annunci/porsche-macan-macan-3-0d-s-260cv-pdk-my16-diesel-grigio-cat_ma57mo20311-3bb8724b-1447-490d-bbf1-88af11ace5a7'),
    ('Formello (Roma)', 'https://www.autoscout24.it/annunci/porsche-macan-macan-3-0d-s-250cv-pdk-my16-diesel-nero-cat_ma57mo20311-767017dc-6710-477c-be78-79d5e092a2d8'),
    ('Guidonia (Roma)', 'https://www.autoscout24.it/annunci/porsche-macan-3-0d-s-258cv-pdk-tetto-pasm-full-diesel-nero-cat_ma57mo20311-dd0ea206-4f26-4212-b26e-2e626cbaa16a'),
    ('Alba (Piemonte - 50 km)', 'https://www.autoscout24.it/annunci/porsche-macan-3-0d-s-258-cv-pdk-diesel-cat_ma57mo20311-a574b93f-5f1f-4450-bcf4-00b083bbe3c6')
]

for name, u in urls:
    r = requests.get(u, headers={'User-Agent': 'Mozilla/5.0'})
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    script = soup.find('script', id='__NEXT_DATA__')
    if script:
        d = json.loads(script.string)
        props = d.get('props', {}).get('pageProps', {}).get('listingDetails', {})
        t = props.get('tracking', {})
        p = props.get('prices', {}).get('public', {})
        veh = props.get('vehicle', {})
        desc = bs4.BeautifulSoup(props.get('description', ''), 'html.parser').get_text()
        
        print("========================================")
        print("NAME:", name)
        for div in soup.find_all(['div', 'span', 'p']):
            txt = div.get_text().strip()
            if 'km' in txt.lower() and any(c.isdigit() for c in txt) and len(txt) < 30:
                print("  KM:", txt)
                break
        for div in soup.find_all(['div', 'span', 'p']):
            txt = div.get_text().strip()
            if '€' in txt and len(txt) < 25:
                print("  PRICE:", txt)
                break
        print("POWER:", veh.get('rawPowerInKw'), "kW /", veh.get('powerInHp'), "HP")
        print("URL:", u)
        print("DESC:", desc[:250].replace('\n', ' '))
