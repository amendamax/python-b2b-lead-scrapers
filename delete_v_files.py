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
            if file.lower().endswith('.v'):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    deleted_files.append(file_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

print(f"S-au sters {deleted_count} fisiere *.V:")
for f in deleted_files[:50]:  # print up to 50
    print(f)
if len(deleted_files) > 50:
    print(f"... si inca {len(deleted_files) - 50} fisiere.")
