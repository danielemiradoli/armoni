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
from . import periodi as PER
from . import modello as M

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
    a = [dict(soggetto=s, relazione='membro_di', oggetto='filo:' + nome_filo, fonte=f, metodo=o['criterio'],
              grado=o['grado'], dominio='atlante/appartenenza', licenza=lic,
              prova=(re.search(r'«(.+?)»', o['criterio']) or [None, None])[1])]
    D = lambda rel, grado, metodo, oggetto=None, valore=None, prova=None: a.append(dict(
        soggetto=s, relazione=rel, oggetto=oggetto, valore=valore, fonte=f, metodo=metodo, grado=grado,
        dominio='nucleo/dichiarazione', licenza=lic, prova=prova))
    if o['origine']:
        D('produzione.luogo', 'dichiarato', 'luogo scritto nel catalogo, riconosciuto con il gazzettiere del filo o dal campo strutturato',
          oggetto='luogo:' + o['origine'], prova=o['cultura'][:200] or None)
    elif o.get('origine_dedotta'):
        D('produzione.luogo', 'dedotto', o.get('criterio_luogo', ''), oggetto='luogo:' + o['origine_dedotta'])
    if o['inizio'] is not None:
        ded = bool(DATA_DEDOTTA.search(o['data_testo'] or '')) or 'convenzional' in o['criterio']
        D('produzione.data', 'dedotto' if ded else 'dichiarato',
          'anni ricavati dall\'epoca o dal secolo nominati dalla scheda' if ded else 'anni scritti dal catalogo',
          valore=f"{o['inizio']}/{o['fine']}", prova=o['data_testo'] or None)
    custode, _ = o.get('_custode') or (None, None)
    if custode:
        D('custode', 'dichiarato', 'istituzione che conserva il pezzo, come la nomina la fonte', oggetto='gruppo:' + custode)
    if o['mercato']:
        D('mercato_destinazione', 'dichiarato', 'mercato di destinazione scritto nel catalogo («for the … market»)',
          oggetto='luogo:' + o['mercato'], prova=o['cultura'][:200])
    for k in ('periodo', 'dinastia'):
        for parte, qid, motivo in PER.riconosci(dich.get(k, ''), o['inizio'], o['fine']):
            if qid:
                D('produzione.periodo', 'dichiarato', f'periodo scritto nel campo «{k}» del catalogo, riconosciuto fra le etichette '
                  f'multilingue di Wikidata ({motivo}); compatibile con le date del pezzo', oggetto='periodo:' + qid, valore=parte, prova=parte)
            else:
                D('produzione.periodo', 'dichiarato', f'campo «{k}» del catalogo, riportato com\'è: periodo non collegato ({motivo})',
                  valore=parte, prova=parte)
    if dich.get('artefice'):
        D('produzione.artefice', 'dichiarato', 'campo «artefice» del catalogo, riportato com\'è', valore=dich['artefice'][:300])
    if o.get('tipo'):
        D('classificato_come', 'dedotto', 'tipo di oggetto letto per parole chiave nel nome (atlante/src/tipi.py)',
          valore=o['tipo'], prova=o.get('tipo_parola'))
    return a


def definizioni_periodo(ent):
    """I periodi citati diventano entità; PeriodO aggiunge le sue definizioni (chi, quando, dove) allo stesso concetto."""
    voc, _ = PER.vocabolario()
    usati = {}
    a_out = []
    # PeriodO: ogni definizione di un'autorità che porta un'etichetta riconosciuta diventa «periodo.definizione»
    p0d = json.load(open(ATLANTE / 'data/p0d.json', encoding='utf-8'))
    for aid, au in p0d['authorities'].items():
        src = au.get('source', {}); tit = (src.get('title') or (src.get('partOf') or {}).get('title') or aid)[:120]
        for pid, p in au.get('periods', {}).items():
            def y(t):
                i = (t or {}).get('in', {})
                for k in ('year', 'earliestYear', 'latestYear'):
                    try: return int(i[k])
                    except (KeyError, ValueError, TypeError): pass
            a, b = y(p.get('start')), y(p.get('stop'))
            if a is None or b is None:
                continue
            for parte, qid, motivo in PER.riconosci(p.get('label', ''), a, b)[:1]:
                if qid:
                    usati[qid] = 1
                    dove = ', '.join(x.get('label', '') for x in p.get('spatialCoverage', []))[:150]
                    a_out.append(dict(soggetto='periodo:' + qid, relazione='periodo.definizione', oggetto='autorita:periodo:' + aid,
                                      valore=f'{a}/{b}', fonte='periodo', metodo=f'definizione PeriodO «{p.get("label")}» ({tit}); '
                                      f'collegata per etichetta ({motivo})' + (f'; copertura: {dove}' if dove else ''),
                                      grado='dichiarato', dominio='nucleo/dichiarazione', licenza='CC0 (PeriodO)', prova=pid, filo=None))
                    ent['autorita:periodo:' + aid] = ('autorita', tit, None, {'periodo': aid})
    return a_out


