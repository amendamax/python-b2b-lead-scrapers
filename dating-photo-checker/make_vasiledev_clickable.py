import glob
import re

files = glob.glob('**/*.html', recursive=True)

link_html = '<a href="https://vasiledev.com" target="_blank" rel="noopener" style="color: #38bdf8; font-weight: 700; text-decoration: underline;">VasileDev</a>'

count = 0
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace plain VasileDev inside footer-copyright paragraph if not already linked
    if 'footer-copyright' in content:
        # Pattern matching VasileDev when not inside <a ...>VasileDev</a>
        pattern = r'(<p class="footer-copyright">.*?)(?<!href="https://vasiledev\.com">)VasileDev(.*?<\/p>)'
        
        def repl(match):
            prefix = match.group(1)
            suffix = match.group(2)
            if 'href="https://vasiledev.com"' in prefix:
                return match.group(0) # Already replaced
            return f"{prefix}{link_html}{suffix}"

        new_content = re.sub(pattern, repl, content, flags=re.DOTALL)
        if new_content != content:
            with open(f, 'w', encoding='utf-8') as file:
                file.write(new_content)
            print(f'Updated {f}')
            count += 1

print(f'Finished updating {count} HTML files.')
