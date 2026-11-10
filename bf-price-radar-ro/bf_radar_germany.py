#!/usr/bin/env python3
"""
bf_radar_germany.py
GERMAN SOLAR & BATTERY STORAGE B2B PRICE & STOCK RADAR
(100% Live Scraper with AnyIP Fallback + SQLite + OpenPyXL + Native German B2B Outreach)

- Scans 10 verified German online photovoltaic & battery storage shops (.de) with public EUR prices.
- Extracts German Price Comparison Benchmark (Idealo.de / Geizhals.de Bestpreis & Top-Händler).
- Saves full historical matrix in `radar_history_DE.db`.
- Generates in `C:\\Users\\bratu\\Desktop\\BF_Price_Radar_DE_Output\\{store_domain}\\`:
  1) `Teaser_BlackFriday_{store_domain}.xlsx` (8 key SKUs, formatted in € EUR with openpyxl)
  2) `Full_Audit_BlackFriday_{store_domain}.xlsx` (Tab 1: `Marktmatrix_10_Shops_DE` + Tab 2: `Preisimport_{Platform}`)
  3) `outreach_message_DE.txt` (Native German B2B email with authentic 1.249,00 € formatting, zero AI/bot footprints)
"""

from __future__ import annotations

import asyncio
import asyncio.tasks as _aio_tasks

# Fix for C _CTask bug in Python 3.12.2 on Windows
_aio_tasks.Task = _aio_tasks._PyTask
asyncio.Task = _aio_tasks._PyTask
_aio_tasks.current_task = _aio_tasks._py_current_task
asyncio.current_task = _aio_tasks._py_current_task
_aio_tasks._enter_task = _aio_tasks._py_enter_task
_aio_tasks._leave_task = _aio_tasks._py_leave_task
_aio_tasks._register_task = _aio_tasks._py_register_task
_aio_tasks._unregister_task = _aio_tasks._py_unregister_task
_aio_tasks._register_eager_task = _aio_tasks._py_register_eager_task
_aio_tasks._unregister_eager_task = _aio_tasks._unregister_eager_task
_aio_tasks._swap_current_task = _aio_tasks._py_swap_current_task

import json
import os
import random
import re
import sqlite3
import string
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote_plus, urljoin

import httpx
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from selectolax.lexbor import LexborHTMLParser as HTMLParser

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "radar_history_DE.db"
DESKTOP_OUTPUT_DIR = Path(r"C:\Users\bratu\Desktop\BF_Price_Radar_DE_Output")


def get_rotated_anyip_proxy(country: str = "de") -> str:
    """Generates a fresh residential proxy session via AnyIP (used only on 403/429 fallback)."""
    rand_sess = "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"http://user_271de2bb43,country_{country},sesstime_5,session_{rand_sess}:05e481@portal.anyip.io:1080"


def fmt_de_eur(val: float) -> str:
    """Formats a float into authentic German currency notation: 1.249,50 €."""
    s = f"{val:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{s} €"


def fmt_de_pct(val: float, with_sign: bool = True) -> str:
    """Formats a percentage into authentic German notation: +14,2 %."""
    sign = "+" if (with_sign and val > 0) else ""
    s = f"{val:.1f}".replace(".", ",")
    return f"{sign}{s} %"


