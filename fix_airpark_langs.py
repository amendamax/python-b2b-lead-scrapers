import os
import re

vies_card = '''
                <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 15px;">
                    <span style="background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px;">✔️ VIES Verified EU</span>
                    <span style="background: rgba(56, 189, 248, 0.12); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px;">🛡️ 100% Free Public Utility</span>
                </div>'''

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        text = f.read()
    
    if "VIES Verified EU" in text:
        return
        
    pattern = re.compile(r'(<div class="logo"[^>]*>.*?<span class="logo-text">.*?<strong>.*?</strong></span>.*?</div>\s*<p>.*?</p>)', re.DOTALL)
    
    # We only want to replace it in the footer-col, so let's find the footer
    footer_idx = text.find('<div class="footer-col">')
    if footer_idx != -1:
        match = pattern.search(text, footer_idx)
        if match:
            old_p = match.group(1)
            text = text[:match.start()] + old_p + vies_card + text[match.end():]
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Updated {filepath}")

for root, _, files in os.walk(r'C:\Users\bratu\Desktop\ECOSISTEM_PLATFORME_LIVE\airparkrefund-platform'):
    for f in files:
        if f.endswith('.html'):
            process_file(os.path.join(root, f))
