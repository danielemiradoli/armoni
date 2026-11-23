"""Guardie sul filo, e sull-accordo fra i moduli.

Eseguire dopo src/build.py, in uno dei due modi - entrambi validi:
    python3 -m pytest atlante/tests
    python3 atlante/tests/test_atlante.py

Il secondo modo prima definiva i test senza eseguirne nessuno e usciva 0:
un-invocazione sbagliata dava verde silenzioso, che e- la classe di errore
che questo progetto passa il tempo a cercare. Il runner in fondo al file la
rende impossibile."""
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


def test_japan_search_epoche():
    po = json.load(open(ROOT / 'web/periodo.json', encoding='utf-8'))
    jps = {p['n']: (p['a'], p['b'], p['r']) for p in po['periodi'] if p['au'] == 'jps'}
    assert jps['中世'] == (1192, 1600, 'Giappone')
    assert jps['中国・明時代'] == (1368, 1644, 'Cina')   # prefisso 中国・ -> Cina, non Giappone
    assert jps['朝鮮・李氏朝鮮時代'][2] == 'Corea'


def test_letteratura_rifiuta_numeri_senza_provenienza():
    import sys; sys.path.insert(0, str(ROOT / 'src'))
    from letteratura import valida
    siti, fonti = {'Songo Mnara': {}}, {'zhao2012': {}}
    buona = dict(sito_id='Songo Mnara', inizio='1300', fine='1500', tipo='qingbai', misura='conteggio', frammenti='10', percentuale='', base='', fonte_id='zhao2012', pagina='tab. 2', nota='')
    assert valida([buona], siti, fonti) == []
    assert valida([{**buona, 'pagina': ''}], siti, fonti)           # senza pagina
    assert valida([{**buona, 'fonte_id': 'boh'}], siti, fonti)      # fonte sconosciuta
    assert valida([{**buona, 'inizio': '1600'}], siti, fonti)       # anni invertiti
    assert valida([{**buona, 'misura': 'presenza'}], siti, fonti)    # presenza con un numero
    assert valida([{**buona, 'misura': 'presenza', 'frammenti': ''}], siti, fonti) == []


def test_qualita_conta_tutti_i_pezzi():
    # ogni pezzo sta in una cella o in una voce 'fuori': nessuno sparisce dal denominatore
    q = json.load(open(ROOT / 'web/qualita.json', encoding='utf-8'))
    fuori = sum(v for k, v in q['fuori'].items() if k != 'di cui con luogo dedotto')  # sottoinsieme di 'senza luogo'
    assert sum(c['n'] for c in q['celle']) + fuori == len(OPERE)
    assert q['fuori']['regione non determinata'] == 0


def test_luogo_dedotto_non_tocca_il_dichiarato():
    ded = [o for o in OPERE if o.get('origine_dedotta')]
    assert ded and all(o['fonte'] == 'colbase' and o['origine'] is None and o['sede'] == 'Tokyo National Museum' for o in ded)


def test_fonti_mancanti_dichiarate():
    q = json.load(open(ROOT / 'web/qualita.json', encoding='utf-8'))
    assert {m['regione'] for m in q['mancanti']} >= {'Cina'}  # Taipei; la Corea ora arriva da eMuseum
    assert all(m['esito'] and m['prossimo_passo'] for m in q['mancanti'])


def test_contesti_accostano_non_collegano():
    c = json.load(open(ROOT / 'web/contesti.json', encoding='utf-8'))
    el = c['elementi']
    assert el and all(e['quando']['da'] is not None and e['luoghi'] for e in el)
    assert not any(k in e for e in el for k in ('opere', 'opera', 'pezzi'))  # nessun legame con le opere
    assert all(l['stato_allora'] is None for e in el for l in e['luoghi'] if l['precisione'] == 'regione')
    assert all(x['via'] in ('territorio', 'partecipante') for e in el for x in e['contesto'])
    assert all('dedotto' in e['quando']['metodo'] for e in el if e['quando'].get('dedotto'))


