import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

# Fix SabioTrade HTML
code = code.replace('font-size: 14px;" border: 2px solid #10b981;">1</div>', 'font-size: 14px; border: 2px solid #10b981;">1</div>')

# Fix FTMO HTML
code = code.replace('font-size: 14px; >2</div>', 'font-size: 14px;">2</div>')

with open("server.py", "w", encoding="utf-8") as f:
    f.write(code)
