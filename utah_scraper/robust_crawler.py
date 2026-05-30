import json
import os
import sys
import io
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

STATE_FILE = "dopl_scraper_state.json"

def parse_date(date_str):
    if not date_str: return None
    for fmt in ("%m/%d/%y", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            pass
    return None

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"keyword_index": 0, "current_page": 1, "leads": [], "seen_licenses": []}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def run_scraper_chunk():
    state = load_state()
    leads = state["leads"]
    seen_licenses = set(state["seen_licenses"])
    start_kw_idx = state["keyword_index"]
    start_page = state["current_page"]
    
    keywords = ["Plumbing", "HVAC", "Heating", "Air", "Mechanical"]
    
    if start_kw_idx >= len(keywords):
        return "DONE", leads
        
    with sync_playwright() as p:
        print("[Crawler] Launching Browser...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.set_default_timeout(60000)
        page = context.new_page()
        
        for kw_idx in range(start_kw_idx, len(keywords)):
            keyword = keywords[kw_idx]
            print(f"\n[Crawler] Keyword '{keyword}' | Starting from page {start_page}")
            
            try:
                page.goto("https://secure.utah.gov/llv/search/index.html")
                page.wait_for_timeout(3000)
                page.fill("input[name='fullName']", keyword)
                page.check("input[name='item38']")
                page.click("input[name='startsWith'][value='false']")
                page.click("input[type='submit'][value='Search']")
                page.wait_for_timeout(5000)
                
                # Fast forward to the page we left off
                current_page = 1
                while current_page < start_page:
                    print(f"Skipping page {current_page}...")
                    next_btn = page.locator("a#pagination-next")
                    if next_btn.count() > 0 and next_btn.is_visible():
                        next_btn.click()
                        page.wait_for_timeout(3000)
                        current_page += 1
                    else:
                        break
                        
                while current_page <= 50:
                    html = page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    table = soup.find('table', class_='resultsTable')
                    if not table:
                        print(f"No results table on page {current_page}. This means we are BLOCKED by ReCAPTCHA.")
                        raise Exception("Blocked by ReCAPTCHA (no table found).")
                        
                    rows = table.find_all('tr')[1:]
                    print(f"Page {current_page} has {len(rows)} rows.")
                    
                    for idx, row in enumerate(rows, start=1):
                        cols = [td.text.strip() for td in row.find_all('td')]
                        if len(cols) < 5: continue
                        name, license_num, status = cols[0], cols[3], cols[4]
                        
                        if status != 'ACTIVE' or license_num in seen_licenses:
                            continue
                            
                        # HEURISTIC: License numbers are sequential.
                        # 5725850 was issued in Sep 2004. 6200000+ is definitely post-2005.
                        try:
                            prefix = int(license_num.split('-')[0])
                            if prefix > 6200000:
                                print(f"[{idx}/{len(rows)}] Skipping {name} ({license_num}) - Prefix implies post-2005")
                                continue
                        except:
                            pass
                            
                        print(f"[{idx}/{len(rows)}] Inspecting: {name} ({license_num})...")
                        link_selector = f"table.resultsTable tr:nth-child({idx + 1}) td a"
                        
                        try:
                            page.click(link_selector)
                            page.wait_for_timeout(4000)
                            detail_html = page.content()
                            detail_soup = BeautifulSoup(detail_html, 'html.parser')
                            detail_table = detail_soup.find('table')
                            
                            if detail_table:
                                info = {}
                                for r in detail_table.find_all('tr'):
                                    cells = [td.text.strip() for td in r.find_all(['td', 'th'])]
                                    if len(cells) >= 2:
                                        info[cells[0].replace(':', '').strip().lower()] = cells[1].strip()
                                        
                                qual_table = detail_soup.find_all('table')
                                classifications = []
                                qualifier = "N/A"
                                if len(qual_table) >= 2:
                                    for r in qual_table[1].find_all('tr')[1:]:
                                        cells = [td.text.strip() for td in r.find_all('td')]
                                        if len(cells) >= 2:
                                            classifications.append(cells[0])
                                            qualifier = cells[1]
                                            
                                issue_date_str = info.get('original issue date', '')
                                issue_date = parse_date(issue_date_str)
                                
                                prof = info.get('profession', '').lower()
                                lic_type = info.get('license type', '').lower()
                                
                                is_contractor = 'contractor' in prof or 'contractor' in lic_type
                                is_pre_2005 = issue_date and issue_date.year < 2005
                                
                                if is_contractor and is_pre_2005:
                                    lead_data = {
                                        "company_name": info.get('name', name).upper(),
                                        "license_number": license_num,
                                        "original_issue_date": issue_date_str,
                                        "city_state_zip": info.get('city, state, zip, country', '').replace(' United States', '').strip(),
                                        "qualifier_name": qualifier,
                                        "classifications": ", ".join(classifications),
                                        "license_status": "Active"
                                    }
                                    leads.append(lead_data)
                                    print(f" -> QUALIFIED! Total valid leads so far: {len(leads)}")
                                else:
                                    print(" -> SKIPPED (Not pre-2005 or not contractor)")
                            
                            seen_licenses.add(license_num)
                            page.go_back()
                            page.wait_for_timeout(2000)
                            
                        except Exception as e:
                            print(f"Error on row {idx} (Rate limit/Timeout): {e}")
                            state["keyword_index"] = kw_idx
                            state["current_page"] = current_page
                            state["leads"] = leads
                            state["seen_licenses"] = list(seen_licenses)
                            save_state(state)
                            browser.close()
                            return "ERROR", leads
                    
                    # Page completed fully, save state
                    current_page += 1
                    state["keyword_index"] = kw_idx
                    state["current_page"] = current_page
                    state["leads"] = leads
                    state["seen_licenses"] = list(seen_licenses)
                    save_state(state)
                    
                    next_btn = page.locator("a#pagination-next")
                    if next_btn.count() > 0 and next_btn.is_visible():
                        next_btn.click()
                        page.wait_for_timeout(4000)
                    else:
                        break
                        
            except Exception as e:
                print(f"Keyword search error: {e}")
                state["keyword_index"] = kw_idx
                state["current_page"] = current_page
                state["leads"] = leads
                state["seen_licenses"] = list(seen_licenses)
                save_state(state)
                browser.close()
                return "ERROR", leads
            
            # Reset page for the next keyword
            start_page = 1
            
        browser.close()
        state["keyword_index"] = 999
        save_state(state)
        return "DONE", leads
