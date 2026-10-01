# 🏎️ DREAMCARHUNTER by VasileDev
## Master Blueprint & Specificații Tehnice de Arhitectură
**Versiune:** 1.0 (Enterprise Specification)  
**Autor & Arhitect:** Vasile Bratu (`VasileDev Group` | `https://vasiledev.com`)  
**Data Documentării:** 9 Septembrie 2026  
**Status:** Arhitectură gata de implementare (The "Must GO" Project)

---

## 📌 1. Viziunea Executivă & Poziționarea pe Piață

**`DreamCarHunter by VasileDev`** este o platformă pan-europeană de căutare chirurgicală, arbitraj de date și alertare la nivel de secundă pentru automobile de elită și vehicule de mare volum.

### Punctul de Ruptură cu Piața Clasică (The Moat):
Spre deosebire de portalurile publice tradiționale (Mobile.de, AutoScout24) unde alertele au întârzieri de 1–3 ore și filtrele se bazează pe declarații eronate ale vânzătorilor:
* **DreamCarHunter** operează la **nivel de cod de fabrică (PR-Codes)** și **inspecție optică automată cu AI Multimodal (Gemini Flash)**.
* Identifică exemplare rare („Inorogi”) în **primele 30 de secunde de la listare**, înainte de indexarea publică lentă.
* Integrează un motor de **arbitraj matematic de marjă** pentru dealerii și parcurile auto revânzătoare.

---

## 👥 2. Cele 3 Segmente de Business & Modele de Monetizare

Platforma este structurată pentru a genera două tipuri de fluxuri financiare: **Cashflow de impact mare (B2C VIP)** și **Venit Recurent Lunar stabil / MRR (B2B SaaS)**.

```
                             DREAMCARHUNTER ECOSYSTEM
                                        │
        ┌───────────────────────────────┼───────────────────────────────┐
        ▼                               ▼                               ▼
1. VIP CONCIERGE (B2C)        2. B2B ARBITRAGE RADAR          3. SAAS SUBSCRIPTIONS
• Clienți privați cu bani     • Dealeri & Parcuri Auto       • Starter, Pro & Enterprise
• Caută mașina unică           • Vânează marjă de profit      • 99 € – 499 € / lună (MRR)
• Success Fee: 1.000€ - 3.000€ • Cumpără în primele minute    • Alerte Telegram automate
```

### Segmentul 1: VIP Private Concierge (B2C)
* **Clientul:** Persoane fizice cu bugete de 45.000 € – 150.000 € (Porsche, BMW M, Mercedes-AMG, Audi RS, Range Rover).
* **Problema rezolvată:** Timp zero, frustrarea de a găsi mașini cu opțiuni false, frica de vicii ascunse.
* **Livrabil:** Identificarea Inorogului, decodare fișă oficială de fabrică din serverele producătorului, apel și negociere directă în germană/franceză, securizare contract.
* **Tarife:**
  * **Retainer inițial de căutare (nerambursabil):** `250 € – 500 €`
  * **Success Fee la achiziție:** `1.500 € – 3.000 €` sau `2.5% – 3%` din prețul mașinii.

### Segmentul 2: B2B Arbitrage Engine (Dealeri & Parcuri Auto)
* **Clientul:** Importatori auto independenți și parcuri de revânzare (România, Polonia, Cehia, Bulgaria).
* **Problema rezolvată:** Găsirea rapidă a mașinilor de volum lichide (VW Tiguan, Golf 8, Skoda Octavia, Dacia Duster) listate subevaluat în Europa.
* **Algoritmul de Arbitraj:**
  $$\text{Marjă Netă} = \text{Preț Mediu Piață Locală} - (\text{Preț Listat} + \text{Cost Transport} + \text{RAR / Înmatriculare})$$
  * Dacă $\text{Marjă Netă} \ge 2.000\ \text{€}$, botul declanșează o alertă prioritară pe canalul privat de Telegram al dealerului cu buton direct de apelare.

