# 📈 Yellowpages B2B Lead Generator & Google Sheets Sync Pipeline

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![gspread](https://img.shields.io/badge/Cloud_Sync-Google_Sheets_API-green?logo=google-sheets)
![Excel](https://img.shields.io/badge/Export-Excel_Emerald_Green-emerald?logo=microsoft-excel)
![PDF](https://img.shields.io/badge/Format-Landscape_Vector_PDF-red?logo=adobe-acrobat-reader)
![License](https://img.shields.io/badge/License-MIT-green)

> A high-performance B2B Lead Scraper targeting Yellowpages to extract local business leads (phones, websites, emails, addresses). Syncs leads to the cloud in real-time via the Google Sheets API, or exports a styled **"Emerald Green"** Excel CRM pipeline and landscape PDF.

---

## 💎 Design System & Presentation ("Emerald Green")

Designed for direct sales and cold outreach campaigns, the generated leads spreadsheet features:
1. **Interactive Hyperlinks (`=HYPERLINK`):** Website links are compressed to `Visit Site ↗` and Yellowpages links to `Profile ↗` in a clean Emerald Green theme (`#059669`).
2. **Emerald Green HSL Color Scheme:** Custom theme inspired by sales CRM systems, utilizing Dark Forest-Green headers (`#064E3B`) and warm borders.
3. **Data Spacing:** Rows are set to **32pt** height with custom indentations, keeping the spreadsheet spacious ("aerat") and preventing text wrapping from stretching columns.
4. **CRM-Ready Structure:** Fully normalized data fields matching column requirements for major CRMs like Salesforce, HubSpot, and Zoho.

---

## ⚙️ Core Technical Features

* **Yellowpages Scraper:** Crawls directory pages, parses business titles, phone numbers, complete street addresses, verified websites, review counts, and average star ratings.
* **Google Sheets Cloud Sync:** Integrates with `gspread` and Google OAuth2 credentials to push scraped leads directly to a shared Google Sheet in real-time.
* **Smart Offline Fallback:** If cloud credentials are not provided, the pipeline automatically writes to a formatted local Excel workbook and prints to a PDF via Win32 COM printing.

---

## 📂 Project Structure

* **[lead_scraper.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/lead_generator/lead_scraper.py):** Extraction parser collecting local business listings.
* **[google_sheets_sync.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/lead_generator/google_sheets_sync.py):** Cloud synchronization pipeline utilizing the Google Sheets API and local Excel layout designer.
* **[convert_pdf.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/lead_generator/convert_pdf.py):** Conversion print script rendering `.xlsx` data into vector `.pdf`.
* **[lead_main.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/lead_generator/lead_main.py):** Interactive CLI orchestrating the lead generation pipeline.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies: `requests`, `beautifulsoup4`, `openpyxl`, `gspread`, `oauth2client`, `pywin32`)*

### 2. Configure Google Sheets API (Optional)
To sync directly to Google Sheets, place your Service Account JSON credentials as `credentials.json` in the project folder.

### 3. Run the pipeline
```bash
python lead_main.py
```

### 4. Check the outputs
* **Local CRM Pipeline:** `scraped_leads_pipeline.xlsx`
* **Print-Ready PDF:** `scraped_leads_pipeline.pdf`

---

## ⚠️ Disclaimer

This tool is for **educational and portfolio demonstration use only**. Please respect directory terms of service and crawl rates.

---

## 👨‍💻 Developer & Author

Built with passion by **VasileDev** — Web Scraping & Data Engineering Specialist.  
📧 amendamax@vasiledev.com | 🌐 [vasiledev.com](https://vasiledev.com)
