"""Secondo filo: la lacca nel mondo.

Stesso metodo del primo filo (build.py): un pezzo entra solo se il catalogo dichiara la lacca
nel materiale o nella tecnica; il luogo è quello scritto nel record (centro, altrimenti paese).
Le imitazioni europee (japanning, vernis) entrano come tali: il record dice «japanned», non «lacquer».

Uscite: web/fili/lacca/opere.json, web/fili/lacca/luoghi.json, out/filo_lacca.md
"""
import csv, json, re, sys
from collections import Counter
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402  (anno, trova, mercato, PAESI, INCERTO, SEDI)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'web/fili/lacca'

# Lacca vera (urushi, lacca cinese, thitsi birmano), lacca persiana e indiana (pittura sotto vernice: i musei
# la chiamano lacquer), maque messicano. 'Lacquer' nei musei moderni è anche vernice industriale: quei
# dipartimenti restano fuori (vedi ESCLUSI).
LACCA = re.compile(r'\blacquer(?:ed|ware|work)?\b|\burushi\b|maki-?e\b|\bmaque\b|\bthitsi\b', re.I)
IMITA = re.compile(r'\bjapann(?:ed|ing)\b|vernis martin|lacca povera|lacca contraffatta', re.I)
ESCLUSI = {'Modern and Contemporary Art', 'Photographs', 'Drawings and Prints'}
NON_LACCA = re.compile(r'nitrocellulose|automotive|spray|lacquer on canvas|nail', re.I)

# Centri della lacca: solo nomi che non sono anche nomi d'epoca (niente Edo, Kamakura, Momoyama).
CENTRI = [('Kyoto', r'kyoto'), ('Wajima', r'wajima'), ('Kanazawa', r'kanazawa|\bkaga\b'), ('Aizu', r'\baizu'),
          ('Nara', r'\bnara\b'), ('Tokyo', r'tokyo'), ('Nagasaki', r'nagasaki'), ('Okinawa', r'ry[uū]ky[uū]|okinawa'),
          ('Beijing', r'beijing|peking'), ('Suzhou', r'suzhou'), ('Yangzhou', r'yangzhou'), ('Fuzhou', r'fuzhou'),
          ('Guangzhou', r'guangzhou|canton'), ('Tongyeong', r'tongyeong'), ('Bagan', r'\bbagan|\bpagan'),
          ('Isfahan', r'isfahan'), ('Shiraz', r'shiraz'), ('Tehran', r'tehran'), ('Kashmir', r'kashmir'),
          ('Sindh', r'sindh'), ('Olinalá', r'olinal'), ('Pátzcuaro', r'p[aá]tzcuaro'), ('Uruapan', r'uruapan'),
          ('Paris', r'\bparis\b'), ('Venice', r'venice|venetian'), ('Spa', r'\bspa\b'), ('Pontypool', r'pontypool'),
          ('Birmingham', r'birmingham'), ('London', r'london'), ('Braunschweig', r'brunswick|braunschweig|stobwasser'),
          ('Fedoskino', r'fedoskino'), ('Palekh', r'palekh')]
PAESI = build.PAESI + [('Tibet', r'\btibet'), ('Cambodia', r'\bcambod|\bkhmer'), ('Mexico', r'\bmexic')]


def origine(centro, paese):
    return build.trova(CENTRI, centro) or build.trova(PAESI, paese)


def inclusione(testo):
    if NON_LACCA.search(testo):
        return None, None, False
    m = LACCA.search(testo)
    if m:
        return 'documentato', 'lacca dichiarata nel record: «%s»' % m.group(0), False
    m = IMITA.search(testo)
    if m:
        return 'documentato', 'imitazione europea dichiarata nel record: «%s»' % m.group(0), True
    return None, None, False


def da_met(path):
    m = pd.read_csv(path, dtype=str, low_memory=False).fillna('')
    m = m[~m['Department'].isin(ESCLUSI)]
    m = m[m['Medium'].str.contains(LACCA.pattern + '|' + IMITA.pattern, case=False, regex=True)]
    m.columns = [c.replace(' ', '_') for c in m.columns]
    for r in m.itertuples(index=False):
        d = r._asdict()
        grado, crit, imit = inclusione(d['Medium'])
        if not grado:
            continue
        cult = d['Culture']
        yield dict(id='met:' + d['Object_ID'], fonte='met', titolo=d['Title'] or d['Object_Name'],
                   cultura=cult, data_testo=d['Object_Date'], inizio=build.anno(d['Object_Begin_Date']),
                   fine=build.anno(d['Object_End_Date']), tecnica=d['Medium'], classe=d['Classification'],
                   testo_centro=' | '.join([d['City'], d['State'], d['Region'], cult, d['Title'], d['Period']]),
                   testo_paese=' | '.join([d['Country'], cult.split(',')[0], d['Period'], d['Dynasty']]),
                   grado=grado, criterio=crit, imitazione=imit, url=d['Link_Resource'],
                   licenza='CC0' if d['Is_Public_Domain'] == 'True' else 'metadati CC0; immagine non di pubblico dominio',
                   wikidata=d['Object_Wikidata_URL'].rsplit('/', 1)[-1] if d['Object_Wikidata_URL'] else '')


