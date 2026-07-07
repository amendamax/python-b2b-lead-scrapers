import requests
import json

token = "8677428441:AAEKsz-dfn_zlF7asRXEy1qtutCYPQOdLdE"
url = f"https://api.telegram.org/bot{token}/getUpdates"

print(f"Fetching updates from Telegram Bot...")
try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: Status {response.status_code}, Response: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
