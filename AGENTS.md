# ETALON DE AUR (MASTER MEMORY & REGULI PERMANENTE — VASILE BRATU)

Acest fișier reprezintă **memoria centrală și etalonul obligatoriu** pentru orice conversație nouă în Antigravity. Este încărcat automat la pornirea fiecărui chat și actualizat automat în fiecare seară la comanda **`nb`** (sau la deschiderea unei sesiuni noi).

---

## 1. REGULI CRITICE DE COMUNICARE ȘI EXECUȚIE (FĂRĂ EXCEPȚIE)

1. **Limba exclusivă:** Comunică **100% EXCLUSIV în limba română** în toate răspunsurile, explicațiile și rapoartele către Vasile.
2. **Ordonare strict alfabetică (A → Z):** Orice listă sau tabel de domenii/proprietăți (în special pentru Google Search Console sau Cloudflare) **TREBUIE sortată strict alfabetic de la A la Z**, exact cum le afișează Google Search Console.
3. **Aprobare prealabilă:** Nu executa modificări arhitecturale majore, ștergeri sau proiecte noi fără să explici pe scurt planul și să primești aprobarea lui Vasile (*„da”*).
4. **Fără domenii sau date fictive:** Folosește exclusiv domeniile reale, bazele de date reale și ID-urile de afiliere reale din acest etalon.
5. **Anticipare proactivă SEO/GSC:** Orice modificare de arhitectură a rutelor sau a sitemap-urilor (ex. trecerea unor sub-sitemap-uri pe `404`) trebuie însoțită **imediat și automat** de curățarea lor în Google Search Console prin API (`robot-seo@solar-indexer.iam.gserviceaccount.com`), fără să aștepți ca Vasile să observe erorile în GSC.
6. **Particularități Windows / PowerShell:**
   - Folosește întotdeauna `npx.cmd` (ex. `npx.cmd wrangler deploy`) în loc de `npx` pentru a evita eroarea de politică PowerShell.
   - Evită `python -c` cu ghilimele imbricate în PowerShell; scrie scripturile ajutătoare în directorul `scratch/` al conversației și rulează `python "cale\catre\script.py"`.
7. **INTERDICȚIE ABSOLUTĂ DE CONFIDENȚIALITATE:**
   - **NICIODATĂ** să nu citești, listezi, deschizi sau atingi directorul privat `C:\Users\bratu\Desktop\02_DOSAR_AVOCAT_LAURA_CANAVESE_SEPARARE`.

---

## 2. PROFILUL TITULARULUI & CADRUL FISCAL

- **Titular:** Vasile Bratu (`amendamax@gmail.com`)
- **Entitate juridică:** Ditta Individuale — **P.IVA `IT04226190041`** (*Regime Forfettario*, Italia)
- **Sediu:** `Via Valcasotto 14, 12075 Garessio (CN), Italia`
- **Cloudflare Account ID:** `f1a640aa4374c2fa099363de273add49`
- **Principiu de monetizare fiscală:** Preferință strictă pentru încasări **B2B curate** (afiliere Amazon Associates, CJ Affiliate, rețele CPA/CPL, AdSense, sau procesatori *Merchant of Record* precum Lemon Squeezy / Paddle care gestionează ei TVA-ul B2C global și plătesc B2B către P.IVA).

---

## 3. FLOTA COMPLETĂ DE 36 DOMENII (ORDONATĂ ALFABETIC A → Z)

Toate cele **35 de domenii din Cloudflare** au înregistrarea `TXT` `google-site-verification` activă pentru `robot-seo@solar-indexer.iam.gserviceaccount.com` (proprietar DNS verificat pe `sc-domain:` și `https://`) și au în Google Search Console **exclusiv sitemap-urile canonice valide (`200 OK`)**:

