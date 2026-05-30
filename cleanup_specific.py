import os
import shutil

base_dir = r"G:\Downloads"
carti_dir = r"G:\1_Cursuri_si_Educatie\CARTI"
if not os.path.exists(carti_dir):
    os.makedirs(carti_dir)

# Cautam si mutam fisierele cerute
moved = 0
for root, dirs, files in os.walk(base_dir):
    for f in files:
        f_lower = f.lower()
        if "pythonlearn.pdf" in f_lower or "sanda marin" in f_lower:
            src = os.path.join(root, f)
            dst = os.path.join(carti_dir, f)
            try:
                shutil.move(src, dst)
                print(f"Salvat cu succes: {f}")
                moved += 1
            except Exception as e:
                print(f"Eroare la salvarea {f}: {e}")

# Stergem directoarele cerute
folders_to_delete = [
    "Computer, Technology and Engineering And More Educational Books Collection 3 - Mantesh",
    "electrotehnica",
    "Free_Download_Manager",
    "GetFreeCourses.Co-Udemy-The Ultimate 2023 Fullstack Web Development Bootcamp_Nice_Voice_and_grafic;)"
]

deleted = 0
for fd in folders_to_delete:
    path = os.path.join(base_dir, fd)
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            print(f"Sters definitiv: {fd}")
            deleted += 1
        except Exception as e:
            print(f"Eroare la stergere {fd}: {e}")

print(f"Operatiune finalizata. Fisiere salvate: {moved}. Foldere sterse: {deleted}.")
