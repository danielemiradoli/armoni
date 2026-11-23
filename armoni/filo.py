"""Il motore dei fili: applica un filo (un file `fili/<nome>.toml`) alle fonti e produce le schede per gli strumenti.

Un filo dice soltanto che cosa entra e con quale criterio: per ogni fonte, quali record guardare (prefiltro),
in quali campi cercare la dichiarazione (il blu, la lacca…), che cosa escludere, quali famiglie o manifatture fanno
entrare un pezzo come ipotesi, e con quali gazzettieri leggere il luogo. Tutto il resto (leggere le fonti,
interpretarne le date, i luoghi strutturati, la sede) sta nei lettori, scritti una volta per tutti i fili.

Uso:  python3 -m armoni.filo blu lacca      (scrive le viste dell'Atlante)
"""
import csv, json, re, sys, tomllib
from collections import Counter
from pathlib import Path

from . import ATLANTE
from .fonti import LETTORI
from .testo import INCERTO, gazzettiere, mercato, trova
from . import periodi as PER

FILI = Path(__file__).resolve().parent / 'fili'


def carica(nome):
    return tomllib.load(open(FILI / f'{nome}.toml', 'rb'))


def _re(p):
    return re.compile(p, re.I) if p else None


class Contesto:
    """Ciò che un lettore riceve: il prefiltro del filo per quella fonte, i luoghi, il conteggio delle esclusioni."""

    def __init__(self, filo, regole, luoghi, esclusi):
        self.filo, self.luoghi, self._esclusi = filo, luoghi, esclusi
        self.alcuni = [(c['campo'], _re(c['regex'])) for c in regole.get('alcuni', [])]
        self.nessuno = [(c['campo'], _re(c['regex'])) for c in regole.get('nessuno', [])]

    def passa(self, campi):
        if self.alcuni and not any(r.search(campi.get(c, '') or '') for c, r in self.alcuni):
            return False
        return not any(r.search(campi.get(c, '') or '') for c, r in self.nessuno)

    def prefiltra(self, df):
        """Lo stesso prefiltro, vettoriale, per le fonti tabellari (Met, Cleveland)."""
        if self.alcuni:
            m = False
            for c, r in self.alcuni:
                m = m | df[c].str.contains(r.pattern, case=False, regex=True)
            df = df[m]
        for c, r in self.nessuno:
            df = df[~df[c].str.contains(r.pattern, case=False, regex=True)]
        return df

    def escluso(self, motivo):
        self._esclusi[motivo] += 1


def includi(s, reg):
    """(grado, criterio, imitazione) oppure None. Le regole della fonte prevalgono su quelle del filo."""
    campi = s['campi']
    if reg.get('per_campo'):
        coppie = [(campi.get(c, '') or '', dove) for c, dove in reg['testo']]
    else:
        coppie = [(' | '.join(campi.get(c, '') or '' for c in reg['testo']), 'record')]
    testo = ' | '.join(t for t, _ in coppie)
    if reg.get('escludi') and re.search(reg['escludi'], testo, re.I) and not (reg.get('salvo') and re.search(reg['salvo'], testo)):
        return None
    for t, dove in coppie:
        m = re.search(reg['dichiarato'], t, re.I)
        if m:
            return 'documentato', reg['criterio'].format(m=m.group(0), dove=dove) + s.get('nota_data', ''), False
    if reg.get('imitazione'):
        m = re.search(reg['imitazione'], testo, re.I)
        if m:
            return 'documentato', reg['criterio_imitazione'].format(m=m.group(0)), True
    if reg.get('famiglie'):
        tf = ' | '.join(campi.get(c, '') or '' for c in reg.get('testo_famiglia', reg['testo']))
        f = trova(reg['famiglie'], tf)
        if f:
            return 'ipotetico', reg['criterio_famiglia'].format(f=f), False
    if reg.get('altrimenti') == 'ipotetico':
        return 'ipotetico', reg['criterio_altrimenti'].format(**campi), False
    return None


