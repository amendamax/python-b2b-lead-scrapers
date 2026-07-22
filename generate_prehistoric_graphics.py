import os
from PIL import Image, ImageDraw, ImageFont

def generate_multiline_png(lines, filename, font_path, font_size=150, text_color=(57, 255, 20), padding=40, line_spacing=20):
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()

    line_sizes = []
    max_width = 0
    total_height = 0
    
    for line in lines:
        try:
            bbox = font.getbbox(line)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
            offset_x, offset_y = bbox[0], bbox[1]
        except AttributeError:
            w, h = font.getsize(line)
            offset_x, offset_y = 0, 0
        line_sizes.append((w, h, offset_x, offset_y))
        max_width = max(max_width, w)
        total_height += h

    total_height += line_spacing * (len(lines) - 1)
    
    img_width = max_width + (padding * 2)
    img_height = total_height + (padding * 2)
    
    image = Image.new("RGBA", (img_width, img_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    current_y = padding
    for i, line in enumerate(lines):
        w, h, offset_x, offset_y = line_sizes[i]
        # Center-align lines
        x_pos = padding + (max_width - w) // 2
        draw.text((x_pos - offset_x, current_y - offset_y), line, font=font, fill=text_color)
        current_y += h + line_spacing
        
    image.save(filename)
    print(f"Saved {filename}")

if __name__ == "__main__":
    fonts = [
        r"C:\Windows\Fonts\consola.ttf",
        r"C:\Windows\Fonts\cour.ttf",
    ]
    
    selected_font = None
    for f in fonts:
        if os.path.exists(f):
            selected_font = f
            break
    if not selected_font:
        selected_font = "arial.ttf"

    output_dir = r"C:\Users\bratu\Documents\antigravity\amazing-borg"
    
    prehistoric_lines = [
        "Manual trading is prehistoric.",
        "I lose money with Python."
    ]
    
    colors = {
        "green": (57, 255, 20, 255),
        "white": (255, 255, 255, 255)
    }

    # Generate
    for color_name, color_rgba in colors.items():
        generate_multiline_png(
            prehistoric_lines,
            os.path.join(output_dir, f"manual_prehistoric_{color_name}.png"),
            selected_font, font_size=150, text_color=color_rgba, line_spacing=40
        )
