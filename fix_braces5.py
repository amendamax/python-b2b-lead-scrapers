import re

with open("dating-photo-checker/server.py", "r", encoding="utf-8") as f:
    content = f.read()

# Let's find all <script> blocks containing geo-meta
# We will use regex to find the blocks

pattern = re.compile(r"<script>\s*// Geo-Location Filter for US visitors \(CFTC Restrictions\).*?</script>", re.DOTALL)
matches = pattern.finditer(content)

new_content = content
for match in matches:
    block = match.group(0)
    # 1. Convert all {{ to { and }} to }
    raw_block = block.replace("{{", "{").replace("}}", "}")
    # 2. Convert all { to {{ and } to }}
    safe_block = raw_block.replace("{", "{{").replace("}", "}}")
    # Replace in new_content
    new_content = new_content.replace(block, safe_block)

with open("dating-photo-checker/server.py", "w", encoding="utf-8") as f:
    f.write(new_content)
