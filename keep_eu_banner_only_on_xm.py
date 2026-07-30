import glob
import re
import os

all_files = glob.glob('broker-verifier/**/reviews/*.html', recursive=True) + glob.glob('dating-photo-checker/broker-verifier/**/reviews/*.html', recursive=True)

count = 0
for f_path in set(all_files):
    if not os.path.exists(f_path):
        continue
    f_lower = f_path.replace('\\', '/').lower()
    
    # If it is NOT xm.html, remove the EU banner!
    if 'xm.html' not in f_lower:
        with open(f_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'EU Resident XM Global Notice' in content or 'XM Global regulations' in content or 'reglementările XM Global' in content:
            # Remove the banner block
            new_content = re.sub(
                r'\s*<!-- EU Resident XM Global Notice -->[\s\S]*?<\/div>',
                '',
                content
            )
            if new_content != content:
                with open(f_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Removed EU banner from non-XM review: {f_path}")
                count += 1

print(f"Total non-XM review files cleaned: {count}")
