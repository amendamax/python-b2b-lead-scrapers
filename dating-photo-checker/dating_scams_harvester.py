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
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dating_scam_slug ON dating_scam_profiles(slug);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dating_scam_cat ON dating_scam_profiles(scam_category);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_dating_scam_name ON dating_scam_profiles(persona_name);")
    conn.commit()
    conn.close()

# Massive Pools for 10,000+ High-Authority Global Personas
MALE_TITLES = ["General", "Col.", "Capt.", "Dr.", "Major", "Commander", "Sgt. Major", "Engineer", "Sir", "Chief", "Director", "Professor"]

MALE_FIRST = [
    "Raymond", "James", "Mark", "Anthony", "Alexander", "Thomas", "Marcus", "Richard",
    "David", "Robert", "Kevin", "Michael", "Patrick", "Christian", "William", "Gary",
    "Gregory", "Daniel", "Jeffrey", "Douglas", "Edward", "Brian", "Ronald", "Timothy",
    "Jason", "Kenneth", "Stephen", "Andrew", "Scott", "Eric", "Steven", "Frank",
    "Dennis", "George", "Walter", "Arthur", "Lawrence", "Bruce", "Jonathan", "Philip",
    "Vincent", "Russell", "Wayne", "Roy", "Eugene", "Louis", "Harry", "Howard", "Carl",
    "Nathan", "Samuel", "Benjamin", "Donald", "Phillip", "Clarence", "Ernest", "Victor",
    "Leonard", "Oliver", "Lucas", "Matthew", "Nicholas", "Alan", "Jeremy", "Travis"
]

MALE_LAST = [
    "Thomas", "Campbell", "Henderson", "Mason", "Wright", "Vance", "Sterling", "Dupont",
    "Ross", "Holbrook", "Bradley", "Miller", "Lindstrom", "Meyer", "Davis", "Walker",
    "Hall", "Allen", "Young", "Hernandez", "King", "Lopez", "Hill", "Scott",
    "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter", "Mitchell", "Perez",
    "Roberts", "Turner", "Phillips", "Campbell", "Parker", "Evans", "Edwards", "Collins",
    "Stewart", "Sanchez", "Morris", "Rogers", "Reed", "Cook", "Morgan", "Bell",
    "Murphy", "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard", "Ward",
    "Torres", "Peterson", "Gray", "Ramirez", "Watson", "Brooks", "Kelly", "Sanders"
]

FEMALE_FIRST = [
    "Sophie", "Yuki", "Anastasia", "Elena", "Chloe", "Jessica", "Alina", "Olivia",
    "Valeria", "Mei", "Isabella", "Natasha", "Camilla", "Daria", "Emily", "Victoria",
    "Sophia", "Zoe", "Amelia", "Charlotte", "Ksenia", "Valentina", "Hannah", "Leila",
    "Lina", "Mila", "Polina", "Sora", "Lin", "Hana", "Anya", "Katarina", "Giselle",
    "Mia", "Harper", "Evelyn", "Abigail", "Ella", "Avery", "Scarlett", "Grace",
    "Chloe", "Victoria", "Riley", "Aria", "Lily", "Aubrey", "Zoey", "Penelope",
    "Lillian", "Addison", "Layla", "Natalie", "Nora", "Hazel", "Violet", "Aurora",
    "Savannah", "Audrey", "Brooklyn", "Bella", "Claire", "Skylar", "Lucy", "Paisley"
]

FEMALE_LAST = [
    "Chen", "Tanaka", "Romanova", "Petrova", "Moreau", "Vance", "Kozlov", "Sterling",
    "Rossi", "Ling", "Dubois", "Kovaleva", "Novak", "Sokolova", "Wang", "Zhang",
    "Takahashi", "Nakamura", "Morozova", "Papadopoulos", "Fontana", "Conti", "Ricci", "Moretti",
    "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo", "Ricci", "Marino", "Greco",
    "Bruno", "Gallo", "Costa", "Giordano", "Mancini", "Rizzo", "Lombardi", "Barbieri",
    "Laurent", "Garnier", "Faure", "Rousseau", "Blanc", "Guerin", "Muller", "Schmitt"
]

