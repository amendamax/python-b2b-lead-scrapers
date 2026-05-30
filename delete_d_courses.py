import os
import shutil

directories_to_check = [
    r"D:\torrents",
    r"D:\torrents\Udemy _Cursuri_video"
]

keywords_to_delete = [
    "Passive Income Ideas",
    "Web Hacking 101",
    "Faceless.AI",
    "Full.Paid.Ads",
    "Web.Development.Bootcamp",
    "The Complete Python Course 2024",
    "Total Python",
    "Linkedin.Learning.Python",
    "Python.Development.and.Python.Programming",
    "Ethical Hacking & Penetration Testing",
    "Ethical.Hacking.Masterclass",
    "8.Things.You.Must.Know.In.Python",
    "Linkedin.Learning.Python-Programming"
]

deleted_count = 0

for base_dir in directories_to_check:
    if not os.path.exists(base_dir):
        continue
        
    for folder_name in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder_name)
        
        # We only delete directories
        if os.path.isdir(folder_path):
            # If any keyword is found in the folder name (case insensitive)
            if any(k.lower() in folder_name.lower() for k in keywords_to_delete):
                print(f"Deleting: {folder_path}")
                try:
                    shutil.rmtree(folder_path)
                    deleted_count += 1
                except Exception as e:
                    print(f"Failed to delete {folder_path}: {e}")

print(f"\nFinalizat! Au fost sterse {deleted_count} cursuri/foldere.")
