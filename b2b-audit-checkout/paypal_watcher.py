#!/usr/bin/env python3
"""
paypal_watcher.py (HARDENED v2)
Daemon pentru portalul B2B Self-Service (https://vasiledev.com/audit/):
1. Verifica la fiecare 35s comenzile din Cloudflare Worker (/api/admin/live).
2. Deblocarea principala se face criptografic server-to-server prin PayPal IPN (ipnpb.paypal.com -> VERIFIED) direct in Cloudflare Worker.
3. Backup IMAP ultra-strict: accepta EXCLUSIV emailuri oficiale semnate DKIM (dkim=pass) de la domenii oficiale @paypal.* / @intl.paypal.com
   (NICIODATA @gmail.com / @vasiledev.com) care contin un Transaction ID PayPal real de 17 caractere.
4. Alerta pe Zoho (amendamax@vasiledev.com) deduplicata per domeniu la checkout si alerta + livrare backup .xlsx doar la PAID verificat.
"""

from __future__ import annotations

import email
import imaplib
import json
import re
import smtplib
import ssl
import sys
import time
import urllib.request
from email.header import decode_header
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid, parseaddr
from pathlib import Path
from typing import Any, Dict, List, Set

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

API_BASE = "https://b2b-audit-checkout.amendamax.workers.dev"
ADMIN_TOKEN = "vd_sec_vault_2026_98f4a17e82b941c09d3e8a"
GMAIL_USER = "amendamax@gmail.com"
GMAIL_PASS = "wbdtsxzkryfekhhx"
ZOHO_ALERT_EMAIL = "amendamax@vasiledev.com"
DESKTOP_DIR = Path(r"C:\Users\bratu\Desktop")
STATE_FILE = Path(__file__).resolve().parent / "fulfilled_orders.json"
NOTIFIED_DOMAINS_FILE = Path(__file__).resolve().parent / "notified_checkout_domains.json"

OFFICIAL_PAYPAL_DOMAINS = (
    "@paypal.com",
    "@intl.paypal.com",
    "@paypal.it",
    "@paypal.co.uk",
    "@paypal.de",
    "@e.paypal.com",
)


def decode_str(s: Any) -> str:
    if not s:
        return ""
    return "".join(
        p.decode(enc or "utf-8", errors="replace") if isinstance(p, bytes) else str(p)
        for p, enc in decode_header(str(s))
    )


def find_full_xlsx_on_disk(domain: str) -> Path | None:
    target = f"Full_Audit_BlackFriday_{domain}".lower()
    for f in DESKTOP_DIR.glob("BF_*_Output/**/*.xlsx"):
        if f.stem.lower() == target:
            return f
    return None


def fetch_live_state() -> Dict[str, Any]:
    req = urllib.request.Request(
        f"{API_BASE}/api/admin/live?token={ADMIN_TOKEN}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=12) as r:
        return json.loads(r.read().decode("utf-8"))


def mark_order_paid_api(order_id: str, txn_id: str, payer_email: str = "") -> None:
    payload = json.dumps({
        "order_id": order_id,
        "txn_id": txn_id,
        "payer_email": payer_email,
    }).encode("utf-8")
    req = urllib.request.Request(
        f"{API_BASE}/api/admin/mark-paid?token={ADMIN_TOKEN}",
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        print(f"[WATCHER] Marked {order_id} PAID (txn={txn_id}) -> {r.read().decode('utf-8')}")


def scan_gmail_for_official_paypal_receipts(pending_orders: List[Dict[str, Any]]) -> None:
    if not pending_orders:
        return
    try:
        M = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        M.login(GMAIL_USER, GMAIL_PASS)
        M.select("INBOX")
        _, data = M.search(None, "SINCE", "30-Oct-2026")
        ids = data[0].split()[-30:]
        for mid in reversed(ids):
            _, msg_data = M.fetch(mid, "(RFC822)")
            msg = email.message_from_bytes(msg_data[0][1])

            _, sender_addr = parseaddr(decode_str(msg.get("From")))
            sender_addr = sender_addr.strip().lower()
            # STRICT: must come from an official @paypal.* address, NEVER @gmail.com
            if not sender_addr or not sender_addr.endswith(OFFICIAL_PAYPAL_DOMAINS):
                continue

            auth_hdr = " ".join(str(h) for h in msg.get_all("Authentication-Results", [])).lower()
            if "dkim=pass" not in auth_hdr or "paypal." not in auth_hdr:
                continue

            subj = decode_str(msg.get("Subject"))
            body_parts = []
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() in ("text/plain", "text/html"):
                        raw = part.get_payload(decode=True)
                        if raw:
                            body_parts.append(raw.decode(part.get_content_charset() or "utf-8", errors="replace"))
            else:
                raw = msg.get_payload(decode=True)
                if raw:
                    body_parts.append(raw.decode(msg.get_content_charset() or "utf-8", errors="replace"))

            full_txt = subj + "\n" + "\n".join(body_parts)
            low_txt = full_txt.lower()
            if not any(k in low_txt for k in ["hai ricevuto un pagamento", "you received a payment", "pagamento ricevuto", "payment received"]):
                continue

            m_txn = re.search(r"\b([0-9A-Z]{17})\b", full_txt)
            if not m_txn:
                continue
            txn_id = m_txn.group(1)

            for po in pending_orders:
                oid = po["order_id"]
                if oid in full_txt:
                    print(f"[OFFICIAL PAYPAL DKIM RECEIPT] Unlocking {oid} (txn={txn_id})...")
                    mark_order_paid_api(oid, txn_id)
        M.logout()
    except Exception as exc:
        print(f"[WATCHER IMAP WARN] {exc}")


def send_backup_delivery_email(order: Dict[str, Any]) -> None:
    dom = order["domain"]
    to_addr = (order.get("buyer_email") or order.get("payer_email") or "").strip()
    xlsx_path = find_full_xlsx_on_disk(dom)
    if not to_addr or "@" not in to_addr or not xlsx_path:
        return

    msg = EmailMessage()
    msg["From"] = formataddr(("Vasile Bratu | VasileDev Group", GMAIL_USER))
    msg["To"] = to_addr
    msg["Bcc"] = ZOHO_ALERT_EMAIL
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="gmail.com")
    msg["Subject"] = f"[UNLOCKED] Full_Audit_BlackFriday_{dom}.xlsx — Order {order['order_id']}"

    msg.set_content(
        f"Hello,\n\n"
        f"Thank you for your payment ({order['amount']} {order['currency']} — Order {order['order_id']}).\n\n"
        f"Attached is your backup copy of the complete unlocked Black Friday Competitor Price & Stock Matrix:\n"
        f"  - File: {xlsx_path.name}\n"
        f"  - Paid Commercial Invoice & Instant Portal Link: https://vasiledev.com/audit/?shop={dom}\n\n"
        f"Best regards,\n"
        f"Vasile Bratu\n"
        f"VasileDev Group (EU VIES VAT: IT04226190041)\n"
        f"Email: amendamax@vasiledev.com | Tel: +39 320 948 1876\n"
    )

    msg.add_attachment(
        xlsx_path.read_bytes(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=xlsx_path.name,
    )

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx, timeout=25) as srv:
        srv.login(GMAIL_USER, GMAIL_PASS)
        srv.send_message(msg)
    print(f"[DELIVERED BACKUP EMAIL] {dom} -> {to_addr} ({xlsx_path.name})")


def send_owner_alert(subject: str, body: str) -> None:
    msg = EmailMessage()
    # IMPORTANT: Never include 'PayPal' in display name and send ONLY to Zoho (no self-CC to Gmail)
    msg["From"] = formataddr(("VasileDev B2B Monitor", GMAIL_USER))
    msg["To"] = ZOHO_ALERT_EMAIL
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="gmail.com")
    msg["Subject"] = subject
    msg.set_content(body)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx, timeout=20) as srv:
        srv.login(GMAIL_USER, GMAIL_PASS)
        srv.send_message(msg)
    print(f"[OWNER ALERT SENT] {subject}")


