import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger("AutomationEngine.PlaywrightManager")

class PlaywrightSessionManager:
    """
    Manages Playwright browser contexts for account persistence,
    cookies storage, and session lifecycle.
    """
    def __init__(self, sessions_dir: str = "data/sessions", headless: bool = True):
        self.sessions_dir = sessions_dir
        self.headless = headless
        os.makedirs(self.sessions_dir, exist_ok=True)

    def get_storage_state_path(self, account_email: str) -> str:
        safe_name = account_email.replace("@", "_at_").replace(".", "_")
        return os.path.join(self.sessions_dir, f"{safe_name}_session.json")

    def has_saved_session(self, account_email: str) -> bool:
        return os.path.exists(self.get_storage_state_path(account_email))

    def get_browser_launch_args(self, proxy: Optional[str] = None) -> Dict[str, Any]:
        args = {
            "headless": self.headless,
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-blink-features=AutomationControlled"
            ]
        }
        if proxy:
            args["proxy"] = {"server": proxy}
        return args
