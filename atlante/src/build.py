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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tipi  # noqa: E402

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
# \b iniziale: senza, 'iran' prendeva 'Hirano', 'ital' 'capital', 'india' 'Indiana'
PAESI = [('China', r'\b(?:chin)'), ('Japan', r'\b(?:japan)'), ('Vietnam', r'\b(?:vietnam)'), ('Korea', r'\b(?:korea)'),
         ('Iran', r'\b(?:iran|persia)'), ('Turkey', r'\b(?:turk|ottoman|anatolia)'), ('Netherlands', r'\b(?:dutch|netherland)'),
         ('Mexico', r'\b(?:mexic)'), ('Egypt', r'\b(?:egypt)'), ('Syria', r'\b(?:syria)'), ('Portugal', r'\b(?:portug)'),
         ('Spain', r'\b(?:spain|spanish)'), ('England', r'\b(?:british|english|england)'), ('France', r'\b(?:french|france)'),
         ('Germany', r'\b(?:german)'), ('Italy', r'\b(?:ital)'), ('Iraq', r'\b(?:iraq)'), ('Uzbekistan', r'\b(?:uzbek)'),
         ('India', r'\b(?:india)'), ('Thailand', r'\b(?:thai)'), ('Poland', r'\b(?:polish|poland)'), ('Austria', r'\b(?:austria|vienna)'),
         ('Belgium', r'\b(?:belgi|flemish)'), ('Denmark', r'\b(?:danish|denmark)'), ('Russia', r'\b(?:russia)'),
         ('Sweden', r'\b(?:swed)'), ('Switzerland', r'\b(?:swiss)'), ('Hungary', r'\b(?:hungar)'),
         ('Czech Republic', r'\b(?:bohemia|czech)'), ('Scotland', r'\b(?:scot)'), ('Ireland', r'\b(?:irish|ireland)'),
         ('Wales', r'\b(?:welsh|wales)'), ('Afghanistan', r'\b(?:afghan)'), ('Morocco', r'\b(?:morocc)'), ('Tunisia', r'\b(?:tunisia)'),
         ('Myanmar', r'\b(?:burm|myanmar)'), ('Indonesia', r'\b(?:indonesia|java)'), ('Philippines', r'\b(?:philippin)'),
         ('United States', r'\b(?:american|united states|usa)'), ('United Kingdom', r'\b(?:great britain|britain|united kingdom)'),
         ('Norway', r'\b(?:norw)'), ('Azerbaijan', r'\b(?:azerbaijan)'), ('Nigeria', r'\b(?:nigeria)'), ('Central Asia', r'\b(?:central asia)')]
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


# ColBase (Japan Search, CC BY): forno e paese nei contributori, epoca e secolo nel campo temporale.
CENTRI_JA = [('Jingdezhen', r'景徳鎮'), ('Arita', r'有田|肥前'), ('Zhangzhou', r'漳州'), ('Kyoto', r'京都|京焼'),
             ('Seto', r'瀬戸'), ('Hirado', r'平戸|三川内'), ('Nagasaki', r'長崎')]
PAESI_JA = [('China', r'中国'), ('Korea', r'朝鮮|韓国'), ('Vietnam', r'ベトナム|安南'), ('Iran', r'イラン|ペルシア'),
            ('Netherlands', r'オランダ'), ('Turkey', r'トルコ'), ('Thailand', r'タイ'), ('Japan', r'日本')]
SEDI_CB = {'tnm': 'Tokyo National Museum', 'kyohaku': 'Kyoto National Museum', 'narahaku': 'Nara National Museum',
           'kyuhaku': 'Kyushu National Museum'}
def sede_cb(p):
    # il campo provider usa a volte il codice ('tnm'), a volte il nome del museo
    if p in SEDI_CB: return SEDI_CB[p]
    if re.search(r'京都国立|Kyoto National', p): return 'Kyoto National Museum'
    if re.search(r'九州国立|Kyushu National', p): return 'Kyushu National Museum'
    if re.search(r'奈良国立', p): return 'Nara National Museum'
    if re.search(r'東京国立', p): return 'Tokyo National Museum'
    return None


# Luogo dedotto, mai dichiarato: al Museo nazionale di Tokyo la categoria 陶磁 separa la ceramica
# giapponese da quella asiatica (東洋陶磁). Misurata sui pezzi 陶磁 di Tokyo con luogo noto: 43 giapponesi
# su 49 (88%); il campione sovrarappresenta i pezzi stranieri, che sono quelli che dichiarano il luogo.
# A Kyoto e al Kyushu la categoria 陶磁 comprende anche la Cina: li' non si deduce nulla.
CRITERIO_DEDOTTO = ('dedotto dalla categoria 陶磁 del Museo nazionale di Tokyo (ceramica giapponese); '
                    'regola misurata: 43 giapponesi su 49 pezzi con luogo noto, 88%')


