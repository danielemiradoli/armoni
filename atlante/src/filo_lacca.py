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
import tipi  # noqa: E402
import build  # noqa: E402  (anno, trova, mercato, PAESI, INCERTO, SEDI)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'web/fili/lacca'

# Lacca vera (urushi, lacca cinese, thitsi birmano), lacca persiana e indiana (pittura sotto vernice: i musei
# la chiamano lacquer), maque messicano. 'Lacquer' nei musei moderni è anche vernice industriale: quei
# dipartimenti restano fuori (vedi ESCLUSI).
LACCA = re.compile(r'\blacquer(?:ed|ware|work)?\b|\burushi\b|maki-?e\b|\bmaque\b|\bthitsi\b', re.I)
IMITA = re.compile(r'\bjapann(?:ed|ing)\b|vernis martin|lacca povera|lacca contraffatta', re.I)
ESCLUSI = {'Modern and Contemporary Art', 'Photographs', 'Drawings and Prints',
           'Contemporary Art', 'Prints and Drawings', 'Photography and Media'}  # Met e Chicago
NON_LACCA = re.compile(r'nitrocellulose|automotive|spray|lacquer on canvas|nail|'
                       # filo metallico: carta laccata avvolta su un'anima, dentro un tessuto (kinran, broccati)
                       r'lacquered[- ]paper[- ]strip|lacquered paper.{0,60}(?:weave|wrapped|thread)', re.I)

# Centri della lacca: solo nomi che non sono anche nomi d'epoca (niente Edo, Kamakura, Momoyama).
CENTRI = [('Bali', r'\bbali\b'), ('Sumatra', r'sumatra'), ('Kyoto', r'kyoto'), ('Wajima', r'wajima'), ('Kanazawa', r'kanazawa|\bkaga\b'), ('Aizu', r'\baizu'),
          ('Nara', r'\bnara\b'), ('Tokyo', r'tokyo'), ('Nagasaki', r'nagasaki'), ('Okinawa', r'ry[uū]ky[uū]|okinawa'),
          ('Beijing', r'beijing|peking'), ('Suzhou', r'suzhou'), ('Yangzhou', r'yangzhou'), ('Fuzhou', r'fuzhou'),
          ('Guangzhou', r'guangzhou|canton'), ('Tongyeong', r'tongyeong'), ('Bagan', r'\bbagan|\bpagan'),
          ('Isfahan', r'isfahan'), ('Shiraz', r'shiraz'), ('Tehran', r'tehran'), ('Kashmir', r'kashmir'),
          ('Sindh', r'sindh'), ('Olinalá', r'olinal'), ('Pátzcuaro', r'p[aá]tzcuaro'), ('Uruapan', r'uruapan'),
          ('Paris', r'\bparis\b'), ('Venice', r'venice|venetian'), ('Spa', r'\bspa\b'), ('Pontypool', r'pontypool'),
          ('Birmingham', r'birmingham'), ('London', r'london'), ('Braunschweig', r'brunswick|braunschweig|stobwasser'),
          ('Fedoskino', r'fedoskino'), ('Palekh', r'palekh')]
PAESI = build.PAESI + [('Ecuador', r'\becuador'), ('Tibet', r'\btibet'), ('Cambodia', r'\bcambod|\bkhmer'), ('Mexico', r'\bmexic')]


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


def da_aic(path):
    if not path.exists():
        return
    for l in open(path, encoding='utf-8'):
        d = json.loads(l)
        if d['department_title'] in ESCLUSI:
            continue
        grado, crit, imit = inclusione(d['medium_display'] or '')
        if not grado:
            continue
        luogo = d['place_of_origin'] or ''
        yield dict(id='aic:%d' % d['id'], fonte='aic', titolo=d['title'], cultura=luogo,
                   data_testo=d['date_display'] or '', inizio=d['date_start'], fine=d['date_end'],
                   tecnica=d['medium_display'], classe=d['artwork_type_title'] or '',
                   testo_centro=' | '.join([luogo, d['title'] or '', d['style_title'] or '']),
                   testo_paese=' | '.join([luogo, d['style_title'] or '']),
                   grado=grado, criterio=crit, imitazione=imit,
                   url='https://www.artic.edu/artworks/%d' % d['id'],
                   licenza='metadati CC0' + ('' if d['is_public_domain'] else '; immagine non di pubblico dominio'),
                   wikidata='')


# eMuseum: epoche coreane oltre a quelle del primo filo (build.EPOCHE_KO). Intervalli convenzionali dei manuali,
# non dichiarati nella scheda: la scheda dichiara solo il nome dell'epoca.
EPOCHE_KO = {**build.EPOCHE_KO, '낙랑': (-108, 313), '초기철기': (-300, -100), '원삼국': (1, 300), '삼국': (-57, 668),
             '신라': (-57, 935), '백제': (-18, 660), '고구려': (-37, 668), '가야': (42, 562), '통일신라': (668, 935),
             '발해': (698, 926)}
LACCA_KO = re.compile(r'칠|漆|나전|螺鈿')


ESCLUSI_EMU = Counter()


