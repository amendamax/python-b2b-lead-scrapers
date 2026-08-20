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
    generate 16-character App Passwords, and persist them into app_passwords.json.
    """
    APP_PASSWORDS_URL = "https://myaccount.google.com/apppasswords"

    def __init__(self, app_passwords_file: str = "app_passwords.json", headless: bool = False):
        self.app_passwords_file = app_passwords_file
        self.headless = headless

    def generate_for_account(
        self,
        account_email: str,
        password: Optional[str] = None,
        storage_state_path: Optional[str] = None,
        app_label: str = "AutomationEngine"
    ) -> Optional[str]:
        """
        Automates App Password generation for a Gmail account using Playwright.
        """
        logger.info(f"Initiating App Password generation for {account_email}...")

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
            )

            context_args = {"viewport": {"width": 1280, "height": 800}}
            if storage_state_path and os.path.exists(storage_state_path):
                context_args["storage_state"] = storage_state_path

            context = browser.new_context(**context_args)
            page = context.new_page()

            try:
                page.goto(self.APP_PASSWORDS_URL, timeout=30000)
                page.wait_for_load_state("networkidle")

                # Handle login if not authenticated
                if "signin" in page.url or "identifier" in page.url:
                    logger.info(f"Logging in {account_email}...")
                    page.fill('input[type="email"]', account_email)
                    page.click('#identifierNext')
                    page.wait_for_selector('input[type="password"]', timeout=10000)
                    if password:
                        page.fill('input[type="password"]', password)
                        page.click('#passwordNext')
                        page.wait_for_load_state("networkidle")
                    else:
                        logger.warning("Password required for manual login authentication.")

                # Wait for App Passwords Input field
                app_name_input = page.locator('input[aria-label="App name"], input[type="text"]').first
                if app_name_input.is_visible(timeout=10000):
                    app_name_input.fill(app_label)
                    
                    # Click Create button
                    create_btn = page.locator('button:has-text("Create"), button:has-text("Generați")').first
                    create_btn.click()
                    page.wait_for_timeout(2000)

                    # Extract generated password from modal dialog
                    pwd_locator = page.locator('.c-app-password, div[aria-live="polite"], div[role="dialog"] span').all_text_contents()
                    extracted_pwd = None
                    for text in pwd_locator:
                        cleaned = text.replace(" ", "")
                        if len(cleaned) == 16 and cleaned.isalpha():
                            extracted_pwd = text.strip()
                            break

                    if extracted_pwd:
                        logger.info(f"Successfully generated App Password for {account_email}: {extracted_pwd}")
                        self._save_to_json(account_email, extracted_pwd)
                        browser.close()
                        return extracted_pwd

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