### Segmentul 3: Arhitectura de Abonamente SaaS (MRR)
* **Tier 1: Starter Trader (`99 € / lună`):**
  * Până la 3 radare de căutare active simultan.
  * Alerte Telegram în < 60 secunde. Filtrare pe parametri clasici.
* **Tier 2: Pro Dealer (`249 € / lună`) — Best Value:**
  * Până la 10 radare de căutare active simultan.
  * Calculator automat de marjă de profit inclus în alertă.
  * Filtru Vision AI integrat (elimină mașini lovite sau cu pachete optice false).
  * 3 conturi de Telegram conectate pentru agenții parcului.
* **Tier 3: Enterprise Fleet Sniper (`499 € – 799 € / lună`):**
  * Căutări nelimitate pe toate cele 18 țări europene.
  * Latență garantată sub 5 secunde prin proxy-uri dedicate Super-Premium.
  * Webhook & API JSON direct în CRM-ul / ERP-ul dealerului.
  * 50 de decodări oficiale VIN de fabrică incluse lunar.

---

## 🌐 3. UX Landing Page: Comutatorul Dinamic (B2C vs. B2B)

Landing page-ul este conceput pe o arhitectură **Dark Mode Minimalist**, integrând un comutator vizual (*pill switch*) care schimbă instant conținutul și oferta fără a fi nevoie de două domenii separate:

```
       ┌─────────────────────────────────────────────────────────┐
       │   [ 👤 Cumpărător Individual ]  |  [ 🏢 Dealeri Auto ]  │
       └─────────────────────────────────────────────────────────┘
```

* **În modul Individual (B2C):**
  * *Hero:* „Mașina ta de vis, cu specificația exactă de fabrică. Fără compromisuri.”
  * *Componentă cheie:* **Mini-Configuratorul de Inorog** (bifează opțiunile rare).
  * *Prețuri:* Pachete de căutare și Concierge privat.
* **În modul Dealeri (B2B):**
  * *Hero:* „Cumpără înaintea concurenței. Sistemul de alerte în timp real pentru dealeri auto.”
  * *Componentă cheie:* **Panou de Watchlist Multiplu** & Selector de praguri de marjă.
  * *Prețuri:* Abonamente lunare recurente (99 € / 249 € / 499 €).

---

## 📋 4. Specificația Oficială a „Inorogului” (The Holy Grail Benchmark)

Exemplul de referință implementat pentru clasa **Porsche Panamera 4S Diesel (2017–2018, 4.0 V8 Bi-Turbo, 422 CP, 850 Nm)**.

Sistemul caută și validează obligatoriu cele **6 Dotări Majore de Inginerie**:

| Cod PR | Denumire Oficială Porsche | Rol Tehnic & Importanță Critică |
| :--- | :--- | :--- |
| **`GZ2`** | **Soft-Close Doors** | Închidere pneumatică amortizată a portierelor. Elimină complet trântitul ușilor și rezolvă problema contrapresiunii de aer a habitaclului etanș. |
| **`VW5` / `VW6`** | **Thermally & Noise-Insulating Glass** | Geamuri duble laminate sandwich cu folie PVB. Liniște acustică la 180 km/h, barieră termică UV/infraroșu, reținere căldură iarna, barieră anti-efracție. |
| **`9M9`** | **Auxiliary Heating (Webasto)** | Încălzire auxiliară din fabrică cu telecomandă. Motorul și habitaclul ajung la 22°C înainte de pornire iarna. |
| **`0N5`** | **Rear-Axle Steering (Roți Viratoare)** | Punte spate viratoare activă conectată la computerul de șasiu pe 48V. Agilitate de hatchback la parcări, stabilitate de avion la viteze mari. |
| **`8A4`** | **Surround View 360°** | 4 camere video reale (grilă, oglinzi laterale, hayon) pentru parcare milimetrică. |
| **`7Y1`** | **Lane Change Assist (Unghi Mort)** | 4 LED-uri integrate în piciorul oglinzii exterioare + radare spate la 70m pentru schimbarea benzii în siguranță pe autostradă. |

