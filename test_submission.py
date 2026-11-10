import json
import requests
from google.oauth2 import service_account
import google.auth.transport.requests

tests = [
    ("JobScam", "job-scam-radar/keys/jobscam-dedicated.json", "https://jobscamradar.com/"),
    ("PillScam", "pill-scam-radar/pill-bot-1-4d5f1834bade.json", "https://pillscamradar.com/"),
    ("Broker", "dating-photo-checker/keys/broker-indexing-key.json", "https://isbrokersafe.com/"),
    ("Dating", "dating-photo-checker/keys/dating-indexing-key.json", "https://verifydating.net/")
]

endpoint = 'https://indexing.googleapis.com/v3/urlNotifications:publish'

for name, key_path, url in tests:
    try:
        creds = service_account.Credentials.from_service_account_file(key_path, scopes=['https://www.googleapis.com/auth/indexing'])
        req = google.auth.transport.requests.Request()
        creds.refresh(req)
        token = creds.token
        headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
        payload = {'url': url, 'type': 'URL_UPDATED'}
        res = requests.post(endpoint, headers=headers, json=payload)
        print(f"[{name}] Status: {res.status_code} | Msg: {res.text[:120]}")
    except Exception as e:
        print(f"[{name}] Error: {e}")
