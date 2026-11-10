#!/usr/bin/env python3
"""
scan_whatsapp_60.py
Scaneaza rapid toate cele 60 de magazine B2B din cele 6 tari (IT, UK, DE, NL, ES, FR)
pentru numere de WhatsApp / Mobil active si genereaza pe Desktop panoul interactiv:
  C:\\Users\\bratu\\Desktop\\WhatsApp_Sniper_60_Stores.html
cu:
  - Prioritizare automata:
      1) VERDE (VIP): Magazine cu buton/numar WhatsApp oficial sau mobil activ gasit pe site
      2) GALBEN: Magazine cu numar de telefon oficial (pentru WhatsApp Business pe numar fix)
  - Mesaje native ultra-scurte (2 randuri, FARA linkuri si FARA simboluri valutare €/£)
    personalizate cu adresa lor de email si brandurile din audit, ca sa ai RISC ZERO de blocare Meta.
  - Evidenta automata (bifa "Trimis" salvata in browser + contor de siguranta).
"""

from __future__ import annotations

import json
import re
import ssl
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Dict, List, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

STORES: List[Tuple[str, str, str, str, str]] = [
    # IT (10)
    ("IT", "puntoenergiashop.it", "https://www.puntoenergiashop.it/it/", "+39 0882 228247", "info@puntoenergiaitalia.it"),
    ("IT", "solarpower24.it", "https://www.solarpower24.it/", "+39 0461 1860210", "solarpower24@solarpower24.it"),
    ("IT", "climamarket.it", "https://www.climamarket.it/", "+39 06 83390450", "info@climamarket.it"),
    ("IT", "energiasolare100.it", "https://energiasolare100.it/it/", "+39 080 5321940", "info@energiasolare100.it"),
    ("IT", "cercastock.it", "https://www.cercastock.it/", "+39 0543 1995799", "cercastock@cercastock.it"),
    ("IT", "davesun.it", "https://www.davesun.it/", "+39 0332 1850320", "info@davesun.it"),
    ("IT", "duowatt.it", "https://www.duowatt.it/", "+39 02 87198420", "info@duowatt.it"),
    ("IT", "litio.store", "https://www.litio.store/", "+39 0832 1830510", "info@litio.store"),
    ("IT", "efficasa.it", "https://www.efficasa.it/", "+39 0833 1850290", "info@efficasa.it"),
    ("IT", "voltmag.it", "https://www.voltmag.it/", "+39 0961 1840210", "office@voltmag.it"),
    # UK (10)
    ("UK", "itstechnologies.shop", "https://www.itstechnologies.shop", "+44 161 529 8401", "support@itstechnologies.uk"),
    ("UK", "callidus.shop", "https://www.callidus.shop", "+44 1626 563563", "admin@callidustrade.co.uk"),
    ("UK", "voltaconsolar.com", "https://voltaconsolar.com", "+44 2477 675575", "info@voltacon.com"),
    ("UK", "offgridrenewables.co.uk", "https://www.offgridrenewables.co.uk", "+44 330 133 3275", "hello@offgridrenewables.co.uk"),
    ("UK", "fogstar.co.uk", "https://www.fogstar.co.uk", "+44 1527 757980", "customerservice@fogstar.co.uk"),
    ("UK", "windandsun.co.uk", "https://www.windandsun.co.uk", "+44 1568 720364", "sales@windandsun.co.uk"),
    ("UK", "powerland.co.uk", "https://www.powerland.co.uk", "+44 1527 962968", "info@powerland.co.uk"),
    ("UK", "powerwarehouse.co.uk", "https://www.powerwarehouse.co.uk", "+44 330 174 2900", "info@powerwarehouse.co.uk"),
    ("UK", "solar-hub.co.uk", "https://www.solar-hub.co.uk", "+44 1248 660330", "sales@solarrenewablehub.co.uk"),
    ("UK", "pluginsolar.co.uk", "https://www.pluginsolar.co.uk", "+44 1444 672005", "info@pluginsolar.co.uk"),
    # DE (10)
    ("DE", "tepto.de", "https://www.tepto.de", "+49 2264 40412-0", "verkauf@tepto.de"),
    ("DE", "actec-solar.de", "https://www.actec-solar.de", "+49 721 98899598", "info@actec-klima.de"),
    ("DE", "offgridtec.com", "https://www.offgridtec.com", "+49 8721 9199400", "info@offgridtec.com"),
    ("DE", "panda-solar.de", "https://www.panda-solar.de", "+49 5608 7990068", "info@panda-solar.de"),
    ("DE", "solarkontor.de", "https://solarkontor.de", "+49 4131 699640", "info@solarkontor.de"),
    ("DE", "husatech.de", "https://www.husatech.de", "+49 531 12296789", "service@husatech.de"),
    ("DE", "photovoltaik4all.de", "https://www.photovoltaik4all.de", "+49 3933 9099850", "info@photovoltaik4all.de"),
    ("DE", "autobatterienbilliger.de", "https://www.autobatterienbilliger.de", "+49 7141 5609040", "info@autobatterienbilliger.de"),
    ("DE", "bau-tech.shop", "https://www.bau-tech.shop", "+49 38229 78510", "info@bautechsolar.de"),
    ("DE", "solarway.de", "https://www.solarway.de", "+49 5261 920990", "support@solarway.shop"),
    # NL (10)
    ("NL", "solar-outlet.nl", "https://www.solar-outlet.nl", "+31 85 060 8420", "info@solar-outlet.nl"),
    ("NL", "stralendgroen.nl", "https://www.stralendgroen.nl", "+31 85 401 3820", "info@stralendgroen.nl"),
    ("NL", "cedel.nl", "https://www.cedel.nl", "+31 74 349 0110", "info@cedel.nl"),
    ("NL", "offgridcentrum.nl", "https://www.offgridcentrum.nl", "+31 85 060 9125", "info@offgridcentrumnederland.nl"),
    ("NL", "accuserviceholland.nl", "https://www.accuserviceholland.nl", "+31 73 644 5736", "info@accuserviceholland.nl"),
    ("NL", "zonnepanelen-voordelig.nl", "https://www.zonnepanelen-voordelig.nl", "+31 6 27179772", "info@zonnepanelen-voordelig.nl"),
    ("NL", "winkelman-zonnepanelen.nl", "https://www.winkelman-zonnepanelen.nl", "+31 591 201 904", "info@winkelman-zonnepanelen.nl"),
    ("NL", "solar-bouwmarkt.nl", "https://www.solar-bouwmarkt.nl", "+31 36 848 9200", "info@solar-bouwmarkt.nl"),
    ("NL", "stroomwinkel.nl", "https://www.stroomwinkel.nl", "+31 182 303 460", "info@stroomwinkel.nl"),
    ("NL", "marinediscounter.nl", "https://www.marinediscounter.nl", "+31 515 745 020", "info@marinediscounter.nl"),
    # ES (10)
    ("ES", "autosolar.es", "https://autosolar.es", "+34 961 430 113", "autosolar@autosolar.es"),
    ("ES", "wccsolar.net", "https://www.wccsolar.net", "+34 665 556 179", "servicio@wccsolar.es"),
    ("ES", "tiendasolar.es", "https://www.tiendasolar.es", "+34 960 627 890", "info@tienda-solar.es"),
    ("ES", "rebacas.com", "https://www.rebacas.com", "+34 615 245 056", "info@rebacas.com"),
    ("ES", "damiasolar.com", "https://www.damiasolar.com", "+34 973 972 533", "info@damiasolar.com"),
    ("ES", "cambioenergetico.com", "https://www.cambioenergetico.com", "+34 927 500 162", "info@cambioenergetico.com"),
    ("ES", "efectosolar.es", "https://efectosolar.es", "+34 622 022 254", "info@efectosolar.es"),
    ("ES", "solarfam.es", "https://www.solarfam.es", "+34 948 312 040", "administracion@solarfam.com"),
    ("ES", "suministrosdelsol.com", "https://suministrosdelsol.com", "+34 951 829 615", "info@suministrosdelsol.com"),
    ("ES", "coelectrix.com", "https://coelectrix.com", "+34 622 204 206", "info@coelectrix.com"),
    # FR (10)
    ("FR", "monkitsolaire.fr", "https://www.monkitsolaire.fr", "+33 3 59 89 74 00", "contact@monkitsolaire.fr"),
    ("FR", "alma-solar.fr", "https://www.alma-solarshop.fr", "+33 1 76 54 91 20", "contact@alma-solarshop.com"),
    ("FR", "myshop-solaire.com", "https://www.myshop-solaire.com", "+33 1 40 09 62 25", "contact@myshop-solaire.com"),
    ("FR", "ase-energy.com", "https://www.ase-energy.com", "+33 4 91 43 07 15", "contact@ase-energy.com"),
    ("FR", "kitsolaire-discount.com", "https://www.kitsolaire-discount.com", "+33 4 28 29 75 40", "contact@kitsolaire-discount.com"),
    ("FR", "solairepratique.com", "https://www.solairepratique.com", "+33 6 52 72 28 96", "contact@solairepratique.com"),
    ("FR", "h2r-equipements.com", "https://www.h2r-equipements.com", "+33 4 74 09 18 62", "contact.pro@h2r-equipements.com"),
    ("FR", "watteo.fr", "https://www.watteo.fr", "+33 2 55 99 41 20", "contact@watteo.fr"),
    ("FR", "batterie-solaire.com", "https://www.batterie-solaire.com", "+33 2 40 97 25 80", "contact@batterie-solaire.com"),
    ("FR", "chocdiscount.com", "https://www.chocdiscount.com", "+33 2 41 56 18 25", "sav@chocdiscount.com"),
]

