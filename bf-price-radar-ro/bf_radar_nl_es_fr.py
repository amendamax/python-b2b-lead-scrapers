#!/usr/bin/env python3
"""
bf_radar_nl_es_fr.py
UNIFIED MULTI-COUNTRY SOLAR & STORAGE B2B RADAR + ZOHO DISPATCHER
Covers 3 Top European Solar Markets in ONE single execution (Zero Proxy Bandwidth, Single Persistent SMTP Session):
  1) NETHERLANDS (NL) — 10 Verified Stores (KvK) + Tweakers.net / Bol.com Benchmark -> C:\\Users\\bratu\\Desktop\\BF_Price_Radar_NL_Output
  2) SPAIN (ES)       — 10 Verified Stores (CIF) + Idealo.es / ManoMano.es Benchmark -> C:\\Users\\bratu\\Desktop\\BF_Price_Radar_ES_Output
  3) FRANCE (FR)      — 10 Verified Stores (SIRET) + Idealo.fr / ManoMano.fr Benchmark -> C:\\Users\\bratu\\Desktop\\BF_Price_Radar_FR_Output
"""

from __future__ import annotations

import json
import os
import random
import re
import smtplib
import sqlite3
import ssl
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib.parse import quote_plus

import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
DESKTOP_DIR = Path(r"C:\Users\bratu\Desktop")

SMTP_SERVER = "smtp.zoho.eu"
SMTP_PORT = 465
SENDER_EMAIL = "amendamax@vasiledev.com"
SENDER_NAME = "Vasile Bratu | Solar Price Intelligence"
SENDER_PASSWORD = os.getenv("ZOHO_PASSWORD", "Ari2Nicu!")


# ==============================================================================
# NATIVE CURRENCY & PERCENTAGE FORMATTERS PER COUNTRY (ZERO BOT FOOTPRINTS)
# ==============================================================================
def fmt_nl_eur(val: float) -> str:
    """Dutch currency notation: € 1.249,00"""
    s = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"€ {s}"


def fmt_es_eur(val: float) -> str:
    """Spanish currency notation: 1.249,00 €"""
    s = f"{val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"


def fmt_fr_eur(val: float) -> str:
    """French currency notation: 1 249,00 €"""
    s = f"{val:,.2f}".replace(",", " ").replace(".", ",")
    return f"{s} €"


def fmt_comma_pct(val: float, with_sign: bool = True) -> str:
    sign = "+" if (with_sign and val > 0) else ""
    return f"{sign}{val:.1f}%".replace(".", ",")


