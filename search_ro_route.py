with open("C:/Users/bratu/Documents/antigravity/amazing-borg/dating-photo-checker/server.py", "r", encoding="utf-8") as f:
    code = f.read()

# Let's find all occurrences of get("/ro") or similar
import re
matches = re.finditer(r'@app\.get\("/ro[^"]*"\)', code)
for m in matches:
    start = max(0, m.start() - 200)
    end = min(len(code), m.end() + 600)
    print(f"Match found at position {m.start()}:\n{code[start:end]}\n" + "="*50)
