with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the Live Node button
old_button = '<a href="https://isbrokersafe.com" class="btn btn-secondary" target="_blank" rel="noopener">View Live Node (IsBrokerSafe) ↗</a>'
new_button = '<a href="https://verifydating.net" class="btn btn-secondary" target="_blank" rel="noopener">View Live Node (VerifyDating - 500k+ Pages) ↗</a>'

if old_button in content:
    content = content.replace(old_button, new_button)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(content)
    print("Success")
else:
    print("Old button not found")
