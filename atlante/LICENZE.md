# Licenze dei componenti dell'atlante

Scelta confermata da Daniele Miradoli il 20/11/2026: **codice Apache 2.0** (vedi `LICENSE` alla radice), **asserzioni prodotte da Armoni CC0**. I dati di terzi conservano la propria licenza, indicata qui e, campo per campo, in `MANIFEST.md`.

| componente | file | licenza | attribuzione richiesta |
| --- | --- | --- | --- |
| codice dell'atlante | `src/`, `tests/`, `web/index.html`, `web/atlante.js` | Apache 2.0 | — |
| asserzioni e tabelle derivate | `web/opere.json`, `web/luoghi.json`, `web/qualita.json`, `data/letteratura.csv`, `data/luoghi.csv`, `data/siti_consumo.csv` | CC0 | — (ogni riga cita comunque la propria fonte) |
| metadati Met, Cleveland, Wikidata, PeriodO | ricavati in `web/opere.json`, `web/periodo.json` | CC0 / pubblico dominio | — |
| metadati ColBase | ricavati in `web/opere.json` | CC BY (政府標準利用規約 2.0) | «出典: ColBase», presente in ogni scheda |
| metadati eMuseum (musei pubblici coreani) | ricavati in `web/opere.json`, solo schede con licenza KOGL tipo 1 | KOGL tipo 1 (공공누리 제1유형: attribuzione) | nome del museo che conserva il pezzo ed eMuseum, presenti in ogni scheda; le schede di tipo 2, 3 e 4 non sono usate |
| metadati Art Institute of Chicago (filo lacca) | ricavati in `web/fili/lacca/opere.json` | CC0 (api.artic.edu) | link alla scheda del museo in ogni pezzo |
| epoche di Japan Search | `data/jps_epoche.csv`, in `web/periodo.json` | CC0 per principio, con richiesta di citare la fonte | citata nella pagina e nel README |
| conteggi V&A | `web/densita_vam.json` | condizioni V&A §9 (uso non commerciale); solo conteggi aggregati, nessuna scheda | Victoria and Albert Museum |
| **confini storici** | `web/confini/*.json`, `web/confini/fini/*.json` (dettaglio) | **GPL-3.0**, da `aourednik/historical-basemaps` | André Ourednik, *historical-basemaps* |
| superfici per gli aloni | `web/aree.json` | CC0 (Wikidata); dove manca, area calcolata dai confini 2010 (GPL-3.0) | — |
| stili e movimenti, guerre e rivoluzioni | `web/contesti.json` | CC0 (Wikidata); il nome dello Stato di allora viene dai confini, GPL-3.0 | — |
| librerie di disegno | `web/lib/d3.min.js`, `web/lib/topojson-client.min.js` | ISC (d3, topojson-client) | testi in `web/lib/LICENSE-*.txt` |
| caratteri | `web/lib/font/` (Newsreader, Instrument Sans) | SIL Open Font License 1.1 | testi in `web/lib/font/OFL-*.txt` |
| terre emerse | `web/terre.json`, `web/terre50.json`, `web/terre10.json` (dettaglio, caricati solo ingrandendo) | Natural Earth, pubblico dominio (via npm `world-atlas`, ISC) | — |

I confini sono file di dati separati, distribuiti accanto al codice e non incorporati in esso: restano sotto GPL-3.0, con l'attribuzione qui sopra. Sostituibili con OpenHistoricalMap (CC0) dove la copertura basta. Questa nota descrive una scelta di progetto, non un parere legale.

La pagina non chiede nulla a server di terzi: caratteri e librerie sono serviti insieme al sito, così nessun indirizzo IP dei visitatori viene trasmesso altrove.