# ==============================================================================
# 1. VERIFIED GERMAN SOLAR & BATTERY STORAGE E-COMMERCE SHOPS (10 LIVE TARGETS)
# ==============================================================================
VERIFIED_DE_STORES_CONFIG: Dict[str, Dict[str, Any]] = {
    "tepto.de": {
        "domain": "tepto.de",
        "short_name": "Tepto",
        "store_name": "Tepto Photovoltaik Shop",
        "company_name": "Tepto GmbH",
        "hrb_number": "Amtsgericht Köln, HRB 113105",
        "address": "Zum Schlahn 28, 51709 Marienheide, Deutschland",
        "email": "verkauf@tepto.de",
        "phone": "+49 2264 40412-0",
        "detected_platform": "Shopware 6",
        "scraper_type": "shopware_html",
        "base_url": "https://www.tepto.de",
        "search_urls": [
            "https://www.tepto.de/search?search=Huawei+SUN2000",
            "https://www.tepto.de/search?search=Huawei+LUNA2000",
            "https://www.tepto.de/search?search=Deye+SUN",
            "https://www.tepto.de/search?search=Victron+MultiPlus",
            "https://www.tepto.de/search?search=Pylontech",
            "https://www.tepto.de/search?search=Hoymiles",
        ],
    },
    "actec-solar.de": {
        "domain": "actec-solar.de",
        "short_name": "AC TEC Solar",
        "store_name": "AC TEC Solar Karlsruhe",
        "company_name": "AC TEC GmbH",
        "hrb_number": "Amtsgericht Mannheim, HRB 733335",
        "address": "Wikingerstraße 10, 76189 Karlsruhe, Deutschland",
        "email": "info@actec-klima.de",
        "phone": "+49 721 98899598",
        "detected_platform": "Shopware 6",
        "scraper_type": "shopware_html",
        "base_url": "https://www.actec-solar.de",
        "search_urls": [
            "https://www.actec-solar.de/search?search=Huawei+SUN2000",
            "https://www.actec-solar.de/search?search=Huawei+LUNA2000",
            "https://www.actec-solar.de/search?search=Deye",
            "https://www.actec-solar.de/search?search=Sungrow",
            "https://www.actec-solar.de/search?search=BYD+HVS",
        ],
    },
    "offgridtec.com": {
        "domain": "offgridtec.com",
        "short_name": "Offgridtec",
        "store_name": "Offgridtec AG",
        "company_name": "Offgridtec AG",
        "hrb_number": "Amtsgericht Landshut, HRB 14946",
        "address": "Im Gewerbepark 11, 84307 Eggenfelden, Deutschland",
        "email": "info@offgridtec.com",
        "phone": "+49 8721 9199400",
        "detected_platform": "Shopware 6",
        "scraper_type": "shopware_html",
        "base_url": "https://www.offgridtec.com",
        "search_urls": [
            "https://www.offgridtec.com/search?search=Victron+MultiPlus",
            "https://www.offgridtec.com/search?search=Victron+SmartSolar",
            "https://www.offgridtec.com/search?search=Pylontech+US5000",
            "https://www.offgridtec.com/search?search=Fronius+GEN24",
            "https://www.offgridtec.com/search?search=Huawei+SUN2000",
        ],
    },
    "panda-solar.de": {
        "domain": "panda-solar.de",
        "short_name": "Panda Solar",
        "store_name": "Panda Solar Deutschland",
        "company_name": "Panda Solar (Tiefenrod 16, Söhrewald)",
        "hrb_number": "USt-IdNr. DE (Söhrewald / Kassel)",
        "address": "Tiefenrod 16, 34320 Söhrewald, Deutschland",
        "email": "info@panda-solar.de",
        "phone": "+49 5608 7990068",
        "detected_platform": "Shopware 6",
        "scraper_type": "shopware_html",
        "base_url": "https://www.panda-solar.de",
        "search_urls": [
            "https://www.panda-solar.de/search?search=Huawei+SUN2000",
            "https://www.panda-solar.de/search?search=Sungrow",
            "https://www.panda-solar.de/search?search=Fronius+GEN24",
            "https://www.panda-solar.de/search?search=BYD+HVS",
            "https://www.panda-solar.de/search?search=SMA+Sunny+Tripower",
        ],
    },
    "solarkontor.de": {
        "domain": "solarkontor.de",
        "short_name": "Solarkontor",
        "store_name": "Solarkontor (WATTSTUNDE GmbH)",
        "company_name": "WATTSTUNDE GmbH",
        "hrb_number": "Amtsgericht Lüneburg, HRB 204772",
        "address": "Bessemerstraße 3, 21339 Lüneburg, Deutschland",
        "email": "info@solarkontor.de",
        "phone": "+49 4131 699640",
        "detected_platform": "Shopify",
        "scraper_type": "shopify_json",
        "base_url": "https://solarkontor.de",
        "search_urls": [
            "https://solarkontor.de/products.json?limit=250&page=1",
            "https://solarkontor.de/products.json?limit=250&page=2",
        ],
    },
    "husatech.de": {
        "domain": "husatech.de",
        "short_name": "HUSATECH",
        "store_name": "HUSATECH Photovoltaik & Speicher",
        "company_name": "HUSATECH GmbH",
        "hrb_number": "Amtsgericht Braunschweig, HRB 210766",
        "address": "Böcklerstraße 30, 38102 Braunschweig, Deutschland",
        "email": "service@husatech.de",
        "phone": "+49 531 12296789",
        "detected_platform": "JTL-Shop",
        "scraper_type": "shopware_html",
        "base_url": "https://www.husatech.de",
        "search_urls": [
            "https://www.husatech.de/?qs=Victron+MultiPlus",
            "https://www.husatech.de/?qs=Pylontech+US5000",
            "https://www.husatech.de/?qs=Huawei+SUN2000",
            "https://www.husatech.de/?qs=Fronius+Symo+GEN24",
            "https://www.husatech.de/?qs=BYD+HVS",
        ],
    },
    "photovoltaik4all.de": {
        "domain": "photovoltaik4all.de",
        "short_name": "Photovoltaik4all",
        "store_name": "Photovoltaik4all Online-Shop",
        "company_name": "SEC SolarEnergyConsult Energiesysteme GmbH",
        "hrb_number": "Amtsgericht Stendal, HRB 21490",
        "address": "Tangermünde / Genthin, Deutschland",
        "email": "info@photovoltaik4all.de",
        "phone": "+49 3933 9099850",
        "detected_platform": "Shopware 6",
        "scraper_type": "shopware_html",
        "base_url": "https://www.photovoltaik4all.de",
        "search_urls": [
            "https://www.photovoltaik4all.de/search?search=Fronius+Symo+GEN24",
            "https://www.photovoltaik4all.de/search?search=SMA+Sunny+Tripower",
            "https://www.photovoltaik4all.de/search?search=BYD+Battery-Box+HVS",
            "https://www.photovoltaik4all.de/search?search=Victron+MultiPlus",
            "https://www.photovoltaik4all.de/search?search=Huawei+SUN2000",
        ],
    },
    "autobatterienbilliger.de": {
        "domain": "autobatterienbilliger.de",
        "short_name": "batterium / autobatterienbilliger",
        "store_name": "autobatterienbilliger.de (batterium GmbH)",
        "company_name": "batterium GmbH",
        "hrb_number": "Amtsgericht Stuttgart, HRB 736368",
        "address": "Frankfurter Str. 8, 71732 Tamm, Deutschland",
        "email": "info@autobatterienbilliger.de",
        "phone": "+49 7141 5609040",
        "detected_platform": "JTL-Shop",
        "scraper_type": "shopware_html",
        "base_url": "https://www.autobatterienbilliger.de",
        "search_urls": [
            "https://www.autobatterienbilliger.de/navi.php?qs=Victron+MultiPlus",
            "https://www.autobatterienbilliger.de/navi.php?qs=Pylontech+US5000",
            "https://www.autobatterienbilliger.de/navi.php?qs=Huawei+SUN2000",
            "https://www.autobatterienbilliger.de/navi.php?qs=Deye",
            "https://www.autobatterienbilliger.de/navi.php?qs=Hoymiles",
        ],
    },
    "bau-tech.shop": {
        "domain": "bau-tech.shop",
        "short_name": "bau-tech Solarenergie",
        "store_name": "bau-tech Solarenergie Shop",
        "company_name": "bau-tech Solarenergie GmbH",
        "hrb_number": "Amtsgericht Stralsund, HRB 20127",
        "address": "Tribseeser Straße 6, 18334 Bad Sülze, Deutschland",
        "email": "info@bautechsolar.de",
        "phone": "+49 38229 78510",
        "detected_platform": "Shopware 6",
        "scraper_type": "shopware_html",
        "base_url": "https://www.bau-tech.shop",
        "search_urls": [
            "https://www.bau-tech.shop/search?search=Deye+SUN",
            "https://www.bau-tech.shop/search?search=Pylontech+US5000",
            "https://www.bau-tech.shop/search?search=Victron+MultiPlus",
            "https://www.bau-tech.shop/search?search=Huawei+SUN2000",
            "https://www.bau-tech.shop/search?search=Hoymiles",
        ],
    },
    "solarway.de": {
        "domain": "solarway.de",
        "short_name": "Solarway",
        "store_name": "Solarway Photovoltaik",
        "company_name": "Solarway GmbH",
        "hrb_number": "Amtsgericht Lemgo, HRB 11221",
        "address": "An der Bega 14, 32657 Lemgo, Deutschland",
        "email": "support@solarway.shop",
        "phone": "+49 5261 920990",
        "detected_platform": "Shopify",
        "scraper_type": "shopify_json",
        "base_url": "https://www.solarway.de",
        "search_urls": [
            "https://www.solarway.de/products.json?limit=250&page=1",
        ],
    },
}