def problemi(a):
    p = [f'manca {c}' for c in comune.CAMPI_ASSERZIONE if not a.get(c)]
    if a.get('grado') and not comune.grado_valido(a['dominio'], a['grado']):
        p.append(f"grado {a['grado']!r} fuori da {a['dominio']}")
    if not (a.get('oggetto') or a.get('valore')):
        p.append('né oggetto né valore')
    return p + M.problemi_modello(a)


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
            c, cq = o.get('_custode') or (None, None)
            if c:
                ent.setdefault('gruppo:' + c, ('gruppo', c, cq, {'ruolo': 'istituzione custode'}))
            for a in asserzioni_pezzo(o, n):
                for p in problemi(a):
                    errori[p] += 1
                tutte.append(dict(a, filo=n))
    d = definizioni_periodo(ent)
    for a in d:
        for p in problemi(a):
            errori[p] += 1
    tutte += d
    for f in {a['fonte'] for a in tutte}:
        ent['fonte:' + f] = ('fonte', f, None, {})
    voc, _ = PER.vocabolario()
    for q in {x['oggetto'][8:] for x in tutte if (x.get('oggetto') or '').startswith('periodo:')} | {x['soggetto'][8:] for x in tutte if x['soggetto'].startswith('periodo:')}:
        p = voc[q]
        ent['periodo:' + q] = ('periodo', PER.etichetta(q), q, {'inizio': p['inizio'], 'fine': p['fine'], 'classi': p['classi'],
                                                              'lingue': sorted(p['etichette'])})
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
    righe += ['', '## Che cosa i cataloghi dichiarano, e quanto la base collega', '',
              'I periodi scritti dai cataloghi si collegano ai concetti di periodo (riconosciuti in qualunque lingua fra le etichette di Wikidata); quelli non riconosciuti restano testo, con il motivo. Gli artefici sono ancora testo: il prossimo ponte, attraverso il motore delle identità.', '',
              '| relazione | collegate a un\'entità | solo testo | pezzi |', '| --- | ---: | ---: | ---: |']
    righe += [f'| {r} | {c} | {t} | {n} |' for r, c, t, n in q("select relazione, sum(oggetto is not null), sum(oggetto is null), count(distinct soggetto) from asserzioni where relazione in ('produzione.periodo','produzione.artefice') group by 1")]
    n_per = q("select count(distinct oggetto) from asserzioni where relazione='produzione.periodo' and oggetto is not null")[0][0]
    n_pez = q("select count(distinct soggetto) from asserzioni where relazione='produzione.periodo' and oggetto is not null")[0][0]
    n_def = q("select count(*) from asserzioni where relazione='periodo.definizione'")[0][0]
    tab = q("select a.oggetto, e.nome, count(distinct a.soggetto), (select count(*) from asserzioni d where d.soggetto=a.oggetto and d.relazione='periodo.definizione') "
            "from asserzioni a join entita e on e.id=a.oggetto where a.relazione='produzione.periodo' group by a.oggetto order by 3 desc limit 25")
    righe += ['', '## Periodi', '',
              f'Periodi citati dai cataloghi e riconosciuti: {n_per} · pezzi con almeno un periodo collegato: {n_pez} · '
              f'definizioni PeriodO collegate a un periodo: {n_def}', '',
              '| periodo | pezzi | definizioni PeriodO |', '| --- | ---: | ---: |']
    righe += [f'| {n} ({o[8:]}) | {k} | {d} |' for o, n, k, d in tab]
    if errori:
        righe += ['', '## Fuori accordo', ''] + [f'- {k}: {v}' for k, v in errori.most_common()]
    (RADICE / 'out/asserzioni.md').write_text('\n'.join(righe) + '\n', encoding='utf-8')
    print('\n'.join(righe))


if __name__ == '__main__':
    sys.path.insert(0, str(ATLANTE / 'src'))
    costruisci(sys.argv[1:] or ['blu', 'lacca'])
