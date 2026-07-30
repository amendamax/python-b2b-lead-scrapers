with open("C:/Users/bratu/Documents/antigravity/amazing-borg/dating-photo-checker/server.py", "r", encoding="utf-8") as f:
    code = f.read()

# Search for any string containing vasiledev or verifydating or isbrokersafe
import re
domains = ["vasiledev", "verifydating", "isbrokersafe"]
for d in domains:
    matches = list(re.finditer(d, code, re.IGNORECASE))
    print(f"Domain '{d}' matches: {len(matches)}")
    for m in matches[:5]:
        start = max(0, m.start() - 100)
        end = min(len(code), m.end() + 200)
        print(f"  Snippet: {code[start:end]}")
