#!/usr/bin/env python3
"""
verify_targeted_polish.py
Quick 10-second check on user-mentioned flagship examples (zgonc.at impressum, contorion.at,
lineonline.it, syrio.it, misterworker.com, kelvinpowertools.com, svh24.de, combitools.be)
and extra Belgian B2B power-tool specialists.
"""

from __future__ import annotations

import concurrent.futures
import re
import subprocess
import sys
from typing import Dict, List, Tuple

from verify_batch2_phase2 import check_mx, detect_cms, extract_emails, fetch_smart

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TARGETS: List[Tuple[str, str, List[str]]] = [
    ("AT", "zgonc.at", ["/pages/impressum", "/pages/kontakt"]),
    ("AT", "contorion.at", ["/impressum", "/service/kontakt"]),
    ("DE", "svh24.de", ["/impressum", "/kontakt"]),
    ("UK", "kelvinpowertools.com", ["/contact-us", "/about-us"]),
    ("NL", "toolmax.nl", ["/contact", "/klantenservice"]),
    ("IT", "lineonline.it", ["/contatti", "/chi-siamo"]),
    ("IT", "syrio.it", ["/contatti", "/chi-siamo"]),
    ("IT", "misterworker.com", ["/it/contatti", "/contatti"]),
    ("BE", "combitools.be", ["/contact", "/klantenservice"]),
    ("BE", "cebeo.be", ["/nl-be/contact", "/fr-be/contact", "/nl-be/privacy"]),
    ("BE", "claerbout.be", ["/contact", "/nl/contact"]),
    ("BE", "fima.be", ["/contact"]),
    ("BE", "toolsquare.be", ["/contact"]),
    ("BE", "powertools.be", ["/contact"]),
    ("BE", "dujardin-outillage.be", ["/contact"]),
    ("BE", "igmtools.be", ["/contact"]),
    ("BE", "btools.be", ["/contact"]),
    ("BE", "astools.be", ["/contact"]),
]


def check_target(cc: str, dom: str, paths: List[str]) -> None:
    st, html, eff, prx = fetch_smart(f"https://www.{dom}", cc)
    if st != 200:
        st, html, eff, prx = fetch_smart(f"https://{dom}", cc)
    emails = extract_emails(html, dom) if st == 200 else []
    cms = detect_cms(html) if st == 200 else "NO_HTTP"
    m_t = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S) if st == 200 else None
    title = re.sub(r"\s+", " ", m_t.group(1)).strip()[:80] if m_t else "-"
    origin = "/".join(eff.split("/")[:3]) if st == 200 else f"https://www.{dom}"
    for p in paths:
        st2, h2, _, _ = fetch_smart(origin + p, cc)
        if st2 == 200:
            for e in extract_emails(h2, dom):
                if e not in emails:
                    emails.append(e)
            if cms in ("UNKNOWN", "NO_HTTP"):
                cms = detect_cms(h2)
    mx_ok, mxh = check_mx(f"info@{dom}")
    print(f"[{cc}] {dom:<24} | HTTP={st} | CMS={cms:<11} | MX={mx_ok} ({mxh}) | emails={emails[:4]} | title={title}")


def main() -> None:
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
        list(ex.map(lambda t: check_target(*t), TARGETS))


if __name__ == "__main__":
    main()
