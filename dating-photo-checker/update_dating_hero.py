import glob

files = glob.glob('**/index.html')
# filter out broker-verifier
files = [f for f in files if 'broker-verifier' not in f]

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if 'Verify Before You Fall' in content:
        content = content.replace(
            '<h1 id="main-title">Verify Before You Fall</h1>',
            '<h1 id="main-title">Reverse Image & Biometric Face Search for Dating Safety</h1>'
        )
        content = content.replace(
            '<span class="hero-tag"><i class="fa-solid fa-circle-check"></i> Trusted by 50,000+ users</span>',
            '<span class="hero-tag"><i class="fa-solid fa-shield-cat"></i> AI Biometric Face Recognition Engine</span>'
        )
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f'Updated {f}')
