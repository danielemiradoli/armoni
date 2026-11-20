# Licenze dei componenti dell'atlante

Scelta confermata da Daniele Miradoli il 20/11/2026: **codice Apache 2.0** (vedi `LICENSE` alla radice), **asserzioni prodotte da Armoni CC0**. I dati di terzi conservano la propria licenza, indicata qui e, campo per campo, in `MANIFEST.md`.

| componente | file | licenza | attribuzione richiesta |
| --- | --- | --- | --- |
| codice dell'atlante | `src/`, `tests/`, `web/index.html`, `web/atlante.js` | Apache 2.0 | — |
| asserzioni e tabelle derivate | `web/opere.json`, `web/luoghi.json`, `web/qualita.json`, `data/letteratura.csv`, `data/luoghi.csv`, `data/siti_consumo.csv` | CC0 | — (ogni riga cita comunque la propria fonte) |
| metadati Met, Cleveland, Wikidata, PeriodO | ricavati in `web/opere.json`, `web/periodo.json` | CC0 / pubblico dominio | — |
| metadati ColBase | ricavati in `web/opere.json` | CC BY (政府標準利用規約 2.0) | «出典: ColBase», presente in ogni scheda |
| epoche di Japan Search | `data/jps_epoche.csv`, in `web/periodo.json` | CC0 per principio, con richiesta di citare la fonte | citata nella pagina e nel README |
| conteggi V&A | `web/densita_vam.json` | condizioni V&A §9 (uso non commerciale); solo conteggi aggregati, nessuna scheda | Victoria and Albert Museum |
| **confini storici** | `web/confini/*.json` | **GPL-3.0**, da `aourednik/historical-basemaps` | André Ourednik, *historical-basemaps* |
| terre emerse | `web/terre.json` | Natural Earth, pubblico dominio (via npm `world-atlas`, ISC) | — |

I confini sono file di dati separati, distribuiti accanto al codice e non incorporati in esso: restano sotto GPL-3.0, con l'attribuzione qui sopra. Sostituibili con OpenHistoricalMap (CC0) dove la copertura basta. Questa nota descrive una scelta di progetto, non un parere legale.
