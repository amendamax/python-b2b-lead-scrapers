import glob
import re
import os

t_labels = {
    'ro': {
        'reg_profile': 'Profil de Reglementare {broker}',
        'trading_cond': 'Condiții de Tranzacționare & Costuri',
        'th_corp': 'Entități Corporative',
        'th_reg': 'Reglementatori Financiari',
        'th_fund': 'Protecție Fonduri Clienți',
        'th_age': 'Vechime Domeniu Web',
        'th_dep': 'Depozit Minim',
        'th_lev': 'Levier Maxim',
        'th_plat': 'Platforme de Tranzacționare',
        'th_exec': 'Model de Execuție',
        'th_spread': 'Spread-uri'
    },
    'it': {
        'reg_profile': 'Profilo Regolamentare {broker}',
        'trading_cond': 'Condizioni di Trading & Costi',
        'th_corp': 'Entità Societarie',
        'th_reg': 'Regolatori Finanziari',
        'th_fund': 'Protezione Fondi Clienti',
        'th_age': 'Età Dominio Web',
        'th_dep': 'Deposito Minimo',
        'th_lev': 'Leva Massima',
        'th_plat': 'Piattaforme di Trading',
        'th_exec': 'Modello di Esecuzione',
        'th_spread': 'Spread'
    },
    'de': {
        'reg_profile': 'Regulatorisches Profil von {broker}',
        'trading_cond': 'Handelsbedingungen & Kosten',
        'th_corp': 'Unternehmenseinheiten',
        'th_reg': 'Finanzaufsichtsbehörden',
        'th_fund': 'Kundengeldabsicherung',
        'th_age': 'Domain-Alter',
        'th_dep': 'Mindesteinzahlung',
        'th_lev': 'Maximaler Hebel',
        'th_plat': 'Handelsplattformen',
        'th_exec': 'Ausführungsmodell',
        'th_spread': 'Spreads'
    },
    'es': {
        'reg_profile': 'Perfil Regulatorio de {broker}',
        'trading_cond': 'Condiciones de Trading y Costes',
        'th_corp': 'Entidades Corporativas',
        'th_reg': 'Reguladores Financieros',
        'th_fund': 'Protección de Fondos',
        'th_age': 'Antigüedad del Dominio',
        'th_dep': 'Depósito Mínimo',
        'th_lev': 'Apalancamiento Máximo',
        'th_plat': 'Plataformas de Trading',
        'th_exec': 'Modelo de Ejecución',
        'th_spread': 'Spreads'
    },
    'fr': {
        'reg_profile': 'Profil Réglementaire de {broker}',
        'trading_cond': 'Conditions de Trading & Coûts',
        'th_corp': 'Entités Corporatives',
        'th_reg': 'Régulateurs Financiers',
        'th_fund': 'Protection des Fonds',
        'th_age': 'Âge du Domaine Web',
        'th_dep': 'Dépôt Minimum',
        'th_lev': 'Levier Maximum',
        'th_plat': 'Plateformes de Trading',
        'th_exec': 'Modèle d\'Exécution',
        'th_spread': 'Spreads'
    },
    'pt': {
        'reg_profile': 'Perfil Regulatório do {broker}',
        'trading_cond': 'Condições de Negociação & Custos',
        'th_corp': 'Entidades Corporativas',
        'th_reg': 'Reguladores Financeiros',
        'th_fund': 'Proteção de Fundos',
        'th_age': 'Idade do Domínio',
        'th_dep': 'Depósito Mínimo',
        'th_lev': 'Alavancagem Máxima',
        'th_plat': 'Plataformas de Trading',
        'th_exec': 'Modelo de Execução',
        'th_spread': 'Spreads'
    },
    'ru': {
        'reg_profile': 'Регуляторный Профиль {broker}',
        'trading_cond': 'Условия Торговли и Комиссии',
        'th_corp': 'Юридические Лица',
        'th_reg': 'Финансовые Регуляторы',
        'th_fund': 'Защита Средств Клиентов',
        'th_age': 'Возраст Веб-Домена',
        'th_dep': 'Минимальный Депозит',
        'th_lev': 'Максимальное Плечо',
        'th_plat': 'Торговые Платформы',
        'th_exec': 'Модель Исполнения',
        'th_spread': 'Спрэды'
    },
    'en': {
        'reg_profile': '{broker} Regulatory Profile',
        'trading_cond': 'Trading Conditions & Costs',
        'th_corp': 'Corporate Entities',
        'th_reg': 'Financial Regulators',
        'th_fund': 'Client Fund Protection',
        'th_age': 'Domain Age',
        'th_dep': 'Minimum Deposit',
        'th_lev': 'Max Leverage',
        'th_plat': 'Trading Platforms',
        'th_exec': 'Execution Model',
        'th_spread': 'Spreads'
    }
}

