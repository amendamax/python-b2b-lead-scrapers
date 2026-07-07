import os
import glob
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

appdata = os.environ.get("APPDATA")
mq_path = os.path.join(appdata, "MetaQuotes", "Terminal")

print("Searching for Pepperstone log files...")
print("=========================")

instances = glob.glob(os.path.join(mq_path, "*"))
for inst in instances:
    if not os.path.isdir(inst):
        continue
    
    # Check origin.txt to see if it is Pepperstone
    origin_txt = os.path.join(inst, "origin.txt")
    is_pepperstone = False
    if os.path.exists(origin_txt):
        try:
            with open(origin_txt, 'r', encoding='utf-16', errors='replace') as f:
                origin_content = f.read().strip()
                if "pepperstone" in origin_content.lower():
                    is_pepperstone = True
                    print(f"Found Pepperstone Terminal: {os.path.basename(inst)}")
                    print(f"Path: {origin_content}")
        except Exception as e:
            print(f"Error reading origin.txt in {os.path.basename(inst)}: {e}")
            
    if not is_pepperstone:
        continue
        
    logs_dir = os.path.join(inst, "logs")
    if not os.path.exists(logs_dir):
        print("  logs directory not found.")
        continue
        
    log_files = glob.glob(os.path.join(logs_dir, "*.log"))
    if not log_files:
        print("  No .log files found.")
        continue
        
    log_files.sort(reverse=True)
    
    print("  Recent log files:")
    for lf in log_files[:5]:
        print(f"    {os.path.basename(lf)} ({os.path.getsize(lf)} bytes)")
        
    # Print the content of the latest log file
    latest_log = log_files[0]
    print(f"\n  Latest Log File details: {os.path.basename(latest_log)}")
    try:
        with open(latest_log, 'r', encoding='utf-16', errors='replace') as f:
            lines = f.readlines()
        print(f"  Total lines: {len(lines)}")
        print("  Last 30 lines of log:")
        for line in lines[-30:]:
            print("   ", line.strip())
    except Exception as e:
        print(f"  Error reading log file: {e}")
