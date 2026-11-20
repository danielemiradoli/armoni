"""Strato di densita' dal V&A: solo conteggi per luogo e decennio, nessuna scheda singola.

Le condizioni del V&A (sezione 9) ammettono usi non commerciali e vietano di conservare i contenuti
dell'API per piu' di quattro settimane: per questo data/raw/vam.csv non entra nel repository e va
cancellato entro quattro settimane dal prelievo. Leggiamo i conteggi aggregati come misure derivate,
non come contenuti dell'API: e' una nostra interpretazione, non un'autorizzazione del V&A.

Ingresso: data/raw/vam.csv (src/fetch_vam.py). Uscita: web/densita_vam.json."""
import csv, json, re
from collections import Counter, defaultdict
from pathlib import Path

import sys
import pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build import origine, ROOT

CERAMICA = r'porcelain|earthenware|fritware|ceramic|stoneware|faience|tin-glaze|bone china|jasper|majolica|maiolica|stonepaste|soft paste|hard paste|creamware|pearlware|clay'
NON_CERAMICA = r'textile|cotton|silk|paper|watercolour|ink|wool|card|pencil|wood|glass|plastic'
PARTI = {'early': (0, 33), 'mid': (33, 66), 'late': (66, 99), 'first half of': (0, 49), 'second half of': (50, 99),
         'first quarter of': (0, 24), 'second quarter of': (25, 49), 'third quarter of': (50, 74),
         'fourth quarter of': (75, 99), 'last quarter of': (75, 99)}


def intervallo(testo):
    """'ca. 1760-65', '1662-1722', 'mid 18th century', '17th-18th century', 'early 1935' -> (a, b) o None.
    'ca.' allarga di 5 anni per lato. Le date a.C. e i testi non riconosciuti restano senza intervallo."""
    s = testo.lower().replace('(made)', '').strip()
    ca = 5 if re.search(r'\bca\.?|circa|about', s) else 0
    m = re.search(r'(?:(' + '|'.join(PARTI) + r')\s+)?(\d{1,2})(?:st|nd|rd|th)(?:\s*-\s*(\d{1,2})(?:st|nd|rd|th))?\s+century', s)
    if m and 'bc' not in s:
        c1, c2 = int(m.group(2)), int(m.group(3) or m.group(2))
        a, b = (c1 - 1) * 100, c2 * 100 - 1
        if m.group(1) and not m.group(3):
            da, db = PARTI[m.group(1)]
            a, b = a + da, a + db
        return a, b
    m = re.search(r'(\d{3,4})\s*-\s*(\d{1,4})', s)
    if m and 'bc' not in s:
        a, e = m.group(1), m.group(2)
        b = int(a[:len(a) - len(e)] + e) if len(e) < len(a) else int(e)
        a = int(a)
        return (a - ca, b + ca) if a <= b else None
    m = re.search(r'(\d{3,4})', s)
    if m and 'bc' not in s:
        return int(m.group(1)) - ca, int(m.group(1)) + ca
    return None


def main():
    luoghi = {r['id']: r for r in csv.DictReader(open(ROOT / 'data/luoghi.csv', encoding='utf-8'))}
    v = pd.read_csv(ROOT / 'data/raw/vam.csv', dtype=str).fillna('')
    v.columns = [c.lstrip('_') for c in v.columns]  # itertuples scarta i nomi con '_' iniziale
    v = v[(v.sampleMaterial.str.contains(CERAMICA, case=False) |
           v.objectType.str.contains(r'\btiles?\b|dish|bowl|jar|vase|plate|cup|ewer|bottle|teapot', case=False)) &
          ~v.sampleMaterial.str.contains(NON_CERAMICA, case=False)]
    celle, stato = defaultdict(float), Counter()
    for r in v.itertuples(index=False):
        luogo = origine(r.primaryPlace + ' | ' + r.primaryTitle, r.primaryPlace)
        iv = intervallo(r.primaryDate)
        if not luogo:
            stato['senza luogo'] += 1
        if not iv:
            stato['senza data'] += 1
        if not (luogo and iv):
            continue
        stato['collocati'] += 1
        decenni = range(iv[0] // 10 * 10, iv[1] // 10 * 10 + 1, 10)
        for d in decenni:  # peso distribuito: la somma su tutti i decenni vale 1 pezzo
            celle[(luogo, d)] += 1 / len(decenni)
    usati = sorted({l for l, _ in celle})
    out = {'fonte': 'Victoria and Albert Museum, api.vam.ac.uk/v2',
           'criterio': 'ceramiche la cui scheda contiene la frase esatta «underglaze blue» o «blue and white»',
           'licenza': 'condizioni V&A, sezione 9: uso non commerciale; qui solo conteggi aggregati',
           'pezzi': len(v), **{k.replace(' ', '_'): n for k, n in stato.items()},
           'luoghi': [luoghi[k] for k in usati],
           'celle': [{'l': l, 'd': d, 'n': round(n, 3)} for (l, d), n in sorted(celle.items())]}
    (ROOT / 'web/densita_vam.json').write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')
    print({k: v for k, v in out.items() if k not in ('luoghi', 'celle')}, len(out['celle']), 'celle')
    peso = Counter()
    for (l, _), n in celle.items():
        peso[luoghi[l]['precisione']] += n
    print('pezzi collocati per precisione:', {k: round(x) for k, x in peso.items()})


if __name__ == '__main__':
    main()