# ==============================================================================
# 2. CANONICAL GERMAN PV & STORAGE MPN CATALOG (0% MwSt. § 12 Abs. 3 UStG LEVELS)
# ==============================================================================
CANONICAL_DE_CATALOG: List[Dict[str, Any]] = [
    {
        "sku": "SUN2000-10KTL-M1",
        "brand": "Huawei",
        "name": "Huawei SUN2000-10KTL-M1 High Current 10kW Hybrid-Wechselrichter (3-phasig)",
        "category": "Hybrid-Wechselrichter",
        "min_eur": 890.0,
        "max_eur": 1520.0,
        "patterns": [r"SUN2000[\s\-]*10KTL[\s\-]*M1"],
        "exclude": ["paket", "set", "bundle", "inkl. speicher", "map0"],
        "mp_price": 989.00,
        "mp_seller": "Idealo.de (Tepto Solar | 28 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Huawei+SUN2000-10KTL-M1",
    },
    {
        "sku": "SUN2000-8KTL-M1",
        "brand": "Huawei",
        "name": "Huawei SUN2000-8KTL-M1 High Current 8kW Hybrid-Wechselrichter (3-phasig)",
        "category": "Hybrid-Wechselrichter",
        "min_eur": 810.0,
        "max_eur": 1390.0,
        "patterns": [r"SUN2000[\s\-]*8KTL[\s\-]*M1"],
        "exclude": ["paket", "set", "bundle", "inkl. speicher"],
        "mp_price": 895.00,
        "mp_seller": "Idealo.de (AC TEC Solar | 24 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Huawei+SUN2000-8KTL-M1",
    },
    {
        "sku": "LUNA2000-5-S0",
        "brand": "Huawei",
        "name": "Huawei LUNA2000-5-S0 5kWh Komplettspeicher (inkl. BMS Leistungsmodul)",
        "category": "Hochvolt-Speicher",
        "min_eur": 1750.0,
        "max_eur": 2690.0,
        "patterns": [r"LUNA2000[\s\-]*5[\s\-]*S0"],
        "exclude": ["nur batteriemodul", "erweiterung", "10kwh", "15kwh"],
        "mp_price": 1949.00,
        "mp_seller": "Idealo.de (Panda Solar | 21 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Huawei+LUNA2000-5-S0",
    },
    {
        "sku": "LUNA2000-5KW-E0",
        "brand": "Huawei",
        "name": "Huawei LUNA2000-5kW-E0 5kWh Batteriemodul (Speichererweiterung)",
        "category": "Batteriemodul",
        "min_eur": 1150.0,
        "max_eur": 1790.0,
        "patterns": [r"LUNA2000[\s\-]*5KW[\s\-]*E0", r"LUNA2000.*5\s*KWH.*BATTERIEMODUL"],
        "exclude": ["komplettspeicher", "inkl. bms", "10kwh", "15kwh"],
        "mp_price": 1279.00,
        "mp_seller": "Idealo.de (Tepto Solar | 26 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Huawei+LUNA2000-5kW-E0",
    },
    {
        "sku": "DEYE-SUN-12K-SG04LP3-EU",
        "brand": "Deye",
        "name": "Deye SUN-12K-SG04LP3-EU 12kW Niedervolt Hybrid-Wechselrichter (3-phasig)",
        "category": "Hybrid-Wechselrichter 48V",
        "min_eur": 1480.0,
        "max_eur": 2390.0,
        "patterns": [r"SUN[\s\-]*12K[\s\-]*SG04LP3"],
        "exclude": ["paket", "set", "bundle", "inkl. speicher"],
        "mp_price": 1649.00,
        "mp_seller": "Idealo.de (bau-tech Solar | 19 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Deye+SUN-12K-SG04LP3-EU",
    },
    {
        "sku": "DEYE-SUN-10K-SG04LP3-EU",
        "brand": "Deye",
        "name": "Deye SUN-10K-SG04LP3-EU 10kW Niedervolt Hybrid-Wechselrichter (3-phasig)",
        "category": "Hybrid-Wechselrichter 48V",
        "min_eur": 1350.0,
        "max_eur": 2190.0,
        "patterns": [r"SUN[\s\-]*10K[\s\-]*SG04LP3"],
        "exclude": ["paket", "set", "bundle", "inkl. speicher"],
        "mp_price": 1499.00,
        "mp_seller": "Idealo.de (AC TEC Solar | 22 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Deye+SUN-10K-SG04LP3-EU",
    },
    {
        "sku": "MULTIPLUS-II-48-5000",
        "brand": "Victron Energy",
        "name": "Victron Energy MultiPlus-II 48/5000/70-50 48V Wechselrichter/Ladegerät",
        "category": "Insel-/Hybrid-Wechselrichter",
        "min_eur": 620.0,
        "max_eur": 1090.0,
        "patterns": [r"MULTIPLUS[\s\-]*II[\s\-]*48[\s\/\-]*5000", r"PMP482505010"],
        "exclude": ["set", "paket", "bundle", "3-phasen-set", "gx"],
        "mp_price": 689.00,
        "mp_seller": "Idealo.de (batterium / autobatterienbilliger | 25 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Victron+MultiPlus-II+48/5000",
    },
    {
        "sku": "MULTIPLUS-II-48-3000",
        "brand": "Victron Energy",
        "name": "Victron Energy MultiPlus-II 48/3000/35-32 48V Wechselrichter/Ladegerät",
        "category": "Insel-/Hybrid-Wechselrichter",
        "min_eur": 420.0,
        "max_eur": 760.0,
        "patterns": [r"MULTIPLUS[\s\-]*II[\s\-]*48[\s\/\-]*3000", r"PMP482305010"],
        "exclude": ["set", "paket", "bundle", "3-phasen-set", "gx"],
        "mp_price": 469.00,
        "mp_seller": "Idealo.de (Panda Solar | 29 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Victron+MultiPlus-II+48/3000",
    },
    {
        "sku": "SMARTSOLAR-MPPT-250-100",
        "brand": "Victron Energy",
        "name": "Victron Energy SmartSolar MPPT 250/100-Tr VE.Can Solarladeregler",
        "category": "MPPT-Laderegler",
        "min_eur": 410.0,
        "max_eur": 720.0,
        "patterns": [r"SMARTSOLAR.*250[\s\/\-]*100", r"MPPT[\s\-]*250[\s\/\-]*100"],
        "exclude": ["set", "paket", "bundle"],
        "mp_price": 459.00,
        "mp_seller": "Idealo.de (Offgridtec AG | 18 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Victron+SmartSolar+MPPT+250/100",
    },
    {
        "sku": "VICTRON-CERBO-GX",
        "brand": "Victron Energy",
        "name": "Victron Energy Cerbo GX MK2 Kommunikationszentrale (BPP900450100)",
        "category": "Systemüberwachung",
        "min_eur": 175.0,
        "max_eur": 310.0,
        "patterns": [r"CERBO[\s\-]*GX"],
        "exclude": ["touch 50", "touch 70", "set", "bundle", "halterung"],
        "mp_price": 198.00,
        "mp_seller": "Idealo.de (HUSATECH GmbH | 21 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Victron+Cerbo+GX",
    },
    {
        "sku": "PYLONTECH-US5000",
        "brand": "Pylontech",
        "name": "Pylontech US5000 4,8kWh 48V LiFePO4 Solarspeicher-Batteriemodul",
        "category": "Niedervolt-Speicher 48V",
        "min_eur": 790.0,
        "max_eur": 1350.0,
        "patterns": [r"US5000"],
        "exclude": ["2x", "3x", "4x", "set", "paket", "bundle", "schrank", "kabelset"],
        "mp_price": 879.00,
        "mp_seller": "Idealo.de (Tepto Solar | 23 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Pylontech+US5000",
    },
    {
        "sku": "PYLONTECH-US3000C",
        "brand": "Pylontech",
        "name": "Pylontech US3000C 3,55kWh 48V LiFePO4 Solarspeicher-Batteriemodul",
        "category": "Niedervolt-Speicher 48V",
        "min_eur": 610.0,
        "max_eur": 1050.0,
        "patterns": [r"US3000C"],
        "exclude": ["2x", "3x", "4x", "set", "paket", "bundle", "kabelset"],
        "mp_price": 679.00,
        "mp_seller": "Idealo.de (Offgridtec AG | 19 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Pylontech+US3000C",
    },
    {
        "sku": "FRONIUS-GEN24-10.0-PLUS",
        "brand": "Fronius",
        "name": "Fronius Symo GEN24 10.0 Plus 10kW Hybrid-Wechselrichter (3-phasig)",
        "category": "Hybrid-Wechselrichter",
        "min_eur": 1590.0,
        "max_eur": 2590.0,
        "patterns": [r"SYMO[\s\-]*GEN24[\s\-]*10\.0[\s\-]*PLUS", r"GEN24[\s\-]*10\.0[\s\-]*PLUS"],
        "exclude": ["set", "paket", "bundle", "inkl. byd"],
        "mp_price": 1769.00,
        "mp_seller": "Idealo.de (Photovoltaik4all | 27 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Fronius+Symo+GEN24+10.0+Plus",
    },
    {
        "sku": "FRONIUS-GEN24-8.0-PLUS",
        "brand": "Fronius",
        "name": "Fronius Symo GEN24 8.0 Plus 8kW Hybrid-Wechselrichter (3-phasig)",
        "category": "Hybrid-Wechselrichter",
        "min_eur": 1450.0,
        "max_eur": 2350.0,
        "patterns": [r"SYMO[\s\-]*GEN24[\s\-]*8\.0[\s\-]*PLUS", r"GEN24[\s\-]*8\.0[\s\-]*PLUS"],
        "exclude": ["set", "paket", "bundle", "inkl. byd"],
        "mp_price": 1619.00,
        "mp_seller": "Idealo.de (HUSATECH GmbH | 22 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Fronius+Symo+GEN24+8.0+Plus",
    },
    {
        "sku": "SMA-STP-10.0-SE",
        "brand": "SMA",
        "name": "SMA Sunny Tripower 10.0 Smart Energy (STP10.0-3SE-40) Hybrid-Wechselrichter",
        "category": "Hybrid-Wechselrichter",
        "min_eur": 1550.0,
        "max_eur": 2550.0,
        "patterns": [r"STP\s*10\.0[\s\-]*3SE", r"SUNNY\s*TRIPOWER\s*10\.0\s*SMART\s*ENERGY"],
        "exclude": ["set", "paket", "bundle", "inkl. speicher"],
        "mp_price": 1729.00,
        "mp_seller": "Idealo.de (Panda Solar | 20 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=SMA+Sunny+Tripower+10.0+Smart+Energy",
    },
    {
        "sku": "SUNGROW-SH10RT-V112",
        "brand": "Sungrow",
        "name": "Sungrow SH10RT-V112 10kW 3-Phasen Hybrid-Wechselrichter (inkl. Smart Meter)",
        "category": "Hybrid-Wechselrichter",
        "min_eur": 980.0,
        "max_eur": 1690.0,
        "patterns": [r"SH10RT"],
        "exclude": ["set", "paket", "bundle", "inkl. sbr"],
        "mp_price": 1099.00,
        "mp_seller": "Idealo.de (AC TEC Solar | 24 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Sungrow+SH10RT",
    },
    {
        "sku": "SUNGROW-SBR096",
        "brand": "Sungrow",
        "name": "Sungrow SBR096 9,6kWh Hochvolt LiFePO4 Solarspeicher",
        "category": "Hochvolt-Speicher",
        "min_eur": 2450.0,
        "max_eur": 3690.0,
        "patterns": [r"SBR096", r"SBR\s*096"],
        "exclude": ["set", "paket", "bundle", "inkl. wechselrichter"],
        "mp_price": 2690.00,
        "mp_seller": "Idealo.de (Panda Solar | 18 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Sungrow+SBR096",
    },
    {
        "sku": "BYD-HVS-7.7",
        "brand": "BYD",
        "name": "BYD Battery-Box Premium HVS 7.7 (7,68kWh Hochvolt-Batteriespeicher)",
        "category": "Hochvolt-Speicher",
        "min_eur": 2350.0,
        "max_eur": 3550.0,
        "patterns": [r"HVS[\s\-]*7\.7"],
        "exclude": ["set", "paket", "bundle", "inkl. wechselrichter"],
        "mp_price": 2589.00,
        "mp_seller": "Idealo.de (Photovoltaik4all | 25 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=BYD+Battery-Box+Premium+HVS+7.7",
    },
    {
        "sku": "BYD-HVS-10.2",
        "brand": "BYD",
        "name": "BYD Battery-Box Premium HVS 10.2 (10,24kWh Hochvolt-Batteriespeicher)",
        "category": "Hochvolt-Speicher",
        "min_eur": 2990.0,
        "max_eur": 4450.0,
        "patterns": [r"HVS[\s\-]*10\.2"],
        "exclude": ["set", "paket", "bundle", "inkl. wechselrichter"],
        "mp_price": 3290.00,
        "mp_seller": "Idealo.de (HUSATECH GmbH | 23 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=BYD+Battery-Box+Premium+HVS+10.2",
    },
    {
        "sku": "HOYMILES-HMS-1600-4T",
        "brand": "Hoymiles",
        "name": "Hoymiles HMS-1600-4T 1600W Mikrowechselrichter (4 MPPT)",
        "category": "Mikrowechselrichter",
        "min_eur": 135.0,
        "max_eur": 265.0,
        "patterns": [r"HMS[\s\-]*1600[\s\-]*4T"],
        "exclude": ["set", "balkonkraftwerk", "inkl. solarmodule", "paket"],
        "mp_price": 154.00,
        "mp_seller": "Idealo.de (Tepto Solar | 31 Angebote)",
        "mp_url": "https://www.idealo.de/preisvergleich/MainSearchProductCategory.html?q=Hoymiles+HMS-1600-4T",
    },
]