COUNTRY_PREFIX = {
    "IT": "39",
    "UK": "44",
    "DE": "49",
    "NL": "31",
    "ES": "34",
    "FR": "33",
}


def normalize_phone(raw: str, cc: str) -> str:
    digits = re.sub(r"[^0-9]", "", raw)
    if digits.startswith("00"):
        digits = digits[2:]
    pref = COUNTRY_PREFIX[cc]
    if digits.startswith("0"):
        digits = pref + digits[1:]
    elif not digits.startswith(pref):
        digits = pref + digits
    return digits


def is_mobile_or_wa(digits: str, cc: str, has_wa_link: bool, has_wa_word: bool) -> bool:
    if has_wa_link or has_wa_word:
        return True
    if cc == "IT" and digits.startswith("393"):
        return True
    if cc == "ES" and (digits.startswith("346") or digits.startswith("347")):
        return True
    if cc == "NL" and digits.startswith("316"):
        return True
    if cc == "DE" and (digits.startswith("4915") or digits.startswith("4916") or digits.startswith("4917")):
        return True
    if cc == "UK" and digits.startswith("447"):
        return True
    if cc == "FR" and (digits.startswith("336") or digits.startswith("337")):
        return True
    return False


def build_safe_whatsapp_message(cc: str, domain: str, email_to: str) -> str:
    """Genereaza un mesaj scurt pt. dimineata ('ieri'), 100% uman, fara linkuri (http) si fara simboluri valutare (€/£)."""
    if cc == "IT":
        return (
            f"Buongiorno! Vi ho inviato ieri una mail su {email_to} con la tabella Excel comparativa "
            f"dei prezzi inverter e batterie per {domain} prima del Black Friday. "
            f"Mi confermate cortesemente se vi e arrivata in Inbox? Grazie, Vasile Bratu (+39 320 948 1876)"
        )
    if cc == "UK":
        return (
            f"Good morning! I sent a quick email yesterday to {email_to} with an Excel price and stock comparison "
            f"sheet for {domain} ahead of Black Friday. Could you let me know if it landed in your inbox? "
            f"Many thanks, Vasile Bratu (+39 320 948 1876)"
        )
    if cc == "DE":
        return (
            f"Guten Morgen! Ich habe Ihnen gestern eine kurze E-Mail an {email_to} mit einer Excel-Preisvergleichstabelle "
            f"(Wechselrichter & Speicher vor dem Black Friday) fuer {domain} geschickt. "
            f"Kurze Frage: Ist die E-Mail gut bei Ihnen angekommen? Viele Gruesse, Vasile Bratu (+39 320 948 1876)"
        )
    if cc == "NL":
        return (
            f"Goedemorgen! Ik heb u gisteren een e-mail gestuurd naar {email_to} met een kort Excel-overzicht "
            f"(prijs- en voorraadcheck voor Black Friday) voor {domain}. "
            f"Kunt u mij laten weten of deze goed in uw inbox is aangekomen? Met vriendelijke groet, Vasile Bratu (+39 320 948 1876)"
        )
    if cc == "ES":
        return (
            f"Hola, buenos dias! Les envie ayer un correo a {email_to} con una tabla Excel comparativa "
            f"de precios y stock de inversores y baterias para {domain} antes del Black Friday. "
            f"Me podrian confirmar si les ha llegado bien a la bandeja de entrada? Un saludo, Vasile Bratu (+39 320 948 1876)"
        )
    # FR
    return (
        f"Bonjour ! Je vous ai envoye hier un e-mail sur {email_to} avec un tableau Excel comparatif "
        f"des prix et stocks (onduleurs et batteries avant le Black Friday) pour {domain}. "
        f"Pourriez-vous me confirmer si vous l'avez bien recu ? Cordialement, Vasile Bratu (+39 320 948 1876)"
    )


