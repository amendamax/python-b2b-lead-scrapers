import re

with open("dating-photo-checker/server.py", "r", encoding="utf-8") as f:
    content = f.read()

# I will find the exact JS block and manually replace it
old_js = """<script>
    // Geo-Location Filter for US visitors (CFTC Restrictions)
    fetch('/api/v1/geo-meta').then(r => r.json()).then(geo => {{
        if (geo.country === "US") {{
            const propCard = document.querySelector('.prop-trading-card');
            if (propCard) {
                const props = propCard.querySelectorAll('a');
                if (props.length > 0) {
                    const sabio = props[0]; 
                    sabio.href = "https://apextraderfunding.com"; // We will replace this with his affiliate link later
                    
                    const name = sabio.querySelector('span[style*="color: #fff"]');
                    if (name) name.innerText = "Apex Trader Funding";
                    
                    const badge = sabio.querySelectorAll('span')[1];
                    if (badge) { 
                        badge.innerText = "FUTURES TRADING"; 
                        badge.style.background = "rgba(56, 189, 248, 0.1)"; 
                        badge.style.color = "#38bdf8"; 
                    }
                    
                    const p1 = sabio.querySelectorAll('p')[0];
                    if (p1) p1.innerText = "No.1 US Regulated Broker. Keep 100% of your first $25,000 in profits.";
                    
                    const p2 = sabio.querySelectorAll('p')[1];
                    if (p2) p2.innerHTML = '<span style="color: #10b981;">&#10004;</span> Up to 20 Accounts';
                    
                    const p3 = sabio.querySelectorAll('p')[2];
                    if (p3) p3.innerHTML = '<span style="color: #10b981;">&#10004;</span> Trade Full-Sized Contracts';
                    
                    const price = sabio.querySelector('div[style*="color: #3b82f6"]');
                    if (price) price.innerHTML = '<span style="font-size: 0.9rem; color: #64748b; font-weight: 400; margin-right: 4px;">from</span>$16<span style="font-size: 0.9rem; color: #64748b; font-weight: 400; margin-left: 2px;">/mo</span>';
                }
            }
        }}
    }}).catch(err => console.error("Geo-meta check failed:", err));
    </script>"""

new_js = old_js.replace("{", "{{").replace("}", "}}")
# But wait, old_js already has {{ and }} in some places because of my previous script!
# Let's just fix it properly by finding the block in the original text, restoring single braces, then doubling them.

# First, extract the block from content. We know it starts with <script> \n // Geo-Location
start_str = "<script>\n    // Geo-Location Filter for US visitors (CFTC Restrictions)"
end_str = "    </script>"
start_idx = content.find(start_str)
end_idx = content.find(end_str, start_idx) + len(end_str)

block = content[start_idx:end_idx]

# Replace all {{ with { and }} with } to get raw JS back
raw_js = block.replace("{{", "{").replace("}}", "}")

# Now replace all { with {{ and } with }}
safe_js = raw_js.replace("{", "{{").replace("}", "}}")

content = content[:start_idx] + safe_js + content[end_idx:]

with open("dating-photo-checker/server.py", "w", encoding="utf-8") as f:
    f.write(content)
