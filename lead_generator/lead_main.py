from lead_scraper import B2BLeadScraper
from google_sheets_sync import LeadExportSyncManager
import os
import sys
import time

def print_banner():
    banner = """
==================================================================
        B2B LOCAL LEAD GENERATOR & SALES PIPELINE SYNC
==================================================================
   * Target Platform: Yellowpages.com (Local B2B Listings)
   * Tech Stack: Python, requests, BeautifulSoup, openpyxl, gspread
   * Features: Rotating Headers, Dynamic Class Rating Parsers,
               Zebra Striping, Google Sheets Sync, Excel Fallback
   * Excel Theme: Premium "Emerald Green" Pipeline Styling
==================================================================
    """
    print(banner)

# Realistic fallback mock B2B leads
# Used to demonstrate the sync/export pipeline when local testing triggers Yellowpages block rate-limiting
MOCK_LEADS = [
    {
        "Business Name": "Beacon Hill Dental",
        "Phone": "(617) 742-1234",
        "Address": "12 Beacon St, Boston, MA 02108",
        "Rating (1-5)": 4.5,
        "Reviews Count": 28,
        "Website": "http://www.beaconhilldental.com",
        "Profile URL": "https://www.yellowpages.com/boston-ma/mip/beacon-hill-dental-1"
    },
    {
        "Business Name": "Boston Dental Group",
        "Phone": "(617) 536-4567",
        "Address": "100 Boylston St, Boston, MA 02116",
        "Rating (1-5)": 5.0,
        "Reviews Count": 142,
        "Website": "http://www.bostondental.com",
        "Profile URL": "https://www.yellowpages.com/boston-ma/mip/boston-dental-group-2"
    },
    {
        "Business Name": "Gentle Dental Boston Common",
        "Phone": "(617) 262-0101",
        "Address": "200 Tremont St, Boston, MA 02111",
        "Rating (1-5)": 4.0,
        "Reviews Count": 96,
        "Website": "http://www.gentledental.com",
        "Profile URL": "https://www.yellowpages.com/boston-ma/mip/gentle-dental-3"
    },
    {
        "Business Name": "Back Bay Family Dentistry",
        "Phone": "(617) 859-7777",
        "Address": "500 Commonwealth Ave, Boston, MA 02215",
        "Rating (1-5)": 4.5,
        "Reviews Count": 54,
        "Website": "http://www.backbaydentistry.com",
        "Profile URL": "https://www.yellowpages.com/boston-ma/mip/back-bay-dentistry-4"
    },
    {
        "Business Name": "Downtown Boston Dental",
        "Phone": "(617) 227-0202",
        "Address": "85 Devonshire St, Boston, MA 02109",
        "Rating (1-5)": 4.8,
        "Reviews Count": 37,
        "Website": "http://www.downtownbostondental.com",
        "Profile URL": "https://www.yellowpages.com/boston-ma/mip/downtown-dental-5"
    },
    {
        "Business Name": "Tufts Dental Associates",
        "Phone": "(617) 636-6500",
        "Address": "1 Kneeland St, Boston, MA 02111",
        "Rating (1-5)": 3.8,
        "Reviews Count": 210,
        "Website": "http://www.tuftsdental.com",
        "Profile URL": "https://www.yellowpages.com/boston-ma/mip/tufts-dental-6"
    },
    {
        "Business Name": "Fenway Health Dental",
        "Phone": "(617) 927-6120",
        "Address": "1340 Boylston St, Boston, MA 02215",
        "Rating (1-5)": 4.2,
        "Reviews Count": 64,
        "Website": "http://www.fenwayhealth.org",
        "Profile URL": "https://www.yellowpages.com/boston-ma/mip/fenway-dental-7"
    },
    {
        "Business Name": "Boston University Dental",
        "Phone": "(617) 638-4700",
        "Address": "100 E Newton St, Boston, MA 02118",
        "Rating (1-5)": 4.0,
        "Reviews Count": 185,
        "Website": "http://www.bu.edu/dental",
        "Profile URL": "https://www.yellowpages.com/boston-ma/mip/bu-dental-8"
    },
    {
        "Business Name": "North End Dental Associates",
        "Phone": "(617) 523-2345",
        "Address": "244 Hanover St, Boston, MA 02113",
        "Rating (1-5)": 4.6,
        "Reviews Count": 19,
        "Website": "http://www.northenddental.com",
        "Profile URL": "https://www.yellowpages.com/boston-ma/mip/north-end-dental-9"
    },
    {
        "Business Name": "Commonwealth Dental Group",
        "Phone": "(617) 266-4664",
        "Address": "31 St James Ave, Boston, MA 02116",
        "Rating (1-5)": 4.9,
        "Reviews Count": 78,
        "Website": "http://www.commonwealthdental.com",
        "Profile URL": "https://www.yellowpages.com/boston-ma/mip/commonwealth-dental-10"
    }
]

