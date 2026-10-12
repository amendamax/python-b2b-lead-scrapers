with open("dating-photo-checker/server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i in range(5990, 6010):
    print(f"{i+1}: {lines[i]}", end="")