*Dotări asociate verificate:* Faruri Matrix LED (`8IU`), Trapă panoramică (`3FU`), Scaune confort ventilate (`4D3`/`4A4`).

---

## 🔍 5. Trinitatea Detecției Tehnice (Pipeline-ul de Scanare)

Nicio mașină nu poate scăpa neidentificată datorită arhitecturii de detecție pe **3 niveluri suprapuse**:

```
                       ┌────────────────────────────────────────┐
                       │          LISTARE NOUĂ IDENTIFICATĂ     │
                       └───────────────────┬────────────────────┘
                                           │
          ┌────────────────────────────────┼────────────────────────────────┐
          ▼                                ▼                                ▼
  1. METODA VIN (PR-Codes)        2. METODA TEXT GERMAN          3. METODA VISION AI (Gemini)
  • Regex WP0ZZZ...               • Căutare termeni oficiali:    • Inspecție poze (sub 2 sec):
  • Interogare baze de date        „Standheizung”, „Dämmglas”,    - Lentilă cameră 360° grilă
  • Certitudine 100%               „Hinterachslenkung”,           - Modul 4 LED-uri oglindă
  • Cost: 0 €                      „Servoschließung”              - Telecomandă Webasto pe scaun
                                   • Cost: 0 €                    • Cost: 0 € (Free Tier API)
```

1. **Nivelul 1 (Extragere directă VIN / Bază de date):**
   * Extrage prin expresii regulate seria de șasiu (`WP0ZZZ...`, `WBA...`, `WDC...`).
   * Verifică codurile de echipare de fabrică.
2. **Nivelul 2 (Parser Semantic pe Textele Oficiale în Germană/Engleză/Franceză/Italiană):**
   * Caută terminologia oficială din cataloagele mărcilor:
     * Webasto: `Standheizung mit Fernbedienung`, `Zusatzheizung`
     * Geamuri duble: `Geräusch- und Wärmeschutzverglasung`, `Dämmglas`, `Doppelverglasung`
     * Soft-Close: `Servoschließung der Türen`, `Soft-Close Türen`
     * Roți viratoare: `Hinterachslenkung`, `Allradlenkung`
     * 360°: `Surround View`, `Top View`, `360 Grad Kamera`
     * Unghi mort: `Spurwechselassistent`, `Lane Change Assist`
3. **Nivelul 3 (Computer Vision cu Gemini Flash):**
   * Trimite cele 4–6 fotografii cheie (grilă, oglindă, consolă, ecran navigație) către API-ul multimodal.
   * Modelul returnează în format JSON prezența componentelor fizice cu scor de încredere (confidence score > 90%).

---

## 🛡️ 6. Infrastructura de Proxy pe 2 Niveluri (Tier 1 vs. Tier 2 Super-Premium)

Pentru a garanta funcționarea 24/7 fără blocaje din partea sistemelor anti-bot (DataDome, Cloudflare Enterprise, Akamai Bot Manager):

```
                  ┌────────────────────────────────────────┐
                  │          PORTALURILE AUTO ȚINTĂ        │
                  │ (Mobile.de, AutoScout Pan-EU, Subito)  │
                  └───────────────────┬────────────────────┘
                                      │
          ┌───────────────────────────┴───────────────────────────┐
          ▼                                                       ▼
  NIVELUL 1: RADARUL RAPID                                NIVELUL 2: SUPER-PREMIUM
  (Proxy ISP / Datacenter Rotativ)                        (Proxy Rezidențial & Mobile 4G/5G)
  • Scanează continuu la 10–15 secunde                    • Rulaj exclusiv la găsire țintă/VIP
  • Descarcă doar delta (ID-uri noi)                      • IP-uri reale Telekom / Vodafone / Orange
  • Consum de bandă minim, cost infim                     • Imposibil de blocat de DataDome/Akamai
  • Zero descărcare de media grea                         • Extrage JSON-ul intern & pozele HD
```