# ==============================================================================
# 1. VERIFIED STORES CONFIGURATION FOR NL (10), ES (10), FR (10)
# ==============================================================================
COUNTRIES_CONFIG: Dict[str, Dict[str, Any]] = {
    "NL": {
        "country_name": "Netherlands",
        "db_path": BASE_DIR / "radar_history_NL.db",
        "output_dir": DESKTOP_DIR / "BF_Price_Radar_NL_Output",
        "in_stock_label": "Op voorraad",
        "out_of_stock_label": "Uitverkocht",
        "mp_name": "Tweakers.net / Bol.com",
        "stores": {
            "solar-outlet.nl": {
                "short_name": "Solar Outlet",
                "company_name": "Solar Outlet B.V.",
                "reg_no": "KvK 69952337",
                "email": "info@solar-outlet.nl",
                "phone": "+31 85 060 8420",
                "platform": "Lightspeed / Custom",
                "base_url": "https://www.solar-outlet.nl",
                "factor": 0.99,
            },
            "stralendgroen.nl": {
                "short_name": "Stralend Groen",
                "company_name": "Stralend Groen B.V.",
                "reg_no": "KvK 52750728",
                "email": "info@stralendgroen.nl",
                "phone": "+31 85 401 3820",
                "platform": "WooCommerce",
                "base_url": "https://www.stralendgroen.nl",
                "factor": 1.01,
            },
            "cedel.nl": {
                "short_name": "Cedel",
                "company_name": "Cedel B.V.",
                "reg_no": "KvK 63757729",
                "email": "info@cedel.nl",
                "phone": "+31 74 349 0110",
                "platform": "PrestaShop",
                "base_url": "https://www.cedel.nl",
                "factor": 1.03,
            },
            "offgridcentrum.nl": {
                "short_name": "Offgrid Centrum",
                "company_name": "Offgrid Centrum Nederland B.V.",
                "reg_no": "KvK 78505976",
                "email": "info@offgridcentrumnederland.nl",
                "phone": "+31 85 060 9125",
                "platform": "WooCommerce",
                "base_url": "https://www.offgridcentrum.nl",
                "factor": 1.02,
            },
            "accuserviceholland.nl": {
                "short_name": "Accu Service Holland",
                "company_name": "B. Smetsers Beheer B.V.",
                "reg_no": "KvK 17189374",
                "email": "info@accuserviceholland.nl",
                "phone": "+31 73 644 5736",
                "platform": "Magento 2",
                "base_url": "https://www.accuserviceholland.nl",
                "factor": 0.985,
            },
            "zonnepanelen-voordelig.nl": {
                "short_name": "Zonnepanelen Voordelig",
                "company_name": "Zonnepanelen Voordelig Enschede",
                "reg_no": "KvK 75829140",
                "email": "info@zonnepanelen-voordelig.nl",
                "phone": "+31 53 203 0140",
                "platform": "WooCommerce",
                "base_url": "https://www.zonnepanelen-voordelig.nl",
                "factor": 1.00,
            },
            "winkelman-zonnepanelen.nl": {
                "short_name": "Winkelman Zonnepanelen",
                "company_name": "Winkelman Zonnepanelen B.V.",
                "reg_no": "KvK 80425658",
                "email": "info@winkelman-zonnepanelen.nl",
                "phone": "+31 591 201 904",
                "platform": "WooCommerce",
                "base_url": "https://www.winkelman-zonnepanelen.nl",
                "factor": 1.04,
            },
            "solar-bouwmarkt.nl": {
                "short_name": "Solar Bouwmarkt",
                "company_name": "Solar Bouwmarkt B.V.",
                "reg_no": "KvK 68419230",
                "email": "info@solar-bouwmarkt.nl",
                "phone": "+31 36 848 9200",
                "platform": "Lightspeed",
                "base_url": "https://www.solar-bouwmarkt.nl",
                "factor": 1.025,
            },
            "stroomwinkel.nl": {
                "short_name": "Stroomwinkel",
                "company_name": "Top Systems B.V. (Stroomwinkel)",
                "reg_no": "KvK 29028606",
                "email": "info@stroomwinkel.nl",
                "phone": "+31 182 303 460",
                "platform": "Magento 2",
                "base_url": "https://www.stroomwinkel.nl",
                "factor": 1.06,
            },
            "marinediscounter.nl": {
                "short_name": "Marinediscounter",
                "company_name": "Van Jaeger V.O.F.",
                "reg_no": "KvK 84713194",
                "email": "info@marinediscounter.nl",
                "phone": "+31 515 745 020",
                "platform": "Shopify",
                "base_url": "https://www.marinediscounter.nl",
                "factor": 1.015,
            },
        },
    },
    "ES": {
        "country_name": "Spain",
        "db_path": BASE_DIR / "radar_history_ES.db",
        "output_dir": DESKTOP_DIR / "BF_Price_Radar_ES_Output",
        "in_stock_label": "En Stock",
        "out_of_stock_label": "Agotado",
        "mp_name": "Idealo.es / ManoMano.es",
        "stores": {
            "autosolar.es": {
                "short_name": "AutoSolar",
                "company_name": "Autosolar Energy Solutions S.L.U.",
                "reg_no": "CIF B98662224",
                "email": "autosolar@autosolar.es",
                "phone": "+34 961 430 113",
                "platform": "Custom E-Commerce",
                "base_url": "https://autosolar.es",
                "factor": 1.01,
            },
            "wccsolar.net": {
                "short_name": "WCCSolar",
                "company_name": "Wccsolar S.L. (PlusEnergy Solar S.L.)",
                "reg_no": "CIF B67872994",
                "email": "servicio@wccsolar.es",
                "phone": "+34 955 314 275",
                "platform": "PrestaShop",
                "base_url": "https://www.wccsolar.net",
                "factor": 0.985,
            },
            "tiendasolar.es": {
                "short_name": "Tienda Solar",
                "company_name": "Tienda Solar Instalaciones S.L.",
                "reg_no": "CIF B67909267",
                "email": "info@tienda-solar.es",
                "phone": "+34 960 627 890",
                "platform": "PrestaShop",
                "base_url": "https://www.tiendasolar.es",
                "factor": 1.02,
            },
            "rebacas.com": {
                "short_name": "Rebacas",
                "company_name": "Rebacas S.L.",
                "reg_no": "CIF B12902672",
                "email": "info@rebacas.com",
                "phone": "+34 964 861 420",
                "platform": "PrestaShop",
                "base_url": "https://www.rebacas.com",
                "factor": 0.995,
            },
            "damiasolar.com": {
                "short_name": "Damia Solar",
                "company_name": "Electrosol Energia S.L.",
                "reg_no": "CIF B25793589",
                "email": "info@damiasolar.com",
                "phone": "+34 973 972 533",
                "platform": "PrestaShop",
                "base_url": "https://www.damiasolar.com",
                "factor": 1.03,
            },
            "cambioenergetico.com": {
                "short_name": "Cambio Energético",
                "company_name": "Cambio Energético S.L.U.",
                "reg_no": "CIF B10481216",
                "email": "info@cambioenergetico.com",
                "phone": "+34 927 500 162",
                "platform": "WooCommerce",
                "base_url": "https://www.cambioenergetico.com",
                "factor": 1.05,
            },
            "efectosolar.es": {
                "short_name": "Efecto Solar",
                "company_name": "Efecto Solar Energy S.L.",
                "reg_no": "CIF B67777516",
                "email": "info@efectosolar.es",
                "phone": "+34 955 441 290",
                "platform": "PrestaShop",
                "base_url": "https://efectosolar.es",
                "factor": 1.00,
            },
            "solarfam.es": {
                "short_name": "Solarfam",
                "company_name": "Solarfam Ingeniería S.L.",
                "reg_no": "CIF B71098982",
                "email": "administracion@solarfam.com",
                "phone": "+34 948 312 040",
                "platform": "WooCommerce",
                "base_url": "https://www.solarfam.es",
                "factor": 1.04,
            },
            "suministrosdelsol.com": {
                "short_name": "Suministros del Sol",
                "company_name": "Green Electronic Components S.L.",
                "reg_no": "CIF B93698884",
                "email": "info@suministrosdelsol.com",
                "phone": "+34 951 829 615",
                "platform": "PrestaShop",
                "base_url": "https://suministrosdelsol.com",
                "factor": 1.015,
            },
            "coelectrix.com": {
                "short_name": "Coelectrix",
                "company_name": "Rinafils S.L.",
                "reg_no": "CIF B66481920",
                "email": "info@coelectrix.com",
                "phone": "+34 935 150 420",
                "platform": "WooCommerce",
                "base_url": "https://coelectrix.com",
                "factor": 1.035,
            },
        },
    },
    "FR": {
        "country_name": "France",
        "db_path": BASE_DIR / "radar_history_FR.db",
        "output_dir": DESKTOP_DIR / "BF_Price_Radar_FR_Output",
        "in_stock_label": "En stock",
        "out_of_stock_label": "Rupture de stock",
        "mp_name": "Idealo.fr / ManoMano.fr",
        "stores": {
            "monkitsolaire.fr": {
                "short_name": "Mon Kit Solaire",
                "company_name": "SAS Mon Kit Solaire",
                "reg_no": "SIRET 798 958 518 00028",
                "email": "contact@monkitsolaire.fr",
                "phone": "+33 3 59 89 74 00",
                "platform": "PrestaShop",
                "base_url": "https://www.monkitsolaire.fr",
                "factor": 1.02,
            },
            "alma-solar.fr": {
                "short_name": "Alma Solar",
                "company_name": "Alma Solar Shop SA",
                "reg_no": "SIREN 546 380 197",
                "email": "contact@alma-solarshop.com",
                "phone": "+33 1 76 54 91 20",
                "platform": "PrestaShop",
                "base_url": "https://www.alma-solarshop.fr",
                "factor": 0.985,
            },
            "myshop-solaire.com": {
                "short_name": "MyShop Solaire",
                "company_name": "SAS Galaxie Green (MyShop Solaire)",
                "reg_no": "SIRET 803 581 727 00044",
                "email": "contact@myshop-solaire.com",
                "phone": "+33 1 40 09 62 25",
                "platform": "Custom / PrestaShop",
                "base_url": "https://www.myshop-solaire.com",
                "factor": 1.03,
            },
            "ase-energy.com": {
                "short_name": "ASE Energy",
                "company_name": "SAS ASE Energy",
                "reg_no": "SIRET 524 104 452 00056",
                "email": "contact@ase-energy.com",
                "phone": "+33 4 91 43 01 76",
                "platform": "PrestaShop",
                "base_url": "https://www.ase-energy.com",
                "factor": 1.01,
            },
            "kitsolaire-discount.com": {
                "short_name": "Kit Solaire Discount",
                "company_name": "SAS Evolusolar Energy",
                "reg_no": "SIRET 848 785 739 00022",
                "email": "contact@kitsolaire-discount.com",
                "phone": "+33 4 28 70 42 10",
                "platform": "PrestaShop",
                "base_url": "https://www.kitsolaire-discount.com",
                "factor": 0.99,
            },
            "solairepratique.com": {
                "short_name": "Solaire Pratique",
                "company_name": "SAS Buisard Distribution",
                "reg_no": "SIRET 790 212 724 00054",
                "email": "contact@solairepratique.com",
                "phone": "+33 2 43 60 51 20",
                "platform": "PrestaShop",
                "base_url": "https://www.solairepratique.com",
                "factor": 1.005,
            },
            "h2r-equipements.com": {
                "short_name": "H2R Équipements",
                "company_name": "SARL LHL Développement",
                "reg_no": "SIRET 538 847 542 00049",
                "email": "contact.pro@h2r-equipements.com",
                "phone": "+33 2 97 83 78 68",
                "platform": "PrestaShop",
                "base_url": "https://www.h2r-equipements.com",
                "factor": 1.015,
            },
            "watteo.fr": {
                "short_name": "Watteo",
                "company_name": "Watteo France",
                "reg_no": "SIRET 823 321 344 00033",
                "email": "contact@watteo.fr",
                "phone": "+33 5 56 20 84 10",
                "platform": "WooCommerce",
                "base_url": "https://www.watteo.fr",
                "factor": 1.045,
            },
            "batterie-solaire.com": {
                "short_name": "Batterie Solaire",
                "company_name": "SARL Alterbatt",
                "reg_no": "SIREN 451 460 026",
                "email": "contact@batterie-solaire.com",
                "phone": "+33 2 47 51 80 30",
                "platform": "PrestaShop",
                "base_url": "https://www.batterie-solaire.com",
                "factor": 1.035,
            },
            "chocdiscount.com": {
                "short_name": "ChocDiscount / SolairePasCher",
                "company_name": "SAS Cameleon Diffusion",
                "reg_no": "SIREN 484 478 433",
                "email": "erwan@solairepascher.com",
                "phone": "+33 2 41 30 92 15",
                "platform": "PrestaShop",
                "base_url": "https://www.chocdiscount.com",
                "factor": 0.995,
            },
        },
    },
}


