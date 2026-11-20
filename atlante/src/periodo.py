"""Strato dei periodi da PeriodO (data/p0d.json, pubblico dominio).

Ogni periodo e' un'asserzione: un'autorita' (libro, banca dati, museo) dice che un nome vale
per una regione fra due anni. Qui si tengono i periodi che toccano le regioni dell'atlante fra
700 e 2000, con la loro autorita' e la lingua in cui sono definiti. Uscita: web/periodo.json."""
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
T0, T1 = 700, 2000
DURATA = (10, 800)  # sotto: eventi (rivolte, guerre); sopra: ere troppo larghe per una corsia
REGIONI = {
    'china': 'Cina', 'korea': 'Corea', 'south korea': 'Corea', 'north korea': 'Corea', 'korean peninsula': 'Corea', 'japan': 'Giappone',
    'vietnam': 'Sud-est asiatico', 'thailand': 'Sud-est asiatico', 'cambodia': 'Sud-est asiatico', 'myanmar': 'Sud-est asiatico',
    'indonesia': 'Sud-est asiatico', 'philippines': 'Sud-est asiatico',
    'iran': 'Iran e Asia centrale', 'iraq': 'Iran e Asia centrale', 'uzbekistan': 'Iran e Asia centrale', 'afghanistan': 'Iran e Asia centrale',
    'india': 'Asia meridionale', 'pakistan': 'Asia meridionale', 'bangladesh': 'Asia meridionale', 'sri lanka': 'Asia meridionale',
    'turkey': 'Anatolia e Mediterraneo', 'syria': 'Anatolia e Mediterraneo', 'egypt': 'Anatolia e Mediterraneo', 'lebanon': 'Anatolia e Mediterraneo',
    'netherlands': 'Europa', 'england': 'Europa', 'united kingdom': 'Europa', 'france': 'Europa', 'italy': 'Europa',
    'germany': 'Europa', 'spain': 'Europa', 'portugal': 'Europa', 'europe': 'Europa',
    'mexico': 'Americhe', 'peru': 'Americhe', 'brazil': 'Americhe',
    'kenya': 'Africa', 'tanzania': 'Africa', 'nigeria': 'Africa', 'morocco': 'Africa', 'africa': 'Africa',
    'east africa': 'Africa', 'west africa': 'Africa', 'mali': 'Africa', 'ethiopia': 'Africa', 'zimbabwe': 'Africa'}


def anno(t):
    i = (t or {}).get('in', {})
    for k in ('year', 'earliestYear', 'latestYear'):
        try:
            return int(i[k])
        except (KeyError, ValueError, TypeError):
            pass
    return None


def autorita(a):
    s = a.get('source', {})
    p = s.get('partOf') or {}
    titolo = s.get('title') or p.get('title') or '—'
    anno_pub = s.get('yearPublished') or p.get('yearPublished') or ''
    chi = [c.get('name', '') for c in (s.get('creators') or p.get('creators') or [])][:2]
    return {'titolo': titolo[:90], 'anno': str(anno_pub)[:4], 'chi': ', '.join(x for x in chi if x)}


def main():
    d = json.load(open(ROOT / 'data/p0d.json', encoding='utf-8'))
    aut, periodi, scarti = {}, [], Counter()
    for aid, a in d['authorities'].items():
        for pid, p in a.get('periods', {}).items():
            s, e = anno(p.get('start')), anno(p.get('stop'))
            if s is None or e is None or e < T0 or s > T1:
                continue
            if not p.get('spatialCoverage'):
                scarti['senza copertura spaziale'] += 1  # es. 'Koryo Dynasty': esiste, ma non dice dove
                continue
            regs = sorted({REGIONI[x['label'].lower()] for x in p.get('spatialCoverage', []) if x.get('label', '').lower() in REGIONI})
            if not regs:
                continue
            if not DURATA[0] <= e - s <= DURATA[1]:
                scarti['durata fuori dai limiti'] += 1
                continue
            aut.setdefault(aid, autorita(a))
            lingua = (p.get('languageTag') or p.get('language', '').rsplit('/', 1)[-1] or '?')[:2]
            for r in regs:
                periodi.append({'r': r, 'n': p.get('label', '')[:80], 'a': s, 'b': e, 'au': aid, 'lg': lingua, 'id': pid})
    out = {'fonte': 'PeriodO, n2t.net/ark:/99152/p0d (pubblico dominio)', 'autorita': aut, 'periodi': periodi}
    (ROOT / 'web/periodo.json').write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')

    righe = ['# PeriodO — chi definisce i periodi delle regioni dell\'atlante (700–2000)', '',
             'Rigenerato da `src/periodo.py`. Lingua = lingua dell\'etichetta del periodo nella fonte.', '',
             '| regione | periodi | autorità | lingue (prime 3) |', '| --- | ---: | ---: | --- |']
    per_r = defaultdict(list)
    for p in periodi:
        per_r[p['r']].append(p)
    for r, ps in sorted(per_r.items(), key=lambda x: -len(x[1])):
        lg = Counter(p['lg'] for p in ps).most_common(3)
        righe.append(f'| {r} | {len(ps)} | {len({p["au"] for p in ps})} | ' + ', '.join(f'{l} {n}' for l, n in lg) + ' |')
    righe += ['', f'Periodi 700–2000 senza copertura spaziale, quindi non assegnabili a una regione: {scarti["senza copertura spaziale"]}.']
    righe += ['', f'Scartati per durata (eventi sotto {DURATA[0]} anni, ere oltre {DURATA[1]}): {scarti["durata fuori dai limiti"]}.']
    (ROOT / 'out/periodo.md').write_text('\n'.join(righe) + '\n', encoding='utf-8')
    print('\n'.join(righe))


if __name__ == '__main__':
    main()
