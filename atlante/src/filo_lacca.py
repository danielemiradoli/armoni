"""Filo 2, la lacca nel mondo: ora è una configurazione del nucleo comune (armoni/fili/lacca.toml).

Questo file resta come punto d'ingresso dell'Atlante e per le metriche del filo.
Uscite: web/fili/lacca/opere.json, luoghi.json, copertura.json; out/filo_lacca.md
"""
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent)); sys.path.insert(0, str(Path(__file__).resolve().parent))

from armoni import filo  # noqa: E402
from armoni.testo import trova, gazzettiere  # noqa: E402

_CFG = filo.carica('lacca')
CENTRI = list(gazzettiere(*_CFG['centri']))
PAESI = list(gazzettiere(*_CFG['paesi']))


def origine(centro, paese):
    return trova(CENTRI, centro) or trova(PAESI, paese)


def inclusione(testo):
    """La regola del filo applicata a un testo di tecnica (per i test): (grado, criterio, imitazione)."""
    r = filo.includi({'campi': {'t': testo}}, {**_CFG['inclusione'], 'testo': ['t']})
    return r if r else (None, None, False)


def main():
    r = filo.scrivi('lacca')
    opere, scarti, senza_coord = r['opere'], r['scarti'], r['senza_coord']
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
