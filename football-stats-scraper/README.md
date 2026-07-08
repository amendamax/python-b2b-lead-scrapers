# ⚽ Football Stats Scraper

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Sources](https://img.shields.io/badge/Sources-FBref%20%7C%20Transfermarkt-orange)

> Scrape **player statistics**, **league standings**, and **market values** for any major football league — exported to **CSV**, **Excel**, or **JSON** with a single command.

---

## 📦 Features

| Feature | Description |
|---------|-------------|
| 🧑‍💼 Player Stats | Goals, Assists, xG, xAG, Minutes, Cards — from FBref |
| 🏆 League Standings | Full table: W/D/L, GF, GA, GD, Points — from FBref |
| 💶 Market Values | Transfer values per player and club — from Transfermarkt |
| 📁 Multi-format Export | CSV, Excel (.xlsx), or JSON |
| 🌍 5 Major Leagues | Premier League, Serie A, La Liga, Bundesliga, Ligue 1 + UCL |

---

## 🚀 Quick Start

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/football-stats-scraper.git
cd football-stats-scraper
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the scraper
```bash
# Scrape everything for Serie A (default) → CSV output
python scraper.py

# Scrape Premier League player stats → Excel
python scraper.py --league "Premier League" --mode stats --format excel

# Scrape La Liga standings → JSON
python scraper.py --league "La Liga" --mode standings --format json

# Scrape Bundesliga market values → CSV
python scraper.py --league "Bundesliga" --mode values
```

---

## 🎛️ CLI Options

| Flag | Options | Default | Description |
|------|---------|---------|-------------|
| `--league` / `-l` | See below | `Serie A` | League to scrape |
| `--mode` / `-m` | `stats`, `standings`, `values`, `all` | `all` | What to scrape |
| `--format` / `-f` | `csv`, `excel`, `json` | `csv` | Output file format |

### Supported Leagues
- `Premier League`
- `Serie A`
- `La Liga`
- `Bundesliga`
- `Ligue 1`
- `Champions League`

---

## 📂 Output Structure

```
output/
├── serie_a_player_stats_20250708.csv
├── serie_a_standings_20250708.csv
└── serie_a_market_values_20250708.csv
```

### Sample Player Stats Output

| Player | Nation | Team | Age | Pos | MP | Goals | Assists | xG | Yellow | Red |
|--------|--------|------|-----|-----|----|----|------|----|--------|-----|
| Kylian Mbappé | FRA | Real Madrid | 26 | FW | 34 | 27 | 10 | 24.3 | 4 | 0 |
| Erling Haaland | NOR | Man City | 24 | FW | 33 | 24 | 5 | 22.1 | 2 | 0 |

---

## ⚠️ Disclaimer

This tool is for **educational and personal use only**. Please respect each website's `robots.txt` and Terms of Service. A delay of 3 seconds between requests is built in by default to avoid server overload.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

## 👨‍💻 Author

Built by **VasileDev** — Python scraping specialist.  
📧 amendamax@gmail.com | 🌐 [isbrokersafe.com](https://isbrokersafe.com)
