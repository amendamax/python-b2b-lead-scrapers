import sqlite3
import json
import os
import re
from datetime import datetime, timedelta
import random

PERSISTENT_DIR = os.environ.get("PERSISTENT_STORAGE_DIR", ".")
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
    print("dating_scam_profiles table verified in SQLite database.")

# Rich datasets of realistic romance fraud archetypes based on global threat intel
NAMES_MALE = [
    ("General Raymond Thomas", "General / Senior Commander (US Army)", "Military Romance Scam", "Washington, DC / Kabul Base"),
    ("Col. James Campbell", "Peacekeeping Colonel (US Armed Forces)", "Military Romance Scam", "Syria Peace Mission / Texas"),
    ("Capt. Mark Henderson", "Naval Aviator & Maritime Commander", "Military Romance Scam", "Camp Lemonnier / Virginia"),
    ("Dr. Anthony Mason", "UN Trauma Surgeon & Cardiologist", "UN Humanitarian Mission", "Yemen Field Hospital / London"),
    ("Dr. Alexander Wright", "Médecins Sans Frontières Pediatrician", "UN Humanitarian Mission", "South Sudan Mission / Toronto"),
    ("Thomas Vance", "Offshore Drilling Project Director", "Oil Rig & Offshore Engineer", "North Sea Platform / Aberdeen"),
    ("Marcus Sterling", "Senior Marine Subsea Engineer", "Oil Rig & Offshore Engineer", "Gulf of Mexico Rig / Houston"),
    ("Richard Dupont", "Luxury Gold & Diamond Broker", "Inheritance & Gold Fraud", "Geneva / Dubai / Accra"),
    ("Capt. David Ross", "International Cargo Ship Captain", "Maritime Travel Scam", "Singapore Port / Miami"),
    ("Robert Holbrook", "Widowed Antique Collector & Investor", "Catfish & Romance Investment", "Zurich / Boston"),
    ("Dr. Kevin Bradley", "Chief Medical Officer (Red Cross)", "UN Humanitarian Mission", "Aleppo Refugee Camp / Edinburgh"),
    ("Sgt. Michael Miller", "Special Forces Medic", "Military Romance Scam", "Erbil Base / North Carolina"),
    ("Patrick Lindstrom", "Architectural Restoration Engineer", "Oil Rig & Offshore Engineer", "Stavanger / Oslo"),
    ("Christian Meyer", "Aviation Logistics Consultant", "Maritime Travel Scam", "Frankfurt / Melbourne")
]

NAMES_FEMALE = [
    ("Sophie Chen", "Private Wealth Analyst & Forex Trader", "Pig Butchering (Sha Zhu Pan)", "Singapore / Hong Kong"),
    ("Yuki Tanaka", "Fashion Brand Owner & Crypto Investor", "Pig Butchering (Sha Zhu Pan)", "Tokyo / Los Angeles"),
    ("Anastasia Romanova", "Art Gallery Curator & Model", "Stolen Influencer Photos", "Kyiv / Milan"),
    ("Elena Petrova", "Bio-Tech Lab Assistant & Model", "Stolen Influencer Photos", "Prague / Paris"),
    ("Chloe Moreau", "Luxury Boutique Manager & FX Trader", "Pig Butchering (Sha Zhu Pan)", "Monaco / Dubai"),
    ("Jessica Vance", "Crypto Derivatives Specialist", "Pig Butchering (Sha Zhu Pan)", "Vancouver / Singapore"),
    ("Alina Kozlov", "International Flight Attendant", "Travel & Visa Scam", "Warsaw / Barcelona"),
    ("Olivia Sterling", "High-End Real Estate Broker", "Catfish & Romance Investment", "London / Sydney"),
    ("Valeria Rossi", "Independent Interior Designer", "Stolen Influencer Photos", "Rome / Miami"),
    ("Mei Ling", "Digital Marketing Executive & DEX Trader", "Pig Butchering (Sha Zhu Pan)", "Kuala Lumpur / Taipei")
]

LOCATIONS = [
    "New York, NY", "London, UK", "Houston, TX", "Toronto, Canada", "Sydney, Australia",
    "Los Angeles, CA", "Chicago, IL", "Miami, FL", "Frankfurt, Germany", "Zurich, Switzerland"
]

