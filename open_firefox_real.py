import os
import subprocess
import winreg

def get_firefox_path():
    # 1. Try Registry App Paths
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\firefox.exe")
        path, _ = winreg.QueryValueEx(key, "")
        if os.path.exists(path):
            return path
    except Exception:
        pass

    # 2. Try common standard installation paths
    candidates = [
        r"C:\Program Files\Mozilla Firefox\firefox.exe",
        r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        os.path.expanduser(r"~\AppData\Local\Mozilla Firefox\firefox.exe"),
        os.path.expanduser(r"~\AppData\Local\Programs\Mozilla Firefox\firefox.exe"),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None

ff_path = get_firefox_path()
print(f"[*] Firefox path gasit: {ff_path}")

urls = [
    "https://www.upwork.com/nx/search/jobs/?q=mt5&sort=recency",
    "https://www.upwork.com/nx/search/jobs/?q=mql5&sort=recency",
    "https://www.upwork.com/nx/search/jobs/?q=metatrader&sort=recency",
    "https://www.upwork.com/nx/search/jobs/?q=forex+bot&sort=recency"
]

if ff_path:
    for url in urls:
        subprocess.Popen([ff_path, url])
    print("[+] Toate cele 4 taburi au fost trimise catre Firefox!")
else:
    print("[-] Nu am gasit firefox.exe la caile standard. Deschidem browser-ul implicit cu start...")
    for url in urls:
        os.system(f'start "" "{url}"')
