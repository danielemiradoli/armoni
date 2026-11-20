# Atlante — primo taglio: il filo del blu e bianco

Atlante storico e geografico della storia dell'arte globale, costruito sul modello ad asserzioni di Armoni. Prototipo sperimentale. La domanda che mette alla prova l'idea: **come si è mosso il blu e bianco fra continenti e secoli, e quanto di questo movimento le fonti aperte permettono davvero di vedere?**

## Strati

| strato | contenuto | file |
| --- | --- | --- |
| 0 · spazio-tempo | confini storici per istantanee (700–1945), terre emerse | `web/confini/`, `web/terre.json` |
| 1 · periodi | periodizzazioni regionali in corsie parallele, ciascuna con il suo QID | `data/periodi.csv` |
| 2 · luoghi | centri di produzione, paesi, zone, sedi; ognuno con QID, **precisione** e metodo di risoluzione | `data/luoghi.csv` |
| 3 · entità | 2.024 pezzi con data da Met e Cleveland, più 101 da Wikidata conservati fuori dagli Stati Uniti (39 con data): origine, sede attuale, mercato dichiarato, intervallo | `web/opere.json` |
| 4 · relazioni | origine → sede (spostamento), origine → mercato (solo se il catalogo scrive «for … market») | calcolate nella pagina |
| 5 · analisi | densità per decennio, silenzio delle fonti (precisione, ipotesi, assenze) | calcolate nella pagina |

Ogni pezzo porta il **grado d'inclusione** (`documentato`: il record nomina il blu; `ipotetico`: manifattura nota per il blu, record muto sul colore) e il **criterio** con cui è entrato.

## Due interfacce

- `#ricerca` — strati, filtri, contesto per luogo e per pezzo, Tavolo per accostare pezzi diversi (tenuto solo nel browser).
- `#percorso` — otto tappe guidate. I testi sono redazionali e **da verificare con la bibliografia**; i numeri di ogni tappa sono calcolati sui dati.

## Riprodurre

```
# scaricare i due CSV in data/raw/ (URL in MANIFEST.md)
sh src/confini.sh          # richiede mapshaper
python3 src/build.py       # scrive web/*.json e out/metrics.md
python3 -m pytest tests    # 11 guardie
cd web && python3 -m http.server
```

## Cosa i dati dicono già (out/metrics.md)

- **Il 75% dei pezzi è localizzato solo per paese.** Jingdezhen è nominata in 59 schede: «Cina» in 679.
- Il 95% dei pezzi è conservato in **due musei degli Stati Uniti**. La terza fonte (Wikidata, collezioni fuori dagli USA) aggiunge São Paulo, Tokyo, Taipei, Macao, ma porta solo 101 pezzi, 68 dei quali azulejos del Museu Paulista senza data: entrano nei dati e non nel tempo.
- Per Iznik, Delft e Puebla il catalogo spesso non nomina il colore: il 20% del campione è ipotetico.

## Errori trovati e corretti in costruzione (ora sono test)

- `Tile` prendeva `Textiles`: 11 tessili entrati in silenzio come ceramica.
- Il criterio «elemento Wikidata più noto con quel nome» metteva Worcester, Chelsea e Bow negli Stati Uniti e le fornaci coreane nella Gwangju sbagliata.
- «Mamluk Sultanate» restituiva il sultanato di Delhi: escluso.
- «Puebla» da solo includeva ceramiche precolombiane dell'anno 900.
- «Azulejo» contiene «azul» ma significa piastrella; «sky blue glaze» e «cobalt blue glaze» sono monocromi: esclusi dal grado documentato.
- Con precisione «secolo» Wikidata registra un anno ambiguo (1800 = XVIII o XIX): si tengono entrambe le letture.

## Limiti dichiarati

- Tre fonti, ma il peso è quasi tutto statunitense; nessuna immagine. Le API di V&A, Europeana, Rijksmuseum, SMK, ColBase, Te Papa non sono raggiungibili da questo ambiente.
- Periodi da Wikidata: sono dinastie e stati, non periodizzazioni storico-artistiche. Lo strato giusto è PeriodO (CC0), non raggiungibile da questo ambiente.
- I confini di historical-basemaps sono GPL-3.0 e approssimati; le istantanee non coprono ogni anno.
