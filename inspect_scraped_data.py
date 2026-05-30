import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"C:\Users\bratu\Documents\antigravity\amazing-borg\utah_scraper\scraped_utah_contractors.xlsx"

try:
    df = pd.read_excel(file_path)
    print("Scraped Leads DataFrame:")
    print(df.to_string())
except Exception as e:
    print(f"Error reading Excel: {e}")
