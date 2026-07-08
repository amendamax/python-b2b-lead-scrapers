"""
╔══════════════════════════════════════════════════════════╗
║          BETTING ODDS AGGREGATOR & ALERTER  v1.0         ║
║  Scrapes upcoming/live odds across bookmakers            ║
║  Source: BetExplorer.com (Dynamic JS Rendering)          ║
║  Features: Value Bet Detector & Surebet Finder           ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import time
import argparse
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from config import (
    SPORTS_URLS,
    DEFAULT_SPORT,
    DEFAULT_VALUE_THRESHOLD,
    USER_AGENT,
    PAGE_LOAD_WAIT,
    OUTPUT_DIR,
)


def init_webdriver() -> webdriver.Chrome:
    """Initialize a headless Google Chrome webdriver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(f"user-agent={USER_AGENT}")
    return webdriver.Chrome(options=options)


def parse_odds_page(sport: str) -> str:
    """Load the target sport page using Selenium and return the page source."""
    url = SPORTS_URLS.get(sport)
    if not url:
        raise ValueError(f"Sport '{sport}' is not supported in configuration.")

    print(f"🌐 Fetching {sport.upper()} matches...")
    print(f"   → {url}")

    driver = init_webdriver()
    try:
        driver.get(url)
        time.sleep(PAGE_LOAD_WAIT)
        return driver.page_source
    finally:
        driver.quit()


def process_match_odds(html_source: str, threshold: float) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Parse the HTML, detect Value Bets and Surebets (Arbitrage).
    Returns: (all_matches_df, value_bets_df, sure_bets_df)
    """
    soup = BeautifulSoup(html_source, "lxml")
    elements = soup.find_all(
        ["li", "ul"],
        class_=lambda x: x and any(c in x.split() for c in ["table-main__tournamentNavLi", "table-main__matchInfo"])
    )

    all_matches = []
    value_bets = []
    sure_bets = []

    current_league = "Unknown League"

    for el in elements:
        classes = el.get("class", [])

        # 1. Update active league when a header row is encountered
        if "table-main__tournamentNavLi" in classes:
            current_league = el.get_text(strip=True)
            continue

        # 2. Process match row
        if "table-main__matchInfo" in classes:
            cells = el.find_all("li", recursive=False)
            if len(cells) < 3:
                continue

            try:
                # Time / Live minute
                time_status = cells[0].get_text(strip=True)

                # Participant/Team Names
                participants_cell = cells[1]
                home_tag = participants_cell.find(class_="table-main__participantHome")
                away_tag = participants_cell.find(class_="table-main__participantAway")

                if not home_tag or not away_tag:
                    continue

                home_team = home_tag.get_text(strip=True)
                away_team = away_tag.get_text(strip=True)

                # Odds Cells
                odds_cell = cells[2]
                odds_elements = odds_cell.find_all("p", class_="liveOdds")

                # Extract Average and Max Odds
                avg_odds = []
                max_odds = []

                for o in odds_elements:
                    avg_val = o.get_text(strip=True)
                    max_val = o.get("data-odd-max")
                    
                    if avg_val and max_val:
                        try:
                            avg_odds.append(float(avg_val))
                            max_odds.append(float(max_val))
                        except ValueError:
                            continue

                if not avg_odds or len(avg_odds) < 2:
                    continue

                # Prepare basic match data dictionary
                match_data = {
                    "League": current_league,
                    "Time_Status": time_status,
                    "Home_Team": home_team,
                    "Away_Team": away_team,
                    "Scraped_At": datetime.now().strftime("%Y-%m-%d %H:%M"),
                }

                # Save odds values depending on count (1X2 vs 12 sports)
                if len(avg_odds) == 3:
                    match_data.update({
                        "Avg_1": avg_odds[0], "Avg_X": avg_odds[1], "Avg_2": avg_odds[2],
                        "Max_1": max_odds[0], "Max_X": max_odds[1], "Max_2": max_odds[2],
                    })
                elif len(avg_odds) == 2:
                    match_data.update({
                        "Avg_1": avg_odds[0], "Avg_2": avg_odds[1],
                        "Max_1": max_odds[0], "Max_2": max_odds[1],
                    })

                all_matches.append(match_data)

                # A. Value Bet Detection (Max Odd significantly higher than Average)
                outcomes = ["1", "X", "2"] if len(avg_odds) == 3 else ["1", "2"]
                for idx, outcome in enumerate(outcomes):
                    avg_o = avg_odds[idx]
                    max_o = max_odds[idx]
                    
                    if avg_o > 1.0:
                        diff_pct = ((max_o - avg_o) / avg_o) * 100
                        if diff_pct >= threshold:
                            value_bets.append({
                                "League": current_league,
                                "Time_Status": time_status,
                                "Match": f"{home_team} vs {away_team}",
                                "Outcome": outcome,
                                "Avg_Odd": avg_o,
                                "Max_Odd": max_o,
                                "Profit_Increase_Pct": round(diff_pct, 1)
                            })

                # B. Surebet / Arbitrage Detection
                # Formula: Sum of Reciprocals (1/Max_Odds) < 1.0
                reciprocals = [1.0 / o for o in max_odds if o > 0]
                if len(reciprocals) == len(avg_odds):
                    margin = sum(reciprocals)
                    if margin < 1.0:
                        profit_pct = (1.0 / margin - 1.0) * 100
                        sure_bets.append({
                            "League": current_league,
                            "Time_Status": time_status,
                            "Match": f"{home_team} vs {away_team}",
                            "Odds": "/".join([str(o) for o in max_odds]),
                            "Margin": round(margin, 3),
                            "Guaranteed_Profit_Pct": round(profit_pct, 1)
                        })

            except Exception:
                continue

    return pd.DataFrame(all_matches), pd.DataFrame(value_bets), pd.DataFrame(sure_bets)


# ─────────────────────────────────────────────
#  EXPORT & REPORTING
# ─────────────────────────────────────────────

def export_results(df: pd.DataFrame, filename: str, fmt: str):
    """Save results into target folder and format."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)

    if fmt == "csv":
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
    elif fmt == "excel":
        df.to_excel(filepath, index=False, engine="openpyxl")
    elif fmt == "json":
        df.to_json(filepath, orient="records", indent=2, force_ascii=False)
    
    print(f"   💾 Saved → {filepath}")


