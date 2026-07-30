import os

search_paths = [
    "C:/Users/bratu/Desktop",
    "C:/Users/bratu/Documents/antigravity/amazing-borg",
    "C:/Users/bratu/Documents"
]

found = []
for path in search_paths:
    if not os.path.exists(path):
        continue
    for root, dirs, files in os.walk(path):
        # Only search shallow on Documents to avoid deep recursion
        if path == "C:/Users/bratu/Documents" and root != "C:/Users/bratu/Documents":
            continue
            
        for file in files:
            lower_file = file.lower()
            if "hub" in lower_file or "vasile" in lower_file or "business" in lower_file or "master" in lower_file:
                found.append(os.path.join(root, file))

print("Found files:")
for f in found:
    print(f)