def da_cma(path):
    c = pd.read_csv(path, dtype=str, low_memory=False).fillna('')
    c = c[c['technique'].str.contains(LACCA.pattern + '|' + IMITA.pattern, case=False, regex=True)]
    for r in c.itertuples(index=False):
        d = r._asdict()
        grado, crit, imit = inclusione(d['technique'])
        if not grado:
            continue
        cult = d['culture']
        yield dict(id='cma:' + d['id'], fonte='cma', titolo=d['title'], cultura=cult,
                   data_testo=d['creation_date'], inizio=build.anno(d['creation_date_earliest']),
                   fine=build.anno(d['creation_date_latest']), tecnica=d['technique'], classe=d['type'],
                   testo_centro=' | '.join([cult, d['title']]), testo_paese=cult.split(',')[0],
                   grado=grado, criterio=crit, imitazione=imit, url=d['url'],
                   licenza='CC0' if d['share_license_status'] == 'CC0' else 'diritti: ' + (d['share_license_status'] or 'non dichiarati'),
                   wikidata='')


def main():
    luoghi = {r['id']: r for r in csv.DictReader(open(ROOT / 'data/luoghi.csv', encoding='utf-8'))}
    opere, scarti, senza_coord = [], Counter(), Counter()
    for rec in list(da_met(ROOT / 'data/raw/MetObjects.csv')) + list(da_cma(ROOT / 'data/raw/cma_data.csv')):
        o = origine(rec.pop('testo_centro'), rec.pop('testo_paese'))
        if o and o not in luoghi:
            senza_coord[o] += 1; o = None
        if rec['inizio'] is None or rec['fine'] is None or rec['inizio'] > rec['fine']:
            scarti['date assenti o invertite'] += 1
            rec['inizio'] = rec['fine'] = None
        mk, export = build.mercato(rec['cultura'])
        rec.update(origine=o, origine_incerta=bool(build.INCERTO.search(rec['cultura'])), sede=build.SEDI[rec['fonte']],
                   mercato=mk if mk in luoghi else None, export_senza_meta=export)
        opere.append(rec)
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / 'opere.json', 'w', encoding='utf-8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(o, ensure_ascii=False) for o in opere) + '\n]\n')
    usati = {o['origine'] for o in opere} | {o['sede'] for o in opere} | {o['mercato'] for o in opere}
    json.dump([luoghi[k] for k in sorted(x for x in usati if x)], open(OUT / 'luoghi.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)

    n = len(opere)
    paesi = Counter(o['origine'] or '(senza luogo)' for o in opere)
    secoli = Counter((o['inizio'] // 100 + 1) if o['inizio'] is not None else None for o in opere)
    righe = ['# Filo 2: la lacca — metriche', '',
             f'Pezzi: **{n}** — Met {sum(o["fonte"] == "met" for o in opere)}, Cleveland {sum(o["fonte"] == "cma" for o in opere)}; '
             f'imitazioni europee dichiarate {sum(o["imitazione"] for o in opere)}; senza date {scarti["date assenti o invertite"]}.', '',
             '| origine | pezzi |', '|---|---|'] + [f'| {k} | {v} |' for k, v in paesi.most_common(30)] + [
             '', '| secolo d\'inizio | pezzi |', '|---|---|'] + [
             f'| {k if k is not None else "—"} | {v} |' for k, v in sorted(secoli.items(), key=lambda t: (t[0] is None, t[0] or 0))]
    if senza_coord:
        righe += ['', 'Luoghi riconosciuti ma senza coordinate in data/luoghi.csv: ' + ', '.join(f'{k} ({v})' for k, v in senza_coord.most_common())]
    (ROOT / 'out/filo_lacca.md').write_text('\n'.join(righe) + '\n', encoding='utf-8')
    print('\n'.join(righe[:3]))
    if senza_coord:
        print(righe[-1])


if __name__ == '__main__':
    main()
