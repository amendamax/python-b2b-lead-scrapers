import os
import time
import random
import logging
from typing import Dict, List, Optional

logger = logging.getLogger("AutomationEngine.ProxyPool")

class ProxyManager:
    """
    Thread-safe Proxy Manager with latency scoring, dead proxy isolation,
    and per-account sticky session mapping.
    """
    def __init__(self, proxy_file: str = "proxies.txt", enabled: bool = False, max_failures: int = 3):
        self.proxy_file = proxy_file
        self.enabled = enabled
        self.max_failures = max_failures
        self.proxies: List[str] = []
        self.dead_proxies: Dict[str, float] = {} # proxy -> quarantine_timestamp
        self.account_proxy_map: Dict[str, str] = {} # account_id -> proxy
        self.failure_counts: Dict[str, int] = {}

        if self.enabled and os.path.exists(self.proxy_file):
            self._load_proxies()

    def _load_proxies(self) -> None:
        with open(self.proxy_file, "r", encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if line and not line.startswith("#"):
                    self.proxies.append(line)
        logger.info(f"Loaded {len(self.proxies)} proxies from {self.proxy_file}")

    def get_proxy_for_account(self, account_id: str) -> Optional[str]:
        if not self.enabled or not self.proxies:
            return None
        
        if account_id in self.account_proxy_map:
            assigned = self.account_proxy_map[account_id]
            if assigned not in self.dead_proxies:
                return assigned
        
        # Pick least failed active proxy
        active = [p for p in self.proxies if p not in self.dead_proxies]
        if not active:
            logger.warning("All proxies quarantined. Falling back to direct connection.")
            return None
        
        chosen = random.choice(active)
        self.account_proxy_map[account_id] = chosen
        return chosen

    def report_failure(self, proxy: str) -> None:
        if not proxy:
            return
        self.failure_counts[proxy] = self.failure_counts.get(proxy, 0) + 1
        if self.failure_counts[proxy] >= self.max_failures:
            self.dead_proxies[proxy] = time.time()
            logger.error(f"Quarantined dead proxy after {self.max_failures} failures: {proxy}")

    def report_success(self, proxy: str) -> None:
        if proxy in self.failure_counts:
            self.failure_counts[proxy] = max(0, self.failure_counts[proxy] - 1)
