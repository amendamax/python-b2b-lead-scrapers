import os

for path in ['ro/index.html', 'it/index.html']:
    if not os.path.exists(path):
        continue
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    text = text.replace('Flotă de Harvestere Date (4M+ Pagini)', 'Flotă de Harvestere Date (100k+ Pagini)')
    text = text.replace('Flotă de Harvestere Date (5M+ Pagini)', 'Flotă de Harvestere Date (100k+ Pagini)')
    text = text.replace('Flotta di Data Harvesters (4M+ Pagine)', 'Flotta di Data Harvesters (100k+ Pagine)')
    text = text.replace('Flotta di Data Harvesters (5M+ Pagine)', 'Flotta di Data Harvesters (100k+ Pagine)')
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)
print("Fixed VasileDev numbers")
