import glob
import re
import os

aff_link = "https://affs.click/E17wj"

minibanners = {
    'ro': f'''
            <!-- Mini-banner Auriu GOLD24-7 (Lățime completă peste tot banerul de la stânga la dreapta) -->
            <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 18px; text-align: left; width: 100%; box-sizing: border-box;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NOU: XM GOLD24-7</span>
                        <strong style="color: #eab308; font-size: 0.85rem;">Tranzacționare Aur 24/7 (Inclusiv în Weekend)</strong>
                    </div>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 5px 14px; border-radius: 4px; text-decoration: none; font-size: 0.8rem;">Tranzacționează GOLD24-7 ➔</a>
                </div>
                <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 6px 0;">
                    Tranzacționează Aur pe MT5 fără pauză 24/7 (inclusiv Sâmbăta și Duminica) cu levier de până la 1:250, conturi Swap-Free și suport Copy Trading.
                </p>
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Fără pauze în weekend</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Levier 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Spread-uri mici de la 19 pips</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Swap-Free & Copy Trading</span>
                </div>
            </div>''',

    'it': f'''
            <!-- Mini-banner Auriu GOLD24-7 (Lățime completă peste tot banerul de la stânga la dreapta) -->
            <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 18px; text-align: left; width: 100%; box-sizing: border-box;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NOVITÀ: XM GOLD24-7</span>
                        <strong style="color: #eab308; font-size: 0.85rem;">Trading su Oro 24/7 (Anche nel Weekend)</strong>
                    </div>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 5px 14px; border-radius: 4px; text-decoration: none; font-size: 0.8rem;">Fai Trading GOLD24-7 ➔</a>
                </div>
                <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 6px 0;">
                    Fai trading su Oro su MT5 senza interruzioni 24/7 (inclusi sabato e domenica) con leva fino a 1:250, conti Swap-Free e Copy Trading.
                </p>
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Operativo 24/7 nel weekend</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Leva fino a 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Spread competitivi da 19 pips</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Conti Swap-Free & Copy Trading</span>
                </div>
            </div>''',

    'de': f'''
            <!-- Mini-banner Auriu GOLD24-7 (Lățime completă peste tot banerul de la stânga la dreapta) -->
            <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 18px; text-align: left; width: 100%; box-sizing: border-box;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NEU: XM GOLD24-7</span>
                        <strong style="color: #eab308; font-size: 0.85rem;">24/7 Gold-Handel am Wochenende</strong>
                    </div>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 5px 14px; border-radius: 4px; text-decoration: none; font-size: 0.8rem;">GOLD24-7 Handeln ➔</a>
                </div>
                <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 6px 0;">
                    Handeln Sie Gold auf MT5 rund um die Uhr 24/7 (auch samstags und sonntags) mit bis zu 1:250 Hebel & Swap-Free-Konten.
                </p>
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Keine Wochenendpause</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Hebel bis zu 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Swap-Free Konten</span>
                </div>
            </div>''',

    'es': f'''
            <!-- Mini-banner Auriu GOLD24-7 (Lățime completă peste tot banerul de la stânga la dreapta) -->
            <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 18px; text-align: left; width: 100%; box-sizing: border-box;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NUEVO: XM GOLD24-7</span>
                        <strong style="color: #eab308; font-size: 0.85rem;">Trading de Oro 24/7 en Fin de Semana</strong>
                    </div>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 5px 14px; border-radius: 4px; text-decoration: none; font-size: 0.8rem;">Operar GOLD24-7 ➔</a>
                </div>
                <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 6px 0;">
                    Opere con oro en MT5 las 24 horas del día 24/7 (incluidos sábados y domingos) con apalancamiento hasta 1:250 y cuentas sin swap.
                </p>
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Sin pausa el fin de semana</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Apalancamiento 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Cuentas sin swap</span>
                </div>
            </div>''',

    'fr': f'''
            <!-- Mini-banner Auriu GOLD24-7 (Lățime completă peste tot banerul de la stânga la dreapta) -->
            <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 18px; text-align: left; width: 100%; box-sizing: border-box;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NOUVEAU: XM GOLD24-7</span>
                        <strong style="color: #eab308; font-size: 0.85rem;">Trading sur l'Or 24/7 le Week-end</strong>
                    </div>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 5px 14px; border-radius: 4px; text-decoration: none; font-size: 0.8rem;">Trader GOLD24-7 ➔</a>
                </div>
                <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 6px 0;">
                    Tradez l'or sur MT5 24h/24 et 7j/7 (y compris le samedi et le dimanche) avec un levier jusqu'à 1:250 et des comptes sans swap.
                </p>
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Pas de pause le week-end</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Levier 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Comptes sans swap</span>
                </div>
            </div>''',

    'pt': f'''
            <!-- Mini-banner Auriu GOLD24-7 (Lățime completă peste tot banerul de la stânga la dreapta) -->
            <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 18px; text-align: left; width: 100%; box-sizing: border-box;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NOVO: XM GOLD24-7</span>
                        <strong style="color: #eab308; font-size: 0.85rem;">Trading de Ouro 24/7 nos Fins de Semana</strong>
                    </div>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 5px 14px; border-radius: 4px; text-decoration: none; font-size: 0.8rem;">Negociar GOLD24-7 ➔</a>
                </div>
                <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 6px 0;">
                    Negocie ouro no MT5 24/7 (incluindo sábados e domingos) com alavancagem até 1:250 e contas sem swap.
                </p>
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Sem pausas nos fins de semana</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Alavancagem 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Contas sem swap</span>
                </div>
            </div>''',

    'ru': f'''
            <!-- Mini-banner Auriu GOLD24-7 (Lățime completă peste tot banerul de la stânga la dreapta) -->
            <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 18px; text-align: left; width: 100%; box-sizing: border-box;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 НОВИНКА: XM GOLD24-7</span>
                        <strong style="color: #eab308; font-size: 0.85rem;">Торговля золотом 24/7 в выходные</strong>
                    </div>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 5px 14px; border-radius: 4px; text-decoration: none; font-size: 0.8rem;">Торговать GOLD24-7 ➔</a>
                </div>
                <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 6px 0;">
                    Торгуйте золотом на MT5 24/7 (включая субботу и воскресенье) с плечом до 1:250 и счетами Swap-Free.
                </p>
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Без перерывов на выходные</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Плечо 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Счета Swap-Free</span>
                </div>
            </div>''',

    'en': f'''
            <!-- Mini-banner Auriu GOLD24-7 (Lățime completă peste tot banerul de la stânga la dreapta) -->
            <div style="margin-top: 14px; background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 8px; padding: 12px 18px; text-align: left; width: 100%; box-sizing: border-box;">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px; margin-bottom: 6px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.75rem; font-weight: 800; padding: 2px 8px; border-radius: 12px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NEW: XM GOLD24-7</span>
                        <strong style="color: #eab308; font-size: 0.85rem;">24/7 Weekend Gold Trading Available</strong>
                    </div>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 5px 14px; border-radius: 4px; text-decoration: none; font-size: 0.8rem;">Trade GOLD24-7 ➔</a>
                </div>
                <p style="color: #cbd5e1; font-size: 0.8rem; line-height: 1.4; margin: 0 0 6px 0;">
                    Trade Gold on MT5 non-stop 24/7 (including Saturday & Sunday) with leverage up to 1:250, Swap-Free accounts & Copy Trading support.
                </p>
                <div style="display: flex; align-items: center; gap: 12px; flex-wrap: wrap;">
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ No weekend gaps</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Up to 1:250 leverage</span>
                    <span style="color: #94a3b8; font-size: 0.75rem;">✓ Swap-Free & Copy Trading</span>
                </div>
            </div>'''
}