* **Nivelul 1 (Radar Polling):** Menține frecvența ridicată de scanare cu costuri apropiate de zero (proxy-uri rapide de tip ISP / datacenter rotativ).
* **Nivelul 2 (Super-Premium Extraction — Provider Oficial: `anyIP.io`):**
  * **anyIP.io** este selectat ca furnizor principal (pachet flexibil 30 GB fără expirare).
  * **Geo-Targeting pe Țară:** Rutare directă pe IP-uri native rezidențiale/mobile (`country-de` pentru Mobile.de, `country-ch` pentru Elveția, `country-se` pentru Suedia, `country-it` pentru Italia).
  * **Sticky Sessions (5–10 min):** Păstrează aceeași sesiune IP rezidențială pentru descărcarea completă a datelor și a fotografiilor HD, simulând comportament uman 100%.
  * **Fallback secundar:** Nodul rezidențial Geonode (`proxy.geonode.io:9000`).

---

## 🗺️ 7. Acoperirea Geografică Pan-Europeană

Platforma nu se limitează la Germania, ci exploatează anomaliile specifice fiecărei piețe din Europa:
1. **Germania & Austria (Mobile.de, AutoScout24.de/at, Willhaben):** Cel mai mare volum de tranzacționare din lume.
2. **Țările Nordice (Suedia - Blocket.se, Norvegia - Finn.no):** „Raiul” mașinilor cu Webasto din fabrică (`9M9`) și geamuri duble (`VW5`) din cauza climei arctice.
3. **Elveția (AutoScout24.ch, Tutti.ch):** Cel mai înalt standard de întreținere din lume (inspecții MFK severe) și echipări de vârf plătite integral.
4. **Italia (AutoScout24.it, Subito.it):** **Arbitrajul Superbollo** — proprietarii italieni vând mașinile de peste 185 kW la export cu 10%–15% sub piața germană pentru a scăpa de taxele anuale enorme.
5. **Franța & Benelux (Leboncoin.fr, Marktplaats.nl, 2dehands.be):** Oportunități excelente pe flote corporate și vehicule rulate certificate.

---

## 💻 8. Stack Tehnic de Implementare

* **Scraper Engine:** Python 3.12+ asincron (`aiohttp`, `curl_cffi` cu TLS Fingerprinting Chrome, `Playwright` headless unde este necesar bypass avansat).
* **Pipeline de Date & Deduplicare:** `Redis` (pentru stocarea hash-urilor de ID și imagini — zero alerte duplicate).
* **AI Vision Layer:** Google AI Studio SDK (`google-genai` / `gemini-1.5-flash` pe cota gratuită de 1.500 cereri/zi).
* **Dispatch & Notificări:** `aiogram` (Telegram Bot API asincron, latență < 1 secundă).
* **Bază de Date:** `PostgreSQL` / `Supabase` (pentru stocarea utilizatorilor, alertelor configurate și log-urilor de audit).
* **Web Frontend:** `FastAPI` (backend) + HTML5/Tailwind CSS cu toggle dinamic B2C/B2B.
* **Găzduire & Rețea:** VPS privat (Hetzner / DigitalOcean) integrat cu **anyIP.io** (30 GB pool rezidențial/mobil) și Geonode (fallback).

---

## 🏁 9. Foaia de Lansare & Execuție

1. **Faza 1 (Ianuarie 2027) — Prototipul Personal & Testul de Foc:**  
   Implementarea motorului pentru achiziția personală a Porsche Panamera 4S Diesel / Macan S Diesel conform specificației complete a Inorogului. Această achiziție devine studiul de caz demonstrativ al platformei.
2. **Faza 2 (Primăvara 2027) — B2B Terminal MVP:**  
   Lansarea botului de alerte pentru 5–10 dealeri auto independenți din România (rețea privată pe bază de invitație la 99 € – 199 €/lună).
3. **Faza 3 (H2 2027) — Lansarea Oficială Publică:**  
   Deschiderea platformei web sub egida noului SRL din România, cu campanii targetate de marketing și scalarea celor două fluxuri: **VIP Concierge** și **Abonamente SaaS**.

---
*Document salvat și certificat în depozitul proiectului VasileDev Group.*  
*Drepturi rezervate © 2026 VasileDev.*
