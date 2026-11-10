# bf-price-radar-ro — Motor B2B de Competitor Price & Stock Intelligence (Fotovoltaice România)

Sistem modular în Python 3.11+ pentru monitorizarea încrucișată a prețurilor, stocurilor reale și a Buy-Box-ului eMAG Marketplace pe nișa de echipamente fotovoltaice (**invertoare hibride/on-grid** și **baterii LiFePO4**) pentru campania de Black Friday din România.

## Structura Arhitecturală

- `.env.example` / `.env` — Configurare proxy (`PROXY_URL`, `USE_PROXY_FOR_EMAG=true`, `USE_PROXY_FOR_STORES=false` cu fallback automat pe proxy la HTTP 403/429).
- `niche_config.json` — Configurarea celor 10 magazine țintă din România (`e-acumulatori.ro`, `esolar.ro`, `solargreen.ro`, `sumin.ro`, `genway.ro`, `darcomenergy.ro`, `arenainstalatiilor.ro`, `volta-x.ro`, `panourisolare24.ro`, `blackseasolar.ro`) + modulul benchmark `emag.ro`.
- `clients_config.json` — Configurarea celor maximum 3 clienți VIP (Pachetul de 450 € / 30 zile, 3 rulări/zi, câte 2 branduri blocate exclusiv per client).
- `sku_matcher.py` — Motor determinist Regex care normalizează și extrage **Codul Oficial de Model (Part Number / SKU Producător)** pentru **Deye, Huawei, Pylontech, Victron Energy, V-Tac, Fronius, Growatt** + filtru anti-accesorii (cabluri/suporturi) + parser strict de stoc (`În stoc` vs. `Stoc Epuizat / La comandă`).
- `platform_detector.py` — Detector automat de platformă tehnică (**Gomag, MerchantPro, WooCommerce, PrestaShop, OpenCart, Magento, Custom**) și extractor de date publice B2B (`stores_contacts.json`).
- `scraper_engine.py` — Motor asincron `Playwright` + `httpx` + `selectolax` cu interceptor de rută (`page.route("**/*", ...)`) care blochează `image`, `media`, `font`, `stylesheet` și scripturile de tracking (Google Analytics, Facebook Pixel, Hotjar, TikTok) pentru un consum sub 50–80 KB/pagină.
- `db.py` — Manager SQLite (`radar_history.db` -> tabelele `runs`, `price_history`, `emag_benchmarks`, `store_profiles`).
- `generate_mirrors.py` — Generator `Polars` + `xlsxwriter` care produce cele 10 sub-dosare `/output/{store_domain}/` cu:
  1. `Teaser_BlackFriday_{store_domain}.xlsx` (Mostra Gratuită de Atac - 8 produse, primele 4 cu numele concurentului vizibil, următoarele 4 cu `[Ascuns în versiunea Demo]`).
  2. `Full_Audit_BlackFriday_{store_domain}.xlsx` (Matricea completă de 150 € cu toate cele 10 magazine + tab-ul `Export_Price_Match_{platforma}` pe codurile interne ale magazinului).
- `generate_outreach.py` — Generatorul de mesaje umane B2B (`mesaj_contact.txt` + `mesaj_whatsapp.txt`) personalizate dinamic pe cifrele fiecărui magazin.
- `live_monitor.py` — Motorul de Diff & Alerte Live (3x/zi) pentru clienții de 450 € (`/output/live_alerts_450eur/`).
- `test_smoke.py` — Scriptul complet de verificare conectivitate live și generare a tuturor livrabilelor în `/output/`.

## Rulare Rapidă

```powershell
.\venv\Scripts\python.exe test_smoke.py
```
