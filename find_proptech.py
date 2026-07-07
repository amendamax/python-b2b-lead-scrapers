import os

search_dirs = [
    r"C:\Users\bratu\Documents\antigravity\amazing-borg",
    r"C:\Users\bratu\Desktop"
]

print("Searching for files containing 'proptech'...")
for sdir in search_dirs:
    if not os.path.exists(sdir):
        continue
    for root, dirs, files in os.walk(sdir):
        # limit depth to prevent long scans
        depth = root.replace(sdir, "").count(os.sep)
        if depth > 3:
            continue
        for file in files:
            file_lower = file.lower()
            if "proptech" in file_lower:
                print(f"FOUND FILE BY NAME: {os.path.join(root, file)}")
            
            # check content for text files
            if file.endswith(('.txt', '.html', '.md', '.json', '.xml', '.csv', '.py')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        if 'proptech' in content:
                            print(f"FOUND CONTENT IN: {filepath}")
                except Exception as e:
                    pass
print("Search finished.")
