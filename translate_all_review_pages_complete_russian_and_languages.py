import os
import glob
import re

brokers = ["exness", "etoro", "plus500", "xm", "avatrade"]
langs = ["ro", "it", "de", "es", "fr", "pt", "ru"]

# Complete dictionary of full HTML templates for each broker in each language
broker_content = {
    "plus500": {
        "ru": {
            "title": "Надежен ли Plus500? Обзор безопасности и аудит регулятора (2026)",
            "description": "Безопасен ли Plus500? Читайте экспертный обзор Plus500. Проверка регулирования LSE, FCA, CySEC, ASIC, комиссии и оценка рисков.",
            "back": "← Назад к главному верификатору",
            "h1": "Plus500 <span>Обзор безопасности</span>",
            "subtitle": "Публичная компания котируемая на бирже LSE. Международный регулируемый брокер CFD.",
            "badge_trust": "91% Оценка доверия",
            "is_safe_h2": "Является ли Plus500 легальным брокером или мошенничеством?",
            "is_safe_p": "<strong>Вердикт: 100% Легитимен и котируется на бирже.</strong> Plus500 — компания из индекса FTSE 250, котирующаяся на Лондонской фондовой бирже (LSE: PLUS). Регулируется авторитетными регуляторами первого уровня, включая FCA (Великобритания), CySEC (Кипр), ASIC (Австралия) и MAS (Сингапур). Публичная финансовая отчетность гарантирует полную фискальную прозрачность.",
            "profile_h2": "Регуляторный профиль Plus500",
            "th_entity": "Юридические лица",
            "th_reg": "Финансовые регуляторы",
            "th_protect": "Схема защиты инвесторов",
            "th_age": "Регистрация домена",
            "val_entity": "Plus500UK Ltd, Plus500CY Ltd, Plus500AU Pty Ltd, Plus500SG Pte Ltd",
            "val_reg": "FCA (Великобритания) - FRN 509909<br>CySEC (Кипр) - Лицензия 250/14<br>ASIC (Австралия) - AFSL 417727<br>MAS (Сингапур) - CMS100648",
            "val_protect": "До £85,000 (UK FSCS) / До €20,000 (Cyprus ICF)",
            "val_age": "Зарегистрирован в 2008 году (18 лет успешной работы)",
            "pros_h2": "Преимущества и недостатки",
            "pros_title": "✓ Ключевые преимущества (Плюсы)",
            "cons_title": "✕ Факторы риска (Минусы)",
            "pros_list": [
                "Публично торгуется на Лондонской фондовой бирже — 100% финансовая прозрачность.",
                "Лицензирован регуляторами FCA, CySEC, ASIC и MAS.",
                "Чрезвычайно удобная и надежная торговая платформа.",
                "Бесплатные инструменты управления рисками и оповещения в реальном времени."
            ],
            "cons_list": [
                "Не поддерживает платформы MetaTrader 4 / MetaTrader 5 (только собственная платформа).",
                "Комиссия за неактивность применяется после 3 месяцев отсутствия входа."
            ],
            "cta_h3": "Торгуйте с публичным регулируемым брокером",
            "cta_p": "Откройте бесплатный демо-счет в Plus500 для тестирования платформы с рыночными котировками.",
            "cta_btn": "Открыть бесплатный счет Plus500 →",
            "risk_warn": "⚠️ Предупреждение о рисках: CFD являются сложными инструментами и несут высокий риск быстрой потери денег из-за кредитного плеча."
        },
        "ro": {
            "title": "Este Plus500 Sigur? Recenzie de Securitate și Audit 2026",
            "description": "Este Plus500 sigur? Citește recenzia noastră de expert despre Plus500. Verificăm reglementarea LSE, FCA, CySEC, ASIC și siguranța fondurilor.",
            "back": "← Înapoi la Verificatorul Principal",
            "h1": "Plus500 <span>Recenzie de Securitate</span>",
            "subtitle": "Companie listată public la Borsa din Londra (LSE: PLUS). Broker reglementat global.",
            "badge_trust": "91% Scor de Încredere",
            "is_safe_h2": "Este Plus500 un Broker Legit sau o Escrocherie?",
            "is_safe_p": "<strong>Verdict: 100% Legitim & Listat Public.</strong> Plus500 este o companie FTSE 250 listată la Bursa de Valori din Londra (LSE: PLUS). Reglementat de autorități de top precum FCA (Marea Britanie), CySEC (Cipru), ASIC (Australia) și MAS (Singapore). Raportarea financiară publică garantează o transparență fiscală totală.",
            "profile_h2": "Profilul de Reglementare Plus500",
            "th_entity": "Entități Corporative",
            "th_reg": "Reglementatori Financiari",
            "th_protect": "Schemă de Protecție a Investitorilor",
            "th_age": "Înregistrare Domeniu",
            "val_entity": "Plus500UK Ltd, Plus500CY Ltd, Plus500AU Pty Ltd, Plus500SG Pte Ltd",
            "val_reg": "FCA (UK) - Licență 509909<br>CySEC (Cipru) - Licență 250/14<br>ASIC (Australia) - AFSL 417727<br>MAS (Singapore) - CMS100648",
            "val_protect": "Până la £85,000 (UK FSCS) / Până la €20,000 (Cyprus ICF)",
            "val_age": "Înregistrat în 2008 (18 ani de activitate)",
            "pros_h2": "Puncte Forte & Limitări",
            "pros_title": "✓ Puncte Forte (Avantaje)",
            "cons_title": "✕ Factori de Risc (Dezavantaje)",
            "pros_list": [
                "Listat public la Bursa de Valori din Londra — transparență financiară de 100%.",
                "Licențiat de FCA, CySEC, ASIC și MAS.",
                "Platformă intuitivă, modernă și extrem de sigură.",
                "Instrumente gratuite de gestionare a riscurilor și alerte de preț în timp real."
            ],
            "cons_list": [
                "Nu suportă platformele MetaTrader 4 / MetaTrader 5 (doar platformă proprie).",
                "Taxă de inactivitate aplicată după 3 luni de lipsă de autentificare."
            ],
            "cta_h3": "Tranzacționează cu un Broker Listat Public și Reglementat",
            "cta_p": "Deschide un cont gratuit de test la Plus500 pentru a încerca platforma lor cu cote în timp real.",
            "cta_btn": "Deschide Cont Gratuit Plus500 ↗",
            "risk_warn": "⚠️ Avertisment de risc: CFD-urile sunt instrumente complexe și vin cu un risc ridicat de a pierde bani rapid din cauza levierului."
        },
        "it": {
            "title": "Plus500 è Sicuro? Recensione di Sicurezza e Audit 2026",
            "description": "Plus500 è sicuro? Leggi la nostra recensione esperta su Plus500. Verifichiamo la quotazione LSE, licenze FCA, CySEC, ASIC e sicurezza fondi.",
            "back": "← Torna al Verificatore Principale",
            "h1": "Plus500 <span>Recensione di Sicurezza</span>",
            "h1_sub": "Società quotata alla Borsa di Londra (LSE: PLUS). Broker CFD regolamentato a livello globale.",
            "badge_trust": "91% Punteggio di Affidabilità",
            "is_safe_h2": "Plus500 è Legittimo o una Truffa?",
            "is_safe_p": "<strong>Verdetto: 100% Legittimo & Quotato in Borsa.</strong> Plus500 è un'azienda FTSE 250 quotata alla Borsa di Londra (LSE: PLUS). Regolamentato da autorità di primo livello tra cui FCA (UK), CySEC (Cipro), ASIC (Australia) e MAS (Singapore). I bilanci pubblici garantiscono una totale trasparenza finanziaria.",
            "profile_h2": "Profilo Regolamentare Plus500",
            "th_entity": "Entità Societarie",
            "th_reg": "Regolatori Finanziari",
            "th_protect": "Schema di Protezione degli Investitori",
            "th_age": "Registrazione Dominio",
            "val_entity": "Plus500UK Ltd, Plus500CY Ltd, Plus500AU Pty Ltd, Plus500SG Pte Ltd",
            "val_reg": "FCA (UK) - Licenza 509909<br>CySEC (Cipro) - Licenza 250/14<br>ASIC (Australia) - AFSL 417727<br>MAS (Singapore) - CMS100648",
            "val_protect": "Fino a £85.000 (UK FSCS) / Fino a €20.000 (Cyprus ICF)",
            "val_age": "Registrato nel 2008 (18 anni di operatività)",
            "pros_h2": "Vantaggi & Svantaggi",
            "pros_title": "✓ Punti di Forza (Pro)",
            "cons_title": "✕ Fattori di Rischio (Contro)",
            "pros_list": [
                "Quotato pubblicamente alla Borsa di Londra (LSE: PLUS) — trasparenza finanziaria al 100%.",
                "Licenziato da FCA, CySEC, ASIC e MAS.",
                "Piattaforma proprietaria intuitiva, moderna e sicura.",
                "Strumenti gratuiti di gestione del rischio e avvisi sui prezzi in tempo reale."
            ],
            "cons_list": [
                "Non supporta MetaTrader 4 / MetaTrader 5 (solo piattaforma proprietaria).",
                "Commissione di inattività applicata dopo 3 mesi di inattività."
            ],
            "cta_h3": "Fai Trading con un Broker Quotato e Regolamentato",
            "cta_p": "Apri un conto demo gratuito su Plus500 per testare la loro piattaforma con quotazioni in tempo reale.",
            "cta_btn": "Apri Conto Ufficiale su Plus500 ↗",
            "risk_warn": "⚠️ Avviso di rischio: I CFD sono strumenti complessi e comportano un elevato rischio di perdere denaro rapidamente a causa della leva finanziaria."
        },
        "de": {
            "title": "Ist Plus500 sicher? Sicherheitsbewertung & Audit 2026",
            "description": "Ist Plus500 sicher? Lesen Sie unsere Expertenbewertung zu Plus500. Prüfung der LSE-Börsennotierung, FCA, CySEC, ASIC Lizenzen und Sicherheit.",
            "back": "← Zurück zur Haupt-Prüfseite",
            "h1": "Plus500 <span>Sicherheitsbericht</span>",
            "subtitle": "Börsennotiertes Unternehmen an der Londoner Börse (LSE: PLUS). Global regulierter CFD-Broker.",
            "badge_trust": "91% Vertrauensbewertung",
            "is_safe_h2": "Ist Plus500 seriös oder ein Betrug?",
            "is_safe_p": "<strong>Urteil: 100% Seriös & Börsennotiert.</strong> Plus500 ist ein FTSE 250 Unternehmen, das an der London Stock Exchange (LSE: PLUS) gehandelt wird. Reguliert durch Spitzenaufsichtsbehörden wie die FCA (UK), CySEC (Zypern), ASIC (Australien) und MAS (Singapur). Öffentliche Finanzberichte garantieren volle finanzielle Transparenz.",
            "profile_h2": "Regulierungsprofil Plus500",
            "th_entity": "Gesellschaftsgesellschaften",
            "th_reg": "Finanzaufsichtsbehörden",
            "th_protect": "Anlegerschutzsystem",
            "th_age": "Domainregistrierung",
            "val_entity": "Plus500UK Ltd, Plus500CY Ltd, Plus500AU Pty Ltd, Plus500SG Pte Ltd",
            "val_reg": "FCA (UK) - Lizenz 509909<br>CySEC (Zypern) - Lizenz 250/14<br>ASIC (Australien) - AFSL 417727<br>MAS (Singapur) - CMS100648",
            "val_protect": "Bis zu £85.000 (UK FSCS) / Bis zu €20.000 (Cyprus ICF)",
            "val_age": "Registriert 2008 (18 Jahre Erfahrung)",
            "pros_h2": "Vor- und Nachteile",
            "pros_title": "✓ Wichtigste Stärken (Vorteile)",
            "cons_title": "✕ Risikofaktoren (Nachteile)",
            "pros_list": [
                "Börsennotiert an der Londoner Börse — 100% finanzielle Transparenz.",
                "Lizenziert durch FCA, CySEC, ASIC und MAS.",
                "Benutzerfreundliche, moderne und extrem sichere Handelsplattform.",
                "Kostenlose Risikomanagement-Tools und Preisalarme in Echtzeit enthalten."
            ],
            "cons_list": [
                "Unterstützt keine MetaTrader 4 / MetaTrader 5 Plattformen (nur eigene Handelsplattform).",
                "Inaktivitätsgebühr wird nach 3 Monaten ohne Login erhoben."
            ],
            "cta_h3": "Handeln Sie mit einem börsennotierten & regulierten Broker",
            "cta_p": "Eröffnen Sie ein kostenloses Demokonto bei Plus500, um die Plattform mit Echtzeitkursen zu testen.",
            "cta_btn": "Kostenloses Plus500 Konto Eröffnen ↗",
            "risk_warn": "⚠️ Risikowarnung: CFDs sind komplexe Instrumente und gehen wegen der Hebelwirkung mit einem hohen Risiko einher, schnell Geld zu verlieren."
        },
        "es": {
            "title": "¿Es Plus500 Seguro? Reseña de Seguridad y Auditoría 2026",
            "description": "¿Es seguro Plus500? Lea nuestra reseña de expertos sobre Plus500. Verificación de cotización en LSE, FCA, CySEC, ASIC y fondos seguros.",
            "back": "← Volver al Verificador Principal",
            "h1": "Plus500 <span>Reseña de Seguridad</span>",
            "subtitle": "Empresa cotizada en la Bolsa de Londres (LSE: PLUS). Bróker de CFD regulado globalmente.",
            "badge_trust": "91% Puntuación de Confianza",
            "is_safe_h2": "¿Es Plus500 Legítimo o una Estafa?",
            "is_safe_p": "<strong>Veredicto: 100% Legítimo y Cotizado en Bolsa.</strong> Plus500 es una empresa del índice FTSE 250 cotizada en la Bolsa de Valores de Londres (LSE: PLUS). Regulado por reguladores internacionales de primer nivel, incluidos FCA (Reino Unido), CySEC (Chipre), ASIC (Australia) y MAS (Singapur). Los informes financieros públicos garantizan total transparencia fiscal.",
            "profile_h2": "Perfil Regulatorio de Plus500",
            "th_entity": "Entidades Corporativas",
            "th_reg": "Reguladores Financieros",
            "th_protect": "Fondo de Garantía de Inversiones",
            "th_age": "Registro de Dominio",
            "val_entity": "Plus500UK Ltd, Plus500CY Ltd, Plus500AU Pty Ltd, Plus500SG Pte Ltd",
            "val_reg": "FCA (UK) - Licencia 509909<br>CySEC (Chipre) - Licencia 250/14<br>ASIC (Australia) - AFSL 417727<br>MAS (Singapur) - CMS100648",
            "val_protect": "Hasta £85,000 (UK FSCS) / Hasta €20,000 (Cyprus ICF)",
            "val_age": "Registrado en 2008 (18 años de trayectoria)",
            "pros_h2": "Pros y Contras",
            "pros_title": "✓ Fortalezas Clave (Pros)",
            "cons_title": "✕ Factores de Riesgo (Contras)",
            "pros_list": [
                "Cotizado públicamente en la Bolsa de Londres — 100% transparencia financiera.",
                "Licenciado por FCA, CySEC, ASIC y MAS.",
                "Plataforma propia muy fácil de usar, moderna y segura.",
                "Herramientas gratuitas de gestión de riesgos y alertas de precios en tiempo real."
            ],
            "cons_list": [
                "No es compatible con MetaTrader 4 / MetaTrader 5 (solo plataforma propia).",
                "Se aplica tarifa de inactividad tras 3 meses sin iniciar sesión."
            ],
            "cta_h3": "Opere con un Bróker Cotizado en Bolsa y Regulado",
            "cta_p": "Abra una cuenta demo gratuita en Plus500 para probar su plataforma propia con precios en tiempo real.",
            "cta_btn": "Abrir Cuenta Gratis en Plus500 ↗",
            "risk_warn": "⚠️ Advertencia de riesgo: Los CFD son instrumentos complejos y conllevan un alto riesgo de perder dinero rápidamente debido al apalancamiento."
        },
        "fr": {
            "title": "Est-ce que Plus500 est Sûr? Avis de Sécurité et Audit 2026",
            "description": "Plus500 est-il fiable? Lisez notre avis d'expert sur Plus500. Vérification de cotation LSE, licences FCA, CySEC, ASIC et sécurité des fonds.",
            "back": "← Retour au Vérificateur Principal",
            "h1": "Plus500 <span>Avis de Sécurité</span>",
            "subtitle": "Société cotée à la Bourse de Londres (LSE: PLUS). Courtier CFD réglementé mondialement.",
            "badge_trust": "91% Score de Confiance",
            "is_safe_h2": "Plus500 est-il Légitime ou une Arnaque?",
            "is_safe_p": "<strong>Verdict: 100% Légitime & Coté en Bourse.</strong> Plus500 est une entreprise membre du FTSE 250 cotée à la Bourse de Londres (LSE: PLUS). Réglementé par des autorités majeures incluant la FCA (Royaume-Uni), la CySEC (Chypre), l'ASIC (Australie) et la MAS (Singapour). Le reporting financier public garantit une totale transparence fiscale.",
            "profile_h2": "Profil Réglementaire de Plus500",
            "th_entity": "Entités Sociales",
            "th_reg": "Régulateurs Financiers",
            "th_protect": "Système de Protection des Investisseurs",
            "th_age": "Enregistrement du Domaine",
            "val_entity": "Plus500UK Ltd, Plus500CY Ltd, Plus500AU Pty Ltd, Plus500SG Pte Ltd",
            "val_reg": "FCA (UK) - Licence 509909<br>CySEC (Chypre) - Licence 250/14<br>ASIC (Australie) - AFSL 417727<br>MAS (Singapour) - CMS100648",
            "val_protect": "Jusqu'à £85,000 (UK FSCS) / Jusqu'à €20,000 (Cyprus ICF)",
            "val_age": "Enregistré en 2008 (18 ans d'expérience)",
            "pros_h2": "Avantages & Inconvénients",
            "pros_title": "✓ Points Forts (Avantages)",
            "cons_title": "✕ Facteurs de Risque (Inconvénients)",
            "pros_list": [
                "Coté en bourse à Londres (LSE: PLUS) — 100% de transparence financière.",
                "Sous licence FCA, CySEC, ASIC et MAS.",
                "Plateforme propriétaire ergonomique, moderne et sécurisée.",
                "Outils gratuits de gestion des risques et alertes de prix en temps réel."
            ],
            "cons_list": [
                "Ne prend pas en charge MetaTrader 4 / MetaTrader 5 (plateforme propriétaire uniquement).",
                "Frais d'inactivité appliqués après 3 mois sans connexion."
            ],
            "cta_h3": "Tradez avec un Courtier Coté en Bourse et Réglementé",
            "cta_p": "Ouvrez un compte démo gratuit chez Plus500 pour tester leur plateforme avec cours en direct.",
            "cta_btn": "Ouvrir un Compte Gratuit chez Plus500 ↗",
            "risk_warn": "⚠️ Avertissement de risque: Les CFD sont des instruments complexes et présentent un risque élevé de perte rapide en capital."
        },
        "pt": {
            "title": "Plus500 é Seguro? Análise de Segurança e Auditoria 2026",
            "description": "A Plus500 é segura? Leia nossa análise de especialista sobre a Plus500. Verificamos cotação na LSE, licenças FCA, CySEC, ASIC e proteção financeira.",
            "back": "← Voltar ao Verificador Principal",
            "h1": "Plus500 <span>Análise de Segurança</span>",
            "subtitle": "Empresa listada na Bolsa de Londres (LSE: PLUS). Corretora de CFD regulamentada globalmente.",
            "badge_trust": "91% Pontuação de Confiança",
            "is_safe_h2": "A Plus500 é Legítima ou um Golpe?",
            "is_safe_p": "<strong>Veredito: 100% Legítima & Listada em Bolsa.</strong> A Plus500 é uma empresa do índice FTSE 250 listada na Bolsa de Valores de Londres (LSE: PLUS). Regulamentada por órgãos de elite como a FCA (Reino Unido), CySEC (Chipre), ASIC (Austrália) e MAS (Cingapura). Os balanços públicos garantem total transparência financeira.",
            "profile_h2": "Perfil Regulatório da Plus500",
            "th_entity": "Entidades Corporativas",
            "th_reg": "Reguladores Financeiros",
            "th_protect": "Esquema de Proteção do Investidor",
            "th_age": "Registro de Domínio",
            "val_entity": "Plus500UK Ltd, Plus500CY Ltd, Plus500AU Pty Ltd, Plus500SG Pte Ltd",
            "val_reg": "FCA (UK) - Licença 509909<br>CySEC (Chipre) - Licença 250/14<br>ASIC (Austrália) - AFSL 417727<br>MAS (Cingapura) - CMS100648",
            "val_protect": "Até £85.000 (UK FSCS) / Até €20.000 (Cyprus ICF)",
            "val_age": "Registrado em 2008 (18 anos de atuação)",
            "pros_h2": "Prós e Contras",
            "pros_title": "✓ Pontos Fortes (Prós)",
            "cons_title": "✕ Fatores de Risco (Contras)",
            "pros_list": [
                "Listada publicamente na Bolsa de Londres — 100% de transparência financeira.",
                "Licenciada pela FCA, CySEC, ASIC e MAS.",
                "Plataforma própria intuitiva, moderna e extremamente segura.",
                "Ferramentas gratuitas de gestão de risco e alertas de preço em tempo real."
            ],
            "cons_list": [
                "Não suporta MetaTrader 4 / MetaTrader 5 (apenas plataforma própria).",
                "Taxa de inatividade cobrada após 3 meses sem acesso."
            ],
            "cta_h3": "Negocie com uma Corretora Listada em Bolsa e Regulamentada",
            "cta_p": "Abra uma conta demo gratuita na Plus500 para testar a plataforma com cotações em tempo real.",
            "cta_btn": "Abrir Conta Grátis na Plus500 ↗",
            "risk_warn": "⚠️ Aviso de risco: Os CFDs são instrumentos complexos e apresentam um elevado risco de perder dinheiro rapidamente devido à alavancagem."
        }
    }
}

print("Loaded comprehensive review translation template for Plus500!")
