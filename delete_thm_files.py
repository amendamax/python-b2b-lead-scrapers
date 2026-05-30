import os

drives_to_scan = [
    r"C:\Users\bratu",
    r"D:\\",
    r"E:\\",
    r"F:\\",
    r"G:\\"
]

deleted_count = 0
deleted_files = []

for drive in drives_to_scan:
    if not os.path.exists(drive):
        continue
    for root, dirs, files in os.walk(drive):
        for file in files:
            if file.lower().endswith('.thm'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    deleted_count += 1
                except Exception as e:
                    pass

print(f"S-au sters {deleted_count} fisiere *.THM:")
for f in deleted_files[:20]:
    print(f)
if len(deleted_files) > 20:
    print(f"... si inca {len(deleted_files) - 20} fisiere.")