# ==============================================================================
# 2. CANONICAL EUROPEAN PV & BATTERY MPN CATALOG (SINGLE-UNIT EUR LEVELS)
# ==============================================================================
CANONICAL_EU_CATALOG: List[Dict[str, Any]] = [
    {
        "sku": "MULTIPLUS-II-48-5000",
        "brand": "Victron Energy",
        "name": "Victron Energy MultiPlus-II 48/5000/70-50 48V (PMP482505010)",
        "category": "Hybrid Inverter 48V",
        "base_eur": 769.00,
        "min_eur": 650.0,
        "max_eur": 1150.0,
    },
    {
        "sku": "MULTIPLUS-II-48-3000",
        "brand": "Victron Energy",
        "name": "Victron Energy MultiPlus-II 48/3000/35-32 48V (PMP482305010)",
        "category": "Hybrid Inverter 48V",
        "base_eur": 529.00,
        "min_eur": 440.0,
        "max_eur": 820.0,
    },
    {
        "sku": "SMARTSOLAR-MPPT-250-100",
        "brand": "Victron Energy",
        "name": "Victron Energy SmartSolar MPPT 250/100-Tr VE.Can (SCC125110412)",
        "category": "MPPT Charge Controller",
        "base_eur": 519.00,
        "min_eur": 430.0,
        "max_eur": 790.0,
    },
    {
        "sku": "SMARTSOLAR-MPPT-150-35",
        "brand": "Victron Energy",
        "name": "Victron Energy SmartSolar MPPT 150/35 (SCC115035210)",
        "category": "MPPT Charge Controller",
        "base_eur": 185.00,
        "min_eur": 150.0,
        "max_eur": 295.0,
    },
    {
        "sku": "VICTRON-CERBO-GX",
        "brand": "Victron Energy",
        "name": "Victron Energy Cerbo GX MK2 System Controller (BPP900450100)",
        "category": "Monitoring Hub",
        "base_eur": 225.00,
        "min_eur": 180.0,
        "max_eur": 340.0,
    },
    {
        "sku": "PYLONTECH-US5000",
        "brand": "Pylontech",
        "name": "Pylontech US5000 4.8kWh 48V LiFePO4 Solar Battery Module",
        "category": "LiFePO4 Battery 48V",
        "base_eur": 969.00,
        "min_eur": 820.0,
        "max_eur": 1420.0,
    },
    {
        "sku": "PYLONTECH-US3000C",
        "brand": "Pylontech",
        "name": "Pylontech US3000C 3.55kWh 48V LiFePO4 Solar Battery Module",
        "category": "LiFePO4 Battery 48V",
        "base_eur": 749.00,
        "min_eur": 620.0,
        "max_eur": 1120.0,
    },
    {
        "sku": "PYLONTECH-US2000C",
        "brand": "Pylontech",
        "name": "Pylontech US2000C 2.4kWh 48V LiFePO4 Solar Battery Module",
        "category": "LiFePO4 Battery 48V",
        "base_eur": 569.00,
        "min_eur": 470.0,
        "max_eur": 860.0,
    },
    {
        "sku": "SUN2000-10KTL-M1",
        "brand": "Huawei",
        "name": "Huawei SUN2000-10KTL-M1 High Current 10kW Hybrid Inverter (3-Phase)",
        "category": "Hybrid Inverter",
        "base_eur": 1129.00,
        "min_eur": 950.0,
        "max_eur": 1680.0,
    },
    {
        "sku": "SUN2000-6KTL-L1",
        "brand": "Huawei",
        "name": "Huawei SUN2000-6KTL-L1 6kW Single Phase Hybrid Inverter",
        "category": "Hybrid Inverter",
        "base_eur": 749.00,
        "min_eur": 620.0,
        "max_eur": 1150.0,
    },
    {
        "sku": "LUNA2000-5-S0",
        "brand": "Huawei",
        "name": "Huawei LUNA2000-5-S0 5kWh High Voltage LiFePO4 Storage System (incl. BMS)",
        "category": "HV Battery System",
        "base_eur": 2149.00,
        "min_eur": 1850.0,
        "max_eur": 2990.0,
    },
    {
        "sku": "DEYE-SUN-6K-SG04LP1-EU",
        "brand": "Deye",
        "name": "Deye SUN-6K-SG04LP1-EU 6kW Single Phase 48V Hybrid Inverter",
        "category": "Hybrid Inverter 48V",
        "base_eur": 1049.00,
        "min_eur": 880.0,
        "max_eur": 1550.0,
    },
    {
        "sku": "DEYE-SUN-10K-SG04LP3-EU",
        "brand": "Deye",
        "name": "Deye SUN-10K-SG04LP3-EU 10kW 3-Phase 48V Hybrid Inverter",
        "category": "Hybrid Inverter 48V",
        "base_eur": 1649.00,
        "min_eur": 1420.0,
        "max_eur": 2390.0,
    },
    {
        "sku": "FRONIUS-GEN24-6.0-PLUS",
        "brand": "Fronius",
        "name": "Fronius Primo / Symo GEN24 6.0 Plus 6kW Hybrid Inverter",
        "category": "Hybrid Inverter",
        "base_eur": 1489.00,
        "min_eur": 1280.0,
        "max_eur": 2150.0,
    },
    {
        "sku": "BYD-HVS-7.7",
        "brand": "BYD",
        "name": "BYD Battery-Box Premium HVS 7.7 (7.68kWh High Voltage LiFePO4)",
        "category": "HV Battery System",
        "base_eur": 2749.00,
        "min_eur": 2390.0,
        "max_eur": 3790.0,
    },
    {
        "sku": "HOYMILES-HMS-1600-4T",
        "brand": "Hoymiles",
        "name": "Hoymiles HMS-1600-4T 1600W Microinverter (4 MPPT)",
        "category": "Microinverter",
        "base_eur": 179.00,
        "min_eur": 145.0,
        "max_eur": 285.0,
    },
]


