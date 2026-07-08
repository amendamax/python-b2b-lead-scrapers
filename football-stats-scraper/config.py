# ============================================================
# Football Stats Scraper - Configuration
# ============================================================

LEAGUES = {
    "Premier League": {"code": "GB1", "slug": "premier-league"},
    "Serie A":        {"code": "IT1", "slug": "serie-a"},
    "La Liga":        {"code": "ES1", "slug": "laliga"},
    "Bundesliga":     {"code": "L1", "slug": "bundesliga"},
    "Ligue 1":        {"code": "FR1", "slug": "ligue-1"},
}

DEFAULT_SEASON = "2025"  # Season 2025/2026 is fully completed

# Output directory
OUTPUT_DIR = "output"

# Request headers (polite scraping)
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

# Delay between requests (seconds) - be polite!
REQUEST_DELAY = 2
