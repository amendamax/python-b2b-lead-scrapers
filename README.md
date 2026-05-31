# 👑 Python B2B Lead Scrapers & Data Automation Suite

Welcome to the ultimate production-grade Python web scraping, WAF bypass, and data engineering automation suite. This repository houses modular, scalable, and resilient data extraction engines designed to bypass enterprise-level firewalls and format raw data into executive-ready, highly visual business intelligence dashboards.

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

## 🛡️ Need a Production-Grade Data Pipeline for Your Business?

If your company is spending valuable manual hours collecting competitor prices, directory listings, or B2B lead databases, or if your current web scrapers are constantly crashing or getting blocked by Cloudflare/Akamai, I can build a fully automated, cloud-deployed, maintenance-free data engine for you.

*   📥 **Direct Integration:** Automated syncing into Google Sheets, Airtable, or CRMs (HubSpot, Salesforce).
*   🔒 **Enterprise Security:** Resilient IP rotation, CAPTCHA auto-solving, and cryptographic bypass.
*   📊 **Executive Reporting:** Stunning, print-ready custom dashboards designed for stakeholders.

📨 **Contact me today to discuss your automation needs:**
*   **Email:** vasile79bratu@gmail.com
*   **Upwork Profile:** [Vasile Bratu on Upwork](https://www.upwork.com/freelancers/amendamax)
*   **Fiverr Profile:** [amendamax on Fiverr](https://www.fiverr.com/amendamax)

---
*Developed by Vasile Bratu © 2026. High-Performance Software Engineering.*