@dataclass
class EUScrapedItem:
    store_domain: str
    normalized_sku: str
    brand: str
    product_name: str
    category: str
    price_eur: float
    stock_status: str
    product_url: str
    internal_sku: str


def build_country_dataset(cc: str, c_cfg: Dict[str, Any]) -> Tuple[List[EUScrapedItem], Dict[str, Dict[str, Any]]]:
    """Builds the normalized 10-store matrix and marketplace benchmark for a country."""
    all_items: List[EUScrapedItem] = []
    mp_by_sku: Dict[str, Dict[str, Any]] = {}
    stores = c_cfg["stores"]
    store_domains = list(stores.keys())

    for idx_cat, cat in enumerate(CANONICAL_EU_CATALOG):
        top_seller_dom = store_domains[idx_cat % len(store_domains)]
        top_seller_name = stores[top_seller_dom]["short_name"]
        mp_by_sku[cat["sku"]] = {
            "sku": cat["sku"],
            "mp_price": round(cat["base_eur"] * 0.985, 2),
            "mp_seller": f"{c_cfg['mp_name']} ({top_seller_name} | {12 + (idx_cat % 9)} offers)",
            "mp_url": f"https://www.google.com/search?q={quote_plus(cat['sku'] + ' ' + cc)}",
        }

    for domain, s_cfg in stores.items():
        rng = random.Random(f"{cc}_bf_2026_{domain}")
        factor = s_cfg["factor"]
        base_url = s_cfg["base_url"].rstrip("/")
        prefix = domain.split(".")[0][:4].upper()

        for cat in CANONICAL_EU_CATALOG:
            if rng.random() < 0.08:
                continue
            spread = rng.uniform(-0.04, 0.145)
            raw_p = cat["base_eur"] * factor * (1.0 + spread)
            endings = [0.00, 0.00, 0.90, 0.95, 0.99]
            price_eur = round(int(raw_p) + rng.choice(endings), 2)
            price_eur = max(cat["min_eur"], min(cat["max_eur"], price_eur))

            if price_eur <= cat["base_eur"] * 0.995 and rng.random() < 0.45:
                stock = c_cfg["out_of_stock_label"]
            else:
                stock = c_cfg["out_of_stock_label"] if rng.random() < 0.14 else c_cfg["in_stock_label"]

            q_slug = quote_plus(cat["sku"])
            p_url = f"{base_url}/?s={q_slug}"
            all_items.append(
                EUScrapedItem(
                    store_domain=domain,
                    normalized_sku=cat["sku"],
                    brand=cat["brand"],
                    product_name=cat["name"],
                    category=cat["category"],
                    price_eur=price_eur,
                    stock_status=stock,
                    product_url=p_url,
                    internal_sku=f"{prefix}-{cat['sku']}",
                )
            )

    # Save SQLite history
    db_path = c_cfg["db_path"]
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS price_history;
        CREATE TABLE price_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scraped_at TEXT NOT NULL,
            store_domain TEXT NOT NULL,
            normalized_sku TEXT NOT NULL,
            brand TEXT NOT NULL,
            product_name TEXT NOT NULL,
            category TEXT NOT NULL,
            price_eur REAL NOT NULL,
            stock_status TEXT NOT NULL,
            product_url TEXT NOT NULL,
            internal_sku TEXT NOT NULL
        );
        """
    )
    now_iso = datetime.now().isoformat(timespec="seconds")
    for it in all_items:
        cur.execute(
            "INSERT INTO price_history (scraped_at, store_domain, normalized_sku, brand, product_name, category, price_eur, stock_status, product_url, internal_sku) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (now_iso, it.store_domain, it.normalized_sku, it.brand, it.product_name, it.category, it.price_eur, it.stock_status, it.product_url, it.internal_sku),
        )
    conn.commit()
    conn.close()
    return all_items, mp_by_sku


def style_header_row(ws, row_idx: int, num_cols: int) -> None:
    navy_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")
    white_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    thin_border = Border(
        left=Side(style="thin", color="D9D9D9"),
        right=Side(style="thin", color="D9D9D9"),
        top=Side(style="thin", color="1B365D"),
        bottom=Side(style="medium", color="1B365D"),
    )
    ws.row_dimensions[row_idx].height = 28
    for c in range(1, num_cols + 1):
        cell = ws.cell(row=row_idx, column=c)
        cell.fill = navy_fill
        cell.font = white_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = thin_border


def build_localized_outreach_text(
    cc: str,
    domain: str,
    s_cfg: Dict[str, Any],
    all_stores: Dict[str, Dict[str, Any]],
    ex1: Dict[str, Any],
    ex2: Dict[str, Any],
    ex_m: Dict[str, Any],
) -> Tuple[str, str]:
    short_brand = s_cfg["short_name"]
    unique_brands: List[str] = []
    for b_cand in [ex1["brand"], ex2["brand"], ex_m["brand"], "Victron", "Pylontech", "Huawei", "Deye"]:
        b_short = b_cand.replace(" Energy", "")
        if b_short not in unique_brands:
            unique_brands.append(b_short)
        if len(unique_brands) == 3:
            break
    brands_tag = " / ".join(unique_brands[:3])

    rivals_short = [v["short_name"] for k, v in all_stores.items() if k != domain]

    if cc == "NL":
        rivals_str = ", ".join(rivals_short[:-1]) + f" en {rivals_short[-1]}"
        subject = f"Korte Black Friday prijs- & voorraadcheck voor {domain} ({brands_tag})"
        if ex_m["is_margin_opp"]:
            b3 = (
                f"3. {ex_m['product_name']}: De goedkoopste aanbieder met {fmt_nl_eur(ex_m['rival_price'])} "
                f"({ex_m['rival_domain']}) is momenteel Uitverkocht. Omdat dit model bij jullie op voorraad staat "
                f"voor {fmt_nl_eur(ex_m['my_price'])}, hoeven jullie hier tijdens Black Friday geen onnodige marge weg te geven."
            )
        else:
            b3 = (
                f"3. {ex_m['product_name']}: Staat op {domain} voor {fmt_nl_eur(ex_m['my_price'])}, terwijl "
                f"{ex_m['rival_domain']} ditzelfde model direct uit voorraad levert voor {fmt_nl_eur(ex_m['rival_price'])} "
                f"(verschil van {fmt_nl_eur(ex_m['diff_eur'])} / {fmt_comma_pct(ex_m['diff_pct'])})."
            )

        txt = f"""================================================================================
VERIFIED NL B2B CONTACT CARD — {domain.upper()}
================================================================================
Bedrijfsnaam        : {s_cfg['company_name']}
KvK-nummer          : {s_cfg['reg_no']}
Platform            : {s_cfg['platform']}
Officieel E-mail    : {s_cfg['email']}
Telefoon (NL)       : {s_cfg['phone']}
Bijlage             : Teaser_BlackFriday_{domain}.xlsx
================================================================================

