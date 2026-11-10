#!/usr/bin/env python3
"""
send_monday_48_unlocked.py
Trimite follow-up-ul personalizat de Luni (2 Noiembrie 2026) catre cele 48 de magazine B2B
care au accesat deja raportul pe vasiledev.com/audit/ (sau au initiat checkout-ul PayPal).

Include:
1. 3 randuri reale COMPLET DEBLOCATE (cu numele exact al concurentului si pretul lui) extrase din fisierul lor Excel,
   ca dovada de acuratete pentru managerul de achizitii;
2. Posibilitatea de livrare pe loc pe baza de Factura B2B cu plata prin Ordin de Plata / Transfer Bancar SEPA
   (doar raspunzand cu "OK Factura" / "OK Invoice", fara sa fie nevoie de card sau PayPal);
3. Linkul direct de Self-Checkout PayPal / Card pastrat activ la tariful redus.
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import random
import re
import smtplib
import ssl
import sys
import time
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import openpyxl

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_kv_bundle as bkb  # noqa: E402

MANIFEST_PATH = HERE / "portal_210_manifest.json"
KV_PAYLOAD_PATH = HERE / "kv_bulk_payload.json"
LOG_PATH = Path(r"C:\Users\bratu\Desktop\Monday_48_Unlocked_Followup_Log_2026-11-02.json")

# All 48 unique domains that opened the audit page or initiated checkout (excluding bounced outilsdespros.fr)
TARGET_48_DOMAINS: List[str] = [
    # Initiated PayPal Checkout (Top Priority!)
    "powertoolmate.co.uk",
    "e-acumulatori.ro",
    # Opened Audit Page (Ordered by country & engagement)
    "misterworker.com",
    "masterfer.it",
    "tehnicbazar.ro",
    "masif.ro",
    "verdon.ro",
    "windandsun.co.uk",
    "protrade.co.uk",
    "machinemart.co.uk",
    "datapowertools.co.uk",
    "brightontools.co.uk",
    "axminstertools.com",
    "angliatoolcentre.co.uk",
    "its.co.uk",
    "tooled-up.com",
    "callidus.shop",
    "werkzeugstore24.de",
    "tepto.de",
    "profishop.de",
    "paulimot.de",
    "offgridtec.com",
    "spiral.at",
    "schachermayer.at",
    "lagerhaus.at",
    "kaindltech.at",
    "haberkorn.com",
    "gereedschappro.nl",
    "mastermate.nl",
    "toolsvoordelig.nl",
    "toolnation.nl",
    "stroomwinkel.nl",
    "isero.nl",
    "gereedschapcentrum.nl",
    "destil.nl",
    "aic.nl",
    "lecot.be",
    "hubo.be",
    "santens.be",
    "marchandise.be",
    "georges.be",
    "claerbout.be",
    "clabots.be",
    "autosolar.es",
    "suministrostorras.com",
    "mabeo-direct.com",
    "h2r-equipements.com",
    "sider.biz",
]

CHECKOUT_INITIATED_DOMAINS: Set[str] = {
    "powertoolmate.co.uk",
    "e-acumulatori.ro",
}

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


def clean_comp_name(raw_h: str) -> str:
    s = raw_h.replace("\n", " ").strip()
    s = re.sub(r"\((Preț|Pret|Price|Prezzo|Preis|Prijs|Prix|Precio).*?\)", "", s, flags=re.IGNORECASE).strip()
    return s


def format_price_with_unit(raw_p: str, cc: str) -> str:
    s = raw_p.split("(")[0].strip()
    if not s:
        return s
    upper = s.upper()
    if any(u in upper for u in ["RON", "LEI", "EUR", "€", "GBP", "£"]):
        return s
    if cc == "RO":
        return f"{s} RON"
    if cc == "UK":
        return f"£{s}"
    return f"{s} EUR"


def extract_unlocked_rows(xlsx_b64: str, cc: str, count: int = 3) -> List[str]:
    raw_bytes = base64.b64decode(xlsx_b64)
    wb = openpyxl.load_workbook(io.BytesIO(raw_bytes), data_only=True)
    ws = wb.active
    r1_c1 = str(ws.cell(1, 1).value or "").strip().upper()
    hdr_row = 3 if r1_c1.startswith("AUDIT COMPLET") else 1
    compact_4col = hdr_row == 3
    comp_start = 5 if compact_4col else 6

    comp_headers: Dict[int, str] = {}
    for c in range(comp_start, ws.max_column + 1):
        hv = str(ws.cell(hdr_row, c).value or "").strip()
        if hv:
            cleaned = clean_comp_name(hv)
            if "." in cleaned and not any(k in cleaned.lower() for k in ["diferen", "minim", "recomand", "status", "diff"]):
                comp_headers[c] = cleaned

    candidates: List[Tuple[float, str]] = []
    for r in range(hdr_row + 1, ws.max_row + 1):
        mpn = str(ws.cell(r, 1).value or "").strip()
        if not mpn or mpn.startswith("---") or "TOTAL" in mpn.upper():
            continue
        brand = str(ws.cell(r, 2).value or "").strip()
        model = str(ws.cell(r, 3).value or "").strip()
        our_raw = str(ws.cell(r, 4).value or "").strip()
        our_num = bkb.parse_price_number(our_raw)
        if not our_num:
            continue

        best_comp = None
        best_val = None
        best_raw = None
        for c, cname in comp_headers.items():
            cv_raw = str(ws.cell(r, c).value or "").strip()
            cv_num = bkb.parse_price_number(cv_raw)
            if cv_num and cv_num < our_num * 0.98 and cv_num > our_num * 0.68:
                if best_val is None or cv_num < best_val:
                    best_val = cv_num
                    best_comp = cname
                    best_raw = cv_raw

        if best_comp and best_val is not None and best_raw is not None:
            diff_pct = round((best_val - our_num) / our_num * 100, 1)
            title = model if model.lower().startswith(brand.lower()) else f"{brand} {model}".strip()
            if len(title) > 58:
                title = title[:55] + "..."
            our_fmt = format_price_with_unit(our_raw, cc)
            comp_fmt = format_price_with_unit(best_raw, cc)
            line = f"  • [{mpn}] {title} -> {our_fmt} vs. {best_comp}: {comp_fmt} ({diff_pct}%)"
            candidates.append((diff_pct, line))

    # Sort by steepest realistic undercut (-32% to -2% first)
    candidates.sort(key=lambda x: x[0])
    if len(candidates) < count:
        for r in range(hdr_row + 1, ws.max_row + 1):
            mpn = str(ws.cell(r, 1).value or "").strip()
            if not mpn or mpn.startswith("---") or "TOTAL" in mpn.upper():
                continue
            brand = str(ws.cell(r, 2).value or "").strip()
            model = str(ws.cell(r, 3).value or "").strip()
            our_raw = str(ws.cell(r, 4).value or "").strip()
            our_num = bkb.parse_price_number(our_raw)
            if not our_num:
                continue
            for c, cname in comp_headers.items():
                cv_raw = str(ws.cell(r, c).value or "").strip()
                cv_num = bkb.parse_price_number(cv_raw)
                if cv_num and cv_num < our_num * 0.68 and cv_num > our_num * 0.40:
                    diff_pct = round((best_val - our_num) / our_num * 100, 1) if (best_val := cv_num) else -35.0
                    title = model if model.lower().startswith(brand.lower()) else f"{brand} {model}".strip()
                    if len(title) > 58:
                        title = title[:55] + "..."
                    line = f"  • [{mpn}] {title} -> {format_price_with_unit(our_raw, cc)} vs. {cname}: {format_price_with_unit(cv_raw, cc)} ({diff_pct}%)"
                    if all(mpn not in ex for _, ex in candidates):
                        candidates.append((diff_pct, line))
                        break
    return [line for _, line in candidates[:count]]


def build_email_content(item: Dict[str, Any], unlocked_lines: List[str]) -> Tuple[str, str]:
    dom = item["domain"]
    lang = item["lang"]
    skus = item["sku_count"]
    url = f"https://vasiledev.com/audit/?shop={dom}"
    samples_block = "\n".join(unlocked_lines)
    is_checkout = dom in CHECKOUT_INITIATED_DOMAINS

    if lang == "ro":
        subj = f"Re: Raportul de prețuri {dom} — 3 poziții deblocate + opțiune plată prin OP (Factură)"
        intro = (
            f"Am observat că ați accesat vineri pagina raportului pentru {dom}"
            + (" (și ați deschis fereastra de comandă, dar plata PayPal nu s-a finalizat)." if is_checkout else ".")
        )
        body = (
            f"Bună ziua,\n\n"
            f"{intro}\n\n"
            f"Pentru a vă ajuta să verificați intern calitatea datelor împreună cu responsabilul de achiziții fără nicio plată în avans cu cardul, "
            f"vă las mai jos 3 poziții complet deblocate (cu numele concurentului vizibil) extrase direct din fișierul dvs. Full_Audit_BlackFriday_{dom}.xlsx ({skus} modele verificate):\n\n"
            f"{samples_block}\n\n"
            f"Dacă preferați plata clasică prin Ordin de Plată bancar (în loc de card/PayPal), răspundeți la acest email cu un simplu «OK Factură» "
            f"(și CUI-ul firmei, dacă diferă) și vă trimit pe loc pe email fișierul Excel complet + factura fiscală B2B (79 EUR, 0% TVA intracomunitar) cu termen de plată 5 zile.\n\n"
            f"Dacă preferați descărcarea instantă cu cardul sau PayPal, linkul rămâne activ aici:\n"
            f"{url}\n\n"
            f"O săptămână excelentă,\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (EU VAT: IT04226190041)\n"
            f"Tel: +39 320 948 1876 | amendamax@vasiledev.com"
        )
    elif lang == "it":
        subj = f"R: Analisi listino {dom} — 3 righe sbloccate + opzione Bonifico su Fattura"
        body = (
            f"Buongiorno,\n\n"
            f"ho notato che venerdì avete consultato la pagina di anteprima del report per {dom}.\n\n"
            f"Per permettervi di verificare internamente la qualità dei dati con l'ufficio acquisti prima di qualsiasi pagamento, "
            f"vi riporto qui sotto 3 righe completamente in chiaro (con il nome del concorrente visibile) estratte dal vostro file Full_Audit_BlackFriday_{dom}.xlsx ({skus} codici MPN verificati):\n\n"
            f"{samples_block}\n\n"
            f"Se per la vostra amministrazione è più comodo il pagamento tramite Bonifico Bancario (anziché PayPal o carta), "
            f"rispondete pure a questa email con «OK Fattura» e vi invierò subito in allegato l'intero file Excel sbloccato insieme alla Fattura B2B (149,00 EUR, esente IVA) pagabile a 5 giorni.\n\n"
            f"In alternativa, il link per il download immediato resta attivo qui:\n"
            f"{url}\n\n"
            f"Cordiali saluti,\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (P.IVA: IT04226190041)\n"
            f"Tel: +39 320 948 1876 | amendamax@vasiledev.com"
        )
    elif lang == "de":
        subj = f"AW: Preis- & Bestandsmatrix {dom} — 3 freigeschaltete Positionen + Kauf auf Rechnung"
        body = (
            f"Guten Tag,\n\n"
            f"ich habe gesehen, dass Ihr Team am Freitag die Vorschauseite der Auswertung für {dom} aufgerufen hat.\n\n"
            f"Damit Ihr Einkauf die Datenqualität vorab ohne Kartenzahlung prüfen kann, "
            f"finden Sie hier 3 vollständig freigeschaltete Positionen (inkl. Klarnamen der Wettbewerber) direkt aus Ihrer Datei Full_Audit_BlackFriday_{dom}.xlsx ({skus} geprüfte MPN-Modelle):\n\n"
            f"{samples_block}\n\n"
            f"Falls Ihre Buchhaltung die klassische SEPA-Überweisung auf Rechnung bevorzugt (statt PayPal oder Firmenkarte), "
            f"antworten Sie einfach kurz mit «OK Rechnung» auf diese E-Mail — ich sende Ihnen dann umgehend die komplette Excel-Datei samt 0%-USt.-B2B-Rechnung (149,00 EUR netto, Zahlungsziel 5 Tage) per E-Mail zu.\n\n"
            f"Für den Sofort-Download per PayPal/Karte bleibt Ihr Link weiterhin aktiv:\n"
            f"{url}\n\n"
            f"Beste Grüße\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (EU USt-IdNr.: IT04226190041)\n"
            f"Tel: +39 320 948 1876 | amendamax@vasiledev.com"
        )
    elif lang == "nl":
        subj = f"Re: Prijsmatrix {dom} — 3 ontgrendelde regels + betaling op factuur (SEPA)"
        body = (
            f"Goedemiddag,\n\n"
            f"Ik zag dat uw team vrijdag de voorbeelpagina van het rapport voor {dom} heeft bekeken.\n\n"
            f"Om de datakwaliteit intern met inkoop te kunnen beoordelen zonder directe kaartbetaling, "
            f"vindt u hieronder 3 volledig ontgrendelde regels (inclusief naam van de concurrent) uit uw bestand Full_Audit_BlackFriday_{dom}.xlsx ({skus} gecontroleerde MPN-modellen):\n\n"
            f"{samples_block}\n\n"
            f"Geeft uw administratie de voorkeur aan betaling per bankoverschrijving op factuur (i.p.v. PayPal of kaart)? "
            f"Beantwoord deze e-mail dan kort met «OK Factuur» en ik stuur u direct het volledige Excel-bestand toe samen met de B2B-factuur (149,00 EUR excl. btw, betalingstermijn 5 dagen).\n\n"
            f"Voor directe download via PayPal of zakelijke kaart blijft uw link hier actief:\n"
            f"{url}\n\n"
            f"Met vriendelijke groet,\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (EU-btw-nr.: IT04226190041)\n"
            f"Tel: +39 320 948 1876 | amendamax@vasiledev.com"
        )
    elif lang == "fr":
        subj = f"Re: Matrice tarifaire {dom} — 3 références débloquées + paiement sur facture (SEPA)"
        body = (
            f"Bonjour,\n\n"
            f"J'ai noté que votre équipe a consulté vendredi l'aperçu du rapport pour {dom}.\n\n"
            f"Afin de vous permettre de valider la précision des relevés en interne avec votre service achats, "
            f"voici 3 lignes entièrement débloquées (avec le nom du concurrent visible) extraites de votre fichier Full_Audit_BlackFriday_{dom}.xlsx ({skus} références MPN vérifiées) :\n\n"
            f"{samples_block}\n\n"
            f"Si votre comptabilité préfère un règlement par virement bancaire SEPA sur facture (plutôt que par carte ou PayPal), "
            f"répondez simplement « OK Facture » à cet e-mail : je vous enverrai immédiatement le fichier Excel complet accompagné de la facture B2B HT (149,00 EUR HT, TVA 0 % autoliquidation, échéance 5 jours).\n\n"
            f"Le lien de téléchargement instantané reste également actif ici :\n"
            f"{url}\n\n"
            f"Bien cordialement,\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (TVA VIES : IT04226190041)\n"
            f"Tél : +39 320 948 1876 | amendamax@vasiledev.com"
        )
    elif lang == "es":
        subj = f"Re: Matriz de precios {dom} — 3 referencias desbloqueadas + pago por transferencia (Factura)"
        body = (
            f"Buenos días,\n\n"
            f"He visto que el viernes vuestro equipo consultó la página de vista previa del informe para {dom}.\n\n"
            f"Para que podáis comprobar internamente con el departamento de compras la exactitud de los datos, "
            f"os dejo a continuación 3 referencias completamente desbloqueadas (con el nombre del competidor visible) extraídas de vuestro archivo Full_Audit_BlackFriday_{dom}.xlsx ({skus} modelos MPN verificados):\n\n"
            f"{samples_block}\n\n"
            f"Si por administración preferís realizar el pago mediante transferencia bancaria SEPA con factura (en lugar de tarjeta o PayPal), "
            f"responded simplemente con «OK Factura» a este correo y os enviaré al instante el Excel completo junto con la factura B2B (149,00 EUR, 0% IVA intracomunitario, vencimiento 5 días).\n\n"
            f"Para descarga inmediata con tarjeta o PayPal, el enlace sigue activo aquí:\n"
            f"{url}\n\n"
            f"Un cordial saludo,\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (NIF-IVA UE: IT04226190041)\n"
            f"Tel: +39 320 948 1876 | amendamax@vasiledev.com"
        )
    else:  # en (UK)
        subj = f"Re: Black Friday Price Matrix for {dom} — 3 unlocked SKUs + B2B Invoice / Bank Transfer option"
        intro = (
            f"I noticed your team checked the preview page for {dom} on Friday"
            + (" (and opened the PayPal checkout window, though the payment didn't complete)." if is_checkout else ".")
        )
        body = (
            f"Good afternoon,\n\n"
            f"{intro}\n\n"
            f"So your buying team can verify the data accuracy internally before any payment, "
            f"here are 3 fully unlocked rows (with the exact competitor domain revealed) straight from your file Full_Audit_BlackFriday_{dom}.xlsx ({skus} verified MPNs):\n\n"
            f"{samples_block}\n\n"
            f"If your accounts team prefers standard B2B Invoice & Bank Transfer (rather than PayPal or corporate card checkout), "
            f"simply reply with «OK Invoice» to this email and I will send over the complete unlocked Excel dataset + 0% VAT B2B Commercial Invoice (£129.00, 5-day payment terms) right away.\n\n"
            f"Alternatively, the instant self-service download link remains active here:\n"
            f"{url}\n\n"
            f"Kind regards,\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (VAT Reg: IT04226190041)\n"
            f"Tel: +39 320 948 1876 | amendamax@vasiledev.com"
        )
    return subj, body


def send_plain_email(cfg: Dict[str, Any], to_addr: str, subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = formataddr(("Vasile Bratu", cfg["user"]))
    msg["To"] = to_addr
    msg["Reply-To"] = "amendamax@vasiledev.com"
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=cfg["msgid_domain"])
    msg["Subject"] = subject
    msg.set_content(body)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=ctx, timeout=25) as srv:
        srv.login(cfg["user"], cfg["pass"])
        srv.send_message(msg)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=48)
    ap.add_argument("--min-delay", type=int, default=85)
    ap.add_argument("--max-delay", type=int, default=115)
    args = ap.parse_args()

    manifest_map = {
        x["domain"]: x
        for x in json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    }
    kv_map = {
        x["key"]: x["value"]
        for x in json.loads(KV_PAYLOAD_PATH.read_text(encoding="utf-8"))
        if x["key"].startswith("xlsx:")
    }

    already_sent: Set[str] = set()
    log_entries: List[Dict[str, Any]] = []
    if LOG_PATH.exists():
        try:
            log_entries = json.loads(LOG_PATH.read_text(encoding="utf-8"))
            already_sent = {e["domain"] for e in log_entries if e.get("status") == "SENT_OK"}
        except Exception:
            log_entries = []

    todo_domains = [d for d in TARGET_48_DOMAINS if d in manifest_map and d not in already_sent][: args.limit]
    print(f"Target 48 stores | Already sent: {len(already_sent)} | Queued now: {len(todo_domains)}")

    if args.dry_run:
        for idx, dom in enumerate(todo_domains[:6], 1):
            it = manifest_map[dom]
            unlocked = extract_unlocked_rows(kv_map["xlsx:" + dom], it["cc"], 3)
            subj, body = build_email_content(it, unlocked)
            print(f"\n=== DRY-RUN #{idx}: {dom} ({it['cc']}/{it['lang']}) -> {it['email']} ===")
            print(f"SUBJECT: {subj}")
            print(body)
        return

    for idx, dom in enumerate(todo_domains, 1):
        it = manifest_map[dom]
        unlocked = extract_unlocked_rows(kv_map["xlsx:" + dom], it["cc"], 3)
        subj, body = build_email_content(it, unlocked)

        primary = ZOHO_CFG if (idx % 3 == 0) else GMAIL_CFG
        used_provider = primary["name"]
        status = "SENT_OK"
        err_msg = ""

        try:
            send_plain_email(primary, it["email"], subj, body)
        except Exception as e1:
            if primary["name"] == "ZOHO":
                try:
                    send_plain_email(GMAIL_CFG, it["email"], subj, body)
                    used_provider = "GMAIL_FAILOVER"
                except Exception as e2:
                    status = "ERROR"
                    err_msg = str(e2)
            else:
                status = "ERROR"
                err_msg = str(e1)

        entry = {
            "idx": len(log_entries) + 1,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cc": it["cc"],
            "lang": it["lang"],
            "domain": dom,
            "to": it["email"],
            "provider": used_provider,
            "status": status,
            "error": err_msg,
        }
        log_entries.append(entry)
        LOG_PATH.write_text(json.dumps(log_entries, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{idx}/{len(todo_domains)}] {entry['timestamp']} | {it['cc']} | {dom} -> {it['email']} | {used_provider} | {status} {err_msg}", flush=True)

        if idx < len(todo_domains):
            time.sleep(random.randint(args.min_delay, args.max_delay))


if __name__ == "__main__":
    main()
