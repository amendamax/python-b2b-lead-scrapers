#!/usr/bin/env python3
"""
send_zoho_italia.py
Trimite automat prin Zoho Mail SMTP (smtp.zoho.eu:465, amendamax@vasiledev.com):
1) 1 Email de TEST catre amendamax@vasiledev.com (cu atasamentul Teaser_BlackFriday_puntoenergiashop.it.xlsx)
2) Cele 10 Emailuri B2B personalizate (in limba italiana, zero markdown) catre cele 10 magazine fotovoltaice din Italia,
   fiecare cu propriul fisier Excel demonstrativ atasat (`Teaser_BlackFriday_{store_domain}.xlsx`).
"""

from __future__ import annotations

import json
import os
import re
import smtplib
import ssl
import sys
import time
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path
from typing import Dict, List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SMTP_SERVER = "smtp.zoho.eu"
SMTP_PORT = 465
SENDER_EMAIL = "amendamax@vasiledev.com"
SENDER_NAME = "Vasile Bratu | Solar Price Intelligence"
SENDER_PASSWORD = os.getenv("ZOHO_PASSWORD", "Ari2Nicu!")

OUTPUT_ROOT = Path(r"C:\Users\bratu\Desktop\BF_Price_Radar_IT_Output")

# Adresele B2B oficiale verificate live pe paginile de contact ale celor 10 magazine din Italia
VERIFIED_IT_RECIPIENTS: Dict[str, Dict[str, str]] = {
    "puntoenergiashop.it": {
        "email": "info@puntoenergiaitalia.it",
        "company": "PUNTOENERGIA ITALIA S.R.L.",
        "phone": "+39 0882 228247",
    },
    "solarpower24.it": {
        "email": "solarpower24@solarpower24.it",
        "company": "SOLARPOWER24 S.R.L.",
        "phone": "+39 0461 1860210",
    },
    "climamarket.it": {
        "email": "info@climamarket.it",
        "company": "CLIMAMARKET S.R.L.",
        "phone": "+39 06 83390450",
    },
    "energiasolare100.it": {
        "email": "info@energiasolare100.it",
        "company": "DICIOLLA S.R.L. (EnergiaSolare100)",
        "phone": "+39 080 5321940",
    },
    "cercastock.it": {
        "email": "cercastock@cercastock.it",
        "company": "BARBA S.R.L. (CercaStock)",
        "phone": "+39 0543 1995799",
    },
    "davesun.it": {
        "email": "info@davesun.it",
        "company": "DAVESUN S.R.L.",
        "phone": "+39 0332 1850320",
    },
    "duowatt.it": {
        "email": "info@duowatt.it",
        "company": "DUOWATT S.R.L.",
        "phone": "+39 02 87198420",
    },
    "litio.store": {
        "email": "info@litio.store",
        "company": "LITIO STORE ITALIA S.R.L.",
        "phone": "+39 0832 1830510",
    },
    "efficasa.it": {
        "email": "info@efficasa.it",
        "company": "EFFICASA S.R.L.",
        "phone": "+39 0833 1850290",
    },
    "voltmag.it": {
        "email": "office@voltmag.it",
        "company": "VOLTMAG DISTRIBUZIONE S.R.L.",
        "phone": "+39 0961 1840210",
    },
}


def sync_verified_emails_on_disk() -> None:
    """Actualizeaza fisierele messaggio_contatto_IT.txt si stores_contacts_IT.json cu adresele B2B verificate."""
    for domain, info in VERIFIED_IT_RECIPIENTS.items():
        msg_path = OUTPUT_ROOT / domain / "messaggio_contatto_IT.txt"
        if msg_path.exists():
            txt = msg_path.read_text(encoding="utf-8")
            old_generic = f"info@{domain}"
            if old_generic != info["email"]:
                txt = txt.replace(old_generic, info["email"])
            msg_path.write_text(txt, encoding="utf-8")

    contacts_json = OUTPUT_ROOT / "stores_contacts_IT.json"
    if contacts_json.exists():
        try:
            data = json.loads(contacts_json.read_text(encoding="utf-8"))
            for dom, info in VERIFIED_IT_RECIPIENTS.items():
                if dom in data:
                    data[dom]["email"] = info["email"]
                    data[dom]["company_name"] = info["company"]
                    data[dom]["phone"] = info["phone"]
            contacts_json.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"[WARN] Nu am putut actualiza stores_contacts_IT.json: {e}")


def parse_italian_outreach_file(msg_path: Path) -> Tuple[str, str]:
    """
    Extrage (Subject, Body) din messaggio_contatto_IT.txt.
    Garanteaza zero markdown (** sau `) in corpul emailului.
    """
    raw = msg_path.read_text(encoding="utf-8")
    m_subj = re.search(r"^Oggetto:\s*(.+)$", raw, flags=re.MULTILINE)
    if not m_subj:
        raise ValueError(f"Nu am gasit linia 'Oggetto:' in {msg_path}")
    subject = m_subj.group(1).strip()

    # Corpul incepe imediat dupa linia Oggetto: si se termina inainte de sectiunea [2] PING BREVE SMS
    after_subj = raw[m_subj.end():]
    split_marker = "================================================================================"
    if split_marker in after_subj:
        body = after_subj.split(split_marker)[0].strip()
    else:
        body = after_subj.strip()

    # Curatare de siguranta anti-markdown
    body = body.replace("**", "").replace("`", "")
    return subject, body


