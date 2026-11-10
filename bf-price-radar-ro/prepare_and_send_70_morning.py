#!/usr/bin/env python3
"""
prepare_and_send_70_morning.py
Pregateste la perfectiune (0 caractere AI, 0 markdown, 0 placeholder-uri, diacritice 100% naturale,
headere Excel native in toate cele 7 limbi) si trimite automat la ora matinala (09:00-10:30 local)
cele 70 de emailuri B2B personalizate (RO 10 + IT 10 + DE 10 + NL 10 + FR 10 + ES 10 + UK 10)
folosind alternanta inteligenta intre Zoho Mail (amendamax@vasiledev.com) si Gmail SMTP (amendamax@gmail.com)
cu failover automat si pauza sigura anti-spam.
"""

from __future__ import annotations

import argparse
import json
import re
import smtplib
import ssl
import sys
import time
from datetime import datetime, timedelta
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path
from typing import Any, Dict, List, Tuple

import openpyxl

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DESKTOP_DIR = Path(r"C:\Users\bratu\Desktop")

# SMTP Accounts (Alternating Round-Robin + Instant Failover)
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


def get_all_70_stores() -> List[Dict[str, Any]]:
    """Returneaza toate cele 70 de magazine ordonate pe fus orar matinal:
    1) RO (UTC+2: 08:30 CET = 09:30 RO)
    2) DE, NL, IT, FR, ES (UTC+1: 08:48 - 10:05 CET)
    3) UK (UTC+0: 10:06 - 10:22 CET = 09:06 - 09:22 UK)
    """
    stores: List[Dict[str, Any]] = []

    # 1. RO (10)
    ro_contacts = json.loads(
        (DESKTOP_DIR / "BF_Price_Radar_RO_Output" / "stores_contacts.json").read_text(encoding="utf-8")
    )
    for item in ro_contacts:
        dom = item["domain"]
        stores.append({
            "cc": "RO",
            "domain": dom,
            "email": item["email"],
            "name": item.get("store_name", dom),
            "src_txt": DESKTOP_DIR / "BF_Price_Radar_RO_Output" / dom / "mesaj_contact.txt",
            "ready_txt": DESKTOP_DIR / "BF_Price_Radar_RO_Output" / dom / "ready_email_29oct.txt",
            "xlsx": DESKTOP_DIR / "BF_Price_Radar_RO_Output" / dom / f"Teaser_BlackFriday_{dom}.xlsx",
        })

    # 2. DE (10)
    de_list = [
        ("tepto.de", "verkauf@tepto.de", "Tepto"),
        ("actec-solar.de", "info@actec-klima.de", "AC TEC Solar"),
        ("offgridtec.com", "info@offgridtec.com", "Offgridtec"),
        ("panda-solar.de", "info@panda-solar.de", "Panda Solar"),
        ("solarkontor.de", "info@solarkontor.de", "Solarkontor"),
        ("husatech.de", "service@husatech.de", "HUSATECH"),
        ("photovoltaik4all.de", "info@photovoltaik4all.de", "Photovoltaik4all"),
        ("autobatterienbilliger.de", "info@autobatterienbilliger.de", "batterium"),
        ("bau-tech.shop", "info@bautechsolar.de", "bau-tech Solarenergie"),
        ("solarway.de", "support@solarway.shop", "Solarway"),
    ]
    for dom, em, name in de_list:
        stores.append({
            "cc": "DE",
            "domain": dom,
            "email": em,
            "name": name,
            "src_txt": DESKTOP_DIR / "BF_Price_Radar_DE_Output" / dom / "outreach_message_DE.txt",
            "ready_txt": DESKTOP_DIR / "BF_Price_Radar_DE_Output" / dom / "ready_email_29oct.txt",
            "xlsx": DESKTOP_DIR / "BF_Price_Radar_DE_Output" / dom / f"Teaser_BlackFriday_{dom}.xlsx",
        })

    # 3. NL (10)
    nl_list = [
        ("solar-outlet.nl", "info@solar-outlet.nl", "Solar Outlet"),
        ("stralendgroen.nl", "info@stralendgroen.nl", "Stralend Groen"),
        ("cedel.nl", "info@cedel.nl", "Cedel"),
        ("offgridcentrum.nl", "info@offgridcentrumnederland.nl", "Offgrid Centrum"),
        ("accuserviceholland.nl", "info@accuserviceholland.nl", "Accu Service Holland"),
        ("zonnepanelen-voordelig.nl", "info@zonnepanelen-voordelig.nl", "Zonnepanelen Voordelig"),
        ("winkelman-zonnepanelen.nl", "info@winkelman-zonnepanelen.nl", "Winkelman Zonnepanelen"),
        ("solar-bouwmarkt.nl", "info@solar-bouwmarkt.nl", "Solar Bouwmarkt"),
        ("stroomwinkel.nl", "info@stroomwinkel.nl", "Stroomwinkel"),
        ("marinediscounter.nl", "info@marinediscounter.nl", "Marinediscounter"),
    ]
    for dom, em, name in nl_list:
        stores.append({
            "cc": "NL",
            "domain": dom,
            "email": em,
            "name": name,
            "src_txt": DESKTOP_DIR / "BF_Price_Radar_NL_Output" / dom / "outreach_message_NL.txt",
            "ready_txt": DESKTOP_DIR / "BF_Price_Radar_NL_Output" / dom / "ready_email_29oct.txt",
            "xlsx": DESKTOP_DIR / "BF_Price_Radar_NL_Output" / dom / f"Teaser_BlackFriday_{dom}.xlsx",
        })

    # 4. IT (10)
    it_list = [
        ("puntoenergiashop.it", "info@puntoenergiaitalia.it", "Punto Energia Italia"),
        ("solarpower24.it", "solarpower24@solarpower24.it", "SolarPower24"),
        ("climamarket.it", "info@climamarket.it", "Climamarket"),
        ("energiasolare100.it", "info@energiasolare100.it", "EnergiaSolare100"),
        ("cercastock.it", "cercastock@cercastock.it", "CercaStock"),
        ("davesun.it", "info@davesun.it", "Davesun"),
        ("duowatt.it", "info@duowatt.it", "Duowatt"),
        ("litio.store", "info@litio.store", "Litio Store"),
        ("efficasa.it", "info@efficasa.it", "Efficasa"),
        ("voltmag.it", "office@voltmag.it", "Voltmag"),
    ]
    for dom, em, name in it_list:
        stores.append({
            "cc": "IT",
            "domain": dom,
            "email": em,
            "name": name,
            "src_txt": DESKTOP_DIR / "BF_Price_Radar_IT_Output" / dom / "messaggio_contatto_IT.txt",
            "ready_txt": DESKTOP_DIR / "BF_Price_Radar_IT_Output" / dom / "ready_email_29oct.txt",
            "xlsx": DESKTOP_DIR / "BF_Price_Radar_IT_Output" / dom / f"Teaser_BlackFriday_{dom}.xlsx",
        })

    # 5. FR (10)
    fr_list = [
        ("monkitsolaire.fr", "contact@monkitsolaire.fr", "Mon Kit Solaire"),
        ("alma-solar.fr", "contact@alma-solarshop.com", "Alma Solar"),
        ("myshop-solaire.com", "contact@myshop-solaire.com", "MyShop Solaire"),
        ("ase-energy.com", "contact@ase-energy.com", "ASE Energy"),
        ("kitsolaire-discount.com", "contact@kitsolaire-discount.com", "Kit Solaire Discount"),
        ("solairepratique.com", "contact@solairepratique.com", "Solaire Pratique"),
        ("h2r-equipements.com", "contact.pro@h2r-equipements.com", "H2R Equipements"),
        ("watteo.fr", "contact@watteo.fr", "Watteo"),
        ("batterie-solaire.com", "contact@batterie-solaire.com", "Batterie Solaire"),
        ("chocdiscount.com", "sav@chocdiscount.com", "ChocDiscount"),
    ]
    for dom, em, name in fr_list:
        stores.append({
            "cc": "FR",
            "domain": dom,
            "email": em,
            "name": name,
            "src_txt": DESKTOP_DIR / "BF_Price_Radar_FR_Output" / dom / "outreach_message_FR.txt",
            "ready_txt": DESKTOP_DIR / "BF_Price_Radar_FR_Output" / dom / "ready_email_29oct.txt",
            "xlsx": DESKTOP_DIR / "BF_Price_Radar_FR_Output" / dom / f"Teaser_BlackFriday_{dom}.xlsx",
        })

    # 6. ES (10)
    es_list = [
        ("autosolar.es", "autosolar@autosolar.es", "AutoSolar"),
        ("wccsolar.net", "servicio@wccsolar.es", "WCCSolar"),
        ("tiendasolar.es", "info@tienda-solar.es", "Tienda Solar"),
        ("rebacas.com", "info@rebacas.com", "Rebacas"),
        ("damiasolar.com", "info@damiasolar.com", "Damia Solar"),
        ("cambioenergetico.com", "info@cambioenergetico.com", "Cambio Energetico"),
        ("efectosolar.es", "info@efectosolar.es", "Efecto Solar"),
        ("solarfam.es", "administracion@solarfam.com", "Solarfam"),
        ("suministrosdelsol.com", "info@suministrosdelsol.com", "Suministros del Sol"),
        ("coelectrix.com", "info@coelectrix.com", "Coelectrix"),
    ]
    for dom, em, name in es_list:
        stores.append({
            "cc": "ES",
            "domain": dom,
            "email": em,
            "name": name,
            "src_txt": DESKTOP_DIR / "BF_Price_Radar_ES_Output" / dom / "outreach_message_ES.txt",
            "ready_txt": DESKTOP_DIR / "BF_Price_Radar_ES_Output" / dom / "ready_email_29oct.txt",
            "xlsx": DESKTOP_DIR / "BF_Price_Radar_ES_Output" / dom / f"Teaser_BlackFriday_{dom}.xlsx",
        })

    # 7. UK (10)
    uk_list = [
        ("itstechnologies.shop", "support@itstechnologies.uk", "ITS Technologies"),
        ("callidus.shop", "admin@callidustrade.co.uk", "Callidus"),
        ("voltaconsolar.com", "info@voltacon.com", "Voltacon"),
        ("offgridrenewables.co.uk", "hello@offgridrenewables.co.uk", "Off Grid Renewables"),
        ("fogstar.co.uk", "customerservice@fogstar.co.uk", "Fogstar"),
        ("windandsun.co.uk", "sales@windandsun.co.uk", "Wind & Sun"),
        ("powerland.co.uk", "info@powerland.co.uk", "Powerland"),
        ("powerwarehouse.co.uk", "info@powerwarehouse.co.uk", "Power Warehouse"),
        ("solar-hub.co.uk", "sales@solarrenewablehub.co.uk", "Solar Hub"),
        ("pluginsolar.co.uk", "info@pluginsolar.co.uk", "Plug In Solar"),
    ]
    for dom, em, name in uk_list:
        stores.append({
            "cc": "UK",
            "domain": dom,
            "email": em,
            "name": name,
            "src_txt": DESKTOP_DIR / "BF_Price_Radar_UK_Output" / dom / "outreach_message_UK.txt",
            "ready_txt": DESKTOP_DIR / "BF_Price_Radar_UK_Output" / dom / "ready_email_29oct.txt",
            "xlsx": DESKTOP_DIR / "BF_Price_Radar_UK_Output" / dom / f"Teaser_BlackFriday_{dom}.xlsx",
        })

    return stores


