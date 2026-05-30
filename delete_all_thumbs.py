import os

drives_to_scan = [
    r"C:\Users\bratu",
    r"D:\\",
    r"E:\\",
    r"F:\\",
    r"G:\\"
]

# We use exact names for things like Thumbs.db, and extensions for .lrv
exact_names_to_delete = {
    "thumbs.db",
    "ehthumbs.db",
    "ehthumbs_vista.db",
    ".ds_store"
}

extensions_to_delete = {
    ".thm",
    ".lrv" # GoPro low resolution video proxy
}

deleted_count = 0
deleted_files = []

for drive in drives_to_scan:
    if not os.path.exists(drive):
        continue
    for root, dirs, files in os.walk(drive):
        for file in files:
            file_lower = file.lower()
            
            # Check if it matches exact name or extension
            should_delete = False
            if file_lower in exact_names_to_delete:
                should_delete = True
            elif any(file_lower.endswith(ext) for ext in extensions_to_delete):
                should_delete = True
                
            if should_delete:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    deleted_count += 1
                except Exception as e:
                    pass

print(f"S-au sters {deleted_count} fisiere (thumbnails/cache):")
for f in deleted_files[:20]:
    print(f)
if len(deleted_files) > 20:
    print(f"... si inca {len(deleted_files) - 20} fisiere.")
