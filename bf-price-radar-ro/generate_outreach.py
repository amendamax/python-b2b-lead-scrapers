"""
generate_outreach.py
Generatorul de mesaje umane B2B (Email + WhatsApp) pentru cele 10 magazine tinta,
populate dinamic cu cifrele reale extrase din baza de date pentru fiecare magazin in parte.
Respecta strict regulile ANTI-ROBOT (persoana I singular, fara clisee de agentie/AI).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from db import RadarDatabase
from generate_mirrors import analyze_sku_for_store, build_cross_market_polars_df


def _fmt_ron(val: float) -> str:
    """Formateaza suma in RON fara zecimale inutile (ex: 6.450)."""
    return f"{int(round(val)):,}".replace(",", ".")


def generate_store_outreach_files(
    store_domain: str,
    store_profile: Dict[str, Any],
    analyzed_items: List[Dict[str, Any]],
    output_root: str | Path = "output",
) -> Dict[str, str]:
    """
    Genereaza in `/output/{store_domain}/mesaj_contact.txt` (si `/output/{store_domain}/mesaj_whatsapp.txt`)
    varianta de Email (Subiect + Corp) si varianta scurta de WhatsApp cu datele reale ale magazinului.
    """
    store_dir = Path(output_root) / store_domain
    store_dir.mkdir(parents=True, exist_ok=True)

    detected_platform = store_profile.get("detected_platform", "Custom")
    store_name = store_profile.get("store_name", store_domain)
    contact_email = store_profile.get("email", f"office@{store_domain}")
    contact_phone = store_profile.get("phone", "N/A")
    company_name = store_profile.get("company_name", "")
    cui = store_profile.get("cui", "")

    # Selectam cele mai dureroase 2 produse unde {store_domain} are stoc activ dar e mai scump (+3%..+45%) decat un rival cu stoc activ
    overpriced = sorted(
        [
            it
            for it in analyzed_items
            if it["my_in_stock"] and 3.0 <= it["diff_vs_active_pct"] <= 45.0 and not it["is_margin_opportunity"]
        ],
        key=lambda x: x["diff_vs_active_ron"],
        reverse=True,
    )
    if len(overpriced) < 2:
        extra_op = sorted(
            [
                it
                for it in analyzed_items
                if it["my_in_stock"] and 0.5 <= it["diff_vs_active_pct"] <= 45.0 and it not in overpriced
            ],
            key=lambda x: x["diff_vs_active_ron"],
            reverse=True,
        )
        overpriced.extend(extra_op)

    # Selectam produsul unde rivalii mai ieftini sunt in Stoc Epuizat / La comanda (oportunitate de marja)
    margin_opps = sorted(
        [it for it in analyzed_items if it["my_in_stock"] and it["is_margin_opportunity"]],
        key=lambda x: (x["my_price"] - (x["cheapest_oos_price"] or x["my_price"])),
        reverse=True,
    )

    prod_1 = overpriced[0] if len(overpriced) >= 1 else analyzed_items[0]
    fallback_p2 = analyzed_items[1] if len(analyzed_items) >= 2 else analyzed_items[0]
    # Cautam ca produsul 2 sa fie de preferinta dintr-un al doilea brand pentru diversitate in subiect
    prod_2 = next(
        (it for it in overpriced[1:] if it["brand"] != prod_1["brand"]),
        overpriced[1] if len(overpriced) >= 2 else fallback_p2,
    )
    prod_oos = margin_opps[0] if margin_opps else analyzed_items[-1]

    brand_1 = prod_1["brand"]
    brand_2 = prod_2["brand"] if prod_2["brand"] != brand_1 else "Pylontech / Huawei"

    produs_1_nume = f"{prod_1['brand']} {prod_1['normalized_sku']}"
    produs_1_pret_client = _fmt_ron(prod_1["my_price"])
    produs_1_pret_rival = _fmt_ron(prod_1["min_active_price"])
    produs_1_diferenta_ron = _fmt_ron(prod_1["diff_vs_active_ron"])
    rival_1_nume = prod_1["min_active_store"]

    produs_2_nume = f"{prod_2['brand']} {prod_2['normalized_sku']}"
    produs_2_diferenta_ron = _fmt_ron(prod_2["diff_vs_active_ron"])

    produs_stoc_epuizat_rival = f"{prod_oos['brand']} {prod_oos['normalized_sku']}"

    email_subject = (
        f"Prețurile la {brand_1} și {brand_2} pe {store_domain} vs. concurența (date extrase azi dimineață)"
    )

    email_body = f"""Subiect: {email_subject}

Salut,

Sunt Vasile, dezvoltator Python specializat pe extracție automată de date și sisteme de monitorizare prețuri.

Cum săptămâna viitoare începe nebunia cu Black Friday, am pus azi dimineață un script făcut de mine să scaneze la sânge prețurile și stocurile reale pe cele 10 magazine principale de fotovoltaice din România (`esolar, e-acumulatori, genway, ecosolaris, solartech, voltexpert, novasol, solargreen` etc.), strict pe invertoare și baterii.

M-am uitat pe rezultatele scoase pentru **{store_domain}** și am zis să vă dau un semn scurt, fiindcă sunt câteva diferențe mari unde pierdeți comenzi azi fără motiv:

1. La **{produs_1_nume}**, voi îl aveți azi la **{produs_1_pret_client} RON**, în timp ce pe `{rival_1_nume}` este în stoc real la **{produs_1_pret_rival} RON** (sunteți cu **+{produs_1_diferenta_ron} RON** mai sus pe exact același cod de producător).
2. La **{produs_2_nume}**, aveți o diferență de **+{produs_2_diferenta_ron} RON** față de cel mai mic preț în stoc din piață (verificat azi pe toate cele 10 magazine).
3. În schimb — o veste bună pentru marja voastră — la **{produs_stoc_epuizat_rival}**, concurenții care afișează preț mic au intrat deja în **Stoc Epuizat / La comandă**, deci acolo chiar nu are rost să lăsați din preț de Black Friday, că sunteți printre singurii cu marfă fizică.

