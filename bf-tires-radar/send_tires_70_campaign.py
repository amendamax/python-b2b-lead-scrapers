#!/usr/bin/env python3
"""
send_tires_70_campaign.py
Outreach script for the 70 Independent Winter Tire Retailers across 7 Countries (RO, IT, DE, NL, FR, ES, UK).
Includes:
- 3 real unlocked competitor rows (Price + Stock) extracted from each store's Full_Audit_BlackFriday_<domain>.xlsx
- Direct Self-Service Instant Unlock URL: https://vasiledev.com/audit/?shop=<domain>
- 5-Day SEPA Bank Transfer on B2B Invoice option ("OK Factură" / "OK Fattura" / "OK Rechnung" / "OK Factuur" / "OK Facture" / "OK Factura" / "OK Invoice")
- Strict 95–125s pacing with 2-send Zoho / 1-send Gmail rotation.
"""

from __future__ import annotations

import argparse
import email.utils
import io
import json
import random
import smtplib
import ssl
import sys
import time
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any, Dict, List, Tuple

import openpyxl

from tires_70_config import LOCALE_BY_CC, TIRES_PRICING_BY_CC, TIRES_STORES_BY_CC

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DESKTOP_DIR = Path(r"C:\Users\bratu\Desktop")
LOG_PATH = DESKTOP_DIR / "Tires_70_Campaign_Log_2026-11-02.json"

ZOHO_CFG = {
    "name": "ZOHO",
    "host": "smtp.zoho.eu",
    "port": 465,
    "user": "amendamax@vasiledev.com",
    "pass": "Ari2Nicu!",
    "msgid_domain": "vasiledev.com",
}
GMAIL_CFG = {
    "name": "GMAIL",
    "host": "smtp.gmail.com",
    "port": 465,
    "user": "amendamax@gmail.com",
    "pass": "wbdtsxzkryfekhhx",
    "msgid_domain": "gmail.com",
}


def extract_3_unlocked_tire_rows(xlsx_path: Path, cc: str) -> List[str]:
    wb = openpyxl.load_workbook(xlsx_path, data_only=True)
    ws = wb.worksheets[0]
    loc = LOCALE_BY_CC[cc]

    scored: List[Tuple[float, str]] = []
    for r in range(2, ws.max_row + 1):
        mpn = str(ws.cell(r, 1).value or "").strip()
        brand = str(ws.cell(r, 2).value or "").strip()
        model = str(ws.cell(r, 3).value or "").strip().split("(")[0].strip()
        our_p = str(ws.cell(r, 4).value or "").strip()
        our_st = str(ws.cell(r, 5).value or "").strip()
        min_cell = str(ws.cell(r, 16).value or "").strip()  # e.g. "439 RON (vadrexim.ro)"
        diff_cell = str(ws.cell(r, 17).value or "").replace("%", "").replace("+", "").strip()
        try:
            diff_val = float(diff_cell)
        except ValueError:
            diff_val = 0.0

        if diff_val > 1.5 and "(" in min_cell:
            min_price_part = min_cell.split("(")[0].strip()
            comp_dom = min_cell.split("(", 1)[1].rstrip(")").strip()
            line = (
                f"• [{mpn}] {brand} {model}: "
                f"dvs. {our_p} ({our_st}) vs. {min_price_part} ({loc['in_stock']} la {comp_dom} | +{diff_val:.1f}%)"
                if cc == "RO"
                else f"• [{mpn}] {brand} {model}: {our_p} ({our_st}) vs. {min_price_part} ({comp_dom} — {loc['in_stock']} | +{diff_val:.1f}%)"
            )
            scored.append((diff_val, line))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in scored[:3]]


