import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta
from database import Database
from file_parser import LimitReachedLogger

logger = logging.getLogger("AutomationEngine.AccountManager")

class AccountManager:
    """
    State machine and scheduler managing multi-account rotation,
    per-account daily/hourly quotas, and cooldown triggers.
    """
    def __init__(self, db: Database, accounts: List[str], app_passwords: Dict[str, str], default_daily_limit: int = 450, reached_log_file: str = "24-reached.txt"):
        self.db = db
        self.accounts = accounts
        self.app_passwords = app_passwords
        self.default_daily_limit = default_daily_limit
        self.reached_log_file = reached_log_file
        
        # Initialize/sync accounts in DB
        self.db.sync_accounts(self.accounts, self.default_daily_limit)

    def get_available_account(self) -> Optional[Dict[str, Any]]:
        """
        Retrieves the best available account using round-robin / least-used strategy
        that has not exceeded its 24-hour limit and is not under cooldown.
        """
        now_utc = datetime.now(timezone.utc)
        now_iso = now_utc.isoformat()
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT account_id, daily_limit, sent_today, cooldown_until, status 
            FROM accounts 
            WHERE is_active = 1 
              AND (cooldown_until IS NULL OR cooldown_until < ?)
              AND sent_today < daily_limit
            ORDER BY sent_today ASC, last_sent_at ASC NULLS FIRST
            LIMIT 1;
            """, (now_iso,))
            row = cursor.fetchone()
            
            if not row:
                return None
            
            acc_id = row["account_id"]
            return {
                "account_id": acc_id,
                "app_password": self.app_passwords.get(acc_id, ""),
                "daily_limit": row["daily_limit"],
                "sent_today": row["sent_today"]
            }

    def check_and_trigger_cooldown(self, account_email: str) -> bool:
        """
        Checks if an account reached its daily limit. If reached, activates 24h cooldown
        and appends an entry to 24-reached.txt.
        """
        now_utc = datetime.now(timezone.utc)
        today_date = now_utc.strftime("%Y-%m-%d")
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT daily_limit, sent_today FROM accounts WHERE account_id = ?;
            """, (account_email,))
            row = cursor.fetchone()
            
            if not row:
                return False
            
            daily_limit = row["daily_limit"]
            sent_today = row["sent_today"]
            
            if sent_today >= daily_limit:
                # Set cooldown until midnight UTC or 24 hours
                cooldown_until = now_utc.replace(hour=23, minute=59, second=59, microsecond=0)
                if cooldown_until <= now_utc:
                    cooldown_until += timedelta(days=1)
                
                cursor.execute("""
                UPDATE accounts 
                SET cooldown_until = ?, status = 'cooling_down'
                WHERE account_id = ?;
                """, (cooldown_until.isoformat(), account_email))

                cursor.execute("""
                UPDATE daily_counters
                SET limit_reached = 1
                WHERE account_id = ? AND send_date = ?;
                """, (account_email, today_date))

                conn.commit()

                # Record in 24-reached.txt
                LimitReachedLogger.record(
                    account_email=account_email,
                    daily_limit=daily_limit,
                    cooldown_until=cooldown_until,
                    file_path=self.reached_log_file
                )
                return True
        return False
