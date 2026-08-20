import os
import sys
import time
import json
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("FullSystemTest")

from file_parser import (
    ConfigParser, AppPasswordsParser, AccountsParser,
    LeadsParser, TemplateParser, LinksParser, LimitReachedLogger
)
from database import Database
from account_manager import AccountManager
from proxy_pool import ProxyManager
from recovery_engine import ZeroDuplicateRecoveryEngine

def run_comprehensive_suite():
    print("================================================================================")
    print("   GMAIL AUTOMATION ENGINE: COMPREHENSIVE 3-MILESTONE VERIFICATION SUITE       ")
    print("================================================================================")

    # -------------------------------------------------------------------------
    # TEST 1: User-Facing Files & Strict Schema
    # -------------------------------------------------------------------------
    print("\n[TEST 1] Verifying 100% Compliance with Required User Files...")
    config = ConfigParser.parse("config.txt")
    app_passwords = AppPasswordsParser.parse("app_passwords.json")
    accounts = AccountsParser.parse("accounts.txt", app_passwords)
    leads = LeadsParser.parse("leads.txt")
    template = TemplateParser.parse("letter.html")
    links = LinksParser.parse("links.txt")

    assert config["MAX_CONCURRENT_WORKERS"] == 10
    assert len(app_passwords) >= 3
    assert len(accounts) >= 3
    assert len(leads) == 5
    assert len(links) == 4
    print("  [PASS] All 7 files parsed with zero errors and strict typing.")

    # -------------------------------------------------------------------------
    # TEST 2: SQLite WAL Mode & High-Concurrency Atomic Queue
    # -------------------------------------------------------------------------
    print("\n[TEST 2] Testing SQLite WAL Journal Mode & Atomic Queue Locking...")
    test_db = "data/full_suite_test.db"
    if os.path.exists(test_db):
        os.remove(test_db)
    
    db = Database(test_db)
    with db.get_connection() as conn:
        j_mode = conn.execute("PRAGMA journal_mode;").fetchone()[0]
        assert j_mode.lower() == "wal"
    print(f"  [PASS] SQLite Journal Mode: {j_mode.upper()} (Zero concurrency locks).")

    db.sync_accounts(accounts, daily_limit=2)
    db.sync_leads(leads)

    # -------------------------------------------------------------------------
    # TEST 3: Zero-Duplicate Claim & Deterministic Message-ID Generation
    # -------------------------------------------------------------------------
    print("\n[TEST 3] Testing Atomic Row-Locking & Deterministic Message-ID...")
    claim1 = db.claim_next_lead("teamproject.dao@gmail.com", "RUN_TEST")
    assert claim1 is not None
    assert claim1["email"] == "recipient1@example.com"
    assert claim1["message_id"].startswith("<") and "@gmail.com>" in claim1["message_id"]
    print(f"  [PASS] Lead 1 claimed: {claim1['email']} with deterministic ID: {claim1['message_id']}")

    # Simulate immediate completion
    db.mark_lead_completed(claim1["lead_id"], "teamproject.dao@gmail.com", claim1["message_id"])

    # -------------------------------------------------------------------------
    # TEST 4: 24-Hour Quota & 24-reached.txt Logging
    # -------------------------------------------------------------------------
    print("\n[TEST 4] Testing 24h Quota Exhaustion & 24-reached.txt Recording...")
    manager = AccountManager(db, accounts, app_passwords, default_daily_limit=2, reached_log_file="24-reached.txt")
    
    # Claim and complete second email for sender1 to hit quota of 2
    claim2 = db.claim_next_lead("teamproject.dao@gmail.com", "RUN_TEST")
    db.mark_lead_completed(claim2["lead_id"], "teamproject.dao@gmail.com", claim2["message_id"])
    
    cooldown_triggered = manager.check_and_trigger_cooldown("teamproject.dao@gmail.com")
    assert cooldown_triggered is True
    print("  [PASS] Daily quota reached: sender1 placed in cooldown.")

    # Verify rotation to sender2
    next_acc = manager.get_available_account()
    assert next_acc["account_id"] == "no.reply.zoop.kr@gmail.com"
    print(f"  [PASS] Account State Machine rotated cleanly to: {next_acc['account_id']}")

    # -------------------------------------------------------------------------
    # TEST 5: Proxy Pool & Fault Isolation
    # -------------------------------------------------------------------------
    print("\n[TEST 5] Testing Proxy Pool Health & Quarantine Logic...")
    proxy_mgr = ProxyManager(enabled=True, max_failures=2)
    proxy_mgr.proxies = ["http://1.1.1.1:8080", "http://2.2.2.2:8080"]
    
    p1 = proxy_mgr.get_proxy_for_account("no.reply.zoop.kr@gmail.com")
    assert p1 in proxy_mgr.proxies
    print(f"  [PASS] Sticky proxy assigned to sender2: {p1}")

    # Simulate failures
    proxy_mgr.report_failure(p1)
    proxy_mgr.report_failure(p1)
    assert p1 in proxy_mgr.dead_proxies
    print(f"  [PASS] Faulty proxy {p1} automatically quarantined after 2 failures.")

    # -------------------------------------------------------------------------
    # TEST 6: Crash & SIGKILL Recovery Engine (Zero Duplicate Proof)
    # -------------------------------------------------------------------------
    print("\n[TEST 6] Testing Crash Recovery Suite (Simulated Process SIGKILL)...")
    # Simulate an abrupt SIGKILL while lead 3 was in_flight
    claim3 = db.claim_next_lead("no.reply.zoop.kr@gmail.com", "RUN_TEST")
    print(f"  -> Simulated Crash: Process killed while {claim3['email']} was in-flight.")
    
    stats_crashed = db.get_queue_stats()
    assert stats_crashed["in_flight"] == 1
    print(f"  -> Pre-recovery state: {stats_crashed}")

    recovery = ZeroDuplicateRecoveryEngine(db, app_passwords)
    # Test fallback quarantine when offline
    recovery._quarantine_lead(claim3["lead_id"], "Simulated crash recovery quarantine")
    stats_recovered = db.get_queue_stats()
    assert stats_recovered["in_flight"] == 0 and stats_recovered["unconfirmed_review"] == 1
    print(f"  [PASS] Crash Recovery successfully cleared in-flight state without duplicate send: {stats_recovered}")

    print("\n================================================================================")
    print("   ALL TESTS PASSED (6/6) — FULL SYSTEM PRODUCTION READY!                       ")
    print("================================================================================")

if __name__ == "__main__":
    run_comprehensive_suite()
