"""L'archivio delle asserzioni: la base comune da cui gli strumenti leggono.

Ogni dato su un pezzo diventa un'asserzione con soggetto, relazione, oggetto (un'entità) o valore (un testo),
e i quattro attributi obbligatori del protocollo: fonte, metodo, grado, licenza; più la prova (le parole del
catalogo che la sostengono) e il dominio del grado (comune.GRADI). Le entità hanno un identificativo ArMoni
(`oggetto:met:1234`, `luogo:Jingdezhen`, `filo:blu`) e, dove esiste, il QID di Wikidata come equivalenza.

Archivio: out/armoni.sqlite (si rigenera; non è nel repository). Riepilogo: out/asserzioni.md.
Uso: python3 -m armoni.asserzioni blu lacca
"""
import json, re, sqlite3, sys
from collections import Counter

from . import RADICE, ATLANTE
from . import filo as F

sys.path.insert(0, str(RADICE))
import comune  # noqa: E402

DB = RADICE / 'out/armoni.sqlite'
SCHEMA = '''
create table entita (id text primary key, tipo text not null, nome text, qid text, dati text);
create table asserzioni (soggetto text not null, relazione text not null, oggetto text, valore text,
                         fonte text not null, metodo text not null, grado text not null, dominio text not null,
                         licenza text not null, prova text, filo text);
create index a_s on asserzioni(soggetto); create index a_o on asserzioni(oggetto); create index a_r on asserzioni(relazione);
'''
# datazioni che il catalogo non scrive in anni: le ricava ArMoni (epoca → anni, secolo → anni)
DATA_DEDOTTA = re.compile(r'\((?:epoca \(Wikidata\)|secolo|secolo ∩ epoca)\)$')


def asserzioni_pezzo(o, nome_filo):
    s, f, lic = 'oggetto:' + o['id'], o['fonte'], o['licenza']
    dich = o.get('_dichiarati', {})
    a = [dict(soggetto=s, relazione='appartiene_a', oggetto='filo:' + nome_filo, fonte=f, metodo=o['criterio'],
              grado=o['grado'], dominio='atlante/appartenenza', licenza=lic,
              prova=(re.search(r'«(.+?)»', o['criterio']) or [None, None])[1])]
    D = lambda rel, grado, metodo, oggetto=None, valore=None, prova=None: a.append(dict(
        soggetto=s, relazione=rel, oggetto=oggetto, valore=valore, fonte=f, metodo=metodo, grado=grado,
        dominio='nucleo/dichiarazione', licenza=lic, prova=prova))
    if o['origine']:
        D('fatto_a', 'dichiarato', 'luogo scritto nel catalogo, riconosciuto con il gazzettiere del filo o dal campo strutturato',
          oggetto='luogo:' + o['origine'], prova=o['cultura'][:200] or None)
    elif o.get('origine_dedotta'):
        D('fatto_a', 'dedotto', o.get('criterio_luogo', ''), oggetto='luogo:' + o['origine_dedotta'])
    if o['inizio'] is not None:
        ded = bool(DATA_DEDOTTA.search(o['data_testo'] or '')) or 'convenzional' in o['criterio']
        D('datato', 'dedotto' if ded else 'dichiarato',
          'anni ricavati dall\'epoca o dal secolo nominati dalla scheda' if ded else 'anni scritti dal catalogo',
          valore=f"{o['inizio']}/{o['fine']}", prova=o['data_testo'] or None)
    if o['sede']:
        D('conservato_presso', 'dichiarato', 'istituzione che pubblica la scheda', oggetto='luogo:' + o['sede'])
    if o['mercato']:
        D('destinato_a', 'dichiarato', 'mercato di destinazione scritto nel catalogo («for the … market»)',
          oggetto='luogo:' + o['mercato'], prova=o['cultura'][:200])
    for k, rel in (('periodo', 'periodo_dichiarato'), ('dinastia', 'periodo_dichiarato'), ('artefice', 'artefice_dichiarato')):
        if dich.get(k):
            D(rel, 'dichiarato', f'campo «{k}» del catalogo, riportato com\'è', valore=dich[k][:300])
    if o.get('tipo'):
        D('tipo', 'dedotto', 'tipo di oggetto letto per parole chiave nel nome (atlante/src/tipi.py)',
          valore=o['tipo'], prova=o.get('tipo_parola'))
    return a