def build_tire_email(cc: str, store: Dict[str, str], unlocked_rows: List[str]) -> Tuple[str, str, str]:
    dom = store["domain"]
    plat = store["platform"].split("/")[0].strip()
    pr = TIRES_PRICING_BY_CC[cc]
    url = f"https://vasiledev.com/audit/?shop={dom}"
    rows_txt = "\n".join(unlocked_rows)
    rows_html = "<br>".join(unlocked_rows)

    f1 = int(pr["flash_opt1"])
    f2 = int(pr["flash_opt2"])
    cur = pr["currency"]

    if cc == "RO":
        subj = f"Matrice Prețuri & Stocuri Anvelope Iarnă (3PMSF) {dom} — 3 poziții deblocate + Plată la 5 zile"
        txt = f"""Bună ziua,

Am finalizat auditul comparativ B2B de prețuri și stocuri pentru sezonul de iarnă (vârful de schimb anvelope Noiembrie – Decembrie + Black Month) pe {dom}, comparând 25 de modele 3PMSF (Continental TS 870, Michelin Alpin 6, Bridgestone Blizzak LM005, Pirelli Cinturato Winter 2, Goodyear UltraGrip 3, Hankook RS3) cu ceilalți 9 retaileri specializați din România + Compari.ro.

Iată 3 poziții complet deblocate (cu numele competitorului, preț și stoc la zi) extrase din fișierul dvs. Full_Audit_BlackFriday_{dom}.xlsx:

{rows_txt}

Puteți descărca acum întregul tabel Excel (cele 25 de modele × 10 magazine RO + foaia gata de import în {plat}):

1. Cu Factură B2B (plată prin OP / SEPA la 5 zile după recepția fișierului):
   Răspundeți direct la acest email cu „OK Factură Opțiunea 1” ({f1} {cur} — Auditul Excel complet) sau „OK Factură Opțiunea 2” ({f2} {cur} — Radar Live 30 Zile pe toată luna noiembrie, 3x/zi + alerte epuizare stoc competitori) și vă trimitem pe loc fișierul .XLSX + factura fiscală B2B (0% TVA VIES).

2. Sau descărcare instantă (Self-Service cu Card B2B / PayPal):
   {url}

Cu stimă,
Vasile Bratu
B2B E-Commerce Price & Stock Intelligence
EU VIES VAT: IT04226190041 | Garessio (CN), Italia
Tel / WhatsApp: +39 320 948 1876"""

    elif cc == "IT":
        subj = f"Matrice Prezzi & Stock Pneumatici Invernali {dom} — 3 codici CAI sbloccati + Fattura 5 gg"
        txt = f"""Buongiorno,

Abbiamo completato l'audit B2B prezzi e disponibilità per il picco del cambio gomme invernali (15 Novembre + Black Month) su {dom}, confrontando 25 codici CAI/MPN ufficiali 3PMSF (Continental TS 870, Michelin Alpin 6, Bridgestone Blizzak LM005, Pirelli Cinturato Winter 2, Goodyear, Hankook) con gli altri 9 principali rivenditori italiani + Trovaprezzi.it.

Ecco 3 righe completamente sbloccate estratte dal vostro file Full_Audit_BlackFriday_{dom}.xlsx:

{rows_txt}

Potete ricevere subito la matrice Excel completa (25 pneumatici invernali × 10 store IT + foglio pronto per importazione in {plat}):

1. Con Fattura B2B (Bonifico SEPA a 5 giorni dalla consegna del file):
   Rispondete semplicemente a questa email con «OK Fattura Opzione 1» ({f1} {cur} — Matrice Excel completa, Esente IVA art. 1 c. 54-89 L. 190/2014) oppure «OK Fattura Opzione 2» ({f2} {cur} — Radar Live 30 Giorni per tutto il mese di picco invernale, 3x/giorno + alert rotture di stock competitor) e vi inviamo subito il file .XLSX + fattura.

2. Oppure sblocco immediato Self-Service (Carta aziendale / PayPal):
   {url}

Cordiali saluti,
Vasile Bratu
B2B E-Commerce Price & Stock Intelligence
P.IVA VIES: IT04226190041 | Garessio (CN), Italia
Tel / WhatsApp: +39 320 948 1876"""

    elif cc == "DE":
        subj = f"Winterreifen Preis- & Bestandsmatrix {dom} — 3 freigeschaltete HAN/CAI + Kauf auf Rechnung"
        txt = f"""Guten Tag,

wir haben den B2B-Preis- und Bestandsabgleich zum aktuellen Winterreifen-Umrüstgeschäft (November-Peak & Black Month) für {dom} abgeschlossen (25 meistverkaufte 3PMSF-Winterreifen von Continental, Michelin, Bridgestone, Pirelli, Goodyear, Hankook im direkten Vergleich mit 9 deutschen Fachhändlern + Idealo.de).

Hier sind 3 vollständig freigeschaltete Positionen direkt aus Ihrer Datei Full_Audit_BlackFriday_{dom}.xlsx:

{rows_txt}

Sie können die komplette Excel-Matrix (alle 25 Winterreifen-SKUs × 10 DE-Shops + Direkt-Importtabelle für {plat}) wie folgt abrufen:

1. Per B2B-Rechnung (SEPA-Überweisung mit 5 Tagen Zahlungsziel nach Erhalt der Datei):
   Antworten Sie einfach kurz auf diese E-Mail mit „OK Rechnung Option 1“ ({f1} {cur} — Komplette Excel-Matrix) oder „OK Rechnung Option 2“ ({f2} {cur} — 30-Tage Live Winter-Radar über den gesamten Umrüstmonat, 3x täglich + Out-of-Stock-Alerts), und wir senden Ihnen umgehend die .XLSX-Datei samt B2B-Rechnung (0% MwSt. Reverse Charge).

2. Oder per Sofort-Download (Self-Service via Firmenkarte / PayPal):
   {url}

Mit freundlichen Grüßen
Vasile Bratu
B2B E-Commerce Price & Stock Intelligence
EU VIES USt-IdNr.: IT04226190041 | Garessio (CN), Italien
Tel / WhatsApp: +39 320 948 1876"""

    elif cc == "NL":
        subj = f"Winterbanden Prijs- & Voorraadmatrix {dom} — 3 vrijgegeven CAI-nummers + Betaling op factuur"
        txt = f"""Beste collega's,

Wij hebben de B2B prijs- en voorraadanalyse voor het winterbandenseizoen (november wisselpiek & Black Month) voor {dom} afgerond (25 3PMSF-winterbanden van Continental, Michelin, Bridgestone, Pirelli, Goodyear en Hankook vergeleken met 9 Nederlandse bandenspecialisten + Kieskeurig.nl).

Hierbij 3 volledig vrijgegeven regels uit uw bestand Full_Audit_BlackFriday_{dom}.xlsx:

{rows_txt}

U kunt de volledige Excel-matrix (alle 25 winterbanden-SKU's × 10 NL-webshops + {plat} prijsimport-tabblad) direct ontvangen:

1. Op B2B-factuur (SEPA-overschrijving binnen 5 dagen na ontvangst van het bestand):
   Reageer eenvoudig op deze e-mail met "OK Factuur Optie 1" ({f1} {cur} — Volledige Excel-matrix) of "OK Factuur Optie 2" ({f2} {cur} — 30-Dagen Live Winterbanden Radar gedurende de hele wisselmaand, 3x/dag + out-of-stock alerts), en wij sturen u direct het .XLSX-bestand en de B2B-factuur (0% btw ICP).

2. Of via directe Self-Service download (Zakelijke kaart / PayPal):
   {url}

Met vriendelijke groet,
Vasile Bratu
B2B E-Commerce Price & Stock Intelligence
EU VIES BTW-nr.: IT04226190041 | Garessio (CN), Italië
Tel / WhatsApp: +39 320 948 1876"""

    elif cc == "FR":
        subj = f"Matrice Prix & Stocks Pneus Hiver (Loi Montagne) {dom} — 3 codes CAI débloqués + Facture B2B"
        txt = f"""Bonjour,

Nous avons finalisé l'audit comparatif B2B des prix et stocks pour le pic Pneus Hiver / Loi Montagne (entrée en vigueur le 1er novembre + Black Month) sur {dom}, portant sur 25 références 3PMSF (Continental TS 870, Michelin Alpin 6, Bridgestone Blizzak LM005, Pirelli, Goodyear, Hankook) face à 9 spécialistes français + Idealo.fr.

Voici 3 lignes entièrement débloquées extraites de votre fichier Full_Audit_BlackFriday_{dom}.xlsx :

{rows_txt}

Vous pouvez obtenir la matrice Excel complète (les 25 pneus hiver × 10 sites FR + onglet d'import direct pour {plat}) :

1. Sur Facture B2B (virement SEPA à 5 jours après réception du fichier) :
   Répondez simplement à cet e-mail avec « OK Facture Option 1 » ({f1} {cur} — Matrice Excel complète) ou « OK Facture Option 2 » ({f2} {cur} — Radar Live 30 Jours sur tout le mois de novembre, 3x/jour + alertes ruptures de stock concurrents) et nous vous envoyons immédiatement le fichier .XLSX + la facture B2B (0% TVA autoliquidation).

2. Ou par téléchargement immédiat en libre-service (Carte B2B / PayPal) :
   {url}

Cordialement,
Vasile Bratu
B2B E-Commerce Price & Stock Intelligence
N° TVA VIES : IT04226190041 | Garessio (CN), Italie
Tél / WhatsApp : +39 320 948 1876"""

    elif cc == "ES":
        subj = f"Matriz de Precios y Stock Neumáticos Invierno {dom} — 3 códigos CAI desbloqueados + Factura B2B"
        txt = f"""Hola,

Hemos completado la auditoría comparativa B2B de precios y stock para la campaña de Neumáticos de Invierno (3PMSF) y Black Month en {dom}, comparando 25 referencias clave (Continental TS 870, Michelin Alpin 6, Bridgestone Blizzak LM005, Pirelli, Goodyear, Hankook) frente a otros 9 especialistas en España + Idealo.es.

Aquí tiene 3 filas totalmente desbloqueadas extraídas de su archivo Full_Audit_BlackFriday_{dom}.xlsx:

{rows_txt}

Puede recibir ahora mismo la matriz Excel completa (las 25 referencias × 10 tiendas ES + pestaña de importación directa para {plat}):

1. Con Factura B2B (transferencia SEPA a 5 días tras recibir el archivo):
   Responda simplemente a este correo con «OK Factura Opción 1» ({f1} {cur} — Matriz Excel completa) u «OK Factura Opción 2» ({f2} {cur} — Radar Live 30 Días durante todo el mes de campaña invernal, 3x/día + alertas de rotura de stock), y le enviaremos al instante el archivo .XLSX junto con la factura B2B (0% IVA ROI/VIES).

2. O mediante descarga inmediata en autoservicio (Tarjeta B2B / PayPal):
   {url}

Atentamente,
Vasile Bratu
B2B E-Commerce Price & Stock Intelligence
NIF-IVA VIES: IT04226190041 | Garessio (CN), Italia
Tel / WhatsApp: +39 320 948 1876"""

    else:  # UK
        subj = f"Winter Tyres Price & Stock Matrix for {dom} — 3 unlocked MPNs + 5-Day B2B Invoice"
        txt = f"""Hello,

We have completed the Winter Tyre Season & Black Month B2B price and stock benchmark for {dom}, comparing 25 high-volume 3PMSF winter tyre SKUs (Continental TS 870, Michelin Alpin 6, Bridgestone Blizzak LM005, Pirelli Cinturato Winter 2, Goodyear UltraGrip 3, Hankook RS3) against 9 UK tyre specialists + PriceRunner UK.

Here are 3 fully unlocked competitor rows extracted directly from your file Full_Audit_BlackFriday_{dom}.xlsx:

{rows_txt}

You can access the complete Excel matrix (all 25 winter tyre SKUs × 10 UK retailers + direct {plat} price import sheet) in two ways:

1. By 5-Day B2B Invoice (Bank Transfer after receiving the file):
   Simply reply to this email with "OK Invoice Option 1" (£{f1} {cur} — Full Excel Matrix) or "OK Invoice Option 2" (£{f2} {cur} — 30-Day Live Winter Tyre Radar across November, 3x daily + competitor out-of-stock alerts), and we will immediately email you the unlocked .XLSX file and commercial B2B invoice (0% VAT reverse charge).

2. Or via Instant Self-Service Unlock (Corporate Card / PayPal):
   {url}

Best regards,
Vasile Bratu
B2B E-Commerce Price & Stock Intelligence
EU VIES VAT: IT04226190041 | Garessio (CN), Italy
Tel / WhatsApp: +39 320 948 1876"""

    html_paragraphs = []
    for p in txt.split("\n\n"):
        p_clean = p.replace("\n", "<br>")
        if url in p_clean:
            p_clean = p_clean.replace(
                url,
                f'<a href="{url}" style="color:#1d4ed8;font-weight:bold;text-decoration:underline;">{url}</a>',
            )
        if p.startswith("• ["):
            html_paragraphs.append(
                f'<div style="background:#f8fafc;border-left:4px solid #1e3a8a;padding:12px 14px;margin:12px 0;font-family:Consolas,monospace;font-size:13px;line-height:1.6;">{rows_html}</div>'
            )
        else:
            html_paragraphs.append(f"<p style='margin:0 0 12px 0;'>{p_clean}</p>")

    html = (
        '<div style="font-family:Segoe UI,Arial,sans-serif;font-size:14px;color:#0f172a;line-height:1.55;max-width:680px;">'
        + "".join(html_paragraphs)
        + "</div>"
    )
    return subj, txt, html


