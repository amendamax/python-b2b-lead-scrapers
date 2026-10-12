from PIL import Image

webp_path = r"C:\Users\bratu\Desktop\seo_fleet_dashboard.webp"
png_path = r"C:\Users\bratu\Desktop\seo_fleet_dashboard.png"

try:
    with Image.open(webp_path) as im:
        im.save(png_path, "PNG")
    print("Converted to PNG")
except Exception as e:
    print(f"Error: {e}")
