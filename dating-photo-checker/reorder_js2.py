import re

def reorder_js(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()
        
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
        
        # Strip ranks just in case
        sabio_code = sabio_code.replace('>3</div>', ' border: 2px solid #10b981;">1</div>')
        sabio_code = sabio_code.replace('border: 2px solid #10b981;">3</div>', ' border: 2px solid #10b981;">1</div>')
        ftmo_code = ftmo_code.replace('border: 2px solid #10b981;">1</div>', '>2</div>')
        fn_code = fn_code.replace('>2</div>', '>3</div>')
        
        sabio_code = sabio_code.replace("background: rgba(16, 185, 129, 0.2); color: #10b981;", "background: rgba(239, 68, 68, 0.2); color: #ef4444;")
        
        new_firms = f"{sabio_code}\n\n                    {ftmo_code}\n\n                    {fn_code}"
        
        # Replace the entire block
        full_pattern = ftmo_pattern + r'.*?' + fn_pattern + r'.*?' + sabio_pattern
        code = re.sub(full_pattern, new_firms, code, flags=re.DOTALL)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        print(f"Success for {filepath}")
    else:
        print(f"Failed to match for {filepath}")

reorder_js("broker-verifier/app.js")
reorder_js("app.js")
