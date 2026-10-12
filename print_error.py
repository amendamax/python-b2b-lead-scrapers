with open("dating-photo-checker/server.py", "r", encoding="utf-8") as f:
    lines = f.readlines()
for i in range(2510, 2540):
    print(f"{i+1}: {lines[i]}", end="")
