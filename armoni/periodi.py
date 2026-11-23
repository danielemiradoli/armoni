"""Periodi: un concetto per periodo (ancorato a Wikidata), riconosciuto in qualunque lingua lo scriva una fonte.

Le fonti scrivono i periodi a modo loro: «Edo period (1615–1868)» (Met), «江戸時代 / 18世紀» (ColBase), «조선» (eMuseum),
«Qing dynasty (1644–1911), Kangxi period (1662–1722)». La base non costruisce una tabella per ciascuna fonte: confronta
ciò che la fonte scrive con le etichette e gli alias del periodo su Wikidata, in 17 lingue (armoni/dati/periodi_wikidata.json).

Regole, uguali per tutte le fonti e tutte le lingue:
- il testo si divide nelle sue parti («, » «;» «/» « or »): ogni parte è una dichiarazione distinta;
- dalle parti e dalle etichette si tolgono le date fra parentesi, i qualificatori (early, middle, late, 前期, 후기…) e le
  parole generiche (period, dynasty, era, 時代, 王朝, 시대, periodo, dinastia…), che non distinguono un periodo da un altro;
- un'etichetta vale solo se il periodo è compatibile con le date del pezzo (si sovrappone, con 50 anni di tolleranza);
- se restano più periodi con la stessa etichetta, vale quello che Wikidata documenta in almeno il doppio delle lingue del secondo
  (di solito il concetto principale rispetto a una voce minore); altrimenti la base non sceglie e la dichiarazione resta testo.
"""
import json, re, unicodedata
from collections import defaultdict
from functools import lru_cache
from pathlib import Path

DATI = Path(__file__).resolve().parent / 'dati/periodi_wikidata.json'
TOLLERANZA = 50

GENERICHE = (r'\b(?:period[oe]?|periods|dynast(?:y|ies)|dinastia|dynastie|dinast[ií]a|era|epoch|epoca|[ée]poque|p[ée]riode|reign|regno|'
             r'empire|impero|kingdom|regno|state|age|times?|the|of|di|del|della|la|le|il)\b|時代|时代|時期|王朝|朝$|시대|왕조|시기')
# non sono periodi: secoli, anni, «sconosciuto»; una parte che contiene solo questo non è una dichiarazione di periodo
NON_PERIODO = (r'\b(?:\d*\s*(?:st|nd|rd|th)|\d+|centur(?:y|ies)|secol[oi]|si[èe]cles?|mark|and|e|et|und|y|ca|circa|ca\.?|after|before|dopo|prima)\b|'
               r'世紀|世纪|年間|年|세기|년|이후|이전|미상|未詳|不明|unknown|ignoto|sconosciut[oa]')
QUALIF = (r'\b(?:early|middle|mid|late|first half of|second half of|first|second|third|final|later|earlier|initial|'
          r'inizio|tardo|primo|medio|alto|basso)\b|前期|中期|後期|后期|初期|末期|前半|後半|后半|초기|중기|후기|말기|전기|후반|전반')


def norma(t):
    t = unicodedata.normalize('NFKC', t or '').lower()
    t = re.sub(r'\([^)]*\)', ' ', t)          # date e note fra parentesi
    t = re.sub(r'[\d–\-~～〜]+', ' ', t)        # anni rimasti fuori dalle parentesi
    t = re.sub(QUALIF, ' ', t)
    t = re.sub(GENERICHE, ' ', t)
    t = re.sub(NON_PERIODO, ' ', t)
    t = re.sub(r"[.,'’\"«»]", ' ', t)
    return re.sub(r'\s+', ' ', t).strip()


def parti(testo):
    """«Qing dynasty (1644–1911), Kangxi period (1662–1722)» → due dichiarazioni distinte."""
    t = re.sub(r'\([^)]*\)', lambda m: m.group(0).replace(',', ' '), testo or '')  # le virgole dentro le parentesi non dividono
    return [p.strip() for p in re.split(r'[,;/|·・･、]| or |\bor\b| o | - ', t) if p.strip()]


@lru_cache(None)
def vocabolario():
    d = json.load(open(DATI, encoding='utf-8'))
    per = {p['qid']: p for p in d['periodi']}
    idx = defaultdict(set)
    for p in d['periodi']:
        for lingua, ts in p['etichette'].items():
            for t in ts:
                n = norma(t)
                if len(n) >= 1:
                    idx[n].add(p['qid'])
    return per, idx


def etichetta(qid, lingue=('it', 'en', 'ja', 'zh', 'ko')):
    per, _ = vocabolario()
    e = per[qid]['etichette']
    return next((e[l][0] for l in lingue if e.get(l)), qid)


def riconosci(testo, inizio=None, fine=None):
    """Per ogni parte del testo: (parte, qid | None, motivo). motivo: 'riconosciuto', 'ambiguo', 'sconosciuto', 'date incompatibili'."""
    per, idx = vocabolario()
    out = []
    for p in parti(testo):
        n = norma(p)
        if not n:
            continue
        cand = idx.get(n, set())
        if not cand:
            out.append((p, None, 'sconosciuto')); continue
        if inizio is not None and fine is not None:
            cand = {q for q in cand if per[q]['inizio'] - TOLLERANZA <= fine and per[q]['fine'] + TOLLERANZA >= inizio}
            if not cand:
                out.append((p, None, 'date incompatibili')); continue
        if len(cand) > 1:
            # più periodi con la stessa etichetta: si sceglie quello che Wikidata documenta in molte più lingue
            # (almeno il doppio del secondo), di solito il concetto principale rispetto a una voce minore; altrimenti non si sceglie
            n_et = sorted(((sum(len(v) for v in per[q]['etichette'].values()), q) for q in cand), reverse=True)
            if n_et[0][0] >= 2 * n_et[1][0]:
                out.append((p, n_et[0][1], 'riconosciuto (fra omonimi, il più documentato)')); continue
            out.append((p, None, 'ambiguo')); continue
        out.append((p, next(iter(cand)), 'riconosciuto'))
    return out
