import re

with open("server.py", "r", encoding="utf-8") as f:
    content = f.read()

# find ALL <script> blocks containing propCard
start = 0
while True:
    idx = content.find("const props = propCard.querySelectorAll('a');", start)
    if idx == -1:
        break
    
    script_start = content.rfind("<script>", 0, idx)
    script_end = content.find("</script>", idx) + 9
    
    block = content[script_start:script_end]
    raw = block.replace("{{", "{").replace("}}", "}")
    safe = raw.replace("{", "{{").replace("}", "}}")
    
    content = content[:script_start] + safe + content[script_end:]
    start = script_start + len(safe)
    print("Replaced one block!")

with open("server.py", "w", encoding="utf-8") as f:
    f.write(content)
