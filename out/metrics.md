# Metriche di riconciliazione

Generato il 2026-11-10 da `armoni-reconcile` 0.1.0 sulle fonti fissate in `data/MANIFEST.md`.

- artisti MoMA: **9389** (anno di nascita noto: 49%)
- artisti Tate: **3532** (anno di nascita noto: 98%)
- asserzioni `sameAs`: **842** (23.8% del roster Tate)
- asserzioni `differentFrom`: **29** (vedi in fondo)

## Grado di certezza delle `sameAs`

| grado | n. | quota |
| --- | ---: | ---: |
| certo | 750 | 89.1% |
| probabile | 64 | 7.6% |
| possibile | 13 | 1.5% |
| contestato | 15 | 1.8% |

## Arbitrato sulle date (giudice indipendente dal nome)

- corroborate da almeno una data concorde: **762**
- in conflitto su una data: **15**
- non verificabili (una delle due fonti non ha date): **65**

Tasso di conflitto sulle coppie verificabili: **1.9%**. Non è un tasso di errore: mescola omonimi veri e casi in cui le due istituzioni registrano date diverse per la stessa persona. Gli omonimi privi di date, inoltre, non vengono intercettati affatto.

## Nessun legame viene scartato in silenzio

Le coppie con date in conflitto restano nel file come asserzioni `contestato`. Alcune sono omonimi veri (la Tate ha due Henry Moore, 1831–1895 e 1898–1986); altre sono la stessa persona su cui le due istituzioni non concordano (Milton Avery, 1885 per il MoMA e 1893 per la Tate). Distinguerle è lavoro editoriale umano, non una soglia da tarare.

## Misura contro il campione di riferimento

Campione: i collegamenti MoMA<->Tate fatti a mano su Wikidata.

| | tutto il campione | sola meta' di riporto |
| --- | ---: | ---: |
| coppie d'oro valutabili | 783 | 337 |
| asserzioni su cui l'oro ha un verdetto | 765 | 328 |
| sbagliate | 0 | 0 |
| **precisione** | **100.0%** | **100.0%** |
| **richiamo** | **97.7%** | **97.3%** |

La colonna di destra e' quella da citare: la meta' M-Z del campione non e'
stata usata per tarare nulla. La taratura e' avvenuta sulla meta' A-L.

**Questa precisione non e' la precisione del sistema.** Il campione d'oro
giudica gli artisti che qualcuno su Wikidata ha avuto motivo di collegare:
i famosi, i facili. Su 842 asserzioni emesse ne giudica
765, cioe' il 91%; sul resto nessuna fonte indipendente si pronuncia.
Meta' delle coppie d'oro riguarda inoltre artisti MoMA mai esposti nella
finestra 1929-1989, ed e' esclusa dal conteggio. La formulazione corretta e':
*100% di precisione sulla parte del problema che Wikidata
e' in grado di giudicare.*

Quanto questo conti si vede abbassando SIM_MIN da 85 a 75: la parte giudicata
dall'oro guadagna 7 asserzioni e la metrica migliora, mentre 174 asserzioni
compaiono dove l'oro tace, con una su quattro in conflitto sulle date.
La soglia e' rimasta a 85 per questo.

### Campione esteso: anche i casi difficili

Il campione sopra contiene solo coppie positive: dice quando due record sono
la stessa persona, mai quando sono persone diverse. Le negative si ricavano
dalla distinzione a livello di item su Wikidata (ID MoMA su un item, ID Tate
su un altro = due persone diverse affermate, non dedotte da un silenzio).

| esito | n. |
| --- | ---: |
| stessa persona | 765 |
| persona diversa, solida | 2 |
| persona diversa, duplicato Wikidata non escludibile | 21 |
| granularita' diversa (duo contro individuo) | 3 |
| nessun item su almeno un lato | 51 |

**Precisione fra 96.7% e 99.7%.** Non un numero ma un intervallo:
contando tutte le negative si ha il limite inferiore, contando solo quelle
solide il superiore. Il campione positivo da solo direbbe 100,0%, che era il
limite superiore di un intervallo di cui non mostrava l'altro capo.