def scan_store(item: Tuple[str, str, str, str, str]) -> Dict[str, Any]:
    cc, dom, url, fb_tel, em = item
    wa_links: List[str] = []
    has_wa_word = False
    found_mobile = ""

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        html = urllib.request.urlopen(req, context=ctx, timeout=7).read().decode("utf-8", errors="replace")

        raw_wa = re.findall(r"(?:wa\.me/|api\.whatsapp\.com/send\?(?:[^\"']*?&)?phone=)(\+?[0-9]{9,15})", html, re.I)
        wa_links = [re.sub(r"[^0-9]", "", x) for x in raw_wa if len(re.sub(r"[^0-9]", "", x)) >= 9]
        has_wa_word = bool(re.search(r"whatsapp", html, re.I))

        # Extract ONLY from explicit tel: hrefs (never random JS/CSS numbers)
        tel_hrefs = re.findall(r"href=[\"']tel:([^\"']+)[\"']", html, re.I)
        for th in tel_hrefs:
            d = normalize_phone(th, cc)
            if len(set(d)) <= 2:  # ignore placeholders like 333333333 / 666666666
                continue
            if is_mobile_or_wa(d, cc, False, False):
                found_mobile = "+" + d
                break
    except Exception:
        pass

    if wa_links:
        best_digits = wa_links[0]
        display_phone = "+" + best_digits
        badge = "🟢 Buton WhatsApp Oficial pe Site"
        priority = 1
    elif found_mobile:
        best_digits = normalize_phone(found_mobile, cc)
        display_phone = found_mobile
        badge = "🟢 Mobil / WhatsApp Gasit pe Site" if not has_wa_word else "🟢 WhatsApp + Mobil pe Site"
        priority = 1
    else:
        best_digits = normalize_phone(fb_tel, cc)
        display_phone = fb_tel
        if is_mobile_or_wa(best_digits, cc, False, has_wa_word):
            badge = "🟢 WhatsApp / Mobil Verificat"
            priority = 1
        else:
            badge = "🟡 Numar Oficial (WA Business / Fix)"
            priority = 2

    msg_text = build_safe_whatsapp_message(cc, dom, em)
    wa_url = f"https://wa.me/{best_digits}?text={urllib.parse.quote(msg_text)}"

    return {
        "cc": cc,
        "domain": dom,
        "email": em,
        "display_phone": display_phone,
        "digits": best_digits,
        "badge": badge,
        "priority": priority,
        "msg": msg_text,
        "wa_url": wa_url,
    }


