import os

broker_i18n_patch = '''
// Broker Descriptions & Verdicts Multi-Language Translation Map
const brokerTranslations = {
    exness: {
        ru: {
            title: "Мировой лидер по объему торгов и мгновенному выводу средств",
            text: "Exness — крупнейший в мире розничный форекс-брокер с месячным объемом торгов более 4 триллионов долларов. Регулируется FCA (Великобритания), CySEC (Кипр) и FSC."
        },
        ro: {
            title: "Lider Mondial de Volum și Retrageri Instantanee 24/7",
            text: "Exness este cel mai mare broker forex de retail din lume, cu un volum lunar de tranzacționare de peste 4 trilioane USD. Reglementat de FCA (Marea Britanie), CySEC și FSC."
        },
        it: {
            title: "Leader Mondiale di Volume e prelievi istantanei 24/7",
            text: "Exness è il più grande broker forex al dettaglio al mondo con un volume mensile di scambi superiore a 4 trilioni di dollari. Regolamentato da FCA, CySEC e FSC."
        },
        de: {
            title: "Weltweiter Volumenmarktführer & Automatische Sofortauszahlungen",
            text: "Exness ist der weltweit größte Retail-Forex-Broker mit einem monatlichen Handelsvolumen von über 4 Billionen USD. Reguliert durch FCA, CySEC und FSC."
        },
        es: {
            title: "Líder Mundial en Volumen y Retiros Instantáneos 24/7",
            text: "Exness es el broker de forex minorista más grande del mundo, con un volumen de operaciones mensual de más de 4 billones de dólares. Regulado por FCA, CySEC y FSC."
        },
        fr: {
            title: "Leader Mondial du Volume et Retraits Instantanés 24/7",
            text: "Exness est le plus grand courtier forex au détail au monde avec un volume de transactions mensuel de plus de 4 billions de dollars. Réglementé par FCA, CySEC et FSC."
        },
        pt: {
            title: "Líder Mundial em Volume e Saques Instantâneos 24/7",
            text: "Exness é a maior corretora forex de varejo do mundo, com um volume mensal de negociação superior a US$ 4 trilhões. Regulamentada por FCA, CySEC e FSC."
        }
    },
    etoro: {
        ru: {
            title: "Высокозащищенный и регулируемый глобальный брокер",
            text: "eToro — ведущая мировая платформа социал-трейдинга, которой доверяют более 30 миллионов пользователей по всему миру. Регулируется FCA (Великобритания), CySEC (Кипр), ASIC (Австралия) и FINRA (США)."
        },
        ro: {
            title: "Broker Global Reglementat și de Înaltă Securitate",
            text: "eToro este o platformă lider mondial de social trading în care au încredere peste 30 de milioane de utilizatori globale. Reglementat de FCA (Marea Britanie), CySEC (Cipru), ASIC și FINRA."
        },
        it: {
            title: "Broker Globale Regolamentato ad Alta Sicurezza",
            text: "eToro è una piattaforma leader globale di social trading con oltre 30 milioni di utenti in tutto il mondo. Regolamentato da FCA, CySEC, ASIC e FINRA."
        },
        de: {
            title: "Hochsicherer und Regulierter Globaler Broker",
            text: "eToro ist eine weltweit führende Social-Trading-Plattform, der über 30 Millionen Nutzer weltweit vertrauen. Reguliert durch FCA, CySEC, ASIC und FINRA."
        },
        es: {
            title: "Broker Global Regulado y de Alta Seguridad",
            text: "eToro es una plataforma líder mundial de social trading en la que confían más de 30 millones de usuarios en todo el mundo. Regulado por FCA, CySEC, ASIC y FINRA."
        },
        fr: {
            title: "Courtier Global Réglementé et Hautement Sécurisé",
            text: "eToro est une plateforme mondiale majeure de trading social à laquelle font confiance plus de 30 millions d'utilisateurs. Réglementé par FCA, CySEC, ASIC et FINRA."
        },
        pt: {
            title: "Corretora Global Regulamentada e de Alta Segurança",
            text: "eToro é uma plataforma líder global de social trading em que confiam mais de 30 milhões de usuários em todo o mundo. Regulamentada por FCA, CySEC, ASIC e FINRA."
        }
    },
    xm: {
        ru: {
            title: "Надежный и регулируемый международный брокер",
            text: "XM Group — один из крупнейших брокеров в мире, обслуживающий более 10 миллионов клиентов в 190+ странах. Регулируется FCA (Великобритания), CySEC (Кипр) и ASIC (Австралия)."
        },
        ro: {
            title: "Broker Internațional Reglementat și de Încredere",
            text: "XM Group este unul dintre cei mai mari brokeri din lume, deservind peste 10 milioane de clienți în peste 190 de țări. Reglementat de FCA, CySEC și ASIC."
        },
        it: {
            title: "Broker Internazionale Regolamentato e Affidabile",
            text: "XM Group è uno dei più grandi broker al mondo, al servizio di oltre 10 milioni di clienti in più di 190 paesi. Regolamentato da FCA, CySEC e ASIC."
        },
        de: {
            title: "Zuverlässiger und Regulierter Internationaler Broker",
            text: "XM Group ist einer der größten Broker der Welt und bedient über 10 Millionen Kunden in mehr als 190 Ländern. Reguliert durch FCA, CySEC und ASIC."
        },
        es: {
            title: "Broker Internacional Regulado y de Confianza",
            text: "XM Group es uno de los brokers más grandes del mundo y presta servicios a más de 10 millones de clientes en más de 190 países. Regulado por FCA, CySEC y ASIC."
        },
        fr: {
            title: "Courtier International Réglementé et Fiable",
            text: "XM Group est l'un des plus grands courtiers au monde, servant plus de 10 millions de clients dans plus de 190 pays. Réglementé par FCA, CySEC et ASIC."
        },
        pt: {
            title: "Corretora Internacional Regulamentada e Confiável",
            text: "XM Group é uma das maiores corretoras do mundo, atendendo a mais de 10 milhões de clientes em mais de 190 países. Regulamentada por FCA, CySEC e ASIC."
        }
    },
    plus500: {
        ru: {
            title: "Публичная компания на Лондонской фондовой бирже (LSE: PLUS)",
            text: "Plus500 — ведущий провайдер CFD, котируемый на основной площадке Лондонской фондовой биржи. Регулируется FCA (Великобритания), CySEC (Кипр), ASIC (Австралия) и MAS (Сингапур)."
        },
        ro: {
            title: "Companie Listată Public la Bursa din Londra (LSE: PLUS)",
            text: "Plus500 este un furnizor de top de CFD-uri listat pe piața principală a Bursei din Londra. Reglementat de FCA, CySEC, ASIC și MAS."
        },
        it: {
            title: "Società Quotata alla Borsa di Londra (LSE: PLUS)",
            text: "Plus500 è un fornitore leader di CFD quotato sul mercato principale della Borsa di Londra. Regolamentato da FCA, CySEC, ASIC e MAS."
        },
        de: {
            title: "Börsennotiertes Unternehmen an der Londoner Börse (LSE: PLUS)",
            text: "Plus500 ist ein führender CFD-Anbieter, der am Hauptmarkt der Londoner Börse notiert ist. Reguliert durch FCA, CySEC, ASIC und MAS."
        },
        es: {
            title: "Empresa Cotizada en la Bolsa de Londres (LSE: PLUS)",
            text: "Plus500 es un proveedor líder de CFD que cotiza en el mercado principal de la Bolsa de Valores de Londres. Regulado por FCA, CySEC, ASIC y MAS."
        },
        fr: {
            title: "Société Cotée à la Bourse de Londres (LSE: PLUS)",
            text: "Plus500 est un fournisseur majeur de CFD coté sur le marché principal de la Bourse de Londres. Réglementé par FCA, CySEC et MAS."
        },
        pt: {
            title: "Empresa Cotada na Bolsa de Valores de Londres (LSE: PLUS)",
            text: "Plus500 é uma provedora líder de CFDs listada no mercado principal da Bolsa de Valores de Londres. Regulamentada por FCA, CySEC, ASIC e MAS."
        }
    },
    avatrade: {
        ru: {
            title: "Надежный брокер с 9 регуляторными лицензиями",
            text: "AvaTrade — пионер онлайн-трейдинга с 2006 года, имеющий регуляторные лицензии на 5 континентах (Central Bank of Ireland, ASIC, FSCA, JFSA)."
        },
        ro: {
            title: "Broker de Încredere cu 9 Licențe de Reglementare",
            text: "AvaTrade este un pionier al tradingului online din 2006, având licențe de reglementare pe 5 continente (Banca Centrală a Irlandei, ASIC, FSCA)."
        },
        it: {
            title: "Broker Affidabile con 9 Licenze di Regolamentazione",
            text: "AvaTrade è un pioniere del trading online dal 2006, con licenze di regolamentazione in 5 continenti (Banca Centrale d'Irlanda, ASIC, FSCA)."
        },
        de: {
            title: "Zuverlässiger Broker mit 9 Regulierungslizenzen",
            text: "AvaTrade ist seit 2006 ein Pionier des Online-Handels mit Regulierungslizenzen auf 5 Kontinenten (Zentralbank von Irland, ASIC, FSCA)."
        },
        es: {
            title: "Broker de Confianza con 9 Licencias Reguladoras",
            text: "AvaTrade es un pionero del trading en línea desde 2006, con licencias reguladoras en 5 continentes (Banco Central de Irlanda, ASIC, FSCA)."
        },
        fr: {
            title: "Courtier Fiable avec 9 Licences de Réglementation",
            text: "AvaTrade est un pionnier du trading en ligne depuis 2006, disposant de licences de réglementation sur 5 continents (Banque centrale d'Irlande, ASIC, FSCA)."
        },
        pt: {
            title: "Corretora Confiável com 9 Licenças de Regulamentação",
            text: "AvaTrade é uma pioneira do trading online desde 2006, com licenças de regulamentação em 5 continentes (Banco Central da Irlanda, ASIC, FSCA)."
        }
    }
};
'''

app_files = ['dating-photo-checker/broker-verifier/app.js', 'broker-verifier/app.js']

fetch_target = "verdictTitle.textContent = data.verdict_title || t.awaitingEval;\n        verdictText.textContent = data.verdict_text || t.scanCompleted;"

fetch_replacement = '''        let vTitle = data.verdict_title || t.awaitingEval;
        let vText = data.verdict_text || t.scanCompleted;

        // Check if localized translation exists for featured broker
        const bKey = (data.broker_name || '').toLowerCase().replace(/\\s+/g, '');
        for (const k in brokerTranslations) {
            if (bKey.includes(k)) {
                const tr = brokerTranslations[k][currentLang];
                if (tr) {
                    vTitle = tr.title;
                    vText = tr.text;
                }
                break;
            }
        }

        verdictTitle.textContent = vTitle;
        verdictText.textContent = vText;'''

for af in app_files:
    if os.path.exists(af):
        with open(af, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'const brokerTranslations =' not in content:
            content = broker_i18n_patch + '\n' + content

        if fetch_target in content:
            content = content.replace(fetch_target, fetch_replacement)

        with open(af, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Injected full broker translations into {af}")

print("Full broker translation engine applied successfully!")