def test_macroregioni_e_tipi():
    tab = {r['paese_2010']: r['macroregione'] for r in csv.DictReader(open(ROOT / 'data/macroregioni.csv', encoding='utf-8'))}
    assert tab['United States'] == 'Nord America' and tab['Netherlands'] == 'Europa' and tab['Guinea'] == 'Africa subsahariana'
    assert len(set(tab.values())) == 11 and all(tab.values())
    el = json.load(open(ROOT / 'web/contesti.json', encoding='utf-8'))['elementi']
    assert {e['tipo'] for e in el} <= {'movimento', 'scuola', 'stile', 'periodizzazione'}
    assert all(e['nome'] for e in el)


def test_relazioni_solo_dichiarate():
    el = json.load(open(ROOT / 'web/contesti.json', encoding='utf-8'))['elementi']
    rel = [(e['id'], r) for e in el for r in e['relazioni']]
    assert rel and all(r['verso'] in '<>' and r['id'] != i for i, r in rel)
    assert {r['rel'] for _, r in rel} <= {'influenzato da', 'parte di', 'caso particolare di', 'segue', 'sostituisce'}
    ids = {e['id'] for e in el}  # ogni arco fra voci collocate compare da entrambi i lati
    for i, r in rel:
        if r['collocata']:
            altra = next(e for e in el if e['id'] == r['id'])
            assert any(x['id'] == i and x['verso'] != r['verso'] for x in altra['relazioni'])


def test_anno_finale_abbreviato():
    import sys; sys.path.insert(0, str(ROOT / 'src'))
    import build as B
    assert B.intervallo_cb(['明時代・嘉靖年間(1522～66)'], {})[:2] == (1522, 1566)
    assert B.intervallo_cb(['江戸時代･天明年間(1781～89)'], {'明': (1368, 1644)})[:2] == (1781, 1789)
    assert B.intervallo_cb(['(1795～05)'], {})[:2] == (1795, 1805)


def test_emuseum_solo_kogl1():
    import json, pathlib
    o = json.load(open(pathlib.Path(__file__).parent.parent / 'web/opere.json'))
    o = o['opere'] if isinstance(o, dict) else o
    k = [x for x in o if str(x.get('id', '')).startswith('emu:')]
    assert k and all('KOGL tipo 1' in x['licenza'] for x in k)
    assert all('emuseum.go.kr/detail?relicId=' in x['url'] for x in k)


def test_filo_lacca_inclusione():
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / 'src'))
    import filo_lacca as f
    assert f.inclusione('Lacquer on wood, gold maki-e')[0] == 'documentato'
    assert f.inclusione('Japanned tinplate')[2] is True
    assert f.inclusione('Nitrocellulose lacquer on canvas')[0] is None
    assert f.inclusione('Porcelain painted in underglaze blue')[0] is None
    assert f.origine('Edo period (1615–1868)', 'Japan') == 'Japan'  # «Edo» è un'epoca, non il centro
    assert f.origine('Ryūkyū Islands', 'Japan') == 'Okinawa'
    assert f.inclusione('Cotton, silk, and silver-leaf-over-lacquered-paper-strip-wrapped bast fiber, plain weave')[0] is None
    import json, pathlib
    o = json.load(open(pathlib.Path(__file__).parent.parent / 'web/fili/lacca/opere.json'))
    assert all('KOGL tipo 1' in x['licenza'] for x in o if x['fonte'] == 'emuseum')


def test_tipi_oggetto():
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / 'src'))
    import tipi
    assert tipi.tipo('Plate with floral design')[0] == 'piatto'  # «design» non fa un disegno
    assert tipi.tipo('청화백자 구연부편')[0] == 'frammento'
    assert tipi.tipo('백자 청화 풀무늬 작은 항아리')[0] == 'vaso'
    assert tipi.tipo('青花柘榴文皿')[0] == 'piatto'
    assert tipi.tipo('Inrō')[0] == 'inrō'
    assert tipi.tipo('Openwork fruit basket') == (None, None)


