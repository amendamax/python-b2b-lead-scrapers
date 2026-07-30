import glob
import re
import os

aff_link = "https://affs.click/E17wj"

boxes = {
    'ro': f'''
                    <!-- XM GOLD24-7 Feature Highlight -->
                    <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 14px; text-align: left;">
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px;">
                            <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NOU: XM GOLD24-7</span>
                            <strong style="color: #eab308; font-size: 0.85rem;">Tranzacționare Aur 24/7 în Weekend</strong>
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 8px 0;">
                            Tranzacționează Aur pe MT5 fără pauză 24/7 (inclusiv Sâmbăta și Duminica) cu levier de până la 1:250, conturi Swap-Free și suport Copy Trading.
                        </p>
                        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 6px;">
                            <span style="color: #94a3b8; font-size: 0.75rem;">✓ Fără pauze în weekend &nbsp; ✓ Spread-uri competitive</span>
                            <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-size: 0.78rem;">Tranzacționează GOLD24-7 ➔</a>
                        </div>
                    </div>''',

    'it': f'''
                    <!-- XM GOLD24-7 Feature Highlight -->
                    <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 14px; text-align: left;">
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px;">
                            <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NOVITÀ: XM GOLD24-7</span>
                            <strong style="color: #eab308; font-size: 0.85rem;">Trading su Oro 24/7 nel Weekend</strong>
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 8px 0;">
                            Fai trading su Oro su MT5 senza interruzioni 24/7 (inclusi sabato e domenica) con leva fino a 1:250, conti Swap-Free e Copy Trading.
                        </p>
                        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 6px;">
                            <span style="color: #94a3b8; font-size: 0.75rem;">✓ Operativo 24/7 &nbsp; ✓ Leva fino a 1:250</span>
                            <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-size: 0.78rem;">Fai Trading GOLD24-7 ➔</a>
                        </div>
                    </div>''',

    'de': f'''
                    <!-- XM GOLD24-7 Feature Highlight -->
                    <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 14px; text-align: left;">
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px;">
                            <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NEU: XM GOLD24-7</span>
                            <strong style="color: #eab308; font-size: 0.85rem;">24/7 Gold-Handel am Wochenende</strong>
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 8px 0;">
                            Handeln Sie Gold auf MT5 rund um die Uhr 24/7 (auch samstags und sonntags) mit bis zu 1:250 Hebel, Swap-Free-Konten & Copy Trading.
                        </p>
                        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 6px;">
                            <span style="color: #94a3b8; font-size: 0.75rem;">✓ Keine Wochenendpause &nbsp; ✓ Hebel 1:250</span>
                            <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-size: 0.78rem;">GOLD24-7 Handeln ➔</a>
                        </div>
                    </div>''',

    'es': f'''
                    <!-- XM GOLD24-7 Feature Highlight -->
                    <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 14px; text-align: left;">
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px;">
                            <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NUEVO: XM GOLD24-7</span>
                            <strong style="color: #eab308; font-size: 0.85rem;">Trading de Oro 24/7 en Fin de Semana</strong>
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 8px 0;">
                            Opere con oro en MT5 las 24 horas del día 24/7 (incluidos sábados y domingos) con apalancamiento hasta 1:250 y cuentas sin swap.
                        </p>
                        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 6px;">
                            <span style="color: #94a3b8; font-size: 0.75rem;">✓ Sin pausa el fin de semana &nbsp; ✓ Apalancamiento 1:250</span>
                            <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-size: 0.78rem;">Operar GOLD24-7 ➔</a>
                        </div>
                    </div>''',

    'fr': f'''
                    <!-- XM GOLD24-7 Feature Highlight -->
                    <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 14px; text-align: left;">
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px;">
                            <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NOUVEAU: XM GOLD24-7</span>
                            <strong style="color: #eab308; font-size: 0.85rem;">Trading sur l'Or 24/7 le Week-end</strong>
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 8px 0;">
                            Tradez l'or sur MT5 24h/24 et 7j/7 (y compris le samedi et le dimanche) avec un levier jusqu'à 1:250 et des comptes sans swap.
                        </p>
                        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 6px;">
                            <span style="color: #94a3b8; font-size: 0.75rem;">✓ Pas de pause le week-end &nbsp; ✓ Levier 1:250</span>
                            <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-size: 0.78rem;">Trader GOLD24-7 ➔</a>
                        </div>
                    </div>''',

    'pt': f'''
                    <!-- XM GOLD24-7 Feature Highlight -->
                    <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 14px; text-align: left;">
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px;">
                            <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NOVO: XM GOLD24-7</span>
                            <strong style="color: #eab308; font-size: 0.85rem;">Trading de Ouro 24/7 nos Fins de Semana</strong>
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 8px 0;">
                            Negocie ouro no MT5 24/7 (incluindo sábados e domingos) com alavancagem até 1:250 e contas sem swap.
                        </p>
                        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 6px;">
                            <span style="color: #94a3b8; font-size: 0.75rem;">✓ Sem pausas nos fins de semana &nbsp; ✓ Alavancagem 1:250</span>
                            <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-size: 0.78rem;">Negociar GOLD24-7 ➔</a>
                        </div>
                    </div>''',

    'ru': f'''
                    <!-- XM GOLD24-7 Feature Highlight -->
                    <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 14px; text-align: left;">
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px;">
                            <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 НОВИНКА: XM GOLD24-7</span>
                            <strong style="color: #eab308; font-size: 0.85rem;">Торговля золотом 24/7 в выходные</strong>
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 8px 0;">
                            Торгуйте золотом на MT5 24/7 (включая субботу и воскресенье) с плечом до 1:250 и счетами Swap-Free.
                        </p>
                        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 6px;">
                            <span style="color: #94a3b8; font-size: 0.75rem;">✓ Без перерывов на выходные &nbsp; ✓ Плечо 1:250</span>
                            <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-size: 0.78rem;">Торговать GOLD24-7 ➔</a>
                        </div>
                    </div>''',

    'en': f'''
                    <!-- XM GOLD24-7 Feature Highlight -->
                    <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 14px; text-align: left;">
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px;">
                            <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NEW: XM GOLD24-7</span>
                            <strong style="color: #eab308; font-size: 0.85rem;">24/7 Weekend Gold Trading Available</strong>
                        </div>
                        <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 8px 0;">
                            Trade Gold on MT5 non-stop 24/7 (including Saturday & Sunday) with leverage up to 1:250, Swap-Free accounts & Copy Trading support.
                        </p>
                        <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 6px;">
                            <span style="color: #94a3b8; font-size: 0.75rem;">✓ No weekend gaps &nbsp; ✓ Up to 1:250 leverage</span>
                            <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 4px 12px; border-radius: 4px; text-decoration: none; font-size: 0.78rem;">Trade GOLD24-7 ➔</a>
                        </div>
                    </div>'''
}

