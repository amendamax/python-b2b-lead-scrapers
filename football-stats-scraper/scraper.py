"""
╔══════════════════════════════════════════════════════════╗
║          FOOTBALL STATS SCRAPER  v1.0                    ║
║  Scrapes player stats & market values for any league     ║
║  Source: Transfermarkt.com                               ║
║  Output: CSV / Excel / JSON                              ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import time
import argparse
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from config import LEAGUES, HEADERS, REQUEST_DELAY, OUTPUT_DIR, DEFAULT_SEASON


# ─────────────────────────────────────────────
#  UTILITY
# ─────────────────────────────────────────────

def get_page(url: str) -> BeautifulSoup | None:
    """Fetch a page and return a BeautifulSoup object."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return BeautifulSoup(resp.text, "lxml")
    except requests.RequestException as e:
        print(f"  [ERROR] Failed to fetch {url}: {e}")
        return None


def ensure_output_dir():
    os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────
#  SCRAPER — PLAYER STATS (Goals & Assists)
# ─────────────────────────────────────────────

def scrape_player_stats(league_name: str, season_id: str) -> pd.DataFrame:
    """
    Scrape player statistics (Goals, Assists, Points) from Transfermarkt.
    """
    league_info = LEAGUES.get(league_name)
    if not league_info:
        print(f"  [WARN] League '{league_name}' not found in config.")
        return pd.DataFrame()

    code = league_info["code"]
    slug = league_info["slug"]
    url = f"https://www.transfermarkt.com/{slug}/scorerliste/wettbewerb/{code}/saison_id/{season_id}"

    print(f"\n⚽ Scraping player stats (Goals & Assists): {league_name} ({season_id}/{int(season_id)+1})")
    print(f"   → {url}")

    soup = get_page(url)
    if not soup:
        return pd.DataFrame()

    table = soup.find("table", {"class": "items"})
    if not table:
        print("  [WARN] Could not find statistics table.")
        return pd.DataFrame()

    rows = []
    for tr in table.find_all("tr", class_=["odd", "even"]):
        cells = tr.find_all("td")
        if len(cells) >= 12:
            try:
                player = cells[3].find("a").get_text(strip=True)
                pos = cells[4].get_text(strip=True)
                
                club_img = cells[5].find("img")
                club = club_img.get("alt") if club_img else "N/A"
                
                nat_img = cells[6].find("img")
                nationality = nat_img.get("alt") if nat_img else "N/A"
                
                age = cells[7].get_text(strip=True)
                matches = cells[8].get_text(strip=True)
                goals = cells[9].get_text(strip=True)
                assists = cells[10].get_text(strip=True)
                points = cells[11].get_text(strip=True)

                rows.append({
                    "Player": player,
                    "Position": pos,
                    "Club": club,
                    "Nationality": nationality,
                    "Age": age,
                    "Matches": matches,
                    "Goals": goals,
                    "Assists": assists,
                    "Scorer_Points": points,
                    "League": league_name,
                    "Season": f"{season_id}/{int(season_id)+1}",
                    "Scraped_At": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
            except Exception as e:
                continue

    df = pd.DataFrame(rows)
    print(f"   ✅ {len(df)} players scraped.")
    return df


# ─────────────────────────────────────────────
#  SCRAPER — LEAGUE STANDINGS
# ─────────────────────────────────────────────

def scrape_standings(league_name: str, season_id: str) -> pd.DataFrame:
    """
    Scrape league standings (table) from Transfermarkt.
    """
    league_info = LEAGUES.get(league_name)
    if not league_info:
        return pd.DataFrame()

    code = league_info["code"]
    slug = league_info["slug"]
    url = f"https://www.transfermarkt.com/{slug}/tabelle/wettbewerb/{code}/saison_id/{season_id}"

    print(f"\n🏆 Scraping standings: {league_name} ({season_id}/{int(season_id)+1})")
    print(f"   → {url}")

    soup = get_page(url)
    if not soup:
        return pd.DataFrame()

    table = soup.find("table", {"class": "items"})
    if not table:
        print("  [WARN] Could not find standings table.")
        return pd.DataFrame()

    rows = []
    for tr in table.find_all("tr")[1:]:  # Skip header row
        cells = tr.find_all("td")
        if len(cells) >= 10:
            try:
                rank = cells[0].get_text(strip=True)
                club = cells[2].get_text(strip=True)
                mp = cells[3].get_text(strip=True)
                w = cells[4].get_text(strip=True)
                d = cells[5].get_text(strip=True)
                l = cells[6].get_text(strip=True)
                goals_ratio = cells[7].get_text(strip=True)
                gd = cells[8].get_text(strip=True)
                pts = cells[9].get_text(strip=True)

                gf, ga = goals_ratio.split(":") if ":" in goals_ratio else (goals_ratio, "0")

                rows.append({
                    "Rank": rank,
                    "Club": club,
                    "Matches_Played": mp,
                    "Wins": w,
                    "Draws": d,
                    "Losses": l,
                    "Goals_For": gf,
                    "Goals_Against": ga,
                    "Goal_Difference": gd,
                    "Points": pts,
                    "League": league_name,
                    "Season": f"{season_id}/{int(season_id)+1}",
                    "Scraped_At": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
            except Exception:
                continue

    df = pd.DataFrame(rows)
    print(f"   ✅ {len(df)} clubs in standings.")
    return df


# ─────────────────────────────────────────────
#  SCRAPER — MARKET VALUES
# ─────────────────────────────────────────────

def scrape_market_values(league_name: str, season_id: str) -> pd.DataFrame:
    """
    Scrape top player market values from Transfermarkt.
    """
    league_info = LEAGUES.get(league_name)
    if not league_info:
        return pd.DataFrame()

    code = league_info["code"]
    slug = league_info["slug"]
    url = f"https://www.transfermarkt.com/{slug}/marktwerte/wettbewerb/{code}/saison_id/{season_id}"

    print(f"\n💶 Scraping player market values: {league_name} ({season_id}/{int(season_id)+1})")
    print(f"   → {url}")

    soup = get_page(url)
    if not soup:
        return pd.DataFrame()

    table = soup.find("table", {"class": "items"})
    if not table:
        print("  [WARN] Could not find market values table.")
        return pd.DataFrame()

    rows = []
    for tr in table.find_all("tr", class_=["odd", "even"]):
        cells = tr.find_all("td")
        if len(cells) >= 9:
            try:
                player = cells[3].find("a").get_text(strip=True)
                pos = cells[4].get_text(strip=True)
                age = cells[6].get_text(strip=True)
                
                club_img = cells[7].find("img")
                club = club_img.get("alt") if club_img else "N/A"
                
                val = cells[8].get_text(strip=True)

                rows.append({
                    "Player": player,
                    "Position": pos,
                    "Age": age,
                    "Club": club,
                    "Market_Value": val,
                    "League": league_name,
                    "Season": f"{season_id}/{int(season_id)+1}",
                    "Scraped_At": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
            except Exception:
                continue

    df = pd.DataFrame(rows)
    print(f"   ✅ {len(df)} market values scraped.")
    return df


# ─────────────────────────────────────────────
#  EXPORT
# ─────────────────────────────────────────────

def export_data(df: pd.DataFrame, filename: str, fmt: str = "csv"):
    """Export DataFrame to CSV, Excel, or JSON."""
    ensure_output_dir()
    filepath = os.path.join(OUTPUT_DIR, filename)

    if fmt == "csv":
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
    elif fmt == "excel":
        df.to_excel(filepath, index=False, engine="openpyxl")
    elif fmt == "json":
        df.to_json(filepath, orient="records", indent=2, force_ascii=False)
    else:
        print(f"  [ERROR] Unknown format: {fmt}")
        return

    print(f"   💾 Saved → {filepath}")


# ─────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="⚽ Football Stats Scraper — Transfermarkt Unified Parser",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--league", "-l",
        default="Serie A",
        choices=list(LEAGUES.keys()),
        help="League to scrape (default: Serie A)"
    )
    parser.add_argument(
        "--mode", "-m",
        default="all",
        choices=["stats", "standings", "values", "all"],
        help=(
            "What to scrape:\n"
            "  stats      → Player goals & assists (Transfermarkt)\n"
            "  standings  → League table (Transfermarkt)\n"
            "  values     → Market values (Transfermarkt)\n"
            "  all        → Everything above (default)"
        )
    )
    parser.add_argument(
        "--season", "-s",
        default=DEFAULT_SEASON,
        help=f"Season starting year (e.g. 2025 for season 2025/2026, default: {DEFAULT_SEASON})"
    )
    parser.add_argument(
        "--format", "-f",
        default="csv",
        choices=["csv", "excel", "json"],
        help="Output format (default: csv)"
    )
    args = parser.parse_args()

    league   = args.league
    mode     = args.mode
    season   = args.season
    fmt      = args.format
    ext      = {"csv": "csv", "excel": "xlsx", "json": "json"}[fmt]
    slug     = league.lower().replace(" ", "_")
    date_str = datetime.now().strftime("%Y%m%d")

    print("=" * 60)
    print(f"  ⚽ Football Stats Scraper (Unified)")
    print(f"  League : {league}")
    print(f"  Season : {season}/{int(season)+1}")
    print(f"  Mode   : {mode}")
    print(f"  Format : {fmt.upper()}")
    print("=" * 60)

    if mode in ("stats", "all"):
        df_stats = scrape_player_stats(league, season)
        if not df_stats.empty:
            export_data(df_stats, f"{slug}_player_stats_{date_str}.{ext}", fmt)

    if mode in ("standings", "all"):
        df_standings = scrape_standings(league, season)
        if not df_standings.empty:
            export_data(df_standings, f"{slug}_standings_{date_str}.{ext}", fmt)

    if mode in ("values", "all"):
        df_values = scrape_market_values(league, season)
        if not df_values.empty:
            export_data(df_values, f"{slug}_market_values_{date_str}.{ext}", fmt)

    print("\n✅ Done! Check the 'output/' folder for your files.")
    print("=" * 60)


if __name__ == "__main__":
    main()
