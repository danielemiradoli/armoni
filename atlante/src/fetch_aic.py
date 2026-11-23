"""Art Institute of Chicago: oggetti la cui tecnica dichiara la lacca (API pubblica, dati CC0).

Uscita: data/raw/aic/lacca.jsonl. Uso: python3 src/fetch_aic.py
"""
import json, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAMPI = ['id', 'title', 'date_start', 'date_end', 'date_display', 'place_of_origin', 'medium_display',
         'artwork_type_title', 'classification_titles', 'material_titles', 'style_title', 'department_title',
         'is_public_domain', 'credit_line']
FRASI = [('medium_display', 'lacquer'), ('material_titles', 'lacquer'), ('medium_display', 'japanned'),
         ('medium_display', 'maki-e'), ('medium_display', 'urushi')]


def pagina(n):
    q = {'query': {'bool': {'should': [{'match_phrase': {k: v}} for k, v in FRASI]}},
         'limit': 100, 'page': n, 'fields': CAMPI}
    r = subprocess.run(['curl', '-sS', '-m', '60', 'https://api.artic.edu/api/v1/artworks/search',
                        '-H', 'Content-Type: application/json',
                        '-H', 'AIC-User-Agent: armoni-atlante (https://danielemiradoli.github.io/armoni/)',
                        '--data-binary', json.dumps(q)], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def main():
    out = ROOT / 'data/raw/aic'; out.mkdir(parents=True, exist_ok=True)
    righe, n = [], 1
    while True:
        d = pagina(n)
        righe += d['data']
        if n >= d['pagination']['total_pages']:
            break
        n += 1
    with open(out / 'lacca.jsonl', 'w', encoding='utf-8') as f:
        for x in righe:
            f.write(json.dumps(x, ensure_ascii=False) + '\n')
    print(len(righe), 'di', d['pagination']['total'])


if __name__ == '__main__':
    main()
