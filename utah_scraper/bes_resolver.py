from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

def clean_company_name_broad(name):
    cleaned = name.upper()
    # Strip corporate endings
    cleaned = re.sub(r'\b(INC|LLC|CORP|CO|LTD|DBA|PARTNERSHIP)\b.*$', '', cleaned)
    # Strip dots, commas
    cleaned = cleaned.replace(".", "").replace(",", "").strip()
    words = cleaned.split()
    search_words = []
    for w in words:
        search_words.append(w)
        if w in ["PLUMBING", "HVAC", "HEATING", "AIR", "MECHANICAL", "CONTRACTING", "CONTRACTORS"]:
            break
    return " ".join(search_words[:4]).strip()

def resolve_street_addresses(leads):
    """Cross-references each company lead with the Utah Division of Corporations registry (BES) to resolve street addresses."""
    print(f"\n[BES Resolver] Enriching {len(leads)} leads with verified street addresses...")
    
    with sync_playwright() as p:
        print("[BES Resolver] Launching Chromium...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        for idx, lead in enumerate(leads, start=1):
            company_name = lead["company_name"]
            print(f"[BES Resolver] [{idx}/{len(leads)}] Resolving address for: {company_name}...")
            
            # Default values
            lead["physical_address"] = "N/A"
            lead["mailing_address"] = "N/A"
            lead["phone_number"] = "N/A"
            lead["registered_agent"] = lead["qualifier_name"]
            
            # Multi-stage queries to attempt
            queries_to_try = [company_name, clean_company_name_broad(company_name)]
            resolved = False
            
            for q_idx, query in enumerate(queries_to_try, start=1):
                if resolved:
                    break
                try:
                    # 1. Navigate to BES home and click search to establish session
                    page.goto("https://secure.utah.gov/bes/")
                    page.click("text=Search Business Entity Records")
                    page.wait_for_timeout(3000)
                    
                    # 2. Fill the company name query
                    page.fill("input[name='BusinessSearch_Index_txtEntityName']", query)
                    page.click("input[name='btnSearch']")
                    page.wait_for_timeout(4000)
                    
                    # Check if results loaded
                    if "OnlineBusinessAndMarkSearchResult" not in page.url:
                        continue
                        
                    locator_rows = page.locator("table tr").all()
                    target_row = None
                    is_fallback = False
                    
                    # Pass 1: Look for an Active row match
                    for r in locator_rows:
                        cells = r.locator("td").all_text_contents()
                        if len(cells) >= 4:
                            name = cells[0].strip()
                            status = cells[3].strip()
                            if name != "" and status.lower() == 'active':
                                target_row = r
                                break
                                
                    # Pass 2: Fallback to Inactive/Dissolved matching row
                    if not target_row:
                        for r in locator_rows:
                            cells = r.locator("td").all_text_contents()
                            if len(cells) >= 4:
                                name = cells[0].strip()
                                status = cells[3].strip()
                                if name != "" and status != "":
                                    target_row = r
                                    is_fallback = True
                                    break
                                    
                    if not target_row:
                        continue
                        
                    # 3. Click the target result row link
                    target_row.locator("td a").first.click()
                    page.wait_for_timeout(4000)
                    
                    if "BusinessInformation" not in page.url:
                        continue
                        
                    detail_html = page.content()
                    detail_soup = BeautifulSoup(detail_html, 'html.parser')
                    
                    # Parse all panels
                    panels = {}
                    for panel in detail_soup.find_all(class_="panel"):
                        heading = panel.find(class_="panel-heading")
                        if not heading:
                            continue
                        heading_text = heading.text.strip().lower()
                        
                        body = panel.find(class_="panel-body")
                        if not body:
                            continue
                            
                        panel_data = {}
                        for label in body.find_all('label'):
                            label_text = label.text.strip().rstrip(':').strip().lower()
                            parent_div = label.find_parent('div')
                            if parent_div:
                                next_sibling = parent_div.find_next_sibling('div')
                                if next_sibling:
                                    classes = next_sibling.get('class', [])
                                    if 'label-side' not in classes:
                                        value_text = next_sibling.text.strip()
                                        value_text = re.sub(r'\s+', ' ', value_text)
                                        panel_data[label_text] = value_text
                                        
                        panels[heading_text] = panel_data
                    
                    # Extract values from parsed panels
                    # 1. Registered Agent
                    agent_info = panels.get("registered agent information", {})
                    agent_name = agent_info.get("name", lead["qualifier_name"])
                    agent_street = agent_info.get("street address", "N/A")
                    
                    if agent_name and agent_name != "N/A":
                        lead["registered_agent"] = agent_name
                        
                    # 2. Addresses
                    addr_info = panels.get("address information", {})
                    phys_addr = addr_info.get("physical address", "N/A")
                    mail_addr = addr_info.get("mailing address", "N/A")
                    
                    # Clean and resolve addresses
                    if phys_addr and phys_addr != "N/A" and phys_addr != "":
                        lead["physical_address"] = phys_addr
                        
                    if mail_addr and mail_addr != "N/A" and mail_addr != "":
                        lead["mailing_address"] = mail_addr
                        
                    # Fallback address resolution using agent street
                    if agent_street and agent_street != "N/A" and agent_street != "":
                        # If physical address is missing, or is a PO box but agent street is a real street address,
                        # we should use agent street for physical address
                        if lead["physical_address"] == "N/A":
                            lead["physical_address"] = agent_street
                        elif "po box" in lead["physical_address"].lower() and "po box" not in agent_street.lower():
                            # Save the PO box to mailing address if mailing is empty
                            if lead["mailing_address"] == "N/A" or lead["mailing_address"] == "":
                                lead["mailing_address"] = lead["physical_address"]
                            lead["physical_address"] = agent_street
                            
                    print(f"  -> SUCCESS (Query '{query}'): Registered Agent: {lead['registered_agent']} | Address: {lead['physical_address']}")
                    resolved = True
                    
                except Exception as e:
                    print(f"  -> Error on query '{query}' for {company_name}: {e}")
            
            if not resolved:
                print(f"  -> FAILED: Could not resolve BES details for {company_name}")
                
        browser.close()
        
    print("[BES Resolver] Address enrichment completed successfully.")
    return leads
