"""
generate_mirrors.py
Generatorul celor 10 "Oglinzi" Excel B2B folosind Polars pentru procesarea matricei incrucisate
si XlsxWriter pentru formatare vizuala executiva:
  1) /output/{store_domain}/Teaser_BlackFriday_{store_domain}.xlsx (Mostra Gratuita de Atac - 8 produse)
  2) /output/{store_domain}/Full_Audit_BlackFriday_{store_domain}.xlsx (Tabelul Complet de 150 EUR + Tab Export Platforma)
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import polars as pl
import xlsxwriter

from db import RadarDatabase


def _sanitize_sheet_name(name: str) -> str:
    """Curata numele tab-ului Excel si il limiteaza la 31 caractere (restrictie Excel)."""
    clean = re.sub(r"[\[\]\:\*\?\/\\]", "_", name)
    return clean[:31]


def build_cross_market_polars_df(
    price_records: List[Dict[str, Any]],
    emag_map: Dict[str, Dict[str, Any]],
) -> pl.DataFrame:
    """
    Construieste DataFrame-ul Polars cu toate preturile si stocurile din rularea curenta,
    imbogatit cu benchmark-ul eMAG Marketplace.
    """
    enriched = []
    for r in price_records:
        sku = r["normalized_sku"]
        em = emag_map.get(sku, {})
        raw_em_price = em.get("emag_lowest_price_ron")
        em_price_val = float(raw_em_price) if (raw_em_price is not None and float(raw_em_price) > 0) else 0.0
        enriched.append(
            {
                "store_domain": r["store_domain"],
                "normalized_sku": sku,
                "brand": r["brand"],
                "category": r.get("category", "Echipament PV"),
                "raw_title": r["raw_title"],
                "store_internal_sku": r["store_internal_sku"],
                "current_price_ron": float(r["current_price_ron"]),
                "in_stock": bool(r["in_stock"]),
                "stock_label": r.get("stock_label", "În stoc" if r["in_stock"] else "Stoc Epuizat"),
                "product_url": r.get("product_url", ""),
                "emag_lowest_price_ron": em_price_val,
                "emag_buybox_seller": str(em.get("emag_buybox_seller") or "Nelistat pe eMAG"),
                "emag_offers_count": int(em.get("emag_offers_count") or 0),
                "emag_url": str(em.get("emag_url") or ""),
            }
        )
    return pl.DataFrame(enriched)


def analyze_sku_for_store(
    df: pl.DataFrame,
    target_store: str,
    sku: str,
) -> Optional[Dict[str, Any]]:
    """
    Calculeaza pozitia exacta a magazinului `target_store` pe modelul `sku`
    fata de toti ceilalti 9 concurenti + eMAG Marketplace.
    """
    sku_rows = df.filter(pl.col("normalized_sku") == sku).to_dicts()
    if not sku_rows:
        return None

    own_row = next((r for r in sku_rows if r["store_domain"] == target_store), None)
    if not own_row:
        return None

    rivals = [r for r in sku_rows if r["store_domain"] != target_store]
    in_stock_rivals = [r for r in rivals if r["in_stock"]]
    oos_rivals = [r for r in rivals if not r["in_stock"]]

    my_price = float(own_row["current_price_ron"])
    my_stock = bool(own_row["in_stock"])

    # Cel mai mic pret concurent cu STOC ACTIV (excludem anomaliile >45% cauzate de sub-variante diferite daca exista rivali comparabili)
    comparable_active_rivals = [
        r for r in in_stock_rivals
        if (my_price - float(r["current_price_ron"])) / float(r["current_price_ron"]) <= 0.45
    ]
    candidate_rivals = comparable_active_rivals if comparable_active_rivals else in_stock_rivals

    if candidate_rivals:
        cheapest_active = min(candidate_rivals, key=lambda x: x["current_price_ron"])
        min_active_price = float(cheapest_active["current_price_ron"])
        min_active_store = str(cheapest_active["store_domain"])
    else:
        min_active_price = my_price
        min_active_store = target_store

    # Verificam daca exista concurenti cu pret afisat mai mic decat noi, dar cu STOC EPUIZAT
    cheaper_oos_rivals = [
        r for r in oos_rivals
        if float(r["current_price_ron"]) < my_price
        and (my_price - float(r["current_price_ron"])) / float(r["current_price_ron"]) <= 0.45
    ]
    cheapest_oos = min(cheaper_oos_rivals, key=lambda x: x["current_price_ron"]) if cheaper_oos_rivals else None

    diff_vs_active_ron = round(my_price - min_active_price, 2)
    diff_vs_active_pct = round((diff_vs_active_ron / min_active_price) * 100.0, 1) if min_active_price > 0 else 0.0

    # Media reala a pietei (RON) si numarul de magazine cu stoc activ din cele 10
    comparable_rows = [
        r for r in sku_rows
        if abs(float(r["current_price_ron"]) - my_price) / max(my_price, 1.0) <= 0.48
    ] or sku_rows
    market_avg_price = round(
        sum(float(r["current_price_ron"]) for r in comparable_rows) / len(comparable_rows),
        2,
    )
    active_stores_count = sum(1 for r in sku_rows if r["in_stock"])
    total_stores_listed = len(sku_rows)

    # Oportunitate de marja (NU IEFTINI!):
    is_margin_opportunity = False
    if cheapest_oos is not None:
        if diff_vs_active_ron <= 0:
            is_margin_opportunity = True
        elif float(cheapest_oos["current_price_ron"]) < min_active_price and diff_vs_active_ron <= 320:
            is_margin_opportunity = True

    emag_raw_price = float(own_row["emag_lowest_price_ron"])
    emag_price = emag_raw_price if emag_raw_price > 0 else None

    return {
        "normalized_sku": sku,
        "brand": own_row["brand"],
        "category": own_row["category"],
        "raw_title": own_row["raw_title"],
        "store_internal_sku": own_row["store_internal_sku"],
        "my_price": my_price,
        "my_in_stock": my_stock,
        "my_stock_label": own_row["stock_label"],
        "min_active_price": min_active_price,
        "min_active_store": min_active_store,
        "diff_vs_active_ron": diff_vs_active_ron,
        "diff_vs_active_pct": diff_vs_active_pct,
        "cheapest_oos_price": float(cheapest_oos["current_price_ron"]) if cheapest_oos else None,
        "cheapest_oos_store": str(cheapest_oos["store_domain"]) if cheapest_oos else None,
        "is_margin_opportunity": is_margin_opportunity,
        "market_avg_price": market_avg_price,
        "active_stores_count": active_stores_count,
        "total_stores_listed": total_stores_listed,
        "emag_price": emag_price,
        "emag_seller": own_row["emag_buybox_seller"],
        "emag_offers": own_row["emag_offers_count"],
        "emag_url": own_row["emag_url"],
        "all_store_rows": {r["store_domain"]: r for r in sku_rows},
    }


def generate_teaser_excel(
    out_path: Path,
    store_domain: str,
    analyzed_items: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Genereaza `Teaser_BlackFriday_{store_domain}.xlsx` (Mostra Gratuita de Atac - 8 produse):
    - Filtru Anti-Anomalii: selecteaza produsele unde diferenta procentuala este intre +3% si +45%
      (exclude diferentele de peste +60% cauzate de pachete/tensiuni diferite).
    - Include ATAT coloana "Media Pietei (10 Magazine)" CAT SI coloana "Etalon eMAG Marketplace (Pret & Seller Buy-Box)"
      100% cu date reale (fara fallback sintetic!).
    - Pe randurile 1-4 (idx < 4) afiseaza pretul real eMAG si sellerul real;
      pe randurile 5-8 (idx >= 4) afiseaza pretul real eMAG, dar mascheaza sellerul cu `[Seller Ascuns în Demo]`.
    """
    in_stock_items = [it for it in analyzed_items if it["my_in_stock"]]

    # Filtru strict Anti-Anomalii (+3% .. +45%), prioritizand produsele listate si pe eMAG
    painful_overpriced = sorted(
        [
            it for it in in_stock_items
            if 3.0 <= it["diff_vs_active_pct"] <= 45.0 and not it["is_margin_opportunity"]
        ],
        key=lambda x: (1 if x["emag_price"] is not None else 0, x["diff_vs_active_ron"]),
        reverse=True,
    )
    if len(painful_overpriced) < 6:
        extra_overpriced = sorted(
            [
                it for it in in_stock_items
                if 0.5 <= it["diff_vs_active_pct"] <= 45.0 and it not in painful_overpriced
            ],
            key=lambda x: (1 if x["emag_price"] is not None else 0, x["diff_vs_active_ron"]),
            reverse=True,
        )
        painful_overpriced.extend(extra_overpriced)

    margin_opps = sorted(
        [it for it in in_stock_items if it["is_margin_opportunity"]],
        key=lambda x: (1 if x["emag_price"] is not None else 0, (x["my_price"] - (x["cheapest_oos_price"] or x["my_price"]))),
        reverse=True,
    )

    # Selectam 6 produse unde pierd bani (+3%..+45%) + 2 produse unde rivalii ieftini au Stoc Epuizat (total 8 produse)
    selected_8: List[Dict[str, Any]] = []
    selected_8.extend(painful_overpriced[:6])
    for m_item in margin_opps[:2]:
        if len(selected_8) < 8 and m_item not in selected_8:
            selected_8.append(m_item)

    if len(selected_8) < 8:
        # Completam cu alte produse comparabile (sub +45%)
        for extra in sorted(
            [it for it in in_stock_items if it["diff_vs_active_pct"] <= 45.0],
            key=lambda x: (1 if x["emag_price"] is not None else 0, x["diff_vs_active_ron"]),
            reverse=True,
        ):
            if extra not in selected_8:
                selected_8.append(extra)
            if len(selected_8) == 8:
                break

    workbook = xlsxwriter.Workbook(str(out_path))
    ws = workbook.add_worksheet("Teaser_8_Produse_BF")
    ws.hide_gridlines(2)

    # Stiluri vizuale B2B
    fmt_title_banner = workbook.add_format({
        "bold": True,
        "font_size": 13,
        "font_color": "#FFFFFF",
        "bg_color": "#0F172A",
        "align": "left",
        "valign": "vcenter",
    })
    fmt_subtitle = workbook.add_format({
        "italic": True,
        "font_size": 10,
        "font_color": "#CBD5E1",
        "bg_color": "#1E293B",
        "align": "left",
        "valign": "vcenter",
    })
    fmt_header = workbook.add_format({
        "bold": True,
        "font_size": 10,
        "font_color": "#FFFFFF",
        "bg_color": "#1E3A8A",
        "border": 1,
        "border_color": "#CBD5E1",
        "align": "center",
        "valign": "vcenter",
        "text_wrap": True,
    })
    fmt_sku = workbook.add_format({
        "bold": True,
        "font_size": 10,
        "font_color": "#0F172A",
        "bg_color": "#F8FAFC",
        "border": 1,
        "border_color": "#E2E8F0",
        "valign": "vcenter",
    })
    fmt_my_price = workbook.add_format({
        "bold": True,
        "font_size": 10,
        "font_color": "#1E293B",
        "bg_color": "#FFFFFF",
        "border": 1,
        "border_color": "#E2E8F0",
        "align": "center",
        "valign": "vcenter",
    })
    fmt_comp = workbook.add_format({
        "font_size": 10,
        "font_color": "#0F172A",
        "bg_color": "#FFFFFF",
        "border": 1,
        "border_color": "#E2E8F0",
        "align": "center",
        "valign": "vcenter",
    })
    fmt_red_loss = workbook.add_format({
        "bold": True,
        "font_size": 10,
        "font_color": "#991B1B",
        "bg_color": "#FEE2E2",
        "border": 1,
        "border_color": "#FCA5A5",
        "align": "center",
        "valign": "vcenter",
    })
    fmt_green_opp = workbook.add_format({
        "bold": True,
        "font_size": 10,
        "font_color": "#166534",
        "bg_color": "#DCFCE7",
        "border": 1,
        "border_color": "#86EFAC",
        "align": "left",
        "valign": "vcenter",
        "text_wrap": True,
    })
    fmt_action_align = workbook.add_format({
        "bold": True,
        "font_size": 10,
        "font_color": "#9A3412",
        "bg_color": "#FFEDD5",
        "border": 1,
        "border_color": "#FDBA74",
        "align": "left",
        "valign": "vcenter",
        "text_wrap": True,
    })

    # Banner superior
    ws.set_row(0, 28)
    ws.set_row(1, 20)
    ws.merge_range(
        0, 0, 0, 6,
        f"RADAR PREȚURI & STOCURI BLACK FRIDAY — MOSTRĂ DEMONSTRATIVĂ (8 PRODUSE) PENTRU {store_domain.upper()}",
        fmt_title_banner,
    )
    ws.merge_range(
        1, 0, 1, 6,
        "Date extrase 100% LIVE (HTTP 200) pe baza Codului Oficial de Producător (SKU) din cele 10 magazine fotovoltaice RO + eMAG Marketplace",
        fmt_subtitle,
    )

    headers = [
        "Cod Model (SKU) & Brand",
        f"Prețul Tău Azi ({store_domain}) + Status Stoc",
        "Cel Mai Mic Preț Concurent în Stoc",
        "Diferența în RON și %",
        "Media Pieței (10 Magazine)",
        "Etalon eMAG Marketplace (Preț & Seller Buy-Box)",
        "Acțiune Recomandată (Fără subcotare în spirală!)",
    ]
    ws.set_row(3, 30)
    for col_idx, h_text in enumerate(headers):
        ws.write(3, col_idx, h_text, fmt_header)

    for idx, item in enumerate(selected_8):
        row_num = 4 + idx
        ws.set_row(row_num, 26)

        col_a = f"{item['normalized_sku']} ({item['brand']})"
        col_b = f"{item['my_price']:,.0f} RON ({item['my_stock_label']})".replace(",", ".")

        # Coloana C: Primele 4 produse afiseaza pretul si numele concurentului;
        # Urmatoarele 4 pun `[Ascuns în versiunea Demo]` la numele concurentului, lasand vizibila diferenta in RON
        if item["is_margin_opportunity"] and item["cheapest_oos_price"]:
            rival_name = item["cheapest_oos_store"] if idx < 4 else "[Ascuns în versiunea Demo]"
            col_c = (
                f"{item['cheapest_oos_price']:,.0f} RON ({rival_name} - STOC EPUIZAT)"
            ).replace(",", ".")
        else:
            rival_name = item["min_active_store"] if idx < 4 else "[Ascuns în versiunea Demo]"
            col_c = f"{item['min_active_price']:,.0f} RON ({rival_name})".replace(",", ".")

        # Coloana D: Diferenta in RON si % (ex: +540 RON (+8.4%) mai scump - colorat cu ROSU)
        diff_ron = item["diff_vs_active_ron"]
        diff_pct = item["diff_vs_active_pct"]
        if item["is_margin_opportunity"] and item["cheapest_oos_price"]:
            fake_diff_ron = round(item["my_price"] - item["cheapest_oos_price"], 0)
            fake_diff_pct = round((fake_diff_ron / item["cheapest_oos_price"]) * 100.0, 1)
            col_d = f"+{fake_diff_ron:,.0f} RON (+{fake_diff_pct:.1f}%) vs. Stoc Epuizat".replace(",", ".")
            d_format = fmt_green_opp
        elif diff_ron > 0:
            col_d = f"+{diff_ron:,.0f} RON (+{diff_pct:.1f}%) mai scump".replace(",", ".")
            d_format = fmt_red_loss
        else:
            col_d = f"{diff_ron:,.0f} RON ({diff_pct:.1f}%)".replace(",", ".")
            d_format = fmt_green_opp

        # Coloana E: Media Pietei (10 Magazine)
        col_e = f"{item['market_avg_price']:,.0f} RON ({item['active_stores_count']} din 10 în stoc)".replace(",", ".")

        # Coloana F: Etalon eMAG Marketplace (Pret & Seller Buy-Box) - 100% REAL sau "Nelistat pe eMAG"
        if item["emag_price"] is not None:
            emag_seller_display = item["emag_seller"] if idx < 4 else "[Seller Ascuns în Demo]"
            offers_str = f" | {item['emag_offers']} oferte" if item["emag_offers"] > 0 else ""
            if idx < 4:
                col_f = f"{item['emag_price']:,.0f} RON (Buy-Box: {emag_seller_display}{offers_str})".replace(",", ".")
            else:
                col_f = f"{item['emag_price']:,.0f} RON ({emag_seller_display}{offers_str})".replace(",", ".")
        else:
            col_f = "Nelistat pe eMAG"

        # Coloana G: Actiune Recomandata
        if item["is_margin_opportunity"]:
            col_g = "🛑 NU IEFTINI! Concurenții ieftini au Stoc Epuizat -> Menține sau Crește marja!"
            g_format = fmt_green_opp
        else:
            target_match = int(item["min_active_price"])
            col_g = f"Aliniere la egalitate (Price Match: {target_match:,} RON)".replace(",", ".")
            g_format = fmt_action_align

        ws.write(row_num, 0, col_a, fmt_sku)
        ws.write(row_num, 1, col_b, fmt_my_price)
        ws.write(row_num, 2, col_c, fmt_comp)
        ws.write(row_num, 3, col_d, d_format)
        ws.write(row_num, 4, col_e, fmt_comp)
        ws.write(row_num, 5, col_f, fmt_comp)
        ws.write(row_num, 6, col_g, g_format)

    # Setam latimi optime auto-ajustate pentru citire imediata pe laptop/mobil
    col_widths = [30, 32, 42, 28, 36, 44, 54]
    for c_i, width in enumerate(col_widths):
        ws.set_column(c_i, c_i, width)

    workbook.close()
    return selected_8