| # | Domeniu | Motor / Worker Cloudflare | Sitemap-uri Canonice Active în GSC |
| :---: | :--- | :--- | :--- |
| 1 | `afstrinity.net` | Wiki Network | `sitemap.xml` |
| 2 | `airparkrefund.com` | AirParkRefund | `sitemap-index.xml` (`en`, `it`, `ro`) |
| 3 | `appscamradar.com` | `scam-radars-edge` | `sitemap.xml` |
| 4 | `australiasolarrebate.com` | `eu-subsidies-gateway` (`AU`) | `sitemap.xml`, `news-sitemap.xml` |
| 5 | `beregnstotte.dk` | `eu-subsidies-gateway` (`DK`) | `sitemap.xml`, `news-sitemap.xml` |
| 6 | `berekensubsidie.nl` | `eu-subsidies-gateway` (`NL`) | `sitemap.xml`, `news-sitemap.xml` |
| 7 | `bidragskalkylator.se` | `eu-subsidies-gateway` (`SE`) | `sitemap.xml`, `news-sitemap.xml` |
| 8 | `bonusbinaryoptions.net` | Wiki Network | `sitemap.xml` |
| 9 | `calcolaincentivi.it` | CF Pages `calcolaincentivi` (`IT`) | `sitemap.xml`, `sitemap-news.xml` |
| 10 | `calculaincentivos.pt` | `eu-subsidies-gateway` (`PT`) | `sitemap.xml`, `news-sitemap.xml` |
| 11 | `calculasubvenciones.es` | `eu-subsidies-gateway` (`ES`) | `sitemap.xml`, `news-sitemap.xml` |
| 12 | `calculeazasubventii.ro` | CF Pages `calculeazasubventii` (`RO`) | `sitemap.xml`, `sitemap-news.xml` |
| 13 | `calculesubventions.fr` | `eu-subsidies-gateway` (`FR` + `/lu`) | `sitemap.xml`, `news-sitemap.xml`, `sitemap-lu.xml` |
| 14 | `chikudenchi-hojyo.com` | `eu-subsidies-gateway` (`JP`) | `sitemap.xml`, `news-sitemap.xml` |
| 15 | `christianspeeddate.com` | Wiki Network | `sitemap.xml` |
| 16 | `dreamcarhunt.com` | DreamCarHunt | `sitemap.xml` |
| 17 | `evplugalliance.org` | Wiki Network | `sitemap.xml` |
| 18 | `foerderungberechnen.at` | `eu-subsidies-gateway` (`AT`) | `sitemap.xml`, `news-sitemap.xml` |
| 19 | `foerderungberechnen.de` | `eu-subsidies-gateway` (`DE`) | `sitemap.xml`, `news-sitemap.xml` |
| 20 | `indianacleanpower.org` | Wiki Network | `sitemap.xml` |
| 21 | `isbrokersafe.com` | `scam-radars-edge` (Native D1+Assets) | `sitemap.xml` |
| 22 | `jobscamradar.com` | `scam-radars-edge` | `sitemap.xml` |
| 23 | `novatec-biosol.com` | Wiki Network | `sitemap.xml` |
| 24 | `obliczdotacje.pl` | `eu-subsidies-gateway` (`PL`) | `sitemap.xml`, `news-sitemap.xml` |
| 25 | `palyazatkalkulator.hu` | `eu-subsidies-gateway` (`HU`) | `sitemap.xml`, `news-sitemap.xml` |
| 26 | `panouri-solare.org` | Wiki Network | `sitemap.xml` |
| 27 | `pillscamradar.com` | `scam-radars-edge` | `sitemap.xml` |
| 28 | `premieberekenen.be` | `eu-subsidies-gateway` (`BE`) | `sitemap.xml`, `news-sitemap.xml` |
| 29 | `pv-nms.net` | Wiki Network | `sitemap.xml` |
| 30 | `sonoraenergygroup.com` | Wiki Network | `sitemap.xml` |
| 31 | `spocitejdotaci.cz` | `eu-subsidies-gateway` (`CZ`) | `sitemap.xml`, `news-sitemap.xml` |
| 32 | `sunfeed.net` | Wiki Network | `sitemap.xml` |
| 33 | `ukgrantcalculator.co.uk` | `eu-subsidies-gateway` (`UK`) | `sitemap.xml`, `news-sitemap.xml` |
| 34 | `ussolarrebates.com` | `eu-subsidies-gateway` (`US`) | `sitemap.xml`, `news-sitemap.xml` |
| 35 | `vasiledev.com` | GitHub Pages (Corporativ) | `sitemap.xml` *(DNS extern Cloudflare)* |
| 36 | `verifydating.net` | `scam-radars-edge` (Native D1+Assets) | `sitemap.xml` |

