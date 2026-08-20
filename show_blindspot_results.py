import json
import os

if os.path.exists('black_blue_with_blindspot.json'):
    with open('black_blue_with_blindspot.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print("Total matches found:", len(data))
    for d in data:
        print("Color:", d.get('color'), "| City:", d.get('city'), "| Price:", d.get('price'))
        print("  Km:", d.get('km'), "| Reg:", d.get('reg'), "| Pano:", d.get('has_pano'), "| 360:", d.get('has_360'))
        print("  URL:", d.get('url'))
        print("---------------------------------------------")
else:
    print("Not ready yet")
