import os
import json
import sqlite3
import requests
import time
from datetime import datetime
from google.oauth2 import service_account
from google.auth.transport.requests import Request

# ----------------- CONFIGURARE -----------------
DB_PATH = "database.db"
KEY_1_PATH = os.path.join("keys", "broker-indexing-key.json")
KEY_2_PATH = os.path.join("keys", "dating-indexing-key.json")
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

# Fisiere de memorie (unde salvam ultimul ID indexat)
TRACKER_BROKER = "last_id_broker.txt"
TRACKER_DATING = "last_id_dating.txt"

DOMAIN_BROKER = "https://isbrokersafe.com/scam-reports"
DOMAIN_DATING = "https://verifydating.net/scam-profile" # SAU CUM E URL-UL TAU EXACT (ex: /profile/)

def get_last_id(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return int(f.read().strip())
    return 0

def save_last_id(filename, last_id):
    with open(filename, 'w') as f:
        f.write(str(last_id))

def get_access_token(key_path):
    if not os.path.exists(key_path):
        return None
    try:
        credentials = service_account.Credentials.from_service_account_file(
            key_path,
            scopes=["https://www.googleapis.com/auth/indexing"]
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print(f"Eroare generare token din {key_path}: {e}")
        return None

def submit_to_google(url, token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = {
        "url": url,
        "type": "URL_UPDATED"
    }
    return requests.post(ENDPOINT, headers=headers, json=payload)

def main():
    print(f"[{datetime.now()}] Incepem Job-ul de Indexare...")
    
    # Incarcam ambele chei in memorie
    keys = [KEY_1_PATH, KEY_2_PATH]
    current_key_idx = 0
    token = get_access_token(keys[current_key_idx])
    
    if not token:
        print("EROARE CRITICA: Nu am putut genera token-ul pentru prima cheie.")
        return

    # Conectare BD
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- 1. PRELUAM NOII BROKERI ---
    last_broker_id = get_last_id(TRACKER_BROKER)
    cursor.execute("SELECT id, slug FROM regulatory_scam_reports WHERE id > ? ORDER BY id ASC LIMIT 200", (last_broker_id,))
    new_brokers = cursor.fetchall()
    
    # --- 2. PRELUAM NOILE PROFILE DATING ---
    last_dating_id = get_last_id(TRACKER_DATING)
    cursor.execute("SELECT id, slug FROM dating_scam_profiles WHERE id > ? ORDER BY id ASC LIMIT 200", (last_dating_id,))
    new_dating = cursor.fetchall()

    # Generam lista mixta de joburi: (url, type, id)
    jobs = []
    for row in new_brokers:
        jobs.append((f"{DOMAIN_BROKER}/{row[1]}", "broker", row[0]))
    for row in new_dating:
        jobs.append((f"{DOMAIN_DATING}/{row[1]}", "dating", row[0]))

    if not jobs:
        print("Nu exista inregistrari noi in baza de date. Totul e la zi!")
        return

    print(f"Avem de trimis {len(jobs)} URL-uri (noi).")
    
    success_count = 0
    quota_exhausted = False

    for url, category, db_id in jobs:
        if quota_exhausted:
            break

        res = submit_to_google(url, token)
        
        if res.status_code == 200:
            print(f"[OK] Indexat -> {url}")
            success_count += 1
            # Salvam progresul instant
            if category == "broker":
                save_last_id(TRACKER_BROKER, db_id)
            else:
                save_last_id(TRACKER_DATING, db_id)
            
            time.sleep(0.5) # O mica pauza ca sa nu spammam Google prea agresiv
            
        elif res.status_code == 429:
            print(f"[ALERTA] Am atins limita (Quota Exceeded) pe Cheia {current_key_idx + 1}!")
            # Trecem la cheia 2 daca exista
            current_key_idx += 1
            if current_key_idx < len(keys):
                print(f"Switching la Cheia {current_key_idx + 1}...")
                token = get_access_token(keys[current_key_idx])
                if token:
                    # Reincercam acelasi URL cu noua cheie
                    res2 = submit_to_google(url, token)
                    if res2.status_code == 200:
                        print(f"[OK] Indexat -> {url}")
                        success_count += 1
                        if category == "broker": save_last_id(TRACKER_BROKER, db_id)
                        else: save_last_id(TRACKER_DATING, db_id)
                    else:
                        print(f"[FAIL pe cheia 2] {url} - {res2.status_code}")
                else:
                    quota_exhausted = True
            else:
                print("Am epuizat AMBELE chei! Ne oprim pe ziua de azi.")
                quota_exhausted = True
        else:
            print(f"[EROARE] Cod {res.status_code} la {url}: {res.text}")

    print(f"Finalizat. Trimise cu succes azi: {success_count}.")
    conn.close()

if __name__ == '__main__':
    main()
