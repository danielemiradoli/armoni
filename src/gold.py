"""Campione di riferimento: i collegamenti MoMA<->Tate fatti a mano su Wikidata.

Serve a misurare precisione e richiamo con un giudice che non e' ne' Claude ne'
Daniele. Tre avvertenze che il codice rende esplicite invece di nasconderle:

1. L'ID Tate su Wikidata (P2741) e' uno SLUG, non un numero: 'berthe-morisot-1663'.
   La chiave di join con artist_data.csv e' il numero finale.
2. Il campione copre solo gli artisti che qualcuno ha avuto motivo di collegare:
   i famosi, i facili. Meta' delle coppie riguarda artisti MoMA mai esposti nella
   finestra 1929-1989. Il richiamo si calcola sulle coppie VALUTABILI e le escluse
   si dichiarano insieme al risultato.
3. Il campione si divide in due meta' con criterio deterministico: si tara sulla
   prima e si pubblicano i numeri della seconda. Altrimenti si riportano numeri
   tarati su se' stessi.
"""
from __future__ import annotations
import re, csv, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
TATE_NUM = re.compile(r"(\d+)$")


def load_pairs() -> set[tuple[str, str]]:
    """Coppie (momaId, tateId numerico) dal campione d'oro."""
    pairs = set()
    with open(RAW / "wikidata_gold.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            moma, slug = row["momaId"].strip(), row["tateId"].strip()
            m = TATE_NUM.search(slug)
            if moma and m:
                pairs.add((moma, m.group(1)))
    return pairs


def load_external_ids() -> dict[str, dict]:
    """ULAN e VIAF per ciascun ID MoMA e ciascun ID Tate numerico.

    Chiavi: ('moma', id) e ('tate', id). Un item puo' avere piu' valori:
    si tengono tutti, perche' il confronto deve poter dire 'si sovrappongono'.
    """
    out = collections.defaultdict(lambda: {"ulan": set(), "viaf": set()})
    for fn, col, norm in (("wikidata_moma.csv", "momaId", lambda s: s),
                          ("wikidata_tate.csv", "tateId",
                           lambda s: (TATE_NUM.search(s).group(1) if TATE_NUM.search(s) else ""))):
        src = "moma" if col == "momaId" else "tate"
        with open(RAW / fn, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                k = norm(row[col].strip())
                if not k:
                    continue
                for field in ("ulan", "viaf"):
                    v = row[field].strip()
                    if v:
                        out[(src, k)][field].add(v)
    return dict(out)


def evaluable(pairs, moma_ids: set[str], tate_ids: set[str]):
    """Coppie d'oro in cui ENTRAMBI gli ID compaiono nei roster che usiamo."""
    return {p for p in pairs if p[0] in moma_ids and p[1] in tate_ids}


def half(pair, names: dict) -> str:
    """Divisione deterministica: iniziale del cognome Tate.

    'taratura' = A-L, 'riporto' = M-Z. Chi non ha cognome leggibile va in taratura,
    cosi' il lato su cui si pubblicano i numeri resta il piu' pulito.
    """
    n = names.get(pair[1], "")
    c = n.strip()[:1].lower()
    return "riporto" if "m" <= c <= "z" else "taratura"


def score(assertions, gold_pairs, which=None, names=None):
    """Precisione e richiamo contro il campione.

    assertions: iterabile di (momaId, tateId, grado).
    L'oro NON e' una verita' completa: su molte nostre asserzioni semplicemente
    tace. 'giudicate' conta solo quelle su cui ha un verdetto, e si riporta
    anche quante restano senza giudice.
    """
    gold = gold_pairs
    if which and names:
        gold = {p for p in gold if half(p, names) == which}
    gold_moma = {p[0] for p in gold}
    gold_tate = {p[1] for p in gold}

    giudicate = corrette = 0
    per_grado = collections.defaultdict(lambda: [0, 0])
    proposte = set()
    for moma, tate, grado in assertions:
        if which and names:
            # si giudica solo cio' che ricade nella meta' considerata
            if not (moma in gold_moma or tate in gold_tate):
                continue
        proposte.add((moma, tate))
        if moma in gold_moma or tate in gold_tate:
            giudicate += 1
            ok = (moma, tate) in gold
            corrette += ok
            per_grado[grado][0] += ok
            per_grado[grado][1] += 1

    mancate = gold - proposte
    return {
        "oro": len(gold),
        "giudicate": giudicate,
        "corrette": corrette,
        "precisione": 100.0 * corrette / giudicate if giudicate else float("nan"),
        "richiamo": 100.0 * len(gold & proposte) / len(gold) if gold else float("nan"),
        "mancate": mancate,
        "per_grado": {g: tuple(v) for g, v in per_grado.items()},
    }


def report(s, titolo):
    print(f"\n{titolo}")
    print(f"  coppie d'oro ................ {s['oro']}")
    print(f"  asserzioni giudicate ........ {s['giudicate']}")
    print(f"    corrette .................. {s['corrette']}")
    print(f"    sbagliate ................. {s['giudicate'] - s['corrette']}")
    print(f"  PRECISIONE .................. {s['precisione']:.1f}%")
    print(f"  RICHIAMO .................... {s['richiamo']:.1f}%  ({len(s['mancate'])} mai proposte)")
    for g, (ok, n) in sorted(s["per_grado"].items()):
        print(f"    {g:<11} {ok}/{n}")


def tune(moma, tate, ev, names, r, sims, tols):
    """Griglia su SIM_MIN e TOL. Si tara sulla meta' A-L e si pubblicano i numeri
    della meta' M-Z: un valore scelto e riportato sullo stesso campione misura
    quanto bene si e' tarato, non quanto bene funziona.

    Criterio: F1 sulla meta' di taratura. Precisione e richiamo da soli si
    massimizzano banalmente (nessuna asserzione, o tutte).
    """
    s0, t0 = r.SIM_MIN, r.TOL
    righe = []
    for sim in sims:
        for tol in tols:
            r.SIM_MIN, r.TOL = sim, tol
            a = [(m["subject"]["id"], m["object"]["id"], r.grade(m["sim"], m["verdict"]))
                 for m in r.reconcile(moma, tate)]
            x = score(a, ev, "taratura", names)
            f1 = (0.0 if not (x["precisione"] and x["richiamo"])
                  else 2 * x["precisione"] * x["richiamo"] / (x["precisione"] + x["richiamo"]))
            righe.append((f1, sim, tol, x["precisione"], x["richiamo"]))
    r.SIM_MIN, r.TOL = s0, t0
    return sorted(righe, reverse=True)


# ---------------------------------------------------------------- campione esteso
# Il campione d'oro di sopra contiene solo coppie POSITIVE: dice quando due record
# sono la stessa persona, mai quando sono persone diverse. Per questo non puo'
# misurare la precisione sui casi difficili, e per questo la misura precedente
# saliva al 100% proprio dove il problema diventa duro.
#
# Le negative si ricavano dalla distinzione a livello di item: se l'ID MoMA sta
# sull'item Q_a e l'ID Tate sull'item Q_b con Q_a != Q_b, Wikidata sta affermando
# che sono due persone diverse. E' un'affermazione, non un silenzio.
#
# DUE MODI IN CUI QUESTO CAMPIONE SBAGLIA, da dichiarare ogni volta che lo si usa:
#
# 1. Duo e collettivi. La Tate registra 'Boyd and Evans, Fionnuala and Leslie'
#    come una scheda sola, il MoMA registra Fionnuala Boyd come persona. Gli item
#    sono legittimamente diversi, ma non e' un errore di abbinamento: e' un
#    disaccordo sulla granularita'. Si marcano e si contano a parte.
#
# 2. Duplicati Wikidata non fusi. Due item per la stessa persona danno un falso
#    negativo. Si escludono quelli in cui i due item condividono un ULAN o un
#    VIAF; dove manca l'identificativo su un lato, il dubbio resta e si dichiara.
#
# Il risultato non e' quindi un numero ma un INTERVALLO: contando tutte le
# negative la precisione e' il limite inferiore, contando solo quelle solide e'
# il limite superiore. La verita' sta in mezzo. Il vecchio campione dava 100%,
# che era il limite superiore di un intervallo di cui non mostrava l'altro capo.

DUO = re.compile(r"\band\b|&", re.I)


def load_identities():
    """momaId e tateId -> {item, ulan, viaf}, da Wikidata e dalla colonna
    WikidataID del CSV MoMA (che copre 230 artisti che la query P2174 non vede).
    """
    out = {}
    for fn, col, src, is_tate in (("wikidata_moma.csv", "momaId", "moma", False),
                                  ("wikidata_tate.csv", "tateId", "tate", True)):
        m = collections.defaultdict(lambda: {"item": set(), "ulan": set(), "viaf": set()})
        path = RAW / fn
        if path.exists():
            with open(path, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    k = row[col].strip()
                    if is_tate:
                        g = TATE_NUM.search(k)
                        k = g.group(1) if g else ""
                    if not k:
                        continue
                    m[k]["item"].add(row["item"].strip())
                    for field in ("ulan", "viaf"):
                        if row[field].strip():
                            m[k][field].add(row[field].strip())
        out[src] = dict(m)
    return out


def add_moma_column(ids, moma_csv):
    """La colonna WikidataID del CSV MoMA, non usata dalla pipeline."""
    import pandas as pd
    d = pd.read_csv(moma_csv, encoding="windows-1252", low_memory=False)
    d = d[(d.ExhibitionRole == "Artist") & (d.ConstituentType == "Individual")]
    d = d.dropna(subset=["ConstituentID"]).drop_duplicates("ConstituentID")
    for row in d.itertuples():
        if pd.notna(row.WikidataID):
            cid = str(int(row.ConstituentID))
            ids["moma"].setdefault(cid, {"item": set(), "ulan": set(), "viaf": set()})
            ids["moma"][cid]["item"].add(str(row.WikidataID).strip())
    return ids


def hard_verdict(a_id, b_id, a_name, b_name, ids):
    """-> 'stessa' | 'diversa' | 'diversa-duo' | 'diversa-incerta' | 'muto'.

    'diversa-incerta': item diversi ma almeno un lato senza ULAN ne' VIAF, quindi
    un duplicato Wikidata non si puo' escludere.
    """
    A, B = ids["moma"].get(a_id), ids["tate"].get(b_id)
    if not A or not B:
        return "muto"
    if A["item"] & B["item"]:
        return "stessa"
    if (A["ulan"] & B["ulan"]) or (A["viaf"] & B["viaf"]):
        return "muto"          # stesso identificativo su item diversi: duplicato
    if DUO.search(a_name or "") or DUO.search(b_name or ""):
        return "diversa-duo"
    if not ((A["ulan"] or A["viaf"]) and (B["ulan"] or B["viaf"])):
        return "diversa-incerta"
    return "diversa"


def score_hard(assertions, ids):
    """assertions: iterabile di (momaId, tateId, grado, nomeA, nomeB).

    Restituisce i conteggi e l'intervallo di precisione.
    """
    c = collections.Counter()
    per = collections.defaultdict(lambda: collections.Counter())
    for a, b, grado, na, nb in assertions:
        v = hard_verdict(a, b, na, nb, ids)
        c[v] += 1
        per[grado][v] += 1
    pos = c["stessa"]
    neg_tutte = c["diversa"] + c["diversa-incerta"] + c["diversa-duo"]
    inf = 100.0 * pos / (pos + neg_tutte) if pos + neg_tutte else float("nan")
    sup = 100.0 * pos / (pos + c["diversa"]) if pos + c["diversa"] else float("nan")
    return {"conteggi": c, "per_grado": per, "inf": inf, "sup": sup}


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    import reconcile as r

    moma, tate = r.load_moma(), r.load_tate()
    names = dict(zip(tate.id, tate.name))
    pairs = load_pairs()
    ev = evaluable(pairs, set(moma.id), set(tate.id))

    print(f"coppie d'oro distinte ......... {len(pairs)}")
    print(f"  momaId nel roster mostre .... {len({p[0] for p in pairs} & set(moma.id))}")
    print(f"  tateId nel roster Tate ...... {len({p[1] for p in pairs} & set(tate.id))}")
    print(f"  COPPIE VALUTABILI ........... {len(ev)} = {100*len(ev)/len(pairs):.1f}%")
    c = collections.Counter(half(p, names) for p in ev)
    print(f"  meta' taratura / riporto .... {c['taratura']} / {c['riporto']}")

    tutte = r.reconcile(moma, tate)
    # Si misura la PRECISIONE DELLE AFFERMAZIONI DI IDENTITA'. Le 'differentFrom'
    # non affermano un'identita': contarle fra gli errori misurerebbe il contrario
    # di cio' che dicono.
    ms_same = [m for m in tutte if m.get("relation", "sameAs") == "sameAs"]
    ms_diff = [m for m in tutte if m.get("relation") == "differentFrom"]
    asserts = [(m["subject"]["id"], m["object"]["id"], m["certainty"]) for m in ms_same]
    report(score(asserts, ev), "=== CAMPIONE POSITIVO, TUTTO ===")
    report(score(asserts, ev, "riporto", names), "=== CAMPIONE POSITIVO, META' DI RIPORTO ===")

    ids = add_moma_column(load_identities(),
                          ROOT / "data" / "sources" / "moma-exhibitions"
                          / "MoMAExhibitions1929to1989.csv")
    quint = [(m["subject"]["id"], m["object"]["id"], m["certainty"],
              m["subject"]["name"], m["object"]["name"]) for m in ms_same]
    h = score_hard(quint, ids)
    print("\n=== CAMPIONE ESTESO (giudica anche i casi difficili) ===")
    for k in ("stessa", "diversa", "diversa-incerta", "diversa-duo", "muto"):
        print(f"  {k:<16} {h['conteggi'][k]}")
    print(f"  PRECISIONE delle sameAs fra {h['inf']:.1f}% e {h['sup']:.1f}%")
    hd = score_hard([(m["subject"]["id"], m["object"]["id"], m["certainty"],
                      m["subject"]["name"], m["object"]["name"]) for m in ms_diff], ids)
    cd = hd["conteggi"]
    print(f"\n  differentFrom emesse: {len(ms_diff)}"
          f"  -> confermate diverse {cd['diversa']+cd['diversa-incerta']+cd['diversa-duo']},"
          f" smentite (stessa persona) {cd['stessa']}, non giudicate {cd['muto']}")
    print(f"\n  {'grado':<12} {'stessa':>7} {'diversa':>8} {'incerta':>8} {'duo':>5} {'muto':>6}")
    for gr in ("certo", "probabile", "possibile", "contestato"):
        p = h["per_grado"][gr]
        if sum(p.values()):
            print(f"  {gr:<12} {p['stessa']:>7} {p['diversa']:>8} "
                  f"{p['diversa-incerta']:>8} {p['diversa-duo']:>5} {p['muto']:>6}")
