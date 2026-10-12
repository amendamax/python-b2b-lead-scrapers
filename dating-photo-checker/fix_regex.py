import re

with open("server.py", "r", encoding="utf-8") as f:
    content = f.read()

# Let's find the exact indices
idx = content.find("const props = propCard.querySelectorAll('a');")
if idx != -1:
    print(f"Found at {idx}")
    # Replace braces locally around idx
    start = content.rfind("<script>", 0, idx)
    end = content.find("</script>", idx) + 9
    
    block = content[start:end]
    # Re-escape the whole block correctly
    # 1. Un-escape
    raw = block.replace("{{", "{").replace("}}", "}")
    # 2. Escape
    safe = raw.replace("{", "{{").replace("}", "}}")
    
    content = content[:start] + safe + content[end:]
    
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(content)
else:
    print("Not found!")
