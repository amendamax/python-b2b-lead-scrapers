import re

# We need to update broker-verifier/app.js
def update_js_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()

        # Same logic: find the Prop Trading Alternative section
        sabio_badge_old = r'"sabio_badge":\s*".*?"'
        sabio_badge_new = '"sabio_badge": "PROMO: SAFE30"'
        sabio_desc_old = r'"sabio_desc":\s*".*?"'
        sabio_desc_new = '"sabio_desc": "30% Discount (code SAFE30) &bull; High Approval"'

        code = re.sub(sabio_badge_old, sabio_badge_new, code)
        code = re.sub(sabio_desc_old, sabio_desc_new, code)

        # Now reorder the HTML injection string
        ftmo_pattern = r'(<!-- FTMO -->.*?</a>)'
        fn_pattern = r'(<!-- FundedNext -->.*?</a>)'
        sabio_pattern = r'(<!-- SabioTrade -->.*?</a>)'

        ftmo_match = re.search(ftmo_pattern, code, re.DOTALL)
        fn_match = re.search(fn_pattern, code, re.DOTALL)
        sabio_match = re.search(sabio_pattern, code, re.DOTALL)

        if ftmo_match and fn_match and sabio_match:
            ftmo_code = ftmo_match.group(1)
            fn_code = fn_match.group(1)
            sabio_code = sabio_match.group(1)

            # Change ranks
            sabio_code = sabio_code.replace('>3</div>', ' border: 2px solid #10b981;">1</div>')
            ftmo_code = ftmo_code.replace('border: 2px solid #10b981;">1</div>', '>2</div>')
            fn_code = fn_code.replace('>2</div>', '>3</div>')

            # Sabio red badge
            sabio_code = sabio_code.replace("background: rgba(16, 185, 129, 0.2); color: #10b981;", "background: rgba(239, 68, 68, 0.2); color: #ef4444;")

            # container
            container_pattern = r'(<div style="display: flex; flex-direction: column; gap: 12px;">\s*)(<!-- FTMO -->.*?<!-- SabioTrade -->.*?</a>)'
            new_firms = f"{sabio_code}\n{ftmo_code}\n{fn_code}"
            
            def replacer(m):
                return m.group(1) + new_firms
                
            code = re.sub(container_pattern, replacer, code, flags=re.DOTALL)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Updated {filepath}")
    except Exception as e:
        print(f"Failed on {filepath}: {e}")

update_js_file("broker-verifier/app.js")
update_js_file("app.js")
