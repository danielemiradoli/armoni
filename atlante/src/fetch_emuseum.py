"""Porcellana bianca e blu dei musei pubblici coreani, da eMuseum (emuseum.go.kr).

Il Museo nazionale di Corea (risposta del 23/11/2026) indica eMuseum come via d'accesso ai dati:
pubblici, senza account, Korea Open Government License tipo 1 per le sue schede. Le altre
istituzioni del portale possono avere licenze diverse: la licenza si legge scheda per scheda e
build.py tiene solo il tipo 1. L'API ufficiale richiede una chiave di data.go.kr, non ottenibile
dall'Italia; si leggono quindi le pagine pubbliche (robots.txt le consente), lentamente.

Due passi, entrambi ripresi da dove si erano fermati:
  1. elenco: la ricerca «청화백자», 36 schede per pagina (il massimo che il portale accetta);
  2. dettaglio: per ogni scheda, i campi della tabella (nazione/periodo, classificazione, materiale,
     misure, numero) e la licenza.
Uscita: data/raw/emuseum/elenco.jsonl, data/raw/emuseum/dettagli.jsonl (fuori dal repository)."""
import concurrent.futures as cf, html, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / 'data/raw/emuseum'
UA = 'Mozilla/5.0 (compatible; armoni-atlante/0.1; +https://danielemiradoli.github.io/armoni/)'
BASE = 'https://www.emuseum.go.kr'
PAROLA = '청화백자'
RIGHE = 36


def get(url, tentativi=3):
    for i in range(tentativi):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': UA}), timeout=60) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            if i == tentativi - 1:
                raise
            time.sleep(3 * (i + 1))


def testo(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()


def elenco():
    out = DIR / 'elenco.jsonl'
    visti = {json.loads(l)['id'] for l in out.open()} if out.exists() else set()
    prima = get(f'{BASE}/headerSearch?keyword={urllib.parse.quote(PAROLA)}&rows={RIGHE}&pageNum=1')
    totale = int(re.search(r"var total = parseInt\('(\d+)'", prima).group(1))
    pagine = -(-totale // RIGHE)
    print('schede annunciate', totale, 'pagine', pagine, 'già lette', len(visti))
    with out.open('a') as f:
        for p in range(max(1, len(visti) // RIGHE), pagine + 1):  # si riparte dalla pagina dove ci si era fermati
            if len(visti) >= totale:
                break
            t = prima if p == 1 else get(f'{BASE}/headerSearch?keyword={urllib.parse.quote(PAROLA)}&rows={RIGHE}&pageNum={p}')
            for m in re.finditer(r'<div class="item">(.*?)id="linkI_(PS\w+)"', t, re.S):
                blocco, rid = m.group(1), m.group(2)
                if rid in visti:
                    continue
                titolo = testo(re.search(r'<div class="title[^"]*">(.*?)</div>', blocco, re.S).group(1))
                li = [testo(x) for x in re.findall(r'<li>(.*?)</li>', blocco, re.S)]
                f.write(json.dumps({'id': rid, 'titolo': titolo, 'museo': li[0] if li else None,
                                    'numero': li[1] if len(li) > 1 else None}, ensure_ascii=False) + '\n')
                visti.add(rid)
            time.sleep(.8)
    print('elenco:', len(visti), 'di', totale)
    return totale


def dettaglio(rid):
    t = get(f'{BASE}/detail?relicId={rid}')
    campi = {testo(k): testo(v) for k, v in re.findall(r'<li>\s*<em>(.*?)</em>\s*<span>(.*?)</span>', t, re.S)}
    lic = re.search(r'제\s*(\d)\s*유형', t)
    museo = re.search(r'<p class="text">(.*?)</p>', t, re.S)
    return {'id': rid, 'campi': campi, 'licenza_kogl': int(lic.group(1)) if lic else None,
            'museo': testo(museo.group(1)).split(' / ')[0] if museo else None}


def dettagli(limite_secondi):
    out = DIR / 'dettagli.jsonl'
    fatti = {json.loads(l)['id'] for l in out.open()} if out.exists() else set()
    ids = [json.loads(l)['id'] for l in (DIR / 'elenco.jsonl').open()]
    da_fare = [i for i in ids if i not in fatti]
    print('dettagli già letti', len(fatti), 'da leggere', len(da_fare))
    t0 = time.time()
    with out.open('a') as f, cf.ThreadPoolExecutor(5) as ex:  # cinque richieste alla volta, non di più
        for i in range(0, len(da_fare), 30):
            if time.time() - t0 > limite_secondi:
                break
            for r in ex.map(dettaglio, da_fare[i:i + 30]):
                f.write(json.dumps(r, ensure_ascii=False) + '\n')
            f.flush()
            time.sleep(.5)
    fatti = sum(1 for _ in out.open())
    print('dettagli letti in tutto:', fatti, 'di', len(ids))
    return fatti >= len(ids)


if __name__ == '__main__':
    DIR.mkdir(parents=True, exist_ok=True)
    if sys.argv[1:] == ['elenco']:
        elenco()
    else:
        dettagli(float(sys.argv[2]) if len(sys.argv) > 2 else 500)
