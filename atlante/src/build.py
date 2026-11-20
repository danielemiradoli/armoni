"""Costruisce i dati dell'atlante per il primo taglio: il filo del blu e bianco.

Ingressi: data/raw/MetObjects.csv, data/raw/cma_data.csv (vedi MANIFEST.md),
data/luoghi.csv, data/periodi.csv.
Uscite: web/opere.json, web/luoghi.json, web/periodi.json, out/metrics.md.

Ogni pezzo e' un'asserzione: non un verdetto. Porta il criterio con cui e' entrato,
la precisione del luogo, la fonte e la licenza del record.
"""
import csv, json, re, sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
csv.field_size_limit(sys.maxsize)

# \bTiles?\b e non 'Tile': la sottostringa prendeva anche 'Textiles' (11 tessili entrati in silenzio).
CERAMICA_MET = r'Ceramic|Porcelain|Pottery|\bTiles?\b|Earthenware|Faience'
# Il catalogo stesso dichiara l'attribuzione incerta: lo si conserva, non lo si risolve.
INCERTO = re.compile(r'possibl|probabl|\?|\bor\b|attributed', re.I)
MEDIUM_CER = r'stonepaste|faience|earthenware|porcelain|fritware|tin-glaze|tin glaze|stoneware'
# Blu dichiarato nel testo del record: e' l'unica prova che il pezzo sia blu e bianco.
BLU = re.compile(r'underglaze[- ](?:cobalt[- ])?blue|cobalt|blue[- ]and[- ]white|blue and white|painted in blue|blue on white', re.I)
# Manifatture associate al blu e bianco: senza blu nel testo l'inclusione resta un'ipotesi.
FAMIGLIE = [('Kraak', r'kraak'), ('Iznik', r'iznik'), ('Kütahya', r'k[uü]tahya'), ('Kubachi', r'kubachi'),
            ('Delft', r'delft'),
            # 'puebla' da solo prendeva ceramiche precolombiane della regione di Puebla (anno 900)
            ('Talavera / Puebla', r'talavera|puebla.*(?:tin[- ]glaz|majolica|maiolica)|(?:tin[- ]glaz|majolica|maiolica).*puebla')]

