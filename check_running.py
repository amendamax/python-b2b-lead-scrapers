import psutil
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("Running Python Processes:")
print("=========================")
count = 0
for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cwd']):
    try:
        # Check if python is in process name
        if 'python' in proc.info['name'].lower():
            count += 1
            print(f"PID: {proc.info['pid']}")
            print(f"Name: {proc.info['name']}")
            print(f"CmdLine: {proc.info['cmdline']}")
            print(f"CWD: {proc.info['cwd']}")
            print("-" * 40)
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
        pass

if count == 0:
    print("No running python processes found.")
