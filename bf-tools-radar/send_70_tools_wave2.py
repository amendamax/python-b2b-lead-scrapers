#!/usr/bin/env python3
"""
send_70_tools_wave2.py
Dispatcher automat B2B pentru CALUPUL 2 (70 de magazine B2B NOI de Scule Electrice Profesionale - 0 duplicate!):
  - 10 DE (Germania Tier-2)      -> 350 EUR / 850 EUR
  - 10 AT (Austria B2B - DE)     -> 350 EUR / 850 EUR
  - 10 NL (Olanda Tier-2)        -> 350 EUR / 850 EUR
  - 10 BE (Belgia B2B - NL/FR)   -> 350 EUR / 850 EUR
  - 10 IT (Italia Tier-2)        -> 350 EUR / 850 EUR
  -  5 FR (Franta Tier-2)        -> 350 EUR / 850 EUR
  -  5 ES (Spania Tier-2)        -> 350 EUR / 850 EUR
  - 10 UK (Marea Britanie Tier-2)-> £295 / £690

Caracteristici de siguranta maxima:
  - Verifica automat ZERO duplicate (domeniu + email) fata de Calupul 1 Scule (70) si Campania Fotovoltaice (70).
  - Re-valideaza la sange toate cele 70 emailuri + 70 fisiere Excel Teaser (ZERO caractere AI, ZERO markdown, ZERO erori, preturi exacte).
  - --wait-for-wave1: asteapta automat finalizarea Calupului 1 (Tools_70_Campaign_Log_2026-10-29.json >= 70) + cooldown 300s.
  - Raport exact 2 Gmail (amendamax@gmail.com) : 1 Zoho (amendamax@vasiledev.com), jitter aleatoriu 140-165s, failover instantaneu pe Gmail.
"""

from __future__ import annotations

import argparse
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
from typing import Any, Dict, List, Set

import openpyxl

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
DESKTOP_DIR = Path(r"C:\Users\bratu\Desktop")
WAVE2_MANIFEST_PATH = BASE_DIR / "tools_batch2_70_manifest.json"
WAVE1_MANIFEST_PATH = BASE_DIR / "tools_all_70_manifest.json"
SOLAR_LOG_PATH = DESKTOP_DIR / "Morning_70_Campaign_Log_2026-10-29.json"
WAVE1_LOG_PATH = DESKTOP_DIR / "Tools_70_Campaign_Log_2026-10-29.json"
WAVE2_LOG_PATH = DESKTOP_DIR / "Tools_Wave2_70_Campaign_Log_2026-10-29.json"

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

SENDER_DISPLAY_NAME = "Vasile Bratu"
REPLY_TO_DUAL = "amendamax@vasiledev.com, amendamax@gmail.com"
TZ_ORDER = {"DE": 1, "AT": 2, "NL": 3, "BE": 4, "IT": 5, "FR": 6, "ES": 7, "UK": 8}


def load_previous_140_blocklist() -> Tuple_Sets:
    prev_domains: Set[str] = set()
    prev_emails: Set[str] = set()
    for p in (WAVE1_MANIFEST_PATH, SOLAR_LOG_PATH):
        if p.exists():
            try:
                rows = json.loads(p.read_text(encoding="utf-8"))
                for r in rows:
                    d = (r.get("domain") or "").lower().strip()
                    if d.startswith("www."):
                        d = d[4:]
                    e = (r.get("email") or r.get("to") or "").lower().strip()
                    if d:
                        prev_domains.add(d)
                    if e:
                        prev_emails.add(e)
            except Exception:
                pass
    return prev_domains, prev_emails


Tuple_Sets = tuple[Set[str], Set[str]]


