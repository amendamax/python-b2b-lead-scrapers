# 🚀 VasileDev Group — Master Project Handoff & Context State
**Last Updated:** 2026-10-19

> **Instrucțiune pentru Agent (New Chat):** Citește acest fișier imediat la începutul sesiunii. Conține tot istoricul tehnic, arhitectura, cheile configurate și pașii următori, astfel încât utilizatorul să nu fie nevoit să re-explice nimic.

---

## 1. Arhitectura Ecosistemului (20 Portaluri & Servicii)

### A. Rețeaua Europeană de Subvenții — 15 Țări (`eu-subsidies-gateway`)
- **Director proiect:** `C:\Users\bratu\Documents\antigravity\eu-subsidies-network`
- **Cloudflare Worker:** `eu-subsidies-gateway` (`src/index.js`, configurat în `wrangler.jsonc`)
- **Funcționalități active pe toate cele 15 țări:**
  - Design glassmorphism + imagini arhitecturale 16:9 specifice fiecărei țări (`/assets/bg-{cc}.jpg`).
  - Optimizare 100% Mobile-Responsive (media queries `@media (max-width: 768px)` și `@media (max-width: 480px)`).
  - Sitemaps XML ierarhice: `sitemap.xml` (index cu 10 sub-sitemap-uri `sitemap-1.xml` ... `sitemap-10.xml`, însumând **50.000 URL-uri pSEO per țară**).
  - `robots.txt` și `llms.txt` active pe fiecare domeniu.
  - **Auto-Indexing Cron (`scheduled`):** Rulează zilnic la `08:00 UTC` și trimite câte 200 URL-uri/zi pentru fiecare țară către Google Indexing API, salvând progresul în Cloudflare KV (`INDEXER_KV`, chei `offset_{cc}` și `stats_{cc}`).

#### Statusul celor 15 Țări din `eu-subsidies-gateway`:
| # | Țară | Domeniu | Status DNS / Cloudflare | Google Indexing API Bot (în Cloudflare Secrets) | Status GSC & Indexare |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 🇮🇹 Italia | `calcolaincentivi.it` | ✅ LIVE | `GCP_CLIENT_EMAIL` (`bratu79@...`) | ✅ Activ (200/zi) |
| 2 | 🇷🇴 România | `calculeazasubventii.ro` | ✅ LIVE | `GCP_CLIENT_EMAIL` (`bratu79@...`) | ✅ Activ (200/zi) |
| 3 | 🇩🇪 Germania | `foerderungsrechner.de` | ✅ LIVE | `GCP_EMAIL_DE` (`bot-de@eu-indexer-de...`) | ✅ Activ (200/zi) |
| 4 | 🇫🇷 Franța | `calculateur-aides.fr` | ✅ LIVE | `GCP_EMAIL_FR` (`bot-fr@eu-indexer-fr...`) | ✅ Activ (200/zi) |
| 5 | 🇪🇸 Spania | `calculadorasubvenciones.es` | ✅ LIVE | `GCP_EMAIL_ES` (`bot-es@eu-indexer-es...`) | ✅ Activ (200/zi) |
| 6 | 🇵🇱 Polonia | `kalkulatordotacji.pl` | ✅ LIVE | `GCP_EMAIL_PL` (`bot-pl@eu-indexer-pl...`) | ✅ Activ (200/zi) |
| 7 | 🇳🇱 Olanda | `subsidieberekenen.nl` | ✅ LIVE | `GCP_EMAIL_NL` (`bot-nl@eu-indexer-nl...`) | ✅ Activ (200/zi) |
| 8 | 🇦🇹 Austria | `foerderungsrechner.at` | ✅ LIVE | `GCP_EMAIL_AT` (`bot-at@eu-indexer-at...`) | ✅ Activ (200/zi) |
| 9 | 🇬🇧 UK | `ukgrantcalculator.co.uk` | ✅ LIVE | `GCP_EMAIL_UK` (`bot-uk@eu-indexer-uk-13301.iam.gserviceaccount.com`) | ✅ Activ (Sitemaps + 200/zi) |
| 10 | 🇵🇹 Portugalia | `calculaincentivos.pt` | ✅ LIVE | `GCP_EMAIL_PT` (`bot-pt@eu-indexer-pt-26542.iam.gserviceaccount.com`) | ✅ Activ (Sitemaps + 200/zi) |
| 11 | 🇧🇪 Belgia | `premieberekenen.be` | ✅ LIVE | `GCP_EMAIL_BE` (`bot-be@eu-indexer-be-20932.iam.gserviceaccount.com`) | ✅ Activ (Sitemaps + 200/zi) |
| 12 | 🇨🇿 Cehia | `kalkulackadotaci.cz` | ✅ LIVE | `GCP_EMAIL_CZ` (`bot-cz@eu-indexer-cz-37898.iam.gserviceaccount.com`) | ✅ Activ (Sitemaps + 200/zi) |
| 13 | 🇩🇰 Danemarca | `beregnstotte.dk` | ⏳ Cod & Imagini Gata (Domeniu de înregistrat) | `GCP_EMAIL_DK` (`bot-dk@eu-indexer-dk-30483.iam.gserviceaccount.com` — deja încărcat în CF!) | ⏳ Așteaptă activarea domeniului |
| 14 | 🇸🇪 Suedia | `bidragskalkylator.se` | ⏳ Cod & Imagini Gata (Domeniu de înregistrat) | `GCP_EMAIL_SE` (`bot-se@eu-indexer-se-17337.iam.gserviceaccount.com` — deja încărcat în CF!) | ⏳ Așteaptă activarea domeniului |
| 15 | 🇭🇺 Ungaria | `palyazatkalkulator.hu` | ⏳ Cod & Imagini Gata (Domeniu de înregistrat) | `GCP_EMAIL_HU` (`bot-hu@eu-indexer-hu-19356.iam.gserviceaccount.com` — deja încărcat în CF!) | ⏳ Așteaptă activarea domeniului |

