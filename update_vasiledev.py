import re

job_link = '<p style="margin: 0 0 8px 0;"><a href="https://jobscamradar.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">🛡️ JobScamRadar.com</a></p>'
pill_link = '<p style="margin: 0 0 8px 0;"><a href="https://pillscamradar.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">💊 PillScamRadar.com</a></p>'

files_to_update = [
    "index.html",
    "ro/index.html",
    "it/index.html",
    "de/index.html",
    "fr/index.html",
    "es/index.html"
]

for file_path in files_to_update:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()

        if "JobScamRadar" not in html:
            html = re.sub(r'(<p[^>]*><a[^>]*>.*?VerifyDating\.net.*?</a></p>)', r'\1\n                  ' + job_link + r'\n                  ' + pill_link, html)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)
    except FileNotFoundError:
        pass

