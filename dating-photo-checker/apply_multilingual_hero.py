import os

# VerifyDating Translations
dating_translations = {
    'ro': {
        'badge': '<i class="fa-solid fa-shield-cat"></i> Motor AI de Recunoaștere Facială Biometrică',
        'title': 'Căutare Inversă & Biometrică Facială pentru Siguranța pe Dating',
        'sub': 'Detectează instant profiluri catfished, escrocherii sentimentale, poze furate pe rețelele sociale și identități false folosind recunoașterea facială AI în baze de date publice.',
        's1_num': '85.4M+', 's1_txt': 'Profiluri Sociale & Web Indexate',
        's2_num': '99.2%', 's2_txt': 'Acuratețe Potrivire Biometrică',
        's3_num': '30s', 's3_txt': 'Audit Confidențial Instant',
        't_title': '🔥 VERIFICĂRI LIVE ÎN TIMP REAL:',
        't1': 'Poză Tinder — Risc Catfish 94% ⚠️',
        't2': 'Profil Bumble — Potrivire Găsită 88% ⚠️',
        't3': 'Audit Instagram — 0% Curat ✓',
        't4': 'Profil Hinge — Poză Furată 97% ⚠️',
    },
    'it': {
        'badge': '<i class="fa-solid fa-shield-cat"></i> Motore AI di Riconoscimento Facciale Biometrico',
        'title': 'Ricerca Immagine Inversa & Biometrica Facciale per la Sicurezza nei Dating',
        'sub': 'Rileva all\'istante profili catfish, truffe romantiche, foto rubate sui social e false identità utilizzando il riconoscimento facciale AI.',
        's1_num': '85.4M+', 's1_txt': 'Profili Social & Web Indicizzati',
        's2_num': '99.2%', 's2_txt': 'Accuratezza Corrispondenza Biometrica',
        's3_num': '30s', 's3_txt': 'Audit Confidenziale Istantaneo',
        't_title': '🔥 VERIFICHE LIVE IN TEMPO REALE:',
        't1': 'Foto Tinder — Rischio Catfish 94% ⚠️',
        't2': 'Profilo Bumble — Corrispondenza 88% ⚠️',
        't3': 'Audit Instagram — 0% Pulito ✓',
        't4': 'Profilo Hinge — Foto Rubata 97% ⚠️',
    },
    'de': {
        'badge': '<i class="fa-solid fa-shield-cat"></i> KI-Biometrische Gesichtserkennungs-Engine',
        'title': 'Umgekehrte Bild- & Biometrische Gesichtssuche für Dating-Sicherheit',
        'sub': 'Erkennen Sie sofort Fake-Profile, Romance Scams, gestohlene Social-Media-Fotos und falsche Identitäten mit KI-Gesichtserkennung.',
        's1_num': '85.4M+', 's1_txt': 'Indizierte Social- & Web-Profile',
        's2_num': '99.2%', 's2_txt': 'Biometrische Treffergenauigkeit',
        's3_num': '30s', 's3_txt': 'Sofortiger Vertraulicher Audit',
        't_title': '🔥 LIVE-SICHERHEITSAUDITS:',
        't1': 'Tinder-Foto — 94% Catfish-Risiko ⚠️',
        't2': 'Bumble-Profil — 88% Treffer ⚠️',
        't3': 'Instagram-Audit — 0% Sauber ✓',
        't4': 'Hinge-Profil — 97% Gestohlenes Foto ⚠️',
    },
    'es': {
        'badge': '<i class="fa-solid fa-shield-cat"></i> Motor IA de Reconocimiento Facial Biométrico',
        'title': 'Búsqueda Inversa de Imágenes y Biometría Facial para Citas Seguras',
        'sub': 'Detecte al instante perfiles falsos, estafas sentimentales, fotos robadas en redes sociales e identidades falsas con reconocimiento facial IA.',
        's1_num': '85.4M+', 's1_txt': 'Perfiles Indexados en Web y Redes',
        's2_num': '99.2%', 's2_txt': 'Precisión Biométrica Facial',
        's3_num': '30s', 's3_txt': 'Auditoría Confidencial Al Instante',
        't_title': '🔥 AUDITORÍAS EN TIEMPO REAL:',
        't1': 'Foto Tinder — 94% Riesgo Catfish ⚠️',
        't2': 'Perfil Bumble — 88% Coincidencia ⚠️',
        't3': 'Auditoría Instagram — 0% Limpio ✓',
        't4': 'Perfil Hinge — 97% Foto Robada ⚠️',
    },
    'fr': {
        'badge': '<i class="fa-solid fa-shield-cat"></i> Moteur IA de Reconnaissance Faciale Biométrique',
        'title': 'Recherche d\'Image Inversée & Biométrie Faciale pour Rencontres Sécurisées',
        'sub': 'Détectez instantanément les faux profils catfish, les arnaques sentimentales, les photos volées et les fausses identités grâce à l\'IA.',
        's1_num': '85.4M+', 's1_txt': 'Profils Web & Sociaux Indexés',
        's2_num': '99.2%', 's2_txt': 'Précision Biométrique Faciale',
        's3_num': '30s', 's3_txt': 'Audit Confidentiel Instantané',
        't_title': '🔥 AUDITS EN DIRECT EN TEMPS RÉEL:',
        't1': 'Photo Tinder — 94% Risque Catfish ⚠️',
        't2': 'Profil Bumble — 88% Correspondance ⚠️',
        't3': 'Audit Instagram — 0% Propre ✓',
        't4': 'Profil Hinge — 97% Photo Volée ⚠️',
    },
    'pt': {
        'badge': '<i class="fa-solid fa-shield-cat"></i> Motor IA de Reconhecimento Facial Biométrico',
        'title': 'Pesquisa Inversa de Imagem e Biometria Facial para Encontros Seguros',
        'sub': 'Detete instantaneamente perfis falsos, burlas amorosas, fotos roubadas nas redes sociais e identidades falsas com reconhecimento facial IA.',
        's1_num': '85.4M+', 's1_txt': 'Perfis Indexados em Redes e Web',
        's2_num': '99.2%', 's2_txt': 'Precisão Biométrica Facial',
        's3_num': '30s', 's3_txt': 'Auditoria Confidencial Instantânea',
        't_title': '🔥 AUDITORIAS EM TEMPO REAL:',
        't1': 'Foto Tinder — 94% Risco Catfish ⚠️',
        't2': 'Perfil Bumble — 88% Correspondência ⚠️',
        't3': 'Auditoria Instagram — 0% Limpo ✓',
        't4': 'Perfil Hinge — 97% Foto Roubada ⚠️',
    },
    'ru': {
        'badge': '<i class="fa-solid fa-shield-cat"></i> ИИ Алгоритм Биометрического Распознавания Лиц',
        'title': 'Обратный Поиск Изображений и Биометрический Поиск Лиц для Безопасности',
        'sub': 'Мгновенное обнаружение фейковых профилей, романтических мошенников, украденных фото из соцсетей и фальшивых личностей с помощью ИИ.',
        's1_num': '85.4M+', 's1_txt': 'Индексированных Профилей в Сети',
        's2_num': '99.2%', 's2_txt': 'Точность Биометрического Поиска',
        's3_num': '30s', 's3_txt': 'Мгновенный Конфиденциальный Аудит',
        't_title': '🔥 ПРОВЕРКИ В РЕАЛЬНОМ ВРЕМЕНИ:',
        't1': 'Фото Tinder — 94% Риск Фейка ⚠️',
        't2': 'Профиль Bumble — 88% Совпадение ⚠️',
        't3': 'Аудит Instagram — 0% Чисто ✓',
        't4': 'Профиль Hinge — 97% Украденное Фото ⚠️',
    }
}