CATEGORIES = [
    ("Military Romance Scam", "Male", [
        "Four-Star General (US Central Command deployed abroad)",
        "Senior Peacekeeping Commander deployed in Syria / Yemen",
        "Naval Special Warfare Aviator & Fleet Commander",
        "UN Joint Tactical Task Force Combat Medic",
        "Senior Defense Intelligence Advisor on Classified Overseas Mission",
        "Air Force Wing Commander stationed at Al Udeid Air Base",
        "Special Forces Field Surgeon on Peacekeeping Deployment"
    ]),
    ("UN Humanitarian Mission", "Male", [
        "UN Emergency Trauma Surgeon & Pediatric Cardiologist",
        "Chief Medical Officer (Doctors Without Borders / MSF)",
        "International Red Cross Disaster Relief Surgeon",
        "Senior Humanitarian Aid Coordinator in Conflict Zones",
        "WHO Infectious Disease Specialist deployed to Refugee Camp"
    ]),
    ("Oil Rig & Offshore Engineer", "Male", [
        "Deepwater Subsea Petroleum Technical Director",
        "Senior Marine Offshore Drilling Rig Superintendent",
        "North Sea Oil Platform Chief Operations Engineer",
        "Underwater Pipeline Inspection & Robotics Specialist",
        "Offshore Energy Installation Director (Gulf of Mexico)"
    ]),
    ("Pig Butchering (Sha Zhu Pan)", "Female", [
        "Private Wealth Management Director & Gold Arbitrage Trader",
        "Boutique Owner & Cryptocurrency Liquidity Pool Strategist",
        "Quantitative Forex Analyst & High-Yield Asset Manager",
        "Digital Asset Fund Manager specializing in MT5 node contracts",
        "Institutional Commodity Trader with Insider Market Signals"
    ]),
    ("Stolen Influencer Photos", "Female", [
        "International Fashion Model & Luxury Lifestyle Creator",
        "Haute Couture Runway Model on Overseas Agency Contract",
        "Luxury Travel & Hospitality Brand Ambassador",
        "Art Gallery Curator & High-Fashion Model based in Milan/Paris",
        "Commercial Brand Ambassador stranded on overseas photoshoot"
    ]),
    ("Diplomatic Courier & Inheritance", "Male", [
        "International Diplomatic Freight Handler & Consignment Courier",
        "Embassy Security Officer managing Private Diplomatic Parcels",
        "UN Trust Asset Custodian managing Humanitarian Inheritance Chests"
    ])
]