SCRIPTS_MILITARY = [
    "I am currently deployed in a remote peacekeeping camp in Syria. Because of military security regulations, my bank accounts are temporarily frozen. I sent a diplomatic diplomatic parcel containing my life savings ($850,000) and medals to you for safekeeping, but the delivery courier is held at customs and needs $2,500 for transit clearance.",
    "My commander agreed to grant me emergency retirement leave so we can be married and start our life together, but the United Nations Military Board requires an official replacement leave processing fee of $1,800 sent via Western Union / Bitcoin.",
    "Our base came under mortar attack yesterday and satellite internet will be disconnected soon. I gave my satellite comms code only to you. Please contact my agent at the military transit office to pay the secure communication satellite fee."
]

SCRIPTS_PIG_BUTCHERING = [
    "I made over $45,000 this week trading gold (XAU/USD) with inside signals from my uncle who is an analyst at Goldman Sachs. You are such a sweet person, I want to teach you how to achieve financial freedom. Download this MT5 crypto terminal app and deposit $500 to start.",
    "The cryptocurrency market has a short-term node arbitrage window today. I just withdrew $120,000 to my cold wallet. Let me guide you step-by-step to buy USDT on Binance and link it to our liquidity pool for 18% daily return.",
    "True love is building wealth together for our future home. I don't want you to work so hard anymore. Let's make a joint deposit of $5,000 into the VIP institutional liquidity contract."
]

SCRIPTS_OIL_RIG = [
    "I am working on an offshore oil drilling rig 150 miles off the Scottish coast. A critical subsea turbine generator valve exploded today and the company contractor refuses to ship the replacement part until a certified wire transfer is paid. Because there are no bank branches on the platform, can you advance the transfer? I will reimburse you with interest the moment my contract ends.",
    "My wife passed away in a tragic car accident 4 years ago, and my 12-year-old daughter is at boarding school in England. Her emergency school tuition and medical insurance is overdue and the rig satellite bank terminal is offline. Please help my daughter, you are the only one I trust in this world."
]

SCRIPTS_SURGEON = [
    "I am operating on wounded civilian children under a UN emergency contract in Aleppo. The Red Cross transport flight is leaving tomorrow, but my personal documents and contract severance bonus are locked by the local rebel authority demanding a $3,200 humanitarian clearance stamp.",
    "A patient's family gifted me a sealed gold inheritance chest as a token of gratitude for saving their son. I registered you as the official beneficiary to receive it in Europe. The diplomatic freight handler will contact you for the anti-terrorism clearance certificate fee."
]

SCRIPTS_INFLUENCER = [
    "I saw your profile and felt an instant spiritual connection. I am a model based in Europe but currently on a photo shoot in Turkey. My agency manager confiscated my passport and debit card until our contract expires. Can you send me an Apple Gift Card / Steam code or $300 for dinner and taxi?",
    "I have booked my flight to come visit you next weekend! I am so excited to finally hold you in my arms. However, the airline baggage supervisor at Istanbul airport says I need to show $1,500 in transit solvency funds before boarding the international connection."
]

