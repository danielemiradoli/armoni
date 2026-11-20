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
          ('Warsaw', r'warsaw'), ('Philadelphia', r'philadelphia'), ('Mexico City', r'mexico city')]
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
         ('United States', r'american|united states')]
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
             f'Pezzi: **{n}** — Met {sum(o["fonte"] == "met" for o in opere)}, Cleveland {sum(o["fonte"] == "cma" for o in opere)}.', '',
             '## Inclusione', '', '| grado | pezzi |', '| --- | ---: |']
    righe += [f'| {g} | {pct(k)} |' for g, k in Counter(o['grado'] for o in opere).most_common()]
    righe += ['', '## Precisione del luogo d\'origine', '', '| precisione | pezzi |', '| --- | ---: |']
    righe += [f'| {p} | {pct(k)} |' for p, k in prec.most_common()]
    righe += ['', f'Attribuzione del luogo dichiarata incerta dal catalogo: {pct(sum(o["origine_incerta"] for o in opere))}.']
    righe += ['', '## Origine (prime 15)', '', '| luogo | pezzi |', '| --- | ---: |']
    righe += [f'| {luoghi[o]["nome"] if o else "—"} | {k} |' for o, k in Counter(o['origine'] for o in opere).most_common(15)]
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
