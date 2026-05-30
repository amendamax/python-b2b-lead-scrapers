import os
import shutil
from pathlib import Path

# Folderele sursă de unde extragem (backups vechi)
SOURCE_FOLDERS = [
    r"F:\AAAAAAAAAAAA",
    r"F:\ddddd",
    r"F:\hardisck",
    r"F:\hardul meu",
    r"F:\mihai hard",
    r"F:\DE PE HDD EXTERN"
]

DEST_FOLDER = r"F:\3_Extrase_din_Backups"

# Extensiile pe care vrem să le salvăm
EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', # Poze
    '.mp4', '.avi', '.mkv', '.mov',          # Video
    '.doc', '.docx', '.xls', '.xlsx', '.pdf',# Documente
    '.mp3', '.wav'                           # Audio
}

def extract_files():
    if not os.path.exists(DEST_FOLDER):
        os.makedirs(DEST_FOLDER)

    total_copied = 0
    for src in SOURCE_FOLDERS:
        if not os.path.exists(src):
            print(f"Folderul {src} nu a fost gasit. Se sare peste.")
            continue
            
        print(f"Incep extragerea din: {src}")
        for root, _, files in os.walk(src):
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in EXTENSIONS:
                    source_path = os.path.join(root, file)
                    # Pentru a evita suprascrierea, vom adăuga un sufix sau vom folosi numele original dacă e unic
                    dest_path = os.path.join(DEST_FOLDER, file)
                    
                    # Evităm suprascrierea (în caz că există mai multe poze cu același nume ex: image.jpg)
                    counter = 1
                    while os.path.exists(dest_path):
                        name = Path(file).stem
                        dest_path = os.path.join(DEST_FOLDER, f"{name}_{counter}{ext}")
                        counter += 1
                        
                    try:
                        shutil.move(source_path, dest_path)
                        total_copied += 1
                    except Exception as e:
                        print(f"Eroare la mutarea {source_path}: {e}")

    print(f"\nExtragerea a fost finalizata! Au fost mutate {total_copied} fisiere valoroase in {DEST_FOLDER}.")

if __name__ == "__main__":
    extract_files()
