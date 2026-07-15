# 👑 Amazon Stealth Scraper & Midnight Gold Executive Dashboard

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![curl_cffi](https://img.shields.io/badge/WAF_Bypass-curl__cffi-orange)
![Excel](https://img.shields.io/badge/Export-Excel_Midnight_Gold-gold?logo=microsoft-excel)
![PDF](https://img.shields.io/badge/Format-Landscape_Vector_PDF-red?logo=adobe-acrobat-reader)
![License](https://img.shields.io/badge/License-MIT-green)

> An enterprise-grade, anti-bot bypassing Amazon Web Scraper that extracts product specifications, pricing, ratings, and image previews. Delivers data in a luxury **"Midnight Gold"** themed Excel dashboard and prints to a pixel-perfect, single-page vector PDF via headless COM automation.

---

## 💎 Design System & Presentation ("Midnight Gold")

This project is engineered to solve the cluttered, wrap-text "dump of data" issue of standard scrapers. It delivers **executive-ready visual spreadsheets** featuring:
1. **Interactive Hyperlinks (`=HYPERLINK`):** Long, ugly Amazon URLs are compressed into elegant clickable links (`View Product ↗` and `View Image 📷`) preventing row stretching.
2. **Midnight Gold Color Scheme:** Curated HSL palette using Slate-Midnight headers (`#0F172A`) and warm Gold accents (`#D97706`).
3. **Airy Symmetrical Padding:** Data row height set to **35pt** (deep breathing room) with aligned cell indentations, ensuring text never touches cell borders.
4. **Clean Name Engineering:** Strict regex filters clean keyword-stuffed Amazon titles (e.g. stripping colons, commas, marketing fluff like *"Gaming Laptop"*, *"Renewed"*), shortening titles to maximum 40 characters.

---

## ⚙️ Core Technical Features

* **Akamai & Cloudflare WAF Bypass:** Utilizing `curl_cffi` to replicate the cryptographic TLS client handshakes of modern web browsers, bypassing advanced anti-bot firewalls without proxy costs.
* **Semantic Filter Engine:** Automatically discards accessories, cables, bags, and phone cases, ensuring the dataset only contains real, matching laptops/devices.
* **Win32 COM PDF Auto-Print:** Headless Win32 COM integration to scale columns to fit on exactly one page width, converting the styled workbook into a landscape PDF.

---

## 📂 Project Structure

* **[amazon_scraper.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/amazon_scraper/amazon_scraper.py):** Crawling and extraction engine powered by HTTP TLS fingerprinting.
* **[amazon_excel_exporter.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/amazon_scraper/amazon_excel_exporter.py):** Layout designer applying the custom styling rules and formulas.
* **[convert_pdf.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/amazon_scraper/convert_pdf.py):** Headless print engine converting `.xlsx` sheets to vector `.pdf`.
* **[amazon_main.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/amazon_scraper/amazon_main.py):** Command Line Interface to run the scraping pipeline with interactive queries.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies: `curl_cffi`, `openpyxl`, `pywin32`)*

### 2. Run the scraping pipeline
```bash
python amazon_main.py
```

### 3. Check the outputs
* **Pristine Spreadsheet:** `amazon_laptops_report.xlsx`
* **Executive PDF:** `amazon_laptops_report.pdf`

---

## ⚠️ Disclaimer

This tool is for **educational and portfolio demonstration use only**. Scrape responsibly and respect server bandwidth rules.

---

## 👨‍💻 Developer & Author

Built with passion by **VasileDev** — Web Scraping & Data Engineering Specialist.  
📧 amendamax@gmail.com | 🌐 [isbrokersafe.com](https://isbrokersafe.com)
