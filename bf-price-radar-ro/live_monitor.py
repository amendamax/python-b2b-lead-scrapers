"""
live_monitor.py
Motorul de Diff & Alerte Live (Pachetul 450 EUR - 3 rulari/zi, max. 3 clienti exclusivi).
Citeste `clients_config.json`, compara rularea curenta cu rularea anterioara din SQLite
si genereaza alerte instant pentru WhatsApp / Telegram / Email DOAR cand:
  1. Un concurent cu stoc activ scade pretul la unul din brandurile rezervate (sugerand Egalarea pretului, nu subcotarea).
  2. Un concurent mai ieftin trece din `in_stock = True` in `in_stock = False` (Alerta de Oportunitate de Marja).
  3. Se schimba detinatorul Buy-Box-ului pe eMAG Marketplace.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from db import RadarDatabase


def _fmt_ron(val: float) -> str:
    return f"{int(round(val)):,}".replace(",", ".")


def run_live_diff_alerts(
    db: RadarDatabase,
    current_run_id: Optional[int] = None,
    previous_run_id: Optional[int] = None,
    clients_config_path: str | Path = "clients_config.json",
    output_root: str | Path = "output",
) -> Dict[str, List[str]]:
    """
    Compara doua rulari consecutive din SQLite si genereaza alertele VIP per client
    exclusiv pe cele 2 branduri blocate de fiecare.
    """
    with open(clients_config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    clients = [c for c in cfg.get("clients", []) if c.get("active", True)][: cfg.get("max_active_clients", 3)]

    if current_run_id is None:
        current_run_id = db.get_latest_run_id()
    if not current_run_id:
        return {}

    if previous_run_id is None:
        previous_run_id = db.get_previous_run_id(current_run_id)
    if not previous_run_id:
        return {}

    curr_prices = db.get_run_prices(current_run_id)
    prev_prices = db.get_run_prices(previous_run_id)
    curr_emag = db.get_run_emag(current_run_id)
    prev_emag = db.get_run_emag(previous_run_id)

    # Indexam (store_domain, normalized_sku) -> row
    curr_idx: Dict[Tuple[str, str], Dict[str, Any]] = {
        (r["store_domain"], r["normalized_sku"]): r for r in curr_prices
    }
    prev_idx: Dict[Tuple[str, str], Dict[str, Any]] = {
        (r["store_domain"], r["normalized_sku"]): r for r in prev_prices
    }

    alerts_dir = Path(output_root) / "live_alerts_450eur"
    alerts_dir.mkdir(parents=True, exist_ok=True)

    all_client_alerts: Dict[str, List[str]] = {}
    consolidated_blocks: List[str] = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    for client in clients:
        c_domain = client["store_domain"]
        c_name = client["store_name"]
        reserved_brands = set(client.get("exclusive_brands", []))
        client_alerts: List[str] = []

        # Gasim toate SKU-urile din brandurile rezervate acestui client
        client_skus = sorted(
            {
                r["normalized_sku"]
                for r in curr_prices
                if r["brand"] in reserved_brands
            }
        )

        for sku in client_skus:
            my_curr = curr_idx.get((c_domain, sku))
            if not my_curr:
                continue
            my_price = float(my_curr["current_price_ron"])
            brand = my_curr["brand"]

            # 1 & 2: Verificam toti concurentii pe acest SKU
            for (store_dom, s_sku), c_row in curr_idx.items():
                if s_sku != sku or store_dom == c_domain:
                    continue
                p_row = prev_idx.get((store_dom, sku))
                if not p_row:
                    continue

                prev_p = float(p_row["current_price_ron"])
                curr_p = float(c_row["current_price_ron"])
                prev_st = bool(p_row["in_stock"])
                curr_st = bool(c_row["in_stock"])

                # Regula 1: Concurent cu stoc activ scade pretul
                if curr_st and curr_p < prev_p:
                    drop_ron = prev_p - curr_p
                    diff_vs_me = my_price - curr_p
                    if diff_vs_me > 0:
                        action_line = (
                            f"👉 Acțiune recomandată: Aliniere la egalitate (Price Match la {_fmt_ron(curr_p)} RON). "
                            f"NU subcota sub {_fmt_ron(curr_p)} RON pentru a evita spirala de scădere!"
                        )
                    else:
                        action_line = (
                            f"👉 Acțiune recomandată: Menține prețul tău ({_fmt_ron(my_price)} RON) — ești în continuare sub sau egal cu ei."
                        )

                    alert_msg = (
                        f"🔴 [ALERTĂ TĂIERE PREȚ - {brand.upper()}] {sku}\n"
                        f"   • Concurent: {store_dom} (Stoc Activ)\n"
                        f"   • Preț vechi: {_fmt_ron(prev_p)} RON -> Preț NOU: {_fmt_ron(curr_p)} RON (-{_fmt_ron(drop_ron)} RON)\n"
                        f"   • Prețul tău ({c_domain}): {_fmt_ron(my_price)} RON\n"
                        f"   {action_line}"
                    )
                    client_alerts.append(alert_msg)

                # Regula 2: Concurent mai ieftin trece din in_stock=True in in_stock=False (Oportunitate de Marja)
                if prev_st and (not curr_st) and curr_p < my_price:
                    # Calculam cine este acum urmatorul cel mai ieftin cu stoc activ
                    active_others = [
                        float(r["current_price_ron"])
                        for (sd, sk), r in curr_idx.items()
                        if sk == sku and sd != c_domain and bool(r["in_stock"])
                    ]
                    next_min_active = min(active_others) if active_others else my_price
                    saved_margin = max(int(round(next_min_active - curr_p)), 0)
                    if my_price <= next_min_active:
                        opp_action = (
                            f"👉 Acțiune recomandată: 🛑 NU IEFTINI! Ești acum CEL MAI IEFTIN magazin cu marfă fizică în stoc "
                            f"— poți păstra prețul actual ({_fmt_ron(my_price)} RON) sau chiar urca marja până la {_fmt_ron(next_min_active)} RON!"
                        )
                    else:
                        opp_action = (
                            f"👉 Acțiune recomandată: 🛑 NU COBORÎ la prețul de stoc epuizat ({_fmt_ron(curr_p)} RON)! "
                            f"Pragul real cu stoc fizic este acum {_fmt_ron(next_min_active)} RON (îți salvezi +{_fmt_ron(saved_margin)} RON/buc la marjă)."
                        )
                    alert_msg = (
                        f"🟢 [OPORTUNITATE DE MARJĂ - STOC EPUIZAT CONCURENT] {brand} {sku}\n"
                        f"   • Concurentul ieftin `{store_dom}` ({_fmt_ron(curr_p)} RON) tocmai a intrat în STOC EPUIZAT / LA COMANDĂ!\n"
                        f"   • Prețul tău în stoc ({c_domain}): {_fmt_ron(my_price)} RON | Următorul concurent cu stoc real: {_fmt_ron(next_min_active)} RON\n"
                        f"   {opp_action}"
                    )
                    client_alerts.append(alert_msg)

            # Regula 3: Schimbare detinator Buy-Box pe eMAG Marketplace
            em_curr = curr_emag.get(sku)
            em_prev = prev_emag.get(sku)
            if em_curr and em_prev:
                old_seller = str(em_prev["emag_buybox_seller"])
                new_seller = str(em_curr["emag_buybox_seller"])
                old_em_p = float(em_prev["emag_lowest_price_ron"])
                new_em_p = float(em_curr["emag_lowest_price_ron"])

                if old_seller != new_seller or abs(new_em_p - old_em_p) >= 10:
                    alert_msg = (
                        f"🟠 [SCHIMBARE BUY-BOX eMAG MARKETPLACE] {brand} {sku}\n"
                        f"   • Buy-Box anterior: {old_seller} ({_fmt_ron(old_em_p)} RON)\n"
                        f"   • Buy-Box ACTUAL:   {new_seller} ({_fmt_ron(new_em_p)} RON | {em_curr['emag_offers_count']} selleri activi)\n"
                        f"   • Prețul tău pe site ({c_domain}): {_fmt_ron(my_price)} RON\n"
                        f"   👉 Acțiune recomandată: Aliniază oferta din eMAG Marketplace la {_fmt_ron(new_em_p)} RON pentru recâștigarea butonului principal."
                    )
                    client_alerts.append(alert_msg)

        all_client_alerts[c_domain] = client_alerts

        header_box = (
            f"================================================================================\n"
            f"RADAR LIVE BLACK FRIDAY (PACHET 450 €) — ALERTE INSTANT WHATSAPP / EMAIL\n"
            f"CLIENT: {c_name} ({c_domain}) | SLOT: {client['client_id']}\n"
            f"BRANDURI REZERVATE EXCLUSIV: {', '.join(client['exclusive_brands'])}\n"
            f"DATA RULARE DIFF: {now_str} (Run #{previous_run_id} -> Run #{current_run_id})\n"
            f"================================================================================\n\n"
        )
        body_text = "\n\n".join(client_alerts) if client_alerts else "Nicio modificare critică de preț/stoc în această fereastră."
        full_client_doc = header_box + body_text + "\n"

        client_file = alerts_dir / f"alerte_live_{c_domain}.txt"
        client_file.write_text(full_client_doc, encoding="utf-8")
        consolidated_blocks.append(full_client_doc)

    all_file = alerts_dir / "ALL_VIP_ALERTS.txt"
    all_file.write_text("\n\n".join(consolidated_blocks), encoding="utf-8")
    return all_client_alerts


if __name__ == "__main__":
    db_inst = RadarDatabase()
    alerts = run_live_diff_alerts(db_inst)
    total = sum(len(v) for v in alerts.values())
    print(f"[OK] S-au generat {total} alerte live pentru cei {len(alerts)} clienti VIP.")
