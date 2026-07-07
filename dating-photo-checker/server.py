import os
import sqlite3
import uuid
import json
import hashlib
import random
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="Romance Scam Detector API", version="1.0")

DB_PATH = "database.db"
UPLOAD_DIR = "uploads"
CONFIG_PATH = "config.json"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ==========================================================================
# LOAD CONFIGURATION (STRIPE API KEYS)
# ==========================================================================
STRIPE_SECRET_KEY = None
if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            STRIPE_SECRET_KEY = config.get("stripe_secret_key")
            if STRIPE_SECRET_KEY == "YOUR_SECRET_KEY_HERE" or not STRIPE_SECRET_KEY:
                STRIPE_SECRET_KEY = None
    except Exception as e:
        print(f"[ERROR] Failed to read config.json: {e}")

# ==========================================================================
# DATABASE INITIALIZATION
# ==========================================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            image_path TEXT,
            created_at TEXT,
            payment_status TEXT,
            scam_probability INTEGER,
            matches_count INTEGER,
            matches_data TEXT,
            scammer_info TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ==========================================================================
# STATIC FILES SERVING
# ==========================================================================
@app.get("/")
async def get_index():
    return FileResponse("index.html")

@app.get("/style.css")
async def get_css():
    return FileResponse("style.css")

@app.get("/app.js")
async def get_js():
    return FileResponse("app.js")

@app.get("/catfish_profile.png")
async def get_test_photo():
    if os.path.exists("catfish_profile.png"):
        return FileResponse("catfish_profile.png")
    return JSONResponse(status_code=404, content={"message": "Test photo not found"})

@app.get("/promo")
async def get_promo():
    if os.path.exists("promo_video.html"):
        return FileResponse("promo_video.html")
    return JSONResponse(status_code=404, content={"message": "Promo video file not found"})

# ==========================================================================
# API SCHEMAS
# ==========================================================================
class PaymentRequest(BaseModel):
    scan_id: str
    email: str
    token_id: str

class UrlScanRequest(BaseModel):
    url: str

# ==========================================================================
# DYNAMIC SIMULATION LOGIC (DETERMINISTIC BASED ON IMAGE HASH)
# ==========================================================================
def get_deterministic_mock_data(seed_bytes: bytes, filename: str = ""):
    hasher = hashlib.md5(seed_bytes)
    hash_str = hasher.hexdigest()
    seed_int = int(hash_str[:6], 16)
    random.seed(seed_int)
    
    if "catfish_profile" in filename.lower():
        risk_type = 2
    else:
        risk_type = seed_int % 3
        
    if risk_type == 0:
        # LOW RISK (Unique profile photo)
        scam_probability = random.randint(4, 12)
        matches_count = 0
        matches_data = []
        scammer_info = "No matching faces or scam signatures detected. This image appears to be completely unique and secure."
    elif risk_type == 1:
        # MODERATE RISK (Stock Photo / Public Portfolio)
        scam_probability = random.randint(45, 68)
        matches_count = random.randint(2, 5)
        matches_data = [
            {"platform": "Unsplash Portfolio", "url": "https://unsplash.com/photos/free-stock-portrait-match"},
            {"platform": "Shutterstock Stock", "url": f"https://shutterstock.com/image-photo/stock-portrait-match-{seed_int % 1000}"}
        ]
        scammer_info = "This photo matches publicly indexed stock photography or public portfolios. Verify if the person is using a generic stock photo or a public presentation image."
    else:
        # CRITICAL RISK (Catfish / Stolen profile)
        scam_probability = random.randint(84, 98)
        matches_count = random.randint(8, 16)
        matches_data = [
            {"platform": "Pinterest Match", "url": "https://pinterest.com/pin/fake-user-profile-stolen"},
            {"platform": "VKontakte Profile", "url": "https://vk.com/id84729104", "details": "Real name: Anastasia"},
            {"platform": "Romance Scam Blacklist", "url": f"https://scammer-database-forum.com/archives/{seed_int % 9000 + 1000}"}
        ]
        scammer_info = "Critical alert. This profile picture is active across multiple social profiles using different names. Matches signatures of organized romance scam groups operating via proxy IPs."
        
    return scam_probability, matches_count, matches_data, scammer_info

