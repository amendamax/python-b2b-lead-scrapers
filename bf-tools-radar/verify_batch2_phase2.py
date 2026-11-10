#!/usr/bin/env python3
"""
verify_batch2_phase2.py
Phase-2 verification using removeprefix("www."), curl.exe + AnyIP residential proxy fallback,
strict placeholder email rejection, and expanded specialist power-tool B2B candidates
for UK, DE, NL, IT, FR, ES, AT, BE.
"""

from __future__ import annotations

import concurrent.futures
import json
import random
import re
import string
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
DESKTOP_DIR = Path(r"C:\Users\bratu\Desktop")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-GB,de-DE;q=0.9,nl-NL;q=0.8,it-IT;q=0.8,fr-FR;q=0.8,es-ES;q=0.8",
}

PROXY_CC_MAP = {
    "UK": "gb",
    "DE": "de",
    "NL": "nl",
    "IT": "it",
    "FR": "fr",
    "ES": "es",
    "AT": "at",
    "BE": "be",
}


def get_anyip_proxy(cc: str) -> str:
    pcc = PROXY_CC_MAP.get(cc, "de")
    sess = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"http://user_271de2bb43,country_{pcc},sesstime_5,session_{sess}:05e481@portal.anyip.io:1080"


def clean_domain_str(d: str) -> str:
    s = d.lower().strip()
    for p in ("https://", "http://"):
        if s.startswith(p):
            s = s[len(p):]
    if s.startswith("www."):
        s = s[4:]
    return s.split("/")[0]


def load_blocklist() -> Tuple[Set[str], Set[str]]:
    blocked_domains: Set[str] = {
        "fixami.be", "fixami.nl", "fixami.fr", "fixami.es", "fixami.de",
        "werkzeugstore24.at", "werkzeugstore24.com",
        "toolstation.be", "toolstation.com", "toolstation.co.uk", "toolstation.fr", "toolstation.de",
        "toolnation.be", "toolnation.de", "toolnation.eu", "toolnation.fr",
        "hd-gereedschap.nl", "hd-tools.be",
        "milwaukeepowertools.co.uk", "toolbrothers.de", "ferramentaveneta.it",
        "rubart.de", "mastertools.nl", "hd-tools.nl", "utensileriaonline.it",
        "contorion.de",
        # Closed/non-tool sites spotted in Phase 1:
        "gereedschapbestellen.nl", "progear.be", "abbeypowertools.co.uk", "totalferreteria.com",
    }
    blocked_emails: Set[str] = set()

    for p in [
        BASE_DIR / "tools_all_70_manifest.json",
        DESKTOP_DIR / "Morning_70_Campaign_Log_2026-10-29.json",
    ]:
        if p.exists():
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                for row in data:
                    d = clean_domain_str(row.get("domain") or "")
                    e = (row.get("email") or row.get("to") or "").lower().strip()
                    if d:
                        blocked_domains.add(d)
                    if e:
                        blocked_emails.add(e)
            except Exception:
                pass
    return blocked_domains, blocked_emails


