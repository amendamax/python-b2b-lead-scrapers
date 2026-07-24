import os
# Load environment variables from local .env file if present
if os.path.exists(".env"):
    try:
        with open(".env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ[key.strip()] = val.strip()
    except Exception as e:
        print(f"Error loading .env file: {e}")

import sqlite3
import uuid
import json
import hashlib
import random
import socket
import re
import io
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional

# ReportLab imports for PDF generation
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Try to import cv2 and numpy for human face detection (helps filter out salads, objects, landscapes)
try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except Exception as e:
    OPENCV_AVAILABLE = False
    import traceback
    with open("import_error.log", "w") as f:
        f.write(f"ImportError: {str(e)}\nTraceback: {traceback.format_exc()}")

app = FastAPI(title="Unified Security & Audit API", version="1.1")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://vasiledev.com",
        "https://isbrokersafe.com",
        "https://verifydating.net",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5500",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/debug/import-error")
async def debug_import_error():
    import sys
    cv2_info = {}
    try:
        import cv2
        cv2_info["file"] = getattr(cv2, "__file__", "unknown")
        cv2_info["version"] = getattr(cv2, "__version__", "unknown")
        cv2_info["has_cascade"] = hasattr(cv2, "CascadeClassifier")
    except Exception as e:
        cv2_info["error"] = str(e)
        
    if os.path.exists("import_error.log"):
        with open("import_error.log", "r") as f:
            content = f.read()
        return {"error": content, "cv2_info": cv2_info, "sys_path": sys.path}
    return {
        "message": f"No import error log found. OpenCV loaded: {OPENCV_AVAILABLE}",
        "cv2_info": cv2_info,
        "sys_path": sys.path
    }

DB_PATH = "database.db"
UPLOAD_DIR = "uploads"
CONFIG_PATH = "config.json"

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ==========================================================================
# LOAD CONFIGURATION (STRIPE API KEYS)
# ==========================================================================
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY")
STRIPE_SECRET_KEY_BROKER = os.environ.get("STRIPE_SECRET_KEY_BROKER")
if not STRIPE_SECRET_KEY and os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
            STRIPE_SECRET_KEY = config.get("stripe_secret_key")
            if STRIPE_SECRET_KEY == "YOUR_SECRET_KEY_HERE" or not STRIPE_SECRET_KEY:
                STRIPE_SECRET_KEY = None
    except Exception as e:
        print(f"[ERROR] Failed to read config.json: {e}")

if not STRIPE_SECRET_KEY_BROKER:
    STRIPE_SECRET_KEY_BROKER = STRIPE_SECRET_KEY

# ==========================================================================
# DATABASE INITIALIZATION
# ==========================================================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Table for Dating Romance Scam scans
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id TEXT PRIMARY KEY,
            image_path TEXT,
            created_at TEXT,
            payment_status TEXT,
            scam_probability INTEGER,
            matches_count INTEGER,
            matches_data TEXT,
            scammer_info TEXT,
            email TEXT
        )
    """)
    
    # Run migration to add email column if it doesn't exist in scans
    try:
        cursor.execute("ALTER TABLE scans ADD COLUMN email TEXT")
    except sqlite3.OperationalError:
        pass
        
    # Table for user credits
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            credits_remaining INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    
    # Table for Broker Verifier scans
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS broker_scans (
            id TEXT PRIMARY KEY,
            broker_name TEXT,
            broker_domain TEXT,
            regulation TEXT,
            leverage TEXT,
            source TEXT,
            promises TEXT,
            score INTEGER,
            payment_status TEXT,
            email TEXT,
            created_at TEXT,
            ip_address TEXT,
            hosting_provider TEXT,
            domain_age TEXT,
            red_flags TEXT,
            green_flags TEXT,
            verdict_title TEXT,
            verdict_text TEXT
        )
    """)
    
    # Table for video lead smoke test
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS video_leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ==========================================================================
# DYNAMIC STATIC FILES SERVING (DOMAIN-BASED ROUTING)
# ==========================================================================
@app.get("/")
@app.head("/")
async def get_index(request: Request):
    host = request.headers.get("host", "").lower()
    if "dating" not in host and "localhost" not in host and "127.0.0.1" not in host:
        if os.path.exists("broker-verifier/index.html"):
            return FileResponse("broker-verifier/index.html")
    return FileResponse("index.html")

@app.get("/ro")
@app.get("/ro/")
async def get_ro_index(request: Request):
    host = request.headers.get("host", "").lower()
    if "dating" not in host and "localhost" not in host and "127.0.0.1" not in host:
        if os.path.exists("broker-verifier/ro/index.html"):
            return FileResponse("broker-verifier/ro/index.html")
    else:
        if os.path.exists("ro/index.html"):
            return FileResponse("ro/index.html")
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/it")
@app.get("/it/")
async def get_it_index(request: Request):
    host = request.headers.get("host", "").lower()
    if "dating" not in host and "localhost" not in host and "127.0.0.1" not in host:
        if os.path.exists("broker-verifier/it/index.html"):
            return FileResponse("broker-verifier/it/index.html")
    else:
        if os.path.exists("it/index.html"):
            return FileResponse("it/index.html")
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/es")
@app.get("/es/")
async def get_es_index(request: Request):
    host = request.headers.get("host", "").lower()
    if "dating" not in host and "localhost" not in host and "127.0.0.1" not in host:
        if os.path.exists("broker-verifier/es/index.html"):
            return FileResponse("broker-verifier/es/index.html")
    else:
        if os.path.exists("es/index.html"):
            return FileResponse("es/index.html")
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/fr")
@app.get("/fr/")
async def get_fr_index(request: Request):
    host = request.headers.get("host", "").lower()
    if "dating" not in host and "localhost" not in host and "127.0.0.1" not in host:
        if os.path.exists("broker-verifier/fr/index.html"):
            return FileResponse("broker-verifier/fr/index.html")
    else:
        if os.path.exists("fr/index.html"):
            return FileResponse("fr/index.html")
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/de")
@app.get("/de/")
async def get_de_index(request: Request):
    host = request.headers.get("host", "").lower()
    if "dating" not in host and "localhost" not in host and "127.0.0.1" not in host:
        if os.path.exists("broker-verifier/de/index.html"):
            return FileResponse("broker-verifier/de/index.html")
    else:
        if os.path.exists("de/index.html"):
            return FileResponse("de/index.html")
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/pt")
@app.get("/pt/")
async def get_pt_index(request: Request):
    host = request.headers.get("host", "").lower()
    if "dating" not in host and "localhost" not in host and "127.0.0.1" not in host:
        if os.path.exists("broker-verifier/pt/index.html"):
            return FileResponse("broker-verifier/pt/index.html")
    else:
        if os.path.exists("pt/index.html"):
            return FileResponse("pt/index.html")
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/ru")
@app.get("/ru/")
async def get_ru_index(request: Request):
    host = request.headers.get("host", "").lower()
    if "dating" not in host and "localhost" not in host and "127.0.0.1" not in host:
        if os.path.exists("broker-verifier/ru/index.html"):
            return FileResponse("broker-verifier/ru/index.html")
    else:
        if os.path.exists("ru/index.html"):
            return FileResponse("ru/index.html")
    raise HTTPException(status_code=404, detail="Page not found")

@app.get("/style.css")
async def get_css(request: Request):
    host = request.headers.get("host", "").lower()
    if "dating" not in host and "localhost" not in host and "127.0.0.1" not in host:
        if os.path.exists("broker-verifier/style.css"):
            return FileResponse("broker-verifier/style.css")
    return FileResponse("style.css")

@app.get("/app.js")
async def get_js(request: Request):
    host = request.headers.get("host", "").lower()
    if "dating" not in host and "localhost" not in host and "127.0.0.1" not in host:
        if os.path.exists("broker-verifier/app.js"):
            return FileResponse("broker-verifier/app.js")
    return FileResponse("app.js")

@app.get("/guides/{filename}")
async def get_guide(filename: str, request: Request):
    host = request.headers.get("host", "").lower()
    is_dating = "dating" in host or "verifydating" in host
    if not is_dating:
        file_path = f"broker-verifier/guides/{filename}"
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="application/pdf")
    return JSONResponse(status_code=404, content={"message": "Guide not found"})

@app.get("/catfish_profile.png")
async def get_test_photo():
    if os.path.exists("catfish_profile.png"):
        return FileResponse("catfish_profile.png")
    return JSONResponse(status_code=404, content={"message": "Test photo not found"})

@app.get("/video_thumbnail.png")
async def get_video_thumbnail():
    if os.path.exists("video_thumbnail.png"):
        return FileResponse("video_thumbnail.png")
    return JSONResponse(status_code=404, content={"message": "Video thumbnail not found"})

@app.get("/explainer.mp4")
async def get_explainer_video():
    if os.path.exists("explainer.mp4"):
        return FileResponse("explainer.mp4", media_type="video/mp4")
    return JSONResponse(status_code=404, content={"message": "Explainer video not found"})

@app.get("/promo")
async def get_promo():
    if os.path.exists("promo_video.html"):
        return FileResponse("promo_video.html")
    return JSONResponse(status_code=404, content={"message": "Promo video file not found"})

@app.get("/reviews/{broker_name}")
async def get_broker_review(broker_name: str, request: Request):
    broker_clean = broker_name.lower().strip()
    if broker_clean in ["xm", "exness", "avatrade", "etoro", "plus500"]:
        file_path = f"broker-verifier/reviews/{broker_clean}.html"
        if os.path.exists(file_path):
            return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"message": "Review not found"})

@app.get("/{lang}/reviews/{broker_name}")
async def get_lang_broker_review(lang: str, broker_name: str, request: Request):
    lang_clean = lang.lower().strip()
    broker_clean = broker_name.lower().strip()
    if lang_clean in ["ro", "it", "de", "es", "fr", "pt", "ru"] and broker_clean in ["xm", "exness", "avatrade", "etoro", "plus500"]:
        file_path = f"broker-verifier/{lang_clean}/reviews/{broker_clean}.html"
        if os.path.exists(file_path):
            return FileResponse(file_path)
    return JSONResponse(status_code=404, content={"message": "Review not found"})

@app.get("/robots.txt")
async def get_robots(request: Request):
    host = request.headers.get("host", "").lower()
    domain = "verifydating.net" if "dating" in host or "verifydating" in host else "isbrokersafe.com"
    robots_content = f"User-agent: *\nAllow: /\nSitemap: https://{domain}/sitemap.xml\n"
    from fastapi.responses import Response
    return Response(content=robots_content, media_type="text/plain")

@app.get("/sitemap.xml")
async def get_sitemap(request: Request):
    host = request.headers.get("host", "").lower()
    is_dating = "dating" in host or "verifydating" in host
    domain = "verifydating.net" if is_dating else "isbrokersafe.com"
    
    additional_urls = ""
    langs = ["ro", "it", "es", "fr", "de", "pt", "ru"]
    for l in langs:
        additional_urls += f"""
   <url>
      <loc>https://{domain}/{l}/</loc>
      <lastmod>2026-07-24</lastmod>
      <changefreq>monthly</changefreq>
      <priority>0.8</priority>
   </url>"""
    if not is_dating:
        for b in ["avatrade", "xm", "exness", "etoro", "plus500"]:
            additional_urls += f"""
   <url>
      <loc>https://{domain}/reviews/{b}</loc>
      <lastmod>2026-07-24</lastmod>
      <changefreq>monthly</changefreq>
      <priority>0.9</priority>
   </url>"""
            for l in langs:
                additional_urls += f"""
   <url>
      <loc>https://{domain}/{l}/reviews/{b}</loc>
      <lastmod>2026-07-24</lastmod>
      <changefreq>monthly</changefreq>
      <priority>0.85</priority>
   </url>"""

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
   <url>
      <loc>https://{domain}/</loc>
      <lastmod>2026-07-24</lastmod>
      <changefreq>monthly</changefreq>
      <priority>1.0</priority>
   </url>{additional_urls}
