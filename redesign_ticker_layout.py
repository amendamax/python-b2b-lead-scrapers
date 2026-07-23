import glob
import re
import os

# 1. Update style.css in both broker-verifier folders
css_files = [
    'dating-photo-checker/broker-verifier/style.css',
    'broker-verifier/style.css'
]

css_addition = '''
/* Clean 2-Row Categorized Ticker Layout */
.recent-audits-ticker {
    margin-top: 1.5rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.8rem;
    width: 100%;
}

.ticker-group {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
    flex-wrap: wrap;
    max-width: 950px;
}

.ticker-group-label {
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    white-space: nowrap;
    padding: 0.2rem 0.5rem;
    border-radius: 6px;
}

.ticker-group-label.safe {
    color: #34d399;
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.25);
}

.ticker-group-label.danger {
    color: #f87171;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.25);
}

.ticker-chips {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    justify-content: center;
}

.ticker-chip {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: #f1f5f9;
    padding: 0.35rem 0.75rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
}

.ticker-chip:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.ticker-chip.safe:hover {
    border-color: #10b981;
    background: rgba(16, 185, 129, 0.15);
}

.ticker-chip.warning:hover,
.ticker-chip.danger:hover {
    border-color: #ef4444;
    background: rgba(239, 68, 68, 0.15);
}

.ticker-chip .score {
    font-size: 0.7rem;
    padding: 0.15rem 0.45rem;
    border-radius: 10px;
    font-weight: 700;
}

.ticker-chip.safe .score {
    background: rgba(16, 185, 129, 0.2);
    color: #34d399;
}

.ticker-chip.warning .score,
.ticker-chip.danger .score {
    background: rgba(239, 68, 68, 0.25);
    color: #f87171;
}

.ticker-chip.danger {
    border-color: rgba(239, 68, 68, 0.3);
    color: #fca5a5;
}
'''

for css_f in css_files:
    if os.path.exists(css_f):
        with open(css_f, 'r', encoding='utf-8') as f:
            content = f.read()
        if '/* Clean 2-Row Categorized Ticker Layout */' not in content:
            content += '\n' + css_addition
            with open(css_f, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {css_f}")

# 2. Update HTML structure in all index.html files to 2 categorized rows
new_ticker_html = '''<div class="recent-audits-ticker">
                <!-- Row 1: Verified Safe Brokers -->
                <div class="ticker-group">
                    <span class="ticker-group-label safe">🟢 Verified Safe Brokers</span>
                    <div class="ticker-chips">
                        <button class="ticker-chip safe" onclick="selectBroker('Exness')">Exness <span class="score">96% Safe</span></button>
                        <button class="ticker-chip safe" onclick="selectBroker('eToro')">eToro <span class="score">95% Safe</span></button>
                        <button class="ticker-chip safe" onclick="selectBroker('XM Group')">XM Group <span class="score">92% Safe</span></button>
                        <button class="ticker-chip safe" onclick="selectBroker('Plus500')">Plus500 <span class="score">91% Safe</span></button>
                        <button class="ticker-chip safe" onclick="selectBroker('AvaTrade')">AvaTrade <span class="score">90% Safe</span></button>
                    </div>
                </div>

                <!-- Row 2: Blacklisted Scam Warnings -->
                <div class="ticker-group">
                    <span class="ticker-group-label danger">🚨 Blacklisted Scam Alerts</span>
                    <div class="ticker-chips">
                        <button class="ticker-chip warning" onclick="selectBroker('PocketOption')">PocketOption <span class="score">42% Risk ⚠️</span></button>
                        <button class="ticker-chip danger" onclick="selectBroker('ApexCryptoFX')">ApexCryptoFX <span class="score">5% Scam 🚨</span></button>
                        <button class="ticker-chip danger" onclick="selectBroker('FxTradersGold')">FxTradersGold <span class="score">8% Scam 🚨</span></button>
                        <button class="ticker-chip danger" onclick="selectBroker('CapitalInvestFX')">CapitalInvestFX <span class="score">4% Scam 🚨</span></button>
                        <button class="ticker-chip danger" onclick="selectBroker('CryptoWealth24')">CryptoWealth24 <span class="score">6% Scam 🚨</span></button>
                    </div>
                </div>
            </div>'''

html_files = glob.glob('dating-photo-checker/broker-verifier/**/index.html', recursive=True) + glob.glob('broker-verifier/**/index.html', recursive=True)
for html_f in html_files:
    with open(html_f, 'r', encoding='utf-8') as f:
        html_content = f.read()
    html_content = re.sub(r'<div class="recent-audits-ticker">[\s\S]*?</div>\s*</div>', new_ticker_html, html_content)
    with open(html_f, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Updated HTML ticker in {html_f}")
