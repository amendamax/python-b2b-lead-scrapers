# 📊 Betting Odds Aggregator & Arbitrage Alerter

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Selenium](https://img.shields.io/badge/Selenium-Headless-green)
![Surebets](https://img.shields.io/badge/Surebets-Arbitrage%20Finder-red)
![License](https://img.shields.io/badge/License-MIT-green)

> A real-time, dynamic **Betting Odds Aggregator** that scrapes upcoming matches and 1X2 / 12 odds across multiple bookmakers. Includes automatic **Value Bet Detection** and **Surebet (Arbitrage) Alerts** for risk-free profit calculations.

---

## 📦 Features

| Feature | Description |
|---------|-------------|
| 🌐 Dynamic Scraping | Uses headless Selenium to render complex JavaScript tables from BetExplorer |
| 🔥 Value Bet Finder | Identifies outcomes where a bookmaker's maximum odd is significantly higher than the market average |
| 🚨 Surebet (Arbitrage) Alerter | Detects risk-free betting opportunities using the sum of reciprocals formula |
| 🎛️ Sports Support | Supports Soccer, Tennis, Basketball, and Hockey |
| 💾 Multi-format Export | Saves aggregated odds, value bets, and surebets into CSV, Excel, or JSON |

---

## 🧮 How It Works

### 1. Value Bet Detection
The tool calculates the percentage difference between the **Maximum available odd** ($O_{max}$) and the **Average market odd** ($O_{avg}$):

$$\text{Profit Increase \%} = \frac{O_{max} - O_{avg}}{O_{avg}} \times 100$$

If this increase meets or exceeds your specified threshold (e.g. 8%), it is flagged as a high-value opportunity.

### 2. Surebet (Arbitrage) Detection
Arbitrage occurs when the sum of the reciprocals of the best odds for all outcomes is less than 1.0:

$$\text{Arbitrage Margin} = \sum_{i=1}^{N} \frac{1}{O_{max, i}} < 1.0$$

*   For Soccer/Hockey ($N=3$): $\frac{1}{\text{Max}_1} + \frac{1}{\text{Max}_X} + \frac{1}{\text{Max}_2} < 1.0$
*   For Tennis/Basketball ($N=2$): $\frac{1}{\text{Max}_1} + \frac{1}{\text{Max}_2} < 1.0$

When a surebet is found, the guaranteed risk-free profit percentage is calculated as:

$$\text{Guaranteed Profit \%} = \left( \frac{1}{\text{Arbitrage Margin}} - 1.0 \right) \times 100$$

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/betting-odds-aggregator.git
cd betting-odds-aggregator
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the tool
```bash
# Scrape upcoming soccer matches and look for value bets above 8% (default)
python scraper.py

# Scrape tennis matches with a stricter value threshold of 5%
python scraper.py --sport tennis --threshold 5.0 --format excel

# Scrape basketball matches and export results as JSON
python scraper.py --sport basketball --format json
```

---

## 🎛️ CLI Options

| Flag | Options | Default | Description |
|------|---------|---------|-------------|
| `--sport` / `-s` | `soccer`, `tennis`, `basketball`, `hockey` | `soccer` | Sport to scrape |
| `--threshold` / `-t` | Any float number (e.g. `5.0`, `10.0`) | `8.0` | Value bet alert threshold (%) |
| `--format` / `-f` | `csv`, `excel`, `json` | `csv` | Export file format |

---

## 📂 Output Structure

All files are exported into the `output/` directory with a timestamp suffix:

```
output/
├── soccer_all_odds_20260708.csv
├── soccer_value_bets_20260708.csv
└── soccer_sure_bets_20260708.csv
```

---

## ⚠️ Disclaimer

This tool is for **educational and personal research use only**. Dynamic scraping can put load on remote servers; please scrape responsibly and respect the website's request guidelines. We do not promote or encourage gambling.

---

## 📄 License

MIT License — free to use and adapt.

---

## 👨‍💻 Author

Built by **VasileDev** — Web Scraping & Data Engineering Specialist.  
📧 amendamax@gmail.com | 🌐 [isbrokersafe.com](https://isbrokersafe.com)
