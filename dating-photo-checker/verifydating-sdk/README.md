# 🛡️ VerifyDating Python SDK (`verifydating`)

[![PyPI version](https://img.shields.io/pypi/v/verifydating.svg?color=ff2d78)](https://pypi.org/project/verifydating/)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/verifydating.svg)](https://pypi.org/project/verifydating/)
[![API Status](https://img.shields.io/badge/API-Online%20(99.99%25)-success)](https://verifydating.net/api/v1/dating-docs)

The official Python client library for the **[VerifyDating.net](https://verifydating.net/api/v1/dating-docs) B2B Anti-Catfish & Facial Scam Intelligence API**. 

Protect dating platforms, social communities, classified marketplaces, and trust & safety workflows against fake profiles, stolen model photos, AI deepfakes, and organized romance scam syndicates.

---

## ⚡ Key Features

- 🎯 **Sub-100ms Facial Screening**: Detect catfish profiles instantly upon user registration.
- 🤖 **Deepfake AI Detection**: Identify synthetic generative AI faces (Midjourney, Stable Diffusion, StyleGAN).
- 🗄️ **Global Stolen Face Database**: Cross-reference 480,000+ monitored stolen identities and romance scam photo signatures.
- 🛑 **Automated Moderation Actions**: Pre-calculated decision recommendations (`APPROVE_PROFILE`, `REQUEST_LIVE_ID`, `REJECT_PROFILE_AND_AUTO_BAN`).
- 🔒 **Zero External Dependencies**: Lightweight Vanilla Python client using standard library.

---

## 📦 Installation

```bash
pip install verifydating
```

---

## 🚀 Quickstart

### 1. Screen a Profile Picture via Image URL

```python
from verifydating import Client

# Initialize client (defaults to free developer sandbox if no api_key passed)
client = Client(api_key="vd_live_YOUR_API_KEY")

# Check a profile photo URL
result = client.check_face(image_url="https://example.com/uploads/user_avatar.jpg")

print(f"Scam Probability: {result.scam_probability}%")
print(f"Risk Level: {result.risk_level}")
print(f"Verdict: {result.verdict}")
print(f"Action: {result.action_recommendation}")

if result.is_catfish:
    print(f"🚨 AUTO-BAN TRIGGERED: Profile photo matches {result.forensic_details.matches_count} known scam syndicates.")
```

---

### 2. Screen a Local Image File Upload

```python
from verifydating import Client

client = Client(api_key="vd_live_YOUR_API_KEY")

with open("user_upload.jpg", "rb") as image_file:
    result = client.check_face(image_bytes=image_file.read())

if result.action_recommendation == "REJECT_PROFILE_AND_AUTO_BAN":
    # Automatically reject registration in your dating backend
    ban_user(user_id=123)
```

---

## 📊 Response Object Schema

`FaceCheckResult` properties:

| Field | Type | Description |
| :--- | :--- | :--- |
| `scam_probability` | `int` | Risk score from 0 (Safe) to 100 (High-Risk Romance Scam) |
| `risk_level` | `str` | `LOW_RISK_VERIFIED`, `MODERATE_SUSPICIOUS`, `CRITICAL_ROMANCE_SCAM_FLAG` |
| `action_recommendation` | `str` | `APPROVE_PROFILE`, `REQUEST_LIVE_ID`, `REJECT_PROFILE_AND_AUTO_BAN` |
| `verdict` | `str` | Human-readable forensic summary |
| `is_catfish` | `bool` | `True` if `scam_probability >= 70` |
| `forensic_details` | `object` | Sub-object containing `matches_count`, `deepfake_probability`, and `scammer_info` |
| `quota` | `object` | Remaining requests in current billing cycle |

---

## 🧪 Developer Sandbox (100 Free Scans/Month)

Need a free API key? Generate one instantly via Python:

```python
from verifydating import Client

client = Client()
key_info = client.generate_sandbox_key(email="developer@yourdatingapp.com")
print(f"Your API Key: {key_info['api_key']}")
```

---

## 🏢 Pricing Plans

| Plan | Monthly Price | Monthly Scans | Features |
| :--- | :---: | :---: | :--- |
| **Developer Free** | **$0** | 100 scans | Sandbox testing, JSON REST |
| **Starter App** | **$99** | 2,500 scans | Real-time registration screening |
| **Pro Growth** | **$299** | 25,000 scans | Deepfake AI detection & Auto-ban Webhooks |
| **Enterprise Scale** | **$699** | 100,000+ scans | Dedicated SLA (99.99%) & Custom Face Hash Stream |

For enterprise contracts and high-volume streams, contact [support@verifydating.net](mailto:support@verifydating.net).

---

## 📄 License

MIT License © 2026 VasileDev Group / VerifyDating.net
