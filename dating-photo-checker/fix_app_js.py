import re

def fix_html(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()

        code = code.replace('font-size: 14px; >2</div>', 'font-size: 14px;">2</div>')
        code = code.replace('font-size: 14px;" border: 2px solid #10b981;">1</div>', 'font-size: 14px; border: 2px solid #10b981;">1</div>')
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
    except:
        pass

fix_html("broker-verifier/app.js")
fix_html("app.js")
