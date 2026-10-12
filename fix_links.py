import re

with open('index.html', encoding='utf-8') as f:
    html = f.read()

correct_links = """                <p style="margin: 0 0 8px 0;"><a href="https://isbrokersafe.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">🏛️ IsBrokerSafe.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://verifydating.net" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">🛡️ VerifyDating.net</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://jobscamradar.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">🛡️ JobScamRadar.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://pillscamradar.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">💊 PillScamRadar.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://appscamradar.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">🐛 AppScamRadar.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://dreamcarhunt.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">🏎️ DreamCarHunt.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://airparkrefund.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">✈️ AirParkRefund.com</a></p>
                <p style="margin: 0;"><a href="https://vasiledev.com" style="color: #38bdf8; font-weight: 700; text-decoration: none;">👑 VasileDev.com</a></p>"""

html = re.sub(
    r'<h4[^>]*>Official Network</h4>.*?</div>\s*</div>\s*<div[^>]*max-width: 1140px',
    f'<h4 style="font-family: \'Outfit\', sans-serif; font-size: 1rem; font-weight: 700; color: #38bdf8; margin: 0 0 14px 0;">Official Network</h4>\n{correct_links}\n            </div>\n        </div>\n\n        <div style="max-width: 1140px',
    html,
    flags=re.DOTALL
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

