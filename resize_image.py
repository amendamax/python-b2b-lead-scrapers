from PIL import Image

png_path = r"C:\Users\bratu\Desktop\seo_fleet_dashboard.png"

try:
    with Image.open(png_path) as im:
        print(f"Original size: {im.size}")
        # Upwork prefers 4:3 ratio. Let's make it 1200x900.
        # But wait, we don't want to stretch it badly.
        # Let's paste it onto a 1200x900 black background to keep it looking perfect.
        new_im = Image.new("RGB", (1200, 900), (10, 15, 29))
        
        # Calculate position to center it
        # If original is 1024x1024, it won't fit in 900 height.
        # So we resize the original first to fit inside 1200x900 while maintaining aspect ratio
        im.thumbnail((1200, 900), Image.Resampling.LANCZOS)
        
        # Now center it
        paste_x = (1200 - im.width) // 2
        paste_y = (900 - im.height) // 2
        
        new_im.paste(im, (paste_x, paste_y))
        new_im.save(png_path, "PNG")
        print(f"Resized and padded to: {new_im.size}")
except Exception as e:
    print(f"Error: {e}")
