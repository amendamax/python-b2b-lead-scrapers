# Strategia di Crescita e Negoziazione: Horus Pizza & Kebab
*Guida completa per Vasile: Roadmap tecnica, marketing e modelli di prezzo*

Questo documento sintetizza tutte le idee, le funzionalità e le strategie di business discusse per il progetto **Horus Pizza & Kebab** (sedi di Garessio e Ceva). Puoi usarlo come supporto durante l'incontro di stasera e per le trattative successive.

---

## 1. Stato del Prototipo e Risultati Attuali (Garessio)
Abbiamo preparato un sito web prototipo di fascia premium, completamente ottimizzato per i dispositivi mobili, disponibile in due varianti:
* **Variante Standard (`index.html`)**: Design pulito in stile street-food, sfondo scuro, con foto grandi solo sui prodotti chiave.
* **Variante Parallasse Trasparente (`index_bg.html`)**: Un effetto visivo spettacolare con l'immagine di sfondo del forno a legna fissa sullo schermo (`background-attachment: fixed`), su cui "fluttuano" le schede dei prodotti in stile vetro sfocato (glassmorphism) durante lo scorrimento.

### Dettagli di pregio già implementati:
* **Suddivisione corretta secondo il volantino**: Il menu è stato strutturato in modo che la sezione *Pizze Bianche* inizi esattamente da *Biancaneve* in poi. Le pizze con salsa di pomodoro precedenti sono state spostate correttamente nella categoria *Classiche*.
* **Foto fedeli all'originale**: 
  * *Pizza Diavola*: Impasto rustico cotto a legna, mozzarella, salsa di pomodoro e fette piatte di salame piccante (senza foglie di basilico, con il peperoncino rosso completamente visibile sul tagliere).
  * *Pizza Capricciosa*: Impasto cotto a legna, olive nere, funghi e strisce di peperoni rossi e gialli (esattamente come nella foto originale inviata nella scatola da asporto).
  * *Panino Kebab*: Sostituita la vecchia immagine con una presa da un'angolazione di profilo (per dare volume e profondità), posizionata su un tagliere di legno (senza mani).
  * *Piatto Kebab* e *Menu Hamburger*: Integrate immagini realistiche e di forte impatto visivo.