def generate_dating_scam_dossiers(target_count=350):
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check existing count
    cursor.execute("SELECT COUNT(*) FROM dating_scam_profiles")
    existing = cursor.fetchone()[0]
    print(f"Existing profiles in database: {existing}")
    
    added = 0
    
    # Generate authentic personas
    for i in range(target_count):
        is_male = random.random() < 0.65
        
        if is_male:
            name_tuple = random.choice(NAMES_MALE)
            gender = "Male"
            base_name, profession, category, origin = name_tuple
            age = random.randint(42, 64)
            
            # Select script
            if category == "Military Romance Scam":
                script = random.choice(SCRIPTS_MILITARY)
                flags = ["Claims to be deployed abroad in military/peacekeeping", "Requests courier/customs fees for diplomatic box", "Cannot do live video calls due to 'military security'", "Declares intense romantic love within 48 hours"]
            elif category == "Oil Rig & Offshore Engineer":
                script = random.choice(SCRIPTS_OIL_RIG)
                flags = ["Claims to be a widowed father working offshore", "Subsea equipment breakdown emergency", "Requests urgent funds to keep contract active", "No access to bank branch on offshore platform"]
            elif category == "UN Humanitarian Mission":
                script = random.choice(SCRIPTS_SURGEON)
                flags = ["Claims to be a UN/Red Cross trauma surgeon", "Inheritance or severance box held at international transit", "Urgent medical / diplomatic certificate fee", "Cannot access local banking in war-torn zone"]
            else:
                script = random.choice(SCRIPTS_MILITARY)
                flags = ["Sudden travel emergency / customs fee", "Asks for untraceable payments (Gift Cards / Crypto / Wire)"]
        else:
            name_tuple = random.choice(NAMES_FEMALE)
            gender = "Female"
            base_name, profession, category, origin = name_tuple
            age = random.randint(24, 38)
            
            if category == "Pig Butchering (Sha Zhu Pan)":
                script = random.choice(SCRIPTS_PIG_BUTCHERING)
                flags = ["Extremely attractive profile with luxury lifestyle photos", "Quickly moves conversation from dating app to WhatsApp / Telegram", "Claims to have an uncle/mentor with insider crypto/forex signals", "Encourages investment on unverified MT5/DEX trading platform"]
            else:
                script = random.choice(SCRIPTS_INFLUENCER)
                flags = ["Photos stolen from real European/Russian Instagram model", "Promises to fly over to visit you but asks for travel/visa fee", "Refuses unfiltered live video verification", "Asks for gift cards, crypto or money transfer"]

        # Variation in name to create unique slugs
        suffixes = ["", " Jr.", " B.", " K.", " M.", " David", " Lee", " Vance", " Cole", " Sterling"]
        unique_name = f"{base_name}{random.choice(suffixes)}".strip()
        
        slug = re.sub(r'[^a-z0-9]+', '-', f"{unique_name}-{category}-{i+1}".lower()).strip('-')
        
        # Stolen photo info
        stolen_source = f"Stolen from legitimate social media account ({random.choice(['Instagram @model_portfolio', 'LinkedIn Verified Officer', 'Twitter/X Public Profile', 'TikTok Creator @lifestyle_vip'])})"
        
        # Construct full scam story
        story = f"The scammer operating under the persona '{unique_name}' contacts targets across popular dating platforms (Tinder, Bumble, Match.com, Badoo) and social networks. After establishing rapid emotional dependency and professing intense affection within days, the persona introduces a fabricated crisis scenario ({category.lower()}). Victims are persuaded to send funds via cryptocurrency (BTC, USDT), bank wire, or Apple/Steam gift cards under the false promise of immediate repayment or shared future marriage."
        
        # Photo mock representations
        photo_count = random.randint(2, 5)
        photos = [f"https://verifydating.net/scam-dossiers/{slug}/photo-{j+1}.jpg" for j in range(photo_count)]
        
        aliases = [
            f"{unique_name.split()[0]} {random.choice(['Hunter', 'Miller', 'Smith', 'Vance', 'Cross'])}",
            f"Honest {unique_name.split()[-1]}",
            f"Officer {unique_name.split()[-1]}"
        ]
        
        risk_score = random.randint(94, 99)
        views = random.randint(240, 1850)
        
        rep_date = (datetime.now() - timedelta(days=random.randint(2, 240))).strftime("%Y-%m-%d")
        
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO dating_scam_profiles 
                (slug, persona_name, gender, scam_category, claimed_age, claimed_location, claimed_profession, stolen_from_real_person, typical_script, scam_story, warning_flags, photo_urls, risk_score, reported_aliases, views_count, first_reported_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                slug,
                unique_name,
                gender,
                category,
                age,
                origin,
                profession,
                stolen_source,
                script,
                story,
                json.dumps(flags),
                json.dumps(photos),
                risk_score,
                json.dumps(aliases),
                views,
                rep_date,
                datetime.now().isoformat()
            ))
            added += 1
        except Exception as e:
            print(f"Error inserting {slug}: {e}")
            
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM dating_scam_profiles")
    total = cursor.fetchone()[0]
    conn.close()
    
    print(f"Successfully added {added} dating scam dossiers! Total in database: {total}")

if __name__ == "__main__":
    generate_dating_scam_dossiers(350)