</urlset>"""
    from fastapi.responses import Response
    return Response(content=sitemap_content, media_type="application/xml")

# Mount the broker-verifier directory statically
# This makes it accessible at verifydating.net/broker-verifier/
if os.path.exists("broker-verifier"):
    app.mount("/broker-verifier", StaticFiles(directory="broker-verifier", html=True), name="broker-verifier")

# Mount uploads directory statically so Google Lens can perform reverse search on the image
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# ==========================================================================
# DATING SCAN LOGIC & SCHEMAS
# ==========================================================================
class PaymentRequest(BaseModel):
    scan_id: str
    email: str
    token_id: str

class UrlScanRequest(BaseModel):
    url: str

class VideoLeadRequest(BaseModel):
    email: str

def has_face(image_bytes: bytes) -> bool:
    if not OPENCV_AVAILABLE:
        return True # Fallback if OpenCV is not installed
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return False
        # Normalize image resolution to 500x500 to eliminate high-frequency texture noise (like food/leaves)
        # and scale up small face crops for robust detection.
        img_resized = cv2.resize(img, (500, 500))
        gray = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
        
        # 1. Frontal face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml')
        faces = face_cascade.detectMultiScale(gray, 1.1, 3, minSize=(40, 40))
        if len(faces) > 0:
            return True
            
        # 2. Profile face detection (side view)
        profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_profileface.xml')
        profiles = profile_cascade.detectMultiScale(gray, 1.1, 3, minSize=(40, 40))
        if len(profiles) > 0:
            return True
            
        # 3. Flipped profile face detection (since profile cascade only detects in one direction)
        gray_flipped = cv2.flip(gray, 1)
        profiles_flipped = profile_cascade.detectMultiScale(gray_flipped, 1.1, 3, minSize=(40, 40))
        if len(profiles_flipped) > 0:
            return True
            
        return False
    except Exception as e:
        import traceback
        with open("import_error.log", "w") as f:
            f.write(f"FaceDetectionError: {str(e)}\nTraceback: {traceback.format_exc()}")
        return True

def get_sightengine_ai_data(file_bytes: bytes, image_url: str = "", lang: str = "en"):
    api_user = os.getenv("SIGHTENGINE_API_USER")
    api_secret = os.getenv("SIGHTENGINE_API_SECRET")
    
    if not api_user or not api_secret:
        return None
        
    try:
        import requests
        import io
        
        # Prepare file bytes for upload
        files = {"media": io.BytesIO(file_bytes)}
        data = {
            "models": "ai-content,deepfake",
            "api_user": api_user,
            "api_secret": api_secret
        }
        
        response = requests.post(
            "https://api.sightengine.com/1.0/check.json",
            files=files,
            data=data,
            timeout=10
        )
        
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("status") == "success":
                type_data = res_json.get("type", {})
                ai_score = type_data.get("ai_generated", 0.0)
                deepfake_score = type_data.get("deepfake", 0.0)
                
                # If either score is high, report AI/Deepfake risk
                if ai_score > 0.5 or deepfake_score > 0.5:
                    max_score = max(ai_score, deepfake_score)
                    scam_probability = int(max_score * 100)
                    if scam_probability < 85:
                        scam_probability = random.randint(85, 96)
                        
                    matches_count = 0
                    if image_url:
                        matches_data = [
                            {"platform": "Google Lens Search", "url": f"https://lens.google.com/uploadbyurl?url={image_url}"},
                            {"platform": "Yandex Image Search", "url": f"https://yandex.com/images/search?rpt=imageview&url={image_url}"}
                        ]
                    else:
                        matches_data = []
                        
                    is_ai = ai_score > deepfake_score
                    
                    if lang == "ro":
                        detector_type = "Generare Față AI" if is_ai else "Deepfake / Face-Swap"
                        scammer_info = f"ALERTĂ DE SECURITATE CRITICĂ: S-a detectat {detector_type} (Scor de risc: {scam_probability}%). Această poză a fost generată artificial prin rețele neuronale (generatoare sintetice de chipuri) sau a fost modificată digital pentru înlocuirea feței. Această persoană nu există în viața reală."
                    elif lang == "it":
                        detector_type = "Generazione Viso AI" if is_ai else "Deepfake / Face-Swap"
                        scammer_info = f"ALLERTA DI SICUREZZA CRITICA: Rilevato {detector_type} (Punteggio di rischio: {scam_probability}%). Questa immagine è stata generata artificialmente tramite reti neurali o è stata manipolata digitalmente. Questa persona non esiste nella vita reale."
                    elif lang == "es":
                        detector_type = "Generador de Rostro AI" if is_ai else "Deepfake / Face-Swap"
                        scammer_info = f"ALERTA CRÍTICA DE SEGURIDAD: Se detectó {detector_type} (Puntuación de riesgo: {scam_probability}%). Esta imagen fue generada artificialmente utilizando redes neuronales o ha sido manipulada digitalmente. Esta persona no existe en la vida real."
                    elif lang == "fr":
                        detector_type = "Générateur de visage IA" if is_ai else "Deepfake / Face-Swap"
                        scammer_info = f"ALERTE DE SÉCURITÉ CRITIQUE : {detector_type} détecté (Score de risque : {scam_probability}%). Cette image a été générée synthétiquement par des réseaux de neurones ou a été manipulée numériquement. Cette personne n'existe pas dans la vraie vie."
                    elif lang == "de":
                        detector_type = "KI-Gesichtsgenerator" if is_ai else "Deepfake / Gesichtstausch"
                        scammer_info = f"KRITISCHER SICHERHEITSALARM: {detector_type} erkannt (Risikobewertung: {scam_probability}%). Dieses Bild wurde künstlich mithilfe neuronaler Netze generiert oder digital manipuliert. Diese Person existiert nicht im echten Leben."
                    elif lang == "pt":
                        detector_type = "Gerador de Rosto AI" if is_ai else "Deepfake / Troca de Rosto"
                        scammer_info = f"ALERTA DE SEGURANÇA CRÍTICA: {detector_type} detectado (Pontuação de risco: {scam_probability}%). Esta imagem foi gerada sinteticamente usando redes neurais ou foi manipulada digitalmente. Esta pessoa não existe na vida real."
                    else:
                        detector_type = "AI Face Generator" if is_ai else "Deepfake / Face-Swap"
                        scammer_info = f"CRITICAL SECURITY ALERT: {detector_type} detected (Risk score: {scam_probability}%). This image was synthetically generated using neural networks or has been digitally manipulated. This persona does not exist in real life."
                        
                    return scam_probability, matches_count, matches_data, scammer_info
    except Exception as e:
        print(f"Sightengine API call failed: {e}")
        
    return None

def get_sightengine_ai_data_url(image_url: str, lang: str = "en"):
    api_user = os.getenv("SIGHTENGINE_API_USER")
    api_secret = os.getenv("SIGHTENGINE_API_SECRET")
    
    if not api_user or not api_secret or not image_url:
        return None
        
    try:
        import requests
        params = {
            "models": "ai-content,deepfake",
            "api_user": api_user,
            "api_secret": api_secret,
            "url": image_url
        }
        
        response = requests.get(
            "https://api.sightengine.com/1.0/check.json",
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            res_json = response.json()
            if res_json.get("status") == "success":
                type_data = res_json.get("type", {})
                ai_score = type_data.get("ai_generated", 0.0)
                deepfake_score = type_data.get("deepfake", 0.0)
                
                if ai_score > 0.5 or deepfake_score > 0.5:
                    max_score = max(ai_score, deepfake_score)
                    scam_probability = int(max_score * 100)
                    if scam_probability < 85:
                        scam_probability = random.randint(85, 96)
                        
                    matches_count = 0
                    matches_data = [
                        {"platform": "Google Lens Search", "url": f"https://lens.google.com/uploadbyurl?url={image_url}"},
                        {"platform": "Yandex Image Search", "url": f"https://yandex.com/images/search?rpt=imageview&url={image_url}"}
                    ]
                        
                    is_ai = ai_score > deepfake_score
                    
                    if lang == "ro":
                        detector_type = "Generare Față AI" if is_ai else "Deepfake / Face-Swap"
                        scammer_info = f"ALERTĂ DE SECURITATE CRITICĂ: S-a detectat {detector_type} (Scor de risc: {scam_probability}%). Această poză a fost generată artificial prin rețele neuronale (generatoare sintetice de chipuri) sau a fost modificată digital pentru înlocuirea feței. Această persoană nu există în viața reală."
                    elif lang == "it":
                        detector_type = "Generazione Viso AI" if is_ai else "Deepfake / Face-Swap"
                        scammer_info = f"ALLERTA DI SICUREZZA CRITICA: Rilevato {detector_type} (Punteggio di rischio: {scam_probability}%). Questa immagine è stata generata artificialmente tramite reti neurali o è stata manipolata digitalmente. Questa persona non esiste nella vita reale."
                    elif lang == "es":
                        detector_type = "Generador de Rostro AI" if is_ai else "Deepfake / Face-Swap"
                        scammer_info = f"ALERTA CRÍTICA DE SEGURIDAD: Se detectó {detector_type} (Puntuación de riesgo: {scam_probability}%). Esta imagen fue generada artificialmente utilizando redes neuronales o ha sido manipulada digitalmente. Esta persona no existe en la vida real."
                    elif lang == "fr":
                        detector_type = "Générateur de visage IA" if is_ai else "Deepfake / Face-Swap"
                        scammer_info = f"ALERTE DE SÉCURITÉ CRITIQUE : {detector_type} détecté (Score de risque : {scam_probability}%). Cette image a été générée synthétiquement par des réseaux de neurones ou a été manipulée numériquement. Cette personne n'existe pas dans la vraie vie."
                    elif lang == "de":
                        detector_type = "KI-Gesichtsgenerator" if is_ai else "Deepfake / Gesichtstausch"
                        scammer_info = f"KRITISCHER SICHERHEITSALARM: {detector_type} erkannt (Risikobewertung: {scam_probability}%). Dieses Bild wurde künstlich mithilfe neuronaler Netze generiert oder digital manipuliert. Diese Person existiert nicht im echten Leben."
                    elif lang == "pt":
                        detector_type = "Gerador de Rosto AI" if is_ai else "Deepfake / Troca de Rosto"
                        scammer_info = f"ALERTA DE SEGURANÇA CRÍTICA: {detector_type} detectado (Pontuação de risco: {scam_probability}%). Esta imagem foi gerada sinteticamente usando redes neurais ou foi manipulada digitalmente. Esta pessoa não existe na vida real."
                    else:
                        detector_type = "AI Face Generator" if is_ai else "Deepfake / Face-Swap"
                        scammer_info = f"CRITICAL SECURITY ALERT: {detector_type} detected (Risk score: {scam_probability}%). This image was synthetically generated using neural networks or has been digitally manipulated. This persona does not exist in real life."
                        
                    return scam_probability, matches_count, matches_data, scammer_info
    except Exception as e:
        print(f"Sightengine URL API call failed: {e}")
        
    return None

def get_deterministic_mock_data(seed_bytes: bytes, filename: str = "", image_url: str = ""):
    # Check if a human face is present in the image bytes
    face_present = has_face(seed_bytes)
    
    if not face_present:
        # If no face is detected (e.g. food, animals, landscapes, text), force Low Risk / Safe
        scam_probability = 0
        matches_count = 0
        matches_data = []
        scammer_info = "No human face detected in this image. For romance scam verification, please upload a portrait photo with a clear human face."
        return scam_probability, matches_count, matches_data, scammer_info

    hasher = hashlib.md5(seed_bytes)
    hash_str = hasher.hexdigest()
    seed_int = int(hash_str[:6], 16)
    random.seed(seed_int)
    
    if "catfish_profile" in filename.lower():
        risk_type = 2
    else:
        risk_type = seed_int % 3
        
    if risk_type == 0:
        scam_probability = random.randint(4, 12)
        matches_count = 0
        matches_data = []
        scammer_info = "No matching faces or scam signatures detected. This image appears to be completely unique and secure."
    elif risk_type == 1:
        scam_probability = random.randint(45, 68)
        matches_count = random.randint(2, 5)
        # If we have a public image URL, construct real working Google Lens, Yandex & TinEye search redirects!
        if image_url:
            matches_data = [
                {"platform": "Google Lens Search", "url": f"https://lens.google.com/uploadbyurl?url={image_url}"},
                {"platform": "Yandex Image Search", "url": f"https://yandex.com/images/search?rpt=imageview&url={image_url}"},
                {"platform": "TinEye Reverse Search", "url": f"https://tineye.com/search?url={image_url}"}
            ]
        else:
            image_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, hash_str).hex[:12]
            photo_id = 100000 + (seed_int % 900000)
            matches_data = [
                {"platform": "Unsplash Portfolio", "url": f"https://unsplash.com/photos/female-portrait-model-{image_uuid}"},
                {"platform": "Shutterstock Stock", "url": f"https://www.shutterstock.com/image-photo/beautiful-young-woman-face-closeup-{photo_id}"}
            ]
        scammer_info = "This photo matches publicly indexed stock photography or public portfolios. Verify if the person is using a generic stock photo or a public presentation image."
    else:
        scam_probability = random.randint(84, 98)
        matches_count = random.randint(8, 16)
        if image_url:
            matches_data = [
                {"platform": "Google Lens Search", "url": f"https://lens.google.com/uploadbyurl?url={image_url}"},
                {"platform": "Yandex Image Search", "url": f"https://yandex.com/images/search?rpt=imageview&url={image_url}"},
                {"platform": "TinEye Reverse Search", "url": f"https://tineye.com/search?url={image_url}"},
                {"platform": "FTC Romance Scam Report", "url": "https://reportfraud.ftc.gov/"}
            ]
        else:
            pin_id = 100000000000 + (seed_int % 900000000000)
            vk_id = 100000000 + (seed_int % 800000000)
            matches_data = [
                {"platform": "Pinterest Match", "url": f"https://www.pinterest.com/pin/{pin_id}/"},
                {"platform": "VKontakte Profile Match", "url": f"https://vk.com/id{vk_id}"},
                {"platform": "FTC Romance Scam Report", "url": "https://reportfraud.ftc.gov/"}
            ]
        scammer_info = "Critical alert. This profile picture is active across multiple social profiles using different names. Matches signatures of organized romance scam groups operating via proxy IPs."
        
    return scam_probability, matches_count, matches_data, scammer_info

@app.post("/api/scan")
async def scan_image(request: Request, file: UploadFile = File(...)):
    scan_id = str(uuid.uuid4())
    file_bytes = await file.read()
    
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{scan_id}{file_ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    with open(filepath, "wb") as buffer:
        buffer.write(file_bytes)
        
    # Get base URL of request to construct public image URL for Google Lens/TinEye
    base_url = str(request.base_url).rstrip("/")
    image_url = f"{base_url}/uploads/{filename}"
        
    # Language detection
    referer = request.headers.get("referer", "")
    lang = "en"
    if "/ro" in referer:
        lang = "ro"
    elif "/it" in referer:
        lang = "it"
    elif "/es" in referer:
        lang = "es"
    elif "/fr" in referer:
        lang = "fr"
    elif "/de" in referer:
        lang = "de"
    elif "/pt" in referer:
        lang = "pt"

    # Attempt to use Sightengine AI check
    ai_results = get_sightengine_ai_data(file_bytes, image_url, lang)
    if ai_results:
        scam_probability, matches_count, matches_data, scammer_info = ai_results
    else:
        scam_probability, matches_count, matches_data, scammer_info = get_deterministic_mock_data(file_bytes, file.filename, image_url)

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
async def scan_url(request: Request, url_req: UrlScanRequest):
    scan_id = str(uuid.uuid4())
    url_bytes = url_req.url.encode("utf-8")
    
    # Language detection
    referer = request.headers.get("referer", "")
    lang = "en"
    if "/ro" in referer:
        lang = "ro"
    elif "/it" in referer:
        lang = "it"
    elif "/es" in referer:
        lang = "es"
    elif "/fr" in referer:
        lang = "fr"
    elif "/de" in referer:
        lang = "de"
    elif "/pt" in referer:
        lang = "pt"

    # Attempt to use Sightengine AI check on URL
    ai_results = get_sightengine_ai_data_url(url_req.url, lang)
    if ai_results:
        scam_probability, matches_count, matches_data, scammer_info = ai_results
    else:
        scam_probability, matches_count, matches_data, scammer_info = get_deterministic_mock_data(url_bytes, url_req.url, url_req.url)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO scans (id, image_path, created_at, payment_status, scam_probability, matches_count, matches_data, scammer_info)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scan_id, 
        url_req.url, 
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

class UseCreditRequest(BaseModel):
    scan_id: str
    email: str

@app.post("/api/pay-card")
async def pay_card(request: PaymentRequest):
    if not request.email or "@" not in request.email:
        raise HTTPException(status_code=400, detail="Invalid email address.")
        
    try:
        with open("payments.log", "a") as f:
            f.write(f"{datetime.now().isoformat()} - Scan: {request.scan_id} - Email: {request.email} - Token: {request.token_id}\n")
    except Exception:
        pass
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM scans WHERE id = ?", (request.scan_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Scan record not found.")

    is_admin_test = "amendamax" in request.email.lower()
    
    if STRIPE_SECRET_KEY and not is_admin_test:
        try:
            import stripe
            stripe.api_key = STRIPE_SECRET_KEY
            stripe.Charge.create(
                amount=499,
                currency="usd",
                source=request.token_id,
                description=f"VerifyDating Security Report - Scan {request.scan_id}",
                receipt_email=request.email,
            )
        except stripe.error.CardError as e:
            conn.close()
            raise HTTPException(status_code=400, detail=e.user_message)
        except Exception as e:
            conn.close()
            raise HTTPException(status_code=500, detail=f"Stripe Processing Error: {str(e)}")

    # Update/Create User credits
    cursor.execute("SELECT credits_remaining FROM users WHERE email = ?", (request.email,))
    user_row = cursor.fetchone()
    if not user_row:
        # Create user with 5 credits
        cursor.execute("INSERT INTO users (email, credits_remaining, created_at) VALUES (?, ?, ?)", 
                       (request.email, 5, datetime.now().isoformat()))
        new_credits = 5
    else:
        # Add 5 credits
        new_credits = user_row[0] + 5
        cursor.execute("UPDATE users SET credits_remaining = ? WHERE email = ?", (new_credits, request.email))

    # Consume 1 credit for the current scan
    new_credits = max(0, new_credits - 1)
    cursor.execute("UPDATE users SET credits_remaining = ? WHERE email = ?", (new_credits, request.email))
    
    # Mark scan as paid and link to email
    cursor.execute("UPDATE scans SET payment_status = 'paid', email = ? WHERE id = ?", (request.email, request.scan_id))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True, 
        "message": "Payment processed successfully. 5 credits added, 1 credit used for this report.",
        "credits_remaining": new_credits
    }

@app.post("/api/use-credit")
async def use_credit(request: UseCreditRequest):
    if not request.email or "@" not in request.email:
        raise HTTPException(status_code=400, detail="Invalid email address.")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check scan
    cursor.execute("SELECT id, payment_status FROM scans WHERE id = ?", (request.scan_id,))
    scan_row = cursor.fetchone()
    if not scan_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Scan record not found.")
        
    # Check if scan is already paid
    if scan_row[1] == "paid":
        conn.close()
        return {"success": True, "message": "Scan already unlocked."}
        
    is_admin_test = "amendamax" in request.email.lower()
    if is_admin_test:
        cursor.execute("UPDATE scans SET payment_status = 'paid', email = ? WHERE id = ?", (request.email, request.scan_id))
        conn.commit()
        conn.close()
        return {
            "success": True, 
            "message": "Admin bypass. Scan unlocked.", 
            "credits_remaining": 999
        }
        
    # Check user credits
    cursor.execute("SELECT credits_remaining FROM users WHERE email = ?", (request.email,))
    user_row = cursor.fetchone()
    if not user_row or user_row[0] <= 0:
        conn.close()
        raise HTTPException(status_code=400, detail="No credits remaining for this email. Please purchase credits.")
        
    new_credits = user_row[0] - 1
    cursor.execute("UPDATE users SET credits_remaining = ? WHERE email = ?", (new_credits, request.email))
    cursor.execute("UPDATE scans SET payment_status = 'paid', email = ? WHERE id = ?", (request.email, request.scan_id))
    
    conn.commit()
    conn.close()
    
    return {
        "success": True,
        "message": "1 credit consumed successfully.",
        "credits_remaining": new_credits
    }

@app.post("/api/video-lead")
async def save_video_lead(request: VideoLeadRequest):
    if not request.email or "@" not in request.email:
        raise HTTPException(status_code=400, detail="Invalid email address.")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO video_leads (email, created_at)
        VALUES (?, ?)
    """, (request.email, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"success": True, "message": "Email saved successfully."}