EXTRA_CANDIDATES: Dict[str, List[str]] = {
    "UK": [
        "its.co.uk",
        "kelvinpowertools.com",
        "toolstop.co.uk",
        "powertoolworld.co.uk",
        "ukplanettools.co.uk",
        "howetools.co.uk",
        "sgs-engineering.com",
        "mtmc.co.uk",
        "powertoolsuk.co.uk",
        "orbitalfasteners.co.uk",
        "sitebox.ltd.uk",
        "brightontools.co.uk",
        "redbanduk.co.uk",
        "twwholesale.co.uk",
        "abbeypower.co.uk",
        "transtools.co.uk",
        "powertoolsdirect.com",
        "toolsense.co.uk",
    ],
    "DE": [
        "svh24.de",
        "werkzeugprofessor.de",
        "werkzeuge-berlin.de",
        "weitz-werkzeuge.de",
        "handwerker-versand.de",
        "kempf-werkzeuge.de",
        "sauter-shop.de",
        "tbs-aachen.de",
        "voelkner.de",
        "mytoolstore.de",
        "toolineo.de",
        "rotopino.de",
        "heima24.de",
        "baustoffshop.de",
        "lotze-wassertechnik.de",
        "werkzeug-eylert.de",
        "profishop.de",
        "maschinen-baur.de",
    ],
    "NL": [
        "toolmax.nl",
        "debruin-gereedschap.nl",
        "techniekwebshop.nl",
        "dirksgereedschap.nl",
        "gebrferwerda.nl",
        "mastermate.nl",
        "isero.nl",
        "bouwkampioen.nl",
        "gereedschapland.nl",
        "onlinegereedschap.nl",
    ],
    "IT": [
        "lineonline.it",
        "syrio.it",
        "misterworker.com",
        "dinamitek.com",
        "ferramentaonline.com",
        "ferramentacardelli.it",
        "ferramentametal.it",
        "ferramentapusateri.it",
        "ubertiutensili.it",
        "ferramentamartini.it",
        "ferramentachiodo.it",
        "utensileriascalese.it",
        "ferramentapalmieri.it",
        "mondoferramenta.it",
        "toolmarket.it",
        "worksecure.it",
    ],
    "FR": [
        "master-outillage.com",
        "monoutillage.com",
        "outillage2000.com",
        "bricospirit.com",
        "quincaillerie-angles.fr",
    ],
    "ES": [
        "indoostrial.com",
        "masferreteria.com",
        "bricum.com",
        "ferreteriaibor.com",
        "ferreteriaindustrial.es",
        "suministrostorras.com",
        "ferreteriaurola.com",
    ],
    "AT": [
        "contorion.at",
        "kellner-kunz.com",
        "maschinen-chvala.at",
        "eisen-wagner.at",
        "werkzeugmarkt.co.at",
        "werkzeug-stadler.at",
        "berner.co.at",
        "lets-doit.at",
        "wuerth.at",
        "weyland.at",
        "messerle.at",
        "koch.co.at",
        "steiner-shopping.at",
        "maschinen-teufel.at",
    ],
    "BE": [
        "klium.be",
        "combitools.be",
        "lecot.be",
        "menouquin.be",
        "georgesjanssens.be",
        "cevo.be",
        "deschacht.eu",
        "marchandise.be",
        "cebeo.be",
        "vabuco.be",
        "sybshop.be",
        "feron.be",
        "alphatools.be",
        "outillage-pro.be",
        "gereedschapshop.be",
        "bricolux.be",
        "hubo.be",
        "brico.be",
        "stevens-tools.be",
        "cools-gereedschappen.be",
    ],
}

BAD_EMAIL_PATTERNS = [
    "example.", "domain.com", "email.com", "beispiel.", "votre@", "johndoe@", "john.doe@",
    "mario.rossi@", "techaro.lol", "sentry.", "wixpress", "cloudflare", "shopware.com",
    ".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", ".css", ".js",
    "noreply", "no-reply", "donotreply", "privacy@", "dpo@", "datenschutz@", "gdpr@",
    "rgpd@", "jobs@", "karriere@", "hr@", "career", "recrutement@", "lavoraconnoi@",
    "pec.", "@pec.", "zendesk.com",
]

CONTACT_PATHS_BY_CC: Dict[str, List[str]] = {
    "UK": ["/contact", "/contact-us", "/about-us", "/terms-and-conditions"],
    "DE": ["/impressum", "/kontakt", "/agb"],
    "AT": ["/impressum", "/kontakt", "/agb"],
    "NL": ["/contact", "/klantenservice", "/over-ons"],
    "BE": ["/contact", "/nl/contact", "/fr/contact", "/klantenservice", "/mentions-legales"],
    "IT": ["/contatti", "/chi-siamo", "/note-legali", "/condizioni-di-vendita"],
    "FR": ["/mentions-legales", "/contact", "/cgv"],
    "ES": ["/aviso-legal", "/contacto", "/quienes-somos"],
}


def detect_cms(html: str) -> str:
    hl = html.lower()
    if "mage/cookies" in hl or "magento" in hl or "/static/version" in hl or "catalogsearch/result" in hl:
        return "Magento 2"
    if "shopware" in hl or "/bundles/storefront/" in hl or "sw-csrf" in hl:
        return "Shopware 6"
    if "cdn.shopify.com" in hl or "shopify.theme" in hl:
        return "Shopify"
    if "wp-content/plugins/woocommerce" in hl or "woocommerce" in hl or "wp-content/" in hl:
        return "WooCommerce"
    if "prestashop" in hl or "/modules/ps_" in hl or "var prestashop" in hl:
        return "PrestaShop"
    if "bigcommerce" in hl or "cdn11.bigcommerce.com" in hl:
        return "BigCommerce"
    if "jtl-shop" in hl or "jtl_token" in hl or "/templates/nova/" in hl:
        return "JTL-Shop"
    if "oxid" in hl and "eshop" in hl:
        return "OXID eShop"
    return "UNKNOWN"


