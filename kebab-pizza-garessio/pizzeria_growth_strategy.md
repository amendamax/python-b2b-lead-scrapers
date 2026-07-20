# Strategie de Dezvoltare și Negociere: Horus Pizza & Kebab
*Ghid complet pentru Vasile: Roadmap tehnic, marketing și modele de preț*

Acest document sintetizează toate ideile, funcționalitățile și strategiile de business discutate pentru proiectul **Horus Pizza & Kebab** (locațiile Garessio și Ceva). Îl poți folosi ca suport de curs pentru prezentarea de la întâlnire și pentru negocierile ulterioare.

---

## 1. Status Prototip și Realizări Curente (Garessio)
Avem pregătit un site-prototip premium, optimizat complet pentru mobil, disponibil în două variante:
* **Varianta Standard (`index.html`)**: Design curat de tip street-food, fundal întunecat, cu poze mari doar pe produsele cheie.
* **Varianta Parallax Transparentă (`index_bg.html`)**: Un efect vizual spectaculos cu fundalul cuptorului pe lemne fixat pe ecran (`background-attachment: fixed`), peste care „plutesc” cardurile translucide (glassmorphism) când se face scroll.

### Detalii de finețe deja implementate:
* **Grupare corectă conform flyer-ului**: Meniul a fost structurat astfel încât Tab-ul de *Pizze Bianche* să înceapă exact de la *Biancaneve* în jos. Pizze-le cu sos de roșii de dinainte au fost mutate corect la *Classiche*.
* **Poze fidele originalului**: 
  * *Pizza Diavola*: Blat rustic pe vatră, mozzarella, sos de roșii și felii plate de salam picant (fără ierburi verzi, cu ardeiul iute complet vizibil pe tocător).
  * *Pizza Capricciosa*: Blat pe vatră, măsline negre, ciuperci și fâșii de ardei gras roșu și galben (exact ca în poza originală trimisă din cutie).
  * *Panino Kebab*: Înlocuită poza veche cu una în unghi de profil (pentru volum și adâncime), așezat pe tocător de lemn (fără mâini).
  * *Piatto Kebab* și *Menu Hamburger*: Integrat imagini realiste și de impact.
* **Etichete picante discrete**: Eticheta roșie a fost înlocuită cu un badge gri-închis semitransparent cu bordură fină (`🌶️`), integrat perfect în stilul site-ului.
* **Căutare inteligentă**: Bara de căutare scanează acum și textul din etichete (ex: căutarea cuvintelor „picant”, „picante”, „iute” sau „🌶️” va afișa instant toate preparatele iuți; căutarea „consigliata” va afișa Pizza Kebab și Piatto Kebab).

---

## 2. Faza 1: Perioada de Test Gratuit (Luna 1)
Pentru a le câștiga încrederea totală (strategie de risc zero), le oferi prima lună gratuit în următoarele condiții:

### Instrumentul de Dovadă (WhatsApp Attribution Prefix)
Fiecare comandă trimisă prin site generează automat un mesaj care începe cu:
`„Ciao! Vorrei ordinare tramite il vostro sito web...”`
Astfel, ei vor vedea direct pe telefoanele lor la fiecare comandă că vânzarea respectivă ți se datorează ție.

### Servicii de valoare adăugată incluse în test:
* **Revendicarea profilului de Google Maps**: Te ocupi de verificarea și configurarea paginilor Google Business Profile pentru ambele locații (Garessio și Ceva).
* **Butonul „Site Web” pe Google Maps**: Adaugi link-ul site-ului tău direct pe Maps (sursa principală de clienți în Italia).
* **QR Code Meniu**: Un cod QR (generat deja în `assets/qr_menu.png`) pentru vitrină/geam, care deschide direct meniul pe telefonul clienților.

---

## 3. Faza 2: Pachetul de Extindere și Funcționalități Premium (Upsell)
După perioada de test de o lună, când le demonstrezi că site-ul aduce bani, le propui extinderea proiectului cu funcționalități premium:

### A. Portalul Franciză (Garessio + Ceva)
* O singură adresă web (ex: `horuspizzerie.it`) cu o pagină de start unde clientul alege orașul: **Garessio** sau **Ceva**.
* Meniul din Ceva va fi adaptat să includă și coloana de **Pizza MAXI** (care nu se face la Garessio), plus numerele de telefon și contul de WhatsApp corespunzător locației din Ceva.

### B. Coșul de Cumpărături Interactiv (Shopping Cart)
* Clienții pot adăuga mai multe produse în coș (ex: 2 Kebab-uri, 1 Fanta, 1 Tiramisu).
* Pot selecta băutura sau sosurile preferate dintr-o listă.
* Comanda ajunge pe WhatsApp ca un singur mesaj compact, cu prețul total calculat automat la cent.

### C. Modalul de Personalizare (Ingrediente, Alergii & Note)
* **Foarte important pentru eliminarea greșelilor din bucătărie:**
* Când dau click pe produs, clienții au opțiuni de configurare precise:
  * *Rimuovi ingredienti (Senza...)*: Debifează ceapa sau sosul picant, iar în mesaj va scrie clar `❌ SENZA cipolla`.
  * *Aggiungi extra*: Bifează ingrediente suplimentare plătite (ex: `➕ Aggiungi mozzarella (+€1.00)`).
  * *Note / Alergii*: Casetă text unde scriu de exemplu „Alergie la gluten” sau „Carne bine prăjită”.

### D. Sistemul QR la Masă (Comenzi fără chelner)
* Fiecare masă fizică din pizzerie va avea un cod QR unic, de exemplu: `site.com/menu/?tavolo=5`.
* Când clientul de la masa 5 scanează codul, site-ul știe instant unde se află. Comanda trimisă pe WhatsApp va scrie automat: `Vorrei ordinare al Tavolo 5: ...`. Chelnerul doar aduce mâncarea la masă, fără să mai piardă timp preluând comanda.

### E. Codul QR de Recenzii Google (La Casa de Marcat)
* Un pliant dedicat (generat în `assets/qr_review_flyer.png`) așezat lângă casa de marcat, cu textul *„Lasciaci una recensione su Google / Aiutaci a crescere! ⭐⭐⭐⭐⭐”*.
* Clienții scanează QR-ul la plecare și li se deschide direct căsuța de recenzii Google Maps a pizzeriei pentru a lăsa 5 stele pe loc.

---

## 4. Modele de Preț Propuse (Post-Trial)

La finalul lunii de probă, le propui una dintre următoarele variante de colaborare la pachet (pentru ambele locații Ceva + Garessio):

### Modelul 1: Comision la Comandă (Pay-per-Order) - *Cel mai profitabil*
* **Tarif**: **€1 pentru fiecare comandă** înregistrată prin site pe WhatsApp.
* **Cum securizezi plata**:
  * *Prepay*: Cumpără pachete de comenzi în avans (ex: reîncarcă cu €100 pentru 100 de comenzi; când se consumă, butoanele se dezactivează până la următoarea reîncărcare).
  * *Abonament bazat pe volum*: Dacă testul arată ~200 de comenzi/lună, din luna a doua transformați comisionul într-o sumă fixă convenabilă (ex: **€150/lună fix** pentru ambele locații).

### Modelul 2: Pachetul Hibrid (Plată unică + Abonament mic)
* **Plată unică de pornire**: **€150 - €180** (acoperă achiziția domeniului `.it` pe un an, configurările DNS, crearea paginii de start tip portal și designul celor două coduri QR).
* **Abonament lunar fix**: **€25 - €30 / lună** (pachet pentru ambele locații - acoperă găzduirea și modificările rapide în meniu când se schimbă prețurile).
