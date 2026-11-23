"""Aggiunge la macro-regione a ogni luogo dei fili (web/luoghi.json, web/fili/*/luoghi.json).

Stessa regola dei contesti (contesti.macroregioni): il paese di oggi, confini 2010, che contiene il punto;
così una ricerca «per provenienza» usa le stesse undici regioni per oggetti e fenomeni.
Si esegue dopo build.py e filo_lacca.py."""
import json
from pathlib import Path

from shapely.geometry import shape
from shapely.strtree import STRtree

import contesti

ROOT = Path(__file__).resolve().parent.parent
# punti che la regola non assegna: il centro del paese cade in mare o il nome 2010 manca dalla tabella
A_MANO = {'Indonesia': 'Sud-Est asiatico', 'Okinawa': 'Asia orientale', 'Switzerland': 'Europa'}


def main():
    fs = json.load(open(ROOT / 'data/raw/confini/world_2010.geojson', encoding='utf-8'))['features']
    geo = [(shape(f['geometry']), (f['properties'] or {}).get('NAME')) for f in fs if f.get('geometry')]
    reg = contesti.macroregioni({2010: (STRtree([g for g, _ in geo]), geo)})
    for p in [ROOT / 'web/luoghi.json', *sorted((ROOT / 'web/fili').glob('*/luoghi.json'))]:
        luoghi = json.load(open(p, encoding='utf-8'))
        for l in luoghi:
            l['macroregione'] = reg(float(l['lon']), float(l['lat'])) or A_MANO.get(l['id'])
        json.dump(luoghi, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        senza = [l['id'] for l in luoghi if not l['macroregione']]
        print(p.relative_to(ROOT), len(luoghi), 'luoghi; senza regione:', senza)


if __name__ == '__main__':
    main()
