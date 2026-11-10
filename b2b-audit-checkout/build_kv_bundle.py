#!/usr/bin/env python3
"""
build_kv_bundle.py
Builds the Cloudflare KV bulk JSON payload (meta:<domain> + xlsx:<domain>) for all 210+ B2B stores
across Solar & Power Tools (RO, IT, DE, AT, NL, BE, FR, ES, UK).
"""

from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import openpyxl

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT_DIR / "bf-tools-radar"
TIRES_DIR = ROOT_DIR / "bf-tires-radar"
DESKTOP_DIR = Path(r"C:\Users\bratu\Desktop")
OUT_JSON = Path(__file__).resolve().parent / "kv_bulk_payload.json"
OUT_TIRES_JSON = Path(__file__).resolve().parent / "kv_tires_payload.json"
MANIFEST_SUMMARY = Path(__file__).resolve().parent / "portal_210_manifest.json"

sys.path.insert(0, str(TOOLS_DIR))
sys.path.insert(0, str(TIRES_DIR))
import genereaza_factura_pdf as inv_mod  # noqa: E402
from tires_70_config import TIRES_PRICING_BY_CC  # noqa: E402

CLIENT_REGISTRY: Dict[str, Dict[str, str]] = inv_mod.CLIENT_REGISTRY

PRICING_BY_CC: Dict[str, Dict[str, Any]] = {
    "RO": {"currency": "EUR", "symbol": "€", "orig_opt1": 150.0, "flash_opt1": 79.0, "orig_opt2": 450.0, "flash_opt2": 249.0},
    "UK": {"currency": "GBP", "symbol": "£", "orig_opt1": 295.0, "flash_opt1": 129.0, "orig_opt2": 690.0, "flash_opt2": 349.0},
    "DE": {"currency": "EUR", "symbol": "€", "orig_opt1": 350.0, "flash_opt1": 149.0, "orig_opt2": 850.0, "flash_opt2": 449.0},
    "AT": {"currency": "EUR", "symbol": "€", "orig_opt1": 350.0, "flash_opt1": 149.0, "orig_opt2": 850.0, "flash_opt2": 449.0},
    "NL": {"currency": "EUR", "symbol": "€", "orig_opt1": 350.0, "flash_opt1": 149.0, "orig_opt2": 850.0, "flash_opt2": 449.0},
    "BE": {"currency": "EUR", "symbol": "€", "orig_opt1": 350.0, "flash_opt1": 149.0, "orig_opt2": 850.0, "flash_opt2": 449.0},
    "IT": {"currency": "EUR", "symbol": "€", "orig_opt1": 350.0, "flash_opt1": 149.0, "orig_opt2": 850.0, "flash_opt2": 449.0},
    "FR": {"currency": "EUR", "symbol": "€", "orig_opt1": 350.0, "flash_opt1": 149.0, "orig_opt2": 850.0, "flash_opt2": 449.0},
    "ES": {"currency": "EUR", "symbol": "€", "orig_opt1": 350.0, "flash_opt1": 149.0, "orig_opt2": 850.0, "flash_opt2": 449.0},
}

DEFAULT_LANG_BY_CC: Dict[str, str] = {
    "RO": "ro",
    "UK": "en",
    "DE": "de",
    "AT": "de",
    "NL": "nl",
    "BE": "nl",
    "IT": "it",
    "FR": "fr",
    "ES": "es",
}


def parse_price_number(val: Any) -> Optional[float]:
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val) if val > 0 else None
    s = str(val).strip()
    if not s:
        return None
    # Extract first price-like token before '('
    s_head = s.split("(")[0]
    m = re.search(r"(\d[\d\.,\s]*\d|\d+)", s_head)
    if not m:
        return None
    num_s = m.group(1).replace(" ", "").replace("\u00a0", "")
    if "," in num_s and "." in num_s:
        if num_s.rfind(",") > num_s.rfind("."):
            num_s = num_s.replace(".", "").replace(",", ".")
        else:
            num_s = num_s.replace(",", "")
    elif "," in num_s:
        parts = num_s.split(",")
        if len(parts[-1]) == 3 and len(parts[0]) <= 3:
            num_s = num_s.replace(",", "")
        else:
            num_s = num_s.replace(",", ".")
    elif "." in num_s:
        parts = num_s.split(".")
        if len(parts[-1]) == 3 and "RON" in s.upper():
            num_s = num_s.replace(".", "")
    try:
        v = float(num_s)
        return v if v > 1.0 else None
    except ValueError:
        return None


