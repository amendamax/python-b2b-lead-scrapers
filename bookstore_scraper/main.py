from scraper import ECommerceScraper
from excel_exporter import ExcelReportExporter
import os
import sys

def print_banner():
    """Prints a professional, clean ASCII banner for the CLI."""
    banner = """
==================================================================
        E-COMMERCE DATA SCRAPER & EXCEL INSIGHTS CENTER
==================================================================
   * Target Platform: Books to Scrape (E-Commerce Bookstore)
   * Tech Stack: Python, requests, BeautifulSoup, openpyxl, lxml
   * Features: Rotating Headers, Clean Data Engineering,
               Zebra Striping, Excel Formulas, Embedded Charts
==================================================================
    """
    print(banner)

def get_integer_input(prompt, default_val, min_val=1, max_val=50):
    """Safely prompts the user for integer input with a default fallback."""
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
    """Safely prompts the user for string input with a default fallback."""
    user_input = input(f"{prompt} [Default: {default_val}]: ").strip()
    if not user_input:
        return default_val
    return user_input

def main():
    print_banner()
    
    # 1. Gather User Inputs
    print("[1] Configuration Settings")
    max_pages = get_integer_input("Enter number of pages to scrape (1-50)", default_val=3, min_val=1, max_val=50)
    output_file = get_string_input("Enter output Excel filename", default_val="scraped_books_report.xlsx")
    
    # Ensure file has .xlsx extension
    if not output_file.lower().endswith('.xlsx'):
        output_file += '.xlsx'
        
    print("\n[2] Executing Scraper Engine")
    print("-" * 50)
    
    scraper = ECommerceScraper()
    exporter = ExcelReportExporter()
    
    # Progress callback function
    def log_progress(page, total_pages, message):
        percent = int((page / total_pages) * 100)
        # Visual progress bar
        bar_length = 20
        filled_length = int(round(bar_length * page / total_pages))
        bar = '#' * filled_length + '-' * (bar_length - filled_length)
        sys.stdout.write(f"\r[{bar}] {percent}% | Page {page}/{total_pages} | {message}")
        sys.stdout.flush()
        if page == total_pages and "completed" in message.lower():
            sys.stdout.write("\n")
            sys.stdout.flush()

    # Start scraping
    import time
    start_time = time.time()
    
    scraped_data = scraper.scrape_query(max_pages=max_pages, progress_callback=log_progress)
    
    elapsed_time = time.time() - start_time
    
    print("-" * 50)
    print(f"Scraping completed in {elapsed_time:.2f} seconds.")
    print(f"Successfully scraped {len(scraped_data)} products.")
    
    if not scraped_data:
        print("\n[!] No products were scraped. Export aborted.")
        return

    # 2. Exporting Data to Excel
    print("\n[3] Generating Premium Excel Report")
    print("-" * 50)
    
    # Generate full path
    workspace_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(workspace_dir, output_file)
    
    try:
        exporter.export_data(scraped_data, output_path)
        print(f"\n[+] SUCCESS: Executive report saved successfully!")
        print(f"File Location: {output_path}")
        
        # Display short summary stats calculated locally for instant validation
        prices = [item['Price'] for item in scraped_data]
        ratings = [item['Rating'] for item in scraped_data]
        avg_price = sum(prices) / len(prices) if prices else 0.0
        avg_rating = sum(ratings) / len(ratings) if ratings else 0.0
        
        print("\n" + "=" * 40)
        print("          EXECUTIVE DATA SUMMARY")
        print("=" * 40)
        print(f" Total Products Scraped : {len(scraped_data)}")
        print(f" Average Product Price  : {avg_price:.2f} GBP")
        print(f" Average Star Rating    : {avg_rating:.1f} / 5.0")
        print(f" Report Status          : READY")
        print("=" * 40)
        print("\nTip for Fiverr clients: Open this Excel file in MS Excel to view the dynamic chart and interactive filters!")
        
    except Exception as e:
        print(f"\n[!] ERROR exporting to Excel: {str(e)}")

if __name__ == "__main__":
    main()
