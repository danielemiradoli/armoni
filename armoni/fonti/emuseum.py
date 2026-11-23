"""eMuseum, i musei pubblici coreani (emuseum.go.kr). File: atlante/data/raw/emuseum[_<filo>]/elenco.jsonl e dettagli.jsonl

Si tengono solo le schede con licenza KOGL tipo 1 (riuso con attribuzione). Le fotografie su lastra di vetro e le
pellicole ritraggono i pezzi, non sono pezzi: escluse. Nazione ed epoca stanno nel campo 국적/시대 («한국 - 조선»);
la scheda nomina l'epoca, non gli anni: gli intervalli sono quelli convenzionali dei manuali, dichiarati come tali.
"""
import json, re
from collections import Counter

from .. import GREZZI

NAZIONI = {'한국': 'Korea', '중국': 'China', '일본': 'Japan', '베트남': 'Vietnam', '아시아': None}
EPOCHE = {'고려': (918, 1392), '조선': (1392, 1897), '대한제국': (1897, 1910), '일제강점': (1910, 1945),
          '광복이후': (1945, 2000), '명': (1368, 1644), '청': (1636, 1912), '원': (1271, 1368),
          '낙랑': (-108, 313), '초기철기': (-300, -100), '원삼국': (1, 300), '삼국': (-57, 668),
          '신라': (-57, 935), '백제': (-18, 660), '고구려': (-37, 668), '가야': (42, 562), '통일신라': (668, 935),
          '발해': (698, 926)}


def schede(ctx):
    cartella = GREZZI / ('emuseum' if ctx.filo == 'blu' else f'emuseum_{ctx.filo}')
    if not (cartella / 'dettagli.jsonl').exists():
        return
    elenco = {json.loads(l)['id']: json.loads(l) for l in open(cartella / 'elenco.jsonl', encoding='utf-8')}
    for l in open(cartella / 'dettagli.jsonl', encoding='utf-8'):
        d = json.loads(l); c = d['campi']; e = elenco.get(d['id'], {})
        if d['licenza_kogl'] != 1:
            ctx.escluso('licenza diversa dal tipo 1'); continue
        cl = c.get('분류', '') + ' ' + c.get('재질', '')
        if '유리건판' in cl + (e.get('numero') or '') or '미디어' in cl:
            ctx.escluso('fotografie e pellicole'); continue
        nome = c.get('명칭') or e.get('titolo', '')
        campi = {**c, '명칭': nome}
        if not ctx.passa(campi):
            continue
        naz, _, epoca = c.get('국적/시대', '').partition(' - ')
        ini, fin = EPOCHE.get(epoca.strip(), (None, None))
        nota = '; date dell\'epoca (convenzionali)' if ini is not None else ''
        tf = c.get('특징', '')
        m = re.search(r'(\d{4})년', tf)
        sec = re.search(r'(\d{1,2})세기', tf)
        if m and 1000 < int(m.group(1)) < 2000:
            ini = fin = int(m.group(1)); nota = f'; anno dichiarato nella descrizione ({m.group(1)}년)'
        elif sec:
            n = int(sec.group(1)); ini, fin = (n - 1) * 100, n * 100 - 1; nota = f'; secolo dichiarato nella descrizione ({n}세기)'
        museo = d.get('museo') or e.get('museo') or ''
        yield dict(campi=campi, id='emu:' + d['id'], fonte='emuseum', titolo=nome, cultura=c.get('국적/시대', ''),
                   data_testo=c.get('국적/시대', ''), inizio=ini, fine=fin,
                   tecnica=' · '.join(x for x in (c.get('재질'), c.get('분류')) if x), classe=c.get('분류', ''),
                   url='https://www.emuseum.go.kr/detail?relicId=' + d['id'],
                   licenza=f'KOGL tipo 1 — fonte: {museo or "e뮤지엄"}, eMuseum (emuseum.go.kr)', wikidata='',
                   origine=NAZIONI.get(naz.strip()) or NAZIONI.get(epoca.strip()), incerto=False,
                   sede='National Museum of Korea' if museo == '국립중앙박물관' else 'Korea',
                   mercato=None, export_senza_meta=False, nota_data=nota, extra={'museo': museo},
                   periodo=epoca.strip(), artefice=c.get('작가', ''))
