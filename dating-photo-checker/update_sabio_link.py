import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

# The current URL might be the one with afftrack=isbrokersafe
new_url = "https://sabiotrade.com/?aff=838346&aff_model=revenue&afftrack=BrokerVerifier"

# Replace it
code = re.sub(r'url="https://sabiotrade\.com.*?status_code=307\)', f'url="{new_url}", status_code=307)', code)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(code)
