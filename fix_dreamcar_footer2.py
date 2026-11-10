import os
import re

vies_card = ""

def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        pattern = re.compile(r'<div class="footer-col">\s*<h4[^>]*>Re.*?eaua Oficial.*?</h4>\s*(<p.*?</div>)', re.DOTALL)
        
        match = pattern.search(text)
        if not match: return
        
        full_match = match.group(0)
        
        h4_match = re.search(r'<h4[^>]*>.*?</h4>', full_match)
        if not h4_match: return
        h4_tag = h4_match.group(0)

        def get_link(domain, icon):
            style = 'color: #38bdf8; font-weight: 700;' if "DreamCarHunt" in domain else 'color: #cbd5e1; font-weight: 400;'
            return f'<p style="margin: 0 0 8px 0;"><a href="https://{domain.lower()}" target="_blank" rel="noopener" style="{style} text-decoration: none;">{icon} {domain}</a></p>'

        new_links = f"""{get_link("IsBrokerSafe.com", "🏛️")}
{get_link("VerifyDating.net", "🛡️")}
{get_link("JobScamRadar.com", "💼")}
{get_link("PillScamRadar.com", "💊")}
{get_link("AppScamRadar.com", "📱")}
{get_link("DreamCarHunt.com", "🏎️")}
{get_link("AirParkRefund.com", "✈️")}
{get_link("VasileDev.com", "👑")}"""
        
        replacement = f'<div class="footer-col">\n    {h4_tag}\n    {new_links}\n</div>'
        
        text = text.replace(full_match, replacement)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Updated {filepath}")
        
    except Exception as e:
        print(f"Error {filepath}: {e}")

process_file(r'C:\Users\bratu\Documents\antigravity\amazing-borg\dreamcarhunt\ro\index.html')
