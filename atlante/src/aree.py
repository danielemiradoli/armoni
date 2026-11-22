"""Estensione dei luoghi che hanno un'area (paesi, regioni, zone, continenti), per l'alone sulla mappa.

Fonte: superficie su Wikidata (P2046, query in data/query/aree.rq, CSV in data/raw/aree.csv).
Dove manca, l'area del paese di oggi che contiene il punto (confini 2010 di historical-basemaps),
calcolata in proiezione sinusoidale (equivalente). Le città restano escluse: su Wikidata la loro
superficie è quella amministrativa, che per molte città cinesi comprende un'intera prefettura
(Zhangzhou 12.880 km², Parigi 105 km²) e darebbe aloni fuorvianti.
Uscita: web/aree.json {qid: {km2, fonte}}."""
import csv, json, math
from pathlib import Path

from shapely.geometry import Point, shape
from shapely.ops import transform

ROOT = Path(__file__).resolve().parent.parent
R = 6371.0088


def sinusoidale(lon, lat, z=None):
    return R * math.radians(lon) * math.cos(math.radians(lat)), R * math.radians(lat)


def main():
    wd = {r['x'].rsplit('/', 1)[-1]: float(r['m2']) / 1e6 for r in csv.DictReader(open(ROOT / 'data/raw/aree.csv', encoding='utf-8'))}
    geo = [(shape(f['geometry']), f['properties'].get('NAME')) for f in
           json.load(open(ROOT / 'data/raw/confini/world_2010.geojson', encoding='utf-8'))['features'] if f.get('geometry')]
    voci = {}  # qid -> (lon, lat)
    for l in json.load(open(ROOT / 'web/luoghi.json', encoding='utf-8')):
        if l['precisione'] in ('paese', 'regione', 'zona') and l.get('qid'):
            voci[l['qid']] = (float(l['lon']), float(l['lat']))
    for e in json.load(open(ROOT / 'web/contesti.json', encoding='utf-8'))['elementi']:
        for l in e['luoghi']:
            if l['precisione'] in ('paese', 'regione'):
                voci[l['id']] = (l['lon'], l['lat'])
    out, conta = {}, {'wikidata': 0, 'confini 2010': 0, 'nessuna': 0}
    for q, (lon, lat) in voci.items():
        if wd.get(q):
            out[q] = {'km2': round(wd[q]), 'fonte': 'wikidata'}
        else:
            p = Point(lon, lat)
            g = next((g for g, _ in geo if g.covers(p)), None)
            if g is None:
                conta['nessuna'] += 1
                continue
            out[q] = {'km2': round(transform(sinusoidale, g).area), 'fonte': 'confini 2010'}
        conta[out[q]['fonte']] += 1
    json.dump(out, open(ROOT / 'web/aree.json', 'w', encoding='utf-8'), separators=(',', ':'))
    print(len(voci), conta)


if __name__ == '__main__':
    main()