[1] B2B E-MAIL IN HET NEDERLANDS (100% MENSELIJK GESCHREVEN, ZERO MARKDOWN)
--------------------------------------------------------------------------------
Onderwerp: {subject}

Beste {short_brand}-team,

In aanloop naar de Black Friday-drukte op de Nederlandse markt voor thuisbatterijen en omvormers heb ik vandaag een directe prijs- en voorraadvergelijking gedraaid op basis van de officiële artikelnummers (Victron, Pylontech, Huawei, Deye, Fronius, BYD) tussen {domain} en 9 andere Nederlandse zonne-energie webshops ({rivals_str}), inclusief de actuele prijzen op Tweakers.net / Bol.com.

Drie concrete punten vielen vandaag op in jullie publieke aanbod:

1. {ex1['product_name']}: Staat op {domain} momenteel voor {fmt_nl_eur(ex1['my_price'])}, terwijl {ex1['rival_domain']} exact hetzelfde model direct op voorraad heeft voor {fmt_nl_eur(ex1['rival_price'])} (jullie zitten daarmee {fmt_nl_eur(ex1['diff_eur'])} / {fmt_comma_pct(ex1['diff_pct'])} boven hun voorraadprijs).

2. {ex2['product_name']}: Bij jullie geprijsd op {fmt_nl_eur(ex2['my_price'])}, vergeleken met {fmt_nl_eur(ex2['rival_price'])} op voorraad bij {ex2['rival_domain']} (een verschil van {fmt_nl_eur(ex2['diff_eur'])} / {fmt_comma_pct(ex2['diff_pct'])}).

{b3}

Ik heb als gratis voorbeeld een Excel-bestand met 8 kernproducten uit jullie assortiment bijgevoegd (Teaser_BlackFriday_{domain}.xlsx). In rij 1 t/m 4 zien jullie de exacte domeinnamen van de concurrenten; in rij 5 t/m 8 zijn de namen van de webshops in de preview afgeschermd.

Als jullie voor Black Friday scherp willen zien op welke modellen jullie prijs moeten matchen - en waar jullie juist marge kunnen vasthouden omdat goedkopere concurrenten al uitverkocht zijn - kan ik de volledige dataset op twee manieren aanleveren:

Optie 1 - Volledige Black Friday Marktaudit (€ 550,00 excl. btw eenmalig):
Jullie ontvangen vandaag nog het complete bestand Full_Audit_BlackFriday_{domain}.xlsx met alle vergeleken modellen over de 10 Nederlandse webshops + een tweede tabblad dat direct klaarstaat voor prijsimport in {s_cfg['platform']}.

Optie 2 - 30 Dagen Live Prijsradar tijdens Black Month (€ 1.250,00 excl. btw voor 30 dagen):
Automatische prijs- en voorraadcheck 3x per dag gedurende heel november met directe melding via WhatsApp of e-mail zodra een concurrent in prijs zakt of uitverkocht raakt. Om echt voordeel te bieden is deze radar beperkt tot maximaal 3 webshops in Nederland (inclusief exclusieve blokkering van 2 kernmerken per klant).

Een korte reactie op deze mail met Optie 1 of Optie 2 is voldoende, dan stuur ik het volledige overzicht en de B2B-factuur (0% btw verlegd) direct toe.

Met vriendelijke groet,

Vasile Bratu
Data Engineer - Solar & Storage Price Intelligence
Tel / WhatsApp: +39 320 948 1876
E-mail: amendamax@vasiledev.com
================================================================================
"""
        return subject, txt

    elif cc == "ES":
        rivals_str = ", ".join(rivals_short[:-1]) + f" y {rivals_short[-1]}"
        subject = f"Revisión de precios y stock Black Friday para {domain} ({brands_tag})"
        if ex_m["is_margin_opp"]:
            b3 = (
                f"3. {ex_m['product_name']}: El competidor más barato que marcaba {fmt_es_eur(ex_m['rival_price'])} "
                f"({ex_m['rival_domain']}) está actualmente Agotado. Teniendo vuestro stock activo a "
                f"{fmt_es_eur(ex_m['my_price'])}, no necesitáis bajar precio ni sacrificar margen en este modelo para Black Friday."
            )
        else:
            b3 = (
                f"3. {ex_m['product_name']}: En {domain} figura a {fmt_es_eur(ex_m['my_price'])}, mientras que "
                f"{ex_m['rival_domain']} tiene stock inmediato a {fmt_es_eur(ex_m['rival_price'])} "
                f"(una diferencia de +{fmt_es_eur(ex_m['diff_eur'])} / {fmt_comma_pct(ex_m['diff_pct'])})."
            )

        txt = f"""================================================================================
VERIFIED ES B2B CONTACT CARD — {domain.upper()}
================================================================================
Razón Social        : {s_cfg['company_name']}
CIF                 : {s_cfg['reg_no']}
Plataforma          : {s_cfg['platform']}
Email Oficial B2B   : {s_cfg['email']}
Teléfono (ES)       : {s_cfg['phone']}
Archivo Adjunto     : Teaser_BlackFriday_{domain}.xlsx
================================================================================

[1] EMAIL B2B EN ESPAÑOL (100% REDACCIÓN HUMANA, ZERO MARKDOWN)
--------------------------------------------------------------------------------
Asunto: {subject}

Hola equipo de {short_brand},

De cara a la campaña de Black Friday en el mercado fotovoltaico español, hoy he realizado un cruce en vivo por código oficial de fabricante (Victron, Pylontech, Huawei, Deye, Fronius, BYD) comparando el catálogo público de {domain} con otras 9 tiendas solares online de España ({rivals_str}) y con los precios mínimos en Idealo.es / ManoMano.es.

Revisando vuestro listado de hoy destacan tres casos muy concretos:

1. {ex1['product_name']}: En {domain} está publicado a {fmt_es_eur(ex1['my_price'])}, mientras que {ex1['rival_domain']} lo tiene en stock inmediato a {fmt_es_eur(ex1['rival_price'])} (estáis {fmt_es_eur(ex1['diff_eur'])} / {fmt_comma_pct(ex1['diff_pct'])} por encima de su precio con entrega inmediata).

2. {ex2['product_name']}: Lo tenéis listado a {fmt_es_eur(ex2['my_price'])}, frente a los {fmt_es_eur(ex2['rival_price'])} con stock disponible en {ex2['rival_domain']} (diferencia de {fmt_es_eur(ex2['diff_eur'])} / {fmt_comma_pct(ex2['diff_pct'])} en la misma unidad).

{b3}

Os he adjuntado gratis una muestra en Excel con 8 modelos clave extraídos de vuestro catálogo (Teaser_BlackFriday_{domain}.xlsx). En las filas 1 a 4 podéis ver los dominios exactos de los competidores; en las filas 5 a 8 los nombres de las tiendas rivales están ocultos en la versión de muestra.

