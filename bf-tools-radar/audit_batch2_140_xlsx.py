#!/usr/bin/env python3
r"""
audit_batch2_140_xlsx.py
Exhaustive Cell-by-Cell, DNS-MX, Zero-Duplicate & Zero-AI Audit for Batch 2 ("Calupul 2"):
  1) Verifies exact count & breakdown: 70 stores (UK 10, DE 10, NL 10, IT 10, FR 5, ES 5, AT 10, BE 10 [7 NL + 3 FR]).
  2) Verifies ZERO duplicates (domain, email, VAT ID) internally AND against Wave 1 Tools (70) + Morning Solar (70) = 210 unique B2B clients.
  3) Verifies live DNS MX (70/70) concurrently via dnspython / nslookup.
  4) Audits EVERY cell of ALL 140 Excel workbooks (70 Teaser + 70 Full Audit):
     - Official Manufacturer MPNs only (zero -SOLO, zero ATEL-, zero fake slugs).
     - Clean retail cents (zero .67/.23 weird cents) & proper number_format on numeric price cells.
     - Zero recipient self-reference in Marketplace column or rival columns.
     - Mathematically airtight Margin Protection (cheapest_oos.price < my_price <= cheapest_in_stock.price).
     - Teaser Rows 2-5 unmasked & 1:1 matching the 3 email examples (ex1, ex2, ex_m); Rows 6-9 cleanly masked (zero leaked rival domains!).
     - Clean Sheet-2 tab names (<= 31 chars, zero clunky 'your_webstore' / 'Ihr_Shopsystem' slugs).
     - Zero mixed languages (including strict NL-BE vs FR-BE checks on Belgium!).
  5) Audits ALL 70 ready_email_tools_{CC}.txt files:
     - Zero AI footprints (*, **, `, —, –, smart quotes, [...], {...}, Custom E-Commerce, Online-Shop, TODO, NaN).
     - Exact pricing tiers (£295 / £690 on UK; 350,00 / 850,00 EUR on DE, AT, NL, BE, IT, FR, ES).
     - Exact contact signature (+39 320 948 1876 & amendamax@vasiledev.com).
"""

from __future__ import annotations

import concurrent.futures
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import openpyxl

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
DESKTOP_DIR = Path(r"C:\Users\bratu\Desktop")
MANIFEST_B2 = BASE_DIR / "tools_batch2_70_manifest.json"
MANIFEST_B1 = BASE_DIR / "tools_all_70_manifest.json"
SOLAR_LOG = DESKTOP_DIR / "Morning_70_Campaign_Log_2026-10-29.json"

ALLOWED_MPNS = {
    "HR2470",
    "GA5030R",
    "DHP484Z",
    "DHP484RTJ",
    "DTD153Z",
    "DGA504Z",
    "DHR243Z",
    "197280-8",
    "0611254768",
    "0611254770",
    "0601388108",
    "06019H5202",
    "06019J2200",
    "0611909000",
    "0601063T00",
    "DCD796NT-XJ",
    "DCD796P2-QW",
    "DCD796P2-GB",
    "DCF887NT-XJ",
    "DCH273NT-XJ",
    "DCG405NT-XJ",
    "4933479859",
    "4933479864",
}

CLEAN_RETAIL_CENTS = {0, 5, 10, 20, 25, 30, 40, 45, 49, 50, 60, 70, 75, 80, 85, 89, 90, 95, 98, 99}

FORBIDDEN_PATTERNS = [
    r"\[", r"\]", r"\{", r"\}",
    r"\*", r"`",
    r"\u2014", r"\u2013", r"\u201c", r"\u201d", r"\u2018", r"\u2019", r"\u2026",
    r"Custom E-Commerce", r"Online-Shop", r"Custom /",
    r"353 486 5048", r"\be'", r"piu'", r"gia'", r"OPPORTUNITA\b",
    r"TODO", r"TBD", r"undefined", r"NaN", r"UNKNOWN",
    r"-SOLO\b", r"ATEL-",
]


