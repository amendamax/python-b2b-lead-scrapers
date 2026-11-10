with open("dating-photo-checker/server.py", "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if "@app.get(" in line and ("scammer" in line or "profile" in line):
            print(line.strip())
