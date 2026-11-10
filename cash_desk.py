# -*- coding: utf-8 -*-
"""
VasileDev Group - Cash Desk B2B (generator + server local live)

Utilizare:
  python cash_desk.py            -> re-exportă din D1 (wrangler --remote), regenerează cash-desk.html și îl deschide
  python cash_desk.py --no-fetch -> regenerează doar din fișierele JSON locale (cash-desk/data/)
  python cash_desk.py serve      -> server local http://127.0.0.1:8765 cu contor LIVE (interoghează D1 la fiecare 60s)

Instalatorii provin din cash-desk/data/installers_*.json (date publice verificate pe site-urile firmelor;
câmpul source_url arată pagina unde a fost văzut fiecare număr). Nimic nu este inventat.
"""
import html
import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "cash-desk", "data")
OUT_HTML = os.path.join(ROOT, "cash-desk.html")
AG = r"C:\Users\bratu\Documents\antigravity"

STORE_ID = "vasiledev-21"
VAT_ID = "IT04226190041"
OWNER_WA_IT = "393209481876"

# Numere / UA folosite la teste interne -> excluse din "real"
TEST_PHONES = {"3209481876", "393209481876", "+393209481876"}
TEST_IP_HASHES = {"MjE2LjEyOC4xMS4y"}
BOT_RE = re.compile(r"bot|crawl|spider|slurp|google|bing|yandex|baidu|headless|lighthouse|preview|facebookexternalhit|curl|wget|python", re.I)

D1 = {
    "IT": {"db": "master_italy", "cwd": os.path.join(AG, "italy-lead-engine", "lifecycle-worker")},
    "RO": {"db": "master_romania", "cwd": os.path.join(AG, "romania-lead-engine", "lifecycle-worker")},
    "EU": {"db": "radar-network-db", "cwd": os.path.join(AG, "eu-subsidies-network")},
}
QUERIES = {
    "it_leads": ("IT", "SELECT id, vertical_slug, comune_istat, customer_name, customer_phone, customer_email, details, status, created_at FROM leads ORDER BY id DESC"),
    "ro_leads": ("RO", "SELECT id, customer_name, customer_phone, customer_email, comune, provincia, province, regione, region, vertical_slug, mode, system_title, estimated_grant_lei, partner_category, status, created_at FROM leads ORDER BY id DESC"),
    "eu_leads": ("EU", "SELECT id, domain, country_code, city_or_postal, service_mode, estimated_grant_eur, full_name, phone, email, status, created_at FROM eu_leads ORDER BY id DESC"),
    "it_clicks": ("IT", "SELECT * FROM affiliate_clicks ORDER BY id DESC"),
    "ro_clicks": ("RO", "SELECT * FROM affiliate_clicks ORDER BY id DESC"),
    "eu_clicks": ("EU", "SELECT * FROM affiliate_clicks ORDER BY id DESC"),
}