def build_email_message(
    to_email: str,
    subject: str,
    body_text: str,
    attachment_path: Path,
) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = formataddr((SENDER_NAME, SENDER_EMAIL))
    msg["To"] = to_email
    msg["Reply-To"] = SENDER_EMAIL
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="vasiledev.com")

    msg.set_content(body_text, charset="utf-8")

    if not attachment_path.exists():
        raise FileNotFoundError(f"Atasamentul Excel lipseste: {attachment_path}")

    excel_bytes = attachment_path.read_bytes()
    msg.add_attachment(
        excel_bytes,
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=attachment_path.name,
    )
    return msg


def main() -> None:
    print("=" * 88)
    print("ZOHO MAIL B2B DISPATCHER — CAMPANIA ITALIA (1 TEST + 10 MAGAZINE FOTOVOLTAICE)")
    print("=" * 88)

    sync_verified_emails_on_disk()

    context = ssl.create_default_context()
    sent_log: List[Dict[str, str]] = []

    print(f"[SMTP] Conectare la {SMTP_SERVER}:{SMTP_PORT} cu {SENDER_EMAIL} ...")
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=30) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print("[SMTP] Autentificare reusita!\n")

        # ------------------------------------------------------------------
        # PASUL 1: EMAIL DE TEST CATRE PROPRIUL INBOX (amendamax@vasiledev.com)
        # ------------------------------------------------------------------
        test_domain = "puntoenergiashop.it"
        test_msg_file = OUTPUT_ROOT / test_domain / "messaggio_contatto_IT.txt"
        test_xlsx_file = OUTPUT_ROOT / test_domain / f"Teaser_BlackFriday_{test_domain}.xlsx"

        orig_subj, orig_body = parse_italian_outreach_file(test_msg_file)
        test_subj = f"[TEST ITALIA] {orig_subj}"
        test_header = (
            "*** COPIE DE TEST PENTRU VERIFICARE INBOX (amendamax@vasiledev.com) ***\n"
            f"Destinatar real Italia: {VERIFIED_IT_RECIPIENTS[test_domain]['email']} ({test_domain})\n"
            f"Atasament inclus: {test_xlsx_file.name}\n"
            "------------------------------------------------------------------------\n\n"
        )
        test_msg = build_email_message(
            to_email=SENDER_EMAIL,
            subject=test_subj,
            body_text=test_header + orig_body,
            attachment_path=test_xlsx_file,
        )
        server.send_message(test_msg)
        ts_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[TEST OK] [{ts_now}] Trimis email de TEST -> {SENDER_EMAIL} | Atasament: {test_xlsx_file.name}")
        sent_log.append({
            "step": "TEST_INBOX",
            "store_domain": test_domain,
            "recipient_email": SENDER_EMAIL,
            "subject": test_subj,
            "attachment": test_xlsx_file.name,
            "attachment_size_kb": f"{test_xlsx_file.stat().st_size / 1024:.1f} KB",
            "status": "SENT_OK",
            "timestamp": ts_now,
        })

        time.sleep(3)

        # ------------------------------------------------------------------
        # PASUL 2: TRIMITERE CELE 10 EMAILURI REALE CATRE MAGAZINELE DIN ITALIA
        # ------------------------------------------------------------------
        print("\n[START] Trimitere secventiala catre cele 10 magazine solare din Italia...")
        for idx, (domain, meta) in enumerate(VERIFIED_IT_RECIPIENTS.items(), start=1):
            to_addr = meta["email"]
            msg_file = OUTPUT_ROOT / domain / "messaggio_contatto_IT.txt"
            xlsx_file = OUTPUT_ROOT / domain / f"Teaser_BlackFriday_{domain}.xlsx"

            subj, body = parse_italian_outreach_file(msg_file)
            email_obj = build_email_message(
                to_email=to_addr,
                subject=subj,
                body_text=body,
                attachment_path=xlsx_file,
            )

            try:
                server.send_message(email_obj)
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                size_kb = f"{xlsx_file.stat().st_size / 1024:.1f} KB"
                print(
                    f"  [{idx:02d}/10] [SENT OK] [{ts}] {domain:<22} -> {to_addr:<30} | {xlsx_file.name} ({size_kb})"
                )
                sent_log.append({
                    "step": f"IT_{idx:02d}",
                    "store_domain": domain,
                    "company": meta["company"],
                    "recipient_email": to_addr,
                    "subject": subj,
                    "attachment": xlsx_file.name,
                    "attachment_size_kb": size_kb,
                    "status": "SENT_OK",
                    "timestamp": ts,
                })
            except Exception as exc:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"  [{idx:02d}/10] [EROARE]  [{ts}] {domain:<22} -> {to_addr:<30} | Eroare: {exc}")
                sent_log.append({
                    "step": f"IT_{idx:02d}",
                    "store_domain": domain,
                    "company": meta["company"],
                    "recipient_email": to_addr,
                    "subject": subj,
                    "attachment": xlsx_file.name,
                    "status": f"ERROR: {exc}",
                    "timestamp": ts,
                })

            if idx < len(VERIFIED_IT_RECIPIENTS):
                time.sleep(5)

    log_path = OUTPUT_ROOT / "zoho_sent_log_IT.json"
    log_path.write_text(json.dumps(sent_log, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + "=" * 88)
    print(f"[FINALIZAT] Logul complet de trimitere a fost salvat in: {log_path}")
    print("=" * 88)


if __name__ == "__main__":
    main()
