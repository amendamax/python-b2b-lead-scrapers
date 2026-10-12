import os
import re

def update_ecosystem(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Regex to capture the Ecosystem column block
        # We look for a column that contains Official Network, Ecosistema, Ecosistemul, Rete Ufficiale, etc.
        pattern = re.compile(r'(<(div|div class="footer-col")([^>]*)>)\s*<h4[^>]*>(Official Network|Ecosistema Ufficiale|Rete Ufficiale|Ecosistemul Oficial|VasileDev Group Ecosystem)</h4>\s*(<p.*?</div>)', re.DOTALL)
        
        match = pattern.search(text)
        if not match:
            # Let's try matching with <div class="footer-col"> and IsBrokerSafe.com inside
            pattern2 = re.compile(r'<div class="footer-col">\s*<h4[^>]*>.*?</h4>\s*(<p.*?IsBrokerSafe\.com.*?</div>)', re.DOTALL)
            match = pattern2.search(text)
            if not match:
                return

        full_match = match.group(0)
        
        # Extract the h4 tag to keep the language
        h4_match = re.search(r'<h4[^>]*>.*?</h4>', full_match)
        if not h4_match: return
        h4_tag = h4_match.group(0)
        
        # Determine the current site to highlight it
        current_site = "unknown"
        if "airparkrefund" in filepath.lower(): current_site = "airparkrefund.com"
        elif "dreamcarhunt" in filepath.lower(): current_site = "dreamcarhunt.com"
        elif "isbrokersafe" in filepath.lower() or "broker-verifier" in filepath.lower(): current_site = "isbrokersafe.com"
        elif "verifydating" in filepath.lower() or "dating-photo-checker" in filepath.lower(): current_site = "verifydating.net"
        elif "jobscamradar" in filepath.lower() or "job-scam-radar" in filepath.lower(): current_site = "jobscamradar.com"
        elif "pillscamradar" in filepath.lower() or "pill-scam-radar" in filepath.lower(): current_site = "pillscamradar.com"
        elif "appscamradar" in filepath.lower() or "app-scam-radar" in filepath.lower(): current_site = "appscamradar.com"
        elif "vasiledev" in filepath.lower(): current_site = "vasiledev.com"

        def get_link(domain, icon):
            style = 'color: #38bdf8; font-weight: 700;' if current_site in domain else 'color: #cbd5e1; font-weight: 400;'
            return f'<p style="margin: 0 0 8px 0;"><a href="https://{domain}" target="_blank" rel="noopener" style="{style} text-decoration: none;">{icon} {domain}</a></p>'

        new_links = f"""{get_link("isbrokersafe.com", "🏛️")}
{get_link("verifydating.net", "🛡️")}
{get_link("jobscamradar.com", "💼")}
{get_link("pillscamradar.com", "💊")}
{get_link("appscamradar.com", "📱")}
{get_link("dreamcarhunt.com", "🏎️")}
{get_link("airparkrefund.com", "✈️")}
{get_link("vasiledev.com", "👑")}"""

        # Are we in a styled div or a clean div?
        div_start = match.group(1) if match.re == pattern else '<div class="footer-col">'
        
        replacement = f"{div_start}\n    {h4_tag}\n    {new_links}\n</div>"
        
        text = text.replace(full_match, replacement)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Updated ecosystem in {filepath}")
        
    except Exception as e:
        print(f"Error {filepath}: {e}")

dirs_to_scan = [
    r'C:\Users\bratu\Desktop\ECOSISTEM_PLATFORME_LIVE\airparkrefund-platform',
    r'C:\Users\bratu\Documents\antigravity\amazing-borg\dreamcarhunt',
    r'C:\Users\bratu\Documents\antigravity\amazing-borg\broker-verifier',
    r'C:\Users\bratu\Documents\antigravity\amazing-borg\dating-photo-checker',
    r'C:\Users\bratu\Documents\antigravity\amazing-borg\job-scam-radar',
    r'C:\Users\bratu\Documents\antigravity\amazing-borg\pill-scam-radar',
    r'C:\Users\bratu\Documents\antigravity\amazing-borg\app-scam-radar',
    r'C:\Users\bratu\Documents\antigravity\amazing-borg' # VasileDev etc
]

for d in dirs_to_scan:
    for root, _, files in os.walk(d):
        if 'node_modules' in root or '.git' in root or '.wrangler' in root: continue
        for f in files:
            if f.endswith('.html') or f.endswith('.py') or f.endswith('.js'):
                process_path = os.path.join(root, f)
                # Don't modify the python script itself
                if 'update_ecosystem.py' in process_path: continue
                update_ecosystem(process_path)

