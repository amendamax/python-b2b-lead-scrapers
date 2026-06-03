import os
import urllib.parse
import openpyxl

def get_leads_from_excel(file_path, niche):
    if not os.path.exists(file_path):
        return []
    
    wb = openpyxl.load_workbook(file_path)
    ws = wb.active
    leads = []
    
    # Read rows starting from row 2 (skipping header)
    for row in range(2, ws.max_row + 1):
        name = ws.cell(row=row, column=1).value
        # If row is empty, skip
        if not name:
            continue
        
        category = ws.cell(row=row, column=2).value
        address = ws.cell(row=row, column=3).value
        # Reconstruct website URL from hyperlink if possible
        cell_web = ws.cell(row=row, column=4)
        website = cell_web.hyperlink.target if cell_web.hyperlink else cell_web.value
        phone = ws.cell(row=row, column=5).value
        owner = ws.cell(row=row, column=6).value
        email = ws.cell(row=row, column=7).value
        
        # Deduce city and country dynamically
        file_name_lower = os.path.basename(file_path).lower()
        if "torino" in file_name_lower:
            city = "Torino"
            country = "italy"
        elif "milano" in file_name_lower:
            city = "Milano"
            country = "italy"
        elif "bucuresti" in file_name_lower:
            city = "București"
            country = "romania"
        elif "london" in file_name_lower:
            city = "London"
            country = "uk"
        elif "new york" in file_name_lower:
            city = "New York"
            country = "usa"
        else:
            city = "Global"
            country = "usa"
        
        leads.append({
            "company_name": name,
            "niche": niche,
            "city": city,
            "country": country,
            "website": website,
            "phone": phone,
            "owner": owner,
            "email": email
        })
    return leads

