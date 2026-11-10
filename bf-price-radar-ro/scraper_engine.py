"""
scraper_engine.py
Motor asincron de scraping B2B 100% LIVE (Playwright + httpx + selectolax) cu:
- ZERO date mock/seed/hardcodate: toate preturile, titlurile, stocurile si URL-urile sunt extrase live din HTML/JSON
- Interceptor strict de ruta in Playwright (blocheaza image, media, font, stylesheet + scripturi analytics/pixel) -> < 50-80 KB/pagina
- Politica de proxy inteligenta (.env): USE_PROXY_FOR_STORES=false implicit, fallback automat pe proxy la HTTP 403/429
- Pauza politicoasa asyncio.sleep(random.uniform(min_delay, max_delay)) intre cererile pe acelasi domeniu
- Parsare multi-layer: WooCommerce Store API JSON, Schema.org JSON-LD, Gomag, CS-Cart, WooCommerce HTML si eMAG Marketplace
"""

from __future__ import annotations

import asyncio
import asyncio.tasks as _aio_tasks
import gzip
import html as html_lib
import json
import os

# Fix pentru bug-ul C _CTask din Python 3.12.2 pe Windows la aruncarea exceptiilor in corutine suspendate
_aio_tasks.Task = _aio_tasks._PyTask
asyncio.Task = _aio_tasks._PyTask
_aio_tasks.current_task = _aio_tasks._py_current_task
asyncio.current_task = _aio_tasks._py_current_task
_aio_tasks._enter_task = _aio_tasks._py_enter_task
_aio_tasks._leave_task = _aio_tasks._py_leave_task
_aio_tasks._register_task = _aio_tasks._py_register_task
_aio_tasks._unregister_task = _aio_tasks._py_unregister_task
_aio_tasks._register_eager_task = _aio_tasks._py_register_eager_task
_aio_tasks._unregister_eager_task = _aio_tasks._py_unregister_eager_task
_aio_tasks._swap_current_task = _aio_tasks._py_swap_current_task

import random
import re
import string
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, quote_plus, urlsplit, urlunsplit, parse_qsl, urlencode

_AFFILIATE_PARAM_BLOCKLIST = {"tag", "associatetag", "linkcode", "ascsubtag", "linkid", "camp", "creative"}


def sanitize_outbound_scrape_url(raw_url: str) -> str:
    """Garanteaza ca niciun scraper sau auditor nu acceseaza URL-uri Amazon cu ?tag=vasiledev... sau /api/v1/go-offer."""
    if not raw_url:
        return raw_url
    parsed = urlsplit(raw_url)
    if "/api/v1/go-offer" in parsed.path:
        raise ValueError(f"Acces blocat catre redirectul intern de afiliere: {raw_url}")
    host_l = parsed.netloc.lower()
    if "amazon." in host_l or "amzn." in host_l:
        clean_q = [
            (k, v)
            for k, v in parse_qsl(parsed.query, keep_blank_values=True)
            if k.lower() not in _AFFILIATE_PARAM_BLOCKLIST and not str(v).lower().startswith("vasiledev")
        ]
        clean_path = re.sub(r"/ref=[^/?#]+", "", parsed.path)
        return urlunsplit((parsed.scheme, parsed.netloc, clean_path, urlencode(clean_q), ""))
    return raw_url

import httpx
from dotenv import load_dotenv
from playwright.async_api import BrowserContext, Route
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from sku_matcher import match_official_sku, parse_ron_price, parse_stock_status

load_dotenv()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.0 Safari/605.1.15",
]

BLOCKED_RESOURCE_TYPES = {"image", "media", "font", "stylesheet", "other"}

BLOCKED_TRACKING_DOMAINS = (
    "google-analytics.com",
    "googletagmanager.com",
    "doubleclick.net",
    "facebook.net",
    "facebook.com/tr",
    "connect.facebook",
    "hotjar.com",
    "tiktok.com",
    "analytics.tiktok.com",
    "clarity.ms",
    "tawk.to",
    "livechatinc.com",
    "smartlook.com",
    "criteo.com",
    "criteo.net",
    "profitshare.ro",
    "2performant.com",
    "youtube.com",
    "ytimg.com",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
)


