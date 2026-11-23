"""Filo 1, la porcellana blu e bianca: ora è una configurazione del nucleo comune (armoni/fili/blu.toml).

Questo file resta come punto d'ingresso dell'Atlante e per le metriche del filo. Le regole (che cosa entra, con
quale criterio, come si leggono luoghi e date) stanno nel nucleo: `armoni/fonti/` (un lettore per fonte),
`armoni/gazzettiere/` (i luoghi), `armoni/fili/blu.toml` (il filo), `armoni/filo.py` (il motore).

Uscite: web/opere.json, web/luoghi.json, web/periodi.json, web/copertura.json, out/metrics.md.
"""
import csv, json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent)); sys.path.insert(0, str(Path(__file__).resolve().parent))

from armoni import filo  # noqa: E402
from armoni.testo import anno, trova, mercato, gazzettiere, INCERTO  # noqa: E402,F401  (usati da altri script e dai test)
from armoni.fonti.colbase import intervallo as intervallo_cb  # noqa: E402,F401
from armoni.fonti.wikidata import intervallo as intervallo_wd  # noqa: E402,F401

CENTRI = list(gazzettiere('centri_ceramica'))
PAESI = list(gazzettiere('paesi'))


def origine(testo_centro, testo_paese):
    """Il luogo d'origine letto nel testo con i gazzettieri del filo (usato anche da densita_vam.py)."""
    return trova(CENTRI, testo_centro) or trova(PAESI, testo_paese)


def main():
    r = filo.scrivi('blu')
    json.dump(list(csv.DictReader(open(ROOT / 'data/periodi.csv', encoding='utf-8'))),
              open(ROOT / 'web/periodi.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    scrivi_metriche(r['opere'], r['luoghi'], r['scarti'])


def scrivi_metriche(opere, luoghi, scarti):
    n = len(opere)
    pct = lambda k: f'{k} ({100 * k / n:.1f}%)'
    prec = Counter(luoghi[o['origine']]['precisione'] if o['origine'] else 'nessun luogo' for o in opere)
    righe = ['# Metriche dell\'atlante — taglio «blu e bianco»', '',
             'Rigenerato da `src/build.py` (nucleo: `armoni/fili/blu.toml`). Ogni cifra si ricalcola dai file in `data/`.', '',
             f'Pezzi: **{n}** — Met {sum(o["fonte"] == "met" for o in opere)}, Cleveland {sum(o["fonte"] == "cma" for o in opere)}, '
             f'Wikidata fuori dagli Stati Uniti {sum(o["fonte"] == "wd" for o in opere)}, '
             f'ColBase {sum(o["fonte"] == "colbase" for o in opere)}, eMuseum {sum(o["fonte"] == "emuseum" for o in opere)}.', '',
             '## Inclusione', '', '| grado | pezzi |', '| --- | ---: |']
    righe += [f'| {g} | {pct(k)} |' for g, k in Counter(o['grado'] for o in opere).most_common()]
    righe += ['', '## Precisione del luogo d\'origine', '', '| precisione | pezzi |', '| --- | ---: |']
    righe += [f'| {p} | {pct(k)} |' for p, k in prec.most_common()]
    righe += ['', f'Attribuzione del luogo dichiarata incerta dal catalogo: {pct(sum(o["origine_incerta"] for o in opere))}.']
    righe += ['', f'Senza luogo dichiarato ma con luogo dedotto (Giappone, ColBase/Tokyo, strato separato): {sum(1 for o in opere if o.get("origine_dedotta"))}.']
    righe += ['', '## Origine (prime 15)', '', '| luogo | pezzi |', '| --- | ---: |']
    righe += [f'| {luoghi[o]["nome"] if o else "—"} | {k} |' for o, k in Counter(o['origine'] for o in opere).most_common(15)]
    sedi = Counter(luoghi[o['sede']]['nome'] if o['sede'] else 'sede senza coordinate' for o in opere)
    righe += ['', '## Dove sono conservati', '', '| sede | pezzi |', '| --- | ---: |']
    righe += [f'| {k} | {v} |' for k, v in sedi.most_common(12)]
    righe += ['', f'Origine Wikidata = Repubblica Popolare Cinese per oggetti anteriori al 1949: '
              f'{sum(o.get("origine_anacronistica", False) for o in opere)}.']
    righe += ['', '## Mercati di destinazione dichiarati nel catalogo', '',
              f'Con mercato riconosciuto: {sum(1 for o in opere if o["mercato"])}. '
              f'«Export» senza destinazione: {sum(o["export_senza_meta"] for o in opere)}.', '']
    righe += ['## Date', '', f'Senza intervallo utilizzabile: {scarti["date assenti o invertite"]}.', '',
              '## Licenze', '', '| licenza | pezzi |', '| --- | ---: |']
    righe += [f'| {l} | {k} |' for l, k in Counter(o['licenza'] for o in opere).most_common()]
    (ROOT / 'out/metrics.md').write_text('\n'.join(righe) + '\n', encoding='utf-8')
    print('\n'.join(righe))



if __name__ == '__main__':
    main()