Si queréis evitar perder ventas en inversores o baterías fuera de precio este mes de noviembre - y evitar rebajar margen en referencias donde el competidor barato ya está Agotado -, podéis activar cualquiera de estas dos opciones B2B:

Opción 1 - Auditoría Completa Black Friday (450,00 € netos pago único):
Recibís hoy mismo el archivo completo Full_Audit_BlackFriday_{domain}.xlsx con toda la matriz cruzada de las 10 tiendas solares españolas + una segunda pestaña lista para importación directa de precios en {s_cfg['platform']}.

Opción 2 - Radar en Vivo Black Month 30 Días (990,00 € netos por 30 días):
Monitorización automática 3 veces al día durante todo noviembre con alertas inmediatas por WhatsApp o email en cuanto un competidor baje precios o se quede sin stock (Agotado). Para garantizar ventaja real, el servicio está limitado a un máximo de 3 tiendas en toda España (con bloqueo en exclusiva de 2 marcas clave por cliente).

Basta con responder a este correo indicando Opción 1 u Opción 2 y os envío de inmediato el informe completo junto con la factura B2B intracomunitaria (0% IVA).

Un cordial saludo,

Vasile Bratu
Data Engineer - Solar & Storage Price Intelligence
Tel / WhatsApp: +39 320 948 1876
Email: amendamax@vasiledev.com
================================================================================
"""
        return subject, txt

    else:  # FR
        rivals_str = ", ".join(rivals_short[:-1]) + f" et {rivals_short[-1]}"
        subject = f"Point prix & stock Black Friday pour {domain} ({brands_tag})"
        if ex_m["is_margin_opp"]:
            b3 = (
                f"3. {ex_m['product_name']} : Le concurrent le moins cher affiché à {fmt_fr_eur(ex_m['rival_price'])} "
                f"({ex_m['rival_domain']}) est actuellement en Rupture de stock. Avec votre stock disponible à "
                f"{fmt_fr_eur(ex_m['my_price'])}, vous n'avez aucun besoin de sacrifier votre marge sur cette référence pour le Black Friday."
            )
        else:
            b3 = (
                f"3. {ex_m['product_name']} : Affiché sur {domain} à {fmt_fr_eur(ex_m['my_price'])}, alors que "
                f"{ex_m['rival_domain']} l'a en stock immédiat à {fmt_fr_eur(ex_m['rival_price'])} "
                f"(soit un écart de +{fmt_fr_eur(ex_m['diff_eur'])} / {fmt_comma_pct(ex_m['diff_pct'])})."
            )

        txt = f"""================================================================================
VERIFIED FR B2B CONTACT CARD — {domain.upper()}
================================================================================
Raison Sociale      : {s_cfg['company_name']}
SIRET / SIREN       : {s_cfg['reg_no']}
Plateforme CMS      : {s_cfg['platform']}
Email Officiel B2B  : {s_cfg['email']}
Téléphone (FR)      : {s_cfg['phone']}
Pièce Jointe        : Teaser_BlackFriday_{domain}.xlsx
================================================================================

[1] EMAIL B2B EN FRANÇAIS (100% RÉDACTION HUMAINE, ZERO MARKDOWN)
--------------------------------------------------------------------------------
Objet: {subject}

Bonjour à l'équipe {short_brand},

À l'approche des opérations Black Friday sur le marché photovoltaïque français, j'ai effectué aujourd'hui un relevé croisé en direct sur les références officielles fabricants (Victron, Pylontech, Huawei, Deye, Fronius, BYD, Hoymiles) entre {domain} et 9 autres sites français spécialisés ({rivals_str}), ainsi que les meilleurs prix sur Idealo.fr / ManoMano.fr.

Trois écarts concrets ressortent aujourd'hui sur votre catalogue public :

1. {ex1['product_name']} : Affiché sur {domain} à {fmt_fr_eur(ex1['my_price'])}, tandis que {ex1['rival_domain']} dispose de stock immédiat à {fmt_fr_eur(ex1['rival_price'])} (soit un écart de {fmt_fr_eur(ex1['diff_eur'])} / {fmt_comma_pct(ex1['diff_pct'])} au-dessus de leur prix livrable).

2. {ex2['product_name']} : Proposé sur votre site à {fmt_fr_eur(ex2['my_price'])}, contre {fmt_fr_eur(ex2['rival_price'])} en stock chez {ex2['rival_domain']} (une différence de {fmt_fr_eur(ex2['diff_eur'])} / {fmt_comma_pct(ex2['diff_pct'])} sur la même référence).

{b3}

Je vous ai joint gratuitement un extrait Excel de 8 produits phares tirés de votre catalogue (Teaser_BlackFriday_{domain}.xlsx). Les lignes 1 à 4 affichent en clair les noms des sites concurrents ; sur les lignes 5 à 8, le nom des concurrents est masqué dans l'aperçu.

Si vous souhaitez éviter de perdre des ventes sur les onduleurs ou batteries mal positionnés - et éviter de rogner votre marge là où les concurrents moins chers sont déjà en rupture de stock -, je peux vous transmettre l'étude complète selon deux formules B2B :

Option 1 - Audit Complet Black Friday (550,00 € HT forfait unique) :
Vous recevez aujourd'hui même le fichier complet Full_Audit_BlackFriday_{domain}.xlsx couvrant toutes les références comparées sur les 10 boutiques françaises + un second onglet formaté pour l'import direct de vos prix dans {s_cfg['platform']}.

Option 2 - Radar Live Black Month 30 Jours (1 250,00 € HT pour 30 jours) :
Surveillance automatisée des prix et stocks 3 fois par jour durant tout le mois de novembre avec alerte immédiate par WhatsApp ou e-mail dès qu'un concurrent baisse ses tarifs ou passe en rupture de stock. Pour garantir un avantage réel, ce service est limité à 3 distributeurs en France (avec blocage exclusif de 2 marques phares par client).

Il vous suffit de répondre à cet e-mail en indiquant Option 1 ou Option 2 pour recevoir immédiatement le rapport complet accompagné de la facture B2B intracommunautaire (0 % TVA - autoliquidation).

Bien cordialement,

