"""Esportazione della base in Linked Art (JSON-LD), validata contro lo schema ufficiale.

Regola, una per tutte le relazioni e tutte le fonti:
- ciò che la fonte dichiara (grado «dichiarato» o «documentato») diventa la proprietà diretta di Linked Art;
- ciò che ArMoni deduce, o tiene per ipotesi, diventa un AttributeAssignment eseguito da ArMoni, con il metodo
  scritto come dichiarazione: chi legge fuori da ArMoni vede che cosa è affermato e da chi;
- ciò che la fonte scrive ma la base non ha ancora collegato a un'entità resta una dichiarazione testuale
  (Statement) del tipo Getty AAT previsto dal modello.

Gli identificativi sono provvisori (BASE): la loro forma stabile è una decisione ancora da prendere.
Uso: python3 -m armoni.linkedart [n]  → out/linkedart.jsonl (tutti) ed esempi in armoni/esempi/linkedart/
"""
import json, re, sqlite3, sys
from collections import defaultdict
from pathlib import Path

from . import RADICE
from . import modello as M

BASE = 'https://danielemiradoli.github.io/armoni/id/'
CONTESTO = 'https://linked.art/ns/v1/linked-art.json'
AAT = M.AAT
DB = RADICE / 'out/armoni.sqlite'
SCHEMI = Path(__file__).parent / 'dati/linkedart_schema'
DICHIARATI = {'dichiarato', 'documentato'}

ARMONI = {'id': BASE + 'gruppo/armoni', 'type': 'Group', '_label': 'ArMoni'}


def T(aat, label):
    return {'id': AAT + aat, 'type': 'Type', '_label': label}


def dichiarazione(testo, aat=None, label=None):
    d = {'type': 'LinguisticObject', 'content': testo}
    if aat:
        d['classified_as'] = [{'id': aat, 'type': 'Type', '_label': label or 'statement',
                               'classified_as': [T('300418049', 'Statement')]}]
    return d


def uri(ent):
    tipo, _, resto = ent.partition(':')
    if tipo == 'periodo':
        return 'http://www.wikidata.org/entity/' + resto
    return BASE + tipo + '/' + resto.replace(' ', '_')


def rif(ent, entita):
    tipo = M.tipo_entita(ent)
    e = entita.get(ent, {})
    r = {'id': uri(ent), 'type': M.ENTITA[tipo]['la'], '_label': e.get('nome') or ent.split(':', 1)[1]}
    if e.get('qid') and tipo != 'periodo':
        r['equivalent'] = [{'id': 'http://www.wikidata.org/entity/' + e['qid'], 'type': r['type']}]
    return r


def anno(y, fine=False):
    s = f'-{abs(y):04d}' if y < 0 else f'{y:04d}'
    return s + ('-12-31T23:59:59Z' if fine else '-01-01T00:00:00Z')


def intervallo(valore, testo=None):
    a, b = (int(x) for x in valore.split('/'))
    ts = {'type': 'TimeSpan', 'begin_of_the_begin': anno(a), 'end_of_the_end': anno(b, True)}
    if testo:
        ts['identified_by'] = [{'type': 'Name', 'content': testo, 'classified_as': [T('300404669', 'Display Name')]}]
    return ts


def assegnazione(a, proprieta, valore):
    """Un'asserzione di ArMoni che non è una dichiarazione della fonte: chi, come, su che cosa."""
    aa = {'type': 'AttributeAssignment', 'carried_out_by': [ARMONI],
          'referred_to_by': [dichiarazione(f"{a['grado']}: {a['metodo']}")]}
    if proprieta:
        aa['assigned_property'] = proprieta
    if valore is not None:
        aa['assigned'] = valore
    return aa


