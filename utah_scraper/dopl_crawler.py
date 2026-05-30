from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re
from datetime import datetime

def parse_date(date_str):
    """Parses date string in MM/DD/YYYY format and returns a datetime object, or None."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str.strip(), "%m/%d/%y")
    except ValueError:
        try:
            return datetime.strptime(date_str.strip(), "%m/%d/%Y")
        except ValueError:
            return None

def scrape_dopl_leads(limit_leads=100):
    """Scrapes Utah DOPL database for active Plumbing/HVAC contractor entities registered prior to 2005."""
    leads = []
    seen_licenses = set()
    
    keywords = ["Plumbing", "HVAC", "Heating", "Air", "Mechanical"]
    
    with sync_playwright() as p:
        print("[DOPL Scraper] Launching Chromium in headful mode to bypass anti-bot...")
        # Launching headful ensures the reCAPTCHA v3 score remains human-like!
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        context.set_default_timeout(60000)
        page = context.new_page()
        
        for keyword in keywords:
            if len(leads) >= limit_leads:
                break
                
            print(f"\n[DOPL Scraper] Searching for keyword: '{keyword}'...")
            try:
                page.goto("https://secure.utah.gov/llv/search/index.html")
                page.wait_for_timeout(4000) # Give reCAPTCHA v3 time to load and run
                
                # 1. Fill search query
                page.fill("input[name='fullName']", keyword)
                page.wait_for_timeout(1000)
                
                # 2. Check Contractor checkbox
                page.check("input[name='item38']")
                page.wait_for_timeout(1000)
                
                # 3. Select CONTAINING search
                page.click("input[name='startsWith'][value='false']")
                page.wait_for_timeout(1000)
                
                # 4. Click Search
                page.click("input[type='submit'][value='Search']")
                page.wait_for_timeout(5000)
                
                current_page = 1
                max_pages_per_keyword = 50 # Crawl up to 50 pages of results per keyword!
                
                while current_page <= max_pages_per_keyword:
                    html = page.content()
                    soup = BeautifulSoup(html, 'html.parser')
                    table = soup.find('table', class_='resultsTable')
                    if not table:
                        print(f"[DOPL Scraper] No results table found for '{keyword}' on Page {current_page}.")
                        break
                        
                    rows = table.find_all('tr')[1:] # Skip header
                    print(f"[DOPL Scraper] Page {current_page}: Found {len(rows)} potential results.")
                    
                    # Loop through rows and look for active ones
                    for idx, row in enumerate(rows, start=1):
                        if len(leads) >= limit_leads:
                            break
                            
                        cols = [td.text.strip() for td in row.find_all('td')]
                        if len(cols) < 5:
                            continue
                            
                        name = cols[0]
                        status = cols[4]
                        license_num = cols[3]
                        
                        if status != 'ACTIVE':
                            continue
                            
                        if license_num in seen_licenses:
                            continue
                            
                        print(f"[DOPL Scraper] Page {current_page} [{idx}/{len(rows)}] Inspecting active entity: {name} ({license_num})...")
                        
                        # Click details link inside that row
                        link_selector = f"table.resultsTable tr:nth-child({idx + 1}) td a"
                        try:
                            page.click(link_selector)
                            page.wait_for_timeout(4000)
                            
                            detail_html = page.content()
                            detail_soup = BeautifulSoup(detail_html, 'html.parser')
                            
                            # Parse details table
                            detail_table = detail_soup.find('table')
                            if not detail_table:
                                print("[DOPL Scraper] Detail table not found. Going back...")
                                page.go_back()
                                page.wait_for_timeout(2000)
                                continue
                                
                            # Extract basic info
                            info = {}
                            for r in detail_table.find_all('tr'):
                                cells = [td.text.strip() for td in r.find_all(['td', 'th'])]
                                if len(cells) >= 2:
                                    key = cells[0].replace(':', '').strip().lower()
                                    val = cells[1].strip()
                                    info[key] = val
                                    
                            # Extract qualifications table
                            qual_table = detail_soup.find_all('table')
                            classifications = []
                            qualifier = "N/A"
                            if len(qual_table) >= 2:
                                for r in qual_table[1].find_all('tr')[1:]:
                                    cells = [td.text.strip() for td in r.find_all('td')]
                                    if len(cells) >= 2:
                                        classifications.append(cells[0])
                                        qualifier = cells[1]
                                        
                            # Check issue date filter (< 2005)
                            issue_date_str = info.get('original issue date', '')
                            issue_date = parse_date(issue_date_str)
                            
                            # Apply filters
                            profession = info.get('profession', '').lower()
                            lic_type = info.get('license type', '').lower()
                            lic_status = info.get('license status', '').lower()
                            
                            is_contractor = 'contractor' in profession or 'contractor' in lic_type
                            is_active = 'active' in lic_status
                            is_pre_2005 = issue_date and issue_date.year < 2005
                            
                            if is_contractor and is_active and is_pre_2005:
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
                                seen_licenses.add(license_num)
                                print(f"  -> SUCCESS: Qualified lead added (Registered: {issue_date_str}). Total: {len(leads)}")
                            else:
                                reasons = []
                                if not is_contractor: reasons.append("Not Contractor")
                                if not is_active: reasons.append("Not Active")
                                if not is_pre_2005: reasons.append(f"Registered {issue_date_str} (not pre-2005)")
                                print(f"  -> SKIPPED: {', '.join(reasons)}")
                                
                            # Navigate back to results page
                            page.go_back()
                            page.wait_for_timeout(3000)
                            
                        except Exception as ex:
                            print(f"[DOPL Scraper] Error scraping details for {name}: {ex}")
                            print("[DOPL Scraper] Sleeping 60s to clear rate limit/captcha block...")
                            page.wait_for_timeout(60000)
                            try:
                                page.goto("https://secure.utah.gov/llv/search/index.html")
                            except Exception:
                                print("[DOPL Scraper] Retry goto failed. Recreating page...")
                                page.close()
                                page = context.new_page()
                                page.goto("https://secure.utah.gov/llv/search/index.html")
                            page.wait_for_timeout(3000)
                            # Re-perform search to recover page state if it got lost
                            page.fill("input[name='fullName']", keyword)
                            page.wait_for_timeout(1000)
                            page.check("input[name='item38']")
                            page.wait_for_timeout(1000)
                            page.click("input[name='startsWith'][value='false']")
                            page.wait_for_timeout(1000)
                            page.click("input[type='submit'][value='Search']")
                            page.wait_for_timeout(5000)
                            # Navigate back to the current results page
                            for p_num in range(2, current_page + 1):
                                page.click("a#pagination-next")
                                page.wait_for_timeout(5000)
                                
                    if len(leads) >= limit_leads:
                        break
                        
                    # Handle pagination next button click
                    next_btn = page.locator("a#pagination-next")
                    if next_btn.count() > 0 and next_btn.is_visible():
                        print(f"[DOPL Scraper] Clicking Next page (going to Page {current_page + 1})...")
                        next_btn.click()
                        page.wait_for_timeout(5000)
                        current_page += 1
                    else:
                        print(f"[DOPL Scraper] No more pages for keyword '{keyword}'.")
                        break
                        
            except Exception as e:
                print(f"[DOPL Scraper] Error during keyword search '{keyword}': {e}")
                
        browser.close()
        
    print(f"\n[DOPL Scraper] Completed! Extracted {len(leads)} qualified leads from DOPL.")
    return leads