def extract_excel_metadata(xlsx_path: Path, cc: str) -> Dict[str, Any]:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    sheet_names = list(wb.sheetnames)
    ws = wb.active

    # Detect header row (Row 3 for Solar IT / Solar RO, Row 1 otherwise)
    r1_c1 = str(ws.cell(1, 1).value or "").strip().upper()
    if r1_c1.startswith("AUDIT COMPLET"):
        hdr_row = 3
        compact_4col = True  # Col1=SKU, Col2=Brand&Cat, Col3=InternalRef, Col4=OurPrice(Stock), Col5..=Competitors
    else:
        hdr_row = 1
        compact_4col = False  # Col1=MPN, Col2=Brand, Col3=Model, Col4=OurPrice, Col5=OurStock, Col6..=Competitors

    comp_start_col = 5 if compact_4col else 6
    comp_end_col = min(ws.max_column, comp_start_col + 8)
    comp_headers = []
    for c in range(comp_start_col, comp_end_col + 1):
        hv = str(ws.cell(hdr_row, c).value or "").strip()
        if hv:
            comp_headers.append(hv)

    brands_seen: List[str] = []
    all_rows: List[Dict[str, Any]] = []

    for r in range(hdr_row + 1, ws.max_row + 1):
        mpn = str(ws.cell(r, 1).value or "").strip()
        if not mpn or mpn.lower().startswith("not") or len(mpn) > 45:
            continue
        raw_brand = str(ws.cell(r, 2).value or "").strip()
        brand_clean = raw_brand.split("(")[0].strip()
        if brand_clean and brand_clean not in brands_seen:
            brands_seen.append(brand_clean)

        if compact_4col:
            model = f"{raw_brand} — {mpn}"
            our_cell = str(ws.cell(r, 4).value or "").strip()
            if "(" in our_cell and ")" in our_cell:
                our_price_str = our_cell.split("(")[0].strip()
                our_stock_str = our_cell.split("(", 1)[1].rsplit(")", 1)[0].strip()
            else:
                our_price_str = our_cell
                our_stock_str = ""
            our_num = parse_price_number(our_price_str)
        else:
            model = str(ws.cell(r, 3).value or "").strip()
            raw_p = ws.cell(r, 4).value
            our_num = parse_price_number(raw_p)
            if isinstance(raw_p, (int, float)):
                if cc == "RO":
                    our_price_str = f"{raw_p:,.0f} RON".replace(",", ".")
                elif cc == "UK":
                    our_price_str = f"£{raw_p:,.2f}"
                else:
                    our_price_str = f"{raw_p:,.2f} €"
            else:
                our_price_str = str(raw_p or "").strip()
            our_stock_str = str(ws.cell(r, 5).value or "").strip()

        # Find lowest valid competitor price strictly across the 9 competitor store columns
        best_comp_num: Optional[float] = None
        best_comp_display: str = ""
        for c in range(comp_start_col, comp_end_col + 1):
            cv = str(ws.cell(r, c).value or "").strip()
            if not cv or cv.startswith("http") or any(x in cv.lower() for x in ["nicht", "non ", "not ", "indispon", "geen", "no list", "epuizat", "ausverkauft", "esaurito", "out of stock", "agotado", "épuisé", "uitverkocht"]):
                continue
            cnum = parse_price_number(cv)
            if cnum and (best_comp_num is None or cnum < best_comp_num):
                best_comp_num = cnum
                best_comp_display = cv

        diff_pct = 0.0
        if our_num and best_comp_num and best_comp_num > 0:
            diff_pct = round(((our_num - best_comp_num) / best_comp_num) * 100.0, 1)

        all_rows.append({
            "mpn": mpn,
            "brand": brand_clean or raw_brand,
            "model": model[:68],
            "our_price": our_price_str,
            "our_stock": our_stock_str,
            "best_market": best_comp_display,
            "diff_pct": diff_pct,
        })

    # Sort preview candidates to show the 3 rows where store is overpriced vs market (most actionable!)
    overpriced = [x for x in all_rows if x["diff_pct"] > 1.5 and x["best_market"]]
    overpriced.sort(key=lambda x: x["diff_pct"], reverse=True)
    preview = overpriced[:3]
    if len(preview) < 3:
        for x in all_rows:
            if x not in preview and x["best_market"]:
                preview.append(x)
            if len(preview) == 3:
                break

    return {
        "sheets": sheet_names,
        "sku_count": len(all_rows),
        "competitor_count": max(9, len(comp_headers)),
        "brands": brands_seen[:6],
        "preview_rows": preview,
    }


