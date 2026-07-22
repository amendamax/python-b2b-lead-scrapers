import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\bratu\Documents\antigravity\amazing-borg\extracted_conversations.txt", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if "viktorija" in line.lower() or "viktoria" in line.lower():
        # Check if it is a real conversation message and not just tool calls
        if any(term in line for term in ["First Request:", "Last Request:", "Content:", "[steps"]):
            print(f"=== MATCH AT LINE {idx+1} ===")
            start = max(0, idx - 15)
            end = min(len(lines), idx + 25)
            for j in range(start, end):
                print(f"{j+1}: {lines[j]}", end="")
            print("\n" + "="*50 + "\n")
