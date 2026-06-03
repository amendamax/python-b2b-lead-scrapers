# B2B Freelance Portfolio: Premium Web Scraping & Data Automation Suite

Welcome to your ultimate B2B freelance portfolio! This project is engineered to serve as a world-class demonstration of your technical capabilities for high-value clients on Fiverr, Upwork, or direct B2B cold outreach. 

Instead of basic, unstyled CSV text dumps, this suite delivers **executive-ready data dashboards** featuring:
1. **Interactive Hyperlinks (`=HYPERLINK`)** with intuitive symbols and emojis, keeping the spreadsheets incredibly spacious ("aerat") and preventing massive raw URLs from wrapping into confusing blocks of text.
2. **Elite Custom Color Palettes** (Luxury Midnight Gold, Corporate Steel Blue, and Premium Sales Emerald Green).
3. **Advanced E-Commerce Name Engineering** using strict regex splitting (delimiters like colons, commas, dashes, parentheses) and marketing buzzword stripping to make titles clean, concise, and highly readable.
4. **Win32 COM Automation** generating pixel-perfect, landscape vector PDFs with all columns scaled to fit on exactly one page.

---

## 📂 Portfolio Folder Structure & File Locations on Disk

All projects are fully self-contained, modular, and situated inside your active workspace directory:
`C:\Users\bratu\Documents\antigravity\amazing-borg\`

### 👑 1. Stealth Amazon Scraper & Executive Dashboard (`amazon_scraper/`)
* **Project Directory:** `C:\Users\bratu\Documents\antigravity\amazing-borg\amazon_scraper\`
* **Code Files:**
  * **[amazon_scraper.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/amazon_scraper/amazon_scraper.py)**: Web crawling engine using `curl_cffi` to mimic Chrome's cryptographic TLS handshake (bypassing Akamai WAF). Features semantic tech spec rules completely filtering out cables, cases, and bags.
  * **[amazon_excel_exporter.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/amazon_scraper/amazon_excel_exporter.py)**: The visual designer. Implements the **"Midnight Gold"** HSL theme, `=HYPERLINK` formulas for clean product and image previews, 35pt high spacious data rows, and auto-fitting.
  * **[amazon_main.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/amazon_scraper/amazon_main.py)**: Interactive CLI orchestrator with safe Unicode formatting and automatic demo fallback data.
  * **[convert_pdf.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/amazon_scraper/convert_pdf.py)**: Launches a headless Excel COM engine to print the styled workbook into a landscape PDF.
* **Production Outputs:**
  * **Excel Spreadsheet:** `C:\Users\bratu\Documents\antigravity\amazing-borg\amazon_scraper\amazon_laptops_report.xlsx`
  * **Vector PDF Document:** `C:\Users\bratu\Documents\antigravity\amazing-borg\amazon_scraper\amazon_laptops_report.pdf`

### 💼 2. E-Commerce Bookstore Analytics (`bookstore_scraper/`)
* **Project Directory:** `C:\Users\bratu\Documents\antigravity\amazing-borg\bookstore_scraper\`
* **Code Files:**
  * **[scraper.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/bookstore_scraper/scraper.py)**: Scrapes paginated data and performs rating maps (e.g. `"Three"` -> `3`).
  * **[excel_exporter.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/bookstore_scraper/excel_exporter.py)**: Formats data with a corporate **"Steel Blue"** HSL theme, `=HYPERLINK` formulas (`View Book ↗` and `View Image 📷`), 32pt high row dimensions, and an embedded price chart.
  * **[main.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/bookstore_scraper/main.py)**: CLI launcher.
* **Production Outputs:**
  * **Excel Spreadsheet:** `C:\Users\bratu\Documents\antigravity\amazing-borg\bookstore_scraper\scraped_books_report.xlsx`
  * **Vector PDF Document:** `C:\Users\bratu\Documents\antigravity\amazing-borg\bookstore_scraper\scraped_books_report.pdf`

### 📈 3. Yellowpages B2B Lead Generator & Sync Pipeline (`lead_generator/`)
* **Project Directory:** `C:\Users\bratu\Documents\antigravity\amazing-borg\lead_generator\`
* **Code Files:**
  * **[lead_scraper.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/lead_generator/lead_scraper.py)**: Crawls Yellowpages, parses business name, phone, address, website, and ratings.
  * **[google_sheets_sync.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/lead_generator/google_sheets_sync.py)**: Exports leads. Connects to `gspread` for direct Google Sheets API cloud sync. If credentials are not supplied, it builds a local **"Emerald Green"** accounting pipeline Excel sheet with hyperlinked websites and Yellowpages profiles.
  * **[lead_main.py](file:///C:/Users/bratu/Documents/antigravity/amazing-borg/lead_generator/lead_main.py)**: High-speed CLI lead manager.
* **Production Outputs:**
  * **Excel Spreadsheet:** `C:\Users\bratu\Documents\antigravity\amazing-borg\lead_generator\scraped_leads_pipeline.xlsx`
  * **Vector PDF Document:** `C:\Users\bratu\Documents\antigravity\amazing-borg\lead_generator\scraped_leads_pipeline.pdf`

---

## 💎 Premium Design Systems (Why it looks so "profi" and "aerat")

To solve the cluttered "block of text" issue that typical developers output, this codebase incorporates elite design paradigms:

### 1. The Interactive Hyperlink Pattern
Long e-commerce URLs (e.g. 150+ characters long) wrap inside cells, stretching them vertically and causing text lines to overlap. 
We solved this by implementing Excel's native `=HYPERLINK(url, display_text)` formula:
- **Products:** `=HYPERLINK("https://...", "View Product ↗")` (Styled in custom Slate-Blue `#3182CE` with an elegant single underline).
- **Images:** `=HYPERLINK("https://...", "View Image 📷")` (Styled in standard blue with underline, allowing single-click image previews).
- **Websites:** `=HYPERLINK("https://...", "Visit Site ↗")`
- **Profiles:** `=HYPERLINK("https://...", "Yellowpages Profile ↗")`

