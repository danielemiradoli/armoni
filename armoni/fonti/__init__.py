"""Un lettore per fonte, scritto una volta e usato da tutti i fili.

Ogni lettore espone `schede(ctx)` e restituisce, per ogni record, un dizionario con:

- `campi`: i campi originali della fonte, con i loro nomi, su cui i fili scrivono le regole di inclusione;
- i campi comuni: id, fonte, titolo, cultura, data_testo, inizio, fine, tecnica, classe, url, licenza, wikidata;
- `centro` e `paese`: i testi in cui cercare il luogo d'origine con il gazzettiere del filo,
  oppure `origine` già risolta quando la fonte la dichiara in forma strutturata (Wikidata, eMuseum);
- facoltativi: `custode` (l'istituzione che conserva il pezzo, come la scrive la fonte) e `custode_qid`; `incerto`, `sede`, `mercato`/`export_senza_meta`, `nota_data`, `extra` (campi propri della fonte).

Il lettore interpreta la fonte (date, epoche, luoghi strutturati), non decide che cosa entra in un filo.
"""
from . import met, cma, aic, colbase, emuseum, wikidata  # noqa: F401

LETTORI = {'met': met, 'cma': cma, 'aic': aic, 'colbase': colbase, 'emuseum': emuseum, 'wd': wikidata}
