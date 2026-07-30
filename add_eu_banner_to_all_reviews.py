import glob
import re
import os

banners = {
    'ro': '''
                    <!-- EU Resident XM Global Notice -->
                    <div style="margin-top: 15px; padding: 12px 16px; background: rgba(16, 185, 129, 0.06); border: 1px dashed rgba(16, 185, 129, 0.4); border-radius: 8px; display: flex; align-items: center; gap: 12px; text-align: left;">
                        <span style="font-size: 1.25rem;">🇪🇺</span>
                        <div style="font-size: 0.82rem; line-height: 1.4; color: #cbd5e1;">
                            <strong>Rezident în Europa?</strong> Obține levier de 1:1000, bonusuri de depozit și Copy Trading sub reglementările XM Global. 
                            <a href="https://wa.me/393209481876?text=Buna,%20doresc%20linkul%20privat%20de%20inregistrare%20XM%20Global." target="_blank" rel="noopener" style="color: #34d399; font-weight: 700; text-decoration: underline; margin-left: 5px;">
                                Discută cu noi pe WhatsApp pentru instrucțiuni de înregistrare privată →
                            </a>
                        </div>
                    </div>''',

    'it': '''
                    <!-- EU Resident XM Global Notice -->
                    <div style="margin-top: 15px; padding: 12px 16px; background: rgba(16, 185, 129, 0.06); border: 1px dashed rgba(16, 185, 129, 0.4); border-radius: 8px; display: flex; align-items: center; gap: 12px; text-align: left;">
                        <span style="font-size: 1.25rem;">🇪🇺</span>
                        <div style="font-size: 0.82rem; line-height: 1.4; color: #cbd5e1;">
                            <strong>Residente in Europa?</strong> Ottieni leva fino a 1:1000, bonus sul deposito e Copy Trading con regolamentazione XM Global. 
                            <a href="https://wa.me/393209481876?text=Ciao,%20desidero%20il%20link%20privato%20di%20registrazione%20XM%20Global." target="_blank" rel="noopener" style="color: #34d399; font-weight: 700; text-decoration: underline; margin-left: 5px;">
                                Chatta con noi su WhatsApp per istruzioni di registrazione privata →
                            </a>
                        </div>
                    </div>''',

    'de': '''
                    <!-- EU Resident XM Global Notice -->
                    <div style="margin-top: 15px; padding: 12px 16px; background: rgba(16, 185, 129, 0.06); border: 1px dashed rgba(16, 185, 129, 0.4); border-radius: 8px; display: flex; align-items: center; gap: 12px; text-align: left;">
                        <span style="font-size: 1.25rem;">🇪🇺</span>
                        <div style="font-size: 0.82rem; line-height: 1.4; color: #cbd5e1;">
                            <strong>Wohnsitz in Europa?</strong> Erhalten Sie 1:1000 Hebel, Einzahlungsboni und Copy Trading unter XM Global Regulierung. 
                            <a href="https://wa.me/393209481876?text=Hallo,%20ich%20moechte%20den%20privaten%20XM%20Global%20Registrierungslink." target="_blank" rel="noopener" style="color: #34d399; font-weight: 700; text-decoration: underline; margin-left: 5px;">
                                Chatten Sie mit uns auf WhatsApp für private Registrierungsanweisungen →
                            </a>
                        </div>
                    </div>''',

    'es': '''
                    <!-- EU Resident XM Global Notice -->
                    <div style="margin-top: 15px; padding: 12px 16px; background: rgba(16, 185, 129, 0.06); border: 1px dashed rgba(16, 185, 129, 0.4); border-radius: 8px; display: flex; align-items: center; gap: 12px; text-align: left;">
                        <span style="font-size: 1.25rem;">🇪🇺</span>
                        <div style="font-size: 0.82rem; line-height: 1.4; color: #cbd5e1;">
                            <strong>¿Residente en Europa?</strong> Obtenga apalancamiento 1:1000, bonos de depósito y Copy Trading bajo regulaciones de XM Global. 
                            <a href="https://wa.me/393209481876?text=Hola,%20deseo%20el%20enlace%20privado%20de%20registro%20XM%20Global." target="_blank" rel="noopener" style="color: #34d399; font-weight: 700; text-decoration: underline; margin-left: 5px;">
                                Chatea con nosotros en WhatsApp para instrucciones de registro privado →
                            </a>
                        </div>
                    </div>''',

    'fr': '''
                    <!-- EU Resident XM Global Notice -->
                    <div style="margin-top: 15px; padding: 12px 16px; background: rgba(16, 185, 129, 0.06); border: 1px dashed rgba(16, 185, 129, 0.4); border-radius: 8px; display: flex; align-items: center; gap: 12px; text-align: left;">
                        <span style="font-size: 1.25rem;">🇪🇺</span>
                        <div style="font-size: 0.82rem; line-height: 1.4; color: #cbd5e1;">
                            <strong>Résident en Europe ?</strong> Obtenez un levier de 1:1000, des bonus de dépôt et le Copy Trading sous la réglementation XM Global. 
                            <a href="https://wa.me/393209481876?text=Bonjour,%20je%20souhaite%20le%20lien%20d'inscription%20prive%20XM%20Global." target="_blank" rel="noopener" style="color: #34d399; font-weight: 700; text-decoration: underline; margin-left: 5px;">
                                Discutez avec nous sur WhatsApp pour les instructions d'inscription privée →
                            </a>
                        </div>
                    </div>''',

    'pt': '''
                    <!-- EU Resident XM Global Notice -->
                    <div style="margin-top: 15px; padding: 12px 16px; background: rgba(16, 185, 129, 0.06); border: 1px dashed rgba(16, 185, 129, 0.4); border-radius: 8px; display: flex; align-items: center; gap: 12px; text-align: left;">
                        <span style="font-size: 1.25rem;">🇪🇺</span>
                        <div style="font-size: 0.82rem; line-height: 1.4; color: #cbd5e1;">
                            <strong>Residente na Europa?</strong> Obtenha alavancagem de 1:1000, bónus de depósito e Copy Trading sob regulamentação XM Global. 
                            <a href="https://wa.me/393209481876?text=Ola,%20desejo%20o%20link%20privado%20de%20registo%20XM%20Global." target="_blank" rel="noopener" style="color: #34d399; font-weight: 700; text-decoration: underline; margin-left: 5px;">
                                Fale conosco no WhatsApp para instruções de registo privado →
                            </a>
                        </div>
                    </div>''',

    'ru': '''
                    <!-- EU Resident XM Global Notice -->
                    <div style="margin-top: 15px; padding: 12px 16px; background: rgba(16, 185, 129, 0.06); border: 1px dashed rgba(16, 185, 129, 0.4); border-radius: 8px; display: flex; align-items: center; gap: 12px; text-align: left;">
                        <span style="font-size: 1.25rem;">🇪🇺</span>
                        <div style="font-size: 0.82rem; line-height: 1.4; color: #cbd5e1;">
                            <strong>Резидент Европы?</strong> Получите плечо 1:1000, бонусы на депозит и Copy Trading в XM Global. 
                            <a href="https://wa.me/393209481876?text=Здравствуйте,%20хочу%20приватную%20ссылку%20на%20регистрацию%20XM%20Global." target="_blank" rel="noopener" style="color: #34d399; font-weight: 700; text-decoration: underline; margin-left: 5px;">
                                Напишите нам в WhatsApp для получения инструкций по приватной регистрации →
                            </a>
                        </div>
                    </div>''',

    'en': '''
                    <!-- EU Resident XM Global Notice -->
                    <div style="margin-top: 15px; padding: 12px 16px; background: rgba(16, 185, 129, 0.06); border: 1px dashed rgba(16, 185, 129, 0.4); border-radius: 8px; display: flex; align-items: center; gap: 12px; text-align: left;">
                        <span style="font-size: 1.25rem;">🇪🇺</span>
                        <div style="font-size: 0.82rem; line-height: 1.4; color: #cbd5e1;">
                            <strong>European Resident?</strong> Get 1:1000 leverage, deposit bonuses, and Copy Trading under XM Global regulations. 
                            <a href="https://wa.me/393209481876?text=Hello,%20I%20want%20the%20private%20XM%20Global%20registration%20link%20and%20partner%20code." target="_blank" rel="noopener" style="color: #34d399; font-weight: 700; text-decoration: underline; margin-left: 5px;">
                                Chat with us on WhatsApp for private registration instructions →
                            </a>
                        </div>
                    </div>'''
}

