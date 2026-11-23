"""Scarica da Wikidata (CC0) i concetti di periodo: periodi storici, dinastie, ere, regni, stati storici, imperi,
con date e con le etichette e gli alias in molte lingue. È il vocabolario universale con cui la base riconosce i
periodi che le fonti scrivono ognuna nella sua lingua (Edo period, 江戸時代, 에도 시대, periodo Edo…).

Uscita: armoni/dati/periodi_wikidata.json. Uso: python3 -m armoni.scarica_periodi
"""
import csv, io, json, subprocess, time
from pathlib import Path

CLASSI = {'Q11514315': 'periodo storico', 'Q164950': 'dinastia', 'Q12857432': 'dinastia cinese', 'Q50068795': 'stato storico cinese',
          'Q1089515': 'dinastia di conquista', 'Q7310094': 'regno (periodo)', 'Q24706': 'nome di era giapponese',
          'Q6428674': 'era', 'Q3024240': 'paese storico', 'Q48349': 'impero', 'Q12759805': 'sultanato'}
LINGUE = ['it', 'en', 'fr', 'de', 'es', 'pt', 'nl', 'ja', 'ko', 'zh', 'zh-hant', 'vi', 'fa', 'ar', 'tr', 'ru', 'hi']
UA = 'armoni/0.1 (https://danielemiradoli.github.io/armoni/)'
OUT = Path(__file__).resolve().parent / 'dati/periodi_wikidata.json'


def sparql(q):
    for t in range(3):
        r = subprocess.run(['curl', '-sS', '-m', '240', '-G', 'https://query.wikidata.org/sparql', '--data-urlencode', f'query={q}',
                            '-H', 'Accept: text/csv', '-H', f'User-Agent: {UA}'], capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.startswith(('p,', 'p\r', 'p\n', 'p,')) or r.stdout[:2] == 'p,':
            return list(csv.DictReader(io.StringIO(r.stdout)))
        time.sleep(5 * (t + 1))
    raise RuntimeError(r.stdout[:300] + r.stderr[:300])


def main():
    per = {}
    for cl, nome in CLASSI.items():
        righe = sparql(f'''SELECT ?p ?s ?e WHERE {{ ?p wdt:P31 wd:{cl} .
          OPTIONAL{{?p wdt:P580 ?s1}} OPTIONAL{{?p wdt:P571 ?s2}} OPTIONAL{{?p wdt:P582 ?e1}} OPTIONAL{{?p wdt:P576 ?e2}}
          BIND(COALESCE(?s1,?s2) AS ?s) BIND(COALESCE(?e1,?e2) AS ?e) FILTER(BOUND(?s) && BOUND(?e)) }}''')
        for r in righe:
            q = r['p'].rsplit('/', 1)[-1]
            try:
                a, b = int(r['s'][:5].rstrip('-') if r['s'].startswith('-') else r['s'][:4]), int(r['e'][:5].rstrip('-') if r['e'].startswith('-') else r['e'][:4])
            except ValueError:
                continue
            if b < a or b - a > 2000:
                continue
            p = per.setdefault(q, {'qid': q, 'classi': [], 'inizio': a, 'fine': b, 'etichette': {}})
            if nome not in p['classi']:
                p['classi'].append(nome)
        print(nome, len(righe), '→', len(per))
    ids = sorted(per)
    for i in range(0, len(ids), 300):
        vals = ' '.join('wd:' + q for q in ids[i:i + 300])
        filtro = ','.join(f'"{l}"' for l in LINGUE)
        for r in sparql(f'''SELECT ?p ?t ?l WHERE {{ VALUES ?p {{ {vals} }}
              {{ ?p rdfs:label ?t }} UNION {{ ?p skos:altLabel ?t }} BIND(LANG(?t) AS ?l) FILTER(?l IN ({filtro})) }}'''):
            p = per[r['p'].rsplit('/', 1)[-1]]
            p['etichette'].setdefault(r['l'], [])
            if r['t'] not in p['etichette'][r['l']]:
                p['etichette'][r['l']].append(r['t'])
        print('etichette', min(i + 300, len(ids)), '/', len(ids))
    OUT.parent.mkdir(exist_ok=True)
    json.dump({'fonte': 'Wikidata (CC0)', 'classi': CLASSI, 'lingue': LINGUE, 'periodi': [per[q] for q in ids]},
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(len(ids), 'periodi')


if __name__ == '__main__':
    main()
