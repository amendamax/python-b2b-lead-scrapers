import os

# Update Romanian page ro/index.html
ro_path = 'ro/index.html'
if os.path.exists(ro_path):
    with open(ro_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Hero section
    ro_hero = """            <div class="hero-content">
                <span class="badge-intro">Full-Stack Architect & Automatizări Complete</span>
                <h1 class="hero-title">Dezvoltare Full-Stack SaaS & <br><span>Automatizări de Orice Fel</span></h1>
                <p class="hero-description">
                    Dezvolt aplicații web complete, platforme SaaS cu rată mare de conversie și automatizez orice flux de business — de la colectare de date stealth și trecere de WAF (Cloudflare/Akamai) la integrări API în cloud și tablouri de bord executive.
                </p>
                <div class="cta-group">
                    <a href="#projects" class="btn btn-primary">Vezi Platformele SaaS & Proiectele ↗</a>
                    <a href="#contact" class="btn btn-secondary">Discută Proiectul Tău 📨</a>
                </div>
            </div>
            <div class="hero-terminal">
                <div class="terminal-header">
                    <div class="terminal-buttons">
                        <span class="t-btn t-close"></span>
                        <span class="t-btn t-minimize"></span>
                        <span class="t-btn t-maximize"></span>
                    </div>
                    <div class="terminal-title">fullstack_automation_engine.py — activ</div>
                </div>
                <div class="terminal-body" id="terminal-console"></div>
            </div>"""

    # Replace hero container content
    start_hero = html.find('<div class="hero-content">')
    end_hero = html.find('</div>\n        </div>\n    </section>', start_hero)
    if start_hero != -1 and end_hero != -1:
        html = html[:start_hero] + ro_hero + html[end_hero:]

    # 2. Capabilities Section
    ro_caps = """    <!-- Capabilities Section -->
    <section id="capabilities">
        <div class="section-header">
            <span class="section-subtitle">Ce Ofer</span>
            <h2 class="section-title">Inginerie Full-Stack & Automatizări Universale</h2>
            <p class="section-desc">Dezvolt soluții software cap-coadă, aplicații web moderne și fluxuri automatizate de date pentru companii din întreaga lume.</p>
        </div>
        <div class="capabilities-grid">
            <div class="cap-card">
                <span class="cap-icon">🚀</span>
                <h3 class="cap-title">Full-Stack SaaS & Aplicații Web</h3>
                <p class="cap-text">Construiesc aplicații web complete de la zero folosind FastAPI, Python, design UI/UX modern, integrări de plăți Stripe/PayPal și deployment 24/7 în cloud.</p>
            </div>
            <div class="cap-card">
                <span class="cap-icon">⚙️</span>
                <h3 class="cap-title">Automatizări de Business Universale</h3>
                <p class="cap-text">Automatizez orice proces operațional repetitiv, integrare API personalizată, pipeline de generare de lead-uri sau sincronizare de date în timp real pentru a elimina munca manuală.</p>
            </div>
            <div class="cap-card">
                <span class="cap-icon">🛡️</span>
                <h3 class="cap-title">Stealth Web Scraping & Bypass WAF</h3>
                <p class="cap-text">Utilizez amprentarea criptografică TLS pentru a simula comportamentul real al browser-ului, trecând de bariere de securitate precum Cloudflare, Akamai și PerimeterX fără blocaje.</p>
            </div>
            <div class="cap-card">
                <span class="cap-icon">📊</span>
                <h3 class="cap-title">Tablouri de Bord Executive & Analytics</h3>
                <p class="cap-text">Înlocuiesc fișierele CSV neorganizate cu rapoarte Excel impecabile, cu formule interactive, grafice integrate și sincronizare în timp real cu baze de date în cloud.</p>
            </div>
        </div>
    </section>"""

    start_cap = html.find('<!-- Capabilities Section -->')
    end_cap = html.find('</section>', start_cap) + len('</section>')
    if start_cap != -1 and end_cap != -1:
        html = html[:start_cap] + ro_caps + html[end_cap:]

    # 3. Projects Section Header & Projects
    ro_projects_prefix = """    <!-- Projects Section -->
    <section id="projects">
        <div class="section-header">
            <span class="section-subtitle">Portofoliu</span>
            <h2 class="section-title">Platforme SaaS Live & Proiecte de Top</h2>
            <p class="section-desc">Explorează aplicațiile SaaS active în producție și sistemele mele automatizate de date.</p>
        </div>

        <div class="projects-list">
            <!-- Live SaaS Project 1: VerifyDating.net -->
            <div class="project-item">
                <div class="project-visual">
                    <div style="background: linear-gradient(135deg, #180e29 0%, #09070f 100%); height: 350px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; border-radius: 12px; border: 1px solid rgba(255, 42, 116, 0.3);">
                        <span style="font-size: 4.5rem;">💖</span>
                        <span style="background: rgba(255,42,116,0.15); color: #ff2a74; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; margin-top: 10px; border: 1px solid rgba(255,42,116,0.3);">🟢 PLATFORMĂ SAAS LIVE</span>
                        
                    </div>
                </div>
                <div class="project-info">
                    <span class="project-tag" style="background: rgba(255,42,116,0.15); color: #ff2a74; border-color: rgba(255,42,116,0.3);">Studiu de Caz: SaaS Full-Stack AI & Securitate Cibernetică</span>
                    <h3 class="project-name">VerifyDating.net — Platformă AI de Audit Facial & Siguranță</h3>
                    
                    <div class="psr-block">
                        <div class="psr-title psr-problem">❌ Problemă</div>
                        <div class="psr-text">Peste 1 din 7 profiluri de pe aplicațiile de dating este fals sau romance scam, generând pierderi de peste $1.3 Miliarde anual.</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-solution">⚙️ Soluție</div>
                        <div class="psr-text">Am proiectat și lansat o platformă SaaS full-stack cu recunoaștere facială AI, audit domenii WHOIS, căutare inversă pe rețele sociale și monetizare automată prin Stripe.</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-result">✅ Rezultat</div>
                        <div class="psr-text">Backend automatizat 24/7 în cloud cu 99.2% acuratețe biometrică, viteză sub o secundă, integrare GA4 și 8 limbi localizate.</div>
                    </div>
                    
                    <div class="project-buttons">
                        <a href="https://verifydating.net/ro/" class="btn btn-primary" target="_blank" rel="noopener">Vizitează Site-ul Live 🌐</a>
                        <a href="https://verifydating.net/admin?token=verifydating_secret_2026" class="btn btn-secondary" target="_blank" rel="noopener">Vezi Panoul Admin 🛡️</a>
                    </div>
                </div>
            </div>

            <!-- Live SaaS Project 2: IsBrokerSafe.com -->
            <div class="project-item">
                <div class="project-visual">
                    <div style="background: linear-gradient(135deg, #0b172a 0%, #050914 100%); height: 350px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.3);">
                        <span style="font-size: 4.5rem;">📈</span>
                        <span style="background: rgba(56,189,248,0.15); color: #38bdf8; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; margin-top: 10px; border: 1px solid rgba(56,189,248,0.3);">🟢 PLATFORMĂ SAAS LIVE</span>
                        
                    </div>
                </div>
                <div class="project-info">
                    <span class="project-tag" style="background: rgba(56,189,248,0.15); color: #38bdf8; border-color: rgba(56,189,248,0.3);">Studiu de Caz: Securitate Financiară & Audit de Reglementare</span>
                    <h3 class="project-name">IsBrokerSafe.com — Motor de Securitate Financiară</h3>
                    
                    <div class="psr-block">
                        <div class="psr-title psr-problem">❌ Problemă</div>
                        <div class="psr-text">Traderii individuali își pierd economiile în brokeri nereglementați din paradisuri fiscale care funcționează fără licențe financiare valabile.</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-solution">⚙️ Soluție</div>
                        <div class="psr-text">Am dezvoltat un parser în timp real pentru registrele FCA, ASIC, CySEC și SEC, cu audit WHOIS și generare automată de rapoarte PDF de risc.</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-result">✅ Rezultat</div>
                        <div class="psr-text">Portal de securitate financiară cu rată mare de conversie, ticker live de căutări, monetizare prin afiliere și campanie activă Google Ads.</div>
                    </div>
                    
                    <div class="project-buttons">
                        <a href="https://isbrokersafe.com/ro/" class="btn btn-primary" target="_blank" rel="noopener">Vizitează Site-ul Live 🌐</a>
                        <a href="https://isbrokersafe.com/" class="btn btn-secondary" target="_blank" rel="noopener">Versiunea Engleză 🇬🇧</a>
                    </div>
                </div>
            </div>"""

    start_proj = html.find('<!-- Projects Section -->')
    target_item = html.find('<!-- Project 1: Amazon Scraper -->', start_proj)
    if start_proj != -1 and target_item != -1:
        html = html[:start_proj] + ro_projects_prefix + "\n            " + html[target_item:]

    with open(ro_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully updated ro/index.html!")

# Update Italian page it/index.html
it_path = 'it/index.html'
if os.path.exists(it_path):
    with open(it_path, 'r', encoding='utf-8') as f:
        html = f.read()

    it_hero = """            <div class="hero-content">
                <span class="badge-intro">Full-Stack Architect & Automazioni Complete</span>
                <h1 class="hero-title">Sviluppo Full-Stack SaaS & <br><span>Automazioni Aziendali</span></h1>
                <p class="hero-description">
                    Sviluppo applicazioni web complete e piattaforme SaaS ad alta conversione, automatizzando qualsiasi flusso aziendale — dallo stealth web scraping al bypass di WAF (Cloudflare/Akamai) fino a integrazioni API e dashboard executive.
                </p>
                <div class="cta-group">
                    <a href="#projects" class="btn btn-primary">Vedi Piattaforme SaaS & Progetti ↗</a>
                    <a href="#contact" class="btn btn-secondary">Discuti il Tuo Progetto 📨</a>
                </div>
            </div>
            <div class="hero-terminal">
                <div class="terminal-header">
                    <div class="terminal-buttons">
                        <span class="t-btn t-close"></span>
                        <span class="t-btn t-minimize"></span>
                        <span class="t-btn t-maximize"></span>
                    </div>
                    <div class="terminal-title">fullstack_automation_engine.py — attivo</div>
                </div>
                <div class="terminal-body" id="terminal-console"></div>
            </div>"""

    start_hero = html.find('<div class="hero-content">')
    end_hero = html.find('</div>\n        </div>\n    </section>', start_hero)
    if start_hero != -1 and end_hero != -1:
        html = html[:start_hero] + it_hero + html[end_hero:]

    it_caps = """    <!-- Capabilities Section -->
    <section id="capabilities">
        <div class="section-header">
            <span class="section-subtitle">Cosa Offro</span>
            <h2 class="section-title">Ingegneria Full-Stack & Automazioni Universali</h2>
            <p class="section-desc">Creo soluzioni software complete, moderne applicazioni web e pipeline di dati automatizzate per aziende in tutto il mondo.</p>
        </div>
        <div class="capabilities-grid">
            <div class="cap-card">
                <span class="cap-icon">🚀</span>
                <h3 class="cap-title">Full-Stack SaaS & App Web</h3>
                <p class="cap-text">Progetto e sviluppo applicazioni web complete da zero usando FastAPI, Python, UI/UX moderno, pagamenti Stripe/PayPal e deployment cloud 24/7.</p>
            </div>
            <div class="cap-card">
                <span class="cap-icon">⚙️</span>
                <h3 class="cap-title">Automazione Aziendale Universale</h3>
                <p class="cap-text">Automatizzo qualsiasi flusso operativo ripetitivo, integrazione API personalizzata, pipeline di lead generation o sincronizzazione dati in tempo reale per eliminare il lavoro manuale.</p>
            </div>
            <div class="cap-card">
                <span class="cap-icon">🛡️</span>
                <h3 class="cap-title">Stealth Web Scraping & Bypass WAF</h3>
                <p class="cap-text">Utilizzo l'impronta crittografica TLS per simulare il comportamento reale dei browser, superando le barriere di sicurezza come Cloudflare, Akamai e PerimeterX senza blocchi.</p>
            </div>
            <div class="cap-card">
                <span class="cap-icon">📊</span>
                <h3 class="cap-title">Dashboard Executive & Analytics</h3>
                <p class="cap-text">Sostituisco i disordinati file CSV con report Excel perfetti con formule interattive, grafici integrati e sincronizzazione in tempo reale con database cloud.</p>
            </div>
        </div>
    </section>"""

    start_cap = html.find('<!-- Capabilities Section -->')
    end_cap = html.find('</section>', start_cap) + len('</section>')
    if start_cap != -1 and end_cap != -1:
        html = html[:start_cap] + it_caps + html[end_cap:]

    it_projects_prefix = """    <!-- Projects Section -->
    <section id="projects">
        <div class="section-header">
            <span class="section-subtitle">Portfolio</span>
            <h2 class="section-title">Piattaforme SaaS Live & Progetti d'Elite</h2>
            <p class="section-desc">Esplora le mie applicazioni SaaS attive in produzione e i miei sistemi di automazione dati.</p>
        </div>

        <div class="projects-list">
            <!-- Live SaaS Project 1: VerifyDating.net -->
            <div class="project-item">
                <div class="project-visual">
                    <div style="background: linear-gradient(135deg, #180e29 0%, #09070f 100%); height: 350px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; border-radius: 12px; border: 1px solid rgba(255, 42, 116, 0.3);">
                        <span style="font-size: 4.5rem;">💖</span>
                        <span style="background: rgba(255,42,116,0.15); color: #ff2a74; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; margin-top: 10px; border: 1px solid rgba(255,42,116,0.3);">🟢 PIATTAFORMA SAAS LIVE</span>
                        
                    </div>
                </div>
                <div class="project-info">
                    <span class="project-tag" style="background: rgba(255,42,116,0.15); color: #ff2a74; border-color: rgba(255,42,116,0.3);">Caso di Studio: SaaS Full-Stack AI & Cybersicurezza</span>
                    <h3 class="project-name">VerifyDating.net — Piattaforma AI di Audit Facciale</h3>
                    
                    <div class="psr-block">
                        <div class="psr-title psr-problem">❌ Problema</div>
                        <div class="psr-text">Oltre 1 profilo su 7 sulle app di incontri è falso o gestito da truffatori, con perdite annuali superiori a 1,3 miliardi di dollari.</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-solution">⚙️ Soluzione</div>
                        <div class="psr-text">Ho progettato e lanciato una piattaforma SaaS full-stack con riconoscimento facciale AI, audit domini WHOIS, ricerca inversa sui social e monetizzazione automatica Stripe.</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-result">✅ Risultato</div>
                        <div class="psr-text">Backend cloud automatizzato 24/7 con il 99.2% di accuratezza biometrica, latenza inferiore al secondo, integrazione GA4 e 8 lingue localizzate.</div>
                    </div>
                    
                    <div class="project-buttons">
                        <a href="https://verifydating.net/it/" class="btn btn-primary" target="_blank" rel="noopener">Visita il Sito Live 🌐</a>
                        <a href="https://verifydating.net/admin?token=verifydating_secret_2026" class="btn btn-secondary" target="_blank" rel="noopener">Vedi Pannello Admin 🛡️</a>
                    </div>
                </div>
            </div>

            <!-- Live SaaS Project 2: IsBrokerSafe.com -->
            <div class="project-item">
                <div class="project-visual">
                    <div style="background: linear-gradient(135deg, #0b172a 0%, #050914 100%); height: 350px; display: flex; flex-direction: column; align-items: center; justify-content: center; position: relative; border-radius: 12px; border: 1px solid rgba(56, 189, 248, 0.3);">
                        <span style="font-size: 4.5rem;">📈</span>
                        <span style="background: rgba(56,189,248,0.15); color: #38bdf8; padding: 4px 12px; border-radius: 20px; font-size: 0.75rem; font-weight: 700; margin-top: 10px; border: 1px solid rgba(56,189,248,0.3);">🟢 PIATTAFORMA SAAS LIVE</span>
                        
                    </div>
                </div>
                <div class="project-info">
                    <span class="project-tag" style="background: rgba(56,189,248,0.15); color: #38bdf8; border-color: rgba(56,189,248,0.3);">Caso di Studio: Sicurezza Finanziaria & Audit Regolatorio</span>
                    <h3 class="project-name">IsBrokerSafe.com — Motore di Intelligence Finanziaria</h3>
                    
                    <div class="psr-block">
                        <div class="psr-title psr-problem">❌ Problema</div>
                        <div class="psr-text">I trader al dettaglio perdono i propri risparmi con broker forex, CFD e crypto non regolamentati operanti da paradisi fiscali.</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-solution">⚙️ Soluzione</div>
                        <div class="psr-text">Ho creato un parser in tempo reale dei registri FCA, ASIC, CySEC e SEC con audit WHOIS e generazione automatica di report PDF di rischio.</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-result">✅ Risultato</div>
                        <div class="psr-text">Portale di sicurezza finanziaria ad alta conversione con ticker di ricerca live, monetizzazione affiliata e campagna Google Ads attiva.</div>
                    </div>
                    
                    <div class="project-buttons">
                        <a href="https://isbrokersafe.com/it/" class="btn btn-primary" target="_blank" rel="noopener">Visita il Sito Live 🌐</a>
                        <a href="https://isbrokersafe.com/" class="btn btn-secondary" target="_blank" rel="noopener">Versione Inglese 🇬🇧</a>
                    </div>
                </div>
            </div>"""

    start_proj = html.find('<!-- Projects Section -->')
    target_item = html.find('<!-- Project 1: Amazon Scraper -->', start_proj)
    if start_proj != -1 and target_item != -1:
        html = html[:start_proj] + it_projects_prefix + "\n            " + html[target_item:]

    with open(it_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print("Successfully updated it/index.html!")
