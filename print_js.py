import re

with open("dating-photo-checker/server.py", "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find('geo.country === "US"')
start = max(0, idx - 500)
end = min(len(content), idx + 800)
print(content[start:end])
