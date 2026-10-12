import re

with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

new_project = """
            <!-- Project: Programmatic SEO Engine & Data Harvester Fleet -->
            <div class="project-item">
                <div class="project-visual" style="position: relative;">
                    <div style="background: url('/seo_fleet_dashboard.webp') no-repeat center center; background-size: 100% 100%; aspect-ratio: 1376 / 768; width: 100%; position: relative; border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.4); background-color: #0f172a;">
                        <!-- Placeholder if image missing -->
                        <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: #10b981; font-size: 4rem; opacity: 0.1;"><i class="fa-solid fa-spider"></i></div>
                    </div>
                    <span class="project-floating-badge" style="position: absolute; top: 12px; right: 12px; background: rgba(10, 15, 29, 0.85); backdrop-filter: blur(8px); -webkit-backdrop-filter: blur(8px); color: #10b981; padding: 5px 12px; border-radius: 20px; font-size: 0.72rem; font-weight: 700; border: 1px solid rgba(16, 185, 129, 0.4); box-shadow: 0 4px 12px rgba(0,0,0,0.5); pointer-events: none; z-index: 2;">🟢 LIVE 8-NODE NETWORK</span>
                </div>
                <div class="project-info">
                    <span class="project-tag" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border-color: rgba(16, 185, 129, 0.3);">Case Study: Extreme Programmatic SEO & Data Pipelines</span>
                    <h3 class="project-name">Programmatic SEO Engine & Data Harvester Fleet (500k+ Pages)</h3>
                    
                    <div class="psr-block">
                        <div class="psr-title psr-problem">❌ The Problem</div>
                        <div class="psr-text">Traditional SEO relies on manual content creation, resulting in slow growth and low domain authority. Generating thousands of targeted, highly-indexed pages in highly competitive financial/security niches is impossible without massive automation and bypassing API limits.</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-solution">⚙️ The Solution</div>
                        <div class="psr-text">Built a decentralized fleet of 8 interconnected Python/FastAPI web platforms (SaaS ecosystem). Integrated completely autonomous Data Harvesters that scrape EU/US regulators (FCA, CySEC, OpenFDA, Abuse.ch) via rotating residential proxies. Engineered a custom <b>Google Indexing API Load-Balancer</b> using dual rotating JSON Service Accounts to forcefully index 400+ new dynamic pages daily while evading quota limits (Status 429).</div>
                    </div>
                    <div class="psr-block">
                        <div class="psr-title psr-result">✅ The Result</div>
                        <div class="psr-text">A zero-maintenance, self-sustaining SEO empire with over 500,000 auto-generated pages successfully injected into Google. Traffic is dynamically geo-routed to premium Prop-Firm affiliate networks or EU brokers based on CFTC-compliance logic.</div>
                    </div>
                    
                    <div class="project-buttons">
                        <a href="#contact" class="btn btn-primary">Build Your Traffic Machine 🚀</a>
                        <a href="https://isbrokersafe.com" class="btn btn-secondary" target="_blank" rel="noopener">View Live Node (IsBrokerSafe) ↗</a>
                    </div>
                </div>
            </div>
"""

insert_target = '            <!-- Project: Enterprise Gmail & Multi-Account SMTP Automation Engine -->'

if insert_target in content:
    content = content.replace(insert_target, new_project + "\n" + insert_target)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Success")
else:
    print("Target not found")
