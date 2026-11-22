# Atlante: analisi d'uso del prototipo

22 novembre 2026. Prototipo verificato in tutte le modalità (Ricerca, Percorso, Affidabilità, Tavolo, Guida), con tastiera, su telefono (390 px), con rete lenta simulata, in tema chiaro e scuro, misurando quello che si poteva misurare. Scopo: togliere gli ostacoli all'uso senza semplificare lo strumento.

## Già corretto durante l'analisi

| | difetto | effetto |
| --- | --- | --- |
| 1 | Date ColBase con l'anno finale abbreviato («1522～66») | 45 schede prendevano l'intervallo dell'epoca intera (Ming 1368–1644, Edo 1603–1868, Qing 1636–1912); una del periodo Tenmei (天明, 1781–89) risultava Ming. Ora 1522–1566 ecc.; guardia nei test |
| 2 | In Affidabilità restava premuto anche «Percorso» | due modi sembravano attivi insieme |
| 3 | Una vista condivisa aperta nella stessa scheda non veniva applicata | il link portava all'atlante ma non alla vista |

## Priorità 1: ostacola o confonde (da sistemare prima dei test)

**Stato al 22 novembre, sera: tutti e cinque risolti e pubblicati.** Caricamento con messaggio; righe del pannello raggiungibili da tastiera e attivabili con Invio, due collegamenti «salta» in testa alla pagina (dal titolo ai risultati in due tasti), anno annunciato dalla barra del tempo; ricerca che conta in tutto il tempo e nella finestra, porta agli anni con più risultati, si toglie con un clic e ora cerca anche nei nomi dei luoghi («iznik»: da 11 a 107 pezzi); nomi sulla mappa senza sovrapposizioni; Tavolo chiuso uscendo dalla Ricerca. Corretto anche «Il 820» → «L'820».

1. **Caricamento senza segnale.** Finché i dati non arrivano la pagina è vuota e l'etichetta sulla mappa dice «0 pezzi attivi · confini del null». Online i dati sono leggeri (circa 0,4 MB compressi), ma su una connessione lenta passano vari secondi senza che si capisca cosa succede. → indicatore di caricamento e testo provvisorio.
2. **Tastiera.** Le righe del pannello di destra (luoghi, pezzi, fenomeni, relazioni) non sono raggiungibili da tastiera: chi non usa il mouse non può aprire nessuna scheda. Il globo non è navigabile da tastiera, e il pannello è l'unica alternativa. La barra del tempo si muove con le frecce ma non annuncia l'anno ai lettori di schermo. → righe come pulsanti veri, valore della barra annunciato.
3. **Ricerca.** Cerca solo dentro la finestra di tempo scelta, senza dirlo: «iznik» nel 1640 trova 5 pezzi, e chi cerca non sa che ce ne sono altri in altri anni. Se non trova nulla dice «Nessun pezzo in questa finestra», senza ricordare che c'è un filtro attivo né come toglierlo. → «N trovati in tutto, X in questa finestra», distribuzione dei risultati sulla barra del tempo, comando per togliere il filtro.
4. **Etichette sovrapposte sulla mappa.** Nomi vicini si sovrappongono e diventano illeggibili (Delft su Paesi Bassi, Cina su Jingdezhen). I fenomeni artistici evitano già le sovrapposizioni; i luoghi no. → stessa regola per tutti i nomi.
5. **Il Tavolo resta aperto cambiando modo.** Passando a Percorso o Affidabilità copre metà schermo, e in quei modi il pulsante Tavolo è nascosto. → chiuderlo al cambio di modo, o lasciare il pulsante.

## Priorità 2: rallenta la comprensione

6. **Gergo nelle schede.** Compaiono codici e formule interne: «Q34405», «etichetta, max sitelinks (luoghi.rq)», «(epoca (Wikidata)) (intervallo 1368–1644)», «documentato» senza spiegazione; nei comandi «corsie», «finestra ±», «PeriodO: chi definisce». → riformulare dal punto di vista di chi legge («Come abbiamo collocato il luogo: …») e un piccolo glossario a comparsa sui termini propri dell'atlante.
7. **Nessuna legenda sulla mappa.** I segni (cerchio pieno, anello, tratteggio, rombo, triangolo, quadrato, puntini) sono spiegati solo nei livelli e nella guida. → legenda compatta che mostra solo i segni dei livelli accesi.
8. **Lo stato dei filtri non è riassunto.** Ricerca attiva, tipi esclusi, livelli spenti: per capire cosa si sta guardando bisogna ripercorrere la colonna di sinistra. Manca un «ripristina la vista iniziale». → riepilogo dei filtri attivi, ciascuno rimovibile, e un comando di ripristino.
9. **Telefono.** La pagina è lunga circa 5.400 px: mappa, tempo, pannello, e solo in fondo i livelli, a 4.100 px. Con il tocco non ci sono suggerimenti al passaggio (il tocco apre direttamente la scheda: accettabile). Manca il pizzico per ingrandire. → livelli in un pannello richiamabile da un pulsante, pizzico sul globo.
10. **L'indirizzo non segue la vista.** Il tasto Indietro del browser non torna alla vista precedente, e per condividere una vista bisogna passare da «Commenta». → comando «Copia il collegamento a questa vista»; eventualmente cronologia delle viste.
11. **Barra del tempo.** I nomi delle corsie sono a 10,5 px; la riga che spiega le corsie è lunga e tecnica. → corpo minimo 12 px, spiegazione breve con rimando al glossario.
12. **Rifiniture di testo.** «Il 820» invece di «L'820»; altre piccole incoerenze da raccogliere in un passaggio unico.

## Priorità 3: portare lo strumento al massimo

13. **Tavolo solo per le opere.** Non si possono mettere sul Tavolo luoghi, fenomeni, scavi, e non c'è un confronto affiancato di due schede.
14. **Lingua.** Solo italiano. Per test con interlocutori di altri paesi serve almeno l'inglese, coerente con l'obiettivo di parlare ai centri culturali di ogni regione.
15. **Ritorno dai tester.** Dopo le prime risposte del modulo, rivedere priorità 2 e 3 sui problemi reali, non su quelli previsti.

## Cosa funziona già bene

- Prestazioni: online circa 0,4 MB compressi all'apertura; coste e confini dettagliati si scaricano solo ingrandendo.
- Contrasto dei testi secondari almeno 5,1:1 in entrambi i temi; nessun testo sotto i 12 px fuori dalla barra del tempo.
- Nessuna richiesta a server di terzi.
- La guida, le domande da provare, le cartelle dei livelli, il segno scelto in risalto, il puntatore che distingue cosa è cliccabile.
- Il principio di lettura (fonte, grado, silenzio) è visibile in ogni scheda.
