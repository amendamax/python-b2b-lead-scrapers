from PIL import Image
import sys

img_path = r"C:\Users\bratu\.gemini\antigravity\brain\8960e2a1-35c4-4c3d-b5da-5f0490b1f189\seo_fleet_dashboard_1791573349855.jpg"
target_path = r"C:\Users\bratu\Documents\antigravity\amazing-borg\seo_fleet_dashboard.webp"

try:
    with Image.open(img_path) as im:
        im.save(target_path, "WEBP", quality=90)
    print("Converted to webp!")
except Exception as e:
    print(f"Error: {e}")
