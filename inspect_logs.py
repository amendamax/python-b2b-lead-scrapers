import os
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
    
    # Find .log files
    log_files = [f for f in os.listdir(folder_path) if f.endswith(".log")]
    if not log_files:
        print("No log files found")
        continue
        
    for log_file in log_files:
        log_path = os.path.join(folder_path, log_file)
        print(f"Log File: {log_file} ({os.path.getsize(log_path)} bytes)")
        try:
            with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            
            print(f"Total lines: {len(lines)}")
            print("--- First 5 lines ---")
            for line in lines[:5]:
                print(line.strip())
            print("--- Last 10 lines ---")
            for line in lines[-10:]:
                print(line.strip())
                
            # Search for errors or warnings or connection issues
            print("--- Error/Warning/Fail analysis ---")
            error_keywords = ["error", "exception", "fail", "cannot", "connect", "timeout", "disabled", "invalid", "missing", "reject"]
            error_count = 0
            for idx, line in enumerate(lines):
                line_lower = line.lower()
                if any(kw in line_lower for kw in error_keywords):
                    print(f"Line {idx+1}: {line.strip()}")
                    error_count += 1
                    if error_count >= 15:
                        print("... Too many error occurrences, truncating list ...")
                        break
            if error_count == 0:
                print("No keywords found.")
        except Exception as e:
            print(f"Error reading log file {log_file}: {e}")
