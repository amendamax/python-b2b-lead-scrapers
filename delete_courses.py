import os
import shutil
import glob

base_dir = r"G:\Downloads"
if not os.path.exists(base_dir):
    print(f"{base_dir} does not exist.")
    exit()

keywords = ["affiliate", "amigoscode", "bytegrad", "aws", "front_end", "react", "make 5 stunning", "javascript", "bootstrap", "next.level.css", "nextjs", "django", "css", "html", "full-stack", "java", "python"]

folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]

deleted_count = 0
for folder in folders:
    folder_lower = folder.lower()
    if any(k in folder_lower for k in keywords):
        folder_path = os.path.join(base_dir, folder)
        print(f"Deleting: {folder_path}")
        try:
            shutil.rmtree(folder_path)
            deleted_count += 1
        except Exception as e:
            print(f"Failed to delete {folder_path}: {e}")

print(f"Deleted {deleted_count} courses.")
