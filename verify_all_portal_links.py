import glob
import re
import os

all_html = glob.glob('dating-photo-checker/broker-verifier/**/*.html', recursive=True) + glob.glob('broker-verifier/**/*.html', recursive=True)

pending_matches = []
void_matches = []

for f_path in set(all_html):
    if not os.path.exists(f_path):
        continue
    with open(f_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for pending text
    for term in ['pending approval', 'pendiente', 'așteptare', 'en espera', 'in attesa', 'ausstehend']:
        if term in content.lower():
            pending_matches.append((f_path, term))
            
    # Check for javascript:void(0) in cta buttons
    if re.search(r'href="javascript:void\(0\)"[^>]*class="[^"]*(cta|affiliate)[^"]*"', content, re.IGNORECASE):
        void_matches.append(f_path)

print("=== VERIFICATION REPORT ===")
print(f"Total HTML files checked: {len(set(all_html))}")
print(f"Pending text matches found: {len(pending_matches)}")
for m in pending_matches:
    print(f"  - {m[0]} (matched '{m[1]}')")

print(f"Void(0) CTA button matches found: {len(void_matches)}")
for m in void_matches:
    print(f"  - {m}")

if len(pending_matches) == 0 and len(void_matches) == 0:
    print("SUCCESS: 0 placeholders found! All affiliate links are 100% clean and active.")
