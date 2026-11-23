"""Il nucleo comune di ArMoni: fili come configurazione, un lettore per fonte, gazzettieri come dati."""
import re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from armoni import filo  # noqa: E402
from armoni.fonti import LETTORI  # noqa: E402
from armoni.testo import gazzettiere, trova  # noqa: E402

FILI = [p.stem for p in filo.FILI.glob('*.toml')]


def test_ogni_filo_si_carica_e_ogni_fonte_ha_un_lettore():
    assert {'blu', 'lacca'} <= set(FILI)
    for n in FILI:
        cfg = filo.carica(n)
        for chiave in ('nome', 'titolo', 'uscita', 'centri', 'paesi', 'inclusione', 'fonti'):
            assert chiave in cfg, (n, chiave)
        for fonte, fr in cfg['fonti'].items():
            assert fonte in LETTORI, (n, fonte)
            reg = {**cfg['inclusione'], **fr}
            assert reg.get('dichiarato') and reg.get('criterio') and reg.get('testo'), (n, fonte)
            for k in ('dichiarato', 'escludi', 'imitazione', 'salvo'):
                if reg.get(k):
                    re.compile(reg[k])


def test_gazzettieri_validi():
    for g in filo.ATLANTE.parent.joinpath('armoni/gazzettiere').glob('*.csv'):
        for luogo, pat in gazzettiere(g.stem):
            assert luogo and re.compile(pat)


def _includi(n, fonte, **campi):
    cfg = filo.carica(n)
    r = filo.includi({'campi': campi}, {**cfg['inclusione'], **cfg['fonti'][fonte]})
    return r[:2] if r else None


def test_regole_blu():
    assert _includi('blu', 'met', Medium='Porcelain painted in underglaze cobalt blue')[0] == 'documentato'
    assert _includi('blu', 'met', Medium='Tin-glazed earthenware', Title='Plate', **{'Object Name': 'Plate', 'Culture': 'Dutch, Delft'})[0] == 'ipotetico'
    assert _includi('blu', 'met', Medium='Earthenware', Culture='Mexico, Puebla') is None   # Puebla da sola non basta
    assert _includi('blu', 'wd', testo='sky blue glaze bowl') is None                     # monocromo
    assert _includi('blu', 'wd', testo='underglaze blue, sky blue glaze') [0] == 'documentato'
    assert _includi('blu', 'colbase', titolo='色絵皿', parole='染付', categoria='陶磁')[0] == 'ipotetico'
    assert _includi('blu', 'emuseum', **{'명칭': '백자 청화 매화문 항아리'})[1].startswith('blu dichiarato nel nome')


def test_regole_lacca():
    assert _includi('lacca', 'met', Medium='Lacquer on wood, gold maki-e')[0] == 'documentato'
    assert _includi('lacca', 'met', Medium='Nitrocellulose lacquer on canvas') is None
    assert 'imitazione' in _includi('lacca', 'met', Medium='Japanned tinplate')[1]
    assert _includi('lacca', 'emuseum', **{'재질': '나무 - 옻칠', '명칭': '소반'})[1] == 'lacca dichiarata nel materiale: «칠»'


def test_gazzettieri_diversi_per_filo():
    cfg = filo.carica('lacca')
    centri = gazzettiere(*cfg['centri'])
    assert trova(centri, 'Edo period (1615–1868)') is None           # Edo è un'epoca
    assert trova(centri, 'Ryūkyū Islands') == 'Okinawa'
