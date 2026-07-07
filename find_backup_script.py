import os

search_dir = r"C:\Users\bratu\Documents\antigravity\amazing-borg"
print("Searching for backup, sync, gdrive, or drive keywords in python files...")

for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith(".py") or file.endswith(".bat") or file.endswith(".ps1"):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    if "gdrive" in content or "google drive" in content or "backup" in content or "rclone" in content:
                        print(f"MATCH FOUND in {filepath}")
                        # print lines containing the keyword
                        lines = content.splitlines()
                        for i, line in enumerate(lines, 1):
                            if any(k in line for k in ["gdrive", "google drive", "backup", "rclone"]):
                                print(f"  Line {i}: {line.strip()[:150]}")
            except Exception as e:
                pass
print("Search finished.")
