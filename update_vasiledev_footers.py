import os
import re

base_dir = r"C:\Users\bratu\Documents\antigravity\amazing-borg"
target_p = '<p>&copy; 2026 VasileDev Group (P.IVA 04226190041) &bull; Direct Email: <a href="mailto:amendamax@vasiledev.com" style="color: #38bdf8; text-decoration: none; font-weight: 600;">amendamax@vasiledev.com</a>. High-Performance Software Engineering. All rights reserved.</p>'

for root, dirs, files in os.walk(base_dir):
    if '.git' in root or 'node_modules' in root or 'dating-photo-checker' in root:
        continue
    for f in files:
        if f.endswith('.html'):
            filepath = os.path.join(root, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            if '<footer>' in content:
                new_content = re.sub(r'<footer>\s*<p>.*?</p>\s*</footer>', f'<footer>\n        {target_p}\n    </footer>', content, flags=re.DOTALL)
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as file:
                        file.write(new_content)
                    print('Updated vasiledev footer in:', filepath)
