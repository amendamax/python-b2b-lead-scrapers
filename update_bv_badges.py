import os

base_dir = os.getcwd()
checker_dir = os.path.join(base_dir, "dating-photo-checker")
bv_dir = os.path.join(checker_dir, "broker-verifier")

chrome_btn_broker = '<a href="/extension" target="_blank" rel="noopener" class="badge-tag" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(56, 189, 248, 0.25) 100%); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.5); font-weight: 800;"><i class="fa-brands fa-chrome"></i> 🛡️ Add to Chrome — Free</a>'

# Check all html files in broker-verifier and its subdirectories
for root, dirs, files in os.walk(bv_dir):
    for f in files:
        if f.endswith(".html"):
            fpath = os.path.join(root, f)
            with open(fpath, "r", encoding="utf-8") as file:
                content = file.read()
            if 'href="/extension"' not in content and '<div class="header-badges">' in content:
                content = content.replace('<div class="header-badges">', '<div class="header-badges">\n                    ' + chrome_btn_broker)
                with open(fpath, "w", encoding="utf-8") as file:
                    file.write(content)
                print(f"Injected Chrome button into: {os.path.relpath(fpath, checker_dir)}")

print("ALL_BROKER_VERIFIER_PAGES_UPDATED")
