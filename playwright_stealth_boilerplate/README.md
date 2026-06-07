# 👤 Playwright Stealth Web Scraper Boilerplate

A ready-to-run, asynchronous Python boilerplate demonstrating how to set up headless **Playwright** combined with **playwright-stealth** to bypass basic automated bot detection checks (like `navigator.webdriver` and fingerprinting tests).

This boilerplate serves as a foundation for building automated web scrapers that require browser emulation.

---

## ⚙️ Features
- **Async Execution:** Built on Playwright's high-performance asynchronous API (`asyncio`).
- **Stealth Integration:** Bypasses basic browser fingerprint checks (e.g. Chrome PDF viewer, WebGL vendor, and driver flags).
- **Custom Browser Contexts:** Programmatic injection of realistic User-Agents, viewports, and custom flags.
- **Auto-Diagnostics:** Saves page screenshots automatically on connection failures or anti-bot challenge blocks.

---

## 🛠️ Quick Start

### 1. Install Dependencies
Run the following commands to install Playwright and the stealth library:
```bash
pip install -r requirements.txt
playwright install chromium
```
*(Dependencies: `playwright`, `playwright-stealth`)*

### 2. Run the Demo Scraper
```bash
python stealth_scraper.py
```
By default, the script visits [sannysoft.com](https://bot.sannysoft.com/) (a standard bot detection verification page) and prints out the results.

---

## ⚠️ Why Simple Browser Automation Fails in Production

While this boilerplate passes basic fingerprinting tests, deploying raw browser automation at scale against enterprise security layers introduces major blocks:

1. **Cryptographic Fingerprinting (TLS/JA3/JA4):** Headless Chromium triggers specific cryptographic handshake signatures. Security shields like **Cloudflare WAF, Akamai, or Imperva** inspect these JA3 signatures and block the requests before JavaScript even executes.
2. **Behavioral Analysis:** Simple linear movements, instant clicks, and rigid scroll patterns are flagged by machine learning security algorithms.
3. **CAPTCHA Challenges:** Turnstile, reCAPTCHA v3, and Arkose Labs require stateful solver integrations, proxy rotations, and human-like interaction delay systems.
4. **Server Overhead:** Spawning multiple headless browser instances consumes huge amounts of CPU and RAM, making it inefficient for millions of pages.

---

## 💎 Premium Web Scraping & Data Pipeline Solutions

If your business needs a resilient, block-resistant web scraping solution, I build custom enterprise data pipelines:

| Feature | Basic Playwright (This Boilerplate) | Premium Custom Data Engine |
| :--- | :---: | :---: |
| **Connection Protocol** | 🌐 standard HTTP/WebSocket | 🛡️ Mimics Chrome TLS & HTTP/2 (`curl_cffi` sockets) |
| **WAF Bypass** | ❌ Blocked by Turnstile/Akamai shields | ✅ Bypasses Cloudflare & Akamai at scale |
| **Proxy Rotation** | ❌ Local IP only (Fast bans) | 🔄 Residential, Mobile & Rotating Proxy integration |
| **Data Extraction** | 📄 Unstructured JSON/CSV | 📊 Styled Excel spreadsheets (Midnight Gold/Steel Blue) |
| **Cloud Sync** | ❌ Local files | ☁️ Automated sync to Google Sheets, CRM, or Databases |
| **Resource Footprint**| ❌ High CPU/RAM usage | ⚡ Lightweight socket-based async pipelines |

---

## 💼 Discuss Your Data Automation Project

Are you spending manual hours collecting competitor prices, generating sales leads, or dealing with broken web scrapers? Let's build a maintenance-free, resilient data engine tailored to your business needs:

*   **🌐 Personal Portfolio & Free Audit:** [vasiledev.com](https://vasiledev.com)
*   **📨 Contact Email:** [amendamax@vasiledev.com](mailto:amendamax@vasiledev.com)
*   **💼 Upwork Profile:** [Hire me on Upwork 💼](https://www.upwork.com/freelancers/amendamax)
*   **🚀 Fiverr Profile:** [Order Scrapy Scrapers on Fiverr 🚀](https://www.fiverr.com/amendamax/build-a-high-speed-web-scraper-using-python-and-scrapy)

*Submit up to 3 competitor URLs on my website, and I will deliver a styled, executive-ready Excel report of the data within 24 hours—completely free.*