# ----------------------------------------------------------------------------- D1
def d1_query(target, sql):
    cfg = D1[target]
    proc = subprocess.run(
        ["npx.cmd", "wrangler", "d1", "execute", cfg["db"], "--remote", "--json", "--command", sql],
        cwd=cfg["cwd"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120,
    )
    out = proc.stdout.strip()
    start = out.find("[")
    if start < 0:
        raise RuntimeError(f"wrangler {cfg['db']} failed: {proc.stderr[-400:]}")
    return json.loads(out[start:])[0].get("results", [])


def fetch_all():
    os.makedirs(DATA, exist_ok=True)
    for name, (target, sql) in QUERIES.items():
        try:
            rows = d1_query(target, sql)
            with open(os.path.join(DATA, f"{name}.json"), "w", encoding="utf-8") as fh:
                json.dump([{"results": rows}], fh, ensure_ascii=False, indent=1)
            print(f"  [D1] {name}: {len(rows)} rânduri")
        except Exception as exc:  # păstrează exportul anterior
            print(f"  [D1] {name}: EROARE ({exc}) - folosesc exportul local existent")


def load_rows(name):
    p = os.path.join(DATA, f"{name}.json")
    if not os.path.exists(p):
        return []
    with open(p, "r", encoding="utf-8-sig") as fh:
        raw = fh.read().strip()
    start = raw.find("[")
    data = json.loads(raw[start:]) if start >= 0 else []
    return data[0].get("results", []) if data else []


def load_installers():
    items = []
    for fn in sorted(os.listdir(DATA)):
        if fn.startswith("installers_") and fn.endswith(".json"):
            with open(os.path.join(DATA, fn), "r", encoding="utf-8-sig") as fh:
                items.extend(json.load(fh))
    return items


# ----------------------------------------------------------------------------- phones
def digits(s):
    return re.sub(r"\D", "", str(s or ""))


def to_e164(number, country):
    d = digits(number)
    if country == "IT":
        if d.startswith("0039"):
            d = d[4:]
        if d.startswith("39") and len(d) >= 11:
            d = d[2:]
        return "39" + d, d.startswith("3")
    if country == "RO":
        if d.startswith("0040"):
            d = d[4:]
        if d.startswith("40") and len(d) >= 11:
            d = d[2:]
        if d.startswith("0"):
            d = d[1:]
        return "40" + d, d.startswith("7")
    return d, False


def wa_target(inst):
    """Returnează (numar_e164, eticheta) pentru WhatsApp sau (None, motiv)."""
    country = inst.get("country")
    phones = inst.get("phones") or []
    for ph in phones:
        if ph.get("type") == "whatsapp":
            e, _ = to_e164(ph.get("number"), country)
            return e, "WhatsApp publicat pe site"
    for ph in phones:
        e, mobile = to_e164(ph.get("number"), country)
        if mobile:
            return e, "mobil publicat (WhatsApp neconfirmat)"
    return None, "doar telefon fix - sună direct"


# ----------------------------------------------------------------------------- leads
def is_test_phone(p):
    d = digits(p)
    return d in {digits(x) for x in TEST_PHONES} or d.endswith("3209481876")


def parse_it_leads():
    leads = []
    for r in load_rows("it_leads"):
        if is_test_phone(r.get("customer_phone")):
            continue
        try:
            det = json.loads(r.get("details") or "{}")
        except Exception:
            det = {}
        if det.get("mode") == "b2b_partner_application":
            continue
        snap = det.get("technical_snapshot") or {}
        leads.append({
            "country": "IT",
            "id": r.get("id"),
            "created_at": r.get("created_at"),
            "status": r.get("status"),
            "comune": det.get("comune") or r.get("comune_istat"),
            "province": det.get("province") or "",
            "region": det.get("region") or "",
            "mode": det.get("mode") or r.get("vertical_slug"),
            "friendly": det.get("friendly_mode") or "",
            "target": det.get("target_type") or "",
            "specs": snap.get("system_specs") or "",
            "gross": snap.get("estimated_cost_gross"),
            "bonus": snap.get("bonus_percentage"),
            "name": r.get("customer_name"),
            "phone": r.get("customer_phone"),
            "email": r.get("customer_email") or det.get("email") or "",
        })
    return leads


def parse_ro_leads():
    leads = []
    for r in load_rows("ro_leads"):
        if is_test_phone(r.get("customer_phone")):
            continue
        leads.append({
            "country": "RO", "id": r.get("id"), "created_at": r.get("created_at"), "status": r.get("status"),
            "comune": r.get("comune"), "province": r.get("province") or r.get("provincia") or "",
            "region": r.get("region") or r.get("regione") or "", "mode": r.get("mode") or r.get("vertical_slug"),
            "friendly": r.get("system_title") or "", "target": "", "specs": r.get("system_title") or "",
            "gross": None, "bonus": None, "name": r.get("customer_name"), "phone": r.get("customer_phone"),
            "email": r.get("customer_email") or "",
        })
    return leads


def parse_eu_leads():
    out = []
    for r in load_rows("eu_leads"):
        if is_test_phone(r.get("phone")):
            continue
        out.append(r)
    return out


def area_key(text):
    t = (text or "").lower()
    for key, words in {
        "Bari": ["bari", "ba"],
        "Chieti/Pescara": ["chieti", "pescara", "treglio", "lanciano", "ortona"],
        "Roma": ["roma"], "Milano": ["milano"], "Torino": ["torino"], "Cuneo": ["cuneo"],
    }.items():
        if any(re.search(rf"\b{re.escape(w)}\b", t) for w in words):
            return key
    return text or "?"


# ----------------------------------------------------------------------------- clicks
def click_stats():
    allc = []
    for src in ("it_clicks", "ro_clicks", "eu_clicks"):
        for c in load_rows(src):
            c["_src"] = src[:2].upper()
            allc.append(c)
    ours = [c for c in allc if f"AssociateTag={STORE_ID}" in (c.get("target_url") or "")]

    def real(c):
        ua = c.get("user_agent") or ""
        return not (BOT_RE.search(ua) or ua.strip() == "Mozilla/5.0" or c.get("user_ip_hash") in TEST_IP_HASHES)

    human = [c for c in ours if real(c)]
    by_country = {}
    for c in human:
        by_country[c.get("country")] = by_country.get(c.get("country"), 0) + 1
    return {
        "total_logged": len(allc),
        "store_tag": len(ours),
        "real_human": len(human),
        "bots_or_tests": len(ours) - len(human),
        "by_country": by_country,
        "last": sorted(human, key=lambda c: c.get("created_at") or "", reverse=True)[:15],
        "updated": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
    }


# ----------------------------------------------------------------------------- messages
def msg_it_treglio_vip():
    return (
        f"Buongiorno New Green Tecnologia S.r.l.s., sono Vasile Bratu di https://calcolaincentivi.it (VasileDev Group, P.IVA UE {VAT_ID}).\n\n"
        f"Ho visto che avete preso in carico con successo la richiesta di preventivo #11 da Treglio (CH) per l'installazione della colonnina di ricarica auto.\n"
        f"Come procede il contatto con il cliente?\n\n"
        f"Dato che siete attivi e operativi sul territorio, vi proponiamo il:\n"
        f"*PACCHETTO PARTNER ESCLUSIVO CHIETI / PESCARA:*\n"
        f"- Tutte le prossime richieste di preventivo (fotovoltaico, batterie LiFePO4, wallbox Bonus MASE 80%) generate dai nostri simulatori per Chieti e Pescara vi verranno girate in ESCLUSIVA DIRETTA su WhatsApp.\n"
        f"- Blocco del territorio per 30 giorni: *50 EUR* (0% IVA con fattura elettronica VasileDev Group, P.IVA {VAT_ID}).\n\n"
        f"Portale: https://calcolaincentivi.it\n"
        f"Vi interessa attivare l'esclusiva provinciale? Rispondete SI e vi invio i dettagli per l'attivazione immediata.\n"
        f"(Se preferite acquistare solo singoli contatti a 35 EUR, fatecelo sapere)."
    )


def msg_it_lead(lead, inst):
    when = (lead.get("created_at") or "")[:10]
    loc = f"{lead.get('comune')} ({lead.get('province')})" if lead.get("province") else lead.get("comune")
    gross = f"~{lead['gross']:,} EUR".replace(",", ".") if isinstance(lead.get("gross"), (int, float)) else "n.d."
    return (
        f"Buongiorno {inst['company']}, sono Vasile Bratu di https://calcolaincentivi.it (VasileDev Group, P.IVA UE {VAT_ID}).\n\n"
        f"Abbiamo una *RICHIESTA REALE* di preventivo nella vostra zona:\n"
        f"- Localita: *{loc}*\n"
        f"- Impianto: *{lead.get('specs') or lead.get('friendly')}*\n"
        f"- Destinazione: {lead.get('target') or 'n.d.'}\n"
        f"- Valore stimato: {gross} (incentivo {lead.get('bonus') or '-'}%)\n"
        f"- Data: {when} (cliente con cellulare verificato)\n\n"
        f"Opzioni:\n"
        f"1) Sblocco ESCLUSIVO di questo contatto (nome + cellulare): *35 EUR* - lo cedo a 1 solo installatore.\n"
        f"2) Pacchetto Partner Provinciale (*50 EUR / 30 giorni*): esclusiva su tutte le prossime richieste della provincia di {lead.get('province') or loc}.\n\n"
        f"Portale: https://calcolaincentivi.it\n"
        f"Fattura elettronica VasileDev Group (P.IVA {VAT_ID}), IVA 0%.\n"
        f"Le interessa? Risponda SI e le invio i dati di pagamento."
    )


def msg_it_partner(area, inst):
    return (
        f"Buongiorno {inst['company']}, sono Vasile Bratu di https://calcolaincentivi.it (VasileDev Group, P.IVA UE {VAT_ID}).\n\n"
        f"I nostri simulatori incentivi (fotovoltaico, accumulo LiFePO4, wallbox Bonus MASE 80%) generano richieste di "
        f"preventivo nella provincia di *{area}*.\n\n"
        f"Stiamo selezionando *1 installatore abilitato DM 37/08* di riferimento per la provincia di {area}:\n"
        f"- La *PRIMA richiesta di preventivo* della vostra zona ve la inviamo *GRATUITAMENTE* su WhatsApp per farvi verificare la qualita dei clienti.\n"
        f"- Solo dopo aver testato il primo contatto gratuito, potrete decidere se attivare l'esclusiva provinciale (50 EUR / 30 giorni) o sbloccare singoli contatti.\n\n"
        f"Portale: https://calcolaincentivi.it\n"
        f"Confermiamo questo numero WhatsApp per inviarvi gratuitamente la prima richiesta di *{area}*? Risponda SI per confermare."
    )


def msg_ro(inst):
    county = inst.get("county") or inst.get("area")
    return (
        f"Bună ziua, {inst['company']}! Sunt Vasile Bratu de la https://calculeazasubventii.ro (VasileDev Group, cod TVA UE {VAT_ID}).\n\n"
        f"Platforma noastră are peste 2.350 de pagini indexate în Google pentru subvenții Casa Verde, "
        f"baterii LiFePO4 și pompe de căldură, iar proprietarii din județul *{county}* își calculează subvenția și cer oferte de montaj.\n\n"
        f"Selectăm câte *1-2 firme autorizate ANRE* pe fiecare județ:\n"
        f"- *PRIMA cerere de montaj* din județul *{county}* v-o trimitem *100% GRATUIT* direct pe WhatsApp, ca să vedeți pe viu calitatea clienților.\n"
        f"- Doar după ce testați primul client gratuit și sunteți mulțumiți, putem discuta de rezervarea exclusivă a județului {county} (250 lei / 30 zile, factură UE 0% TVA).\n\n"
        f"Platformă: https://calculeazasubventii.ro\n"
        f"Putem nota acest număr de WhatsApp ca să vă trimitem *gratuit prima cerere* din județul *{county}*? Răspundeți DA pentru confirmare."
    )


def wa_link(num, text):
    return f"https://wa.me/{num}?text={urllib.parse.quote(text)}"


# ----------------------------------------------------------------------------- HTML
def esc(s):
    return html.escape(str(s if s is not None else ""))


def installer_card(inst, message, btn_label, btn_class):
    num, why = wa_target(inst)
    phones = ", ".join(f"{esc(p.get('number'))} <span class='t'>({esc(p.get('type'))})</span>" for p in inst.get("phones") or [])
    site = f"<a href='{esc(inst.get('website'))}' target='_blank'>{esc(inst.get('website'))}</a>" if inst.get("website") else "—"
    
    email = (inst.get("email") or "").strip()
    country = inst.get("country") or "IT"
    loc_name = inst.get('city') or inst.get('county') or inst.get('area') or ''
    subject = (
        f"Proposta Partner Installatore Fotovoltaico / Colonnine - calcolaincentivi.it ({loc_name})"
        if country == "IT"
        else f"Propunere Parteneriat Instalator ANRE - calculeazasubventii.ro ({loc_name})"
    )
    mailto_url = f"mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(message)}" if email else None

    action_buttons = []
    if num:
        action_buttons.append(f"<a class='btn {btn_class}' target='_blank' href='{esc(wa_link(num, message))}' onclick='markSent(this)'>{btn_label}</a>")
        if email:
            action_buttons.append(f"<a class='btn blue' href='{esc(mailto_url)}' onclick='markSent(this)'>✉ Trimite Email</a>")
    else:
        if email:
            action_buttons.append(f"<a class='btn blue' href='{esc(mailto_url)}' onclick='markSent(this)'>✉ Trimite Oferta pe Email</a>")
        action_buttons.append(f"<span class='btn off'>{esc(why)}</span>")

    btns_html = " ".join(action_buttons)
    return f"""
    <div class='inst'>
      <div class='ih'><b>{esc(inst.get('company'))}</b> <span class='muted'>• {esc(inst.get('city'))}</span></div>
      <div class='small'>📞 {phones}</div>
      <div class='small'>🌐 {site} {('• ✉ <a href="' + esc(mailto_url or '#') + '">' + esc(email) + '</a>') if email else ''}</div>
      <div class='small muted'>{esc(inst.get('services'))}</div>
      <div class='small muted'>Sursă: <a href='{esc(inst.get('source_url'))}' target='_blank'>{esc(inst.get('source_url'))}</a> • WA: {esc(why)}</div>
      <div class='row'>{btns_html}
        <details><summary>mesaj</summary><pre>{esc(message)}</pre></details></div>
    </div>"""


def build_html(live=False):
    it_leads, ro_leads, eu_leads = parse_it_leads(), parse_ro_leads(), parse_eu_leads()
    installers = load_installers()
    it_inst = [i for i in installers if i.get("country") == "IT"]
    ro_inst = [i for i in installers if i.get("country") == "RO"]
    stats = click_stats()

    by_area = {}
    for i in it_inst:
        by_area.setdefault(area_key(f"{i.get('area')} {i.get('province')} {i.get('city')}"), []).append(i)

    # --- secțiunea lead-uri IT
    lead_rows = []
    covered = set()
    for L in it_leads:
        ak = area_key(f"{L.get('province')} {L.get('comune')}")
        covered.add(ak)
        insts = by_area.get(ak, [])
        warn = ""
        if (L.get("status") or "").lower() in ("claimed", "sold", "closed"):
            warn = f"<div class='warn'>⚠️ Status în D1: <b>{esc(L.get('status'))}</b> – lead deja revendicat de un partener. Nu îl mai vinde ca „exclusiv”.</div>"
        cards = "".join(installer_card(i, msg_it_lead(L, i), "Trimite Oferta pe WhatsApp (35 €)", "green") for i in insts) or "<div class='muted'>Niciun instalator găsit încă pentru zonă.</div>"
        lead_rows.append(f"""
        <div class='lead'>
          <div class='lh'>🇮🇹 #{esc(L['id'])} • <b>{esc(L.get('comune'))}</b> ({esc(L.get('province'))}, {esc(L.get('region'))}) • {esc(L.get('created_at'))}</div>
          <div>{esc(L.get('specs') or L.get('friendly'))} • {esc(L.get('target'))} • valoare ~{esc(L.get('gross'))} € • bonus {esc(L.get('bonus'))}%</div>
          <div class='small'>Client: {esc(L.get('name'))} • {esc(L.get('phone'))} {esc(L.get('email'))} • status: <b>{esc(L.get('status'))}</b></div>
          {warn}
          <div class='grid'>{cards}</div>
        </div>""")

    # --- provincii IT fără lead (pachet partener)
    partner_rows = []
    for area, insts in by_area.items():
        if area in covered:
            continue
        cards = "".join(installer_card(i, msg_it_partner(area, i), "Trimite Oferta pe WhatsApp (35 €)", "green") for i in insts)
        partner_rows.append(f"<div class='lead'><div class='lh'>🇮🇹 Provincia {esc(area)} – fără lead încă (ofertă Partner Provinciale)</div><div class='grid'>{cards}</div></div>")

    # --- VIP Partner Lead #11 (Treglio - CH)
    vip_lead11_msg = msg_it_treglio_vip()
    vip_lead11_html = f"""
    <div class='vip-card'>
      <div class='vh'>👑 PARTENER ACTIV CHIETI / PESCARA – LEAD #11 REVENDICAT CU SUCCES</div>
      <div class='vip-body'>
        <div style='font-size:16px'><b>New Green Tecnologia S.r.l.s. (NGT Srl)</b> <span class='muted'>• Ortona (CH), Abruzzo</span></div>
        <div class='small' style='margin-top:5px'>📍 Corso Giacomo Matteotti 66, Ortona (CH) • ✉️ <a href='mailto:amministrazione@ngtsrls.it'>amministrazione@ngtsrls.it</a> • 📞 <b>+39 342 059 4172</b> <span class='t'>(WhatsApp verificat)</span></div>
        <div class='small muted' style='margin-top:4px'>⚡ A revendicat în D1 Lead-ul #11 (Treglio, CH • Colonnina auto elettrica 11 kW) la 21.10.2026 12:19 • Status D1: <b>claimed</b> (Tier: free_trial_1)</div>
        <div class='row' style='margin-top:12px'>
          <a class='btn gold' target='_blank' href='{esc(wa_link("393420594172", vip_lead11_msg))}' onclick='markSent(this)'>👑 Trimite Pachet Exclusivitate Chieti / Pescara (50 €) pe WhatsApp →</a>
          <details><summary>vezi mesajul precompletat</summary><pre>{esc(vip_lead11_msg)}</pre></details>
        </div>
      </div>
    </div>"""

    # --- RO (toate cele 41 de județe + Municipiul București)
    ro_by_county = {}
    for i in ro_inst:
        c_name = i.get("area")
        if c_name == "București / Ilfov":
            c_name = i.get("county") or "București"
        ro_by_county.setdefault(c_name, []).append(i)

    ro_rows = []
    for county in sorted(ro_by_county.keys()):
        insts = ro_by_county[county]
        label = "Municipiul București" if county == "București" else f"Județul {county}"
        cards = "".join(installer_card(i, msg_ro(i), "Trimite Rezervare Județ pe WhatsApp (250 Lei / 50 €)", "green") for i in insts)
        ro_rows.append(f"<div class='lead'><div class='lh'>🇷🇴 <b>{esc(label)}</b> <span class='muted'>({len(insts)} firme verificate ANRE/mobil)</span></div><div class='grid'>{cards}</div></div>")

    ro_leads_html = "".join(
        f"<li>#{esc(l['id'])} {esc(l.get('comune'))} ({esc(l.get('province'))}) – {esc(l.get('specs'))} – {esc(l.get('created_at'))}</li>" for l in ro_leads
    ) or "<li class='muted'>0 lead-uri reale în master_romania.</li>"
    eu_leads_html = "".join(
        f"<li>#{esc(l['id'])} {esc(l.get('country_code'))} {esc(l.get('city_or_postal'))} – {esc(l.get('service_mode'))} – {esc(l.get('created_at'))}</li>" for l in eu_leads
    ) or "<li class='muted'>0 lead-uri reale în radar-network-db (eu_leads).</li>"

    last_clicks = "".join(
        f"<tr><td>{esc(c.get('created_at'))}</td><td>{esc(c.get('country'))}</td><td>{esc(c.get('city_slug'))}</td><td>{esc(c.get('sku'))}</td></tr>" for c in stats["last"]
    ) or "<tr><td colspan='4' class='muted'>Încă niciun click uman real.</td></tr>"

    n_it_wa = sum(1 for i in it_inst if wa_target(i)[0])
    n_ro_wa = sum(1 for i in ro_inst if wa_target(i)[0])

    live_js = """
    async function refreshStats(){
      try{ const r = await fetch('/stats?ts='+Date.now()); if(!r.ok) return; const s = await r.json();
        document.getElementById('c-real').textContent = s.real_human;
        document.getElementById('c-tag').textContent = s.store_tag;
        document.getElementById('c-bot').textContent = s.bots_or_tests;
        document.getElementById('c-upd').textContent = s.updated + ' (LIVE)';
        document.getElementById('c-country').textContent = Object.entries(s.by_country).map(([k,v])=>k+': '+v).join(' • ') || '—';
      }catch(e){}
    }
    refreshStats(); setInterval(refreshStats, 60000);
    """ if live else ""

    return f"""<!doctype html>
<html lang="ro"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cash Desk B2B – VasileDev Group</title>
<style>
 body{{font-family:system-ui,Segoe UI,Arial;background:#0b1220;color:#e2e8f0;margin:0;padding:24px}}
 h1{{margin:0 0 4px}} h2{{margin:28px 0 10px;border-bottom:1px solid #1e293b;padding-bottom:6px}}
 .muted{{color:#94a3b8}} .small{{font-size:12.5px;margin-top:3px}} .t{{color:#64748b;font-size:11px}}
 .kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:10px;margin:14px 0}}
 .kpi{{background:#111a2e;border:1px solid #1e293b;border-radius:12px;padding:12px}} .kpi b{{font-size:26px;color:#34d399;display:block}}
 .vip-card{{background:linear-gradient(135deg,#1c1917 0%,#1e293b 100%);border:2px solid #f59e0b;border-radius:14px;padding:16px;margin:18px 0}}
 .vh{{color:#fbbf24;font-size:13.5px;font-weight:800;letter-spacing:0.5px}}
 .gold{{background:#f59e0b;color:#000;font-weight:800}} .gold:hover{{background:#fbbf24}}
 .lead{{background:#0f172a;border:1px solid #1e3a5f;border-radius:14px;padding:14px;margin:12px 0}}
 .lh{{font-size:15px;margin-bottom:6px}} .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:10px;margin-top:10px}}
 .inst{{background:#111a2e;border:1px solid #243049;border-radius:12px;padding:11px}}
 .row{{display:flex;gap:8px;align-items:flex-start;flex-wrap:wrap;margin-top:8px}}
 .btn{{display:inline-block;padding:9px 12px;border-radius:10px;font-weight:800;font-size:13px;text-decoration:none}}
 .green{{background:#22c55e;color:#04130a}} .green:hover{{background:#4ade80}} .sent{{background:#334155!important;color:#cbd5e1!important}}
 .off{{background:#1e293b;color:#94a3b8;font-weight:600}}
 .warn{{background:#422006;border:1px solid #b45309;color:#fde68a;border-radius:10px;padding:8px;margin-top:8px;font-size:13px}}
 pre{{white-space:pre-wrap;background:#020617;padding:8px;border-radius:8px;font-size:12px;max-width:520px}}
 table{{border-collapse:collapse;width:100%;font-size:13px}} td,th{{border-bottom:1px solid #1e293b;padding:6px;text-align:left}}
 a{{color:#7dd3fc}}
</style></head><body>
<h1>💰 Cash Desk B2B – VasileDev Group</h1>
<div class="muted">Generat: {datetime.now().strftime('%d.%m.%Y %H:%M')} • StoreID Amazon: <b>{STORE_ID}</b> • P.IVA UE {VAT_ID}
 • Pentru contor LIVE rulează <code>python cash_desk.py serve</code></div>

{vip_lead11_html}

<h2>📊 Click-uri afiliere Amazon ({STORE_ID})</h2>
<div class="kpis">
 <div class="kpi"><b id="c-real">{stats['real_human']}</b>Click-uri umane reale</div>
 <div class="kpi"><b id="c-tag">{stats['store_tag']}</b>Total logate cu tag {STORE_ID}</div>
 <div class="kpi"><b id="c-bot">{stats['bots_or_tests']}</b>Boți / teste interne (excluse)</div>
 <div class="kpi"><b style="font-size:15px" id="c-country">{esc(' • '.join(f'{k}: {v}' for k, v in stats['by_country'].items()) or '—')}</b>Pe țări (reale)</div>
 <div class="kpi"><b style="font-size:15px" id="c-upd">{stats['updated']}</b>Ultima actualizare</div>
</div>
<table><tr><th>Data</th><th>Țară</th><th>Oraș</th><th>SKU</th></tr>{last_clicks}</table>

<h2>🇮🇹 Lead-uri reale Italia (master_italy) + instalatori din zonă</h2>
<div class="muted">{len(it_leads)} lead-uri reale • {len(it_inst)} instalatori găsiți ({n_it_wa} cu WhatsApp/mobil)</div>
{''.join(lead_rows) or "<div class='muted'>Niciun lead real.</div>"}

<h2>🇮🇹 Provincii cu trafic, fără lead încă – ofertă Partner Provinciale</h2>
{''.join(partner_rows) or "<div class='muted'>—</div>"}

<h2>🇷🇴 România – Rezervare Județ (250 lei / 50 €) – Toate cele 41 de Județe + București (42 Unități)</h2>
<div class="muted">Acoperire națională: <b>{len(ro_by_county)}</b> unități administrative • {len(ro_inst)} firme instalatori verificate ({n_ro_wa} cu WhatsApp/mobil direct)</div>
<div class="muted" style="margin-top:6px">Lead-uri reale în master_romania: <ul>{ro_leads_html}</ul></div>
{''.join(ro_rows)}

<h2>🇪🇺 Lead-uri reale EU (13 portale)</h2><ul>{eu_leads_html}</ul>

<script>
 function markSent(a){{ a.classList.add('sent'); a.textContent = '✓ Deschis în WhatsApp'; try{{ const k='sent:'+a.href.slice(0,60); localStorage.setItem(k, Date.now()); }}catch(e){{}} }}
 document.querySelectorAll('a.btn.green').forEach(a=>{{ try{{ if(localStorage.getItem('sent:'+a.href.slice(0,60))) {{ a.classList.add('sent'); a.textContent='✓ Trimis anterior (retrimite)'; }} }}catch(e){{}} }});
 {live_js}
</script>
</body></html>"""


def write_html(live=False):
    with open(OUT_HTML, "w", encoding="utf-8") as fh:
        fh.write(build_html(live=live))
    return OUT_HTML


# ----------------------------------------------------------------------------- live server
class _State:
    stats = None
    last = 0.0
    lock = threading.Lock()


def refresh_clicks_cached(max_age=60):
    with _State.lock:
        if _State.stats and time.time() - _State.last < max_age:
            return _State.stats
        for name in ("it_clicks", "ro_clicks", "eu_clicks"):
            target, sql = QUERIES[name]
            try:
                rows = d1_query(target, sql)
                with open(os.path.join(DATA, f"{name}.json"), "w", encoding="utf-8") as fh:
                    json.dump([{"results": rows}], fh, ensure_ascii=False)
            except Exception as exc:
                print("refresh error", name, exc)
        s = click_stats()
        s.pop("last", None)
        _State.stats, _State.last = s, time.time()
        return s


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        if self.path.startswith("/stats"):
            body = json.dumps(refresh_clicks_cached()).encode("utf-8")
            ctype = "application/json"
        else:
            body = build_html(live=True).encode("utf-8")
            ctype = "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main():
    args = sys.argv[1:]
    if args and args[0] == "serve":
        port = 8765
        srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        print(f"Cash Desk LIVE: http://127.0.0.1:{port}  (Ctrl+C pentru oprire)")
        webbrowser.open(f"http://127.0.0.1:{port}")
        srv.serve_forever()
        return
    if "--no-fetch" not in args:
        print("Export D1 (remote)...")
        fetch_all()
    path = write_html(live=False)
    print("Generat:", path)
    if "--no-open" not in args:
        webbrowser.open("file:///" + path.replace("\\", "/"))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    main()
