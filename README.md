# 👑 Python B2B Lead Scrapers & Data Automation Suite

Welcome to the ultimate production-grade Python web scraping, WAF bypass, and data engineering automation suite. This repository houses modular, scalable, and resilient data extraction engines designed to bypass enterprise-level firewalls and format raw data into executive-ready, highly visual business intelligence dashboards.

🌐 **Live Portfolio & Active Demos:** [vasiledev.com](https://vasiledev.com) | 💼 **Upwork Profile:** [Vasile Bratu on Upwork](https://www.upwork.com/freelancers/amendamax)

---

## 🚀 Key Technical Architectures

This suite is built to showcase senior-level software engineering paradigms in data acquisition and automation:

### 1. Cryptographic WAF & Bot Bypass (TLS Fingerprinting)
Standard Python `requests` or `urllib` libraries fail instantly against modern Web Application Firewalls (WAFs) like **Cloudflare, Akamai, Datadome, or Imperva** due to SSL/TLS JA3 fingerprint mismatch.
* This suite implements **`curl_cffi`** to mimic Chrome's exact JA3 cryptographic handshakes at the socket level, bypassing high-end firewalls without expensive API wrappers.
* Incorporates advanced stealth browser contexts via **Playwright Stealth** to run headless automation completely undetected by behavioral analysis.

### 2. High-Performance Asynchronous Crawlers
* Utilizes **`asyncio`** and concurrent worker architectures (including Scrapy and async Playwright) to scrape, clean, and pipe thousands of pages concurrently with strict rate-limiting safeguards to prevent server overload.

### 3. Executive-Ready Reporting Systems (The HSL Design System)
Instead of basic, unstyled CSV text dumps that wrap awkwardly in Excel, this suite implements a **custom HSL-based styling engine** using **`openpyxl`**:
* **Airy Padding ("Spatios & Aerat"):** Header row heights are set to 35pt, and data rows to 32pt, creating clean breathing room.
* **Typographical Hierarchy:** Styled entirely in **Segoe UI** with distinct weights, border grids, and alternating light mint/gold zebra rows to enhance horizontal tracking.
* **Interactive Hyperlinks:** Implements Excel's native `=HYPERLINK(url, "Visit Site ↗")` formulas, keeping columns compact and prevents raw URLs from cluttering the grid.

### 4. Headless PDF Vector Rendering
* Integrates Windows **`pywin32` COM Automation** to spin up a headless Excel instance, auto-fit column margins, scale all grid cells to fit perfectly on exactly one landscape page, and export print-ready vector PDFs on demand.

---

## 📂 Project Structure & Directories

*   **`amazon_scraper/`**: Stealth e-commerce scraper using `curl_cffi` and `openpyxl`. Generates the **"Midnight Gold"** HSL styled dashboard. Includes automated Win32 COM PDF printer.
*   **`bookstore_scraper/`**: Generalist paginated scraper generating the **"Steel Blue"** corporate styled spreadsheet with embedded price charting.
*   **`lead_generator/`**: Yellowpages lead generation scraper featuring direct **Google Sheets API Sync** via `gspread` and a local **"Forest Emerald Green"** CRM-ready pipeline output.
*   **`utah_scraper/`**: Stateful Playwright B2B scraper built specifically to crawl the Utah DOPL database, resolve corporate registrations on the Utah BES registry, and bypass Recaptcha challenges.

---

## ⚙️ How It Works (Visual Showcase)

### 📊 Forest Emerald Lead Pipeline:
Raw addresses and telephone numbers are programmatically cleaned using regex delimiters and formatted into beautiful accounting-compliant tables:

```python
# HSL Palette Definition inside our Exporter
header_fill = PatternFill(start_color="1B4D3E", end_color="1B4D3E", fill_type="solid") # Deep Emerald
zebra_fill = PatternFill(start_color="F2F7F5", end_color="F2F7F5", fill_type="solid")  # Mint Zebra
link_font = Font(name="Segoe UI", size=10, underline="single", color="1B4D3E")         # Clickable Emerald
```

---

## 📖 Case Studies & Technical Publications

For deep-dives into the inner workings of web scraping security, database automation, and quantitative systems, check out my published guides on major developer platforms:

*   **[Medium | Cloudflare WAF Bypass Guide](https://medium.com/@amendamax/bypassing-cloudflare-waf-and-akamai-in-python-using-tls-fingerprinting-the-curl-cffi-guide-2b4110127669)**: A comprehensive analysis of modern Web Application Firewalls (WAFs), SSL/TLS socket handshakes, JA3 fingerprinting, and programmatic stealth requests.
*   **[dev.to | High-Performance Scraping & Reporting with curl_cffi](https://dev.to/amendamax2025)**: An in-depth case study on using `curl_cffi` for secure connections and using `openpyxl` to build premium, executive-ready Excel reports.

### 📚 Multilingual Strategy & Authority Publications (4 Topics × 3 Languages)

I have authored a series of 12 authoritative, highly localized publications detailing the business impact and software architectures of my automation systems. Access the full-text drafts below:

#### 1. PropTech & Real Estate Data Automation
*   **[Romanian (RO) on Medium](https://medium.com/@amendamax/proptech-%C3%AEn-2026-cum-automatizarea-datelor-imobiliare-elimin%C4%83-munca-manual%C4%83-a-agen%C8%9Bilor-%C8%99i-le-e897e6c7b233)**: *PropTech în 2026: Cum automatizarea datelor imobiliare elimină munca manuală a agenților și le crește vânzările cu 40%*
*   **[Italian (IT) on Medium](https://medium.com/@amendamax/proptech-nel-2026-come-lautomazione-dei-dati-immobiliari-elimina-il-lavoro-manuale-degli-agenti-e-eb1b54d9c220)**: *PropTech nel 2026: come l'automazione dei dati immobiliari elimina il lavoro manuale degli agenti e aumenta le vendite del 40%*
*   **[English (EN)](file:///C:/Users/bratu/.gemini/antigravity/brain/9bd01f8c-3a81-42f5-99f3-c521cfe09c9c/article_proptech_en.md)**: *PropTech in 2026: How Real Estate Data Automation Eliminates Broker Grunt Work and Boosts Sales by 40%*

#### 2. E-commerce Competitor Price Intelligence
*   **[Romanian (RO) on Medium](https://medium.com/@amendamax/inteligen%C8%9Ba-pre%C8%9Burilor-%C3%AEn-e-commerce-cum-automatizarea-monitoriz%C4%83rii-competitorilor-protejeaz%C4%83-7abde4e1e508)**: *Inteligența Prețurilor în E-commerce: Cum automatizarea monitorizării competitorilor protejează marjele și crește vânzările cu 25%*
*   **[Italian (IT)](file:///C:/Users/bratu/.gemini/antigravity/brain/9bd01f8c-3a81-42f5-99f3-c521cfe09c9c/article_ecommerce_it.md)**: *E-commerce Price Intelligence: Come l'automatizzazione del monitoraggio dei prezzi protegge i margini e aumenta le vendite del 25%*
*   **[English (EN)](file:///C:/Users/bratu/.gemini/antigravity/brain/9bd01f8c-3a81-42f5-99f3-c521cfe09c9c/article_ecommerce_en.md)**: *E-commerce Price Intelligence: How Automated Competitor Monitoring Protects Margins and Boosts Sales by 25%*

#### 3. FinTech & Algorithmic Risk Control
*   **[Romanian (RO) on Medium](https://medium.com/@amendamax/fintech-%C8%99i-controlul-algoritmic-al-riscului-cum-automatizarea-vps-%C8%99i-integrarea-api-protejeaz%C4%83-11d74527edcb)**: *FinTech și Controlul Algoritmic al Riscului: Cum automatizarea VPS și integrarea API protejează capitalul și elimină erorile umane în tranzacționare*
*   **[Italian (IT)](file:///C:/Users/bratu/.gemini/antigravity/brain/9bd01f8c-3a81-42f5-99f3-c521cfe09c9c/article_fintech_it.md)**: *FinTech e Controllo Algoritmico del Rischio: Come l'automatizzazione VPS e l'integrazione API proteggono il capitale ed eliminano gli errori umani nel trading*
*   **[English (EN) on dev.to](https://dev.to/amendamax2025/fintech-algorithmic-risk-control-how-vps-automation-and-api-integration-protect-capital-and-25c8)**: *FinTech & Algorithmic Risk Control: How VPS Automation and API Integration Protect Capital and Eliminate Human Execution Errors in Trading*

#### 4. Ethical Web Scraping & GDPR Compliance
*   **[Romanian (RO) on Medium](https://medium.com/@amendamax/web-scraping-etic-%C8%99i-gdpr-cum-companiile-pot-colecta-date-publice-online-%C3%AEn-deplin%C4%83-siguran%C8%9B%C4%83-42d685139dd6)**: *Web Scraping Etic și GDPR: Cum companiile pot colecta date publice online în deplină siguranță legală și tehnică*
*   **[Italian (IT) on Medium](https://medium.com/@amendamax/web-scraping-etico-e-gdpr-come-le-aziende-possono-raccogliere-dati-pubblici-online-in-totale-24715b5c76e0)**: *Web Scraping Etico e GDPR: Come le aziende possono raccogliere dati pubblici online in totale sicurezza legale e tecnica*
*   **[English (EN) on dev.to](https://dev.to/amendamax2025/ethical-web-scraping-gdpr-how-enterprises-extract-public-web-data-with-absolute-legal--1fb9)**: *Ethical Web Scraping & GDPR: How Enterprises Extract Public Web Data with Absolute Legal & Technical Security*

---

## 🛡️ Need a Production-Grade Data Pipeline for Your Business?

If your company is spending valuable manual hours collecting competitor prices, directory listings, or B2B lead databases, or if your current web scrapers are constantly crashing or getting blocked by Cloudflare/Akamai, I can build a fully automated, cloud-deployed, maintenance-free data engine for you.

*   📥 **Direct Integration:** Automated syncing into Google Sheets, Airtable, or CRMs (HubSpot, Salesforce).
*   🔒 **Enterprise Security:** Resilient IP rotation, CAPTCHA auto-solving, and cryptographic bypass.
*   📊 **Executive Reporting:** Stunning, print-ready custom dashboards designed for stakeholders.

📨 **Contact me today to discuss your automation needs:**
*   **Email:** [amendamax@vasiledev.com](mailto:amendamax@vasiledev.com)
*   **Upwork Profile:** [Vasile Bratu on Upwork](https://www.upwork.com/freelancers/amendamax)
*   **Fiverr Profile:** [Vasile Bratu on Fiverr](https://www.fiverr.com/amendamax)

---
*Developed by Vasile Bratu © 2026. High-Performance Software Engineering.*

