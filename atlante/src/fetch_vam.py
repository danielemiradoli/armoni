"""Scarica dal V&A (api.vam.ac.uk/v2) gli oggetti la cui scheda contiene le frasi esatte
«underglaze blue» o «blue and white». Uscita: data/raw/vam.csv, una riga per oggetto, con la frase
o le frasi che lo hanno trovato. Fallisce invece di depositare dati parziali."""
import csv, io, json, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = 'https://api.vam.ac.uk/v2/objects/search'
FRASI = ['"underglaze blue"', '"blue and white"']


def get(params, fmt='json'):
    url = API + '?' + urllib.parse.urlencode({**params, 'response_format': fmt})
    for tentativo in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'armoni-atlante/0.1'}), timeout=60) as r:
                return r.read().decode('utf-8')
        except Exception as e:  # rete instabile: riprova, poi fallisce
            if tentativo == 3:
                raise
            time.sleep(3 * (tentativo + 1))


def main():
    righe = {}
    for frase in FRASI:
        attesi = json.loads(get({'q': frase, 'page_size': 1}))['info']['record_count']
        pagine = -(-attesi // 100)
        visti = 0
        for p in range(1, pagine + 1):
            for r in csv.DictReader(io.StringIO(get({'q': frase, 'page_size': 100, 'page': p}, 'csv'))):
                visti += 1
                k = r['systemNumber']
                if k in righe:
                    righe[k]['frasi'] += ' ' + frase
                else:
                    righe[k] = {**r, 'frasi': frase}
            time.sleep(0.3)
        print(f'{frase}: attesi {attesi}, ricevuti {visti}', file=sys.stderr)
        if visti != attesi:
            sys.exit(f'prelievo incompleto per {frase}: {visti} su {attesi}')
    out = ROOT / 'data/raw/vam.csv'
    with open(out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(next(iter(righe.values())).keys()))
        w.writeheader(); w.writerows(righe.values())
    print(f'{len(righe)} oggetti distinti -> {out}', file=sys.stderr)


if __name__ == '__main__':
    main()