def get_templates():
    # Real estate
    re_it_subject = "Automazione dati e reportistica Excel premium per il vostro business"
    re_it_body = """Gentile {owner},

Spero che questa email vi trovi bene.

Sono Vasile Bratu, uno sviluppatore Python senior specializzato in automazione dati e web scraping, residente a Garessio (Cuneo).

Ho analizzato attentamente il settore immobiliare nella zona di {city} e ho notato come la raccolta manuale dei dati di mercato, il monitoraggio degli annunci pubblicati direttamente dai proprietari ("privati") o il caricamento delle schede immobiliari richieda spesso molte ore preziose ogni settimana per il team di {company_name}.

Aiuto le agenzie immobiliari a risparmiare tempo e a battere la concorrenza sul tempo automatizzando questi processi. Nello specifico, posso creare per voi:
1. Estrattori automatici in tempo reale: Per essere sempre i primi a sapere quando un proprietario pubblica un nuovo annuncio sui portali.
2. Dashboard Excel di livello Executive: Report ordinati e spaziosi con formule di hyperlink cliccabili per accedere direttamente agli annunci e alle foto con un solo clic.
3. Sincronizzazione Cloud automatica: Integrazione diretta e sicura con il vostro CRM aziendale o Google Sheets.

Potete visionare una demo dei miei report premium e i miei progetti open-source sul mio portfolio GitHub qui:
👉 https://github.com/amendamax/python-b2b-lead-scrapers

La mia proposta per voi:
Sarei felice di creare per voi o per il vostro team una demo gratuita con 5 annunci reali della zona di {city}, formattati nel mio database premium, così potrete valutare voi stessi l'utilità del sistema senza alcun impegno.

Fatemi sapere se può interessarvi e quale zona preferite per la demo!

Cordiali saluti,

Vasile Bratu
Senior Python & Data Automation Engineer
amendamax@vasiledev.com
GitHub Portfolio: https://github.com/amendamax"""

    re_ro_subject = "Automatizare date si rapoarte Excel inteligente pentru afacerea dumneavoastra"
    re_ro_body = """Buna ziua {owner},

Numele meu este Vasile Bratu si sunt inginer software senior specializat in automatizari de date, web scraping si raportare de business.

Daca echipa dumneavoastra de la {company_name} pierde timp pretios in fiecare zi cu monitorizarea manuala a pietei imobiliare, copierea anunturilor noi postate de proprietari pe diverse portaluri sau curatarea listelor de prospecti din {city}, va pot ajuta sa eliminati complet aceasta munca manuala prin construirea unui pipeline de date automat.

Iata ce pot implementa pentru afacerea dumneavoastra:
1. Scrapere de date in timp real: Extragere automata a anunturilor noi din portalurile imobiliare relevante, direct in secunda in care apar.
2. Rapoarte Excel premium (Executive Dashboards): Livrarea datelor in tabele extrem de aerisite si organizate, cu formule di hyperlink active pentru o navigare extrem de rapida.
3. Sincronizare Cloud: Integrare automata directa in CRM-ul agentiei dumneavoastra sau in Google Sheets.

Puteti analiza o mostra a calitatii muncii mele si a codului meu pe portofoliul meu GitHub:
👉 https://github.com/amendamax/python-b2b-lead-scrapers

Propunerea mea gratuita:
Pentru a va convinge de utilitatea sistemului, sunt bucuros sa realizez un test gratuit cu 5 anunturi reale/date extrase din {city}, formatate in raportul meu premium, fara nicio obligatie din partea dumneavoastra.

Daca vi se pare interesant, va rog sa imi spuneti ce oras/zona va intereseaza pentru testul gratuit!

Cu stima,

Vasile Bratu
Senior Python & Data Automation Engineer
amendamax@vasiledev.com
GitHub Portfolio: https://github.com/amendamax"""

    # E-commerce
    eco_it_subject = "Monitoraggio automatico dei prezzi concorrenti per il vostro e-commerce"
    eco_it_body = """Gentile {owner},

Spero che questa email vi trovi bene.

Sono Vasile Bratu, uno sviluppatore Python senior specializzato in automazione dati e price scraping per e-commerce, residente a Garessio (Cuneo).

Ho analizzato il vostro negozio online {company_name} e ho notato quanto sia cruciale oggi monitorare in tempo reale i prezzi dei concorrenti (su Amazon, eBay o siti web rivali) per rimanere competitivi ed evitare perdite di margine.

Aiuto gli e-commerce di medie dimensioni ad automatizzare il monitoraggio dei prezzi e l'analisi dei cataloghi. Nello specifico, posso creare per voi:
1. Scraping dei prezzi della concorrenza: Monitoraggio automatico e giornaliero dei listini dei vostri concorrenti.
2. Executive Price Dashboard: Report Excel ordinati ed eleganti (in formato "Midnight Gold") con variazioni percentuali, grafici e link rapidi ai prodotti.
3. Riconciliazione automatica nel vostro store: Sincronizzazione dei dati direttamente su Shopify, WooCommerce o Google Sheets.

Potete visionare una demo dei miei report premium e i miei progetti open-source sul mio portfolio GitHub qui:
👉 https://github.com/amendamax/python-b2b-lead-scrapers

La mia proposta:
Sarei felice di creare una demo gratuita con il monitoraggio in tempo reale di 5 prodotti della concorrenza a vostra scelta, senza alcun impegno.

Fatemi sapere se può interessarvi!

Cordiali saluti,

Vasile Bratu
Senior Python & Data Automation Engineer
amendamax@vasiledev.com
GitHub Portfolio: https://github.com/amendamax"""

    eco_ro_subject = "Monitorizare automata preturi concurenta pentru e-commerce"
    eco_ro_body = """Buna ziua {owner},

Numele meu este Vasile Bratu si sunt inginer software senior specializat in automatizari de date si price scraping pentru magazine online.

Daca echipa dumneavoastra de la {company_name} pierde timp pretios in fiecare zi cu monitorizarea manuala a preturilor concurentilor pe diverse site-uri sau pe platforme de tip marketplace, va pot ajuta sa eliminati complet aceasta munca manuala.

Iata ce pot implementa pentru magazinul dumneavoastra online:
1. Scrapere de preturi in timp real: Urmarirea automata a schimbarilor de pret de pe site-urile concurente sau marketplace-uri.
2. Rapoarte Excel premium (Midnight Gold Dashboards): Tabele aerisite si organizate cu semnalari vizuale pentru oportunitatile de crestere a pretului sau reduceri de pret necesare.
3. Sincronizare automata: Integrare directa in platforma dumneavoastra e-commerce (Shopify/WooCommerce) sau in Google Sheets.

Puteti analiza o mostra a calitatii muncii mele si a codului meu pe portofoliul meu GitHub:
👉 https://github.com/amendamax/python-b2b-lead-scrapers

Propunerea mea gratuita:
Sunt bucuros sa realizez un test gratuit cu monitorizarea automata a 5 produse din magazinul dumneavoastra in raport cu concurenta, fara nicio obligatie.

Daca vi se pare interesant, va rog sa imi spuneti ce produse doriti sa monitorizam!

Cu stima,

Vasile Bratu
Senior Python & Data Automation Engineer
amendamax@vasiledev.com
GitHub Portfolio: https://github.com/amendamax"""

    # English Real Estate template
    re_en_subject = "Automating your property data pipeline & custom Excel reporting"
    re_en_body = """Hi {owner},

I hope this email finds you well.

I'm Vasile Bratu, a Senior Python & Data Automation Engineer specializing in web scraping, API integration, and executive-ready reporting dashboards.

I analyzed the real estate market in your area and noticed how much manual time teams at {company_name} spend copy-pasting property listings, monitoring private seller ads, or updating internal listings in {city}.

I help real estate agencies save time and beat competitors by automating these workflows. Specifically, I can build for you:
1. Real-time property scrapers: To be the first to know when a private owner lists a new property.
2. Executive Excel Dashboards: Spacious, beautiful reports (Midnight Gold & Forest Green) with active, clickable hyperlink formulas for one-click access.
3. CRM Sync: Real-time synchronization directly into Google Sheets, HubSpot, or Salesforce APIs.

Additionally, I recently published a technical breakdown on Dev.to about FinTech, API integration, and VPS automated risk control, which demonstrates my approach to high-performance and resilient systems engineering:
👉 https://dev.to/amendamax2025/fintech-algorithmic-risk-control-how-vps-automation-and-api-integration-protect-capital-and-25c8

You can review my open-source code and portfolio repositories on GitHub:
👉 https://github.com/amendamax/python-b2b-lead-scrapers

My risk-free offer:
I am ready to perform a 5-lead free trial targeting your preferred area formatted in my premium report so you can evaluate the speed and quality firsthand.

Let me know if this sounds interesting!

Best regards,

Vasile Bratu
Senior Python & Data Automation Engineer
amendamax@vasiledev.com
GitHub Portfolio: https://github.com/amendamax"""

    # English E-commerce template
    eco_en_subject = "Automating your competitor price monitoring & e-commerce reporting"
    eco_en_body = """Hi {owner},

I hope this email finds you well.

I'm Vasile Bratu, a Senior Python & Data Automation Engineer specializing in web scraping, API integration, and competitor price tracking for e-commerce stores.

I analyzed your online store {company_name} and noticed how crucial real-time competitor price monitoring (on Amazon, eBay, or direct competitor sites) is today to stay competitive and protect your margins.

I help e-commerce brands automate price tracking and catalog analysis. Specifically, I can build for you:
1. High-Performance Competitor Price Scraping: Automated daily tracking of your competitors' prices.
2. Executive Price Dashboards: Breathtaking reports (Midnight Gold & Forest Green) with percentage variations, price history charts, and direct product links.
3. CRM/Store Sync: Real-time synchronization directly into Shopify, WooCommerce, or Google Sheets.

Additionally, I recently published a detailed technical guide on Dev.to regarding ethical web scraping and GDPR compliance, which ensures your data operations are 100% legally and technically secure:
👉 https://dev.to/amendamax2025/ethical-web-scraping-gdpr-how-enterprises-extract-public-web-data-with-absolute-legal--1fb9

You can review my open-source code and portfolio repositories on GitHub:
👉 https://github.com/amendamax/python-b2b-lead-scrapers

My risk-free offer:
I am ready to perform a 5-product free competitor price tracking trial for you so you can see the results firsthand.

Let me know if this sounds interesting!

Best regards,

Vasile Bratu
Senior Python & Data Automation Engineer
amendamax@vasiledev.com
GitHub Portfolio: https://github.com/amendamax"""

    return {
        "Imobiliare": {
            "italy": (re_it_subject, re_it_body),
            "romania": (re_ro_subject, re_ro_body),
            "usa": (re_en_subject, re_en_body),
            "uk": (re_en_subject, re_en_body)
        },
        "E-commerce": {
            "italy": (eco_it_subject, eco_it_body),
            "romania": (eco_ro_subject, eco_ro_body),
            "usa": (eco_en_subject, eco_en_body),
            "uk": (eco_en_subject, eco_en_body)
        }
    }

