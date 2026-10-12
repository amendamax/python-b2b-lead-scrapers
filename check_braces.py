with open("dating-photo-checker/server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i, line in enumerate(lines[2660:]):
    print(f"{i+2661}: {line}", end="")