### 2. Advanced E-Commerce Name Engine
Keyword-stuffed Amazon titles (e.g., `"ASUS ROG Strix G16 Gaming Laptop, 16” 165Hz FHD+, GeForce RTX 4060..."`) are completely parsed and simplified at runtime:
1. Strips all curly quotes (`”` or `’`) and replacement markers to eliminate character encoding crashes on Windows machines.
2. Splits using standard delimiters: colons (`:`), commas (`,`), vertical bars (`|`), dashes (`-`), slashes (`/`), and parentheses.
3. Automatically discards marketing fluff like *"Gaming Laptop"*, *"Unlocked"*, *"Renewed"*, or *"Black"* using strict brand-safeguards.
4. Capitalizes and shortens the output to exactly one line of text (maximum 40 characters), making it beautiful and instantly readable.

### 3. Airy Structural Padding ("Spatios & Aerat")
- **Header Row Height:** Set to **28-30pt** with center-aligned headings.
- **Data Row Height:** Expanded to **32-35pt** (instead of Excel's default 15pt), creating deep breathing room around the cell text.
- **Column Padding:** Integrated cell alignment `indent=1` so cell borders never squeeze or touch the text borders.
- **No Text Wrapping:** By shortening titles and hyperlinks, we set `wrap_text=False`. All rows remain exactly one clean line high, forming a perfectly balanced, symmetrical grid.

---

## 🏆 Freelance Upwork & Fiverr Pitch Guidelines

When showing these samples to prospective buyers, emphasize these selling points:
* **"WAF Bypass Experience"**: You build robust scrapers using cryptographic TLS fingerprinting to bypass high-end enterprise firewalls like Cloudflare and Akamai.
* **"Data Engineering & Cleaning"**: Instead of serving messy raw text, you build custom regex cleaners to format and standardize names, phones, and physical addresses.
* **"Executive Reporting"**: You provide interactive, double-underlined accounting-compliant sheets with embedded charting, service indicators (conditional color formats), and custom HSL palettes designed to impress corporate stakeholders.
* **"Multi-Language Support"**: You offer professional development and setup in English, Italian, and Romanian.

To showcase these files to a client, simply send them the clean Excel spreadsheets (`.xlsx`) or print-ready PDFs (`.pdf`) listed in the folder structure above. They will be immediately blown away by the level of visual excellence!

---

## ✉️ Professional B2B Email & Deliverability Configuration

To perform cold outreach with maximum reply rates and zero spam filtering, a custom email domain and deliverability suite have been configured:
*   **Outreach Domain:** `vasiledev.com` (Registered via Namecheap)
*   **Outreach Email:** [amendamax@vasiledev.com](mailto:amendamax@vasiledev.com) (Hosted via Zoho Mail Forever Free Plan)
*   **Deliverability Security Standards Configured in DNS:**
    *   **MX Records:** Routed to `mx.zoho.eu`, `mx2.zoho.eu`, and `mx3.zoho.eu` for receiving incoming replies.
    *   **SPF (Sender Policy Framework):** Configured TXT record `v=spf1 include:zoho.eu ~all` to authorize Zoho servers to send mail.
    *   **DKIM (DomainKeys Identified Mail):** Configured `zmail._domainkey` with a 1024-bit cryptographic key to digitally sign outgoing emails.
    *   **DMARC (Domain-based Message Authentication):** Configured `_dmarc` TXT record with `v=DMARC1; p=none;` to pass compliance checks of Google, Yahoo, and Outlook.
