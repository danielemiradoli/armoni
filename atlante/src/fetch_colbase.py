"""Scarica da Japan Search (API di ricerca, banca dati 'cobas' = ColBase, licenza CC BY) gli oggetti
che contengono 染付 (sometsuke) o 青花 (qinghua). Uscita: data/raw/colbase.json, un record per oggetto,
con le parole che lo hanno trovato. Fallisce se i conteggi non tornano."""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = 'https://jpsearch.go.jp/api/item/search/jps-cross'
PAROLE = ['染付', '青花']


def get(params):
    url = API + '?' + urllib.parse.urlencode(params)
    for t in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'armoni-atlante/0.1'}), timeout=90) as r:
                return json.loads(r.read().decode('utf-8'))
        except Exception:
            if t == 3:
                raise
            time.sleep(3 * (t + 1))


def main():
    rec = {}
    for k in PAROLE:
        tot = get({'keyword': k, 'f-db': 'cobas', 'size': 1})['hit']
        visti = 0
        for da in range(0, tot, 100):
            for it in get({'keyword': k, 'f-db': 'cobas', 'size': 100, 'from': da})['list']:
                visti += 1
                if it['id'] in rec:
                    rec[it['id']]['parole'].append(k)
                else:
                    rec[it['id']] = {**it, 'parole': [k]}
            time.sleep(0.5)
        print(f'{k}: attesi {tot}, ricevuti {visti}', file=sys.stderr)
        if visti != tot:
            sys.exit(f'prelievo incompleto per {k}')
    (ROOT / 'data/raw/colbase.json').write_text(json.dumps(list(rec.values()), ensure_ascii=False), encoding='utf-8')
    print(f'{len(rec)} oggetti distinti', file=sys.stderr)


if __name__ == '__main__':
    main()
