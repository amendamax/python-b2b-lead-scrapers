import re

with open("app-scam-radar/server.py", "r", encoding="utf-8") as f:
    server = f.read()

# I want to inject the footer HTML right before </body>
footer_html = """
        <div style="max-width: 1140px; margin: 40px auto 0; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.1); text-align: center; color: #64748b; font-size: 13px;">
            <p>&copy; 2026 AppScamRadar™ by VasileDev Group. All rights reserved. Powered globally by Cloudflare Edge Network.</p>
        </div>
"""

if "&copy; 2026 AppScamRadar" not in server:
    server = server.replace("</body>", f"{footer_html}\n    </body>")
    with open("app-scam-radar/server.py", "w", encoding="utf-8") as f:
        f.write(server)
