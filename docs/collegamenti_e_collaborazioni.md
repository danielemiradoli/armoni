# Collegamenti di approfondimento e collaborazioni

Decisione del 22 novembre 2026, nata dall'incontro con *Atlante dell'Arte* (atlantedellarte.it). Documento di lavoro.

## L'idea

Armoni non scrive racconti: registra asserzioni con la loro fonte. Il racconto (contesto, lettura delle opere, interpretazione) esiste già altrove, scritto da chi lo sa fare: siti didattici, musei, centri di ricerca, istituti culturali dei vari paesi. Armoni **non lo copia: lo collega**.

Ogni voce di Armoni (un movimento, una dinastia, una scuola, un luogo, un'opera) può avere una sezione **«Per approfondire»** con collegamenti a fonti esterne, scelte da noi e, quando possibile, **in collaborazione dichiarata** con chi le pubblica.

Il beneficio va nei due sensi: la fonte esterna riceve lettori, e Armoni guadagna profondità e qualità senza scrivere testi propri.

Lo strumento è anche il più diretto per superare l'eurocentrismo. Armoni si rivolge ai centri culturali di riferimento di ogni paese, nella loro lingua, e lascia che siano loro a raccontare la propria arte.

## Due cose da non confondere

| | **fonti di dati** | **collegamenti di approfondimento** |
| --- | --- | --- |
| cosa entra in Armoni | i dati, come asserzioni | solo un collegamento con poche righe di presentazione |
| licenza richiesta | aperta (CC0, CC BY…) | nessuna: il contenuto resta sul sito di chi lo pubblica |
| chi ne risponde | Armoni, con fonte, metodo e grado | l'autore, con il suo nome |
| regola | protocollo di ingestione | criteri di questo documento |

Un partner può essere anche fonte di dati, se pubblica dati con licenza aperta: in quel caso le due cose restano distinte.

## Come si registra un collegamento

Due tabelle nel repository, leggibili da chiunque:

- `partner.csv`: chi è, che cosa pubblica, lingua, paese e macro-regione, tipo (sito didattico, museo, università, istituto culturale, rivista), stato (`collaborazione` con data dell'accordo, oppure `segnalato`), referente, condizioni concordate.
- `collegamenti.csv`: la voce di Armoni (identificativo Wikidata quando c'è), l'URL, il partner, la lingua della pagina, una riga di presentazione scritta dal partner o tratta dal titolo, chi l'ha proposto, la data di aggiunta, la data dell'ultimo controllo del collegamento.

L'identificativo Wikidata è la chiave comune. Un partner che sa a quale voce Wikidata corrisponde la propria pagina può fornire i suoi collegamenti in blocco, e usarli a sua volta per rimandare ad Armoni.

## Criteri di scelta (pubblici)

1. Responsabilità editoriale riconoscibile: un autore o un'istituzione con nome.
2. Indirizzi stabili.
3. Consultazione gratuita, almeno per la pagina collegata.
4. Fonti dichiarate, o competenza dell'autore verificabile.
5. Nessuna finalità di vendita della pagina collegata.
6. Priorità ai centri del paese o della cultura di cui si parla, e alle lingue locali.

## Partecipazione

Chiunque può proporre un tema verticale da coprire e una fonte che lo approfondisca. La proposta registra chi propone, la voce di Armoni, la fonte e il motivo. Entra se rispetta i criteri. Per ora le proposte arrivano a Daniele; più avanti, un modulo pubblico o un modello di segnalazione su GitHub.

## Misura

Come per i dati, la copertura si misura: collegamenti per macro-regione, per lingua e per tipo di partner. La misura compare nella vista Affidabilità. Così si vede dove mancano ancora interlocutori.

I collegamenti si controllano periodicamente: un collegamento rotto viene segnalato, mai tolto in silenzio.

## Primo caso: Atlante dell'Arte

Progetto didattico indipendente di Nicola Moscardi, insegnante di liceo: circa 197 capitoli di storia dell'arte, 1.757 opere nell'indice. È profondo e italiano dove Armoni è largo e mondiale. Proposta: collegare le voci di Armoni ai suoi capitoli e, se è d'accordo, ricevere i collegamenti inversi.

## Decisioni (22 novembre 2026)

- **A. Entrambe.** Si collegano sia le fonti in collaborazione attiva sia le fonti autorevoli «segnalate» senza accordo. La scheda le distingue.
- **B. La riga di presentazione** la scrive il partner quando c'è una collaborazione; altrimenti si usa il solo titolo della pagina. Si cambia approccio se servirà.
- **L'inserimento lo gestisce sempre Armoni**, a livello tecnico. Se servirà, uno strumento riservato ai collaboratori li aiuterà a fornire i materiali nel formato richiesto.
- **Tempi:** le collaborazioni partono dopo che il prototipo sarà online per i test reali. Il messaggio ad Atlante dell'Arte è pronto ma resta in attesa.
