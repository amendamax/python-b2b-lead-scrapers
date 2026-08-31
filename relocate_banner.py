import os, re

base_dir = os.getcwd()
checker_dir = os.path.join(base_dir, "dating-photo-checker")
bv_dir = os.path.join(checker_dir, "broker-verifier")

for root, dirs, files in os.walk(bv_dir):
    for f in files:
        if f.endswith(".html"):
            fpath = os.path.join(root, f)
            with open(fpath, "r", encoding="utf-8") as file:
                content = file.read()
            
            # Find the awards-showcase-bar section
            match = re.search(r'(<!-- VERIFIABLE STATUTORY DATA.*?-->\s*<section class="awards-showcase-bar".*?</section>)', content, flags=re.DOTALL)
            if not match:
                match = re.search(r'(<section class="awards-showcase-bar".*?</section>)', content, flags=re.DOTALL)
            
            if match:
                banner_block = match.group(1)
                # Remove it from current position
                content_without_banner = content.replace(banner_block, "")
                # Insert it right before <footer class="app-footer"
                if '<footer class="app-footer"' in content_without_banner:
                    new_content = content_without_banner.replace(
                        '<footer class="app-footer"',
                        banner_block + '\n\n        <footer class="app-footer"'
                    )
                    with open(fpath, "w", encoding="utf-8") as file:
                        file.write(new_content)
                    print(f"Relocated banner above footer in: {os.path.relpath(fpath, checker_dir)}")

print("ALL_PAGES_RELOCATED_SUCCESS")
