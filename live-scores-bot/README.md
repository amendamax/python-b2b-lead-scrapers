# 🤖 Soccer Live Scores & Fixtures Telegram Bot

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot--API-blue?logo=telegram)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

> An automated, real-time **Telegram Bot** that delivers football live scores, daily fixtures, and yesterday's results using the completely free, public ESPN API. Includes a reply keyboard for easy mobile navigation.

---

## 📦 Features

| Feature | Description |
|---------|-------------|
| 🔴 Live Scores | Fetches matches currently in progress, displaying live time and real-time scores |
| 📅 Daily Fixtures | Lists matches scheduled for today or tomorrow, grouped by league |
| 🏆 Past Results | Displays yesterday's scores and full-time outcomes |
| 📱 Custom Keyboard | Reply buttons (Live, Today, Yesterday, Help) for easy tapping on mobile |
| 🆓 Free Sports API | Powered by ESPN's public endpoints (requires no paid api keys or signup) |

---

## 🚀 Setup & Installation

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/live-scores-bot.git
cd live-scores-bot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get your Telegram Bot Token
1. Open Telegram and search for `@BotFather`.
2. Send the command `/newbot` and follow the instructions to choose a name and username.
3. Copy the HTTP API token provided (looks like `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).
4. Paste your token in `config.py` as `TELEGRAM_BOT_TOKEN`, or set it as an environment variable:
   - **Windows:** `$env:TELEGRAM_BOT_TOKEN="your_token_here"`
   - **Linux/Mac:** `export TELEGRAM_BOT_TOKEN="your_token_here"`

### 4. Run the bot
```bash
python bot.py
```

---

## 🎛️ Bot Commands

*   `/start` or `/help` - Welcome guide and commands menu.
*   `/live` - Show all matches currently in progress.
*   `/today [league]` - Today's schedule. Example: `/today pl` for Premier League.
*   `/results [league]` - Yesterday's full-time results.
*   `/tomorrow [league]` - Tomorrow's fixtures.

### Supported League Filters:
*   `pl` - English Premier League
*   `seriea` - Italian Serie A
*   `laliga` - Spanish La Liga
*   `bundes` - German Bundesliga
*   `ligue1` - French Ligue 1
*   `ucl` - UEFA Champions League
*   `mls` - Major League Soccer

---

## 📄 License

MIT License — free to use, customize, and commercialize.

---

## 👨‍💻 Author

Built by **VasileDev** — Bot & Web Automation Engineer.  
📧 amendamax@gmail.com | 🌐 [isbrokersafe.com](https://isbrokersafe.com)
