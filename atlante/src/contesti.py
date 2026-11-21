"""Livello «Contesti»: stili e movimenti artistici collocati nello spazio e nel tempo.

Il livello non e' collegato alle opere: accosta, non asserisce relazioni.
Per ogni elemento: nome, tipo, quando (dichiarato o dedotto, con il criterio), dove (uno o piu'
luoghi, con la precisione), il nome del luogo oggi e lo Stato che c'era allora (dai confini
storici), guerre e rivoluzioni in corso negli anni della nascita.

Ingressi (CC0, Wikidata; query in data/query/contesti_*.rq): data/raw/contesti/*.csv.
Confini: data/raw/confini/world_<anno>.geojson (historical-basemaps, GPL-3.0).
Uscite: web/contesti.json, out/contesti.md."""
import csv, json, re, statistics
from collections import Counter, defaultdict
from pathlib import Path

from shapely.geometry import Point, shape
from shapely.strtree import STRtree

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / 'data/raw/contesti'
TIPI = {'Q968159': 'movimento', 'Q1792644': 'stile'}
CONTINENTI = {'Q46': 'Europa', 'Q48': 'Asia', 'Q15': 'Africa', 'Q49': 'America settentrionale',
              'Q18': 'America meridionale', 'Q538': 'Oceania', 'Q55643': 'Oceania', 'Q3960': 'Oceania',
              'Q27611': 'America centrale', 'Q828': 'Americhe', 'Q5401': 'Eurasia'}
# Tipi di evento tenuti per il contesto: guerra, rivoluzione, guerra civile, guerra mondiale, conflitto, ribellione.
EVENTI = {'Q198': 'guerra', 'Q10931': 'rivoluzione', 'Q8465': 'guerra civile', 'Q103495': 'guerra mondiale',
          'Q180684': 'conflitto', 'Q124734': 'ribellione'}
FINESTRA = 3       # anni attorno alla nascita del movimento in cui un evento conta come contesto
MIN_ARTISTI = 5    # artisti associati necessari per dedurre la datazione
ETA = (25, 50)     # attivita' dedotta: dalla mediana delle nascite +25 alla +50
ORDINE_LUOGO = ['P740', 'P276', 'P17', 'P495']  # luogo di formazione, luogo, paese, paese d'origine


def q(u):
    return u.rsplit('/', 1)[-1] if isinstance(u, str) and u else None


def leggi(nome):
    return list(csv.DictReader(open(RAW / nome, encoding='utf-8')))


def anno(t):
    m = re.match(r'([+-]?\d+)-', t or '')
    return int(m.group(1)) if m else None


def intervallo(t, prec):
    """Anno di Wikidata con la sua precisione -> (da, a). 9 anno, 8 decennio, 7 secolo."""
    y, p = anno(t), int(prec or 9)
    if y is None:
        return None
    if p >= 9:
        return y, y
    if p == 8:
        return y - y % 10, y - y % 10 + 9
    if p == 7:  # Wikidata scrive il secolo come un anno dentro il secolo: si tengono entrambe le letture
        c = (y - 1) // 100 * 100 + 1 if y % 100 else y - 99
        return c, c + 99
    return y - 500, y + 499


def confini():
    anni = sorted(int(p.stem.split('_')[1]) for p in (ROOT / 'data/raw/confini').glob('world_*.geojson'))
    snap = {}
    for a in anni:
        fs = json.load(open(ROOT / f'data/raw/confini/world_{a}.geojson', encoding='utf-8'))['features']
        geo = [(shape(f['geometry']), (f['properties'] or {}).get('NAME')) for f in fs if f.get('geometry')]
        snap[a] = (STRtree([g for g, _ in geo]), geo)
    return anni, snap


def stato_allora(lon, lat, y, anni, snap):
    """Nome dello Stato nell'ultima istantanea non successiva all'anno: la stessa che la mappa disegna."""
    a = max([x for x in anni if x <= y] or [anni[0]])
    tree, geo = snap[a]
    p = Point(lon, lat)
    for i in tree.query(p):
        g, nome = geo[i]
        if nome and g.covers(p):
            return nome, a
    return None, a


