# Metriche di riconciliazione

Generato il 2026-11-10 da `armoni-reconcile` 0.1.0 sulle fonti fissate in `data/MANIFEST.md`.

- artisti MoMA: **9389** (anno di nascita noto: 49%)
- artisti Tate: **3532** (anno di nascita noto: 98%)
- asserzioni di identita' emesse: **871** (24.7% del roster Tate)

## Grado di certezza

| grado | n. | quota |
| --- | ---: | ---: |
| certo | 751 | 86.2% |
| probabile | 73 | 8.4% |
| possibile | 16 | 1.8% |
| contestato | 31 | 3.6% |

## Arbitrato sulle date (giudice indipendente dal nome)

- corroborate da almeno una data concorde: **764**
- in conflitto su una data: **31**
- non verificabili (una delle due fonti non ha date): **76**

Tasso di conflitto sulle coppie verificabili: **3.9%**. Non è un tasso di errore: mescola omonimi veri e casi in cui le due istituzioni registrano date diverse per la stessa persona. Gli omonimi privi di date, inoltre, non vengono intercettati affatto.

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
i famosi, i facili. Su 871 asserzioni emesse ne giudica
765, cioe' il 88%; sul resto nessuna fonte indipendente si pronuncia.
Meta' delle coppie d'oro riguarda inoltre artisti MoMA mai esposti nella
finestra 1929-1989, ed e' esclusa dal conteggio. La formulazione corretta e':
*100% di precisione sulla parte del problema che Wikidata
e' in grado di giudicare.*

Quanto questo conti si vede abbassando SIM_MIN da 85 a 75: la parte giudicata
dall'oro guadagna 7 asserzioni e la metrica migliora, mentre 174 asserzioni
compaiono dove l'oro tace, con una su quattro in conflitto sulle date.
La soglia e' rimasta a 85 per questo.

## Asserzioni contestate

| MoMA | Tate | nascita | morte |
| --- | --- | --- | --- |
| William Merritt Chase | Chase, William | 1849 / 1878 | 1916 / 1944 |
| Louis Marcoussis | Marcoussis, Louis | 1883 / 1878 | 1941 / 1941 |
| Charles Martin | Martin, Charles | 1952 / 1812 | — |
| George Constant | Constant | 1892 / 1920 | 1978 / 2005 |
| John James Burnet | Burnet, John | 1857 / 1784 | 1938 / 1868 |
| Adolf Dehn | Dehn, Adolf | 1895 / 1895 | 1968 / 1963 |
| Lisette Model | Model, Lisette | 1901 / 1906 | 1983 / 1983 |
| Allan D. Jones, Jr. | Gwynne-Jones, Allan | — | — |
| Richard Taylor | Taylor, Richard | 1902 / 1775 | 1970 / 1791 |
| Milton Avery | Avery, Milton | 1885 / 1893 | 1965 / 1965 |
| Manuel Antonio Caro | Caro, Antonio | — | — |
| T. Chambers | Chambers, George | 1808 / 1803 | 1869 / 1840 |
| George Bernard Shaw | Shaw, George | 1856 / 1966 | — |
| John Thomson | Thomson, Rev. John, of Duddingston | 1837 / 1778 | 1921 / 1840 |
| William P. Frost | Frost, William Edward | — | — |
| Philip John Martin | Martin, John | 1927 / 1789 | — |
| Jane Wilson | Wilson, Jane | 1924 / 1967 | — |
| Ernest Briggs | Briggs, Ernest | — | — |
| Emilio Vedova | Vedova, Emilio | 1919 / 1919 | 1995 / 2006 |
| Serge Poliakoff | Poliakoff, Serge | 1906 / 1900 | 1969 / 1969 |
| Bryan Wynter | Wynter, Bryan | 1915 / 1915 | 1981 / 1975 |
| Frances Macdonald | Macdonald, Frances | 1873 / 1914 | 1921 / 2002 |
| Eric H. Olson | Olson, Eric | 1909 / 1909 | 1986 / 1996 |
| Harold Jones | Jones, Harold | 1940 / 1904 | — |
| Robert Adams | Adams, Robert | 1937 / 1917 | — |
| William T. Williams | Williams, William | 1942 / 1758 | — |
| Olivier | Olivier, Herbert A. | — | — |
| James Hamilton | Hamilton, James | 1928 / 1640 | — |
| Charles Atlas | Atlas, Charles | 1949 / 1958 | — |
| William Allan | Allan, Sir William | 1936 / 1782 | — |
| Camille Graeser | Graeser, Camille | 1892 / 1918 | 1980 / 1980 |