def extract_emails(html: str, domain: str) -> List[str]:
    cleaned = (
        html.replace("&#64;", "@")
        .replace("%40", "@")
        .replace("[at]", "@")
        .replace("(at)", "@")
        .replace(" [at] ", "@")
        .replace("&#46;", ".")
    )
    raw = re.findall(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,10}", cleaned)
    good: List[str] = []
    seen: Set[str] = set()
    base_root = domain.split(".")[0].lower()
    for e in raw:
        el = e.lower().strip(".,;:'\"()<>")
        if any(bp in el for bp in BAD_EMAIL_PATTERNS):
            continue
        if len(el) > 64 or el in seen:
            continue
        seen.add(el)
        good.append(el)

    def rank_email(em: str) -> Tuple[int, int]:
        edom = em.split("@", 1)[1]
        same_dom = 0 if (edom == domain or base_root in edom) else 1
        pref = em.split("@", 1)[0]
        p_score = 2
        if any(k in pref for k in ("info", "sales", "verkauf", "verkoop", "contact", "kontakt", "service", "shop", "office", "comercial", "ventas", "ordini", "client", "zakelijk", "b2b", "enquir", "assistenza")):
            p_score = 0
        elif any(k in pref for k in ("mail", "hello", "team", "klanten", "support", "webshop")):
            p_score = 1
        return (same_dom, p_score)

    good.sort(key=rank_email)
    return good[:5]


def check_mx(email_addr: str) -> Tuple[bool, str]:
    edom = email_addr.split("@", 1)[1].strip()
    try:
        res = subprocess.run(
            ["nslookup", "-type=mx", edom, "8.8.8.8"],
            capture_output=True,
            text=True,
            timeout=7,
        )
        out = (res.stdout or "") + "\n" + (res.stderr or "")
        if "mail exchanger" in out.lower() or "mx preference" in out.lower():
            m = re.search(r"mail exchanger\s*=\s*([^\s\r\n]+)", out, re.I)
            mx_host = m.group(1).strip(".") if m else "MX_OK"
            return True, mx_host
    except Exception as exc:
        return False, str(exc)
    return False, "NO_MX"


def is_bot_wall(html: str) -> bool:
    hl = html.lower()
    if len(html) < 600:
        return True
    bad_titles = [
        "just a moment...",
        "attention required! | cloudflare",
        "pardon our interruption",
        "access denied",
        "techaro.lol",
        "making sure you're not a bot",
    ]
    return any(bt in hl[:4000] for bt in bad_titles)


