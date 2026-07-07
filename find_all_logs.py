import os
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

paths = [
    r"C:\Users\bratu\Desktop",
    r"C:\Users\bratu\Desktop\New folder"
]

print("Searching for log files...")
print("=========================")

for base in paths:
    if not os.path.exists(base):
        continue
    for root, dirs, files in os.walk(base):
        for file in files:
            if file.endswith(".log"):
                full_path = os.path.join(root, file)
                print(f"Log: {full_path}")
                print(f"  Size: {os.path.getsize(full_path)} bytes")
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                        lines = f.readlines()
                    if lines:
                        print(f"  Total lines: {len(lines)}")
                        print(f"  Last line: {lines[-1].strip()}")
                except Exception as e:
                    print(f"  Error reading: {e}")
                print("-" * 30)
