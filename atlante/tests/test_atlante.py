"""Guardie sul taglio «blu e bianco». Eseguire dopo src/build.py:  python3 -m pytest atlante/tests"""
import csv, json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OPERE = json.load(open(ROOT / 'web/opere.json', encoding='utf-8'))
LUOGHI = {r['id']: r for r in csv.DictReader(open(ROOT / 'data/luoghi.csv', encoding='utf-8'))}


def test_nessun_tessile():
    # 'Tile' prendeva 'Textiles': i tessili blu e bianchi non sono ceramica
    # (sul materiale, non sul titolo: 'Dish with ... Textile Curtains' e' un piatto)
    assert not [o for o in OPERE if re.search(r'\b(silk|cotton|linen|wool)\b', o['tecnica'], re.I)]


def test_luoghi_omonimi_nel_paese_giusto():
    # il criterio 'piu' sitelinks' metteva Worcester, Chelsea e Bow negli Stati Uniti
    for k in ('Worcester', 'Chelsea', 'Bow'):
        assert -3 < float(LUOGHI[k]['lon']) < 0.5 and 51 < float(LUOGHI[k]['lat']) < 53, k
    # le fornaci reali coreane sono a Gwangju nel Gyeonggi, non a Gwangju nel Jeolla
    assert LUOGHI['Gwangju']['qid'] == 'Q42069'


def test_documentato_solo_con_blu_nel_testo():
    for o in OPERE:
        if o['fonte'] != 'colbase':
            assert (o['grado'] == 'documentato') == o['criterio'].startswith('blu dichiarato'), o['id']


def test_intervalli_validi():
    assert all(o['inizio'] <= o['fine'] for o in OPERE if o['inizio'] is not None)


def test_incertezza_conservata():
    o = [o for o in OPERE if 'possibly Valencia or Talavera' in o['cultura']]
    assert all(x['origine_incerta'] for x in o)


def test_nessuna_talavera_precolombiana():
    assert not [o for o in OPERE if o['grado'] == 'ipotetico' and 'Talavera' in o['criterio'] and o['inizio'] < 1500]


def test_mercato_non_inventato():
    # un mercato si emette solo se il catalogo scrive 'for ... market'
    for o in OPERE:
        if o['mercato']:
            assert re.search(r'market', o['cultura'], re.I), o['id']


def test_cina_per_portogallo():
    o = [o for o in OPERE if o['cultura'] == 'Chinese, for Portuguese market']
    assert o and all(x['origine'] == 'China' and x['mercato'] == 'Portugal' for x in o)


WD = [o for o in OPERE if o['fonte'] == 'wd']


def test_azulejo_non_e_azul():
    # 'azulejo' contiene 'azul' ma significa piastrella: senza blu dichiarato resta ipotetico
    az = [o for o in WD if 'azulejo' in o['titolo'].lower()]
    assert az and all(o['grado'] == 'ipotetico' for o in az)


def test_monocromi_esclusi():
    assert not [o for o in WD if re.search(r'sky blue glaze|cobalt blue glaze', o['titolo'] + o['tecnica'], re.I)
                and not re.search(r'underglaze', o['titolo'] + o['tecnica'], re.I)]


def test_secolo_ambiguo_tiene_entrambe_le_letture():
    import sys; sys.path.insert(0, str(ROOT / 'src'))
    from build import intervallo_wd
    assert intervallo_wd('+1800-00-00T00:00:00Z', '7', '', '') [:2] == (1701, 1900)


def test_date_vam():
    import sys; sys.path.insert(0, str(ROOT / 'src'))
    from densita_vam import intervallo
    assert intervallo('ca. 1760-65') == (1755, 1770)
    assert intervallo('mid 18th century') == (1733, 1766)
    assert intervallo('17th-18th century') == (1600, 1799)
    assert intervallo('200 BC') is None


def test_vam_solo_conteggi():
    # condizioni V&A: nessuna scheda, titolo o numero d'inventario nella pagina pubblicata
    v = json.load(open(ROOT / 'web/densita_vam.json', encoding='utf-8'))
    assert set(v['celle'][0]) == {'l', 'd', 'n'}
    testo = json.dumps(v)
    assert 'systemNumber' not in testo and 'accessionNumber' not in testo and 'primaryTitle' not in testo


CB = [o for o in OPERE if o['fonte'] == 'colbase']


def test_museo_non_e_luogo_d_origine():
    # 'Kyoto National Museum' fra i contributori faceva risultare Kyoto origine di 464 pezzi
    assert sum(o['origine'] == 'Kyoto' for o in CB) < 50


def test_donatore_non_e_paese():
    # 'Gift of Dr. Hirano Kosuke' conteneva 'iran'
    assert not [o for o in OPERE if o['origine'] == 'Iran' and 'hirano' in o['cultura'].lower()]
    import sys; sys.path.insert(0, str(ROOT / 'src'))
    from build import trova, PAESI
    assert trova(PAESI, 'Hirano') is None and trova(PAESI, 'capital') is None


def test_meiji_non_e_ming():
    import sys; sys.path.insert(0, str(ROOT / 'src'))
    from build import intervallo_cb
    per = {'Periodo Meiji': (1868, 1912), 'Dinastia Ming': (1368, 1644)}
    assert intervallo_cb(['明治時代'], per)[:2] == (1868, 1912)
    assert intervallo_cb(['明時代・17世紀'], per)[:2] == (1600, 1644)


def test_colbase_documentato_solo_dal_titolo():
    for o in CB:
        assert (o['grado'] == 'documentato') == o['criterio'].startswith('blu nel titolo'), o['id']


def test_periodo_regioni_e_autorita():
    po = json.load(open(ROOT / 'web/periodo.json', encoding='utf-8'))
    regioni = {p['r'] for p in po['periodi']}
    assert 'Corea' in regioni  # PeriodO la chiama 'Korean Peninsula'
    assert all(p['au'] in po['autorita'] for p in po['periodi'])
    assert all(10 <= p['b'] - p['a'] <= 800 for p in po['periodi'])