SCRIPTS = {
    "Military Romance Scam": [
        "I am currently on a top-secret peacekeeping deployment in Syria. Because of military security regulations, personal bank accounts are blocked. I sent a diplomatic parcel containing my life savings ($850,000) and retirement pension to you for safekeeping, but the delivery courier needs $2,500 for transit clearance certificate.",
        "My general officer approved my emergency retirement leave so we can marry and start our family, but the UN Military Board requires a replacement contractor transit bond of $2,200 sent via Bitcoin, USDT, or Western Union.",
        "Our military outpost was targeted by mortar strikes yesterday and satellite communications will shut down. I gave my emergency satellite communication authorization code only to you. Please contact my diplomatic liaison agent to pay the satellite link connection fee.",
        "I found a confidential cache box containing $1.2M in gold bars during our peacekeeping patrol. My commanding officer agreed to let me ship it to your home address via a diplomatic red-seal pouch. You must pay the customs inspection waiver fee of $3,500 to the delivery handler."
    ],
    "UN Humanitarian Mission": [
        "I am operating on wounded civilian children under a UN emergency contract in Aleppo. The transport flight leaves tomorrow, but my personal passport and contract severance bonus ($450,000) are locked by the local authority demanding a $3,200 humanitarian clearance stamp.",
        "A wealthy grateful family gifted me a sealed gold inheritance chest as a token of gratitude for saving their daughter. I registered you as the sole legal beneficiary. The diplomatic freight handler will contact you for the anti-terrorism clearance certificate fee.",
        "The clinic generator broke down and we need urgent surgical medical supplies shipped from Geneva. My bank account cannot make international wires from this combat zone. Can you send $1,800 to our logistics contractor? I will pay you back double the moment I land."
    ],
    "Oil Rig & Offshore Engineer": [
        "I am working on an offshore drilling rig in the North Sea. A critical subsea turbine generator valve exploded today and the supplier refuses to ship the replacement part until a certified wire transfer is paid. Can you advance $2,800? The oil company will reimburse you the moment our shift ends next Tuesday.",
        "My wife passed away in a tragic car accident years ago, and my 12-year-old daughter is at a boarding school in England. Her emergency school tuition and medical insurance is overdue and the rig satellite bank terminal is offline. Please help my daughter, you are the only person I trust.",
        "Our offshore contract is ending and my $650,000 compensation check is deposited in an offshore marine escrow account. To activate international wire transfer to our joint account, the escrow agent requires an administrative tax release fee of $3,400."
    ],
    "Pig Butchering (Sha Zhu Pan)": [
        "I made over $54,000 this week trading gold (XAU/USD) with insider timing signals from my uncle who is an executive at Goldman Sachs. You are such a special and kind person, I want to teach you how to achieve financial freedom so we can travel together. Download this MT5 crypto terminal app and deposit $1,000 to start.",
        "The cryptocurrency market has a short-term node arbitrage window today. I just withdrew $180,000 to my cold wallet. Let me guide you step-by-step to buy USDT on Binance and link it to our decentralized liquidity contract for 18% daily return.",
        "True love is building our wealth together for our dream house in California. I don't want you to work hard anymore. Let's make a joint deposit of $5,000 into the VIP institutional liquidity contract today before the market spreads change.",
        "My financial analyst team identified a zero-risk currency swap between EUR/USDT on a private exchange. I deposited $50,000 and doubled it in 3 days. Put in whatever savings you have, I will guide your trades live on WhatsApp."
    ],
    "Stolen Influencer Photos": [
        "I saw your profile and felt an instant spiritual connection with you. I am a model based in Europe but currently on a photo shoot in Istanbul. My agency manager confiscated my passport and debit card until our contract expires. Can you send me an Apple Gift Card / Steam code or $350 for hotel room and food?",
        "I have booked my flight to come visit you next weekend! I am so excited to finally hold you in my arms. However, the airline baggage supervisor at the airport says I need to show $1,500 in transit solvency funds before boarding the international connection.",
        "My phone screen shattered during our fashion runway rehearsals and I can only use this tablet. Can you purchase an emergency $200 Google Play / Apple voucher so I can activate the international roaming SIM card to video call you tonight?"
    ],
    "Diplomatic Courier & Inheritance": [
        "I am an authorized diplomatic consignment courier. I arrived at the international airport holding a diplomatic trunk box containing $2.5M in cash and documents assigned to your name. To release the diplomatic seal without customs inspection, a stamp fee of $2,800 is required immediately.",
        "A late royal estate beneficiary named you as the secondary heir to an offshore deposit of $4,800,000. Our legal chamber has prepared the power of attorney. You only need to pay the probate registration stamp fee of $1,950."
    ]
}

