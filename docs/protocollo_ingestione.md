# Protocollo di ingestione dei dati

Versione del 22 novembre 2026. Vale per tutto Armoni: riconciliazione delle identità, atlante, ogni livello futuro. Ricavato da quello che è successo davvero nelle prime fonti (Met, Cleveland, Wikidata, ColBase, V&A, PeriodO, letteratura): ogni regola qui sotto corrisponde a un errore trovato o evitato. Documento di lavoro: si aggiorna quando una fonte nuova insegna qualcosa.

## 0. Il principio

Armoni non scrive verità: registra **asserzioni**. Ogni dato porta con sé quattro cose:

| campo | domanda |
| --- | --- |
| **fonte** | chi lo dice (istituzione, dataset, articolo con pagina) |
| **metodo** | come è arrivato qui (dichiarato, estratto da testo, dedotto con una regola) |
| **grado** | quanto è sicuro, con un vocabolario fisso (es. `documentato` / `ipotetico` / `dedotto`) |
| **licenza** | a quali condizioni lo si può ridistribuire |

Due conseguenze. Le fonti in disaccordo restano entrambe, con il disaccordo visibile. E il silenzio si mostra: dove una fonte non dice nulla, l'atlante non riempie.

Armoni procede **senza filtro di esperti umani**: solo dati aperti e fonti attendibili. I contributi umani qualificati, quando arriveranno, entreranno come un tipo di fonte in più (`contributo`, con autore e data), accanto alle altre e mai al loro posto. Lo schema non richiede modifiche per accoglierli.

## 1. Le otto fasi di una fonte nuova

### 1. Identificare
- Chi pubblica, che cosa, con quale licenza **per campo** (immagini, metadati e testi spesso hanno licenze diverse).
- Condizioni d'uso che limitano la conservazione. *Caso V&A: i contenuti dell'API non si conservano oltre 4 settimane → si tengono solo conteggi aggregati, il file grezzo si cancella.*
- Come si accede: dump, API, pagine. Se l'accesso fallisce, registrarlo subito in `fonti_mancanti.csv` (§5).
- Riga nel `MANIFEST.md` del livello.

### 2. Prelevare
- La query o lo script di prelievo **sta nel repository**, così il prelievo è ripetibile.
- **Il numero di record ottenuti si confronta con un conteggio indipendente** prima di usare il file. *Caso Wikidata: un CSV sintatticamente valido ma troncato, senza nessun errore; è il modo di fallire che nessun controllo di buon esito intercetta.*
- Data del prelievo e, per i file conservati, impronta sha256.
- I file grezzi stanno in `data/raw/` (escluso dal repository) quando sono grandi o quando le condizioni d'uso lo impongono.

### 3. Leggere a mano prima di scrivere regole
- Un campione di record, guardato uno per uno, prima di qualsiasi regola automatica.
- Si cercano i falsi amici. *Casi reali: «Tile» che prende «Textiles»; il museo che conserva l'oggetto letto come luogo di produzione (Kyoto, 464 pezzi); «Meiji» confuso con «Ming»; il donatore scambiato per un paese; l'azulejo che contiene «azul» ma non è blu.*

### 4. Mappare sullo schema
- Ogni campo diventa un'asserzione con i quattro attributi del §0.
- Si usano i vocabolari esistenti: tipi di fenomeno (movimento, scuola, stile, periodizzazione, macro-tendenza), precisione del luogo (città, paese, regione, zona, istituzione), macro-regioni (11), gradi.
- **Nessuno scarto per lingua**: un nome che esiste solo in giapponese o in catalano entra con la sua lingua dichiarata.

### 5. Dedurre solo con una regola misurata
Una deduzione è ammessa solo se:
1. la regola è scritta in chiaro, nel codice e nella scheda;
2. è **misurata sui casi in cui la risposta è nota**, e il tasso di errore è pubblicato;
3. il risultato sta in uno **strato separato**, spento all'apertura, e **fuori dalle metriche principali**.

*Casi: il luogo dedotto per ColBase (giusto in 43 casi su 49, 88%); la datazione dei movimenti ricavata dagli artisti (scarto mediano 13 anni su 120 casi con data nota).*

