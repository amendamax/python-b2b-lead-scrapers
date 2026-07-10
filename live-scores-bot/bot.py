"""
╔══════════════════════════════════════════════════════════╗
║          SOCCER LIVE SCORES & FIXTURES BOT  v1.0         ║
║  Telegram Bot for real-time scores and matches           ║
║  Source: ESPN Public API                                 ║
║  Features: Custom keyboards, Live scores, Yesterday/     ║
║            Tomorrow matches & Custom alerts              ║
╚══════════════════════════════════════════════════════════╝
"""

import os
import telebot
import requests
from datetime import datetime, timedelta
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

from config import LEAGUES, TELEGRAM_BOT_TOKEN

# Initialize Bot
token = os.environ.get("TELEGRAM_BOT_TOKEN", TELEGRAM_BOT_TOKEN)
if not token or token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
    print("[WARN] Telegram Bot Token is missing. Please set it in config.py or as an environment variable.")

bot = telebot.TeleBot(token)


# ─────────────────────────────────────────────
#  API PARSING UTILITIES
# ─────────────────────────────────────────────

def fetch_scoreboard(league_code: str, date_str: str = None) -> list:
    """Fetch matches from the ESPN API for a given league and optional date."""
    url = f"http://site.api.espn.com/apis/site/v2/sports/soccer/{league_code}/scoreboard"
    params = {}
    if date_str:
        params["dates"] = date_str

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("events", [])
    except Exception as e:
        print(f"Error fetching data for league {league_code}: {e}")
        return []


def format_match_info(event: dict) -> str:
    """Format an ESPN event object into a clean markdown string."""
    try:
        status_text = event["status"]["type"]["detail"]
        state = event["status"]["type"]["state"]  # pre, in, post
        
        competitors = event["competitions"][0]["competitors"]
        # Home/Away can be ordered differently. We inspect the 'homeAway' field.
        home = competitors[0] if competitors[0]["homeAway"] == "home" else competitors[1]
        away = competitors[1] if competitors[0]["homeAway"] == "home" else competitors[0]

        home_team = home["team"]["displayName"]
        away_team = away["team"]["displayName"]
        
        # State formatting
        if state == "in":
            # Live match
            home_score = home["score"]
            away_score = away["score"]
            status_indicator = f"🔴 *LIVE {status_text}*"
            score_text = f"*{home_score} - {away_score}*"
        elif state == "post":
            # Finished match
            home_score = home["score"]
            away_score = away["score"]
            status_indicator = "🏁 *FT*"
            score_text = f"*{home_score} - {away_score}*"
        else:
            # Scheduled match
            status_indicator = f"⏱️ {status_text}"
            score_text = "vs"

        return f"{status_indicator}\n🆚 {home_team} {score_text} {away_team}\n"
    except Exception:
        return ""


# ─────────────────────────────────────────────
#  TELEGRAM BOT COMMAND HANDLERS
# ─────────────────────────────────────────────

def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Create a reply keyboard for easy navigation."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    btn_live = KeyboardButton("🔴 Live Scores")
    btn_today = KeyboardButton("📅 Today's Matches")
    btn_yest = KeyboardButton("🏆 Yesterday's Results")
    btn_help = KeyboardButton("📖 Commands / Help")
    markup.row(btn_live, btn_today)
    markup.row(btn_yest, btn_help)
    return markup


@bot.message_handler(commands=["start", "help"])
def send_welcome(message):
    """Welcome message and instruction guide."""
    welcome_text = (
        "⚽ *Welcome to Soccer Live Scores Bot!*\n\n"
        "Get live scores, schedules, and past results for major European and World leagues instantly.\n\n"
        "*Available Commands:*\n"
        "👉 `/live` - Show all matches currently in progress\n"
        "👉 `/today [league]` - Show today's matches (e.g. `/today pl`)\n"
        "👉 `/results [league]` - Show yesterday's results\n"
        "👉 `/tomorrow [league]` - Show tomorrow's fixtures\n\n"
        "*Supported League Codes:*\n"
        "• `worldcup` - FIFA World Cup\n"
        "• `pl` - Premier League\n"
        "• `seriea` - Serie A\n"
        "• `laliga` - La Liga\n"
        "• `bundes` - Bundesliga\n"
        "• `ligue1` - Ligue 1\n"
        "• `ucl` - Champions League\n"
        "• `mls` - MLS\n\n"
        "Use the buttons below to navigate quickly!"
    )
    bot.send_message(
        message.chat.id,
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard()
    )


