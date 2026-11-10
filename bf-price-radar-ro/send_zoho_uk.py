#!/usr/bin/env python3
"""
send_zoho_uk.py
Dispatches via Zoho Mail SMTP (smtp.zoho.eu:465, amendamax@vasiledev.com):
1) 1 TEST Email to amendamax@vasiledev.com (with Teaser_BlackFriday_itstechnologies.shop.xlsx attached)
2) The 10 personalized British English B2B emails (human-written, zero markdown) to the 10 verified UK solar stores,
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

OUTPUT_ROOT = Path(r"C:\Users\bratu\Desktop\BF_Price_Radar_UK_Output")

# Verified UK B2B Recipients (Companies House & official contact pages verified)
VERIFIED_UK_RECIPIENTS: Dict[str, Dict[str, str]] = {
    "itstechnologies.shop": {
        "email": "support@itstechnologies.uk",
        "company": "ITS Technologies Ltd (Co. No. 08961559)",
        "phone": "+44 161 529 8401",
    },
    "callidus.shop": {
        "email": "admin@callidustrade.co.uk",
        "company": "Callidus Trade Limited (Co. No. 13604025)",
        "phone": "+44 1626 563563",
    },
    "voltaconsolar.com": {
        "email": "info@voltacon.com",
        "company": "Voltacon UK Limited (Co. No. 07524135)",
        "phone": "+44 2477 675575",
    },
    "offgridrenewables.co.uk": {
        "email": "hello@offgridrenewables.co.uk",
        "company": "Off Grid Renewables Ltd (Co. No. 15471192)",
        "phone": "+44 330 133 3275",
    },
    "fogstar.co.uk": {
        "email": "customerservice@fogstar.co.uk",
        "company": "Fogstar Ltd (Co. No. 10490056)",
        "phone": "+44 1527 757980",
    },
    "windandsun.co.uk": {
        "email": "sales@windandsun.co.uk",
        "company": "Wind & Sun Limited (Co. No. 03403803)",
        "phone": "+44 1568 720364",
    },
    "powerland.co.uk": {
        "email": "info@powerland.co.uk",
        "company": "Powerland Industries Ltd (Co. No. 09039034)",
        "phone": "+44 1527 962968",
    },
    "powerwarehouse.co.uk": {
        "email": "info@powerwarehouse.co.uk",
        "company": "Power Warehouse Ltd (Co. No. 14346564)",
        "phone": "+44 330 174 2900",
    },
    "solar-hub.co.uk": {
        "email": "sales@solarrenewablehub.co.uk",
        "company": "Solar Renewable Hub Ltd (Co. No. 14668774)",
        "phone": "+44 1248 660330",
    },
    "pluginsolar.co.uk": {
        "email": "info@pluginsolar.co.uk",
        "company": "Plug In Solar Ltd (Co. No. 07483249)",
        "phone": "+44 1444 672005",
    },
}


def parse_uk_outreach_file(msg_path: Path) -> Tuple[str, str]:
    """Extracts (Subject, Body) from outreach_message_UK.txt with zero markdown."""
    raw = msg_path.read_text(encoding="utf-8")
    m_subj = re.search(r"^Subject:\s*(.+)$", raw, flags=re.MULTILINE)
    if not m_subj:
        raise ValueError(f"Could not find 'Subject:' line in {msg_path}")
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
    print("ZOHO MAIL B2B DISPATCHER — UK CAMPAIGN (1 TEST + 10 UK SOLAR STORES)")
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
        test_domain = "itstechnologies.shop"
        test_msg_file = OUTPUT_ROOT / test_domain / "outreach_message_UK.txt"
        test_xlsx_file = OUTPUT_ROOT / test_domain / f"Teaser_BlackFriday_{test_domain}.xlsx"

        orig_subj, orig_body = parse_uk_outreach_file(test_msg_file)
        test_subj = f"[TEST UK] {orig_subj}"
        test_header = (
            "*** TEST COPY FOR INBOX VERIFICATION (amendamax@vasiledev.com) ***\n"
            f"Real UK Recipient: {VERIFIED_UK_RECIPIENTS[test_domain]['email']} ({VERIFIED_UK_RECIPIENTS[test_domain]['company']})\n"
            f"Attached Excel: {test_xlsx_file.name}\n"
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
        print(f"[TEST OK] [{ts_now}] Sent UK TEST email -> {SENDER_EMAIL} | Attachment: {test_xlsx_file.name}")
        sent_log.append({
            "step": "TEST_INBOX_UK",
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
        # STEP 2: SEQUENTIAL DISPATCH TO THE 10 VERIFIED UK SOLAR STORES
        # ------------------------------------------------------------------
        print("\n[START] Sending personalized British English emails to the 10 UK solar stores...")
        for idx, (domain, meta) in enumerate(VERIFIED_UK_RECIPIENTS.items(), start=1):
            to_addr = meta["email"]
            msg_file = OUTPUT_ROOT / domain / "outreach_message_UK.txt"
            xlsx_file = OUTPUT_ROOT / domain / f"Teaser_BlackFriday_{domain}.xlsx"

            subj, body = parse_uk_outreach_file(msg_file)
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
                    f"  [{idx:02d}/10] [SENT OK] [{ts}] {domain:<24} -> {to_addr:<32} | {xlsx_file.name} ({size_kb})"
                )
                sent_log.append({
                    "step": f"UK_{idx:02d}",
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
                print(f"  [{idx:02d}/10] [ERROR]   [{ts}] {domain:<24} -> {to_addr:<32} | Error: {exc}")
                sent_log.append({
                    "step": f"UK_{idx:02d}",
                    "store_domain": domain,
                    "company": meta["company"],
                    "recipient_email": to_addr,
                    "subject": subj,
                    "attachment": xlsx_file.name,
                    "status": f"ERROR: {exc}",
                    "timestamp": ts,
                })

            if idx < len(VERIFIED_UK_RECIPIENTS):
                time.sleep(5)

    log_path = OUTPUT_ROOT / "zoho_sent_log_UK.json"
    log_path.write_text(json.dumps(sent_log, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n" + "=" * 88)
    print(f"[COMPLETED] Full UK dispatch log saved to: {log_path}")
    print("=" * 88)


if __name__ == "__main__":
    main()