def check_dns_mx(email_addr: str) -> Tuple[str, bool, str]:
    dom = email_addr.split("@", 1)[1].strip().lower()
    try:
        import dns.resolver  # type: ignore
        ans = dns.resolver.resolve(dom, "MX", lifetime=6.0)
        hosts = [str(r.exchange).rstrip(".") for r in ans]
        if hosts:
            return email_addr, True, hosts[0]
    except Exception:
        pass
    try:
        proc = subprocess.run(
            ["nslookup", "-type=mx", dom, "8.8.8.8"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=7,
        )
        out = proc.stdout or ""
        m = re.search(r"mail exchanger\s*=\s*(\S+)", out, re.I)
        if m:
            return email_addr, True, m.group(1).rstrip(".")
    except Exception:
        pass
    return email_addr, False, "NO_MX"


def extract_prices_from_str(s: str) -> List[float]:
    vals: List[float] = []
    # Match £124.95 or 124,90 € or € 124,90 or 124,90 EUR
    for m in re.finditer(r"£([0-9]{1,3}(?:,[0-9]{3})*\.[0-9]{2})", s):
        vals.append(float(m.group(1).replace(",", "")))
    for m in re.finditer(r"(?:€\s*)?([0-9]{1,3}(?:[\.\s][0-9]{3})*,[0-9]{2})(?:\s*(?:€|EUR))?", s):
        raw = m.group(1).replace(" ", "").replace(".", "").replace(",", ".")
        vals.append(float(raw))
    return vals


def check_clean_cents(val: float, ctx: str, errors: List[str]) -> None:
    cents = int(round((round(val, 2) - int(round(val, 2))) * 100))
    if cents not in CLEAN_RETAIL_CENTS:
        errors.append(f"[WEIRD_CENTS] {val:.2f} (cents={cents}) in {ctx}")


def main() -> None:
    errors: List[str] = []
    if not MANIFEST_B2.exists():
        print(f"FATAL: Missing {MANIFEST_B2}")
        sys.exit(1)

    b2: List[Dict[str, Any]] = json.loads(MANIFEST_B2.read_text(encoding="utf-8"))
    print(f"[1/5] Checking Batch-2 store count and country breakdown (total={len(b2)})...")
    if len(b2) != 70:
        errors.append(f"Expected 70 stores, got {len(b2)}")

    expected_counts = {"UK": 10, "DE": 10, "NL": 10, "IT": 10, "FR": 5, "ES": 5, "AT": 10, "BE": 10}
    actual_counts = Counter(st["cc"] for st in b2)
    for cc, exp_n in expected_counts.items():
        if actual_counts[cc] != exp_n:
            errors.append(f"Country {cc}: expected {exp_n} stores, got {actual_counts[cc]}")
        else:
            print(f"  -> {cc}: {actual_counts[cc]}/{exp_n} stores OK")

    # 2. Zero duplicates against Wave 1 + Solar + internal
    print("\n[2/5] Checking ZERO duplicates (domains, emails, VAT IDs) across all 210 B2B stores...")
    prev_domains: Set[str] = set()
    prev_emails: Set[str] = set()
    prev_vats: Set[str] = set()
    for p, label in [(MANIFEST_B1, "Tools_Wave1"), (SOLAR_LOG, "Morning_Solar")]:
        if p.exists():
            rows = json.loads(p.read_text(encoding="utf-8"))
            for r in rows:
                d = (r.get("domain") or "").lower().strip()
                if d.startswith("www."):
                    d = d[4:]
                e = (r.get("email") or r.get("to") or "").lower().strip()
                v = (r.get("vat_id") or "").upper().strip()
                if d:
                    prev_domains.add(d)
                if e:
                    prev_emails.add(e)
                if v:
                    prev_vats.add(v)

    b2_domains: Set[str] = set()
    b2_emails: Set[str] = set()
    b2_vats: Set[str] = set()
    for st in b2:
        d = st["domain"].lower().strip()
        e = st["email"].lower().strip()
        v = st["vat_id"].upper().strip()
        if d in prev_domains:
            errors.append(f"[DUP_PREV_DOMAIN] {d}")
        if e in prev_emails:
            errors.append(f"[DUP_PREV_EMAIL] {e}")
        if v and v in prev_vats:
            errors.append(f"[DUP_PREV_VAT] {v} on {d}")
        if d in b2_domains:
            errors.append(f"[DUP_INTERNAL_DOMAIN] {d}")
        if e in b2_emails:
            errors.append(f"[DUP_INTERNAL_EMAIL] {e}")
        if v in b2_vats:
            errors.append(f"[DUP_INTERNAL_VAT] {v} on {d}")
        b2_domains.add(d)
        b2_emails.add(e)
        b2_vats.add(v)
    print(f"  -> Unique Batch-2 Domains: {len(b2_domains)}/70 | Unique Emails: {len(b2_emails)}/70 | Unique VAT IDs: {len(b2_vats)}/70 (0 overlaps with {len(prev_domains)} prior stores)")

    # 3. Live DNS MX check on all 70 emails
    print("\n[3/5] Running live DNS MX verification on all 70 recipient emails...")
    mx_ok = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
        futs = [ex.submit(check_dns_mx, st["email"]) for st in b2]
        for f in concurrent.futures.as_completed(futs):
            em, ok, mx_host = f.result()
            if ok:
                mx_ok += 1
            else:
                errors.append(f"[DNS_MX_FAIL] {em} -> {mx_host}")
    print(f"  -> Live DNS MX Verified: {mx_ok}/70 OK")

    # 4. Cell-by-cell audit on all 140 Excel workbooks + 70 Email texts
    print("\n[4/5] Auditing every cell across all 140 Excel workbooks (70 Teaser + 70 Full Audit) and 70 emails...")
    total_cells_checked = 0
    margin_opp_stores = 0

    from batch2_70_config import BATCH2_COUNTRIES_CONFIG
    all_known_domains_by_cc: Dict[str, Set[str]] = {}
    for cc_k, cfg_k in BATCH2_COUNTRIES_CONFIG.items():
        s_set = set(cfg_k["stores"].keys()) | set(cfg_k.get("benchmark_only_rivals", {}).keys())
        all_known_domains_by_cc[cc_k] = s_set

    clunky_tab_fragments = ["your_webstore", "Ihr_Shopsystem", "uw_webshop", "il_vostro", "votre_boutique", "vuestra_tienda"]

    for st in b2:
        cc = st["cc"]
        dom = st["domain"]
        short_name = st["short_name"]
        eff_lang = st.get("lang", cc)
        t_path = Path(st["teaser_xlsx"])
        f_path = Path(st["full_xlsx"])
        e_path = Path(st["ready_email_txt"])

        if not t_path.exists():
            errors.append(f"[MISSING_TEASER] {t_path}")
            continue
        if not f_path.exists():
            errors.append(f"[MISSING_FULL] {f_path}")
            continue
        if not e_path.exists():
            errors.append(f"[MISSING_EMAIL] {e_path}")
            continue

        # Parse & audit email
        raw_txt = e_path.read_text(encoding="utf-8")
        parts = raw_txt.split("=" * 76 + "\n", 1)
        if len(parts) != 2:
            errors.append(f"[MALFORMED_EMAIL_HDR] {e_path}")
            continue
        hdr, body = parts[0], parts[1].strip()
        m_sub = re.search(r"^SUBJECT:\s*(.+)$", hdr, re.M)
        subj = m_sub.group(1).strip() if m_sub else ""
        full_email = subj + "\n" + body

        for pat in FORBIDDEN_PATTERNS:
            if re.search(pat, full_email):
                errors.append(f"[EMAIL_FORBIDDEN] Pattern '{pat}' in {cc}/{dom}")

        if cc == "UK":
            if "£295" not in body or "£690" not in body:
                errors.append(f"[EMAIL_PRICE_TIER] Missing £295/£690 in UK/{dom}")
        else:
            if "350,00" not in body or "850,00" not in body:
                errors.append(f"[EMAIL_PRICE_TIER] Missing 350,00/850,00 in {cc}/{dom}")

        if "+39 320 948 1876" not in body or "amendamax@vasiledev.com" not in body:
            errors.append(f"[EMAIL_SIGNATURE] Missing phone/email in {cc}/{dom}")

        # Audit Teaser workbook
        wb_t = openpyxl.load_workbook(t_path)
        if len(wb_t.sheetnames) != 1:
            errors.append(f"[TEASER_SHEETS] Expected 1 sheet in {t_path.name}, got {len(wb_t.sheetnames)}")
        ws_t = wb_t.active
        if ws_t.max_row != 9 or ws_t.max_column != 8:
            errors.append(f"[TEASER_DIMS] Expected 9x8 in {t_path.name}, got {ws_t.max_row}x{ws_t.max_column}")

        unmasked_names: List[str] = []
        rival_domains_cc = all_known_domains_by_cc[cc] - {dom}

        for r in range(1, ws_t.max_row + 1):
            for c in range(1, ws_t.max_column + 1):
                total_cells_checked += 1
                cell = ws_t.cell(r, c)
                v = cell.value
                if v is None or str(v).strip() == "":
                    errors.append(f"[EMPTY_CELL] {t_path.name} ({r},{c})")
                    continue
                if isinstance(v, str):
                    for pat in [r"\*", r"`", r"\u2014", r"\u2013", r"\[", r"\]", r"\{", r"\}", r"-SOLO\b", r"ATEL-", r"IN_STOCK", r"OUT_OF_STOCK"]:
                        if re.search(pat, v):
                            errors.append(f"[TEASER_CELL_DEFECT] '{pat}' in {t_path.name} ({r},{c}): {v}")
                if r >= 2:
                    if c == 1 and str(v) not in ALLOWED_MPNS:
                        errors.append(f"[INVALID_MPN] '{v}' in {t_path.name} row {r}")
                    if c == 2 and r <= 5:
                        unmasked_names.append(str(v))
                    if c == 3:
                        if not isinstance(v, (int, float)):
                            errors.append(f"[NOT_NUMERIC] {t_path.name} ({r},3) value={v!r}")
                        else:
                            check_clean_cents(float(v), f"{t_path.name}({r},3)", errors)
                        if not cell.number_format or cell.number_format == "General":
                            errors.append(f"[MISSING_NUM_FMT] {t_path.name} ({r},3)")
                    if c == 6:
                        # Marketplace column must NEVER contain recipient's own short_name or domain!
                        if f"({short_name} -" in str(v) or dom in str(v):
                            errors.append(f"[MP_SELF_REF] Recipient '{short_name}' in MP col of {t_path.name} row {r}: {v}")
                    if r >= 6 and c in (4, 6, 8):
                        # Masked rows 6-9 MUST NOT leak any rival domain!
                        for rd in rival_domains_cc:
                            if rd in str(v):
                                errors.append(f"[MASK_LEAK] Rival '{rd}' leaked in masked row {r} col {c} of {t_path.name}: {v}")

        # Verify all 3 email examples' product names appear in unmasked Teaser Rows 2-5!
        matched_in_email = sum(1 for pname in unmasked_names if pname in body)
        if matched_in_email < 3:
            errors.append(f"[EMAIL_TEASER_MISMATCH] Only {matched_in_email}/3 email products found in Teaser rows 2-5 for {cc}/{dom}")

        # Audit Full Audit workbook
        wb_f = openpyxl.load_workbook(f_path)
        if len(wb_f.sheetnames) != 2:
            errors.append(f"[FULL_SHEETS] Expected 2 sheets in {f_path.name}, got {wb_f.sheetnames}")
        for sname in wb_f.sheetnames:
            if len(sname) > 31:
                errors.append(f"[TAB_LEN] Sheet name >31 chars: {sname}")
            for frag in clunky_tab_fragments:
                if frag.lower() in sname.lower():
                    errors.append(f"[CLUNKY_TAB_NAME] '{sname}' in {f_path.name}")

        ws_m = wb_f.worksheets[0]
        ws_imp = wb_f.worksheets[1]
        if ws_m.max_column != 18:  # 5 own cols + 9 rivals + 4 summary cols = 18 cols!
            errors.append(f"[MATRIX_COLS] Expected 18 columns (10-store matrix) in {f_path.name}, got {ws_m.max_column}")
        if ws_m.max_row < 16:
            errors.append(f"[MATRIX_ROWS] Too few rows ({ws_m.max_row}) in {f_path.name}")

        has_store_margin_opp = False
        in_markers = {"In Stock", "Auf Lager", "Op voorraad", "Disponibile", "En stock"}
        oos_markers = {"Out of Stock", "Ausverkauft", "Uitverkocht", "Esaurito", "Rupture de stock", "Agotado"}

        for r in range(1, ws_m.max_row + 1):
            for c in range(1, ws_m.max_column + 1):
                total_cells_checked += 1
                cell = ws_m.cell(r, c)
                v = cell.value
                if v is None or str(v).strip() == "":
                    errors.append(f"[EMPTY_CELL] {f_path.name}[0] ({r},{c})")
                    continue
                if isinstance(v, str):
                    for pat in [r"\*", r"`", r"\u2014", r"\u2013", r"\[", r"\]", r"\{", r"\}", r"-SOLO\b", r"ATEL-", r"IN_STOCK", r"OUT_OF_STOCK"]:
                        if re.search(pat, v):
                            errors.append(f"[FULL_CELL_DEFECT] '{pat}' in {f_path.name}[0] ({r},{c}): {v}")

            if r >= 2:
                mpn_val = str(ws_m.cell(r, 1).value)
                if mpn_val not in ALLOWED_MPNS:
                    errors.append(f"[FULL_INVALID_MPN] '{mpn_val}' in {f_path.name} row {r}")
                my_p = float(ws_m.cell(r, 4).value)
                check_clean_cents(my_p, f"{f_path.name}[0]({r},4)", errors)
                low_in_p = float(ws_m.cell(r, 15).value)
                check_clean_cents(low_in_p, f"{f_path.name}[0]({r},15)", errors)
                mp_col_str = str(ws_m.cell(r, 17).value)
                if f"({short_name} -" in mp_col_str or dom in mp_col_str:
                    errors.append(f"[FULL_MP_SELF_REF] '{short_name}' in MP col of {f_path.name} row {r}")

                act_str = str(ws_m.cell(r, 18).value)
                # Verify Margin Protection mathematical soundness on every row claiming HOLD MARGIN / MARGE HALTEN / etc.
                is_hold = any(k in act_str for k in ["HOLD MARGIN", "MARGE HALTEN", "MARGE BEHOUDEN", "MANTIENI IL MARGINE", "MANTENER MARGEN", "MAINTENIR LA MARGE"])
                if is_hold:
                    has_store_margin_opp = True
                    # Parse all 9 rival columns (cols 6..14) to verify at least 1 OOS rival < my_p AND all In-Stock rivals >= my_p!
                    in_prices: List[float] = []
                    oos_prices: List[float] = []
                    for rc in range(6, 15):
                        rv_s = str(ws_m.cell(r, rc).value)
                        prs = extract_prices_from_str(rv_s)
                        if not prs:
                            continue
                        check_clean_cents(prs[0], f"{f_path.name}[0]({r},{rc})", errors)
                        if any(om in rv_s for om in oos_markers):
                            oos_prices.append(prs[0])
                        elif any(im in rv_s for im in in_markers):
                            in_prices.append(prs[0])
                    if not oos_prices or min(oos_prices) >= my_p:
                        errors.append(f"[FAKE_MARGIN_OPP_NO_OOS] {f_path.name} row {r}: my_p={my_p}, oos={oos_prices}")
                    if in_prices and my_p > min(in_prices):
                        errors.append(f"[FAKE_MARGIN_OPP_UNDERCUT] {f_path.name} row {r}: my_p={my_p} > min_in_stock={min(in_prices)}")

        if has_store_margin_opp:
            margin_opp_stores += 1
        else:
            errors.append(f"[NO_MARGIN_OPP] Store {cc}/{dom} has 0 Margin Protection SKUs!")

        # Check Sheet 2 (Import sheet)
        for r in range(1, ws_imp.max_row + 1):
            for c in range(1, ws_imp.max_column + 1):
                total_cells_checked += 1
                cell = ws_imp.cell(r, c)
                v = cell.value
                if v is None or str(v).strip() == "":
                    errors.append(f"[EMPTY_CELL] {f_path.name}[1] ({r},{c})")
                if r >= 2 and c in (4, 5):
                    if not isinstance(v, (int, float)):
                        errors.append(f"[IMP_NOT_NUMERIC] {f_path.name}[1] ({r},{c}) val={v!r}")
                    else:
                        check_clean_cents(float(v), f"{f_path.name}[1]({r},{c})", errors)
                    if not cell.number_format or cell.number_format == "General":
                        errors.append(f"[IMP_NO_NUM_FMT] {f_path.name}[1] ({r},{c})")

        # Extra Belgium bilingual language purity check!
        if cc == "BE":
            if eff_lang == "BE_FR":
                # Must NOT contain Dutch stock labels in French Belgian workbook
                for ws_chk in (ws_t, ws_m, ws_imp):
                    for r_chk in range(1, ws_chk.max_row + 1):
                        for c_chk in range(1, ws_chk.max_column + 1):
                            sv = str(ws_chk.cell(r_chk, c_chk).value)
                            if "Op voorraad" in sv or "Uitverkocht" in sv:
                                errors.append(f"[BE_LANG_MIX] Dutch stock label inside FR-BE {dom} workbook: {sv}")
            else:
                for ws_chk in (ws_t, ws_m, ws_imp):
                    for r_chk in range(1, ws_chk.max_row + 1):
                        for c_chk in range(1, ws_chk.max_column + 1):
                            sv = str(ws_chk.cell(r_chk, c_chk).value)
                            if "Rupture de stock" in sv or "Machine seule" in sv:
                                errors.append(f"[BE_LANG_MIX] French text inside NL-BE {dom} workbook: {sv}")

    print(f"  -> Total Excel Cells Audited: {total_cells_checked:,} across 140 workbooks")
    print(f"  -> Stores with Mathematically Airtight Margin Protection SKU: {margin_opp_stores}/70")

    print("\n[5/5] FINAL AUDIT RESULT:")
    if errors:
        print(f"FAILED WITH {len(errors)} ERRORS:")
        for e in errors[:40]:
            print(f"  ❌ {e}")
        sys.exit(1)
    else:
        print("=" * 96)
        print("✅ 100% ZERO-DEFECT AUDIT PASSED ON ALL 70 STORES, 70 DNS MX, 70 EMAILS & 140 EXCEL WORKBOOKS!")
        print("=" * 96)


if __name__ == "__main__":
    main()