---

## 4. BAZE DE DATE D1, INFRASTRUCTURĂ & TAG-URI DE AFILIERE

### A. Baze de date Cloudflare D1
1. **`radar-network-db`** (`fb926a0f-f76c-4a9c-addf-abaf17f3fd2a`) — folosită de `eu-subsidies-gateway` (`C:\Users\bratu\Documents\antigravity\eu-subsidies-network`) și `scam-radars-edge` (`C:\Users\bratu\Documents\antigravity\amazing-borg\scam-radars-edge`).
2. **`master_italy`** (`08eee5f4-d966-41f9-8981-7da60a395807`) — folosită de `calcolaincentivi.it` (`C:\Users\bratu\Documents\antigravity\italy-lead-engine`).
3. **`master_romania`** (`59928b3b-b4b7-45e2-8c79-7a2a6f0fa83a`) — folosită de `calculeazasubventii.ro` (`C:\Users\bratu\Documents\antigravity\romania-lead-engine`).
- Tabelul central de conversii în toate cele 3 baze D1: **`affiliate_clicks`** (`id, created_at, country, city_slug, sku, network, target_url, user_ip_hash, user_agent, vpp_prechecked`).
- Cele 5 categorii principale de produse pe subvenții/energie: **`baterie-20kwh`**, **`solar-kit`**, **`wallbox-11kw`**, **`heatpump-r290`**, **`invertor-deye-10kw`**.

### B. Tag-uri Oficiale Amazon Associates (VasileDev)
- **Italia (`amazon.it`):** `vasiledev-21`
- **Germania / Europa Centrală & Est (`amazon.de` — DE, AT, CH, RO, DK, CZ, HU etc.):** `vasiledev0c-21`
- **Franța (`amazon.fr`):** `vasiledev0a-21`
- **Spania & Portugalia (`amazon.es`):** `vasiledev09-21`
- **Marea Britanie (`amazon.co.uk`):** `vasiledev0b-21`
- **Olanda (`amazon.nl`):** `vasiledev03-21`
- **Belgia (`amazon.com.be`):** `vasiledev0a9-21`
- **Polonia (`amazon.pl`):** `vasiledev02-21`
- **Suedia (`amazon.se`):** `vasiledev09c-21`
- **SUA / Global (`amazon.com`):** `vasiledev-20`
- **Australia (`amazon.com.au`):** `vasiledev-22`
- **Japonia (`amazon.co.jp`):** `vasiledev08-22`

### C. Afiliere Financiară / Securitate / Dating (`scam-radars-edge`)
- **Brokeri (`isbrokersafe.com`):** IBKR (`vasile651`), Exness (`hb0ywi6abh`), eToro (`B21647_A131664` EU / `B21933_A131664` US), BlackBull (`43450`), AvaTrade (`222287`), Plus500 (`139742`), XM (`E17wj`), FTMO (`kclcyQANbTsQxpzBCCEQ`), SabioTrade (`838346`), FundedNext (`BROKERSAFE`), TradingView (`amendamax`).
- **CJ Affiliate (`101863908`) & Privacy (`verifydating.net` + Radars):** Spokeo (`17066431` / `17040818` / `17040894` / `12673645`), NordVPN (`16968809`), Surfshark (`15438547`), Intego (`15733644`), Identity Monitoring (`15740542`), Incogni (`aff_id=1505`).

