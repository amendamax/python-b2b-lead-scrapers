import os
import re

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # If it has both VasileDev Group Ecosystem AND Official Network/Ecosistema Ufficiale in adjacent columns, delete one.
        # Find Official Network/Ecosistema Ufficiale column
        pattern1 = re.compile(r'<div class="footer-col">\s*<h4>(?:VasileDev Group Ecosystem|Ecosistem VasileDev Group)</h4>.*?</div>', re.DOTALL)
        
        match = pattern1.search(text)
        if match and "Official Network" in text or "Ecosistema Ufficiale" in text or "Rete Ufficiale" in text:
            # Remove the VasileDev Group Ecosystem column because the Official Network one is the good one we injected
            text = text.replace(match.group(0), "")
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"Removed duplicate column in {filepath}")
            
    except Exception as e:
        print(e)

for root, _, files in os.walk(r'C:\Users\bratu\Documents\antigravity\amazing-borg\dreamcarhunt'):
    for f in files:
        if f.endswith('.html'):
            process_file(os.path.join(root, f))
