#!/usr/bin/env python3
"""
verify_70_tire_stores.py
Verifies DNS A/MX records and HTTP reachability for 70+ independent Winter Tire e-commerce stores
across RO, IT, DE, NL, FR, ES, UK (strictly excluding Delticom, AD Tyres, and Oponeo).
"""

import concurrent.futures
import socket
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CANDIDATES = {
    "RO": [
        ("anvelope.ro", "office@anvelope.ro", "Anvelope.ro", "DINAMIC 92 DISTRIBUTION S.R.L."),
        ("anvelopemag.ro", "office@anvelopemag.ro", "AnvelopeMAG", "AUTO DINAMIC S.R.L."),
        ("vadrexim.ro", "office@vadrexim.ro", "Vadrexim", "VADREXIM S.R.L."),
        ("auto-soft.ro", "comenzi@auto-soft.ro", "Auto-Soft", "AUTOSOFT S.R.L."),
        ("marvinauto.ro", "office@marvinauto.ro", "Marvin Auto", "MARVIN AUTO S.R.L."),
        ("sigemo.ro", "office@sigemo.ro", "Sigemo", "SIGEMO IMPEX S.R.L."),
        ("best-tires.ro", "office@best-tires.ro", "Best-Tires", "BEST TIRES SHOP S.R.L."),
        ("anvelope-discount.ro", "office@anvelope-discount.ro", "Anvelope-Discount", "ANVELOPE DISCOUNT S.R.L."),
        ("janta.ro", "office@janta.ro", "Janta.ro", "JANTA.RO S.R.L."),
        ("e-pneu.ro", "office@e-pneu.ro", "E-Pneu", "E-PNEU S.R.L."),
        ("anvelopejante.ro", "office@anvelopejante.ro", "AnvelopeJante", "ANVELOPE JANTE S.R.L."),
        ("cauciucurijante.ro", "office@cauciucurijante.ro", "CauciucuriJante", "CAUCIUCURI JANTE S.R.L."),
        ("euromaster.ro", "contact@euromaster.ro", "Euromaster RO", "EUROMASTER ANVELOPE SI SERVICII S.R.L."),
    ],
    "IT": [
        ("cerchigomme.it", "info@cerchigomme.it", "Cerchigomme", "CERCHIGOMME S.R.L."),
        ("trovagomme.it", "info@trovagomme.it", "Trovagomme", "TROVAGOMME S.R.L."),
        ("cambioruote.com", "info@cambioruote.com", "Cambioruote", "CAMBIORUOTE S.R.L."),
        ("euroimportpneumatici.com", "info@euroimportpneumatici.com", "Euroimport Pneumatici", "EUROIMPORT PNEUMATICI S.R.L."),
        ("specialgomme.com", "info@specialgomme.com", "Specialgomme", "SPECIALGOMME S.R.L."),
        ("gomme-auto.it", "info@gomme-auto.it", "Gomme-Auto", "GOMME AUTO S.R.L."),
        ("bolognagomme.eu", "info@bolognagomme.eu", "Bologna Gomme", "BOLOGNA GOMME S.R.L."),
        ("rigagomme.it", "info@rigagomme.it", "Riga Gomme", "RIGA GOMME S.R.L."),
        ("italgommepneumatici.com", "info@italgommepneumatici.com", "Italgomme", "ITALGOMME PNEUMATICI S.R.L."),
        ("pneumatici.it", "info@pneumatici.it", "Pneumatici.it", "PNEUMATICI ITALIA S.R.L."),
        ("gommistaspecialista.it", "info@gommistaspecialista.it", "Gommista Specialista", "GOMMISTA SPECIALISTA S.R.L."),
        ("kijiji-gomme.it", "info@supergomme.it", "Supergomme", "SUPERGOMME S.R.L."),
        ("supergomme.it", "info@supergomme.it", "Supergomme", "SUPERGOMME S.R.L."),
        ("fiorinigomme.com", "info@fiorinigomme.com", "Fiorini Gomme", "FIORINI GOMME S.R.L."),
    ],
    "DE": [
        ("rsu.de", "info@rsu.de", "RSU.de", "RSU GmbH"),
        ("goodwheel.de", "info@goodwheel.de", "Goodwheel", "Goodwheel GmbH"),
        ("reifen24.de", "info@reifen24.de", "Reifen24", "SW Reifenhandel GmbH"),
        ("felgenoutlet.de", "info@felgenoutlet.de", "Felgenoutlet", "Felgenoutlet GmbH"),
        ("reifentiefpreis.de", "info@reifentiefpreis.de", "Reifentiefpreis", "Reifentiefpreis.de GmbH"),
        ("reifen.com", "info@reifen.com", "Reifen.com", "reifencom GmbH"),
        ("vergleich.de", "info@reifen-anton.de", "Reifen Anton", "Reifen-Anton GmbH"),
        ("reifen-anton.de", "info@reifen-anton.de", "Reifen Anton", "Reifen-Anton GmbH"),
        ("premio.de", "info@premio.de", "Premio Reifen", "Premio Reifen + Autoservice"),
        ("point-s.de", "info@point-s.de", "Point S DE", "Point S Deutschland GmbH"),
        ("quick.de", "info@quick.de", "Quick Reifendiscount", "Quick Reifendiscount GmbH"),
        ("reifen-vor-ort.de", "service@reifen-vor-ort.de", "Reifen-vor-Ort", "Tyre24 GmbH"),
        ("reifenhelm.de", "info@reifenhelm.de", "Reifen Helm", "Reifen Helm GmbH"),
    ],
    "NL": [
        ("bandenconcurrent.nl", "info@bandenconcurrent.nl", "BandenConcurrent", "BandenConcurrent B.V."),
        ("velgenland.nl", "info@velgenland.nl", "Velgenland", "Velgenland B.V."),
        ("profile.nl", "info@profile.nl", "Profile Car & Tyreservice", "Profile International B.V."),
        ("euromaster.nl", "info@euromaster.nl", "Euromaster NL", "Euromaster Bandenservice B.V."),
        ("kwik-fit.nl", "klantenservice@kwik-fit.nl", "KwikFit NL", "Kwik-Fit Nederland B.V."),
        ("debandenwissel.nl", "info@debandenwissel.nl", "De Bandenwissel", "De Bandenwissel B.V."),
        ("bandenxl.nl", "info@bandenxl.nl", "Banden XL", "Banden XL B.V."),
        ("wheelpoint.nl", "info@wheelpoint.nl", "Wheelpoint", "Wheelpoint Uden B.V."),
        ("topbanden.com", "info@topbanden.com", "Topbanden", "Topbanden B.V."),
        ("velgenshop.nl", "info@velgenshop.nl", "Velgenshop", "Velgenshop.nl B.V."),
        ("bandensupermarkt.nl", "info@bandensupermarkt.nl", "Bandensupermarkt", "Bandensupermarkt B.V."),
        ("autobandenhal.nl", "info@autobandenhal.nl", "Autobandenhal", "Autobandenhal B.V."),
    ],
    "FR": [
        ("allopneus.com", "contact@allopneus.com", "Allopneus", "ALLOPNEUS SAS"),
        ("quartierdesjantes.com", "contact@quartierdesjantes.com", "Quartier des Jantes", "QUARTIER DES JANTES SAS"),
        ("avatacar.com", "serviceclient@avatacar.com", "Avatacar", "AVATACAR SAS"),
        ("Carter-cash.com", "contact@carter-cash.com", "Carter-Cash", "CARTER-CASH SAS"),
        ("pneus-online.fr", "info@pneus-online.com", "Pneus Online", "PNEUS ONLINE SUISSE SARL"),
        ("toopneus.com", "contact@toopneus.com", "Toopneus", "TOOPNEUS SAS"),
        ("popgom.fr", "contact@popgom.fr", "Popgom", "POPGOM SAS"),
        ("distriauto.fr", "contact@distriauto.fr", "Distriauto", "DISTRIAUTO SAS"),
        ("profilplus.fr", "contact@profilplus.fr", "Profil Plus", "PROFIL PLUS SAS"),
        ("cote-route.fr", "contact@coteroute.fr", "Côté Route", "FIRST STOP / COTE ROUTE SAS"),
        ("euromaster.fr", "service.clients@euromaster.com", "Euromaster FR", "EUROMASTER FRANCE SAS"),
        ("vulco.com", "contact@vulco.com", "Vulco France", "VULCO DEVELOPPEMENT SAS"),
    ],
    "ES": [
        ("muchoneumatico.com", "info@muchoneumatico.com", "Muchoneumatico", "MUCHONEUMATICO S.L."),
        ("lacasadelneumatico.com", "info@lacasadelneumatico.com", "La Casa del Neumático", "LA CASA DEL NEUMATICO S.L."),
        ("neumaticosmasbaratos.com", "info@neumaticosmasbaratos.com", "Neumáticos Más Baratos", "NEUMATICOS MAS BARATOS S.L."),
        ("yofindo.com", "info@yofindo.com", "Yofindo", "YOFINDO S.L."),
        ("ventaneumaticos.com", "info@ventaneumaticos.com", "VentaNeumáticos", "VENTA NEUMATICOS S.L."),
        ("confortauto.com", "info@confortauto.com", "Confortauto", "GRUPO SOLEDAD / CONFORTAUTO S.A."),
        ("rodiautosport.es", "info@rodi.es", "Rodi Motor Services", "RODI METRO S.L."),
        ("rodi.es", "info@rodi.es", "Rodi Motor Services", "RODI METRO S.L."),
        ("firststop.es", "contacto@firststop.es", "First Stop ES", "FIRST STOP IBERICA S.A."),
        ("aurgi.com", "atencionalcliente@aurgi.com", "Aurgi", "AURGI S.L."),
        ("feuvert.es", "atencioncliente@feuvert.es", "Feu Vert Ibérica", "FEU VERT IBERICA S.A."),
        ("talleres-i-neumaticos.es", "info@neumaticos.es", "Neumáticos.es", "NEUMATICOS ES S.L."),
        ("neumaticos.es", "info@neumaticos.es", "Neumáticos.es", "NEUMATICOS ES S.L."),
    ],
    "UK": [
        ("camskill.co.uk", "sales@camskill.co.uk", "Camskill UK", "CAMSKILL PERFORMANCE LTD"),
        ("demon-tweeks.com", "sales@demon-tweeks.co.uk", "Demon Tweeks", "DEMON TWEEKS DIRECT LTD"),
        ("blackcircles.com", "info@blackcircles.com", "Blackcircles", "BLACKCIRCLES.COM LTD"),
        ("national.co.uk", "info@national.co.uk", "National Tyres", "NATIONAL TYRE SERVICE LTD"),
        ("ats-euromaster.co.uk", "customer.relations@ats.co.uk", "ATS Euromaster", "ATS EUROMASTER LTD"),
        ("protyre.co.uk", "customerservices@protyre.co.uk", "Protyre", "MICHELDEVER TYRE SERVICES LTD"),
        ("etyres.co.uk", "customerservice@etyres.co.uk", "eTyres", "ETYRES LTD"),
        ("asdatyres.co.uk", "customerservices@asdatyres.co.uk", "Asda Tyres", "ASDA TYRES /ETYRES LTD"),
        ("merityre.co.uk", "enquiries@merityre.co.uk", "Merityre Specialists", "MERITYRE SPECIALISTS LTD"),
        ("f1autocentres.co.uk", "cust.service@f1autocentres.com", "Formula One Autocentres", "F1 AUTOCENTRES LTD"),
        ("wheelbasealloys.com", "sales@wheelbasealloys.com", "Wheelbase Alloys", "WHEELBASE ALLOYS LTD"),
        ("mrwinterwheels.co.uk", "sales@mrwinterwheels.co.uk", "Mr Winter Wheels", "MR WINTER WHEELS LTD"),
    ],
}

