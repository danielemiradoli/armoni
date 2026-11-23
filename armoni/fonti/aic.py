"""Art Institute of Chicago, API pubblica (metadati CC0). File: atlante/data/raw/aic/lacca.jsonl (src/fetch_aic.py)"""
import json

from .. import GREZZI

SEDE = 'Art Institute of Chicago'


def schede(ctx):
    p = GREZZI / 'aic/lacca.jsonl'
    if not p.exists():
        return
    for l in open(p, encoding='utf-8'):
        d = json.loads(l)
        campi = {k: (v if isinstance(v, str) else ' | '.join(v) if isinstance(v, list) else '' if v is None else str(v)) for k, v in d.items()}
        if not ctx.passa(campi):
            continue
        luogo = d['place_of_origin'] or ''
        yield dict(campi=campi, id='aic:%d' % d['id'], fonte='aic', titolo=d['title'], cultura=luogo,
                   data_testo=d['date_display'] or '', inizio=d['date_start'], fine=d['date_end'],
                   tecnica=d['medium_display'], classe=d['artwork_type_title'] or '',
                   centro=' | '.join([luogo, d['title'] or '', d['style_title'] or '']),
                   paese=' | '.join([luogo, d['style_title'] or '']),
                   url='https://www.artic.edu/artworks/%d' % d['id'], sede=SEDE, wikidata='',
                   licenza='metadati CC0' + ('' if d['is_public_domain'] else '; immagine non di pubblico dominio'))
