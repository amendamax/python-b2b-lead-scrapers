import os
import re

footer_template = """
    <!-- UNIFIED VASILEDEV ECOSYSTEM FOOTER -->
    <footer class="vasiledev-ecosystem-footer" style="background: #03060a; border-top: 1px solid rgba(255, 255, 255, 0.1); padding: 50px 20px 24px; font-family: 'Inter', system-ui, -apple-system, sans-serif; color: #94a3b8; font-size: 0.85rem; line-height: 1.6; text-align: left; margin-top: 60px;">
        <div style="max-width: 1140px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 36px; margin-bottom: 36px;">
            <div>
                <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                    <span style="display: inline-flex; align-items: center; justify-content: center; width: 34px; height: 34px; border-radius: 8px; background: rgba(56, 189, 248, 0.15); color: #38bdf8; font-size: 16px;">
                        <i class="fa-solid {icon}"></i>
                    </span>
                    <span style="font-family: 'Outfit', sans-serif; font-size: 18px; font-weight: 800; color: #ffffff; letter-spacing: -0.3px;">
                        {name_part1}<strong style="color: #38bdf8;">{name_part2}</strong>
                    </span>
                </div>
                <p style="color: #94a3b8; font-size: 0.85rem; line-height: 1.5; margin: 0 0 12px 0;">
                    {description}
                </p>
                <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                    <span style="background: rgba(16, 185, 129, 0.12); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px;">✔️ VIES Verified EU</span>
                    <span style="background: rgba(56, 189, 248, 0.12); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.3); font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px;">🛡️ 100% Free Public Utility</span>
                </div>
            </div>

            <div>
    <h4 style="font-family: 'Outfit', sans-serif; font-size: 1rem; font-weight: 700; color: #38bdf8; margin: 0 0 14px 0;">VasileDev Group Ecosystem</h4>
    <p style="margin: 0 0 8px 0;"><a href="https://isbrokersafe.com" target="_blank" rel="noopener" style="color: #cbd5e1; font-weight: 400; text-decoration: none;">🏛️ isbrokersafe.com</a></p>
<p style="margin: 0 0 8px 0;"><a href="https://verifydating.net" target="_blank" rel="noopener" style="color: #cbd5e1; font-weight: 400; text-decoration: none;">🛡️ verifydating.net</a></p>
<p style="margin: 0 0 8px 0;"><a href="https://jobscamradar.com" target="_blank" rel="noopener" style="color: #cbd5e1; font-weight: 400; text-decoration: none;">💼 jobscamradar.com</a></p>
<p style="margin: 0 0 8px 0;"><a href="https://pillscamradar.com" target="_blank" rel="noopener" style="color: #cbd5e1; font-weight: 400; text-decoration: none;">💊 pillscamradar.com</a></p>
<p style="margin: 0 0 8px 0;"><a href="https://appscamradar.com" target="_blank" rel="noopener" style="color: #cbd5e1; font-weight: 400; text-decoration: none;">📱 appscamradar.com</a></p>
<p style="margin: 0 0 8px 0;"><a href="https://dreamcarhunt.com" target="_blank" rel="noopener" style="color: #cbd5e1; font-weight: 400; text-decoration: none;">🏎️ dreamcarhunt.com</a></p>
<p style="margin: 0 0 8px 0;"><a href="https://airparkrefund.com" target="_blank" rel="noopener" style="color: #cbd5e1; font-weight: 400; text-decoration: none;">✈️ airparkrefund.com</a></p>
<p style="margin: 0 0 8px 0;"><a href="https://vasiledev.com" target="_blank" rel="noopener" style="color: #cbd5e1; font-weight: 400; text-decoration: none;">👑 vasiledev.com</a></p>
</div>

            <div>
                <h4 style="font-family: 'Outfit', sans-serif; font-size: 1rem; font-weight: 700; color: #38bdf8; margin: 0 0 14px 0;">Official Network</h4>
                <p style="margin: 0 0 8px 0;"><a href="https://isbrokersafe.com" target="_blank" rel="noopener" style="color: {isbroker_color}; font-weight: {isbroker_weight}; text-decoration: none;">🏦 IsBrokerSafe.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://jobscamradar.com" target="_blank" rel="noopener" style="color: {jobscam_color}; font-weight: {jobscam_weight}; text-decoration: none;">🛡️ JobScamRadar.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://pillscamradar.com" target="_blank" rel="noopener" style="color: {pillscam_color}; font-weight: {pillscam_weight}; text-decoration: none;">💊 PillScamRadar.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://verifydating.net" target="_blank" rel="noopener" style="color: {dating_color}; font-weight: {dating_weight}; text-decoration: none;">🛡️ VerifyDating.net</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://appscamradar.com" target="_blank" rel="noopener" style="color: {appscam_color}; font-weight: {appscam_weight}; text-decoration: none;">🐛 AppScamRadar.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://dreamcarhunt.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">🏎️ DreamCarHunt.com</a></p>
                <p style="margin: 0 0 8px 0;"><a href="https://airparkrefund.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">✈️ AirParkRefund.com</a></p>
                <p style="margin: 0;"><a href="https://vasiledev.com" target="_blank" rel="noopener" style="color: #cbd5e1; text-decoration: none;">👑 VasileDev.com</a></p>
            </div>
        </div>

        <div style="max-width: 1140px; margin: 0 auto; border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 20px; text-align: center; font-size: 0.8rem; color: #64748b;">
            <p style="margin: 0;">&copy; 2026 {full_name}™ by VasileDev Group. All rights reserved. Powered globally by Cloudflare Edge Network.</p>
        </div>
    </footer>
"""

