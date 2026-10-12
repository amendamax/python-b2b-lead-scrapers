import re

def update_file(filepath, lang="en"):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Titles and Numbers
    content = content.replace("(5M+ Pages)", "(100k+ Pages)")
    content = content.replace("(VerifyDating - 5M+ Pagine)", "(IsBrokerSafe.com)")
    content = content.replace("(VerifyDating - 5M+ Pagini)", "(IsBrokerSafe.com)")
    content = content.replace("(VerifyDating - 5M+ Pages)", "(IsBrokerSafe.com)")
    
    # EN replacements
    if lang == "en":
        content = content.replace("over 5,000,000 auto-generated pages", "over 100,000 verified regulatory scam reports")
        content = content.replace("Traffic is dynamically geo-routed to premium Prop-Firm affiliate networks or EU brokers based on CFTC-compliance logic.", "Traffic is dynamically routed worldwide via a custom 4-zone global geo-location matrix, serving compliant premium Prop-Firm or EU broker affiliate networks based on regional laws.")
        content = content.replace("https://verifydating.net", "https://isbrokersafe.com")
        
    elif lang == "ro":
        content = content.replace("peste 5.000.000 de pagini autogenerate", "peste 100.000 de pagini cu rapoarte financiare reale")
        content = content.replace("Traficul organic este rutat dinamic prin Javascript către oferte premium de afiliere, în funcție de geolocalizare (SUA vs Europa).", "Traficul organic este împărțit mondial printr-o matrice de geo-localizare pe 4 zone, afișând dinamic oferte complet conforme cu legislația regională (Prop-Firms în SUA vs Brokeri reglementați în UE/Restul lumii).")
        content = content.replace("https://verifydating.net", "https://isbrokersafe.com")
        
    elif lang == "it":
        content = content.replace("oltre 5.000.000 di pagine auto-generate", "oltre 100.000 di pagine con report finanziari verificati")
        content = content.replace("Il traffico organico viene reindirizzato dinamicamente in base alla geolocalizzazione verso reti di affiliazione premium.", "Il traffico organico è instradato in tutto il mondo attraverso una matrice di geo-localizzazione a 4 zone, servendo offerte affiliate conformi alle leggi regionali (Prop-Firms negli USA vs Broker regolamentati in EU/Mondo).")
        content = content.replace("https://verifydating.net", "https://isbrokersafe.com")

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

update_file("index.html", "en")
update_file("ro/index.html", "ro")
update_file("it/index.html", "it")

print("Files updated!")
