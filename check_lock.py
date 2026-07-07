import os
import json
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

paths = [
    r"C:\Users\bratu\Desktop\ftmo_lock.json",
    r"C:\Users\bratu\Desktop\New folder\ftmo_lock.json"
]

for lock_path in paths:
    print(f"\nChecking lock file: {lock_path}")
    if os.path.exists(lock_path):
        print("Lock file EXISTS.")
        try:
            with open(lock_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print("Content:")
            print(json.dumps(data, indent=4))
        except Exception as e:
            print(f"Error reading lock file: {e}")
    else:
        print("Lock file does not exist.")
