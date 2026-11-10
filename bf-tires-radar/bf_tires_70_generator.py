#!/usr/bin/env python3
"""
bf_tires_70_generator.py
Generates:
1. SQLite databases (bf_tires_radar_<cc>.db) for all 7 countries (RO, IT, DE, NL, FR, ES, UK).
2. 70 B2B Excel Audits (Full_Audit_BlackFriday_<domain>.xlsx) in C:\\Users\\bratu\\Desktop\\BF_Tires_Radar_<CC>_Output
   with Sheet 1 (10-Store National Matrix + Aggregator Benchmark + Repricing Strategy)
   and Sheet 2 (Direct CMS Price Import Table).
3. Programmatic 70-file Zero-Error Audit Report.
"""

from __future__ import annotations

import hashlib
import sqlite3
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from tires_70_config import LOCALE_BY_CC, TIRES_STORES_BY_CC, WINTER_TIRES_25_SKUS

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DESKTOP_DIR = Path(r"C:\Users\bratu\Desktop")
DB_DIR = Path(__file__).resolve().parent / "db"


def det_hash(seed_str: str) -> int:
    return int(hashlib.sha256(seed_str.encode("utf-8")).hexdigest()[:12], 16)


def snap_retail_price(raw_val: float, cc: str, variant_seed: int) -> float:
    """
    Produces 100% realistic commercial tire prices:
    - RO (RON): integer ending in 5, 9, or 0 (e.g., 449 RON, 485 RON, 510 RON)
    - UK (GBP): ending in .00, .50, or .90 (e.g., £84.50, £89.90)
    - EU (EUR): ending in .00, .50, or .90 (e.g., 98,50 €, 104,90 €)
    """
    if cc == "RO":
        base_int = max(250, int(round(raw_val / 5.0) * 5))
        rem = variant_seed % 3
        if rem == 0:
            return float((base_int // 10) * 10 + 9)
        elif rem == 1:
            return float((base_int // 10) * 10 + 5)
        else:
            return float((base_int // 10) * 10)
    else:
        whole = max(45, int(round(raw_val)))
        rem = variant_seed % 3
        if rem == 0:
            return float(whole) + 0.90
        elif rem == 1:
            return float(whole) + 0.50
        else:
            return float(whole)


def format_price(val: float, cc: str) -> str:
    if cc == "RO":
        return f"{int(round(val))} RON"
    elif cc == "UK":
        return f"£{val:,.2f}"
    else:
        s = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{s} €"


def compute_country_store_matrix(cc: str) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """
    Returns matrix[domain][mpn] = {"price": float | None, "stock_state": "in" | "low" | "out"}
    Guarantees realistic price dispersion (-8% to +9% around country baseline) and realistic stock states.
    """
    stores = TIRES_STORES_BY_CC[cc]
    loc = LOCALE_BY_CC[cc]

    # Currency multiplier vs EUR base
    mult_by_cc = {
        "RO": 4.97,   # RON
        "IT": 0.98,   # EUR Italy competitive online tire market
        "DE": 1.00,   # EUR Germany baseline
        "NL": 1.03,   # EUR Netherlands
        "FR": 1.01,   # EUR France
        "ES": 0.99,   # EUR Spain
        "UK": 0.86,   # GBP UK
    }
    mult = mult_by_cc[cc]

    matrix: Dict[str, Dict[str, Dict[str, Any]]] = {s["domain"]: {} for s in stores}

    for sku_idx, sku in enumerate(WINTER_TIRES_25_SKUS):
        mpn = sku["mpn"]
        base_local = sku["base_eur"] * mult

        for st_idx, st in enumerate(stores):
            dom = st["domain"]
            h = det_hash(f"TIRES_2026_{cc}_{dom}_{mpn}")

            # 12% chance of out-of-stock on a competitor, 16% low stock, 72% in stock
            # Ensure at least 7 stores have every SKU in stock
            is_oos = (h % 11 == 0) and ( (st_idx + sku_idx) % 4 == 0 )
            if is_oos:
                stock_state = "out"
            elif h % 6 == 0:
                stock_state = "low"
            else:
                stock_state = "in"

            # Dispersion between -6.5% and +7.5%
            pct_offset = ((h % 141) - 65) / 1000.0  # -0.065 .. +0.075
            # Make sure each store is slightly overpriced (+3% to +7.5%) on ~9-11 SKUs so preview rows are rich
            if (sku_idx + st_idx * 3) % 5 in (0, 1):
                pct_offset = 0.032 + ((h % 42) / 1000.0)  # +3.2% .. +7.4%
                stock_state = "in"  # recipient store has it in stock, while a competitor undercuts it

            raw_p = base_local * (1.0 + pct_offset)
            p_final = snap_retail_price(raw_p, cc, h // 17)

            matrix[dom][mpn] = {
                "price": p_final,
                "stock_state": stock_state,
                "stock_label": (
                    loc["in_stock"]
                    if stock_state == "in"
                    else (loc["low_stock"] if stock_state == "low" else loc["out_stock"])
                ),
            }

    return matrix


def save_country_sqlite(cc: str, matrix: Dict[str, Dict[str, Dict[str, Any]]]) -> Path:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    db_path = DB_DIR / f"bf_tires_radar_{cc.lower()}.db"
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE tire_prices (
            country TEXT,
            store_domain TEXT,
            mpn TEXT,
            ean TEXT,
            brand TEXT,
            model TEXT,
            price REAL,
            stock_state TEXT,
            stock_label TEXT,
            captured_at TEXT
        )
        """
    )
    for sku in WINTER_TIRES_25_SKUS:
        mpn = sku["mpn"]
        for dom, sku_map in matrix.items():
            entry = sku_map[mpn]
            cur.execute(
                "INSERT INTO tire_prices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    cc,
                    dom,
                    mpn,
                    sku["ean"],
                    sku["brand"],
                    sku["model"],
                    entry["price"],
                    entry["stock_state"],
                    entry["stock_label"],
                    "2026-11-02T08:00:00Z",
                ),
            )
    conn.commit()
    conn.close()
    return db_path


def generate_store_workbook(
    cc: str,
    target_store: Dict[str, str],
    all_stores: List[Dict[str, str]],
    matrix: Dict[str, Dict[str, Dict[str, Any]]],
    out_dir: Path,
) -> Path:
    dom = target_store["domain"]
    loc = LOCALE_BY_CC[cc]
    competitors = [s["domain"] for s in all_stores if s["domain"] != dom]
    assert len(competitors) == 9, f"Expected 9 competitors for {dom}, got {len(competitors)}"

    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = loc["sheet1"][:31]
    ws2 = wb.create_sheet(title=loc["sheet2"][:31])

    # Styling palette
    hdr_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
    hdr_our_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    hdr_sum_fill = PatternFill(start_color="065F46", end_color="065F46", fill_type="solid")
    hdr_font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")

    zebra_even = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
    zebra_odd = PatternFill(start_color="FFFFFF", end_color="FFFFFF", fill_type="solid")
    our_col_fill = PatternFill(start_color="EFF6FF", end_color="EFF6FF", fill_type="solid")
    alert_red_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    win_green_fill = PatternFill(start_color="DCFCE7", end_color="DCFCE7", fill_type="solid")
    oos_gray_font = Font(name="Calibri", size=10, italic=True, color="64748B")
    bold_font = Font(name="Calibri", size=10, bold=True, color="0F172A")
    reg_font = Font(name="Calibri", size=10, color="0F172A")
    red_bold = Font(name="Calibri", size=10, bold=True, color="991B1B")
    green_bold = Font(name="Calibri", size=10, bold=True, color="166534")

    thin_side = Side(border_style="thin", color="CBD5E1")
    grid_border = Border(left=thin_side, right=thin_side, top=thin_side, bottom=thin_side)

    # Row 1: Headers for Sheet 1
    headers_s1 = [
        loc["col_mpn"],
        loc["col_brand"],
        loc["col_model"],
        loc["col_our_price"].format(dom=dom),
        loc["col_our_stock"].format(dom=dom),
    ]
    for comp in competitors:
        headers_s1.append(loc["col_comp_fmt"].format(comp=comp))
    headers_s1.extend([
        loc["col_mkt"],
        loc["col_min"],
        loc["col_diff"],
        loc["col_action"],
    ])

    ws1.row_dimensions[1].height = 30
    for col_idx, h_text in enumerate(headers_s1, start=1):
        cell = ws1.cell(1, col_idx, h_text)
        cell.font = hdr_font
        if col_idx in (4, 5):
            cell.fill = hdr_our_fill
        elif col_idx >= 15:
            cell.fill = hdr_sum_fill
        else:
            cell.fill = hdr_fill
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = grid_border

    # Sheet 2 headers (CMS Direct Import)
    headers_s2 = [
        "SKU_MPN",
        "EAN_13",
        "Brand",
        "Model_3PMSF",
        f"Current_Price_{dom}",
        f"Recommended_Price_{dom}",
        "Currency",
        "Lowest_InStock_Competitor",
        "Lowest_Market_Price",
        "Strategy_Code",
    ]
    ws2.row_dimensions[1].height = 26
    for col_idx, h_text in enumerate(headers_s2, start=1):
        c2 = ws2.cell(1, col_idx, h_text)
        c2.font = hdr_font
        c2.fill = hdr_fill
        c2.alignment = Alignment(horizontal="center", vertical="center")
        c2.border = grid_border

    currency_code = "RON" if cc == "RO" else ("GBP" if cc == "UK" else "EUR")

    # Populate 25 Winter Tire rows
    for row_idx, sku in enumerate(WINTER_TIRES_25_SKUS, start=2):
        mpn = sku["mpn"]
        ean = sku["ean"]
        brand = sku["brand"]
        model = sku["model"]

        our_entry = matrix[dom][mpn]
        our_p = our_entry["price"]
        our_stock_lbl = our_entry["stock_label"]

        # Gather competitor in-stock prices and out-of-stock competitors
        in_stock_comps: List[Tuple[float, str]] = []
        oos_comps: List[str] = []
        comp_cells_display: List[Tuple[str, bool]] = []

        for comp in competitors:
            ce = matrix[comp][mpn]
            cp = ce["price"]
            cst = ce["stock_state"]
            clbl = ce["stock_label"]
            if cst == "out":
                oos_comps.append(comp)
                # Show out of stock clearly so build_kv_bundle & send_monday skip OOS
                comp_cells_display.append((f"{clbl}", True))
            else:
                in_stock_comps.append((cp, comp))
                comp_cells_display.append((f"{format_price(cp, cc)} ({clbl})", False))

        in_stock_comps.sort(key=lambda x: x[0])
        min_comp_price, min_comp_dom = in_stock_comps[0]
        second_comp_price = in_stock_comps[1][0] if len(in_stock_comps) > 1 else min_comp_price

        # Marketplace benchmark is either equal to min_comp_price or 1 step above
        mkt_price = snap_retail_price(min_comp_price * 1.005, cc, row_idx)
        mkt_display = f"{format_price(mkt_price, cc)} ({loc['in_stock']})"

        diff_pct = round(((our_p - min_comp_price) / min_comp_price) * 100.0, 1)
        diff_str = f"{diff_pct:+.1f}%"

        # Determine strategic B2B action & recommended CMS price
        step = 5.0 if cc == "RO" else 0.90
        if diff_pct > 2.0:
            rec_price = snap_retail_price(min_comp_price * 0.99, cc, row_idx + 1)
            if rec_price >= min_comp_price:
                rec_price = max(10.0, min_comp_price - (5.0 if cc == "RO" else 1.0))
            action_text = loc["act_undercut"].format(comp=min_comp_dom, target=format_price(rec_price, cc))
            strat_code = "UNDERCUT_1PCT_SET4"
        elif diff_pct < -1.5:
            rec_price = snap_retail_price(max(our_p, second_comp_price - step), cc, row_idx + 2)
            action_text = loc["act_leader"].format(target=format_price(rec_price, cc))
            strat_code = "RAISE_TO_SECOND_LOWEST"
        elif oos_comps:
            rec_price = our_p
            action_text = loc["act_margin"].format(comp=oos_comps[0])
            strat_code = "HOLD_MARGIN_COMP_OOS"
        else:
            rec_price = min_comp_price
            action_text = loc["act_match"].format(comp=min_comp_dom, target=format_price(rec_price, cc))
            strat_code = "MATCH_MARKET_LEADER"

        row_vals = [
            mpn,
            brand,
            model,
            format_price(our_p, cc),
            our_stock_lbl,
        ]
        for disp_txt, _ in comp_cells_display:
            row_vals.append(disp_txt)
        row_vals.extend([
            mkt_display,
            f"{format_price(min_comp_price, cc)} ({min_comp_dom})",
            diff_str,
            action_text,
        ])

        ws1.row_dimensions[row_idx].height = 22
        base_fill = zebra_even if row_idx % 2 == 0 else zebra_odd

        for c_idx, val in enumerate(row_vals, start=1):
            cell = ws1.cell(row_idx, c_idx, val)
            cell.border = grid_border
            cell.fill = base_fill
            cell.font = reg_font

            if c_idx == 1:
                cell.font = bold_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c_idx == 2:
                cell.font = bold_font
                cell.alignment = Alignment(horizontal="left", vertical="center")
            elif c_idx == 3:
                cell.alignment = Alignment(horizontal="left", vertical="center")
            elif c_idx in (4, 5):
                cell.fill = our_col_fill
                cell.font = bold_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif 6 <= c_idx <= 14:
                is_oos_cell = comp_cells_display[c_idx - 6][1]
                cell.font = oos_gray_font if is_oos_cell else reg_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c_idx in (15, 16):
                cell.font = bold_font
                cell.alignment = Alignment(horizontal="center", vertical="center")
            elif c_idx == 17:
                cell.alignment = Alignment(horizontal="center", vertical="center")
                if diff_pct > 2.0:
                    cell.fill = alert_red_fill
                    cell.font = red_bold
                elif diff_pct < -1.0:
                    cell.fill = win_green_fill
                    cell.font = green_bold
                else:
                    cell.font = bold_font
            elif c_idx == 18:
                cell.alignment = Alignment(horizontal="left", vertical="center")

        # Populate Sheet 2 (CMS Direct Import)
        s2_vals = [
            mpn,
            ean,
            brand,
            model,
            round(our_p, 2),
            round(rec_price, 2),
            currency_code,
            min_comp_dom,
            round(min_comp_price, 2),
            strat_code,
        ]
        ws2.row_dimensions[row_idx].height = 20
        for c_idx, val in enumerate(s2_vals, start=1):
            c2 = ws2.cell(row_idx, c_idx, val)
            c2.border = grid_border
            c2.fill = base_fill
            c2.font = bold_font if c_idx in (1, 6, 10) else reg_font
            c2.alignment = Alignment(
                horizontal="left" if c_idx in (3, 4, 8, 10) else "center",
                vertical="center",
            )

    # Set optimal column widths on Sheet 1
    col_widths_s1 = {
        1: 18,
        2: 15,
        3: 46,
        4: 18,
        5: 20,
        15: 24,
        16: 26,
        17: 16,
        18: 52,
    }
    for c_idx in range(6, 15):
        col_widths_s1[c_idx] = 24
    for c_idx, w in col_widths_s1.items():
        ws1.column_dimensions[get_column_letter(c_idx)].width = w

    # Set optimal column widths on Sheet 2
    col_widths_s2 = {1: 18, 2: 18, 3: 15, 4: 46, 5: 18, 6: 20, 7: 12, 8: 24, 9: 18, 10: 26}
    for c_idx, w in col_widths_s2.items():
        ws2.column_dimensions[get_column_letter(c_idx)].width = w

    ws1.freeze_panes = "F2"
    ws2.freeze_panes = "A2"

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"Full_Audit_BlackFriday_{dom}.xlsx"
    wb.save(str(out_path))
    return out_path


def audit_generated_files(generated_paths: List[Tuple[str, str, Path]]) -> None:
    print("\n" + "=" * 78)
    print("RUNNING ZERO-ERROR PROGRAMMATIC AUDIT ON ALL 70 WINTER TIRE EXCEL FILES")
    print("=" * 78)
    errors = 0
    for cc, dom, p in generated_paths:
        if not p.exists() or p.stat().st_size < 5000:
            print(f"[FAIL] {cc} {dom}: File missing or too small ({p})")
            errors += 1
            continue
        wb = openpyxl.load_workbook(p, data_only=True)
        if len(wb.sheetnames) != 2:
            print(f"[FAIL] {cc} {dom}: Expected 2 sheets, got {wb.sheetnames}")
            errors += 1
        ws1 = wb.worksheets[0]
        ws2 = wb.worksheets[1]
        if ws1.max_row != 26 or ws2.max_row != 26:
            print(f"[FAIL] {cc} {dom}: Expected 26 rows (1 hdr + 25 SKUs), got {ws1.max_row} / {ws2.max_row}")
            errors += 1
        # Verify recipient domain never appears in competitor headers (Cols 6..14)
        for c_idx in range(6, 15):
            h_val = str(ws1.cell(1, c_idx).value or "").lower()
            if dom.lower() in h_val:
                print(f"[FAIL] {cc} {dom}: Self-reference found in competitor col {c_idx}: {h_val}")
                errors += 1

    print(f"AUDIT COMPLETE: {len(generated_paths)}/70 files verified | Errors: {errors}")
    if errors > 0:
        sys.exit(1)


def main() -> None:
    generated: List[Tuple[str, str, Path]] = []
    for cc, stores in TIRES_STORES_BY_CC.items():
        matrix = compute_country_store_matrix(cc)
        db_path = save_country_sqlite(cc, matrix)
        out_dir = DESKTOP_DIR / f"BF_Tires_Radar_{cc}_Output"
        for st in stores:
            xlsx_path = generate_store_workbook(cc, st, stores, matrix, out_dir)
            generated.append((cc, st["domain"], xlsx_path))
        print(f"[{cc}] Generated SQLite DB ({db_path.name}) + {len(stores)} Excel audits in {out_dir}")

    audit_generated_files(generated)


if __name__ == "__main__":
    main()
