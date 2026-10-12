import os
import glob
import re

files = glob.glob('broker-verifier/*/index.html') + glob.glob('*/index.html') + glob.glob('broker-verifier/index.html') + ['index.html']
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        content = re.sub(r'<link rel="alternate" hreflang="([^"]+)" href="https://isbrokersafe\.com/" />', 
                         r'<link rel="alternate" hreflang="en" href="https://isbrokersafe.com/" />', content)
                         
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        pass
