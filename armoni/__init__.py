"""ArMoni: la base comune.

ArMoni è il contenitore; gli strumenti (l'Atlante, il grafo delle relazioni, il motore delle identità…) sono viste
che leggono e scrivono la stessa base. Questo pacchetto è quella base:

- `fonti/`      un lettore per fonte, scritto una volta (Met, Cleveland, Chicago, ColBase, eMuseum, Wikidata);
- `gazzettiere/` i nomi di luogo riconosciuti nei testi dei cataloghi, come dati e non come codice;
- `fili/`       i fili tematici come configurazione (che cosa entra, con quale criterio);
- `filo.py`     il motore che applica un filo alle fonti;
- `asserzioni.py` l'archivio delle asserzioni (fonte, metodo, grado, licenza) da cui si generano le viste.

Le regole di metodo sono in `claude/protocollo_ingestione.md` e, in forma verificabile, in `comune.py`.
"""
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent      # il repository
ATLANTE = RADICE / 'atlante'                          # lo strumento Atlante (dati grezzi e sito, per ora)
GREZZI = ATLANTE / 'data/raw'
