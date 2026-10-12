with open("server.py", "r", encoding="utf-8") as f:
    content = f.read()

# Let's do it simply:
# Replace the single braces in this specific geo-meta block string that is currently unescaped.

bad_string = """<script>
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
                        badge.style.background = "rgba(14, 165, 233, 0.2)"; 
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

good_string = bad_string.replace("{", "{{").replace("}", "}}").replace("{{{{", "{{").replace("}}}}", "}}")

content = content.replace(bad_string, good_string)

with open("server.py", "w", encoding="utf-8") as f:
    f.write(content)
