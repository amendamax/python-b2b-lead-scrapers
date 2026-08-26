# IsBrokerSafe Python SDK 🛡️⚡

[![PyPI Version](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org/project/isbrokersafe/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-brightgreen.svg)](https://www.python.org/)

The official Python client library for the **[IsBrokerSafe.com](https://isbrokersafe.com)** Threat Intelligence and Financial Broker Legitimacy API.

Audit any Forex broker, Crypto platform, or CFD entity in real-time across **14,600+ verified records**, official regulatory registries (FCA, CySEC, ASIC, CFTC, CONSOB, CNBV), and WHOIS age detection.

---

## 📦 Installation

```bash
pip install isbrokersafe
```

*(Zero external dependencies! Works right out of the box with standard library).*

---

## 🚀 Quickstart

```python
import isbrokersafe

# Initialize with your API key (or leave empty for anonymous free tier)
client = isbrokersafe.Client(api_key="YOUR_API_KEY")

# 1. Audit a broker or crypto domain
result = client.check("exness.com")

print(f"Status: {result.status}")              # 'SAFE'
print(f"Safety Score: {result.safety_score}/100") # 95
print(f"Is Regulated: {result.is_regulated}")  # True
print(f"Regulators: {result.regulators}")      # ['FCA', 'CySEC', 'FSA']
print(f"Verdict: {result.trust_verdict}")

# 2. Check for scam / blacklisted domain
scam = client.check("apexcryptofx.com")
print(f"Status: {scam.status}")                # 'BLACKLISTED'
print(f"Risk Factors: {scam.risk_factors}")    # ['Unregulated Entity', 'Domain < 30 days']
```

---

## 🔍 Features

* 🏛️ **Real-Time Regulatory Verification**: Audits official license statuses from Tier-1 and Tier-2 regulators (*FCA, ASIC, CySEC, CFTC, BaFin, CONSOB*).
* 🚨 **Global Blacklist Feeds**: Cross-references international fraud warnings and clone entity databases.
* 🌐 **WHOIS Forensic Age Inspection**: Detects fly-by-night domains registered less than 90 days ago.
* ⚡ **Ultra-Fast & Lightweight**: Sub-50ms response times worldwide.

---

## 📖 Advanced Usage

### Fetching Latest Regulatory Warnings

```python
warnings = client.get_warnings(regulator="fca", limit=20)

for w in warnings:
    print(f"[{w.warning_date}] {w.entity_name} ({w.domain}) - {w.reason}")
```

### Global Threat Intelligence Stats

```python
stats = client.get_stats()
print(f"Total Audited Entities: {stats.total_brokers:,}")
print(f"Blacklisted Scams: {stats.blacklisted_entities:,}")
```

### Error Handling

```python
from isbrokersafe import AuthenticationError, QuotaExceededError, IsBrokerSafeError

try:
    result = client.check("suspicious-broker.com")
except AuthenticationError:
    print("Invalid API Key! Get one free at https://isbrokersafe.com/api/v1/docs")
except QuotaExceededError:
    print("Monthly quota exceeded. Upgrade to Pro at https://isbrokersafe.com")
except IsBrokerSafeError as e:
    print(f"API Error: {e}")
```

---

## 🔑 Obtaining an API Key

Generate a free developer API key (100 requests/month) instantly at:  
👉 **[https://isbrokersafe.com/api/v1/docs](https://isbrokersafe.com/api/v1/docs)**

---

## 📄 License

Distributed under the MIT License. Copyright © 2026 **VasileDev Group**.
