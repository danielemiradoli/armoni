"""Copertura di ogni filo, per la riga in fondo all'atlante: cosa c'è, cosa è stato escluso e perché,
quali fonti mancano. Chiamata da build.py e filo_lacca.py dopo aver scritto le opere."""
import csv, json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MOTIVI = {'licenza diversa dal tipo 1': 'schede coreane con licenza più restrittiva della KOGL tipo 1',
          'fotografia su lastra': 'fotografie su lastra di vetro (ritraggono i pezzi, non sono pezzi)',
          'fotografie e pellicole': 'fotografie e pellicole (ritraggono i pezzi, non sono pezzi)'}


def scrivi(cartella, opere, esclusi_emuseum):
    mancanti = [dict(fonte=r['fonte'], esito=r['esito'], prossimo=r['prossimo_passo'])
                for r in csv.DictReader(open(ROOT / 'data/fonti_mancanti.csv', encoding='utf-8'))]
    esclusi = [dict(motivo=MOTIVI[k], n=v) for k, v in esclusi_emuseum.items() if k in MOTIVI and v]
    d = dict(pezzi=len(opere), senza_data=sum(o['inizio'] is None for o in opere),
             fonti=dict(Counter(o['fonte'] for o in opere).most_common()), esclusi=esclusi, mancanti=mancanti)
    json.dump(d, open(cartella / 'copertura.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
