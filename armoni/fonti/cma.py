"""Cleveland Museum of Art, Open Access CSV (CC0). File: atlante/data/raw/cma_data.csv"""
from .. import GREZZI
from ..testo import anno

SEDE = 'Cleveland Museum of Art'
_CACHE = {}


def tabella():
    if 'df' not in _CACHE:
        import pandas as pd
        _CACHE['df'] = pd.read_csv(GREZZI / 'cma_data.csv', dtype=str, low_memory=False).fillna('')
    return _CACHE['df']


def schede(ctx):
    df = ctx.prefiltra(tabella())
    cols = list(df.columns)
    for row in df.itertuples(index=False, name=None):
        d = dict(zip(cols, row))
        cult = d['culture']
        yield dict(campi=d, id='cma:' + d['id'], fonte='cma', titolo=d['title'], cultura=cult,
                   data_testo=d['creation_date'], inizio=anno(d['creation_date_earliest']),
                   fine=anno(d['creation_date_latest']), tecnica=d['technique'], classe=d['type'],
                   centro=' | '.join([cult, d['title']]), paese=cult.split(',')[0],
                   url=d['url'], sede=SEDE, wikidata='',
                   licenza='CC0' if d['share_license_status'] == 'CC0' else 'diritti: ' + (d['share_license_status'] or 'non dichiarati'),
                   artefice=d.get('creators', ''))
