import glob
import re
import os

aff_link = "https://affs.click/E17wj"

boxes = {
    'ro': f'''
            <!-- GOLD24-7 Highlight Feature Box -->
            <div style="background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 12px; padding: 1.5rem; margin: 1.8rem 0; box-shadow: 0 4px 20px rgba(234, 179, 8, 0.15);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.8rem; flex-wrap: wrap;">
                    <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.8rem; font-weight: 800; padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NOU: GOLD24-7 PE XM</span>
                    <span style="color: #eab308; font-weight: 700; font-size: 0.95rem;">Tranzacționare Aur 24/7 (Inclusiv în Weekend)</span>
                </div>
                <p style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6; margin-bottom: 1rem;">
                    XM a lansat noul instrument exclusiv <strong>GOLD24-7</strong> pe MT5! Acum poți tranzacționa Aur neîntrerupt 24 de ore din 24, inclusiv Sâmbăta și Duminica, cu levier de până la 1:250, conturi Swap-Free și suport complet pentru Copy Trading & boți automați.
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 1rem; align-items: center;">
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Fără pauză în weekend</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Levier 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Spread-uri competitive</span>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-size: 0.88rem; margin-left: auto;">Tranzacționează GOLD24-7 Acum ➔</a>
                </div>
            </div>''',

    'it': f'''
            <!-- GOLD24-7 Highlight Feature Box -->
            <div style="background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 12px; padding: 1.5rem; margin: 1.8rem 0; box-shadow: 0 4px 20px rgba(234, 179, 8, 0.15);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.8rem; flex-wrap: wrap;">
                    <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.8rem; font-weight: 800; padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NOVITÀ: XM GOLD24-7</span>
                    <span style="color: #eab308; font-weight: 700; font-size: 0.95rem;">Trading su Oro 24/7 Anche nel Weekend</span>
                </div>
                <p style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6; margin-bottom: 1rem;">
                    XM ha lanciato lo strumento esclusivo <strong>GOLD24-7</strong> su MT5! Ora puoi fare trading su Oro senza interruzioni 24 ore su 24, inclusi sabato e domenica, con leva fino a 1:250, conti Swap-Free e supporto completo per Copy Trading & bot automatici.
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 1rem; align-items: center;">
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Operativo 24/7 nel weekend</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Leva fino a 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Spread competitivi</span>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-size: 0.88rem; margin-left: auto;">Fai Trading su GOLD24-7 Ora ➔</a>
                </div>
            </div>''',

    'de': f'''
            <!-- GOLD24-7 Highlight Feature Box -->
            <div style="background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 12px; padding: 1.5rem; margin: 1.8rem 0; box-shadow: 0 4px 20px rgba(234, 179, 8, 0.15);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.8rem; flex-wrap: wrap;">
                    <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.8rem; font-weight: 800; padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NEU: XM GOLD24-7</span>
                    <span style="color: #eab308; font-weight: 700; font-size: 0.95rem;">24/7 Gold-Handel auch am Wochenende</span>
                </div>
                <p style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6; margin-bottom: 1rem;">
                    XM startet <strong>GOLD24-7</strong> auf MT5! Handeln Sie Gold rund um die Uhr, auch samstags und sonntags, mit einem Hebel von bis zu 1:250, Swap-Free-Konten und voller Unterstützung für Copy-Trading und automatisierte Bots.
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 1rem; align-items: center;">
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Keine Wochenendpause</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Hebel bis zu 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Enge Spreads</span>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-size: 0.88rem; margin-left: auto;">Jetzt GOLD24-7 Handeln ➔</a>
                </div>
            </div>''',

    'es': f'''
            <!-- GOLD24-7 Highlight Feature Box -->
            <div style="background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 12px; padding: 1.5rem; margin: 1.8rem 0; box-shadow: 0 4px 20px rgba(234, 179, 8, 0.15);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.8rem; flex-wrap: wrap;">
                    <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.8rem; font-weight: 800; padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NUEVO: XM GOLD24-7</span>
                    <span style="color: #eab308; font-weight: 700; font-size: 0.95rem;">Trading de Oro 24/7 Incluyendo Fin de Semana</span>
                </div>
                <p style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6; margin-bottom: 1rem;">
                    ¡XM presenta <strong>GOLD24-7</strong> en MT5! Ahora puede operar con oro las 24 horas del día, incluidos sábados y domingos, con un apalancamiento de hasta 1:250, cuentas sin swap y soporte completo para Copy Trading y bots automáticos.
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 1rem; align-items: center;">
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Sin pausas de fin de semana</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Apalancamiento 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Spreads ajustados</span>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-size: 0.88rem; margin-left: auto;">Operar GOLD24-7 Ahora ➔</a>
                </div>
            </div>''',

    'fr': f'''
            <!-- GOLD24-7 Highlight Feature Box -->
            <div style="background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 12px; padding: 1.5rem; margin: 1.8rem 0; box-shadow: 0 4px 20px rgba(234, 179, 8, 0.15);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.8rem; flex-wrap: wrap;">
                    <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.8rem; font-weight: 800; padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NOUVEAU: XM GOLD24-7</span>
                    <span style="color: #eab308; font-weight: 700; font-size: 0.95rem;">Trading sur l'Or 24/7 y Compris le Week-end</span>
                </div>
                <p style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6; margin-bottom: 1rem;">
                    XM lance <strong>GOLD24-7</strong> sur MT5 ! Vous pouvez désormais trader l'or 24h/24, y compris le samedi et le dimanche, avec un levier allant jusqu'à 1:250, des comptes sans swap et un support complet pour le Copy Trading et les bots automatiques.
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 1rem; align-items: center;">
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Pas de pause le week-end</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Levier jusqu'à 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Spreads serrés</span>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-size: 0.88rem; margin-left: auto;">Trader GOLD24-7 Maintenant ➔</a>
                </div>
            </div>''',

    'pt': f'''
            <!-- GOLD24-7 Highlight Feature Box -->
            <div style="background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 12px; padding: 1.5rem; margin: 1.8rem 0; box-shadow: 0 4px 20px rgba(234, 179, 8, 0.15);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.8rem; flex-wrap: wrap;">
                    <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.8rem; font-weight: 800; padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NOVO: XM GOLD24-7</span>
                    <span style="color: #eab308; font-weight: 700; font-size: 0.95rem;">Trading de Ouro 24/7 Incluindo Fins de Semana</span>
                </div>
                <p style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6; margin-bottom: 1rem;">
                    A XM lançou o <strong>GOLD24-7</strong> no MT5! Agora você pode negociar ouro 24 horas por dia, incluindo sábados e domingos, com alavancagem de até 1:250, contas sem swap e suporte total a Copy Trading e bots automatizados.
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 1rem; align-items: center;">
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Sem pausas nos fins de semana</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Alavancagem 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Spreads baixos</span>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-size: 0.88rem; margin-left: auto;">Negociar GOLD24-7 Agora ➔</a>
                </div>
            </div>''',

    'ru': f'''
            <!-- GOLD24-7 Highlight Feature Box -->
            <div style="background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 12px; padding: 1.5rem; margin: 1.8rem 0; box-shadow: 0 4px 20px rgba(234, 179, 8, 0.15);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.8rem; flex-wrap: wrap;">
                    <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.8rem; font-weight: 800; padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 НОВИНКА: XM GOLD24-7</span>
                    <span style="color: #eab308; font-weight: 700; font-size: 0.95rem;">Торговля золотом 24/7, включая выходные</span>
                </div>
                <p style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6; margin-bottom: 1rem;">
                    XM запустила инструмент <strong>GOLD24-7</strong> на MT5! Теперь вы можете торговать золотом 24 часа в сутки, включая субботу и воскресенье, с кредитным плечом до 1:250, счетами Swap-Free и поддержкой Copy Trading.
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 1rem; align-items: center;">
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Без перерывов на выходные</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Плечо до 1:250</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Узкие спрэды</span>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-size: 0.88rem; margin-left: auto;">Торговать GOLD24-7 Сейчас ➔</a>
                </div>
            </div>''',

    'en': f'''
            <!-- GOLD24-7 Highlight Feature Box -->
            <div style="background: linear-gradient(135deg, rgba(234, 179, 8, 0.12) 0%, rgba(5, 8, 15, 0.95) 100%); border: 1px solid rgba(234, 179, 8, 0.4); border-radius: 12px; padding: 1.5rem; margin: 1.8rem 0; box-shadow: 0 4px 20px rgba(234, 179, 8, 0.15);">
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 0.8rem; flex-wrap: wrap;">
                    <span style="background: rgba(234, 179, 8, 0.2); color: #eab308; font-size: 0.8rem; font-weight: 800; padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(234, 179, 8, 0.4);">🥇 NEW: XM GOLD24-7</span>
                    <span style="color: #eab308; font-weight: 700; font-size: 0.95rem;">24/7 Weekend Gold Trading Available</span>
                </div>
                <p style="color: #e2e8f0; font-size: 0.92rem; line-height: 1.6; margin-bottom: 1rem;">
                    XM introduces <strong>GOLD24-7</strong> on MT5! You can now trade Gold non-stop 24 hours a day, including Saturday and Sunday, with leverage up to 1:250, Swap-Free accounts, and full Copy Trading & automated bot support.
                </p>
                <div style="display: flex; flex-wrap: wrap; gap: 1rem; align-items: center;">
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ No weekend gaps</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Up to 1:250 leverage</span>
                    <span style="color: #94a3b8; font-size: 0.82rem;">✓ Tight competitive spreads</span>
                    <a href="{aff_link}" target="_blank" rel="noopener" style="background: linear-gradient(135deg, #eab308, #ca8a04); color: #000000 !important; font-weight: 800; padding: 8px 18px; border-radius: 6px; text-decoration: none; font-size: 0.88rem; margin-left: auto;">Trade GOLD24-7 Now ➔</a>
                </div>
            </div>'''
}

