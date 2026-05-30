import sys
from moviepy import VideoFileClip

def crop_video(input_path, output_path, crop_top_pixels):
    print(f"Se încarcă videoclipul: {input_path}...")
    clip = VideoFileClip(input_path)
    width, height = clip.size
    print(f"Dimensiuni originale: {width}x{height}")
    
    # Calculăm noua zonă. Tăiem doar de sus.
    # crop(x1, y1, x2, y2) sau crop(y1=...) din moviepy
    # În moviepy v2.0+, clip.cropped se folosește astfel:
    # Sau folosind fx.crop:
    # clip.cropped(y1=crop_top_pixels)
    
    new_clip = clip.cropped(y1=crop_top_pixels)
    print(f"Dimensiuni noi după crop: {new_clip.size}")
    
    print("Se salvează videoclipul optimizat (poate dura câteva secunde)...")
    # Folosim libx264 pentru compatibilitate maximă și compresie excelentă
    new_clip.write_videofile(
        output_path, 
        codec="libx264", 
        audio_codec="aac",
        temp_audiofile="temp-audio.m4a",
        remove_temp=True
    )
    print("Finalizat cu succes!")

if __name__ == "__main__":
    crop_video("0508.mp4", "0508_upwork.mp4", 50)