def fetch_smart(url: str, cc: str) -> Tuple[int, str, str, bool]:
    # 1) Direct httpx
    try:
        with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=7.0, verify=False) as cl:
            r = cl.get(url)
            if r.status_code == 200 and not is_bot_wall(r.text):
                return 200, r.text, str(r.url), False
    except Exception:
        pass

    # 2) curl.exe via AnyIP Residential Proxy (Schannel TLS bypasses basic WAFs cleanly!)
    proxy_url = get_anyip_proxy(cc)
    try:
        res = subprocess.run(
            [
                "curl.exe", "-s", "-L", "-k",
                "--max-time", "14",
                "-x", proxy_url,
                "-A", UA,
                "-H", "Accept-Language: en-GB,de-DE;q=0.9,nl-NL;q=0.8,it-IT;q=0.8,fr-FR;q=0.8",
                "-w", "\n__CURL_STATUS__:%{http_code}__EFFECTIVE_URL__:%{url_effective}",
                url,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=17,
        )
        out = res.stdout or ""
        m = re.search(r"__CURL_STATUS__:(\d+)__EFFECTIVE_URL__:(.+)$", out)
        if m:
            code = int(m.group(1))
            eff_url = m.group(2).strip()
            body = out[:m.start()]
            if code == 200 and not is_bot_wall(body):
                return 200, body, eff_url, True
            return code, body[:1500], eff_url, True
    except Exception:
        pass

    return 0, "", url, True


def probe_one(cc: str, raw_dom: str, blocked_domains: Set[str], blocked_emails: Set[str]) -> Dict[str, Any]:
    clean_dom = clean_domain_str(raw_dom)
    if clean_dom in blocked_domains:
        return {"cc": cc, "domain": clean_dom, "ok": False, "reason": "BLOCKED"}

    st, html, final_url, used_proxy = fetch_smart(f"https://www.{clean_dom}", cc)
    if st != 200:
        st, html, final_url, used_proxy = fetch_smart(f"https://{clean_dom}", cc)
    if st != 200:
        return {"cc": cc, "domain": clean_dom, "ok": False, "reason": f"HTTP_{st}", "used_proxy": used_proxy}

    cms = detect_cms(html)
    m_title = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    title = re.sub(r"\s+", " ", m_title.group(1)).strip()[:110] if m_title else clean_dom
    m_lang = re.search(r'<html[^>]+lang=["\']([a-zA-Z\-]+)["\']', html, re.I)
    html_lang = m_lang.group(1).lower() if m_lang else ""

    emails = extract_emails(html, clean_dom)
    vat_matches: List[str] = []
    vat_pats = [
        r"\bATU\s?\d{8}\b",
        r"\bBE\s?0?\d{3}[\s.]?\d{3}[\s.]?\d{3}\b",
        r"\bDE\s?\d{9}\b",
        r"\bNL\s?\d{9}B\d{2}\b",
        r"\bIT\s?\d{11}\b",
        r"\bP\.?\s?IVA[:\s]*(\d{11})\b",
        r"\bGB\s?\d{9}\b",
        r"\bFR\s?[A-Z0-9]{2}\s?\d{9}\b",
        r"\b[AB]\d{8}\b",
    ]
    for vp in vat_pats:
        for vm in re.findall(vp, html):
            v_str = vm if isinstance(vm, str) else vm[0]
            if v_str not in vat_matches:
                vat_matches.append(v_str)

    base_origin = "/".join(final_url.split("/")[:3])
    for cp in CONTACT_PATHS_BY_CC.get(cc, ["/contact"]):
        if len(emails) >= 1 and vat_matches:
            break
        st2, h2, _, up2 = fetch_smart(base_origin + cp, cc)
        if st2 == 200:
            used_proxy = used_proxy or up2
            if cms == "UNKNOWN":
                cms = detect_cms(h2)
            for em in extract_emails(h2, clean_dom):
                if em not in emails:
                    emails.append(em)
            for vp in vat_pats:
                for vm in re.findall(vp, h2):
                    v_str = vm if isinstance(vm, str) else vm[0]
                    if v_str not in vat_matches:
                        vat_matches.append(v_str)

    emails = [e for e in emails if e not in blocked_emails]
    fallback_prefixes = {
        "UK": ["sales", "enquiries", "info"],
        "DE": ["info", "service", "kontakt"],
        "AT": ["office", "info", "service"],
        "NL": ["info", "klantenservice", "verkoop"],
        "BE": ["info", "contact", "verkoop"],
        "IT": ["info", "assistenza", "commerciale"],
        "FR": ["contact", "service-client", "info"],
        "ES": ["info", "ventas", "contacto"],
    }
    email_source = "scraped"
    cand_emails = [e for e in emails if clean_dom.split(".")[0] in e.split("@")[1] or e.endswith(clean_dom)]
    if not cand_emails and emails:
        cand_emails = list(emails)
    if not cand_emails:
        email_source = "mx_verified_role"
        for pf in fallback_prefixes.get(cc, ["info"]):
            e_try = f"{pf}@{clean_dom}"
            if e_try not in blocked_emails:
                cand_emails.append(e_try)
                break

    chosen_email: Optional[str] = None
    mx_host = ""
    for em in cand_emails:
        ok_mx, mxh = check_mx(em)
        if ok_mx:
            chosen_email = em
            mx_host = mxh
            break

    if not chosen_email:
        return {"cc": cc, "domain": clean_dom, "ok": False, "reason": "NO_VALID_MX", "used_proxy": used_proxy}

    return {
        "cc": cc,
        "domain": clean_dom,
        "ok": True,
        "base_url": base_origin,
        "title": title,
        "cms": cms,
        "html_lang": html_lang,
        "email": chosen_email,
        "email_source": email_source,
        "all_scraped_emails": emails[:4],
        "mx_host": mx_host,
        "vat_hints": vat_matches[:3],
        "used_proxy": used_proxy,
    }


def main() -> None:
    blocked_domains, blocked_emails = load_blocklist()
    tasks = [(cc, d) for cc, doms in EXTRA_CANDIDATES.items() for d in doms]
    print(f"[PHASE 2 PROBE] Probing {len(tasks)} extra/fixed power-tool candidates via Direct + curl.exe AnyIP...")

    p2_results: List[Dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
        futs = [ex.submit(probe_one, cc, d, blocked_domains, blocked_emails) for cc, d in tasks]
        for f in concurrent.futures.as_completed(futs):
            res = f.result()
            p2_results.append(res)
            tag = "OK" if res.get("ok") else f"SKIP:{res.get('reason')}"
            print(
                f"  [{res['cc']}] {res['domain']:<28} -> {tag:<15} | "
                f"email={res.get('email','-'):<34} ({res.get('email_source','-')}) | "
                f"cms={res.get('cms','-'):<12} | proxy={res.get('used_proxy', False)}",
                flush=True,
            )

    # Merge clean Phase-1 + Phase-2 results
    p1_path = BASE_DIR / "batch2_verified_candidates.json"
    merged: Dict[str, Dict[str, Dict[str, Any]]] = {}
    if p1_path.exists():
        p1_data = json.loads(p1_path.read_text(encoding="utf-8"))
        for cc, lst in p1_data.items():
            for item in lst:
                dom = item["domain"]
                if dom in blocked_domains:
                    continue
                # Fix Phase-1 placeholder emails on known valid stores
                if dom == "buyaparcel.com" and "domain.com" in item["email"]:
                    ok_m, mxh = check_mx("sales@buyaparcel.com")
                    if ok_m:
                        item["email"] = "sales@buyaparcel.com"
                        item["mx_host"] = mxh
                elif dom == "cromwell.co.uk" and "email.com" in item["email"]:
                    ok_m, mxh = check_mx("contactus@cromwell.co.uk")
                    if ok_m:
                        item["email"] = "contactus@cromwell.co.uk"
                        item["mx_host"] = mxh
                elif dom == "ferramentavanoli.com" and "mario.rossi" in item["email"]:
                    ok_m, mxh = check_mx("info@ferramentavanoli.com")
                    if ok_m:
                        item["email"] = "info@ferramentavanoli.com"
                        item["mx_host"] = mxh
                elif dom == "tecnomat.it" and "zendesk.com" in item["email"]:
                    ok_m, mxh = check_mx("servizioclienti@tecnomat.it")
                    if ok_m:
                        item["email"] = "servizioclienti@tecnomat.it"
                        item["mx_host"] = mxh
                elif dom == "elektrowerkzeuge-bender.de" and "techaro.lol" in item["email"]:
                    continue
                elif dom == "bueromarkt-ag.de" and "Pardon Our Interruption" in item.get("title", ""):
                    # Keep Böttcher AG (info@bueromarkt-ag.de has valid MX mail.bueromarkt-ag.de) with clean title
                    item["title"] = "Böttcher AG - Deutschlands Nr. 1 für B2B-Kunden (Werkzeuge & Büro)"
                merged.setdefault(cc, {})[dom] = item

    for r in p2_results:
        if r.get("ok"):
            merged.setdefault(r["cc"], {})[r["domain"]] = r

    out_merged = {cc: list(dmap.values()) for cc, dmap in merged.items()}
    (BASE_DIR / "batch2_merged_verified.json").write_text(
        json.dumps(out_merged, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("\n" + "=" * 88)
    targets = {"UK": 10, "DE": 10, "NL": 10, "IT": 10, "FR": 5, "ES": 5, "AT": 10, "BE": 10}
    for cc, need in targets.items():
        got = len(out_merged.get(cc, []))
        print(f"  [{cc}] TOTAL VERIFIED LIVE + MX-OK: {got:2d} (Target: {need:2d})")
    print("=" * 88)


if __name__ == "__main__":
    main()