def clean_xlsx_file(xlsx_path: Path, cc: str, domain: str) -> None:
    """Curata em-dash/en-dash din toate celulele Excel si localizeaza headerele NL/ES/FR."""
    wb = openpyxl.load_workbook(xlsx_path)
    for ws in wb.worksheets:
        if ws.max_row >= 1 and ws.max_column >= 7:
            c1 = str(ws.cell(1, 1).value or "")
            if c1 == "Official MPN / SKU" and cc == "NL":
                headers = [
                    "Artikelnummer (MPN)",
                    "Productnaam",
                    f"Jullie prijs op {domain} (EUR)",
                    "Laagste NL-concurrent (EUR & webshop)",
                    "Voorraadstatus concurrent",
                    "Marktplaats-referentie (Tweakers.net / Bol.com)",
                    "Prijsverschil (EUR / %)",
                ]
                for idx, h in enumerate(headers, 1):
                    ws.cell(1, idx).value = h
            elif c1 == "Official MPN / SKU" and cc == "ES":
                headers = [
                    "Referencia oficial (MPN)",
                    "Producto / Modelo",
                    f"Vuestro precio en {domain} (EUR)",
                    "Competidor ES más barato (EUR y tienda)",
                    "Estado de stock competidor",
                    "Referencia Marketplace (Idealo.es / ManoMano.es)",
                    "Diferencia de precio (EUR / %)",
                ]
                for idx, h in enumerate(headers, 1):
                    ws.cell(1, idx).value = h
            elif c1 == "Official MPN / SKU" and cc == "FR":
                headers = [
                    "Référence fabricant (MPN)",
                    "Modèle / Produit",
                    f"Votre prix sur {domain} (EUR)",
                    "Concurrent FR le moins cher (EUR & site)",
                    "État du stock concurrent",
                    "Référence Marketplace (Idealo.fr / ManoMano.fr)",
                    "Écart de prix (EUR / %)",
                ]
                for idx, h in enumerate(headers, 1):
                    ws.cell(1, idx).value = h

        for r in range(1, ws.max_row + 1):
            for c in range(1, ws.max_column + 1):
                val = ws.cell(r, c).value
                if isinstance(val, str):
                    cleaned = (
                        val.replace("\u2014", "-")
                        .replace("\u2013", "-")
                        .replace("\u00a0", " ")
                        .replace("\u202f", " ")
                    )
                    if cleaned != val:
                        ws.cell(r, c).value = cleaned
    wb.save(xlsx_path)


