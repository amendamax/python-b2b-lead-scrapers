#!/usr/bin/env python3
"""
send_sms_cloud.py
Trimite automat din Cloud (prin Brevo Transactional SMS API sau Twilio REST API)
cele 11 SMS-uri B2B catre magazinele fotovoltaice din Olanda, Spania, Franta si Italia
care au numere de mobil GSM verificate.
Toate mesajele sunt optimizate sub 160 caractere (1 singur segment GSM-7) cu Sender ID "VasileDev".
"""

from __future__ import annotations

import base64
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SENDER_ID = "VasileDev"

# Cele 11 numere de mobil GSM verificate (care nu au fost inca contactate pe WhatsApp la 18:18)
SMS_TARGETS: List[Tuple[str, str, str, str]] = [
    # (Country, Domain, Mobile_E164, Email_Sent_To)
    ("NL", "offgridcentrum.nl", "+31628278640", "info@offgridcentrumnederland.nl"),
    ("NL", "zonnepanelen-voordelig.nl", "+31627179772", "info@zonnepanelen-voordelig.nl"),
    ("ES", "wccsolar.net", "+34665556179", "servicio@wccsolar.es"),
    ("ES", "rebacas.com", "+34648482497", "info@rebacas.com"),
    ("ES", "cambioenergetico.com", "+34646936201", "info@cambioenergetico.com"),
    ("ES", "efectosolar.es", "+34638973150", "info@efectosolar.es"),
    ("ES", "suministrosdelsol.com", "+34642028284", "info@suministrosdelsol.com"),
    ("ES", "coelectrix.com", "+34722486679", "info@coelectrix.com"),
    ("FR", "alma-solar.fr", "+33755539417", "contact@alma-solarshop.com"),
    ("FR", "solairepratique.com", "+33652722896", "contact@solairepratique.com"),
    ("IT", "climamarket.it", "+393356990916", "info@climamarket.it"),
]


def build_short_sms(cc: str, domain: str, email_to: str) -> str:
    """Mesaj SMS B2B sub 160 caractere (1 credit GSM-7), fara linkuri."""
    if cc == "NL":
        return f"Goedendag! Ik heb net de Black Friday prijs-Excel voor {domain} gestuurd naar {email_to}. Is deze goed aangekomen? Mvg, Vasile Bratu (amendamax@vasiledev.com)"
    if cc == "ES":
        return f"Hola! Les he enviado hoy el Excel comparativo Black Friday para {domain} a {email_to}. Les ha llegado bien? Saludos, Vasile Bratu (amendamax@vasiledev.com)"
    if cc == "FR":
        return f"Bonjour! Je vous ai envoye le comparatif Excel Black Friday pour {domain} sur {email_to}. L'avez-vous bien recu? Cdlt, Vasile Bratu (amendamax@vasiledev.com)"
    # IT
    return f"Buongiorno! Vi ho inviato su {email_to} la tabella Excel prezzi Black Friday per {domain}. Vi e arrivata in Inbox? Grazie, Vasile Bratu"


def send_via_brevo(api_key: str, recipient: str, content: str) -> Dict:
    url = "https://api.brevo.com/v3/transactionalSMS/sms"
    payload = {
        "sender": SENDER_ID,
        "recipient": recipient,
        "content": content,
        "type": "transactional",
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": api_key.strip(),
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_via_twilio(account_sid: str, auth_token: str, from_sender: str, recipient: str, content: str) -> Dict:
    url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid.strip()}/Messages.json"
    data = urllib.parse.urlencode({
        "From": from_sender,
        "To": recipient,
        "Body": content,
    }).encode("utf-8")
    creds = base64.b64encode(f"{account_sid.strip()}:{auth_token.strip()}".encode("utf-8")).decode("ascii")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Basic {creds}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> None:
    brevo_key = os.getenv("BREVO_API_KEY", "").strip()
    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    twilio_from = os.getenv("TWILIO_FROM", SENDER_ID).strip()

    if not brevo_key and not (twilio_sid and twilio_token):
        print("[INFO] Seteaza BREVO_API_KEY (xkeysib-...) sau TWILIO_ACCOUNT_SID + TWILIO_AUTH_TOKEN.")
        return

    for idx, (cc, dom, phone, em) in enumerate(SMS_TARGETS, 1):
        txt = build_short_sms(cc, dom, em)
        try:
            if brevo_key:
                res = send_via_brevo(brevo_key, phone, txt)
            else:
                res = send_via_twilio(twilio_sid, twilio_token, twilio_from, phone, txt)
            print(f"[SMS {idx:02d}/{len(SMS_TARGETS)}] [SENT OK] {cc} | {dom:<25} | {phone:<15} -> {res}")
        except Exception as exc:
            print(f"[SMS {idx:02d}/{len(SMS_TARGETS)}] [ERROR]   {cc} | {dom:<25} | {phone:<15} -> {exc}")
        time.sleep(3)


if __name__ == "__main__":
    main()
