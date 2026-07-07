import os
import glob

search_dirs = [
    r"C:\Users\bratu\Desktop",
    r"C:\Users\bratu\Downloads",
    r"C:\Users\bratu\Documents"
]

print("Searching for files containing 'viktorija' or 'viktoria'...")
for sdir in search_dirs:
    if not os.path.exists(sdir):
        continue
    print(f"Searching in {sdir}...")
    for root, dirs, files in os.walk(sdir):
        # limit depth to prevent long scans
        depth = root.replace(sdir, "").count(os.sep)
        if depth > 3:
            continue
        for file in files:
            file_lower = file.lower()
            if any(term in file_lower for term in ["viktorija", "viktoria"]):
                print(f"FOUND FILE BY NAME: {os.path.join(root, file)}")
            
            # check content for text files
            if file.endswith(('.txt', '.html', '.md', '.json', '.xml', '.csv', '.py')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()
                        if 'viktorija' in content or 'viktoria' in content:
                            print(f"FOUND CONTENT IN: {filepath}")
                except Exception as e:
                    pass
print("Search finished.")