all_files = glob.glob('broker-verifier/**/xm.html', recursive=True) + glob.glob('dating-photo-checker/broker-verifier/**/xm.html', recursive=True)

count = 0
for f_path in set(all_files):
    if not os.path.exists(f_path):
        continue
    with open(f_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'GOLD24-7' in content:
        continue  # Already updated
        
    f_lower = f_path.replace('\\', '/').lower()
    lang = 'en'
    for l in ['ro', 'it', 'de', 'es', 'fr', 'pt', 'ru']:
        if f'/{l}/' in f_lower:
            lang = l
            break
            
    box_html = boxes.get(lang, boxes['en'])
    
    # Insert right before <h2 class="review-section-title"> or before pros-cons-grid
    if '<h2 class="review-section-title">' in content:
        parts = content.split('<h2 class="review-section-title">', 1)
        new_content = parts[0] + box_html + '\n            <h2 class="review-section-title">' + parts[1]
    elif '<div class="pros-cons-grid">' in content:
        parts = content.split('<div class="pros-cons-grid">', 1)
        new_content = parts[0] + box_html + '\n            <div class="pros-cons-grid">' + parts[1]
    else:
        continue
        
    with open(f_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Updated XM review: {f_path}")
    count += 1

print(f"Total XM review files updated with GOLD24-7: {count}")
