import os
import shutil
from bes_resolver import resolve_street_addresses
from excel_formatter import format_excel_report

def main():
    print("=" * 60)
    print("      UTAH CONTRACTORS LEADS ENRICHMENT & COMPILATION PIEPELINE      ")
    print("=" * 60)
    print("Target: Enrich existing DOPL-extracted leads with verified BES addresses")
    print("-" * 60)
    
    # 1. Existing DOPL-scraped qualified pre-2005 contractor leads
    leads = [
        {
            "company_name": "A&E PLUMBING & CONTRACTING, INC.",
            "license_number": "4961149-5501",
            "original_issue_date": "03/04/2002",
            "qualifier_name": "Eric Richard Dansie",
            "classifications": "B100 - General Building Qualifier, P200 - General Plumbing Qualifier, S350 - HVAC Qualifier",
            "license_status": "Active"
        },
        {
            "company_name": "A-JACKS PLUMBING & HEATING, INC",
            "license_number": "263831-5501",
            "original_issue_date": "06/23/1993",
            "qualifier_name": "John J Murphy",
            "classifications": "P200 - General Plumbing Qualifier",
            "license_status": "Active"
        },
        {
            "company_name": "A-QUALITY PLUMBING, HEATING & COOLING, INC.",
            "license_number": "1278950-5501",
            "original_issue_date": "04/30/2001",
            "qualifier_name": "John Daniel England",
            "classifications": "P200 - General Plumbing Qualifier, B100 - General Building Qualifier, S350 - HVAC Qualifier",
            "license_status": "Active"
        },
        {
            "company_name": "A-TEAM PLUMBING, INC.",
            "license_number": "5725850-5501",
            "original_issue_date": "09/17/2004",
            "qualifier_name": "Wade Curtis Hanberg",
            "classifications": "P200 - General Plumbing Qualifier, B100 - General Building Qualifier, E100 - General Engineering Qualifier",
            "license_status": "Active"
        },
        {
            "company_name": "A-TOM PLUMBING INC.",
            "license_number": "231034-5501",
            "original_issue_date": "01/01/1911",
            "qualifier_name": "source data blank",
            "classifications": "P200 - General Plumbing Qualifier, S410 - Boiler, Pipeline, Waste and Cond.",
            "license_status": "Active"
        },
        {
            "company_name": "A.S.A.P. PLUMBING & DRAINS, INC.",
            "license_number": "1409671-5501",
            "original_issue_date": "08/14/2001",
            "qualifier_name": "Kevin James Newman",
            "classifications": "P200 - General Plumbing Qualifier",
            "license_status": "Active"
        }
    ]
    
    # 2. Enrich using optimized BES resolver
    enriched_leads = resolve_street_addresses(leads)
    
    # 3. Output files paths
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_xlsx = os.path.join(output_dir, "scraped_utah_contractors.xlsx")
    output_pdf = os.path.join(output_dir, "scraped_utah_contractors.pdf")
    
    # 4. Generate report
    format_excel_report(enriched_leads, output_xlsx, output_pdf)
    
    # 5. Copy to Desktop for extremely easy user access
    desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
    desktop_xlsx = os.path.join(desktop_dir, "scraped_utah_contractors.xlsx")
    desktop_pdf = os.path.join(desktop_dir, "scraped_utah_contractors.pdf")
    
    print("\n[Copying to Desktop] Preparing delivery files on Desktop...")
    try:
        shutil.copy2(output_xlsx, desktop_xlsx)
        shutil.copy2(output_pdf, desktop_pdf)
        print(f"  -> Successfully copied Excel to: {desktop_xlsx}")
        print(f"  -> Successfully copied PDF to:   {desktop_pdf}")
    except Exception as copy_err:
        print(f"  -> Error copying files to Desktop: {copy_err}")
        
    print("\n" + "=" * 60)
    print("                ENRICHMENT PIPELINE COMPLETED SUCCESSFULLY               ")
    print("=" * 60)
    print(f"Total Enriched Leads: {len(enriched_leads)}")
    print(f"Excel Output: {output_xlsx}")
    print(f"PDF Output:   {output_pdf}")
    print("=" * 60)

if __name__ == "__main__":
    main()