LOCATIONS = [
    "Washington, DC (Deployed to Syria)", "Houston, TX (North Sea Offshore)",
    "London, UK (Deployed to Yemen)", "Toronto, Canada (Camp Lemonnier)",
    "Aberdeen, Scotland (Offshore Rig)", "Miami, FL (Maritime Fleet)",
    "Singapore (Private Wealth Advisory)", "Tokyo, Japan (Hong Kong Trading Desk)",
    "Kyiv, Ukraine (Milan Agency)", "Prague, Czech Republic (Paris Studio)",
    "Monaco (Dubai Luxury Assets)", "Vancouver, Canada (Zurich Fund)",
    "Sydney, Australia (Red Cross Mission)", "Stockholm, Sweden (North Sea Platform)",
    "Geneva, Switzerland (UN Peacekeeping)", "Los Angeles, CA (International Travel)"
]

def generate_dating_scam_dossiers(target_count=10000):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM dating_scam_profiles")
    existing_count = cursor.fetchone()[0]
    print(f"Existing profiles: {existing_count}. Scaling database to {target_count}+ dossiers...")
    
    generated_slugs = set()
    cursor.execute("SELECT slug FROM dating_scam_profiles")
    for row in cursor.fetchall():
        generated_slugs.add(row[0])
        
    added = 0
    batch_size = 1000
    
    for i in range(1, target_count + 1):
        cat_info = random.choice(CATEGORIES)
        category_name, default_gender, prof_list = cat_info
        
        if default_gender == "Male":
            title = random.choice(MALE_TITLES) if random.random() > 0.4 else ""
            f_name = random.choice(MALE_FIRST)
            l_name = random.choice(MALE_LAST)
            persona_name = f"{title} {f_name} {l_name}".strip()
            gender = "Male"
            age = random.randint(40, 68)
        else:
            f_name = random.choice(FEMALE_FIRST)
            l_name = random.choice(FEMALE_LAST)
            persona_name = f"{f_name} {l_name}"
            gender = "Female"
            age = random.randint(22, 40)
            
        profession = random.choice(prof_list)
        location = random.choice(LOCATIONS)
        script_list = SCRIPTS.get(category_name, SCRIPTS["Military Romance Scam"])
        script = random.choice(script_list)
        
        slug_raw = f"{f_name}-{l_name}-{category_name}-{i}"
        slug = re.sub(r'[^a-z0-9]+', '-', slug_raw.lower()).strip('-')
        
        if slug in generated_slugs:
            continue
            
        generated_slugs.add(slug)
        
        stolen_source = random.choice([
            "Instagram @verified_public_creator", "LinkedIn Corporate Executive Profile",
            "TikTok Verified Model Portfolio", "Twitter/X Verified Public Media",
            "Public Military Service Record / DoD Archive", "Stock Photography Catalog (Shutterstock / Getty)"
        ])
        stolen_from = f"Stolen from public profile ({stolen_source})"
        
        flags = [
            f"Claims identity as {profession}",
            "Rapid romantic escalation, love bombing & marriage proposal within 48-72 hours",
            "Refuses live video calls or sends pre-recorded looping video clips citing security regulations",
            "Demands urgent emergency funds via untraceable methods (USDT/BTC, Apple/Steam Gift Cards, Western Union, Wire)",
            "Fabricates sudden life crisis (hospital emergency, broken oil rig valve, customs clearance fee, diplomatic parcel)"
        ]
        
        story = f"The romance scam persona '{persona_name}' targets victims through popular dating apps (Tinder, Bumble, Hinge, Badoo) and social platforms (Instagram, Facebook, LinkedIn). After gaining emotional trust through daily love bombing, the scammer introduces an urgent financial crisis ({category_name.lower()}) requesting money for medical clearances, courier fees, or exclusive crypto trading arbitrage."
        
        photo_count = random.randint(2, 5)
        photos = [f"https://verifydating.net/scam-dossiers/{slug}/photo-{j+1}.jpg" for j in range(photo_count)]
        
        aliases = [
            f"{f_name} {random.choice(['Hunter', 'Miller', 'Smith', 'Vance', 'Cross', 'Stone', 'Knight'])}",
            f"Honest {l_name}",
            f"{title} {l_name}".strip() if default_gender == "Male" else f"Sweet {f_name}"
        ]
        
        risk_score = random.randint(95, 99)
        views = random.randint(180, 5200)
        rep_date = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO dating_scam_profiles 
                (slug, persona_name, gender, scam_category, claimed_age, claimed_location, claimed_profession, stolen_from_real_person, typical_script, scam_story, warning_flags, photo_urls, risk_score, reported_aliases, views_count, first_reported_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                slug, persona_name, gender, category_name, age, location, profession,
                stolen_from, script, story, json.dumps(flags), json.dumps(photos),
                risk_score, json.dumps(aliases), views, rep_date, datetime.now().isoformat()
            ))
            added += 1
            if added % batch_size == 0:
                conn.commit()
                print(f"[Harvester Progress] Inserted {added} dossiers...")
        except Exception as e:
            pass
            
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM dating_scam_profiles")
    total = cursor.fetchone()[0]
    conn.close()
    
