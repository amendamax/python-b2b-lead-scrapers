"""
verify_live_urls.py
Audit Anti-Mock & Verificare Live HTTP 200 pe URL-urile din SQLite (`radar_history.db`):
1. Extrage 10 `product_url` din tabelul `price_history` (cate unul de la fiecare din cele 10 magazine).
2. Executa un request HTTP GET real pe fiecare URL si afiseaza:
   Store | SKU | Preț în DB | Status HTTP Live | URL exact
3. Regenereaza toate fisierele din `/output/` (Teaser Excel, Full Audit Excel, Outreach B2B, Alerte Live).
"""

from __future__ import annotations

import shutil
import sqlite3
from pathlib import Path

import httpx

from db import RadarDatabase
from scraper_engine import sanitize_outbound_scrape_url
from generate_mirrors import generate_all_mirrors
from generate_outreach import generate_all_outreach
from live_monitor import run_live_diff_alerts


def run_verification_and_regenerate() -> None:
    db_path = Path("radar_history.db")
    if not db_path.exists():
        raise FileNotFoundError("Nu exista `radar_history.db`. Ruleaza mai intai `test_smoke.py`.")

    db = RadarDatabase(db_path)
    latest_run_id = db.get_latest_run_id()
    if latest_run_id is None:
        raise RuntimeError("Baza de date `radar_history.db` nu contine nicio rulare.")

    prev_run_id = db.get_previous_run_id(latest_run_id) or latest_run_id

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    # Curatam eventualele intrari cu control-box / back-up-box din URL/titlu
    conn.execute(
        """
        DELETE FROM price_history
        WHERE LOWER(product_url) LIKE '%accesoriu%'
           OR LOWER(product_url) LIKE '%control-box%'
           OR LOWER(product_url) LIKE '%back-up-box%'
        """
    )
    conn.commit()

    rows = conn.execute(
        """
        SELECT store_domain, normalized_sku, current_price_ron, product_url
        FROM price_history
        WHERE run_id = ?
        GROUP BY store_domain
        ORDER BY store_domain
        LIMIT 10
        """,
        (latest_run_id,),
    ).fetchall()
    conn.close()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ro-RO,ro;q=0.9,en-US;q=0.8",
    }

    print("=" * 124)
    print("🔍 AUDIT ANTI-MOCK & VERIFICARE LIVE URL-URI DIN SQLITE (`radar_history.db` -> `price_history`)")
    print("=" * 124)
    print(f"{'Store':<22} | {'SKU':<22} | {'Preț în DB':<15} | {'Status HTTP Live':<16} | {'URL exact'}")
    print("-" * 124)

    all_ok = True
    with httpx.Client(verify=False, follow_redirects=True, timeout=20.0, headers=headers) as client:
        for r in rows:
            store = r["store_domain"]
            sku = r["normalized_sku"]
            price_str = f"{float(r['current_price_ron']):,.2f} RON"
            url = r["product_url"]
            try:
                resp = client.get(sanitize_outbound_scrape_url(url))
                status = resp.status_code
            except Exception as exc:
                status = f"ERR ({exc})"
                all_ok = False

            if status != 200:
                all_ok = False
            status_str = f"HTTP {status} (OK)" if status == 200 else f"HTTP {status}"
            print(f"{store:<22} | {sku:<22} | {price_str:<15} | {status_str:<16} | {url}")

    print("-" * 124)
    if all_ok and len(rows) == 10:
        print("✅ VERIFICARE 10/10 REUȘITĂ: Toate cele 10 URL-uri din SQLite sunt reale și răspund cu HTTP 200 Live!")
    else:
        print(f"⚠️ ATENȚIE: S-au verificat {len(rows)} magazine (all_ok={all_ok}).")

    # Regeneram toate fisierele din /output/
    out_dir = Path("output")
    out_dir.mkdir(parents=True, exist_ok=True)

    mirrors = generate_all_mirrors(db, latest_run_id, output_root=out_dir)
    outreach = generate_all_outreach(db, latest_run_id, output_root=out_dir)
    alerts = run_live_diff_alerts(db, current_run_id=latest_run_id, previous_run_id=prev_run_id, output_root=out_dir)
    total_alerts = sum(len(v) for v in alerts.values())

    print(
        f"🔄 REGENERARE `/output/` COMPLETĂ: {len(mirrors) * 2} fișiere Excel + "
        f"{len(outreach)} pachete Outreach B2B + {total_alerts} alerte VIP 450 EUR."
    )
    print("=" * 124)


if __name__ == "__main__":
    run_verification_and_regenerate()