all_files = glob.glob('broker-verifier/**/reviews/*.html', recursive=True) + glob.glob('dating-photo-checker/broker-verifier/**/reviews/*.html', recursive=True)

count = 0
for f_path in set(all_files):
    if not os.path.exists(f_path):
        continue
    with open(f_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'EU Resident XM Global Notice' in content or 'European Resident?' in content or 'Rezident în Europa?' in content or 'Residente in Europa?' in content:
        continue  # Already present
        
    f_lower = f_path.replace('\\', '/').lower()
    lang = 'en'
    for l in ['ro', 'it', 'de', 'es', 'fr', 'pt', 'ru']:
        if f'/{l}/' in f_lower:
            lang = l
            break
            
    banner_html = banners.get(lang, banners['en'])
    
    # Insert right inside <div class="cta-box"> right after class="cta-btn-review">...</a>
    if 'class="cta-btn-review">' in content:
        parts = re.split(r'(<\/a>\s*(?:<p[^>]*>.*?<\/p>)?\s*<\/div>)', content, flags=re.DOTALL)
        # Find cta-btn-review and insert banner right after the CTA anchor button
        pattern = r'(<a\s+[^>]*class="cta-btn-review"[^>]*>[\s\S]*?<\/a>)'
        new_content = re.sub(pattern, r'\1\n' + banner_html, content, count=1)
        if new_content != content:
            with open(f_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Added EU banner to review: {f_path}")
            count += 1

print(f"Total review pages updated with EU banner: {count}")