def main():
    lab = {q(r['m']): r for r in leggi('lab.csv')}
    tipo = {k: TIPI.get(q(r['tipo'])) for k, r in lab.items()}

    # quando: dichiarato
    ini, fin = {}, {}
    for r in leggi('tempo.csv'):
        m, iv = q(r['m']), intervallo(r['t'], r['prec'])
        if not iv:
            continue
        d = ini if r['prop'] in ('P571', 'P580') else fin
        d.setdefault(m, []).append(iv)
    per = defaultdict(list)
    for r in leggi('per.csv'):
        a, b = anno(r['a']), anno(r['b'])
        if a is not None and b is not None:
            per[q(r['m'])].append((a, b))
    sl = {q(r['m']): int(r['sl'] or 0) for r in leggi('per.csv')}
    nasc = defaultdict(list)
    for r in leggi('art.csv'):
        if r['y']:
            nasc[q(r['m'])].append(int(float(r['y'])))

    # dove
    luoghi = {q(r['x']): r for r in leggi('luoghi.csv')}
    cont = defaultdict(set)
    for r in leggi('luoghi.csv'):
        if r['cont']:
            cont[q(r['x'])].add(CONTINENTI.get(q(r['cont']), q(r['cont'])))
    for c, nome in CONTINENTI.items():  # un continente usato come luogo e' continente di se stesso
        cont[c].add(nome)
    paesi_di = defaultdict(set)
    for r in leggi('luoghi.csv'):
        if r['paese']:
            paesi_di[q(r['x'])].add(q(r['paese']))
    dove = defaultdict(list)
    for r in leggi('dove.csv'):
        m = re.match(r'Point\(([-\d.]+) ([-\d.]+)\)', r['coord'] or '')
        if m:
            dove[q(r['m'])].append((r['prop'], q(r['x']), float(m.group(1)), float(m.group(2))))
    nomi = defaultdict(list)
    for r in leggi('nomi.csv'):
        a, b = anno(r['a']), anno(r['b'])
        if b is not None:  # solo i nomi che hanno smesso di valere: sono i nomi «di allora»
            nomi[q(r['x'])].append((a, b, r['nome'], r['lang']))

    # contesto: eventi
    ev = {}
    for r in leggi('ev.csv'):
        t = EVENTI.get(q(r['tipo']))
        a, b = anno(r['a']), anno(r['b']) or anno(r['a'])
        if t and a is not None:
            e = q(r['e'])
            ev[e] = dict(id=e, nome=r['it'] or r['en'], tipo=t, da=a, a=b, sl=int(r['sl']))
    ev_paesi = defaultdict(lambda: defaultdict(set))  # evento -> via -> paesi
    for r in leggi('evp.csv'):
        ev_paesi[q(r['e'])][r['via']].add(q(r['c']))
    nazioni = {q(r['paese']) for r in leggi('luoghi.csv') if r['paese']}
    capitale = {}  # per i paesi lo Stato di allora si cerca alla capitale: il baricentro di un paese grande cade lontano
    for r in leggi('capitali.csv'):
        m = re.match(r'Point\(([-\d.]+) ([-\d.]+)\)', r['coord'])
        if m:
            capitale.setdefault(q(r['x']), (float(m.group(1)), float(m.group(2))))

    # la regola di deduzione della data, misurata dove la data e' dichiarata
    scarti = []
    for m, ys in nasc.items():
        if len(ys) >= MIN_ARTISTI and m in ini:
            scarti.append(abs(statistics.median(ys) + ETA[0] - min(a for a, _ in ini[m])))
    regola = dict(n=len(scarti), mediana=statistics.median(scarti) if scarti else None,
                  entro20=sum(s <= 20 for s in scarti))

    anni, snap = confini()
    out, scarto = [], Counter()
    for m, r in lab.items():
        if not tipo.get(m):
            continue
        quando = None
        if m in ini:
            a = min(x for x, _ in ini[m])
            b = max(y for _, y in fin[m]) if m in fin else None
            quando = dict(da=a, a=b, metodo='dichiarato (Wikidata: inizio' + (', fine' if b else '') + ')')
        elif per[m]:
            quando = dict(da=min(a for a, _ in per[m]), a=max(b for _, b in per[m]), metodo='dichiarato come periodo (Wikidata P2348)')
        elif len(nasc[m]) >= MIN_ARTISTI:
            med = int(statistics.median(nasc[m]))
            quando = dict(da=med + ETA[0], a=med + ETA[1], metodo=f'dedotto da {len(nasc[m])} artisti associati: '
                          f'mediana delle nascite {med}, attività stimata +{ETA[0]}/+{ETA[1]} anni', dedotto=True)
        if not quando:
            scarto['senza data'] += 1
            continue
        if not dove[m]:
            scarto['senza luogo'] += 1
            continue
        y = quando['da']
        punti = sorted(dove[m], key=lambda d: ORDINE_LUOGO.index(d[0]))
        luoghi_out, visti = [], set()
        for prop, x, lon, lat in punti:
            if x in visti:
                continue
            visti.add(x)
            lr = luoghi.get(x, {})
            # precisione dalla natura del luogo, non dalla proprieta': paese, luogo dentro un paese, o regione/continente
            prec = 'paese' if x in nazioni else 'luogo' if paesi_di.get(x) and x not in CONTINENTI else 'regione'
            paese = prec == 'paese'
            cx, cy = capitale.get(x, (lon, lat)) if paese else (lon, lat)
            st, sa = stato_allora(cx, cy, y, anni, snap) if prec != 'regione' else (None, None)
            nome_allora = next((n for a, b, n, _ in nomi.get(x, []) if (a is None or a <= y) and y <= b), None)
            luoghi_out.append(dict(id=x, oggi=lr.get('it') or lr.get('en') or x, paese_oggi=lr.get('pl') or None,
                                   _en={lr.get('en'), lr.get('pe')} - {None, ''},
                                   precisione=prec, lon=lon, lat=lat,
                                   stato_allora=st, istantanea=sa, nome_allora=nome_allora if not paese else None))
        for l in luoghi_out:  # i confini storici danno nomi inglesi: il confronto si fa con i nomi inglesi di oggi
            en = l.pop('_en')
            l['diverso'] = bool(l['stato_allora']) and l['stato_allora'] not in en
        paesi = set()
        for l in luoghi_out:
            paesi |= {l['id']} | paesi_di.get(l['id'], set())
        def via(e):  # sul territorio del paese prima della partecipazione a guerre combattute altrove
            return 'territorio' if ev_paesi[e]['territorio'] & paesi else 'partecipante' if ev_paesi[e]['partecipante'] & paesi else None
        contesto = sorted(({**e, 'via': via(e['id'])} for e in ev.values()
                           if e['da'] <= y + FINESTRA and e['a'] >= y - FINESTRA and via(e['id'])),
                          key=lambda e: (e['via'] != 'territorio', -e['sl']))[:3]
        continenti = sorted({c for l in luoghi_out for c in cont.get(l['id'], ())})
        # corsia nel tempo: il continente del primo luogo; un paese su due continenti (Russia, Turchia) va in «Eurasia»
        c0 = cont.get(luoghi_out[0]['id'], set()) - {'Eurasia'}
        corsia = 'Eurasia' if {'Europa', 'Asia'} <= c0 or cont.get(luoghi_out[0]['id'], set()) == {'Eurasia'} else min(c0) if len(c0) == 1 else 'più continenti' if c0 else 'non determinato'
        out.append(dict(id=m, nome=r['it'] or r['en'], nome_en=r['en'] or None, tipo=tipo[m],
                        descr=r['dit'] or r['den'] or None, descr_lingua='it' if r['dit'] else 'en' if r['den'] else None,
                        quando=quando, luoghi=luoghi_out, continenti=continenti, corsia=corsia, sitelinks=sl.get(m, 0),
                        contesto=[{k: e[k] for k in ('id', 'nome', 'tipo', 'da', 'a', 'via')} for e in contesto]))
    out.sort(key=lambda x: -x['sitelinks'])
    json.dump({'elementi': out, 'regola_data': regola, 'finestra': FINESTRA}, open(ROOT / 'web/contesti.json', 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    metriche(lab, tipo, out, scarto, regola)


def metriche(lab, tipo, out, scarto, regola):
    tot = sum(1 for m in lab if tipo.get(m))
    ded = sum(1 for x in out if x['quando'].get('dedotto'))
    perc = Counter(c for x in out for c in (x['continenti'] or ['non determinato']))
    secoli = Counter(x['quando']['da'] // 100 * 100 for x in out)
    allora = sum(1 for x in out if any(l['stato_allora'] for l in x['luoghi']))
    diverso = sum(1 for x in out if any(l['diverso'] for l in x['luoghi']))
    nomi = sum(1 for x in out if any(l['nome_allora'] for l in x['luoghi']))
    ctx = sum(1 for x in out if x['contesto'])
    ctx_t = sum(1 for x in out if any(c['via'] == 'territorio' for c in x['contesto']))
    prec = Counter(l['precisione'] for x in out for l in x['luoghi'])
    righe = ['# Livello «Contesti»: stili e movimenti', '',
             'Rigenerato da `src/contesti.py`. Fonte: Wikidata (CC0), voci con istanza «movimento artistico» (Q968159) o «stile artistico» (Q1792644).', '',
             f'- Voci su Wikidata: **{tot}**. Collocate nello spazio e nel tempo: **{len(out)}** ({round(100 * len(out) / tot)}%). '
             f'Escluse: senza data {scarto["senza data"]}, con data ma senza luogo {scarto["senza luogo"]}.',
             f'- Datazione dedotta dagli artisti associati: {ded}. Regola misurata su {regola["n"]} voci con data dichiarata: '
             f'scarto mediano {regola["mediana"]} anni, entro 20 anni in {regola["entro20"]} casi.',
             f'- Stato di allora dai confini storici: {allora}; diverso dal nome di oggi in {diverso}. Nome storico del luogo (Wikidata P1448 con data di fine): {nomi}.',
             f'- Luoghi per precisione: ' + ', '.join(f'{k} {v}' for k, v in prec.most_common()) + '. Alle regioni e ai continenti non si assegna uno Stato.',
             f'- Con almeno una guerra o rivoluzione entro ±{FINESTRA} anni dalla nascita: {ctx}; combattuta sul territorio del paese: {ctx_t} '
             '(le altre sono guerre a cui il paese partecipa altrove). Eventi da Wikidata con almeno 20 versioni linguistiche.', '',
             '## Per continente (una voce può stare in più continenti)', '', '| continente | voci |', '| --- | ---: |']
    righe += [f'| {c} | {n} |' for c, n in perc.most_common()]
    righe += ['', '## Per secolo d\'inizio', '', '| secolo | voci |', '| --- | ---: |']
    righe += [f'| {s} | {n} |' for s, n in sorted(secoli.items())]
    (ROOT / 'out/contesti.md').write_text('\n'.join(righe) + '\n', encoding='utf-8')
    print('\n'.join(righe))


if __name__ == '__main__':
    main()
