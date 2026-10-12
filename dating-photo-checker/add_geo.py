import re

geo_js = """
<script>
    // Geo-Location Filter for US visitors (CFTC Restrictions)
    fetch('/api/v1/geo-meta').then(r => r.json()).then(geo => {
        if (geo.country === "US") {
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
                    
                    const desc = sabio.querySelector('div[style*="color: #94a3b8"]');
                    if (desc) desc.innerHTML = "US Traders Accepted &bull; Keep 100% of First $25k";
                }
            }
        }
    }).catch(e => console.error(e));
</script>
"""

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

if "Geo-Location Filter for US visitors" not in code:
    code = code.replace("</body>\n</html>", geo_js + "\n</body>\n</html>")
    
    with open("server.py", "w", encoding="utf-8") as f:
        f.write(code)

with open("broker-verifier/app.js", "r", encoding="utf-8") as f:
    js_code = f.read()
    
# We will just append the logic to the end of the scammer lookup in app.js
if "Geo-Location Filter for US visitors" not in js_code:
    geo_js_dom = """
        // Geo-Location Filter for US visitors (CFTC Restrictions)
        fetch('/api/v1/geo-meta').then(r => r.json()).then(geo => {
            if (geo.country === "US") {
                const propCard = document.getElementById('sabio-dynamic-box');
                if (propCard) {
                    const props = propCard.querySelectorAll('a');
                    if (props.length > 0) {
                        const sabio = props[0]; 
                        sabio.href = "https://apextraderfunding.com"; 
                        const name = sabio.querySelector('span[style*="color: #fff"]');
                        if (name) name.innerText = "Apex Trader Funding";
                        const badge = sabio.querySelectorAll('span')[1];
                        if (badge) { badge.innerText = "FUTURES TRADING"; badge.style.background = "rgba(14, 165, 233, 0.2)"; badge.style.color = "#38bdf8"; }
                        const desc = sabio.querySelector('div[style*="color: #94a3b8"]');
                        if (desc) desc.innerHTML = "US Traders Accepted &bull; Keep 100% of First $25k";
                    }
                }
            }
        });
"""
    # inject after propBox.innerHTML = html_string;
    js_code = js_code.replace("brokerContainer.parentNode.insertBefore(propBox, brokerContainer);\n                }", "brokerContainer.parentNode.insertBefore(propBox, brokerContainer);\n                }\n" + geo_js_dom)
    with open("broker-verifier/app.js", "w", encoding="utf-8") as f:
        f.write(js_code)

print("Geo scripts injected!")
