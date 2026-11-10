# Raport D1 – lead-uri reale și click-uri de afiliere (22.10.2026, 12:46)

Sursă: `wrangler d1 execute --remote` pe `master_italy`, `master_romania` și `radar-network-db`. Exporturile JSON brute sunt în `cash-desk/data/`.

## Lead-uri reale (testele cu 3209481876 sunt excluse)

| Țară | ID | Data | Localitate | Cerere | Client | Status |
|---|---|---|---|---|---|---|
| 🇮🇹 IT | 11 | 2026-10-20 08:25 | Treglio (CH, Abruzzo) | Wallbox 11 kW, garaj condominial, Bonus MASE 80% (~2.300 €) | Bruno D'Orazio, 3477466572, brunodorazio@virgilio.it | **claimed** (deja revendicat) |
| 🇮🇹 IT | 10 | 2026-10-19 21:50 | Bari (BA, Puglia) | Wallbox 7,4 kW, garaj condominial, Bonus MASE 80% (~1.900 €) | „Cliente Web”, 3274015326 | **NEW** |
| 🇷🇴 RO | – | – | – | **0 lead-uri** în `master_romania` | – | – |
| 🇪🇺 EU | – | – | – | **0 lead-uri** în `eu_leads` (13 portale) | – | – |

## Click-uri de afiliere (`affiliate_clicks`)

| Sursă | Total logate | Cu tag `vasiledev-21` | Click-uri umane reale |
|---|---|---|---|
| IT | 2 | 1 | 0 (testele noastre interne: UA `Mozilla/5.0`, IP-ul nostru) |
| RO | 2 | 1 | 0 (teste interne) |
| EU | 7 | 7 | 0 (4 teste interne + 3 crawlere **GoogleOther**: CZ Nepomuk, CZ Jindřichov, DE Leck) |
| **Total** | **11** | **9** | **0** |

## Probleme găsite și reparate azi
1. **Bug critic în `italy-lead-engine/frontend/functions/api/v1/energy/calculate.ts`:** INSERT-ul lead-ului în D1 folosea `body.direct_equipment`, dar `body` nu exista (variabila corectă e `data`). Asta arunca `ReferenceError` într-un `try/catch`, așa că **niciun lead italian nu se mai salva în D1** de când au fost adăugate coloanele VPP. Notificările pe email/WhatsApp se trimiteau înainte de INSERT, deci probabil au mers în continuare. Același bug exista la aplicațiile B2B partener (`vppReady` și `body` nedefinite). Reparat și deployat.
2. **Click-urile boților erau logate ca reale:** în `/api/v1/go-offer` (IT, RO și EU) am adăugat un filtru pe User-Agent, ca boții să nu mai fie scriși în D1. Sunt în continuare redirecționați normal.