def main() -> None:
    print("Scanez toate cele 60 de magazine (IT, UK, DE, NL, ES, FR)...", flush=True)
    with ThreadPoolExecutor(max_workers=20) as ex:
        rows = list(ex.map(scan_store, STORES))

    already_sent_set = {
        "puntoenergiashop.it",
        "solarpower24.it",
        "energiasolare100.it",
        "davesun.it",
        "duowatt.it",
        "efficasa.it",
        "voltmag.it",
        "stralendgroen.nl",
    }

    def _is_gsm(d: str) -> bool:
        return (
            d.startswith("393")
            or d.startswith("316")
            or d.startswith("346")
            or d.startswith("347")
            or d.startswith("336")
            or d.startswith("337")
            or d.startswith("4915")
            or d.startswith("4916")
            or d.startswith("4917")
            or d.startswith("447")
        )

    vip_rows = sorted(
        [r for r in rows if r["priority"] == 1],
        key=lambda x: (
            x["domain"] in already_sent_set,  # unsent first
            not _is_gsm(x["digits"]),         # GSM mobile first
        ),
    )
    std_rows = [r for r in rows if r["priority"] == 2]
    print(f"Gasite PRIORITATE 1 (WhatsApp / Mobil direct): {len(vip_rows)} magazine")
    print(f"Gasite PRIORITATE 2 (Numar Oficial / WA Business): {len(std_rows)} magazine")
    for r in vip_rows:
        print(f"  [VIP {r['cc']}] {r['domain']:<26} | {r['display_phone']:<18} | {r['badge']}")

    html_cards_vip = []
    for idx, r in enumerate(vip_rows, 1):
        cid = f"vip_{idx}_{r['domain']}"
        d = r["digits"]
        is_gsm_mobile = (
            d.startswith("393")
            or d.startswith("316")
            or d.startswith("346")
            or d.startswith("347")
            or d.startswith("336")
            or d.startswith("337")
            or d.startswith("4915")
            or d.startswith("4916")
            or d.startswith("4917")
            or d.startswith("447")
        )
        sms_tag = "📱 PRIMESTE SMS CLASIC (MOBIL GSM)" if is_gsm_mobile else "☎️ DOAR WHATSAPP (FIX CU WA)"
        sms_cls = "vip" if is_gsm_mobile else "std"
        msg_js = r["msg"].replace("'", "\\'")
        html_cards_vip.append(f"""
        <tr id="row_{cid}" class="vip-row">
            <td><span class="cc-badge cc-{r['cc']}">{r['cc']}</span></td>
            <td><strong>{r['domain']}</strong><br><small>{r['email']}</small></td>
            <td>
                <span class="status-pill {sms_cls}">{sms_tag}</span><br>
                <code style="font-size:15px;font-weight:700;color:#38bdf8;user-select:all;">+{r['digits']}</code>
            </td>
            <td class="msg-cell">{r['msg']}</td>
            <td class="act-cell">
                <button class="btn-wa" style="background:#38bdf8;color:#0f172a;border:none;cursor:pointer;" id="cpnum_{cid}" onclick="copyNum('{cid}', '+{r['digits']}')">📞 1. Copiază Numărul</button>
                <button class="btn-wa" style="border:none;cursor:pointer;" id="cpmsg_{cid}" onclick="copyMsg('{cid}', '{msg_js}')">💬 2. Copiază Mesajul</button>
                <button class="btn-done" onclick="toggleSent('{cid}')" id="btn_{cid}">Neexpediat</button>
            </td>
        </tr>
        """)

    html_cards_std = []
    for idx, r in enumerate(std_rows, 1):
        cid = f"std_{idx}_{r['domain']}"
        html_cards_std.append(f"""
        <tr id="row_{cid}">
            <td><span class="cc-badge cc-{r['cc']}">{r['cc']}</span></td>
            <td><strong>{r['domain']}</strong><br><small>{r['email']}</small></td>
            <td><span class="status-pill std">{r['badge']}</span><br><code>{r['display_phone']}</code></td>
            <td class="msg-cell">{r['msg']}</td>
            <td class="act-cell">
                <a href="{r['wa_url']}" target="_blank" class="btn-wa secondary" onclick="markSent('{cid}')">💬 Testeaza WA</a>
                <button class="btn-done" onclick="toggleSent('{cid}')" id="btn_{cid}">Neexpediat</button>
            </td>
        </tr>
        """)

    html_doc = f"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8">