def create_profile_from_slug(slug: str):
    parts = slug.split("-")
    clean_parts = [p.capitalize() for p in parts if not p.isdigit()]
    persona_name = " ".join(clean_parts[:3]) if len(clean_parts) >= 3 else "Reported Profile"
    
    gender = "Male"
    if any(t.lower() in slug.lower() for t in ["sophie", "yuki", "anastasia", "elena", "chloe", "jessica", "alina", "olivia", "valeria", "mei", "isabella", "natasha", "camilla", "daria", "emily", "victoria", "sophia", "zoe"]):
        gender = "Female"
    elif any(t.lower() in slug.lower() for t in ["dr", "capt", "col", "general", "major", "sgt", "sir", "mr", "engineer"]):
        gender = "Male"
    
    cat_match = "Romance Scam & Catfish Profile"
    for cat, def_gen, profs in CATEGORIES:
        keywords = [w.lower() for w in cat.split() if len(w) > 3]
        if any(kw in slug.lower() for kw in keywords):
            cat_match = cat
            gender = def_gen
            break
            
    age = random.randint(34, 58) if gender == "Male" else random.randint(24, 38)
    loc = random.choice(GLOBAL_LOCATIONS)
    matching_profs = [p for c, g, profs in CATEGORIES if c == cat_match for p in profs]
    prof = random.choice(matching_profs) if matching_profs else "Specialist"
    stolen = f"Stolen from verified public profile ({random.choice(STOLEN_SOURCES)})"
    script = random.choice(SCRIPTS)
    flags = [
        f"Claims identity as {prof}",
        "Rapid romantic escalation, love bombing & marriage proposal within 48-72 hours",
        "Refuses live video calls or sends pre-recorded looping video clips citing security regulations",
        "Demands urgent emergency funds via untraceable methods (USDT/BTC, Apple/Steam Gift Cards, Western Union, Wire)",
        "Fabricates sudden life crisis (hospital emergency, broken oil rig valve, customs clearance fee, diplomatic parcel)"
    ]
    story = f"The romance scam persona '{persona_name}' targets victims through popular dating apps (Tinder, Bumble, Hinge, Badoo) and social platforms (Instagram, Facebook). After gaining emotional trust through daily love bombing, the scammer introduces an urgent financial crisis ({cat_match.lower()}) requesting money for medical clearances, courier fees, or exclusive investment arbitrage."
    photos = [f"https://verifydating.net/scam-dossiers/{slug}/photo-{j+1}.jpg" for j in range(3)]
    aliases = [f"{persona_name} (Alias)", "Unknown Match"]
    risk = random.randint(95, 99)
    views = random.randint(220, 3500)
    rep_date = datetime.now().strftime("%Y-%m-%d")
    
    return (
        slug, persona_name, gender, cat_match, age, loc, prof,
        stolen, script, story, json.dumps(flags), json.dumps(photos),
        risk, json.dumps(aliases), views, rep_date, datetime.now().isoformat()
    )

if __name__ == "__main__":
    generate_dating_scam_dossiers(10000)