def format_it_numbers(text: str) -> str:
    """Transforma 2,097.49 EUR -> 2.097,49 EUR si +20.9% -> +20,9% in textul italian."""
    def _num_repl(m: re.Match) -> str:
        thousands = m.group(1)
        hundreds = m.group(2)
        decimals = m.group(3)
        return f"{thousands}.{hundreds},{decimals} EUR"

    text = re.sub(r"\b(\d{1,3}),(\d{3})\.(\d{2})\s*EUR\b", _num_repl, text)
    text = re.sub(r"\b(\d{1,3})\.(\d{2})\s*EUR\b", lambda m: f"{m.group(1)},{m.group(2)} EUR", text)
    text = re.sub(r"([+-]?\d+)\.(\d+)%", lambda m: f"{m.group(1)},{m.group(2)}%", text)
    return text


def build_clean_human_email(store: Dict[str, Any]) -> Tuple[str, str]:
    cc = store["cc"]
    dom = store["domain"]
    raw = store["src_txt"].read_text(encoding="utf-8")

    m_subj = re.search(r"^(?:Subiect|Oggetto|Subject|Betreff|Onderwerp|Asunto|Objet):\s*(.+)$", raw, flags=re.M)
    if not m_subj:
        raise ValueError(f"Subject missing in {store['src_txt']}")
    subj = m_subj.group(1).strip()

    after = raw[m_subj.end():]
    body = after.split("================================================================================")[0]
    body = body.split("--------------------------------------------------------------------------------")[0].strip()

    if cc == "RO":
        subj = subj.replace("(date extrase azi dimineață)", "- verificare prețuri și stocuri Black Friday")
        body = body.replace("Salut,", "Bună dimineața,")
        body = body.replace("În schimb — o veste bună pentru marja voastră — la ", "În schimb, o veste bună pentru marja voastră: la ")
        body = body.replace("extrase acum două ore", "extrase direct din piață")
        body = body.replace("[Telefon / WhatsApp]", "Tel / WhatsApp: +39 320 948 1876\nEmail: amendamax@vasiledev.com")
        body = body.replace("– 150 €", "- 150 EUR")
        body = body.replace("– 450 €", "- 450 EUR")
        body = body.replace("150 €", "150 EUR").replace("450 €", "450 EUR")

    elif cc == "IT":
        body = body.replace("+39 353 486 5048 / +39 320 948 1876", "+39 320 948 1876")
        body = re.sub(r"\be'", "è", body)
        body = body.replace("piu'", "più").replace("gia'", "già")
        body = body.replace("OPPORTUNITA DI MARGINE SU", "Opportunità di margine su")
        body = format_it_numbers(body)
        body = body.replace("\nin vista della campagna", "\nIn vista della campagna")
        # Insert natural 1-line morning note right after greeting line
        lines = body.splitlines()
        if lines and lines[0].startswith("Buongiorno"):
            note = (
                f"\nvi invio un breve riscontro mattutino nel caso il messaggio di ieri per {dom} "
                f"fosse finito nello spam a causa dell'allegato Excel, lasciandovi qui sotto la sintesi aggiornata."
            )
            lines.insert(1, note)
            body = "\n".join(lines)

    elif cc == "DE":
        body = body.replace("\nvor dem Start der Black-Friday", "\nVor dem Start der Black-Friday")
        lines = body.splitlines()
        if lines and lines[0].startswith("Guten Tag"):
            lines[0] = lines[0].replace("Guten Tag", "Guten Morgen", 1)
            note = (
                f"\nich melde mich heute Morgen noch einmal kurz zu meiner gestrigen Auswertung für {dom}, "
                f"falls die erste E-Mail wegen des Excel-Anhangs im Spam-Filter hängengeblieben ist."
            )
            lines.insert(1, note)
            body = "\n".join(lines)

    elif cc == "NL":
        body = body.replace("in Lightspeed / Custom", "in Lightspeed")
        lines = body.splitlines()
        if lines and lines[0].startswith("Beste"):
            lines[0] = lines[0].replace("Beste ", "Goedemorgen ", 1)
            note = (
                f"\nIk stuur deze ochtend nog even een korte opvolging voor {dom}, "
                f"voor het geval mijn e-mail van gisteren door de Excel-bijlage in jullie spamfolder is beland."
            )
            lines.insert(1, note)
            body = "\n".join(lines)

    elif cc == "FR":
        body = body.replace("dans Custom / PrestaShop", "dans PrestaShop")
        lines = body.splitlines()
        if lines and lines[0].startswith("Bonjour"):
            note = (
                f"\nJe me permets un court message ce matin concernant {dom}, "
                f"au cas où mon envoi d'hier aurait été retenu par votre filtre anti-spam à cause du fichier Excel joint."
            )
            lines.insert(1, note)
            body = "\n".join(lines)

    elif cc == "ES":
        body = body.replace("en Custom E-Commerce", "en vuestro catálogo online")
        lines = body.splitlines()
        if lines and lines[0].startswith("Hola"):
            lines[0] = lines[0].replace("Hola ", "Buenos días ", 1)
            note = (
                f"\nOs escribo brevemente esta mañana respecto a {dom}, "
                f"por si mi correo de ayer se filtró a la carpeta de spam al llevar la tabla Excel adjunta."
            )
            lines.insert(1, note)
            body = "\n".join(lines)

    elif cc == "UK":
        lines = body.splitlines()
        if lines and lines[0].startswith("Hi "):
            lines[0] = lines[0].replace("Hi ", "Good morning ", 1)
            note = (
                f"\nJust following up briefly this morning on the price and stock sheet for {dom}, "
                f"in case yesterday's email got caught in a spam filter due to the Excel attachment."
            )
            lines.insert(1, note)
            body = "\n".join(lines)

    # Global anti-AI / anti-markdown sanitation
    for target in ["subj", "body"]:
        val = subj if target == "subj" else body
        val = (
            val.replace("**", "")
            .replace("*", "")
            .replace("`", "")
            .replace("\u2014", "-")
            .replace("\u2013", "-")
            .replace("\u201c", '"')
            .replace("\u201d", '"')
            .replace("\u2018", "'")
            .replace("\u2019", "'")
            .replace("\u201e", '"')
            .replace("\u00ab", '"')
            .replace("\u00bb", '"')
            .replace("\u2026", "...")
            .replace("\u00a0", " ")
            .replace("\u202f", " ")
        )
        # Collapse 3+ blank lines to max 2
        val = re.sub(r"\n{3,}", "\n\n", val).strip()
        if target == "subj":
            subj = val
        else:
            body = val

    return subj, body


