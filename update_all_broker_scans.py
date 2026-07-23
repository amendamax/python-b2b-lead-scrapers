import glob
import re
import os

# 1. Update server.py with CapitalInvestFX and CryptoWealth24
server_path = 'dating-photo-checker/server.py'
with open(server_path, 'r', encoding='utf-8') as f:
    server_content = f.read()

scam_entries = '''    "capitalinvestfx.com": {
        "name": "CapitalInvestFX",
        "type": "Confirmed Scam",
        "score": 4,
        "source": "CySEC / BaFin Investor Alert",
        "verdictTitle": "CRITICAL FRAUD ALERT / BLACKLISTED",
        "verdictText": "CapitalInvestFX is an illegal, unregulated scam entity blacklisted by European regulators. They manipulate trading software and block client withdrawals.",
        "redFlags": ["Blacklisted by European financial watchdogs.", "Manipulated trading interface with fake balances.", "Demands secondary fee payments to process withdrawals."],
        "greenFlags": ["None. Avoid completely."],
        "mockIp": "185.220.101.5",
        "mockHoster": "Bulletproof Offshore Hosting",
        "mockDomainAge": "2026-03-01 (4 months ago)",
        "mockRegStatus": "CRITICAL: Officially Blacklisted by CySEC and BaFin"
    },
    "capitalinvestfx": {
        "name": "CapitalInvestFX",
        "type": "Confirmed Scam",
        "score": 4,
        "source": "CySEC / BaFin Investor Alert",
        "verdictTitle": "CRITICAL FRAUD ALERT / BLACKLISTED",
        "verdictText": "CapitalInvestFX is an illegal, unregulated scam entity blacklisted by European regulators. They manipulate trading software and block client withdrawals.",
        "redFlags": ["Blacklisted by European financial watchdogs.", "Manipulated trading interface with fake balances.", "Demands secondary fee payments to process withdrawals."],
        "greenFlags": ["None. Avoid completely."],
        "mockIp": "185.220.101.5",
        "mockHoster": "Bulletproof Offshore Hosting",
        "mockDomainAge": "2026-03-01 (4 months ago)",
        "mockRegStatus": "CRITICAL: Officially Blacklisted by CySEC and BaFin"
    },
    "cryptowealth24.com": {
        "name": "CryptoWealth24",
        "type": "Confirmed Scam",
        "score": 6,
        "source": "CNMV / ASIC Warning List",
        "verdictTitle": "HIGH RISK PONZI SCHEME",
        "verdictText": "CryptoWealth24 operates an illegal multi-level Ponzi scheme using fake social media account managers to solicit deposits.",
        "redFlags": ["Unregulated crypto Ponzi scheme.", "Recruits victims via Instagram/Telegram unsolicited messaging.", "Promises guaranteed daily crypto yields of 15%+."],
        "greenFlags": ["None. Illegal scam."],
        "mockIp": "194.26.29.110",
        "mockHoster": "Anonymous Cloud Server",
        "mockDomainAge": "2026-04-12 (3 months ago)",
        "mockRegStatus": "ALERT: Blacklisted by CNMV (Spain) and ASIC (AU)"
    },
    "cryptowealth24": {
        "name": "CryptoWealth24",
        "type": "Confirmed Scam",
        "score": 6,
        "source": "CNMV / ASIC Warning List",
        "verdictTitle": "HIGH RISK PONZI SCHEME",
        "verdictText": "CryptoWealth24 operates an illegal multi-level Ponzi scheme using fake social media account managers to solicit deposits.",
        "redFlags": ["Unregulated crypto Ponzi scheme.", "Recruits victims via Instagram/Telegram unsolicited messaging.", "Promises guaranteed daily crypto yields of 15%+."],
        "greenFlags": ["None. Illegal scam."],
        "mockIp": "194.26.29.110",
        "mockHoster": "Anonymous Cloud Server",
        "mockDomainAge": "2026-04-12 (3 months ago)",
        "mockRegStatus": "ALERT: Blacklisted by CNMV (Spain) and ASIC (AU)"
    },'''