# Centri di produzione: l'ordine conta (Puebla prima di Talavera, Chelsea prima di London).
CENTRI = [('Jingdezhen', r'jingdezhen'), ('İznik', r'iznik'), ('Kütahya', r'k[uü]tahya'), ('Delft', r'delft'),
          ('Arita', r'arita|hizen'), ('Hirado', r'hirado'), ('Seto', r'\bseto\b'), ('Kyoto', r'kyoto'),
          ('Puebla City', r'puebla'), ('Talavera de la Reina', r'talavera'), ('Zhangzhou', r'zhangzhou|swatow'),
          ('Hải Dương', r'h[aả]i d[uư][oơ]ng'), ('Hội An', r'h[oộ]i an\b'), ('Gwangju', r'gwangju'),
          ('Kashan', r'kashan'), ('Mashhad', r'mashhad'), ('Kerman', r'kirman|kerman'), ('Tabriz', r'tabriz'),
          ('Isfahan', r'isfahan'), ('Nishapur', r'nishapur'), ('Samarkand', r'samarqand|samarkand'),
          ('Damascus', r'damascus'), ('Cairo', r'cairo|fustat'), ('Worcester', r'worcester'),
          ('Lowestoft', r'lowestoft'), ('Chelsea', r'chelsea'), ('Bow', r'\bbow\b'), ('Derby', r'\bderby\b'),
          ('Bristol', r'bristol'), ('Liverpool', r'liverpool'), ('Staffordshire', r'staffordshire'),
          ('London', r'london|lambeth|southwark'), ('Saint-Cloud', r'saint-cloud'), ('Chantilly', r'chantilly'),
          ('Rouen', r'rouen'), ('Nevers', r'nevers'), ('Paris', r'\bparis\b'), ('Meissen', r'meissen'),
          ('Hanau', r'hanau'), ('Frankfurt', r'frankfurt'), ('Florence', r'florence|medici'),
          ('Venice', r'venice|venetian'), ('Lisbon', r'lisbon'), ('Seville', r'seville'), ('Antwerp', r'antwerp'),
          ('Warsaw', r'warsaw'), ('Philadelphia', r'philadelphia'), ('Mexico City', r'mexico city'),
          # aggiunti per il V&A (luoghi_vam.rq); Hyderabad resta non risolto: Sindh o India
          ('Caughley', r'caughley'), ('Etruria', r'etruria'), ('Barlaston', r'barlaston'), ('Burslem', r'burslem'),
          ('Hanley', r'hanley'), ('Stoke-on-Trent', r'stoke-on-trent'), ('Shropshire', r'shropshire'),
          ('Forlì', r'forl[iì]'), ('Sesto Fiorentino', r'doccia'), ('Naples', r'naples|capo ?di ?monte'),
          ('Tournai', r'tournai'), ('Sèvres', r's[eè]vres'), ('Copenhagen', r'copenhagen'), ('Plymouth', r'plymouth'),
          ('Vauxhall', r'vauxhall'), ('Glasgow', r'glasgow'), ('Leeds', r'\bleeds\b'), ('Kolkata', r'kolkata|calcutta'),
          ('Fez', r'\bfe[sz]\b'), ('Nagasaki', r'nagasaki'), ('Yokohama', r'yokohama'),
          ('Hong Kong', r'hong kong'), ('Dehua County', r'dehua'), ('Fujian', r'fujian'), ('Gansu', r'gansu'),
          ('Sindh', r'sindh')]
PAESI = [('China', r'chin'), ('Japan', r'japan'), ('Vietnam', r'vietnam'), ('Korea', r'korea'),
         ('Iran', r'iran|persia'), ('Turkey', r'turk|ottoman|anatolia'), ('Netherlands', r'dutch|netherland'),
         ('Mexico', r'mexic'), ('Egypt', r'egypt'), ('Syria', r'syria'), ('Portugal', r'portug'),
         ('Spain', r'spain|spanish'), ('England', r'british|english|england'), ('France', r'french|france'),
         ('Germany', r'german'), ('Italy', r'ital'), ('Iraq', r'iraq'), ('Uzbekistan', r'uzbek'),
         ('India', r'india'), ('Thailand', r'thai'), ('Poland', r'polish|poland'), ('Austria', r'austria|vienna'),
         ('Belgium', r'belgi|flemish'), ('Denmark', r'danish|denmark'), ('Russia', r'russia'),
         ('Sweden', r'swed'), ('Switzerland', r'swiss'), ('Hungary', r'hungar'),
         ('Czech Republic', r'bohemia|czech'), ('Scotland', r'scot'), ('Ireland', r'irish|ireland'),
         ('Wales', r'welsh|wales'), ('Afghanistan', r'afghan'), ('Morocco', r'morocc'), ('Tunisia', r'tunisia'),
         ('Myanmar', r'burm|myanmar'), ('Indonesia', r'indonesia|java'), ('Philippines', r'philippin'),
         ('United States', r'american|united states|\busa\b'), ('United Kingdom', r'great britain|\bbritain\b|united kingdom'),
         ('Norway', r'norw'), ('Azerbaijan', r'azerbaijan'), ('Nigeria', r'nigeria'), ('Central Asia', r'central asia')]
MERCATI = [('Portugal', r'portug'), ('Netherlands', r'dutch'), ('Japan', r'japan'), ('England', r'english|british'),
           ('United States', r'american'), ('Iran', r'persian|iran'), ('Turkey', r'ottoman|turkish'),
           ('Europe', r'europ')]
SEDI = {'met': 'Metropolitan Museum of Art', 'cma': 'Cleveland Museum of Art'}


