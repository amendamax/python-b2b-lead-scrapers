import os
import sys
import time
import json
import re
import random
import logging
from typing import Dict, List, Optional, Tuple
from playwright.sync_api import sync_playwright, Page, BrowserContext, TimeoutError as PlaywrightTimeoutError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)
logger = logging.getLogger("AutomationEngine.AppPasswordGen")

class GmailAppPasswordGenerator:
    """
    Enterprise automated Playwright generator for 16-character Google App Passwords.
    Features:
    - Multi-proxy automatic failover on latency/timeout
    - ColdProxy TCP optimization (--disable-quic, --disable-http2)
    - Google v3 sign-in challenge selection & recovery email resolution with explicit wait
    - Anti-bot stealth launch parameters with SSL certificate bypass
    - Auto-persistence to app_passwords.json
    """
    APP_PASSWORDS_URL = "https://accounts.google.com/ServiceLogin?continue=https://myaccount.google.com/apppasswords"

    def __init__(self, app_passwords_file: str = "app_passwords.json", headless: bool = False, max_proxy_retries: int = 3):
        self.app_passwords_file = app_passwords_file
        self.headless = headless
        self.max_proxy_retries = max_proxy_retries

    def _parse_proxy(self, proxy_str: Optional[str]) -> Optional[Dict[str, str]]:
        if not proxy_str or not proxy_str.strip():
            return None
        p = proxy_str.strip()
        if not p.startswith("http://") and not p.startswith("https://") and not p.startswith("socks5://"):
            p = "http://" + p
        
        if "@" in p:
            proto, rest = p.split("://", 1)
            auth, host_port = rest.split("@", 1)
            if ":" in auth:
                username, password = auth.split(":", 1)
            else:
                username, password = auth, ""
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
        proxies: Optional[List[str]] = None,
        app_label: str = "AutomationEngine"
    ) -> Optional[str]:
        proxy_pool = list(proxies) if proxies else [None]
        random.shuffle(proxy_pool)
        
        attempts = min(self.max_proxy_retries, len(proxy_pool))
        for attempt in range(attempts):
            proxy_str = proxy_pool[attempt] if proxy_pool else None
            proxy_cfg = self._parse_proxy(proxy_str)
            proxy_display = proxy_cfg.get('server') if proxy_cfg else 'DIRECT'
            logger.info(f"[{account_email}] Attempt {attempt + 1}/{attempts} | Proxy: {proxy_display}")

            res = self._run_browser_session(
                account_email=account_email,
                password=password,
                recovery_email=recovery_email,
                proxy_cfg=proxy_cfg,
                app_label=app_label
            )
            if res:
                return res
            logger.warning(f"[{account_email}] Attempt {attempt + 1} finished without password. Rotating to next proxy...")
            time.sleep(1)

        logger.error(f"[{account_email}] All proxy attempts exhausted.")
        return None

    def _run_browser_session(
        self,
        account_email: str,
        password: Optional[str],
        recovery_email: Optional[str],
        proxy_cfg: Optional[Dict[str, str]],
        app_label: str
    ) -> Optional[str]:
        with sync_playwright() as p:
            launch_args = [
                "--disable-blink-features=AutomationControlled",
                "--disable-quic",
                "--disable-http2",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--ignore-certificate-errors",
                "--allow-running-insecure-content",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--start-maximized"
            ]

            try:
                browser = p.chromium.launch(
                    headless=self.headless,
                    args=launch_args,
                    proxy=proxy_cfg if proxy_cfg else None,
                    timeout=30000
                )
            except Exception as e:
                logger.error(f"Failed to launch browser with proxy: {e}")
                return None

            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                ignore_https_errors=True
            )
            page = context.new_page()

            try:
                logger.info("Navigating to Google Sign In...")
                page.goto(self.APP_PASSWORDS_URL, timeout=30000)
                time.sleep(2)

                # Step 1: Email
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

                # Step 3: Handle Verification / Challenge Flow
                for step_attempt in range(5):
                    time.sleep(2)
                    url = page.url.lower()

                    # Check Challenge Selection page
                    if "challenge/selection" in url:
                        opts = page.locator('div[data-challengetype], li[data-challengetype], [data-challengeindex], div[role="link"], div[jsname], li').filter(has_text=re.compile(r'recovery|adresse|email|confir', re.I))
                        if opts.count() > 0:
                            logger.info("Clicking recovery email challenge option...")
                            try:
                                opts.first.click()
                                time.sleep(4)
                            except Exception:
                                pass

                    # Step 3b: Fill Recovery Email if input box appears
                    recov_input = page.locator('input#knowledge-preregistered-email-response, input[name="knowledgePreregisteredEmailResponse"], input[type="email"], input[type="text"]').first
                    if "challenge" in url and recov_input.is_visible(timeout=5000):
                        if recovery_email:
                            logger.info(f"Filling recovery email: {recovery_email}")
                            recov_input.fill(recovery_email)
                            time.sleep(1)
                            submit_btn = page.locator('#next, button:has-text("Next"), button:has-text("Suivant"), button[type="button"]').first
                            if submit_btn.is_visible():
                                submit_btn.click()
                            else:
                                page.keyboard.press("Enter")
                            time.sleep(6)
                        break

                    if "apppasswords" in url or "myaccount.google.com" in url:
                        break

                # Step 4: Direct navigation to App Passwords if logged in
                time.sleep(3)
                if "apppasswords" not in page.url and "challenge" not in page.url and "signin" not in page.url:
                    logger.info("Redirecting to App Passwords dashboard...")
                    page.goto("https://myaccount.google.com/apppasswords", timeout=25000)
                    time.sleep(3)

                # Step 5: Input App Name & Generate
                if "apppasswords" in page.url or "myaccount.google.com" in page.url:
                    app_input = page.locator('input[aria-label*="App"], input[aria-label*="nom"], input[aria-label*="nombre"], input[aria-label*="application"]').first
                    if not app_input.is_visible(timeout=5000):
                        app_input = page.locator('div[role="main"] input[type="text"]').first

                    if app_input.is_visible(timeout=5000):
                        logger.info(f"Entering App Name: {app_label}")
                        app_input.fill(app_label)
                        time.sleep(1)

                        create_btn = page.locator('button:has-text("Create"), button:has-text("Créer"), button:has-text("Crear"), button:has-text("Generați")').first
                        if create_btn.is_visible(timeout=5000):
                            create_btn.click()
                            time.sleep(3)

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

                logger.warning(f"App Password modal not available for {account_email} (2FA might be disabled on this account). URL: {page.url}")
                browser.close()
                return None

            except PlaywrightTimeoutError as e:
                logger.warning(f"Proxy timeout for {account_email}: {e}")
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

    gen = GmailAppPasswordGenerator(app_passwords_file="app_passwords.json", headless=False, max_proxy_retries=3)

    for i, (email, pwd, rec) in enumerate(accounts, 1):
        print(f"\n[{i}/{len(accounts)}] Processing {email}...")
        res = gen.generate_for_account(email, pwd, rec, proxies=proxies)
        if res:
            print(f"  -> SUCCESS! Password: {res}")
        else:
            print(f"  -> Finished check for {email}")
