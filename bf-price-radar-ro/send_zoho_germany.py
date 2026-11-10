#!/usr/bin/env python3
"""
send_zoho_germany.py
Dispatches via Zoho Mail SMTP (smtp.zoho.eu:465, amendamax@vasiledev.com):
1) 1 TEST Email to amendamax@vasiledev.com (with Teaser_BlackFriday_tepto.de.xlsx attached)
2) The 10 personalized German B2B emails (native German formatting 1.249,00 €, zero markdown) to the 10 verified German solar shops,
   each with its own `Teaser_BlackFriday_{store_domain}.xlsx` attachment.
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

OUTPUT_ROOT = Path(r"C:\Users\bratu\Desktop\BF_Price_Radar_DE_Output")

# Verified German Impressum B2B Recipients
VERIFIED_DE_RECIPIENTS: Dict[str, Dict[str, str]] = {
    "tepto.de": {
        "email": "verkauf@tepto.de",
        "company": "Tepto GmbH (HRB 113105)",
        "phone": "+49 2264 40412-0",
    },
    "actec-solar.de": {
        "email": "info@actec-klima.de",
        "company": "AC TEC GmbH (HRB 733335)",
        "phone": "+49 721 98899598",
    },
    "offgridtec.com": {
        "email": "info@offgridtec.com",
        "company": "Offgridtec AG (HRB 14946)",
        "phone": "+49 8721 9199400",
    },
    "panda-solar.de": {
        "email": "info@panda-solar.de",
        "company": "Panda Solar (Söhrewald / Kassel)",
        "phone": "+49 5608 7990068",
    },
    "solarkontor.de": {
        "email": "info@solarkontor.de",
        "company": "WATTSTUNDE GmbH (HRB 204772)",
        "phone": "+49 4131 699640",
    },
    "husatech.de": {
        "email": "service@husatech.de",
        "company": "HUSATECH GmbH (HRB 210766)",
        "phone": "+49 531 12296789",
    },
    "photovoltaik4all.de": {
        "email": "info@photovoltaik4all.de",
        "company": "SEC SolarEnergyConsult GmbH (HRB 21490)",
        "phone": "+49 3933 9099850",
    },
    "autobatterienbilliger.de": {
        "email": "info@autobatterienbilliger.de",
        "company": "batterium GmbH (HRB 736368)",
        "phone": "+49 7141 5609040",
    },
    "bau-tech.shop": {
        "email": "info@bautechsolar.de",
        "company": "bau-tech Solarenergie GmbH (HRB 20127)",
        "phone": "+49 38229 78510",
    },
    "solarway.de": {
        "email": "support@solarway.shop",
        "company": "Solarway GmbH (HRB 11221)",
        "phone": "+49 5261 920990",
    },
}


def parse_de_outreach_file(msg_path: Path) -> Tuple[str, str]:
    """Extracts (Betreff, Body) from outreach_message_DE.txt with zero markdown."""
    raw = msg_path.read_text(encoding="utf-8")
    m_subj = re.search(r"^Betreff:\s*(.+)$", raw, flags=re.MULTILINE)
    if not m_subj:
        raise ValueError(f"Could not find 'Betreff:' line in {msg_path}")
    subject = m_subj.group(1).strip()

    after_subj = raw[m_subj.end():]
    split_marker = "================================================================================"
    if split_marker in after_subj:
        body = after_subj.split(split_marker)[0].strip()
    else:
        body = after_subj.strip()

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
        raise FileNotFoundError(f"Excel attachment missing: {attachment_path}")

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
    print("ZOHO MAIL B2B DISPATCHER — GERMANY CAMPAIGN (1 TEST + 10 DE SOLAR SHOPS)")
    print("=" * 88)

    context = ssl.create_default_context()
    sent_log: List[Dict[str, str]] = []

    print(f"[SMTP] Connecting to {SMTP_SERVER}:{SMTP_PORT} as {SENDER_EMAIL} ...")
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=30) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print("[SMTP] Authentication successful!\n")

        # ------------------------------------------------------------------
        # STEP 1: TEST EMAIL TO OWN INBOX (amendamax@vasiledev.com)
        # ------------------------------------------------------------------
        test_domain = "tepto.de"
        test_msg_file = OUTPUT_ROOT / test_domain / "outreach_message_DE.txt"
        test_xlsx_file = OUTPUT_ROOT / test_domain / f"Teaser_BlackFriday_{test_domain}.xlsx"

        orig_subj, orig_body = parse_de_outreach_file(test_msg_file)
        test_subj = f"[TEST DE] {orig_subj}"
        test_header = (
            "*** TEST-KOPIE FÜR INBOX-PRÜFUNG (amendamax@vasiledev.com) ***\n"
            f"Echter Empfänger (DE): {VERIFIED_DE_RECIPIENTS[test_domain]['email']} ({VERIFIED_DE_RECIPIENTS[test_domain]['company']})\n"
            f"Excel-Anhang: {test_xlsx_file.name}\n"
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
        print(f"[TEST OK] [{ts_now}] Sent DE TEST email -> {SENDER_EMAIL} | Attachment: {test_xlsx_file.name}")
        sent_log.append({
            "step": "TEST_INBOX_DE",
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
        # STEP 2: SEQUENTIAL DISPATCH TO THE 10 VERIFIED GERMAN SOLAR SHOPS
        # ------------------------------------------------------------------
        print("\n[START] Sending personalized German B2B emails to the 10 DE solar shops...")
        for idx, (domain, meta) in enumerate(VERIFIED_DE_RECIPIENTS.items(), start=1):
            to_addr = meta["email"]
            msg_file = OUTPUT_ROOT / domain / "outreach_message_DE.txt"
            xlsx_file = OUTPUT_ROOT / domain / f"Teaser_BlackFriday_{domain}.xlsx"

            subj, body = parse_de_outreach_file(msg_file)
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
                    f"  [{idx:02d}/10] [SENT OK] [{ts}] {domain:<26} -> {to_addr:<32} | {xlsx_file.name} ({size_kb})"
                )
                sent_log.append({
                    "step": f"DE_{idx:02d}",
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
                print(f"  [{idx:02d}/10] [ERROR]   [{ts}] {domain:<26} -> {to_addr:<32} | Error: {exc}")
                sent_log.append({
                    "step": f"DE_{idx:02d}",
                    "store_domain": domain,
                    "company": meta["company"],
                    "recipient_email": to_addr,
                    "subject": subj,
                    "attachment": xlsx_file.name,
                    "status": f"ERROR: {exc}",
                    "timestamp": ts,
                })

            if idx < len(VERIFIED_DE_RECIPIENTS):
                time.sleep(5)

    log_path = OUTPUT_ROOT / "zoho_sent_log_DE.json"
    log_path.write_text(json.dumps(sent_log, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + "=" * 88)
    print(f"[COMPLETED] Full DE dispatch log saved to: {log_path}")
    print("=" * 88)


if __name__ == "__main__":
    main()
