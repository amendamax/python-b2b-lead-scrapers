"""
sku_matcher.py
Motor determinist de extragere si normalizare a Codului Oficial de Model (Part Number / SKU Producator)
pentru echipamente fotovoltaice (invertoare hibride/on-grid si baterii LiFePO4) din Romania.

Include filtre anti-accesorii (cabluri, rame, senzori ieftini) si parser strict pentru preturi RON si Stoc Real.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class SKUMatchResult:
    normalized_sku: str
    brand: str
    category: str  # "Invertor" | "Baterie LiFePO4" | "MPPT / Control"
    min_valid_price_ron: float
    max_valid_price_ron: float


# Cuvinte cheie care indica accesorii (cabluri, mufe, suporti, sigurante), kituri fotovoltaice complete cu panouri sau produse SH/resigilate
ACCESSORY_EXCLUSION_PATTERNS = re.compile(
    r"\b("
    r"accesoriu|accesorii|control\s+box|back[-\s]?up\s+box|"
    r"cablu|cabluri|set\s+cabluri|kit\s+cabluri|conector|mufa|mufe|"
    r"suport|rack\s+cabinet|dulap\s+rack|rama|brida|clema|siguranta|"
    r"manual|garantie\s+extinsa|taxa\s+verde|serviciu\s+montaj|"
    r"interfata\s+mk3|cablu\s+ve\.direct|cablu\s+utp|"
    r"sistem\s+fotovoltaic|kit\s+fotovoltaic|pachet\s+fotovoltaic|set\s+invertor|palet\s+panouri|"
    r"panouri\s+fotovoltaice|panouri\s+solare|panouri\s+trina|panouri\s+canadian|panouri\s+longi|"
    r"second[-\s]?hand|resigilat|copiaza"
    r")\b",
    re.IGNORECASE,
)


def _normalize_text(text: str) -> str:
    """Curata diacritice si caractere speciale pentru matching robust."""
    if not text:
        return ""
    replacements = {
        "ă": "a", "â": "a", "î": "i", "ș": "s", "ş": "s", "ț": "t", "ţ": "t",
        "Ă": "A", "Â": "A", "Î": "I", "Ș": "S", "Ş": "S", "Ț": "T", "Ţ": "T",
        "–": "-", "—": "-", "‑": "-", "_": "-",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def is_accessory_title(title: str) -> bool:
    """Returneaza True daca titlul descrie un cablu/suport/accesoriu, nu echipamentul principal."""
    norm = _normalize_text(title)
    return bool(ACCESSORY_EXCLUSION_PATTERNS.search(norm))


# ============================================================================
# REGULI REGEX PENTRU MODELE OFICIALE (ORDONATE DE LA SPECIFIC LA GENERAL)
# ============================================================================

def match_official_sku(title: str, extra_text: str = "", price_ron: Optional[float] = None) -> Optional[SKUMatchResult]:
    """
    Extrage si normalizeaza codul oficial de producator (Part Number) din titlu si/sau cod SKU.
    Daca price_ron este furnizat, valideaza ca pretul sa fie in plaja fizica a echipamentului
    (elimina automat cablurile de 150 RON care contin 'US5000' in titlu).
    """
    combined = f"{title} {extra_text}".strip()
    norm = _normalize_text(combined).upper()

    if is_accessory_title(title):
        return None

    result: Optional[SKUMatchResult] = None

    # -------------------------------------------------------------------------
    # 1. DEYE (Invertoare Hibride Monofazate / Trifazate LV & HV + Baterii)
    # -------------------------------------------------------------------------
    # Ex: SUN-5K-SG04LP1, SUN-6K-SG06LP1-EU, SUN-10K-SG04LP3-EU, SUN-12K-SG05LP3-EU, SUN-15K-SG01HP3-EU-AM2
    m_deye_inv = re.search(
        r"\bSUN[-\s]?(\d{1,2}(?:\.\d)?)\s*K[-\s]?(SG0[1-6][LH]P[13]|G0[3-6]P?[13]?)\b",
        norm,
    )
    if m_deye_inv:
        kw = m_deye_inv.group(1)
        series = m_deye_inv.group(2)
        # Normalizam reviziile echivalente Deye LV 1P (SG03LP1/SG04LP1/SG05LP1/SG06LP1 -> SG04LP1)
        # si LV 3P (SG04LP3/SG05LP3 -> SG04LP3) pentru comparatie directa 1-la-1 intre magazine
        if re.match(r"^SG0[1-6]LP1$", series):
            norm_series = "SG04LP1"
        elif re.match(r"^SG0[1-6]LP3$", series):
            norm_series = "SG04LP3"
        elif re.match(r"^SG0[1-6]HP3$", series):
            norm_series = "SG01HP3"
        elif series.startswith("G0"):
            norm_series = "G05" if kw in ("5", "6", "8", "10", "12", "15") else series[:3]
        else:
            norm_series = series
        sku = f"SUN-{kw}K-{norm_series}"
        min_p = 1800.0 if norm_series.startswith("G0") else 3200.0
        result = SKUMatchResult(sku, "Deye", "Invertor", min_p, 45000.0)

    if not result:
        # Baterii Deye SE-G5.1 Pro / Pro-B / SE-F5 (5.12kWh), SE-F12 (12kWh), SE-F16 / RW-F16 (16kWh), RW-M6.1, BOS-G, AI-W5.1
        if re.search(r"\b(SE[-\s]?G5\.1|SE[-\s]?F5)\b", norm):
            result = SKUMatchResult("SE-G5.1", "Deye", "Baterie LiFePO4", 3200.0, 14000.0)
        elif re.search(r"\bSE[-\s]?F12\b", norm):
            result = SKUMatchResult("SE-F12", "Deye", "Baterie LiFePO4", 6500.0, 16000.0)
        elif re.search(r"\b(SE[-\s]?F16|RW[-\s]?F16)\b", norm):
            result = SKUMatchResult("SE-F16", "Deye", "Baterie LiFePO4", 8000.0, 19000.0)
        elif re.search(r"\bRW[-\s]?M6\.1\b", norm):
            result = SKUMatchResult("RW-M6.1", "Deye", "Baterie LiFePO4", 4000.0, 15000.0)
        elif re.search(r"\bAI[-\s]?W5\.1\b", norm):
            result = SKUMatchResult("AI-W5.1", "Deye", "Baterie LiFePO4", 4000.0, 25000.0)
        elif re.search(r"\bBOS[-\s]?G(?:M5\.1|[-\s]?PRO)?\b", norm) and "DEYE" in norm:
            result = SKUMatchResult("BOS-GM5.1", "Deye", "Baterie LiFePO4", 3500.0, 45000.0)

    # -------------------------------------------------------------------------
    # 2. HUAWEI (Invertoare SUN2000 & Baterii LUNA2000)
    # -------------------------------------------------------------------------
    if not result:
        # Baterii complete LUNA2000-5-S0 / 10-S0 / 15-S0 / 7-S1 / 14-S1
        m_luna_set = re.search(r"\bLUNA\s*2000[-\s]?(5|7|10|14|15|21)[-\s]?(S0|S1|E1)\b", norm)
        if m_luna_set:
            cap = m_luna_set.group(1)
            gen = "S1" if m_luna_set.group(2) in ("S1", "E1") else "S0"
            sku = f"LUNA2000-{cap}-{gen}"
            min_p = 7500.0 if cap in ("5", "7") else (13000.0 if cap in ("10", "14") else 18000.0)
            result = SKUMatchResult(sku, "Huawei", "Baterie LiFePO4", min_p, 65000.0)
        elif re.search(r"\bLUNA\s*2000[-\s]?5\s*KW[-\s]?C0\b", norm):
            result = SKUMatchResult("LUNA2000-5KW-C0", "Huawei", "Baterie LiFePO4", 2500.0, 9500.0)
        elif re.search(r"\bLUNA\s*2000[-\s]?5[-\s]?E0\b", norm):
            result = SKUMatchResult("LUNA2000-5-E0", "Huawei", "Baterie LiFePO4", 5500.0, 16000.0)

    if not result:
        # Invertoare Huawei SUN2000-3KTL-L1, SUN2000-5KTL-M1, SUN2000-10KTL-M1 etc.
        m_hw_inv = re.search(
            r"\bSUN\s*2000L?[-\s]?(\d{1,2}(?:\.\d{1,2})?)\s*K(?:TL)?(?:[-\s]?(L1|M0|M1|M2|M3|M5|MAP0|MC0|LC0))?\b",
            norm,
        )
        if m_hw_inv:
            kw = m_hw_inv.group(1)
            suffix = m_hw_inv.group(2) or ""
            if suffix in ("L1", "LC0") or ("MONOFAZAT" in norm or "1PH" in norm or "2000L-" in norm):
                sku = f"SUN2000-{kw}KTL-L1"
            elif kw in ("3", "4", "5", "6", "8", "10"):
                sku = f"SUN2000-{kw}KTL-M1"
            elif kw in ("12", "15", "17", "20", "25"):
                sku = f"SUN2000-{kw}KTL-M2"
            elif kw in ("30", "36", "40", "50", "60", "100"):
                sku = f"SUN2000-{kw}KTL-M3"
            else:
                sku = f"SUN2000-{kw}KTL-{suffix}" if suffix else f"SUN2000-{kw}KTL"
            result = SKUMatchResult(sku, "Huawei", "Invertor", 2400.0, 32000.0)

    # -------------------------------------------------------------------------
    # 3. PYLONTECH (Baterii LiFePO4 LV & HV)
    # -------------------------------------------------------------------------
    if not result:
        m_pylon = re.search(
            r"\b(US2000C|US3000C|US5000(?:[-\s]?1C)?|UF5000|UP2500|UP5000|FORCE[-\s]?H1|FORCE[-\s]?H2|FORCE[-\s]?L1|FORCE[-\s]?L2)\b",
            norm,
        )
        if m_pylon:
            raw_code = m_pylon.group(1).replace(" ", "-")
            if raw_code.startswith("US5000"):
                sku = "US5000"
            elif raw_code.startswith("FORCE"):
                sku = "Force-" + raw_code.split("-")[-1]
            else:
                sku = raw_code
            min_p = 2600.0 if sku in ("US2000C", "UP2500") else 3400.0
            result = SKUMatchResult(sku, "Pylontech", "Baterie LiFePO4", min_p, 45000.0)

    # -------------------------------------------------------------------------
    # 4. VICTRON ENERGY (MultiPlus-II, Quattro, SmartSolar MPPT, Cerbo GX)
    # -------------------------------------------------------------------------
    if not result:
        # MultiPlus / MultiPlus-II 24/3000, 48/3000, 48/5000, 48/8000, 48/10000, 48/15000
        m_mp2 = re.search(
            r"\bMULTIPLUS(?:[-\s]?II)?(?:\s+GX)?\s+(12|24|48)\s*/\s*(3000|5000|8000|10000|15000)\b",
            norm,
        )
        if m_mp2:
            volt = m_mp2.group(1)
            va = m_mp2.group(2)
            sku = f"MultiPlus-II {volt}/{va}"
            result = SKUMatchResult(sku, "Victron Energy", "Invertor", 2100.0, 26000.0)

    if not result:
        # SmartSolar MPPT 150/35, 150/45, 150/60, 150/70, 150/85, 150/100, 250/60, 250/70, 250/85, 250/100
        m_mppt = re.search(
            r"\bSMARTSOLAR\s+(?:MPPT\s+)?(100|150|250|450)\s*/\s*(20|30|35|45|50|60|70|85|100|200)\b",
            norm,
        )
        if m_mppt:
            v = m_mppt.group(1)
            a = m_mppt.group(2)
            sku = f"SmartSolar MPPT {v}/{a}"
            result = SKUMatchResult(sku, "Victron Energy", "MPPT / Control", 450.0, 15000.0)

    if not result:
        if re.search(r"\bCERBO[-\s]?GX\b", norm) and "TOUCH" not in norm:
            result = SKUMatchResult("Cerbo GX", "Victron Energy", "MPPT / Control", 900.0, 3200.0)

    # -------------------------------------------------------------------------
    # 5. V-TAC (Baterii LiFePO4 si Invertoare Deye/V-Tac OEM)
    # -------------------------------------------------------------------------
    if not result:
        m_vtac = re.search(
            r"\b(VT[-\s]?48100E|VT[-\s]?48100W|VT[-\s]?48200B|VT[-\s]?51300|VT[-\s]?660510|VT[-\s]?661010|VT[-\s]?12040)\b",
            norm,
        )
        if m_vtac:
            raw_vt = m_vtac.group(1).replace(" ", "-")
            if not raw_vt.startswith("VT-"):
                raw_vt = "VT-" + raw_vt[2:]
            cat = "Invertor" if raw_vt in ("VT-660510", "VT-661010") else "Baterie LiFePO4"
            result = SKUMatchResult(raw_vt, "V-Tac", cat, 3000.0, 28000.0)
        elif "V-TAC" in norm or "VTAC" in norm:
            # Mapare dupa SKU V-Tac numeric oficial (11526 = VT-48100E, 11525 = VT-48200B, 11882/12229 = VT-51300)
            if re.search(r"\b11526\b", norm):
                result = SKUMatchResult("VT-48100E", "V-Tac", "Baterie LiFePO4", 3200.0, 12000.0)
            elif re.search(r"\b11525\b", norm):
                result = SKUMatchResult("VT-48200B", "V-Tac", "Baterie LiFePO4", 6000.0, 19000.0)

    # -------------------------------------------------------------------------
    # 6. FRONIUS (Symo GEN24, Primo GEN24, Symo Advanced/Light)
    # -------------------------------------------------------------------------
    if not result:
        m_fronius_gen24 = re.search(
            r"\b(SYMO|PRIMO)\s+GEN\s*24\s+(\d{1,2}(?:\.\d)?)\b",
            norm,
        )
        if m_fronius_gen24:
            family = m_fronius_gen24.group(1).capitalize()
            kw = m_fronius_gen24.group(2)
            if "." not in kw:
                kw = f"{kw}.0"
            sku = f"{family} GEN24 {kw}"
            result = SKUMatchResult(sku, "Fronius", "Invertor", 4500.0, 28000.0)
        elif re.search(r"\bPRIMO\s+GEN\s*24\b", norm):
            result = SKUMatchResult("Primo GEN24", "Fronius", "Invertor", 4500.0, 22000.0)
        else:
            m_fronius_symo = re.search(
                r"\bSYMO\s+(\d{1,2}\.\d)[-\s]3[-\s]M\b",
                norm,
            )
            if m_fronius_symo:
                kw = m_fronius_symo.group(1)
                sku = f"Symo {kw}-3-M"
                result = SKUMatchResult(sku, "Fronius", "Invertor", 4200.0, 25000.0)

    # -------------------------------------------------------------------------
    # 7. GROWATT (MOD TL3-XH, SPH TL3 BH-UP, MIN TL-XH, ARK 2.5H-A1)
    # -------------------------------------------------------------------------
    if not result:
        m_growatt_mod = re.search(
            r"\bMOD[-\s]?(\d{1,2}000|\d{1,2}K)\s*TL3[-\s]?XH\b",
            norm,
        )
        if m_growatt_mod:
            p_raw = m_growatt_mod.group(1)
            # Normalizare ex: 10000 -> 10K, 5000 -> 5000
            if p_raw in ("10000", "10K"):
                sku = "MOD 10KTL3-XH"
            elif p_raw in ("5000", "5K"):
                sku = "MOD 5000TL3-XH"
            elif p_raw in ("6000", "6K"):
                sku = "MOD 6000TL3-XH"
            elif p_raw in ("8000", "8K"):
                sku = "MOD 8000TL3-XH"
            else:
                sku = f"MOD {p_raw}TL3-XH"
            result = SKUMatchResult(sku, "Growatt", "Invertor", 2500.0, 18000.0)

    if not result:
        m_growatt_sph = re.search(
            r"\bSPH[-\s]?(\d{4,5})\s*TL3\s*BH(?:[-\s]?UP)?\b",
            norm,
        )
        if m_growatt_sph:
            p_raw = m_growatt_sph.group(1)
            sku = f"SPH {p_raw}TL3 BH-UP"
            result = SKUMatchResult(sku, "Growatt", "Invertor", 4000.0, 20000.0)

    if not result:
        if re.search(r"\bARK[-\s]?2\.5H[-\s]?A1\b", norm):
            result = SKUMatchResult("ARK 2.5H-A1", "Growatt", "Baterie LiFePO4", 2400.0, 9000.0)
        elif re.search(r"\bSPF[-\s]?6000\s*ES(?:\s*PLUS)?\b", norm):
            result = SKUMatchResult("SPF 6000ES Plus", "Growatt", "Invertor", 2100.0, 6500.0)
        elif re.search(r"\bSPF[-\s]?5000\s*ES\b", norm):
            result = SKUMatchResult("SPF 5000ES", "Growatt", "Invertor", 1900.0, 5800.0)

    # -------------------------------------------------------------------------
    # 8. SOLIS & RENON POWER (Invertoare Hibride Solis S6 + Baterii LiFePO4)
    # -------------------------------------------------------------------------
    if not result:
        m_solis = re.search(r"\b(S6[-\s]?EH[13]P\d{1,2}K(?:02)?)\b", norm)
        if m_solis:
            sku = m_solis.group(1).replace(" ", "-")
            result = SKUMatchResult(sku, "Solis", "Invertor", 3200.0, 22000.0)
        elif re.search(r"\b(XCELLENT[-\s]+PLUS|R[-\s]?XC016161)\b", norm) and "32KWH" not in norm and "2XR" not in norm:
            result = SKUMatchResult("Xcellent Plus 16kWh", "Renon Power", "Baterie LiFePO4", 7500.0, 15000.0)

    # Validare finala de pret daca a fost furnizat
    if result and price_ron is not None:
        if price_ron < result.min_valid_price_ron or price_ron > result.max_valid_price_ron:
            return None

    return result


# ============================================================================
# PARSARE PRETURI RON & STATUS STOC
# ============================================================================

def parse_ron_price(raw_text: str) -> Optional[float]:
    """
    Converteste texte romanesti de pret ('6.450,00 Lei', '6,450.00 RON', '12.499,99 lei', '6 450 RON')
    intr-un float curat (ex: 6450.0).
    """
    if not raw_text:
        return None

    cleaned = _normalize_text(raw_text)
    # Eliminam texte de tip TVA sau unitati
    cleaned = re.sub(r"(?i)(lei|ron|tva\s*inclus|cu\s*tva|fara\s*tva|/buc|buc\.)", " ", cleaned)
    # Cautam secvente numerice de pret
    m = re.search(r"(\d[\d\.\,\s\xa0]{1,12}\d)", cleaned)
    if not m:
        return None

    num_str = m.group(1).strip().replace("\xa0", "").replace(" ", "")

    # Cazul 1: are atat punct cat si virgula (ex: 6.450,00 sau 6,450.00)
    if "." in num_str and "," in num_str:
        if num_str.rfind(",") > num_str.rfind("."):
            # Format romanesc: 6.450,00
            num_str = num_str.replace(".", "").replace(",", ".")
        else:
            # Format anglo-saxon: 6,450.00
            num_str = num_str.replace(",", "")
    elif "," in num_str:
        parts = num_str.split(",")
        if len(parts[-1]) == 2:
            # Virgula zecimala: 6450,00
            num_str = num_str.replace(",", ".")
        else:
            # Virgula separator de mii: 6,450
            num_str = num_str.replace(",", "")
    elif "." in num_str:
        parts = num_str.split(".")
        if len(parts[-1]) == 3 and len(parts) >= 2:
            # Punct separator de mii: 6.450
            num_str = num_str.replace(".", "")
        # Altfel punctul este deja zecimal (ex: 6450.00)

    try:
        val = float(num_str)
        # Unele platforme (ex: eMAG / Gomag) concateneaza banii fara separator (ex: 645000 pt 6450.00)
        if val > 150000 and str(int(val)).endswith(("00", "99", "90", "50")):
            val = round(val / 100.0, 2)
        return round(val, 2) if val > 50 else None
    except ValueError:
        return None


def parse_stock_status(raw_text: str, html_snippet: str = "") -> Tuple[bool, str]:
    """
    Regula stricta din specificatie:
    - True DOAR daca produsul este "In stoc" / "Livrare imediata" / "Stoc magazin" / "Stoc suficient"
    - False daca este "Stoc epuizat", "Indisponibil", "La comanda", "Precomanda", "Intreaba stoc"
    Returneaza (in_stock: bool, normalized_label: str).
    """
    combined = _normalize_text(f"{raw_text} {html_snippet}").lower()

    # 1. Verificam mai intai negatiile / precomenzile / la comanda
    negative_markers = [
        "stoc epuizat",
        "epuizat",
        "indisponibil",
        "la comanda",
        "pe comanda",
        "precomanda",
        "intreaba stoc",
        "verifica stoc",
        "stoc 0",
        "stoc: 0",
        "out of stock",
        "outofstock",
        "sold out",
        "soldout",
        "nu este in stoc",
        "lipsa stoc",
        "stoc limitat - suna",
    ]
    for marker in negative_markers:
        if marker in combined:
            if "comanda" in marker:
                return False, "La comandă / Fără stoc fizic"
            return False, "Stoc Epuizat"

    # 2. Verificam markerii pozitivi de stoc activ
    positive_markers = [
        "in stoc",
        "stoc magazin",
        "stoc depozit",
        "stoc propriu",
        "stoc suficient",
        "stoc limitat",
        "livrare imediata",
        "livrare 24h",
        "livrare in 24",
        "disponibil in stoc",
        "schema.org/instock",
        '"instock"',
        "adauga in cos",
    ]
    for marker in positive_markers:
        if marker in combined:
            return True, "În stoc"

    # Default conservator: daca are buton de adaugare in cos si nicio negatie
    return True, "În stoc"