def get_valid_proxy_url() -> Optional[str]:
    """Returneaza URL-ul de proxy din .env doar daca este configurat real (nu placeholder-ul din .env.example)."""
    raw = os.getenv("PROXY_URL", "").strip().strip('"').strip("'")
    if not raw or "user:pass@proxy-host:port" in raw:
        return None
    return raw


def get_rotated_proxy_url(base_proxy_url: Optional[str] = None) -> Optional[str]:
    """
    Inlocuieste dinamic sufixul `session_<id>` (ex: `session_z6jhcw9fsp`) din PROXY_URL
    cu un string alfanumeric random de 10 caractere (`session_<random10>`), fortand
    instantaneu un IP rezidential nou de Romania fara a astepta expirarea celor 5 minute.
    """
    raw = base_proxy_url or get_valid_proxy_url()
    if not raw:
        return None
    rand10 = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    if re.search(r"session_[a-zA-Z0-9]+", raw):
        return re.sub(r"session_[a-zA-Z0-9]+", f"session_{rand10}", raw)
    return raw


def test_proxy_ipinfo(proxy_url: Optional[str] = None) -> Dict[str, Any]:
    """
    Verifica conexiunea prin PROXY_URL interogand https://ipinfo.io/json
    si returneaza IP-ul rezidential de Romania, orasul si ISP-ul (org).
    """
    target_proxy = proxy_url or get_valid_proxy_url()
    if not target_proxy:
        return {"ok": False, "error": "PROXY_URL neconfigurat"}
    try:
        with httpx.Client(proxy=target_proxy, timeout=15.0, verify=False) as client:
            resp = client.get("https://ipinfo.io/json")
            if resp.status_code == 200:
                data = resp.json()
                data["ok"] = True
                data["proxy_session"] = (
                    re.search(r"(session_[a-zA-Z0-9]+)", target_proxy).group(1)
                    if re.search(r"(session_[a-zA-Z0-9]+)", target_proxy)
                    else "default"
                )
                return data
            return {"ok": False, "status_code": resp.status_code}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


class BandwidthTracker:
    """Contorizeaza traficul consumat per domeniu (total vs. prin proxy) pentru protejarea bugetului de 10 GB."""

    def __init__(self) -> None:
        self.bytes_per_domain: Dict[str, int] = {}
        self.proxy_bytes_per_domain: Dict[str, int] = {}
        self.requests_per_domain: Dict[str, int] = {}
        self.proxy_requests_per_domain: Dict[str, int] = {}
        self.blocked_requests_count: int = 0
        self.proxy_rotations_count: int = 0

    def record(self, domain: str, n_bytes: int, used_proxy: bool = False) -> None:
        self.bytes_per_domain[domain] = self.bytes_per_domain.get(domain, 0) + n_bytes
        self.requests_per_domain[domain] = self.requests_per_domain.get(domain, 0) + 1
        if used_proxy:
            self.proxy_bytes_per_domain[domain] = self.proxy_bytes_per_domain.get(domain, 0) + n_bytes
            self.proxy_requests_per_domain[domain] = self.proxy_requests_per_domain.get(domain, 0) + 1

    def summary(self) -> Dict[str, Any]:
        total_bytes = sum(self.bytes_per_domain.values())
        proxy_bytes = sum(self.proxy_bytes_per_domain.values())
        total_reqs = sum(self.requests_per_domain.values())
        proxy_reqs = sum(self.proxy_requests_per_domain.values())
        avg_kb = (total_bytes / 1024.0 / total_reqs) if total_reqs else 0.0
        return {
            "total_kb": round(total_bytes / 1024.0, 2),
            "total_mb": round(total_bytes / (1024.0 * 1024.0), 3),
            "proxy_kb": round(proxy_bytes / 1024.0, 2),
            "proxy_mb": round(proxy_bytes / (1024.0 * 1024.0), 3),
            "total_requests": total_reqs,
            "proxy_requests": proxy_reqs,
            "proxy_rotations": self.proxy_rotations_count,
            "avg_kb_per_page": round(avg_kb, 2),
            "blocked_requests": self.blocked_requests_count,
            "per_domain_kb": {
                k: round(v / 1024.0, 2) for k, v in self.bytes_per_domain.items()
            },
        }


