import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

# Replace all sabio_badge translations
code = re.sub(r'"sabio_badge":\s*".*?"', '"sabio_badge": "PROMO: SAFE30"', code)

# Replace all sabio_desc translations to mention the 30% discount
code = re.sub(r'"sabio_desc":\s*".*?"', '"sabio_desc": "-30% Discount (code SAFE30) &bull; High Approval"', code)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(code)