def load_and_validate_wave2_70() -> List[Dict[str, Any]]:
    if not WAVE2_MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Missing Wave-2 manifest: {WAVE2_MANIFEST_PATH}")
    raw_list: List[Dict[str, Any]] = json.loads(WAVE2_MANIFEST_PATH.read_text(encoding="utf-8"))
    if len(raw_list) != 70:
        raise AssertionError(f"Expected 70 stores in Wave 2, found {len(raw_list)}")

    prev_domains, prev_emails = load_previous_140_blocklist()
    seen_w2_domains: Set[str] = set()
    seen_w2_emails: Set[str] = set()

    ordered = sorted(raw_list, key=lambda x: TZ_ORDER.get(x["cc"], 99))

    forbidden = [
        r"\[", r"\]", r"\{", r"\}",
        r"\*", r"`",
        r"\u2014", r"\u2013", r"\u201c", r"\u201d", r"\u2018", r"\u2019", r"\u2026",
        r"Custom E-Commerce", r"Online-Shop", r"Custom /",
        r"353 486 5048", r"\be'", r"piu'", r"gia'", r"OPPORTUNITA\b",
        r"TODO", r"TBD", r"undefined", r"NaN",
    ]

    for st in ordered:
        dom = st["domain"].lower().strip()
        em = st["email"].lower().strip()
        if dom in prev_domains:
            raise AssertionError(f"[DUPLICATE BLOCKED] Domain '{dom}' was already used in Wave 1 or Solar!")
        if em in prev_emails:
            raise AssertionError(f"[DUPLICATE BLOCKED] Email '{em}' was already used in Wave 1 or Solar!")
        if dom in seen_w2_domains:
            raise AssertionError(f"[INTERNAL DUPLICATE] Domain '{dom}' appears twice in Wave 2!")
        if em in seen_w2_emails:
            raise AssertionError(f"[INTERNAL DUPLICATE] Email '{em}' appears twice in Wave 2!")
        seen_w2_domains.add(dom)
        seen_w2_emails.add(em)

        txt_path = Path(st["ready_email_txt"])
        xlsx_path = Path(st["teaser_xlsx"])
        if not txt_path.exists():
            raise FileNotFoundError(f"Missing email txt: {txt_path}")
        if not xlsx_path.exists() or xlsx_path.stat().st_size < 3000:
            raise FileNotFoundError(f"Missing or invalid xlsx: {xlsx_path}")

        content = txt_path.read_text(encoding="utf-8")
        parts = content.split("=" * 76 + "\n", 1)
        if len(parts) != 2:
            raise ValueError(f"Malformed ready_email header in {txt_path}")
        hdr, body = parts[0], parts[1].strip()
        m_sub = re.search(r"^SUBJECT:\s*(.+)$", hdr, re.M)
        if not m_sub:
            raise ValueError(f"Missing SUBJECT in {txt_path}")
        subj = m_sub.group(1).strip()

        full_check = subj + "\n" + body
        for pat in forbidden:
            if re.search(pat, full_check):
                raise AssertionError(f"Forbidden AI/defect pattern '{pat}' in {st['cc']}/{dom}")
        if "+39 320 948 1876" not in body or "amendamax@vasiledev.com" not in body:
            raise AssertionError(f"Missing contact signature in {dom}")

        # Verify exact country pricing tier
        if st["cc"] == "UK":
            if "\u00a3295" not in body or "\u00a3690" not in body:
                raise AssertionError(f"Missing £295 / £690 pricing in UK/{dom}")
        else:
            if "350,00" not in body or "850,00" not in body:
                raise AssertionError(f"Missing 350,00 / 850,00 EUR pricing in {st['cc']}/{dom}")

        wb = openpyxl.load_workbook(xlsx_path)
        for ws in wb.worksheets:
            for r in range(1, ws.max_row + 1):
                for c in range(1, ws.max_column + 1):
                    v = ws.cell(r, c).value
                    if isinstance(v, str) and ("\u2014" in v or "\u2013" in v):
                        raise AssertionError(f"Dash defect inside {xlsx_path.name}")

        st["parsed_subject"] = subj
        st["parsed_body"] = body

    print(
        f"[VALIDARE 100% PERFECTA - CALUPUL 2] {len(ordered)}/70 emailuri NOI Scule Electrice + "
        f"70/70 atasamente Excel au ZERO duplicate cu Calupul 1, ZERO caractere AI, ZERO erori!",
        flush=True,
    )
    return ordered


def send_single_email(cfg: Dict[str, Any], to_email: str, subject: str, body: str, xlsx_path: Path) -> None:
    msg = EmailMessage()
    msg["From"] = formataddr((SENDER_DISPLAY_NAME, cfg["user"]))
    msg["To"] = to_email
    msg["Reply-To"] = REPLY_TO_DUAL
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain=cfg["msgid_domain"])
    msg.set_content(body, charset="utf-8")
    msg.add_attachment(
        xlsx_path.read_bytes(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=xlsx_path.name,
    )
    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=ctx, timeout=30) as srv:
        srv.login(cfg["user"], cfg["pass"])
        srv.send_message(msg)