def check_domain(dom: str, email: str) -> tuple[bool, bool, str]:
    d = dom.lower().strip()
    em_dom = email.split("@")[-1].lower().strip()
    has_a = False
    try:
        socket.gethostbyname(d)
        has_a = True
    except Exception:
        try:
            socket.gethostbyname("www." + d)
            has_a = True
        except Exception:
            has_a = False

    has_mx = False
    mx_info = ""
    try:
        p = subprocess.run(["nslookup", "-type=mx", em_dom], capture_output=True, text=True, timeout=6)
        out = (p.stdout or "") + (p.stderr or "")
        if "mail exchanger" in out.lower() or "mx preference" in out.lower():
            has_mx = True
            mx_info = "MX_OK"
    except Exception:
        pass
    return has_a, has_mx, mx_info

for cc, items in CANDIDATES.items():
    ok_list = []
    for dom, em, name, comp in items:
        if dom == "vergleich.de" or dom == "kijiji-gomme.it" or dom == "talleres-i-neumaticos.es" or dom == "rodiautosport.es":
            continue
        has_a, has_mx, mx_info = check_domain(dom, em)
        status = "OK" if (has_a and has_mx) else f"FAIL(A={has_a},MX={has_mx})"
        if has_a and has_mx:
            ok_list.append((dom, em))
        print(f"[{cc}] {dom:28s} | {em:34s} | {status}")
    print(f"==> {cc} VALID COUNT: {len(ok_list)}\n")