def validate_zero_defects(store: Dict[str, Any], subj: str, body: str) -> None:
    full = subj + "\n" + body
    forbidden_regexes = [
        r"\[", r"\]", r"\{", r"\}",
        r"\*", r"`",
        r"\u2014", r"\u2013", r"\u201c", r"\u201d", r"\u2018", r"\u2019", r"\u2026",
        r"Custom E-Commerce", r"Lightspeed / Custom", r"Custom /",
        r"353 486 5048", r"erwan@solairepascher",
        r"\be'", r"piu'", r"gia'", r"OPPORTUNITA\b",
        r"TODO", r"TBD", r"undefined", r"NaN",
    ]
    for pat in forbidden_regexes:
        if re.search(pat, full):
            raise AssertionError(f"Forbidden pattern '{pat}' found in {store['cc']} / {store['domain']}")
    if "+39 320 948 1876" not in body:
        raise AssertionError(f"Missing verified WhatsApp number in {store['domain']}")
    if "amendamax@vasiledev.com" not in body:
        raise AssertionError(f"Missing verified email in {store['domain']}")
    if store["domain"] not in full:
        raise AssertionError(f"Missing store domain {store['domain']} in body")
    if not store["xlsx"].exists() or store["xlsx"].stat().st_size < 2500:
        raise AssertionError(f"Invalid Excel attachment for {store['domain']}")


