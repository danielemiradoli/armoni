"""ColBase, i quattro musei nazionali giapponesi, via Japan Search (CC BY). File: atlante/data/raw/colbase.json

Forno e paese stanno nei contributori; epoca e secolo nel campo temporale. Le date si leggono così:
anni espliciti > un solo anno dichiarato > secolo (con metà) > epoca; secolo ed epoca si intersecano se si sovrappongono.
"""
import csv, json, re

from .. import ATLANTE, GREZZI

SEDI = {'tnm': 'Tokyo National Museum', 'kyohaku': 'Kyoto National Museum', 'narahaku': 'Nara National Museum',
        'kyuhaku': 'Kyushu National Museum'}


def sede(p):
    # il campo provider usa a volte il codice ('tnm'), a volte il nome del museo
    if p in SEDI: return SEDI[p]
    if re.search(r'京都国立|Kyoto National', p): return 'Kyoto National Museum'
    if re.search(r'九州国立|Kyushu National', p): return 'Kyushu National Museum'
    if re.search(r'奈良国立', p): return 'Nara National Museum'
    if re.search(r'東京国立', p): return 'Tokyo National Museum'
    return None


# Luogo dedotto, mai dichiarato: al Museo nazionale di Tokyo la categoria 陶磁 separa la ceramica
# giapponese da quella asiatica (東洋陶磁). Misurata sui pezzi 陶磁 di Tokyo con luogo noto: 43 giapponesi
# su 49 (88%); il campione sovrarappresenta i pezzi stranieri, che sono quelli che dichiarano il luogo.
# A Kyoto e al Kyushu la categoria 陶磁 comprende anche la Cina: lì non si deduce nulla.
CRITERIO_DEDOTTO = ('dedotto dalla categoria 陶磁 del Museo nazionale di Tokyo (ceramica giapponese); '
                    'regola misurata: 43 giapponesi su 49 pezzi con luogo noto, 88%')

# 明治 prima di 明: '明治時代' contiene il carattere della dinastia Ming
EPOCHE = [('Periodo Meiji', r'明治|meiji'), ('Periodo Taishō', r'大正|taish'), ('Periodo Shōwa', r'昭和|sh[oō]wa'),
          ('Dinastia Ming', r'明|ming'), ('Dinastia Qing', r'清|qing'), ('Dinastia Yuan', r'元時代|yuan'),
          ('Periodo Edo', r'江戸|edo'), ('Periodo Muromachi', r'室町|muromachi'), ('Joseon', r'朝鮮時代|joseon')]


def intervallo(testi, periodi):
    t = ' '.join(testi)
    m = re.search(r'(\d{4})\s*[～~〜–-]\s*(\d{4})', t)
    if m:
        return int(m.group(1)), int(m.group(2)), 'anni'
    # anno finale abbreviato, come scrivono le ere giapponesi e cinesi: «1522～66» vale 1522–1566
    m = re.search(r'(\d{4})\s*[～~〜–-]\s*(\d{1,2})(?!\d)', t)
    if m:
        a, fine = m.group(1), m.group(2)
        b = int(a[:4 - len(fine)] + fine)
        return int(a), b if b >= int(a) else b + 100, 'anni'
    # un solo anno dichiarato («1618年») vale più dell'epoca
    m = re.search(r'(?<!\d)(1\d{3})\s*年', t)
    if m:
        return int(m.group(1)), int(m.group(1)), 'anno'
    sec = None
    m = re.search(r'(\d{1,2})(?:世紀|st|nd|rd|th)(?:\s*[～~–-]\s*(\d{1,2})(?:世紀|st|nd|rd|th))?', t)
    if m:
        c1, c2 = int(m.group(1)), int(m.group(2) or m.group(1))
        a, b = (c1 - 1) * 100, c2 * 100 - 1
        if not m.group(2) and re.search(r'前半|first half', t): b = a + 49
        if not m.group(2) and re.search(r'後半|second half', t): a = a + 50
        sec = (a, b)
    ep = next((periodi[n] for n, pat in EPOCHE if re.search(pat, t, re.I) and n in periodi), None)
    if sec and ep and sec[0] <= ep[1] and ep[0] <= sec[1]:
        return max(sec[0], ep[0]), min(sec[1], ep[1]), 'secolo ∩ epoca'
    if sec:
        return sec[0], sec[1], 'secolo'
    if ep:
        return ep[0], ep[1], 'epoca (Wikidata)'
    return None, None, None


def schede(ctx):
    periodi = {r['nome']: (int(r['inizio']), int(r['fine'])) for r in csv.DictReader(open(ATLANTE / 'data/periodi.csv', encoding='utf-8'))}
    for it in json.load(open(GREZZI / 'colbase.json', encoding='utf-8')):
        c = it['common']
        titolo = c.get('title', '') + ' ' + c.get('titleEn', '')
        campi = {'categoria': it.get('cobas-4-s') or '', 'titolo': titolo, 'parole': '/'.join(it['parole'])}
        if not ctx.passa(campi):
            continue
        # i contributori includono il museo che conserva e i donatori: non sono luoghi d'origine
        contrib = ' | '.join(x for x in c.get('contributor', []) if not re.search(r'博物館|museum|寄贈|gift|財団|foundation|研究所', x, re.I))
        ini, fin, prec = intervallo(c.get('temporal', []) + [it.get('cobas-11-s', '')], periodi)
        s = sede(c.get('provider', ''))
        yield dict(campi=campi, id=c['id'], fonte='colbase', titolo=c.get('titleEn') or c.get('title', ''), cultura=contrib[:160],
                   data_testo=' / '.join(x for x in c.get('temporal', []) if x) + (f' ({prec})' if prec else ''),
                   inizio=ini, fine=fin, tecnica=(c.get('title', '') + ' · ' + it.get('cobas-12-s', '')).strip(' ·'),
                   url=c.get('linkUrl', ''), licenza='CC BY — fonte: ColBase (国立文化財機構所蔵品統合検索システム)', wikidata='',
                   centro=contrib + ' | ' + titolo, paese=contrib,
                   incerto=bool(re.search(r'伝|推定|attributed|\?', contrib)), sede=s, mercato=None, export_senza_meta=False,
                   periodo=' / '.join(c.get('temporal', [])),
                   # la deduzione del luogo vale solo se il luogo non è dichiarato: la decide il motore del filo
                   deduci=(lambda o, s=s, it=it: {} if o or s != 'Tokyo National Museum' or it.get('cobas-4-s') != '陶磁'
                           else {'origine_dedotta': 'Japan', 'criterio_luogo': CRITERIO_DEDOTTO}))
