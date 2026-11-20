# Atlante — fonti

Prelievo del 20 novembre 2026. I file grezzi stanno in `data/raw/` e **non** sono nel repository (superano i 100 MB); si riscaricano dagli URL qui sotto e si confrontano con le impronte. Le sorgenti sono allineate al ramo principale, non a un commit: se un'impronta cambia, la fonte è cambiata.

Licenza registrata **per campo**, non per fonte (vedi `claude/integrazione_visione.md` §3C).

| file | fonte | sha256 | campi usati | licenza dei campi | immagini |
| --- | --- | --- | --- | --- | --- |
| `MetObjects.csv` | `media.githubusercontent.com/media/metmuseum/openaccess/master/MetObjects.csv` | `f53eb3bd6e321a05…` | titolo, cultura, date, tecnica, luogo, link, Wikidata | CC0 | non usate; record con `Is Public Domain = False` marcati |
| `cma_data.csv` | `media.githubusercontent.com/media/ClevelandMuseumArt/openaccess/master/data.csv` | `cbcbec43a61f68cd…` | titolo, cultura, date, tecnica, descrizione, url | CC0 (`share_license_status`) | non usate: il CDN non è raggiungibile e la pagina pubblicata non carica immagini remote |
| `data/luoghi.csv` | Wikidata, query in `data/query/luoghi*.rq`, `zone.rq` | nel repository | coordinate P625, QID | CC0 | — |
| `data/periodi.csv` | Wikidata, `data/query/periodi.rq` | nel repository | P571/P576 o P580/P582 | CC0 | — |
| `wikidata_ceramiche.csv` | Wikidata, `data/query/wikidata_ceramiche.rq` (oggetti in porcellana o ceramica con collezione fuori dagli Stati Uniti; 3.688 item, uguale al `COUNT` indipendente) | `02f799d3d8831b03…` | etichette, descrizioni, P571 con precisione, P495, P1071, P195 | CC0 | — |
| `vam.csv` | `api.vam.ac.uk/v2/objects/search`, frasi esatte «underglaze blue» e «blue and white» (`src/fetch_vam.py`; 10.036 oggetti, conteggi uguali a quelli dichiarati dall'API) | `d55de65d84f191d6…` | luogo, data, materiale, tipo, titolo (solo per riconoscere il luogo) | **condizioni V&A §9: uso non commerciale; vietato conservare i contenuti oltre 4 settimane** — il file non entra nel repository e va cancellato entro il 18/12/2026; nella pagina solo `web/densita_vam.json`, conteggi per luogo e decennio | non usate |
| `colbase.json` | Japan Search, `jpsearch.go.jp/api/item/search/jps-cross`, banca dati `cobas` (ColBase), parole 染付 e 青花 (`src/fetch_colbase.py`; 1.727 oggetti, conteggi uguali a quelli dichiarati) | `abf3124de52ad84e…` | titolo ja/en, contributori (forno, paese), epoca, materiale, link | **CC BY** (政府標準利用規約 2.0), attribuzione: «出典: ColBase» | non usate (la pagina non carica immagini remote) |
| `data/p0d.json` | PeriodO, `n2t.net/ark:/99152/p0d.json`, scaricato e caricato a mano da Daniele il 20/11/2026 (commit `d09e90d`) | `c745db85d7403025…` | periodi, autorità, copertura spaziale, lingua | pubblico dominio (CC0) | — |
| `data/jps_epoche.csv` | Japan Search, `jpsearch.go.jp/rdf/sparql`, `data/query/jps_epoche.rq` (72 epoche `HistoricalEra`, 48 con intervallo) | `ff83c982bbf36c6e…` | nome, intervallo, epoca madre, equivalente Wikidata | dati del portale, condizioni Japan Search (da verificare per campo) | — |
| `web/confini/*.json` | `aourednik/historical-basemaps`, `geojson/world_<anno>.geojson`, semplificati al 4% con mapshaper | sotto | NAME, geometrie | **GPL-3.0** | — |
| `web/terre.json` | npm `world-atlas@2.0.2`, `land-110m.json` (Natural Earth) | — | geometrie | pacchetto ISC, dati Natural Earth di pubblico dominio | — |

Impronte dei confini grezzi (primi 16 caratteri):

| file | sha256 |
| --- | --- |
| `world_1000.geojson` | `2140776fd7888c1d` |
| `world_1100.geojson` | `8b038ee5ec8f032d` |
| `world_1200.geojson` | `2d6913ecedb38e26` |
| `world_1279.geojson` | `839f48f61d984dd5` |
| `world_1300.geojson` | `a27985e60d936611` |
| `world_1400.geojson` | `c6b0efcb42d9520a` |
| `world_1492.geojson` | `b0e6b0f299fc7b19` |
| `world_1500.geojson` | `d01ffc9b80629787` |
| `world_1530.geojson` | `984005809f085285` |
| `world_1600.geojson` | `7285c07eeedfda90` |
| `world_1650.geojson` | `e691a3b5bab4ca7a` |
| `world_1700.geojson` | `eb73d6b00e98205f` |
| `world_1715.geojson` | `fdf5097dd21c30c9` |
| `world_1783.geojson` | `7cfa92418a8628df` |
| `world_1800.geojson` | `51fcb6b1f1c36195` |
| `world_1815.geojson` | `fb654f734583f550` |
| `world_1880.geojson` | `4751e30d881d60d3` |
| `world_1900.geojson` | `9c9221c851eaba49` |
| `world_1914.geojson` | `5adf01da9a7c25c9` |
| `world_1945.geojson` | `3005839db7bcc525` |
| `world_700.geojson` | `bb66ebee15e57f5d` |
| `world_800.geojson` | `9d046cdc4662109c` |
| `world_900.geojson` | `f483b93e799d6518` |