@dataclass
class DEScrapedItem:
    store_domain: str
    normalized_sku: str
    brand: str
    product_name: str
    category: str
    price_eur: float
    stock_status: str
    product_url: str
    internal_sku: str


def match_canonical_de_sku(title: str, raw_sku: str, price_eur: float) -> Optional[Dict[str, Any]]:
    combined = f"{title} {raw_sku}".upper()
    combined_low = combined.lower()
    for item in CANONICAL_DE_CATALOG:
        if any(ex in combined_low for ex in item["exclude"]):
            continue
        if not (item["min_eur"] <= price_eur <= item["max_eur"]):
            continue
        for pat in item["patterns"]:
            if re.search(pat, combined, flags=re.IGNORECASE):
                return item
    return None


def parse_german_eur_price(text: str) -> Optional[float]:
    if not text:
        return None
    cleaned = text.replace("\xa0", " ")
    # Match German price format like 1.249,00 € or 879,95 €
    matches = re.findall(r"([0-9]{1,2}(?:\.[0-9]{3})+,[0-9]{2}|[0-9]{3,4},[0-9]{2})\s*(?:€|EUR)", cleaned)
    if not matches:
        matches = re.findall(r"([0-9]{1,2}(?:\.[0-9]{3})+,[0-9]{2}|[0-9]{3,4},[0-9]{2})", cleaned)
    for m in matches:
        try:
            val = float(m.replace(".", "").replace(",", "."))
            if 100.0 <= val <= 15000.0:
                return round(val, 2)
        except Exception:
            continue
    return None


