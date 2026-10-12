import re
import os

gtag_code = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-6V4XM02QDM"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-6V4XM02QDM');
</script>
"""

# Update index.html
with open("app-scam-radar/index.html", "r", encoding="utf-8") as f:
    html = f.read()

if "G-6V4XM02QDM" not in html:
    html = html.replace("</head>", f"{gtag_code}</head>")
    with open("app-scam-radar/index.html", "w", encoding="utf-8") as f:
        f.write(html)

# Update server.py
with open("app-scam-radar/server.py", "r", encoding="utf-8") as f:
    server = f.read()

if "G-6V4XM02QDM" not in server:
    server = server.replace("</head>", f"{gtag_code}    </head>")
    with open("app-scam-radar/server.py", "w", encoding="utf-8") as f:
        f.write(server)

