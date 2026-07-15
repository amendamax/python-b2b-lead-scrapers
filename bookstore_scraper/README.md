# 📚 E-Commerce Bookstore Analytics & Corporate Steel-Blue Dashboard

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![BeautifulSoup](https://img.shields.io/badge/Scraper-BeautifulSoup4-green)
![Excel](https://img.shields.io/badge/Export-Excel_Steel_Blue-blue?logo=microsoft-excel)
![PDF](https://img.shields.io/badge/Format-Landscape_Vector_PDF-red?logo=adobe-acrobat-reader)
![License](https://img.shields.io/badge/License-MIT-green)

> A paginated, asynchronous-ready BeautifulSoup4 web scraper that collects catalog books, prices, ratings, and covers. Generates a corporate **"Steel Blue"** HSL spreadsheet dashboard featuring custom price-range charts and automated PDF conversions via headless Windows COM printing.

---

## 💎 Design System & Presentation ("Steel Blue")

This catalog scraper generates investor-ready analytics and data dashboards featuring:
1. **Interactive Hyperlinks (`=HYPERLINK`):** Formats product links as `View Book ↗` and images as `View Image 📷` in custom Slate-Blue (`#1E3A8A`) to keep rows narrow and clean.
2. **Steel Blue HSL Color Scheme:** Curated theme with Dark Steel-Blue headers (`#1E3A8A`) and ice-blue borders.
3. **Data Padding & Indentation:** Set to **32pt** height with custom text indents to ensure a spacious ("aerat") layout.
4. **Embedded Charting:** Automatically adds a native line/bar chart displaying the price distribution across catalog categories directly in the Excel file.

---

## ⚙️ Core Technical Features

* **Paginated Scraping:** Automated traversal across book pages, capturing title, price, star ratings, stock status, and image URLs.
* **Semantic Rating Mapping:** Automatically translates text-based ratings (e.g. `"Three"` or `"Five"`) into integer safety ratings (`3` and `5`).
* **Headless PDF Rendering:** Direct Win32 COM interaction to print the finished Excel workbook into a vector PDF format.

---

## 📂 Project Structure

* **[scraper.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/bookstore_scraper/scraper.py):** Extraction engine utilizing `requests` and `BeautifulSoup4` with client headers.
* **[excel_exporter.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/bookstore_scraper/excel_exporter.py):** Visual layout engine setting styles, colors, and the embedded price chart.
* **[convert_pdf.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/bookstore_scraper/convert_pdf.py):** Excel COM print script converting `.xlsx` output into a landscape `.pdf`.
* **[main.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/bookstore_scraper/main.py):** Interactive command line orchestrator to run the scraper.

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```
*(Dependencies: `requests`, `beautifulsoup4`, `openpyxl`, `pywin32`)*

### 2. Run the scraping pipeline
```bash
python main.py
```

### 3. Check the outputs
* **Pristine Spreadsheet:** `scraped_books_report.xlsx`
* **Executive PDF:** `scraped_books_report.pdf`

---

## ⚠️ Disclaimer

This project is built for **educational and portfolio demonstration use only**.

---

## 👨‍💻 Developer & Author

Built with passion by **VasileDev** — Web Scraping & Data Engineering Specialist.  
📧 amendamax@vasiledev.com | 🌐 [vasiledev.com](https://vasiledev.com)
