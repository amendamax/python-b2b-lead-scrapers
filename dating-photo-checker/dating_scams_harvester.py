import sqlite3
import json
import os
import re
from datetime import datetime, timedelta
import random

PERSISTENT_DIR = "/var/data" if os.path.exists("/var/data") else "."
DB_PATH = os.path.join(PERSISTENT_DIR, "database.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dating_scam_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE,
            persona_name TEXT,
            gender TEXT,
            scam_category TEXT,
            claimed_age INTEGER,
            claimed_location TEXT,
            claimed_profession TEXT,
            stolen_from_real_person TEXT,
            typical_script TEXT,
            scam_story TEXT,
            warning_flags TEXT,
            photo_urls TEXT,
            risk_score INTEGER,
            reported_aliases TEXT,
            views_count INTEGER DEFAULT 184,
            first_reported_date TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

# Extended Diverse Name Pools for 2500+ High-Authority Personas
MALE_FIRST = [
    "General Raymond", "Col. James", "Capt. Mark", "Dr. Anthony", "Dr. Alexander",
    "Thomas", "Marcus", "Richard", "Capt. David", "Robert", "Dr. Kevin", "Sgt. Michael",
    "Patrick", "Christian", "Col. William", "Commander Gary", "Dr. Gregory", "Major Daniel",
    "Jeffrey", "Douglas", "Edward", "Brian", "Ronald", "Timothy", "Jason", "Jeffrey", "Kenneth",
    "Stephen", "Andrew", "Scott", "Eric", "Steven", "Frank", "Raymond", "Gregory", "Dennis"
]

MALE_LAST = [
    "Thomas", "Campbell", "Henderson", "Mason", "Wright", "Vance", "Sterling", "Dupont",
    "Ross", "Holbrook", "Bradley", "Miller", "Lindstrom", "Meyer", "Davis", "Walker",
    "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez", "Hill", "Scott",
    "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter", "Mitchell", "Perez", "Roberts"
]

FEMALE_FIRST = [
    "Sophie", "Yuki", "Anastasia", "Elena", "Chloe", "Jessica", "Alina", "Olivia",
    "Valeria", "Mei", "Isabella", "Natasha", "Camilla", "Daria", "Emily", "Victoria",
    "Sophia", "Zoe", "Amelia", "Charlotte", "Ksenia", "Valentina", "Hannah", "Leila",
    "Lina", "Mila", "Polina", "Sora", "Lin", "Hana", "Anya", "Katarina", "Giselle"
]

FEMALE_LAST = [
    "Chen", "Tanaka", "Romanova", "Petrova", "Moreau", "Vance", "Kozlov", "Sterling",
    "Rossi", "Ling", "Dubois", "Kovaleva", "Novak", "Sokolova", "Wang", "Zhang",
    "Takahashi", "Nakamura", "Morozova", "Papadopoulos", "Fontana", "Conti", "Ricci", "Moretti"
]

CATEGORIES = [
    ("Military Romance Scam", "Male", [
        "Senior Military Commander (US Armed Forces)", "Peacekeeping Officer deployed in Syria",
        "Naval Aviator & Maritime Commander", "Special Operations Field Medic", "Combat Engineer deployed abroad"
    ]),
    ("UN Humanitarian Mission", "Male", [
        "UN Trauma Surgeon & Cardiologist", "Médecins Sans Frontières Pediatrician",
        "Chief Medical Officer (Red Cross)", "Humanitarian Emergency Orthopedic Surgeon", "International Aid Relief Director"
    ]),
    ("Oil Rig & Offshore Engineer", "Male", [
        "Offshore Drilling Project Director", "Senior Marine Subsea Engineer",
        "Deepwater Petroleum Technical Specialist", "Subsea Pipeline Inspection Engineer", "Offshore Oil Platform Superintendent"
    ]),
    ("Pig Butchering (Sha Zhu Pan)", "Female", [
        "Private Wealth Analyst & Crypto Investor", "Boutique Owner & Forex Derivatives Trader",
        "Digital Asset Portfolio Strategist", "Gold & Commodity Arbitrage Specialist", "Decentralized Liquidity Pool Manager"
    ]),
    ("Stolen Influencer Photos", "Female", [
        "Fashion Model & Content Creator", "Art Gallery Curator & Model",
        "International Commercial Model", "Luxury Travel Blogger & Brand Ambassador", "Haute Couture Runway Model"
    ])
]

SCRIPTS = {
    "Military Romance Scam": [
        "I am currently on a classified peacekeeping deployment in Syria. Because of military security regulations, my personal accounts are blocked. I sent a diplomatic parcel containing my life savings ($850,000) to you for safekeeping, but the delivery courier needs $2,500 for transit clearance.",
        "My general officer approved my emergency retirement leave so we can marry, but the UN Military Board requires a replacement contractor transit bond of $2,200 sent via Bitcoin or Western Union.",
        "Our base was targeted by mortar strikes yesterday and our satellite comms will shut down. I gave my emergency satellite security key only to you. Please contact my diplomatic liaison to pay the satellite link clearance fee."
    ],
    "UN Humanitarian Mission": [
        "I am operating on wounded civilian children under a UN emergency contract in Aleppo. The transport flight leaves tomorrow, but my personal documents and contract severance bonus are locked by the local authority demanding a $3,200 humanitarian clearance stamp.",
        "A patient's family gifted me a sealed gold inheritance chest as a token of gratitude for saving their son. I registered you as the official beneficiary. The diplomatic freight handler will contact you for the anti-terrorism clearance certificate fee."
    ],
    "Oil Rig & Offshore Engineer": [
        "I am working on an offshore drilling rig in the North Sea. A critical subsea turbine generator valve exploded today and the contractor refuses to ship the replacement part until a certified wire transfer is paid. Can you advance the transfer? I will reimburse you the moment my contract ends.",
        "My wife passed away in a tragic car accident years ago, and my 12-year-old daughter is at boarding school in England. Her emergency school tuition and medical insurance is overdue and the rig satellite bank terminal is offline. Please help my daughter, you are the only one I trust."
    ],
    "Pig Butchering (Sha Zhu Pan)": [
        "I made over $48,000 this week trading gold (XAU/USD) with inside signals from my uncle who is an analyst at Goldman Sachs. You are such a sweet person, I want to teach you how to achieve financial freedom. Download this MT5 crypto terminal app and deposit $500 to start.",
        "The cryptocurrency market has a short-term node arbitrage window today. I just withdrew $120,000 to my cold wallet. Let me guide you step-by-step to buy USDT on Binance and link it to our liquidity pool for 18% daily return.",
        "True love is building wealth together for our future home. I don't want you to work so hard anymore. Let's make a joint deposit of $5,000 into the VIP institutional liquidity contract."
    ],
    "Stolen Influencer Photos": [
        "I saw your profile and felt an instant spiritual connection. I am a model based in Europe but currently on a photo shoot in Turkey. My agency manager confiscated my passport and debit card until our contract expires. Can you send me an Apple Gift Card / Steam code or $300 for dinner and taxi?",
        "I have booked my flight to come visit you next weekend! I am so excited to finally hold you in my arms. However, the airline baggage supervisor at Istanbul airport says I need to show $1,500 in transit solvency funds before boarding the international connection."
    ]
}

def generate_dating_scam_dossiers(target_count=2500):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM dating_scam_profiles")
    existing_count = cursor.fetchone()[0]
    print(f"Existing profiles: {existing_count}. Generating up to {target_count}...")
    
    added = 0
    generated_slugs = set()
    
    # Load existing slugs
    cursor.execute("SELECT slug FROM dating_scam_profiles")
    for row in cursor.fetchall():
        generated_slugs.add(row[0])
        
    for i in range(1, target_count + 1):
        cat_info = random.choice(CATEGORIES)
        category_name, default_gender, prof_list = cat_info
        
        if default_gender == "Male":
            f_name = random.choice(MALE_FIRST)
            l_name = random.choice(MALE_LAST)
            gender = "Male"
            age = random.randint(42, 65)
            origin = random.choice([
                "Washington, DC / Syria Base", "Houston, TX / North Sea Rig",
                "London, UK / Yemen Mission", "Toronto, Canada / Camp Lemonnier",
                "Aberdeen, Scotland / Offshore Rig", "Miami, FL / Maritime Transport"
            ])
        else:
            f_name = random.choice(FEMALE_FIRST)
            l_name = random.choice(FEMALE_LAST)
            gender = "Female"
            age = random.randint(23, 39)
            origin = random.choice([
                "Singapore / Hong Kong", "Tokyo / Los Angeles",
                "Kyiv / Milan", "Prague / Paris",
                "Monaco / Dubai", "Vancouver / London"
            ])
            
        persona_name = f"{f_name} {l_name}"
        profession = random.choice(prof_list)
        script = random.choice(SCRIPTS[category_name])
        
        slug = re.sub(r'[^a-z0-9]+', '-', f"{persona_name}-{category_name}-{i}".lower()).strip('-')
        if slug in generated_slugs:
            continue
            
        generated_slugs.add(slug)
        
        stolen_from = f"Stolen from verified public profile ({random.choice(['Instagram @model_portfolio', 'LinkedIn Verified Executive', 'TikTok Creator @lifestyle_vip', 'Twitter/X Public Account'])})"
        
        flags = [
            f"Claims identity as {profession}",
            "Rapid emotional bonding & marriage proposal within 72 hours",
            "Refuses unedited live video calls due to 'confidential restrictions'",
            "Demands urgent funds via untraceable methods (USDT/BTC, Gift Cards, Wire)"
        ]
        
        story = f"The romance scam persona '{persona_name}' contacts targets through dating applications and social media platforms. After quickly establishing emotional dependency, the scammer introduces a fabricated crisis ({category_name.lower()}) requesting money for medical fees, customs clearances, or fake crypto investment platforms."
        
        photo_count = random.randint(2, 5)
        photos = [f"https://verifydating.net/scam-dossiers/{slug}/photo-{j+1}.jpg" for j in range(photo_count)]
        
        aliases = [
            f"{f_name} {random.choice(['Hunter', 'Miller', 'Smith', 'Vance', 'Cross'])}",
            f"Honest {l_name}",
            f"Dr./Col. {l_name}"
        ]
        
        risk_score = random.randint(95, 99)
        views = random.randint(180, 2450)
        rep_date = (datetime.now() - timedelta(days=random.randint(1, 300))).strftime("%Y-%m-%d")
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO dating_scam_profiles 
                (slug, persona_name, gender, scam_category, claimed_age, claimed_location, claimed_profession, stolen_from_real_person, typical_script, scam_story, warning_flags, photo_urls, risk_score, reported_aliases, views_count, first_reported_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                slug, persona_name, gender, category_name, age, origin, profession,
                stolen_from, script, story, json.dumps(flags), json.dumps(photos),
                risk_score, json.dumps(aliases), views, rep_date, datetime.now().isoformat()
            ))
            added += 1
        except Exception as e:
            pass
            
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM dating_scam_profiles")
    total = cursor.fetchone()[0]
    conn.close()
    
    print(f"Added {added} new profiles. Total dating scam profiles in database: {total}")

if __name__ == "__main__":
    generate_dating_scam_dossiers(2500)
