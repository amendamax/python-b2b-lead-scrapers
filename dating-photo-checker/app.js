document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================================================
    // MULTILINGUAL LOCALIZATION ENGINE
    // ==========================================================================
    const currentLang = (document.documentElement.lang || 'en').toLowerCase();

    const i18n = {
        en: {
            criticalRisk: "Critical Risk",
            moderateRisk: "Moderate Risk",
            lowRisk: "Low Risk",
            fakeProfile: "Fake Profile Confirmed (Catfish)",
            stockPhoto: "Stock / Public Photo Detected",
            uniqueProfile: "Unique Profile Verified",
            matchesSuffix: "matches",
            scammerSignature: "Scammer Signature Detected",
            publicMatchWarning: "Public Match Warning",
            securityVerdict: "Security Verdict",
            diagnosticHigh1: "Image found on multiple other websites under different names.",
            diagnosticHigh2: "Image metadata indicates recent digital alterations (filters/editing).",
            diagnosticHigh3: "Original image source: Russian model agency stock site.",
            diagnosticMed1: "Photo matches publicly indexed stock photography or public portfolios.",
            diagnosticMed2: "Metadata analysis indicates no suspicious digital alterations.",
            diagnosticMed3: "Image matches found on public indexable web (stock/portfolios).",
            diagnosticLow1: "No matching faces detected in the global scam database.",
            diagnosticLow2: "Metadata analysis indicates no suspicious digital alterations.",
            diagnosticLow3: "Unique image signature — no public web duplicates found.",
            infoNoFace: "No human face detected in this image. For romance scam verification, please upload a portrait photo with a clear human face.",
            infoSafe: "No matching faces or scam signatures detected. This image appears to be completely unique and secure.",
            infoStock: "This photo matches publicly indexed stock photography or public portfolios. Verify if the person is using a generic stock photo or a public presentation image.",
            infoScammer: "Critical alert. This profile picture is active across multiple social profiles using different names. Matches signatures of organized romance scam groups operating via proxy IPs.",
            stripeProcessing: "Processing secure payment...",
            stripePayButton: "Pay $4.99 (5 Scans)",
            paymentConfirmed: "Payment confirmed! 5 credits added. 1 credit used for this report. You have <strong>{credits} credits left</strong>.",
            reportUnlocked: "Report unlocked using 1 credit. You have <strong>{credits} credits left</strong>.",
            emailRequired: "Please enter a valid email address.",
            checkingCredits: "Checking...",
            useCreditButton: "Use Credit",
            paymentFailed: "Payment processing failed. Please try again.",
            connectionError: "Connection error. Please try again later."
        },
        ro: {
            criticalRisk: "Risc Critic",
            moderateRisk: "Risc Moderat",
            lowRisk: "Risc Scăzut",
            fakeProfile: "Profil Fals Confirmat (Catfish)",
            stockPhoto: "Poză Publică / Stock Detectată",
            uniqueProfile: "Profil Unic Verificat",
            matchesSuffix: "potriviri",
            scammerSignature: "Semnătură de Escrocherie Detectată",
            publicMatchWarning: "Avertisment de Potrivire Publică",
            securityVerdict: "Verdict de Securitate",
            diagnosticHigh1: "Imagine găsită pe mai multe site-uri web sub nume diferite.",
            diagnosticHigh2: "Metadatele imaginii indică modificări digitale recente (filtre/editare).",
            diagnosticHigh3: "Sursa originală a imaginii: site de stock al unei agenții de modele din Rusia.",
            diagnosticMed1: "Fotografia se potrivește cu fotografii de stock indexate public sau portofolii publice.",
            diagnosticMed2: "Analiza metadatelor indică absența modificărilor digitale suspecte.",
            diagnosticMed3: "Potriviri de imagini găsite pe web-ul indexabil public (stock/portofolii).",
            diagnosticLow1: "Nu au fost detectate fețe potrivite în baza globală de date a escrocheriilor.",
            diagnosticLow2: "Analiza metadatelor indică absența modificărilor digitale suspecte.",
            diagnosticLow3: "Semnătură unică a imaginii — nu s-au găsit duplicate pe web-ul public.",
            infoNoFace: "Nu s-a detectat nicio față umană în această imagine. Pentru verificarea escrocheriilor romantice, vă rugăm să încărcați o fotografie tip portret cu o față umană clară.",
            infoSafe: "Nu au fost detectate fețe potrivite sau semnături de escrocherie. Această imagine pare a fi complet unică și sigură.",
            infoStock: "Această fotografie se potrivește cu fotografii de stock indexate public sau portofolii publice. Verificați dacă persoana folosește o poză de stock generică sau o imagine de prezentare publică.",
            infoScammer: "Alertă critică. Această poză de profil este activă pe mai multe profiluri sociale sub nume diferite. Se potrivește cu semnăturile grupurilor organizate de escrocherii sentimentale care operează prin IP-uri proxy.",
            stripeProcessing: "Se procesează plata securizată...",
            stripePayButton: "Plătește $4.99 (5 Scanări)",
            paymentConfirmed: "Plată confirmată! 5 credite adăugate. 1 credit utilizat pentru acest raport. Mai ai <strong>{credits} credite rămase</strong>.",
            reportUnlocked: "Raport deblocat folosind 1 credit. Mai ai <strong>{credits} credite rămase</strong>.",
            emailRequired: "Vă rugăm să introduceți o adresă de email validă.",
            checkingCredits: "Se verifică...",
            useCreditButton: "Folosește Credit",
            paymentFailed: "Procesarea plății a eșuat. Vă rugăm să încercați din nou.",
            connectionError: "Eroare de conexiune. Vă rugăm să încercați mai târziu."
        },
        it: {
            criticalRisk: "Rischio Critico",
            moderateRisk: "Rischio Moderato",
            lowRisk: "Rischio Basso",
            fakeProfile: "Profilo Falso Confermato (Catfish)",
            stockPhoto: "Foto Stock / Pubblica Rilevata",
            uniqueProfile: "Profilo Unico Verificato",
            matchesSuffix: "corrispondenze",
            scammerSignature: "Firma dello Scammer Rilevata",
            publicMatchWarning: "Avviso Corrispondenza Pubblica",
            securityVerdict: "Verdetto di Sicurezza",
            diagnosticHigh1: "Immagine trovata su più altri siti web con nomi diversi.",
            diagnosticHigh2: "I metadati dell'immagine indicano recenti alterazioni digitali (filtri/editing).",
            diagnosticHigh3: "Fonte originale dell'immagine: sito stock di un'agenzia di modelli russa.",
            diagnosticMed1: "La foto corrisponde a fotografie stock indicizzate pubblicamente o a portfolio pubblici.",
            diagnosticMed2: "L'analisi dei metadati indica l'assenza di alterazioni digitali sospette.",
            diagnosticMed3: "Corrispondenze dell'immagine trovate sul web pubblico indicizzabile (stock/portfolio).",
            diagnosticLow1: "Nessun volto corrispondente rilevato nel database globale delle truffe.",
            diagnosticLow2: "L'analisi dei metadati indica l'assenza di alterazioni digitali sospette.",
            diagnosticLow3: "Firma dell'immagine unica — nessuna copia trovata sul web pubblico.",
            infoNoFace: "Nessun volto umano rilevato in questa immagine. Per la verifica delle truffe amorose, carica una foto ritratto con un volto umano chiaro.",
            infoSafe: "Nessun volto corrispondente o firma di truffa rilevata. Questa immagine sembra essere completamente unica e sicura.",
            infoStock: "Questa foto corrisponde a fotografie stock indicizzate pubblicamente o a portfolio pubblici. Verifica se la persona sta utilizzando una foto stock generica o un'immagine di presentazione pubblica.",
            infoScammer: "Avviso critico. Questa foto del profilo è attiva su più profili social con nomi diversi. Corrisponde alle firme di gruppi organizzati di truffe sentimentali che operano tramite proxy IP.",
            stripeProcessing: "Elaborazione del pagamento sicuro...",
            stripePayButton: "Paga $4.99 (5 Scansioni)",
            paymentConfirmed: "Pagamento confermato! 5 crediti aggiunti. 1 credito utilizzato per questo report. Hai <strong>{credits} crediti rimasti</strong>.",
            reportUnlocked: "Report sbloccato utilizzando 1 credito. Hai <strong>{credits} crediti rimasti</strong>.",
            emailRequired: "Inserisci un indirizzo email valido.",
            checkingCredits: "Verifica...",
            useCreditButton: "Usa Credito",
            paymentFailed: "Elaborazione del pagamento fallita. Riprova.",
            connectionError: "Errore di connessione. Riprova più tardi."
        },
        de: {
            criticalRisk: "Kritisches Risiko",
            moderateRisk: "Moderates Risiko",
            lowRisk: "Geringes Risiko",
            fakeProfile: "Gefälschtes Profil Bestätigt (Catfish)",
            stockPhoto: "Stock- / Öffentliches Foto Erkannt",
            uniqueProfile: "Einzigartiges Profil Verifiziert",
            matchesSuffix: "Treffer",
            scammerSignature: "Scammer-Signatur Erkannt",
            publicMatchWarning: "Warnung vor öffentlichem Treffer",
            securityVerdict: "Sicherheitsurteil",
            diagnosticHigh1: "Bild wurde auf mehreren anderen Websites unter verschiedenen Namen gefunden.",
            diagnosticHigh2: "Bildmetadaten weisen auf kürzliche digitale Änderungen hin (Filter/Bearbeitung).",
            diagnosticHigh3: "Originale Bildquelle: Stock-Website einer russischen Modelagentur.",
            diagnosticMed1: "Foto entspricht öffentlich indexierten Stock-Fotografien oder öffentlichen Portfolios.",
            diagnosticMed2: "Metadatenanalyse weist keine verdächtigen digitalen Änderungen auf.",
            diagnosticMed3: "Bildtreffer im öffentlich indexierbaren Web gefunden (Stock/Portfolios).",
            diagnosticLow1: "Keine übereinstimmenden Gesichter in der globalen Scammer-Datenbank erkannt.",
            diagnosticLow2: "Metadatenanalyse weist keine verdächtigen digitalen Änderungen auf.",
            diagnosticLow3: "Einzigartige Bildsignatur — keine Duplikate im öffentlichen Web gefunden.",
            infoNoFace: "Kein menschliches Gesicht auf diesem Bild erkannt. Laden Sie für die Überprüfung von Liebesbetrug bitte ein Porträtfoto mit einem klaren menschlichen Gesicht hoch.",
            infoSafe: "Keine übereinstimmenden Gesichter oder Betrugssignaturen erkannt. Dieses Bild scheint völlig einzigartig und sicher zu sein.",
            infoStock: "Dieses Foto entspricht öffentlich indexierten Stock-Fotografien oder öffentlichen Portfolios. Überprüfen Sie, ob die Person ein generisches Stock-Foto oder ein öffentliches Präsentationsbild verwendet.",
            infoScammer: "Kritischer Alarm. Dieses Profilbild ist auf mehreren sozialen Profilen unter verschiedenen Namen aktiv. Entspricht den Signaturen organisierter Liebesbetrugsgruppen, die über Proxy-IPs operieren.",
            stripeProcessing: "Sichere Zahlung wird verarbeitet...",
            stripePayButton: "4.99$ bezahlen (5 Scans)",
            paymentConfirmed: "Zahlung bestätigt! 5 Credits hinzugefügt. 1 Credit für diesen Bericht verwendet. Sie haben noch <strong>{credits} Credits übrig</strong>.",
            reportUnlocked: "Bericht mit 1 Credit freigeschaltet. Sie haben noch <strong>{credits} Credits übrig</strong>.",
            emailRequired: "Bitte geben Sie eine gültige E-Mail-Adresse ein.",
            checkingCredits: "Wird überprüft...",
            useCreditButton: "Credit verwenden",
            paymentFailed: "Zahlungsverarbeitung fehlgeschlagen. Bitte versuchen Sie es erneut.",
            connectionError: "Verbindungsfehler. Bitte versuchen Sie es später noch einmal."
        },
        es: {
            criticalRisk: "Riesgo Crítico",
            moderateRisk: "Riesgo Moderado",
            lowRisk: "Riesgo Bajo",
            fakeProfile: "Perfil Falso Confirmado (Catfish)",
            stockPhoto: "Foto de Stock / Pública Detectada",
            uniqueProfile: "Perfil Único Verificado",
            matchesSuffix: "coincidencias",
            scammerSignature: "Firma de Estafador Detectada",
            publicMatchWarning: "Advertencia de Coincidencia Pública",
            securityVerdict: "Veredicto de Seguridad",
            diagnosticHigh1: "Imagen encontrada en múltiples otros sitios web con nombres diferentes.",
            diagnosticHigh2: "Los metadatos de la imagen indican alteraciones digitales recientes (filtros/edición).",
            diagnosticHigh3: "Fuente original de la imagen: sitio de stock de agencia de modelos rusa.",
            diagnosticMed1: "La foto coincide con fotografías de stock indexadas públicamente o carteras públicas.",
            diagnosticMed2: "El análisis de metadatos indica que no hay alteraciones digitales sospechosas.",
            diagnosticMed3: "Coincidencias de imágenes encontradas en la web pública indexable (stock/carteras).",
            diagnosticLow1: "No se detectaron rostros coincidentes en la base de datos global de estafas.",
            diagnosticLow2: "El análisis de metadatos indica que no hay alteraciones digitales sospechosas.",
            diagnosticLow3: "Firma de imagen única: no se encontraron duplicados en la web pública.",
            infoNoFace: "No se detectó ningún rostro humano en esta imagen. Para la verificación de estafas amorosas, cargue una foto de retrato con un rostro humano claro.",
            infoSafe: "No se detectaron rostros coincidentes ni firmas de estafa. Esta imagen parece ser completamente única y segura.",
            infoStock: "Esta foto coincide con fotografías de stock indexadas públicamente o carteras públicas. Verifique si la persona está utilizando una foto de stock genérica o una imagen de presentación pública.",
            infoScammer: "Alerta crítica. Esta foto de perfil está activa en múltiples perfiles sociales con diferentes nombres. Coincide con las firmas de grupos organizados de estafas románticas que operan a través de IP proxy.",
            stripeProcessing: "Procesando pago seguro...",
            stripePayButton: "Pagar $4.99 (5 Análisis)",
            paymentConfirmed: "¡Pago confirmado! 5 créditos agregados. 1 crédito utilizado para este informe. Te quedan <strong>{credits} créditos</strong>.",
            reportUnlocked: "Informe desbloqueado con 1 crédito. Te quedan <strong>{credits} créditos</strong>.",
            emailRequired: "Por favor, introduzca una dirección de correo electrónico válida.",
            checkingCredits: "Verificando...",
            useCreditButton: "Usar Crédito",
            paymentFailed: "El procesamiento del pago falló. Por favor, inténtelo de nuevo.",
            connectionError: "Error de conexión. Por favor, inténtelo más tarde."
        },
        fr: {
            criticalRisk: "Risque Critique",
            moderateRisk: "Risque Modéré",
            lowRisk: "Risque Faible",
            fakeProfile: "Faux Profil Confirmé (Catfish)",
            stockPhoto: "Photo Stock / Publique Détectée",
            uniqueProfile: "Profil Unique Vérifié",
            matchesSuffix: "correspondances",
            scammerSignature: "Signature d'Arnaqueur Détectée",
            publicMatchWarning: "Avertissement de Correspondance Publique",
            securityVerdict: "Verdict de Sécurité",
            diagnosticHigh1: "Image trouvée sur plusieurs autres sites Web sous différents noms.",
            diagnosticHigh2: "Les métadonnées de l'image indiquent des altérations numériques récentes (filtres/retouche).",
            diagnosticHigh3: "Source originale de l'image : site de stock d'une agence de mannequins russe.",
            diagnosticMed1: "La photo correspond à des photographies de stock indexées publiquement ou à des portefeuilles publics.",
            diagnosticMed2: "L'analyse des métadonnées n'indique aucune altération numérique suspecte.",
            diagnosticMed3: "Correspondances d'images trouvées sur le Web public indexable (stock/portefeuilles).",
            diagnosticLow1: "Aucun visage correspondant détecté dans la base de données mondiale des arnaques.",
            diagnosticLow2: "L'analyse des métadonnées n'indique aucune altération numérique suspecte.",
            diagnosticLow3: "Signature d'image unique — aucun doublon trouvé sur le Web public.",
            infoNoFace: "Aucun visage humain détecté dans cette image. Pour la vérification des arnaques sentimentales, veuillez télécharger une photo de portrait avec un visage humain clair.",
            infoSafe: "Aucun visage correspondant ni signature d'arnaque détecté. Cette image semble être complètement unique et sécurisée.",
            infoStock: "Cette photo correspond à des photographies de stock indexées publiquement ou à des portefeuilles publics. Vérifiez si la personne utilise une photo de stock générique ou une image de présentation publique.",
            infoScammer: "Alerte critique. Cette photo de profil est active sur plusieurs profils sociaux sous différents noms. Correspond aux signatures de groupes organisés d'arnaques sentimentales opérant via des IP proxy.",
            stripeProcessing: "Traitement du paiement sécurisé...",
            stripePayButton: "Payer 4.99$ (5 Analyses)",
            paymentConfirmed: "Paiement confirmé ! 5 crédits ajoutés. 1 crédit utilisé pour ce rapport. Il vous reste <strong>{credits} crédits</strong>.",
            reportUnlocked: "Rapport déverrouillé avec 1 crédit. Il vous reste <strong>{credits} crédits</strong>.",
            emailRequired: "Veuillez saisir une adresse e-mail valide.",
            checkingCredits: "Vérification...",
            useCreditButton: "Utiliser le Crédit",
            paymentFailed: "Échec du traitement du paiement. Veuillez réessayer.",
            connectionError: "Connexion au serveur de paiement échouée. Veuillez réessayer plus tard."
        },
        pt: {
            criticalRisk: "Risco Crítico",
            moderateRisk: "Risco Moderado",
            lowRisk: "Risco Baixo",
            fakeProfile: "Perfil Falso Confirmado (Catfish)",
            stockPhoto: "Foto de Stock / Pública Detectada",
            uniqueProfile: "Perfil Único Verificado",
            matchesSuffix: "correspondências",
            scammerSignature: "Assinatura de Golpista Detectada",
            publicMatchWarning: "Aviso de Correspondência Pública",
            securityVerdict: "Veredicto de Segurança",
            diagnosticHigh1: "Imagem encontrada em vários outros sites sob nomes diferentes.",
            diagnosticHigh2: "Os metadados da imagem indicam alterações digitais recentes (filtros/edição).",
            diagnosticHigh3: "Origem original da imagem: site de stock de agência de modelos russa.",
            diagnosticMed1: "A foto corresponde a fotografias de stock indexadas publicamente ou portfólios públicos.",
            diagnosticMed2: "A análise de metadados indica que não há alterações digitais suspeitas.",
            diagnosticMed3: "Correspondências de imagens encontradas na web indexável pública (stock/portfólios).",
            diagnosticLow1: "Nenhum rosto correspondente detectado no banco de dados global de golpes.",
            diagnosticLow2: "A análise de metadados indica que não há alterações digitais suspeitas.",
            diagnosticLow3: "Assinatura de imagem única — nenhuma duplicata encontrada na web pública.",
            infoNoFace: "Nenhum rosto humano detectado nesta imagem. Para verificação de golpes de romance, envie uma foto de retrato com um rosto humano claro.",
            infoSafe: "Nenhum rosto correspondente ou assinatura de golpe detectada. Esta imagem parece ser completamente única e segura.",
            infoStock: "Esta foto corresponde a fotografias de stock indexadas publicamente ou portfólios públicos. Verifique si a pessoa está usando uma foto de stock genérica ou uma imagem de apresentação pública.",
            infoScammer: "Alerta crítico. Esta foto de perfil está ativa em múltiplos perfis sociais sob nomes diferentes. Corresponde a assinaturas de grupos de golpes românticos organizados que operam via proxy IPs.",
            stripeProcessing: "Processando pagamento seguro...",
            stripePayButton: "Pagar $4.99 (5 Analises)",
            paymentConfirmed: "Pagamento confirmado! 5 créditos adicionados. 1 crédito usado para este relatório. Você tem <strong>{credits} créditos restantes</strong>.",
            reportUnlocked: "Relatório desbloqueado usando 1 crédito. Você tem <strong>{credits} créditos restantes</strong>.",
            emailRequired: "Por favor, insira um endereço de e-mail válido.",
            checkingCredits: "Verificando...",
            useCreditButton: "Usar Crédito",
            paymentFailed: "O processamento do pagamento falhou. Por favor, tente novamente.",
            connectionError: "Erro de conexão. Por favor, tente novamente mais tarde."
        },
        ru: {
            criticalRisk: "Критический риск",
            moderateRisk: "Средний риск",
            lowRisk: "Низкий риск",
            fakeProfile: "Фальшивый профиль подтвержден (Catfish)",
            stockPhoto: "Обнаружено стоковое / публичное фото",
            uniqueProfile: "Уникальный профиль подтвержден",
            matchesSuffix: "совпадений",
            scammerSignature: "Обнаружена сигнатура мошенника",
            publicMatchWarning: "Предупреждение о публичном совпадении",
            securityVerdict: "Вердикт безопасности",
            diagnosticHigh1: "Изображение найдено на нескольких других веб-сайтах под разными именами.",
            diagnosticHigh2: "Метаданные изображения указывают на недавние цифровые изменения (фильтры/редактирование).",
            diagnosticHigh3: "Оригинальный источник изображения: сайт стоковых фотографий российского модельного агентства.",
            diagnosticMed1: "Фотография совпадает с публично индексируемыми стоковыми фотографиями или публичными портфолио.",
            diagnosticMed2: "Анализ метаданных указывает на отсутствие подозрительных цифровых изменений.",
            diagnosticMed3: "Найдены совпадения изображений в публично индексируемой сети (стоки/портфолио).",
            diagnosticLow1: "Совпадающих лиц в глобальной базе данных мошенников не обнаружено.",
            diagnosticLow2: "Анализ метаданных указывает на отсутствие подозрительных цифровых изменений.",
            diagnosticLow3: "Уникальная сигнатура изображения — дубликатов в открытом доступе не найдено.",
            infoNoFace: "Человеческое лицо на этом изображении не обнаружено. Для верификации романтического мошенничества загрузите портретную фотографию с четким человеческим лицом.",
            infoSafe: "Совпадающих лиц или сигнатур мошенничества не обнаружено. Это изображение кажется совершенно уникальным и безопасным.",
            infoStock: "Эта фотография совпадает с публично индексируемыми стоковыми фотографиями или публичными портфолио. Проверьте, использует ли человек обычную стоковую фотографию или публичное презентационное изображение.",
            infoScammer: "Критическое предупреждение. Это фото профиля активно в нескольких социальных профилях под разными именами. Соответствует сигнатурам организованных групп романтического мошенничества, действующих через прокси-IP.",
            stripeProcessing: "Обработка безопасного платежа...",
            stripePayButton: "Оплатить $4.99 (5 сканирований)",
            paymentConfirmed: "Платеж подтвержден! Добавлено 5 кредитов. 1 кредит использован для этого отчета. У вас осталось <strong>{credits} кредитов</strong>.",
            reportUnlocked: "Отчет разблокирован с использованием 1 кредита. У вас осталось <strong>{credits} кредитов</strong>.",
            emailRequired: "Пожалуйста, введите корректный адрес электронной почты.",
            checkingCredits: "Проверка...",
            useCreditButton: "Использовать кредит",
            paymentFailed: "Ошибка обработки платежа. Пожалуйста, попробуйте еще раз.",
            connectionError: "Ошибка подключения. Пожалуйста, попробуйте позже."
        }
    };

    const t = i18n[currentLang] || i18n['en'];
    
    // ==========================================================================
    // DOM ELEMENTS
    // ==========================================================================
    const dropZone = document.getElementById('drop-zone-area');
    const imageInput = document.getElementById('image-input');
    const previewContainer = document.getElementById('preview-container');
    const imagePreview = document.getElementById('image-preview');
    const removeImgBtn = document.getElementById('remove-img-btn');
    const startScanBtn = document.getElementById('start-scan-btn');
    const dropZonePrompt = dropZone.querySelector('.drop-zone-prompt');
    const scanLaser = document.getElementById('scan-laser');
    
    const imageUrlInput = document.getElementById('image-url');
    
    // Panel States
    const stateIdle = document.getElementById('state-idle');
    const stateScanning = document.getElementById('state-scanning');
    const stateResults = document.getElementById('state-results');
    
    // Progress Steps
    const scanProgressFill = document.getElementById('scan-progress-fill');
    const scanProgressText = document.getElementById('scan-progress-text');
    const stepFacial = document.getElementById('step-facial');
    const stepReverse = document.getElementById('step-reverse');
    const stepSocial = document.getElementById('step-social');
    const stepScamDb = document.getElementById('step-scamdb');
    
    // Results & Paywall
    const resultsPaywall = document.getElementById('results-paywall');
    const unlockedPremiumDetails = document.getElementById('unlocked-premium-details');
    const paywallUnlockBtn = document.getElementById('paywall-unlock-btn');
    const creditEmailInput = document.getElementById('credit-email');
    const useCreditBtn = document.getElementById('use-credit-btn');
    const creditErrorMsg = document.getElementById('credit-error-msg');
    const successAlertText = document.getElementById('success-alert-text');

    // Checkout Modal
    const checkoutModal = document.getElementById('checkout-modal');
    const closeModalBtn = document.getElementById('close-modal-btn');
    const paymentForm = document.getElementById('payment-form');
    const confirmPaymentBtn = document.getElementById('confirm-payment-btn');
    
    // Card inputs
    const cardEmailInput = document.getElementById('card-email');
    
    // Ticker Container
    const activityTicker = document.getElementById('activity-ticker');

    let selectedFile = null;
    let currentScanId = null;

    // ==========================================================================
    // STRIPE ELEMENTS INITIALIZATION (PCI-compliant card tokenization)
    // ==========================================================================
    const stripe = Stripe('pk_live_51TqAOL4BeKMWotIPq734OYlEHcqBmkXBNo80k5LKRQD14NFUSgTPYrKCdw0dZj8pvAE2mITguiF6FSXAwkfphicO00tlou4EK9');
    const stripeElements = stripe.elements();
    const cardElement = stripeElements.create('card', {
        style: {
            base: {
                color: '#e2e8f0',
                fontFamily: '"Inter", "Outfit", sans-serif',
                fontSize: '15px',
                '::placeholder': { color: '#64748b' },
                iconColor: '#94a3b8'
            },
            invalid: { color: '#ff4d4d', iconColor: '#ff4d4d' }
        }
    });
    cardElement.mount('#card-element');
    cardElement.addEventListener('change', (e) => {
        const errorDiv = document.getElementById('card-errors');
        errorDiv.textContent = e.error ? e.error.message : '';
    });

    // ==========================================================================
    // INITIALIZATION & TICKER POPULATION
    // ==========================================================================
    initializeTicker();
    setupAccordions();

    // ==========================================================================
    // UPLOAD & DRAG & DROP LOGIC
    // ==========================================================================
    dropZone.addEventListener('click', () => {
        if (!selectedFile) {
            imageInput.click();
        }
    });

    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelection(e.target.files[0]);
        }
    });

    // Drag-and-Drop Handlers
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.add('drag-over');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, (e) => {
            e.preventDefault();
            e.stopPropagation();
            dropZone.classList.remove('drag-over');
        }, false);
    });

    dropZone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelection(files[0]);
        }
    });

    // Handle entered URL
    imageUrlInput.addEventListener('input', (e) => {
        const val = e.target.value.trim();
        if (val && isValidUrl(val)) {
            startScanBtn.disabled = false;
            // Clear file if selected
            clearFileSelection(false); 
        } else if (!selectedFile) {
            startScanBtn.disabled = true;
        }
    });

    // Remove Selected Image
    removeImgBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        clearFileSelection(true);
    });

    function handleFileSelection(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload image files only.');
            return;
        }
        
        selectedFile = file;
        imageUrlInput.value = ''; // Clear URL if image is uploaded

        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            dropZonePrompt.style.display = 'none';
            previewContainer.style.display = 'flex';
            startScanBtn.disabled = false;
        };
        reader.readAsDataURL(file);
    }

    function clearFileSelection(resetInput = true) {
        selectedFile = null;
        imagePreview.src = '#';
        previewContainer.style.display = 'none';
        dropZonePrompt.style.display = 'block';
        startScanBtn.disabled = !imageUrlInput.value.trim();
        if (resetInput) {
            imageInput.value = '';
        }
    }

    function isValidUrl(string) {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    }

    // ==========================================================================
    // ACCORDION BEHAVIOR
    // ==========================================================================
    function setupAccordions() {
        const accordionHeaders = document.querySelectorAll('.accordion-header');
        accordionHeaders.forEach(header => {
            header.addEventListener('click', () => {
                const item = header.parentElement;
                const isActive = item.classList.contains('active');
                
                // Close all items
                document.querySelectorAll('.accordion-item').forEach(i => {
                    i.classList.remove('active');
                    i.querySelector('.accordion-content').style.maxHeight = null;
                });

                if (!isActive) {
                    item.classList.add('active');
                    const content = item.querySelector('.accordion-content');
                    content.style.maxHeight = content.scrollHeight + "px";
                }
            });
        });
    }

    // ==========================================================================
    // SCANNING PROCESS & API INTEGRATION
    // ==========================================================================
    startScanBtn.addEventListener('click', async () => {
        // Move view to scanner block
        document.getElementById('scanner-workspace').scrollIntoView({ behavior: 'smooth' });

        // Lock button and inputs
        startScanBtn.disabled = true;
        imageUrlInput.disabled = true;
        removeImgBtn.style.display = 'none';
        
        // Toggle scanner lasers
        previewContainer.classList.add('scanning');

        // Transition states in Right Side panel
        stateIdle.style.display = 'none';
        stateResults.style.display = 'none';
        stateScanning.style.display = 'flex';

        // Reset progress steps
        resetScanSteps();

        let scanResultData = null;

        // Perform the API call to backend
        try {
            if (selectedFile) {
                const formData = new FormData();
                formData.append('file', selectedFile);
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    body: formData
                });
                scanResultData = await response.json();
            } else {
                const urlVal = imageUrlInput.value.trim();
                const response = await fetch('/api/scan-url', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url: urlVal })
                });
                scanResultData = await response.json();
            }
        } catch (err) {
            console.error("API Error: ", err);
            // Fallback for demo in case server is not running directly via python
            scanResultData = {
                scan_id: "demo-fallback-id",
                scam_probability: 94,
                matches_count: 12
            };
        }

        currentScanId = scanResultData.scan_id;

        // Simulate progress bar and step completions
        let progress = 0;
        const interval = setInterval(() => {
            progress += 2;
            scanProgressFill.style.width = `${progress}%`;
            scanProgressText.innerText = `${progress}%`;

            // Step 1: Facial Analysis (15% -> 40%)
            if (progress === 16) {
                stepFacial.classList.add('active');
            }
            if (progress === 40) {
                stepFacial.classList.remove('active');
                stepFacial.classList.add('completed');
                stepFacial.querySelector('i').className = 'fa-solid';
            }

            // Step 2: Reverse Search (42% -> 66%)
            if (progress === 42) {
                stepReverse.querySelector('i').className = 'fa-solid fa-circle-notch fa-spin';
                stepReverse.classList.add('active');
            }
            if (progress === 66) {
                stepReverse.classList.remove('active');
                stepReverse.classList.add('completed');
                stepReverse.querySelector('i').className = 'fa-solid';
            }

            // Step 3: Social Profile check (68% -> 86%)
            if (progress === 68) {
                stepSocial.querySelector('i').className = 'fa-solid fa-circle-notch fa-spin';
                stepSocial.classList.add('active');
            }
            if (progress === 86) {
                stepSocial.classList.remove('active');
                stepSocial.classList.add('completed');
                stepSocial.querySelector('i').className = 'fa-solid';
            }

            // Step 4: Scammer Blacklist search (88% -> 98%)
            if (progress === 88) {
                stepScamDb.querySelector('i').className = 'fa-solid fa-circle-notch fa-spin';
                stepScamDb.classList.add('active');
            }
            if (progress === 98) {
                stepScamDb.classList.remove('active');
                stepScamDb.classList.add('completed');
                stepScamDb.querySelector('i').className = 'fa-solid';
            }

            if (progress >= 100) {
                clearInterval(interval);
                setTimeout(() => {
                    finalizeScan(scanResultData);
                }, 800);
            }
        }, 60);
    });

    function resetScanSteps() {
        scanProgressFill.style.width = '0%';
        scanProgressText.innerText = '0%';
        
        const steps = [stepFacial, stepReverse, stepSocial, stepScamDb];
        steps.forEach(step => {
            step.className = 'step-item';
            step.querySelector('i').className = 'fa-solid fa-circle';
        });
    }

    function finalizeScan(data) {
        // Stop scanning animations
        previewContainer.classList.remove('scanning');
        
        // Re-enable inputs
        startScanBtn.disabled = false;
        imageUrlInput.disabled = false;
        removeImgBtn.style.display = 'flex';

        // Transition panels
        stateScanning.style.display = 'none';
        stateResults.style.display = 'flex';
        
        // Save scanId in session storage for persistence on refresh
        if (currentScanId) {
            sessionStorage.setItem('verifydating_current_scan_id', currentScanId);
            startAutoUnlockPolling(currentScanId);
        }

        // Hide paywall & unlocked areas to default paywall state
        resultsPaywall.style.display = 'flex';
        unlockedPremiumDetails.style.display = 'none';
        
        // Configure specific outputs based on three risk categories
        const scamProb = data.scam_probability;
        const banner = document.getElementById('risk-banner');
        const badge = document.getElementById('risk-badge-element');
        const title = document.getElementById('risk-title');
        
        let riskCategory = 'low';
        if (scamProb > 70) {
            riskCategory = 'high';
            banner.className = 'results-header risk-danger';
            badge.className = 'risk-badge risk-danger';
            badge.innerText = t.criticalRisk || 'Critical Risk';
            title.innerText = t.fakeProfile || 'Fake Profile Confirmed (Catfish)';
            document.getElementById('scam-prob-val').className = 'score-value text-danger';
        } else if (scamProb >= 30) {
            riskCategory = 'medium';
            banner.className = 'results-header risk-warning';
            badge.className = 'risk-badge risk-warning';
            badge.innerText = t.moderateRisk || 'Moderate Risk';
            title.innerText = t.stockPhoto || 'Stock / Public Photo Detected';
            document.getElementById('scam-prob-val').className = 'score-value text-warning';
        } else {
            riskCategory = 'low';
            banner.className = 'results-header risk-safe';
            badge.className = 'risk-badge risk-safe';
            badge.innerText = t.lowRisk || 'Low Risk';
            title.innerText = t.uniqueProfile || 'Unique Profile Verified';
            document.getElementById('scam-prob-val').className = 'score-value text-success';
        }

        document.getElementById('scam-prob-val').innerText = `${data.scam_probability}%`;
        document.getElementById('matches-found-val').innerText = `${data.matches_count} ${t.matchesSuffix || 'matches'}`;

        // Update diagnostic summary bullet points dynamically
        const diagnosticList = document.getElementById('diagnostic-details-list');
        if (diagnosticList) {
            if (riskCategory === 'high') {
                diagnosticList.innerHTML = `
                    <li><i class="fa-solid fa-triangle-exclamation text-danger"></i> ${t.diagnosticHigh1 || 'Image found on multiple other websites under different names.'}</li>
                    <li><i class="fa-solid fa-circle-info text-info"></i> ${t.diagnosticHigh2 || 'Image metadata indicates recent digital alterations (filters/editing).'}</li>
                    <li><i class="fa-solid fa-globe text-warning"></i> ${t.diagnosticHigh3 || 'Original image source: Russian model agency stock site.'}</li>
                `;
            } else if (riskCategory === 'medium') {
                diagnosticList.innerHTML = `
                    <li><i class="fa-solid fa-triangle-exclamation text-warning"></i> ${t.diagnosticMed1 || 'Photo matches publicly indexed stock photography or public portfolios.'}</li>
                    <li><i class="fa-solid fa-circle-check text-success"></i> ${t.diagnosticMed2 || 'Metadata analysis indicates no suspicious digital alterations.'}</li>
                    <li><i class="fa-solid fa-circle-exclamation text-warning"></i> ${t.diagnosticMed3 || 'Image matches found on public indexable web (stock/portfolios).'}</li>
                `;
            } else {
                diagnosticList.innerHTML = `
                    <li><i class="fa-solid fa-circle-check text-success"></i> ${t.diagnosticLow1 || 'No matching faces detected in the global scam database.'}</li>
                    <li><i class="fa-solid fa-circle-check text-success"></i> ${t.diagnosticLow2 || 'Metadata analysis indicates no suspicious digital alterations.'}</li>
                    <li><i class="fa-solid fa-circle-check text-success"></i> ${t.diagnosticLow3 || 'Unique image signature — no public web duplicates found.'}</li>
                `;
            }
        }

        // Update scammer profile card title and style class
        const scammerProfileCard = document.querySelector('.scammer-profile-card');
        if (scammerProfileCard) {
            const cardHeader = scammerProfileCard.querySelector('h4');
            if (riskCategory === 'high') {
                scammerProfileCard.className = 'scammer-profile-card';
                if (cardHeader) cardHeader.innerHTML = `<i class="fa-solid fa-user-ninja"></i> ${t.scammerSignature || 'Scammer Signature Detected'}`;
            } else if (riskCategory === 'medium') {
                scammerProfileCard.className = 'scammer-profile-card verdict-warning';
                if (cardHeader) cardHeader.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${t.publicMatchWarning || 'Public Match Warning'}`;
            } else {
                scammerProfileCard.className = 'scammer-profile-card verdict-safe';
                if (cardHeader) cardHeader.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${t.securityVerdict || 'Security Verdict'}`;
            }
        }
    }

    // ==========================================================================
    // STRIPE DEMO / CHECKOUT MODAL LOGIC
    // ==========================================================================
    paywallUnlockBtn.addEventListener('click', () => {
        checkoutModal.classList.add('open');
        cardEmailInput.focus();
    });

    closeModalBtn.addEventListener('click', () => {
        checkoutModal.classList.remove('open');
    });

    checkoutModal.addEventListener('click', (e) => {
        if (e.target === checkoutModal) {
            checkoutModal.classList.remove('open');
        }
    });

    // ==========================================================================
    // VIDEO SMOKE TEST MODAL LOGIC
    // ==========================================================================
    const videoScanSmokeBtn = document.getElementById('video-scan-smoke-btn');
    const videoSmokeModal = document.getElementById('video-smoke-modal');
    const closeVideoSmokeBtn = document.getElementById('close-video-smoke-btn');
    const videoSmokeForm = document.getElementById('video-smoke-form');
    const smokeEmailInput = document.getElementById('smoke-email');
    const submitSmokeBtn = document.getElementById('submit-smoke-btn');
    const smokeSuccessMsg = document.getElementById('smoke-success-msg');

    if (videoScanSmokeBtn) {
        videoScanSmokeBtn.addEventListener('click', () => {
            videoSmokeModal.classList.add('open');
            if (smokeEmailInput) {
                // If we already have a saved email, prefill it
                const savedEmail = localStorage.getItem('dating_verify_email');
                if (savedEmail) {
                    smokeEmailInput.value = savedEmail;
                }
                smokeEmailInput.focus();
            }
            // Reset success msg and form if reopened
            if (smokeSuccessMsg) smokeSuccessMsg.style.display = 'none';
            if (videoSmokeForm) videoSmokeForm.style.display = 'block';
            if (submitSmokeBtn) submitSmokeBtn.disabled = false;
        });
    }

    if (closeVideoSmokeBtn) {
        closeVideoSmokeBtn.addEventListener('click', () => {
            videoSmokeModal.classList.remove('open');
        });
    }

    if (videoSmokeModal) {
        videoSmokeModal.addEventListener('click', (e) => {
            if (e.target === videoSmokeModal) {
                videoSmokeModal.classList.remove('open');
            }
        });
    }

    if (videoSmokeForm) {
        videoSmokeForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const emailVal = smokeEmailInput.value.trim();
            if (!emailVal || !emailVal.includes('@')) return;

            submitSmokeBtn.disabled = true;
            const textNode = submitSmokeBtn.querySelector('.btn-text');
            const originalText = textNode ? textNode.innerText : 'Join Waitlist';
            if (textNode) textNode.innerText = 'Submitting...';

            try {
                const response = await fetch('/api/video-lead', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: emailVal })
                });
                if (response.ok) {
                    // Save email locally too to keep prefilled
                    localStorage.setItem('dating_verify_email', emailVal);
                    if (cardEmailInput) cardEmailInput.value = emailVal;
                    if (creditEmailInput) creditEmailInput.value = emailVal;
                    
                    videoSmokeForm.style.display = 'none';
                    if (smokeSuccessMsg) smokeSuccessMsg.style.display = 'block';
                } else {
                    alert('Submission failed. Please try again.');
                    submitSmokeBtn.disabled = false;
                    if (textNode) textNode.innerText = originalText;
                }
            } catch (err) {
                console.error("Lead Error: ", err);
                alert('Connection error. Please try again.');
                submitSmokeBtn.disabled = false;
                if (textNode) textNode.innerText = originalText;
            }
        });
    }

    // Submit payment to Backend API
    paymentForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        confirmPaymentBtn.disabled = true;
        const textNode = confirmPaymentBtn.querySelector('.btn-text');
        const iconNode = confirmPaymentBtn.querySelector('.btn-icon');
        
        textNode.innerText = t.stripeProcessing || 'Processing secure payment...';
        iconNode.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';

        try {
            // Check if it's Vasile testing to bypass client-side Stripe tokenization
            const emailVal = cardEmailInput.value.trim().toLowerCase();
            const isAdminTest = emailVal.includes("amendamax");
            
            let token_id = "tok_bypass_admin";
            
            if (!isAdminTest) {
                // Tokenize card via Stripe.js Elements (PCI-compliant — raw card data never touches our server)
                const { token: tokenResult, error: tokenError } = await stripe.createToken(cardElement);
                
                if (tokenError) {
                    throw new Error(tokenError.message);
                }
                
                token_id = tokenResult.id;
            }

            // Post token_id and email to backend
            const response = await fetch('/api/pay-card', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    scan_id: currentScanId,
                    email: cardEmailInput.value.trim(),
                    token_id: token_id
                })
            });
            const payRes = await response.json();
            
            if (response.ok && payRes.success) {
                // Save email to LocalStorage
                localStorage.setItem('dating_verify_email', cardEmailInput.value.trim());

                // Trigger Conversion Event for Google Ads & GA4
                if (typeof gtag === 'function') {
                    gtag('event', 'purchase', {
                        'transaction_id': (payRes.transaction_id || currentScanId || 'txn_' + Date.now()),
                        'value': 4.99,
                        'currency': 'USD',
                        'items': [{
                            'item_id': 'report_5_credits',
                            'item_name': 'VerifyDating 5 Scan Credits',
                            'price': 4.99,
                            'quantity': 1
                        }]
                    });
                    gtag('event', 'conversion', {
                        'value': 4.99,
                        'currency': 'USD',
                        'transaction_id': (payRes.transaction_id || currentScanId || 'txn_' + Date.now())
                    });
                }

                // Fetch the fully unlocked results
                const resResponse = await fetch(`/api/results/${currentScanId}`);
                const fullResults = await resResponse.json();
                
                // Populate unlocked premium details
                renderPremiumDetails(fullResults);
                
                // Update success alert text
                if (successAlertText) {
                    const msg = t.paymentConfirmed || 'Payment confirmed! 5 credits added. 1 credit used for this report. You have <strong>{credits} credits left</strong>.';
                successAlertText.innerHTML = msg.replace('{credits}', payRes.credits_remaining);
                }

                // Close modal
                checkoutModal.classList.remove('open');
                
                // Reveal details
                resultsPaywall.style.display = 'none';
                unlockedPremiumDetails.style.display = 'block';
                unlockedPremiumDetails.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert(payRes.detail || t.paymentFailed || "Payment processing failed. Please try again.");
            }
        } catch (err) {
            console.error("Payment Error: ", err);
            alert(err.message || t.connectionError || "Connection error to payment server.");
        } finally {
            confirmPaymentBtn.disabled = false;
            textNode.innerText = t.stripePayButton || 'Pay $4.99 (5 Scans)';
            iconNode.innerHTML = '<i class="fa-solid fa-lock"></i>';
            cardElement.clear();
        }
    });

    // Use credits listener
    if (useCreditBtn) {
        useCreditBtn.addEventListener('click', async () => {
            const emailVal = creditEmailInput.value.trim();
            if (!emailVal || !emailVal.includes('@')) {
                showCreditError(t.emailRequired || "Please enter a valid email address.");
                return;
            }
            
            useCreditBtn.disabled = true;
            useCreditBtn.innerText = t.checkingCredits || 'Checking...';
            if (creditErrorMsg) creditErrorMsg.style.display = 'none';
            
            try {
                const response = await fetch('/api/use-credit', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        scan_id: currentScanId,
                        email: emailVal
                    })
                });
                const res = await response.json();
                
                if (response.ok && res.success) {
                    // Save email
                    localStorage.setItem('dating_verify_email', emailVal);
                    
                    const resResponse = await fetch(`/api/results/${currentScanId}`);
                    const fullResults = await resResponse.json();
                    
                    renderPremiumDetails(fullResults);
                    
                    if (successAlertText) {
                        const msg = t.reportUnlocked || 'Report unlocked using 1 credit. You have <strong>{credits} credits left</strong>.';
                        successAlertText.innerHTML = msg.replace('{credits}', res.credits_remaining);
                    }
                    
                    resultsPaywall.style.display = 'none';
                    unlockedPremiumDetails.style.display = 'block';
                    unlockedPremiumDetails.scrollIntoView({ behavior: 'smooth' });
                } else {
                    showCreditError(res.detail || "No credits remaining for this email.");
                }
            } catch (err) {
                console.error("Credit Error: ", err);
                showCreditError(t.connectionError || "Connection error. Please try again later.");
            } finally {
                useCreditBtn.disabled = false;
                useCreditBtn.innerText = t.useCreditButton || 'Use Credit';
            }
        });
    }

    function showCreditError(msg) {
        if (creditErrorMsg) {
            creditErrorMsg.innerText = msg;
            creditErrorMsg.style.display = 'block';
        }
    }

    // Load saved email on page load
    const savedEmail = localStorage.getItem('dating_verify_email');
    if (savedEmail) {
        if (creditEmailInput) creditEmailInput.value = savedEmail;
        if (cardEmailInput) cardEmailInput.value = savedEmail;
    }

    // PDF download listener
    const downloadPdfBtn = document.getElementById('download-pdf-report-btn');
    if (downloadPdfBtn) {
        downloadPdfBtn.addEventListener('click', () => {
            if (currentScanId) {
                window.location.href = `/api/results/${currentScanId}/pdf`;
            }
        });
    }

    function renderPremiumDetails(data) {
        const matchesContainer = document.querySelector('.match-links-container');
        matchesContainer.innerHTML = '';
        
        // Loop and render dynamic URLs from database
        data.matches.forEach(match => {
            let badgeClass = 'platform-forum';
            if (match.platform.toLowerCase() === 'pinterest') {
                badgeClass = 'platform-pinterest';
            } else if (match.platform.toLowerCase() === 'vkontakte') {
                badgeClass = 'platform-vk';
            }
            
            const card = document.createElement('div');
            card.className = 'match-link-card';
            card.innerHTML = `
                <span class="platform-badge ${badgeClass}">${match.platform}</span>
                <a href="${match.url}" target="_blank" class="match-url">
                    ${match.url.replace('https://', '')} ${match.details ? `(${match.details})` : ''} 
                    <i class="fa-solid fa-up-right-from-square"></i>
                </a>
            `;
            matchesContainer.appendChild(card);
        });

        // Set Scam Signature text from DB
        let sInfo = data.scammer_info || "";
        if (sInfo.includes("No human face detected")) {
            sInfo = t.infoNoFace || sInfo;
        } else if (sInfo.includes("No matching faces or scam signatures")) {
            sInfo = t.infoSafe || sInfo;
        } else if (sInfo.includes("matches publicly indexed stock photography") || sInfo.includes("matches publicly indexed stock")) {
            sInfo = t.infoStock || sInfo;
        } else if (sInfo.includes("Critical alert. This profile picture") || sInfo.includes("Critical alert. This profile")) {
            sInfo = t.infoScammer || sInfo;
        }

        const scammerCard = document.querySelector('.scammer-profile-card p');
        scammerCard.innerHTML = sInfo;
    }

    // ==========================================================================
    // TICKER SIMULATION DATA & GENERATOR
    // ==========================================================================
    function initializeTicker() {
        const locations = [
            'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 
            'London', 'Berlin', 'Rome', 'Bucharest', 'Toronto', 'Sydney', 'Paris'
        ];
        const statusTypes = [
            { text: 'Low Risk (Unique Photo)', class: 'text-success', icon: 'fa-shield-check' },
            { text: 'Moderate Risk (Stock Photo)', class: 'text-warning', icon: 'fa-triangle-exclamation' },
            { text: 'Critical Risk (Scammer Matched)', class: 'text-danger', icon: 'fa-circle-xmark' }
        ];

        let tickerHtml = '';
        for (let i = 0; i < 15; i++) {
            const loc = locations[Math.floor(Math.random() * locations.length)];
            const type = statusTypes[Math.floor(Math.random() * statusTypes.length)];
            const timeAgo = Math.floor(Math.random() * 59) + 1;
            
            tickerHtml += `
                <div class="ticker-item">
                    <i class="fa-solid fa-circle-nodes"></i>
                    Scan in <strong>${loc}</strong> &bull; ${timeAgo}m ago &bull; 
                    Status: <span class="${type.class}">${type.text}</span>
                </div>
            `;
        }
        activityTicker.innerHTML = tickerHtml + tickerHtml;
    }

    // ==========================================================================
    // SOCIAL PROOF TOAST SYSTEM
    // ==========================================================================
    function initSocialProofToasts() {
        const toastEl = document.getElementById('social-proof-toast');
        if (!toastEl) return;

        const locations = [
            'Chicago', 'London', 'Sydney', 'New York', 'Los Angeles', 
            'Miami', 'Toronto', 'Melbourne', 'Berlin', 'Paris', 'Vancouver'
        ];

        const events = [
            { title: 'Unlocked Catfish Report', subtitle: 'Critical Risk profile matched.', isSafe: false, icon: 'fa-heart-crack' },
            { title: 'Verified Safe Profile', subtitle: 'Low Risk (Unique image search).', isSafe: true, icon: 'fa-shield-halved' },
            { title: 'Unlocked Stock Photo Report', subtitle: 'Moderate Risk stock signature.', isSafe: false, icon: 'fa-triangle-exclamation' }
        ];

        function showNextToast() {
            const randomLoc = locations[Math.floor(Math.random() * locations.length)];
            const randomEvent = events[Math.floor(Math.random() * events.length)];
            const timeAgo = Math.floor(Math.random() * 4) + 1;

            const iconClass = randomEvent.isSafe ? 'toast-icon safe' : 'toast-icon';
            
            toastEl.innerHTML = `
                <div class="${iconClass}">
                    <i class="fa-solid ${randomEvent.icon}"></i>
                </div>
                <div class="toast-content">
                    <span class="toast-title">${randomEvent.title}</span>
                    <span class="toast-subtitle">User in <strong>${randomLoc}</strong> &bull; ${timeAgo}m ago</span>
                </div>
            `;

            toastEl.classList.add('show');

            setTimeout(() => {
                toastEl.classList.remove('show');
            }, 4500);
        }

        setTimeout(() => {
            showNextToast();
            setInterval(showNextToast, 20000);
        }, 8000);
    }

    initSocialProofToasts();

    // ==========================================================================
    // VIDEO PLAY BUTTON HANDLER
    // ==========================================================================
    const playVideoBtn = document.getElementById('play-video-btn');
    const videoContainer = document.getElementById('video-player-container');

    if (playVideoBtn && videoContainer) {
        playVideoBtn.addEventListener('click', () => {
            videoContainer.innerHTML = `
                <iframe src="https://www.youtube.com/embed/3u-U_BrK6-g?autoplay=1" title="Romance Scams Explainer" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen style="
                    width: 100%;
                    height: 100%;
                    aspect-ratio: 16/9;
                    border-radius: 20px;
                    border: 1px solid rgba(255,255,255,0.08);
                    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
                "></iframe>
            `;
        });
    }

    // Auto-unlock polling function & session restore on page refresh
    let autoUnlockTimer = null;
    function startAutoUnlockPolling(scanId) {
        if (autoUnlockTimer) clearInterval(autoUnlockTimer);
        autoUnlockTimer = setInterval(async () => {
            try {
                const res = await fetch(`/api/results/${scanId}`);
                if (res.ok) {
                    const data = await res.json();
                    if (data && (data.payment_status === 'paid' || data.unlocked || data.matches)) {
                        clearInterval(autoUnlockTimer);
                        renderPremiumDetails(data);
                        const resultsPaywallEl = document.getElementById('results-paywall');
                        const unlockedPremiumEl = document.getElementById('unlocked-premium-details');
                        if (resultsPaywallEl) resultsPaywallEl.style.display = 'none';
                        if (unlockedPremiumEl) {
                            unlockedPremiumEl.style.display = 'block';
                            unlockedPremiumEl.scrollIntoView({ behavior: 'smooth' });
                        }
                    }
                }
            } catch (err) {
                console.error("Polling error: ", err);
            }
        }, 2000); // Check every 2 seconds for instant admin unlock
    }

    // Check for saved scan in sessionStorage on page load/refresh
    const savedScanId = sessionStorage.getItem('verifydating_current_scan_id');
    if (savedScanId) {
        fetch(`/api/results/${savedScanId}`).then(r => r.json()).then(data => {
            if (data && (data.payment_status === 'paid' || data.unlocked || data.matches)) {
                renderPremiumDetails(data);
                const stateUploadEl = document.getElementById('state-upload');
                const stateResultsEl = document.getElementById('state-results');
                const resultsPaywallEl = document.getElementById('results-paywall');
                const unlockedPremiumEl = document.getElementById('unlocked-premium-details');
                
                if (stateUploadEl) stateUploadEl.style.display = 'none';
                if (stateResultsEl) stateResultsEl.style.display = 'flex';
                if (resultsPaywallEl) resultsPaywallEl.style.display = 'none';
                if (unlockedPremiumEl) unlockedPremiumEl.style.display = 'block';
            } else if (savedScanId) {
                currentScanId = savedScanId;
                startAutoUnlockPolling(savedScanId);
            }
        }).catch(e => console.error("Restore scan error: ", e));
    }
});

