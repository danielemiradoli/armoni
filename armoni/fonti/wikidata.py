"""Wikidata, oggetti fuori dalle collezioni statunitensi (CC0). File: atlante/data/raw/wikidata_ceramiche.csv

Il luogo è strutturato: P1071 (luogo di fabbricazione) prima di P495 (paese d'origine); la sede da P195.
Le date da P571 con la sua precisione; con precisione «secolo» l'anno registrato è ambiguo (1800 = XVIII o XIX?):
si tengono entrambe le letture invece di sceglierne una.
"""
import re

from .. import GREZZI
from ..testo import anno

PRC = 'Q148'  # Repubblica Popolare Cinese, fondata nel 1949


def intervallo(data, prec, a, b):
    if a and b:
        return anno(a[:5].rstrip('-')), anno(b[:5].rstrip('-')), 'P1319/P1326'
    if not data:
        return None, None, None
    y = anno(re.match(r'[+-]?\d+', data).group(0))
    p = int(float(prec)) if prec else 9
    if p >= 9:
        return y, y, 'anno'
    if p == 8:
        return y - y % 10, y - y % 10 + 9, 'decennio'
    if p == 7:
        c = (y // 100) * 100
        return c - 99, c + 100, 'secolo (lettura ambigua: entrambe tenute)'
    return None, None, None


def schede(ctx):
    import pandas as pd
    luoghi = ctx.luoghi
    qid2id = {r['qid']: k for k, r in luoghi.items()}
    q = lambda u: u.rsplit('/', 1)[-1] if u else ''

    def luogo(qid, nome, coord, prec, metodo):
        if not qid:
            return None
        if qid in qid2id:
            return qid2id[qid]
        if coord and qid not in luoghi:
            lo, la = re.match(r'Point\(([-\d.]+) ([-\d.]+)\)', coord).groups()
            luoghi[qid] = dict(id=qid, nome=nome or qid, qid=qid, lat=round(float(la), 4), lon=round(float(lo), 4),
                               precisione=prec, metodo=metodo)
        return qid if qid in luoghi else None

    d = pd.read_csv(GREZZI / 'wikidata_ceramiche.csv', dtype=str).fillna('')
    for w, g in d.groupby('w', sort=False):
        uniq = lambda c: sorted(set(x for x in g[c] if x))
        campi = {'testo': ' | '.join(uniq('lab') + uniq('desc'))}
        if not ctx.passa(campi):
            continue
        r = g.iloc[0]
        ini, fin, prec = intervallo(r['data'], r['prec'], r['inizio'], r['fine'])
        crea = luogo(q(r['crea']), r['creaLab'], r['creaCoord'], 'citta', 'P1071 su Wikidata')
        orig = crea or luogo(q(r['orig']), r['origLab'], r['origCoord'], 'paese', 'P495 su Wikidata')
        sede = luogo(q(r['col']), r['colLab'], next((c for c in g['colCoord'] if c), ''), 'istituzione',
                     'P625 della collezione o della sua sede')
        titoli = uniq('lab')
        yield dict(campi=campi, id='wd:' + q(w), fonte='wd',
                   titolo=next((t for t in titoli if re.match(r'[A-Za-zÀ-ÿ]', t)), titoli[0] if titoli else q(w)),
                   cultura=' | '.join(titoli[1:3]), data_testo=(r['data'][:4].lstrip('+') + f' ({prec})') if prec else '',
                   inizio=ini, fine=fin, tecnica=' | '.join(uniq('desc'))[:300],
                   url=w, licenza='CC0 (Wikidata)', wikidata=q(w), origine=orig, incerto=False,
                   sede=sede, mercato=None, export_senza_meta=False, custode=r['colLab'] or None, custode_qid=q(r['col']) or None,
                   extra={'origine_anacronistica': q(r['orig']) == PRC and fin is not None and fin < 1949})
