import json
import requests
import bs4

with open('black_blue_with_blindspot.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for d in data:
    if d.get('color') in ['Schwarz', 'Blau'] and d.get('has_pano') and d.get('has_blind_spot'):
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
            
            print("========================================")
            print("COLOR:", d.get('color'), "| CITY:", props.get('location', {}).get('city'))
            print("PRICE:", prices.get('priceFormatted'), "| KM:", tracking.get('mileage'), "| REG:", tracking.get('firstRegistration'))
            print("URL:", u)
            print("DESC:", desc[:350].replace('\n', ' '))
        except Exception as e:
            pass
