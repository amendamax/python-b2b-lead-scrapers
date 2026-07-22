import glob
import os

files = glob.glob('broker-verifier/**/*.html', recursive=True)
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if 'G-BXS970H1KK' in content and 'G-BRLWMFCM12' not in content:
        new_content = content.replace("gtag('config', 'G-BXS970H1KK');", "gtag('config', 'G-BRLWMFCM12');\n      gtag('config', 'G-BXS970H1KK');")
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f'Updated {f}')
