import json

with open('all_detailed_macan_italy.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for d in data:
    if d.get('kw') and d.get('kw') >= 189:
        print("Oras:", d.get('city'), "| Pret:", d.get('price'), "| Kw:", d.get('kw'))
        print("  Tetto:", d.get('has_tetto'), "| Privacy:", d.get('has_vetri'), "| Corsia:", d.get('has_corsia'))
        print("  URL:", d.get('url'))
        print("  Desc:", d.get('desc')[:250])
        print("-----------------------------------------")
