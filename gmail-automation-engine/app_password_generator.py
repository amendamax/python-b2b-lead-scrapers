import os
import time
import json
import logging
from typing import Dict, List, Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext

logger = logging.getLogger("AutomationEngine.AppPasswordGen")

class GmailAppPasswordGenerator:
    """
    Playwright automation tool to navigate Google Security settings,
    solve authentication & recovery email challenges, generate 16-character
    App Passwords, and persist them into app_passwords.json.
    """
    APP_PASSWORDS_URL = "https://myaccount.google.com/apppasswords"

    def __init__(self, app_passwords_file: str = "app_passwords.json", headless: bool = False):
        self.app_passwords_file = app_passwords_file
        self.headless = headless

    def generate_for_account(
        self,
        account_email: str,
        password: Optional[str] = None,
        recovery_email: Optional[str] = None,
        storage_state_path: Optional[str] = None,
        app_label: str = "AutomationEngine"
    ) -> Optional[str]:
        """
        Automates App Password generation for a Gmail account using Playwright.
        Handles email, password, and Google recovery email challenges.
        """
        logger.info(f"Initiating App Password generation for {account_email}...")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--start-maximized"
                ]
            )

            context_args = {
                "viewport": {"width": 1280, "height": 800},
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
            }
            if storage_state_path and os.path.exists(storage_state_path):
                context_args["storage_state"] = storage_state_path

            context = browser.new_context(**context_args)
            page = context.new_page()

            try:
                page.goto(self.APP_PASSWORDS_URL, timeout=45000)
                page.wait_for_load_state("domcontentloaded")
                time.sleep(2)

                # 1. Handle Email Entry
                if page.locator('input[type="email"]').is_visible(timeout=5000):
                    logger.info(f"Filling email: {account_email}...")
                    page.fill('input[type="email"]', account_email)
                    page.keyboard.press("Enter")
                    time.sleep(3)

                # 2. Handle Password Entry
                if page.locator('input[type="password"]').is_visible(timeout=8000):
                    if password:
                        logger.info("Filling password...")
                        page.fill('input[type="password"]', password)
                        page.keyboard.press("Enter")
                        time.sleep(4)
                    else:
                        logger.warning("Password prompt detected but no password provided.")

                # 3. Handle Recovery Email Challenge if triggered
                if recovery_email and (page.locator('text="Confirm your recovery email"').is_visible(timeout=4000) or page.locator('div[data-challengeindex]').is_visible(timeout=3000)):
                    logger.info(f"Recovery email challenge detected. Handling with: {recovery_email}...")
                    if page.locator('text="Confirm your recovery email"').is_visible():
                        page.locator('text="Confirm your recovery email"').click()
                        time.sleep(2)
                    
                    recov_input = page.locator('input[type="email"], input[type="text"]').first
                    if recov_input.is_visible(timeout=5000):
                        recov_input.fill(recovery_email)
                        page.keyboard.press("Enter")
                        time.sleep(4)

                # 4. Navigate directly to App Passwords if redirected to general security
                if "apppasswords" not in page.url:
                    page.goto(self.APP_PASSWORDS_URL, timeout=30000)
                    time.sleep(2)

                # 5. Handle App Name Input & Generation
                app_name_input = page.locator('input[aria-label="App name"], input[type="text"]').first
                if app_name_input.is_visible(timeout=10000):
                    app_name_input.fill(app_label)
                    time.sleep(1)
                    
                    # Click Create button
                    create_btn = page.locator('button:has-text("Create"), button:has-text("Generați"), button:has-text("Crear")').first
                    create_btn.click()
                    time.sleep(3)

                    # Extract generated password
                    pwd_elements = page.locator('.c-app-password, div[aria-live="polite"], div[role="dialog"] span').all_text_contents()
                    extracted_pwd = None
                    for text in pwd_elements:
                        cleaned = text.replace(" ", "").strip()
                        if len(cleaned) == 16 and cleaned.isalpha():
                            extracted_pwd = text.strip()
                            break

                    if extracted_pwd:
                        logger.info(f"SUCCESS: Generated App Password for {account_email}: {extracted_pwd}")
                        self._save_to_json(account_email, extracted_pwd)
                        browser.close()
                        return extracted_pwd

                logger.warning("Could not locate App Password generation modal. Please inspect page manually.")
                browser.close()
                return None

            except Exception as e:
                logger.error(f"Error during App Password automation for {account_email}: {e}")
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
        logger.info(f"Updated {self.app_passwords_file} with new App Password for {account_email}")