def main() -> None:
    fulfilled: Set[str] = set()
    if STATE_FILE.exists():
        try:
            fulfilled = set(json.loads(STATE_FILE.read_text(encoding="utf-8")))
        except Exception:
            fulfilled = set()

    notified_domains: Set[str] = {"e-acumulatori.ro", "powertoolmate.co.uk"}
    if NOTIFIED_DOMAINS_FILE.exists():
        try:
            notified_domains |= set(json.loads(NOTIFIED_DOMAINS_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass

    print(f"[B2B WATCHER v2 ONLINE] Monitoring {API_BASE} every 35s...")
    while True:
        try:
            state = fetch_live_state()
            orders = state.get("orders", [])

            for o in orders:
                dom = (o.get("domain") or "").lower().strip()
                oid = o.get("order_id", "")
                if dom and dom not in notified_domains and o.get("status") == "PENDING":
                    notified_domains.add(dom)
                    NOTIFIED_DOMAINS_FILE.write_text(
                        json.dumps(sorted(notified_domains), indent=2), encoding="utf-8"
                    )
                    send_owner_alert(
                        f"[CHECKOUT PORNIT] {dom} ({o['amount']} {o['currency']}) — {oid}",
                        f"Un magazin a apasat butonul de checkout pe vasiledev.com/audit/ (asteptam confirmarea platii in PayPal):\n\n"
                        f"- Magazin: {dom}\n"
                        f"- Companie / CUI: {o.get('company_name')} ({o.get('vat_id')})\n"
                        f"- Email client: {o.get('buyer_email')}\n"
                        f"- Suma: {o['amount']} {o['currency']} ({o.get('tier')})\n"
                        f"- Order ID: {oid}\n"
                        f"- Ora (UTC): {o.get('created_at')}\n",
                    )

            pending = [o for o in orders if o.get("status") == "PENDING"]
            if pending:
                scan_gmail_for_official_paypal_receipts(pending)
                state = fetch_live_state()
                orders = state.get("orders", [])

            for o in orders:
                oid = o.get("order_id", "")
                txn = (o.get("txn_id") or "").strip()
                # Require genuine PAID status AND non-empty verified txn_id (never PAYPAL-IMAP-VERIFIED)
                if o.get("status") == "PAID" and oid and txn and txn != "PAYPAL-IMAP-VERIFIED" and oid not in fulfilled:
                    send_owner_alert(
                        f"💰 [PLATA INCASATA] +{o['amount']} {o['currency']} de la {o['domain']} ({oid})",
                        f"PLATA CONFIRMATA CRIPTOGRAFIC IN PAYPAL!\n\n"
                        f"- Magazin: {o['domain']}\n"
                        f"- Suma incasata: {o['amount']} {o['currency']}\n"
                        f"- Companie / VAT: {o.get('company_name')} ({o.get('vat_id')})\n"
                        f"- Email cumparator: {o.get('buyer_email')} / PayPal: {o.get('payer_email')}\n"
                        f"- Tranzactie PayPal: {txn}\n"
                        f"- Order ID: {oid}\n",
                    )
                    send_backup_delivery_email(o)
                    fulfilled.add(oid)
                    STATE_FILE.write_text(json.dumps(sorted(fulfilled), indent=2), encoding="utf-8")
        except Exception as e:
            print(f"[WATCHER LOOP ERR] {e}")
        time.sleep(35)


if __name__ == "__main__":
    main()
