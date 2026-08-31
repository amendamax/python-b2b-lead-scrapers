import os, re

base_dir = os.getcwd()
checker_dir = os.path.join(base_dir, "dating-photo-checker")
bv_dir = os.path.join(checker_dir, "broker-verifier")

# Update CSS for header-nav, header-badges, and header-action in broker-verifier/style.css
css_path = os.path.join(bv_dir, "style.css")
with open(css_path, "r", encoding="utf-8") as f:
    css = f.read()

# Replace header-nav and header-badges definition
old_header_css = re.search(r'/\* =+\s*Header\s*=+ \*/\s*\.header-nav \{.*?\}\s*\.header-badges \{.*?\}', css, flags=re.DOTALL)
new_header_css = """/* ==========================================================================
   Header
   ========================================================================== */
.header-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    gap: 12px;
    flex-wrap: nowrap;
    width: 100%;
}

.header-badges {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}

.header-action {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: nowrap;
    flex-shrink: 0;
}"""

if old_header_css:
    css = css.replace(old_header_css.group(0), new_header_css)
    with open(css_path, "w", encoding="utf-8") as f:
        f.write(css)
    print("Updated broker-verifier/style.css layout rules")

# Update HTML files in broker-verifier
for root, dirs, files in os.walk(bv_dir):
    for f in files:
        if f.endswith(".html"):
            fpath = os.path.join(root, f)
            with open(fpath, "r", encoding="utf-8") as file:
                content = file.read()
            
            # Find the header-nav block
            match = re.search(r'<div class="header-nav">(.*?)</div>\s*</div>\s*<div class="hero-box">', content, flags=re.DOTALL)
            if not match:
                match = re.search(r'<div class="header-nav">(.*?)</div>\s*</header>', content, flags=re.DOTALL)
            
            # Let's cleanly structure the inner header-nav
            lang = os.path.basename(root)
            dating_text = "❤️ Dating Check ↗" if lang != "ro" else "❤️ Verifică Dating ↗"
            live_audit_text = "Live Audit" if lang != "ro" else "Audit Live"
            
            structured_header = f"""<div class="header-nav">
                <a href="/" class="logo-link"><span class="logo-cyber-shield"><i class="fa-solid fa-shield-halved"></i></span><h1 class="logo" style="margin: 0;">Broker<span>Verifier</span></h1></a>
                
                <div class="header-badges">
                    <a href="/pricing" class="badge-tag" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.35);">💳 Pricing</a>
                    <a href="/widget" class="badge-tag" style="background: rgba(168, 85, 247, 0.15); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.35);">🛡️ Trust Widget</a>
                    <a href="/api/v1/docs" class="badge-tag badge-api-glow">⚡ Threat API</a>
                </div>

                <div class="header-action" style="display: flex; align-items: center; gap: 8px;">
                    <a href="/extension" target="_blank" rel="noopener" class="badge-tag" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(56, 189, 248, 0.25) 100%); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.5); font-weight: 800;"><i class="fa-brands fa-chrome"></i> 🛡️ Add to Chrome — Free</a>
                    <a href="https://pypi.org/project/isbrokersafe/" target="_blank" rel="noopener" class="badge-tag" style="background: rgba(56, 189, 248, 0.15); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.35);">🐍 PyPI SDK ↗</a>
                    <a href="https://verifydating.net/" target="_blank" rel="noopener" class="badge-tag badge-dating-glow">{dating_text}</a>
                    <span class="badge badge-live" style="background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.35); padding: 5px 12px; border-radius: 20px; font-size: 11.5px; font-weight: 800; display: inline-flex; align-items: center; gap: 6px;"><span class="pulse-dot" style="width: 7px; height: 7px; background: #10b981; border-radius: 50%; display: inline-block; box-shadow: 0 0 8px #10b981;"></span> {live_audit_text}</span>
                </div>
            </div>"""
            
            # Replace existing header-nav in content
            content = re.sub(r'<div class="header-nav">.*?</div>\s*</div>\s*(?=<div class="hero-box">)', structured_header + '\n            ', content, flags=re.DOTALL)
            
            with open(fpath, "w", encoding="utf-8") as file:
                file.write(content)
            print(f"Structured identical 3-part header in: {os.path.relpath(fpath, checker_dir)}")

print("ALL_BROKER_HEADERS_BALANCED_SUCCESS")
