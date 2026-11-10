#!/usr/bin/env python3
"""
send_friday_flash_210.py
Trimite follow-up-ul scurt de Vineri (fara atasament = 99% Primary Inbox, zero caractere AI)
catre magazinele B2B din cele 3 campanii (Solar 70 + Scule Calup 1 + Scule Calup 2),
cu linkul personalizat de Self-Checkout PayPal / Card si descarcare automata pe loc:
  https://vasiledev.com/audit/?shop=<domain>

Tarife Varianta B (Friday Pre-Black-Friday Self-Service Unlock, valabil pana Duminica 1 Noiembrie):
  - RO: 79 EUR (redus de la 150 EUR)
  - UK: £129 (redus de la £295)
  - DE, AT, NL, BE, IT, FR, ES: 149 EUR (redus de la 350 EUR)
"""

from __future__ import annotations

import argparse
import json
import random
import smtplib
import ssl
import sys
import time
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path
from typing import Any, Dict, List, Set

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
MANIFEST_PATH = HERE / "portal_210_manifest.json"
LOG_PATH = Path(r"C:\Users\bratu\Desktop\Friday_Flash_SelfCheckout_Log_2026-10-30.json")

# Exclude stores that politely declined or had hard domain issues
DO_NOT_CONTACT_DOMAINS: Set[str] = {
    "atelierultau.ro",  # Replied: "avem si noi dezvoltatorul nostru"
    "ase-energy.com",   # 451 4.4.4 tenant delay in Gmail
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


def build_subject_and_body(item: Dict[str, Any]) -> tuple[str, str]:
    dom = item["domain"]
    lang = item["lang"]
    skus = item["sku_count"]
    url = f"https://vasiledev.com/audit/?shop={dom}"
    orig_subj = item.get("orig_subject", "").strip()

    if lang == "ro":
        subj = f"Re: {orig_subj}" if orig_subj else f"Acces direct tabel complet Black Friday pentru {dom} (79 EUR azi)"
        body = (
            f"Bună ziua,\n\n"
            f"Revin cu o notă scurtă înainte de weekend și de startul campaniilor de pe 1 noiembrie: "
            f"pentru magazinele care vor să își ajusteze prețurile azi fără să mai aștepte facturarea manuală prin contabilitate, "
            f"am activat descărcarea automată pe loc a fișierului complet Full_Audit_BlackFriday_{dom}.xlsx "
            f"({skus} modele verificate + foaia a 2-a gata de import prețuri).\n\n"
            f"Până duminică seara îl puteți debloca și descărca instant cu cardul firmei sau PayPal la tariful redus self-service "
            f"de 79 EUR (în loc de 150 EUR), cu factura fiscală B2B 0% TVA generată automat pe ecran:\n"
            f"{url}\n\n"
            f"Spor la vânzări de Black Friday,\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (EU VAT: IT04226190041)\n"
            f"Tel: +39 320 948 1876 | amendamax@vasiledev.com"
        )
    elif lang == "de":
        subj = f"AW: {orig_subj}" if orig_subj else f"Direkt-Download Black-Friday Preis- & Bestandsmatrix für {dom}"
        body = (
            f"Guten Tag,\n\n"
            f"kurzes Update vor dem Wochenende und dem Start der Black-Friday-Aktionswochen am 1. November: "
            f"Falls Sie Ihre Preise noch heute ohne manuellen Rechnungslauf über die Buchhaltung abgleichen möchten, "
            f"habe ich Ihre vollständige Auswertung Full_Audit_BlackFriday_{dom}.xlsx ({skus} geprüfte MPN-Modelle inkl. Shop-Importblatt) "
            f"für den automatischen Direkt-Download freigeschaltet.\n\n"
            f"Bis Sonntagabend können Sie die komplette Excel-Datei samt automatischer 0%-USt.-B2B-Rechnung (Reverse-Charge) "
            f"direkt per PayPal oder Firmen-Kreditkarte zum Self-Service-Tarif von 149,00 EUR netto (statt 350,00 EUR) herunterladen:\n"
            f"{url}\n\n"
            f"Beste Grüße\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (EU USt-IdNr.: IT04226190041)\n"
            f"Tel: +39 320 948 1876 | amendamax@vasiledev.com"
        )
    elif lang == "nl":
        subj = f"Re: {orig_subj}" if orig_subj else f"Directe download Black Friday prijs- & voorraadmatrix voor {dom}"
        body = (
            f"Goedemiddag,\n\n"
            f"Korte aanvulling voor het weekend en de start van de Black Friday-campagnes op 1 november: "
            f"voor webshops die hun prijzen vandaag direct willen bijwerken zonder handmatige facturatie vooraf, "
            f"staat het volledige bestand Full_Audit_BlackFriday_{dom}.xlsx ({skus} gecontroleerde MPN-modellen + importtabblad) "
            f"nu klaar voor directe download.\n\n"
            f"Tot zondagavond kunt u de complete Excel-matrix inclusief automatische 0% btw B2B-factuur direct ontgrendelen "
            f"via PayPal of zakelijke kaart tegen het self-service tarief van 149,00 EUR excl. btw (i.p.v. 350,00 EUR):\n"
            f"{url}\n\n"
            f"Met vriendelijke groet,\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (EU-btw-nr.: IT04226190041)\n"
            f"Tel: +39 320 948 1876 | amendamax@vasiledev.com"
        )
    elif lang == "it":
        subj = f"R: {orig_subj}" if orig_subj else f"Download immediato matrice completa Black Friday per {dom}"
        body = (
            f"Buongiorno,\n\n"
            f"un rapido aggiornamento prima del weekend e dell'avvio delle promozioni del 1° novembre: "
            f"per consentirvi di verificare e allineare i listini già oggi senza attendere la fatturazione manuale, "
            f"ho attivato il download automatico immediato del file completo Full_Audit_BlackFriday_{dom}.xlsx "
            f"({skus} codici MPN verificati + secondo foglio pronto per importazione listino).\n\n"
            f"Fino a domenica sera potete sbloccare e scaricare istantaneamente l'intera matrice Excel + Fattura B2B esente IVA "
            f"tramite PayPal o Carta Aziendale alla tariffa self-service di 149,00 EUR (anziché 350,00 EUR):\n"
            f"{url}\n\n"
            f"Cordiali saluti,\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (P.IVA: IT04226190041)\n"
            f"Tel: +39 320 948 1876 | amendamax@vasiledev.com"
        )
    elif lang == "es":
        subj = f"Re: {orig_subj}" if orig_subj else f"Descarga directa matriz completa Black Friday para {dom}"
        body = (
            f"Buenos días,\n\n"
            f"Una nota rápida antes del fin de semana y del arranque de las campañas del 1 de noviembre: "
            f"para que podáis revisar y ajustar precios hoy mismo sin esperar trámites de facturación manual, "
            f"he habilitado la descarga automática inmediata del archivo completo Full_Audit_BlackFriday_{dom}.xlsx "
            f"({skus} referencias MPN verificadas + segunda pestaña lista para importación en tienda).\n\n"
            f"Hasta el domingo por la noche podéis desbloquear y descargar al instante el Excel completo + Factura B2B 0% IVA "
            f"con PayPal o tarjeta corporativa a la tarifa self-service de 149,00 EUR (en lugar de 350,00 EUR):\n"
            f"{url}\n\n"
            f"Un cordial saludo,\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (NIF-IVA UE: IT04226190041)\n"
            f"Tel: +39 320 948 1876 | amendamax@vasiledev.com"
        )
    elif lang == "fr":
        subj = f"Re: {orig_subj}" if orig_subj else f"Téléchargement direct matrice complète Black Friday pour {dom}"
        body = (
            f"Bonjour,\n\n"
            f"Un court message avant le week-end et le lancement des opérations Black Friday du 1er novembre : "
            f"pour vous permettre d'ajuster vos tarifs dès aujourd'hui sans délai de facturation manuelle, "
            f"j'ai activé le téléchargement automatique immédiat de votre fichier complet Full_Audit_BlackFriday_{dom}.xlsx "
            f"({skus} références MPN vérifiées + second onglet prêt pour l'importation).\n\n"
            f"Jusqu'à dimanche soir, vous pouvez débloquer et télécharger instantanément la matrice Excel complète + Facture B2B 0 % TVA "
            f"par PayPal ou carte bancaire entreprise au tarif self-service de 149,00 EUR HT (au lieu de 350,00 EUR) :\n"
            f"{url}\n\n"
            f"Bien cordialement,\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (TVA VIES : IT04226190041)\n"
            f"Tél : +39 320 948 1876 | amendamax@vasiledev.com"
        )
    else:  # en (UK)
        subj = f"Re: {orig_subj}" if orig_subj else f"Instant download: Full Black Friday Price & Stock Matrix for {dom}"
        body = (
            f"Good afternoon,\n\n"
            f"Quick note ahead of the weekend and Monday's November Black Friday launches: "
            f"for teams wanting to review and adjust pricing today without waiting on manual invoice processing, "
            f"I have enabled instant self-service download for your complete file Full_Audit_BlackFriday_{dom}.xlsx "
            f"({skus} verified manufacturer MPNs + Sheet 2 shop import matrix).\n\n"
            f"Until Sunday midnight you can unlock and download the full Excel dataset + automated 0% VAT B2B Commercial Invoice "
            f"instantly via PayPal or corporate card at the self-service rate of £129.00 (reduced from £295.00):\n"
            f"{url}\n\n"
            f"Kind regards,\n"
            f"Vasile Bratu\n"
            f"VasileDev Group (VAT Reg: IT04226190041)\n"
            f"Tel: +39 320 948 1876 | amendamax@vasiledev.com"
        )
    return subj, body


def prioritize_stores(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # Warm replies & highest-PayPal-adoption markets first!
    priority_domains = {"rebacas.com": 0, "lefeld.de": 1}
    cc_rank = {"DE": 2, "NL": 3, "AT": 4, "UK": 5, "BE": 6, "IT": 7, "RO": 8, "ES": 9, "FR": 10}
    filtered = [x for x in items if x["domain"] not in DO_NOT_CONTACT_DOMAINS]
    filtered.sort(key=lambda x: (priority_domains.get(x["domain"], 99), cc_rank.get(x["cc"], 50), x["domain"]))
    return filtered


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
    ap.add_argument("--dry-run", action="store_true", help="Preview prioritized emails without sending")
    ap.add_argument("--limit", type=int, default=210, help="Max emails to send in this run")
    ap.add_argument("--min-delay", type=int, default=95, help="Min jitter seconds between emails")
    ap.add_argument("--max-delay", type=int, default=125, help="Max jitter seconds between emails")
    args = ap.parse_args()

    items = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    ordered = prioritize_stores(items)

    already_sent: Set[str] = set()
    log_entries: List[Dict[str, Any]] = []
    if LOG_PATH.exists():
        try:
            log_entries = json.loads(LOG_PATH.read_text(encoding="utf-8"))
            already_sent = {e["domain"] for e in log_entries if e.get("status") == "SENT_OK"}
        except Exception:
            log_entries = []

    todo = [x for x in ordered if x["domain"] not in already_sent][: args.limit]
    print(f"Total eligible: {len(ordered)} | Already sent: {len(already_sent)} | Queued now: {len(todo)}")

    if args.dry_run:
        for idx, it in enumerate(todo[:8], 1):
            subj, body = build_subject_and_body(it)
            print(f"\n--- DRY-RUN #{idx}: {it['domain']} ({it['cc']}/{it['lang']}) -> {it['sent_to']} ---")
            print(f"SUBJ: {subj}")
            print(body)
        return

    for idx, it in enumerate(todo, 1):
        subj, body = build_subject_and_body(it)
        # 2 Gmail : 1 Zoho rotation with instant failover to Gmail
        primary = ZOHO_CFG if (idx % 3 == 0) else GMAIL_CFG
        used_provider = primary["name"]
        status = "SENT_OK"
        err_msg = ""
        try:
            send_plain_email(primary, it["sent_to"], subj, body)
        except Exception as e1:
            if primary["name"] == "ZOHO":
                try:
                    send_plain_email(GMAIL_CFG, it["sent_to"], subj, body)
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
            "domain": it["domain"],
            "to": it["sent_to"],
            "provider": used_provider,
            "status": status,
            "checkout_url": it["checkout_url"],
            "error": err_msg,
        }
        log_entries.append(entry)
        LOG_PATH.write_text(json.dumps(log_entries, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[{idx}/{len(todo)}] {entry['timestamp']} | {it['cc']} | {it['domain']} -> {it['sent_to']} | {used_provider} | {status} {err_msg}")

        if idx < len(todo):
            wait_s = random.randint(args.min_delay, args.max_delay)
            time.sleep(wait_s)


if __name__ == "__main__":
    main()
