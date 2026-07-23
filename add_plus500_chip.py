import glob

old_target = '<button class="ticker-chip safe" onclick="selectBroker(\'Exness\')">Exness <span class="score">96% Safe</span></button>'
new_target = '<button class="ticker-chip safe" onclick="selectBroker(\'Exness\')">Exness <span class="score">96% Safe</span></button>\n                    <button class="ticker-chip safe" onclick="selectBroker(\'Plus500\')">Plus500 <span class="score">91% Safe</span></button>'

files = glob.glob('dating-photo-checker/broker-verifier/**/index.html', recursive=True) + glob.glob('broker-verifier/**/index.html', recursive=True)
count = 0
for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        content = fp.read()
    if old_target in content and "selectBroker('Plus500')" not in content:
        content = content.replace(old_target, new_target)
        with open(f, 'w', encoding='utf-8') as fp:
            fp.write(content)
        count += 1
        print(f'Updated {f}')

print(f'Total files updated: {count}')
