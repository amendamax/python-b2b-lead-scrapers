from PIL import Image

# Path to the original generated image (it should still be in your amazing-borg repo as .webp)
webp_path = r"C:\Users\bratu\Documents\antigravity\amazing-borg\seo_fleet_dashboard.webp"
png_path = r"C:\Users\bratu\Desktop\seo_fleet_dashboard.png"

try:
    with Image.open(webp_path) as im:
        im.save(png_path, "PNG")
    print("Image restored to Desktop as PNG")
except Exception as e:
    print(f"Error restoring image: {e}")
