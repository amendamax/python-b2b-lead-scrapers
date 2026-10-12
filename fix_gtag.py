import re

with open("app-scam-radar/server.py", "r", encoding="utf-8") as f:
    server = f.read()

# Fix the f-string curly braces issue in gtag
server = server.replace("function gtag(){dataLayer.push(arguments);}", "function gtag(){{dataLayer.push(arguments);}}")

with open("app-scam-radar/server.py", "w", encoding="utf-8") as f:
    f.write(server)