---

### B. Panoul Central de Control & Indexare (`radar-indexer`)
- **URL Live:** `https://radar-indexer.amendamax.workers.dev`
- **Director proiect:** `C:\Users\bratu\Documents\antigravity\amazing-borg\radar-indexer` (`src/index.ts`)
- **Funcționalități:**
  - Monitorizează toate cele **20 de portaluri** în timp real (8 portaluri principale + 12/15 portaluri EU Subsidies).
  - Fiecare card afișează emailul exact al robotului Google Indexing API (cu buton `📋 Copiază`), cota zilnică `200/200`, ultimul URL indexat și butonul albastru `⚡ Indexează 35 URLs Acum`.
  - Are secțiune colapsabilă în partea de jos cu cele 3 domenii în așteptare (`DK`, `SE`, `HU`) și adresele lor de Service Account pregătite pentru Google Search Console.

---

### C. Celelalte 8 Portaluri Live din Rețeaua VasileDev Group
1. **`vasiledev.com`** — Hub corporativ (`VasileDev Group`, VAT `IT04226190041`)
2. **`isbrokersafe.com`** — Verificare brokeri & alerte reglementare (`dating-photo-checker/broker-verifier`)
3. **`verifydating.net`** — Verificare profiluri dating & anti-scam (`dating-photo-checker`)
4. **`dreamcarhunt.com`** — Inspector auto AI & TCO
5. **`airparkrefund.com`** — Despăgubiri zboruri EU261 (`airpark-worker`)
6. **`jobscamradar.com`** — Radar fraude joburi (`radar-network`)
7. **`pillscamradar.com`** — Radar suplimente & farmacii (`radar-network`)
8. **`appscamradar.com`** — Radar aplicații & APK-uri (`radar-network`)

---

## 2. Ce a rămas de făcut când utilizatorul dorește să continue:
1. **Activarea ultimelor 3 domenii EU (`beregnstotte.dk`, `bidragskalkylator.se`, `palyazatkalkulator.hu`):**
   - După înregistrarea domeniilor și adăugarea lor în Cloudflare:
   - Decomentarea rutelor `beregnstotte.dk/*`, `bidragskalkylator.se/*`, `palyazatkalkulator.hu/*` în `C:\Users\bratu\Documents\antigravity\eu-subsidies-network\wrangler.jsonc` și rularea `npx wrangler deploy`.
   - Adăugarea proprietăților în Google Search Console, trimiterea `sitemap.xml` și adăugarea celor 3 roboți (`bot-dk@...`, `bot-se@...`, `bot-hu@...`) ca **Owner (Proprietar)**.
   - Mutarea `dk`, `se`, `hu` în lista `ACTIVE_EU_COUNTRIES` din `C:\Users\bratu\Documents\antigravity\amazing-borg\radar-indexer\src\index.ts` și `npx wrangler deploy`.
