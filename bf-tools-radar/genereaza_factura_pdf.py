#!/usr/bin/env python3
"""
genereaza_factura_pdf.py
Generator instantaneu (B2B) de Facturi Proforme / Commercial Invoices in format PDF vectorial (A4),
conform legislatiei fiscale din Italia (Regime Forfettario - Legge n. 190/2014 & Reverse Charge B2B),
cu metoda de plata PAYPAL BUSINESS si suport complet pentru toate cele 7 tari (RO, IT, UK, DE, NL, ES, FR).

Exemple de rulare rapida (preturi setate automat pe tara: RO 150/450 EUR | DE,IT,NL,FR,ES 350/850 EUR | UK 295/690 GBP):
  python genereaza_factura_pdf.py --client masif.ro --optiune 1
  python genereaza_factura_pdf.py --client masterfer.it --pachet 350
  python genereaza_factura_pdf.py --client gotools.de --pachet 350
  python genereaza_factura_pdf.py --client gereedschapcentrum.nl --pachet 350
  python genereaza_factura_pdf.py --client ferreteria.es --pachet 850
  python genereaza_factura_pdf.py --client sobrico.com --pachet 850
  python genereaza_factura_pdf.py --client nutsandbolts.co.uk --pachet 295 --currency GBP
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ==============================================================================
# 1. DATE FURNIZOR / TITOLARE & PAYPAL BUSINESS + GRILE OFICIALE PRETURI B2B
# ==============================================================================
TITOLARE_NOME = "Vasile Bratu - Python Automation & Data Intelligence"
TITOLARE_INDIRIZZO = "Garessio (CN), CAP 12075, Piemonte, Italia"
PARTITA_IVA = "IT04226190041"
CODICE_FISCALE = "BRTVSL79R29Z129Y"
PAYPAL_BUSINESS_EMAIL = "amendamax@gmail.com"
PAYPAL_MERCHANT_NAME = "Vasile Bratu | B2B Price Intelligence (PayPal Business)"
CONTATTO_EMAIL = "amendamax@vasiledev.com"
CONTATTO_TEL = "+39 320 948 1876"

COUNTRY_PRICING_TIERS: Dict[str, Dict[str, Any]] = {
    "RO": {"opt1": 150.0, "opt2": 450.0, "currency": "EUR"},
    "IT": {"opt1": 350.0, "opt2": 850.0, "currency": "EUR"},
    "DE": {"opt1": 350.0, "opt2": 850.0, "currency": "EUR"},
    "AT": {"opt1": 350.0, "opt2": 850.0, "currency": "EUR"},
    "NL": {"opt1": 350.0, "opt2": 850.0, "currency": "EUR"},
    "BE": {"opt1": 350.0, "opt2": 850.0, "currency": "EUR"},
    "FR": {"opt1": 350.0, "opt2": 850.0, "currency": "EUR"},
    "ES": {"opt1": 350.0, "opt2": 850.0, "currency": "EUR"},
    "UK": {"opt1": 295.0, "opt2": 690.0, "currency": "GBP"},
}

# ==============================================================================
# 2. REGISTRU PRE-ÎNCĂRCAT DE CLIENȚI B2B (RO, IT, UK, DE, NL, ES, FR)
# ==============================================================================
CLIENT_REGISTRY: Dict[str, Dict[str, str]] = {
    # --- ROMANIA (RO) ---
    "e-acumulatori.ro": {
        "country": "RO",
        "company_name": "P PLUS 2002 S.R.L.",
        "vat_id": "RO14560121",
        "reg_com": "J40/2719/2002",
        "address": "Bucuresti, Romania",
        "email": "office@e-acumulatori.ro",
        "phone": "0734 523 766",
        "platform": "Gomag",
    },
    "esolar.ro": {
        "country": "RO",
        "company_name": "SC AMUR SOLAR ENERGY S.R.L.",
        "vat_id": "RO33108859",
        "reg_com": "J22/1895/2012",
        "address": "Iasi, Romania",
        "email": "info@esolar.ro",
        "phone": "0253 943 101",
        "platform": "CS-Cart",
    },
    "solargreen.ro": {
        "country": "RO",
        "company_name": "SOLAR GREEN ENGINEERING S.R.L.",
        "vat_id": "RO45048041",
        "reg_com": "J22/3455/2021",
        "address": "Iasi, Romania",
        "email": "comenzi@solargreen.ro",
        "phone": "0749 124 855",
        "platform": "WooCommerce",
    },
    "genway.ro": {
        "country": "RO",
        "company_name": "S.C. ELECTRO-SERVICE DISTRIBUTIE S.R.L.",
        "vat_id": "RO21241885",
        "reg_com": "J40/4862/2015",
        "address": "Bucuresti, Romania",
        "email": "office@genway.ro",
        "phone": "0350 733 035",
        "platform": "WooCommerce",
    },
    "ecosolaris.ro": {
        "country": "RO",
        "company_name": "ECOSOLARIS S.R.L.",
        "vat_id": "RO31489210",
        "reg_com": "J40/4120/2013",
        "address": "Bucuresti, Romania",
        "email": "oferta@ecosolaris.ro",
        "phone": "0745 082 110",
        "platform": "WooCommerce",
    },
    "solartech.ro": {
        "country": "RO",
        "company_name": "TRACK WEBSERVICE SOFT S.R.L.",
        "vat_id": "RO35568098",
        "reg_com": "J29/214/2016",
        "address": "Ploiesti, Prahova, Romania",
        "email": "contact@solartech.ro",
        "phone": "0799 889 266",
        "platform": "WooCommerce",
    },
    "voltexpert.ro": {
        "country": "RO",
        "company_name": "ISR BACAU S.R.L.",
        "vat_id": "RO44855086",
        "reg_com": "J40/9120/2018",
        "address": "Bucuresti / Bacau, Romania",
        "email": "office@voltexpert.ro",
        "phone": "0722 390 410",
        "platform": "WooCommerce",
    },
    "novasol.ro": {
        "country": "RO",
        "company_name": "DOMUS TRAVEL S.R.L.",
        "vat_id": "RO52527543",
        "reg_com": "J12/4190/2021",
        "address": "Cluj-Napoca, Romania",
        "email": "energiesolara@novasol.ro",
        "phone": "0740 891 200",
        "platform": "WooCommerce",
    },
    "solarenergysighet.ro": {
        "country": "RO",
        "company_name": "SOLAR ENERGY SIGHET S.R.L.",
        "vat_id": "RO45773626",
        "reg_com": "J24/1420/2022",
        "address": "Sighetu Marmatiei, Maramures, Romania",
        "email": "bb.constructsrl@gmail.com",
        "phone": "0742 910 330",
        "platform": "WooCommerce",
    },
    "fotovoltaice.ro": {
        "country": "RO",
        "company_name": "SECURISTIKA S.R.L.",
        "vat_id": "RO33108921",
        "reg_com": "J35/1105/2014",
        "address": "Timisoara, Romania",
        "email": "info@fotovoltaice.ro",
        "phone": "0758 100 900",
        "platform": "CS-Cart",
    },
    # --- ITALIA (IT) ---
    "puntoenergiashop.it": {
        "country": "IT",
        "company_name": "PUNTOENERGIA ITALIA S.R.L.",
        "vat_id": "IT03805690710",
        "reg_com": "REA FG-274510",
        "address": "Via T. Tardio SNC, 71016 San Severo (FG), Italia",
        "email": "info@puntoenergiaitalia.it",
        "phone": "+39 0882 228247",
        "platform": "PrestaShop",
    },
    "solarpower24.it": {
        "country": "IT",
        "company_name": "SOLARPOWER24 S.R.L.",
        "vat_id": "IT02648190224",
        "reg_com": "REA TN-241090",
        "address": "Trento (TN) / Verona, Italia",
        "email": "solarpower24@solarpower24.it",
        "phone": "+39 0461 1860210",
        "platform": "WooCommerce",
    },
    "climamarket.it": {
        "country": "IT",
        "company_name": "CLIMAMARKET S.R.L.",
        "vat_id": "IT13489211005",
        "reg_com": "REA RM-1451290",
        "address": "Roma (RM), Lazio, Italia",
        "email": "info@climamarket.it",
        "phone": "+39 06 83390450",
        "platform": "Shopify",
    },
    "energiasolare100.it": {
        "country": "IT",
        "company_name": "DICIOLLA S.R.L. (EnergiaSolare100)",
        "vat_id": "IT07827270724",
        "reg_com": "REA BA-584210",
        "address": "Bari (BA), Puglia, Italia",
        "email": "info@energiasolare100.it",
        "phone": "+39 080 5321940",
        "platform": "Magento",
    },
    "cercastock.it": {
        "country": "IT",
        "company_name": "BARBA S.R.L. (CercaStock)",
        "vat_id": "IT04490370400",
        "reg_com": "REA FC-415210",
        "address": "Viale Roma 174, 47122 Forli (FC), Italia",
        "email": "cercastock@cercastock.it",
        "phone": "+39 0543 1995799",
        "platform": "PrestaShop",
    },
    "davesun.it": {
        "country": "IT",
        "company_name": "DAVESUN S.R.L.",
        "vat_id": "IT03981990124",
        "reg_com": "REA VA-392815",
        "address": "Varese (VA), Lombardia, Italia",
        "email": "info@davesun.it",
        "phone": "+39 0332 1850320",
        "platform": "WooCommerce",
    },
    "duowatt.it": {
        "country": "IT",
        "company_name": "DUOWATT S.R.L.",
        "vat_id": "IT12674150961",
        "reg_com": "REA MI-2677120",
        "address": "Milano (MI), Lombardia, Italia",
        "email": "info@duowatt.it",
        "phone": "+39 02 87198420",
        "platform": "WooCommerce",
    },
    "litio.store": {
        "country": "IT",
        "company_name": "LITIO STORE ITALIA S.R.L.",
        "vat_id": "IT04921840752",
        "reg_com": "REA LE-328140",
        "address": "Lecce (LE) / Milano, Italia",
        "email": "info@litio.store",
        "phone": "+39 0832 1830510",
        "platform": "Shopify",
    },
    "efficasa.it": {
        "country": "IT",
        "company_name": "EFFICASA S.R.L.",
        "vat_id": "IT04712330754",
        "reg_com": "REA LE-314209",
        "address": "Lecce (LE), Puglia, Italia",
        "email": "info@efficasa.it",
        "phone": "+39 0833 1850290",
        "platform": "PrestaShop",
    },
    "voltmag.it": {
        "country": "IT",
        "company_name": "VOLTMAG DISTRIBUZIONE S.R.L.",
        "vat_id": "IT03894120791",
        "reg_com": "REA CZ-219044",
        "address": "Catanzaro (CZ), Calabria, Italia",
        "email": "office@voltmag.it",
        "phone": "+39 0961 1840210",
        "platform": "PrestaShop",
    },
    # --- UK ---
    "fogstar.co.uk": {
        "country": "UK",
        "company_name": "FOGSTAR LTD",
        "vat_id": "GB256104900",
        "reg_com": "Companies House 10490056",
        "address": "Bromsgrove, Worcestershire, United Kingdom",
        "email": "customerservice@fogstar.co.uk",
        "phone": "+44 1527 757980",
        "platform": "Shopify",
    },
    "itstechnologies.shop": {
        "country": "UK",
        "company_name": "ITS TECHNOLOGIES LTD",
        "vat_id": "GB189089615",
        "reg_com": "Companies House 08961559",
        "address": "Manchester / Cheshire, United Kingdom",
        "email": "support@itstechnologies.uk",
        "phone": "+44 161 529 8401",
        "platform": "Shopify",
    },
    "ukplanettools.co.uk": {
        "country": "UK",
        "company_name": "UK PLANET TOOLS LTD",
        "vat_id": "GB294819210",
        "reg_com": "Company No. 11048920",
        "address": "Unit 9, Holdom Avenue, Milton Keynes, MK1 1QU, UK",
        "email": "support@ukplanettools.co.uk",
        "phone": "+44 20 3397 2367",
        "platform": "Magento 2",
        "niche": "tools",
    },
    # --- GERMANY (DE) ---
    "tepto.de": {
        "country": "DE",
        "company_name": "TEPTO GMBH",
        "vat_id": "DE354113105",
        "reg_com": "Amtsgericht Koeln, HRB 113105",
        "address": "Zum Schlahn 28, 51709 Marienheide, Deutschland",
        "email": "verkauf@tepto.de",
        "phone": "+49 2264 40412-0",
        "platform": "Shopware 6",
    },
    "actec-solar.de": {
        "country": "DE",
        "company_name": "AC TEC GMBH",
        "vat_id": "DE326819402",
        "reg_com": "Amtsgericht Mannheim, HRB 733335",
        "address": "Wikingerstr. 10, 76189 Karlsruhe, Deutschland",
        "email": "info@actec-klima.de",
        "phone": "+49 721 98899598",
        "platform": "Shopware 6",
    },
    "offgridtec.com": {
        "country": "DE",
        "company_name": "OFFGRIDTEC AG",
        "vat_id": "DE277456819",
        "reg_com": "Amtsgericht Landshut, HRB 14946",
        "address": "Im Gewerbepark 11, 84307 Eggenfelden, Deutschland",
        "email": "info@offgridtec.com",
        "phone": "+49 8721 9199400",
        "platform": "Shopware 6",
    },
    "panda-solar.de": {
        "country": "DE",
        "company_name": "PANDA SOLAR DEUTSCHLAND",
        "vat_id": "DE - B2B USt-IdNr.",
        "reg_com": "Handelsregister Kassel / Soehrewald",
        "address": "Tiefenrod 16, 34320 Soehrewald, Deutschland",
        "email": "info@panda-solar.de",
        "phone": "+49 5608 7990068",
        "platform": "Shopware 6",
    },
    "solarkontor.de": {
        "country": "DE",
        "company_name": "WATTSTUNDE GMBH (SOLARKONTOR)",
        "vat_id": "DE293847120",
        "reg_com": "Amtsgericht Lueneburg, HRB 204772",
        "address": "Bessemerstr. 3, 21339 Lueneburg, Deutschland",
        "email": "info@solarkontor.de",
        "phone": "+49 4131 699640",
        "platform": "Shopify",
    },
    "husatech.de": {
        "country": "DE",
        "company_name": "HUSATECH GMBH",
        "vat_id": "DE358912405",
        "reg_com": "Amtsgericht Braunschweig, HRB 210766",
        "address": "Boecklerstr. 30, 38102 Braunschweig, Deutschland",
        "email": "service@husatech.de",
        "phone": "+49 531 12296789",
        "platform": "JTL-Shop",
    },
    "photovoltaik4all.de": {
        "country": "DE",
        "company_name": "SEC SOLARENERGYCONSULT GMBH",
        "vat_id": "DE299104512",
        "reg_com": "Amtsgericht Stendal, HRB 21490",
        "address": "Tangermuende / Genthin, Deutschland",
        "email": "info@photovoltaik4all.de",
        "phone": "+49 3933 9099850",
        "platform": "Shopware 6",
    },
    "autobatterienbilliger.de": {
        "country": "DE",
        "company_name": "BATTERIUM GMBH",
        "vat_id": "DE276532910",
        "reg_com": "Amtsgericht Stuttgart, HRB 736368",
        "address": "Frankfurter Str. 8, 71732 Tamm, Deutschland",
        "email": "info@autobatterienbilliger.de",
        "phone": "+49 7141 5609040",
        "platform": "JTL-Shop",
    },
    "bau-tech.shop": {
        "country": "DE",
        "company_name": "BAU-TECH SOLARENERGIE GMBH",
        "vat_id": "DE298201270",
        "reg_com": "Amtsgericht Stralsund, HRB 20127",
        "address": "Tribseeser Str. 6, 18334 Bad Suelze, Deutschland",
        "email": "info@bautechsolar.de",
        "phone": "+49 38229 78510",
        "platform": "Shopware 6",
    },
    "solarway.de": {
        "country": "DE",
        "company_name": "SOLARWAY GMBH",
        "vat_id": "DE321904811",
        "reg_com": "Amtsgericht Lemgo, HRB 11221",
        "address": "An der Bega 14, 32657 Lemgo, Deutschland",
        "email": "support@solarway.shop",
        "phone": "+49 5261 920990",
        "platform": "Shopify",
    },
    # --- NETHERLANDS (NL), SPAIN (ES), FRANCE (FR) ---
    "solar-outlet.nl": {
        "country": "NL",
        "company_name": "SOLAR OUTLET B.V.",
        "vat_id": "NL858078412B01",
        "reg_com": "KvK 69952337",
        "address": "Nederland",
        "email": "info@solar-outlet.nl",
        "phone": "+31 85 060 8420",
        "platform": "Lightspeed",
    },
    "autosolar.es": {
        "country": "ES",
        "company_name": "AUTOSOLAR ENERGY SOLUTIONS S.L.U.",
        "vat_id": "ESB98662224",
        "reg_com": "CIF B98662224",
        "address": "Valencia, Espana",
        "email": "autosolar@autosolar.es",
        "phone": "+34 961 430 113",
        "platform": "E-Commerce",
    },
    "monkitsolaire.fr": {
        "country": "FR",
        "company_name": "SAS MON KIT SOLAIRE",
        "vat_id": "FR42798958518",
        "reg_com": "SIRET 798 958 518 00028",
        "address": "Lille / Hauts-de-France, France",
        "email": "contact@monkitsolaire.fr",
        "phone": "+33 3 59 89 74 00",
        "platform": "PrestaShop",
    },
}


def _load_tools_70_into_registry() -> None:
    """Auto-registers all remaining Solar EU40 + all 70 European Power-Tool stores (140+ total) for 1-click PDF invoicing."""
    solar_p = Path(r"C:\Users\bratu\Documents\antigravity\amazing-borg\bf-price-radar-ro\solar_eu40_manifest.json")
    if solar_p.exists():
        try:
            s_items = json.loads(solar_p.read_text(encoding="utf-8"))
            for it in s_items:
                dom = it["domain"].lower().strip()
                if dom not in CLIENT_REGISTRY:
                    CLIENT_REGISTRY[dom] = {
                        "country": it["cc"],
                        "company_name": it["company_name"],
                        "vat_id": it["vat_id"],
                        "reg_com": it["reg_com"],
                        "address": it["address"],
                        "email": it["email"],
                        "phone": it["phone"],
                        "platform": it["platform"],
                        "niche": "solar",
                    }
        except Exception:
            pass

    for mp_str in [
        r"C:\Users\bratu\Documents\antigravity\amazing-borg\bf-tools-radar\tools_all_70_manifest.json",
        r"C:\Users\bratu\Documents\antigravity\amazing-borg\bf-tools-radar\tools_batch2_70_manifest.json",
    ]:
        manifest_p = Path(mp_str)
        if not manifest_p.exists():
            continue
        try:
            items = json.loads(manifest_p.read_text(encoding="utf-8"))
            for it in items:
                dom = it["domain"].lower().strip()
                CLIENT_REGISTRY[dom] = {
                    "country": it["cc"],
                    "company_name": it["company_name"],
                    "vat_id": it["vat_id"],
                    "reg_com": it["reg_com"],
                    "address": it["address"],
                    "email": it["email"],
                    "phone": it["phone"],
                    "platform": "E-Commerce" if any(k in it["platform"].lower() for k in ("platforma", "shopsystem", "webshop", "webstore", "vostro", "boutique", "tienda", "catalogo")) else it["platform"],
                    "niche": "tools",
                }
        except Exception:
            pass


_load_tools_70_into_registry()


def _load_tires_70_into_registry() -> None:
    try:
        tires_dir = Path(__file__).resolve().parent.parent / "bf-tires-radar"
        if str(tires_dir) not in sys.path:
            sys.path.insert(0, str(tires_dir))
        from tires_70_config import TIRES_STORES_BY_CC
        for cc, stores in TIRES_STORES_BY_CC.items():
            for st in stores:
                CLIENT_REGISTRY[st["domain"]] = {
                    "country": cc,
                    "company_name": st["company_name"],
                    "vat_id": st["vat_id"],
                    "reg_com": "-",
                    "address": st["address"],
                    "email": st["email"],
                    "phone": "-",
                    "platform": st["platform"],
                    "niche": "tires",
                }
    except Exception:
        pass


_load_tires_70_into_registry()


def _resolve_package_description(
    country: str,
    pachet_val: float,
    client_domain: str,
    platform: str,
    niche: str = "solar",
) -> Tuple[str, str]:
    """Returneaza titlul scurt al serviciului (fara trunchiere) si descrierea detaliata (Solar, Scule sau Anvelope Iarna)."""
    amt = int(round(pachet_val))
    c_up = country.upper()
    is_tools = (niche == "tools")
    is_tires = (niche == "tires")
    if c_up == "RO":
        seg_ro = "anvelope de iarna RO" if is_tires else ("scule electrice RO" if is_tools else "fotovoltaice RO")
        if amt <= 160:
            title = "Optiunea 1: Audit Complet Preturi & Stocuri Sezon Iarna / BF"
            desc = (
                f"Domeniu analizat: {client_domain}. Servicii B2B de analiza comparativa preturi si stocuri pe "
                f"10 magazine {seg_ro} + Compari/eMAG (Matrice Excel 25 modele + Tabel Import {platform})."
            )
        else:
            title = "Optiunea 2: Radar Live Sezon Iarna 30 Zile & Alerte Stoc/Pret"
            desc = (
                f"Domeniu monitorizat: {client_domain}. Monitorizare automata B2B (3x/zi timp de 30 zile) + "
                f"Alerte WhatsApp/Email + Exclusivitate pe 2 branduri principale + Fisiere import {platform}."
            )
    elif c_up == "IT":
        seg_it = "pneumatici invernali (3PMSF)" if is_tires else ("utensileria ed elettroutensili" if is_tools else "fotovoltaici")
        if amt <= 260:
            title = "Opzione 1: Audit Completo Prezzi & Stock Stagione Invernale"
            desc = (
                f"Dominio analizzato: {client_domain}. Servizio B2B di Price & Stock Intelligence sui Top 10 e-commerce "
                f"{seg_it} in Italia + Benchmark Trovaprezzi (Matrice Excel + Foglio Import {platform})."
            )
        else:
            title = "Opzione 2: Radar Live Stagione Invernale 30 Giorni (Esclusiva)"
            desc = (
                f"Dominio monitorato: {client_domain}. Monitoraggio automatico B2B (3x/giorno per 30 giorni) di prezzi "
                f"e rotture di stock + Alert WhatsApp/Email + Esclusiva su 2 brand + Export {platform}."
            )
    else:
        seg_eu = "winter tyre (3PMSF) retailers" if is_tires else ("power-tool & hardware distributors" if is_tools else "solar & battery distributors")
        seg_brand = "winter tyre brands" if is_tires else ("power-tool brands" if is_tools else "solar brands")
        threshold = 200 if c_up == "UK" else 260
        if amt <= threshold:
            title = "Option 1: Full Winter Season / BF Price & Stock Market Audit"
            desc = (
                f"Target store: {client_domain} ({c_up}). B2B Competitive Price & Stock Matrix across Top 10 national "
                f"{seg_eu} + Marketplace Benchmark + Direct {platform} Price Import Sheet."
            )
        else:
            title = "Option 2: 30-Day Live Winter Season Price & Stock Radar"
            desc = (
                f"Target store: {client_domain} ({c_up}). Automated 3x daily B2B price & stock monitoring for 30 days + "
                f"Instant WhatsApp/Email alerts + Exclusive lock on 2 core {seg_brand} + {platform} exports."
            )
    return title, desc


# ==============================================================================
# 3. MOTOR VECTORIAL PDF 1.4 NATIV (CU ALINIERE LA DREAPTA PERFECTA)
# ==============================================================================
def _pdf_escape(text: str) -> str:
    replacements = {
        "ă": "a", "Ă": "A",
        "â": "a", "Â": "A",
        "î": "i", "Î": "I",
        "ș": "s", "Ș": "S", "ş": "s", "Ş": "S",
        "ț": "t", "Ț": "T", "ţ": "t", "Ţ": "T",
        "—": "-", "–": "-",
        "“": '"', "”": '"', "’": "'", "‘": "'",
        "•": "-",
    }
    clean = text
    for k, v in replacements.items():
        clean = clean.replace(k, v)
    raw_bytes = clean.encode("cp1252", errors="replace")
    out = []
    for b in raw_bytes:
        ch = chr(b)
        if ch in ("(", ")", "\\"):
            out.append("\\" + ch)
        elif 32 <= b <= 126:
            out.append(ch)
        else:
            out.append(f"\\{b:03o}")
    return "".join(out)


def _estimate_text_width(txt: str, size: float, bold: bool = False) -> float:
    """Estimeaza latimea in puncte a unui string Helvetica pentru aliniere la dreapta fara suprapunere."""
    avg_factor = 0.56 if bold else 0.52
    return len(txt) * size * avg_factor


def _wrap_text(text: str, max_chars: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    cur: List[str] = []
    cur_len = 0
    for w in words:
        if cur_len + len(w) + (1 if cur else 0) <= max_chars:
            cur.append(w)
            cur_len += len(w) + (1 if len(cur) > 1 else 0)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
            cur_len = len(w)
    if cur:
        lines.append(" ".join(cur))
    return lines or [""]


class VectorPDFCanvas:
    """Generator PDF 1.4 vectorial rapid si curat pentru facturi B2B A4 (595 x 842 pt)."""

    def __init__(self) -> None:
        self.ops: List[str] = []

    def rect_fill(self, x: float, y: float, w: float, h: float, r: float, g: float, b: float) -> None:
        self.ops.append(f"q {r:.3f} {g:.3f} {b:.3f} rg {x:.2f} {y:.2f} {w:.2f} {h:.2f} re f Q")

    def rect_stroke(self, x: float, y: float, w: float, h: float, r: float, g: float, b: float, lw: float = 0.8) -> None:
        self.ops.append(f"q {lw:.2f} w {r:.3f} {g:.3f} {b:.3f} RG {x:.2f} {y:.2f} {w:.2f} {h:.2f} re S Q")

    def line(self, x1: float, y1: float, x2: float, y2: float, r: float, g: float, b: float, lw: float = 0.8) -> None:
        self.ops.append(f"q {lw:.2f} w {r:.3f} {g:.3f} {b:.3f} RG {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S Q")

    def text(
        self,
        x: float,
        y: float,
        txt: str,
        font: str = "F1",
        size: float = 10.0,
        color: Tuple[float, float, float] = (0.06, 0.09, 0.16),
    ) -> None:
        r, g, b = color
        esc = _pdf_escape(txt)
        self.ops.append(f"BT /{font} {size:.2f} Tf {r:.3f} {g:.3f} {b:.3f} rg {x:.2f} {y:.2f} Td ({esc}) Tj ET")

    def text_right(
        self,
        right_x: float,
        y: float,
        txt: str,
        font: str = "F2",
        size: float = 10.0,
        color: Tuple[float, float, float] = (0.06, 0.09, 0.16),
    ) -> None:
        w = _estimate_text_width(txt, size, bold=(font == "F2"))
        self.text(right_x - w, y, txt, font=font, size=size, color=color)

    def save(self, out_path: Path) -> None:
        stream_data = "\n".join(self.ops).encode("latin-1")
        objects: List[bytes] = []

        objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
        objects.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
        objects.append(
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Resources << /Font << /F1 4 0 R /F2 5 0 R /F3 6 0 R >> >> /Contents 7 0 R >>"
        )
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique /Encoding /WinAnsiEncoding >>")
        objects.append(
            f"<< /Length {len(stream_data)} >>\nstream\n".encode("latin-1")
            + stream_data
            + b"\nendstream"
        )

        pdf_bytes = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets: List[int] = []
        for idx, obj in enumerate(objects, start=1):
            offsets.append(len(pdf_bytes))
            pdf_bytes.extend(f"{idx} 0 obj\n".encode("latin-1"))
            pdf_bytes.extend(obj)
            pdf_bytes.extend(b"\nendobj\n")

        xref_pos = len(pdf_bytes)
        pdf_bytes.extend(f"xref\n0 {len(objects) + 1}\n".encode("latin-1"))
        pdf_bytes.extend(b"0000000000 65535 f \n")
        for off in offsets:
            pdf_bytes.extend(f"{off:010d} 00000 n \n".encode("latin-1"))

        pdf_bytes.extend(
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin-1")
        )
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(bytes(pdf_bytes))


def generate_proforma_pdf(
    client_domain: str,
    pachet_val: float,
    country_override: Optional[str] = None,
    currency: str = "EUR",
    invoice_number: Optional[str] = None,
) -> Tuple[Path, Path]:
    clean_dom = client_domain.lower().strip().replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]

    client_info = CLIENT_REGISTRY.get(clean_dom)
    if not client_info:
        if clean_dom.endswith(".ro"):
            auto_c = "RO"
        elif clean_dom.endswith(".it") or clean_dom.endswith(".store"):
            auto_c = "IT"
        elif clean_dom.endswith(".uk") or clean_dom.endswith(".shop"):
            auto_c = "UK"
        elif clean_dom.endswith(".de"):
            auto_c = "DE"
        elif clean_dom.endswith(".at"):
            auto_c = "AT"
        elif clean_dom.endswith(".nl"):
            auto_c = "NL"
        elif clean_dom.endswith(".be"):
            auto_c = "BE"
        elif clean_dom.endswith(".es"):
            auto_c = "ES"
        elif clean_dom.endswith(".fr") or clean_dom.endswith(".solar"):
            auto_c = "FR"
        else:
            auto_c = "IT"
        client_info = {
            "country": auto_c,
            "company_name": f"{clean_dom.upper()}",
            "vat_id": f"{auto_c} - B2B VIES",
            "reg_com": "Commercial Register",
            "address": auto_c,
            "email": f"info@{clean_dom}",
            "phone": "-",
            "platform": "E-Commerce",
        }

    country = (country_override or client_info["country"]).upper()
    curr = "GBP" if (country == "UK" and currency == "EUR" and pachet_val in (295, 690)) else currency.upper()
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    date_display = now.strftime("%d/%m/%Y")
    due_display = (now + timedelta(days=5)).strftime("%d/%m/%Y")
    slug6 = clean_dom.split(".")[0].replace("-", "").replace("_", "")[:6].upper()
    inv_no = invoice_number or f"PRO-{now.strftime('%y%m%d')}-{slug6}"

    c = VectorPDFCanvas()

    # --------------------------------------------------------------------------
    # 1. BANNER SUPERIOR DARK NAVY (#0F172A) — FARA SUPRAPUNERE CU CASETA DREAPTA
    # --------------------------------------------------------------------------
    c.rect_fill(0, 742, 595, 100, 0.059, 0.090, 0.165)
    doc_title = (
        "FATTURA PROFORMA / FACTURA B2B"
        if country == "RO"
        else "FATTURA PROFORMA / B2B INVOICE"
    )
    c.text(36, 804, doc_title, font="F2", size=16.0, color=(1.0, 1.0, 1.0))
    c.text(36, 784, TITOLARE_NOME, font="F2", size=10.2, color=(0.58, 0.77, 0.99))
    c.text(
        36,
        767,
        f"Sede: {TITOLARE_INDIRIZZO}  |  Partita IVA: {PARTITA_IVA}",
        font="F1",
        size=8.8,
        color=(0.82, 0.86, 0.92),
    )
    c.text(
        36,
        752,
        f"Email: {CONTATTO_EMAIL} | PayPal: {PAYPAL_BUSINESS_EMAIL} | WhatsApp: +39 320 948 1876",
        font="F1",
        size=7.8,
        color=(0.82, 0.86, 0.92),
    )

    # Caseta Numar & Data Factura (dreapta sus — lata de 165pt ca sa incapa comod)
    c.rect_fill(394, 750, 165, 76, 0.118, 0.161, 0.231)
    c.rect_stroke(394, 750, 165, 76, 0.22, 0.30, 0.42, lw=0.7)
    c.text(404, 808, f"N. Doc: {inv_no}", font="F2", size=9.2, color=(1.0, 1.0, 1.0))
    c.text(404, 792, f"Data: {date_display}", font="F1", size=8.8, color=(0.85, 0.90, 0.96))
    c.text(404, 776, f"Scadenza: {due_display}", font="F1", size=8.8, color=(0.85, 0.90, 0.96))
    c.text(404, 759, f"Valuta: {curr} (0% IVA / VAT)", font="F2", size=8.6, color=(0.30, 0.87, 0.50))

    # --------------------------------------------------------------------------
    # 2. CASETA FORNITORE (Stanga) & CLIENTE / BENEFICIAR (Dreapta)
    # --------------------------------------------------------------------------
    c.rect_fill(36, 610, 250, 112, 0.973, 0.980, 0.988)
    c.rect_stroke(36, 610, 250, 112, 0.80, 0.84, 0.90)
    lbl_forn = "FORNITORE / FURNIZOR (ITALIA):" if country == "RO" else "FORNITORE / SUPPLIER (ITALY):"
    c.text(46, 705, lbl_forn, font="F2", size=8.8, color=(0.12, 0.23, 0.54))
    c.text(46, 689, "Vasile Bratu", font="F2", size=10.5, color=(0.06, 0.09, 0.16))
    c.text(46, 674, "Python Automation & Data Intelligence", font="F1", size=9.0, color=(0.20, 0.25, 0.33))
    c.text(46, 659, TITOLARE_INDIRIZZO, font="F1", size=8.8, color=(0.20, 0.25, 0.33))
    c.text(46, 644, f"P.IVA IT: {PARTITA_IVA}", font="F2", size=9.0, color=(0.06, 0.09, 0.16))
    c.text(46, 629, "Regime Forfettario (Legge n. 190/2014)", font="F3", size=8.5, color=(0.30, 0.35, 0.45))

    c.rect_fill(305, 610, 254, 112, 0.973, 0.980, 0.988)
    c.rect_stroke(305, 610, 254, 112, 0.80, 0.84, 0.90)
    lbl_cli = f"CLIENTE / BENEFICIAR B2B ({country}):"
    c.text(315, 705, lbl_cli, font="F2", size=8.8, color=(0.12, 0.23, 0.54))
    c.text(315, 689, client_info["company_name"][:38], font="F2", size=10.0, color=(0.06, 0.09, 0.16))
    c.text(315, 674, f"VAT / P.IVA / CIF: {client_info['vat_id']}", font="F2", size=8.8, color=(0.06, 0.09, 0.16))
    c.text(315, 659, f"Reg.: {client_info['reg_com']}  |  Web: {clean_dom}", font="F1", size=8.4, color=(0.20, 0.25, 0.33))
    c.text(315, 644, f"Sede: {client_info['address'][:42]}", font="F1", size=8.4, color=(0.20, 0.25, 0.33))
    c.text(315, 629, f"Email: {client_info['email']}", font="F1", size=8.4, color=(0.20, 0.25, 0.33))

    # --------------------------------------------------------------------------
    # 3. TABELUL DE SERVICII FACTURATE (FARA TRUNCHIERE SI FARA SUPRAPUNERE)
    # --------------------------------------------------------------------------
    c.rect_fill(36, 566, 523, 26, 0.118, 0.227, 0.541)
    col_desc_hdr = "DESCRIZIONE SERVIZIO / DESCRIERE SERVICII B2B" if country == "RO" else "DESCRIZIONE SERVIZIO B2B / DESCRIPTION"
    c.text(46, 575, "#", font="F2", size=9.0, color=(1.0, 1.0, 1.0))
    c.text(68, 575, col_desc_hdr, font="F2", size=9.0, color=(1.0, 1.0, 1.0))
    c.text(382, 575, "Q.TA", font="F2", size=9.0, color=(1.0, 1.0, 1.0))
    c.text(425, 575, "IVA / VAT", font="F2", size=9.0, color=(1.0, 1.0, 1.0))
    c.text_right(549, 575, f"TOTALE {curr}", font="F2", size=9.0, color=(1.0, 1.0, 1.0))

    svc_title, svc_desc = _resolve_package_description(
        country,
        pachet_val,
        clean_dom,
        client_info.get("platform", "Custom"),
        client_info.get("niche", "solar"),
    )
    desc_lines = _wrap_text(svc_desc, 56)

    # Randul 1: Pachetul Principal
    c.rect_fill(36, 476, 523, 90, 1.0, 1.0, 1.0)
    c.rect_stroke(36, 476, 523, 90, 0.82, 0.86, 0.91)
    c.text(46, 546, "1", font="F2", size=9.5)
    c.text(68, 546, svc_title, font="F2", size=9.3, color=(0.06, 0.09, 0.16))
    y_cursor = 531
    for dl in desc_lines[:4]:
        c.text(68, y_cursor, dl, font="F1", size=8.4, color=(0.25, 0.30, 0.38))
        y_cursor -= 12
    c.text(390, 546, "1", font="F1", size=9.5)
    c.text(425, 546, "0% (Esente)", font="F2", size=8.6, color=(0.09, 0.40, 0.20))
    c.text_right(549, 546, f"{pachet_val:,.2f} {curr}", font="F2", size=9.8)

    # Randul 2: Imposta di bollo (scurtata curat ca sa nu atinga niciodata coloana Q.TA)
    c.rect_fill(36, 444, 523, 32, 0.98, 0.99, 1.0)
    c.rect_stroke(36, 444, 523, 32, 0.82, 0.86, 0.91)
    c.text(46, 456, "2", font="F1", size=9.0)
    bollo_txt = (
        "Imposta di bollo (2,00 EUR assolta sull'originale - inclusa / zero costi extra)"
        if country != "RO"
        else "Imposta di bollo (2,00 EUR assolta sull'originale - inclusa / fara cost suplimentar)"
    )
    c.text(68, 456, bollo_txt, font="F3", size=8.2, color=(0.30, 0.35, 0.45))
    c.text(390, 456, "1", font="F1", size=9.0)
    c.text(425, 456, "N/A", font="F1", size=8.5)
    c.text_right(549, 456, f"0.00 {curr}", font="F1", size=9.0)

    # --------------------------------------------------------------------------
    # 4. CASETA METODA DE PLATA: PAYPAL BUSINESS (Stanga, y=306..428, h=122)
    # --------------------------------------------------------------------------
    c.rect_fill(36, 306, 282, 122, 0.975, 0.982, 0.995)
    c.rect_stroke(36, 306, 282, 122, 0.12, 0.23, 0.54, lw=0.9)
    pay_hdr = (
        "MODALITA DI PAGAMENTO: PAYPAL BUSINESS"
        if country != "RO"
        else "MODALITA DI PAGAMENTO / PLATA: PAYPAL BUSINESS"
    )
    c.text(46, 410, pay_hdr, font="F2", size=8.8, color=(0.12, 0.23, 0.54))
    c.text(46, 393, "Metodo: PayPal Business (Checkout B2B / Carta)", font="F2", size=8.8, color=(0.06, 0.09, 0.16))
    c.text(46, 376, f"Conto PayPal Business: {PAYPAL_BUSINESS_EMAIL}", font="F2", size=9.2, color=(0.09, 0.40, 0.20))
    c.text(46, 359, "Intestatario: Vasile Bratu (P.IVA IT04128900045)", font="F1", size=8.6, color=(0.20, 0.25, 0.33))
    c.text(46, 342, f"Causale / Ref. Plata: {inv_no} ({clean_dom})", font="F2", size=8.6, color=(0.12, 0.23, 0.54))
    deliv_note = (
        "Livrare fisiere Excel + Activare: Imediat la confirmarea PayPal."
        if country == "RO"
        else "Consegna report Excel + Attivazione: Immediata via PayPal."
    )
    c.text(46, 320, deliv_note, font="F3", size=8.0, color=(0.30, 0.35, 0.45))

    # --------------------------------------------------------------------------
    # 5. CASETA SUMAR DE PLATA & TOTALE DA PAGARE (Dreapta, y=306..428, h=122)
    #    Aliniere perfecta stanga-dreapta, cu banda evidentiata jos pentru TOTALE DA PAGARE
    # --------------------------------------------------------------------------
    c.rect_fill(330, 306, 229, 122, 0.96, 0.975, 0.995)
    c.rect_stroke(330, 306, 229, 122, 0.12, 0.23, 0.54, lw=1.1)

    lbl_sub = "Imponibile / Baza Impozabila:" if country == "RO" else "Imponibile Netto B2B:"
    c.text(342, 406, lbl_sub, font="F1", size=8.8, color=(0.15, 0.20, 0.28))
    c.text_right(547, 406, f"{pachet_val:,.2f} {curr}", font="F2", size=9.2, color=(0.06, 0.09, 0.16))

    lbl_iva = "IVA / TVA (0% Scutit B2B):" if country == "RO" else "IVA / VAT (0% Regime Forfettario):"
    c.text(342, 384, lbl_iva, font="F1", size=8.8, color=(0.15, 0.20, 0.28))
    c.text_right(547, 384, f"0.00 {curr}", font="F2", size=9.2, color=(0.09, 0.40, 0.20))

    c.text(342, 362, "Imposta di Bollo (Inclusa):", font="F1", size=8.6, color=(0.30, 0.35, 0.45))
    c.text_right(547, 362, f"0.00 {curr}", font="F1", size=8.8, color=(0.30, 0.35, 0.45))

    # Banda Dark Navy in partea de jos a casetei de total pentru TOTALE DA PAGARE (vizibilitate 100%, zero suprapunere)
    c.rect_fill(330, 306, 229, 42, 0.09, 0.18, 0.42)
    c.text(342, 323, "TOTALE DA PAGARE:", font="F2", size=9.6, color=(1.0, 1.0, 1.0))
    c.text_right(547, 321, f"{pachet_val:,.2f} {curr}", font="F2", size=12.2, color=(0.45, 0.95, 0.62))

    # --------------------------------------------------------------------------
    # 6. CLAUZE LEGALE OBLIGATORII (Footer Fiscal)
    # --------------------------------------------------------------------------
    c.rect_fill(36, 125, 523, 158, 0.97, 0.98, 0.99)
    c.rect_stroke(36, 125, 523, 158, 0.78, 0.82, 0.88)

    if country == "RO":
        c.text(48, 263, "MENTIUNI FISCALE OBLIGATORII (BILINGV ITALIA / ROMANIA - B2B INTRACOMUNITAR):", font="F2", size=8.8, color=(0.12, 0.23, 0.54))
        legal_lines = [
            "1. Operazione effettuata ai sensi dell'art. 1, commi da 54 a 89, della Legge n. 190/2014 - Regime forfettario (0% IVA).",
            "2. Operazione non soggetta a IVA ai sensi dell'art. 7-ter DPR 633/72 - Inversione contabile / Reverse Charge intracomunitario B2B.",
            "3. Imposta di bollo da 2,00 EUR assolta sull'originale (per importi superiori a 77,47 EUR).",
            "4. NOTA CONTABILITATE ROMANIA: Factura externa de servicii B2B emisa din Italia in regim de scutire de TVA (0% TVA).",
            f"   Achitabila rapid prin PayPal Business ({PAYPAL_BUSINESS_EMAIL}); deductibila integral pe cheltuieli B2B.",
        ]
    elif country == "IT":
        c.text(48, 263, "DICITURE FISCALI OBBLIGATORIE DI LEGGE (CLIENTI B2B ITALIA):", font="F2", size=8.8, color=(0.12, 0.23, 0.54))
        legal_lines = [
            "1. Operazione effettuata ai sensi dell'art. 1, commi da 54 a 89, della Legge n. 190/2014 e successive modificazioni -",
            "   Regime forfettario senza applicazione dell'IVA (0% IVA).",
            "2. Prestazione di servizi non soggetta a ritenuta d'acconto ai sensi del comma 67 della Legge n. 190/2014.",
            "3. Imposta di bollo da 2,00 EUR assolta sull'originale (per importi superiori a 77,47 EUR).",
            f"4. Pagamento immediato tramite PayPal Business ({PAYPAL_BUSINESS_EMAIL}) - Zero IVA da anticipare.",
        ]
    else:
        c.text(48, 263, f"MANDATORY EU / INTERNATIONAL B2B TAX & INVOICE NOTES ({country}):", font="F2", size=8.8, color=(0.12, 0.23, 0.54))
        legal_lines = [
            "1. Issued under Italian Law n. 190/2014 (Art. 1, paragraphs 54-89) - Regime Forfettario (0% VAT / Tax Exempt).",
            "2. Cross-border B2B service not subject to Italian VAT pursuant to Art. 7-ter DPR 633/72 (B2B Reverse Charge).",
            "3. Italian stamp duty (Imposta di bollo 2.00 EUR) settled on the original by the supplier.",
            f"4. Instant B2B settlement via PayPal Business ({PAYPAL_BUSINESS_EMAIL}). Full Excel deliverables released upon payment.",
        ]

    y_leg = 243
    for ll in legal_lines:
        c.text(48, y_leg, ll, font="F1", size=8.4, color=(0.15, 0.20, 0.28))
        y_leg -= 18

    # Footer semnatura
    c.line(36, 95, 559, 95, 0.82, 0.86, 0.91, lw=0.7)
    c.text(
        36,
        76,
        f"Documento generato elettronicamente il {date_display} da {TITOLARE_NOME} | PayPal Business: {PAYPAL_BUSINESS_EMAIL}",
        font="F1",
        size=7.6,
        color=(0.35, 0.40, 0.48),
    )

    filename = f"Fattura_Proforma_{clean_dom}_{date_str}.pdf"
    desktop_dir = Path(r"C:\Users\bratu\Desktop")
    gen_dir = Path(r"C:\Users\bratu\Desktop\BF_Invoice_Generator")

    out_desktop = desktop_dir / filename
    out_gen = gen_dir / filename

    c.save(out_gen)
    c.save(out_desktop)
    return out_desktop, out_gen


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generator Instant B2B de Facturi Proforme PDF (PayPal Business) - Vasile Bratu"
    )
    parser.add_argument(
        "--client",
        type=str,
        default="masif.ro",
        help="Domeniul magazinului client (ex: masif.ro, masterfer.it, gotools.de, gereedschapcentrum.nl, sobrico.com, ferreteria.es, nutsandbolts.co.uk)",
    )
    parser.add_argument(
        "--optiune",
        type=int,
        choices=[1, 2],
        default=1,
        help="Varianta 1 (Audit Complet: RO 150 EUR | DE/IT/NL/FR/ES 350 EUR | UK 295 GBP) sau Varianta 2 (Radar Live 30 zile: RO 450 EUR | DE/IT/NL/FR/ES 850 EUR | UK 690 GBP)",
    )
    parser.add_argument(
        "--pachet",
        type=float,
        default=None,
        help="Valoarea explicita a pachetului (ex: 150, 450 pt RO | 350, 850 pt DE/IT/NL/FR/ES | 295, 690 pt UK). Daca lipseste, se aplica automat grila tarii!",
    )
    parser.add_argument(
        "--country",
        type=str,
        default=None,
        help="Fortare mod fiscal (RO, IT, UK, DE, NL, ES, FR)",
    )
    parser.add_argument(
        "--currency",
        type=str,
        default=None,
        help="Moneda facturii (EUR sau GBP; daca lipseste, se seteaza automat GBP pt UK si EUR pt restul)",
    )
    args = parser.parse_args()

    clean_dom = args.client.lower().strip().replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
    reg_entry = CLIENT_REGISTRY.get(clean_dom)
    detected_cc = (args.country or (reg_entry["country"] if reg_entry else ("UK" if clean_dom.endswith(".uk") else ("RO" if clean_dom.endswith(".ro") else "IT")))).upper()
    tier = COUNTRY_PRICING_TIERS.get(detected_cc, COUNTRY_PRICING_TIERS["IT"])

    resolved_pachet = args.pachet if args.pachet is not None else (tier["opt1"] if args.optiune == 1 else tier["opt2"])
    resolved_curr = (args.currency or tier["currency"]).upper()

    out_desktop, out_gen = generate_proforma_pdf(
        client_domain=args.client,
        pachet_val=resolved_pachet,
        country_override=args.country.upper() if args.country else None,
        currency=resolved_curr,
    )
    print(f"[OK] Factura Proforma B2B (PayPal Business) generata instantaneu ({resolved_pachet:.2f} {resolved_curr}):")
    print(f"  -> Desktop : {out_desktop}")
    print(f"  -> Arhiva  : {out_gen}")


if __name__ == "__main__":
    main()
