"""Scarica da Wikidata i tre insiemi usati come campione di riferimento.

Perche' paginato: la query sugli ID MoMA tocca oltre 20.000 item e, con
SERVICE wikibase:label, il servizio SPARQL supera il tempo massimo *mentre
sta gia' scrivendo la risposta*. Il risultato e' un CSV valido e tronco,
senza codice di errore. Un prelievo non paginato del 10/11/2026 aveva reso
12.270 item su 20.350 e sembrava riuscito.

Per questo ogni file e' verificato contro un COUNT(DISTINCT) indipendente:
se il numero di item non coincide, lo script fallisce invece di depositare
dati parziali.
"""
import sys, time, json, pathlib, hashlib, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = ROOT / "data" / "raw"
EP = "https://query.wikidata.org/sparql"
UA = "ArmoniBot/0.1 (https://github.com/danielemiradoli/armoni)"
PAGE = 4000

LABEL = 'SERVICE wikibase:label { bd:serviceParam wikibase:language "en,it". }'
OPTIONALS = """  OPTIONAL { ?item wdt:P245  ?ulan }
  OPTIONAL { ?item wdt:P214  ?viaf }
  OPTIONAL { ?item wdt:P569  ?birth }
  OPTIONAL { ?item wdt:P570  ?death }"""
COLS = ["item", "itemLabel", "momaId", "tateId", "ulan", "viaf", "birth", "death"]

# nome file -> (vincolo sugli item, righe obbligatorie, righe facoltative)
SETS = {
    "wikidata_gold.csv": ("?i wdt:P2174 ?a ; wdt:P2741 ?b",
                          "  ?item wdt:P2174 ?momaId .\n  ?item wdt:P2741 ?tateId .", ""),
    "wikidata_moma.csv": ("?i wdt:P2174 ?a",
                          "  ?item wdt:P2174 ?momaId .", "  OPTIONAL { ?item wdt:P2741 ?tateId }"),
    "wikidata_tate.csv": ("?i wdt:P2741 ?a",
                          "  ?item wdt:P2741 ?tateId .", "  OPTIONAL { ?item wdt:P2174 ?momaId }"),
}


def _get(query, accept):
    url = EP + "?" + urllib.parse.urlencode({"query": query})
    req = urllib.request.Request(url, headers={"Accept": accept, "User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                return r.read()
        except Exception as e:
            print(f"    tentativo {attempt + 1} fallito: {e}", file=sys.stderr)
            if attempt == 2:
                raise
            time.sleep(10)


def count_items(constraint):
    q = f"SELECT (COUNT(DISTINCT ?i) AS ?n) WHERE {{ {constraint} }}"
    body = json.loads(_get(q, "application/sparql-results+json"))
    return int(body["results"]["bindings"][0]["n"]["value"])


def page(constraint, required, optional, limit, offset):
    return (f"SELECT {' '.join('?' + c for c in COLS)} WHERE {{\n"
            f"  {{ SELECT DISTINCT ?item WHERE {{ {constraint.replace('?i', '?item')} }}\n"
            f"    ORDER BY ?item LIMIT {limit} OFFSET {offset} }}\n"
            f"{required}\n{optional}\n{OPTIONALS}\n  {LABEL}\n}}")


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def fetch(name, constraint, required, optional):
    expected = count_items(constraint)
    print(f"{name}: {expected} item attesi")
    header, rows, offset = None, [], 0
    while offset < expected:
        raw = _get(page(constraint, required, optional, PAGE, offset), "text/csv")
        lines = raw.decode("utf-8").splitlines()
        if header is None:
            header = lines[0]
        elif lines[0] != header:
            raise SystemExit(f"{name}: intestazione cambiata a offset {offset}")
        rows.extend(lines[1:])
        offset += PAGE
        print(f"    offset {offset}: {len(rows)} righe cumulate")
    data = ("\r\n".join([header] + rows) + "\r\n").encode("utf-8")
    got = len({r.split(",")[0] for r in rows})
    if got != expected:
        raise SystemExit(f"{name}: {got} item distinti invece di {expected}. "
                         "Prelievo parziale, nulla depositato.")
    DEST.mkdir(parents=True, exist_ok=True)
    (DEST / name).write_bytes(data)
    print(f"    OK {len(rows)} righe, {got} item, sha256 {sha256(data)}\n")
    return len(rows), got, sha256(data)


if __name__ == "__main__":
    for n, (c, req, opt) in SETS.items():
        fetch(n, c, req, opt)
