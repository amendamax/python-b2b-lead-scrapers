import json
import os
from google.oauth2 import service_account
import google.auth.transport.requests

keys = [
    ("JobScam Dedicated", "C:/Users/bratu/Downloads/jobscam-dedicated-5dd0ad164181.json"),
    ("PillBot 1", "pill-scam-radar/pill-bot-1-4d5f1834bade.json"),
    ("Broker Key", "dating-photo-checker/keys/broker-indexing-key.json"),
    ("Dating Key", "dating-photo-checker/keys/dating-indexing-key.json"),
]

for name, key_path in keys:
    if not os.path.exists(key_path):
        print(f"[-] {name}: File NOT FOUND ({key_path})")
        continue
    try:
        data = json.load(open(key_path))
        email = data.get("client_email")
        project = data.get("project_id")
        creds = service_account.Credentials.from_service_account_file(
            key_path,
            scopes=["https://www.googleapis.com/auth/indexing"]
        )
        req = google.auth.transport.requests.Request()
        creds.refresh(req)
        token_len = len(creds.token) if creds.token else 0
        print(f"[+] {name}: OK! Project={project} | Email={email} | TokenLen={token_len}")
    except Exception as e:
        print(f"[-] {name}: ERROR -> {e}")
