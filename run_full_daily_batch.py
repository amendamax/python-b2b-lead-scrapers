import urllib.request
import json
import time

def trigger_batch(site, count):
    url = f"https://radar-indexer.amendamax.workers.dev/trigger?site={site}&count={count}"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            return data
    except Exception as e:
        return {'status': 'ERROR', 'error': str(e)}

def run_site_quota(site_name, site_id, target_count, batch_size=35):
    print(f"\n==========================================")
    print(f"[*] Pornim indexarea pentru {site_name} (Tinta: {target_count} URLs)...")
    print(f"==========================================")
    
    total_processed = 0
    while total_processed < target_count:
        to_send = min(batch_size, target_count - total_processed)
        print(f"  -> Trimit batch de {to_send} pagini...")
        res = trigger_batch(site_id, to_send)
        status = res.get('status')
        processed = res.get('processed', 0)
        total_processed += processed
        print(f"     Status: {status} | Trimise in acest batch: {processed} | Total azi: {total_processed}")
        
        if status == 'QUOTA_EXCEEDED':
            print(f"  [!] S-a atins cota maxima permisa de Google (200/zi) pentru {site_name}.")
            break
        if status == 'EMPTY' or processed == 0:
            print(f"  [*] Toate paginile disponibile au fost indexate pentru {site_name}!")
            break
            
        time.sleep(1) # mica pauza intre batch-uri

# 1. JobScamRadar: are 47 de pagini ramase (le trimitem pe toate)
run_site_quota("JobScamRadar", "jobscam", 47, batch_size=35)

# 2. IsBrokerSafe: trimitem pana la 195 pagini (cota maxima Google)
run_site_quota("IsBrokerSafe", "broker", 195, batch_size=35)

# 3. VerifyDating: trimitem pana la 195 pagini (cota maxima Google)
run_site_quota("VerifyDating", "dating", 195, batch_size=35)

print("\n==========================================")
print("INDEXARE FINALIZATA CU SUCCES PENTRU ZIUA DE AZI!")
print("==========================================")