broker_data = {
    'xm': {
        'name': 'XM Group',
        'corp': 'Trading Point of Financial Instruments Ltd (Cyprus)<br>Trading Point of Financial Instruments Pty Ltd (Australia)<br>XM Global Limited (Belize)',
        'reg': 'CySEC (Cyprus) - License: 120/10<br>ASIC (Australia) - License: 443670<br>FSC (Belize) - License: 000261/397<br>DFSA (Dubai) - License: F003484',
        'fund': 'Segregated Accounts, Negative Balance Protection',
        'age': 'Registered in 2003 (23 Years Old)',
        'dep': '$5 (Micro and Standard accounts)',
        'lev': '1:30 (CySEC/ASIC) / Up to 1:1000 (XM Global offshore)',
        'plat': 'MetaTrader 4 (MT4), MetaTrader 5 (MT5), XM Mobile App',
        'exec': 'STP/NDD (99.35% executed under 1 second)',
        'spread': 'From 0.6 pips (Ultra Low accounts, 0 commission)'
    },
    'exness': {
        'name': 'Exness Group',
        'corp': 'Exness (SC) Ltd (Seychelles)<br>Exness B.V. (Curaçao)<br>Exness (Cy) Ltd (Cyprus)',
        'reg': 'FCA (UK) - Financial Conduct Authority<br>CySEC (Cyprus) - License: 178/12<br>FSA (Seychelles) - License: SD025<br>CBCG (Curaçao) - License: 0003LSI',
        'fund': 'Tier-1 Segregated Accounts, Instant Automatic Withdrawals',
        'age': 'Registered in 2008 (18 Years Old)',
        'dep': '$1 (Standard accounts)',
        'lev': '1:2000 to Unlimited (Offshore entity)',
        'plat': 'MetaTrader 4, MetaTrader 5, Exness Terminal, Mobile App',
        'exec': 'Instant & Market Execution (Volume over $4 Trillion/month)',
        'spread': 'From 0.0 pips (Raw Spread & Zero Accounts)'
    },
    'etoro': {
        'name': 'eToro',
        'corp': 'eToro (Europe) Ltd (Cyprus)<br>eToro (UK) Ltd (United Kingdom)<br>eToro AUS Capital Limited (Australia)<br>eToro USA LLC (United States)',
        'reg': 'FCA (UK) - License: 583263<br>CySEC (Cyprus) - License: 109/10<br>ASIC (Australia) - License: 491139<br>FINRA & FinCEN (USA)',
        'fund': 'Segregated Accounts, Insurance up to 1 Million EUR/AUD',
        'age': 'Registered in 2007 (19 Years Old)',
        'dep': '$50 - $100 depending on country',
        'lev': '1:30 (Retail) / Up to 1:400 (Professional)',
        'plat': 'eToro Web Platform, eToro Mobile App (CopyTrader)',
        'exec': 'Market Execution with Copy Trading engine',
        'spread': '1.0 pip on EUR/USD, 0% Commission on Real Stocks'
    },
    'plus500': {
        'name': 'Plus500',
        'corp': 'Plus500UK Ltd (United Kingdom)<br>Plus500CY Ltd (Cyprus)<br>Plus500AU Pty Ltd (Australia)',
        'reg': 'FCA (UK) - License: 509909<br>CySEC (Cyprus) - License: 250/14<br>ASIC (Australia) - License: 354141<br>Publicly Listed on London Stock Exchange (LSE: PLUS)',
        'fund': 'Segregated Client Accounts, FTSE 250 Listed Financial Transparency',
        'age': 'Registered in 2008 (18 Years Old)',
        'dep': '$100',
        'lev': '1:30 (ESMA / ASIC Retail Limit)',
        'plat': 'Plus500 Proprietary WebTrader, iOS & Android Apps',
        'exec': 'Direct Market Execution with Guaranteed Stop Loss option',
        'spread': 'Dynamic tight spreads, zero trading commissions'
    },
    'avatrade': {
        'name': 'AvaTrade',
        'corp': 'AVA Trade EU Ltd (Ireland)<br>Ava Capital Markets Australia Pty Ltd<br>Ava Trade Japan K.K.',
        'reg': 'CBI (Central Bank of Ireland) - License: C53877<br>ASIC (Australia) - License: 406684<br>FSA (Japan) - License: 1662<br>FSCA (South Africa) - License: 45984',
        'fund': 'Segregated Funds, AvaProtect Loss Protection Mechanism',
        'age': 'Registered in 2006 (20 Years Old)',
        'dep': '$100',
        'lev': '1:30 (EU/AU) / Up to 1:400 (International)',
        'plat': 'MetaTrader 4, MetaTrader 5, AvaTradeGO, AvaOptions',
        'exec': 'Market Execution with Fixed & Floating Spreads',
        'spread': 'From 0.9 pips on EUR/USD'
    }
}

all_files = glob.glob('broker-verifier/**/reviews/*.html', recursive=True) + glob.glob('dating-photo-checker/broker-verifier/**/reviews/*.html', recursive=True)

