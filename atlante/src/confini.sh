#!/bin/sh
# Scarica e semplifica le istantanee dei confini storici di aourednik/historical-basemaps (GPL-3.0).
# Uscita: web/confini/<anno>.json (TopoJSON) e web/confini/anni.json. Richiede mapshaper (npm).
set -e
cd "$(dirname "$0")/.."
COMMIT=${HB_COMMIT:-master}
mkdir -p data/raw/confini web/confini web/confini/fini
ANNI="700 800 900 1000 1100 1200 1279 1300 1400 1492 1500 1530 1600 1650 1700 1715 1783 1800 1815 1880 1900 1914 1920 1930 1938 1945 1960 1994 2010"
for a in $ANNI; do
  f=data/raw/confini/world_$a.geojson
  [ -s "$f" ] || curl -sS -m 120 -o "$f" "https://raw.githubusercontent.com/aourednik/historical-basemaps/$COMMIT/geojson/world_$a.geojson"
  mapshaper -i "$f" -filter-fields NAME -simplify 4% keep-shapes -o format=topojson quantization=1e4 "web/confini/$a.json" 2>/dev/null
  # versione dettagliata, caricata dalla pagina solo quando si ingrandisce molto
  mapshaper -i "$f" -filter-fields NAME -simplify 25% keep-shapes -o format=topojson quantization=1e5 "web/confini/fini/$a.json" 2>/dev/null
done
printf '[%s]\n' "$(echo $ANNI | tr ' ' ',')" > web/confini/anni.json
du -ch web/confini/*.json | tail -1