def generate_full_audit_excel(
    out_path: Path,
    store_domain: str,
    detected_platform: str,
    all_store_domains: List[str],
    analyzed_items: List[Dict[str, Any]],
) -> None:
    """
    Genereaza `Full_Audit_BlackFriday_{store_domain}.xlsx` (Tabelul Complet de 150 EUR):
    - Tab 1: Matricea completa cu toate produsele comune, toate cele 10 magazine pe coloane + stocul fiecaruia + Buy-Box eMAG.
    - Tab 2: `Export_Price_Match_{platforma}` formatat exact pe codurile interne (`store_internal_sku`) ale magazinului.
    """
    workbook = xlsxwriter.Workbook(str(out_path))

    # Stiluri
    fmt_banner = workbook.add_format({
        "bold": True,
        "font_size": 13,
        "font_color": "#FFFFFF",
        "bg_color": "#0F172A",
        "valign": "vcenter",
    })
    fmt_header = workbook.add_format({
        "bold": True,
        "font_size": 9,
        "font_color": "#FFFFFF",
        "bg_color": "#1E3A8A",
        "border": 1,
        "border_color": "#CBD5E1",
        "align": "center",
        "valign": "vcenter",
        "text_wrap": True,
    })
    fmt_header_own = workbook.add_format({
        "bold": True,
        "font_size": 9,
        "font_color": "#FFFFFF",
        "bg_color": "#047857",
        "border": 1,
        "border_color": "#CBD5E1",
        "align": "center",
        "valign": "vcenter",
        "text_wrap": True,
    })
    fmt_cell = workbook.add_format({
        "font_size": 9,
        "border": 1,
        "border_color": "#E2E8F0",
        "align": "center",
        "valign": "vcenter",
    })
    fmt_cell_left = workbook.add_format({
        "font_size": 9,
        "bold": True,
        "border": 1,
        "border_color": "#E2E8F0",
        "align": "left",
        "valign": "vcenter",
    })
    fmt_oos_cell = workbook.add_format({
        "font_size": 9,
        "font_color": "#64748B",
        "bg_color": "#F1F5F9",
        "border": 1,
        "border_color": "#E2E8F0",
        "align": "center",
        "valign": "vcenter",
    })
    fmt_red = workbook.add_format({
        "bold": True,
        "font_size": 9,
        "font_color": "#991B1B",
        "bg_color": "#FEE2E2",
        "border": 1,
        "border_color": "#FCA5A5",
        "align": "center",
        "valign": "vcenter",
    })
    fmt_green = workbook.add_format({
        "bold": True,
        "font_size": 9,
        "font_color": "#166534",
        "bg_color": "#DCFCE7",
        "border": 1,
        "border_color": "#86EFAC",
        "align": "center",
        "valign": "vcenter",
    })

    # =========================================================================
    # TAB 1: MATRICE COMPLETA 10 MAGAZINE + eMAG BUY-BOX
    # =========================================================================
    ws_matrix = workbook.add_worksheet("Matrice_Piata_10_Magazine")
    ws_matrix.hide_gridlines(2)
    ws_matrix.freeze_panes(3, 3)

    other_stores = [s for s in all_store_domains if s != store_domain]
    ordered_stores = [store_domain] + other_stores

    total_cols = 3 + len(ordered_stores) + 6
    ws_matrix.set_row(0, 26)
    ws_matrix.merge_range(
        0, 0, 0, total_cols - 1,
        f"AUDIT COMPLET BLACK FRIDAY — MATRICE COMPARATIVĂ 10 MAGAZINE FOTOVOLTAICE RO + eMAG MARKETPLACE PENTRU {store_domain.upper()} (Platformă: {detected_platform})",
        fmt_banner,
    )

    matrix_headers = [
        "Cod Model (SKU)",
        "Brand & Categorie",
        f"Cod Intern ({store_domain})",
        f"PREȚUL TĂU ({store_domain})",
    ] + [f"{s}\n(Preț & Stoc)" for s in other_stores] + [
        "Minim Piață (În Stoc)",
        "Diferență vs. Minim În Stoc",
        "Media Pieței (10 Magazine)",
        "Etalon eMAG Marketplace (Preț & Seller Buy-Box)",
        "URL Exact eMAG",
        "Recomandare Marjă / Price Match",
    ]

    ws_matrix.set_row(2, 30)
    for c_idx, h_val in enumerate(matrix_headers):
        h_fmt = fmt_header_own if c_idx == 3 else fmt_header
        ws_matrix.write(2, c_idx, h_val, h_fmt)

    for r_i, item in enumerate(analyzed_items):
        row = 3 + r_i
        ws_matrix.set_row(row, 22)

        ws_matrix.write(row, 0, item["normalized_sku"], fmt_cell_left)
        ws_matrix.write(row, 1, f"{item['brand']} ({item['category']})", fmt_cell)
        ws_matrix.write(row, 2, item["store_internal_sku"], fmt_cell)

        # Coloanele celor 10 magazine
        for s_i, s_dom in enumerate(ordered_stores):
            col_pos = 3 + s_i
            s_data = item["all_store_rows"].get(s_dom)
            if not s_data:
                ws_matrix.write(row, col_pos, "N/A", fmt_oos_cell)
                continue
            p_val = float(s_data["current_price_ron"])
            in_st = bool(s_data["in_stock"])
            cell_txt = f"{p_val:,.0f} RON ({'În stoc' if in_st else 'Stoc Epuizat'})".replace(",", ".")
            if not in_st:
                ws_matrix.write(row, col_pos, cell_txt, fmt_oos_cell)
            elif s_dom == store_domain and item["diff_vs_active_ron"] > 0:
                ws_matrix.write(row, col_pos, cell_txt, fmt_red)
            elif p_val <= item["min_active_price"]:
                ws_matrix.write(row, col_pos, cell_txt, fmt_green)
            else:
                ws_matrix.write(row, col_pos, cell_txt, fmt_cell)

        base_col = 3 + len(ordered_stores)
        ws_matrix.write(
            row,
            base_col,
            f"{item['min_active_price']:,.0f} RON ({item['min_active_store']})".replace(",", "."),
            fmt_green,
        )

        diff_r = item["diff_vs_active_ron"]
        diff_p = item["diff_vs_active_pct"]
        diff_str = f"{'+' if diff_r > 0 else ''}{diff_r:,.0f} RON ({'+' if diff_p > 0 else ''}{diff_p:.1f}%)".replace(",", ".")
        ws_matrix.write(row, base_col + 1, diff_str, fmt_red if diff_r > 0 else fmt_green)

        ws_matrix.write(
            row,
            base_col + 2,
            f"{item['market_avg_price']:,.0f} RON ({item['active_stores_count']} din 10 în stoc)".replace(",", "."),
            fmt_cell,
        )

        if item["emag_price"] is not None:
            offers_str = f" | {item['emag_offers']} oferte" if item["emag_offers"] > 0 else ""
            emag_txt = f"{item['emag_price']:,.0f} RON (Buy-Box: {item['emag_seller']}{offers_str})".replace(",", ".")
        else:
            emag_txt = "Nelistat pe eMAG"
        ws_matrix.write(row, base_col + 3, emag_txt, fmt_cell)
        ws_matrix.write(row, base_col + 4, item["emag_url"] or "N/A", fmt_cell)

        if item["is_margin_opportunity"]:
            rec_txt = "🛑 NU IEFTINI! Concurenții ieftini au Stoc Epuizat -> Menține sau Crește marja!"
            ws_matrix.write(row, base_col + 5, rec_txt, fmt_green)
        elif diff_r > 0:
            rec_txt = f"Aliniere la egalitate (Price Match: {int(item['min_active_price']):,} RON)".replace(",", ".")
            ws_matrix.write(row, base_col + 5, rec_txt, fmt_red)
        else:
            rec_txt = "✅ Ai deja cel mai bun preț cu stoc activ -> Păstrează prețul actual!"
            ws_matrix.write(row, base_col + 5, rec_txt, fmt_green)

    ws_matrix.set_column(0, 0, 22)
    ws_matrix.set_column(1, 1, 26)
    ws_matrix.set_column(2, 2, 22)
    ws_matrix.set_column(3, 3 + len(ordered_stores) - 1, 25)
    ws_matrix.set_column(3 + len(ordered_stores), 3 + len(ordered_stores) + 2, 28)
    ws_matrix.set_column(3 + len(ordered_stores) + 3, 3 + len(ordered_stores) + 3, 38)
    ws_matrix.set_column(3 + len(ordered_stores) + 4, 3 + len(ordered_stores) + 4, 45)
    ws_matrix.set_column(3 + len(ordered_stores) + 5, 3 + len(ordered_stores) + 5, 52)

    # =========================================================================
    # TAB 2: EXPORT PRICE MATCH FORMATAT PE CODURILE INTERNE ALE PLATFORMEI
    # =========================================================================
    platform_slug = re.sub(r"[^a-zA-Z0-9]", "", detected_platform.split("/")[0].strip()) or "Custom"
    export_sheet_name = _sanitize_sheet_name(f"Export_Price_Match_{platform_slug}")
    ws_exp = workbook.add_worksheet(export_sheet_name)
    ws_exp.hide_gridlines(2)

    ws_exp.set_row(0, 26)
    ws_exp.merge_range(
        0, 0, 0, 6,
        f"TABEL IMPORT RAPID PREȚURI ({detected_platform.upper()}) — CODURI INTERNE {store_domain.upper()}",
        fmt_banner,
    )

    exp_headers = [
        "store_internal_sku (Cod Intern Magazin)",
        "normalized_sku (Cod Oficial Producător)",
        "Brand",
        "Denumire Produs în Catalog",
        "Preț Actual RON",
        "Preț Recomandat Black Friday RON (Price Match Fără Subcotare)",
        "Motiv / Regulă Aplicată",
    ]
    ws_exp.set_row(2, 28)
    for c_i, h_val in enumerate(exp_headers):
        ws_exp.write(2, c_i, h_val, fmt_header)

    for r_i, item in enumerate(analyzed_items):
        row = 3 + r_i
        ws_exp.set_row(row, 22)

        if item["is_margin_opportunity"]:
            new_price = item["my_price"]
            reason = "Menține prețul! Concurenții mai ieftini au Stoc Epuizat"
            p_fmt = fmt_green
        elif item["diff_vs_active_ron"] > 0:
            new_price = item["min_active_price"]
            reason = f"Aliniere la egalitate cu {item['min_active_store']} (stoc activ)"
            p_fmt = fmt_red
        else:
            new_price = item["my_price"]
            reason = "Lider de preț pe stoc activ — nu necesita reducere"
            p_fmt = fmt_green

        ws_exp.write(row, 0, item["store_internal_sku"], fmt_cell_left)
        ws_exp.write(row, 1, item["normalized_sku"], fmt_cell)
        ws_exp.write(row, 2, item["brand"], fmt_cell)
        ws_exp.write(row, 3, item["raw_title"], fmt_cell_left)
        ws_exp.write(row, 4, item["my_price"], fmt_cell)
        ws_exp.write(row, 5, new_price, p_fmt)
        ws_exp.write(row, 6, reason, fmt_cell_left)

    ws_exp.set_column(0, 0, 28)
    ws_exp.set_column(1, 1, 24)
    ws_exp.set_column(2, 2, 16)
    ws_exp.set_column(3, 3, 52)
    ws_exp.set_column(4, 5, 24)
    ws_exp.set_column(6, 6, 48)

    workbook.close()


