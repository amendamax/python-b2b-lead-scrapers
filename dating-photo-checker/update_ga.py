import glob
import os

files = glob.glob('**/index.html', recursive=True)
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if 'G-GLKH6MW0RC' in content and 'G-3FF4JJT4JN' not in content:
        new_content = content.replace("gtag('config', 'G-GLKH6MW0RC');", "gtag('config', 'G-3FF4JJT4JN');\n      gtag('config', 'G-GLKH6MW0RC');")
        with open(f, 'w', encoding='utf-8') as file:
            file.write(new_content)
        print(f'Updated {f}')