if '"capitalinvestfx.com"' not in server_content:
    server_content = server_content.replace('static_broker_db = {', 'static_broker_db = {\n' + scam_entries)
    with open(server_path, 'w', encoding='utf-8') as f:
        f.write(server_content)
    print("Updated server.py with scam entries!")

# 2. Update app.js brokerDatabase
new_js_db = '''const brokerDatabase = [
    { name: "Exness", domain: "exness.com" },
    { name: "eToro", domain: "etoro.com" },
    { name: "XM Group", domain: "xm.com" },
    { name: "Plus500", domain: "plus500.com" },
    { name: "AvaTrade", domain: "avatrade.com" },
    { name: "PocketOption", domain: "pocketoption.com" },
    { name: "ApexCryptoFX", domain: "apexcryptofx.com" },
    { name: "FxTradersGold", domain: "fxtradersgold.com" },
    { name: "CapitalInvestFX", domain: "capitalinvestfx.com" },
    { name: "CryptoWealth24", domain: "cryptowealth24.com" },
    { name: "Interactive Brokers", domain: "interactivebrokers.com" },
    { name: "Pepperstone", domain: "pepperstone.com" },
    { name: "IC Markets", domain: "icmarkets.com" }
];'''

js_files = ['dating-photo-checker/broker-verifier/app.js', 'broker-verifier/app.js']
for js_f in js_files:
    if os.path.exists(js_f):
        with open(js_f, 'r', encoding='utf-8') as f:
            js_content = f.read()
        js_content = re.sub(r'const brokerDatabase = \[[\s\S]*?\];', new_js_db, js_content)
        with open(js_f, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"Updated brokerDatabase in {js_f}")

# 3. Update HTML ticker chips in all index.html files
new_chips_html = '''<div class="ticker-chips">
                    <button class="ticker-chip safe" onclick="selectBroker('XM Group')">XM Group <span class="score">92% Safe</span></button>
                    <button class="ticker-chip safe" onclick="selectBroker('eToro')">eToro <span class="score">95% Safe</span></button>
                    <button class="ticker-chip safe" onclick="selectBroker('Exness')">Exness <span class="score">96% Safe</span></button>
                    <button class="ticker-chip safe" onclick="selectBroker('Plus500')">Plus500 <span class="score">91% Safe</span></button>
                    <button class="ticker-chip safe" onclick="selectBroker('AvaTrade')">AvaTrade <span class="score">90% Safe</span></button>
                    <button class="ticker-chip warning" onclick="selectBroker('PocketOption')">PocketOption <span class="score">42% Risk ⚠️</span></button>
                    <button class="ticker-chip danger" onclick="selectBroker('ApexCryptoFX')" style="border-color: rgba(239, 68, 68, 0.4); color: #ef4444;">ApexCryptoFX <span class="score" style="background: rgba(239, 68, 68, 0.2); color: #ef4444;">5% Scam 🚨</span></button>
                    <button class="ticker-chip danger" onclick="selectBroker('FxTradersGold')" style="border-color: rgba(239, 68, 68, 0.4); color: #ef4444;">FxTradersGold <span class="score" style="background: rgba(239, 68, 68, 0.2); color: #ef4444;">8% Scam 🚨</span></button>
                    <button class="ticker-chip danger" onclick="selectBroker('CapitalInvestFX')" style="border-color: rgba(239, 68, 68, 0.4); color: #ef4444;">CapitalInvestFX <span class="score" style="background: rgba(239, 68, 68, 0.2); color: #ef4444;">4% Scam 🚨</span></button>
                    <button class="ticker-chip danger" onclick="selectBroker('CryptoWealth24')" style="border-color: rgba(239, 68, 68, 0.4); color: #ef4444;">CryptoWealth24 <span class="score" style="background: rgba(239, 68, 68, 0.2); color: #ef4444;">6% Scam 🚨</span></button>
                </div>'''

html_files = glob.glob('dating-photo-checker/broker-verifier/**/index.html', recursive=True) + glob.glob('broker-verifier/**/index.html', recursive=True)
for html_f in html_files:
    with open(html_f, 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_content = re.sub(r'<div class="ticker-chips">[\s\S]*?</div>', new_chips_html, html_content)
    with open(html_f, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Updated ticker chips in {html_f}")