def anno(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def trova(tabella, testo):
    for luogo, pat in tabella:
        if re.search(pat, testo, re.I):
            return luogo
    return None


def origine(testo_centro, testo_paese):
    c = trova(CENTRI, testo_centro)
    if c:
        return c
    return trova(PAESI, testo_paese)


def mercato(cultura):
    m = re.search(r'for (?:the )?([^,;()]*?)\bmarket', cultura, re.I)
    if not m:
        return None, ('export' in cultura.lower())
    return trova(MERCATI, m.group(1)), False


def inclusione(testo_blu, testo_famiglia):
    if BLU.search(testo_blu):
        return 'documentato', 'blu dichiarato nel record: «%s»' % BLU.search(testo_blu).group(0)
    fam = trova(FAMIGLIE, testo_famiglia)
    if fam:
        return 'ipotetico', 'manifattura %s; il record non nomina il blu' % fam
    return None, None


def da_met(path):
    m = pd.read_csv(path, dtype=str, low_memory=False).fillna('')
    cer = m[m['Classification'].str.contains(CERAMICA_MET, case=False) | m['Medium'].str.contains(MEDIUM_CER, case=False)]
    cer.columns = [c.replace(' ', '_') for c in cer.columns]
    for r in cer.itertuples(index=False):
        d = r._asdict()
        cult = d['Culture']
        grado, crit = inclusione(' | '.join([d['Medium'], d['Title'], d['Object_Name']]),
                                 ' | '.join([d['Title'], d['Object_Name'], cult, d['Medium'], d['Period'], d['City'], d['Tags']]))
        if not grado:
            continue
        yield dict(id='met:' + d['Object_ID'], fonte='met', titolo=d['Title'] or d['Object_Name'],
                   cultura=cult, data_testo=d['Object_Date'], inizio=anno(d['Object_Begin_Date']),
                   fine=anno(d['Object_End_Date']), tecnica=d['Medium'],
                   testo_centro=' | '.join([d['City'], d['State'], d['Region'], cult, d['Title'], d['Period']]),
                   testo_paese=' | '.join([d['Country'], cult.split(',')[0], d['Period'], d['Dynasty']]),
                   grado=grado, criterio=crit, url=d['Link_Resource'],
                   licenza='CC0' if d['Is_Public_Domain'] == 'True' else 'metadati CC0; immagine non di pubblico dominio',
                   wikidata=d['Object_Wikidata_URL'].rsplit('/', 1)[-1] if d['Object_Wikidata_URL'] else '')


def da_cma(path):
    c = pd.read_csv(path, dtype=str, low_memory=False).fillna('')
    cer = c[c['type'].str.contains('Ceramic', case=False)]
    for r in cer.itertuples(index=False):
        d = r._asdict()
        cult = d['culture']
        grado, crit = inclusione(' | '.join([d['technique'], d['title'], d['description']]),
                                 ' | '.join([d['title'], cult, d['technique'], d['description']]))
        if not grado:
            continue
        yield dict(id='cma:' + d['id'], fonte='cma', titolo=d['title'], cultura=cult,
                   data_testo=d['creation_date'], inizio=anno(d['creation_date_earliest']),
                   fine=anno(d['creation_date_latest']), tecnica=d['technique'],
                   testo_centro=' | '.join([cult, d['title']]), testo_paese=cult.split(',')[0],
                   grado=grado, criterio=crit, url=d['url'],
                   licenza='CC0' if d['share_license_status'] == 'CC0' else 'diritti: ' + (d['share_license_status'] or 'non dichiarati'),
                   wikidata='')


# Wikidata: blu dichiarato in etichette o descrizioni (pt, en, ja, zh, fr, ...).
# Niente 'cobalt' nudo e niente 'azul' dentro 'azulejo': 'cobalt blue glaze' e 'sky blue glaze' sono monocromi.
BLU_WD = re.compile(r'underglazed?[- ](?:cobalt[- ]?)?blue|underglaze cobalt|blue[- ]and[- ]white|blue and white|'
                    r'azul[- ]e[- ]branco|azul[- ]cobalto|\bazul\b|bleu de cobalt|bleu et blanc|染付|青花|sometsuke|qinghua', re.I)
FAMIGLIE_WD = FAMIGLIE + [('azulejo', r'azulejo')]
PRC = 'Q148'  # Repubblica Popolare Cinese, fondata nel 1949


def intervallo_wd(data, prec, a, b):
    """Intervallo da P571. Con precisione 'secolo' l'anno registrato e' ambiguo (1800 = XVIII o XIX?):
    si tengono entrambe le letture invece di sceglierne una."""
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


def da_wd(path, luoghi):
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
    d = pd.read_csv(path, dtype=str).fillna('')
    for w, g in d.groupby('w', sort=False):
        uniq = lambda c: sorted(set(x for x in g[c] if x))
        testo = ' | '.join(uniq('lab') + uniq('desc'))
        if re.search(r'monochrome|sky blue glaze|cobalt blue glaze|blue[- ]glazed|霽青|天青', testo, re.I) and not re.search(r'underglaze|染付|青花', testo):
            continue
        m = BLU_WD.search(testo)
        if m:
            grado, crit = 'documentato', 'blu dichiarato su Wikidata: «%s»' % m.group(0)
        else:
            fam = trova(FAMIGLIE_WD, testo)
            if not fam:
                continue
            grado, crit = 'ipotetico', 'genere o manifattura %s; Wikidata non nomina il blu' % fam
        r = g.iloc[0]
        ini, fin, prec = intervallo_wd(r['data'], r['prec'], r['inizio'], r['fine'])
        crea = luogo(q(r['crea']), r['creaLab'], r['creaCoord'], 'citta', 'P1071 su Wikidata')
        orig = crea or luogo(q(r['orig']), r['origLab'], r['origCoord'], 'paese', 'P495 su Wikidata')
        sede = luogo(q(r['col']), r['colLab'], next((c for c in g['colCoord'] if c), ''), 'istituzione',
                     'P625 della collezione o della sua sede')
        titoli = uniq('lab')
        yield dict(id='wd:' + q(w), fonte='wd', titolo=next((t for t in titoli if re.match(r'[A-Za-zÀ-ÿ]', t)), titoli[0] if titoli else q(w)),
                   cultura=' | '.join(titoli[1:3]), data_testo=(r['data'][:4].lstrip('+') + f' ({prec})') if prec else '',
                   inizio=ini, fine=fin, tecnica=' | '.join(uniq('desc'))[:300], grado=grado, criterio=crit,
                   url=w, licenza='CC0 (Wikidata)', wikidata=q(w), origine=orig, origine_incerta=False,
                   origine_anacronistica=q(r['orig']) == PRC and fin is not None and fin < 1949,
                   sede=sede, mercato=None, export_senza_meta=False)


def main():
    luoghi = {r['id']: r for r in csv.DictReader(open(ROOT / 'data/luoghi.csv', encoding='utf-8'))}
    opere, scarti = [], Counter()
    for rec in list(da_met(ROOT / 'data/raw/MetObjects.csv')) + list(da_cma(ROOT / 'data/raw/cma_data.csv')):
        o = origine(rec.pop('testo_centro'), rec.pop('testo_paese'))
        if rec['inizio'] is None or rec['fine'] is None or rec['inizio'] > rec['fine']:
            scarti['date assenti o invertite'] += 1
            rec['inizio'] = rec['fine'] = None
        mk, export = mercato(rec['cultura'])
        rec.update(origine=o, origine_incerta=bool(INCERTO.search(rec['cultura'])), sede=SEDI[rec['fonte']],
                   mercato=mk, export_senza_meta=export)
        opere.append(rec)
    for rec in da_wd(ROOT / 'data/raw/wikidata_ceramiche.csv', luoghi):
        if rec['inizio'] is None or rec['fine'] is None or rec['inizio'] > rec['fine']:
            scarti['date assenti o invertite'] += 1
            rec['inizio'] = rec['fine'] = None
        opere.append(rec)

    web = ROOT / 'web'
    with open(web / 'opere.json', 'w', encoding='utf-8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(o, ensure_ascii=False) for o in opere) + '\n]\n')
    usati = {o['origine'] for o in opere} | {o['sede'] for o in opere} | {o['mercato'] for o in opere}
    json.dump([luoghi[k] for k in sorted(x for x in usati if x)], open(web / 'luoghi.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    json.dump(list(csv.DictReader(open(ROOT / 'data/periodi.csv', encoding='utf-8'))),
              open(web / 'periodi.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    scrivi_metriche(opere, luoghi, scarti)


def scrivi_metriche(opere, luoghi, scarti):
    n = len(opere)
    pct = lambda k: f'{k} ({100 * k / n:.1f}%)'
    prec = Counter(luoghi[o['origine']]['precisione'] if o['origine'] else 'nessun luogo' for o in opere)
    righe = ['# Metriche dell\'atlante — taglio «blu e bianco»', '',
             'Rigenerato da `src/build.py`. Ogni cifra si ricalcola dai file in `data/`.', '',
             f'Pezzi: **{n}** — Met {sum(o["fonte"] == "met" for o in opere)}, Cleveland {sum(o["fonte"] == "cma" for o in opere)}, '
             f'Wikidata fuori dagli Stati Uniti {sum(o["fonte"] == "wd" for o in opere)}.', '',
             '## Inclusione', '', '| grado | pezzi |', '| --- | ---: |']
    righe += [f'| {g} | {pct(k)} |' for g, k in Counter(o['grado'] for o in opere).most_common()]
    righe += ['', '## Precisione del luogo d\'origine', '', '| precisione | pezzi |', '| --- | ---: |']
    righe += [f'| {p} | {pct(k)} |' for p, k in prec.most_common()]
    righe += ['', f'Attribuzione del luogo dichiarata incerta dal catalogo: {pct(sum(o["origine_incerta"] for o in opere))}.']
    righe += ['', '## Origine (prime 15)', '', '| luogo | pezzi |', '| --- | ---: |']
    righe += [f'| {luoghi[o]["nome"] if o else "—"} | {k} |' for o, k in Counter(o['origine'] for o in opere).most_common(15)]
    sedi = Counter(luoghi[o['sede']]['nome'] if o['sede'] else 'sede senza coordinate' for o in opere)
    righe += ['', '## Dove sono conservati', '', '| sede | pezzi |', '| --- | ---: |']
    righe += [f'| {k} | {v} |' for k, v in sedi.most_common(12)]
    righe += ['', f'Origine Wikidata = Repubblica Popolare Cinese per oggetti anteriori al 1949: '
              f'{sum(o.get("origine_anacronistica", False) for o in opere)}.']
    righe += ['', '## Mercati di destinazione dichiarati nel catalogo', '',
              f'Con mercato riconosciuto: {sum(1 for o in opere if o["mercato"])}. '
              f'«Export» senza destinazione: {sum(o["export_senza_meta"] for o in opere)}.', '']
    righe += ['## Date', '', f'Senza intervallo utilizzabile: {scarti["date assenti o invertite"]}.', '',
              '## Licenze', '', '| licenza | pezzi |', '| --- | ---: |']
    righe += [f'| {l} | {k} |' for l, k in Counter(o['licenza'] for o in opere).most_common()]
    (ROOT / 'out/metrics.md').write_text('\n'.join(righe) + '\n', encoding='utf-8')
    print('\n'.join(righe))


if __name__ == '__main__':
    main()