def test_luoghi_hanno_macroregione():
    import json, pathlib
    w = pathlib.Path(__file__).parent.parent / 'web'
    for p in [w / 'luoghi.json', *w.glob('fili/*/luoghi.json')]:
        assert all(l.get('macroregione') for l in json.load(open(p))), p


def test_vocabolari_rispettano_l_accordo_comune():
    """I termini dell-atlante sono quelli dichiarati in comune.py.

    Non unifica i gradi col motore: le due scale rispondono a domande diverse,
    e comune.py spiega perche- non vanno fuse. Verifica soltanto che l-atlante
    non introduca termini nuovi senza dichiararli.
    """
    import sys as _s
    _s.path.insert(0, str(ROOT.parent))
    import comune

    for p in [ROOT / "web/opere.json", *ROOT.glob("web/fili/*/opere.json")]:
        pezzi = json.load(open(p, encoding="utf-8"))
        fuori = {x["grado"] for x in pezzi
                 if not comune.grado_valido("atlante/appartenenza", x["grado"])}
        assert not fuori, "%s: gradi non dichiarati %s" % (p, fuori)
        guasti = [g for x in pezzi[:200]
                  for g in comune.problemi_asserzione(x, "atlante/appartenenza")]
        assert not guasti, "%s: %s" % (p, guasti[:3])

    c = json.load(open(ROOT / "web/contesti.json", encoding="utf-8"))["elementi"]
    ammessi = comune.gradi("atlante/datazione")
    for x in c:
        m = (x.get("quando") or {}).get("metodo")
        if m:
            assert m.split()[0] in ammessi, "metodo non dichiarato: %r" % m
    tipi = {x.get("tipo") for x in c}
    assert tipi <= set(comune.TIPI_FENOMENO), \
        "tipi non dichiarati: %s" % (tipi - set(comune.TIPI_FENOMENO))
    # I luoghi dei FILI: solo i cinque livelli canonici, nessuna indulgenza.
    # Questo controllo mancava, ed e' il motivo per cui comune.py ha registrato
    # per qualche ora tre livelli invece di cinque: il test guardava solo i
    # contesti, cioe' l'unico file che non li usa tutti.
    for f in [ROOT / "web/luoghi.json", *ROOT.glob("web/fili/*/luoghi.json")]:
        pr = {l.get("precisione") for l in json.load(open(f, encoding="utf-8"))}
        fuori = pr - set(comune.PRECISIONE_LUOGO)
        assert not fuori, "%s: precisioni non dichiarate %s" % (f, fuori)

    # I CONTESTI: ammesso in piu' il solo valore transitorio, e confinato qui.
    prec = {l.get("precisione") for x in c for l in x.get("luoghi", [])}
    ammesse = set(comune.PRECISIONE_LUOGO) | set(comune.PRECISIONE_TRANSITORIA)
    assert prec <= ammesse, "precisioni non dichiarate: %s" % (prec - ammesse)


def test_il_valore_transitorio_resta_confinato_nei_contesti():
    """'luogo' e' il secchio unico che contesti.py assegnava a tutto cio' che
    sta dentro un paese. La regola che lo suddivide e' scritta e misurata
    (query contesti_natura_luogo.rq, 97% su 297 luoghi) e i dati prendono i
    valori fini al prossimo build. Questo test impedisce che il valore
    transitorio si diffonda altrove nel frattempo, e quindi che la migrazione
    diventi permanente per dimenticanza."""
    import sys as _s
    _s.path.insert(0, str(ROOT.parent))
    import comune
    for f in [ROOT / "web/luoghi.json", *ROOT.glob("web/fili/*/luoghi.json")]:
        pr = {l.get("precisione") for l in json.load(open(f, encoding="utf-8"))}
        assert not pr & set(comune.PRECISIONE_TRANSITORIA), \
            "%s usa un valore transitorio: %s" % (f, pr & set(comune.PRECISIONE_TRANSITORIA))