all_homepages = [
    'broker-verifier/index.html',
    'broker-verifier/ro/index.html',
    'broker-verifier/it/index.html',
    'broker-verifier/de/index.html',
    'broker-verifier/es/index.html',
    'broker-verifier/fr/index.html',
    'broker-verifier/pt/index.html',
    'broker-verifier/ru/index.html',
    'dating-photo-checker/broker-verifier/index.html',
    'dating-photo-checker/broker-verifier/ro/index.html',
    'dating-photo-checker/broker-verifier/it/index.html',
    'dating-photo-checker/broker-verifier/de/index.html',
    'dating-photo-checker/broker-verifier/es/index.html',
    'dating-photo-checker/broker-verifier/fr/index.html',
    'dating-photo-checker/broker-verifier/pt/index.html',
    'dating-photo-checker/broker-verifier/ru/index.html'
]

count = 0
for f_path in set(all_homepages):
    if not os.path.exists(f_path):
        continue
        
    with open(f_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'XM GOLD24-7 Feature Highlight' in content:
        continue  # Already updated
        
    f_lower = f_path.replace('\\', '/').lower()
    lang = 'en'
    for l in ['ro', 'it', 'de', 'es', 'fr', 'pt', 'ru']:
        if f'/{l}/' in f_lower:
            lang = l
            break
            
    box_html = boxes.get(lang, boxes['en'])
    
    # Insert right inside xm-broker section after affiliate-features ul
    pattern = r'(<id="xm-broker"[\s\S]*?<\/ul>)'
    # Or search for id="xm-broker" block
    if 'id="xm-broker"' in content:
        parts = content.split('id="xm-broker"', 1)
        if '</ul>' in parts[1]:
            subparts = parts[1].split('</ul>', 1)
            new_content = parts[0] + 'id="xm-broker"' + subparts[0] + '</ul>\n' + box_html + subparts[1]
            with open(f_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Added GOLD24-7 card box to homepage: {f_path}")
            count += 1

print(f"Total homepage XM cards updated: {count}")
