#!/usr/bin/env python3
"""
send_zoho_fr_only.py
Trimite exclusiv cele 10 emailuri B2B pentru Franta (FR) din C:\\Users\\bratu\\Desktop\\BF_Price_Radar_FR_Output
cu pauza de 2,5 minute (150 secunde) intre mesaje si reconectare curata la fiecare email
(ca sa nu expire conexiunea SMTP in timpul pauzei de 2,5 minute + auto-retry daca Zoho inca e in cooldown).
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

PAUSE_SECONDS = 150  # 2,5 minute (150 secunde)

OUTPUT_ROOT = Path(r"C:\Users\bratu\Desktop\BF_Price_Radar_FR_Output")

FR_RECIPIENTS: Dict[str, str] = {
    "monkitsolaire.fr": "contact@monkitsolaire.fr",
    "alma-solar.fr": "contact@alma-solarshop.com",
    "myshop-solaire.com": "contact@myshop-solaire.com",
    "ase-energy.com": "contact@ase-energy.com",
    "kitsolaire-discount.com": "contact@kitsolaire-discount.com",
    "solairepratique.com": "contact@solairepratique.com",
    "h2r-equipements.com": "contact.pro@h2r-equipements.com",
    "watteo.fr": "contact@watteo.fr",
    "batterie-solaire.com": "contact@batterie-solaire.com",
    "chocdiscount.com": "erwan@solairepascher.com",
}


def parse_fr_outreach(msg_path: Path) -> Tuple[str, str]:
    raw = msg_path.read_text(encoding="utf-8")
    m_subj = re.search(r"^Objet:\s*(.+)$", raw, flags=re.MULTILINE)
    subject = m_subj.group(1).strip()
    body = raw[m_subj.end():].split("================================================================================")[0].strip()
    return subject, body


def send_single_email_via_zoho(msg: EmailMessage) -> None:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=30) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)


def main() -> None:
    print("=" * 88)
    print("ZOHO MAIL DISPATCHER — FRANTA (10 MAGAZINE CU PAUZA DE 2,5 MINUTE / 150 SECUNDE)")
    print("=" * 88, flush=True)

    sent_log: List[Dict[str, str]] = []
    log_path = OUTPUT_ROOT / "zoho_sent_log_FR.json"

    for idx, (domain, to_email) in enumerate(FR_RECIPIENTS.items(), start=1):
        msg_path = OUTPUT_ROOT / domain / "outreach_message_FR.txt"
        xlsx_path = OUTPUT_ROOT / domain / f"Teaser_BlackFriday_{domain}.xlsx"
        subj, body = parse_fr_outreach(msg_path)

        msg = EmailMessage()
        msg["From"] = formataddr((SENDER_NAME, SENDER_EMAIL))
        msg["To"] = to_email
        msg["Reply-To"] = SENDER_EMAIL
        msg["Subject"] = subj
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid(domain="vasiledev.com")
        msg.set_content(body, charset="utf-8")
        msg.add_attachment(
            xlsx_path.read_bytes(),
            maintype="application",
            subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename=xlsx_path.name,
        )

        # Incearca trimiterea; daca Zoho este inca in cooldown 550 5.4.6, asteapta 2,5 minute si reincearca
        for attempt in range(1, 25):
            try:
                send_single_email_via_zoho(msg)
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[FR {idx:02d}/10] [SENT OK] [{ts}] {domain:<25} -> {to_email}", flush=True)
                sent_log.append({
                    "domain": domain,
                    "email": to_email,
                    "subject": subj,
                    "attachment": xlsx_path.name,
                    "status": "SENT_OK",
                    "timestamp": ts,
                })
                log_path.write_text(json.dumps(sent_log, indent=2, ensure_ascii=False), encoding="utf-8")
                break
            except Exception as exc:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[FR {idx:02d}/10] [COOLDOWN/WAIT attempt #{attempt}] [{ts}] {domain} -> astept 2,5 minute (150s)... ({exc})",
                    flush=True,
                )
                time.sleep(PAUSE_SECONDS)

        if idx < len(FR_RECIPIENTS):
            print(f"    -> Pauza programata de 2,5 minute (150 secunde) inainte de urmatorul email FR...", flush=True)
            time.sleep(PAUSE_SECONDS)

    print("=" * 88)
    print(f"[FINALIZAT FRANTA] Toate cele 10 emailuri au fost trimise! Log: {log_path}")
    print("=" * 88, flush=True)


if __name__ == "__main__":
    main()