### 6. Misurare
Per ogni livello, rigenerato a ogni esecuzione:
- quanti record entrano e quanti no, e per quale motivo;
- distribuzione per **macro-regione** e per **secolo**, così lo squilibrio si vede invece di nascondersi;
- quanti record hanno ciascun campo.

### 7. Proteggere con i test
Ogni errore trovato diventa un test che fallirebbe se l'errore tornasse. Il numero dei test cresce con le fonti.

### 8. Pubblicare
Un commit per fonte o per passo, con le misure nel messaggio. Gli errori propri si dichiarano nel documento del livello, non si correggono in silenzio.

## 2. Regole per i campi delicati

**Fasi temporali** (germinale, apice, declino, fine). Entrano solo dove una fonte le dichiara **con quel significato**. Ogni marcatore ha la propria fonte: si possono avere l'inizio da Wikidata e l'apice da un articolo. Se una fonte testuale scrive «fiorì fra il 1680 e il 1720», l'asserzione è `apice: 1680–1720`, con metodo `estratto da testo` e il riferimento al passo (pagina o URL e frase). Non si deducono fasi da descrizioni generiche. Dove mancano, restano vuote e la barra del tempo mostra solo inizio e fine dichiarati.

**Relazioni fra fenomeni** (deriva da, reagisce contro, influenza su, parte di). Solo se una fonte le afferma. Livello separato, spento all'apertura. **La vicinanza nello spazio e nel tempo non genera mai una relazione.**

**Attribuzione di un'opera a un fenomeno.** Solo se lo scrive il catalogo dell'istituzione che conserva l'opera. Mai dedotta dalla data o dal luogo.

**Nomi di allora.** Lo Stato di allora viene dalle carte dei confini storici, con l'anno della carta dichiarato; se la carta più vicina dista più di 50 anni, nessuno Stato. Il nome storico di una città solo se la fonte ne dà le date.

**Aree di diffusione.** Nessun poligono disegnato a mano. Un'area si può ricavare da centri datati e dichiarati, e va etichettata come ricavata.

## 3. Ordine di attendibilità delle fonti

Non è una classifica di valore, ma l'ordine in cui conviene cercare:

1. dati strutturati di istituzioni (musei, archivi, gazetteer, PeriodO);
2. Wikidata, preferendo le affermazioni con riferimento;
3. letteratura scientifica, con autore, anno e pagina;
4. opere di consultazione (enciclopedie), con il riferimento al passo;
5. altro, solo come segnalazione da verificare su una fonte dei livelli precedenti.

Una fonte nuova entra sempre come strato separato, finché la sua misura non dice quanto vale.

## 4. Accesso al web: stato al 22 novembre 2026

Verificato dall'ambiente di lavoro di Claude, con una richiesta per indirizzo:

| raggiungibili | non raggiungibili o limitati |
| --- | --- |
| Wikidata, it.wikipedia, PeriodO, Getty (vocab, data), Pleiades, Iconclass, OpenHistoricalMap, ORBIS, Internet Archive, JSTOR (pagine), Met, Cleveland, Art Institute of Chicago, Rijksmuseum, Japan Search | en.wikipedia e OpenAlex (limite di richieste, 429), World Historical Gazetteer e openalex.org (403), museo di Taipei (connessione interrotta, anche dall'Italia), data.go.kr (403 dall'Italia), OpenEdition e tDAR (protezioni anti-bot, leggibili con Chrome) |

Per rendere l'ingestione fluida:
- **Domini**: si aggiungono in blocco, una volta, per le fonti già previste; quelli di questa tabella vanno già bene.
- **Pagine protette o dinamiche**: Chrome con l'estensione, quando è aperto.
- **Limiti di richieste**: prelievi lenti e ripresi, mai a raffica; per Wikipedia l'API ufficiale con un User-Agent dichiarato.
- **Blocchi per paese**: nessuna scorciatoia tecnica; richiesta scritta all'istituzione, e intanto il vuoto si dichiara (§5).

## 5. Le fonti che mancano si registrano

`atlante/data/fonti_mancanti.csv` registra ogni fonte cercata e non raggiunta: tentativo, esito, ripiego misurato, prossimo passo. Compare nella vista Affidabilità. Un vuoto nella mappa può essere un vuoto delle fonti e non della storia: il lettore deve poterli distinguere.
