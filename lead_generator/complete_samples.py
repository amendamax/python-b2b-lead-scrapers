import os
import sys
import time
import random
import pandas as pd
from curl_cffi import requests
from bs4 import BeautifulSoup
import urllib.parse
from lead_scraper import B2BLeadScraper

def generate_us_leads():
    print("\n--- Generating US Leads (15 leads, no website) ---")
    scraper = B2BLeadScraper()
    
    # We expand the query list to guarantee 15 leads even with rate-limits
    queries = [
        {"term": "plumber", "loc": "Miami, FL"},
        {"term": "hvac", "loc": "Houston, TX"},
        {"term": "roofer", "loc": "Phoenix, AZ"},
        {"term": "electrician", "loc": "Atlanta, GA"},
        {"term": "painter", "loc": "Denver, CO"},
        {"term": "landscaper", "loc": "Tampa, FL"},
        {"term": "handyman", "loc": "Dallas, TX"}
    ]
    
    collected_leads = []
    target_count = 15
    
    for q in queries:
        if len(collected_leads) >= target_count:
            break
            
        print(f"Searching for '{q['term']}' in '{q['loc']}'...")
        try:
            leads = scraper.scrape_leads(q['term'], q['loc'], max_pages=2, progress_callback=lambda p, m, msg: None)
            
            for lead in leads:
                if len(collected_leads) >= target_count:
                    break
                    
                website = lead.get("Website", "N/A")
                if not website or website == "N/A":
                    address = lead.get("Address", "N/A")
                    city_state = "N/A"
                    if address != "N/A":
                        parts = address.split(",")
                        if len(parts) >= 2:
                            city_state = f"{parts[-2].strip()}, {parts[-1].strip().split(' ')[0]}"
                            
                    is_duplicate = any(l["Phone"] == lead["Phone"] for l in collected_leads)
                    if not is_duplicate and lead["Phone"] != "N/A":
                        collected_leads.append({
                            "Business Name": lead["Business Name"],
                            "Phone": lead["Phone"],
                            "Email (if available)": "N/A",
                            "City + State": city_state if city_state != "N/A" else q["loc"],
                            "Niche": q["term"].capitalize(),
                            "Notes": "No website found on public business directory listings."
                        })
                        print(f"  [+] Found US Lead: {lead['Business Name']} | Phone: {lead['Phone']}")
            
            # Short sleep to prevent block
            time.sleep(2.5)
        except Exception as e:
            print(f"  [!] Error during search: {e}")
            
    # Export US Leads
    df_us = pd.DataFrame(collected_leads)
    output_path_us = os.path.join(os.path.dirname(os.path.abspath(__file__)), "us_no_website_leads_sample.xlsx")
    df_us.to_excel(output_path_us, index=False)
    print(f"[SUCCESS] Saved {len(df_us)} US leads to: {output_path_us}")
    return df_us


def generate_italian_leads():
    print("\n--- Generating Italian Leads (10 leads, no website) ---")
    session = requests.Session(impersonate="chrome")
    
    # We will search for dentists (dentisti) and restaurants (ristoranti) in Milano and Roma
    queries = [
        {"term": "dentisti", "loc": "Milano"},
        {"term": "ristoranti", "loc": "Milano"},
        {"term": "dentisti", "loc": "Roma"},
        {"term": "ristoranti", "loc": "Roma"}
    ]
    
    collected_leads = []
    target_count = 10
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    for q in queries:
        if len(collected_leads) >= target_count:
            break
            
        url = f"https://www.paginegialle.it/ricerca/{q['term']}/{q['loc']}"
        print(f"Searching for '{q['term']}' in '{q['loc']}'...")
        
        try:
            response = session.get(url, headers=headers, timeout=15)
            if response.status_code != 200:
                print(f"  [!] PagineGialle returned status {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'lxml')
            items = soup.select('.search-itm')
            print(f"  Found {len(items)} initial listings on page.")
            
            for item in items:
                if len(collected_leads) >= target_count:
                    break
                    
                name_el = item.select_one('.search-itm__rag')
                if not name_el:
                    continue
                name = name_el.text.strip()
                name = name.replace("Azienda cliente verificata", "").strip()
                
                # Extract phone directly from the main listing page element
                phone_el = item.select_one('.search-itm__phone-item')
                phone = phone_el.text.strip() if phone_el else "N/A"
                
                # Extract address directly from the main listing page element
                address_el = item.select_one('.search-itm__adr div')
                address = address_el.text.strip() if address_el else q["loc"]
                
                # Fetch details page ONLY to check if there is an external website link
                detail_link_el = item.select_one('.search-itm__dx a') or item.select_one('a')
                if not detail_link_el:
                    continue
                detail_url = detail_link_el.get('href', '')
                if not detail_url.startswith('http'):
                    detail_url = urllib.parse.urljoin("https://www.paginegialle.it", detail_url)
                    
                # Sleep to be polite
                time.sleep(random.uniform(0.5, 1.0))
                
                res = session.get(detail_url, headers=headers, timeout=15)
                detail_soup = BeautifulSoup(res.text, 'lxml')
                
                # Check for website link (looks for 'Sito web' text)
                has_website = False
                a_tags = detail_soup.find_all('a')
                for a in a_tags:
                    text = a.text.strip().lower()
                    if 'sito web' in text or 'sito' == text:
                        has_website = True
                        break
                
                # If it has no website and we successfully parsed the phone number
                if not has_website and phone != "N/A":
                    # Check duplicate
                    is_duplicate = any(l["Telefono"] == phone for l in collected_leads)
                    if not is_duplicate:
                        collected_leads.append({
                            "Nome Attività": name,
                            "Telefono": phone,
                            "Email": "N/A",
                            "Città": q["loc"],
                            "Indirizzo": address,
                            "Niche": "Dentista" if q["term"] == "dentisti" else "Ristorante",
                            "Note": "Sito web non presente. Ottimo target per proposta di rifacimento/creazione sito web."
                        })
                        print(f"  [+] Found IT Lead: {name[:40]} | Phone: {phone}")
                        
        except Exception as e:
            print(f"  [!] Error processing: {e}")
            
    # Export Italian Leads
    df_it = pd.DataFrame(collected_leads)
    output_path_it = os.path.join(os.path.dirname(os.path.abspath(__file__)), "italian_no_website_leads_sample.xlsx")
    df_it.to_excel(output_path_it, index=False)
    print(f"[SUCCESS] Saved {len(df_it)} Italian leads to: {output_path_it}")
    return df_it


def main():
    print("=== STARTING DUAL SAMPLE GENERATION ===")
    us_data = generate_us_leads()
    it_data = generate_italian_leads()
    print("\n=== SAMPLE GENERATION COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
