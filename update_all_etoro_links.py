import glob
import re
import os

etoro_link = "https://med.etoro.com/B12087_A131664_TClick_Sisbrokersafe_main.aspx"

all_files = glob.glob('broker-verifier/**/*.html', recursive=True) + glob.glob('dating-photo-checker/broker-verifier/**/*.html', recursive=True)

labels = {
    'ro': 'Deschide Cont Oficial la eToro ↗',
    'it': 'Apri Conto Ufficiale su eToro ↗',
    'de': 'Offizielles Konto bei eToro Eröffnen ↗',
    'es': 'Abrir Cuenta Oficial en eToro ↗',
    'fr': 'Ouvrir un Compte Officiel sur eToro ↗',
    'pt': 'Abrir Conta Oficial na eToro ↗',
    'ru': 'Открыть Официальный Счет на eToro ↗',
    'en': 'Open Official Account at eToro ↗'
}

count = 0
for f_path in set(all_files):
    if not os.path.exists(f_path):
        continue
    with open(f_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False
    f_lower = f_path.replace('\\', '/').lower()
    
    # Determine language
    lang = 'en'
    for l in ['ro', 'it', 'de', 'es', 'fr', 'pt', 'ru']:
        if f'/{l}/' in f_lower:
            lang = l
            break

    # 1. Update review pages (etoro.html)
    if 'etoro.html' in f_lower:
        btn_label = labels.get(lang, labels['en'])
        # Replace any cta-btn-review anchor tag
        new_content = re.sub(
            r'<a\s+[^>]*class="cta-btn-review"[^>]*>[\s\S]*?<\/a>',
            f'<a href="{etoro_link}" target="_blank" rel="noopener" class="cta-btn-review">{btn_label}</a>',
            content
        )
        if new_content != content:
            content = new_content
            modified = True

    # 2. Update index.html pages (#etoro-cta)
    if 'etoro-cta' in content:
        if lang == 'ro':
            idx_label = 'Deschide Cont Gratuit →'
        elif lang == 'it':
            idx_label = 'Apri Conto Gratuito →'
        elif lang == 'de':
            idx_label = 'Kostenloses Konto Eröffnen →'
        elif lang == 'es':
            idx_label = 'Abrir Cuenta Gratis →'
        elif lang == 'fr':
            idx_label = 'Ouvrir un Compte Gratuit →'
        elif lang == 'pt':
            idx_label = 'Abrir Conta Gratuita →'
        elif lang == 'ru':
            idx_label = 'Открыть Бесплатный Счет →'
        else:
            idx_label = 'Open Free Account →'

        new_content = re.sub(
            r'<a\s+[^>]*id="etoro-cta"[^>]*>[\s\S]*?<\/a>',
            f'<a href="{etoro_link}" target="_blank" rel="noopener sponsored" class="btn-affiliate" id="etoro-cta" style="background: linear-gradient(135deg, #10b981, #059669); color: #ffffff !important; font-weight: 700; margin-bottom: 8px;">\n                        {idx_label}\n                    </a>',
            content
        )
        if new_content != content:
            content = new_content
            modified = True

    if modified:
        with open(f_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {f_path}")
        count += 1

print(f"Total HTML files updated: {count}")
