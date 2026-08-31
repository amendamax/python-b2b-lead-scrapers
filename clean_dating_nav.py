import os, re

base_dir = os.getcwd()
checker_dir = os.path.join(base_dir, "dating-photo-checker")

files_to_clean = [
    os.path.join(checker_dir, "index.html"),
    os.path.join(checker_dir, "ro", "index.html"),
    os.path.join(checker_dir, "it", "index.html"),
    os.path.join(checker_dir, "de", "index.html"),
    os.path.join(checker_dir, "es", "index.html"),
    os.path.join(checker_dir, "fr", "index.html"),
    os.path.join(checker_dir, "pt", "index.html"),
    os.path.join(checker_dir, "ru", "index.html")
]

for fpath in files_to_clean:
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remove plain text links from nav-links
        # 1. remove #about
        content = re.sub(r'<a\s+href="#about"[^>]*>.*?</a>\s*', '', content, flags=re.IGNORECASE)
        # 2. remove #redflags
        content = re.sub(r'<a\s+href="#redflags"[^>]*>.*?</a>\s*', '', content, flags=re.IGNORECASE)
        # 3. remove #faq
        content = re.sub(r'<a\s+href="#faq"[^>]*>.*?</a>\s*', '', content, flags=re.IGNORECASE)
        
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Cleaned nav links in: {os.path.relpath(fpath, checker_dir)}")

print("ALL_DATING_NAVBARS_CLEANED_SUCCESS")