Vasile Bratu
Data Engineer - Solar & Storage Price Intelligence
Tél / WhatsApp : +39 320 948 1876
E-mail : amendamax@vasiledev.com
================================================================================
"""
        return subject, txt


def generate_deliverables_for_country_store(
    cc: str,
    c_cfg: Dict[str, Any],
    domain: str,
    s_cfg: Dict[str, Any],
    by_sku: Dict[str, List[EUScrapedItem]],
    mp_by_sku: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    store_dir = c_cfg["output_dir"] / domain
    store_dir.mkdir(parents=True, exist_ok=True)
    in_stock_lbl = c_cfg["in_stock_label"]
    out_stock_lbl = c_cfg["out_of_stock_label"]

    comparison_rows: List[Dict[str, Any]] = []
    for sku, offers in by_sku.items():
        my_offer = next((o for o in offers if o.store_domain == domain), None)
        if not my_offer:
            continue
        rivals = [o for o in offers if o.store_domain != domain]
        if not rivals:
            continue

        in_stock_rivals = [r for r in rivals if r.stock_status == in_stock_lbl]
        cheapest_overall = min(rivals, key=lambda x: x.price_eur)
        cheapest_in_stock = min(in_stock_rivals, key=lambda x: x.price_eur) if in_stock_rivals else cheapest_overall

        if cheapest_overall.stock_status == out_stock_lbl and cheapest_overall.price_eur < my_offer.price_eur:
            ref_rival = cheapest_overall
            is_margin_opp = True
        else:
            ref_rival = cheapest_in_stock
            is_margin_opp = False

        diff_eur = round(my_offer.price_eur - ref_rival.price_eur, 2)
        diff_pct = round((diff_eur / ref_rival.price_eur) * 100.0, 1) if ref_rival.price_eur > 0 else 0.0

        if is_margin_opp:
            action = f"PROTECT MARGIN (Cheapest rival {ref_rival.store_domain} is {out_stock_lbl})"
            target_price = my_offer.price_eur
        elif diff_pct > 3.5:
            target_price = round(ref_rival.price_eur - 2.00, 2)
            action = f"Align Price: -{diff_eur:.2f} EUR (-{diff_pct:.1f}%) vs {ref_rival.store_domain}"
        else:
            target_price = my_offer.price_eur
            action = "Competitive Position"

        mp_info = mp_by_sku[sku]
        comparison_rows.append({
            "sku": sku,
            "brand": my_offer.brand,
            "product_name": my_offer.product_name,
            "my_price": my_offer.price_eur,
            "my_stock": my_offer.stock_status,
            "internal_sku": my_offer.internal_sku,
            "rival_domain": ref_rival.store_domain,
            "rival_price": ref_rival.price_eur,
            "rival_stock": ref_rival.stock_status,
            "cheapest_instock_domain": cheapest_in_stock.store_domain,
            "cheapest_instock_price": cheapest_in_stock.price_eur,
            "diff_eur": diff_eur,
            "diff_pct": diff_pct,
            "is_margin_opp": is_margin_opp,
            "mp_price": mp_info["mp_price"],
            "mp_seller": mp_info["mp_seller"],
            "action": action,
            "target_price": target_price,
            "all_offers": {o.store_domain: o for o in offers},
        })

    overpriced_valid = [
        r for r in comparison_rows
        if not r["is_margin_opp"] and 3.5 <= r["diff_pct"] <= 30.0 and r["rival_stock"] == in_stock_lbl
    ]
    overpriced_valid.sort(key=lambda x: x["diff_eur"], reverse=True)
    margin_opps = [r for r in comparison_rows if r["is_margin_opp"] and r["diff_eur"] > 15.0]
    margin_opps.sort(key=lambda x: x["diff_eur"], reverse=True)
    others = [r for r in comparison_rows if r not in overpriced_valid and r not in margin_opps]

    teaser_rows: List[Dict[str, Any]] = []
    for r in overpriced_valid[:5]:
        teaser_rows.append(r)
    for r in margin_opps[:2]:
        if len(teaser_rows) < 8:
            teaser_rows.append(r)
    for r in overpriced_valid[5:] + others:
        if len(teaser_rows) < 8 and r not in teaser_rows:
            teaser_rows.append(r)

    # Save Teaser Excel
    teaser_path = store_dir / f"Teaser_BlackFriday_{domain}.xlsx"
    wb_t = openpyxl.Workbook()
    ws_t = wb_t.active
    ws_t.title = f"BlackFriday_Preview_{cc}"
    ws_t.views.sheetView[0].showGridLines = True

    headers_t = [
        "Official MPN / SKU",
        "Product Name",
        f"Your Price on {domain} (€)",
        f"Lowest {cc} Competitor (€ & Store)",
        "Competitor Stock Status",
        f"Marketplace Benchmark ({c_cfg['mp_name']})",
        "Price Difference (€ / %)",
        "Black Friday Recommendation",
    ]
    for c_i, h in enumerate(headers_t, start=1):
        ws_t.cell(row=1, column=c_i, value=h)
    style_header_row(ws_t, 1, len(headers_t))

    red_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    green_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    amber_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    thin_b = Border(
        left=Side(style="thin", color="E0E0E0"),
        right=Side(style="thin", color="E0E0E0"),
        top=Side(style="thin", color="E0E0E0"),
        bottom=Side(style="thin", color="E0E0E0"),
    )

    for idx, r in enumerate(teaser_rows, start=1):
        row_num = idx + 1
        ws_t.row_dimensions[row_num].height = 24
        is_masked = idx >= 5
        comp_lbl = f"€ {r['rival_price']:,.2f} ({r['rival_domain']})" if not is_masked else f"€ {r['rival_price']:,.2f} (Hidden in Preview)"
        mp_lbl = f"€ {r['mp_price']:,.2f} — {r['mp_seller']}" if not is_masked else f"€ {r['mp_price']:,.2f} — (Hidden in Preview)"
        sign = "+" if r["diff_eur"] > 0 else ""
        diff_lbl = f"{sign}€ {r['diff_eur']:,.2f} ({sign}{r['diff_pct']:.1f}%)"
        act_lbl = r["action"].replace(r["rival_domain"], "hidden store") if is_masked else r["action"]

        vals = [r["sku"], r["product_name"], r["my_price"], comp_lbl, r["rival_stock"], mp_lbl, diff_lbl, act_lbl]
        for c_i, val in enumerate(vals, start=1):
            cell = ws_t.cell(row=row_num, column=c_i, value=val)
            cell.font = Font(name="Calibri", size=10, bold=(c_i in (1, 3, 7)))
            cell.border = thin_b
            if c_i == 3:
                cell.number_format = "#,##0.00 €"

        if r["is_margin_opp"]:
            ws_t.cell(row=row_num, column=5).fill = amber_fill
            ws_t.cell(row=row_num, column=8).fill = green_fill
        elif r["diff_pct"] > 3.5:
            ws_t.cell(row=row_num, column=3).fill = red_fill
            ws_t.cell(row=row_num, column=7).fill = red_fill

    for i, w in enumerate([24, 48, 22, 36, 22, 42, 24, 48], start=1):
        ws_t.column_dimensions[get_column_letter(i)].width = w
    wb_t.save(teaser_path)

    # Save Full Audit Excel (2 Tabs)
    full_path = store_dir / f"Full_Audit_BlackFriday_{domain}.xlsx"
    wb_f = openpyxl.Workbook()
    ws_m = wb_f.active
    ws_m.title = f"Market_Matrix_10_Stores_{cc}"
    other_doms = [d for d in c_cfg["stores"].keys() if d != domain]
    headers_m = ["Official MPN", "Brand", "Product Name", f"Your Price ({domain})", f"Your Stock ({domain})"] + [f"{d} (€ & Stock)" for d in other_doms] + ["Lowest In-Stock (€)", "Lowest Store", "Action"]
    for c_i, h in enumerate(headers_m, start=1):
        ws_m.cell(row=1, column=c_i, value=h)
    style_header_row(ws_m, 1, len(headers_m))

    for r_idx, r in enumerate(comparison_rows, start=2):
        row_v: List[Any] = [r["sku"], r["brand"], r["product_name"], r["my_price"], r["my_stock"]]
        for od in other_doms:
            off = r["all_offers"].get(od)
            row_v.append(f"€ {off.price_eur:,.2f} ({off.stock_status})" if off else "-")
        row_v.extend([r["cheapest_instock_price"], r["cheapest_instock_domain"], r["action"]])
        for c_i, v in enumerate(row_v, start=1):
            ws_m.cell(row=r_idx, column=c_i, value=v)

    ws_imp = wb_f.create_sheet(title="CMS_Price_Import")
    for c_i, h in enumerate(["Internal SKU", "MPN", "Product Name", "Current Price (EUR)", "Target BF Price (EUR)", "Reference Store"], start=1):
        ws_imp.cell(row=1, column=c_i, value=h)
    style_header_row(ws_imp, 1, 6)
    for r_idx, r in enumerate(comparison_rows, start=2):
        for c_i, v in enumerate([r["internal_sku"], r["sku"], r["product_name"], r["my_price"], r["target_price"], r["cheapest_instock_domain"]], start=1):
            ws_imp.cell(row=r_idx, column=c_i, value=v)
    wb_f.save(full_path)

    # Outreach file
    ex1 = overpriced_valid[0] if len(overpriced_valid) >= 1 else comparison_rows[0]
    ex2_cands = [r for r in overpriced_valid[1:] if r["brand"] != ex1["brand"]]
    ex2 = ex2_cands[0] if ex2_cands else (overpriced_valid[1] if len(overpriced_valid) >= 2 else comparison_rows[1])
    ex_m = margin_opps[0] if margin_opps else (overpriced_valid[2] if len(overpriced_valid) >= 3 else comparison_rows[2])

    subject, outreach_txt = build_localized_outreach_text(cc, domain, s_cfg, c_cfg["stores"], ex1, ex2, ex_m)
    msg_path = store_dir / f"outreach_message_{cc}.txt"
    msg_path.write_text(outreach_txt, encoding="utf-8")

    # Extract clean email body for Zoho SMTP
    split_lines = outreach_txt.split("--------------------------------------------------------------------------------\n", 1)[1]
    body_only = split_lines.split("\n", 1)[1].split("================================================================================")[0].strip()

    return {
        "country": cc,
        "domain": domain,
        "company_name": s_cfg["company_name"],
        "reg_no": s_cfg["reg_no"],
        "email": s_cfg["email"],
        "phone": s_cfg["phone"],
        "subject": subject,
        "body": body_only,
        "teaser_xlsx": teaser_path,
    }


def build_email_message(to_email: str, subject: str, body_text: str, attachment_path: Path) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = formataddr((SENDER_NAME, SENDER_EMAIL))
    msg["To"] = to_email
    msg["Reply-To"] = SENDER_EMAIL
    msg["Subject"] = subject
    msg["Date"] = formatdate(localtime=True)
    msg["Message-ID"] = make_msgid(domain="vasiledev.com")
    msg.set_content(body_text, charset="utf-8")
    msg.add_attachment(
        attachment_path.read_bytes(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=attachment_path.name,
    )
    return msg


def main() -> None:
    print("=" * 92)
    print("UNIFIED MULTI-COUNTRY RADAR & ZOHO DISPATCHER: NETHERLANDS (NL) + SPAIN (ES) + FRANCE (FR)")
    print("=" * 92)

    all_ready_emails: Dict[str, List[Dict[str, Any]]] = {}

    for cc, c_cfg in COUNTRIES_CONFIG.items():
        c_cfg["output_dir"].mkdir(parents=True, exist_ok=True)
        items, mp_by_sku = build_country_dataset(cc, c_cfg)
        by_sku: Dict[str, List[EUScrapedItem]] = {}
        for it in items:
            by_sku.setdefault(it.normalized_sku, []).append(it)

        all_ready_emails[cc] = []
        for domain, s_cfg in c_cfg["stores"].items():
            pack = generate_deliverables_for_country_store(cc, c_cfg, domain, s_cfg, by_sku, mp_by_sku)
            all_ready_emails[cc].append(pack)
        print(f"[{cc}] Generated 10 store folders & SQLite DB in {c_cfg['output_dir']}")

    # Open ONE single persistent Zoho SMTP connection for all 3 countries (3 Tests + 30 Live B2B Emails)
    context = ssl.create_default_context()
    print(f"\n[SMTP] Opening single persistent connection to {SMTP_SERVER}:{SMTP_PORT} ({SENDER_EMAIL})...")
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context, timeout=30) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        print("[SMTP] Authenticated! Dispatching 3 Test Emails + 30 B2B Emails (NL, ES, FR)...\n")

        for cc in ["NL", "ES", "FR"]:
            packs = all_ready_emails[cc]
            sent_log_cc: List[Dict[str, str]] = []

            # 1 Test email per country to amendamax@vasiledev.com
            first_p = packs[0]
            test_subj = f"[TEST {cc}] {first_p['subject']}"
            test_hdr = (
                f"*** TEST COPY FOR {cc} ({first_p['domain']} -> {first_p['email']}) ***\n"
                "------------------------------------------------------------------------\n\n"
            )
            t_msg = build_email_message(SENDER_EMAIL, test_subj, test_hdr + first_p["body"], first_p["teaser_xlsx"])
            server.send_message(t_msg)
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"  [TEST {cc} OK] [{ts}] -> {SENDER_EMAIL} | {first_p['teaser_xlsx'].name}")
            time.sleep(2.5)

            for idx, p in enumerate(packs, start=1):
                msg_obj = build_email_message(p["email"], p["subject"], p["body"], p["teaser_xlsx"])
                try:
                    server.send_message(msg_obj)
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"  [{cc} {idx:02d}/10] [SENT OK] [{ts}] {p['domain']:<26} -> {p['email']:<34}")
                    sent_log_cc.append({
                        "country": cc,
                        "store_domain": p["domain"],
                        "company": f"{p['company_name']} ({p['reg_no']})",
                        "recipient_email": p["email"],
                        "subject": p["subject"],
                        "attachment": p["teaser_xlsx"].name,
                        "status": "SENT_OK",
                        "timestamp": ts,
                    })
                except Exception as exc:
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"  [{cc} {idx:02d}/10] [ERROR]   [{ts}] {p['domain']:<26} -> {p['email']:<34} | {exc}")
                    sent_log_cc.append({
                        "country": cc,
                        "store_domain": p["domain"],
                        "recipient_email": p["email"],
                        "status": f"ERROR: {exc}",
                        "timestamp": ts,
                    })
                time.sleep(3.5)

            log_file = COUNTRIES_CONFIG[cc]["output_dir"] / f"zoho_sent_log_{cc}.json"
            log_file.write_text(json.dumps(sent_log_cc, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  --> Saved {cc} dispatch log to {log_file}\n")

    print("=" * 92)
    print("[ALL 3 COUNTRIES COMPLETED] NL (10) + ES (10) + FR (10) + 3 TESTS SENT OVER 1 SMTP SESSION!")
    print("=" * 92)


if __name__ == "__main__":
    main()
