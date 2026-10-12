import re
import os

gtag_code = """
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-950R9NXTL9"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-950R9NXTL9');
</script>
"""

gtag_code_server = gtag_code.replace("function gtag(){dataLayer.push(arguments);}", "function gtag(){{dataLayer.push(arguments);}}")

# Update index.html
with open("job-scam-radar/index.html", "r", encoding="utf-8") as f:
    html = f.read()

if "G-950R9NXTL9" not in html:
    html = html.replace("</head>", f"{gtag_code}</head>")
    with open("job-scam-radar/index.html", "w", encoding="utf-8") as f:
        f.write(html)

# Update server.py
server_path = "job-scam-radar/server.py"
if os.path.exists(server_path):
    with open(server_path, "r", encoding="utf-8") as f:
        server = f.read()
    
    if "G-950R9NXTL9" not in server:
        server = server.replace("</head>", f"{gtag_code_server}    </head>")
        with open(server_path, "w", encoding="utf-8") as f:
            f.write(server)