V-am atașat un Excel scurt cu 8 produse din catalogul vostru extrase acum două ore, ca să vedeți exact cum arată datele.

Pentru că am deja toată infrastructura pornită pe cele 10 magazine (și am văzut din cod că site-ul vostru rulează pe **{detected_platform}**, deci pot scoate tabelele direct pe codurile voastre interne de produs), vă pot ajuta în două moduri luna asta:

- **Varianta 1 (Auditul Complet la zi – 150 €):** Vă trimit azi tabelul complet cu toate invertoarele și bateriile comune comparate între voi și ceilalți 9 concurenți (prețuri + media pieței + cine are stoc real și cine vinde doar pe hârtie).
- **Varianta 2 (Radar Live de Black Friday pe 30 de zile – 450 €):** Scriptul meu verifică piața de 3 ori pe zi toată luna noiembrie și vă dă alertă direct pe WhatsApp sau Email în secunda în care un concurent taie prețul la un produs sau rămâne fără stoc (ca să știți când să vă aliniați la preț fără să vindeți în pierdere și când puteți păstra marja sus).

*O singură mențiune cinstită:* tabelul de 150 € îl pot da oricui, dar **Radarul Live (450 €) îl activez pentru maximum 3 magazine din România**, iar fiecare dintre cele 3 își blochează exclusiv alertele prioritare pe 2 branduri principale (ex: Deye + Pylontech sau Huawei + Victron), ca să nu vă bateți cap în cap pe aceleași alerte.

Aruncați un ochi pe fișierul atașat și dați-mi un semn aici sau pe WhatsApp dacă vreți să vă trimit toată matricea sau să blocăm două branduri pentru voi înainte să înceapă reducerile.

Spor la vânzări,
**Vasile Bratu**
Python Automation & Price Intelligence (Facturare B2B intracomunitară 0% TVA)
[Telefon / WhatsApp]"""

    whatsapp_text = f"""Salut! Sunt Vasile (lucrez pe automatizări Python și analiză de prețuri). Am rulat azi dimineață un script care a comparat la leu toate prețurile și stocurile la invertoare și baterii între **{store_domain}** și celelalte 9 magazine principale de fotovoltaice din RO (`esolar, e-acumulatori, genway, ecosolaris, solartech, voltexpert, novasol, solargreen`), înainte de Black Friday.

Am văzut că la **{produs_1_nume}** sunteți azi cu **+{produs_1_diferenta_ron} RON** peste `{rival_1_nume}` (care are stoc activ), iar la **{produs_2_nume}** cu **+{produs_2_diferenta_ron} RON**. În schimb, aveți câteva produse unde concurenții ieftini tocmai au rămas fără stoc, deci nu trebuie să tăiați din marjă.

V-am trimis acum pe email un tabel Excel cu 8 exemple concrete din magazinul vostru. Îmi ziceți dacă vreți să vă arunc fișierul demonstrativ și aici pe WhatsApp ca să-l vedeți direct pe telefon?"""

    combined_content = f"""================================================================================
DESTINATAR B2B: {store_name} ({store_domain})
COMPANIE:       {company_name} | CUI: {cui}
PLATFORMA:      {detected_platform}
EMAIL CONTACT:  {contact_email}
TELEFON:        {contact_phone}
ATAȘAMENT:      Teaser_BlackFriday_{store_domain}.xlsx
================================================================================

--------------------------------------------------------------------------------
[1] VARIANTA EMAIL B2B
--------------------------------------------------------------------------------
{email_body}

--------------------------------------------------------------------------------
[2] VARIANTA WHATSAPP DIRECT
--------------------------------------------------------------------------------
{whatsapp_text}
"""

    contact_file = store_dir / "mesaj_contact.txt"
    wa_file = store_dir / "mesaj_whatsapp.txt"

    contact_file.write_text(combined_content, encoding="utf-8")
    wa_file.write_text(whatsapp_text, encoding="utf-8")

    return {
        "store_domain": store_domain,
        "contact_file": str(contact_file),
        "whatsapp_file": str(wa_file),
        "email_subject": email_subject,
    }


def generate_all_outreach(
    db: RadarDatabase,
    run_id: int,
    output_root: str | Path = "output",
) -> List[Dict[str, str]]:
    """Genereaza fisierele de outreach B2B pentru toate cele 10 magazine."""
    price_records = db.get_run_prices(run_id)
    emag_map = db.get_run_emag(run_id)
    profiles = db.get_store_profiles()

    df = build_cross_market_polars_df(price_records, emag_map)
    all_stores = sorted(df["store_domain"].unique().to_list())
    all_skus = df["normalized_sku"].unique(maintain_order=True).to_list()

    results = []
    for store_domain in all_stores:
        analyzed = []
        for sku in all_skus:
            res = analyze_sku_for_store(df, store_domain, sku)
            if res:
                analyzed.append(res)

        prof = profiles.get(store_domain, {"domain": store_domain, "detected_platform": "Custom"})
        out_info = generate_store_outreach_files(store_domain, prof, analyzed, output_root=output_root)
        results.append(out_info)

    return results


if __name__ == "__main__":
    db_inst = RadarDatabase()
    latest = db_inst.get_latest_run_id()
    if latest:
        res = generate_all_outreach(db_inst, latest)
        print(f"[OK] S-au generat mesajele B2B (Email + WhatsApp) pentru {len(res)} magazine.")
