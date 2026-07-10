# ============================================================
# Live Scores Telegram Bot - Configuration
# ============================================================

# Mapping of user-friendly league names to ESPN competition codes
LEAGUES = {
    "worldcup": {"code": "fifa.world", "name": "FIFA World Cup"},
    "pl":      {"code": "eng.1", "name": "English Premier League"},
    "seriea":  {"code": "ita.1", "name": "Italian Serie A"},
    "laliga":  {"code": "esp.1", "name": "Spanish La Liga"},
    "bundes":  {"code": "ger.1", "name": "German Bundesliga"},
    "ligue1":  {"code": "fra.1", "name": "French Ligue 1"},
    "ucl":     {"code": "uefa.champions", "name": "UEFA Champions League"},
    "mls":     {"code": "usa.1", "name": "Major League Soccer (MLS)"},
}

# Telegram Bot settings
# If the user does not set an environment variable, they can paste their token here
TELEGRAM_BOT_TOKEN = "8798726145:AAHj6U0raPtC9u1gpyF5a01nE98wTDjKxoE"

# Refresh rate for live polling (seconds)
LIVE_REFRESH_RATE = 60