def main():
    workspace_dir = r"C:\Users\bratu\Documents\antigravity\amazing-borg"
    
    # Gather all leads dynamically using glob
    import glob
    leads = []
    excel_files = glob.glob(os.path.join(workspace_dir, "leads_*.xlsx"))
    for file_path in excel_files:
        filename = os.path.basename(file_path).lower()
        if "ecommerce" in filename:
            niche_type = "E-commerce"
        else:
            niche_type = "Imobiliare"
        leads.extend(get_leads_from_excel(file_path, niche_type))
    
    if not leads:
        print("No leads found in Excel sheets!")
        return
        
    templates = get_templates()
    
    # Generate HTML content
    html_content = """<!DOCTYPE html>
<html lang="ro">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Lansare Outreach B2B - Vasile Bratu</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid #1e293b;
        }
        h1 {
            color: #38bdf8;
            margin-bottom: 5px;
            font-size: 2.5em;
        }
        p.subtitle {
            color: #94a3b8;
            font-size: 1.1em;
            margin-top: 5px;
        }
        .stats {
            display: flex;
            justify-content: space-around;
            margin: 30px 0;
            background: rgba(30, 41, 59, 0.5);
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #334155;
        }
        .stat-item {
            text-align: center;
        }
        .stat-val {
            font-size: 1.8em;
            font-weight: bold;
            color: #34d399;
        }
        .stat-lbl {
            color: #94a3b8;
            font-size: 0.9em;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 20px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            border-color: #38bdf8;
        }
        .card-header {
            border-bottom: 1px solid #334155;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .comp-name {
            font-size: 1.2em;
            font-weight: bold;
            color: #f1f5f9;
        }
        .badge {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            margin-top: 5px;
        }
        .badge-it { background-color: #0d9488; color: #f0fdfa; }
        .badge-ro { background-color: #dc2626; color: #fef2f2; }
        .badge-re { background-color: #059669; color: #ecfdf5; }
        .badge-eco { background-color: #d97706; color: #fffbeb; }
        .badge-uk { background-color: #1e3a8a; color: #dbeafe; }
        .badge-usa { background-color: #3b82f6; color: #eff6ff; }
        .details {
            font-size: 0.95em;
            color: #cbd5e1;
            line-height: 1.6;
        }
        .details strong {
            color: #94a3b8;
        }
        .btn {
            display: block;
            text-align: center;
            background-color: #0284c7;
            color: white;
            text-decoration: none;
            padding: 12px;
            border-radius: 8px;
            font-weight: bold;
            margin-top: 20px;
            transition: background-color 0.2s;
        }
        .btn:hover {
            background-color: #0369a1;
        }
        .btn-send {
            background-color: #10b981;
        }
        .btn-send:hover {
            background-color: #059669;
        }
        
        /* Tabs Styling */
        .tabs {
            display: flex;
            justify-content: center;
            margin-bottom: 30px;
            gap: 15px;
        }
        .tab-btn {
            background-color: #1e293b;
            border: 1px solid #334155;
            color: #94a3b8;
            padding: 12px 24px;
            font-size: 1.1em;
            font-weight: bold;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .tab-btn:hover {
            border-color: #38bdf8;
            color: #f1f5f9;
        }
        .tab-btn.active {
            background-color: #0284c7;
            border-color: #38bdf8;
            color: white;
            box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.4);
        }
        .tab-content {
            display: none;
        }
        .tab-content.active-content {
            display: block;
        }
        
        /* Card Actions & Sent State */
        .card-actions {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 15px;
        }
        .btn-sent-toggle {
            background-color: #334155;
            color: #cbd5e1;
            border: 1px solid #475569;
            padding: 8px;
            border-radius: 6px;
            font-size: 0.9em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-sent-toggle:hover {
            background-color: #475569;
            color: white;
        }
        .btn-sent-toggle.btn-sent-active {
            background-color: #065f46;
            border-color: #059669;
            color: #a7f3d0;
        }
        .card.card-sent {
            opacity: 0.45;
            border-color: #1e293b;
            filter: grayscale(40%);
            transition: all 0.3s ease;
        }
        .card.card-sent:hover {
            opacity: 0.85;
            filter: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>✉️ Lansator Outreach B2B Global</h1>
            <p class="subtitle">Selectează o firmă calificată de mai jos pentru a deschide e-mailul pre-formatat cu portofoliul tău</p>
        </header>
        
        <div class="stats">
            <div class="stat-item">
                <div class="stat-val">""" + str(len(leads)) + """</div>
                <div class="stat-lbl">Total Prospecte Calificate</div>
            </div>
            <div class="stat-item">
                <div class="stat-val">""" + str(len([l for l in leads if l["country"] == "italy"])) + """</div>
                <div class="stat-lbl">Italia (IT)</div>
            </div>
            <div class="stat-item">
                <div class="stat-val">""" + str(len([l for l in leads if l["country"] == "romania"])) + """</div>
                <div class="stat-lbl">România (RO)</div>
            </div>
            <div class="stat-item">
                <div class="stat-val">""" + str(len([l for l in leads if l["country"] in ["usa", "uk"]])) + """</div>
                <div class="stat-lbl">Global (EN)</div>
            </div>
            <div class="stat-item">
                <div class="stat-val">""" + str(len([l for l in leads if l["niche"] == "Imobiliare"])) + """</div>
                <div class="stat-lbl">Imobiliare (RE)</div>
            </div>
            <div class="stat-item">
                <div class="stat-val">""" + str(len([l for l in leads if l["niche"] == "E-commerce"])) + """</div>
                <div class="stat-lbl">E-commerce (ECO)</div>
            </div>
        </div>
        
        <!-- Tab Navigation Buttons -->
        <div class="tabs">
            <button class="tab-btn active" onclick="openTab(event, 'italy-tab')">Italia 🇮🇹</button>
            <button class="tab-btn" onclick="openTab(event, 'romania-tab')">România 🇷🇴</button>
            <button class="tab-btn" onclick="openTab(event, 'global-tab')">Internațional 🌐</button>
        </div>
"""
    
    # Partition leads by group
    italy_leads = [l for l in leads if l["country"] == "italy"]
    romania_leads = [l for l in leads if l["country"] == "romania"]
    global_leads = [l for l in leads if l["country"] in ["usa", "uk"]]
    
    def render_leads_group(group_leads):
        group_html = ""
        for l in group_leads:
            subj, body = templates[l["niche"]][l["country"]]
            
            # Handle empty/None owner gracefully
            owner_val = l["owner"]
            if not owner_val or owner_val == "None" or str(owner_val).strip() == "":
                if l["country"] == "italy":
                    owner_val = f"Team di {l['company_name']}"
                else:
                    owner_val = f"Echipa {l['company_name']}"
            
            # Populate template parameters
            formatted_subj = subj
            formatted_body = body.format(
                owner=owner_val,
                city=l["city"],
                company_name=l["company_name"]
            )
            
            # URL encode subject and body for mailto link
            encoded_subj = urllib.parse.quote(formatted_subj)
            # Replace '+' with '%20' if any, though quote uses %20. mailto requires %20 for spaces
            encoded_body = urllib.parse.quote(formatted_body)
            
            # Using standard mailto: link to open the system's default mail client (e.g. Zoho Mail app)
            mail_link = f"mailto:{l['email']}?subject={encoded_subj}&body={encoded_body}"
            if l["country"] == "italy":
                badge_class = "badge-it"
                country_lbl = "Italia 🇮🇹"
            elif l["country"] == "romania":
                badge_class = "badge-ro"
                country_lbl = "România 🇷🇴"
            elif l["country"] == "uk":
                badge_class = "badge-uk"
                country_lbl = "Marea Britanie 🇬🇧"
            else: # usa
                badge_class = "badge-usa"
                country_lbl = "SUA 🇺🇸"
            niche_badge_class = "badge-re" if l["niche"] == "Imobiliare" else "badge-eco"
            
            group_html += f"""
                <div class="card" data-company="{l['company_name']}">
                    <div>
                        <div class="card-header">
                            <div class="comp-name">{l['company_name']}</div>
                            <span class="badge {badge_class}">{country_lbl} - {l['city']}</span>
                            <span class="badge {niche_badge_class}">{l['niche']}</span>
                        </div>
                        <div class="details">
                            <strong>Proprietar / Manager:</strong> {l['owner'] if l['owner'] and l['owner'] != 'None' else 'Echipă / Nespecificat'}<br>
                            <strong>Email:</strong> {l['email']}<br>
                            <strong>Telefon:</strong> {l['phone']}<br>
                            <strong>Site:</strong> <a href="{l['website']}" target="_blank" style="color: #38bdf8; text-decoration: none;">{l['clean_domain'] if 'clean_domain' in l else l['website']} ↗</a>
                        </div>
                    </div>
                    <div class="card-actions">
                        <a href="{mail_link}" class="btn btn-send" onclick="markAutoSent('{l['company_name']}')">Trimite Email ✉️</a>
                        <button class="btn-sent-toggle">Marchează ca Trimis</button>
                    </div>
                </div>
            """
        return group_html

    # Render Italy Tab
    html_content += """
        <div id="italy-tab" class="tab-content active-content">
            <div class="grid">
    """ + render_leads_group(italy_leads) + """
            </div>
        </div>
    """
    
    # Render Romania Tab
    html_content += """
        <div id="romania-tab" class="tab-content">
            <div class="grid">
    """ + render_leads_group(romania_leads) + """
            </div>
        </div>
    """
    
    # Render Global Tab
    html_content += """
        <div id="global-tab" class="tab-content">
            <div class="grid">
    """ + render_leads_group(global_leads) + """
            </div>
        </div>
    """
        
    html_content += """
    </div>
    
    <script>
        // Tab switching logic
        function openTab(evt, tabId) {
            // Hide all tab contents
            const contents = document.querySelectorAll('.tab-content');
            contents.forEach(c => {
                c.classList.remove('active-content');
            });
            
            // Deactivate all tab buttons
            const buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(b => {
                b.classList.remove('active');
            });
            
            // Show selected tab content and active button
            document.getElementById(tabId).classList.add('active-content');
            evt.currentTarget.classList.add('active');
        }
        
        // Auto mark as sent on click (optional but nice)
        function markAutoSent(companyName) {
            const card = document.querySelector(`[data-company="${companyName}"]`);
            if (card) {
                const sentBtn = card.querySelector('.btn-sent-toggle');
                card.classList.add('card-sent');
                if (sentBtn) {
                    sentBtn.classList.add('btn-sent-active');
                    sentBtn.innerHTML = 'Trimis ✔️';
                }
                localStorage.setItem('sent_' + companyName, 'true');
            }
        }
        
        // Persistent Sent Tracking using localStorage
        document.addEventListener("DOMContentLoaded", function() {
            // Auto-deselect recently repaired emails
            const repaired = [
                "Savedbythedress",
                "Flamingoshoptorino",
                "The Realestateagency",
                "Top10Propertyagents",
                "Chestertons",
                "Floridarealtyofmiami",
                "Vestique",
                "Miss Rosier",
                "Erdem"
            ];
            repaired.forEach(comp => {
                localStorage.removeItem("sent_" + comp);
            });

            const cards = document.querySelectorAll(".card");
            
            cards.forEach(card => {
                const companyName = card.getAttribute("data-company");
                const sentBtn = card.querySelector('.btn-sent-toggle');
                
                // Check if already sent in localStorage
                if (localStorage.getItem('sent_' + companyName) === 'true') {
                    card.classList.add('card-sent');
                    if (sentBtn) {
                        sentBtn.classList.add('btn-sent-active');
                        sentBtn.innerHTML = 'Trimis ✔️';
                    }
                }
                
                if (sentBtn) {
                    sentBtn.addEventListener('click', function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        
                        const isSent = card.classList.toggle('card-sent');
                        sentBtn.classList.toggle('btn-sent-active');
                        
                        if (isSent) {
                            sentBtn.innerHTML = 'Trimis ✔️';
                            localStorage.setItem('sent_' + companyName, 'true');
                        } else {
                            sentBtn.innerHTML = 'Marchează ca Trimis';
                            localStorage.removeItem('sent_' + companyName);
                        }
                    });
                }
            });
        });
    </script>
</body>
</html>
"""
    
    # Save the HTML dashboard to Desktop/Outreach_B2B
    outreach_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Outreach_B2B")
    os.makedirs(outreach_dir, exist_ok=True)
    desktop_html = os.path.join(outreach_dir, "TRIMITE_EMAILURI_B2B.html")
    with open(desktop_html, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Interactive outreach dashboard generated successfully at: {desktop_html}")

if __name__ == "__main__":
    main()
