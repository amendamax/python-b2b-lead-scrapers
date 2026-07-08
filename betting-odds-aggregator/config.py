# ============================================================
# Betting Odds Aggregator - Configuration
# ============================================================

# Sports URLs on BetExplorer
SPORTS_URLS = {
    "soccer": "https://www.betexplorer.com/next/soccer/",
    "tennis": "https://www.betexplorer.com/next/tennis/",
    "basketball": "https://www.betexplorer.com/next/basketball/",
    "hockey": "https://www.betexplorer.com/next/hockey/",
}

# Default settings
DEFAULT_SPORT = "soccer"
DEFAULT_VALUE_THRESHOLD = 8.0  # Alert if Max Odd is 8%+ higher than Average Odd

# Chrome WebDriver Settings
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
PAGE_LOAD_WAIT = 6  # Seconds to wait for dynamic JavaScript content to load

# Output directory
OUTPUT_DIR = "output"
