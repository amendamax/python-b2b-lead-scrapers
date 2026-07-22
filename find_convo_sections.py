import sys
sys.stdout.reconfigure(encoding='utf-8')

with open(r"C:\Users\bratu\Documents\antigravity\amazing-borg\extracted_conversations.txt", "r", encoding="utf-8", errors="ignore") as f:
    content = f.read()

# Split by "### " to get individual sections
sections = content.split("### ")
for idx, sec in enumerate(sections):
    sec_lower = sec.lower()
    if "viktorija" in sec_lower or "viktoria" in sec_lower:
        # Check if it contains real discussion content
        if "conversation list" not in sec_lower and "index of all" not in sec_lower:
            print(f"=== SECTION {idx} ===")
            print(sec[:4000]) # Print first 4000 chars of the section
            print("\n" + "="*80 + "\n")
