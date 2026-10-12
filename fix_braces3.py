with open("dating-photo-checker/server.py", "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("}}});", "}});")

with open("dating-photo-checker/server.py", "w", encoding="utf-8") as f:
    f.write(content)
