import glob
import re
import os

translations = {
    'en': 'Read Full Security Review ➔',
    'ro': 'Citește recenzia completă de siguranță ➔',
    'it': 'Leggi la recensione completa sulla sicurezza ➔',
    'de': 'Vollständige Sicherheitsbewertung lesen ➔',
    'es': 'Lea la reseña completa de seguridad ➔',
    'fr': "Lire l'examen complet de la sécurité ➔",
    'pt': 'Leia a análise completa de segurança ➔',
    'ru': 'Читать полный обзор безопасности ➔'
}

brokers = ['plus500', 'avatrade', 'xm', 'etoro', 'exness']

html_files = glob.glob('dating-photo-checker/broker-verifier/**/index.html', recursive=True) + glob.glob('broker-verifier/**/index.html', recursive=True)

updated_count = 0

for html_f in set(html_files):
    if not os.path.exists(html_f):
        continue
    
    # Determine language from folder path
    lang = 'en'
    path_parts = os.path.normpath(html_f).split(os.sep)
    for p in path_parts:
        if p in translations:
            lang = p
            break
            
    review_text = translations[lang]
    
    with open(html_f, 'r', encoding='utf-8') as f:
        content = f.read()
    
    modified = False

    # 1. Plus500 Card Fix
    if 'href="/reviews/plus500"' not in content:
        # Match plus500 CTA button and append review link right under it
        p500_pattern = r'(<a href="https://www\.plus500\.com/Home\.aspx\?id=139742"[\s\S]*?</a>)'
        replacement = r'\1\n                    <a href="/reviews/plus500" class="btn-review-link" style="display: block; margin-top: 6px; margin-bottom: 12px; color: var(--text-muted); font-size: 0.85rem; text-decoration: underline; font-weight: 500;">' + review_text + r'</a>'
        new_content = re.sub(p500_pattern, replacement, content)
        if new_content != content:
            content = new_content
            modified = True

    # 2. eToro Card Fix - update review link text to matching language
    etoro_pattern = r'(<a href="/reviews/etoro" class="btn-review-link"[\s\S]*?>)(.*?)(</a>)'
    if re.search(etoro_pattern, content):
        new_content = re.sub(etoro_pattern, r'\1' + review_text + r'\3', content)
        if new_content != content:
            content = new_content
            modified = True

    # 3. AvaTrade Card Fix - ensure review link text matches language
    avatrade_pattern = r'(<a href="/reviews/avatrade" class="btn-review-link"[\s\S]*?>)(.*?)(</a>)'
    if re.search(avatrade_pattern, content):
        new_content = re.sub(avatrade_pattern, r'\1' + review_text + r'\3', content)
        if new_content != content:
            content = new_content
            modified = True

    # 4. XM Card Fix - ensure review link text matches language
    xm_pattern = r'(<a href="/reviews/xm" class="btn-review-link"[\s\S]*?>)(.*?)(</a>)'
    if re.search(xm_pattern, content):
        new_content = re.sub(xm_pattern, r'\1' + review_text + r'\3', content)
        if new_content != content:
            content = new_content
            modified = True

    # 5. Exness Card Fix - ensure review link text matches language
    exness_pattern = r'(<a href="/reviews/exness" class="btn-review-link"[\s\S]*?>)(.*?)(</a>)'
    if re.search(exness_pattern, content):
        new_content = re.sub(exness_pattern, r'\1' + review_text + r'\3', content)
        if new_content != content:
            content = new_content
            modified = True

    if modified:
        with open(html_f, 'w', encoding='utf-8') as f:
            f.write(content)
        updated_count += 1
        print(f"Updated review links for language [{lang.upper()}] in {html_f}")

print(f"Total files updated: {updated_count}")
