import re

with open("dating-photo-checker/broker-verifier/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Let's just find VerifyDating and insert AppScamRadar after it
app_scam_html = '<p style="margin: 0 0 8px 0;"><a href="https://appscamradar.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">🐛 AppScamRadar.com</a></p>'

if "AppScamRadar.com" not in html:
    html = html.replace('<p style="margin: 0 0 8px 0;"><a href="https://verifydating.net" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">🛡️ VerifyDating.net</a></p>', 
                        '<p style="margin: 0 0 8px 0;"><a href="https://verifydating.net" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">🛡️ VerifyDating.net</a></p>\n                  ' + app_scam_html)
    
    with open("dating-photo-checker/broker-verifier/index.html", "w", encoding="utf-8") as f:
        f.write(html)

# Also update for other languages just in case
for lang in ["de", "es", "fr", "it", "pt", "ro", "ru"]:
    path = f"dating-photo-checker/broker-verifier/{lang}/index.html"
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            html = f.read()
        if "AppScamRadar.com" not in html:
            html = html.replace('<p style="margin: 0 0 8px 0;"><a href="https://verifydating.net" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">🛡️ VerifyDating.net</a></p>', 
                                '<p style="margin: 0 0 8px 0;"><a href="https://verifydating.net" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">🛡️ VerifyDating.net</a></p>\n                  ' + app_scam_html)
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)

