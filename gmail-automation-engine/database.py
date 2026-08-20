import os
import sqlite3
import hashlib
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timezone

logger = logging.getLogger("AutomationEngine.Database")

class Database:
    """
    High-reliability SQLite engine with WAL (Write-Ahead Logging) mode,
    busy timeout handling, and atomic row-level state locking for Zero Duplicates.
    """
    def __init__(self, db_path: str = "data/automation_engine.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        # WAL Mode Configuration for Concurrent Reads/Writes
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA busy_timeout=10000;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Accounts Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                account_id TEXT PRIMARY KEY,
                is_active INTEGER DEFAULT 1,
                daily_limit INTEGER DEFAULT 450,
                sent_today INTEGER DEFAULT 0,
                total_sent INTEGER DEFAULT 0,
                last_sent_at TEXT,
                cooldown_until TEXT,
                status TEXT DEFAULT 'idle',
                created_at TEXT DEFAULT (datetime('now'))
            );
            """)

            # Recipient Queue Table with deterministic message_id tracking
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads_queue (
                lead_id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                status TEXT DEFAULT 'pending', -- pending, in_flight, completed, failed, unconfirmed_review
                assigned_account TEXT,
                message_id TEXT,
                attempt_count INTEGER DEFAULT 0,
                last_attempt_at TEXT,
                completed_at TEXT,
                error_message TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads_queue(status);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_msgid ON leads_queue(message_id);")

            # Dispatch History Logs Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS dispatch_logs (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_email TEXT NOT NULL,
                account_email TEXT NOT NULL,
                message_id TEXT,
                status TEXT NOT NULL, -- success, failure, retry, skipped
                error_details TEXT,
                dispatch_time TEXT DEFAULT (datetime('now'))
            );
            """)

            # Daily Counters Table (Persisted across calendar days)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_counters (
                account_id TEXT NOT NULL,
                send_date TEXT NOT NULL,
                sent_count INTEGER DEFAULT 0,
                limit_reached INTEGER DEFAULT 0,
                PRIMARY KEY (account_id, send_date)
            );
            """)

            conn.commit()
            logger.info("Initialized SQLite WAL database successfully.")

    # Account Management Queries
    def sync_accounts(self, accounts: List[str], daily_limit: int = 450) -> None:
        with self.get_connection() as conn:
            for acc in accounts:
                conn.execute("""
                INSERT INTO accounts (account_id, daily_limit)
                VALUES (?, ?)
                ON CONFLICT(account_id) DO UPDATE SET is_active=1, daily_limit=excluded.daily_limit;
                """, (acc, daily_limit))
            conn.commit()

    def sync_leads(self, leads: List[str]) -> int:
        added = 0
        with self.get_connection() as conn:
            for email in leads:
                try:
                    conn.execute("""
                    INSERT INTO leads_queue (email, status)
                    VALUES (?, 'pending')
                    ON CONFLICT(email) DO NOTHING;
                    """, (email,))
                    added += 1
                except sqlite3.Error:
                    pass
            conn.commit()
        return added

    def get_queue_stats(self) -> Dict[str, int]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT status, COUNT(*) as count FROM leads_queue GROUP BY status;
            """)
            rows = cursor.fetchall()
            stats = {"pending": 0, "in_flight": 0, "completed": 0, "failed": 0, "unconfirmed_review": 0}
            for row in rows:
                stats[row["status"]] = row["count"]
            return stats

    # Atomic Queue Locking (Zero Duplicates Guarantee)
    def claim_next_lead(self, account_email: str, run_id: str) -> Optional[Dict[str, Any]]:
        """
        Atomically claims the next pending lead and transitions it to 'in_flight'
        with a deterministic Message-ID. Prevents race conditions among concurrent workers.
        """
        now_utc = datetime.now(timezone.utc).isoformat()
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE;")
            
            # Select the first available pending lead
            cursor.execute("""
            SELECT lead_id, email FROM leads_queue 
            WHERE status = 'pending' 
            ORDER BY lead_id ASC LIMIT 1;
            """)
            row = cursor.fetchone()
            if not row:
                conn.commit()
                return None
            
            lead_id = row["lead_id"]
            lead_email = row["email"]
            
            # Generate deterministic Message-ID
            hash_input = f"{lead_email}:{run_id}:{account_email}:{datetime.now(timezone.utc).strftime('%Y%m%d')}".encode("utf-8")
            msg_hash = hashlib.sha256(hash_input).hexdigest()[:16]
            domain = account_email.split("@")[-1] if "@" in account_email else "gmail.com"
            message_id = f"<{msg_hash}.{int(datetime.now(timezone.utc).timestamp())}@{domain}>"

            cursor.execute("""
            UPDATE leads_queue 
            SET status = 'in_flight',
                assigned_account = ?,
                message_id = ?,
                attempt_count = attempt_count + 1,
                last_attempt_at = ?
            WHERE lead_id = ? AND status = 'pending';
            """, (account_email, message_id, now_utc, lead_id))
            
            if cursor.rowcount == 0:
                # Contention: lead was claimed by another thread
                conn.commit()
                return None

            conn.commit()
            return {
                "lead_id": lead_id,
                "email": lead_email,
                "assigned_account": account_email,
                "message_id": message_id
            }

    def mark_lead_completed(self, lead_id: int, account_email: str, message_id: str) -> None:
        now_utc = datetime.now(timezone.utc).isoformat()
        today_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("BEGIN IMMEDIATE;")
            
            # 1. Update lead status
            cursor.execute("""
            UPDATE leads_queue
            SET status = 'completed', completed_at = ?
            WHERE lead_id = ?;
            """, (now_utc, lead_id))

            # 2. Update account counters
            cursor.execute("""
            UPDATE accounts
            SET sent_today = sent_today + 1,
                total_sent = total_sent + 1,
                last_sent_at = ?
            WHERE account_id = ?;
            """, (now_utc, account_email))

            # 3. Update daily persisted table
            cursor.execute("""
            INSERT INTO daily_counters (account_id, send_date, sent_count)
            VALUES (?, ?, 1)
            ON CONFLICT(account_id, send_date) DO UPDATE SET sent_count = sent_count + 1;
            """, (account_email, today_date))

            # 4. Insert log
            cursor.execute("""
            INSERT INTO dispatch_logs (lead_email, account_email, message_id, status)
            SELECT email, ?, ?, 'success' FROM leads_queue WHERE lead_id = ?;
            """, (account_email, message_id, lead_id))

            conn.commit()

    def mark_lead_failed(self, lead_id: int, account_email: str, error_message: str, can_retry: bool = True) -> None:
        new_status = 'pending' if can_retry else 'failed'
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE leads_queue
            SET status = ?, error_message = ?
            WHERE lead_id = ?;
            """, (new_status, error_message, lead_id))

            cursor.execute("""
            INSERT INTO dispatch_logs (lead_email, account_email, status, error_details)
            SELECT email, ?, 'failure', ? FROM leads_queue WHERE lead_id = ?;
            """, (account_email, error_message, lead_id))

            conn.commit()
