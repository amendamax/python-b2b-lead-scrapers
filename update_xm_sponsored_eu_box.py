import glob
import re
import os

# Update affiliate-notice-box styling across all index.html files
html_files = glob.glob('dating-photo-checker/broker-verifier/**/index.html', recursive=True) + glob.glob('broker-verifier/**/index.html', recursive=True)

old_red_box_pattern = r'<div class="affiliate-notice-box"[\s\S]*?</div>\s*</div>'

def replace_box(match):
    full_str = match.group(0)
    # Replace border, background, and link color from red to emerald green
    full_str = re.sub(r'border:\s*1px dashed rgba\(200,\s*30,\s*40,\s*0\.35\);', 'border: 1px dashed rgba(16, 185, 129, 0.4);', full_str)
    full_str = re.sub(r'background:\s*rgba\(255,\s*255,\s*255,\s*0\.03\);', 'background: rgba(16, 185, 129, 0.06);', full_str)
    full_str = re.sub(r'color:\s*#e01e28;', 'color: #34d399;', full_str)
    return full_str

count = 0
for html_f in html_files:
    if os.path.exists(html_f):
        with open(html_f, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'affiliate-notice-box' in content:
            new_content = re.sub(old_red_box_pattern, replace_box, content)
            if new_content != content:
                with open(html_f, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                count += 1
                print(f"Updated XM EU box in {html_f}")

print(f"Total files updated: {count}")
