import os

# Update ro/index.html
ro_file = 'ro/index.html'
if os.path.exists(ro_file):
    with open(ro_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace(
        '<span class="badge-intro">Inginerie de Date & Automatizare</span>',
        '<span class="badge-intro">Full-Stack Architect & Automatizări Complete</span>'
    )
    content = content.replace(
        '<h1 class="hero-title">Automatizare Date Premium & <br><span>Web Scraping Avanzat</span></h1>',
        '<h1 class="hero-title">Dezvoltare Full-Stack SaaS & <br><span>Automatizări de Orice Fel</span></h1>'
    )
    content = content.replace(
        'Ajut companiile B2B și magazinele e-commerce să elimine munca manuală, să monitorizeze prețurile concurenței în timp real și să obțină tablouri de bord executive impecabile.',
        'Dezvolt aplicații web complete, platforme SaaS și automatizez orice proces de business — de la colectare de date stealth și trecere de WAF (Cloudflare/Akamai) la integrări API și tablouri de bord executive.'
    )
    
    with open(ro_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated ro/index.html hero positioning")

# Update it/index.html
it_file = 'it/index.html'
if os.path.exists(it_file):
    with open(it_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = content.replace(
        '<span class="badge-intro">Data Engineering & Automazione</span>',
        '<span class="badge-intro">Full-Stack Architect & Automazioni Complete</span>'
    )
    content = content.replace(
        '<h1 class="hero-title">Automazione Dati Premium & <br><span>Stealth Web Scraping</span></h1>',
        '<h1 class="hero-title">Sviluppo Full-Stack SaaS & <br><span>Automazioni Aziendali</span></h1>'
    )
    
    with open(it_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Updated it/index.html hero positioning")