for lang, data in dating_translations.items():
    file_path = f"{lang}/index.html"
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()
        
        # Replace hero section
        hero_replacement = f"""        <!-- Hero Section -->
        <section class="hero-section">
            <div class="hero-badge-row">
                <span class="hero-tag">{data['badge']}</span>
                <span class="hero-tag hero-tag-warning"><i class="fa-solid fa-triangle-exclamation"></i> 1/7</span>
            </div>
            <h1 id="main-title">{data['title']}</h1>
            <p class="hero-subtitle">{data['sub']}</p>

            <!-- Impact Statistics -->
            <div class="impact-stats-row">
                <div class="impact-stat">
                    <span class="impact-num">{data['s1_num']}</span>
                    <span class="impact-label">{data['s1_txt']}</span>
                </div>
                <div class="impact-divider"></div>
                <div class="impact-stat">
                    <span class="impact-num">{data['s2_num']}</span>
                    <span class="impact-label">{data['s2_txt']}</span>
                </div>
                <div class="impact-divider"></div>
                <div class="impact-stat">
                    <span class="impact-num">{data['s3_num']}</span>
                    <span class="impact-label">{data['s3_txt']}</span>
                </div>
            </div>

            <!-- Live Safety Scans Ticker -->
            <div class="recent-scans-ticker">
                <span class="ticker-title">{data['t_title']}</span>
                <div class="ticker-tags">
                    <span class="scan-tag risk-high"><i class="fa-solid fa-user-ninja"></i> {data['t1']}</span>
                    <span class="scan-tag risk-high"><i class="fa-solid fa-user-xmark"></i> {data['t2']}</span>
                    <span class="scan-tag risk-low"><i class="fa-solid fa-user-check"></i> {data['t3']}</span>
                    <span class="scan-tag risk-high"><i class="fa-solid fa-masks-theater"></i> {data['t4']}</span>
                </div>
            </div>

            <!-- Trust Badges -->
            <div class="trust-badges-row">
                <div class="trust-badge">
                    <i class="fa-solid fa-shield-halved"></i>
                    <span>256-bit SSL</span>
                </div>
                <div class="trust-badge">
                    <i class="fa-solid fa-eye-slash"></i>
                    <span>24h Delete</span>
                </div>
                <div class="trust-badge">
                    <i class="fa-solid fa-user-shield"></i>
                    <span>100% Anonymous</span>
                </div>
                <div class="trust-badge">
                    <i class="fa-solid fa-rotate-left"></i>
                    <span>Money-Back Guarantee</span>
                </div>
            </div>
        </section>"""
        
        # Replace hero section in HTML
        if '<section class="hero-section">' in html:
            start = html.find('<section class="hero-section">')
            end = html.find('</section>', start) + len('</section>')
            new_html = html[:start] + hero_replacement + html[end:]
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_html)
            print(f"Updated multilingual hero for {file_path}")
