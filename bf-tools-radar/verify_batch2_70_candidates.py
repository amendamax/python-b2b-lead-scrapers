#!/usr/bin/env python3
"""
verify_batch2_70_candidates.py
Live HTTP + AnyIP Residential Proxy + Contact/Impressum Scraper + DNS MX Verifier
for Batch 2 (70 NEW European Power-Tool B2B Stores across UK, DE, NL, IT, FR, ES, AT, BE).
Guarantees ZERO overlap with Batch 1 (70 Tools) and Morning Solar (70 Solar).
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

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
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


def load_blocklist() -> Tuple[Set[str], Set[str]]:
    blocked_domains: Set[str] = {
        "fixami.be", "fixami.nl", "fixami.fr", "fixami.es", "fixami.de",
        "werkzeugstore24.at", "werkzeugstore24.com",
        "toolstation.be", "toolstation.com", "toolstation.co.uk", "toolstation.fr", "toolstation.de",
        "toolnation.be", "toolnation.de", "toolnation.eu", "toolnation.fr",
        "hd-gereedschap.nl", "hd-tools.be",
        "milwaukeepowertools.co.uk", "toolbrothers.de", "ferramentaveneta.it",
        "rubart.de", "mastertools.nl", "hd-tools.nl", "utensileriaonline.it",
        "contorion.de",  # Reserved for AT (contorion.at) so zero corporate duplication!
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
                    d = (row.get("domain") or "").lower().strip().lstrip("www.")
                    e = (row.get("email") or row.get("to") or "").lower().strip()
                    if d:
                        blocked_domains.add(d)
                    if e:
                        blocked_emails.add(e)
            except Exception as exc:
                print(f"[WARN] Failed reading {p}: {exc}")

    return blocked_domains, blocked_emails


CANDIDATES: Dict[str, List[str]] = {
    "UK": [
        "tooled-up.com",
        "kelvinpowertools.com",
        "its.co.uk",
        "toolstop.co.uk",
        "angliatoolcentre.co.uk",
        "howetools.co.uk",
        "ukplanettools.co.uk",
        "buyaparcel.com",
        "powertoolworld.co.uk",
        "dm-tools.co.uk",
        "axminstertools.com",
        "mtmc.co.uk",
        "abbeypowertools.co.uk",
        "alanwadkins.co.uk",
        "toolsense.co.uk",
        "tradetoolsdirect.co.uk",
        "powertoolsdirect.com",
        "sgs-engineering.com",
        "cromwell.co.uk",
    ],
    "DE": [
        "svh24.de",
        "cbdirekt.de",
        "bueromarkt-ag.de",
        "sauter-shop.de",
        "werkzeugprofessor.de",
        "tbs-aachen.de",
        "werkzeuge-berlin.de",
        "elektrowerkzeuge-bender.de",
        "handwerker-versand.de",
        "kempf-werkzeuge.de",
        "dittmar-werkzeuge.de",
        "maschinenhandel-gronau.de",
        "paulimot.de",
        "voelkner.de",
        "toptools24.de",
        "fachhandel-plus.de",
        "weitz-werkzeuge.de",
        "immer-gut.de",
        "digitalo.de",
    ],
    "NL": [
        "toolmax.nl",
        "kruis.nl",
        "toolsidee.nl",
        "gyzs.nl",
        "destil.nl",
        "elektramat.nl",
        "aic.nl",
        "keizers.nu",
        "indi.nl",
        "techniekwebshop.nl",
        "gereedschapbestellen.nl",
        "debruin-gereedschap.nl",
        "bouwmaat.nl",
        "boorhamer-shop.nl",
        "vanmelis.nl",
        "gebrferwerda.nl",
        "dirksgereedschap.nl",
        "toolprofessional.nl",
    ],
    "IT": [
        "lineonline.it",
        "syrio.it",
        "ferramentagiovannetti.it",
        "ferramentavanoli.com",
        "bricobravo.com",
        "agrieuro.com",
        "ferramentacardelli.it",
        "ferramentametal.it",
        "utensilbieffe.it",
        "ferramentapusateri.it",
        "ubertiutensili.it",
        "utilfer.it",
        "ferramentamartini.it",
        "ferramentachiodo.it",
        "ferramentapalmieri.it",
        "emporioditutto.it",
        "ferramentabolognese.it",
        "tecnomat.it",
    ],
    "FR": [
        "master-outillage.com",
        "outillage-online.fr",
        "monoutillage.com",
        "quincaillerie.pro",
        "mabeo-direct.com",
        "outillage2000.com",
        "euro-expos.com",
        "centrale-brico.com",
        "sider.biz",
        "manutan.fr",
        "stortle.com",
        "fixtout.fr",
    ],
    "ES": [
        "indoostrial.com",
        "masferreteria.com",
        "modregohogar.com",
        "bricolemar.com",
        "ferreteriacampollano.com",
        "totalferreteria.com",
        "ferreteriaibor.com",
        "ferreteriaindustrial.es",
        "ferreteriabras.com",
        "suministroslandaburu.com",
        "ferreteriaxerez.es",
    ],
    "AT": [
        "zgonc.at",
        "contorion.at",
        "spiral.at",
        "schachermayer.at",
        "haberkorn.com",
        "kellner-kunz.com",
        "neureiter-shop.at",
        "maschinen-chvala.at",
        "eisen-wagner.at",
        "kaindltech.at",
        "let-it-work.at",
        "baushop-express.at",
        "profimarkt.at",
        "werkzeugmarkt.co.at",
        "berner.co.at",
        "lagerhaus.at",
        "werkzeug-stadler.at",
        "handwerker-profi.at",
    ],
    "BE": [
        "klium.be",
        "combitools.be",
        "clabots.be",
        "progear.be",
        "georgesjanssens.be",
        "cevo.be",
        "santens.be",
        "deschacht.eu",
        "fernandgeorges.be",
        "outillage-placide.be",
        "cools-gereedschappen.be",
        "vynckier-tools.be",
        "christiaensen-tools.be",
        "dupont-outillage.be",
        "stevens-tools.be",
        "toolcenter.be",
        "mertens-gereedschappen.be",
        "bricolagedirect.be",
    ],
}

CONTACT_PATHS_BY_CC: Dict[str, List[str]] = {
    "UK": ["/contact", "/contact-us", "/about-us", "/terms-and-conditions", "/privacy-policy"],
    "DE": ["/impressum", "/kontakt", "/datenschutz", "/agb"],
    "AT": ["/impressum", "/kontakt", "/ueber-uns", "/agb"],
    "NL": ["/contact", "/klantenservice", "/over-ons", "/algemene-voorwaarden"],
    "BE": ["/contact", "/nl/contact", "/fr/contact", "/klantenservice", "/over-ons", "/mentions-legales", "/algemene-voorwaarden"],
    "IT": ["/contatti", "/chi-siamo", "/note-legali", "/privacy-policy", "/termini-e-condizioni"],
    "FR": ["/mentions-legales", "/contact", "/nous-contacter", "/cgv"],
    "ES": ["/aviso-legal", "/contacto", "/contactar", "/quienes-somos", "/condiciones-generales"],
}

BAD_EMAIL_PATTERNS = [
    "example.", "sentry.", "wixpress", "cloudflare", ".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif",
    ".css", ".js", "noreply", "no-reply", "donotreply", "privacy@", "dpo@", "datenschutz@", "gdpr@",
    "rgpd@", "jobs@", "karriere@", "hr@", "career", "recrutement@", "lavoraconnoi@",
]


def detect_cms(html: str, headers_dict: Dict[str, str]) -> str:
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
    if "jtl-shop" in hl or "jtl_token" in hl or "/templates/evo/" in hl or "/templates/nova/" in hl:
        return "JTL-Shop"
    if "oxid" in hl and "eshop" in hl:
        return "OXID eShop"
    return "UNKNOWN"


def extract_emails(html: str, domain: str) -> List[str]:
    # Decode common obfuscations
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

    # Sort preferring emails on the store's own domain and sales/info/contact/service prefixes
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


def fetch_url_with_anyip_fallback(url: str, cc: str) -> Tuple[int, str, str, bool]:
    # 1) Direct attempt
    try:
        with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=8.0, verify=False) as cl:
            r = cl.get(url)
            if r.status_code == 200 and len(r.text) > 800 and " attention required! | cloudflare" not in r.text.lower():
                return r.status_code, r.text, str(r.url), False
    except Exception:
        pass

    # 2) AnyIP Residential Proxy attempt
    proxy_url = get_anyip_proxy(cc)
    try:
        with httpx.Client(headers=HEADERS, proxy=proxy_url, follow_redirects=True, timeout=14.0, verify=False) as cl:
            r = cl.get(url)
            if r.status_code == 200 and len(r.text) > 500:
                return r.status_code, r.text, str(r.url), True
            return r.status_code, r.text[:2000], str(r.url), True
    except Exception as exc:
        return 0, str(exc), url, True


def probe_candidate(cc: str, domain: str, blocked_domains: Set[str], blocked_emails: Set[str]) -> Dict[str, Any]:
    clean_dom = domain.lower().strip().lstrip("www.")
    if clean_dom in blocked_domains:
        return {"cc": cc, "domain": clean_dom, "ok": False, "reason": "BLOCKED_DUPLICATE"}

    # Try https://www.{domain} then https://{domain}
    status, html, final_url, used_proxy = fetch_url_with_anyip_fallback(f"https://www.{clean_dom}", cc)
    if status != 200:
        status, html, final_url, used_proxy = fetch_url_with_anyip_fallback(f"https://{clean_dom}", cc)

    if status != 200:
        return {"cc": cc, "domain": clean_dom, "ok": False, "reason": f"HTTP_{status}"}

    cms = detect_cms(html, {})
    m_title = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    title = re.sub(r"\s+", " ", m_title.group(1)).strip()[:110] if m_title else clean_dom

    # Detect language on BE
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
        if len(emails) >= 2 and vat_matches:
            break
        st2, h2, _, up2 = fetch_url_with_anyip_fallback(base_origin + cp, cc)
        if st2 == 200 and len(h2) > 500:
            used_proxy = used_proxy or up2
            if cms == "UNKNOWN":
                cms = detect_cms(h2, {})
            for em in extract_emails(h2, clean_dom):
                if em not in emails:
                    emails.append(em)
            for vp in vat_pats:
                for vm in re.findall(vp, h2):
                    v_str = vm if isinstance(vm, str) else vm[0]
                    if v_str not in vat_matches:
                        vat_matches.append(v_str)

    # Filter out any blocked emails
    emails = [e for e in emails if e not in blocked_emails]

    chosen_email: Optional[str] = None
    mx_host = ""
    # If no scraped email found on page (e.g. JS-protected form), test standard domain addresses ONLY if domain MX exists!
    fallback_prefixes = {
        "UK": ["sales", "enquiries", "info", "customerservices"],
        "DE": ["info", "service", "kontakt", "shop"],
        "AT": ["office", "info", "verkauf", "service"],
        "NL": ["info", "klantenservice", "verkoop"],
        "BE": ["info", "verkoop", "contact", "klantenservice"],
        "IT": ["info", "commerciale", "assistenza", "ordini"],
        "FR": ["contact", "service-client", "info"],
        "ES": ["info", "ventas", "comercial", "contacto"],
    }
    email_Source = "scraped"
    cand_emails = list(emails)
    if not cand_emails:
        email_Source = "mx_verified_role"
        for pf in fallback_prefixes.get(cc, ["info"]):
            e_try = f"{pf}@{clean_dom}"
            if e_try not in blocked_emails:
                cand_emails.append(e_try)
                break

    for em in cand_emails:
        ok_mx, mxh = check_mx(em)
        if ok_mx:
            chosen_email = em
            mx_host = mxh
            break

    if not chosen_email:
        return {"cc": cc, "domain": clean_dom, "ok": False, "reason": "NO_VALID_MX"}

    return {
        "cc": cc,
        "domain": clean_dom,
        "ok": True,
        "base_url": base_origin,
        "title": title,
        "cms": cms,
        "html_lang": html_lang,
        "email": chosen_email,
        "email_source": email_Source,
        "all_scraped_emails": emails[:4],
        "mx_host": mx_host,
        "vat_hints": vat_matches[:3],
        "used_proxy": used_proxy,
    }


def main() -> None:
    blocked_domains, blocked_emails = load_blocklist()
    print(f"[BLOCKLIST LOADED] {len(blocked_domains)} blocked domains | {len(blocked_emails)} blocked emails")

    tasks: List[Tuple[str, str]] = []
    for cc, doms in CANDIDATES.items():
        for d in doms:
            tasks.append((cc, d))

    results: List[Dict[str, Any]] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=18) as ex:
        futs = [ex.submit(probe_candidate, cc, d, blocked_domains, blocked_emails) for cc, d in tasks]
        for f in concurrent.futures.as_completed(futs):
            res = f.result()
            results.append(res)
            status_tag = "OK" if res.get("ok") else f"SKIP:{res.get('reason')}"
            print(
                f"  [{res['cc']}] {res['domain']:<28} -> {status_tag:<18} | "
                f"email={res.get('email','-'):<34} ({res.get('email_source','-')}) | "
                f"cms={res.get('cms','-'):<12} | proxy={res.get('used_proxy', False)}",
                flush=True,
            )

    by_cc: Dict[str, List[Dict[str, Any]]] = {}
    for r in results:
        if r.get("ok"):
            by_cc.setdefault(r["cc"], []).append(r)

    # Sort within each country so scraped emails rank ahead of role fallbacks, keeping original candidate priority
    for cc, lst in by_cc.items():
        orig_order = {d: i for i, d in enumerate(CANDIDATES[cc])}
        lst.sort(key=lambda x: (0 if x["email_source"] == "scraped" else 1, orig_order.get(x["domain"], 99)))

    out_path = BASE_DIR / "batch2_verified_candidates.json"
    out_path.write_text(json.dumps(by_cc, indent=2, ensure_ascii=False), encoding="utf-8")

    print("\n" + "=" * 88)
    targets = {"UK": 10, "DE": 10, "NL": 10, "IT": 10, "FR": 5, "ES": 5, "AT": 10, "BE": 10}
    for cc, need in targets.items():
        got = len(by_cc.get(cc, []))
        scraped_cnt = sum(1 for x in by_cc.get(cc, [])[:need] if x["email_source"] == "scraped")
        print(f"  [{cc}] Verified Live + MX-OK: {got:2d} (Need {need:2d}) | Direct-Scraped Emails in Top-{need}: {scraped_cnt}/{min(got, need)}")
    print("=" * 88)


if __name__ == "__main__":
    main()
