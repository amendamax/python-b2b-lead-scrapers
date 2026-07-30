import glob
import re
import os

files = glob.glob('broker-verifier/**/index.html', recursive=True) + glob.glob('dating-photo-checker/broker-verifier/**/index.html', recursive=True)
pattern = re.compile(r'<a href="javascript:void\(0\)" class="btn-affiliate" id="etoro-cta"[\s\S]*?</a>')

updated_count = 0
for f_path in set(files):
    if not os.path.exists(f_path):
        continue
    with open(f_path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'etoro-cta' in content and 'javascript:void(0)' in content:
        f_lower = f_path.replace('\\', '/').lower()
        if '/ro/' in f_lower:
            label = 'Deschide Cont Gratuit →'
        elif '/it/' in f_lower:
            label = 'Apri Conto Gratuito →'
        elif '/de/' in f_lower:
            label = 'Kostenloses Konto Eröffnen →'
        elif '/es/' in f_lower:
            label = 'Abrir Cuenta Gratis →'
        elif '/fr/' in f_lower:
            label = 'Ouvrir un Compte Gratuit →'
        elif '/pt/' in f_lower:
            label = 'Abrir Conta Gratuita →'
        elif '/ru/' in f_lower:
            label = 'Открыть Бесплатный Счет →'
        else:
            label = 'Open Free Account →'
        
        replacement = f'''<a href="https://med.etoro.com/B12087_A131664_TClick_Sisbrokersafe_main.aspx" target="_blank" rel="noopener sponsored" class="btn-affiliate" id="etoro-cta" style="background: linear-gradient(135deg, #10b981, #059669); color: #ffffff !important; font-weight: 700; margin-bottom: 8px;">
                        {label}
                    </a>'''
        
        new_content = pattern.sub(replacement, content)
        with open(f_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated: {f_path}")
        updated_count += 1

print(f"Total files updated: {updated_count}")
