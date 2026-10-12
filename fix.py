import re
with open('index.html', encoding='utf-8') as f:
    html = f.read()

with open('job-scam-radar/index.html', encoding='utf-8') as f:
    job = f.read()

footer = re.search(r'(<footer class="vasiledev-ecosystem-footer".*?</footer>)', job, re.DOTALL).group(1)

# Modify it for VasileDev
footer = footer.replace('fa-briefcase', 'fa-code')
footer = footer.replace('JOBSCAM<strong style="color: #38bdf8;">RADAR</strong>', '&lt;/&gt; <strong style="color:#fff">VASILEDEV</strong>')
footer = footer.replace('Employment fraud defense system. Identifying fake recruitment agencies, task scams, and human trafficking operations.', 'High-Performance Distributed Software Engineering, AI Automation Systems & Cloud-Scale Data Intelligence.')
footer = footer.replace('JobScamRadar', 'VasileDev')
footer = footer.replace('style="color: #38bdf8; font-weight: 700; text-decoration: none;">?? JobScamRadar.com', 'style="color: #cbd5e1; font-weight: 400; text-decoration: none;">?? JobScamRadar.com')
footer = footer.replace('style="color: #cbd5e1; text-decoration: none;">?? VasileDev.com', 'style="color: #38bdf8; font-weight: 700; text-decoration: none;">?? VasileDev.com')

# Make the crown blue for vasiledev link
footer = footer.replace('?? VasileDev.com', '?? VasileDev.com') # Keep emojis safe, we don't touch them directly here since we replace strings

html = re.sub(r'<footer.*?</footer>', footer, html, flags=re.DOTALL)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
