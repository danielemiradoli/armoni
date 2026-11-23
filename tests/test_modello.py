"""Il modello di riferimento (CIDOC CRM / Linked Art) e l'esportazione: verifiche che non richiedono i dati grezzi."""
import json, re
from pathlib import Path

import pytest

from armoni import modello as M
from armoni import linkedart as L

RADICE = Path(__file__).resolve().parents[1]
FONTI = ('met', 'metropolitan', 'cleveland', 'cma', 'chicago', 'aic', 'colbase', 'emuseum', 'e뮤지엄', 'tokyo', 'korea')


@pytest.fixture(scope='module')
def v():
    return L.validatore()


def test_il_modello_non_nomina_le_fonti():
    """Principio di universalità: le voci del modello non nominano nessuna fonte."""
    voci = json.dumps([M.ENTITA, M.RELAZIONI], ensure_ascii=False).lower()
    for f in FONTI:
        assert not re.search(r'\b' + re.escape(f) + r'\b', voci), f


def test_ogni_relazione_scritta_dalla_base_e_nel_modello():
    testo = (RADICE / 'armoni/asserzioni.py').read_text(encoding='utf-8')
    usate = set(re.findall(r"D\('([\w.]+)'", testo)) | set(re.findall(r"relazione='([\w.]+)'", testo))
    assert usate and usate <= set(M.RELAZIONI), usate - set(M.RELAZIONI)


def test_ogni_relazione_punta_a_tipi_definiti():
    for nome, r in M.RELAZIONI.items():
        assert r['soggetto'] in M.ENTITA, nome
        assert all(t in M.ENTITA for t in r['oggetto']), nome
        assert r.get('oggetto') or r.get('valore'), nome
        assert r['crm'] and r['la'], nome


def test_il_controllo_del_modello_vede_gli_errori():
    buona = dict(soggetto='oggetto:x:1', relazione='produzione.luogo', oggetto='luogo:Jingdezhen')
    assert M.problemi_modello(buona) == []
    assert M.problemi_modello(dict(buona, relazione='fatto_a'))            # relazione fuori dal modello
    assert M.problemi_modello(dict(buona, oggetto='periodo:Q1'))           # tipo di oggetto sbagliato
    assert M.problemi_modello(dict(buona, oggetto=None, valore='Jingdezhen'))  # testo dove serve un'entità


def riga(rel, grado, oggetto=None, valore=None, prova=None):
    return dict(soggetto='oggetto:t:1', relazione=rel, oggetto=oggetto, valore=valore, fonte='t', metodo='regola di prova',
                grado=grado, dominio='nucleo/dichiarazione', licenza='CC0', prova=prova, filo='blu')


ENTITA = {'oggetto:t:1': dict(nome='vaso di prova', qid=None, dati={'url': 'https://example.org/1'}),
          'luogo:Jingdezhen': dict(nome='Jingdezhen', qid='Q75092', dati={}),
          'periodo:Q9903': dict(nome='dinastia Ming', qid='Q9903', dati={}),
          'gruppo:Museo': dict(nome='Museo', qid=None, dati={}),
          'filo:blu': dict(nome='blu e bianco', qid=None, dati={})}


def test_dichiarato_diretto_dedotto_assegnato(v):
    """La regola di esportazione: ciò che la fonte dichiara è proprietà diretta; ciò che ArMoni deduce è un
    AttributeAssignment di ArMoni con il metodo scritto."""
    righe = [riga('membro_di', 'documentato', 'filo:blu'),
             riga('produzione.luogo', 'dedotto', 'luogo:Jingdezhen'),
             riga('produzione.data', 'dichiarato', valore='1403/1424', prova='Yongle'),
             riga('produzione.periodo', 'dichiarato', 'periodo:Q9903', 'Ming'),
             riga('produzione.artefice', 'dichiarato', valore='bottega imperiale'),
             riga('custode', 'dichiarato', 'gruppo:Museo'),
             riga('mercato_destinazione', 'dichiarato', 'luogo:Jingdezhen')]
    rec = L.oggetto('oggetto:t:1', righe, ENTITA)
    assert L.errori(rec, v) == []
    p = rec['produced_by']
    assert 'took_place_at' not in p                           # dedotto: non diventa una proprietà diretta
    aa = p['attributed_by'][0]
    assert aa['assigned_property'] == 'took_place_at' and aa['carried_out_by'][0]['_label'] == 'ArMoni'
    assert 'regola di prova' in aa['referred_to_by'][0]['content']
    assert p['timespan']['begin_of_the_begin'].startswith('1403') and p['during'][0]['id'].endswith('Q9903')
    assert p['referred_to_by'][0]['content'] == 'bottega imperiale'    # artefice non collegato: resta testo
    assert rec['current_custodian'][0]['type'] == 'Group' and rec['member_of'][0]['type'] == 'Set'
    assert any(a.get('classified_as', [{}])[0].get('id', '').endswith('mercato_destinazione') for a in rec['attributed_by'])


def test_anni_prima_di_cristo(v):
    rec = L.oggetto('oggetto:t:1', [riga('produzione.data', 'dichiarato', valore='-206/220')], ENTITA)
    assert rec['produced_by']['timespan']['begin_of_the_begin'] == '-0206-01-01T00:00:00Z'
    assert L.errori(rec, v) == []


def test_il_validatore_respinge(v):
    rec = L.oggetto('oggetto:t:1', [riga('custode', 'dichiarato', 'gruppo:Museo')], ENTITA)
    assert L.errori(dict(rec, type='Vaso'), v)
    assert L.errori(dict(rec, fatto_a='x'), v)


@pytest.mark.parametrize('f', sorted((RADICE / 'armoni/esempi/linkedart').glob('*.json')), ids=lambda p: p.stem)
def test_gli_esempi_sono_linked_art_valido(f, v):
    assert L.errori(json.load(open(f, encoding='utf-8')), v) == []
