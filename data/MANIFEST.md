# Manifest delle fonti

Ogni riga registra **che cosa** abbiamo usato, **da dove**, **in quale stato esatto** e
**con quale licenza**. Senza questo file un risultato non è riproducibile: fra sei mesi
non sapremmo su quale versione di un catalogo girava una metrica.

Le fonti già versionate pubblicamente su GitHub **non vengono duplicate qui**: ne fissiamo
il commit esatto e `src/fetch.py` le scarica a quello stato. Le fonti che non stanno su
GitHub (Getty, Wikidata, DoME) vanno depositate a mano in `data/raw/` e registrate sotto.

## Fonti recuperate automaticamente (commit fissato)

| Fonte | Contenuto | Repository | Commit | Licenza | Prelievo |
| --- | --- | --- | --- | --- | --- |
| MoMA, storia espositiva 1929–1989 | 1.727 mostre, 11.257 nomi, ruoli, date, ID Wikidata/ULAN/VIAF parziali | `MuseumofModernArt/exhibitions` | `5e1ce97416613068832255bdc4ddccc0fec7c508` | CC0 1.0 | 2026-11-09 |
| Tate, collezione | 69.201 opere, 3.532 artisti, anni di nascita e morte, anno di acquisizione | `tategallery/collection` | `a51d8afc988ed083557e2950f4d0b644e7719f4a` | CC0 1.0 | 2026-11-09 |

Impronte sha256 dei file letti dalla pipeline (le ristampa `src/fetch.py`):

- `MoMAExhibitions1929to1989.csv` — `d9e86c86fa5c379dd1aba588dfc35378a1276181c7334aa94c37d8c6fc12040e`
- `artist_data.csv` (Tate) — `b4a3cb051fe6ee93073e8a57ab600c449c37f64d9ea8135efb15d56e76299be2`

## Fonti da depositare a mano in `data/raw/`

| Fonte | Che cosa serve | Licenza | Stato |
| --- | --- | --- | --- |
| Getty ULAN | ID, nome preferito, varianti, nascita, morte, nazionalità. Non il dump integrale | ODC-By 1.0 (attribuzione obbligatoria) | da depositare |
| DoME (Univ. Vienna) | mostre europee 1905–1915 | da verificare | opzionale |

Limite GitHub: 100 MB per file. Depositare sottoinsiemi compressi, mai dump integrali.

## Fonti depositate in `data/raw/` (Wikidata)

Prelievo del 10 novembre 2026 con `src/fetch_wikidata.py`, licenza CC0 1.0.
Lo script pagina le query e **verifica ogni file contro un `COUNT(DISTINCT)`
indipendente**: senza questo controllo un prelievo parziale passa inosservato.

| File | Item attesi e ottenuti | Righe | sha256 |
| --- | ---: | ---: | --- |
| `wikidata_gold.csv` — item con entrambi gli ID (P2174 e P2741) | 1.668 | 1.863 | `a05cd418a5b0ae43995607c88d8f8ea8539511373218ea3f4dc2fa1180c88662` |
| `wikidata_moma.csv` — item con ID MoMA (P2174) | 20.350 | 22.032 | `732df9b450a0be6076ea63cf8673fdde86d6f00240bfaf25e36e92c4c7d9df56` |
| `wikidata_tate.csv` — item con ID Tate (P2741) | 4.299 | 4.868 | `1cd60deac103adcd4c3c65d80c9d8b9200e0da37153b41cf8eb95d541654e9ec` |

Le righe superano gli item perche' ULAN e VIAF possono avere piu' valori per item.

**Avvertenza sul prelievo precedente.** Un prelievo non paginato dello stesso
giorno aveva reso 12.270 item per `wikidata_moma.csv` (12.919 in una esecuzione
ancora precedente) e sembrava riuscito: con `SERVICE wikibase:label` il servizio
SPARQL supera il tempo massimo mentre scrive la risposta e restituisce un CSV
valido e tronco, senza codice di errore. Le cifre sugli item MoMA anteriori a
questo manifest sono quindi sottostimate. Gold e Tate non erano interessati.
