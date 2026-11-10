import urllib.request
import json

sites = ['pillscam', 'broker', 'dating', 'appscam']

for s in sites:
    url = f"https://radar-indexer.amendamax.workers.dev/trigger?site={s}&count=5"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"[{s}] Status: {data.get('status')} | Processed: {data.get('processed')} | Errors: {data.get('errors')}")
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        print(f"[{s}] HTTP Error {e.code}: {body[:200]}")
    except Exception as e:
        print(f"[{s}] Error: {e}")