def dedotto(o, c, it):
    if o or sede_cb(c.get('provider', '')) != 'Tokyo National Museum' or it.get('cobas-4-s') != '陶磁':
        return {}
    return {'origine_dedotta': 'Japan', 'criterio_luogo': CRITERIO_DEDOTTO}


# 明治 prima di 明: '明治時代' contiene il carattere della dinastia Ming
EPOCHE = [('Periodo Meiji', r'明治|meiji'), ('Periodo Taishō', r'大正|taish'), ('Periodo Shōwa', r'昭和|sh[oō]wa'),
          ('Dinastia Ming', r'明|ming'), ('Dinastia Qing', r'清|qing'), ('Dinastia Yuan', r'元時代|yuan'),
          ('Periodo Edo', r'江戸|edo'), ('Periodo Muromachi', r'室町|muromachi'), ('Joseon', r'朝鮮時代|joseon')]


def intervallo_cb(testi, periodi):
    """Anni espliciti > secolo (con meta') > epoca; secolo ed epoca si intersecano se si sovrappongono."""
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


def da_colbase(path):
    periodi = {r['nome']: (int(r['inizio']), int(r['fine'])) for r in csv.DictReader(open(ROOT / 'data/periodi.csv', encoding='utf-8'))}
    for it in json.load(open(path, encoding='utf-8')):
        c = it['common']
        if it.get('cobas-4-s') not in ('陶磁', '東洋陶磁'):
            continue
        titolo = c.get('title', '') + ' ' + c.get('titleEn', '')
        if re.search(r'染付|青花|underglaze[- ]blue|blue[- ]and[- ]white', titolo, re.I):
            grado, crit = 'documentato', 'blu nel titolo ColBase: «%s»' % re.search(r'染付|青花|underglaze[- ]blue|blue[- ]and[- ]white', titolo, re.I).group(0)
        else:
            grado, crit = 'ipotetico', '%s solo nella descrizione o nel marchio: il pezzo puo\' essere policromo' % '/'.join(it['parole'])
        # i contributori includono il museo che conserva e i donatori: non sono luoghi d'origine
        contrib = ' | '.join(x for x in c.get('contributor', []) if not re.search(r'博物館|museum|寄贈|gift|財団|foundation|研究所', x, re.I))
        testo = contrib + ' | ' + titolo
        o = trova(CENTRI_JA, testo) or trova(CENTRI, testo) or trova(PAESI_JA, contrib) or trova(PAESI, contrib)
        tempi = c.get('temporal', []) + [it.get('cobas-11-s', '')]
        ini, fin, prec = intervallo_cb(tempi, periodi)
        yield dict(id=c['id'], fonte='colbase', titolo=c.get('titleEn') or c.get('title', ''), cultura=contrib[:160],
                   data_testo=' / '.join(x for x in c.get('temporal', []) if x) + (f' ({prec})' if prec else ''),
                   inizio=ini, fine=fin, tecnica=(c.get('title', '') + ' · ' + it.get('cobas-12-s', '')).strip(' ·'),
                   grado=grado, criterio=crit, url=c.get('linkUrl', ''),
                   licenza='CC BY — fonte: ColBase (国立文化財機構所蔵品統合検索システム)', wikidata='',
                   origine=o, origine_incerta=bool(re.search(r'伝|推定|attributed|\?', contrib)),
                   sede=sede_cb(c.get('provider', '')), mercato=None, export_senza_meta=False,
                   **dedotto(o, c, it))


# eMuseum (musei pubblici coreani): si tengono solo le schede con licenza KOGL tipo 1, ceramiche, e il blu
# dichiarato nel nome (청화 = bianco e blu). Le fotografie su lastra di vetro (유리건판) ritraggono i pezzi: escluse.
NAZIONI_KO = {'한국': 'Korea', '중국': 'China', '일본': 'Japan', '베트남': 'Vietnam', '아시아': None}
EPOCHE_KO = {'고려': (918, 1392), '조선': (1392, 1897), '대한제국': (1897, 1910), '일제강점': (1910, 1945),
             '광복이후': (1945, 2000), '명': (1368, 1644), '청': (1636, 1912), '원': (1271, 1368)}


ESCLUSI_EMU = Counter()


