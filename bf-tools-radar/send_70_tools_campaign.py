#!/usr/bin/env python3
"""
send_70_tools_campaign.py
Dispatcher automat B2B pentru toate cele 70 de magazine specializate de Scule Electrice Profesionale
(RO 10 + DE 10 + NL 10 + IT 10 + FR 10 + ES 10 + UK 10), ordonate inteligent pe fus orar:
  1) RO (UTC+2)
  2) DE, NL, IT, FR, ES (UTC+1)
  3) UK (UTC+0)

Caracteristici de siguranta maxima:
  - Re-valideaza la sange toate cele 70 emailuri + 70 fisiere Excel Teaser (ZERO caractere AI, ZERO markdown, ZERO erori).
  - --wait-for-solar: asteapta automat finalizarea campaniei matinale de 70 emailuri Fotovoltaice
    (Morning_70_Campaign_Log_2026-10-29.json == 70/70) + pauza de siguranta, ca sa NU existe coliziune SMTP!
  - Dual-SMTP (Zoho Mail amendamax@vasiledev.com + Gmail amendamax@gmail.com) cu circuit-breaker inteligent
    si failover instantaneu pe Gmail.
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
from typing import Any, Dict, List, Tuple

import openpyxl

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
DESKTOP_DIR = Path(r"C:\Users\bratu\Desktop")
MANIFEST_PATH = BASE_DIR / "tools_all_70_manifest.json"
SOLAR_LOG_PATH = DESKTOP_DIR / "Morning_70_Campaign_Log_2026-10-29.json"
TOOLS_LOG_PATH = DESKTOP_DIR / "Tools_70_Campaign_Log_2026-10-29.json"

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
TZ_ORDER = {"RO": 1, "DE": 2, "NL": 3, "IT": 4, "FR": 5, "ES": 6, "UK": 7}


def load_and_validate_70_tools(only_wave1: bool = False) -> List[Dict[str, Any]]:
    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(f"Missing manifest: {MANIFEST_PATH}")
    raw_list: List[Dict[str, Any]] = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if only_wave1:
        raw_list = [x for x in raw_list if x["cc"] in ("RO", "IT", "DE")]

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
                raise AssertionError(f"Forbidden AI/defect pattern '{pat}' in {st['cc']}/{st['domain']}")
        if "+39 320 948 1876" not in body or "amendamax@vasiledev.com" not in body:
            raise AssertionError(f"Missing contact signature in {st['domain']}")

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
        f"[VALIDARE 100% PERFECTA] {len(ordered)}/{len(ordered)} emailuri Scule Electrice + "
        f"{len(ordered)}/{len(ordered)} atasamente Excel au ZERO caractere AI, ZERO markdown, ZERO erori!",
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


def wait_for_solar_completion(cooldown_sec: int = 300) -> None:
    print("[SYNC] Verific starea campaniei matinale Fotovoltaice (70 magazine) inainte de start...", flush=True)
    while True:
        if SOLAR_LOG_PATH.exists():
            try:
                entries = json.loads(SOLAR_LOG_PATH.read_text(encoding="utf-8"))
                if len(entries) >= 70:
                    print(
                        f"[SYNC OK] Campania Fotovoltaice a ajuns la {len(entries)}/70! "
                        f"Astept cooldown {cooldown_sec}s pentru protectie SMTP...",
                        flush=True,
                    )
                    time.sleep(cooldown_sec)
                    return
                print(
                    f"  -> Campania Fotovoltaice este la {len(entries)}/70. Re-verific peste 60s...",
                    flush=True,
                )
            except Exception:
                pass
        time.sleep(60)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Valideaza toate cele 70 emailuri si atasamente Excel fara a trimite")
    ap.add_argument("--send", action="store_true", help="Trimite efectiv cele 70 emailuri B2B Scule Electrice")
    ap.add_argument("--wave1-only", action="store_true", help="Trimite doar valul 1 (30 magazine: RO + IT + DE)")
    ap.add_argument("--wait-for-solar", action="store_true", help="Asteapta automat terminarea celor 70 emailuri Fotovoltaice")
    ap.add_argument("--jitter-min", type=int, default=140, help="Limita inferioara delay aleatoriu intre mesaje (default 140s)")
    ap.add_argument("--jitter-max", type=int, default=165, help="Limita superioara delay aleatoriu intre mesaje (default 165s)")
    args = ap.parse_args()

    stores = load_and_validate_70_tools(only_wave1=args.wave1_only)

    if not args.send:
        print("\n[DRY-RUN REZUMAT PE TARI]")
        for cc in ["RO", "DE", "NL", "IT", "FR", "ES", "UK"]:
            sub = [s for s in stores if s["cc"] == cc]
            if sub:
                print(f"  - {cc}: {len(sub)} magazine pregatite (ex: {sub[0]['domain']} -> {sub[0]['email']})")
        return

    if args.wait_for_solar:
        wait_for_solar_completion(cooldown_sec=300)

    already_sent = set()
    log_entries: List[Dict[str, Any]] = []
    if TOOLS_LOG_PATH.exists():
        try:
            log_entries = json.loads(TOOLS_LOG_PATH.read_text(encoding="utf-8"))
            already_sent = {e["domain"] for e in log_entries if e.get("status") == "SENT_OK"}
        except Exception:
            log_entries = []

    zoho_skip_remaining = 0
    total = len(stores)
    print("=" * 94, flush=True)
    print(
        f"[START LIVRARE B2B SCULE ELECTRICE] {total} Magazine | Raport 2 Gmail : 1 Zoho | "
        f"Jitter aleatoriu: {args.jitter_min}-{args.jitter_max}s (~{(args.jitter_min + args.jitter_max) * 3 // 2}s intre 2 emailuri Zoho)",
        flush=True,
    )
    print("=" * 94, flush=True)

    for idx, st in enumerate(stores, start=1):
        dom = st["domain"]
        if dom in already_sent:
            print(f"[{idx:02d}/{total}] [{st['cc']}] [SKIP_ALREADY_SENT] {dom}", flush=True)
            continue

        xlsx_p = Path(st["teaser_xlsx"])
        # Raport exact 2 Gmail : 1 Zoho (#1 Gmail, #2 Gmail, #3 Zoho, #4 Gmail, #5 Gmail, #6 Zoho => 47 Gmail + 23 Zoho)
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
                # Fallback instant pe Gmail + pauza temporara pe urmatoarele 6 sloturi Zoho daca apare vreo limita
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
        print(f"[{idx:02d}/{total}] [{st['cc']}] [{status}] [{used_provider:<14}] [{ts}] {dom:<26} -> {st['email']}", flush=True)

        log_entries.append({
            "index": idx,
            "cc": st["cc"],
            "domain": dom,
            "email": st["email"],
            "subject": st["parsed_subject"],
            "provider": used_provider,
            "status": status,
            "timestamp": ts,
            "error": err_msg,
        })
        TOOLS_LOG_PATH.write_text(json.dumps(log_entries, indent=2, ensure_ascii=False), encoding="utf-8")

        if idx < total:
            jitter_pause = random.randint(args.jitter_min, args.jitter_max)
            time.sleep(jitter_pause)

    ok_cnt = sum(1 for e in log_entries if e.get("status") == "SENT_OK")
    print("=" * 94, flush=True)
    print(f"[FINALIZAT] {ok_cnt}/{total} emailuri B2B Scule Electrice livrate cu succes! Log: {TOOLS_LOG_PATH}", flush=True)
    print("=" * 94, flush=True)


if __name__ == "__main__":
    main()