def costruisci(nome):
    cfg = carica(nome)
    luoghi = {r['id']: r for r in csv.DictReader(open(ATLANTE / 'data/luoghi.csv', encoding='utf-8'))}
    opere, esclusi, scarti, senza_coord = [], Counter(), Counter(), Counter()
    for fonte, fr in cfg['fonti'].items():
        reg = {**cfg['inclusione'], **fr}
        ctx = Contesto(nome, fr, luoghi, esclusi)
        centri = gazzettiere(*fr.get('centri_extra', []), *cfg['centri'])
        paesi = gazzettiere(*fr.get('paesi_extra', []), *cfg['paesi'])
        for s in LETTORI[fonte].schede(ctx):
            inc = includi(s, reg)
            if not inc:
                continue
            grado, criterio, imit = inc
            o = s['origine'] if 'origine' in s else (trova(centri, s['centro']) or trova(paesi, s['paese']))
            if o and o not in luoghi:
                senza_coord[o] += 1; o = None
            ini, fin = s['inizio'], s['fine']
            if ini is None or fin is None or ini > fin:
                scarti['date assenti o invertite'] += 1
                ini = fin = None
            if 'mercato' in s:
                mk, export = s['mercato'], s['export_senza_meta']
            else:
                mk, export = mercato(s['cultura'])
            rec = dict(id=s['id'], fonte=s['fonte'], titolo=s['titolo'], cultura=s['cultura'], data_testo=s['data_testo'],
                       inizio=ini, fine=fin, tecnica=s['tecnica'], classe=s.get('classe', ''), grado=grado, criterio=criterio,
                       imitazione=imit, url=s['url'], licenza=s['licenza'], wikidata=s.get('wikidata', ''),
                       origine=o, origine_incerta=s['incerto'] if s.get('incerto') is not None else bool(INCERTO.search(s['cultura'])),
                       sede=s.get('sede') or fr.get('sede'), mercato=mk if mk in luoghi else None, export_senza_meta=export,
                       **s.get('extra', {}))
            if 'deduci' in s:
                rec.update(s['deduci'](o))
            # dichiarati dal catalogo, conservati per le asserzioni (periodo, artefice); non vanno nelle viste
            rec['_dichiarati'] = {k: s[k] for k in ('periodo', 'dinastia', 'artefice') if s.get(k)}
            # il custode come lo dichiara la fonte (un'istituzione, in qualunque lingua): distinto dalla «sede»,
            # che è il punto sulla mappa scelto per la vista
            rec['_custode'] = (s['custode'] if 'custode' in s else s.get('sede'), s.get('custode_qid'))
            # periodi dichiarati dal catalogo e riconosciuti nel vocabolario comune (armoni/periodi.py): solo i QID
            rec['periodi'] = list(dict.fromkeys(q for k in ('periodo', 'dinastia') for _, q, _ in PER.riconosci(s.get(k, ''), ini, fin) if q))
            opere.append(rec)
    from tipi import tipo  # atlante/src/tipi.py: lettura del tipo di oggetto dal nome
    for rec in opere:
        rec['tipo'], rec['tipo_parola'] = tipo(rec['titolo'], rec.get('classe'))
    return dict(cfg=cfg, opere=opere, luoghi=luoghi, esclusi=esclusi, scarti=scarti, senza_coord=senza_coord)


def scrivi(nome):
    r = costruisci(nome)
    out = ATLANTE / r['cfg']['uscita']
    out.mkdir(parents=True, exist_ok=True)
    viste = [{k: v for k, v in o.items() if not k.startswith('_')} for o in r['opere']]
    with open(out / 'opere.json', 'w', encoding='utf-8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(o, ensure_ascii=False) for o in viste) + '\n]\n')
    usati = {o['origine'] for o in viste} | {o['sede'] for o in viste} | {o['mercato'] for o in viste}
    json.dump([r['luoghi'][k] for k in sorted(x for x in usati if x)], open(out / 'luoghi.json', 'w', encoding='utf-8'),
              ensure_ascii=False, indent=0)
    import copertura
    copertura.scrivi(out, viste, r['esclusi'])
    # i concetti di periodo citati, per le schede (nome, date); condivisi da tutti i fili
    voc, _ = PER.vocabolario()
    cartella = ATLANTE / 'web'
    f = cartella / 'periodi_base.json'
    tutti = json.load(open(f, encoding='utf-8')) if f.exists() else {}
    for q in {q for o in viste for q in o['periodi']}:
        tutti[q] = {'n': PER.etichetta(q), 'a': voc[q]['inizio'], 'b': voc[q]['fine']}
    json.dump(dict(sorted(tutti.items())), open(f, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f"{nome}: {len(viste)} pezzi; esclusi {dict(r['esclusi'])}; senza coordinate {dict(r['senza_coord'])}")
    return r


if __name__ == '__main__':
    sys.path.insert(0, str(ATLANTE / 'src'))
    for n in sys.argv[1:] or ['blu', 'lacca']:
        scrivi(n)