def problemi(a):
    p = [f'manca {c}' for c in comune.CAMPI_ASSERZIONE if not a.get(c)]
    if a.get('grado') and not comune.grado_valido(a['dominio'], a['grado']):
        p.append(f"grado {a['grado']!r} fuori da {a['dominio']}")
    if not (a.get('oggetto') or a.get('valore')):
        p.append('né oggetto né valore')
    return p


def costruisci(fili):
    DB.parent.mkdir(exist_ok=True)
    if DB.exists():
        DB.unlink()
    db = sqlite3.connect(DB)
    db.executescript(SCHEMA)
    ent, tutte, errori = {}, [], Counter()
    for n in fili:
        r = F.costruisci(n)
        ent['filo:' + n] = ('filo', r['cfg']['titolo'], None, {})
        for k, l in r['luoghi'].items():
            ent['luogo:' + k] = ('luogo', l.get('nome'), l.get('qid') or None,
                                 {c: l.get(c) for c in ('lat', 'lon', 'precisione', 'metodo')})
        for o in r['opere']:
            ent['oggetto:' + o['id']] = ('oggetto', o['titolo'], o.get('wikidata') or None, {'url': o['url']})
            for a in asserzioni_pezzo(o, n):
                for p in problemi(a):
                    errori[p] += 1
                tutte.append(dict(a, filo=n))
    for f in {a['fonte'] for a in tutte}:
        ent['fonte:' + f] = ('fonte', f, None, {})
    db.executemany('insert into entita values (?,?,?,?,?)', [(k, t, nm, q, json.dumps(d, ensure_ascii=False)) for k, (t, nm, q, d) in ent.items()])
    cols = ('soggetto', 'relazione', 'oggetto', 'valore', 'fonte', 'metodo', 'grado', 'dominio', 'licenza', 'prova', 'filo')
    db.executemany(f'insert into asserzioni values ({",".join("?" * len(cols))})', [tuple(a.get(c) for c in cols) for a in tutte])
    db.commit()
    riepilogo(db, errori)
    return db, errori


def riepilogo(db, errori):
    q = lambda sql: db.execute(sql).fetchall()
    righe = ['# Archivio delle asserzioni — riepilogo', '',
             'Rigenerato da `python3 -m armoni.asserzioni`. L\'archivio completo è `out/armoni.sqlite` (si rigenera).', '',
             f"Entità: {q('select count(*) from entita')[0][0]} · asserzioni: {q('select count(*) from asserzioni')[0][0]} · "
             f"asserzioni fuori dall'accordo (comune.py): {sum(errori.values())}", '',
             '| entità | quante |', '| --- | ---: |'] + [f'| {t} | {n} |' for t, n in q('select tipo, count(*) from entita group by tipo order by 2 desc')]
    righe += ['', '| relazione | grado | asserzioni |', '| --- | --- | ---: |']
    righe += [f'| {r} | {g} | {n} |' for r, g, n in q('select relazione, grado, count(*) from asserzioni group by 1,2 order by 1, 3 desc')]
    righe += ['', '## Che cosa i cataloghi dichiarano e la base non collega ancora', '',
              'Periodi e artefici sono riportati come testo: non sono ancora entità. È il prossimo ponte (periodi unificati, artefici attraverso il motore delle identità).', '',
              '| relazione | valori distinti | pezzi |', '| --- | ---: | ---: |']
    righe += [f'| {r} | {d} | {n} |' for r, d, n in q("select relazione, count(distinct valore), count(distinct soggetto) from asserzioni where relazione in ('periodo_dichiarato','artefice_dichiarato') group by 1")]
    if errori:
        righe += ['', '## Fuori accordo', ''] + [f'- {k}: {v}' for k, v in errori.most_common()]
    (RADICE / 'out/asserzioni.md').write_text('\n'.join(righe) + '\n', encoding='utf-8')
    print('\n'.join(righe))


if __name__ == '__main__':
    sys.path.insert(0, str(ATLANTE / 'src'))
    costruisci(sys.argv[1:] or ['blu', 'lacca'])