Questo campione ha due modi propri di sbagliare, entrambi dichiarati: i duo
d'artisti, che la Tate registra come scheda unica e il MoMA come persone
(granularita', non errore di abbinamento); e i duplicati Wikidata non fusi,
escludibili solo quando i due item portano un ULAN o un VIAF.

| grado | stessa | diversa | incerta | duo | muto |
| --- | ---: | ---: | ---: | ---: | ---: |
| certo | 743 | 2 | 2 | 2 | 1 |
| probabile | 12 | 0 | 9 | 1 | 42 |
| possibile | 0 | 0 | 8 | 0 | 5 |
| contestato | 10 | 0 | 2 | 0 | 3 |

I quattro gradi si separano nettamente, ed e' la conferma piu' utile: `certo`
regge, `contestato` e' davvero una coppia contesa, e `possibile` non contiene
nemmeno un caso confermato come stessa persona. Quel grado va riesaminato.

## Asserzioni contestate

| MoMA | Tate | nascita | morte |
| --- | --- | --- | --- |
| Louis Marcoussis | Marcoussis, Louis | 1883 / 1878 | 1941 / 1941 |
| Charles Martin | Martin, Charles | 1952 / 1812 | — |
| Adolf Dehn | Dehn, Adolf | 1895 / 1895 | 1968 / 1963 |
| Lisette Model | Model, Lisette | 1901 / 1906 | 1983 / 1983 |
| Richard Taylor | Taylor, Richard | 1902 / 1775 | 1970 / 1791 |
| Milton Avery | Avery, Milton | 1885 / 1893 | 1965 / 1965 |
| T. Chambers | Chambers, George | 1808 / 1803 | 1869 / 1840 |
| Emilio Vedova | Vedova, Emilio | 1919 / 1919 | 1995 / 2006 |
| Serge Poliakoff | Poliakoff, Serge | 1906 / 1900 | 1969 / 1969 |
| Bryan Wynter | Wynter, Bryan | 1915 / 1915 | 1981 / 1975 |
| Frances Macdonald | Macdonald, Frances | 1873 / 1914 | 1921 / 2002 |
| Eric H. Olson | Olson, Eric | 1909 / 1909 | 1986 / 1996 |
| William T. Williams | Williams, William | 1942 / 1758 | — |
| Charles Atlas | Atlas, Charles | 1949 / 1958 | — |
| Camille Graeser | Graeser, Camille | 1892 / 1918 | 1980 / 1980 |

## Non-identita' (`differentFrom`)

Decisione D1, approvata il 10/11/2026. Si emette una non-identita' **solo
con prova positiva di distinzione**: il silenzio di una fonte non e' una
prova, e una coppia su cui nessuno si pronuncia resta `sameAs` contestata.
Due forme di prova:

- il campione d'oro assegna esplicitamente uno dei due record a un partner
  diverso (grado `certo`);
- gli item Wikidata sono distinti e ULAN o VIAF sono presenti e disgiunti
  su entrambi i lati (`certo`), oppure i soli item sono distinti con un
  ancoraggio esterno su entrambi i lati (`probabile`).

Tre casi in cui ci si astiene, tutti sostanziali: identificativo esterno
condiviso fra item distinti (duplicato Wikidata non fuso); identificativo
assente su un lato (il duplicato non si puo' escludere); duo e collettivi,
riconosciuti anche dall'etichetta Wikidata e non solo dal nome di catalogo
('Becher, Prof. Bernd' per la Tate, ma l'item e' 'Bernd and Hilla Becher').
Si tace inoltre davanti alla firma del duplicato non fuso: stesso nome e
stessa data di nascita su item diversi, come i due Ryszard Otreba.

| MoMA | Tate | grado | prova |
| --- | --- | --- | --- |
| William Merritt Chase | Chase, William | certo | ulan+viaf |
| R. Campbell | Campbell, Duncan | certo | oro |
| George Constant | Constant | certo | oro |
| McCarthy | McCarthy, Paul | certo | oro |
| John James Burnet | Burnet, John | certo | ulan+viaf |
| G. Clarke | Clarke Hall, Lady Edna | certo | oro |
| Hugh Donnell | O'Donnell, Hugh | certo | oro |
| Scott Wilson | Wilson, Scottie | certo | oro |
| Allan D. Jones, Jr. | Gwynne-Jones, Allan | certo | viaf |
| Manuel Antonio Caro | Caro, Antonio | certo | viaf |
| Alexander Benois | Benois, Alexander | certo | oro |
| Newman | Newman, Avis | certo | oro |
| George Bernard Shaw | Shaw, George | certo | oro |
| Lee | Lee, Catherine | certo | oro |
| John Thomson | Thomson, Rev. John, of Duddingston | certo | ulan+viaf |
| Leonard | Leonard, Zoe | certo | oro |
| William P. Frost | Frost, William Edward | certo | viaf |
| Philip John Martin | Martin, John | certo | ulan+viaf |
| Jane Wilson | Wilson, Jane | certo | oro |
| Martin Craig | Craig-Martin, Michael | certo | oro |
| Ernest Briggs | Briggs, Ernest | certo | viaf |
| Mario Garcia | Garcia Torres, Mario | certo | oro |
| Harry Gordon | Gordon, Sir Harry Percy, 2nd Bt | probabile | item |
| W. Jansen | Jansen, Angela | certo | oro |
| Harold Jones | Jones, Harold | certo | ulan+viaf |
| Robert Adams | Adams, Robert | certo | ulan+viaf |
| Olivier | Olivier, Herbert A. | certo | ulan |
| James Hamilton | Hamilton, James | certo | ulan+viaf |
| William Allan | Allan, Sir William | certo | ulan+viaf |