count = 0
for f_path in set(all_files):
    if not os.path.exists(f_path):
        continue
        
    f_lower = f_path.replace('\\', '/').lower()
    
    broker_key = None
    for b in ['xm', 'exness', 'etoro', 'plus500', 'avatrade']:
        if f'/{b}.html' in f_lower:
            broker_key = b
            break
    if not broker_key:
        continue
        
    lang = 'en'
    for l in ['ro', 'it', 'de', 'es', 'fr', 'pt', 'ru']:
        if f'/{l}/' in f_lower:
            lang = l
            break
            
    if lang == 'en':
        continue
        
    b_info = broker_data[broker_key]
    lbl = t_labels.get(lang, t_labels['en'])
    
    with open(f_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if 'review-table-wrapper' in content:
        continue
        
    tables_html = f'''
            <h2 class="review-section-title">{lbl['reg_profile'].format(broker=b_info['name'])}</h2>
            <div class="review-table-wrapper" style="margin: 1.5rem 0; border-radius: 12px; overflow: hidden; border: 1px solid var(--border-color);">
                <table class="review-table" style="width: 100%; border-collapse: collapse; background: rgba(18, 27, 45, 0.3);">
                    <tr style="border-bottom: 1px solid var(--border-color);">
                        <th style="padding: 1rem 1.2rem; text-align: left; background: rgba(10, 15, 26, 0.6); color: var(--text-main); font-weight: 600; width: 35%;">{lbl['th_corp']}</th>
                        <td style="padding: 1rem 1.2rem; color: var(--text-muted);">{b_info['corp']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--border-color);">
                        <th style="padding: 1rem 1.2rem; text-align: left; background: rgba(10, 15, 26, 0.6); color: var(--text-main); font-weight: 600;">{lbl['th_reg']}</th>
                        <td style="padding: 1rem 1.2rem; color: var(--text-muted);">{b_info['reg']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--border-color);">
                        <th style="padding: 1rem 1.2rem; text-align: left; background: rgba(10, 15, 26, 0.6); color: var(--text-main); font-weight: 600;">{lbl['th_fund']}</th>
                        <td style="padding: 1rem 1.2rem; color: var(--text-muted);">{b_info['fund']}</td>
                    </tr>
                    <tr>
                        <th style="padding: 1rem 1.2rem; text-align: left; background: rgba(10, 15, 26, 0.6); color: var(--text-main); font-weight: 600;">{lbl['th_age']}</th>
                        <td style="padding: 1rem 1.2rem; color: var(--text-muted);">{b_info['age']}</td>
                    </tr>
                </table>
            </div>

            <h2 class="review-section-title">{lbl['trading_cond']}</h2>
            <div class="review-table-wrapper" style="margin: 1.5rem 0 2rem 0; border-radius: 12px; overflow: hidden; border: 1px solid var(--border-color);">
                <table class="review-table" style="width: 100%; border-collapse: collapse; background: rgba(18, 27, 45, 0.3);">
                    <tr style="border-bottom: 1px solid var(--border-color);">
                        <th style="padding: 1rem 1.2rem; text-align: left; background: rgba(10, 15, 26, 0.6); color: var(--text-main); font-weight: 600; width: 35%;">{lbl['th_dep']}</th>
                        <td style="padding: 1rem 1.2rem; color: var(--text-muted);">{b_info['dep']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--border-color);">
                        <th style="padding: 1rem 1.2rem; text-align: left; background: rgba(10, 15, 26, 0.6); color: var(--text-main); font-weight: 600;">{lbl['th_lev']}</th>
                        <td style="padding: 1rem 1.2rem; color: var(--text-muted);">{b_info['lev']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--border-color);">
                        <th style="padding: 1rem 1.2rem; text-align: left; background: rgba(10, 15, 26, 0.6); color: var(--text-main); font-weight: 600;">{lbl['th_plat']}</th>
                        <td style="padding: 1rem 1.2rem; color: var(--text-muted);">{b_info['plat']}</td>
                    </tr>
                    <tr style="border-bottom: 1px solid var(--border-color);">
                        <th style="padding: 1rem 1.2rem; text-align: left; background: rgba(10, 15, 26, 0.6); color: var(--text-main); font-weight: 600;">{lbl['th_exec']}</th>
                        <td style="padding: 1rem 1.2rem; color: var(--text-muted);">{b_info['exec']}</td>
                    </tr>
                    <tr>
                        <th style="padding: 1rem 1.2rem; text-align: left; background: rgba(10, 15, 26, 0.6); color: var(--text-main); font-weight: 600;">{lbl['th_spread']}</th>
                        <td style="padding: 1rem 1.2rem; color: var(--text-muted);">{b_info['spread']}</td>
                    </tr>
                </table>
            </div>'''

    # Insert before <div class="pros-cons-grid"> or before <h2 class="review-section-title">
    if '<div class="pros-cons-grid">' in content:
        parts = content.split('<div class="pros-cons-grid">', 1)
        # Find the last <h2> before pros-cons-grid if it exists, or insert right before pros-cons-grid
        last_h2_idx = parts[0].rfind('<h2 class="review-section-title">')
        if last_h2_idx != -1:
            new_content = parts[0][:last_h2_idx] + tables_html + '\n            ' + parts[0][last_h2_idx:] + '<div class="pros-cons-grid">' + parts[1]
        else:
            new_content = parts[0] + tables_html + '\n            <div class="pros-cons-grid">' + parts[1]
            
        with open(f_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Enriched: {f_path}")
        count += 1

print(f"Total non-English review files enriched: {count}")
