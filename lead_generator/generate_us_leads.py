import os
import sys
import pandas as pd
from lead_scraper import B2BLeadScraper

def main():
    print("Starting B2B Lead Generation for 'sine-si' (US leads with NO website)...")
    scraper = B2BLeadScraper()
    
    # We will search for plumbers and HVAC contractors in Miami, FL and Houston, TX
    queries = [
        {"term": "plumber", "loc": "Miami, FL"},
        {"term": "hvac", "loc": "Houston, TX"},
        {"term": "electrician", "loc": "Dallas, TX"}
    ]
    
    collected_leads = []
    target_count = 15
    
    def log_progress(page, max_pages, msg):
        print(f"  [Page {page}/{max_pages}] {msg}")
        
    for q in queries:
        if len(collected_leads) >= target_count:
            break
            
        print(f"\nSearching for '{q['term']}' in '{q['loc']}'...")
        # Scrape 3 pages per query to find plenty of leads without websites
        leads = scraper.scrape_leads(q['term'], q['loc'], max_pages=3, progress_callback=log_progress)
        
        for lead in leads:
            if len(collected_leads) >= target_count:
                break
                
            # Filter for leads with NO website
            website = lead.get("Website", "N/A")
            if not website or website == "N/A":
                # Parse City + State from address
                address = lead.get("Address", "N/A")
                city_state = "N/A"
                if address != "N/A":
                    parts = address.split(",")
                    if len(parts) >= 2:
                        city_state = f"{parts[-2].strip()}, {parts[-1].strip().split(' ')[0]}" # City, State Zip
                
                # Check for duplicates
                is_duplicate = any(l["Phone"] == lead["Phone"] for l in collected_leads)
                if not is_duplicate and lead["Phone"] != "N/A":
                    collected_leads.append({
                        "Business Name": lead["Business Name"],
                        "Phone": lead["Phone"],
                        "Email (if available)": "N/A", # Yellowpages does not show email directly without website scraping
                        "City + State": city_state if city_state != "N/A" else q["loc"],
                        "Niche": q["term"].capitalize(),
                        "Notes": "Identified as local service business with completely missing online presence (no website)."
                    })
                    print(f"  [+] Found Lead: {lead['Business Name']} | Phone: {lead['Phone']}")
                    
    print(f"\nCollected {len(collected_leads)} leads out of {target_count} target.")
    
    # Save to Excel
    df = pd.DataFrame(collected_leads)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "us_no_website_leads_sample.xlsx")
    
    df.to_excel(output_path, index=False)
    print(f"\n[SUCCESS] Leads successfully exported to: {output_path}")
    
    # Print the table preview
    print("\nLeads Preview:")
    print(df.to_string())

if __name__ == "__main__":
    main()
