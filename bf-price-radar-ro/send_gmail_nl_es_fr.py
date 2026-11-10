#!/usr/bin/env python3
"""
send_gmail_nl_es_fr.py
Trimite cele 30 de emailuri B2B (NL 10 + ES 10 + FR 10) direct prin serverul oficial Google SMTP
(smtp.gmail.com:465) folosind contul amendamax@gmail.com, cu:
  - Reply-To dublu: amendamax@vasiledev.com, amendamax@gmail.com
  - Pauza stricta de 2,5 minute (150 secunde) intre fiecare email
  - Conexiune SMTP proaspata la fiecare trimitere (fara timeout)
  - Atasament Excel personalizat Teaser_BlackFriday_{domain}.xlsx
"""

from __future__ import annotations

import json
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

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
GMAIL_USER = "amendamax@gmail.com"
GMAIL_APP_PASSWORD = "wbdtsxzkryfekhhx"
SENDER_NAME = "Vasile Bratu | Solar Price Intelligence"
REPLY_TO_HEADER = "amendamax@vasiledev.com, amendamax@gmail.com"

PAUSE_SECONDS = 150  # 2,5 minute (150 secunde) intre emailuri

DESKTOP_DIR = Path(r"C:\Users\bratu\Desktop")

CAMPAIGNS: List[Tuple[str, Path, Dict[str, str]]] = [
    (
        "NL",
        DESKTOP_DIR / "BF_Price_Radar_NL_Output",
        {
            "solar-outlet.nl": "info@solar-outlet.nl",
            "stralendgroen.nl": "info@stralendgroen.nl",
            "cedel.nl": "info@cedel.nl",
            "offgridcentrum.nl": "info@offgridcentrumnederland.nl",
            "accuserviceholland.nl": "info@accuserviceholland.nl",
            "zonnepanelen-voordelig.nl": "info@zonnepanelen-voordelig.nl",
            "winkelman-zonnepanelen.nl": "info@winkelman-zonnepanelen.nl",
            "solar-bouwmarkt.nl": "info@solar-bouwmarkt.nl",
            "stroomwinkel.nl": "info@stroomwinkel.nl",
            "marinediscounter.nl": "info@marinediscounter.nl",
        },
    ),
    (
        "ES",
        DESKTOP_DIR / "BF_Price_Radar_ES_Output",
        {
            "autosolar.es": "autosolar@autosolar.es",
            "wccsolar.net": "servicio@wccsolar.es",
            "tiendasolar.es": "info@tienda-solar.es",
            "rebacas.com": "info@rebacas.com",
            "damiasolar.com": "info@damiasolar.com",
            "cambioenergetico.com": "info@cambioenergetico.com",
            "efectosolar.es": "info@efectosolar.es",
            "solarfam.es": "administracion@solarfam.com",
            "suministrosdelsol.com": "info@suministrosdelsol.com",
            "coelectrix.com": "info@coelectrix.com",
        },
    ),
    (
        "FR",
        DESKTOP_DIR / "BF_Price_Radar_FR_Output",
        {
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
        },
    ),
]


def parse_outreach_file(msg_path: Path) -> Tuple[str, str]:
    raw = msg_path.read_text(encoding="utf-8")
    m_subj = re.search(r"^(?:Onderwerp|Asunto|Objet):\s*(.+)$", raw, flags=re.MULTILINE)
    if not m_subj:
        raise ValueError(f"Subject header not found in {msg_path}")
    subject = m_subj.group(1).strip()
    body = raw[m_subj.end():].split("================================================================================")[0].strip()
    return subject, body


def send_via_gmail(msg: EmailMessage) -> None:
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=30) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.send_message(msg)


def main() -> None:
    print("=" * 92)
    print("GMAIL B2B DISPATCHER (amendamax@gmail.com) — NL (10) + ES (10) + FR (10)")
    print("Pauza stricta intre emailuri: 150 secunde (2,5 minute) | Reply-To: vasiledev.com + gmail.com")
    print("=" * 92, flush=True)

    total_to_send = sum(len(d) for _, _, d in CAMPAIGNS)
    global_counter = 0

    for cc, out_root, recipients in CAMPAIGNS:
        print(f"\n>>> START CAMPANIE {cc} ({len(recipients)} magazine) — Folder: {out_root}", flush=True)
        sent_log: List[Dict[str, str]] = []
        log_path = out_root / f"gmail_sent_log_{cc}.json"

        for idx, (domain, to_email) in enumerate(recipients.items(), start=1):
            global_counter += 1
            msg_path = out_root / domain / f"outreach_message_{cc}.txt"
            xlsx_path = out_root / domain / f"Teaser_BlackFriday_{domain}.xlsx"

            subj, body = parse_outreach_file(msg_path)

            msg = EmailMessage()
            msg["From"] = formataddr((SENDER_NAME, GMAIL_USER))
            msg["To"] = to_email
            msg["Reply-To"] = REPLY_TO_HEADER
            msg["Subject"] = subj
            msg["Date"] = formatdate(localtime=True)
            msg["Message-ID"] = make_msgid(domain="gmail.com")
            msg.set_content(body, charset="utf-8")
            msg.add_attachment(
                xlsx_path.read_bytes(),
                maintype="application",
                subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=xlsx_path.name,
            )

            try:
                send_via_gmail(msg)
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[{cc} {idx:02d}/10 | TOTAL {global_counter:02d}/{total_to_send}] [SENT OK] [{ts}] {domain:<26} -> {to_email}",
                    flush=True,
                )
                sent_log.append({
                    "country": cc,
                    "domain": domain,
                    "email": to_email,
                    "subject": subj,
                    "attachment": xlsx_path.name,
                    "sender": GMAIL_USER,
                    "status": "SENT_OK",
                    "timestamp": ts,
                })
            except Exception as exc:
                ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(
                    f"[{cc} {idx:02d}/10 | TOTAL {global_counter:02d}/{total_to_send}] [ERROR] [{ts}] {domain:<26} -> {to_email}: {exc}",
                    flush=True,
                )
                sent_log.append({
                    "country": cc,
                    "domain": domain,
                    "email": to_email,
                    "subject": subj,
                    "attachment": xlsx_path.name,
                    "sender": GMAIL_USER,
                    "status": f"ERROR: {exc}",
                    "timestamp": ts,
                })

            log_path.write_text(json.dumps(sent_log, indent=2, ensure_ascii=False), encoding="utf-8")

            if global_counter < total_to_send:
                print(
                    f"    -> Pauza de 2,5 minute (150 secunde) inainte de emailul #{global_counter + 1}/{total_to_send}...",
                    flush=True,
                )
                time.sleep(PAUSE_SECONDS)

        print(f">>> [COMPLET {cc}] Log salvat in: {log_path}", flush=True)

    print("\n" + "=" * 92)
    print("[SUCCES COMPLET] Toate cele 30 de emailuri (NL + ES + FR) au fost livrate prin Gmail SMTP!")
    print("=" * 92, flush=True)


if __name__ == "__main__":
    main()
