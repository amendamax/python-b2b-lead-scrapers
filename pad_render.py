from PIL import Image

input_path = r"C:\Users\bratu\.gemini\antigravity\brain\8960e2a1-35c4-4c3d-b5da-5f0490b1f189\.user_uploaded\media_1791578547961_480fcc4d.png"
output_path = r"C:\Users\bratu\Desktop\render_metrics_upwork.png"

try:
    with Image.open(input_path) as im:
        print(f"Original Render screenshot size: {im.size}")
        
        # Upwork wants at least 1000x750. Let's make it 1200x900
        new_im = Image.new("RGB", (1200, 900), (10, 10, 10)) # Dark background to match Render
        
        # Resize to fit inside 1200x900 while maintaining aspect ratio
        im.thumbnail((1200, 900), Image.Resampling.LANCZOS)
        
        # Center it
        paste_x = (1200 - im.width) // 2
        paste_y = (900 - im.height) // 2
        
        new_im.paste(im, (paste_x, paste_y))
        new_im.save(output_path, "PNG")
        print("Created padded Render metrics image on Desktop!")
except Exception as e:
    print(f"Error: {e}")
