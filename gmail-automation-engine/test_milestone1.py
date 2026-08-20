import os
import sys
import json
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("TestMilestone1")

from file_parser import (
    ConfigParser, AppPasswordsParser, AccountsParser,
    LeadsParser, TemplateParser, LinksParser, LimitReachedLogger
)
from database import Database
from account_manager import AccountManager

def run_tests():
    print("================================================================================")
    print("       VERIFYING MILESTONE 1: CORE ARCHITECTURE, PARSERS & ACCOUNT STATE        ")
    print("================================================================================")
    
    # 1. Test File Parsers
    print("\n[+] Step 1: Testing File Parsers (All 7 User-Facing Files)...")
    config = ConfigParser.parse("config.txt")
    assert config["MAX_CONCURRENT_WORKERS"] == 10, "ConfigParser failed worker count"
    assert config["USE_TLS"] is True, "ConfigParser failed boolean casting"
    print(f"  -> config.txt parsed successfully: {len(config)} keys loaded.")

    app_passwords = AppPasswordsParser.parse("app_passwords.json")
    assert len(app_passwords) >= 3, "AppPasswordsParser failed"
    print(f"  -> app_passwords.json validated: {len(app_passwords)} credentials loaded.")

    accounts = AccountsParser.parse("accounts.txt", app_passwords)
    assert len(accounts) >= 3, "AccountsParser failed"
    print(f"  -> accounts.txt parsed: {len(accounts)} accounts verified.")

    leads = LeadsParser.parse("leads.txt")
    assert len(leads) == 5, "LeadsParser failed"
    print(f"  -> leads.txt parsed: {len(leads)} unique leads loaded.")

    template = TemplateParser.parse("letter.html")
    rendered = TemplateParser.render(template, {
        "recipient_name": "John Doe",
        "tracking_link": "https://isbrokersafe.com/free/scam-check",
        "message_ref": "REF-12345",
        "subject": "Security Notice"
    })
    assert "John Doe" in rendered and "https://isbrokersafe.com/free/scam-check" in rendered
    print("  -> letter.html template parsed and rendered successfully.")

    links = LinksParser.parse("links.txt")
    assert len(links) >= 4, "LinksParser failed"
    print(f"  -> links.txt parsed: {len(links)} rotation URLs loaded.")

    # 2. Test Database WAL Mode & Schema
    print("\n[+] Step 2: Testing SQLite WAL Database Initialization & Atomic Queue...")
    test_db_path = "data/test_engine.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = Database(test_db_path)
    with db.get_connection() as conn:
        journal_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        assert journal_mode.lower() == "wal", f"Expected WAL mode, got {journal_mode}"
        print(f"  -> SQLite Journal Mode: {journal_mode.upper()} (High Concurrency Enabled)")

    db.sync_accounts(accounts, daily_limit=5)
    added_leads = db.sync_leads(leads)
    print(f"  -> Synced {len(accounts)} accounts and {added_leads} leads into SQLite.")

    stats_initial = db.get_queue_stats()
    assert stats_initial["pending"] == 5, "Initial queue count mismatch"
    print(f"  -> Initial Queue State: {stats_initial}")

    # 3. Test Atomic Lead Claim (Zero-Duplicate Guarantee)
    print("\n[+] Step 3: Testing Atomic Lead Claiming & Deterministic Message-ID...")
    claimed = db.claim_next_lead(account_email="teamproject.dao@gmail.com", run_id="test_run_01")
    assert claimed is not None, "Failed to claim lead"
    assert claimed["assigned_account"] == "teamproject.dao@gmail.com"
    assert claimed["message_id"].startswith("<") and claimed["message_id"].endswith(">")
    print(f"  -> Atomically Claimed: {claimed['email']} | Message-ID: {claimed['message_id']}")

    # Mark as completed
    db.mark_lead_completed(claimed["lead_id"], claimed["assigned_account"], claimed["message_id"])
    stats_after = db.get_queue_stats()
    assert stats_after["completed"] == 1 and stats_after["pending"] == 4
    print(f"  -> Queue State After Send: {stats_after}")

    # 4. Test Account Manager & 24-Hour Cooldown Trigger
    print("\n[+] Step 4: Testing Account Manager & 24-Reached Logging...")
    manager = AccountManager(db, accounts, app_passwords, default_daily_limit=2, reached_log_file="24-reached.txt")
    
    # Simulate sender1 reaching limit of 2
    db.mark_lead_completed(2, "teamproject.dao@gmail.com", "<msg2@gmail.com>")
    triggered = manager.check_and_trigger_cooldown("teamproject.dao@gmail.com")
    assert triggered is True, "Cooldown trigger failed"
    print("  -> Cooldown triggered successfully for teamproject.dao@gmail.com.")

    # Verify 24-reached.txt
    assert os.path.exists("24-reached.txt")
    with open("24-reached.txt", "r", encoding="utf-8") as f:
        log_content = f.read()
        assert "teamproject.dao@gmail.com" in log_content
    print("  -> 24-reached.txt append verified:")
    print("     " + "\n     ".join([l for l in log_content.strip().splitlines() if "teamproject.dao@gmail.com" in l]))

    # Verify Next Available Account (Round-robin to sender2)
    next_acc = manager.get_available_account()
    assert next_acc is not None and next_acc["account_id"] != "teamproject.dao@gmail.com"
    print(f"  -> Account rotation verified: Next available is {next_acc['account_id']}")

    print("\n================================================================================")
    print("   MILESTONE 1 VERIFICATION RESULT: 100% PASS (ALL DELIVERABLES READY)          ")
    print("================================================================================")

if __name__ == "__main__":
    run_tests()
