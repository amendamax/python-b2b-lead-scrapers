import os
import json
import sys

# Reconfigure stdout to handle encoding errors on Windows console
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

folders = ["AUR_FTMO", "EURO", "NASDAQ", "XAUUSD"]
base_dir = r"C:\Users\bratu\Desktop\New folder"

for folder in folders:
    folder_path = os.path.join(base_dir, folder)
    print(f"\n==========================================")
    print(f"Folder: {folder}")
    if not os.path.exists(folder_path):
        print("Directory does not exist")
        continue
    
    # Check for json config files
    config_files = [f for f in os.listdir(folder_path) if f.endswith(".json") and f != "model.json" and f != "economic_calendar.json"]
    if not config_files:
        print("No configuration files found")
        continue
        
    for cf in config_files:
        cf_path = os.path.join(folder_path, cf)
        print(f"Config File: {cf}")
        try:
            with open(cf_path, 'r', encoding='utf-8', errors='replace') as f:
                data = json.load(f)
            print(json.dumps(data, indent=2))
        except Exception as e:
            print(f"Error reading config: {e}")