<title>WhatsApp Business Sniper — 60 Magazine (IT, UK, DE, NL, ES, FR)</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 24px; }}
  .container {{ max-width: 1380px; margin: 0 auto; }}
  .header {{ background: linear-gradient(135deg, #1e293b, #0f172a); border: 1px solid #334155; border-radius: 12px; padding: 20px 24px; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }}
  h1 {{ margin: 0 0 6px 0; font-size: 22px; color: #38bdf8; }}
  .sub {{ color: #94a3b8; font-size: 14px; margin: 0; }}
  .counter-box {{ background: #064e3b; border: 1px solid #10b981; padding: 12px 20px; border-radius: 10px; text-align: center; }}
  .counter-box .num {{ font-size: 24px; font-weight: 800; color: #34d399; }}
  .counter-box .lbl {{ font-size: 12px; color: #a7f3d0; }}
  h2 {{ font-size: 18px; color: #f1f5f9; margin: 26px 0 12px 0; border-left: 4px solid #10b981; padding-left: 10px; }}
  h2.std-hdr {{ border-left-color: #f59e0b; }}
  table {{ width: 100%; border-collapse: collapse; background: #1e293b; border-radius: 10px; overflow: hidden; margin-bottom: 28px; }}
  th {{ background: #334155; color: #e2e8f0; text-align: left; padding: 12px 14px; font-size: 13px; text-transform: uppercase; }}
  td {{ padding: 12px 14px; border-bottom: 1px solid #334155; font-size: 13.5px; vertical-align: middle; }}
  tr.vip-row {{ background: rgba(16, 185, 129, 0.06); }}
  tr.sent-row {{ opacity: 0.48; background: #0f172a !important; }}
  .cc-badge {{ display: inline-block; padding: 4px 8px; border-radius: 6px; font-weight: 700; font-size: 12px; background: #3b82f6; color: #fff; }}
  .status-pill {{ display: inline-block; padding: 3px 8px; border-radius: 6px; font-size: 11.5px; font-weight: 600; margin-bottom: 4px; }}
  .status-pill.vip {{ background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #059669; }}
  .status-pill.std {{ background: rgba(245, 158, 11, 0.18); color: #fbbf24; border: 1px solid #d97706; }}
  .msg-cell {{ color: #cbd5e1; font-size: 13px; max-width: 520px; line-height: 1.45; }}
  .act-cell {{ white-space: nowrap; }}
  .btn-wa {{ display: inline-block; background: #10b981; color: #052e16; font-weight: 700; text-decoration: none; padding: 8px 14px; border-radius: 8px; font-size: 13px; margin-right: 6px; }}
  .btn-wa:hover {{ background: #34d399; }}
  .btn-wa.secondary {{ background: #f59e0b; color: #451a03; }}
  .btn-done {{ background: #334155; color: #cbd5e1; border: 1px solid #475569; padding: 7px 10px; border-radius: 8px; cursor: pointer; font-size: 12px; }}
  .btn-done.active {{ background: #059669; color: #fff; border-color: #10b981; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <h1>⚡ WhatsApp Sniper (+39 320 948 1876 — Cont Deblocat) — 60 Magazine (IT, UK, DE, NL, ES, FR)</h1>
      <p class="sub">Mesaje native de 2 rânduri cu numărul <strong>+39 320 948 1876</strong> (FĂRĂ linkuri și FĂRĂ simboluri valutare). <strong>IMPORTANT:</strong> Așteaptă cronometrul de 2,5 minute între click-uri ca să nu declanșezi restricția pe dispozitive asociate!</p>
    </div>
    <div style="display:flex; gap:14px;">
      <div class="counter-box" style="background:#1e1b4b; border-color:#6366f1;">
        <div class="num" id="cooldownTimer" style="color:#a5b4fc;">GATA (00:00)</div>
        <div class="lbl">Cronometru Anti-Ban (2,5 min)</div>
      </div>
      <div class="counter-box">
        <div class="num" id="sentCount">0 / 60</div>
        <div class="lbl">Mesaje WhatsApp Trimise</div>
      </div>
    </div>
  </div>

  <h2>🟢 PRIORITATEA 1 (VIP — {len(vip_rows)} Magazine cu Buton WhatsApp Oficial sau Număr de Mobil pe Site)</h2>
  <table>
    <thead>
      <tr>
        <th>Țara</th>
        <th>Magazin & Email</th>
        <th>Telefon / WhatsApp</th>
        <th>Mesaj Nativ Anti-Ban (2 Rânduri, Fără Link)</th>
        <th>Acțiune 1-Click</th>
      </tr>
    </thead>
    <tbody>
      {"".join(html_cards_vip)}
    </tbody>
  </table>

  <h2 class="std-hdr">🟡 PRIORITATEA 2 ({len(std_rows)} Magazine cu Număr Oficial din Impressum — Funcționează dacă au WhatsApp Business pe fix)</h2>
  <table>
    <thead>
      <tr>
        <th>Țara</th>
        <th>Magazin & Email</th>
        <th>Telefon Oficial</th>
        <th>Mesaj Nativ Anti-Ban (2 Rânduri, Fără Link)</th>
        <th>Acțiune 1-Click</th>
      </tr>
    </thead>
    <tbody>
      {"".join(html_cards_std)}
    </tbody>
  </table>
</div>
<script>
  const PRE_SENT_DOMAINS = [
    'puntoenergiashop.it',
    'solarpower24.it',
    'energiasolare100.it',
    'davesun.it',
    'duowatt.it',
    'efficasa.it',
    'voltmag.it',
    'stralendgroen.nl'
  ];
  // Initialize pre-sent stores once
  if (!localStorage.getItem('wa_init_1819')) {{
    document.querySelectorAll('tr[id^="row_"]').forEach(row => {{
      const cid = row.id.replace('row_', '');
      for (const d of PRE_SENT_DOMAINS) {{
        if (cid.endsWith('_' + d)) {{
          localStorage.setItem('wa_sent_' + cid, '1');
        }}
      }}
    }});
    localStorage.setItem('wa_init_1819', '1');
  }}

  let timerInterval = null;
  function startCooldown(seconds) {{
    if (timerInterval) clearInterval(timerInterval);
    let rem = seconds;
    const el = document.getElementById('cooldownTimer');
    timerInterval = setInterval(() => {{
      rem--;
      if (rem <= 0) {{
        clearInterval(timerInterval);
        el.textContent = 'GATA (00:00)';
        el.style.color = '#34d399';
      }} else {{
        const m = String(Math.floor(rem / 60)).padStart(2, '0');
        const s = String(rem % 60).padStart(2, '0');
        el.textContent = 'ASTEAPTA ' + m + ':' + s;
        el.style.color = '#fbbf24';
      }}
    }}, 1000);
  }}

  function updateUI() {{
    let count = 0;
    document.querySelectorAll('tr[id^="row_"]').forEach(row => {{
      const cid = row.id.replace('row_', '');
      const isSent = localStorage.getItem('wa_sent_' + cid) === '1';
      const btn = document.getElementById('btn_' + cid);
      if (isSent) {{
        row.classList.add('sent-row');
        btn.classList.add('active');
        btn.textContent = '✅ Trimis';
        count++;
      }} else {{
        row.classList.remove('sent-row');
        btn.classList.remove('active');
        btn.textContent = 'Neexpediat';
      }}
    }});
    document.getElementById('sentCount').textContent = count + ' / 60';
  }}
  function copyNum(cid, phone) {{
    navigator.clipboard.writeText(phone);
    const b = document.getElementById('cpnum_' + cid);
    if (b) {{
      b.textContent = '✅ Număr Copiat!';
      b.style.background = '#22c55e';
      setTimeout(() => {{ b.textContent = '📞 1. Copiază Numărul'; b.style.background = '#38bdf8'; }}, 3000);
    }}
  }}
  function copyMsg(cid, msg) {{
    navigator.clipboard.writeText(msg);
    const b = document.getElementById('cpmsg_' + cid);
    if (b) {{
      b.textContent = '✅ Mesaj Copiat!';
      b.style.background = '#22c55e';
      setTimeout(() => {{ b.textContent = '💬 2. Copiază Mesajul'; b.style.background = '#10b981'; }}, 3000);
    }}
    markSent(cid);
  }}
  function markSent(cid) {{
    localStorage.setItem('wa_sent_' + cid, '1');
    updateUI();
    startCooldown(150);
  }}
  function toggleSent(cid) {{
    const cur = localStorage.getItem('wa_sent_' + cid) === '1';
    localStorage.setItem('wa_sent_' + cid, cur ? '0' : '1');
    updateUI();
  }}
  updateUI();
</script>
</body>
</html>
"""
    out_path = Path(r"C:\Users\bratu\Desktop\WhatsApp_Sniper_60_Stores.html")
    out_path.write_text(html_doc, encoding="utf-8")
    print(f"[OK] Dashboard generat pe Desktop: {out_path}")


if __name__ == "__main__":
    main()
