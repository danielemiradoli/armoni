"""Metropolitan Museum of Art, Open Access CSV (CC0). File: atlante/data/raw/MetObjects.csv"""
from .. import GREZZI
from ..testo import anno

SEDE = 'Metropolitan Museum of Art'
_CACHE = {}


def tabella():
    """Il CSV si legge una volta per esecuzione, anche se lo usano più fili."""
    if 'df' not in _CACHE:
        import pandas as pd
        _CACHE['df'] = pd.read_csv(GREZZI / 'MetObjects.csv', dtype=str, low_memory=False).fillna('')
    return _CACHE['df']


def schede(ctx):
    df = ctx.prefiltra(tabella())
    cols = list(df.columns)
    for row in df.itertuples(index=False, name=None):
        d = dict(zip(cols, row))
        cult = d['Culture']
        yield dict(campi=d, id='met:' + d['Object ID'], fonte='met', titolo=d['Title'] or d['Object Name'],
                   cultura=cult, data_testo=d['Object Date'], inizio=anno(d['Object Begin Date']),
                   fine=anno(d['Object End Date']), tecnica=d['Medium'], classe=d['Classification'],
                   centro=' | '.join([d['City'], d['State'], d['Region'], cult, d['Title'], d['Period']]),
                   paese=' | '.join([d['Country'], cult.split(',')[0], d['Period'], d['Dynasty']]),
                   url=d['Link Resource'], sede=SEDE,
                   licenza='CC0' if d['Is Public Domain'] == 'True' else 'metadati CC0; immagine non di pubblico dominio',
                   wikidata=d['Object Wikidata URL'].rsplit('/', 1)[-1] if d['Object Wikidata URL'] else '',
                   # dichiarati dal catalogo, per le asserzioni: periodo e artefice
                   periodo=d['Period'], dinastia=d['Dynasty'], artefice=d['Artist Display Name'])
