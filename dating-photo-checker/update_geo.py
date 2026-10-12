import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Modify the route handlers to pass country
code = re.sub(r'html = generate_scam_report_page\("([^"]+)", slug\)', r'country = request.headers.get("cf-ipcountry", "US").upper()\n    html = generate_scam_report_page("\1", slug, country)', code)
code = re.sub(r'html = generate_scam_report_page\((lang), slug\)', r'country = request.headers.get("cf-ipcountry", "US").upper()\n    html = generate_scam_report_page(\1, slug, country)', code)

# 2. Update function signature
code = code.replace('def generate_scam_report_page(lang, slug):', 'def generate_scam_report_page(lang, slug, country="US"):')

# 3. Add Topstep block in generate_scam_report_page
# We will inject Topstep if country == "US", otherwise SabioTrade
prop_block = '''
                          <div style="display: flex; flex-direction: column; gap: 12px;">
'''
# SabioTrade block is already there. Let's find it.
# Instead of complex regex, let's just make the /go/sabiotrade route dynamic in python and use JS to switch the UI names for JS generated pages, but for server.py we can just use python.

