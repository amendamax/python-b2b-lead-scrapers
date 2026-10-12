with open("dating-photo-checker/scam_regulators_scraper.py", "r", encoding="utf-8") as f:
    content = f.read()
print("Contains hardcoded data?", "True" if "hsbc-privatefx.com" in content else "False")