* **Badge piccante discreto**: Il badge rosso è stato sostituito con una pillola grigio-scuro semitrasparente con un bordo sottile (`🌶️`), perfettamente integrata nello stile grafico del sito.
* **Ricerca intelligente**: La barra di ricerca ora analizza anche il testo dei badge (es. cercando "piccante", "iute", "spicy" o "🌶️" verranno mostrati all'istante tutti i piatti piccanti; cercando "consigliato" o "consigliata" appariranno il Pizza Kebab e il Piatto Kebab).

---

## 2. Fase 1: Periodo di Prova Gratuito (Mese 1)
Per conquistare la loro totale fiducia (strategia a rischio zero per il cliente), offri il primo mese gratuito alle seguenti condizioni:

### Lo Strumento di Prova (WhatsApp Attribution Prefix)
Ogni ordine inviato tramite il sito genera automaticamente un messaggio su WhatsApp che inizia con:
`"Ciao! Vorrei ordinare tramite il vostro sito web..."`
In questo modo, vedranno direttamente sui loro telefoni a ogni singolo ordine che la vendita è arrivata grazie al sito creato da te.

### Servizi a valore aggiunto inclusi nella prova:
* **Rivendicazione del profilo Google Maps**: Ti occupi della verifica e della configurazione delle schede Google Business Profile per entrambe le sedi (Garessio e Ceva).
* **Pulsante "Sito Web" su Google Maps**: Colleghi il link del tuo sito direttamente su Google Maps (la fonte principale di clienti locali in Italia).
* **QR Code Menu**: Un codice QR (già generato in `assets/qr_menu.png`) per la vetrina o il bancone, che apre direttamente il menu sul telefono dei clienti.

---

## 3. Fase 2: Pacchetto di Espansione e Funzionalità Premium (Upsell)
Dopo il periodo di prova di un mese, quando avrai dimostrato con i fatti che il sito porta clienti, puoi proporre l'espansione del progetto con funzionalità premium:

### A. Il Portale Franchising (Garessio + Ceva)
* Un unico indirizzo web (es. `horuspizzerie.it`) con una pagina iniziale dove il cliente sceglie la città: **Garessio** o **Ceva**.
* Il menu di Ceva sarà adattato per includere anche la colonna delle **Pizze MAXI** (che non vengono fatte a Garessio), insieme ai numeri di telefono e al contatto WhatsApp corrispondente alla sede di Ceva.

### B. Carrello della Spesa Interattivo (Shopping Cart)
* I clienti possono aggiungere più prodotti al carrello (es. 2 Kebab, 1 Fanta, 1 Tiramisù).
* Possono selezionare le bevande o le salse preferite da un menu a tendina.
* L'ordine arriva su WhatsApp come un unico messaggio compatto, con il prezzo totale calcolato automaticamente al centesimo.

### C. Finestra di Personalizzazione (Ingredienti, Allergie e Note)
* **Fondamentale per eliminare gli errori in cucina:**
* Cliccando sul prodotto, i clienti possono configurarlo con precisione:
  * *Rimuovi ingredienti (Senza...)*: Deselezionano la cipolla o la salsa piccante, e nel messaggio apparirà chiaramente `❌ SENZA cipolla`.
  * *Aggiungi extra*: Selezionano ingredienti aggiuntivi a pagamento (es. `➕ Aggiungi mozzarella (+€1.00)`).
  * *Note / Allergie*: Un campo di testo libero dove scrivere ad esempio "Allergia al glutine" o "Carne ben cotta".

### D. Sistema QR al Tavolo (Ordini senza cameriere)
* Ogni tavolo fisico della pizzeria avrà un codice QR unico, ad esempio: `site.com/menu/?tavolo=5`.
* Quando il cliente al tavolo 5 scansiona il codice, il sito sa già dove si trova. L'ordine inviato su WhatsApp riporterà automaticamente: `Vorrei ordinare al Tavolo 5: ...`. Il cameriere dovrà solo portare i piatti al tavolo, senza perdere tempo a prendere l'ordine.

### E. Codice QR per Recensioni Google (Alla Cassa)
* Un cartello dedicato (generato in `assets/qr_review_flyer.png`) posizionato vicino alla cassa, con il testo *„Lasciaci una recensione su Google / Aiutaci a crescere! ⭐⭐⭐⭐⭐”*.
* I clienti scansionano il QR al momento del pagamento e aprono all'istante la schermata per lasciare una recensione a 5 stelle su Google Maps.

---

## 4. Modelli di Prezzo Proposti (Post-Trial)

Alla fine del mese di prova, proponi una delle seguenti opzioni di collaborazione a pacchetto (per entrambe le sedi Ceva + Garessio):

### Modello 1: Commissione sull'Ordine (Pay-per-Order) - *Il più redditizio*
* **Tariffa**: **€1 per ogni ordine** inviato tramite il sito su WhatsApp.
* **Come garantire il pagamento**:
  * *Prepagato*: Acquistano pacchetti di ordini in anticipo (es. ricaricano €100 per 100 ordini; al termine, i pulsanti del sito si disattivano fino alla ricarica successiva).
  * *Abbonamento basato sul volume*: Se il test rileva circa 200 ordini al mese, dal secondo mese trasformate la commissione in una quota fissa conveniente (es. **€150/mese fisso** per entrambe le sedi).

### Modello 2: Pacchetto Ibrido (Quota una tantum + Abbonamento mensile)
* **Configurazione iniziale (una tantum)**: **€150 - €180** (copre l'acquisto del dominio `.it` per un anno, la configurazione dei DNS, la creazione del portale iniziale e il design dei due codici QR).
* **Abbonamento mensile fisso**: **€25 - €30 / mese** (pacchetto per entrambe le sedi - copre l'hosting e gli aggiornamenti rapidi del menu in caso di cambio prezzi).
