"""
=============================================================================
MASTER LICENSED & REGULATED BROKERS HARVESTER (ALL 15 GLOBAL AUTHORITIES)
Author: VasileDev / IsBrokerSafe.com Engine
Downloads / compiles licensed brokers across:
1. CONSOB (Italy)        6. CNMV (Spain)         11. MAS (Singapore)
2. FCA (UK)              7. AMF / ACPR (France)  12. SFC (Hong Kong)
3. CySEC (EU / Cyprus)   8. FINMA (Switzerland)  13. DFSA (Dubai / UAE)
4. BaFin (Germany)       9. ASIC (Australia)     14. FSCA (South Africa)
5. SEC & CFTC/NFA (US)  10. CSA & CIRO (Canada)  15. FMA (Austria)
=============================================================================
"""

import os
import sys
import re
import csv
import json
import sqlite3
import urllib.request
import ssl
from datetime import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

if os.path.exists('/var/data'):
    PERSISTENT_DIR = '/var/data'
else:
    PERSISTENT_DIR = os.path.dirname(os.path.abspath(__file__))

DB_PATH = os.path.join(PERSISTENT_DIR, "database.db")
CSV_OUT_DIR = r"C:\Users\bratu\Desktop\ECOSISTEM_PLATFORME_LIVE\Campanii_B2B_Outbound_IsBrokerSafe"
CSV_OUT_PATH = os.path.join(CSV_OUT_DIR, "Master_15_Regulators_Licensed_Brokers_2026.csv")

# Vasile's existing affiliate partner domains (Tier-1 Verified Partner -> 95-98/100 + Affiliate CTA)
AFFILIATE_PARTNER_DOMAINS = {
    "capital.com", "exness.com", "etoro.com", "avatrade.com", "pocketoption.com",
    "interactivebrokers.com", "xm.com", "plus500.com", "pepperstone.com",
    "icmarkets.com", "oanda.com", "ig.com", "sabiotrade.com", "apextraderfunding.com"
}

def slugify(text):
    text = re.sub(r'[^\w\s.-]', '', str(text)).strip().lower()
    return re.sub(r'[-\s.]+', '-', text)

def init_regulated_db():
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode = WAL;")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS regulated_brokers_registry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT UNIQUE,
            entity_name TEXT NOT NULL,
            domain TEXT UNIQUE,
            regulator TEXT NOT NULL,
            license_number TEXT,
            jurisdiction TEXT,
            category TEXT,
            contact_email TEXT,
            official_register_url TEXT,
            is_affiliate_partner INTEGER DEFAULT 0,
            claim_status TEXT DEFAULT 'UNCLAIMED_LICENSED',
            trust_score INTEGER DEFAULT 72,
            created_at TEXT
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reg_brokers_domain ON regulated_brokers_registry(domain);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reg_brokers_regulator ON regulated_brokers_registry(regulator);")
    conn.commit()
    conn.close()


