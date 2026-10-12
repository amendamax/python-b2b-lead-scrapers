import re
import os

gtag_code = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-JYVX5B6FRC"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-JYVX5B6FRC');
</script>
"""

gtag_code_server = gtag_code.replace("function gtag(){dataLayer.push(arguments);}", "function gtag(){{dataLayer.push(arguments);}}")

# Update index.html
with open("pill-scam-radar/index.html", "r", encoding="utf-8") as f:
    html = f.read()

if "G-JYVX5B6FRC" not in html:
    html = html.replace("</head>", f"{gtag_code}</head>")
    with open("pill-scam-radar/index.html", "w", encoding="utf-8") as f:
        f.write(html)

# Update server.py
server_path = "pill-scam-radar/server.py"
if os.path.exists(server_path):
    with open(server_path, "r", encoding="utf-8") as f:
        server = f.read()
    
    if "G-JYVX5B6FRC" not in server:
        server = server.replace("</head>", f"{gtag_code_server}    </head>")
        with open(server_path, "w", encoding="utf-8") as f:
            f.write(server)