@bot.message_handler(commands=["live"])
def show_live_scores(message):
    """Retrieve all matches that are currently in progress."""
    bot.send_chat_action(message.chat.id, "typing")
    live_matches_found = False
    response_text = "📣 *Live Matches in Progress:*\n\n"

    for key, info in LEAGUES.items():
        events = fetch_scoreboard(info["code"])
        league_live_text = ""
        
        for event in events:
            if event["status"]["type"]["state"] == "in":
                match_str = format_match_info(event)
                if match_str:
                    league_live_text += match_str + "\n"

        if league_live_text:
            response_text += f"🏆 *{info['name']}*\n{league_live_text}"
            live_matches_found = True

    if not live_matches_found:
        response_text = "🔴 *No matches are currently live.* Check back later!"

    bot.send_message(message.chat.id, response_text, parse_mode="Markdown")


def show_matches_for_date(chat_id, date_str: str, title: str, league_filter: str = None):
    """Fetch and format matches for a specific date and optional league."""
    bot.send_chat_action(chat_id, "typing")
    
    # Identify target leagues
    target_leagues = {}
    if league_filter:
        clean_filter = league_filter.lower().strip()
        if clean_filter in LEAGUES:
            target_leagues = {clean_filter: LEAGUES[clean_filter]}
        else:
            bot.send_message(
                chat_id,
                f"⚠️ League code `{league_filter}` is not supported. Showing all leagues instead.",
                parse_mode="Markdown"
            )
            target_leagues = LEAGUES
    else:
        target_leagues = LEAGUES

    response_text = f"{title}\n\n"
    matches_found = False

    for key, info in target_leagues.items():
        events = fetch_scoreboard(info["code"], date_str)
        league_text = ""
        
        for event in events:
            match_str = format_match_info(event)
            if match_str:
                league_text += match_str + "\n"

        if league_text:
            response_text += f"🏆 *{info['name']}*\n{league_text}"
            matches_found = True

    if not matches_found:
        response_text += "📭 *No matches scheduled.*"

    # Split message if it exceeds Telegram's 4096 character limit
    if len(response_text) > 4000:
        for x in range(0, len(response_text), 4000):
            bot.send_message(chat_id, response_text[x:x+4000], parse_mode="Markdown")
    else:
        bot.send_message(chat_id, response_text, parse_mode="Markdown")


@bot.message_handler(commands=["today"])
def cmd_today(message):
    args = telebot.util.extract_arguments(message.text)
    date_str = datetime.now().strftime("%Y%m%d")
    show_matches_for_date(message.chat.id, date_str, "📅 *Today's Matches:*", args)


@bot.message_handler(commands=["results", "yesterday"])
def cmd_yesterday(message):
    args = telebot.util.extract_arguments(message.text)
    date_str = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    show_matches_for_date(message.chat.id, date_str, "🏆 *Yesterday's Results:*", args)


@bot.message_handler(commands=["tomorrow"])
def cmd_tomorrow(message):
    args = telebot.util.extract_arguments(message.text)
    date_str = (datetime.now() + timedelta(days=1)).strftime("%Y%m%d")
    show_matches_for_date(message.chat.id, date_str, "⏱️ *Tomorrow's Fixtures:*", args)


@bot.message_handler(commands=["test"])
def cmd_test(message):
    # Query May 17, 2026 (a busy matchday in the past to demonstrate format)
    show_matches_for_date(message.chat.id, "20260517", "🧪 *Test Matchday Results (17 May 2026):*")


# ─────────────────────────────────────────────
#  REPLY KEYBOARD TEXT ROUTING
# ─────────────────────────────────────────────

@bot.message_handler(func=lambda msg: True)
def text_routing(message):
    """Route custom keyboard clicks to respective handlers."""
    text = message.text
    if text == "🔴 Live Scores":
        show_live_scores(message)
    elif text == "📅 Today's Matches":
        cmd_today(message)
    elif text == "🏆 Yesterday's Results":
        cmd_yesterday(message)
    elif text == "📖 Commands / Help":
        send_welcome(message)
    else:
        # Default fallback
        bot.reply_to(
            message,
            "I only respond to the commands listed in `/help` or keyboard buttons.",
            reply_markup=get_main_keyboard()
        )


if __name__ == "__main__":
    print("[INFO] Live Scores Bot is starting...")
    print("Ready and listening for messages...")
    bot.infinity_polling()
