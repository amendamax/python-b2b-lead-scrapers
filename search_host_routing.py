with open("C:/Users/bratu/Documents/antigravity/amazing-borg/dating-photo-checker/server.py", "r", encoding="utf-8") as f:
    code = f.read()

import re
matches = re.finditer(r'host =', code)
for m in matches:
    start = max(0, m.start() - 200)
    end = min(len(code), m.end() + 600)
    print(f"Match found:\n{code[start:end]}\n" + "="*50)
