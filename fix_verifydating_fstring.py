import re

with open("dating-photo-checker/server.py", "r", encoding="utf-8") as f:
    content = f.read()

# I need to double the curly braces in the javascript block that I added earlier today!
# Wait, let's just find the JS block and double the braces for the f-string.

# The JS block is:
"""
<script>
fetch('/api/v1/geo-meta')
  .then(response => response.json())
  .then(geo => {
    if (geo.country === "US") {
        document.querySelectorAll('.prop-firm-box').forEach(box => {
            box.querySelector('.prop-logo').src = "https://www.apextraderfunding.com/wp-content/uploads/2021/04/Apex-Trader-Funding-Logo.png";
            box.querySelector('.prop-name').textContent = "Apex Trader Funding";
            box.querySelector('.prop-desc').textContent = "No.1 US Regulated Broker. Keep 100% of your first $25,000 in profits.";
            box.querySelector('.prop-btn').href = "https://apextraderfunding.com";
        });
    }
  })
  .catch(err => console.error("Geo-meta error:", err));
</script>
"""

# If it's already there with single braces, we double them
content = content.replace("geo => {", "geo => {{")
content = content.replace("if (geo.country === \"US\") {", "if (geo.country === \"US\") {{")
content = content.replace("document.querySelectorAll('.prop-firm-box').forEach(box => {", "document.querySelectorAll('.prop-firm-box').forEach(box => {{")
content = content.replace("});", "}});")
content = content.replace(".catch(err => console.error(\"Geo-meta error:\", err));\n</script>", ".catch(err => console.error(\"Geo-meta error:\", err));\n}}</script>")
content = content.replace(".catch(err => console.error('Geo-meta error:', err));\n</script>", ".catch(err => console.error('Geo-meta error:', err));\n}}</script>")
content = content.replace("  })\n  .catch", "  }})\n  .catch")

with open("dating-photo-checker/server.py", "w", encoding="utf-8") as f:
    f.write(content)