def da_emuseum(cartella):
    if not (cartella / 'dettagli.jsonl').exists():
        return
    elenco = {json.loads(l)['id']: json.loads(l) for l in open(cartella / 'elenco.jsonl', encoding='utf-8')}
    conta = Counter()
    for l in open(cartella / 'dettagli.jsonl', encoding='utf-8'):
        d = json.loads(l); c = d['campi']; e = elenco.get(d['id'], {})
        if d['licenza_kogl'] != 1:
            conta['licenza diversa dal tipo 1'] += 1; continue
        if '유리건판' in c.get('분류', '') + c.get('재질', '') + e.get('numero', ''):
            conta['fotografia su lastra'] += 1; continue
        nome = c.get('명칭') or e.get('titolo', '')
        if '청화' not in nome:
            conta['blu non nel nome'] += 1; continue
        naz, _, epoca = c.get('국적/시대', '').partition(' - ')
        ini, fin = EPOCHE_KO.get(epoca.strip(), (None, None))
        crit = 'blu dichiarato nel nome: «청화» (bianco e blu)'
        tf = c.get('특징', '')
        m = re.search(r'(\d{4})년', tf) or None
        sec = re.search(r'(\d{1,2})세기', tf)
        if m and 1000 < int(m.group(1)) < 2000:
            ini = fin = int(m.group(1)); crit += f'; anno dichiarato nella descrizione ({m.group(1)}년)'
        elif sec:
            n = int(sec.group(1)); ini, fin = (n - 1) * 100, n * 100 - 1; crit += f'; secolo dichiarato nella descrizione ({n}세기)'
        museo = d.get('museo') or e.get('museo') or ''
        conta['tenute'] += 1
        yield dict(id='emu:' + d['id'], fonte='emuseum', titolo=nome, cultura=c.get('국적/시대', ''),
                   data_testo=c.get('국적/시대', ''), inizio=ini, fine=fin,
                   tecnica=' · '.join(x for x in (c.get('재질'), c.get('분류')) if x),
                   grado='documentato', criterio=crit,
                   url='https://www.emuseum.go.kr/detail?relicId=' + d['id'],
                   licenza=f'KOGL tipo 1 — fonte: {museo or "e뮤지엄"}, eMuseum (emuseum.go.kr)', wikidata='',
                   origine=NAZIONI_KO.get(naz.strip()) or NAZIONI_KO.get(epoca.strip()), origine_incerta=False,
                   sede='National Museum of Korea' if museo == '국립중앙박물관' else 'Korea',
                   mercato=None, export_senza_meta=False, museo=museo)
    print('eMuseum:', dict(conta)); ESCLUSI_EMU.update(conta)


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
    for rec in list(da_wd(ROOT / 'data/raw/wikidata_ceramiche.csv', luoghi)) + list(da_colbase(ROOT / 'data/raw/colbase.json')) + list(da_emuseum(ROOT / 'data/raw/emuseum')):
        if rec['inizio'] is None or rec['fine'] is None or rec['inizio'] > rec['fine']:
            scarti['date assenti o invertite'] += 1
            rec['inizio'] = rec['fine'] = None
        opere.append(rec)

    for rec in opere:  # tipo di oggetto: lettura per parole chiave del nome (src/tipi.py), non dato della fonte
        rec['tipo'], rec['tipo_parola'] = tipi.tipo(rec['titolo'], rec.get('classe'))
    web = ROOT / 'web'
    with open(web / 'opere.json', 'w', encoding='utf-8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(o, ensure_ascii=False) for o in opere) + '\n]\n')
    usati = {o['origine'] for o in opere} | {o['sede'] for o in opere} | {o['mercato'] for o in opere}
    json.dump([luoghi[k] for k in sorted(x for x in usati if x)], open(web / 'luoghi.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    json.dump(list(csv.DictReader(open(ROOT / 'data/periodi.csv', encoding='utf-8'))),
              open(web / 'periodi.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    import copertura; copertura.scrivi(ROOT / 'web', opere, ESCLUSI_EMU)
    scrivi_metriche(opere, luoghi, scarti)


def scrivi_metriche(opere, luoghi, scarti):
    n = len(opere)
    pct = lambda k: f'{k} ({100 * k / n:.1f}%)'
    prec = Counter(luoghi[o['origine']]['precisione'] if o['origine'] else 'nessun luogo' for o in opere)
    righe = ['# Metriche dell\'atlante — taglio «blu e bianco»', '',
             'Rigenerato da `src/build.py`. Ogni cifra si ricalcola dai file in `data/`.', '',
             f'Pezzi: **{n}** — Met {sum(o["fonte"] == "met" for o in opere)}, Cleveland {sum(o["fonte"] == "cma" for o in opere)}, '
             f'Wikidata fuori dagli Stati Uniti {sum(o["fonte"] == "wd" for o in opere)}, '
             f'ColBase {sum(o["fonte"] == "colbase" for o in opere)}, eMuseum {sum(o["fonte"] == "emuseum" for o in opere)}.', '',
             '## Inclusione', '', '| grado | pezzi |', '| --- | ---: |']
    righe += [f'| {g} | {pct(k)} |' for g, k in Counter(o['grado'] for o in opere).most_common()]
    righe += ['', '## Precisione del luogo d\'origine', '', '| precisione | pezzi |', '| --- | ---: |']
    righe += [f'| {p} | {pct(k)} |' for p, k in prec.most_common()]
    righe += ['', f'Attribuzione del luogo dichiarata incerta dal catalogo: {pct(sum(o["origine_incerta"] for o in opere))}.']
    righe += ['', f'Senza luogo dichiarato ma con luogo dedotto (Giappone, ColBase/Tokyo, strato separato): {sum(1 for o in opere if o.get("origine_dedotta"))}.']
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