# ─────────────────────────────────────────────
#  CLI
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="📊 Betting Odds Aggregator, Value Bet Finder & Arbitrage Alerter",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--sport", "-s",
        default=DEFAULT_SPORT,
        choices=list(SPORTS_URLS.keys()),
        help=f"Sport to scrape (default: {DEFAULT_SPORT})"
    )
    parser.add_argument(
        "--threshold", "-t",
        type=float,
        default=DEFAULT_VALUE_THRESHOLD,
        help=f"Value bet alert percentage threshold (default: {DEFAULT_VALUE_THRESHOLD}%)"
    )
    parser.add_argument(
        "--format", "-f",
        default="csv",
        choices=["csv", "excel", "json"],
        help="Export format (default: csv)"
    )
    args = parser.parse_args()

    sport = args.sport
    threshold = args.threshold
    fmt = args.format
    ext = {"csv": "csv", "excel": "xlsx", "json": "json"}[fmt]
    date_str = datetime.now().strftime("%Y%m%d")

    print("=" * 60)
    print(f"  📊 Betting Odds Aggregator & Alerter")
    print(f"  Sport     : {sport.upper()}")
    print(f"  Threshold : {threshold}%")
    print(f"  Format    : {fmt.upper()}")
    print("=" * 60)

    try:
        html = parse_odds_page(sport)
        df_all, df_value, df_sure = process_match_odds(html, threshold)

        print(f"\n📈 Results Summary:")
        print(f"   Matches Scraped   : {len(df_all)}")
        print(f"   Value Bets Found  : {len(df_value)}")
        print(f"   Surebets Found    : {len(df_sure)}")

        # Exports
        if not df_all.empty:
            export_results(df_all, f"{sport}_all_odds_{date_str}.{ext}", fmt)
        if not df_value.empty:
            export_results(df_value, f"{sport}_value_bets_{date_str}.{ext}", fmt)
            print(f"\n🔥 Top Value Bets (Max vs Avg Odd Diff >= {threshold}%):")
            # Print value bets cleanly
            print(df_value[["Match", "Outcome", "Avg_Odd", "Max_Odd", "Profit_Increase_Pct"]].head(10).to_string(index=False))
        if not df_sure.empty:
            export_results(df_sure, f"{sport}_sure_bets_{date_str}.{ext}", fmt)
            print(f"\n🚨 Arbitrage/Surebets Found (Risk-free Profit):")
            print(df_sure[["Match", "Odds", "Margin", "Guaranteed_Profit_Pct"]].to_string(index=False))

    except Exception as e:
        print(f"\n[ERROR] Execution failed: {e}")
    finally:
        print("=" * 60)


if __name__ == "__main__":
    main()
