import os
import sys
import time
import random
import signal
import logging
import concurrent.futures
import threading
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

# Local Architecture Imports
from file_parser import (
    ConfigParser, AppPasswordsParser, AccountsParser,
    LeadsParser, TemplateParser, LinksParser
)
from database import Database
from account_manager import AccountManager
from smtp_dispatcher import SMTPDispatcher
from proxy_pool import ProxyManager
from recovery_engine import ZeroDuplicateRecoveryEngine

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("AutomationEngine.Supervisor")

class AutomationSupervisor:
    """
    Enterprise Parallel Automation Engine orchestrating multi-account concurrency,
    real-time multi-threaded worker pools, proxy rotation, SQLite WAL atomic queuing,
    and graceful shutdown.
    """
    def __init__(self, config_path: str = "config.txt"):
        logger.info("Initializing Gmail Multi-Account Parallel Automation Engine...")
        self.run_id = f"RUN_{int(time.time())}"
        self.is_running = True
        self.lock = threading.Lock()

        # Load configurations and user files
        self.config = ConfigParser.parse(config_path)
        self.max_workers = int(self.config.get("CONCURRENT_WORKERS", 5))
        self.app_passwords = AppPasswordsParser.parse("app_passwords.json")
        self.accounts = AccountsParser.parse("accounts.txt", self.app_passwords)
        self.leads = LeadsParser.parse("leads.txt")
        self.template_html = TemplateParser.parse("letter.html")
        self.links = LinksParser.parse("links.txt")

        # Initialize Database & State
        db_file = self.config.get("DATABASE_FILE", "data/automation_engine.db")
        self.db = Database(db_file)
        self.db.sync_accounts(self.accounts, self.config.get("DEFAULT_DAILY_LIMIT_PER_ACCOUNT", 450))
        added_leads = self.db.sync_leads(self.leads)
        if added_leads > 0:
            logger.info(f"Enqueued {added_leads} new unique leads into database.")

        # Initialize Managers
        self.account_manager = AccountManager(
            db=self.db,
            accounts=self.accounts,
            app_passwords=self.app_passwords,
            default_daily_limit=self.config.get("DEFAULT_DAILY_LIMIT_PER_ACCOUNT", 450),
            reached_log_file="24-reached.txt"
        )
        self.dispatcher = SMTPDispatcher(
            host=self.config.get("SMTP_HOST", "smtp.gmail.com"),
            port=self.config.get("SMTP_PORT", 587),
            use_tls=self.config.get("USE_TLS", True),
            timeout=self.config.get("SMTP_TIMEOUT_SEC", 30)
        )
        self.proxy_manager = ProxyManager(
            proxy_file=self.config.get("PROXY_LIST_FILE", "proxies.txt"),
            enabled=self.config.get("ENABLE_PROXIES", False),
            max_failures=self.config.get("MAX_PROXY_FAILURES", 3)
        )

        # Execute Crash Recovery Sweep on Boot
        if self.config.get("ENABLE_IMAP_SENT_VERIFICATION", True):
            recovery_engine = ZeroDuplicateRecoveryEngine(self.db, self.app_passwords)
            recovery_engine.sweep_and_recover()

        # Register Signal Handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        logger.warning(f"Received termination signal ({signum}). Initiating graceful shutdown...")
        self.is_running = False

    def _worker_loop(self, worker_id: int) -> None:
        """
        Independent concurrent worker thread pulling leads and dispatching via SMTP.
        """
        logger.info(f"[Worker-{worker_id}] Thread online and connected to queue.")
        
        while self.is_running:
            # 1. Atomic queue check
            stats = self.db.get_queue_stats()
            if stats["pending"] == 0:
                break

            # 2. Thread-safe account selection
            with self.lock:
                account_info = self.account_manager.get_available_account()
            
            if not account_info:
                time.sleep(2)
                continue

            account_email = account_info["account_id"]
            app_password = account_info["app_password"]

            # 3. Atomically claim next lead (Zero Duplicates across threads)
            claim = self.db.claim_next_lead(account_email, f"{self.run_id}_W{worker_id}")
            if not claim:
                time.sleep(1)
                continue

            lead_id = claim["lead_id"]
            lead_email = claim["email"]
            message_id = claim["message_id"]

            # 4. Prepare personalized MIME message
            chosen_link = random.choice(self.links) if self.links else "https://isbrokersafe.com"
            recipient_name = lead_email.split("@")[0].capitalize()
            rendered_html = TemplateParser.render(self.template_html, {
                "recipient_name": recipient_name,
                "tracking_link": chosen_link,
                "message_ref": message_id.strip("<>"),
                "subject": self.config.get("SUBJECT", "Important Account Verification Notification"),
                "email": lead_email
            })

            proxy = self.proxy_manager.get_proxy_for_account(account_email)

            # 5. Concurrent Transmission
            logger.info(f"[Worker-{worker_id}] Dispatching to {lead_email} via {account_email} [Proxy: {proxy or 'DIRECT'}]...")
            result = self.dispatcher.send_email(
                account_email=account_email,
                app_password=app_password,
                recipient_email=lead_email,
                subject=self.config.get("SUBJECT", "Important Account Verification Notification"),
                html_body=rendered_html,
                message_id=message_id,
                sender_name=self.config.get("SENDER_NAME", "Verification Team"),
                proxy=proxy
            )

            # 6. Commit status & counters
            if result["success"]:
                self.db.mark_lead_completed(lead_id, account_email, message_id)
                self.proxy_manager.report_success(proxy)
                with self.lock:
                    self.account_manager.check_and_trigger_cooldown(account_email)
                logger.info(f"[Worker-{worker_id}] SUCCESS -> {lead_email} via {account_email}")
            else:
                err = result.get("error", "Unknown error")
                if "Daily user sending limit exceeded" in err or "550" in err:
                    logger.warning(f"[Worker-{worker_id}] Account {account_email} reached daily limit. Marking exhausted.")
                    with self.lock:
                        self.account_manager.mark_account_exhausted(account_email)
                    self.db.mark_lead_failed(lead_id, account_email, err)
                elif "Auth failed" in err:
                    logger.error(f"[Worker-{worker_id}] Auth failed for {account_email}. Marking error.")
                    with self.lock:
                        self.account_manager.mark_account_exhausted(account_email)
                    self.db.mark_lead_failed(lead_id, account_email, err)
                else:
                    self.db.mark_lead_failed(lead_id, account_email, err)
                    if proxy:
                        self.proxy_manager.report_failure(proxy)

            # Thread-safe worker pacing
            delay_min = float(self.config.get("MIN_PACING_DELAY_SEC", 1.0))
            delay_max = float(self.config.get("MAX_PACING_DELAY_SEC", 3.0))
            sleep_dur = random.uniform(delay_min, delay_max)
            time.sleep(sleep_dur)

        logger.info(f"[Worker-{worker_id}] Finished tasks.")

    def run(self) -> None:
        logger.info(f"Automation Engine Active | Parallel Workers: {self.max_workers} | Run ID: {self.run_id}")
        
        # Launch real multi-threaded worker pool
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self._worker_loop, w_id) for w_id in range(1, self.max_workers + 1)]
            concurrent.futures.wait(futures)

        logger.info("Supervisor finished all parallel operations.")

if __name__ == "__main__":
    supervisor = AutomationSupervisor("config.txt")
    supervisor.run()
