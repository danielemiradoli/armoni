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
| Wikidata | artisti con ULAN o VIAF, date, nazionalità — esito di una query SPARQL esportato in CSV | CC0 1.0 | da depositare |
| DoME (Univ. Vienna) | mostre europee 1905–1915 | da verificare | opzionale |

Limite GitHub: 100 MB per file. Depositare sottoinsiemi compressi, mai dump integrali.
