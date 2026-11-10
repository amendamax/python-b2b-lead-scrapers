import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

keys = [
    ("PillBot 1", "pill-scam-radar/pill-bot-1-4d5f1834bade.json"),
    ("PillBot 2 / Old JobScam", "pill-scam-radar/pill-bot-2.json"),
    ("Broker Key", "dating-photo-checker/keys/broker-indexing-key.json"),
    ("Dating Key", "dating-photo-checker/keys/dating-indexing-key.json"),
    ("New JobScam Dedicated", "job-scam-radar/keys/jobscam-dedicated.json"),
    ("Solar Indexer", "C:/Users/bratu/Downloads/solar-indexer-0adcad788b8c.json"),
]

endpoint = 'https://indexing.googleapis.com/v3/urlNotifications:publish'

for name, path in keys:
    try:
        creds = service_account.Credentials.from_service_account_file(path, scopes=['https://www.googleapis.com/auth/indexing'])
        req = google.auth.transport.requests.Request()
        creds.refresh(req)
        token = creds.token
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        payload = {'url': 'https://appscamradar.com/', 'type': 'URL_UPDATED'}
        res = requests.post(endpoint, headers=headers, json=payload)
        data = json.load(open(path))
        print(f"[{name}] ({data.get('client_email')}): Status={res.status_code}")
    except Exception as e:
        print(f"[{name}]: Error {e}")
