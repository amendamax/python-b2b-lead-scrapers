import os
import glob
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Look in AppData for MetaQuotes Terminals
appdata = os.environ.get("APPDATA")
mq_path = os.path.join(appdata, "MetaQuotes", "Terminal")

print(f"Searching MetaQuotes Terminal path: {mq_path}")
if not os.path.exists(mq_path):
    print("MetaQuotes directory not found.")
    sys.exit(0)

# Find all terminal instances (folders with hex names)
instances = glob.glob(os.path.join(mq_path, "*"))
for inst in instances:
    if not os.path.isdir(inst):
        continue
    
    # Check if this terminal has logs
    logs_dir = os.path.join(inst, "logs")
    if not os.path.exists(logs_dir):
        # Try bases directory (sometimes MT5 logs are under bases/...)
        logs_dir = os.path.join(inst, "MQL5", "Logs")
        if not os.path.exists(logs_dir):
            continue
            
    # Find log files in logs directory
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    if not log_files:
        continue
        
    # Sort log files by modification time or name (which has the date like yyyymmdd.log)
    log_files.sort(reverse=True)
    latest_log = log_files[0]
    
    print(f"\n==========================================")
    print(f"Terminal Instance: {os.path.basename(inst)}")
    print(f"Latest Log File: {latest_log} ({os.path.getsize(latest_log)} bytes)")
    
    # Try to identify which broker this terminal belongs to by reading the log header or looking at origin.txt
    origin_txt = os.path.join(inst, "origin.txt")
    if os.path.exists(origin_txt):
        with open(origin_txt, 'r', encoding='utf-16', errors='replace') as f:
            print(f"Origin/Broker Path: {f.read().strip()}")
            
    try:
        with open(latest_log, 'r', encoding='utf-16', errors='replace') as f:
            lines = f.readlines()
        print(f"Total lines: {len(lines)}")
        print("Last 15 lines of log:")
        for line in lines[-15:]:
            print(line.strip())
            
        # Search for connection or trade errors
        print("--- Error search in log ---")
        err_keywords = ["failed", "rejected", "disabled", "error", "connect", "authorize", "login", "invalid"]
        err_count = 0
        for idx, line in enumerate(lines):
            line_lower = line.lower()
            if any(kw in line_lower for kw in err_keywords):
                print(f"Line {idx+1}: {line.strip()}")
                err_count += 1
                if err_count >= 15:
                    print("... Too many errors, truncating ...")
                    break
                    
    except Exception as e:
        print(f"Error reading log: {e}")