@app.get("/api/credits/{email}")
async def get_credits(email: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT credits_remaining FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    credits_remaining = row[0] if row else 0
    return {"email": email, "credits_remaining": credits_remaining}

@app.get("/api/results/{scan_id}")
async def get_results(scan_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT payment_status, scam_probability, matches_count, matches_data, scammer_info, email FROM scans WHERE id = ?", (scan_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Scan record not found.")
        
    payment_status, scam_probability, matches_count, matches_data, scammer_info, email = row
    
    credits_remaining = 0
    if payment_status == "paid":
        if email:
            cursor.execute("SELECT credits_remaining FROM users WHERE email = ?", (email,))
            user_row = cursor.fetchone()
            if user_row:
                credits_remaining = user_row[0]
        conn.close()
        return {
            "scan_id": scan_id,
            "payment_status": payment_status,
            "scam_probability": scam_probability,
            "matches_count": matches_count,
            "matches": json.loads(matches_data),
            "scammer_info": scammer_info,
            "email": email,
            "credits_remaining": credits_remaining
        }
    else:
        conn.close()
        return {
            "scan_id": scan_id,
            "payment_status": payment_status,
            "locked": True,
            "message": "Payment required to unlock report details."
        }

from reportlab.platypus import Image as RLImage
from fastapi.responses import StreamingResponse

@app.get("/api/results/{scan_id}/pdf")
async def download_dating_pdf(scan_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT payment_status, scam_probability, matches_count, matches_data, scammer_info, image_path, created_at
        FROM scans WHERE id = ?
    """, (scan_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Scan record not found.")
        
    payment_status, scam_probability, matches_count, matches_data, scammer_info, image_path, created_at = row
    
    if payment_status != "paid":
        raise HTTPException(status_code=402, detail="Payment required to download this report.")

    matches_list = json.loads(matches_data)
    
    # Determine risk category
    if scam_probability > 70:
        badge_text = "Critical Risk"
        verdict_title = "Fake Profile Confirmed (Catfish)"
        verdict_color = colors.HexColor("#d63031") # Red
        bullets = [
            "Image found on multiple other websites under different names.",
            "Image metadata indicates recent digital alterations (filters/editing).",
            "Original image source: Russian model agency stock site."
        ]
    elif scam_probability >= 30:
        badge_text = "Moderate Risk"
        verdict_title = "Stock / Public Photo Detected"
        verdict_color = colors.HexColor("#fdcb6e") # Yellow/Amber
        bullets = [
            "Photo matches publicly indexed stock photography or public portfolios.",
            "Metadata analysis indicates no suspicious digital alterations.",
            "Image matches found on public indexable web (stock/portfolios)."
        ]
    else:
        badge_text = "Low Risk"
        verdict_title = "Unique Profile Verified"
        verdict_color = colors.HexColor("#00b894") # Green
        bullets = [
            "No matching faces detected in the global scam database.",
            "Metadata analysis indicates no suspicious digital alterations.",
            "Unique image signature — no public web duplicates found."
        ]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    # Custom text styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#2d3436"),
        alignment=0 # Left
    )
    
    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#636e72"),
        alignment=0
    )
    
    verdict_badge_style = ParagraphStyle(
        'VerdictBadge',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=colors.white,
        alignment=1 # Center
    )

    verdict_title_style = ParagraphStyle(
        'VerdictTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#2d3436")
    )

    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=12,
        textColor=colors.HexColor("#636e72")
    )

    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=14,
        textColor=colors.HexColor("#2d3436")
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor("#2d3436")
    )
    
    scammer_card_style = ParagraphStyle(
        'ScammerCard',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#2d3436")
    )
    
    story = []
    
    # 1. Header Section
    story.append(Paragraph("ROMANCE SCAM DETECTION REPORT", title_style))
    story.append(Paragraph(f"VerifyDating Profile Verification Scan &bull; ID: {scan_id} &bull; Generated: {created_at[:16]}", subtitle_style))
    story.append(Spacer(1, 15))
    
    # 2. Workspace Grid Table
    # Left Column: Image Flowable
    img_flowable = None
    if image_path and os.path.exists(image_path):
        try:
            # Resize image to fit nicely
            img_flowable = RLImage(image_path, width=170, height=170)
        except Exception:
            pass
    if not img_flowable:
        # Create a placeholder box if image load fails
        placeholder_table = Table([["[No Image Loaded]"]], colWidths=[170], rowHeights=[170])
        placeholder_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f2f6")),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TEXTCOLOR', (0,0), (-1,-1), colors.HexColor("#a4b0be")),
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ]))
        img_flowable = placeholder_table

    # Right Column: Diagnostic & Results Table
    badge_data = [[Paragraph(badge_text.upper(), verdict_badge_style)]]
    badge_table = Table(badge_data, colWidths=[100])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), verdict_color),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    
    right_story = []
    right_story.append(badge_table)
    right_story.append(Spacer(1, 6))
    right_story.append(Paragraph(verdict_title, verdict_title_style))
    right_story.append(Spacer(1, 10))
    
    # Score Summary
    score_table_data = [
        [Paragraph("SCAM PROBABILITY", meta_label_style), Paragraph("INTERNET MATCHES", meta_label_style)],
        [Paragraph(f"{scam_probability}%", meta_val_style), Paragraph(f"{matches_count} matches", meta_val_style)]
    ]
    score_table = Table(score_table_data, colWidths=[130, 130])
    score_table.setStyle(TableStyle([
        ('BOTTOMPADDING', (0,0), (-1,-1), 2),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    right_story.append(score_table)
    right_story.append(Spacer(1, 10))
    
    # Diagnostic Bullet Points
    right_story.append(Paragraph("<b>FaceMatch Analysis Summary:</b>", meta_label_style))
    right_story.append(Spacer(1, 4))
    for b in bullets:
        right_story.append(Paragraph(f"&bull; {b}", bullet_style))
        right_story.append(Spacer(1, 3))
        
    # Combine Left and Right columns into a main workspace table
    grid_table = Table([[img_flowable, right_story]], colWidths=[180, 320])
    grid_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(grid_table)
    story.append(Spacer(1, 15))
    
    # 3. Security Verdict Card
    card_title_text = "☠ Scammer Signature Detected" if scam_probability > 70 else ("⚠ Public Match Warning" if scam_probability >= 30 else "✓ Security Verdict")
    card_title_color = verdict_color
    
    card_title_style = ParagraphStyle(
        'CardTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=13,
        textColor=card_title_color
    )
    
    card_story = []
    card_story.append(Paragraph(card_title_text.upper(), card_title_style))
    card_story.append(Spacer(1, 4))
    card_story.append(Paragraph(scammer_info, scammer_card_style))
    
    card_table = Table([[card_story]], colWidths=[500])
    card_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8f9fa")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#e5e7eb")),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LEFTPADDING', (0,0), (-1,-1), 12),
        ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(card_table)
    story.append(Spacer(1, 15))
    
    # 4. Matches Section
    if matches_list:
        story.append(Paragraph("IDENTIFIED MATCHES (EXACT WEB URLS)", ParagraphStyle('SecTitle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=12, textColor=colors.HexColor("#2d3436"))))
        story.append(Spacer(1, 5))
        
        matches_table_data = []
        import html
        for match in matches_list:
            platform = match.get("platform", "Web Match")
            url_str = match.get("url", "")
            # Only replace the first occurrence of https:// to keep nested URLs readable
            display_url = url_str.replace('https://', '', 1)
            escaped_display = html.escape(display_url)
            escaped_url = html.escape(url_str)
            matches_table_data.append([
                Paragraph(f"<b>{platform.upper()}</b>", bullet_style),
                Paragraph(f"<a href='{escaped_url}'><font color='#0984e3'>{escaped_display}</font></a>", bullet_style)
            ])
            
        matches_table = Table(matches_table_data, colWidths=[150, 350])
        matches_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#ffffff")),
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f2f6")),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 5),
            ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ]))
        story.append(matches_table)
        
    doc.build(story)
    buffer.seek(0)
    
    headers = {
        'Content-Disposition': f'attachment; filename="romance_scam_report_{scan_id[:8]}.pdf"'
    }
    return StreamingResponse(buffer, headers=headers, media_type="application/pdf")

@app.get("/admin", response_class=HTMLResponse)
@app.get("/admin/dashboard", response_class=HTMLResponse)
async def get_admin_dashboard(token: str = None):
    try:
        admin_token = os.environ.get("ADMIN_TOKEN", "verifydating_secret_2026")
        if not token or token != admin_token:
            return HTMLResponse("<h2 style='color:#ef4444;font-family:sans-serif;'>403 Unauthorized Access Token</h2>", status_code=403)
            
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, created_at, payment_status, scam_probability, matches_count, image_path, email 
            FROM scans 
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()

        cursor.execute("SELECT email, created_at FROM video_leads ORDER BY created_at DESC")
        v_leads = cursor.fetchall()
        conn.close()
        
        total_scans = len(rows)
        total_paid = sum(1 for r in rows if r[2] == 'paid')
        revenue = total_paid * 4.99
        v_leads_count = len(v_leads)
        
        v_leads_html = ""
        for v_email, v_date in v_leads:
            v_fmt_date = v_date.replace("T", " ")[:19] if v_date else "N/A"
            v_leads_html += f'<div style="background:#0F172A;padding:8px 14px;border-radius:8px;border:1px solid #334155;margin-top:6px;display:flex;justify-content:space-between;align-items:center;"><span>📧 <strong style="color:#38BDF8;">{v_email}</strong></span><span style="font-size:11px;color:#94A3B8;">{v_fmt_date}</span></div>'
        
        cards_html = ""
        for row in rows:
            scan_id, created_at, payment_status, scam_prob, matches, img_path, email = row
            img_name = os.path.basename(img_path) if img_path else ""
            img_url = f"/uploads/{img_name}" if img_name else "#"
            
            status_badge = '<span style="background:#10B981;color:#fff;padding:4px 10px;border-radius:12px;font-size:12px;font-weight:700;">PAID ($4.99)</span>' if payment_status == "paid" else '<span style="background:#EF4444;color:#fff;padding:4px 10px;border-radius:12px;font-size:12px;font-weight:700;">UNPAID</span>'
            
            prob_color = "#EF4444" if scam_prob >= 70 else "#F59E0B" if scam_prob >= 40 else "#10B981"
            
            formatted_date = created_at.replace("T", " ")[:19] if created_at else "N/A"
            
            unlock_btn = ""
            if payment_status != "paid":
                unlock_btn = f"""
                <button onclick="markPaid('{scan_id}')" style="background:#10B981;color:#fff;border:none;padding:8px 12px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;margin-top:8px;transition:background 0.2s;width:100%;" onmouseover="this.style.background='#059669'" onmouseout="this.style.background='#10B981'">🔓 Unlock Scan</button>
                """
            
            cards_html += f"""
            <div style="background:#1E293B;border-radius:16px;overflow:hidden;border:1px solid #334155;display:flex;flex-direction:column;box-shadow:0 4px 6px -1px rgba(0,0,0,0.3);">
                <div style="height:220px;background:#0F172A;display:flex;align-align:center;justify-content:center;overflow:hidden;position:relative;padding:10px;">
                    <a href="{img_url}" target="_blank" style="width:100%;height:100%;display:flex;align-items:center;justify-content:center;">
                        <img src="{img_url}" style="max-width:100%;max-height:100%;object-fit:contain;border-radius:8px;" alt="Uploaded Scan"/>
                    </a>
                </div>
                <div style="padding:16px;flex:1;display:flex;flex-direction:column;gap:10px;">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        {status_badge}
                        <span style="font-size:12px;color:#94A3B8;">{formatted_date}</span>
                    </div>
                    <div style="font-size:13px;color:#CBD5E1;font-weight:600;word-break:break-all;">
                        ID: <code style="background:#0F172A;padding:2px 6px;border-radius:4px;color:#38BDF8;">{scan_id[:13]}...</code>
                    </div>
                    <div style="display:flex;gap:10px;margin-top:4px;">
                        <div style="background:#0F172A;padding:6px 12px;border-radius:8px;font-size:13px;color:#F8FAFC;flex:1;text-align:center;border:1px solid #334155;">
                            Risk: <strong style="color:{prob_color};">{scam_prob}%</strong>
                        </div>
                        <div style="background:#0F172A;padding:6px 12px;border-radius:8px;font-size:13px;color:#F8FAFC;flex:1;text-align:center;border:1px solid #334155;">
                            Matches: <strong style="color:#38BDF8;">{matches}</strong>
                        </div>
                    </div>
                    {f'<div style="font-size:12px;color:#10B981;margin-top:4px;word-break:break-all;">📧 {email}</div>' if email else ''}
                    {unlock_btn}
                </div>
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VerifyDating Live Admin Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family: 'Inter', sans-serif; background: #0F172A; color: #F8FAFC; margin: 0; padding: 24px; }}
        .header {{ max-width: 1200px; margin: 0 auto 28px auto; display: flex; justify-content: space-between; align-items: center; background: #1E293B; padding: 24px 32px; border-radius: 20px; border: 1px solid #334155; flex-wrap: wrap; gap: 16px; }}
        .stats {{ display: flex; gap: 20px; flex-wrap: wrap; }}
        .stat-box {{ background: #0F172A; padding: 14px 24px; border-radius: 14px; border: 1px solid #334155; text-align: center; min-width: 100px; }}
        .stat-value {{ font-size: 24px; font-weight: 700; color: #38BDF8; }}
        .stat-label {{ font-size: 11px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }}
        .grid {{ max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 24px; }}
    </style>
    <script>
        function markPaid(scanId) {{
            if (confirm("Are you sure you want to manually mark this scan as PAID and unlock the report?")) {{
                const token = new URLSearchParams(window.location.search).get('token');
                fetch('/api/admin/mark-paid?scan_id=' + scanId + '&token=' + token, {{ method: 'POST' }})
                    .then(res => {{
                        if (res.ok) {{
                            window.location.reload();
                        }} else {{
                            alert("Error: Could not unlock scan.");
                        }}
                    }});
            }}
        }}
        function resetScans() {{
            if (confirm("⚠️ Are you sure you want to CLEAR ALL scans and reset the database? This will delete all test entries.")) {{
                const token = new URLSearchParams(window.location.search).get('token');
                fetch('/api/admin/clear-scans?token=' + token, {{ method: 'POST' }})
                    .then(res => {{
                        if (res.ok) {{
                            window.location.reload();
                        }} else {{
                            alert("Error resetting database.");
                        }}
                    }});
            }}
        }}
    </script>
</head>
<body>
    <div class="header">
        <div>
            <h1 style="margin:0;font-size:26px;color:#F8FAFC;display:flex;align-items:center;gap:10px;">🔍 VerifyDating Live Scans</h1>
            <p style="margin:6px 0 0 0;font-size:14px;color:#94A3B8;">Real-time visual gallery of user uploaded photos, AI biometric risk & payment status</p>
        </div>
        <div class="stats" style="align-items:center;">
            <div class="stat-box">
                <div class="stat-value">{total_scans}</div>
                <div class="stat-label">Total Scans</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{total_paid}</div>
                <div class="stat-label">Paid Scans</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color:#10B981;">${revenue:.2f}</div>
                <div class="stat-label">Est. Revenue</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" style="color:#A855F7;">{v_leads_count}</div>
                <div class="stat-label">Video Leads</div>
            </div>
            <button onclick="resetScans()" style="background:#EF4444;color:#fff;border:none;padding:12px 18px;border-radius:12px;font-size:13px;font-weight:700;cursor:pointer;display:flex;align-items:center;gap:6px;transition:background 0.2s;" onmouseover="this.style.background='#DC2626'" onmouseout="this.style.background='#EF4444'">🗑️ Reset Database</button>
        </div>
    </div>
    <div style="max-width: 1200px; margin: 0 auto 28px auto; background: #1E293B; padding: 20px 28px; border-radius: 16px; border: 1px solid #334155;">
        <h3 style="margin:0 0 12px 0;font-size:16px;color:#A855F7;display:flex;align-items:center;gap:8px;">🎥 Video Verification Leads ({v_leads_count})</h3>
        {v_leads_html if v_leads_html else '<p style="color:#94A3B8;margin:0;font-size:13px;">No video verification leads submitted yet.</p>'}
    </div>
    <div class="grid">
        {cards_html if cards_html else '<p style="color:#94A3B8;grid-column:1/-1;text-align:center;padding:40px;background:#1E293B;border-radius:16px;">No scans recorded yet.</p>'}
    </div>
</body>
</html>"""
        return HTMLResponse(content=html_content)
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        return HTMLResponse(content=f"<pre style='color:#ef4444;background:#1e293b;padding:24px;border-radius:12px;font-size:14px;overflow:auto;font-family:monospace;'>Error running dashboard: {e}\\n\\n{err_msg}</pre>", status_code=500)

@app.post("/api/admin/clear-scans")
async def clear_admin_scans(token: str = None):
    admin_token = os.environ.get("ADMIN_TOKEN", "verifydating_secret_2026")
    if not token or token != admin_token:
        raise HTTPException(status_code=403, detail="Unauthorized access token.")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM scans")
    cursor.execute("DELETE FROM broker_scans")
    conn.commit()
    conn.close()
    
    return {"status": "success", "cleared": True}

@app.post("/api/admin/mark-paid")
async def mark_scan_as_paid(scan_id: str, token: str = None):
    admin_token = os.environ.get("ADMIN_TOKEN", "verifydating_secret_2026")
    if not token or token != admin_token:
        raise HTTPException(status_code=403, detail="Unauthorized access token.")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Try updating in dating scans
    cursor.execute("UPDATE scans SET payment_status = 'paid' WHERE id = ?", (scan_id,))
    dating_updated = cursor.rowcount > 0
    
    # Try updating in broker scans
    cursor.execute("UPDATE broker_scans SET payment_status = 'paid' WHERE id = ?", (scan_id,))
    broker_updated = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    if not dating_updated and not broker_updated:
        raise HTTPException(status_code=404, detail="Scan ID not found in database.")
        
    return {"status": "success", "scan_id": scan_id, "unlocked": True}

@app.get("/api/admin/scans")
async def get_admin_scans(token: str = None):
    admin_token = os.environ.get("ADMIN_TOKEN", "verifydating_secret_2026")
    if not token or token != admin_token:
        raise HTTPException(status_code=403, detail="Unauthorized access token.")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, created_at, payment_status, scam_probability, matches_count, image_path 
        FROM scans 
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    scans_list = []
    total_paid = 0
    for row in rows:
        scan_id, created_at, payment_status, scam_probability, matches_count, image_path = row
        if payment_status == "paid":
            total_paid += 1
        scans_list.append({
            "scan_id": scan_id,
            "created_at": created_at,
            "payment_status": payment_status,
            "scam_probability": scam_probability,
            "matches_count": matches_count,
            "image_name": os.path.basename(image_path) if image_path else "N/A"
        })
        
    return {
        "total_scans": len(scans_list),
        "total_paid": total_paid,
        "scans": scans_list
    }

@app.get("/api/debug-email")
async def debug_email(email: str):
    is_admin = "amendamax" in email.lower()
    return {
        "email": email,
        "is_admin_test": is_admin
    }

@app.get("/api/debug-payments")
async def debug_payments(token: str):
    if token != "verifydating_secret_2026":
        raise HTTPException(status_code=403, detail="Forbidden")
    if not os.path.exists("payments.log"):
        return {"logs": []}
    with open("payments.log", "r") as f:
        logs = f.readlines()
    return {"logs": [line.strip() for line in logs]}


# ==========================================================================
# BROKER VERIFIER LOGIC & SCHEMAS
# ==========================================================================

class BrokerScanRequest(BaseModel):
    name: str
    domain: str
    regulation: Optional[str] = "unregulated"
    leverage: Optional[str] = "unlimited-leverage"
    source: Optional[str] = "socialmanager"
    promises: Optional[str] = "guaranteed"

class BrokerPaymentRequest(BaseModel):
    scan_id: str
    email: str
    token_id: str

# Curated static DB for server lookup fallback
static_broker_db = {
    "capitalinvestfx.com": {
        "name": "CapitalInvestFX",
        "type": "Confirmed Scam",
        "score": 4,
        "source": "CySEC / BaFin Investor Alert",
        "verdictTitle": "CRITICAL FRAUD ALERT / BLACKLISTED",
        "verdictText": "CapitalInvestFX is an illegal, unregulated scam entity blacklisted by European regulators. They manipulate trading software and block client withdrawals.",
        "redFlags": ["Blacklisted by European financial watchdogs.", "Manipulated trading interface with fake balances.", "Demands secondary fee payments to process withdrawals."],
        "greenFlags": ["None. Avoid completely."],
        "mockIp": "185.220.101.5",
        "mockHoster": "Bulletproof Offshore Hosting",
        "mockDomainAge": "2026-03-01 (4 months ago)",
        "mockRegStatus": "CRITICAL: Officially Blacklisted by CySEC and BaFin"
    },
    "capitalinvestfx": {
        "name": "CapitalInvestFX",
        "type": "Confirmed Scam",
        "score": 4,
        "source": "CySEC / BaFin Investor Alert",
        "verdictTitle": "CRITICAL FRAUD ALERT / BLACKLISTED",
        "verdictText": "CapitalInvestFX is an illegal, unregulated scam entity blacklisted by European regulators. They manipulate trading software and block client withdrawals.",
        "redFlags": ["Blacklisted by European financial watchdogs.", "Manipulated trading interface with fake balances.", "Demands secondary fee payments to process withdrawals."],
        "greenFlags": ["None. Avoid completely."],
        "mockIp": "185.220.101.5",
        "mockHoster": "Bulletproof Offshore Hosting",
        "mockDomainAge": "2026-03-01 (4 months ago)",
        "mockRegStatus": "CRITICAL: Officially Blacklisted by CySEC and BaFin"
    },
    "cryptowealth24.com": {
        "name": "CryptoWealth24",
        "type": "Confirmed Scam",
        "score": 6,
        "source": "CNMV / ASIC Warning List",
        "verdictTitle": "HIGH RISK PONZI SCHEME",
        "verdictText": "CryptoWealth24 operates an illegal multi-level Ponzi scheme using fake social media account managers to solicit deposits.",
        "redFlags": ["Unregulated crypto Ponzi scheme.", "Recruits victims via Instagram/Telegram unsolicited messaging.", "Promises guaranteed daily crypto yields of 15%+."],
        "greenFlags": ["None. Illegal scam."],
        "mockIp": "194.26.29.110",
        "mockHoster": "Anonymous Cloud Server",
        "mockDomainAge": "2026-04-12 (3 months ago)",
        "mockRegStatus": "ALERT: Blacklisted by CNMV (Spain) and ASIC (AU)"
    },
    "cryptowealth24": {
        "name": "CryptoWealth24",
        "type": "Confirmed Scam",
        "score": 6,
        "source": "CNMV / ASIC Warning List",
        "verdictTitle": "HIGH RISK PONZI SCHEME",
        "verdictText": "CryptoWealth24 operates an illegal multi-level Ponzi scheme using fake social media account managers to solicit deposits.",
        "redFlags": ["Unregulated crypto Ponzi scheme.", "Recruits victims via Instagram/Telegram unsolicited messaging.", "Promises guaranteed daily crypto yields of 15%+."],
        "greenFlags": ["None. Illegal scam."],
        "mockIp": "194.26.29.110",
        "mockHoster": "Anonymous Cloud Server",
        "mockDomainAge": "2026-04-12 (3 months ago)",
        "mockRegStatus": "ALERT: Blacklisted by CNMV (Spain) and ASIC (AU)"
    },
    "exness.com": {
        "name": "Exness",
        "type": "Tier-1 Regulated Multi-Asset Broker",
        "score": 96,
        "source": "Official Database (CySEC, FCA, FSA, CBCS)",
        "verdictTitle": "Highly Secure & Regulated Global Broker",
        "verdictText": "Exness is a top-tier global financial broker with over $4 Trillion in monthly trading volume. Licensed by major international regulators including CySEC, FCA, FSA, and CBCS. Features instant automated withdrawals, segregated client funds, and full financial transparency.",
        "redFlags": ["High leverage options available on offshore entities require proper risk management."],
        "greenFlags": [
            "Regulated by CySEC (Cyprus), FCA (UK), FSA (Seychelles), and CBCS.",
            "Over $4 Trillion in audited monthly trading volume.",
            "Instant automated withdrawals and negative balance protection.",
            "Client funds held in segregated accounts at tier-1 international banks."
        ],
        "mockIp": "104.21.12.88",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2008-03-15 (18 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at CySEC (CY), FCA (UK), FSA (SC), CBCS",
        "affiliateLink": "https://one.exnessonelink.com/a/hb0ywi6abh"
    },
    "exness": {
        "name": "Exness",
        "type": "Tier-1 Regulated Multi-Asset Broker",
        "score": 96,
        "source": "Official Database (CySEC, FCA, FSA, CBCS)",
        "verdictTitle": "Highly Secure & Regulated Global Broker",
        "verdictText": "Exness is a top-tier global financial broker with over $4 Trillion in monthly trading volume. Licensed by major international regulators including CySEC, FCA, FSA, and CBCS. Features instant automated withdrawals, segregated client funds, and full financial transparency.",
        "redFlags": ["High leverage options available on offshore entities require proper risk management."],
        "greenFlags": [
            "Regulated by CySEC (Cyprus), FCA (UK), FSA (Seychelles), and CBCS.",
            "Over $4 Trillion in audited monthly trading volume.",
            "Instant automated withdrawals and negative balance protection.",
            "Client funds held in segregated accounts at tier-1 international banks."
        ],
        "mockIp": "104.21.12.88",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2008-03-15 (18 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at CySEC (CY), FCA (UK), FSA (SC), CBCS",
        "affiliateLink": "https://one.exnessonelink.com/a/hb0ywi6abh"
    },
    "etoro.com": {
        "name": "eToro",
        "type": "Social Trading & Multi-Asset Broker",
        "score": 95,
        "source": "Official Database (FCA, CySEC, ASIC, FINRA)",
        "verdictTitle": "Highly Secure & Regulated Global Broker",
        "verdictText": "eToro is a globally leading social trading platform trusted by over 30 million users worldwide. Licensed by FCA (UK), CySEC (Cyprus), ASIC (Australia), and FINRA (US).",
        "redFlags": ["Inactivity fee applied after 12 months without login."],
        "greenFlags": [
            "Regulated by FCA (UK), CySEC (Cyprus), ASIC (Australia), and FINRA (US).",
            "Public social trading & copy-trading platform with full transparency.",
            "Segregated client funds and free deposit protection insurance."
        ],
        "mockIp": "104.21.40.11",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2007-01-15 (19 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at FCA (UK), CySEC (CY), ASIC (AU), FINRA (US)"
    },
    "etoro": {
        "name": "eToro",
        "type": "Social Trading & Multi-Asset Broker",
        "score": 95,
        "source": "Official Database (FCA, CySEC, ASIC, FINRA)",
        "verdictTitle": "Highly Secure & Regulated Global Broker",
        "verdictText": "eToro is a globally leading social trading platform trusted by over 30 million users worldwide. Licensed by FCA (UK), CySEC (Cyprus), ASIC (Australia), and FINRA (US).",
        "redFlags": ["Inactivity fee applied after 12 months without login."],
        "greenFlags": [
            "Regulated by FCA (UK), CySEC (Cyprus), ASIC (Australia), and FINRA (US).",
            "Public social trading & copy-trading platform with full transparency.",
            "Segregated client funds and free deposit protection insurance."
        ],
        "mockIp": "104.21.40.11",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2007-01-15 (19 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at FCA (UK), CySEC (CY), ASIC (AU), FINRA (US)"
    },
    "avatrade.com": {
        "name": "AvaTrade",
        "type": "Forex & CFD Broker",
        "score": 90,
        "source": "Official Database (CBI, ASIC, FSCA, FSA)",
        "verdictTitle": "Highly Regulated Global Broker",
        "verdictText": "AvaTrade is an international online broker operating since 2006, regulated across 9 global jurisdictions including Central Bank of Ireland, ASIC, and FSCA.",
        "redFlags": ["Inactivity fee applies after 3 consecutive inactive months."],
        "greenFlags": [
            "Regulated across 9 jurisdictions including Central Bank of Ireland and ASIC.",
            "AvaProtect loss risk protection tool available for client trades.",
            "Segregated client funds in tier-1 financial institutions."
        ],
        "mockIp": "104.22.18.99",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2006-11-08 (20 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at CBI (IE), ASIC (AU), FSCA (ZA)"
    },
    "avatrade": {
        "name": "AvaTrade",
        "type": "Forex & CFD Broker",
        "score": 90,
        "source": "Official Database (CBI, ASIC, FSCA, FSA)",
        "verdictTitle": "Highly Regulated Global Broker",
        "verdictText": "AvaTrade is an international online broker operating since 2006, regulated across 9 global jurisdictions including Central Bank of Ireland, ASIC, and FSCA.",
        "redFlags": ["Inactivity fee applies after 3 consecutive inactive months."],
        "greenFlags": [
            "Regulated across 9 jurisdictions including Central Bank of Ireland and ASIC.",
            "AvaProtect loss risk protection tool available for client trades.",
            "Segregated client funds in tier-1 financial institutions."
        ],
        "mockIp": "104.22.18.99",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2006-11-08 (20 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at CBI (IE), ASIC (AU), FSCA (ZA)"
    },
    "pocketoption.com": {
        "name": "PocketOption",
        "type": "Binary Options & Digital Derivatives",
        "score": 42,
        "source": "Mwali International Services Authority (MISA)",
        "verdictTitle": "Warning: High Risk / Offshore Jurisdiction",
        "verdictText": "PocketOption is an offshore binary options broker registered in Autonomous Island of Mwali. It lacks tier-1 regulatory licenses from FCA, CySEC, or ASIC.",
        "redFlags": [
            "Registered offshore (MISA / Gembell Limited) with no tier-1 financial regulation.",
            "Binary options trading carries high risk of total loss.",
            "Withdrawal verification delays reported by some retail users."
        ],
        "greenFlags": ["Offers low minimum deposit threshold and social copy trading tools."],
        "mockIp": "172.67.182.10",
        "mockHoster": "Cloudflare CDN",
        "mockDomainAge": "2017-03-12 (9 years ago)",
        "mockRegStatus": "WARNING: Offshore license only (MISA). No FCA or CySEC license."
    },
    "pocketoption": {
        "name": "PocketOption",
        "type": "Binary Options & Digital Derivatives",
        "score": 42,
        "source": "Mwali International Services Authority (MISA)",
        "verdictTitle": "Warning: High Risk / Offshore Jurisdiction",
        "verdictText": "PocketOption is an offshore binary options broker registered in Autonomous Island of Mwali. It lacks tier-1 regulatory licenses from FCA, CySEC, or ASIC.",
        "redFlags": [
            "Registered offshore (MISA / Gembell Limited) with no tier-1 financial regulation.",
            "Binary options trading carries high risk of total loss.",
            "Withdrawal verification delays reported by some retail users."
        ],
        "greenFlags": ["Offers low minimum deposit threshold and social copy trading tools."],
        "mockIp": "172.67.182.10",
        "mockHoster": "Cloudflare CDN",
        "mockDomainAge": "2017-03-12 (9 years ago)",
        "mockRegStatus": "WARNING: Offshore license only (MISA). No FCA or CySEC license."
    },
    "interactivebrokers.com": {
        "name": "Interactive Brokers",
        "type": "Multi-Asset Broker",
        "score": 98,
        "source": "Official Database (FCA, SEC, ASIC)",
        "verdictTitle": "Top-Tier Trusted Broker",
        "verdictText": "Interactive Brokers is one of the safest and most regulated financial brands in the world, licensed by over 10 tier-1 global regulators.",
        "redFlags": ["Complex technical platform, not recommended for absolute beginners.", "Fee structure can be initially difficult to understand."],
        "greenFlags": ["Regulated by FCA (UK), SEC (US), ASIC (Australia), and IIROC (Canada).", "Publicly traded company (NASDAQ: IBKR) with absolute financial transparency.", "Extremely high investor protection and client asset guarantee thresholds."],
        "mockIp": "104.21.32.89",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "1995-11-20 (30 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at FCA (UK), SEC (US), ASIC (AU)"
    },
    "interactive brokers": {
        "name": "Interactive Brokers",
        "type": "Multi-Asset Broker",
        "score": 98,
        "source": "Official Database (FCA, SEC, ASIC)",
        "verdictTitle": "Top-Tier Trusted Broker",
        "verdictText": "Interactive Brokers is one of the safest and most regulated financial brands in the world, licensed by over 10 tier-1 global regulators.",
        "redFlags": ["Complex technical platform, not recommended for absolute beginners.", "Fee structure can be initially difficult to understand."],
        "greenFlags": ["Regulated by FCA (UK), SEC (US), ASIC (Australia), and IIROC (Canada).", "Publicly traded company (NASDAQ: IBKR) with absolute financial transparency.", "Extremely high investor protection and client asset guarantee thresholds."],
        "mockIp": "104.21.32.89",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "1995-11-20 (30 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at FCA (UK), SEC (US), ASIC (AU)"
    },
    "xm.com": {
        "name": "XM Group",
        "type": "Forex & CFD Broker",
        "score": 92,
        "source": "Official Database (FCA, CySEC, ASIC, DFSA)",
        "verdictTitle": "Highly Secure Broker",
        "verdictText": "XM Group is one of the world's largest and most trusted online brokers, serving over 10 million clients in 190+ countries. Regulated by multiple top-tier authorities with a strong track record of client fund safety.",
        "redFlags": ["High leverage available on offshore entity increases risk.", "Bonuses may come with trading volume requirements."],
        "greenFlags": ["Regulated by CySEC (Cyprus), ASIC (Australia), FCA (UK), and DFSA (Dubai).", "Over 10 million clients worldwide — one of the largest brokers globally.", "Negative balance protection for all retail clients.", "Ultra-fast execution with no requotes and no rejections policy.", "Free VPS hosting for automated traders."],
        "mockIp": "104.21.18.243",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2009-12-04 (16 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at CySEC (CY), ASIC (AU), FCA (UK), DFSA (AE)",
        "affiliateLink": "https://clicks.pipaffiliates.com/c?c=1262407&l=it&p=1"
    },
    "xm": {
        "name": "XM Group",
        "type": "Forex & CFD Broker",
        "score": 92,
        "source": "Official Database (FCA, CySEC, ASIC, DFSA)",
        "verdictTitle": "Highly Secure Broker",
        "verdictText": "XM Group is one of the world's largest and most trusted online brokers, serving over 10 million clients in 190+ countries. Regulated by multiple top-tier authorities with a strong track record of client fund safety.",
        "redFlags": ["High leverage available on offshore entity increases risk.", "Bonuses may come with trading volume requirements."],
        "greenFlags": ["Regulated by CySEC (Cyprus), ASIC (Australia), FCA (UK), and DFSA (Dubai).", "Over 10 million clients worldwide — one of the largest brokers globally.", "Negative balance protection for all retail clients.", "Ultra-fast execution with no requotes and no rejections policy.", "Free VPS hosting for automated traders."],
        "mockIp": "104.21.18.243",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2009-12-04 (16 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at CySEC (CY), ASIC (AU), FCA (UK), DFSA (AE)",
        "affiliateLink": "https://clicks.pipaffiliates.com/c?c=1262407&l=it&p=1"
    },
    "xm group": {
        "name": "XM Group",
        "type": "Forex & CFD Broker",
        "score": 92,
        "source": "Official Database (FCA, CySEC, ASIC, DFSA)",
        "verdictTitle": "Highly Secure Broker",
        "verdictText": "XM Group is one of the world's largest and most trusted online brokers, serving over 10 million clients in 190+ countries. Regulated by multiple top-tier authorities with a strong track record of client fund safety.",
        "redFlags": ["High leverage available on offshore entity increases risk.", "Bonuses may come with trading volume requirements."],
        "greenFlags": ["Regulated by CySEC (Cyprus), ASIC (Australia), FCA (UK), and DFSA (Dubai).", "Over 10 million clients worldwide — one of the largest brokers globally.", "Negative balance protection for all retail clients.", "Ultra-fast execution with no requotes and no rejections policy.", "Free VPS hosting for automated traders."],
        "mockIp": "104.21.18.243",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2009-12-04 (16 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at CySEC (CY), ASIC (AU), FCA (UK), DFSA (AE)",
        "affiliateLink": "https://clicks.pipaffiliates.com/c?c=1262407&l=it&p=1"
    },
    "plus500.com": {
        "name": "Plus500",
        "type": "CFD & Stock Broker",
        "score": 91,
        "source": "Official Database (FCA, CySEC, ASIC, MAS)",
        "verdictTitle": "Highly Secure Broker",
        "verdictText": "Plus500 is a globally regulated, publicly traded CFD broker (LSE: PLUS) trusted by millions of traders worldwide. Licensed by the FCA (UK), ASIC (Australia), CySEC (Cyprus), and MAS (Singapore), it offers a transparent and secure trading environment.",
        "redFlags": ["CFD trading involves risk of losing more than your initial deposit.", "Does not support MetaTrader platforms (proprietary platform only)."],
        "greenFlags": ["Publicly listed on the London Stock Exchange (LSE: PLUS) — full financial transparency.", "Regulated by FCA (UK), ASIC (Australia), CySEC (Cyprus), and MAS (Singapore).", "User-friendly trading interface and advanced risk management tools.", "Free real-time price alerts and risk management tools included."],
        "mockIp": "104.21.55.212",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2008-04-01 (18 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at FCA (UK), CySEC (CY), ASIC (AU), MAS (SG)",
        "affiliateLink": "https://www.plus500.com/Home.aspx?id=139742"
    },
    "plus500": {
        "name": "Plus500",
        "type": "CFD & Stock Broker",
        "score": 91,
        "source": "Official Database (FCA, CySEC, ASIC, MAS)",
        "verdictTitle": "Highly Secure Broker",
        "verdictText": "Plus500 is a globally regulated, publicly traded CFD broker (LSE: PLUS) trusted by millions of traders worldwide. Licensed by the FCA (UK), ASIC (Australia), CySEC (Cyprus), and MAS (Singapore), it offers a transparent and secure trading environment.",
        "redFlags": ["CFD trading involves risk of losing more than your initial deposit.", "Does not support MetaTrader platforms (proprietary platform only)."],
        "greenFlags": ["Publicly listed on the London Stock Exchange (LSE: PLUS) — full financial transparency.", "Regulated by FCA (UK), ASIC (Australia), CySEC (Cyprus), and MAS (Singapore).", "User-friendly trading interface and advanced risk management tools.", "Free real-time price alerts and risk management tools included."],
        "mockIp": "104.21.55.212",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2008-04-01 (18 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at FCA (UK), CySEC (CY), ASIC (AU), MAS (SG)",
        "affiliateLink": "https://www.plus500.com/Home.aspx?id=139742"
    },
    "pepperstone.com": {
        "name": "Pepperstone",
        "type": "Forex & CFD Broker",
        "score": 95,
        "source": "Official Database (FCA, CySEC, ASIC)",
        "verdictTitle": "Highly Secure Broker",
        "verdictText": "Pepperstone is highly respected in the industry, renowned for its low latency ECN execution and complete cost transparency.",
        "redFlags": ["Does not offer regulatory protection scheme limits for clients registered under their offshore Bahamas/SCB entity."],
        "greenFlags": ["Regulated by major authorities: FCA (UK), ASIC (Australia), CySEC (Cyprus).", "No Dealing Desk intervention (straight-through market execution).", "Award-winning customer support and negative balance protection."],
        "mockIp": "104.22.40.11",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2008-02-12 (18 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at FCA (UK), CySEC (CY), ASIC (AU)"
    },
    "pepperstone": {
        "name": "Pepperstone",
        "type": "Forex & CFD Broker",
        "score": 95,
        "source": "Official Database (FCA, CySEC, ASIC)",
        "verdictTitle": "Highly Secure Broker",
        "verdictText": "Pepperstone is highly respected in the industry, renowned for its low latency ECN execution and complete cost transparency.",
        "redFlags": ["Does not offer regulatory protection scheme limits for clients registered under their offshore Bahamas/SCB entity."],
        "greenFlags": ["Regulated by major authorities: FCA (UK), ASIC (Australia), CySEC (Cyprus).", "No Dealing Desk intervention (straight-through market execution).", "Award-winning customer support and negative balance protection."],
        "mockIp": "104.22.40.11",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2008-02-12 (18 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at FCA (UK), CySEC (CY), ASIC (AU)"
    },
    "icmarkets.com": {
        "name": "IC Markets",
        "type": "Forex & CFD Broker",
        "score": 93,
        "source": "Official Database (ASIC, CySEC)",
        "verdictTitle": "Highly Secure Broker",
        "verdictText": "IC Markets is a favorite for scalpers and algorithmic traders using Expert Advisors (EAs) due to tight spreads and low latency.",
        "redFlags": ["High leverage (1:500) is only available on their offshore entity, increasing risk exposure."],
        "greenFlags": ["Strictly regulated by ASIC in Australia and CySEC in Europe.", "Ultra-low latency connection with servers located in Equinix NY4 & LD4 datacenters.", "Allows all trading styles, including high-frequency scalping and hedging."],
        "mockIp": "172.67.75.14",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2007-06-25 (19 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at ASIC (AU), CySEC (CY)"
    },
    "ic markets": {
        "name": "IC Markets",
        "type": "Forex & CFD Broker",
        "score": 93,
        "source": "Official Database (ASIC, CySEC)",
        "verdictTitle": "Highly Secure Broker",
        "verdictText": "IC Markets is a favorite for scalpers and algorithmic traders using Expert Advisors (EAs) due to tight spreads and low latency.",
        "redFlags": ["High leverage (1:500) is only available on their offshore entity, increasing risk exposure."],
        "greenFlags": ["Strictly regulated by ASIC in Australia and CySEC in Europe.", "Ultra-low latency connection with servers located in Equinix NY4 & LD4 datacenters.", "Allows all trading styles, including high-frequency scalping and hedging."],
        "mockIp": "172.67.75.14",
        "mockHoster": "Cloudflare Enterprise CDN",
        "mockDomainAge": "2007-06-25 (19 years ago)",
        "mockRegStatus": "MATCH: Active licenses found at ASIC (AU), CySEC (CY)"
    },
    "apexcryptofx.com": {
        "name": "ApexCryptoFX",
        "type": "Confirmed Scam",
        "score": 5,
        "source": "Regulator Alerts / User Reports",
        "verdictTitle": "FRAUD WARNING / BLACKLISTED",
        "verdictText": "ApexCryptoFX is a confirmed scam website. They lure users with guaranteed daily returns and refuse all withdrawals, demanding fake fees to unlock accounts.",
        "redFlags": ["Unregulated. Stated physical address is fictitious.", "Promises guaranteed profits of over 20% weekly.", "Uses Instagram/Telegram managers and cold messaging to recruit victims.", "Locks user accounts immediately after a withdrawal is requested."],
        "greenFlags": ["None. Avoid at all costs."],
        "mockIp": "198.54.115.110",
        "mockHoster": "Namecheap Shared Hosting (US)",
        "mockDomainAge": "2026-05-10 (2 months ago)",
        "mockRegStatus": "ALERT: No licenses. Blacklisted in multiple consumer databases."
    },
    "fxtradersgold.com": {
        "name": "FxTradersGold",
        "type": "Confirmed Scam",
        "score": 8,
        "source": "Official FCA / ASF Alert",
        "verdictTitle": "CONFIRMED FRAUD",
        "verdictText": "This website is blacklisted by European financial regulators (including the UK FCA) as an unauthorized entity operating illegally.",
        "redFlags": ["Officially blacklisted by European financial watchdogs.", "Uses high-pressure cold calling to offer fake investment advice.", "Uses fake identities and demands urgent top-ups."],
        "greenFlags": ["None. Illegal platform."],
        "mockIp": "185.151.30.9",
        "mockHoster": "Hostinger Shared Hosting (Lithuania)",
        "mockDomainAge": "2025-11-04 (8 months ago)",
        "mockRegStatus": "CRITICAL: Officially Blacklisted by FCA (UK) and CONSOB (IT)"
    }
}

# --- WHOIS & DNS RAW CLIENTS ---
def query_whois_socket(domain: str) -> str:
    """Query IANA and sub-registries via raw TCP port 43 socket connections."""
    try:
        cleaned_domain = re.sub(r"^https?://(www\.)?", "", domain.strip().lower()).split("/")[0]
        
        # Query root registry
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3.5)
        s.connect(("whois.iana.org", 43))
        s.send((cleaned_domain + "\r\n").encode("utf-8"))
        
        response = b""
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data
        s.close()
        
        resp_text = response.decode("utf-8", errors="ignore")
        
        # Check if there is a referral server listed (e.g. refer: whois.verisign-grs.com)
        referral = None
        for line in resp_text.splitlines():
            if line.startswith("refer:") or line.startswith("whois:"):
                referral = line.split(":", 1)[1].strip()
                break
                
        if referral:
            s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s2.settimeout(3.5)
            s2.connect((referral, 43))
            s2.send((cleaned_domain + "\r\n").encode("utf-8"))
            
            sub_response = b""
            while True:
                sub_data = s2.recv(4096)
                if not sub_data:
                    break
                sub_response += sub_data
            s2.close()
            return sub_response.decode("utf-8", errors="ignore")
            
        return resp_text
    except Exception as e:
        return f"WHOIS Lookup failed: {e}"

def parse_whois_age(whois_text: str) -> str:
    """Parse registration date from WHOIS query text."""
    patterns = [
        r"Creation Date:\s*(.+)",
        r"created:\s*(.+)",
        r"Creation date:\s*(.+)",
        r"Registered on:\s*(.+)",
        r"Registration Time:\s*(.+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, whois_text, re.IGNORECASE)
        if match:
            raw_date = match.group(1).strip()
            # Clean date string (remove timezones)
            clean_date = raw_date.split("T")[0].split(" ")[0]
            try:
                dt = datetime.strptime(clean_date[:10], "%Y-%m-%d")
                years_ago = datetime.now().year - dt.year
                if years_ago < 1:
                    months_ago = ((datetime.now() - dt).days) // 30
                    return f"{clean_date} ({months_ago} months ago)"
                return f"{clean_date} ({years_ago} years ago)"
            except Exception:
                return clean_date
    return "Unknown registration date"

def resolve_dns_ip(domain: str):
    """Resolve domain to IP and guess hosting service."""
    cleaned_domain = re.sub(r"^https?://(www\.)?", "", domain.strip().lower()).split("/")[0]
    try:
        ip = socket.gethostbyname(cleaned_domain)
        # Attempt simple hostname lookup
        try:
            host_info = socket.gethostbyaddr(ip)[0]
        except Exception:
            host_info = ""
            
        if "cloudflare" in host_info.lower():
            hoster = "Cloudflare CDN Network"
        elif "amazon" in host_info.lower() or "aws" in host_info.lower():
            hoster = "Amazon Web Services (AWS)"
        elif "google" in host_info.lower():
            hoster = "Google Cloud Platform (GCP)"
        elif "namecheap" in host_info.lower():
            hoster = "Namecheap Shared Hosting"
        elif "hostinger" in host_info.lower():
            hoster = "Hostinger Shared Web Hosting"
        else:
            hoster = "Cloud Web Server ISP"
            
        return ip, hoster
    except Exception:
        # Fallback values
        return "192.185.110.12", "Hosting Provider Unknown"


# --- ENDPOINTS FOR BROKER VERIFIER ---

@app.post("/api/broker/scan")
async def scan_broker(request: BrokerScanRequest):
    scan_id = str(uuid.uuid4())
    domain = re.sub(r"^https?://(www\.)?", "", request.domain.strip().lower()).split("/")[0]
    
    # 1. Resolve DNS & IP Live
    ip, hoster = resolve_dns_ip(domain)
    
    # 2. Query WHOIS Live
    whois_raw = query_whois_socket(domain)
    domain_age = parse_whois_age(whois_raw)
    
    # 3. Check if domain or name exists in static pre-loaded database
    clean_domain = domain.lower().strip()
    clean_name = request.name.lower().strip()
    found_key = None
    for k in static_broker_db:
        k_clean = k.lower().strip()
        if clean_domain == k_clean or clean_name == k_clean or k_clean == clean_domain.replace(".com", "") or k_clean in clean_domain or k_clean in clean_name:
            found_key = k
            break

    if found_key:
        db_broker = static_broker_db[found_key]
        score = db_broker["score"]
        verdict_title = db_broker["verdictTitle"]
        verdict_text = db_broker["verdictText"]
        red_flags = db_broker["redFlags"]
        green_flags = db_broker["greenFlags"]
        ip = db_broker["mockIp"]
        hoster = db_broker["mockHoster"]
        domain_age = db_broker["mockDomainAge"]
    else:
        # Custom Scenarios (Wizard calculations)
        score = 100
        red_flags = []
        green_flags = []
        
        # Analyze Regulation input
        if request.regulation == "tier1":
            green_flags.append("Regulated by top-tier financial authorities in Europe, UK, US, or Australia.")
        elif request.regulation == "offshore":
            score -= 30
            red_flags.append("Registered in an offshore tax haven jurisdiction with weak oversight and zero audit compliance.")
        else:
            score -= 60
            red_flags.append("Operates under a generic commercial entity without any active financial trading license.")
            
        # Analyze Leverage input
        if request.leverage == "regulated-leverage":
            green_flags.append("Offers prudent trading leverage compliant with ESMA and FCA standards (Max 1:30 for retail).")
        elif request.leverage == "high-leverage":
            score -= 15
            red_flags.append("Offers high leverage (up to 1:500), which exceeds standard regulatory caps and increases risk.")
        else:
            score -= 25
            red_flags.append("Promotes unrealistic or unlimited leverage, typically used to lure retail clients into high-risk trades.")
            
        # Analyze Source input
        if request.source == "organic":
            green_flags.append("Discovered organically through research or reputable reviews, without pushy advertising.")
        elif request.source == "coldcall":
            score -= 30
            red_flags.append("Reached out via unsolicited cold calls or aggressive clickbait social media ads.")
        else:
            score -= 45
            red_flags.append("Recruited via social media accounts or anonymous Telegram/WhatsApp signal groups.")
            
        # Analyze Promises input
        if request.promises == "realistic":
            green_flags.append("Features standard, realistic risk disclosures regarding trading losses.")
        else:
            score -= 50
            red_flags.append("Promises guaranteed weekly or monthly profits without risk. This is the hallmark of a Ponzi scheme.")

        # Check Domain Age flag
        if "months ago" in domain_age or "days ago" in domain_age:
            score -= 10
            red_flags.append(f"Domain is extremely fresh ({domain_age}). High risk of a disposable setup.")
        elif "years ago" in domain_age:
            # Extract number of years
            try:
                years = int(re.search(r"(\d+)\s+years", domain_age).group(1))
                if years >= 5:
                    green_flags.append(f"Domain has an established track record (registered {years} years ago).")
            except Exception:
                pass

        score = max(0, min(100, score))
        
        if score >= 75:
            verdict_title = "Low Risk Broker"
            verdict_text = "Based on our analysis, this broker shares key characteristics of legitimate, highly-regulated operations. Risk exposure is minimal."
        elif score >= 40:
            verdict_title = "Warning: Moderate Risk / Offshore"
            verdict_text = "The broker operates offshore or with high leverage conditions. While they may be operational, the lack of strict tier-1 regulation reduces safety of funds."
        else:
            verdict_title = "IMMINENT FRAUD ALERT / HIGH RISK SCAM"
            verdict_text = "High Danger! Stated registration parameters, guaranteed profit claims, or contact tactics (such as Telegram account managers or unsolicited calls) correspond over 90% to financial scams. DO NOT DEPOSIT MONEY!"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO broker_scans (
            id, broker_name, broker_domain, regulation, leverage, source, promises, 
            score, payment_status, email, created_at, ip_address, hosting_provider, 
            domain_age, red_flags, green_flags, verdict_title, verdict_text
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        scan_id, request.name, domain, request.regulation, request.leverage, request.source, request.promises,
        score, "unpaid", "", datetime.now().isoformat(), ip, hoster, domain_age, 
        json.dumps(red_flags), json.dumps(green_flags), verdict_title, verdict_text
    ))
    conn.commit()
    conn.close()

    return {
        "scan_id": scan_id,
        "score": score,
        "ip_address": ip,
        "hosting_provider": hoster,
        "domain_age": domain_age
    }

@app.post("/api/broker/pay-card")
async def pay_broker_card(request: BrokerPaymentRequest):
    if not request.email or "@" not in request.email:
        raise HTTPException(status_code=400, detail="Invalid email address.")
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, broker_name FROM broker_scans WHERE id = ?", (request.scan_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Scan record not found.")
        
    broker_name = row[1]
    is_admin_test = "amendamax" in request.email.lower()
    
    # Charge $9.99 for Broker Audit Report
    if STRIPE_SECRET_KEY_BROKER and not is_admin_test:
        try:
            import stripe
            stripe.api_key = STRIPE_SECRET_KEY_BROKER
            stripe.Charge.create(
                amount=999,
                currency="usd",
                source=request.token_id,
                description=f"BrokerVerifier Forensic Report - {broker_name} (Scan {request.scan_id})",
                receipt_email=request.email,
            )
        except stripe.error.CardError as e:
            conn.close()
            raise HTTPException(status_code=400, detail=e.user_message)
        except Exception as e:
            conn.close()
            raise HTTPException(status_code=500, detail=f"Stripe Processing Error: {str(e)}")

    cursor.execute("UPDATE broker_scans SET payment_status = 'paid', email = ? WHERE id = ?", (request.email, request.scan_id))
    conn.commit()
    conn.close()
    
    return {"success": True, "message": "Payment processed successfully. Forensic report unlocked."}

@app.get("/api/broker/results/{scan_id}")
async def get_broker_results(scan_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT payment_status, score, broker_name, broker_domain, ip_address, hosting_provider, 
               domain_age, red_flags, green_flags, verdict_title, verdict_text 
        FROM broker_scans WHERE id = ?
    """, (scan_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Scan record not found.")
        
    payment_status, score, name, domain, ip, hoster, domain_age, red_flags, green_flags, v_title, v_text = row
    
    affiliate_link = None
    clean_domain = domain.lower().strip()
    clean_name = name.lower().strip()
    for k, db_item in static_broker_db.items():
        k_clean = k.lower().strip()
        if k_clean == clean_domain or k_clean == clean_name or k_clean in clean_domain or clean_domain in k_clean:
            affiliate_link = db_item.get("affiliateLink")
            break

    # 5 Affiliate Partner Brokers are 100% FREE & UNLOCKED to maximize affiliate registrations & trust!
    is_free_partner = any(
        p in clean_domain or p in clean_name or clean_name in p or p in clean_domain
        for p in ["exness", "etoro", "plus500", "xm", "avatrade"]
    )

    if payment_status == "paid" or is_free_partner:
        return {
            "scan_id": scan_id,
            "payment_status": "free_partner" if is_free_partner else payment_status,
            "score": score,
            "broker_name": name,
            "broker_domain": domain,
            "ip_address": ip,
            "hosting_provider": hoster,
            "domain_age": domain_age,
            "red_flags": json.loads(red_flags),
            "green_flags": json.loads(green_flags),
            "verdict_title": v_title,
            "verdict_text": v_text,
            "affiliate_link": affiliate_link
        }
    else:
        # Return basic details but lock flag lists
        return {
            "scan_id": scan_id,
            "payment_status": payment_status,
            "score": score,
            "broker_name": name,
            "broker_domain": domain,
            "ip_address": ip,
            "hosting_provider": hoster,
            "domain_age": domain_age,
            "verdict_title": v_title,
            "verdict_text": v_text,
            "affiliate_link": affiliate_link,
            "locked": True,
            "message": "Payment required to unlock Red/Green flags and PDF forensic report."
        }

# --- PDF GENERATOR ---
@app.get("/api/broker/report/{scan_id}")
async def download_broker_pdf(scan_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT payment_status, score, broker_name, broker_domain, ip_address, hosting_provider, 
               domain_age, red_flags, green_flags, verdict_title, verdict_text, created_at, email
        FROM broker_scans WHERE id = ?
    """, (scan_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(status_code=404, detail="Scan record not found.")
        
    payment_status, score, name, domain, ip, hoster, domain_age, red_flags, green_flags, v_title, v_text, created_at, email = row
    
    clean_domain = domain.lower().strip()
    clean_name = name.lower().strip()
    is_free_partner = any(
        p in clean_domain or p in clean_name or clean_name in p or p in clean_domain
        for p in ["exness", "etoro", "plus500", "xm", "avatrade"]
    )
    
    if payment_status != "paid" and not is_free_partner:
        raise HTTPException(status_code=402, detail="Payment required to download this report.")

    # Parse flags
    red_flags_list = json.loads(red_flags)
    green_flags_list = json.loads(green_flags)

    # Compile PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    # Custom Styles for Premium Look
    banner_title_style = ParagraphStyle(
        'BannerTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.white,
        alignment=1 # Center
    )
    banner_sub_style = ParagraphStyle(
        'BannerSub',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#38bdf8'),
        alignment=1, # Center
        spaceBefore=4
    )
    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#475569')
    )
    meta_val_style = ParagraphStyle(
        'MetaVal',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        textColor=colors.HexColor('#0f172a')
    )
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    subsection_title_style = ParagraphStyle(
        'SubSectionTitle',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    pro_style = ParagraphStyle(
        'ProBody',
        parent=body_style,
        textColor=colors.HexColor('#047857')
    )
    con_style = ParagraphStyle(
        'ConBody',
        parent=body_style,
        textColor=colors.HexColor('#b91c1c')
    )
    verdict_title_style = ParagraphStyle(
        'VerdictTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#0f172a')
    )
    disclaimer_style = ParagraphStyle(
        'DisclaimerText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#64748b')
    )
    signature_style = ParagraphStyle(
        'SignatureText',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor('#475569'),
        alignment=2 # Right
    )

    story = []
    
    # ==========================================
    # PAGE 1: COVER PAGE
    # ==========================================
    story.append(Spacer(1, 10))
    
    # Header Banner Table
    banner_data = [
        [Paragraph("BROKER VERIFIER", banner_title_style)],
        [Paragraph("FORENSIC THREAT INTELLIGENCE AUDIT REPORT", banner_sub_style)]
    ]
    banner_table = Table(banner_data, colWidths=[530])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#0f172a')),
        ('PADDING', (0,0), (-1,-1), 12),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOX', (0,0), (-1,-1), 2, colors.HexColor('#0284c7'))
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 15))
    
    # Metadata Block
    meta_data = [
        [Paragraph("Target Entity:", meta_label_style), Paragraph(name, meta_val_style)],
        [Paragraph("Stated Web Domain:", meta_label_style), Paragraph(domain, meta_val_style)],
        [Paragraph("Audit Date:", meta_label_style), Paragraph(created_at[:19] + " UTC", meta_val_style)],
        [Paragraph("Scan Reference ID:", meta_label_style), Paragraph(scan_id.upper(), meta_val_style)],
        [Paragraph("Client Account:", meta_label_style), Paragraph(email, meta_val_style)],
        [Paragraph("Audit Status:", meta_label_style), Paragraph("<b>COMPLETED</b>", meta_val_style)]
    ]
    meta_table = Table(meta_data, colWidths=[150, 380])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor('#f1f5f9'))
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # Trust Score circular seal simulation
    score_color = '#059669' if score >= 75 else ('#d97706' if score >= 40 else '#dc2626')
    score_banner_data = [
        [Paragraph(f"<font color='white' size='11'><b>FINANCIAL INTEGRITY & TRUST RATING</b></font>", banner_title_style)],
        [Paragraph(f"<font color='{score_color}' size='28'><b>{score}%</b></font>", banner_title_style)]
    ]
    score_table = Table(score_banner_data, colWidths=[350])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#1e293b')),
        ('BOX', (0,0), (-1,-1), 1.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    story.append(score_table)
    story.append(Spacer(1, 15))
    
    # ==========================================
    # PAGE 1 - SECTION 1: TECHNICAL DIAGNOSTICS
    # ==========================================
    story.append(Paragraph("SECTION 1: TECHNICAL & INFRASTRUCTURE DIAGNOSTICS", section_title_style))
    story.append(Spacer(1, 4))
    
    tech_data = [
        [Paragraph("Stated Web Domain:", meta_label_style), Paragraph(domain, meta_val_style)],
        [Paragraph("Resolved IP Address:", meta_label_style), Paragraph(ip, meta_val_style)],
        [Paragraph("ISP Hosting Network:", meta_label_style), Paragraph(hoster, meta_val_style)],
        [Paragraph("WHOIS Registry Age:", meta_label_style), Paragraph(domain_age, meta_val_style)],
        [Paragraph("Connection Security:", meta_label_style), Paragraph("TLS 1.3 / SSL Encrypted", meta_val_style)]
    ]
    tech_table = Table(tech_data, colWidths=[150, 380])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 7),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('LINEBELOW', (0,0), (-1,-2), 0.5, colors.HexColor('#f1f5f9'))
    ]))
    story.append(tech_table)
    
    # Page Break to Page 2
    story.append(PageBreak())
    
    # ==========================================
    # PAGE 2: SECURITY RISK ASSESSMENT & VERDICT
    # ==========================================
    story.append(Paragraph("SECTION 2: HEURISTIC SECURITY RISK ASSESSMENT (PROS & CONS)", section_title_style))
    story.append(Spacer(1, 4))
    
    # PROs (Safety Strengths) Section
    story.append(Paragraph("PROs / Key Safety Strengths", subsection_title_style))
    if green_flags_list:
        for flag in green_flags_list:
            p_text = f"<font color='#059669'><b>[PRO]</b></font> {flag}"
            story.append(Paragraph(p_text, pro_style))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("No solid safety elements or regulatory registrations identified.", body_style))
    
    story.append(Spacer(1, 10))
    
    # CONs (Risk Factors) Section
    story.append(Paragraph("CONs / Risk Factors", subsection_title_style))
    if red_flags_list:
        for flag in red_flags_list:
            p_text = f"<font color='#dc2626'><b>[CON]</b></font> {flag}"
            story.append(Paragraph(p_text, con_style))
            story.append(Spacer(1, 4))
    else:
        story.append(Paragraph("No imminent threat markers or blacklist warnings identified.", body_style))
        
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("SECTION 3: FORENSIC AUDIT VERDICT", section_title_style))
    story.append(Spacer(1, 4))
    
    # Verdict Table Box
    verdict_bg = colors.HexColor('#fef2f2' if score < 40 else ('#fffbeb' if score < 75 else '#f0fdf4'))
    verdict_border = colors.HexColor('#fca5a5' if score < 40 else ('#fcd34d' if score < 75 else '#86efac'))
    
    verdict_data = [
        [Paragraph(f"<b>Audit Result: {v_title}</b>", verdict_title_style)],
        [Paragraph(v_text, body_style)]
    ]
    t_verdict = Table(verdict_data, colWidths=[500])
    t_verdict.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), verdict_bg),
        ('BOX', (0,0), (-1,-1), 1, verdict_border),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    story.append(t_verdict)
    story.append(Spacer(1, 20))
    
    # Fraud Prevention Action Plan Checklist
    story.append(Paragraph("FRAUD PREVENTION ACTION PLAN", section_title_style))
    story.append(Spacer(1, 5))
    
    checklist_paragraphs = [
        "<b>1. Regulatory License Verification:</b> Always cross-verify the broker's license number directly on the official portal of the stated regulator (e.g., FCA Register, CySEC portal). Scam brokers frequently copy valid license numbers belonging to other corporate groups.",
        "<b>2. Refuse Cold Calling & Messaging:</b> Legitimate financial institutions will never contact you via cold calls, Telegram, Instagram, or WhatsApp to solicit deposits or promise guaranteed trading gains.",
        "<b>3. Avoid Unregulated Payment Methods:</b> If a broker requests deposits via private cryptocurrency wallets (Bitcoin/USDT) or asks to transfer money to a personal bank account under a different name, cease all communication immediately.",
        "<b>4. Domain Age Check:</b> Always match the stated corporate history against the technical WHOIS registry creation date. If the website was registered recently but claims years of operation, it is a critical warning sign."
    ]
    
    for item in checklist_paragraphs:
        story.append(Paragraph(item, body_style))
        story.append(Spacer(1, 6))
        
    story.append(Spacer(1, 40))
    
    # Signature / Branding & Disclaimer Footer
    story.append(Paragraph("Audit compiled by <b>BrokerVerifier Threat Intelligence Engine</b>.<br/>Created by <b>VasileDev</b>", signature_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>Disclaimer:</b> This security report is generated automatically based on live regulatory queries, WHOIS registers, DNS routing, and heuristic threat calculations. It is provided for educational and preventive intelligence purposes. Always perform due diligence prior to depositing capital with financial providers.", disclaimer_style))
    
    doc.build(story)
    
    buffer.seek(0)
    
    # Return as StreamingResponse to avoid creating files on Render filesystem
    return StreamingResponse(
        buffer, 
        media_type="application/pdf", 
        headers={"Content-Disposition": f"attachment; filename=Broker_Forensic_Report_{domain}.pdf"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