all_homepages = glob.glob('broker-verifier/**/index.html', recursive=True) + glob.glob('dating-photo-checker/broker-verifier/**/index.html', recursive=True)

count = 0
for f_path in set(all_homepages):
    if not os.path.exists(f_path):
        continue
        
    with open(f_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    f_lower = f_path.replace('\\', '/').lower()
    lang = 'en'
    for l in ['ro', 'it', 'de', 'es', 'fr', 'pt', 'ru']:
        if f'/{l}/' in f_lower:
            lang = l
            break
            
    gold_html = minibanners.get(lang, minibanners['en'])
    
    # 1. Clean out any GOLD24-7 box inside affiliate-text-area
    content = re.sub(r'\s*<!-- XM GOLD24-7 Feature Highlight[\s\S]*?<\/div>\s*', '\n', content)
    
    # 2. Find the XM banner block inside .affiliate-banner-inner
    if 'id="xm-broker"' in content:
        parts = content.split('id="xm-broker"', 1)
        if '</section>' in parts[1]:
            card_parts = parts[1].split('</section>', 1)
            card_html = card_parts[0]
            
            # Remove any existing notice box from inside affiliate-text-area if we move it to bottom of banner inner
            # Extract notice box HTML
            notice_match = re.search(r'(<!-- XM Global Private Registration Support CTA -->[\s\S]*?<div class="affiliate-notice-box"[\s\S]*?<\/div>\s*<\/div>)', card_html)
            if notice_match:
                notice_html = notice_match.group(1).replace('margin-top: 18px;', 'margin-top: 12px; width: 100%; box-sizing: border-box;')
                # Clean notice_html from card_html
                card_html_clean = card_html.replace(notice_match.group(1), '')
            else:
                notice_html = ''
                card_html_clean = card_html
                
            # Place gold_html AND notice_html directly inside .affiliate-banner-inner right before the closing </div> of .affiliate-banner-inner
            # Find the closing </div> of .affiliate-banner-inner (which is the last </div></div> before </section>)
            closing_idx = card_html_clean.rfind('</div>\n        </div>')
            if closing_idx == -1:
                closing_idx = card_html_clean.rfind('</div>\n    </div>')
            if closing_idx == -1:
                closing_idx = card_html_clean.rfind('</div>')
                
            if closing_idx != -1:
                new_card_html = card_html_clean[:closing_idx] + '\n' + gold_html + card_html_clean[closing_idx:]
                new_content = parts[0] + 'id="xm-broker"' + new_card_html + '</section>' + card_parts[1]
                with open(f_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Applied 100% full-banner width mini-banners locally: {f_path}")
                count += 1

print(f"Total homepages updated locally: {count}")
