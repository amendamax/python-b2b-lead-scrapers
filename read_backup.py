import json
with open(r'C:\Users\bratu\Documents\antigravity\conversations_backup\049703b9-c2f0-478d-82b4-696f8c1e76c6.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    if 'history' in data:
        for msg in data['history']:
            content = str(msg.get('content', ''))
            if '5m ' in content.lower() or '5 milioane' in content.lower() or '5.000.000' in content.lower():
                print(f"Role: {msg.get('role')} -> {content[:300]}")