def load_sent_logs() -> Dict[str, Dict[str, Any]]:
    sent_info: Dict[str, Dict[str, Any]] = {}
    log_Configs = [
        ("solar", DESKTOP_DIR / "Morning_70_Campaign_Log_2026-10-29.json"),
        ("tools_w1", DESKTOP_DIR / "Tools_70_Campaign_Log_2026-10-29.json"),
        ("tools_w2", DESKTOP_DIR / "Tools_Wave2_70_Campaign_Log_2026-10-29.json"),
    ]
    for wave_tag, p in log_Configs:
        raw = json.loads(p.read_text(encoding="utf-8"))
        items = raw if isinstance(raw, list) else raw.get("sent", raw.get("entries", []))
        for it in items:
            dom = str(it.get("domain", "")).strip().lower()
            cc = str(it.get("country") or it.get("cc") or "").strip().upper()
            recip = str(it.get("recipient") or it.get("email") or it.get("to") or "").strip()
            subj = str(it.get("subject") or "").strip()
            prov = str(it.get("smtp_used") or it.get("provider") or "").strip()
            lang = DEFAULT_LANG_BY_CC.get(cc, "en")
            if cc == "BE":
                if any(w in subj.lower() for w in ["comparatif", "stocks", "prix"]):
                    lang = "fr"
                else:
                    lang = "nl"
            sent_info[dom] = {
                "wave": wave_tag,
                "vertical": "solar" if wave_tag == "solar" else "tools",
                "cc": cc,
                "lang": lang,
                "sent_to": recip,
                "orig_subject": subj,
                "orig_provider": prov,
            }
    return sent_info


