"""Strato del consumo dalla letteratura: numeri ricavati da articoli scientifici, non da cataloghi.

Ogni riga di data/letteratura.csv e' un'asserzione bibliografica: in un sito, fra due anni,
una pubblicazione conta N frammenti (o una percentuale) di un tipo di ceramica, a una pagina o
tabella precisa. Lo script rifiuta righe senza pagina, con sito o fonte sconosciuti, con anni
invertiti o percentuali fuori scala: meglio nessun numero che un numero senza provenienza.
Uscita: web/letteratura.json."""
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def leggi(nome):
    return list(csv.DictReader(open(ROOT / 'data' / nome, encoding='utf-8')))


def valida(righe, siti, fonti):
    errori = []
    for i, r in enumerate(righe, start=2):
        if r['sito_id'] not in siti: errori.append(f'riga {i}: sito sconosciuto «{r["sito_id"]}»')
        if r['fonte_id'] not in fonti: errori.append(f'riga {i}: fonte sconosciuta «{r["fonte_id"]}»')
        if not r['pagina'].strip(): errori.append(f'riga {i}: manca pagina o tabella')
        if not (r['frammenti'].strip() or r['percentuale'].strip()): errori.append(f'riga {i}: né frammenti né percentuale')
        try:
            if int(r['inizio']) > int(r['fine']): errori.append(f'riga {i}: anni invertiti')
        except ValueError:
            errori.append(f'riga {i}: anni non numerici')
        if r['percentuale'].strip() and not 0 <= float(r['percentuale']) <= 100: errori.append(f'riga {i}: percentuale fuori scala')
    return errori


def main():
    siti = {r['id']: r for r in leggi('siti_consumo.csv')}
    fonti = {r['fonte_id']: r for r in leggi('bibliografia.csv')}
    righe = leggi('letteratura.csv')
    errori = valida(righe, siti, fonti)
    if errori:
        sys.exit('\n'.join(errori))
    usati = {r['sito_id'] for r in righe}
    out = {'siti': [siti[k] for k in sorted(usati)], 'fonti': fonti,
           'asserzioni': [{**r, 'inizio': int(r['inizio']), 'fine': int(r['fine'])} for r in righe]}
    (ROOT / 'web/letteratura.json').write_text(json.dumps(out, ensure_ascii=False), encoding='utf-8')
    print(f'{len(righe)} asserzioni da {len({r["fonte_id"] for r in righe})} fonti, {len(usati)} siti')


if __name__ == '__main__':
    main()
