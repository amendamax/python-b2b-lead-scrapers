import re

# ROMANIAN
with open("ro/index.html", "r", encoding="utf-8") as f:
    content_ro = f.read()

new_project_ro = """
            <!-- Proiect: Motor de SEO Programatic & Flota Harvester -->
            <div class="project-item">
                <div class="project-visual" style="position: relative;">
                    <div style="background: url('/seo_fleet_dashboard.webp') no-repeat center center; background-size: 100% 100%; aspect-ratio: 1376 / 768; width: 100%; position: relative; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.4); background-color: #0f172a;">
                        <!-- Placeholder if image missing -->
                        <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: #10b981; font-size: 4rem; opacity: 0.1;"><i class="fa-solid fa-spider"></i></div>
                    </div>
                    <span class="project-floating-badge" style="position: absolute; top: 12px; right: 12px; background: rgba(10, 15, 29, 0.85); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); color: #10b981; padding: 5px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.4); box-shadow: 0 4px 12px rgba(0,0,0,0.5); pointer-events: none; z-index: 2;">🟢 REȚEA LIVE (8 NODURI)</span>
                </div>
                <div class="project-info">
                    <span class="project-tag" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border-color: rgba(16, 185, 129, 0.3);">Studiu de Caz: SEO Programatic Extrem & Pipeline de Date</span>
                    <h3 class="project-name">Motor de SEO Programatic & Flotă de Harvestere Date (5M+ Pagini)</h3>
                    
                    <div class="psr-block">
                        <div class="psr-title psr-problem">❌ Problema</div>
                        <div class="psr-text">SEO-ul tradițional se bazează pe scrierea manuală a conținutului, rezultând într-o creștere extrem de lentă. Generarea a mii de pagini indexate în nișe super-competitive (financiar / securitate) este imposibilă fără automatizare masivă și fără a fenta limitările de trafic ale API-urilor.</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-solution">⚙️ Soluția</div>
                        <div class="psr-text">Am construit o flotă descentralizată de 8 platforme web interconectate (FastAPI/Python). Am integrat "Harvestere" complet autonome care extrag liste cu fraude direct de la autorități (FCA, CySEC, FDA, Abuse.ch) prin proxy-uri rezidențiale. Am proiectat un <b>Load-Balancer custom pentru Google Indexing API</b> ce rotește mai multe chei secrete (Service Accounts) pentru a forța indexarea a peste 400 de pagini zilnic, ocolind blocajele de cotă zilnică.</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-result">✅ Rezultatul</div>
                        <div class="psr-text">Un imperiu SEO auto-sustenabil (zero mentenanță umană) care a injectat deja peste 5.000.000 de pagini autogenerate în ecosistemul Google. Traficul organic este rutat dinamic prin Javascript către oferte premium de afiliere, în funcție de geolocalizare (SUA vs Europa).</div>
                    </div>
                    
                    <div class="project-buttons">
                        <a href="#contact" class="btn btn-primary">Construiește Mașina de Trafic 🚀</a>
                        <a href="https://verifydating.net" class="btn btn-secondary" target="_blank" rel="noopener">Vezi Nodul Live (VerifyDating - 5M+ Pagini) ↗</a>
                    </div>
                </div>
            </div>
"""

insert_target_ro = '            <!-- Proiect: Motor Enterprise de Automatizare Gmail & SMTP Multi-Cont -->'
if insert_target_ro in content_ro:
    content_ro = content_ro.replace(insert_target_ro, new_project_ro + "\n" + insert_target_ro)
    with open("ro/index.html", "w", encoding="utf-8") as f:
        f.write(content_ro)
    print("RO Success")


# ITALIAN
with open("it/index.html", "r", encoding="utf-8") as f:
    content_it = f.read()

new_project_it = """
            <!-- Progetto: Motore SEO Programmatico & Flotta Harvester -->
            <div class="project-item">
                <div class="project-visual" style="position: relative;">
                    <div style="background: url('/seo_fleet_dashboard.webp') no-repeat center center; background-size: 100% 100%; aspect-ratio: 1376 / 768; width: 100%; position: relative; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.4); background-color: #0f172a;">
                        <!-- Placeholder if image missing -->
                        <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: #10b981; font-size: 4rem; opacity: 0.1;"><i class="fa-solid fa-spider"></i></div>
                    </div>
                    <span class="project-floating-badge" style="position: absolute; top: 12px; right: 12px; background: rgba(10, 15, 29, 0.85); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); color: #10b981; padding: 5px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.4); box-shadow: 0 4px 12px rgba(0,0,0,0.5); pointer-events: none; z-index: 2;">🟢 RETE LIVE (8 NODI)</span>
                </div>
                <div class="project-info">
                    <span class="project-tag" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border-color: rgba(16, 185, 129, 0.3);">Case Study: SEO Programmatica Estrema & Pipeline di Dati</span>
                    <h3 class="project-name">Motore SEO Programmatico & Flotta di Data Harvesters (5M+ Pagine)</h3>
                    
                    <div class="psr-block">
                        <div class="psr-title psr-problem">❌ Il Problema</div>
                        <div class="psr-text">La SEO tradizionale si basa sulla creazione manuale di contenuti, con conseguente crescita lenta e scarsa autorità. Generare migliaia di pagine indicizzate in nicchie altamente competitive è impossibile senza una massiccia automazione e l'elusione dei limiti API.</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-solution">⚙️ La Soluzione</div>
                        <div class="psr-text">Ho costruito una flotta decentralizzata di 8 piattaforme web (SaaS in Python/FastAPI). Ho integrato Data Harvester completamente autonomi che estraggono dati di frode dalle autorità (FCA, CySEC, FDA, Abuse.ch) tramite proxy residenziali. Ho ingegnerizzato un <b>Load-Balancer per Google Indexing API</b> che utilizza account rotativi (Service Accounts JSON) per forzare l'indicizzazione di oltre 400 nuove pagine al giorno eludendo i blocchi (Status 429).</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-result">✅ Il Risultato</div>
                        <div class="psr-text">Un impero SEO autosufficiente (zero manutenzione) con oltre 5.000.000 di pagine auto-generate iniettate con successo in Google. Il traffico organico viene reindirizzato dinamicamente in base alla geolocalizzazione verso reti di affiliazione premium.</div>
                    </div>
                    
                    <div class="project-buttons">
                        <a href="#contact" class="btn btn-primary">Costruisci il tuo Motore di Traffico 🚀</a>
                        <a href="https://verifydating.net" class="btn btn-secondary" target="_blank" rel="noopener">Vedi Nodo Live (VerifyDating - 5M+ Pagine) ↗</a>
                    </div>
                </div>
            </div>
"""

insert_target_it = '            <!-- Progetto: Motore Enterprise di Automazione Gmail & SMTP Multi-Account -->'
if insert_target_it in content_it:
    content_it = content_it.replace(insert_target_it, new_project_it + "\n" + insert_target_it)
    with open("it/index.html", "w", encoding="utf-8") as f:
        f.write(content_it)
    print("IT Success")