def da_emuseum(cartella):
    if not (cartella / 'dettagli.jsonl').exists():
        return
    elenco = {json.loads(l)['id']: json.loads(l) for l in open(cartella / 'elenco.jsonl', encoding='utf-8')}
    conta = Counter()
    for l in open(cartella / 'dettagli.jsonl', encoding='utf-8'):
        d = json.loads(l); c = d['campi']; e = elenco.get(d['id'], {})
        if d['licenza_kogl'] != 1:
            conta['licenza diversa dal tipo 1'] += 1; continue
        cl = c.get('분류', '') + ' ' + c.get('재질', '')
        if '유리건판' in cl + (e.get('numero') or '') or '미디어' in cl:
            conta['fotografie e pellicole'] += 1; continue
        nome = c.get('명칭') or e.get('titolo', '')
        m = LACCA_KO.search(c.get('재질', '')) or LACCA_KO.search(nome)
        if not m:
            conta['lacca non dichiarata'] += 1; continue
        naz, _, epoca = c.get('국적/시대', '').partition(' - ')
        ini, fin = EPOCHE_KO.get(epoca.strip(), (None, None))
        museo = d.get('museo') or e.get('museo') or ''
        conta['tenute'] += 1
        dove = 'materiale' if LACCA_KO.search(c.get('재질', '')) else 'nome'
        yield dict(id='emu:' + d['id'], fonte='emuseum', titolo=nome, cultura=c.get('국적/시대', ''),
                   data_testo=c.get('국적/시대', ''), inizio=ini, fine=fin,
                   tecnica=' · '.join(x for x in (c.get('재질'), c.get('분류')) if x), classe=c.get('분류', ''),
                   testo_centro='', testo_paese='',
                   grado='documentato', criterio=f'lacca dichiarata nel {dove}: «{m.group(0)}»'
                   + ('; date dell\'epoca (convenzionali)' if ini is not None else ''),
                   imitazione=False, url='https://www.emuseum.go.kr/detail?relicId=' + d['id'],
                   licenza=f'KOGL tipo 1 — fonte: {museo or "e뮤지엄"}, eMuseum (emuseum.go.kr)', wikidata='',
                   _origine=build.NAZIONI_KO.get(naz.strip()) or build.NAZIONI_KO.get(epoca.strip()),
                   _sede='National Museum of Korea' if museo == '국립중앙박물관' else 'Korea')
    print('eMuseum (lacca):', dict(conta)); ESCLUSI_EMU.update(conta)


def main():
    luoghi = {r['id']: r for r in csv.DictReader(open(ROOT / 'data/luoghi.csv', encoding='utf-8'))}
    opere, scarti, senza_coord = [], Counter(), Counter()
    for rec in list(da_met(ROOT / 'data/raw/MetObjects.csv')) + list(da_cma(ROOT / 'data/raw/cma_data.csv')) + list(da_aic(ROOT / 'data/raw/aic/lacca.jsonl')) + list(da_emuseum(ROOT / 'data/raw/emuseum_lacca')):
        o = rec.pop('_origine') if '_origine' in rec else origine(rec.pop('testo_centro'), rec.pop('testo_paese'))
        rec.pop('testo_centro', None); rec.pop('testo_paese', None); sede = rec.pop('_sede', None)
        if o and o not in luoghi:
            senza_coord[o] += 1; o = None
        if rec['inizio'] is None or rec['fine'] is None or rec['inizio'] > rec['fine']:
            scarti['date assenti o invertite'] += 1
            rec['inizio'] = rec['fine'] = None
        mk, export = build.mercato(rec['cultura'])
        rec.update(origine=o, origine_incerta=bool(build.INCERTO.search(rec['cultura'])), sede=sede or {**build.SEDI, 'aic': 'Art Institute of Chicago'}[rec['fonte']],
                   mercato=mk if mk in luoghi else None, export_senza_meta=export)
        opere.append(rec)
    for rec in opere:  # tipo di oggetto: lettura per parole chiave del nome (src/tipi.py), non dato della fonte
        rec['tipo'], rec['tipo_parola'] = tipi.tipo(rec['titolo'], rec.get('classe'))
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / 'opere.json', 'w', encoding='utf-8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(o, ensure_ascii=False) for o in opere) + '\n]\n')
    import copertura; copertura.scrivi(OUT, opere, ESCLUSI_EMU)
    usati = {o['origine'] for o in opere} | {o['sede'] for o in opere} | {o['mercato'] for o in opere}
    json.dump([luoghi[k] for k in sorted(x for x in usati if x)], open(OUT / 'luoghi.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)

    n = len(opere)
    paesi = Counter(o['origine'] or '(senza luogo)' for o in opere)
    secoli = Counter((o['inizio'] // 100 + 1) if o['inizio'] is not None else None for o in opere)
    righe = ['# Filo 2: la lacca — metriche', '',
             f'Pezzi: **{n}** — Met {sum(o["fonte"] == "met" for o in opere)}, Cleveland {sum(o["fonte"] == "cma" for o in opere)}, Chicago {sum(o["fonte"] == "aic" for o in opere)}, eMuseum {sum(o["fonte"] == "emuseum" for o in opere)}; '
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
