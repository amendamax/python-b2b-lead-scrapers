import os
import sys
import time
import json
import re
import random
import logging
from typing import Dict, List, Optional, Tuple
from playwright.sync_api import sync_playwright, Page, BrowserContext

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("AutomationEngine.AppPasswordGen")

class GmailAppPasswordGenerator:
    """
    Automated Playwright generator for 16-character Google App Passwords.
    Supports proxy rotation, Google login, password input, recovery challenge resolution,
    and automatic persistence into app_passwords.json.
    """
    APP_PASSWORDS_URL = "https://myaccount.google.com/apppasswords"

    def __init__(self, app_passwords_file: str = "app_passwords.json", headless: bool = False):
        self.app_passwords_file = app_passwords_file
        self.headless = headless

    def _parse_proxy(self, proxy_str: Optional[str]) -> Optional[Dict[str, str]]:
        if not proxy_str or not proxy_str.strip():
            return None
        p = proxy_str.strip()
        if not p.startswith("http://") and not p.startswith("https://") and not p.startswith("socks5://"):
            p = "http://" + p
        
        # Check if auth is embedded (http://user:pass@host:port)
        if "@" in p:
            proto, rest = p.split("://", 1)
            auth, host_port = rest.split("@", 1)
            username, password = auth.split(":", 1)
            return {
                "server": f"{proto}://{host_port}",
                "username": username,
                "password": password
            }
        return {"server": p}

    def generate_for_account(
        self,
        account_email: str,
        password: Optional[str] = None,
        recovery_email: Optional[str] = None,
        proxy: Optional[str] = None,
        app_label: str = "AutomationEngine"
    ) -> Optional[str]:
        """
        Logs into Google and generates a 16-character App Password.
        """
        logger.info(f"Starting App Password generation for {account_email}...")
        proxy_cfg = self._parse_proxy(proxy)
        if proxy_cfg:
            logger.info(f"Using Proxy: {proxy_cfg.get('server')}")

        with sync_playwright() as p:
            launch_args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--start-maximized"
            ]

            browser = p.chromium.launch(
                headless=self.headless,
                args=launch_args,
                proxy=proxy_cfg if proxy_cfg else None
            )

            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            try:
                page.goto(self.APP_PASSWORDS_URL, timeout=60000)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(3)

                # Step 1: Identifier / Email
                email_input = page.locator('#identifierId, input[name="identifier"], input[type="email"]').first
                if email_input.is_visible(timeout=8000):
                    logger.info(f"Entering email: {account_email}")
                    email_input.fill(account_email)
                    time.sleep(1)
                    
                    next_btn = page.locator('#identifierNext, button:has-text("Next"), button:has-text("Suivant"), button:has-text("Siguiente")').first
                    if next_btn.is_visible():
                        next_btn.click()
                    else:
                        page.keyboard.press("Enter")
                    time.sleep(4)

                # Step 2: Password
                pwd_input = page.locator('input[name="Passwd"], input[type="password"]').first
                if pwd_input.is_visible(timeout=10000):
                    if password:
                        logger.info("Entering password...")
                        pwd_input.fill(password)
                        time.sleep(1)
                        pwd_next = page.locator('#passwordNext, button:has-text("Next"), button:has-text("Suivant"), button:has-text("Siguiente")').first
                        if pwd_next.is_visible():
                            pwd_next.click()
                        else:
                            page.keyboard.press("Enter")
                        time.sleep(5)
                    else:
                        logger.warning(f"No password provided for {account_email}!")
                        browser.close()
                        return None

                # Step 3: Challenge / Recovery Email
                recov_btn = page.locator('div[data-challengeindex]:has-text("recovery"), div[data-challengetype="12"], li:has-text("recovery"), div:has-text("Confirm your recovery email"), div:has-text("Confirmez votre adresse")').first
                if recov_btn.is_visible(timeout=5000):
                    logger.info("Handling recovery email challenge...")
                    recov_btn.click()
                    time.sleep(3)

                recov_input = page.locator('input#knowledge-preregistered-email-response, input[type="email"], input[name="knowledgePreregisteredEmailResponse"]').first
                if recov_input.is_visible(timeout=5000):
                    if recovery_email:
                        logger.info(f"Filling recovery email: {recovery_email}")
                        recov_input.fill(recovery_email)
                        time.sleep(1)
                        page.keyboard.press("Enter")
                        time.sleep(5)
                    else:
                        logger.warning(f"Recovery email requested by Google, but not provided for {account_email}")

                # Step 4: Ensure we are on the App Passwords URL
                time.sleep(3)
                if "apppasswords" not in page.url:
                    logger.info("Navigating to App Passwords page...")
                    page.goto(self.APP_PASSWORDS_URL, timeout=45000)
                    time.sleep(3)

                # Step 5: Input App Name & Generate
                app_input = page.locator('input[aria-label*="App"], input[aria-label*="nom"], input[aria-label*="nombre"], input[aria-label*="application"], input[type="text"]').first
                if app_input.is_visible(timeout=10000):
                    logger.info(f"Entering App Name: {app_label}")
                    app_input.fill(app_label)
                    time.sleep(1)

                    create_btn = page.locator('button:has-text("Create"), button:has-text("Créer"), button:has-text("Crear"), button:has-text("Generați")').first
                    if create_btn.is_visible(timeout=5000):
                        create_btn.click()
                        time.sleep(4)

                        # Extract 16-character password from dialog
                        dialog_texts = page.locator('div[role="dialog"] span, .c-app-password, div[aria-live="polite"]').all_text_contents()
                        extracted_pwd = None
                        for txt in dialog_texts:
                            clean = txt.replace(" ", "").strip()
                            if len(clean) == 16 and clean.isalpha():
                                extracted_pwd = txt.strip()
                                break

                        if extracted_pwd:
                            logger.info(f"SUCCESS: Generated App Password for {account_email} -> {extracted_pwd}")
                            self._save_to_json(account_email, extracted_pwd)
                            browser.close()
                            return extracted_pwd

                logger.warning(f"Could not automatically locate App Password modal for {account_email}. URL: {page.url}")
                time.sleep(2)
                browser.close()
                return None

            except Exception as e:
                logger.error(f"Error during generation for {account_email}: {e}")
                browser.close()
                return None

    def _save_to_json(self, account_email: str, app_password: str) -> None:
        data = {}
        if os.path.exists(self.app_passwords_file):
            try:
                with open(self.app_passwords_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}

        data[account_email.strip().lower()] = app_password.strip()
        with open(self.app_passwords_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        logger.info(f"Persisted App Password for {account_email} in {self.app_passwords_file}")


def load_accounts(file_path: str = "accounts.txt") -> List[Tuple[str, str, Optional[str]]]:
    accounts = []
    # If xlsx exists, load from xlsx
    if file_path.endswith(".xlsx") or os.path.exists("accounts.xlsx"):
        xlsx_path = file_path if file_path.endswith(".xlsx") else "accounts.xlsx"
        try:
            import openpyxl
            wb = openpyxl.load_workbook(xlsx_path)
            sheet = wb.active
            for row in list(sheet.iter_rows(values_only=True))[1:]:
                if row[0] and "@" in str(row[0]):
                    email = str(row[0]).strip().lower()
                    pwd = str(row[1]).strip() if len(row) > 1 and row[1] else ""
                    rec = str(row[2]).strip() if len(row) > 2 and row[2] else None
                    accounts.append((email, pwd, rec))
            return accounts
        except Exception as e:
            logger.warning(f"Could not load .xlsx directly: {e}. Falling back to accounts.txt")

    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith(";"):
                continue
            parts = re.split(r"[:|,\t\s]+", line)
            email = parts[0].strip().lower()
            if "@" not in email:
                continue
            pwd = parts[1].strip() if len(parts) > 1 else ""
            rec = parts[2].strip() if len(parts) > 2 else None
            accounts.append((email, pwd, rec))
    return accounts


def load_proxies(file_path: str = "proxies.txt") -> List[str]:
    if not os.path.exists(file_path):
        return []
    proxies = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            p = line.strip()
            if p and not p.startswith("#"):
                proxies.append(p)
    return proxies


if __name__ == "__main__":
    print("=" * 75)
    print("   GMAIL APP PASSWORD AUTOMATION GENERATOR (PLAYWRIGHT + PROXIES)     ")
    print("=" * 75)

    accounts = load_accounts("accounts.txt")
    if not accounts:
        print("No accounts found in accounts.txt or accounts.xlsx!")
        sys.exit(1)

    proxies = load_proxies("proxies.txt")
    print(f"Loaded {len(accounts)} accounts.")
    if proxies:
        print(f"Loaded {len(proxies)} rotating proxies.")
    else:
        print("No proxies.txt detected (using direct server connection).")

    gen = GmailAppPasswordGenerator(app_passwords_file="app_passwords.json", headless=False)

    for i, (email, pwd, rec) in enumerate(accounts, 1):
        proxy = random.choice(proxies) if proxies else None
        print(f"\n[{i}/{len(accounts)}] Processing {email}...")
        res = gen.generate_for_account(email, pwd, rec, proxy=proxy)
        if res:
            print(f"  -> SUCCESS! Password: {res}")
        else:
            print(f"  -> Could not generate for {email}. Please verify credentials/2FA.")
