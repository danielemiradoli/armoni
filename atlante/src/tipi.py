"""Tipo di oggetto, uguale per tutti i fili: una parola italiana ricavata dal nome dell'oggetto nella scheda.

Non è un dato della fonte ma una lettura per parole chiave (inglese, coreano, giapponese, cinese): per questo
ogni pezzo porta anche la parola che l'ha deciso, e chi non corrisponde a nessuna voce resta «non riconosciuto».
L'ordine conta: frammento prima di tutto, poi le forme più specifiche."""
import re

VOCI = [
    ('frammento', r'\bfragments?\b|\bsherds?\b|\bshards?\b|편(?=$|[\s(),])|조각(?=$|[\s(),])|片$|破片|陶片'),
    ('inrō', r'\binr[oō]\b|印籠'),
    ('ornamento', r'netsuke|ojime|ornament|pendant|hairpin|\bcomb\b|\bbeads?\b|brooch|노리개|根付|簪|櫛'),
    ('scrittura', r'writing box|writing table|suzuri|ink ?stone|inkstone|\bbrush\b|water[- ]dropper|연적|벼루|硯|筆|水滴'),
    ('arma e armatura', r'\bswords?\b|scabbard|\bsaddle|armou?r|helmet|stirrup|quiver|dagger|\bbows?\b|arrow|\bspear|shield|shaffron|baton|'
                        r'tsuba|\bsheath|鞍|鐙|刀|兜|鎧|태도|안장'),
    ('strumento musicale', r'\bbiwa\b|\bkoto\b|instrument|\blute\b|\bdrum\b|琵琶|箏|太鼓'),
    ('piastrella', r'\btiles?\b|타일|塼'),
    ('versatore', r'\bewers?\b|\bjugs?\b|pitcher|tea ?pot|kettle|주자|주전자|注子|水注|急須|水指|執壺|水差'),
    ('bottiglia', r'\bbottles?\b|\bflasks?\b|gourd|병$|병\s|瓶|徳利|甁'),
    ('vaso', r'\bvases?\b|\bjars?\b|\bpots?\b|\burns?\b|\bvessel|\bolla\b|tea caddy|항아리|단지|호$|壺|罐|缸|壷|甕|통$|그릇$'),
    ('piatto', r'\bplates?\b|\bdish(?:es)?\b|charger|platter|saucer|접시|皿|盤|盘|楪'),
    ('tazza', r'\bcups?\b|teacup|beaker|\bmugs?\b|잔$|잔\s|盃|杯|猪口|盞'),
    ('ciotola', r'\bbowls?\b|\bbasin|대접|사발|바리|발$|완$|완\s|鉢|碗|椀|盌'),
    ('scatola', r'\bbox(?:es)?\b|\bcase\b|casket|container|cosmetic|\bcanister|kobako|snuff ?box|\bdrawer|상자|함$|합$|함\s|합\s|盒|箱|筥|匣|奩'),
    ('vassoio', r'\btrays?\b|쟁반|盆|소반'),
    ('mobile', r'cabinet|commode|\bchest\b|\btable\b|\bscreen\b|\bdesk\b|\bshelf|\bstand\b|\bstool|\bchair|\bpanel\b|장$|궤$|반$|棚|卓|屏|几|함롱'),
    ('disegno, stampa, pittura', r'\bprints?\b|painting|album leaf|\bscroll|^the actors?\b|초본|도안|\bdrawing\b|圖|畫|画'),
    ('scultura', r'sculpture|\bfigure|statue|figurine|buddha|bodhisattva|불상|像|俑'),
    ('incensiere', r'incense|censer|향로|香炉|香爐'),
]
_RE = [(nome, re.compile(p, re.I)) for nome, p in VOCI]


def tipo(*testi):
    for t in testi:
        t = (t or '').strip()
        if not t:
            continue
        for nome, r in _RE:
            m = r.search(t)
            if m:
                return nome, m.group(0).strip()
    return None, None