sites_config = {
    "app-scam-radar": {
        "icon": "fa-bug", "name_part1": "APPSCAM", "name_part2": "RADAR",
        "description": "Global mobile threat intelligence. Scanning and exposing malicious Android & iOS applications to protect user data.",
        "full_name": "AppScamRadar",
        "active_link": "appscam"
    },
    "pill-scam-radar": {
        "icon": "fa-pills", "name_part1": "PILLSCAM", "name_part2": "RADAR",
        "description": "Healthcare intelligence platform. Detecting fake supplements and FDA-banned dangerous weight-loss & enhancement pills.",
        "full_name": "PillScamRadar",
        "active_link": "pillscam"
    },
    "job-scam-radar": {
        "icon": "fa-briefcase", "name_part1": "JOBSCAM", "name_part2": "RADAR",
        "description": "Employment fraud defense system. Identifying fake recruitment agencies, task scams, and human trafficking operations.",
        "full_name": "JobScamRadar",
        "active_link": "jobscam"
    },
    "dating-photo-checker": {
        "icon": "fa-heart-crack", "name_part1": "VERIFY", "name_part2": "DATING",
        "description": "Romance scam detection and AI photo verification platform. Protecting singles from financial fraud and catfishing.",
        "full_name": "VerifyDating",
        "active_link": "dating"
    }
}

for site_dir, config in sites_config.items():
    file_path = os.path.join(site_dir, "index.html")
    if not os.path.exists(file_path):
        continue
        
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
        
    # Generate the footer for this site
    colors = {k: "#cbd5e1" for k in ["isbroker_color", "jobscam_color", "pillscam_color", "dating_color", "appscam_color"]}
    weights = {k: "400" for k in ["isbroker_weight", "jobscam_weight", "pillscam_weight", "dating_weight", "appscam_weight"]}
    
    # Highlight the active link
    colors[config["active_link"] + "_color"] = "#38bdf8"
    weights[config["active_link"] + "_weight"] = "700"
    
    footer_html = footer_template.format(
        icon=config["icon"],
        name_part1=config["name_part1"],
        name_part2=config["name_part2"],
        description=config["description"],
        full_name=config["full_name"],
        **colors,
        **weights
    )
    
    # Replace the old footer
    # Using regex to find the old <footer ...> ... </footer>
    html_new = re.sub(r'<footer[^>]*vasile-ecosystem-footer[^>]*>.*?</footer>', footer_html, html, flags=re.DOTALL)
    
    # Sometimes it might not have class="vasile-ecosystem-footer", so let's fallback to just replacing any <footer...</footer> at the end of body
    if html_new == html:
        # Just replace the last footer
        parts = html.rsplit('<footer', 1)
        if len(parts) == 2:
            end_parts = parts[1].split('</footer>', 1)
            if len(end_parts) == 2:
                html_new = parts[0] + footer_html + end_parts[1]
                
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_new)
        
    print(f"Updated {site_dir}/index.html")