# Comprehensive dataset across all 15 regulatory authorities
# Format: (entity_name, domain, regulator, license_number, jurisdiction, category, contact_email, official_register_url)
LICENSED_BROKERS_15_AUTHORITIES = [
    # =========================================================================
    # 1. CONSOB (Italy) - Albo SIM & Succursali Imprese di Investimento
    # =========================================================================
    ("Directa SIM S.p.A.", "directa.it", "CONSOB (Italy)", "Albo SIM n. 59", "IT", "Stock & Derivatives Broker", "directa@directa.it", "https://www.consob.it/web/area-pubblica/sim"),
    ("FinecoBank S.p.A.", "finecobank.com", "CONSOB (Italy)", "Banca d'Italia / CONSOB n. 5442", "IT", "Multi-Asset Bank & Broker", "helpdesk@finecobank.com", "https://www.consob.it/web/area-pubblica/sim"),
    ("BG SAXO SIM S.p.A.", "bgsaxo.it", "CONSOB (Italy)", "Albo SIM n. 296", "IT", "Multi-Asset & FX Broker", "supporto@bgsaxo.it", "https://www.consob.it/web/area-pubblica/sim"),
    ("Webank (Banco BPM)", "webank.it", "CONSOB (Italy)", "Albo Banche / CONSOB", "IT", "Online Trading & Banking", "webank@webank.it", "https://www.consob.it/web/area-pubblica/sim"),
    ("Banca Sella Trading (Sella.it)", "sella.it", "CONSOB (Italy)", "Albo Banche n. 5090", "IT", "Online Trading Platform", "info@sella.it", "https://www.consob.it/web/area-pubblica/sim"),
    ("Investimenti & Trading (Banca Akros)", "bancaakros.it", "CONSOB (Italy)", "Albo Banche n. 5328", "IT", "Investment Banking & Broker", "info@bancaakros.it", "https://www.consob.it/web/area-pubblica/sim"),
    ("ActivTrades Europe SA (Succursale Italia)", "activtrades.eu", "CONSOB (Italy)", "Elenco Imprese UE / CSSF", "IT", "Forex & CFD Broker", "italiandesk@activtrades.eu", "https://www.consob.it/web/area-pubblica/sim"),
    ("Equita SIM S.p.A.", "equita.eu", "CONSOB (Italy)", "Albo SIM n. 67", "IT", "Institutional & Retail Broker", "info@equita.eu", "https://www.consob.it/web/area-pubblica/sim"),
    ("Intermonte SIM S.p.A.", "intermonte.it", "CONSOB (Italy)", "Albo SIM n. 90", "IT", "Investment & Brokerage SIM", "info@intermonte.it", "https://www.consob.it/web/area-pubblica/sim"),
    ("Moneyfarm SIM", "moneyfarm.com", "CONSOB (Italy)", "Albo SIM / FCA Authorized", "IT", "Digital Wealth & ETF Broker", "info@moneyfarm.com", "https://www.consob.it/web/area-pubblica/sim"),

    # =========================================================================
    # 2. FCA (UK) - Financial Conduct Authority Register
    # =========================================================================
    ("IG Markets Limited", "ig.com", "FCA (UK)", "FRN 195355", "UK", "Tier-1 Multi-Asset & Spread Betting", "helpdesk.uk@ig.com", "https://register.fca.org.uk/s/firm?id=001b000000MfefxAAB"),
    ("CMC Markets UK plc", "cmcmarkets.com", "FCA (UK)", "FRN 173730", "UK", "Forex, CFD & Spread Betting", "clientmanagement@cmcmarkets.co.uk", "https://register.fca.org.uk/s/"),
    ("Capital Com (UK) Limited", "capital.com", "FCA (UK)", "FRN 793714", "UK", "Tier-1 Regulated Broker", "support@capital.com", "https://register.fca.org.uk/s/"),
    ("Plus500UK Ltd", "plus500.com", "FCA (UK)", "FRN 509909", "UK", "CFD Trading Platform", "support@plus500.com", "https://register.fca.org.uk/s/"),
    ("City Index (StoneX Financial Ltd)", "cityindex.com", "FCA (UK)", "FRN 446717", "UK", "Spread Betting & FX Broker", "support@cityindex.co.uk", "https://register.fca.org.uk/s/"),
    ("Spreadex Limited", "spreadex.com", "FCA (UK)", "FRN 190941", "UK", "Financial Spread Betting & CFDs", "info@spreadex.com", "https://register.fca.org.uk/s/"),
    ("Saxo Capital Markets UK Ltd", "home.saxo", "FCA (UK)", "FRN 551422", "UK", "Multi-Asset Investment Bank", "uksupport@saxobank.com", "https://register.fca.org.uk/s/"),
    ("Tickmill UK Ltd", "tickmill.co.uk", "FCA (UK)", "FRN 717270", "UK", "ECN Forex & CFD Broker", "support@tickmill.co.uk", "https://register.fca.org.uk/s/"),
    ("FxPro UK Limited", "fxpro.com", "FCA (UK)", "FRN 509956", "UK", "Forex & CFD Broker", "support@fxpro.com", "https://register.fca.org.uk/s/"),
    ("Admirals (Admiral Markets UK Ltd)", "admiralmarkets.com", "FCA (UK)", "FRN 595450", "UK", "Multi-Asset & FX Broker", "global@admiralmarkets.com", "https://register.fca.org.uk/s/"),
    ("ThinkMarkets (TF Global Markets UK)", "thinkmarkets.com", "FCA (UK)", "FRN 629628", "UK", "Multi-Asset Forex Broker", "support@thinkmarkets.com", "https://register.fca.org.uk/s/"),
    ("Darwinex (Tradeslide Trading Tech)", "darwinex.com", "FCA (UK)", "FRN 586466", "UK", "Social Asset Mgmt & FX Broker", "info@darwinex.com", "https://register.fca.org.uk/s/"),
    ("LMAX Global (LMAX Broker Ltd)", "lmax.com", "FCA (UK)", "FRN 783200", "UK", "Institutional FX & Crypto Exchange", "info@lmax.com", "https://register.fca.org.uk/s/"),
    ("Hantec Markets Limited", "hmarkets.com", "FCA (UK)", "FRN 502635", "UK", "Forex & Bullion Broker", "info-uk@hmarkets.com", "https://register.fca.org.uk/s/"),
    ("Equiti Capital UK Limited", "equiticapital.co.uk", "FCA (UK)", "FRN 528328", "UK", "Prime Brokerage & FX", "support.uk@equiti.com", "https://register.fca.org.uk/s/"),
    ("INFINOX Capital Ltd", "infinox.com", "FCA (UK)", "FRN 501057", "UK", "ECN Forex & CFD Broker", "support@infinox.com", "https://register.fca.org.uk/s/"),
    ("Valutrades Limited", "valutrades.com", "FCA (UK)", "FRN 586541", "UK", "ECN Forex Broker", "support@valutrades.com", "https://register.fca.org.uk/s/"),
    ("ATFX UK (AT Global Markets UK Ltd)", "atfx.com", "FCA (UK)", "FRN 760555", "UK", "Institutional & Retail FX", "cs.uk@atfx.com", "https://register.fca.org.uk/s/"),
    ("Hargreaves Lansdown Asset Mgmt", "hl.co.uk", "FCA (UK)", "FRN 115248", "UK", "Stockbroker & ISA Platform", "helpdesk@hl.co.uk", "https://register.fca.org.uk/s/"),
    ("AJ Bell Securities Limited", "ajbell.co.uk", "FCA (UK)", "FRN 155593", "UK", "Investment & Stockbroker", "help@ajbell.co.uk", "https://register.fca.org.uk/s/"),
    ("Interactive Investor Services", "ii.co.uk", "FCA (UK)", "FRN 141282", "UK", "Retail Stock & Fund Broker", "service@ii.co.uk", "https://register.fca.org.uk/s/"),
    ("Trading 212 UK Ltd", "trading212.com", "FCA (UK)", "FRN 609146", "UK", "Zero-Commission Stocks & CFDs", "info@trading212.com", "https://register.fca.org.uk/s/"),
    ("Freetrade Limited", "freetrade.io", "FCA (UK)", "FRN 783189", "UK", "Mobile Stock Brokerage", "hello@freetrade.io", "https://register.fca.org.uk/s/"),

    # =========================================================================
    # 3. CySEC (EU / Cyprus) - Cyprus Investment Firms (CIFs)
    # =========================================================================
    ("eToro (Europe) Ltd", "etoro.com", "CySEC (EU / Cyprus)", "CIF 109/10", "CY", "Social Trading & Multi-Asset", "partners@etoro.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("Exness (Cy) Ltd", "exness.com", "CySEC (EU / Cyprus)", "CIF 178/12", "CY", "Global Multi-Asset Broker", "support@exness.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("XM / Trading Point of Financial Instruments", "xm.com", "CySEC (EU / Cyprus)", "CIF 120/10", "CY", "Forex & Commodity Broker", "support@xm.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("IC Markets (EU) Ltd", "icmarkets.eu", "CySEC (EU / Cyprus)", "CIF 362/18", "CY", "Raw Spread ECN Broker", "support@icmarkets.eu", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("Orbex Limited", "orbex.com.cy", "CySEC (EU / Cyprus)", "CIF 121/10", "CY", "Forex & Metals CIF", "support@orbex.com.cy", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("HF Markets (Europe) Ltd (HFM)", "hfm.com", "CySEC (EU / Cyprus)", "CIF 183/12", "CY", "Multi-Asset & Copy Trading", "support@hfm.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("Exinity Limited (FXTM)", "forextime.com", "CySEC (EU / Cyprus)", "CIF 185/12", "CY", "Forex & CFD Broker", "info@forextime.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("Windsor Brokers Ltd", "windsorbrokers.eu", "CySEC (EU / Cyprus)", "CIF 030/04", "CY", "Regulated EU Forex Broker", "support@windsorbrokers.eu", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("IronFX (Notesco Financial Services)", "ironfx.eu", "CySEC (EU / Cyprus)", "CIF 125/10", "CY", "Global FX & CFD Broker", "support@ironfx.eu", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("Skilling Limited", "skilling.com", "CySEC (EU / Cyprus)", "CIF 357/18", "CY", "Scandinavian FinTech CFD Broker", "support@skilling.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("NAGA Markets Europe Ltd", "nagamarkets.com", "CySEC (EU / Cyprus)", "CIF 204/13", "CY", "Social Investing Network", "support@nagamarkets.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("Libertex (Indication Investments Ltd)", "libertex.com", "CySEC (EU / Cyprus)", "CIF 164/12", "CY", "Online CFD & Stock Platform", "info@libertex.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("easyMarkets (EF Worldwide Ltd)", "easymarkets.com", "CySEC (EU / Cyprus)", "CIF 079/07", "CY", "Fixed Spread FX & Options", "support@easymarkets.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("Just2Trade Online Ltd", "just2trade.online", "CySEC (EU / Cyprus)", "CIF 281/15", "CY", "Direct Market Access Broker", "24_support@just2trade.online", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("RoboMarkets Ltd", "robomarkets.com", "CySEC (EU / Cyprus)", "CIF 191/13", "CY", "European Multi-Asset Broker", "info@robomarkets.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("SquaredFinancial (CY) Limited", "squaredfinancial.com", "CySEC (EU / Cyprus)", "CIF 329/17", "CY", "FinTech Brokerage", "support@squaredfinancial.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("TopFX Ltd", "topfx.com.sc", "CySEC (EU / Cyprus)", "CIF 138/11", "CY", "Prime Liquidity & cTrader Broker", "support@topfx.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("Freedom Finance Europe Ltd (Freedom24)", "freedom24.com", "CySEC (EU / Cyprus)", "CIF 275/15", "CY", "European Stock & ETF Broker", "info@freedom24.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("CAPEX.com (Key Way Investments Ltd)", "capex.com", "CySEC (EU / Cyprus)", "CIF 292/16", "CY", "Multi-Licensed Global Broker", "support@capex.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("Colmex Pro Ltd", "colmexpro.com", "CySEC (EU / Cyprus)", "CIF 123/10", "CY", "Equities & FX CFD Broker", "support@colmexpro.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("Alvexo (VPR Safe Financial Group)", "alvexo.com", "CySEC (EU / Cyprus)", "CIF 236/14", "CY", "Regulated Investment Firm", "support@alvexo.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("Fibo Group Holdings Ltd", "fibogroup.eu", "CySEC (EU / Cyprus)", "CIF 118/10", "CY", "Forex & Spot Metals CIF", "service@fibogroup.eu", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("Tickmill Europe Ltd", "tickmill.eu", "CySEC (EU / Cyprus)", "CIF 278/15", "CY", "Low-Spread EU Forex Broker", "support@tickmill.eu", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("Deriv Investments (Europe) Ltd", "deriv.com", "CySEC (EU / Cyprus)", "MFSA / EU MiFID Passport", "CY", "Synthetic Indices & FX", "support@deriv.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),
    ("AvaTrade EU Ltd", "avatrade.com", "CySEC (EU / Cyprus)", "CBI C53877 / CySEC", "CY", "Multi-Regulated FX & Options", "cs@avatrade.com", "https://www.cysec.gov.cy/en-GB/entities/investment-firms/cypriot/"),

    # =========================================================================
    # 4. BaFin (Germany) - Zugelassene Finanzdienstleistungsinstitute
    # =========================================================================
    ("Trade Republic Bank GmbH", "traderepublic.com", "BaFin (Germany)", "BaFin ID 10150363", "DE", "Neobroker & Savings Platform", "service@traderepublic.com", "https://portal.mvp.bafin.de/database/InstInfo/"),
    ("Scalable Capital GmbH", "scalable.capital", "BaFin (Germany)", "BaFin ID 10144391", "DE", "Prime Neo-Broker & ETF Wealth", "service@scalable.capital", "https://portal.mvp.bafin.de/database/InstInfo/"),
    ("flatexDEGIRO Bank AG", "flatex.de", "BaFin (Germany)", "BaFin ID 10117761", "DE", "Pan-European Online Broker", "info@flatex.de", "https://portal.mvp.bafin.de/database/InstInfo/"),
    ("FXFlat Bank GmbH", "fxflat.com", "BaFin (Germany)", "BaFin ID 10109603", "DE", "German Regulated Forex & Futures", "service@fxflat.com", "https://portal.mvp.bafin.de/database/InstInfo/"),
    ("GBE brokers Ltd (Niederlassung Deutschland)", "gbebrokers.com", "BaFin (Germany)", "BaFin Reg. 149674", "DE", "Institutional Liquidity & FX", "info@gbebrokers.com", "https://portal.mvp.bafin.de/database/InstInfo/"),
    ("WH SelfInvest GmbH", "whselfinvest.de", "BaFin (Germany)", "BaFin ID 120089", "DE", "Futures, CFDs & NanoTrader", "info@whselfinvest.de", "https://portal.mvp.bafin.de/database/InstInfo/"),
    ("Smartbroker+ (Smartbroker Holding AG)", "smartbrokerplus.de", "BaFin (Germany)", "BaFin / Baader Bank", "DE", "German Discount Broker", "kundenservice@smartbrokerplus.de", "https://portal.mvp.bafin.de/database/InstInfo/"),
    ("Consorsbank (BNP Paribas S.A.)", "consorsbank.de", "BaFin (Germany)", "BaFin ID 10102059", "DE", "Direct Bank & Securities Broker", "info@consorsbank.de", "https://portal.mvp.bafin.de/database/InstInfo/"),
    ("comdirect (Commerzbank AG)", "comdirect.de", "BaFin (Germany)", "BaFin ID 100003", "DE", "Online Brokerage & Banking", "info@comdirect.de", "https://portal.mvp.bafin.de/database/InstInfo/"),
    ("finanzen.net zero GmbH", "finanzen-zero.net", "BaFin (Germany)", "BaFin / DonauCapital", "DE", "Zero-Fee German Stockbroker", "kontakt@finanzen-zero.net", "https://portal.mvp.bafin.de/database/InstInfo/"),

    # =========================================================================
    # 5. SEC & CFTC / NFA (US) - Registered RFEDs, FCMs & Broker-Dealers
    # =========================================================================
    ("Interactive Brokers LLC", "interactivebrokers.com", "SEC & CFTC (US)", "NFA ID 0258600 / SEC 8-47257", "US", "Tier-1 Global Electronic Broker", "ibkr@interactivebrokers.com", "https://www.nfa.futures.org/basicnet/"),
    ("OANDA Corporation", "oanda.com", "SEC & CFTC (US)", "NFA ID 0325821", "US", "Retail Foreign Exchange Dealer", "frontdesk@oanda.com", "https://www.nfa.futures.org/basicnet/"),
    ("FOREX.com (StoneX Financial Inc.)", "forex.com", "SEC & CFTC (US)", "NFA ID 0339826", "US", "CFTC Regulated US Forex Dealer", "support@forex.com", "https://www.nfa.futures.org/basicnet/"),
    ("Charles Schwab & Co., Inc.", "schwab.com", "SEC & CFTC (US)", "SEC 8-16514 / CRD 5393", "US", "Full-Service US Brokerage", "clientservice@schwab.com", "https://brokercheck.finra.org/"),
    ("Tastytrade, Inc.", "tastytrade.com", "SEC & CFTC (US)", "SEC 8-69739 / NFA 0500856", "US", "Options, Futures & Stock Broker", "support@tastytrade.com", "https://brokercheck.finra.org/"),
    ("TradeStation Securities, Inc.", "tradestation.com", "SEC & CFTC (US)", "SEC 8-48711 / NFA 0274990", "US", "Algorithmic Futures & Equities", "clientexperience@tradestation.com", "https://brokercheck.finra.org/"),
    ("NinjaTrader Clearing, LLC", "ninjatrader.com", "SEC & CFTC (US)", "NFA ID 0309379", "US", "Futures Commission Merchant", "support@ninjatrader.com", "https://www.nfa.futures.org/basicnet/"),
    ("Robinhood Financial LLC", "robinhood.com", "SEC & CFTC (US)", "SEC 8-69188 / CRD 165998", "US", "Commission-Free Trading App", "support@robinhood.com", "https://brokercheck.finra.org/"),
    ("Webull Financial LLC", "webull.com", "SEC & CFTC (US)", "SEC 8-69978 / CRD 289063", "US", "US Equities & Options Broker", "customerservices@webull.us", "https://brokercheck.finra.org/"),
    ("AMP Futures (AMP Global Clearing)", "ampfutures.com", "SEC & CFTC (US)", "NFA ID 0412490", "US", "Ultra-Low Cost Futures FCM", "helpdesk@ampfutures.com", "https://www.nfa.futures.org/basicnet/"),
    ("Optimus Futures LLC", "optimusfutures.com", "SEC & CFTC (US)", "NFA ID 0360978", "US", "Independent Introducing Broker", "general@optimusfutures.com", "https://www.nfa.futures.org/basicnet/"),
    ("Tradier Brokerage, Inc.", "tradier.com", "SEC & CFTC (US)", "SEC 8-35318 / CRD 104235", "US", "API-First Equities & Options", "service@tradierbrokerage.com", "https://brokercheck.finra.org/"),
    ("Trading.com Markets Inc.", "trading.com", "SEC & CFTC (US)", "NFA ID 0516820", "US", "US Registered Retail FX Dealer", "support.us@trading.com", "https://www.nfa.futures.org/basicnet/"),
    ("Ironbeam, Inc.", "ironbeam.com", "SEC & CFTC (US)", "NFA ID 0425912", "US", "Futures Clearing & Execution", "sales@ironbeam.com", "https://www.nfa.futures.org/basicnet/"),

    # =========================================================================
    # 6. CNMV (Spain) - Empresas de Servicios de Inversión
    # =========================================================================
    ("XTB Spain (X-Trade Brokers DM SA)", "xtb.com", "CNMV (Spain)", "CNMV Reg. n. 40", "ES", "Listed Multi-Asset & FX Broker", "sales.es@xtb.com", "https://www.cnmv.es/portal/consultas/"),
    ("iBroker Global Markets SV, S.A.", "ibroker.es", "CNMV (Spain)", "CNMV Reg. n. 260", "ES", "Spanish Futures & Derivatives SV", "clientes@ibroker.es", "https://www.cnmv.es/portal/consultas/"),
    ("Renta 4 Banco, S.A.", "r4.com", "CNMV (Spain)", "CNMV / Banco de España 0083", "ES", "Investment Bank & Broker", "clientes@renta4.es", "https://www.cnmv.es/portal/consultas/"),
    ("ClickTrade (iBroker / Auriga)", "clicktrade.es", "CNMV (Spain)", "CNMV Reg. n. 260", "ES", "Spanish Stock & CFD Broker", "info@clicktrade.es", "https://www.cnmv.es/portal/consultas/"),
    ("MyInvestor Banco S.A.", "myinvestor.es", "CNMV (Spain)", "Banco de España n. 1544", "ES", "Neobank & Index Fund Broker", "info@myinvestor.es", "https://www.cnmv.es/portal/consultas/"),
    ("Activotrade Valores AV, S.A.", "activotrade.com", "CNMV (Spain)", "CNMV Reg. n. 279", "ES", "Agencia de Valores", "info@activotrade.com", "https://www.cnmv.es/portal/consultas/"),
    ("HeyTrade (Beka Finance SV)", "heytrade.com", "CNMV (Spain)", "CNMV Reg. n. 36", "ES", "Mobile Investment Platform", "support@heytrade.com", "https://www.cnmv.es/portal/consultas/"),
    ("GVC Gaesco Valores SV, S.A.", "gvcgaesco.es", "CNMV (Spain)", "CNMV Reg. n. 182", "ES", "Sociedad de Valores", "atencioncliente@gvcgaesco.es", "https://www.cnmv.es/portal/consultas/"),

    # =========================================================================
    # 7. AMF / ACPR (France) - Prestataires de Services d'Investissement (PSI)
    # =========================================================================
    ("Bourse Direct SA", "boursedirect.fr", "AMF (France)", "ACPR / AMF CIB 11448", "FR", "French Online Stock & Derivatives", "service.clientele@boursedirect.fr", "https://www.regafi.fr/"),
    ("BoursoBank (Boursorama SA)", "boursobank.com", "AMF (France)", "ACPR CIB 40618", "FR", "Online Banking & Stock Trading", "service.commercial@boursobank.com", "https://www.regafi.fr/"),
    ("Fortuneo (Arkéa Direct Bank)", "fortuneo.fr", "AMF (France)", "ACPR CIB 14518", "FR", "French Online Brokerage", "clientele@fortuneo.fr", "https://www.regafi.fr/"),
    ("ProRealTime (IT-Finance SAS)", "prorealtime.com", "AMF (France)", "ACPR / AMF PSI 11433", "FR", "Charting & Brokerage Execution", "broker@prorealtime.com", "https://www.regafi.fr/"),
    ("Saxo Banque (France)", "saxobanque.fr", "AMF (France)", "ACPR CIB 15868", "FR", "Multi-Asset Trading Bank", "infos@saxobanque.fr", "https://www.regafi.fr/"),
    ("EasyBourse (La Banque Postale)", "easybourse.com", "AMF (France)", "ACPR CIB 16188", "FR", "Online Stockbroker", "serviceclient@easybourse.com", "https://www.regafi.fr/"),

    # =========================================================================
    # 8. FINMA (Switzerland) - Authorized Banks & Securities Firms
    # =========================================================================
    ("Swissquote Bank SA", "swissquote.com", "FINMA (Switzerland)", "FINMA Bank License CHE-101.322.632", "CH", "Swiss Online Trading Bank", "info@swissquote.ch", "https://www.finma.ch/en/finma-public/authorised-institutions-individuals-and-products/"),
    ("Dukascopy Bank SA", "dukascopy.com", "FINMA (Switzerland)", "FINMA Bank License CHE-112.008.962", "CH", "Swiss ECN Forex & Banking", "info@dukascopy.com", "https://www.finma.ch/en/finma-public/authorised-institutions-individuals-and-products/"),
    ("Cornèrtrader (Cornèr Banca SA)", "cornertrader.ch", "FINMA (Switzerland)", "FINMA Bank License CHE-105.962.409", "CH", "Swiss Multi-Asset Trading Desk", "info@cornertrader.ch", "https://www.finma.ch/en/finma-public/authorised-institutions-individuals-and-products/"),
    ("Saxo Bank (Schweiz) AG", "saxobank.ch", "FINMA (Switzerland)", "FINMA Bank License CHE-106.798.353", "CH", "Swiss Institutional & Retail FX", "info@saxobank.ch", "https://www.finma.ch/en/finma-public/authorised-institutions-individuals-and-products/"),
    ("Sygnum Bank AG", "sygnum.com", "FINMA (Switzerland)", "FINMA Digital Asset Bank License", "CH", "Regulated Swiss Crypto Bank", "info@sygnum.com", "https://www.finma.ch/en/finma-public/authorised-institutions-individuals-and-products/"),
    ("AMINA Bank AG (formerly SEBA Bank)", "aminagroup.com", "FINMA (Switzerland)", "FINMA Bank & Securities Dealer", "CH", "Swiss Crypto & Digital Asset Bank", "info@aminagroup.com", "https://www.finma.ch/en/finma-public/authorised-institutions-individuals-and-products/"),

    # =========================================================================
    # 9. ASIC (Australia) - Australian Financial Services (AFS) Licensees
    # =========================================================================
    ("Pepperstone Group Limited", "pepperstone.com", "ASIC (Australia)", "AFSL 414530", "AU", "Tier-1 ECN Forex & CFD Broker", "support@pepperstone.com", "https://connectonline.asic.gov.au/"),
    ("IC Markets (International Capital Markets)", "icmarkets.com", "ASIC (Australia)", "AFSL 335692", "AU", "True ECN Forex Broker", "support@icmarkets.com", "https://connectonline.asic.gov.au/"),
    ("FP Markets (First Prudential Markets)", "fpmarkets.com", "ASIC (Australia)", "AFSL 286354", "AU", "DMA Equities & Raw ECN FX", "support@fpmarkets.com", "https://connectonline.asic.gov.au/"),
    ("Eightcap Pty Ltd", "eightcap.com", "ASIC (Australia)", "AFSL 391441", "AU", "Crypto Derivatives & FX Broker", "global@eightcap.com", "https://connectonline.asic.gov.au/"),
    ("GO Markets Pty Ltd", "gomarkets.com", "ASIC (Australia)", "AFSL 254963", "AU", "Australian MT4/MT5 FX Broker", "support@gomarkets.com", "https://connectonline.asic.gov.au/"),
    ("Axi (AxiCorp Financial Services Pty)", "axi.com", "ASIC (Australia)", "AFSL 318232", "AU", "Global FX & Copy Trading", "service@axi.com", "https://connectonline.asic.gov.au/"),
    ("Vantage Global Prime Pty Ltd", "vantagemarkets.com", "ASIC (Australia)", "AFSL 428901", "AU", "Multi-Asset CFD Broker", "support@vantagemarkets.com", "https://connectonline.asic.gov.au/"),
    ("TMGM (Trademax Australia Limited)", "tmgm.com", "ASIC (Australia)", "AFSL 436416", "AU", "Australian ECN CFD Broker", "support@tmgm.com", "https://connectonline.asic.gov.au/"),
    ("ACY Securities Pty Ltd", "acy.com", "ASIC (Australia)", "AFSL 403863", "AU", "Multi-Asset & Institutional FX", "support@acy.com", "https://connectonline.asic.gov.au/"),
    ("Fusion Markets (Gleneagle Asset Mgmt)", "fusionmarkets.com", "ASIC (Australia)", "AFSL 385620", "AU", "Ultra-Low Cost Australian FX", "help@fusionmarkets.com", "https://connectonline.asic.gov.au/"),
    ("Blueberry Markets Pty Ltd", "blueberrymarkets.com", "ASIC (Australia)", "AFSL 545929", "AU", "Retail Forex & Synthetics", "global@blueberrymarkets.com", "https://connectonline.asic.gov.au/"),
    ("Global Prime Pty Ltd", "globalprime.com", "ASIC (Australia)", "AFSL 385620", "AU", "A-Book Institutional Execution", "support@globalprime.com", "https://connectonline.asic.gov.au/"),
    ("BlackBull Markets", "blackbull.com", "ASIC (Australia)", "FMA FSP403326 / ASIC", "AU", "Prime ECN & TradingView Broker", "support@blackbull.com", "https://connectonline.asic.gov.au/"),
    ("Moneta Markets", "monetamarkets.com", "ASIC (Australia)", "AFSL 428901 / FSCA 47490", "AU", "Global FX & Indices Broker", "support@monetamarkets.com", "https://connectonline.asic.gov.au/"),
    ("Stake (Hellostake Limited)", "hellostake.com", "ASIC (Australia)", "AFSL 548196", "AU", "ASX & Wall St Stockbroker", "support@hellostake.com", "https://connectonline.asic.gov.au/"),
    ("SelfWealth Limited", "selfwealth.com.au", "ASIC (Australia)", "AFSL 421789", "AU", "Flat-Fee Australian Stockbroker", "support@selfwealth.com.au", "https://connectonline.asic.gov.au/"),

    # =========================================================================
    # 10. CSA & OSC / CIRO (Canada) - Regulated Investment Dealers
    # =========================================================================
    ("Questrade, Inc.", "questrade.com", "CSA & OSC (Canada)", "CIRO / IIROC Dealer Member", "CA", "Canadian Online Brokerage & FX", "support@questrade.com", "https://www.ciro.ca/"),
    ("Wealthsimple Investments Inc.", "wealthsimple.com", "CSA & OSC (Canada)", "CIRO Regulated Dealer", "CA", "Canadian Stock & Crypto Platform", "support@wealthsimple.com", "https://www.ciro.ca/"),
    ("Qtrade Direct Investing", "qtrade.ca", "CSA & OSC (Canada)", "CIRO / CIPF Member", "CA", "Canadian Discount Broker", "customersupport@qtrade.ca", "https://www.ciro.ca/"),
    ("Friedberg Direct (Friedberg Mercantile)", "friedbergdirect.com", "CSA & OSC (Canada)", "CIRO Regulated FX Dealer", "CA", "Canadian Forex & CFD Broker", "info@friedbergdirect.com", "https://www.ciro.ca/"),
    ("VirtualBrokers (CI Investment Services)", "virtualbrokers.com", "CSA & OSC (Canada)", "CIRO / CIPF Regulated", "CA", "Canadian Equities & Options", "Track@virtualbrokers.com", "https://www.ciro.ca/"),

    # =========================================================================
    # 11. MAS (Singapore) - Capital Markets Services (CMS) Licensees
    # =========================================================================
    ("Phillip Securities Pte Ltd (POEMS)", "poems.com.sg", "MAS (Singapore)", "CMS100043", "SG", "Singapore Multi-Asset Broker", "talktophillip@phillip.com.sg", "https://eservices.mas.gov.sg/fid"),
    ("Moomoo Financial Singapore Pte. Ltd.", "moomoo.com", "MAS (Singapore)", "CMS101000", "SG", "Global Stock & Options Platform", "clientservice@sg.moomoo.com", "https://eservices.mas.gov.sg/fid"),
    ("Tiger Brokers (Singapore) Pte. Ltd.", "itiger.com", "MAS (Singapore)", "CMS100869", "SG", "Asian & US Equities Broker", "service@tigerbrokers.com.sg", "https://eservices.mas.gov.sg/fid"),
    ("UOB Kay Hian Private Limited", "utrade.com.sg", "MAS (Singapore)", "CMS100050", "SG", "Institutional & Retail Brokerage", "cs@uobkayhian.com", "https://eservices.mas.gov.sg/fid"),
    ("CGS International Securities Singapore", "cgsi.com", "MAS (Singapore)", "CMS100005", "SG", "Pan-Asian Financial Broker", "clientservices.sg@cgsi.com", "https://eservices.mas.gov.sg/fid"),

    # =========================================================================
    # 12. SFC (Hong Kong) - Licensed Corporations
    # =========================================================================
    ("Futu Securities International (HK) Ltd", "futuhk.com", "SFC (Hong Kong)", "SFC CE No. AZT137", "HK", "Hong Kong & US Equities Broker", "cs@futuhk.com", "https://apps.sfc.hk/publicregWeb/"),
    ("BOOM Securities (H.K.) Limited", "boom.com", "SFC (Hong Kong)", "SFC CE No. AEF808", "HK", "Multi-Market Asian Stockbroker", "service@boom.com", "https://apps.sfc.hk/publicregWeb/"),
    ("Bright Smart Securities International", "bsgroup.com.hk", "SFC (Hong Kong)", "SFC CE No. AAF544", "HK", "HKEX Listed Brokerage", "cs@bsgroup.com.hk", "https://apps.sfc.hk/publicregWeb/"),
    ("KGI Asia Limited", "kgi.com.hk", "SFC (Hong Kong)", "SFC CE No. AEL221", "HK", "Wealth Management & Brokerage", "info@kgi.com", "https://apps.sfc.hk/publicregWeb/"),
    ("Emperor Financial International", "empfs.com", "SFC (Hong Kong)", "SFC CE No. AAJ097", "HK", "Bullion & Forex HK Broker", "cs@empfs.com", "https://apps.sfc.hk/publicregWeb/"),

    # =========================================================================
    # 13. DFSA (Dubai / UAE) - DIFC & UAE Regulated Financial Firms
    # =========================================================================
    ("MultiBank Group (MEX Atlantic / DIFC)", "multibankfx.com", "DFSA (Dubai / UAE)", "DFSA Ref. F007340 / SCA", "AE", "Global Financial Derivatives", "cs@multibankfx.com", "https://www.dfsa.ae/public-register"),
    ("CFI Financial (Credit Financier Invest)", "cfifinancial.com", "DFSA (Dubai / UAE)", "DFSA Ref. F003933", "AE", "MENA Multi-Asset & FX Leader", "uae@cfifinancial.com", "https://www.dfsa.ae/public-register"),
    ("Century Financial Consultancy LLC", "centuryfinancial.ae", "DFSA (Dubai / UAE)", "SCA Cat. 1 / UAE Licensed", "AE", "UAE Investment & Trading", "info@centuryfinancial.ae", "https://www.dfsa.ae/public-register"),
    ("HYCM (Henyep Capital Markets DIFC)", "hycm.com", "DFSA (Dubai / UAE)", "DFSA Ref. F000048 / FCA", "AE", "Multi-Regulated Forex Broker", "support@hycm.com", "https://www.dfsa.ae/public-register"),
    ("ADSS (ADS Securities LLC)", "adss.com", "DFSA (Dubai / UAE)", "SCA / Central Bank UAE", "AE", "Abu Dhabi Institutional & Retail FX", "info@adss.com", "https://www.dfsa.ae/public-register"),
    ("Amana Capital", "amanacapital.com", "DFSA (Dubai / UAE)", "DFSA Ref. F003269", "AE", "MENA Mobile Trading & FX", "support@amanacapital.com", "https://www.dfsa.ae/public-register"),
    ("INGOT Brokers", "ingotbrokers.com", "DFSA (Dubai / UAE)", "JSC / ASIC / FSA Licensed", "AE", "Multi-Asset Liquidity & FX", "info@ingotbrokers.com", "https://www.dfsa.ae/public-register"),
    ("OneRoyal (Royal Financial Trading)", "oneroyal.com", "DFSA (Dubai / UAE)", "ASIC AFSL 420268 / CySEC", "AE", "Global Forex & Institutional CFD", "support@oneroyal.com", "https://www.dfsa.ae/public-register"),

    # =========================================================================
    # 14. FSCA (South Africa) - Authorized Financial Services Providers (FSPs)
    # =========================================================================
    ("CMTrading (GCMT South Africa Pty)", "cmtrading.com", "FSCA (South Africa)", "FSP No. 38782", "ZA", "African Forex & Copykat Broker", "support@cmtrading.com", "https://www.fsca.co.za/"),
    ("Khwezi Trade (Khwezi Financial Services)", "khwezitrade.co.za", "FSCA (South Africa)", "FSP No. 44816 / ODP", "ZA", "South African ODP Licensed FX", "info@khwezitrade.co.za", "https://www.fsca.co.za/"),
    ("Markets.com (Finalto South Africa)", "markets.com", "FSCA (South Africa)", "FSP No. 46860 / CySEC", "ZA", "Global Multi-Asset CFD Platform", "support@markets.com", "https://www.fsca.co.za/"),
    ("IFX Brokers Holdings (Pty) Ltd", "ifxbrokers.com", "FSCA (South Africa)", "FSP No. 48021 / ODP", "ZA", "South African ECN Forex Broker", "support@ifxbrokers.com", "https://www.fsca.co.za/"),
    ("EasyEquities (First World Trader Pty)", "easyequities.co.za", "FSCA (South Africa)", "FSP No. 22588", "ZA", "Fractional Shares & TFSA Broker", "helpme@easyequities.co.za", "https://www.fsca.co.za/"),
    ("GT247.com (Purple Group Ltd)", "gt247.com", "FSCA (South Africa)", "FSP No. 46315", "ZA", "South African Derivatives Broker", "supportdesk@gt247.com", "https://www.fsca.co.za/"),
    ("globex360 (Globex360 Pty Ltd)", "globex360.co.za", "FSCA (South Africa)", "FSP No. 50130", "ZA", "FSCA Regulated MT4 Broker", "info@globex360.co.za", "https://www.fsca.co.za/"),

    # =========================================================================
    # 15. FMA (Austria) - Finanzmarktaufsicht Konzessionierte Wertpapierfirmen
    # =========================================================================
    ("Bitpanda Financial Services GmbH", "bitpanda.com", "FMA (Austria)", "FMA MiFID II License 485838k", "AT", "Regulated Crypto & Stocks Broker", "support@bitpanda.com", "https://www.fma.gv.at/en/search-company-database/"),
    ("DADAT Bank (Bankhaus Schelhammer)", "dad.at", "FMA (Austria)", "FMA Bank License FN 58248i", "AT", "Austrian Direct Broker Bank", "office@dad.at", "https://www.fma.gv.at/en/search-company-database/"),
    ("21bitcoin (FIOR Digital GmbH)", "21bitcoin.app", "FMA (Austria)", "FMA VASP Registration", "AT", "Regulated Austrian Bitcoin Broker", "support@21bitcoin.app", "https://www.fma.gv.at/en/search-company-database/"),
    ("Coinfinity GmbH", "coinfinity.co", "FMA (Austria)", "FMA Registered Digital Asset Broker", "AT", "Austrian Crypto Brokerage", "office@coinfinity.co", "https://www.fma.gv.at/en/search-company-database/"),
    ("easybank (BAWAG P.S.K.)", "easybank.at", "FMA (Austria)", "FMA Bank License FN 205340x", "AT", "Austrian Online Bank & Securities", "easy@easybank.at", "https://www.fma.gv.at/en/search-company-database/"),

    # =========================================================================
    # 16. Prop Trading & Institutional FinTech Entities (Global)
    # =========================================================================
    ("FundingPips", "fundingpips.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "UAE / Global", "Prop Trading Firm", "support@fundingpips.com", "https://fundingpips.com"),
    ("Alpha Capital Group", "alphacapitalgroup.uk", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "UK", "Prop Trading Firm", "support@alphacapitalgroup.uk", "https://alphacapitalgroup.uk"),
    ("The5ers (Five Percent Online Ltd)", "the5ers.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "Israel / UK", "Growth Prop Fund", "support@the5ers.com", "https://the5ers.com"),
    ("Goat Funded Trader", "goatfundedtrader.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "Global", "Prop Trading Firm", "support@goatfundedtrader.com", "https://goatfundedtrader.com"),
    ("FundedNext", "fundednext.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "UAE / Global", "Prop Trading Firm", "support@fundednext.com", "https://fundednext.com"),
    ("Blue Guardian", "blueguardian.co.uk", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "UK", "Prop Trading Firm", "support@blueguardian.com", "https://blueguardian.co.uk"),
    ("Instant Funding", "instantfunding.io", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "UK", "Instant Prop Firm", "support@instantfunding.io", "https://instantfunding.io"),
    ("MyFundedFX", "myfundedfx.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "USA", "Prop Trading Firm", "support@myfundedfx.com", "https://myfundedfx.com"),
    ("E8 Markets", "e8markets.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "USA / Global", "Prop Tech Firm", "support@e8markets.com", "https://e8markets.com"),
    ("Maven Trading", "maventrading.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "Canada", "Prop Trading Firm", "support@maventrading.com", "https://maventrading.com"),
    ("Topstep LLC", "topstep.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "USA", "Futures Prop Firm", "support@topstep.com", "https://topstep.com"),
    ("Apex Trader Funding", "apextraderfunding.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "USA", "Futures Prop Firm", "support@apextraderfunding.com", "https://apextraderfunding.com"),
    ("Earn2Trade", "earn2trade.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "USA", "Trading Education & Funding", "support@earn2trade.com", "https://earn2trade.com"),
    ("City Traders Imperium (CTI)", "citytradersimperium.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "UK", "Forex Prop Firm", "support@citytradersimperium.com", "https://citytradersimperium.com"),
    ("Bulenox Futures", "bulenox.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "Cyprus / Global", "Prop Trading Firm", "support@bulenox.com", "https://bulenox.com"),
    ("Audacity Capital", "audacitycapital.co.uk", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "UK", "Funded Trader Program", "support@audacitycapital.co.uk", "https://audacitycapital.co.uk"),
    ("Funded Trading Plus", "fundedtradingplus.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "UK", "Prop Trading Firm", "support@fundedtradingplus.com", "https://fundedtradingplus.com"),
    ("Lux Trading Firm", "luxtradingfirm.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "UK / Slovakia", "Elite Prop Firm", "support@luxtradingfirm.com", "https://luxtradingfirm.com"),
    ("RebelsFunding", "rebelsfunding.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "Czech Republic", "Prop Trading Firm", "support@rebelsfunding.com", "https://rebelsfunding.com"),
    ("FXIFY", "fxify.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "UK / Canada", "Multi-Asset Prop Firm", "support@fxify.com", "https://fxify.com"),
    ("TradeDay", "tradeday.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "USA", "Futures Funding", "support@tradeday.com", "https://tradeday.com"),
    ("Leeloo Trading", "leelootrading.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "USA", "Futures Prop Firm", "support@leelootrading.com", "https://leelootrading.com"),
    ("Uprofit Trader", "uprofittrader.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "USA", "Futures Prop Program", "support@uprofittrader.com", "https://uprofittrader.com"),
    ("Trade The Pool", "tradethepool.com", "Prop Trading / Self-Regulated", "Prop Evaluation Entity", "USA", "Stock & Equities Prop Firm", "support@tradethepool.com", "https://tradethepool.com"),
    ("Finvasia Group", "finvasia.com", "Prop Trading / Self-Regulated", "Institutional FinTech & Liquidity", "UK / India", "Fintech & Broker Gateway", "contact@finvasia.com", "https://finvasia.com"),
    ("Match-Prime Liquidity", "match-prime.com", "Prop Trading / Self-Regulated", "CySEC Regulated Liquidity Provider", "Cyprus", "Institutional FX Liquidity", "contact@match-prime.com", "https://match-prime.com"),
    ("B2Broker", "b2broker.com", "Prop Trading / Self-Regulated", "Institutional Prime of Prime Liquidity", "UAE / UK", "Liquidity & Crypto Gateway", "sales@b2broker.com", "https://b2broker.com"),
    ("Leverate Technological Trading Ltd", "leverate.com", "Prop Trading / Self-Regulated", "CySEC Regulated FinTech Provider", "Israel / Cyprus", "Broker Trading Infrastructure", "sales@leverate.com", "https://leverate.com"),
    ("cTrader / Spotware Systems Ltd", "spotware.com", "Prop Trading / Self-Regulated", "Institutional Trading Platform Vendor", "Cyprus / UK", "Trading Platform Vendor", "connect@spotware.com", "https://spotware.com"),
    ("Devexperts / dxFeed", "devexperts.com", "Prop Trading / Self-Regulated", "Institutional Capital Markets Software", "Germany / USA", "Capital Markets FinTech", "sales@devexperts.com", "https://devexperts.com"),
]


def load_prop_firms_from_lot4():
    """Returns empty list as all 30 Prop Trading & FinTech entities are now embedded directly in LICENSED_BROKERS_15_AUTHORITIES."""
    return []


def run_harvester():
    print("=" * 75)
    print("🌐 HARVESTING & COMPILING LICENSED BROKERS ACROSS ALL 15 AUTHORITIES")
    print("=" * 75)

    init_regulated_db()
    all_records = list(LICENSED_BROKERS_15_AUTHORITIES)

    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode = WAL;")
    cursor = conn.cursor()

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inserted_or_updated = 0
    authority_counts = {}

    csv_rows = []
    for item in all_records:
        entity_name, domain, regulator, license_number, jurisdiction, category, contact_email, official_url = item
        clean_domain = domain.strip().lower().replace("https://", "").replace("http://", "").replace("www.", "").split("/")[0]
        slug = slugify(clean_domain)

        is_aff = 1 if clean_domain in AFFILIATE_PARTNER_DOMAINS else 0
        if is_aff:
            claim_status = "VERIFIED_PARTNER"
            trust_score = 96
        elif "Prop Trading" in regulator:
            claim_status = "UNCLAIMED_PROP_FIRM"
            trust_score = 72
        else:
            claim_status = "UNCLAIMED_LICENSED"
            trust_score = 72

        cursor.execute("""
            INSERT OR REPLACE INTO regulated_brokers_registry
            (slug, entity_name, domain, regulator, license_number, jurisdiction, category, contact_email, official_register_url, is_affiliate_partner, claim_status, trust_score, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            slug, entity_name, clean_domain, regulator, license_number,
            jurisdiction, category, contact_email, official_url,
            is_aff, claim_status, trust_score, now_str
        ))
        inserted_or_updated += 1
        authority_counts[regulator] = authority_counts.get(regulator, 0) + 1

        csv_rows.append({
            "ID": inserted_or_updated,
            "Entity_Name": entity_name,
            "Domain": clean_domain,
            "Regulator": regulator,
            "License_Number": license_number,
            "Jurisdiction": jurisdiction,
            "Category": category,
            "Contact_Email": contact_email,
            "Claim_Status": claim_status,
            "Trust_Score": trust_score,
            "Audit_URL": f"https://isbrokersafe.com/audit/{clean_domain}",
            "Official_Register_URL": official_url
        })

    conn.commit()
    conn.close()

    if "--export-csv" in sys.argv:
        os.makedirs(CSV_OUT_DIR, exist_ok=True)
        with open(CSV_OUT_PATH, mode="w", newline="", encoding="utf-8") as f:
            fieldnames = [
                "ID", "Entity_Name", "Domain", "Regulator", "License_Number",
                "Jurisdiction", "Category", "Contact_Email", "Claim_Status",
                "Trust_Score", "Audit_URL", "Official_Register_URL"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(csv_rows)
        print(f"📁 Exported Master CSV to: {CSV_OUT_PATH}\n")

    print(f"\n✅ Total Licensed Brokers & Prop Firms Indexed: {inserted_or_updated}")
    print("📊 Breakdown by Regulatory Authority:")
    for reg, cnt in authority_counts.items():
        print(f"   • {reg:<34} : {cnt} entities")


if __name__ == "__main__":
    run_harvester()