def generate_all_mirrors(
    db: RadarDatabase,
    run_id: int,
    output_root: str | Path = "output",
) -> Dict[str, Dict[str, Any]]:
    """
    Ruleaza procesarea Polars pe rularea `run_id` si genereaza cele 20 de fisiere Excel
    (cate 2 per magazin) in `/output/{store_domain}/`.
    Returneaza sumarul statistic pentru fiecare magazin (folosit ulterior de `generate_outreach.py`).
    """
    price_records = db.get_run_prices(run_id)
    emag_map = db.get_run_emag(run_id)
    profiles = db.get_store_profiles()

    df = build_cross_market_polars_df(price_records, emag_map)
    all_stores = sorted(df["store_domain"].unique().to_list())
    all_skus = df["normalized_sku"].unique(maintain_order=True).to_list()

    out_root = Path(output_root)
    store_summaries: Dict[str, Dict[str, Any]] = {}

    for store_domain in all_stores:
        store_dir = out_root / store_domain
        store_dir.mkdir(parents=True, exist_ok=True)

        prof = profiles.get(store_domain, {})
        detected_platform = prof.get("detected_platform", "Custom")

        analyzed_items: List[Dict[str, Any]] = []
        for sku in all_skus:
            res = analyze_sku_for_store(df, store_domain, sku)
            if res:
                analyzed_items.append(res)

        teaser_path = store_dir / f"Teaser_BlackFriday_{store_domain}.xlsx"
        full_path = store_dir / f"Full_Audit_BlackFriday_{store_domain}.xlsx"

        selected_teaser = generate_teaser_excel(teaser_path, store_domain, analyzed_items)
        generate_full_audit_excel(full_path, store_domain, detected_platform, all_stores, analyzed_items)

        store_summaries[store_domain] = {
            "store_domain": store_domain,
            "detected_platform": detected_platform,
            "teaser_excel": str(teaser_path),
            "full_excel": str(full_path),
            "analyzed_items": analyzed_items,
            "teaser_items": selected_teaser,
        }

    return store_summaries


if __name__ == "__main__":
    db_inst = RadarDatabase()
    latest = db_inst.get_latest_run_id()
    if latest:
        res = generate_all_mirrors(db_inst, latest)
        print(f"[OK] S-au generat oglinzile Excel pentru {len(res)} magazine (Run #{latest}).")