def send_via_smtp(cfg: Dict[str, Any], to_addr: str, subj: str, txt: str, html: str) -> None:
    msg = MIMEMultipart("alternative")
    msg["From"] = f"Vasile Bratu | B2B Price Intelligence <{cfg['user']}>"
    msg["To"] = to_addr
    msg["Reply-To"] = "amendamax@vasiledev.com"
    msg["Subject"] = subj
    msg["Date"] = email.utils.formatdate(localtime=True)
    msg["Message-ID"] = email.utils.make_msgid(domain=cfg["msgid_domain"])
    msg.attach(MIMEText(txt, "plain", "utf-8"))
    msg.attach(MIMEText(html, "html", "utf-8"))

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=ctx, timeout=30) as server:
        server.login(cfg["user"], cfg["pass"])
        server.sendmail(cfg["user"], [to_addr], msg.as_string())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Verify all 70 emails without sending")
    args = ap.parse_args()

    # Build ordered list of 70 stores interleaved across countries so no single TLD gets burst traffic
    all_targets: List[Tuple[str, Dict[str, str]]] = []
    country_order = ["RO", "IT", "DE", "NL", "FR", "ES", "UK"]
    for i in range(10):
        for cc in country_order:
            all_targets.append((cc, TIRES_STORES_BY_CC[cc][i]))

    print(f"Total Winter Tire targets prepared: {len(all_targets)}")

    if args.dry_run:
        for idx, (cc, st) in enumerate(all_targets, start=1):
            dom = st["domain"]
            xlsx_path = DESKTOP_DIR / f"BF_Tires_Radar_{cc}_Output" / f"Full_Audit_BlackFriday_{dom}.xlsx"
            unlocked = extract_3_unlocked_tire_rows(xlsx_path, cc)
            assert len(unlocked) == 3, f"Expected 3 unlocked rows for {dom}, got {len(unlocked)}"
            subj, txt, _ = build_tire_email(cc, st, unlocked)
            if idx <= 7:
                print(f"\n--- DRY RUN [{idx}/70] ({cc}) {dom} -> {st['email']} ---")
                print(f"Subject: {subj}")
                for u in unlocked:
                    print(f"  {u}")
        print(f"\nDRY RUN COMPLETE: 70/70 Winter Tire outreach emails verified with 3 unlocked rows each.")
        return

    sent_log: List[Dict[str, Any]] = []
    if LOG_PATH.exists():
        try:
            sent_log = json.loads(LOG_PATH.read_text(encoding="utf-8"))
        except Exception:
            sent_log = []
    already_sent = {e["domain"] for e in sent_log if e.get("status") == "SENT_OK"}

    # Wait for Monday 48 Follow-up campaign to reach 48/48 before opening SMTP connections
    monday_log = DESKTOP_DIR / "Monday_48_Unlocked_Followup_Log_2026-11-02.json"
    while monday_log.exists():
        try:
            m_entries = json.loads(monday_log.read_text(encoding="utf-8"))
            if len(m_entries) >= 48:
                print("Monday 48 Follow-up completed (48/48). Pausing 90s before starting Winter Tires 70 campaign...")
                time.sleep(90.0)
                break
            print(f"Waiting for Monday 48 Follow-up ({len(m_entries)}/48) to finish...")
        except Exception:
            pass
        time.sleep(25.0)

    for idx, (cc, st) in enumerate(all_targets, start=1):
        dom = st["domain"]
        if dom in already_sent:
            print(f"[{idx}/70] SKIP already sent: {dom}")
            continue

        xlsx_path = DESKTOP_DIR / f"BF_Tires_Radar_{cc}_Output" / f"Full_Audit_BlackFriday_{dom}.xlsx"
        unlocked = extract_3_unlocked_tire_rows(xlsx_path, cc)
        subj, txt, html = build_tire_email(cc, st, unlocked)

        primary = ZOHO_CFG if (idx % 3 != 0) else GMAIL_CFG
        fallback = GMAIL_CFG if primary["name"] == "ZOHO" else ZOHO_CFG

        used_prov = primary["name"]
        status = "SENT_OK"
        err_msg = ""
        try:
            send_via_smtp(primary, st["email"], subj, txt, html)
        except Exception as e1:
            try:
                used_prov = fallback["name"]
                send_via_smtp(fallback, st["email"], subj, txt, html)
            except Exception as e2:
                status = "ERROR"
                err_msg = f"{primary['name']}: {e1} | {fallback['name']}: {e2}"

        entry = {
            "idx": idx,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cc": cc,
            "domain": dom,
            "to": st["email"],
            "subject": subj,
            "provider": used_prov,
            "status": status,
            "error": err_msg,
        }
        sent_log.append(entry)
        LOG_PATH.write_text(json.dumps(sent_log, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{idx}/70] {status} ({used_prov}) | {cc} {dom} -> {st['email']}")

        if idx < len(all_targets):
            time.sleep(random.uniform(95.0, 125.0))


if __name__ == "__main__":
    main()