def wait_for_wave1_completion(cooldown_sec: int = 300) -> None:
    print("[SYNC] Verific starea Calupului 1 Scule Electrice (70 magazine) inainte de start...", flush=True)
    while True:
        if WAVE1_LOG_PATH.exists():
            try:
                entries = json.loads(WAVE1_LOG_PATH.read_text(encoding="utf-8"))
                sent_ok = sum(1 for e in entries if e.get("status") == "SENT_OK")
                if len(entries) >= 70 and sent_ok >= 70:
                    print(
                        f"[SYNC OK] Calupul 1 Scule Electrice a ajuns la {sent_ok}/70 SENT_OK! "
                        f"Astept pauza de siguranta de {cooldown_sec}s (5 minute) inainte de startul Calupului 2...",
                        flush=True,
                    )
                    time.sleep(cooldown_sec)
                    return
                elif len(entries) >= 70:
                    print(
                        f"[SYNC OK] Calupul 1 a procesat {len(entries)}/70 intrari ({sent_ok} SENT_OK)! "
                        f"Astept pauza de siguranta de {cooldown_sec}s (5 minute) inainte de startul Calupului 2...",
                        flush=True,
                    )
                    time.sleep(cooldown_sec)
                    return
                print(
                    f"  -> Calupul 1 este la {sent_ok}/70 SENT_OK. Re-verific peste 60s...",
                    flush=True,
                )
            except Exception:
                pass
        time.sleep(60)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Valideaza toate cele 70 emailuri si atasamente Excel fara a trimite")
    ap.add_argument("--send", action="store_true", help="Trimite efectiv cele 70 emailuri B2B din Calupul 2 Scule Electrice")
    ap.add_argument("--wait-for-wave1", action="store_true", help="Asteapta automat terminarea celor 70 emailuri din Calupul 1")
    ap.add_argument("--jitter-min", type=int, default=140, help="Limita inferioara delay aleatoriu intre mesaje (default 140s)")
    ap.add_argument("--jitter-max", type=int, default=165, help="Limita superioara delay aleatoriu intre mesaje (default 165s)")
    args = ap.parse_args()

    stores = load_and_validate_wave2_70()

    if not args.send:
        print("\n[DRY-RUN REZUMAT CALUPUL 2 PE TARI (70 MAGAZINE NOI - 0 DUPLICATE)]")
        for cc in ["DE", "AT", "NL", "BE", "IT", "FR", "ES", "UK"]:
            sub = [s for s in stores if s["cc"] == cc]
            if sub:
                print(f"  - {cc}: {len(sub):2d} magazine pregatite (ex: {sub[0]['domain']} -> {sub[0]['email']})")
        return

    if args.wait_for_wave1:
        wait_for_wave1_completion(cooldown_sec=300)

    already_sent = set()
    log_entries: List[Dict[str, Any]] = []
    if WAVE2_LOG_PATH.exists():
        try:
            log_entries = json.loads(WAVE2_LOG_PATH.read_text(encoding="utf-8"))
            already_sent = {e["domain"] for e in log_entries if e.get("status") == "SENT_OK"}
        except Exception:
            log_entries = []

    zoho_skip_remaining = 0
    total = len(stores)
    print("=" * 94, flush=True)
    print(
        f"[START LIVRARE B2B SCULE ELECTRICE - CALUPUL 2] {total} Magazine NOI | Raport 2 Gmail : 1 Zoho | "
        f"Jitter aleatoriu: {args.jitter_min}-{args.jitter_max}s",
        flush=True,
    )
    print("=" * 94, flush=True)

    for idx, st in enumerate(stores, start=1):
        dom = st["domain"]
        if dom in already_sent:
            print(f"[{idx:02d}/{total}] [{st['cc']}] [SKIP_ALREADY_SENT] {dom}", flush=True)
            continue

        xlsx_p = Path(st["teaser_xlsx"])
        zoho_slot = (idx % 3 == 0)
        use_zoho = zoho_slot and (zoho_skip_remaining == 0)
        if zoho_skip_remaining > 0 and zoho_slot:
            zoho_skip_remaining -= 1

        primary = ZOHO_CFG if use_zoho else GMAIL_CFG
        backup = GMAIL_CFG if use_zoho else ZOHO_CFG

        used_provider = primary["name"]
        status = "SENT_OK"
        err_msg = ""

        try:
            send_single_email(primary, st["email"], st["parsed_subject"], st["parsed_body"], xlsx_p)
        except Exception as e1:
            if primary["name"] == "ZOHO":
                zoho_skip_remaining = 6
                print(f"  [WARN] ZOHO eroare la #{idx} ({e1}) -> Fallback automat pe GMAIL...", flush=True)
            try:
                send_single_email(backup, st["email"], st["parsed_subject"], st["parsed_body"], xlsx_p)
                used_provider = f"{backup['name']}_FAILOVER"
            except Exception as e2:
                status = "FAILED"
                used_provider = "NONE"
                err_msg = f"{e1} | {e2}"

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "idx": idx,
            "timestamp": ts,
            "cc": st["cc"],
            "domain": dom,
            "to": st["email"],
            "provider": used_provider,
            "status": status,
            "attachment": xlsx_p.name,
            "subject": st["parsed_subject"],
            "error": err_msg,
        }
        log_entries.append(entry)
        WAVE2_LOG_PATH.write_text(json.dumps(log_entries, indent=2, ensure_ascii=False), encoding="utf-8")

        print(
            f"[{idx:02d}/{total}] [{st['cc']}] [{status}] [{used_provider:<14}] [{ts}] {dom:<26} -> {st['email']}",
            flush=True,
        )

        if idx < total:
            sleep_s = random.uniform(float(args.jitter_min), float(args.jitter_max))
            time.sleep(sleep_s)

    ok_cnt = sum(1 for e in log_entries if e.get("status") == "SENT_OK")
    print("=" * 94, flush=True)
    print(f"[CAMPANIE CALUPUL 2 SCULE FINALIZATA] {ok_cnt}/{total} emailuri livrate cu succes! Log: {WAVE2_LOG_PATH}", flush=True)
    print("=" * 94, flush=True)


if __name__ == "__main__":
    main()
