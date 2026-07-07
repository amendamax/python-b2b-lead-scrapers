import os
import glob
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

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
    
    logs_dir = os.path.join(inst, "logs")
    if not os.path.exists(logs_dir):
        continue
            
    # Find log files in logs directory that match date formats, ex: 20260602.log or similar
    log_files = glob.glob(os.path.join(logs_dir, "2026*.log"))
    if not log_files:
        # fallback to any log
        log_files = [f for f in glob.glob(os.path.join(logs_dir, "*.log")) if "metaeditor" not in f.lower()]
        
    if not log_files:
        continue
        
    log_files.sort(reverse=True)
    latest_log = log_files[0]
    
    print(f"\n==========================================")
    print(f"Terminal Instance: {os.path.basename(inst)}")
    print(f"Latest Terminal Log File: {latest_log} ({os.path.getsize(latest_log)} bytes)")
    
    origin_txt = os.path.join(inst, "origin.txt")
    if os.path.exists(origin_txt):
        with open(origin_txt, 'r', encoding='utf-16', errors='replace') as f:
            print(f"Origin/Broker Path: {f.read().strip()}")
            
    try:
        # MT5 logs are typically UTF-16 encoded
        with open(latest_log, 'r', encoding='utf-16', errors='replace') as f:
            lines = f.readlines()
        print(f"Total lines: {len(lines)}")
        print("Last 20 lines of log:")
        for line in lines[-20:]:
            print(line.strip())
            
        print("--- Connection/Trade Events search in log ---")
        keywords = ["failed", "rejected", "disabled", "error", "connect", "authorize", "login", "invalid", "deal", "order"]
        err_count = 0
        for idx, line in enumerate(lines):
            line_lower = line.lower()
            if any(kw in line_lower for kw in keywords):
                print(f"Line {idx+1}: {line.strip()}")
                err_count += 1
                if err_count >= 15:
                    print("... Too many events, truncating ...")
                    break
                    
    except Exception as e:
        print(f"Error reading log: {e}")
