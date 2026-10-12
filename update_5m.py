with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace occurrences of 500k with 5M+
content = content.replace("Programmatic SEO Engine & Data Harvester Fleet (500k+ Pages)", "Programmatic SEO Engine & Data Harvester Fleet (5M+ Pages)")
content = content.replace("over 500,000 auto-generated pages", "over 5,000,000 auto-generated pages")
content = content.replace("View Live Node (VerifyDating - 500k+ Pages)", "View Live Node (VerifyDating - 5M+ Pages)")

with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
print("Success")
