import re

with open("server.py", "r", encoding="utf-8") as f:
    code = f.read()

# I will find the block of FTMO, FundedNext, and SabioTrade and rearrange them.
# They are clearly commented.
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

    # Change the ranks
    sabio_code = sabio_code.replace('>3</div>', ' border: 2px solid #10b981;">1</div>')
    ftmo_code = ftmo_code.replace('border: 2px solid #10b981;">1</div>', '>2</div>')
    fn_code = fn_code.replace('>2</div>', '>3</div>')

    # Update Sabio badge and description
    # Find the badge and add the SAFE30
    sabio_badge_old = "{t.get('sabio_badge', 'EXCELLENT UI')}"
    sabio_badge_new = "{t.get('sabio_badge', 'PROMO: SAFE30')}"
    
    # Make SabioTrade badge red or gold to pop!
    sabio_code = sabio_code.replace("background: rgba(16, 185, 129, 0.2); color: #10b981;", "background: rgba(239, 68, 68, 0.2); color: #ef4444;")
    sabio_code = sabio_code.replace(sabio_badge_old, sabio_badge_new)
    
    sabio_desc_old = "{t.get('sabio_desc', 'Great for Beginners &bull; High Approval')}"
    sabio_desc_new = "{t.get('sabio_desc', '30% Discount with code SAFE30 &bull; High Approval')}"
    sabio_code = sabio_code.replace(sabio_desc_old, sabio_desc_new)

    # Now replace them in the original code
    # Find the container
    container_pattern = r'(<div style="display: flex; flex-direction: column; gap: 12px;">\s*)(<!-- FTMO -->.*?<!-- SabioTrade -->.*?</a>)'
    
    new_firms = f"{sabio_code}\n{ftmo_code}\n{fn_code}"
    
    def replacer(m):
        return m.group(1) + new_firms
        
    code = re.sub(container_pattern, replacer, code, flags=re.DOTALL)

    with open("server.py", "w", encoding="utf-8") as f:
        f.write(code)
    print("Replaced successfully!")
else:
    print("Could not find blocks.")

