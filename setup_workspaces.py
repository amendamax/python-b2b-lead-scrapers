import os
import shutil

base_dir = r"C:\Users\bratu\Documents\antigravity\amazing-borg"
source_dir = os.path.join(base_dir, "dating-photo-checker")

new_projects = [
    "job-scam-radar",
    "pill-scam-radar",
    "app-scam-radar"
]

files_to_remove = [
    "scammers.db",
    "scammers.db-journal",
    ".git",
    "logs",
    "sitemaps" # any leftover generated sitemaps
]

for project in new_projects:
    target_dir = os.path.join(base_dir, project)
    if os.path.exists(target_dir):
        print(f"Skipping {project}, already exists.")
        continue
    
    print(f"Cloning to {project}...")
    shutil.copytree(source_dir, target_dir)
    
    # Cleanup target
    for root, dirs, files in os.walk(target_dir):
        # Remove sitemaps
        for f in files:
            if f.startswith("sitemap") and f.endswith(".xml"):
                os.remove(os.path.join(root, f))
        
    for item in files_to_remove:
        item_path = os.path.join(target_dir, item)
        if os.path.exists(item_path):
            if os.path.isdir(item_path):
                import stat
                # Handle readonly files in .git
                def remove_readonly(func, path, _):
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                shutil.rmtree(item_path, onerror=remove_readonly)
            else:
                os.remove(item_path)
    
    print(f"Initialized clean slate for {project}.")

print("All clones created successfully!")