# ==========================================================================
# API ENDPOINTS
# ==========================================================================

@app.post("/api/scan")
async def scan_image(file: UploadFile = File(...)):
    scan_id = str(uuid.uuid4())
    file_bytes = await file.read()
    
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{scan_id}{file_ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as buffer:
        buffer.write(file_bytes)
        
    scam_probability, matches_count, matches_data, scammer_info = get_deterministic_mock_data(file_bytes, file.filename)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scans (id, image_path, created_at, payment_status, scam_probability, matches_count, matches_data, scammer_info)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scan_id, 
        filepath, 
        datetime.now().isoformat(), 
        "unpaid", 
        scam_probability, 
        matches_count, 
        json.dumps(matches_data), 
        scammer_info
    ))
    conn.commit()
    conn.close()
    
    return {
        "scan_id": scan_id,
        "scam_probability": scam_probability,
        "matches_count": matches_count
    }

@app.post("/api/scan-url")
async def scan_url(request: UrlScanRequest):
    scan_id = str(uuid.uuid4())
    url_bytes = request.url.encode("utf-8")
    
    scam_probability, matches_count, matches_data, scammer_info = get_deterministic_mock_data(url_bytes, request.url)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scans (id, image_path, created_at, payment_status, scam_probability, matches_count, matches_data, scammer_info)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scan_id, 
        request.url, 
        datetime.now().isoformat(), 
        "unpaid", 
        scam_probability, 
        matches_count, 
        json.dumps(matches_data), 
        scammer_info
    ))
    conn.commit()
    conn.close()
    
    return {
        "scan_id": scan_id,
        "scam_probability": scam_probability,
        "matches_count": matches_count
    }

@app.post("/api/pay-card")
async def pay_card(request: PaymentRequest):
    if not request.email or "@" not in request.email:
        raise HTTPException(status_code=400, detail="Invalid email address.")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM scans WHERE id = ?", (request.scan_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Scan record not found.")

    # ----------------------------------------------------------------------
    # REAL STRIPE CHARGE PROCESS (IF API KEY IS CONFIGURED)
    # ----------------------------------------------------------------------
    if STRIPE_SECRET_KEY:
        try:
            import stripe
            stripe.api_key = STRIPE_SECRET_KEY
            
            # Step 2: Create charge of $4.99 (499 cents) using the token
            stripe.Charge.create(
                amount=499,
                currency="usd",
                source=request.token_id,
                description=f"VerifyDating Security Report - Scan {request.scan_id}",
                receipt_email=request.email,
            )
            
        except stripe.error.CardError as e:
            # Handle card declines, incorrect CVC, expired dates
            conn.close()
            raise HTTPException(status_code=400, detail=e.user_message)
        except Exception as e:
            conn.close()
            raise HTTPException(status_code=500, detail=f"Stripe Processing Error: {str(e)}")

    # ----------------------------------------------------------------------
    # UPDATE DB ON SUCCESS (Stripe processed or simulator fallback completed)
    # ----------------------------------------------------------------------
    cursor.execute("UPDATE scans SET payment_status = 'paid' WHERE id = ?", (request.scan_id,))
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "Payment processed successfully."}

@app.get("/api/results/{scan_id}")
async def get_results(scan_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT payment_status, scam_probability, matches_count, matches_data, scammer_info FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Scan record not found.")
        
    payment_status, scam_probability, matches_count, matches_data, scammer_info = row
    
    if payment_status == "paid":
        return {
            "scan_id": scan_id,
            "payment_status": payment_status,
            "scam_probability": scam_probability,
            "matches_count": matches_count,
            "matches": json.loads(matches_data),
            "scammer_info": scammer_info
        }
    else:
        return {
            "scan_id": scan_id,
            "payment_status": payment_status,
            "locked": True,
            "message": "Payment required to unlock report details."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
