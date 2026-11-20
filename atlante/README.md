# Atlante — primo taglio: il filo del blu e bianco

Atlante storico e geografico della storia dell'arte globale, costruito sul modello ad asserzioni di Armoni. Prototipo sperimentale. La domanda che mette alla prova l'idea: **come si è mosso il blu e bianco fra continenti e secoli, e quanto di questo movimento le fonti aperte permettono davvero di vedere?**

## Strati

| strato | contenuto | file |
| --- | --- | --- |
| 0 · spazio-tempo | confini storici per istantanee (700–1945), terre emerse | `web/confini/`, `web/terre.json` |
| 1 · periodi | **PeriodO** più le epoche di **Japan Search** (in giapponese): 1.237 definizioni di periodo per 10 regioni, ognuna con l'autorità che la definisce e la lingua del nome; in alternativa le dinastie di Wikidata | `data/p0d.json`, `web/periodo.json`, `data/periodi.csv` |
| 2 · luoghi | centri di produzione, paesi, zone, sedi; ognuno con QID, **precisione** e metodo di risoluzione | `data/luoghi.csv` |
| 3 · entità | 2.024 pezzi con data da Met e Cleveland, più 101 da Wikidata conservati fuori dagli Stati Uniti (39 con data): origine, sede attuale, mercato dichiarato, intervallo | `web/opere.json` |
| 4 · relazioni | origine → sede (spostamento), origine → mercato (solo se il catalogo scrive «for … market») | calcolate nella pagina |
| 3b · densità V&A | 6.396 ceramiche del V&A ridotte a conteggi per luogo e decennio, senza schede (condizioni d'uso del museo) | `web/densita_vam.json` |
| 3c · consumo dalla letteratura | siti archeologici (costa swahili e oltre) con i numeri dei frammenti cinesi ricavati da articoli; ogni numero con autore e pagina; `src/letteratura.py` rifiuta righe senza provenienza | `data/siti_consumo.csv`, `data/bibliografia.csv`, `data/letteratura.csv` |
| 5 · analisi | densità per decennio, silenzio delle fonti (precisione, ipotesi, assenze) | calcolate nella pagina |

Ogni pezzo porta il **grado d'inclusione** (`documentato`: il record nomina il blu; `ipotetico`: manifattura nota per il blu, record muto sul colore) e il **criterio** con cui è entrato.

## Tre viste

- `#ricerca` — strati, filtri, contesto per luogo e per pezzo, Tavolo per accostare pezzi diversi (tenuto solo nel browser).
- `#percorso` — dieci tappe guidate. Ogni frase con riferimento tra parentesi rimanda a pagina o paragrafo di una fonte letta per intero; quanto non ha fonte sta in un riquadro «Da verificare». I numeri sono calcolati sui dati.
- `#qualita` — dove l'atlante regge e dove no: per regione e secolo, quota documentata, quota localizzata per città, pezzi, conteggi V&A (`src/qualita.py`, `out/qualita.md`).

## Riprodurre

```
# scaricare i due CSV in data/raw/ (URL in MANIFEST.md)
sh src/confini.sh          # richiede mapshaper
python3 src/build.py       # scrive web/*.json e out/metrics.md
python3 src/periodo.py && python3 src/letteratura.py && python3 src/qualita.py
python3 src/fetch_vam.py && python3 src/densita_vam.py   # V&A: solo conteggi; cancellare data/raw/vam.csv entro 4 settimane
python3 -m pytest tests    # 21 guardie
cd web && python3 -m http.server
```

## Cosa i dati dicono già (out/metrics.md)

- **Il 75% dei pezzi è localizzato solo per paese.** Jingdezhen è nominata in 59 schede: «Cina» in 679.
- Il V&A, anche se solo in forma di conteggi, ribalta la precisione: **il 68% dei suoi pezzi collocati è localizzato per città**, contro il 25% delle altre fonti; Jingdezhen vi compare 1.339 volte. Ma è un museo inglese, e la sua densità si concentra in Inghilterra.
- Con ColBase (1.707 ceramiche dei musei nazionali giapponesi, CC BY) le schede conservate negli Stati Uniti scendono dal 95% al **53%**. Ma ColBase porta il proprio silenzio: 1.332 pezzi senza luogo d'origine nel record (quasi tutti nel dipartimento di ceramica giapponese, che non lo dichiara; non lo deduciamo dal dipartimento perché vi compaiono anche pezzi olandesi) e 760 senza data.
- In precedenza il 95% dei pezzi era conservato in **due musei degli Stati Uniti**. La terza fonte (Wikidata, collezioni fuori dagli USA) aggiunge São Paulo, Tokyo, Taipei, Macao, ma porta solo 101 pezzi, 68 dei quali azulejos del Museu Paulista senza data: entrano nei dati e non nel tempo.
- Per Iznik, Delft e Puebla il catalogo spesso non nomina il colore: il 20% del campione è ipotetico.

## Dove l'atlante regge (out/qualita.md)

- In Asia il colore è quasi sempre dichiarato (90-100%) ma il luogo raramente è una città (Giappone 1-14%); in Europa e Anatolia il contrario (città 65-100%, colore dichiarato 3-30% dal Cinquecento: Iznik e Delft). Dove i cataloghi sanno il luogo non sanno il colore, e viceversa.
- Asia meridionale e Africa sono vuote nei cataloghi museali; l'Africa compare solo nello strato bibliografico.
- Fuori dalla tabella: 609 pezzi senza luogo, 834 senza data.

## Chi definisce il tempo (out/periodo.md)

- Fra 700 e 2000 PeriodO ha 140 periodi per la Cina, **tutti in inglese**; 93 per l'Iran, tutti in inglese; 85 per il Giappone, 18 in giapponese (un dizionario del 2014). Nessuno in cinese, persiano, coreano, vietnamita.
- Le autorità sono soprattutto il British Museum e la Library of Congress; per alcune regioni compaiono tavole europee del Sette-Ottocento (Priestley 1769, Willard 1835): nel 1700 le Americhe si chiamano «Spanish Mexico», «Portuguese Brasil».
- Japan Search aggiunge 33 epoche definite in giapponese, anche per Cina e Corea: un altro punto di vista, non neutro (usa «李氏朝鮮» per la Corea Joseon, elenca il Manciukuò come epoca cinese). Il suo 中世 finisce nel 1600; il «Middle Ages» di Emerton (1918) nel 1300, il «Medieval» di Historic England nel 1540.
- 93 periodi esistono ma non dicono a quale luogo si applicano (es. «Koryo Dynasty»).

## Il consumo, dalla letteratura (data/letteratura.csv)

- 11 asserzioni da Zhao Bing 2015 (*Afriques* 06, accesso aperto), letto per intero dal browser di Daniele: 7 siti fra Kenya e Tanzania. Ogni riga porta paragrafo e nota.
- Percentuali di ceramica dell'Estremo Oriente sul totale dei frammenti: 0,12% a Shanga, 0,9% a Gedi. Il blu e bianco qui è un bene raro, di élite.
- Ardabil (Medley, *Encyclopaedia Iranica* 1986, accesso aperto): il dono di Shah Abbas I contava 1.162 porcellane, circa 400 blu e bianche, installate nel 1611; 805 portate a Teheran nel 1935. La curva per secolo (37 del XIV, oltre 200 del primo XV, 25-30 del tardo XV, oltre 120 del XVI) segue il calo del commercio dopo il 1436. Il blu e bianco del Trecento di Topkapı viene dal saccheggio della collezione reale di Tabriz nel 1516.
- Topkapı (Tufan, *Millî Saraylar* 26, 2024, in turco, scritto dal responsabile della collezione): 5.373 blu e bianchi in inventario su ~12.000 porcellane cinesi; per epoca 40 Yuan, 54 primo Ming, 288 medio Ming, 2.308 tardo Ming, 2.680 primo Qing (somma 5.370: scarto di 3). Nel 1582, per la festa del principe Mehmed, 397 porcellane cinesi dal tesoro non bastarono: si comprarono 541 piatti di Iznik al bazar.
- Galeone di Manila (Von der Porten 2015, riassunto su tDAR): le porcellane di Drake (1579) e del San Agustín (1595) a Drakes Bay; il carico kraak di un galeone in Baja California datato 1575-1577, con identificazione poi rivista. I Miwok ne fecero gioielli (Zhao 2015 §30).
- Tre tipi di misura: conteggio, percentuale, presenza; unità «frammenti» (scavi) o «pezzi» (collezioni). Una presenza non porta numeri.
- Zhao 2012 (*Journal of World History*) non è ad accesso aperto: su HAL c'è solo la scheda.

## Errori trovati e corretti in costruzione (ora sono test)

- `Tile` prendeva `Textiles`: 11 tessili entrati in silenzio come ceramica.
- Il criterio «elemento Wikidata più noto con quel nome» metteva Worcester, Chelsea e Bow negli Stati Uniti e le fornaci coreane nella Gwangju sbagliata.
- «Mamluk Sultanate» restituiva il sultanato di Delhi: escluso.
- «Puebla» da solo includeva ceramiche precolombiane dell'anno 900.
- «Azulejo» contiene «azul» ma significa piastrella; «sky blue glaze» e «cobalt blue glaze» sono monocromi: esclusi dal grado documentato.
- ColBase: il museo stesso fra i contributori faceva risultare Kyoto origine di 464 pezzi; il donatore «Hirano» conteneva «iran». Ora le regole sui paesi hanno il confine di parola.
- 明治 (Meiji) contiene il carattere di 明 (Ming): l'ordine delle regole conta.
- Con precisione «secolo» Wikidata registra un anno ambiguo (1800 = XVIII o XIX): si tengono entrambe le letture.

## Limiti dichiarati

- Tre fonti, ma il peso è quasi tutto statunitense; nessuna immagine. V&A, ColBase e Japan Search raggiungibili dal 20/11. Europeana, Rijksmuseum, SMK, Te Papa non raggiungibili.
- PeriodO copre le regioni in modo diseguale e quasi solo in inglese: lo strato lo mostra, non lo corregge. Le dinastie di Wikidata servono ancora a datare le schede ColBase che indicano solo l'epoca.
- I confini di historical-basemaps sono GPL-3.0 e approssimati; le istantanee non coprono ogni anno. Restano file di dati separati sotto la loro licenza: l'elenco completo è in `LICENZE.md`.
- Luogo dedotto: 676 schede ColBase del Museo nazionale di Tokyo non dichiarano il luogo; la categoria 陶磁 le indica come ceramica giapponese. La regola, verificata sulle 49 schede della stessa categoria che il luogo lo dichiarano, è giusta 43 volte (88%), e il campione sovrarappresenta i pezzi stranieri. Strato separato, spento di default, fuori dalle metriche di localizzazione.
