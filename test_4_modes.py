import urllib.request
import json

modes = ['solar', 'battery', 'heatpump', 'all']

for m in modes:
    payload = json.dumps({'cap': '00100', 'sqm': '120', 'bill': '150', 'mode': m}).encode('utf-8')
    req = urllib.request.Request(
        'https://calcolaincentivi.it/api/v1/energy/calculate',
        data=payload,
        headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"[{m.upper()}] Title: {data.get('system_title')} | Specs: {data.get('system_specs')} | Risparmio: €{data.get('savings_per_year')}/anno | Bonus: {data.get('bonus_percentage')}% | Con Sconto: €{data.get('estimated_cost_with_ecobonus')}")
    except Exception as e:
        print(f"[{m.upper()}] Error: {e}")
