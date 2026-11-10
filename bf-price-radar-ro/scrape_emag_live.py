"""
scrape_emag_live.py
Scraper 100% LIVE pentru eMAG Marketplace folosind proxy-ul rezidential de Romania (`PROXY_URL` din `.env`)
cu rotire automata de sesiune (`session_<random10>`) la orice HTTP 403/429/511 sau Captcha.

REGULA STRICTA:
- INTERZIS orice fallback matematic (`minim * 0.99`) sau text generic `"eMAG Marketplace Seller"`.
- Extrage exclusiv din DOM-ul real eMAG:
  * `emag_real_price_ron` (din `button[data-product]` / `.product-new-price`)
  * `emag_real_seller` (din `a[href*='see_vendor_page']` / `"Vândut și livrat de: eMAG"` / `"Vandut pe eMAG"` daca e doar din cautare)
  * `emag_product_url` (`https://www.emag.ro/.../pd/...`)
- Daca un SKU nu este gasit pe eMAG, salveaza `NULL` (`None`) si `"Nelistat pe eMAG"`.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
import shutil
import sqlite3
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote_plus, unquote

import httpx
from dotenv import load_dotenv
from selectolax.lexbor import LexborHTMLParser as HTMLParser

from db import RadarDatabase
from generate_mirrors import generate_all_mirrors
from generate_outreach import generate_all_outreach
from scraper_engine import get_rotated_proxy_url
from sku_matcher import match_official_sku

load_dotenv(override=True)

RO_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8,en;q=0.7",
}

BROAD_EMAG_QUERIES = [
    "Invertor Deye",
    "Acumulator Deye",
    "Invertor Huawei SUN2000",
    "Acumulator Huawei LUNA2000",
    "Invertor Fronius Symo",
    "Invertor Fronius Primo",
    "Victron MultiPlus",
    "Victron SmartSolar MPPT",
    "Victron Quattro",
    "Victron Cerbo GX",
    "Acumulator Pylontech",
    "Invertor Growatt",
    "Acumulator Growatt",
    "Acumulator V-Tac",
    "Invertor Solis",
    "Fronius Smart Meter",
    "Huawei Smart Power Sensor",
]


def _parse_romanian_price(text: str) -> Optional[float]:
    if not text:
        return None
    cleaned = re.sub(r"(?i)(lei|ron|tva|inclus|\s)", "", text)
    m = re.search(r"(\d{1,3}(?:[\.\s]\d{3})+(?:,\d{1,2})?|\d+(?:[.,]\d{1,2})?)", cleaned)
    if not m:
        return None
    token = m.group(1)
    if "." in token and "," in token:
        token = token.replace(".", "").replace(",", ".")
    elif "." in token:
        parts = token.split(".")
        if len(parts[-1]) == 3:
            token = token.replace(".", "")
    elif "," in token:
        token = token.replace(",", ".")
    try:
        val = float(token)
        return round(val, 2) if val > 100 else None
    except ValueError:
        return None


def _parse_emag_cards_from_html(html: str) -> List[Dict[str, Any]]:
    """Extrage toate cardurile de produs reale din HTML-ul paginii de cautare eMAG."""
    tree = HTMLParser(html)
    cards = tree.css(".card-item, .card-v2")
    results: List[Dict[str, Any]] = []
    for card in cards:
        pd_link = card.css_first('a[href*="/pd/"]')
        if not pd_link:
            continue
        href = pd_link.attributes.get("href", "")
        if not href:
            continue
        if href.startswith("/"):
            href = f"https://www.emag.ro{href}"
        href = href.split("?")[0]
        if not href.startswith("https://www.emag.ro/") or "/pd/" not in href:
            continue

        title = ""
        price_val: Optional[float] = None

        btn = card.css_first("button[data-product]")
        if btn and "data-product" in btn.attributes:
            try:
                pdata = json.loads(btn.attributes["data-product"])
                title = str(pdata.get("product_name") or "").strip()
                raw_p = pdata.get("price")
                if raw_p is not None:
                    price_val = round(float(raw_p), 2)
            except Exception:
                pass

        if not title:
            title_node = card.css_first(".card-v2-title, a.card-v2-title, h2 a")
            title = (
                title_node.text(strip=True)
                if title_node
                else (pd_link.attributes.get("title") or pd_link.text(strip=True))
            )

        if not price_val:
            p_node = card.css_first(".product-new-price")
            if p_node:
                price_val = _parse_romanian_price(p_node.text(strip=True))

        if not title or not price_val or price_val <= 150:
            continue

        # Extragem eventualul seller vizibil direct pe card
        seller_hint = None
        card_text = card.text(separator=" ", strip=True)
        m_v = re.search(r"Livrat de\s+([A-Za-z0-9\s\.\-\_&]+?)(?:\s+În stoc|\s+In stoc|\s+Ultimele|\s+\d|$)", card_text)
        if m_v:
            seller_hint = m_v.group(1).strip()

        norm = match_official_sku(title, price_val)
        results.append(
            {
                "normalized_sku": norm.normalized_sku if norm else None,
                "brand": norm.brand if norm else None,
                "title": title,
                "price_ron": price_val,
                "url": href,
                "seller_hint": seller_hint,
            }
        )
    return results


async def fetch_emag_url_with_rotation(
    url: str,
    base_proxy_url: str,
    max_retries: int = 3,
) -> Optional[str]:
    """
    Descarca o pagina de pe emag.ro prin proxy-ul rezidential RO.
    Daca primeste 403/429/511 sau Captcha, roteste instantaneu `session_<random10>` si reincearca.
    """
    current_proxy = base_proxy_url
    for attempt in range(1, max_retries + 1):
        try:
            async with httpx.AsyncClient(
                proxy=current_proxy,
                headers=RO_HEADERS,
                follow_redirects=True,
                timeout=18.0,
            ) as client:
                resp = await client.get(url)
                html = resp.text
                is_captcha = (
                    resp.status_code in (403, 429, 511)
                    or "captcha" in str(resp.url).lower()
                    or ("g-recaptcha" in html.lower() and ".card-v2" not in html and "product-new-price" not in html)
                )
                if not is_captcha and resp.status_code == 200 and len(html) > 5000:
                    return html
                # Rotim sesiunea de proxy pentru un IP nou de Romania
                current_proxy = get_rotated_proxy_url(base_proxy_url)
                await asyncio.sleep(0.4 * attempt)
        except Exception:
            current_proxy = get_rotated_proxy_url(base_proxy_url)
            await asyncio.sleep(0.4 * attempt)
    return None


async def search_duckduckgo_emag_fallback(
    sku: str,
    brand: str,
    base_proxy_url: str,
) -> List[str]:
    """
    Fallback Pasul A: cauta pe DuckDuckGo HTML `site:emag.ro "{sku}"` pentru a gasi URL-uri `/pd/` directe.
    """
    clean_q = re.sub(r"[/\\]+", " ", f'site:emag.ro "{sku}" {brand}')
    ddg_url = f"https://html.duckduckgo.com/html/?q={quote_plus(clean_q)}"
    proxy_to_use = get_rotated_proxy_url(base_proxy_url)
    found_urls: List[str] = []
    try:
        async with httpx.AsyncClient(
            proxy=proxy_to_use,
            headers=RO_HEADERS,
            follow_redirects=True,
            timeout=15.0,
        ) as client:
            resp = await client.get(ddg_url)
            if resp.status_code == 200:
                raw_links = re.findall(r"(https?://(?:www\.)?emag\.ro/[^\s\"'<>]+/pd/[A-Za-z0-9]+/?)", unquote(resp.text))
                for u in raw_links:
                    clean_u = u.split("?")[0].split("&")[0]
                    if not clean_u.endswith("/"):
                        clean_u += "/"
                    if clean_u not in found_urls:
                        found_urls.append(clean_u)
    except Exception:
        pass
    return found_urls[:2]


async def extract_emag_product_page_details(
    pd_url: str,
    fallback_price: Optional[float],
    fallback_seller: Optional[str],
    base_proxy_url: str,
) -> Tuple[Optional[float], str, int]:
    """
    Pasul B: Descarca pagina de produs eMAG (`https://www.emag.ro/.../pd/...`) prin proxy-ul rezidential RO
    cu rotire de sesiune si extrage din DOM-ul real:
      - `emag_real_price_ron`
      - `emag_real_seller` (din `a[href*='see_vendor_page']` / `"Vândut și livrat de: eMAG"`)
      - `emag_offers_count`
    """
    html = await fetch_emag_url_with_rotation(pd_url, base_proxy_url, max_retries=3)
    if not html:
        return fallback_price, (fallback_seller or "Vandut pe eMAG"), 1

    tree = HTMLParser(html)

    # 1. Pretul real din DOM
    real_price = fallback_price
    btn = tree.css_first("button[data-product]")
    if btn and "data-product" in btn.attributes:
        try:
            pdata = json.loads(btn.attributes["data-product"])
            if pdata.get("price"):
                real_price = round(float(pdata["price"]), 2)
        except Exception:
            pass
    if not real_price:
        p_node = tree.css_first(".product-new-price")
        if p_node:
            parsed_p = _parse_romanian_price(p_node.text(strip=True))
            if parsed_p:
                real_price = parsed_p

    # 2. Sellerul real din DOM (`a[href*='see_vendor_page']` sau eMAG direct)
    real_seller = None
    vendor_node = tree.css_first("a[href*='see_vendor_page']")
    if vendor_node:
        v_txt = vendor_node.text(strip=True)
        if v_txt:
            real_seller = v_txt

    if not real_seller:
        if re.search(r"V[aâ]ndut\s+[sș]i\s+livrat\s+de:\s*eMAG", html, re.I):
            real_seller = "eMAG"
        else:
            m_sell = re.search(
                r"V[aâ]ndut\s+[sș]i\s+livrat\s+de:?\s*(?:<[^>]+>\s*)*([A-Za-z0-9\s\.\-\_&]{2,40})",
                html,
                re.I,
            )
            if m_sell:
                cand = m_sell.group(1).strip()
                if cand and cand.lower() not in ("emag", "vezi", "detalii", "span", "div"):
                    real_seller = cand

    if not real_seller:
        real_seller = fallback_seller or "Vandut pe eMAG"

    # 3. Numarul real de oferte
    offers_count = 1
    m_off = re.search(r"(\d+)\s+oferte\s+disponibile|alte\s+(\d+)\s+oferte", html, re.I)
    if m_off:
        num_str = m_off.group(1) or m_off.group(2)
        if num_str:
            val = int(num_str)
            offers_count = val if m_off.group(1) else (val + 1)

    return real_price, real_seller, offers_count


async def run_live_emag_scrape() -> None:
    base_proxy_url = os.getenv("PROXY_URL", "").strip()
    if not base_proxy_url:
        raise RuntimeError("PROXY_URL nu este setat in .env!")

    db = RadarDatabase("radar_history.db")
    run_id = db.get_latest_run_id()
    if not run_id:
        raise RuntimeError("Nu exista nicio rulare activa in radar_history.db!")

    price_records = db.get_run_prices(run_id)
    # Grupam produsele pe SKU normalizat si calculam intervalul de pret din magazinele reale
    sku_info_map: Dict[str, Dict[str, Any]] = {}
    for r in price_records:
        sku = r["normalized_sku"]
        p = float(r["current_price_ron"])
        if sku not in sku_info_map:
            sku_info_map[sku] = {
                "normalized_sku": sku,
                "brand": r["brand"],
                "min_store_price": p,
                "max_store_price": p,
                "stores_count": 1,
            }
        else:
            sku_info_map[sku]["min_store_price"] = min(sku_info_map[sku]["min_store_price"], p)
            sku_info_map[sku]["max_store_price"] = max(sku_info_map[sku]["max_store_price"], p)
            sku_info_map[sku]["stores_count"] += 1

    print(f"[eMAG LIVE] Start scanare 100% REALA pe emag.ro pentru {len(sku_info_map)} SKU-uri din SQLite (Run #{run_id})...")

    # Mapare: normalized_sku -> lista de carduri eMAG valide
    matched_cards_by_sku: Dict[str, List[Dict[str, Any]]] = {}

    def _register_cards(cards: List[Dict[str, Any]], target_sku_hint: Optional[str] = None) -> None:
        for c in cards:
            c_sku = c["normalized_sku"]
            if not c_sku:
                continue
            if c_sku in sku_info_map:
                min_p = sku_info_map[c_sku]["min_store_price"]
                max_p = sku_info_map[c_sku]["max_store_price"]
                # Filtru anti-accesorii / anti-pachete gresite: pretul eMAG trebuie sa fie in plaja reala a echipamentului
                if min_p * 0.45 <= c["price_ron"] <= max_p * 1.85:
                    matched_cards_by_sku.setdefault(c_sku, []).append(c)
            elif target_sku_hint and target_sku_hint in sku_info_map:
                # Verificam daca codul cautat apare textual in titlul eMAG
                clean_target = re.sub(r"[^A-Z0-9]", "", target_sku_hint.upper())
                clean_title = re.sub(r"[^A-Z0-9]", "", c["title"].upper())
                if clean_target in clean_title:
                    min_p = sku_info_map[target_sku_hint]["min_store_price"]
                    max_p = sku_info_map[target_sku_hint]["max_store_price"]
                    if min_p * 0.45 <= c["price_ron"] <= max_p * 1.85:
                        matched_cards_by_sku.setdefault(target_sku_hint, []).append(c)

    # PASUL A.1: Scanare rapida pe cele 17 pagini de categorie/brand eMAG
    sem_search = asyncio.Semaphore(5)

    async def _fetch_broad_query(q: str) -> None:
        async with sem_search:
            url = f"https://www.emag.ro/search/{quote_plus(q)}"
            html = await fetch_emag_url_with_rotation(url, base_proxy_url, max_retries=3)
            if html:
                cards = _parse_emag_cards_from_html(html)
                _register_cards(cards)

    await asyncio.gather(*[_fetch_broad_query(q) for q in BROAD_EMAG_QUERIES])
    print(f"[eMAG LIVE] Dupa scanarea de brand: {len(matched_cards_by_sku)} SKU-uri gasite direct pe eMAG.")

    # PASUL A.2: Cautare tintita pentru toate SKU-urile ramase neimperecheate
    unmatched_skus = [sku for sku in sku_info_map if sku not in matched_cards_by_sku]
    print(f"[eMAG LIVE] Rulam cautare tintita pe emag.ro pentru cele {len(unmatched_skus)} SKU-uri ramase...")

    async def _fetch_targeted_sku(sku: str) -> None:
        info = sku_info_map[sku]
        brand = info["brand"]
        # Inlocuim slash-ul '/' cu spatiu pentru a nu rupe rutarea /search/ pe eMAG
        clean_query = re.sub(r"[/\\]+", " ", f"{brand} {sku}").strip()
        async with sem_search:
            url = f"https://www.emag.ro/search/{quote_plus(clean_query)}"
            html = await fetch_emag_url_with_rotation(url, get_rotated_proxy_url(base_proxy_url), max_retries=3)
            if html:
                cards = _parse_emag_cards_from_html(html)
                _register_cards(cards, target_sku_hint=sku)

            # Daca tot nu am gasit card pe cautarea eMAG si SKU-ul e in minim 2 magazine, incercam DuckDuckGo HTML fallback
            if sku not in matched_cards_by_sku and info["stores_count"] >= 2:
                ddg_urls = await search_duckduckgo_emag_fallback(sku, brand, base_proxy_url)
                for pd_u in ddg_urls:
                    price_val, seller_val, off_cnt = await extract_emag_product_page_details(
                        pd_u, None, None, base_proxy_url
                    )
                    if price_val and (info["min_store_price"] * 0.45 <= price_val <= info["max_store_price"] * 1.85):
                        matched_cards_by_sku.setdefault(sku, []).append(
                            {
                                "normalized_sku": sku,
                                "brand": brand,
                                "title": f"{brand} {sku}",
                                "price_ron": price_val,
                                "url": pd_u,
                                "seller_hint": seller_val,
                                "verified_pd": True,
                                "offers_count": off_cnt,
                            }
                        )
                        break

    await asyncio.gather(*[_fetch_targeted_sku(s) for s in unmatched_skus])
    print(f"[eMAG LIVE] Total SKU-uri gasite pe eMAG dupa cautarea tintita: {len(matched_cards_by_sku)} din {len(sku_info_map)}.")

    # PASUL B: Extragem din pagina de produs `/pd/` Sellerul Buy-Box REAL pentru fiecare SKU gasit
    sem_pd = asyncio.Semaphore(6)
    final_emag_rows: List[Dict[str, Any]] = []

    async def _resolve_sku_emag_benchmark(sku: str) -> Dict[str, Any]:
        info = sku_info_map[sku]
        cards = matched_cards_by_sku.get(sku, [])
        if not cards:
            # STRICT: Nu inventam pretul! Punem NULL / "Nelistat pe eMAG"
            return {
                "normalized_sku": sku,
                "brand": info["brand"],
                "emag_title": "Nelistat pe eMAG",
                "emag_lowest_price_ron": None,
                "emag_buybox_seller": "Nelistat pe eMAG",
                "emag_offers_count": 0,
                "in_stock": False,
                "emag_url": "",
                "min_store_price": info["min_store_price"],
            }

        # Alegem oferta cu cel mai mic pret valid de pe eMAG
        unique_urls = {c["url"] for c in cards}
        best_card = min(cards, key=lambda x: x["price_ron"])

        if best_card.get("verified_pd"):
            return {
                "normalized_sku": sku,
                "brand": info["brand"],
                "emag_title": best_card["title"],
                "emag_lowest_price_ron": best_card["price_ron"],
                "emag_buybox_seller": best_card.get("seller_hint") or "Vandut pe eMAG",
                "emag_offers_count": max(best_card.get("offers_count", 1), len(unique_urls)),
                "in_stock": True,
                "emag_url": best_card["url"],
                "min_store_price": info["min_store_price"],
            }

        async with sem_pd:
            real_price, real_seller, pd_offers = await extract_emag_product_page_details(
                best_card["url"],
                best_card["price_ron"],
                best_card.get("seller_hint"),
                get_rotated_proxy_url(base_proxy_url),
            )
            final_price = real_price or best_card["price_ron"]
            total_offers = max(pd_offers, len(unique_urls))
            return {
                "normalized_sku": sku,
                "brand": info["brand"],
                "emag_title": best_card["title"],
                "emag_lowest_price_ron": final_price,
                "emag_buybox_seller": real_seller,
                "emag_offers_count": total_offers,
                "in_stock": True,
                "emag_url": best_card["url"],
                "min_store_price": info["min_store_price"],
            }

    resolved_list = await asyncio.gather(*[_resolve_sku_emag_benchmark(sku) for sku in sku_info_map])
    final_emag_rows.extend(resolved_list)

    # Recreem tabela `emag_benchmarks` (pentru a permite NULL pe emag_lowest_price_ron) si salvam datele 100% REALE
    with sqlite3.connect("radar_history.db") as conn:
        conn.execute("DROP TABLE IF EXISTS emag_benchmarks")
        conn.commit()
    db._init_schema()

    db.insert_emag_benchmarks(run_id, final_emag_rows)

    finalize_and_verify(db, run_id)


def finalize_and_verify(db: RadarDatabase, run_id: int) -> None:
    price_records = db.get_run_prices(run_id)
    min_store_map: Dict[str, float] = {}
    for r in price_records:
        sku = r["normalized_sku"]
        p = float(r["current_price_ron"])
        min_store_map[sku] = min(min_store_map.get(sku, p), p)

    emag_map = db.get_run_emag(run_id)
    all_rows = list(emag_map.values())
    matched_only = [r for r in all_rows if r["emag_lowest_price_ron"] is not None]
    # Punem mai intai produsele cu seller nominal explicit (diferit de generic), apoi sortat pe SKU
    matched_only.sort(
        key=lambda x: (
            0 if x["emag_buybox_seller"] not in ("Vandut pe eMAG", "Nelistat pe eMAG") else 1,
            x["normalized_sku"],
        )
    )

    print("\n" + "=" * 150)
    print(f"VERIFICARE LIVE eMAG MARKETPLACE: {len(matched_only)} PRODUSE GASITE REAL DIN {len(all_rows)} SKU-URI (ZERO FALLBACK SINTETIC)")
    print("=" * 150)
    print(f"{'SKU':<24} | {'Preț Minim Magazine':<20} | {'Preț REAL eMAG':<16} | {'Seller REAL eMAG':<28} | {'URL Exact eMAG'}")
    print("-" * 150)
    for row in matched_only[:15]:
        sku_s = row["normalized_sku"][:24]
        min_s = f"{min_store_map.get(row['normalized_sku'], 0.0):,.2f} RON"
        em_p = f"{float(row['emag_lowest_price_ron']):,.2f} RON"
        em_s = str(row["emag_buybox_seller"])[:28]
        em_u = row["emag_url"]
        print(f"{sku_s:<24} | {min_s:<20} | {em_p:<16} | {em_s:<28} | {em_u}")
    print("=" * 150 + "\n")

    # Regeneram toate fisierele din /output/ si le copiem pe Desktop
    generate_all_mirrors(db, run_id, output_root="output")
    generate_all_outreach(db, run_id, output_root="output")

    desktop_target = Path(r"C:\Users\bratu\Desktop\BF_Price_Radar_RO_Output")
    shutil.copytree(Path("output"), desktop_target, dirs_exist_ok=True)
    print(f"[OK] S-au regenerat toate fisierele in output/ si in {desktop_target}!")


async def enrich_sellers_for_multi_store_skus() -> None:
    base_proxy_url = os.getenv("PROXY_URL", "").strip()
    db = RadarDatabase("radar_history.db")
    run_id = db.get_latest_run_id()
    if not run_id:
        return
    prices = db.get_run_prices(run_id)
    store_counts: Dict[str, int] = {}
    for r in prices:
        s = r["normalized_sku"]
        store_counts[s] = store_counts.get(s, 0) + 1

    emag_map = db.get_run_emag(run_id)
    to_enrich = [
        v for s, v in emag_map.items()
        if v.get("emag_lowest_price_ron") is not None
        and v.get("emag_buybox_seller") == "Vandut pe eMAG"
        and v.get("emag_url")
        and store_counts.get(s, 0) >= 2
    ]
    if to_enrich:
        print(f"[eMAG LIVE] Extragem sellerul exact de pe pagina /pd/ pentru {len(to_enrich)} SKU-uri comune...")
        sem = asyncio.Semaphore(3)

        async def _fix_one(row: Dict[str, Any]) -> None:
            async with sem:
                p_val, seller_val, off_cnt = await extract_emag_product_page_details(
                    row["emag_url"],
                    float(row["emag_lowest_price_ron"]),
                    None,
                    get_rotated_proxy_url(base_proxy_url),
                )
                if seller_val and seller_val != "Vandut pe eMAG":
                    with sqlite3.connect("radar_history.db") as conn:
                        conn.execute(
                            "UPDATE emag_benchmarks SET emag_buybox_seller = ?, emag_offers_count = ? WHERE run_id = ? AND normalized_sku = ?",
                            (seller_val, max(off_cnt, int(row.get("emag_offers_count") or 1)), run_id, row["normalized_sku"]),
                        )
                        conn.commit()

        await asyncio.gather(*[_fix_one(r) for r in to_enrich])

    finalize_and_verify(db, run_id)


if __name__ == "__main__":
    if "--finalize-only" in sys.argv:
        asyncio.run(enrich_sellers_for_multi_store_skus())
    else:
        asyncio.run(run_live_emag_scrape())
