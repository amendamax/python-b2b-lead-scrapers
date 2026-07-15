# 🚀 VerifyDating — Deployment Guide (Windows Server VPS)

> **Recomandat**: Rulează Antigravity direct pe VPS și spune-i "deploy dating-photo-checker" pentru setup automat.

---

## 📋 Cerințe minime VPS

| Componentă | Minim | Recomandat |
|---|---|---|
| RAM | 1 GB | 2 GB |
| CPU | 1 vCPU | 2 vCPU |
| Disk | 10 GB | 20 GB |
| OS | Windows Server 2019 | Windows Server 2022 |
| Python | 3.9+ | 3.11+ |

---

## 🔑 Chei importante (PĂSTREAZĂ SECRET!)

Cheile Stripe live sunt în `config.json`:
- **Publishable key**: `pk_live_51TqAOL4Be...` (frontend)
- **Secret key**: `sk_live_51TqAOL4Be...` (backend — nu expune niciodată!)

---

## 📦 PASUL 1 — Copiază proiectul pe VPS

### Opțiunea A: Prin RDP (drag & drop)
1. Conectează-te la VPS prin RDP
2. Copiază folderul `dating-photo-checker` pe VPS (ex: `C:\apps\dating-photo-checker\`)

### Opțiunea B: Prin Git (recomandat)
```powershell
git clone https://github.com/USER/REPO.git C:\apps\dating-photo-checker
```

### Opțiunea C: Prin WinSCP / FileZilla
- Conectează-te la VPS prin SFTP/FTP și uploadează folderul

---

## 🐍 PASUL 2 — Instalează Python și dependențele

```powershell
# Verifică dacă Python e instalat
python --version

# Instalează dependențele
cd C:\apps\dating-photo-checker
pip install -r requirements.txt
```

**Dacă `requirements.txt` nu există**, rulează:
```powershell
pip install fastapi uvicorn stripe pillow requests aiofiles python-multipart
```

---

## ⚙️ PASUL 3 — Verifică config.json

Asigură-te că `config.json` conține cheile live corecte:
```json
{
    "stripe_publishable_key": "pk_live_51TqAOL4Be...",
    "stripe_secret_key": "sk_live_51TqAOL4Be...",
    "google_api_key": "...",
    "google_cse_id": "..."
}
```

---

## 🧪 PASUL 4 — Test rapid (fără service)

```powershell
cd C:\apps\dating-photo-checker
python server.py
```

Deschide browser: `http://localhost:8000` — dacă merge, treci la pasul următor.

Testează și din exterior: `http://IP-VPS:8000`

> ⚠️ Dacă nu e accesibil din exterior, deschide portul în Windows Firewall (Pasul 5).

---

## 🔥 PASUL 5 — Deschide portul în Windows Firewall

```powershell
# Rulează ca Administrator
New-NetFirewallRule -DisplayName "VerifyDating App" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

Sau prin interfața grafică:
`Windows Defender Firewall → Advanced Settings → Inbound Rules → New Rule → Port 8000`

---

## 🛡️ PASUL 6 — Rulează ca Windows Service (permanent)

### Instalează NSSM (Non-Sucking Service Manager)
```powershell
# Descarcă NSSM
Invoke-WebRequest -Uri "https://nssm.cc/release/nssm-2.24.zip" -OutFile "C:\nssm.zip"
Expand-Archive -Path "C:\nssm.zip" -DestinationPath "C:\nssm"
```

### Creează serviciul
```powershell
# Rulează ca Administrator
C:\nssm\nssm-2.24\win64\nssm.exe install VerifyDating

# În interfața NSSM care apare:
# Path:        C:\Python311\python.exe   (sau unde e python la tine)
# Startup dir: C:\apps\dating-photo-checker
# Arguments:   server.py
```

### Sau direct din linia de comandă:
```powershell
$python = (Get-Command python).Source
C:\nssm\nssm-2.24\win64\nssm.exe install VerifyDating $python server.py
nssm set VerifyDating AppDirectory C:\apps\dating-photo-checker
nssm set VerifyDating DisplayName "VerifyDating App"
nssm set VerifyDating Description "Dating Photo Checker - FastAPI Backend"
nssm set VerifyDating Start SERVICE_AUTO_START

# Pornește serviciul
nssm start VerifyDating
```

### Verifică statusul:
```powershell
nssm status VerifyDating
# sau
Get-Service -Name VerifyDating
```

---

## 🌐 PASUL 7 (Opțional) — Reverse Proxy cu Caddy (Port 80)

Dacă vrei să accesezi pe portul 80 (http://IP direct fără :8000):

### Instalează Caddy
```powershell
winget install Caddy.Caddy
```

### Creează `Caddyfile` în `C:\caddy\Caddyfile`:
```
:80 {
    reverse_proxy localhost:8000
}
```

### Pornește Caddy:
```powershell
cd C:\caddy
caddy run
```

---

## 🔒 PASUL 8 (Opțional) — HTTPS cu domeniu propriu

Când adaugi un domeniu (ex: `verifydating.net`):

1. Îndreaptă DNS-ul domeniului spre IP-ul VPS
2. Modifică `Caddyfile`:
```
verifydating.net {
    reverse_proxy localhost:8000
}
```
Caddy obține certificat SSL gratuit automat prin Let's Encrypt! ✅

---

## 📊 Comenzi utile după deployment

```powershell
# Status serviciu
Get-Service -Name VerifyDating

# Restart serviciu (după update)
Restart-Service -Name VerifyDating

# Stop serviciu
Stop-Service -Name VerifyDating

# Vizualizează logs NSSM
Get-Content "C:\apps\dating-photo-checker\nssm-output.log" -Tail 50

# Verifică dacă portul e în ascultare
netstat -ano | findstr :8000
```

---

## 🔄 Update-uri viitoare

Când modifici codul:
```powershell
# 1. Copiază fișierele noi
# 2. Restart serviciu
Restart-Service -Name VerifyDating
```

---

## ✅ Checklist final

- [ ] Python instalat pe VPS
- [ ] Dependențe instalate (`pip install -r requirements.txt`)
- [ ] `config.json` cu cheile live Stripe
- [ ] Port 8000 deschis în Firewall
- [ ] Serviciu Windows creat cu NSSM
- [ ] Serviciu pornit și setat pe AUTO_START
- [ ] Testat din browser extern: `http://IP-VPS:8000`
- [ ] (Opțional) Caddy configurat pentru port 80
- [ ] (Opțional) Domeniu + HTTPS configurat

---

## 🆘 Probleme frecvente

| Problemă | Soluție |
|---|---|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Port 8000 inaccesibil | Verifică Windows Firewall + firewall VPS provider |
| Serviciul se oprește | Verifică logs NSSM, probabil eroare în `server.py` |
| Stripe nu funcționează | Verifică că `config.json` are cheile `sk_live_` corecte |
| `Address already in use` | `netstat -ano | findstr :8000` + `taskkill /PID <id> /F` |

---

> 💡 **Sfat**: Dacă folosești Antigravity pe VPS, poți spune direct "deploy-ează aplicația" și va face toți pașii automat!