def prepare_all() -> List[Dict[str, Any]]:
    stores = get_all_70_stores()
    print(f"Pregatesc si validez la sange toate cele {len(stores)} magazine + 70 fisiere Excel...", flush=True)
    for idx, st in enumerate(stores, 1):
        clean_xlsx_file(st["xlsx"], st["cc"], st["domain"])
        subj, body = build_clean_human_email(st)
        validate_zero_defects(st, subj, body)
        st["subject"] = subj
        st["body"] = body
        st["ready_txt"].write_text(
            f"TO: {st['email']}\nSUBJECT: {subj}\nATTACHMENT: {st['xlsx'].name}\n"
            f"{'=' * 76}\n{body}\n",
            encoding="utf-8",
        )
    print(f"[VALIDARE 100% TRECUTA] 70/70 emailuri + 70/70 fisiere Excel au ZERO caractere AI, ZERO markdown, ZERO erori!", flush=True)
    return stores


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
    with smtplib.SMTP_SSL(cfg["host"], cfg["port"], context=ctx, timeout=35) as server:
        server.login(cfg["user"], cfg["pass"])
        server.send_message(msg)


def dispatch_at_morning_schedule(start_time_str: str, pause_sec: int) -> None:
    stores = prepare_all()
    log_path = DESKTOP_DIR / "Morning_70_Campaign_Log_2026-10-29.json"

    # Wait until target start time (e.g. 08:30 CET = 09:30 RO, finishing UK around 10:25 CET = 09:25 UK)
    now = datetime.now()
    hh, mm = [int(x) for x in start_time_str.split(":")]
    target_dt = now.replace(hour=hh, minute=mm, second=0, microsecond=0)
    if target_dt > now:
        wait_s = int((target_dt - now).total_seconds())
        print(
            f"[PROGRAMAT] Ora curenta: {now.strftime('%H:%M:%S')} | Start automat la {target_dt.strftime('%H:%M:%S')} "
            f"(peste {wait_s // 60} min {wait_s % 60} sec)...",
            flush=True,
        )
        while datetime.now() < target_dt:
            rem = int((target_dt - datetime.now()).total_seconds())
            if rem <= 0:
                break
            time.sleep(min(30, rem))

    print("=" * 94)
    print(f"[START LIVRARE MATINALA] 70 Magazine B2B (RO -> DE -> NL -> IT -> FR -> ES -> UK) | Pauza: {pause_sec}s")
    print("=" * 94, flush=True)

    sent_records: List[Dict[str, Any]] = []
    zoho_healthy = True

    for idx, st in enumerate(stores, 1):
        # Round-robin: odd -> Zoho (if healthy), even -> Gmail; automatic failover to the other server on any error
        primary = ZOHO_CFG if (idx % 2 == 1 and zoho_healthy) else GMAIL_CFG
        fallback = GMAIL_CFG if primary["name"] == "ZOHO" else ZOHO_CFG

        used_server = primary["name"]
        status = "SENT_OK"
        try:
            send_single_email(primary, st["email"], st["subject"], st["body"], st["xlsx"])
        except Exception as e1:
            print(f"  [WARN] {primary['name']} a refuzat la #{idx} ({e1}) -> Failover instant pe {fallback['name']}...", flush=True)
            if primary["name"] == "ZOHO":
                zoho_healthy = False
            try:
                send_single_email(fallback, st["email"], st["subject"], st["body"], st["xlsx"])
                used_server = f"{fallback['name']}_FAILOVER"
            except Exception as e2:
                status = f"ERROR: {e2}"

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(
            f"[{idx:02d}/70] [{st['cc']}] [{status}] [{used_server:<14}] [{ts}] {st['domain']:<26} -> {st['email']}",
            flush=True,
        )
        sent_records.append({
            "index": idx,
            "country": st["cc"],
            "domain": st["domain"],
            "recipient": st["email"],
            "subject": st["subject"],
            "attachment": st["xlsx"].name,
            "smtp_used": used_server,
            "status": status,
            "timestamp": ts,
        })
        log_path.write_text(json.dumps(sent_records, indent=2, ensure_ascii=False), encoding="utf-8")

        if idx < len(stores):
            time.sleep(pause_sec)

    ok_cnt = sum(1 for r in sent_records if r["status"] == "SENT_OK")
    print("=" * 94)
    print(f"[CAMPANIE FINALIZATA] Livrate cu succes: {ok_cnt} / {len(stores)} | Log: {log_path}")
    print("=" * 94, flush=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--print-samples", action="store_true")
    ap.add_argument("--send", action="store_true")
    ap.add_argument("--start-at", default="08:35", help="HH:MM local CET start time (08:35 CET = 09:35 RO)")
    ap.add_argument("--pause", type=int, default=95, help="Seconds between emails (95s total = 190s per SMTP server)")
    args = ap.parse_args()

    if args.prepare_only or args.print_samples:
        stores = prepare_all()
        if args.print_samples:
            seen_cc = set()
            for st in stores:
                if st["cc"] not in seen_cc:
                    seen_cc.add(st["cc"])
                    print(f"\n{'#' * 80}\nSAMPLE [{st['cc']}] {st['domain']} -> {st['email']}\nSUBJECT: {st['subject']}\n{'-' * 80}\n{st['body']}\n")
    elif args.send:
        dispatch_at_morning_schedule(args.start_at, args.pause)


if __name__ == "__main__":
    main()
