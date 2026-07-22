import glob

files = glob.glob('**/*.html', recursive=True)
unlinked = []

for f in files:
    content = open(f, encoding='utf-8').read()
    if 'VasileDev' in content and 'href="https://vasiledev.com"' not in content:
        unlinked.append(f)

print('Unlinked files count:', len(unlinked))
print('Unlinked files:', unlinked)