def test_interfaccia_e_comune_concordano_sugli_aloni():
    """L'interfaccia non puo' importare comune.py, quindi la costante e'
    ripetuta in atlante.js. Questo test la tiene allineata, cosi' la
    ripetizione e' guardata invece di essere un rischio.
    """
    import re, sys as _s
    _s.path.insert(0, str(ROOT.parent))
    import comune
    js = (ROOT / 'web/atlante.js').read_text(encoding='utf-8')
    m = re.search(r"const CON_ESTENSIONE = \[([^\]]*)\]", js)
    assert m, "CON_ESTENSIONE non dichiarata in atlante.js"
    nel_js = tuple(x.strip().strip("'\"") for x in m.group(1).split(','))
    assert nel_js == comune.PRECISIONE_CON_ESTENSIONE, \
        f"atlante.js dice {nel_js}, comune.py dice {comune.PRECISIONE_CON_ESTENSIONE}"


# Quanti aloni, nei dati pubblicati, poggiano ancora sul poligono del paese
# contenitore pur non essendo paesi. La regola in aree.py non li produce piu':
# questi sono residui di aree.json, che si rigenera solo con data/raw/. Il
# numero puo' solo SCENDERE, e la prossima ricostruzione lo porta a 0.
ALONI_RIPIEGATI_RESIDUI = 23


def test_gli_aloni_ripiegati_possono_solo_diminuire():
    """Il ripiego sul poligono del paese contenitore vale solo per i paesi.

    Misurato il 23/11/2026: era attivo su 23 luoghi che non sono paesi, tutti
    stati storici senza corrispondenza con uno Stato di oggi — il regno di
    Gandhara con l'area del Pakistan (871.410 km2), il Regno Ahom con quella
    dell'India (3.151.482). Non e' un'approssimazione: e' l'estensione di
    un'altra cosa, e sbaglia piu' spesso fuori dall'Europa, dove i confini di
    oggi somigliano meno a quelli di allora.

    Il test e' una cricca, non un rosso atteso: misura i dati pubblicati, che
    si rigenerano solo con data/raw/, e passa finche' il numero non sale. Alla
    prossima ricostruzione scende a 0 e la costante si abbassa. Un rosso
    atteso, qui, sarebbe diventato verde da solo e avrebbe richiesto a qualcuno
    di ricordarsi di togliere il marcatore: una cricca non chiede di ricordare
    niente.
    """
    import json as _j, sys as _s
    _s.path.insert(0, str(ROOT.parent))
    import comune
    aree = _j.load(open(ROOT / 'web/aree.json', encoding='utf-8'))
    prec = {}
    for l in _j.load(open(ROOT / 'web/luoghi.json', encoding='utf-8')):
        if l.get('qid'):
            prec.setdefault(l['qid'], l['precisione'])
    for e in _j.load(open(ROOT / 'web/contesti.json', encoding='utf-8'))['elementi']:
        for l in e['luoghi']:
            prec.setdefault(l['id'], l['precisione'])
    residui = [q for q, v in aree.items()
               if v['fonte'] != 'wikidata'
               and prec.get(q) not in comune.PRECISIONE_CON_RIPIEGO_PAESE]
    assert len(residui) <= ALONI_RIPIEGATI_RESIDUI, (
        f"gli aloni ripiegati sono saliti a {len(residui)} (soglia "
        f"{ALONI_RIPIEGATI_RESIDUI}): {residui[:5]}")
    if len(residui) < ALONI_RIPIEGATI_RESIDUI:
        print(f"    [la cricca puo' scendere: {len(residui)} residui, "
              f"abbassare ALONI_RIPIEGATI_RESIDUI]")


if __name__ == "__main__":
    # Senza questo blocco il file, lanciato direttamente, definiva i test e non
    # ne eseguiva nessuno, uscendo 0.
    _rossi = []
    for _nome, _f in list(globals().items()):
        if not _nome.startswith("test_"):
            continue
        try:
            _f()
        except AssertionError as _e:
            _rossi.append(_nome)
            print("FALLITO  %s\n         %s" % (_nome, _e))
        else:
            print("ok", _nome)
    print("\n%d falliti" % len(_rossi))
    raise SystemExit(1 if _rossi else 0)
