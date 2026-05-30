import os
import shutil
import datetime
from pathlib import Path

SOURCE_FOLDERS = [
    r"F:\DE PE HDD EXTERN",
    r"F:\hardisck",
    r"F:\hardul meu",
    r"F:\mihai hard"
]

DEST_FOLDER = r"F:\3_Extrase_din_Backups\Sortate_pe_Ani"

EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.thm', # Foto si thumbnails
    '.mp4', '.avi', '.mkv', '.mov', '.mpg', '.3gp', '.mts', # Video (inclusiv formate vechi)
    '.doc', '.docx', '.xls', '.xlsx', '.pdf', # Documente
    '.mp3', '.wav' # Audio
}

def extract_and_sort():
    total_moved = 0
    for src in SOURCE_FOLDERS:
        if not os.path.exists(src):
            print(f"Folderul {src} nu exista. Se sare peste.")
            continue
            
        print(f"Incep scanarea in: {src}")
        for root, _, files in os.walk(src):
            for file in files:
                ext = Path(file).suffix.lower()
                if ext in EXTENSIONS:
                    source_path = os.path.join(root, file)
                    
                    try:
                        # Obtinem data modificarii fisierului
                        mtime = os.path.getmtime(source_path)
                        year = datetime.datetime.fromtimestamp(mtime).year
                        
                        # Cream folderul specific anului daca nu exista
                        year_folder = os.path.join(DEST_FOLDER, str(year))
                        if not os.path.exists(year_folder):
                            os.makedirs(year_folder)
                            
                        # Setam calea destinatiei si rezolvam coliziunile de nume
                        dest_path = os.path.join(year_folder, file)
                        counter = 1
                        while os.path.exists(dest_path):
                            name = Path(file).stem
                            dest_path = os.path.join(year_folder, f"{name}_{counter}{ext}")
                            counter += 1
                            
                        # Mutam fisierul
                        shutil.move(source_path, dest_path)
                        total_moved += 1
                    except Exception as e:
                        print(f"Eroare la procesarea fisierului {source_path}: {e}")

    print(f"\nFinalizat! Au fost sortate si mutate pe ani {total_moved} de amintiri/fisiere in {DEST_FOLDER}.")

if __name__ == "__main__":
    extract_and_sort()
