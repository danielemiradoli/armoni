# ArMoni

**Una base di conoscenza aperta sulla storia dell'arte globale, fatta di asserzioni con fonte; sopra, strumenti per leggerla.**
Progetto sperimentale, in corso, a costo zero.

Ogni dato di ArMoni è un'**asserzione**: dice che cosa afferma, **chi** lo afferma (la fonte),
**con quale metodo** è stato letto, **quanto è certo** e **con quale licenza** si può riusare.
Un disaccordo fra due istituzioni non viene risolto d'ufficio né scartato in silenzio, e dove
le fonti tacciono la base lo dice invece di riempire il vuoto.

ArMoni è il contenitore. Gli strumenti sono modi di leggerlo e di costruirlo:

| | che cosa fa | dove |
| --- | --- | --- |
| **la base comune** | un lettore per fonte (Met, Cleveland, Chicago, ColBase, eMuseum, Wikidata), i fili tematici come configurazione, l'archivio delle asserzioni | [`armoni/`](armoni/), [`comune.py`](comune.py) |
| **Atlante** | globo e tempo: i fili (porcellana blu e bianca, lacca) e i contesti artistici, con i silenzi delle fonti | [`atlante/`](atlante/) · [online](https://danielemiradoli.github.io/armoni/) |
| **motore delle identità** | riconosce quando due cataloghi parlano della stessa persona; oggi su MoMA ↔ Tate, da estendere agli artefici dei fili | [`src/`](src/), [`out/`](out/) |

Rigenerare la base: `python3 -m armoni.asserzioni blu lacca` → `out/armoni.sqlite` e il riepilogo
[`out/asserzioni.md`](out/asserzioni.md).

**Il modello è uno standard, non una nostra invenzione.** Entità e relazioni della base seguono
[CIDOC CRM](https://cidoc-crm.org/) (norma ISO 21127) nella forma pratica di [Linked Art](https://linked.art/),
e sono definite una volta sola in [`armoni/modello.py`](armoni/modello.py), senza nominare nessuna fonte:
sono le fonti ad adattarsi al modello, attraverso i loro lettori. Nella base ogni asserzione corrisponde a
un *E13 Attribute Assignment* (chi afferma, che cosa, con quale metodo). Nell'esportazione
(`python3 -m armoni.linkedart` → `out/linkedart.jsonl`, validata contro lo
[schema ufficiale](armoni/dati/linkedart_schema/)) ciò che la fonte dichiara diventa la proprietà diretta,
ciò che ArMoni deduce resta un'assegnazione esplicita di ArMoni con il metodo scritto. Un esempio per fonte
in [`armoni/esempi/linkedart/`](armoni/esempi/linkedart/).

---

# Il motore delle identità

Oggi non esiste un identificatore condiviso fra i cataloghi aperti di due dei musei
meglio documentati al mondo. Il MoMA pubblica un ID Wikidata sul 34% dei suoi artisti
e un ULAN sul 31%; i dati aperti della Tate non contengono né Wikidata, né ULAN, né
VIAF. Il collegamento fra le due collezioni regge interamente su confronto di stringhe.
Il motore nasce per rendere quel collegamento misurabile.

## Stato attuale

Due fonti collegate (MoMA ↔ Tate), **795 asserzioni di identità** emesse. Risultati
correnti in [`out/metrics.md`](out/metrics.md), dati in `out/identity_assertions.jsonl`.

| grado | quota | significato |
| --- | ---: | --- |
| certo | 82,9% | nomi identici e almeno una data concorde |
| probabile | 11,8% | nomi molto simili e date concordi, oppure nomi identici senza date verificabili |
| possibile | 2,3% | nomi simili ma non identici: date concordi con similarità sotto 90, oppure nessuna data verificabile |
| contestato | 3,0% | le due fonti sono in disaccordo su una data |

Il **3,4% delle coppie verificabili è in conflitto sulle date** (24 coppie). Non è un
tasso di errore: in 9 casi una data concorda e l'altra no, il che fa pensare alla stessa
persona registrata diversamente dalle due istituzioni; gli altri sono con ogni
probabilità omonimi. Gli omonimi privi di date non vengono intercettati affatto.

Limiti noti: le soglie (similarità 85, tolleranza 3 anni) sono state scelte a occhio e
non ancora tarate su un campione di riferimento; 9 artisti Tate risultano collegati a
due artisti MoMA diversi, e almeno alcuni di questi doppi legami sono errori.

## Il metodo

Il principio è che **la verifica deve venire da un campo che il matcher non ha usato**.
Qui gli abbinamenti si fanno sui nomi e si giudicano sulle date di nascita e morte.

1. Normalizzazione del nome (diacritici, punteggiatura, ordine dei token, onorificenze).
2. Blocco sul cognome, poi similarità fuzzy con soglia a 85.
3. Arbitrato sulle date con tolleranza di 3 anni: corroborato, in conflitto, non verificabile.
4. Emissione dell'asserzione con il grado di certezza che ne consegue.

Tre casi spiegano perché serve tutto questo:

- **Henry Moore.** La Tate ne ha due, il pittore di marine 1831–1895 e lo scultore
  1898–1986. L'abbinamento per solo nome prende il primo. Con l'arbitrato sulle date
  Armoni prende il secondo, quello giusto.
- **Vasily / Wassily Kandinsky.** Un abbinamento vero che il confronto esatto perde e
  che il fuzzy recupera, confermato da entrambe le date.
- **Milton Avery.** MoMA 1885, Tate 1893, stessa persona. Qui un filtro binario
  scarterebbe un legame corretto. Armoni lo emette come contestato e lo lascia a un
  occhio umano.

## Riprodurre i risultati

```bash
pip install pandas numpy rapidfuzz
python3 src/fetch.py       # scarica le fonti al commit fissato nel manifest
python3 src/reconcile.py   # produce out/identity_assertions.jsonl e out/metrics.md
```

Le fonti non vengono duplicate in questo repository: `data/MANIFEST.md` ne fissa il
commit esatto, la licenza e l'impronta dei file, e `src/fetch.py` le recupera a quello
stato. MoMA e Tate rilasciano i propri dati in CC0.

## Da dove viene

Armoni nasce come contrazione di *Art Monitor*, per un progetto che prevedeva un modulo
osservativo con funzioni predittive. Quel modulo è stato accantonato: nei primi test
la posizione di un artista nella rete delle co-esposizioni del MoMA aggiunge poco a ciò
che già dice il suo semplice profilo espositivo, sia nel prevedere le personali del MoMA
sia le acquisizioni della Tate. Un contributo piccolo c'è, ma non abbastanza da
giustificare un modulo.

Quello che i test hanno invece reso evidente è il vero collo di bottiglia:
l'armonizzazione delle identità. Il nome è rimasto perché ci piace e perché funziona.

## Cosa non è

Non è una piattaforma, non è un prodotto, non prevede nulla e non valuta nessuno. Non
stima prezzi e non classifica artisti. È uno strato di dati verificabile, e la sua unica
promessa è che ogni affermazione dichiari su cosa si regge.

## Prossimi passi

- Terza e quarta fonte: Getty ULAN e Wikidata, da depositare in `data/raw/` (vedi manifest)
- Pubblicazione delle asserzioni in JSON-LD Linked Art
- Revisione editoriale umana delle asserzioni contestate

## Licenze

Codice: Apache 2.0. Asserzioni prodotte: CC0, come le fonti da cui derivano. I dati di terzi conservano la propria licenza (per l'atlante: `atlante/LICENZE.md`; i confini storici sono GPL-3.0).