def main() -> None:
    sent_info = load_sent_logs()
    print(f"Loaded {len(sent_info)} unique sent domains from the 3 logs.")

    # Index all Full_Audit xlsx files on Desktop
    xlsx_by_domain: Dict[str, Tuple[Path, str, str]] = {}
    for folder in sorted(DESKTOP_DIR.glob("BF_*_Output")):
        m = re.match(r"BF_(Price_Radar|Tools_Radar|Tools_Wave2|Tires_Radar)_([A-Z]{2})_Output", folder.name)
        if not m:
            continue
        kind, cc = m.group(1), m.group(2)
        vertical = "solar" if kind == "Price_Radar" else ("tires" if kind == "Tires_Radar" else "tools")
        for f in folder.rglob("*.xlsx"):
            if "full" not in f.name.lower():
                continue
            # Extract domain from Full_Audit_BlackFriday_<domain>.xlsx
            dm = re.sub(r"^Full_Audit_BlackFriday_", "", f.name, flags=re.I)
            dm = re.sub(r"\.xlsx$", "", dm, flags=re.I).strip().lower()
            xlsx_by_domain[dm] = (f, cc, vertical)

    kv_entries: List[Dict[str, str]] = []
    kv_tires_entries: List[Dict[str, str]] = []
    manifest_out: List[Dict[str, Any]] = []

    all_domains = sorted(set(sent_info.keys()) | set(xlsx_by_domain.keys()))
    matched_sent = 0
    tires_count = 0

    for dom in all_domains:
        if dom not in xlsx_by_domain:
            print(f"[WARN] Missing xlsx for {dom}!")
            continue
        xlsx_path, folder_cc, folder_vert = xlsx_by_domain[dom]
        s_meta = sent_info.get(dom, {})
        reg = CLIENT_REGISTRY.get(dom, {})

        cc = s_meta.get("cc") or reg.get("country") or folder_cc
        lang = s_meta.get("lang") or DEFAULT_LANG_BY_CC.get(cc, "en")
        vertical = s_meta.get("vertical") or folder_vert
        if vertical == "tires":
            pricing = TIRES_PRICING_BY_CC.get(cc, TIRES_PRICING_BY_CC["DE"])
        else:
            pricing = PRICING_BY_CC.get(cc, PRICING_BY_CC["DE"])

        excel_meta = extract_excel_metadata(xlsx_path, cc)
        raw_bytes = xlsx_path.read_bytes()
        b64_xlsx = base64.b64encode(raw_bytes).decode("ascii")
        file_kb = round(len(raw_bytes) / 1024.0, 1)

        public_meta = {
            "domain": dom,
            "cc": cc,
            "lang": lang,
            "vertical": vertical,
            "company_name": reg.get("company_name", dom.upper()),
            "vat_id": reg.get("vat_id", ""),
            "address": reg.get("address", cc),
            "email": s_meta.get("sent_to") or reg.get("email", ""),
            "platform": reg.get("platform", "E-Commerce"),
            "file_name": xlsx_path.name,
            "file_kb": file_kb,
            "pricing": pricing,
            **excel_meta,
        }

        kv_entries.append({"key": f"meta:{dom}", "value": json.dumps(public_meta, ensure_ascii=False)})
        kv_entries.append({"key": f"xlsx:{dom}", "value": b64_xlsx})
        if vertical == "tires":
            tires_count += 1
            kv_tires_entries.append({"key": f"meta:{dom}", "value": json.dumps(public_meta, ensure_ascii=False)})
            kv_tires_entries.append({"key": f"xlsx:{dom}", "value": b64_xlsx})

        if dom in sent_info:
            matched_sent += 1
            manifest_out.append({
                **public_meta,
                "wave": s_meta["wave"],
                "sent_to": s_meta["sent_to"],
                "orig_subject": s_meta["orig_subject"],
                "orig_provider": s_meta["orig_provider"],
                "checkout_url": f"https://vasiledev.com/audit/?shop={dom}",
            })

    kv_entries.append({"key": "index:count", "value": str(len(manifest_out) + tires_count)})
    OUT_JSON.write_text(json.dumps(kv_entries, ensure_ascii=False), encoding="utf-8")
    OUT_TIRES_JSON.write_text(json.dumps(kv_tires_entries, ensure_ascii=False), encoding="utf-8")
    meta_only = [e for e in kv_entries if not e["key"].startswith("xlsx:")]
    (OUT_JSON.parent / "kv_meta_only.json").write_text(json.dumps(meta_only, ensure_ascii=False), encoding="utf-8")
    MANIFEST_SUMMARY.write_text(json.dumps(manifest_out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(
        f"SUCCESS: Matched {matched_sent}/{len(sent_info)} sent stores + {tires_count} tire stores. "
        f"Total KV entries: {len(kv_entries)} ({OUT_JSON.stat().st_size/1024/1024:.2f} MB) | "
        f"Tires KV entries: {len(kv_tires_entries)} ({OUT_TIRES_JSON.stat().st_size/1024/1024:.2f} MB)"
    )


if __name__ == "__main__":
    main()
