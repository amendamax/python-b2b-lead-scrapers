import os

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
        
    search_str = "<p>The Global AI Airport Parking Consumer Protection & Dispute Recovery Platform.<br>Defending passenger rights across Europe and North America.</p>"
    if search_str in text:
        text = text.replace(search_str, search_str + vies_card)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Updated {filepath}")
    else:
        # Try without <br> just in case
        search_str2 = "The Global AI Airport Parking Consumer Protection"
        if search_str2 in text:
            # find the end of the <p> tag containing this
            idx = text.find(search_str2)
            end_p = text.find("</p>", idx)
            if end_p != -1:
                old_p = text[text.rfind("<p", 0, idx):end_p+4]
                text = text.replace(old_p, old_p + vies_card)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(text)
                print(f"Updated {filepath} (fallback)")

for root, _, files in os.walk(r'C:\Users\bratu\Desktop\ECOSISTEM_PLATFORME_LIVE\airparkrefund-platform'):
    for f in files:
        if f.endswith('.html'):
            process_file(os.path.join(root, f))
