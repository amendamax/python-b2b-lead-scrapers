#!/usr/bin/env python3
r"""
resend_wave2_bounces.py
Retrimite prin Gmail (amendamax@gmail.com) cu pauza de 145s intre mesaje pozitiile din Calupul 2
care au returnat bounce 550 (cele 3 din Zoho + cele 4 identificate la scanarea IMAP din Gmail),
folosind adresele si pachetele Excel regenerate si auditate 100%, actualizand live logul de pe Desktop:
  C:\Users\bratu\Desktop\Tools_Wave2_70_Campaign_Log_2026-10-29.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from send_70_tools_wave2 import (
    GMAIL_CFG,
    WAVE2_LOG_PATH,
    load_and_validate_wave2_70,
    send_single_email,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ordered list: first the 3 Zoho 550 bounces, then the 4 Gmail 550.4.1 bounces found via IMAP
BOUNCE_REPLACEMENTS: List[Tuple[str, str, str]] = [
    # (old_bounced_email, old_domain, new_domain_in_manifest)
    ("info@toolsquare.be", "toolsquare.be", "vulpp.be"),
    ("info@fernandgeorges.be", "fernandgeorges.be", "georges.be"),
    ("info@syrio.it", "syrio.it", "syriosrl.it"),
    ("office@lets-doit.at", "lets-doit.at", "lets-doit.at"),
    ("info@clabots.be", "clabots.be", "clabots.be"),
    ("sales@buyaparcel.com", "buyaparcel.com", "buyaparcel.com"),
    ("sales@powertoolsuk.co.uk", "powertoolsuk.co.uk", "powertoolsuk.co.uk"),
    ("support@ukplanettools.co.uk", "ukplanettools.co.uk", "howetools.co.uk"),
]


def extract_body_from_ready_txt(ready_path: Path) -> str:
    raw = ready_path.read_text(encoding="utf-8")
    sep = "=" * 76
    if sep in raw:
        return raw.split(sep, 1)[1].strip()
    lines = raw.splitlines()
    return "\n".join(lines[4:]).strip()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pause", type=int, default=145, help="Pauza in secunde intre emailurile retrimise (default 145s)")
    ap.add_argument("--only-three", action="store_true", help="Trimite doar primele 3 (cele din Zoho)")
    args = ap.parse_args()

    validated_stores = load_and_validate_wave2_70()
    by_domain: Dict[str, Dict[str, Any]] = {s["domain"].lower().strip(): s for s in validated_stores}

    if not WAVE2_LOG_PATH.exists():
        raise FileNotFoundError(f"Missing Desktop log: {WAVE2_LOG_PATH}")
    log_entries: List[Dict[str, Any]] = json.loads(WAVE2_LOG_PATH.read_text(encoding="utf-8"))

    targets = BOUNCE_REPLACEMENTS[:3] if args.only_three else BOUNCE_REPLACEMENTS
    total = len(targets)

    print("=" * 96, flush=True)
    print(
        f"[START RETRIMITERE BOUNCE-URI 550 CALUPUL 2] {total} pozitii corectate | Provider: GMAIL | Pauza: {args.pause}s",
        flush=True,
    )
    print("=" * 96, flush=True)

    for step_i, (old_email, old_dom, new_dom) in enumerate(targets, start=1):
        st = by_domain[new_dom]
        ready_p = Path(st["ready_email_txt"])
        xlsx_p = Path(st["teaser_xlsx"])
        body_txt = extract_body_from_ready_txt(ready_p)
        to_email = st["email"]
        subj = st["subject"]

        # Find matching slot in Desktop log
        log_slot = None
        for entry in log_entries:
            if (entry.get("to") or "").lower().strip() == old_email.lower() or (entry.get("domain") or "").lower().strip() == old_dom.lower():
                log_slot = entry
                break
            # If already updated on an earlier partial run
            if (entry.get("domain") or "").lower().strip() == new_dom.lower() and old_email.lower() in (entry.get("replaced_bounce_from") or "").lower():
                log_slot = entry
                break

        if log_slot and (log_slot.get("to") or "").lower().strip() == to_email.lower() and old_email.lower() in (log_slot.get("replaced_bounce_from") or "").lower() and log_slot.get("status") == "SENT_OK":
            print(f"[{step_i}/{total}] [SKIP_ALREADY_RESENT] {new_dom} -> {to_email}", flush=True)
            continue

        send_single_email(GMAIL_CFG, to_email, subj, body_txt, xlsx_p)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        slot_idx = log_slot["idx"] if log_slot else -1

        if log_slot is not None:
            log_slot["timestamp"] = ts
            log_slot["cc"] = st["cc"]
            log_slot["domain"] = new_dom
            log_slot["to"] = to_email
            log_slot["provider"] = "GMAIL"
            log_slot["status"] = "SENT_OK"
            log_slot["attachment"] = xlsx_p.name
            log_slot["subject"] = subj
            log_slot["error"] = ""
            log_slot["replaced_bounce_from"] = f"{old_dom} ({old_email})"
        else:
            log_entries.append({
                "idx": len(log_entries) + 1,
                "timestamp": ts,
                "cc": st["cc"],
                "domain": new_dom,
                "to": to_email,
                "provider": "GMAIL",
                "status": "SENT_OK",
                "attachment": xlsx_p.name,
                "subject": subj,
                "error": "",
                "replaced_bounce_from": f"{old_dom} ({old_email})",
            })

        WAVE2_LOG_PATH.write_text(json.dumps(log_entries, indent=2, ensure_ascii=False), encoding="utf-8")
        print(
            f"[{step_i}/{total}] [IDX {slot_idx:02d}/70] [{st['cc']}] [RESENT_OK] [GMAIL] [{ts}] "
            f"{new_dom:<24} -> {to_email:<30} (inlocuit bounce 550: {old_email})",
            flush=True,
        )

        if step_i < total:
            time.sleep(args.pause)

    print("=" * 96, flush=True)
    print(f"[FINALIZAT] {total}/{total} pozitii cu bounce 550 retrimise cu succes si actualizate in {WAVE2_LOG_PATH}!", flush=True)
    print("=" * 96, flush=True)


if __name__ == "__main__":
    main()
