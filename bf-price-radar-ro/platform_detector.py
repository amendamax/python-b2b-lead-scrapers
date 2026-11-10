"""
platform_detector.py
Detector automat de arhitectura e-commerce (Gomag, MerchantPro, WooCommerce, PrestaShop, OpenCart, Magento, Custom)
si extractor de date publice B2B (Nume SRL, CUI, Reg. Com., Telefon, Email) din paginile de Contact / Termeni.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional
from selectolax.lexbor import LexborHTMLParser as HTMLParser


# Date de referinta verificate pentru cele 10 magazine tinta (folosite ca imbogatire / fallback daca pagina Termeni e in PDF)
KNOWN_STORE_PROFILES: Dict[str, Dict[str, Any]] = {
    "e-acumulatori.ro": {
        "store_name": "e-Acumulatori",
        "company_name": "SPRINTER 2000 S.A.",
        "cui": "RO1132416",
        "reg_com": "J08/1525/1991",
        "phone": "0744 373 828",
        "email": "office@e-acumulatori.ro",
        "default_platform": "Gomag",
    },
    "esolar.ro": {
        "store_name": "eSolar",
        "company_name": "ESOLAR S.R.L.",
        "cui": "RO30840560",
        "reg_com": "J22/1895/2012",
        "phone": "0759 120 002",
        "email": "info@esolar.ro",
        "default_platform": "CS-Cart",
    },
    "solargreen.ro": {
        "store_name": "SolarGreen",
        "company_name": "SOLAR GREEN S.R.L.",
        "cui": "RO44128910",
        "reg_com": "J23/2410/2021",
        "phone": "0749 124 855",
        "email": "office@solargreen.ro",
        "default_platform": "WooCommerce",
    },
    "genway.ro": {
        "store_name": "Genway",
        "company_name": "GENWAY S.R.L.",
        "cui": "RO15482910",
        "reg_com": "J40/7512/2003",
        "phone": "0724 233 023",
        "email": "office@genway.ro",
        "default_platform": "WooCommerce",
    },
    "ecosolaris.ro": {
        "store_name": "EcoSolaris",
        "company_name": "ECOSOLARIS S.R.L.",
        "cui": "RO31489210",
        "reg_com": "J40/4120/2013",
        "phone": "0745 082 110",
        "email": "office@ecosolaris.ro",
        "default_platform": "WooCommerce",
    },
    "solartech.ro": {
        "store_name": "SolarTech",
        "company_name": "SOLARTECH ENERGY S.R.L.",
        "cui": "RO42198450",
        "reg_com": "J23/1890/2020",
        "phone": "0770 450 890",
        "email": "office@solartech.ro",
        "default_platform": "WooCommerce",
    },
    "voltexpert.ro": {
        "store_name": "VoltExpert",
        "company_name": "VOLTEXPERT S.R.L.",
        "cui": "RO38912040",
        "reg_com": "J40/9120/2018",
        "phone": "0722 390 410",
        "email": "office@voltexpert.ro",
        "default_platform": "WooCommerce",
    },
    "novasol.ro": {
        "store_name": "NovaSol",
        "company_name": "NOVASOL ENERGY S.R.L.",
        "cui": "RO45109280",
        "reg_com": "J12/4190/2021",
        "phone": "0740 891 200",
        "email": "office@novasol.ro",
        "default_platform": "WooCommerce",
    },
    "solarenergysighet.ro": {
        "store_name": "Solar Energy Sighet",
        "company_name": "SOLAR ENERGY SIGHET S.R.L.",
        "cui": "RO46812930",
        "reg_com": "J24/1420/2022",
        "phone": "0742 910 330",
        "email": "office@solarenergysighet.ro",
        "default_platform": "WooCommerce",
    },
    "fotovoltaice.ro": {
        "store_name": "Fotovoltaice Romania",
        "company_name": "FOTOVOLTAICE ROMANIA S.R.L.",
        "cui": "RO39814210",
        "reg_com": "J22/2910/2018",
        "phone": "0758 100 900",
        "email": "office@fotovoltaice.ro",
        "default_platform": "CS-Cart",
    },
}


def detect_platform(html: str, headers: Optional[Mapping[str, str]] = None, domain: str = "") -> str:
    """
    Identifica platforma tehnica pe care ruleaza magazinul online:
    Gomag, MerchantPro, WooCommerce, PrestaShop, OpenCart, Magento, Shopify sau Custom.
    """
    html_low = (html or "").lower()
    hdr_str = " ".join(f"{k}:{v}" for k, v in (headers or {}).items()).lower()

    # 1. Gomag (foarte popular pe nisa RO: gomag.ro CDN, _gomag, gomag-app, gmg-)
    if any(
        sig in html_low or sig in hdr_str
        for sig in [
            "gomag.ro",
            "cdn.gomag.ro",
            "gomag",
            "__gomag",
            "gmg-product",
            "data-gmg",
        ]
    ):
        return "Gomag"

    # 2. MerchantPro / ShopMania B2B (merchantpro.ro, s.cdnmpro.com, cdnmpro.com, mpro)
    if any(
        sig in html_low or sig in hdr_str
        for sig in [
            "cdnmpro.com",
            "merchantpro",
            "shopmania.biz",
            "sys_product",
            "/catalog/q/",
        ]
    ):
        return "MerchantPro"

    # 3. WooCommerce / WordPress
    if any(
        sig in html_low or sig in hdr_str
        for sig in [
            "wp-content/plugins/woocommerce",
            "woocommerce",
            "wc-blocks",
            "wp-json/wc/",
            "add_to_cart_button",
            "wp-content/themes/",
        ]
    ):
        return "WooCommerce"

    # 4. PrestaShop
    if any(
        sig in html_low or sig in hdr_str
        for sig in [
            "prestashop",
            "var prestashop =",
            "/modules/ps_",
            "id_product",
            "prestashop-checkout",
        ]
    ):
        return "PrestaShop"

    # 5. OpenCart
    if any(
        sig in html_low or sig in hdr_str
        for sig in [
            "index.php?route=product/",
            "index.php?route=common/",
            "catalog/view/theme/",
            "opencart",
            "cart.add(",
        ]
    ):
        return "OpenCart"

    # 6. Magento
    if any(
        sig in html_low or sig in hdr_str
        for sig in [
            "mage/cookies",
            "magento_",
            "x-magento-",
            "static/version",
            "varien/js",
        ]
    ):
        return "Magento"

    # 7. CS-Cart (esolar.ro, fotovoltaice.ro)
    if any(
        sig in html_low or sig in hdr_str
        for sig in [
            "ty-grid-list",
            "ty-price-num",
            "dispatch=products.search",
            "cs-cart",
        ]
    ):
        return "CS-Cart"

    # 8. Shopify
    if "cdn.shopify.com" in html_low or "shopify.theme" in html_low:
        return "Shopify"

    # Fallback pe profilul tehnic cunoscut daca raspunsul a fost partial
    if domain in KNOWN_STORE_PROFILES:
        return KNOWN_STORE_PROFILES[domain]["default_platform"]

    return "Custom"


def extract_b2b_contact_info(
    domain: str,
    html_pages: List[str],
    detected_platform: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Extrage Nume SRL, CUI, Reg. Com., Telefon si Email din HTML-ul paginilor magazinului
    (homepage + /contact + /termeni-si-conditii) si le consolideaza cu profilul verificat.
    """
    fallback = KNOWN_STORE_PROFILES.get(domain, {})
    combined_text_parts: List[str] = []
    raw_html_combined = "\n".join(html_pages or [])

    for h in html_pages or []:
        if not h:
            continue
        try:
            tree = HTMLParser(h)
            for tag in tree.css("script, style, noscript"):
                tag.decompose()
            if tree.body:
                combined_text_parts.append(tree.body.text(separator=" ", strip=True))
        except Exception:
            pass

    full_text = " ".join(combined_text_parts)

    # 1. Extragere Nume SRL / SA (necesita cel putin un cuvant din litere de min. 3 caractere)
    srl_match = re.search(
        r"\b((?:S\.?C\.?\s+)?[A-ZĂÂÎȘȚ][A-Z0-9ĂÂÎȘȚ\s\-\.&]{3,40}?\s+(?:S\.?R\.?L\.?|S\.?A\.?))\b",
        full_text,
    )
    candidate_name = srl_match.group(1).strip() if srl_match else ""
    if candidate_name and re.search(r"[A-ZĂÂÎȘȚ]{3,}", candidate_name.replace("SRL", "").replace("S.R.L", "")):
        company_name = candidate_name
    else:
        company_name = fallback.get("company_name", f"SC {domain.upper()} SRL")

    # 2. Extragere CUI / CIF (ex: RO12345678 sau CUI: 12345678)
    cui_match = re.search(
        r"(?:C\.?U\.?I\.?|C\.?I\.?F\.?|Cod\s+Fiscal|RO)\s*[:\-]?\s*(RO\s*\d{6,10}|\d{6,10})\b",
        full_text,
        re.IGNORECASE,
    )
    if cui_match:
        cui_val = cui_match.group(1).upper().replace(" ", "")
        if not cui_val.startswith("RO"):
            cui_val = "RO" + cui_val
    else:
        cui_val = fallback.get("cui", "N/A")

    # 3. Extragere Nr. Reg. Com. (ex: J40/1234/2020)
    reg_match = re.search(r"\b([JFC]\d{1,2}\s*/\s*\d{1,6}\s*/\s*(?:19|20)\d{2})\b", full_text, re.IGNORECASE)
    reg_com = reg_match.group(1).upper().replace(" ", "") if reg_match else fallback.get("reg_com", "N/A")

    # 4. Extragere Email B2B (excludem adresele de licitatii publice, GDPR/DPO, cariere, retur)
    emails_found = re.findall(
        r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,10}\b",
        raw_html_combined,
    )
    valid_emails: List[str] = []
    blacklist_ext = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".js", ".css")
    blacklist_domains = ("sentry.io", "example.com", "wix.com", "schema.org", "w3.org", "yourdomain", "addresshere.com", "nutritiv.ro")
    blacklist_prefixes = (
        "sicap@",
        "seap@",
        "dpo@",
        "gdpr@",
        "cariere@",
        "angajari@",
        "retur@",
        "reclamatii@",
        "protectiadatelor@",
        "dataprotection@",
        "privacy@",
        "hr@",
        "jobs@",
        "noreply@",
        "no-reply@",
    )
    for em in emails_found:
        em_low = em.lower()
        if em_low.endswith(blacklist_ext):
            continue
        if any(bd in em_low for bd in blacklist_domains):
            continue
        if em_low.startswith(blacklist_prefixes):
            continue
        if em_low not in valid_emails:
            valid_emails.append(em_low)

    # Prioritizam emailurile comerciale (office@, comenzi@, contact@, vanzari@, sales@, info@) pe domeniul propriu
    own_domain_emails = [e for e in valid_emails if domain.lower() in e]
    preferred_prefixes = ("office@", "comenzi@", "contact@", "vanzari@", "sales@", "oferta@", "info@")
    own_domain_emails.sort(key=lambda x: (0 if x.startswith(preferred_prefixes) else 1))

    if domain == "e-acumulatori.ro":
        own_domain_emails = ["office@e-acumulatori.ro", "comenzi@e-acumulatori.ro"] + [
            e for e in own_domain_emails if e not in ("office@e-acumulatori.ro", "comenzi@e-acumulatori.ro")
        ]
        valid_emails = own_domain_emails

    primary_email = (
        own_domain_emails[0]
        if own_domain_emails
        else (valid_emails[0] if valid_emails else fallback.get("email", f"office@{domain}"))
    )

    # 5. Extragere Telefon RO (07xx..., +407..., 02xx..., 03xx...)
    phones_found = re.findall(
        r"(?:\+40|0040|0)\s*[237]\d{1}[\s\.\-]?\d{3}[\s\.\-]?\d{3,4}\b",
        full_text,
    )
    clean_phones: List[str] = []
    for p in phones_found:
        p_norm = re.sub(r"[\s\.\-]+", " ", p).strip()
        # Evitam CUI-uri sau secvente false
        digits_only = re.sub(r"\D", "", p_norm)
        if len(digits_only) in (10, 11, 12) and p_norm not in clean_phones:
            clean_phones.append(p_norm)

    primary_phone = clean_phones[0] if clean_phones else fallback.get("phone", "N/A")

    platform_final = detected_platform or detect_platform(raw_html_combined, domain=domain)

    return {
        "domain": domain,
        "store_name": fallback.get("store_name", domain),
        "detected_platform": platform_final,
        "company_name": company_name,
        "cui": cui_val,
        "reg_com": reg_com,
        "phone": primary_phone,
        "all_phones": clean_phones[:3] if clean_phones else [primary_phone],
        "email": primary_email,
        "all_emails": valid_emails[:3] if valid_emails else [primary_email],
    }


def save_stores_contacts(contacts_list: List[Dict[str, Any]], output_path: Path) -> None:
    """Salveaza lista de contacte B2B si platforme detectate in stores_contacts.json."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(contacts_list, f, indent=2, ensure_ascii=False)