def oggetto(sid, righe, entita):
    e = entita[sid]
    rec = {'@context': CONTESTO, 'id': uri(sid), 'type': 'HumanMadeObject', '_label': e['nome'],
           'identified_by': [{'type': 'Name', 'content': e['nome'], 'classified_as': [T('300404670', 'Primary Name')]}],
           'classified_as': [T('300404024', 'Collection Item')]}
    if e.get('qid'):
        rec['equivalent'] = [{'id': 'http://www.wikidata.org/entity/' + e['qid'], 'type': 'HumanMadeObject'}]
    prod, attr, rif_testo, prod_testo, fonti = {}, [], [], [], {}
    for a in righe:
        rel, dich = a['relazione'], a['grado'] in DICHIARATI
        r = M.RELAZIONI[rel]
        fonti[a['fonte']] = a['licenza']
        val = rif(a['oggetto'], entita) if a['oggetto'] else None
        if rel == 'produzione.data':
            ts = intervallo(a['valore'], a['prova'])
            if dich:
                prod['timespan'] = ts
            else:
                prod.setdefault('attributed_by', []).append(assegnazione(a, 'timespan', ts))
            continue
        if val is None:  # testo dichiarato dalla fonte, non ancora collegato a un'entità
            d = dichiarazione(a['valore'], r.get('dichiarazione'), rel)
            if not dich:
                attr.append(assegnazione(a, 'referred_to_by', d))
            elif rel.startswith('produzione.'):
                prod_testo.append(d)
            else:
                rif_testo.append(d)
            continue
        if r.get('estensione'):
            aa = assegnazione(a, None, val)
            aa['classified_as'] = [{'id': BASE + 'proprieta/' + rel, 'type': 'Type', '_label': r['descrizione']}]
            attr.append(aa)
            continue
        campo = r['la'].split('.')[-1]
        if rel.startswith('produzione.'):
            if dich:
                prod.setdefault(campo, []).append(val)
            else:
                prod.setdefault('attributed_by', []).append(assegnazione(a, campo, val))
        elif dich:
            rec.setdefault(campo, []).append(val)
        else:
            attr.append(assegnazione(a, campo, val))
    if prod or prod_testo:
        p = {'type': 'Production'}
        p.update(prod)
        if prod_testo:
            p['referred_to_by'] = prod_testo
        rec['produced_by'] = p
    licenze = '; '.join(f'{f}: {l}' for f, l in sorted(fonti.items()))
    rif_testo.append(dichiarazione(licenze, AAT + '300435434', 'Rights Statement'))
    rec['referred_to_by'] = rif_testo
    url = (e.get('dati') or {}).get('url')
    if url:
        rec['subject_of'] = [{'type': 'LinguisticObject', '_label': 'scheda della fonte',
                              'digitally_carried_by': [{'type': 'DigitalObject',
                                                        'access_point': [{'id': url, 'type': 'DigitalObject'}]}]}]
    if attr:
        rec['attributed_by'] = attr
    return rec


def esporta(limite=None, db=None):
    db = db or sqlite3.connect(DB)
    db.row_factory = sqlite3.Row
    entita = {r['id']: dict(r, dati=json.loads(r['dati'] or '{}')) for r in db.execute('select * from entita')}
    per = defaultdict(list)
    for a in db.execute("select * from asserzioni where soggetto like 'oggetto:%'"):
        per[a['soggetto']].append(dict(a))
    for i, (sid, righe) in enumerate(per.items()):
        if limite and i >= limite:
            break
        yield oggetto(sid, righe, entita)


def validatore():
    from jsonschema import Draft202012Validator
    from referencing import Registry, Resource
    reg = Registry()
    for f in SCHEMI.glob('*.json'):
        s = json.load(open(f, encoding='utf-8'))
        reg = reg.with_resource(s['$id'], Resource.from_contents(s))
        reg = reg.with_resource('https://linked.art/api/1.0/schema/' + f.name, Resource.from_contents(s))
    return Draft202012Validator(json.load(open(SCHEMI / 'object.json', encoding='utf-8')), registry=reg)


def errori(rec, v=None):
    v = v or validatore()
    return [f"{'/'.join(map(str, e.absolute_path))}: {e.message[:200]}" for e in v.iter_errors(rec)]


if __name__ == '__main__':
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else None
    v, n, cattivi = validatore(), 0, 0
    uscita = RADICE / 'out/linkedart.jsonl'
    esempi = Path(__file__).parent / 'esempi/linkedart'
    esempi.mkdir(parents=True, exist_ok=True)
    scelti = {}
    with open(uscita, 'w', encoding='utf-8') as f:
        for rec in esporta(limite):
            n += 1
            e = errori(rec, v)
            if e:
                cattivi += 1
                if cattivi <= 5:
                    print(rec['id'], e[:3])
            f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            fonte = re.split('[:-]', rec['id'].rsplit('/', 1)[-1])[0]
            completo = 'attributed_by' in json.dumps(rec) and 'took_place_at' in rec.get('produced_by', {})
            if fonte not in scelti or (completo and not scelti[fonte][1]):
                scelti[fonte] = (rec, completo)
    for fonte, (rec, _) in scelti.items():
        json.dump(rec, open(esempi / f'{fonte}.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'{n} pezzi esportati in {uscita.relative_to(RADICE)}; non validi secondo lo schema Linked Art: {cattivi}; '
          f'esempi: {sorted(scelti)}')