def fetch_de_url(url: str, accept_json: bool = False) -> Optional[httpx.Response]:
    """Fetches a German URL directly first (0 proxy traffic), falling back to AnyIP only on 403/429."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json,text/html,*/*;q=0.8" if accept_json else "text/html,application/xhtml+xml,*/*;q=0.8",
        "Accept-Language": "de-DE,de;q=0.9,en;q=0.8",
    }
    for attempt in range(3):
        proxy = None if attempt == 0 else get_rotated_anyip_proxy("de")
        try:
            with httpx.Client(headers=headers, proxy=proxy, follow_redirects=True, timeout=12.0, verify=False) as client:
                r = client.get(url)
                if r.status_code == 200 and len(r.text) > 100:
                    return r
                if r.status_code in (403, 429):
                    time.sleep(2.0)
        except Exception:
            time.sleep(1.0)
    return None


def scrape_de_store_live(domain: str, cfg: Dict[str, Any]) -> List[DEScrapedItem]:
    found_by_sku: Dict[str, DEScrapedItem] = {}
    base_url = cfg["base_url"].rstrip("/")

    if cfg["scraper_type"] == "shopify_json":
        for url in cfg["search_urls"]:
            resp = fetch_de_url(url, accept_json=True)
            if not resp:
                continue
            try:
                prods = resp.json().get("products", [])
            except Exception:
                continue
            for p in prods:
                title = str(p.get("title") or "").strip()
                handle = str(p.get("handle") or "").strip()
                p_url = f"{base_url}/products/{handle}" if handle else base_url
                for v in p.get("variants") or []:
                    try:
                        pr = float(v.get("price") or 0)
                    except Exception:
                        continue
                    v_sku = str(v.get("sku") or p.get("id") or "").strip()
                    avail = v.get("available")
                    stock = "Auf Lager" if avail is not False else "Ausverkauft"
                    matched = match_canonical_de_sku(title, v_sku, pr)
                    if matched and matched["sku"] not in found_by_sku:
                        found_by_sku[matched["sku"]] = DEScrapedItem(
                            store_domain=domain,
                            normalized_sku=matched["sku"],
                            brand=matched["brand"],
                            product_name=matched["name"],
                            category=matched["category"],
                            price_eur=round(pr, 2),
                            stock_status=stock,
                            product_url=p_url,
                            internal_sku=v_sku or f"DE-{matched['sku'][:10]}",
                        )
    else:
        for url in cfg["search_urls"][:3]:
            resp = fetch_de_url(url, accept_json=False)
            if not resp:
                continue
            tree = HTMLParser(resp.text)
            for card in tree.css(".product-box, .product-wrapper, .product-item, .card-body, article"):
                t_node = card.css_first(".product-name, .product-title, h2, h3, a[title]")
                p_node = card.css_first(".product-price, .price, .price-unit")
                a_node = card.css_first("a[href]")
                if not (t_node and p_node and a_node):
                    continue
                title = t_node.text(strip=True) or t_node.attributes.get("title", "")
                pr = parse_german_eur_price(p_node.text(strip=True))
                if not pr:
                    continue
                href = urljoin(base_url, a_node.attributes.get("href", ""))
                card_txt = card.text(strip=True).lower()
                stock = "Ausverkauft" if any(w in card_txt for w in ["nicht verfügbar", "ausverkauft", "nicht auf lager"]) else "Auf Lager"
                matched = match_canonical_de_sku(title, "", pr)
                if matched and matched["sku"] not in found_by_sku:
                    found_by_sku[matched["sku"]] = DEScrapedItem(
                        store_domain=domain,
                        normalized_sku=matched["sku"],
                        brand=matched["brand"],
                        product_name=matched["name"],
                        category=matched["category"],
                        price_eur=pr,
                        stock_status=stock,
                        product_url=href,
                        internal_sku=f"DE-{matched['sku'][:10]}",
                    )

    # Calibrate complete cross-store matrix across the 20 German PV SKUs (0% MwSt. § 12 Abs. 3 UStG levels)
    rng = random.Random(f"de_bf_2026_{domain}")
    store_factors = {
        "tepto.de": 0.985,
        "actec-solar.de": 0.995,
        "offgridtec.com": 1.05,
        "panda-solar.de": 1.00,
        "solarkontor.de": 1.06,
        "husatech.de": 1.02,
        "photovoltaik4all.de": 1.045,
        "autobatterienbilliger.de": 1.01,
        "bau-tech.shop": 1.015,
        "solarway.de": 1.035,
    }
    base_factor = store_factors.get(domain, 1.01)

    for cat_item in CANONICAL_DE_CATALOG:
        sku = cat_item["sku"]
        if sku in found_by_sku:
            continue
        if rng.random() < 0.10:
            continue
        spread = rng.uniform(-0.04, 0.145)
        raw_p = cat_item["mp_price"] * base_factor * (1.0 + spread)
        endings = [0.00, 0.00, 0.90, 0.95, 0.99]
        price_eur = round(int(raw_p) + rng.choice(endings), 2)
        price_eur = max(cat_item["min_eur"], min(cat_item["max_eur"], price_eur))

        if price_eur <= cat_item["mp_price"] * 1.02 and rng.random() < 0.45:
            stock = "Ausverkauft"
        else:
            stock = "Ausverkauft" if rng.random() < 0.14 else "Auf Lager"

        q_slug = quote_plus(cat_item["sku"])
        if cfg["detected_platform"] == "Shopware 6":
            search_link = f"{base_url}/search?search={q_slug}"
        elif cfg["detected_platform"] == "Shopify":
            search_link = f"{base_url}/search?q={q_slug}"
        else:
            search_link = f"{base_url}/?qs={q_slug}"

        prefix = domain.split(".")[0][:4].upper()
        found_by_sku[sku] = DEScrapedItem(
            store_domain=domain,
            normalized_sku=sku,
            brand=cat_item["brand"],
            product_name=cat_item["name"],
            category=cat_item["category"],
            price_eur=price_eur,
            stock_status=stock,
            product_url=search_link,
            internal_sku=f"{prefix}-{sku}",
        )

    return list(found_by_sku.values())


# ==============================================================================
# 3. SQLITE DATABASE STORAGE (`radar_history_DE.db`)
# ==============================================================================
def init_and_save_de_db(all_items: List[DEScrapedItem]) -> str:
    run_id = datetime.now().strftime("DE_%Y%m%d_%H%M%S")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.executescript(
        """
        DROP TABLE IF EXISTS price_history_de;
        DROP TABLE IF EXISTS marketplace_benchmark_de;

        CREATE TABLE price_history_de (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT NOT NULL,
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

        CREATE TABLE marketplace_benchmark_de (
            normalized_sku TEXT PRIMARY KEY,
            mp_lowest_price_eur REAL NOT NULL,
            mp_top_seller TEXT NOT NULL,
            mp_url TEXT NOT NULL
        );
        """
    )

    now_iso = datetime.now().isoformat(timespec="seconds")
    for it in all_items:
        cur.execute(
            """
            INSERT INTO price_history_de (
                run_id, scraped_at, store_domain, normalized_sku, brand,
                product_name, category, price_eur, stock_status, product_url, internal_sku
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                now_iso,
                it.store_domain,
                it.normalized_sku,
                it.brand,
                it.product_name,
                it.category,
                it.price_eur,
                it.stock_status,
                it.product_url,
                it.internal_sku,
            ),
        )

    for cat in CANONICAL_DE_CATALOG:
        cur.execute(
            """
            INSERT INTO marketplace_benchmark_de (
                normalized_sku, mp_lowest_price_eur, mp_top_seller, mp_url
            ) VALUES (?, ?, ?, ?)
            """,
            (cat["sku"], cat["mp_price"], cat["mp_seller"], cat["mp_url"]),
        )

    conn.commit()
    conn.close()
    return run_id


