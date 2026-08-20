import imaplib
import email
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from database import Database

logger = logging.getLogger("AutomationEngine.RecoveryEngine")

class ZeroDuplicateRecoveryEngine:
    """
    Crash & Restart Recovery Engine.
    Resolves the distributed dual-write problem by querying the Gmail account's
    [Gmail]/Sent Mail folder for in-flight deterministic Message-IDs upon boot.
    """
    def __init__(self, db: Database, app_passwords: Dict[str, str], imap_host: str = "imap.gmail.com", imap_port: int = 993):
        self.db = db
        self.app_passwords = app_passwords
        self.imap_host = imap_host
        self.imap_port = imap_port

    def sweep_and_recover(self) -> Dict[str, int]:
        """
        Scans SQLite for any leads left in 'in_flight' state after an unexpected shutdown.
        Verifies against IMAP Sent Mail. Commits completed if sent, resets to pending if not.
        """
        results = {"verified_sent": 0, "reset_pending": 0, "quarantined": 0}
        
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT lead_id, email, assigned_account, message_id 
            FROM leads_queue 
            WHERE status = 'in_flight';
            """)
            in_flight_leads = cursor.fetchall()
        
        if not in_flight_leads:
            logger.info("Crash Recovery Check: No unconfirmed in-flight leads found. State is clean.")
            return results

        logger.warning(f"Crash Recovery Check: Found {len(in_flight_leads)} unconfirmed in-flight leads. Starting verification...")

        for lead in in_flight_leads:
            lead_id = lead["lead_id"]
            lead_email = lead["email"]
            account_email = lead["assigned_account"]
            message_id = lead["message_id"]

            if not account_email or account_email not in self.app_passwords:
                logger.warning(f"Cannot verify lead {lead_id} ({lead_email}): Account {account_email} not configured.")
                self._quarantine_lead(lead_id, "Missing account credentials during recovery")
                results["quarantined"] += 1
                continue

            app_password = self.app_passwords[account_email].replace(" ", "")
            
            # Check IMAP Sent Folder
            is_sent = self._check_imap_sent(account_email, app_password, message_id, lead_email)
            
            if is_sent is True:
                # Confirmed sent by Google
                logger.info(f"Recovery Verified: Message {message_id} was found in Sent Mail. Marking completed.")
                self.db.mark_lead_completed(lead_id, account_email, message_id)
                results["verified_sent"] += 1
            elif is_sent is False:
                # Confirmed NOT sent before crash
                logger.info(f"Recovery Reset: Message {message_id} was not sent. Safely resetting {lead_email} to pending.")
                self.db.mark_lead_failed(lead_id, account_email, "Recovered after crash (never reached SMTP)", can_retry=True)
                results["reset_pending"] += 1
            else:
                # IMAP unreachable: Quarantine to enforce ZERO DUPLICATES
                logger.warning(f"Recovery Timeout: Could not connect to IMAP for {account_email}. Quarantining {lead_email}.")
                self._quarantine_lead(lead_id, "IMAP unreachable during crash recovery")
                results["quarantined"] += 1

        return results

    def _check_imap_sent(self, account_email: str, app_password: str, target_message_id: str, recipient_email: str) -> Optional[bool]:
        try:
            mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port, timeout=15)
            mail.login(account_email, app_password)
            
            # Select Sent Mail (handles standard and internationalized folder names)
            status, _ = mail.select('"[Gmail]/Sent Mail"')
            if status != "OK":
                status, _ = mail.select("Sent")
            
            if status != "OK":
                mail.logout()
                return None

            # Search by recipient email in recent messages
            search_query = f'(TO "{recipient_email}")'
            typ, msg_ids = mail.search(None, search_query)
            
            if typ != "OK" or not msg_ids[0]:
                mail.logout()
                return False

            # Check matching Message-ID
            ids_list = msg_ids[0].split()
            for m_id in ids_list[-10:]: # Check last 10 matching sends
                typ, data = mail.fetch(m_id, "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])")
                if typ == "OK" and data and data[0]:
                    header_text = data[0][1].decode("utf-8", errors="ignore")
                    if target_message_id.strip("<>") in header_text:
                        mail.logout()
                        return True

            mail.logout()
            return False

        except Exception as e:
            logger.error(f"IMAP verification error for {account_email}: {e}")
            return None

    def _quarantine_lead(self, lead_id: int, reason: str) -> None:
        with self.db.get_connection() as conn:
            conn.execute("""
            UPDATE leads_queue 
            SET status = 'unconfirmed_review', error_message = ? 
            WHERE lead_id = ?;
            """, (reason, lead_id))
            conn.commit()