class RadarScraperEngine:
    def __init__(self, config_path: str | Path = "niche_config.json") -> None:
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.proxy_url = get_valid_proxy_url()
        self.use_proxy_for_emag = os.getenv("USE_PROXY_FOR_EMAG", "true").lower() == "true"
        self.use_proxy_for_stores = os.getenv("USE_PROXY_FOR_STORES", "false").lower() == "true"
        self.min_delay = float(os.getenv("MIN_DELAY_SEC", "0.4"))
        self.max_delay = float(os.getenv("MAX_DELAY_SEC", "1.0"))
        self.timeout_sec = float(os.getenv("REQUEST_TIMEOUT_SEC", "20.0"))
        self.bandwidth = BandwidthTracker()
        self._last_domain_hit: Dict[str, float] = {}

    def rotate_proxy_session(self) -> Optional[str]:
        """Roteste sesiunea proxy (`session_<random10>`) si actualizeaza self.proxy_url."""
        if not self.proxy_url:
            return None
        self.proxy_url = get_rotated_proxy_url(self.proxy_url)
        self.bandwidth.proxy_rotations_count += 1
        return self.proxy_url

    async def polite_pause(self, domain: str) -> None:
        """Respecta pauza politicoasa intre cereri pe acelasi domeniu."""
        now = asyncio.get_event_loop().time()
        last = self._last_domain_hit.get(domain)
        if last is not None:
            delay = random.uniform(self.min_delay, self.max_delay)
            elapsed = now - last
            if elapsed < delay:
                await asyncio.sleep(delay - elapsed)
        self._last_domain_hit[domain] = asyncio.get_event_loop().time()

    async def _intercept_playwright_route(self, route: Route) -> None:
        """
        Interceptor obligatoriu de ruta Playwright:
        Blocheaza complet image, media, font, stylesheet si scripturile de analytics/tracking
        pentru a mentine consumul sub 50-80 KB per pagina!
        """
        req = route.request
        url_low = req.url.lower()

        if req.resource_type in BLOCKED_RESOURCE_TYPES:
            self.bandwidth.blocked_requests_count += 1
            await route.abort()
            return

        if any(pat in url_low for pat in BLOCKED_TRACKING_DOMAINS):
            self.bandwidth.blocked_requests_count += 1
            await route.abort()
            return

        if url_low.endswith((".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".woff", ".woff2", ".ttf", ".css", ".mp4")):
            self.bandwidth.blocked_requests_count += 1
            await route.abort()
            return

        await route.continue_()

    @staticmethod
    def _is_captcha_or_block_page(text: str, status_code: int) -> bool:
        """Detecteaza daca raspunsul HTTP este blocat (403/429/511) sau contine pagina de Captcha."""
        if status_code in (403, 429, 503, 511):
            return True
        if not text:
            return True
        low = text[:4000].lower()
        if any(
            m in low
            for m in (
                "cf-browser-verification",
                "g-recaptcha",
                "rc-anchor",
                "geetest",
                "datadome",
                "challenge-running",
                "introduceti codul din imagine",
                "verifica daca esti om",
            )
        ) and len(text) < 25000:
            return True
        return False

    async def fetch_html_smart(
        self,
        url: str,
        domain: str,
        pw_context: Optional[BrowserContext] = None,
        force_proxy: bool = False,
        retry_count: int = 0,
    ) -> Tuple[str, int, Dict[str, str], bool]:
        """
        Incearca mai intai extragere ultra-usoara prin httpx (doar documentul HTML/JSON comprimat gzip).
        Daca primeste 403/429/511 sau provocare Captcha:
        - Pentru magazine (USE_PROXY_FOR_STORES=false): activeaza automat proxy-ul cu o sesiune rotita (`session_<random10>`)
        - Pentru eMAG (USE_PROXY_FOR_EMAG=true): roteste sesiunea proxy (`get_rotated_proxy_url()`) si reincearca instant!
        Returneaza: (body_text, status_code, headers_dict, used_proxy)
        """
        await self.polite_pause(domain)

        use_proxy = force_proxy or (self.use_proxy_for_emag if "emag.ro" in domain else self.use_proxy_for_stores)
        active_proxy = self.proxy_url if (use_proxy and self.proxy_url) else None

        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/json,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }

        try:
            def _do_sync_get() -> httpx.Response:
                with httpx.Client(
                    proxy=active_proxy,
                    timeout=self.timeout_sec,
                    follow_redirects=True,
                    verify=False,
                ) as client:
                    return client.get(url, headers=headers)

            resp = await asyncio.to_thread(_do_sync_get)
            text = resp.text or ""
            wire_bytes = len(gzip.compress((resp.content or b""), compresslevel=6)) if resp.content else 0
            self.bandwidth.record(domain, wire_bytes, used_proxy=bool(active_proxy))
            hdrs = {k.lower(): v for k, v in resp.headers.items()}

            if self._is_captcha_or_block_page(text, resp.status_code) and self.proxy_url and retry_count < 2:
                # Rotim instantaneu sesiunea proxy (session_<random10>) si reincercam prin noul IP de Romania
                self.rotate_proxy_session()
                return await self.fetch_html_smart(
                    url, domain, pw_context=pw_context, force_proxy=True, retry_count=retry_count + 1
                )

            if resp.status_code == 200 and len(text) > 50 and not self._is_captcha_or_block_page(text, resp.status_code):
                return text, resp.status_code, hdrs, bool(active_proxy)
        except Exception:
            if self.proxy_url and retry_count < 1:
                self.rotate_proxy_session()
                return await self.fetch_html_smart(
                    url, domain, pw_context=pw_context, force_proxy=True, retry_count=retry_count + 1
                )

        if pw_context is not None:
            return await self.fetch_with_playwright_interceptor(url, domain, pw_context, bool(active_proxy))

        return "", 0, {}, bool(active_proxy)

    async def fetch_with_playwright_interceptor(
        self,
        url: str,
        domain: str,
        pw_context: BrowserContext,
        used_proxy: bool = False,
    ) -> Tuple[str, int, Dict[str, str], bool]:
        """
        Descarca pagina folosind Playwright cu interceptorul strict `page.route("**/*", ...)`
        care blocheaza image, media, font, stylesheet si scripturile de tracking.
        """
        page = await pw_context.new_page()
        await page.route("**/*", self._intercept_playwright_route)
        try:
            resp = await page.goto(url, wait_until="domcontentloaded", timeout=int(self.timeout_sec * 1000))
            status = resp.status if resp else 0
            html = await page.content()
            raw_utf8 = html.encode("utf-8", errors="ignore")
            wire_bytes = len(gzip.compress(raw_utf8, compresslevel=6)) if raw_utf8 else 1024
            self.bandwidth.record(domain, wire_bytes, used_proxy=used_proxy)
            hdrs = (await resp.all_headers()) if resp else {}
            await page.close()
            return html, status, hdrs, used_proxy
        except Exception:
            await page.close()
            return "", 0, {}, used_proxy

    # =========================================================================
    # 1. PARSARE WOOCOMMERCE STORE API JSON (/wp-json/wc/store/v1/products)
    # =========================================================================
    def parse_products_from_wc_json(
        self,
        json_text: str,
        store_domain: str,
        base_url: str,
    ) -> List[Dict[str, Any]]:
        """Extrage produse reale din endpoint-ul JSON oficial WooCommerce Store API."""
        if not json_text or not json_text.strip().startswith("["):
            return []

        found_by_sku: Dict[str, Dict[str, Any]] = {}
        try:
            items = json.loads(json_text)
        except Exception:
            return []

        if not isinstance(items, list):
            return []

        for item in items:
            if not isinstance(item, dict):
                continue
            raw_title = html_lib.unescape(str(item.get("name", "")).strip())
            internal_sku = html_lib.unescape(str(item.get("sku", "")).strip())
            prod_url = str(item.get("permalink") or "").strip()
            if not raw_title or not prod_url or not prod_url.startswith("http"):
                continue

            prices_obj = item.get("prices", {}) or {}
            try:
                minor_unit = int(prices_obj.get("currency_minor_unit", 2))
            except Exception:
                minor_unit = 2

            divisor = float(10 ** minor_unit) if minor_unit >= 0 else 1.0
            try:
                price_val = round(float(prices_obj.get("price", 0) or 0) / divisor, 2)
            except Exception:
                price_val = 0.0

            try:
                reg_val = round(float(prices_obj.get("regular_price", 0) or 0) / divisor, 2)
            except Exception:
                reg_val = None

            old_price_val = reg_val if (reg_val and reg_val > price_val) else None

            if price_val <= 100:
                continue

            match = match_official_sku(raw_title, internal_sku, price_val)
            if not match:
                continue

            in_stock = bool(item.get("is_in_stock", True))
            stock_lbl = "În stoc" if in_stock else "Stoc Epuizat"

            existing = found_by_sku.get(match.normalized_sku)
            # Pastram produsul in stoc sau cu pretul cel mai reprezentativ
            if existing is None or (in_stock and not existing["in_stock"]):
                found_by_sku[match.normalized_sku] = {
                    "store_domain": store_domain,
                    "normalized_sku": match.normalized_sku,
                    "brand": match.brand,
                    "category": match.category,
                    "raw_title": raw_title,
                    "store_internal_sku": internal_sku or f"WC-{store_domain.split('.')[0].upper()}-{match.normalized_sku}",
                    "current_price_ron": price_val,
                    "old_price_ron": old_price_val,
                    "in_stock": in_stock,
                    "stock_label": stock_lbl,
                    "product_url": prod_url,
                }

        return list(found_by_sku.values())

    # =========================================================================
    # 2. PARSARE MULTI-PLATFORMA DIN HTML (JSON-LD + GOMAG + CS-CART + WC)
    # =========================================================================
    def parse_products_from_html(
        self,
        html: str,
        store_domain: str,
        base_url: str,
    ) -> List[Dict[str, Any]]:
        """
        Extrage produsele fotovoltaice din HTML folosind:
        1) Schema.org JSON-LD (Product / ItemList)
        2) Selectoare specifice CS-Cart (form[name^='product_form_'], .ut2-gl__item, .ty-column3)
        3) Selectoare specifice Gomag (div.product-box), WooCommerce, MerchantPro, PrestaShop
        """
        if not html:
            return []

        if html.strip().startswith("["):
            return self.parse_products_from_wc_json(html, store_domain, base_url)

        found_by_sku: Dict[str, Dict[str, Any]] = {}
        tree = HTMLParser(html)

        # 1. Extragere din JSON-LD Schema.org
        for script_node in tree.css('script[type="application/ld+json"]'):
            raw_json = script_node.text(strip=True)
            if not raw_json:
                continue
            try:
                data = json.loads(raw_json)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    graph = item.get("@graph", [item])
                    for g in (graph if isinstance(graph, list) else [graph]):
                        if not isinstance(g, dict):
                            continue
                        g_type = str(g.get("@type", "")).lower()
                        if "product" in g_type:
                            title = str(g.get("name", "")).strip()
                            sku_internal = str(g.get("sku") or g.get("mpn") or "").strip()
                            offers = g.get("offers", {})
                            if isinstance(offers, list) and offers:
                                offers = offers[0]
                            if isinstance(offers, dict):
                                price_val = parse_ron_price(str(offers.get("price", "")))
                                avail = str(offers.get("availability", ""))
                                url_val = str(offers.get("url") or g.get("url") or "")
                                if not url_val:
                                    continue
                                in_stock, stock_lbl = parse_stock_status(avail)
                                match = match_official_sku(title, sku_internal, price_val)
                                if match and price_val:
                                    found_by_sku[match.normalized_sku] = {
                                        "store_domain": store_domain,
                                        "normalized_sku": match.normalized_sku,
                                        "brand": match.brand,
                                        "category": match.category,
                                        "raw_title": title,
                                        "store_internal_sku": sku_internal or f"{store_domain.split('.')[0].upper()}-{match.normalized_sku}",
                                        "current_price_ron": price_val,
                                        "old_price_ron": None,
                                        "in_stock": in_stock,
                                        "stock_label": stock_lbl,
                                        "product_url": urljoin(base_url, url_val),
                                    }
            except Exception:
                continue

        # 2. Extragere din cardurile HTML (CS-Cart, Gomag, WooCommerce, MerchantPro, PrestaShop)
        card_selectors = [
            "form[name^='product_form_']",
            "div.ut2-gl__item",
            "div.ty-column3",
            "div.product-box",
            "li.product",
            "div.product-item",
            "div.product-card",
            "article.product-miniature",
            "div.product-thumb",
            "div.item-product",
            "div.cp-item",
        ]

        cards = []
        for sel in card_selectors:
            matched_nodes = tree.css(sel)
            if matched_nodes:
                cards.extend(matched_nodes)

        for card in cards:
            card_html = card.html or ""
            card_text = card.text(separator=" ", strip=True)
            if len(card_text) < 15:
                continue

            title_text = ""
            prod_url = ""
            for t_sel in [
                "a.product-title",
                "h2.woocommerce-loop-product__title",
                "h3.product-title a",
                "h2.product-title a",
                ".product-item-link",
                ".product-name a",
                ".title a",
                "h2 a",
                "h3 a",
                "a[title]",
            ]:
                node = card.css_first(t_sel)
                if node:
                    title_text = node.attributes.get("title") or node.text(strip=True)
                    href = node.attributes.get("href", "")
                    if href and not href.startswith("javascript"):
                        prod_url = urljoin(base_url, href)
                    if len(title_text) >= 8 and prod_url:
                        break

            if not title_text or not prod_url:
                continue

            price_val: Optional[float] = None
            old_price_val: Optional[float] = None

            ins_node = card.css_first(
                "[id^='sec_discounted_price_'], .ty-price-num, ins .amount, .special-price .price, .product-new-price, .price-new"
            )
            del_node = card.css_first(
                "[id^='sec_list_price_'], .ty-list-price, del .amount, .old-price .price, .product-old-price, .price-old"
            )
            if ins_node:
                price_val = parse_ron_price(ins_node.text(strip=True))
            if del_node:
                old_price_val = parse_ron_price(del_node.text(strip=True))
                if old_price_val and price_val and old_price_val <= price_val:
                    old_price_val = None

            if not price_val:
                for p_sel in [
                    ".price",
                    ".product-price",
                    ".amount",
                    "[data-price]",
                    ".current-price",
                ]:
                    p_node = card.css_first(p_sel)
                    if p_node:
                        raw_p = p_node.attributes.get("data-price") or p_node.text(strip=True)
                        price_val = parse_ron_price(raw_p)
                        if price_val:
                            break

            if not price_val:
                continue

            internal_sku = (
                card.attributes.get("data-product-id")
                or card.attributes.get("data-id")
                or ""
            )
            if not internal_sku:
                sku_node = card.css_first("[id^='product_code_'], .ty-control-group__item, [data-product_sku], [data-product_id]")
                if sku_node:
                    internal_sku = (
                        sku_node.attributes.get("data-product_sku")
                        or sku_node.attributes.get("data-product_id")
                        or sku_node.text(strip=True)
                        or ""
                    )

            match = match_official_sku(title_text, internal_sku, price_val)
            if not match:
                continue

            in_stock, stock_lbl = parse_stock_status(card_text, card_html)
            existing = found_by_sku.get(match.normalized_sku)
            if existing is None or (in_stock and not existing["in_stock"]):
                found_by_sku[match.normalized_sku] = {
                    "store_domain": store_domain,
                    "normalized_sku": match.normalized_sku,
                    "brand": match.brand,
                    "category": match.category,
                    "raw_title": title_text,
                    "store_internal_sku": internal_sku[:32] if internal_sku else f"{store_domain.split('.')[0].upper()}-{match.normalized_sku}",
                    "current_price_ron": price_val,
                    "old_price_ron": old_price_val,
                    "in_stock": in_stock,
                    "stock_label": stock_lbl,
                    "product_url": prod_url,
                }

        return list(found_by_sku.values())

    # =========================================================================
    # 3. SCRAPING LIVE INTEGRAL PE CATALOGUL CELOR 10 MAGAZINE
    # =========================================================================
    async def scrape_store_live_catalog(
        self,
        store_cfg: Dict[str, Any],
        pw_context: Optional[BrowserContext] = None,
    ) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, str]]:
        """
        Descarca si parseaza 100% LIVE catalogul magazinului (categorii + cautari dupa brand/model)
        si paginile de contact/termeni pentru extragerea B2B.
        Returneaza: (products_list, html_pages_for_b2b, last_headers)
        """
        domain = store_cfg["domain"]
        base_url = store_cfg["base_url"]
        search_tpl = store_cfg.get("search_url_template", "")
        cat_urls = store_cfg.get("category_urls", [])
        queries = self.config.get("search_queries", [])

        found_by_sku: Dict[str, Dict[str, Any]] = {}
        b2b_html_pages: List[str] = []
        last_headers: Dict[str, str] = {}

        # 1. Homepage + Pagini de Contact pentru detectie platforma si date B2B (SRL, CUI, Email, Telefon)
        home_html, home_status, home_hdrs, _ = await self.fetch_html_smart(base_url, domain, pw_context=pw_context)
        if home_html:
            b2b_html_pages.append(home_html)
            last_headers = home_hdrs

        for c_path in store_cfg.get("contact_paths", ["/contact"])[:2]:
            c_url = urljoin(base_url, c_path)
            c_html, c_status, _, _ = await self.fetch_html_smart(c_url, domain, pw_context=pw_context)
            if c_html and c_status == 200:
                b2b_html_pages.append(c_html)

        # 2. Scanam URL-urile de categorii configurate
        for cat_url in cat_urls:
            body, status, _, _ = await self.fetch_html_smart(cat_url, domain, pw_context=pw_context)
            if status == 200 and body:
                items = self.parse_products_from_html(body, domain, base_url)
                for it in items:
                    sku = it["normalized_sku"]
                    if sku not in found_by_sku or (it["in_stock"] and not found_by_sku[sku]["in_stock"]):
                        found_by_sku[sku] = it

        # 3. Scanam cautarile live dupa brandurile/modelele tinta
        if search_tpl:
            for q in queries:
                s_url = search_tpl.replace("{query}", quote_plus(q))
                body, status, _, _ = await self.fetch_html_smart(s_url, domain, pw_context=pw_context)
                if status == 200 and body:
                    items = self.parse_products_from_html(body, domain, base_url)
                    for it in items:
                        sku = it["normalized_sku"]
                        if sku not in found_by_sku or (it["in_stock"] and not found_by_sku[sku]["in_stock"]):
                            found_by_sku[sku] = it

        return list(found_by_sku.values()), b2b_html_pages, last_headers

    # =========================================================================
    # 4. SCRAPING LIVE BENCHMARK eMAG MARKETPLACE (DOAR PE CODURILE SKU EXTRASE)
    # =========================================================================
    async def scrape_emag_benchmark_live(
        self,
        skus_list: List[str],
        pw_context: Optional[BrowserContext] = None,
    ) -> List[Dict[str, Any]]:
        """
        Interogheaza LIVE https://www.emag.ro/search/{sku} pentru codurile SKU extrase din magazine.
        Parseaza cardurile `.card-v2` si JSON-ul `button[data-product]` pentru a extrage
        pretul Buy-Box real, numarul de oferte active si URL-ul exact al produsului pe eMAG.
        """
        emag_cfg = self.config.get("benchmark", {})
        search_tpl = emag_cfg.get("search_url_template", "https://www.emag.ro/search/{query}")
        max_reqs = int(emag_cfg.get("max_requests_per_run", 40))

        benchmarks: List[Dict[str, Any]] = []

        for sku in skus_list[:max_reqs]:
            s_url = search_tpl.replace("{query}", quote_plus(sku))
            html, status, _, _ = await self.fetch_html_smart(s_url, "emag.ro", pw_context=pw_context)
            if status != 200 or not html:
                continue

            tree = HTMLParser(html)
            matching_offers: List[Tuple[float, str, str]] = []  # (price_ron, pnk, product_url)

            for card in tree.css(".card-v2"):
                btn = card.css_first("button[data-product]")
                link_node = card.css_first("a.js-product-url, .card-v2-title")
                href = link_node.attributes.get("href", "") if link_node else ""

                title = ""
                price_val: Optional[float] = None
                pnk = ""

                if btn and btn.attributes.get("data-product"):
                    try:
                        p_data = json.loads(html_lib.unescape(btn.attributes["data-product"]))
                        title = str(p_data.get("product_name", "")).strip()
                        price_val = float(p_data.get("price", 0) or 0)
                        pnk = str(p_data.get("pnk", "")).strip()
                    except Exception:
                        pass

                if not title and link_node:
                    title = link_node.text(strip=True) or link_node.attributes.get("title", "")

                if not price_val:
                    p_node = card.css_first(".product-new-price")
                    if p_node:
                        price_val = parse_ron_price(p_node.text(strip=True))

                if not title or not price_val:
                    continue

                m = match_official_sku(title, pnk, price_val)
                if m and m.normalized_sku == sku:
                    full_url = urljoin("https://www.emag.ro", href) if href else s_url
                    matching_offers.append((round(price_val, 2), pnk or "EMAG", full_url))

            if matching_offers:
                matching_offers.sort(key=lambda x: x[0])
                best_price, best_pnk, best_url = matching_offers[0]
                seller_name = f"eMAG Marketplace (PNK {best_pnk})"

                # Extragem si numele exact al sellerului din pagina de produs Buy-Box prin proxy-ul rezidential RO
                if "/pd/" in best_url:
                    p_html, p_status, _, _ = await self.fetch_html_smart(best_url, "emag.ro", pw_context=pw_context)
                    if p_status == 200 and p_html:
                        p_tree = HTMLParser(p_html)
                        v_node = p_tree.css_first("a[href*='see_vendor_page']")
                        if v_node and v_node.text(strip=True):
                            seller_name = v_node.text(strip=True)
                        elif "Vândut și livrat de: eMAG" in p_html or "Vandut si livrat de: eMAG" in p_html:
                            seller_name = "eMAG"

                benchmarks.append({
                    "normalized_sku": sku,
                    "emag_lowest_price_ron": best_price,
                    "emag_seller": seller_name,
                    "emag_offers_count": len(matching_offers),
                    "emag_url": best_url,
                })

        return benchmarks
