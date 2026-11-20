"""Riepilogo di affidabilita' dell'atlante: dove i dati reggono e dove no, per regione e secolo.

Per ogni cella regione x secolo: quanti pezzi, quota documentata (il record nomina il blu),
quota localizzata per citta', quota con attribuzione dichiarata incerta; accanto, i conteggi
aggregati del V&A e le asserzioni bibliografiche. A parte: pezzi senza luogo e senza data.
Il secolo e' quello del punto medio dell'intervallo di datazione.
Regione: dal paese (P17 su Wikidata, data/paesi_luoghi.csv); i tre luoghi senza P17 sono assegnati qui.
Uscite: out/qualita.md, web/qualita.json."""
import csv, json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGIONE_PAESE = {
    "People's Republic of China": 'Cina', 'Taiwan': 'Cina', 'Japan': 'Giappone', 'Empire of Japan': 'Giappone',
    'Joseon': 'Corea', 'Goryeo': 'Corea', 'Korean Empire': 'Corea', 'Later Silla': 'Corea',
    'Later Three Kingdoms': 'Corea', 'Three Kingdoms of Korea': 'Corea', 'Vietnam': 'Sud-est asiatico',
    'Thailand': 'Sud-est asiatico', 'Myanmar': 'Sud-est asiatico', 'Indonesia': 'Sud-est asiatico', 'Philippines': 'Sud-est asiatico',
    'Iran': 'Iran e Asia centrale', 'Iraq': 'Iran e Asia centrale', 'Uzbekistan': 'Iran e Asia centrale', 'Afghanistan': 'Iran e Asia centrale',
    'Azerbaijan': 'Iran e Asia centrale', 'India': 'Asia meridionale', 'Pakistan': 'Asia meridionale',
    'Turkey': 'Anatolia e Mediterraneo', 'Syria': 'Anatolia e Mediterraneo', 'Egypt': 'Anatolia e Mediterraneo',
    'Morocco': 'Africa', 'Tunisia': 'Africa', 'Nigeria': 'Africa', 'Mexico': 'Americhe', 'United States': 'Americhe', 'Brazil': 'Americhe'}
EUROPA = {'Austria', 'Belgium', 'Denmark', 'Kingdom of Denmark', 'France', 'Germany', 'Ireland', 'Italy', 'Netherlands',
          'Kingdom of the Netherlands', 'Norway', 'Poland', 'Portugal', 'Russia', 'Spain', 'Sweden', 'United Kingdom',
          'Switzerland', 'Hungary', 'Czech Republic'}
SENZA_P17 = {'Q46': 'Europa', 'Q9903': 'Cina', 'Q29520': 'Cina'}  # Europa, dinastia Ming, Cina (regione storica)
REGIONI = ['Cina', 'Corea', 'Giappone', 'Sud-est asiatico', 'Iran e Asia centrale', 'Asia meridionale',
           'Anatolia e Mediterraneo', 'Africa', 'Europa', 'Americhe']
SECOLI = list(range(800, 2000, 100))


def regioni_per_qid():
    out = dict(SENZA_P17)
    for r in csv.DictReader(open(ROOT / 'data/paesi_luoghi.csv', encoding='utf-8')):
        q = r['item'].rsplit('/', 1)[-1]
        p = r['paeseLabel']
        reg = 'Europa' if p in EUROPA else REGIONE_PAESE.get(p)
        if reg and q not in out:
            out[q] = reg
    return out


def main():
    reg_q = regioni_per_qid()
    luoghi = {l['id']: l for l in json.load(open(ROOT / 'web/luoghi.json', encoding='utf-8'))}
    opere = json.load(open(ROOT / 'web/opere.json', encoding='utf-8'))
    celle = defaultdict(lambda: {'n': 0, 'doc': 0, 'citta': 0, 'incerta': 0, 'vam': 0.0})
    fuori = {'senza luogo': 0, 'senza data': 0, 'regione non determinata': 0, 'fuori scala (prima dell\'800)': 0}
    for o in opere:
        if o['inizio'] is None:
            fuori['senza data'] += 1
            continue
        if not o['origine']:
            fuori['senza luogo'] += 1
            continue
        reg = reg_q.get(luoghi[o['origine']]['qid'])
        if not reg:
            fuori['regione non determinata'] += 1
            continue
        sec = (o['inizio'] + o['fine']) // 2 // 100 * 100
        if sec < 800:
            fuori['fuori scala (prima dell\'800)'] += 1
            continue
        c = celle[(reg, min(sec, 1900))]
        c['n'] += 1
        c['doc'] += o['grado'] == 'documentato'
        c['citta'] += luoghi[o['origine']]['precisione'] == 'citta'
        c['incerta'] += bool(o['origine_incerta'])
    vam = json.load(open(ROOT / 'web/densita_vam.json', encoding='utf-8'))
    vq = {l['id']: l['qid'] for l in vam['luoghi']}
    for k in vam['celle']:
        reg = reg_q.get(vq.get(k['l']))
        if reg and 800 <= k['d'] < 2000:
            celle[(reg, k['d'] // 100 * 100)]['vam'] += k['n']
    let = json.load(open(ROOT / 'web/letteratura.json', encoding='utf-8'))
    n_let = len(let['asserzioni'])

    tab = [{'r': r, 's': s, **{k: (round(v, 1) if k == 'vam' else v) for k, v in celle[(r, s)].items()}}
           for r in REGIONI for s in SECOLI if (r, s) in celle]
    json.dump({'celle': tab, 'fuori': fuori, 'letteratura': n_let, 'regioni': REGIONI, 'secoli': SECOLI},
              open(ROOT / 'web/qualita.json', 'w', encoding='utf-8'), ensure_ascii=False)

    righe = ['# Affidabilità dell\'atlante per regione e secolo', '',
             'Rigenerato da `src/qualita.py`. Cella: pezzi · % documentati (blu nel record) · % localizzati per città. '
             'Secolo del punto medio della datazione; regione dal paese su Wikidata (P17).', '',
             '| regione | ' + ' | '.join(f'{s}' for s in SECOLI) + ' |', '| --- |' + ' ---: |' * len(SECOLI)]
    for r in REGIONI:
        cel = []
        for s in SECOLI:
            c = celle.get((r, s))
            cel.append(f'{c["n"]} · {round(100 * c["doc"] / c["n"])}% · {round(100 * c["citta"] / c["n"])}%' if c and c['n'] else '—')
        righe.append(f'| {r} | ' + ' | '.join(cel) + ' |')
    righe += ['', 'Fuori dalla tabella: ' + ', '.join(f'{k} {v}' for k, v in fuori.items()) + '.',
              f'Asserzioni bibliografiche (consumo): {n_let}, in `data/letteratura.csv`.']
    (ROOT / 'out/qualita.md').write_text('\n'.join(righe) + '\n', encoding='utf-8')
    print('\n'.join(righe))


if __name__ == '__main__':
    main()