def get_integer_input(prompt, default_val, min_val=1, max_val=10):
    while True:
        try:
            user_input = input(f"{prompt} [Default: {default_val}]: ").strip()
            if not user_input:
                return default_val
            val = int(user_input)
            if min_val <= val <= max_val:
                return val
            else:
                print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def get_string_input(prompt, default_val):
    user_input = input(f"{prompt} [Default: {default_val}]: ").strip()
    if not user_input:
        return default_val
    return user_input

def main():
    print_banner()
    
    print("[1] Lead Generation Configuration")
    search_term = get_string_input("Enter search keyword (e.g. dentist, plumber)", "dentist")
    location = get_string_input("Enter location (e.g. Boston, MA)", "Boston, MA")
    max_pages = get_integer_input("Enter number of pages to scrape (1-10)", default_val=1, min_val=1, max_val=10)
    
    print("\n[2] Export & Sync Options")
    google_sheet_input = input("Enter Google Sheet Name or URL (or press Enter to skip Google Sync): ").strip()
    output_file = get_string_input("Enter output Excel filename", "scraped_leads_pipeline.xlsx")
    
    if not output_file.lower().endswith('.xlsx'):
        output_file += '.xlsx'

    print("\n[3] Executing Yellowpages Scraper")
    print("-" * 55)
    
    scraper = B2BLeadScraper()
    export_manager = LeadExportSyncManager()
    
    # Progress callback
    def log_progress(page, total_pages, message):
        percent = int((page / total_pages) * 100)
        bar_length = 20
        filled_length = int(round(bar_length * page / total_pages))
        bar = '#' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f"\r[{bar}] {percent}% | Page {page}/{total_pages} | {message}")
        sys.stdout.flush()
        if page == total_pages and "completed" in message.lower():
            sys.stdout.write("\n")
            sys.stdout.flush()

    start_time = time.time()
    leads = scraper.scrape_leads(search_term, location, max_pages=max_pages, progress_callback=log_progress)
    elapsed_time = time.time() - start_time
    
    print("-" * 55)
    print(f"Scraper session completed in {elapsed_time:.2f} seconds.")
    
    is_mocked = False
    if not leads:
        print("\n[!] ALERT: Yellowpages rate limit or connection issue detected.")
        print("    -> Activating Safe Portfolio Mock Mode to demonstrate full pipeline...")
        time.sleep(1.0)
        leads = MOCK_LEADS
        is_mocked = True
        print(f"    Loaded {len(leads)} pristine dental clinic leads in Boston.")
    else:
        print(f"Successfully extracted {len(leads)} B2B leads.")

    # 4. Export & Synchronization
    print("\n[4] Executing Export & Synchronization Pipeline")
    print("-" * 55)
    
    sync_success = False
    google_url = ""
    
    if google_sheet_input:
        print(f"[>] Attempting to sync leads directly to Google Sheets: '{google_sheet_input}'...")
        try:
            google_url = export_manager.sync_to_google_sheets(leads, google_sheet_input)
            print("[+] Google Sheets sync completed successfully!")
            sync_success = True
        except FileNotFoundError:
            print("[!] GOOGLE SYNC SKIPPED: 'credentials.json' not found in this folder.")
            print("    (To enable Google Sheets Sync, create a Google Service Account key and save it here.)")
        except Exception as e:
            print(f"[!] GOOGLE SYNC ERROR: {str(e)}")
            
    # Always generate the local Excel backup with our signature Emerald Green design
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(workspace_dir, output_file)
    
    print(f"[>] Generating premium Excel lead file...")
    try:
        export_manager.export_to_local_excel(leads, output_path)
        print(f"[+] Local Excel lead report saved successfully!")
    except Exception as e:
        print(f"[!] ERROR generating Excel file: {str(e)}")

    # Display Executive Leads Summary
    ratings = [item['Rating (1-5)'] for item in leads if item['Rating (1-5)'] > 0]
    avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
    
    print("\n" + "=" * 45)
    print("          EXECUTIVE LEADS SUMMARY")
    print("=" * 45)
    print(f" Total B2B Leads Gathered : {len(leads)}")
    print(f" Average Leads Rating     : {avg_rating:.1f} / 5.0")
    print(f" Pipeline Target Keyword  : {search_term.upper()}")
    print(f" Target Region            : {location.upper()}")
    print(f" Google Sheets Synced     : {'YES (' + google_url[:30] + '...)' if sync_success else 'NO (Local Only)'}")
    print(f" Data Mode                : {'DEMO FALLBACK' if is_mocked else 'LIVE SCRAPED'}")
    print(f" Excel Report Styling     : EMERALD GREEN (SALES READY)")
    print("=" * 45)
    print(f"\nTip: Double-click '{output_file}' to view the beautiful Emerald Green lead lists and dynamic Excel formulas!")

if __name__ == "__main__":
    main()