### D. Scutul Anti-Bot & Anti-Proxy Rezidențial (Activ pe `/api/v1/go-offer`, `/go/*`, `/out/*`)
- Blochează cu `403 Forbidden`: rețeaua Tor (`T1`), cererile fără `Sec-Fetch-Mode: navigate`, cererile directe de tip scraper (`Sec-Fetch-Site: none`), ASN-urile de datacenter (OVH, Alibaba, Hetzner, Tencent etc.), versiunile vechi/falsificate de browser (`Chrome < 122`, `Firefox < 115`, `iOS <= 14`, `Windows 7`, `Safari Version/25+`), parametrii SQLi invalizi și proxy-urile rezidențiale din America de Sud / Asia / Africa pe portalurile de subvenții.

---

## 5. PROTOCOLUL AUTOMAT DE SEARĂ (`nb`) & ARHIVA DE CONVERSAȚII

- Toate conversațiile din `C:\Users\bratu\.gemini\antigravity\brain\` sunt arhivate automat în **`C:\Users\bratu\Documents\antigravity\conversations_backup\`**, iar indexul lor complet se află în **[`INDEX_CONVERSATII.md`](file:///C:/Users/bratu/Documents/antigravity/conversations_backup/INDEX_CONVERSATII.md)**.
- **Când Vasile scrie `nb` (sau `noapte buna` / `noapte bună`):**
  1. Hook-ul `PreInvocation` rulează automat `C:\Users\bratu\.gemini\config\sync_memory_etalon.py` și salvează toate conversațiile la zi.
  2. Agentul **TREBUIE** să actualizeze secțiunea **„6. STAREA LA ZI & JURNALUL ULTIMELOR SESIUNI”** de mai jos (în ambele fișiere `C:\Users\bratu\Documents\antigravity\amazing-borg\AGENTS.md` și `C:\Users\bratu\Documents\antigravity\AGENTS.md`) cu tot ce s-a lucrat în ziua respectivă, apoi să-i confirme lui Vasile salvarea și să-i ureze noapte bună.

---

<!-- DYNAMIC_STATUS_START -->
## 6. STAREA LA ZI & JURNALUL ULTIMELOR SESIUNI

- **Ultima sincronizare automată a arhivei:** `2026-11-10 16:05:44`
- **Ultimele lucrări finalizate și verificate în producție (09–10 Noiembrie 2026):**
  1. **`scam-radars-edge` (`isbrokersafe.com`, `verifydating.net`, `jobscamradar.com`, `pillscamradar.com`, `appscamradar.com` — Versiunea `62d28d0e-c03a-4edd-92f0-30b14e320763`):**
     - Restaurat 100% linkurile reale de afiliere VasileDev + Global Amazon Guard (`US/CA/MX/BR`, `AU/NZ`, `JP` + toate țările UE) + `/llms.txt` și IndexNow.
     - Activat scutul complet anti-bot / anti-Tor / anti-SQLi pe `/go/*` și `/out/*`.
  2. **Curățare generală automată Google Search Console + DNS TXT pe toate cele 35 de domenii Cloudflare (`eu-subsidies-gateway` Versiunea `a5deabce-f787-4450-8562-856be3917243`):**
     - Adăugat `TXT` `google-site-verification` pentru `robot-seo@solar-indexer.iam.gserviceaccount.com` pe toate cele 35 de zone Cloudflare.
     - Șters definitiv **64 de sub-sitemap-uri vechi (`404`) sau duplicate `www.`** din Google Search Console; au rămas active exclusiv sitemap-urile canonice `200 OK` (inclusiv `sitemap-lu.xml` pe `calculesubventions.fr`).
  3. **Scut Anti-Proxy Rezidențial pe Afiliere (`eu-subsidies-gateway`, `calcolaincentivi.it`, `calculeazasubventii.ro`, `scam-radars-edge`):**
     - Auditul D1 a arătat **3.042 click-uri umane** (**2.427** în ultimele 7 zile), dar a depistat crawlere cu proxy-uri rezidențiale din Brazilia/Vietnam/Asia și Tor (`T1`) care accesau `/api/v1/go-offer`.
     - S-a implementat și publicat live blocarea `403` pentru proxy-uri non-target, `Sec-Fetch-Site: none`, `Tor (T1)` și browsere vechi falsificate (`Chrome < 122`), oprind instantaneu traficul fals în D1 și Amazon Associates.
<!-- DYNAMIC_STATUS_END -->
