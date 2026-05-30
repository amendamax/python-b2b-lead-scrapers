import os
import sys
import io
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from robust_crawler import run_scraper_chunk
from bes_resolver import resolve_street_addresses
from excel_formatter import format_excel_report
import shutil

def main():
    print("============================================================")
    print("      UTAH DOPL & CORPORATIONS B2B LEADS PIPELINE CRAWLER   ")
    print("============================================================")
    print("Target: Active HVAC & Plumbing Contractor Businesses (Pre-2005)")
    print("Mode: Bulletproof Stateful Execution (Handles ReCAPTCHA Blocks)")
    print("-" * 60)
    
    while True:
        status, leads = run_scraper_chunk()
        if status == "DONE":
            print(f"\n[Scraper] Finished all keywords! Total leads gathered: {len(leads)}")
            break
        print("\n[Scraper] Hit a timeout or anti-bot block.")
        print("[Scraper] Sleeping for 4 minutes to cool down before resuming...")
        time.sleep(240)
        
    if not leads:
        print("\n[Orchestrator] No qualified leads found. Exiting...")
        return
        
    print("\n[Orchestrator] Starting BES Address Resolution for all leads...")
    enriched_leads = resolve_street_addresses(leads)
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_xlsx = os.path.join(output_dir, "scraped_utah_contractors.xlsx")
    output_pdf = os.path.join(output_dir, "scraped_utah_contractors.pdf")
    
    print("\n[Orchestrator] Formatting Excel & PDF...")
    format_excel_report(enriched_leads, output_xlsx, output_pdf)
    
    desktop_xlsx = os.path.join(os.path.expanduser("~"), "Desktop", "UTAH_CONTRACTORS_FULL.xlsx")
    desktop_pdf = os.path.join(os.path.expanduser("~"), "Desktop", "UTAH_CONTRACTORS_FULL.pdf")
    try:
        shutil.copy(output_xlsx, desktop_xlsx)
        if os.path.exists(output_pdf):
            shutil.copy(output_pdf, desktop_pdf)
    except Exception as e:
        print(f"Failed to copy to Desktop: {e}")
        
    print("\n" + "=" * 60)
    print("                   PIPELINE COMPLETED SUCCESSFULLY               ")
    print("=" * 60)
    print(f"Total Qualified Leads Extracted: {len(enriched_leads)}")
    print(f"Excel Output Path: {desktop_xlsx}")
    print("-" * 60)

if __name__ == "__main__":
    main()