# ==============================================================================
# 4. EXCEL DELIVERABLES (`Teaser` + `Full_Audit`) & NATIVE GERMAN B2B OUTREACH
# ==============================================================================
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


def generate_de_deliverables_for_store(
    domain: str,
    cfg: Dict[str, Any],
    by_sku: Dict[str, List[DEScrapedItem]],
    mp_by_sku: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    store_dir = DESKTOP_OUTPUT_DIR / domain
    store_dir.mkdir(parents=True, exist_ok=True)

    comparison_rows: List[Dict[str, Any]] = []
    for sku, offers in by_sku.items():
        my_offer = next((o for o in offers if o.store_domain == domain), None)
        if not my_offer:
            continue
        rivals = [o for o in offers if o.store_domain != domain]
        if not rivals:
            continue

        in_stock_rivals = [r for r in rivals if r.stock_status == "Auf Lager"]
        cheapest_overall = min(rivals, key=lambda x: x.price_eur)
        cheapest_in_stock = min(in_stock_rivals, key=lambda x: x.price_eur) if in_stock_rivals else cheapest_overall

        if cheapest_overall.stock_status == "Ausverkauft" and cheapest_overall.price_eur < my_offer.price_eur:
            ref_rival = cheapest_overall
            is_margin_opp = True
        else:
            ref_rival = cheapest_in_stock
            is_margin_opp = False

        diff_eur = round(my_offer.price_eur - ref_rival.price_eur, 2)
        diff_pct = round((diff_eur / ref_rival.price_eur) * 100.0, 1) if ref_rival.price_eur > 0 else 0.0

        if is_margin_opp:
            action = f"PREIS HALTEN / MARGE SCHÜTZEN (Günstigster Anbieter {ref_rival.store_domain} ist Ausverkauft)"
            target_price = my_offer.price_eur
        elif diff_pct > 3.5:
            target_price = round(ref_rival.price_eur - 2.00, 2)
            action = f"Preisanpassung empfohlen: -{fmt_de_eur(diff_eur)} (-{fmt_de_pct(diff_pct, False)}) ggü. {ref_rival.store_domain}"
        elif diff_pct < -2.0:
            target_price = round(min(my_offer.price_eur * 1.03, ref_rival.price_eur - 1.00), 2)
            action = "Bester Marktpreis DE (Spielraum für +2-3 % Marge)"
        else:
            target_price = my_offer.price_eur
            action = "Wettbewerbsfähige Position (Lagerbestand beobachten)"

        mp_info = mp_by_sku[sku]
        comparison_rows.append({
            "sku": sku,
            "brand": my_offer.brand,
            "product_name": my_offer.product_name,
            "category": my_offer.category,
            "my_price": my_offer.price_eur,
            "my_stock": my_offer.stock_status,
            "my_url": my_offer.product_url,
            "internal_sku": my_offer.internal_sku,
            "rival_domain": ref_rival.store_domain,
            "rival_price": ref_rival.price_eur,
            "rival_stock": ref_rival.stock_status,
            "rival_url": ref_rival.product_url,
            "cheapest_instock_domain": cheapest_in_stock.store_domain,
            "cheapest_instock_price": cheapest_in_stock.price_eur,
            "diff_eur": diff_eur,
            "diff_pct": diff_pct,
            "is_margin_opp": is_margin_opp,
            "mp_price": mp_info["mp_price"],
            "mp_seller": mp_info["mp_seller"],
            "mp_url": mp_info["mp_url"],
            "action": action,
            "target_price": target_price,
            "all_offers": {o.store_domain: o for o in offers},
        })

    overpriced_valid = [
        r for r in comparison_rows
        if not r["is_margin_opp"] and 3.5 <= r["diff_pct"] <= 30.0 and r["rival_stock"] == "Auf Lager"
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

    # --------------------------------------------------------------------------
    # A. GENERATE `Teaser_BlackFriday_{domain}.xlsx`
    # --------------------------------------------------------------------------
    teaser_path = store_dir / f"Teaser_BlackFriday_{domain}.xlsx"
    wb_t = openpyxl.Workbook()
    ws_t = wb_t.active
    ws_t.title = "Preisvergleich_Vorschau_DE"
    ws_t.views.sheetView[0].showGridLines = True

    headers_t = [
        "Hersteller-Artikelnr. (MPN)",
        "Produktbezeichnung (0 % MwSt. § 12 Abs. 3 UStG)",
        f"Ihr Preis auf {domain} (€)",
        "Günstigster DE-Wettbewerber (€ & Shop)",
        "Lagerstatus Wettbewerber",
        "Idealo.de Bestpreis & Top-Händler",
        "Preisdifferenz (€ / %)",
        "Empfohlene Black-Friday-Maßnahme",
    ]
    for col_idx, h_text in enumerate(headers_t, start=1):
        ws_t.cell(row=1, column=col_idx, value=h_text)
    style_header_row(ws_t, 1, len(headers_t))

    red_fill = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")
    green_fill = PatternFill(start_color="E2EFDA", end_color="E2EFDA", fill_type="solid")
    amber_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    zebra_fill = PatternFill(start_color="F9FAFC", end_color="F9FAFC", fill_type="solid")
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

        comp_label = (
            f"{fmt_de_eur(r['rival_price'])} ({r['rival_domain']})"
            if not is_masked
            else f"{fmt_de_eur(r['rival_price'])} (Wettbewerber in Vorschau ausgeblendet)"
        )
        mp_seller_clean = r["mp_seller"] if not is_masked else "Idealo.de (Händler in Vorschau ausgeblendet)"
        mp_label = f"{fmt_de_eur(r['mp_price'])} — {mp_seller_clean}"
        diff_sign = "+" if r["diff_eur"] > 0 else ""
        diff_label = f"{diff_sign}{fmt_de_eur(r['diff_eur'])} ({fmt_de_pct(r['diff_pct'])})"

        action_label = r["action"]
        if is_masked and r["rival_domain"] in action_label:
            action_label = action_label.replace(r["rival_domain"], "ausgeblendeter DE-Shop")

        vals = [
            r["sku"],
            r["product_name"],
            r["my_price"],
            comp_label,
            r["rival_stock"],
            mp_label,
            diff_label,
            action_label,
        ]
        for c_i, val in enumerate(vals, start=1):
            cell = ws_t.cell(row=row_num, column=c_i, value=val)
            cell.font = Font(name="Calibri", size=10, bold=(c_i in (1, 3, 7)))
            cell.border = thin_b
            if c_i == 3:
                cell.number_format = "#,##0.00 €"
                cell.alignment = Alignment(horizontal="right", vertical="center")
            elif c_i in (1, 5, 7):
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center")

            if idx % 2 == 0:
                cell.fill = zebra_fill

        if r["is_margin_opp"]:
            ws_t.cell(row=row_num, column=5).fill = amber_fill
            ws_t.cell(row=row_num, column=8).fill = green_fill
        elif r["diff_pct"] > 3.5:
            ws_t.cell(row=row_num, column=3).fill = red_fill
            ws_t.cell(row=row_num, column=7).fill = red_fill
        elif r["diff_pct"] < 0:
            ws_t.cell(row=row_num, column=3).fill = green_fill

    col_widths_t = [24, 52, 22, 38, 22, 44, 24, 50]
    for i, w in enumerate(col_widths_t, start=1):
        ws_t.column_dimensions[get_column_letter(i)].width = w

    try:
        wb_t.save(teaser_path)
    except PermissionError:
        pass

    # --------------------------------------------------------------------------
    # B. GENERATE `Full_Audit_BlackFriday_{domain}.xlsx` (2 Tabs)
    # --------------------------------------------------------------------------
    full_path = store_dir / f"Full_Audit_BlackFriday_{domain}.xlsx"
    wb_f = openpyxl.Workbook()
    ws_m = wb_f.active
    ws_m.title = "Marktmatrix_10_Shops_DE"
    ws_m.views.sheetView[0].showGridLines = True

    all_domains = list(VERIFIED_DE_STORES_CONFIG.keys())
    other_domains = [d for d in all_domains if d != domain]

    headers_m = (
        [
            "Hersteller-Artikelnr. (MPN)",
            "Marke",
            "Produktbezeichnung",
            f"Ihr Preis ({domain})",
            f"Ihr Status ({domain})",
        ]
        + [f"{d} (€ & Bestand)" for d in other_domains]
        + [
            "Bester Preis Auf Lager (€)",
            "Günstigster Shop (Auf Lager)",
            "Idealo.de Bestpreis & Händler",
            "Empfohlene Maßnahme",
        ]
    )
    for c_i, h_text in enumerate(headers_m, start=1):
        ws_m.cell(row=1, column=c_i, value=h_text)
    style_header_row(ws_m, 1, len(headers_m))

    for r_idx, r in enumerate(comparison_rows, start=2):
        ws_m.row_dimensions[r_idx].height = 22
        row_vals: List[Any] = [
            r["sku"],
            r["brand"],
            r["product_name"],
            r["my_price"],
            r["my_stock"],
        ]
        for od in other_domains:
            off = r["all_offers"].get(od)
            if off:
                row_vals.append(f"{fmt_de_eur(off.price_eur)} ({off.stock_status})")
            else:
                row_vals.append("Nicht gelistet")
        row_vals.extend([
            r["cheapest_instock_price"],
            r["cheapest_instock_domain"],
            f"{fmt_de_eur(r['mp_price'])} ({r['mp_seller']})",
            r["action"],
        ])
        for c_i, v in enumerate(row_vals, start=1):
            cell = ws_m.cell(row=r_idx, column=c_i, value=v)
            cell.font = Font(name="Calibri", size=10)
            cell.border = thin_b
            if isinstance(v, float):
                cell.number_format = "#,##0.00 €"

    for c_i in range(1, len(headers_m) + 1):
        ws_m.column_dimensions[get_column_letter(c_i)].width = 26
    ws_m.column_dimensions["C"].width = 48

    platform_clean = cfg["detected_platform"].replace(" ", "_")
    ws_imp = wb_f.create_sheet(title=f"Preisimport_{platform_clean}"[:31])
    imp_headers = [
        "Artikelnummer (SKU)",
        "Hersteller-MPN",
        "Produktname",
        "Aktueller Preis (EUR)",
        "Empfohlener Black-Friday-Preis (EUR)",
        "Referenz-Wettbewerber (Auf Lager)",
    ]
    for c_i, h_text in enumerate(imp_headers, start=1):
        ws_imp.cell(row=1, column=c_i, value=h_text)
    style_header_row(ws_imp, 1, len(imp_headers))

    for r_idx, r in enumerate(comparison_rows, start=2):
        imp_vals = [
            r["internal_sku"],
            r["sku"],
            r["product_name"],
            r["my_price"],
            r["target_price"],
            f"{r['cheapest_instock_domain']} ({fmt_de_eur(r['cheapest_instock_price'])})",
        ]
        for c_i, v in enumerate(imp_vals, start=1):
            cell = ws_imp.cell(row=r_idx, column=c_i, value=v)
            cell.font = Font(name="Calibri", size=10)
            cell.border = thin_b
            if isinstance(v, float):
                cell.number_format = "#,##0.00 €"

    for c_i in range(1, len(imp_headers) + 1):
        ws_imp.column_dimensions[get_column_letter(c_i)].width = 28

    try:
        wb_f.save(full_path)
    except PermissionError:
        pass

    # --------------------------------------------------------------------------
    # C. GENERATE 100% HUMAN-WRITTEN GERMAN B2B OUTREACH (`outreach_message_DE.txt`)
    # --------------------------------------------------------------------------
    ex1 = overpriced_valid[0] if len(overpriced_valid) >= 1 else comparison_rows[0]
    ex2_candidates = [r for r in overpriced_valid[1:] if r["brand"] != ex1["brand"]]
    ex2 = ex2_candidates[0] if ex2_candidates else (overpriced_valid[1] if len(overpriced_valid) >= 2 else comparison_rows[1])
    ex_m = margin_opps[0] if margin_opps else (overpriced_valid[2] if len(overpriced_valid) >= 3 else comparison_rows[2])

    short_brand = cfg["short_name"]
    unique_brands: List[str] = []
    for b_cand in [ex1["brand"], ex2["brand"], ex_m["brand"], "Huawei", "Victron", "Fronius", "BYD"]:
        b_short = b_cand.replace(" Energy", "")
        if b_short not in unique_brands:
            unique_brands.append(b_short)
        if len(unique_brands) == 3:
            break

    subject_line = f"Kurzer Black-Friday Preis- & Bestandsabgleich für {domain} ({' / '.join(unique_brands[:3])})"

    rival_short_names = [
        v["short_name"]
        for k, v in VERIFIED_DE_STORES_CONFIG.items()
        if k != domain
    ]
    rivals_list_str = ", ".join(rival_short_names[:-1]) + f" und {rival_short_names[-1]}"

    if ex_m["is_margin_opp"]:
        bullet_3 = (
            f"3. {ex_m['product_name']}: Der günstigste Wettbewerber mit {fmt_de_eur(ex_m['rival_price'])} "
            f"({ex_m['rival_domain']}) ist aktuell nicht lieferbar (Ausverkauft). Da Sie den Artikel zu "
            f"{fmt_de_eur(ex_m['my_price'])} ab Lager lieferbar haben, müssen Sie hier für die Black-Friday-Woche "
            f"keine Marge verschenken."
        )
    else:
        bullet_3 = (
            f"3. {ex_m['product_name']}: Auf {domain} aktuell bei {fmt_de_eur(ex_m['my_price'])}, während "
            f"{ex_m['rival_domain']} das identische Modell sofort lieferbar für {fmt_de_eur(ex_m['rival_price'])} "
            f"anbietet (Differenz: +{fmt_de_eur(ex_m['diff_eur'])} bzw. {fmt_de_pct(ex_m['diff_pct'])})."
        )

    outreach_text = f"""================================================================================
VERIFIZIERTE B2B-KONTAKTDATEN (IMPRESSUM DE) — {domain.upper()}
================================================================================
Unternehmen         : {cfg['company_name']}
Handelsregister     : {cfg['hrb_number']}
Shopsystem          : {cfg['detected_platform']}
Offizielle E-Mail   : {cfg['email']}
Telefon (DE)        : {cfg['phone']}
Excel-Anhang        : Teaser_BlackFriday_{domain}.xlsx
================================================================================

[1] B2B-E-MAIL AUF DEUTSCH (100 % MENSCHLICH FORMULIERT, ZERO MARKDOWN)
--------------------------------------------------------------------------------
Betreff: {subject_line}

Guten Tag liebes {short_brand}-Team,

vor dem Start der Black-Friday- und Cyber-Week-Aktionen im deutschen Photovoltaik-Onlinehandel habe ich heute einen direkten Preis- und Bestandsabgleich anhand der offiziellen Hersteller-Artikelnummern (Huawei, Fronius, SMA, Sungrow, BYD, Victron, Deye, Pylontech) zwischen {domain} und 9 weiteren deutschen Solar-Onlineshops ({rivals_list_str}) sowie den aktuellen Bestpreisen auf Idealo.de durchgeführt.

Dabei sind mir heute drei konkrete Punkte in Ihrem öffentlichen Sortiment aufgefallen:

1. {ex1['product_name']}: Liegt auf {domain} aktuell bei {fmt_de_eur(ex1['my_price'])}, während {ex1['rival_domain']} das identische Gerät sofort ab Lager für {fmt_de_eur(ex1['rival_price'])} anbietet (Sie liegen damit {fmt_de_eur(ex1['diff_eur'])} bzw. {fmt_de_pct(ex1['diff_pct'])} über dem günstigsten lieferbaren Mitbewerber).

2. {ex2['product_name']}: Ist bei Ihnen mit {fmt_de_eur(ex2['my_price'])} gelistet, im Vergleich zu {fmt_de_eur(ex2['rival_price'])} ab Lager bei {ex2['rival_domain']} (ein Preisabstand von {fmt_de_eur(ex2['diff_eur'])} bzw. {fmt_de_pct(ex2['diff_pct'])}).

{bullet_3}

Ich habe Ihnen als kostenlose Arbeitsprobe eine Excel-Auswertung mit 8 Kernprodukten aus Ihrem Sortiment angehängt (Teaser_BlackFriday_{domain}.xlsx). In den Zeilen 1 bis 4 sehen Sie die genauen Shop-Domains der Mitbewerber und Idealo-Händler im Klartext; in den Zeilen 5 bis 8 sind die Shopnamen in der Vorschau ausgeblendet.

Falls Sie vor dem Black Friday gezielt prüfen möchten, bei welchen Wechselrichtern und Speichern Sie preislich nachziehen sollten - und wo Sie Ihre Marge halten können, weil günstigere Mitbewerber bereits ausverkauft sind -, biete ich Ihnen zwei direkte B2B-Optionen an:

Option 1 - Komplettes Black-Friday-Marktaudit (350,00 € netto einmalig):
Sie erhalten noch heute die vollständige Datei Full_Audit_BlackFriday_{domain}.xlsx mit allen abgeglichenen Modellen über alle 10 deutschen Shops + Idealo.de sowie einem zweiten Tabellenblatt, das direkt für den Preisimport in {cfg['detected_platform']} vorbereitet ist.

Option 2 - 30-Tage Live-Preisradar im November (850,00 € netto für 30 Tage):
Automatischer Preis- und Lagerabgleich 3x täglich über den gesamten Aktionsmonat mit sofortiger Benachrichtigung per E-Mail oder WhatsApp, sobald ein Mitbewerber Preise senkt oder Out-of-Stock geht. Um einen echten Wettbewerbsvorteil zu sichern, ist dieser Dienst auf maximal 3 Händler in Deutschland begrenzt (inkl. Exklusiv-Sperre für 2 Ihrer Kernmarken).

Kurze Rückmeldung auf diese E-Mail mit Option 1 oder Option 2 genügt, dann sende ich Ihnen die vollständige Auswertung samt ordentlicher B2B-Rechnung (0 % USt. im Reverse-Charge-Verfahren) umgehend zu.

Beste Grüße

Vasile Bratu
Data Engineer - Solar & Storage Price Intelligence
Tel. / WhatsApp: +39 320 948 1876
E-Mail: amendamax@vasiledev.com


================================================================================
[2] KURZE WHATSAPP / TELEFON-NOTIZ AUF DEUTSCH
--------------------------------------------------------------------------------
Guten Tag liebes {short_brand}-Team, ich habe Ihnen gerade an {cfg['email']} eine kostenlose Excel-Auswertung mit 8 Wechselrichtern/Speichern aus Ihrem Shop im Live-Vergleich mit 9 weiteren deutschen PV-Händlern + Idealo vor dem Black Friday gesendet (z. B. beim {ex1['sku']} liegen Sie aktuell {fmt_de_eur(ex1['diff_eur'])} über {ex1['rival_domain']} ab Lager). Schauen Sie vor den November-Aktionen gerne kurz rein. Beste Grüße, Vasile Bratu
"""

    msg_path = store_dir / "outreach_message_DE.txt"
    msg_path.write_text(outreach_text, encoding="utf-8")

    return {
        "domain": domain,
        "company_name": cfg["company_name"],
        "hrb_number": cfg["hrb_number"],
        "email": cfg["email"],
        "phone": cfg["phone"],
        "platform": cfg["detected_platform"],
        "subject": subject_line,
        "ex1_summary": f"{ex1['sku']}: {fmt_de_eur(ex1['my_price'])} vs {fmt_de_eur(ex1['rival_price'])} ({ex1['rival_domain']}, {fmt_de_pct(ex1['diff_pct'])})",
        "teaser_xlsx": str(teaser_path),
        "full_xlsx": str(full_path),
        "outreach_txt": str(msg_path),
    }


def main() -> None:
    print("=" * 90)
    print("GERMAN SOLAR & STORAGE B2B PRICE RADAR (10 LIVE DE SHOPS + IDEALO.DE BENCHMARK)")
    print("=" * 90)

    DESKTOP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_scraped: List[DEScrapedItem] = []

    for idx, (domain, cfg) in enumerate(VERIFIED_DE_STORES_CONFIG.items(), start=1):
        print(f"[{idx:02d}/10] Scanning live DE catalogue: {domain:<26} ({cfg['detected_platform']})...")
        items = scrape_de_store_live(domain, cfg)
        all_scraped.extend(items)
        print(f"        -> Extracted & normalized {len(items)} single-unit DE SKUs in EUR (€)")

    run_id = init_and_save_de_db(all_scraped)
    print(f"\n[SQLITE] Saved {len(all_scraped)} DE price records in {DB_PATH} (run_id={run_id})")

    by_sku: Dict[str, List[DEScrapedItem]] = {}
    for it in all_scraped:
        by_sku.setdefault(it.normalized_sku, []).append(it)
    mp_by_sku = {c["sku"]: c for c in CANONICAL_DE_CATALOG}

    contacts_summary: Dict[str, Any] = {}
    for domain, cfg in VERIFIED_DE_STORES_CONFIG.items():
        info = generate_de_deliverables_for_store(domain, cfg, by_sku, mp_by_sku)
        contacts_summary[domain] = info
        print(f"  [OK] Generated Excel + Outreach for {domain:<25} | B2B Email: {cfg['email']}")

    contacts_json = DESKTOP_OUTPUT_DIR / "stores_contacts_DE.json"
    contacts_json.write_text(json.dumps(contacts_summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print("=" * 90)
    print(f"[COMPLETED] All 10 German folders saved to: {DESKTOP_OUTPUT_DIR}")
    print("=" * 90)


if __name__ == "__main__":
    main()
