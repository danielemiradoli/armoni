"""Armoni — strato di riconciliazione delle identita' fra collezioni.

Produce ASSERZIONI, non verdetti. Ogni legame porta metodo, prova, grado di certezza.
Un disaccordo fra due istituzioni non viene risolto d'ufficio ne' scartato in silenzio:
viene emesso come asserzione 'contestata'. Caso di riferimento: Milton Avery, nato 1885
per il MoMA e 1893 per la Tate.
"""
from __future__ import annotations
import pandas as pd, unicodedata, re, json, pathlib, collections, datetime
from rapidfuzz import fuzz

VERSION = "0.1.0"
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "data" / "sources", ROOT / "out"
TOL = 3           # anni di tolleranza fra due date che dovrebbero coincidere
SIM_MIN = 85      # similarita' minima del nome per considerare una coppia
STOP = {"jr", "sir", "dame", "the", "of", "and", "om", "ch"}

# ---------------------------------------------------------------- normalizzazione
def tokens(s: str) -> list[str]:
    if not isinstance(s, str):
        return []
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z ]", " ", s.lower())
    return [t for t in s.split() if t not in STOP and len(t) > 1]

def name_key(s: str) -> str:
    return " ".join(sorted(tokens(s)))

def block_key(s: str, comma_form: bool) -> str:
    """Chiave di blocco: il cognome. comma_form=True per 'Cognome, Nome'."""
    t = tokens(s)
    return "" if not t else (t[0] if comma_form else t[-1])

# ---------------------------------------------------------------- caricamento
def load_moma() -> pd.DataFrame:
    d = pd.read_csv(SRC / "moma-exhibitions" / "MoMAExhibitions1929to1989.csv",
                    encoding="windows-1252", low_memory=False)
    d = d[(d.ExhibitionRole == "Artist") & (d.ConstituentType == "Individual")]
    d = d.dropna(subset=["ConstituentID"]).drop_duplicates("ConstituentID")
    return pd.DataFrame({
        "src": "moma",
        "id": d.ConstituentID.astype(int).astype(str).values,
        "name": d.DisplayName.values,
        "key": [name_key(x) for x in d.DisplayName],
        "block": [block_key(x, True) for x in d.AlphaSort],
        "birth": pd.to_numeric(d.ConstituentBeginDate, errors="coerce").values,
        "death": pd.to_numeric(d.ConstituentEndDate, errors="coerce").values,
    }).query("key != ''").reset_index(drop=True)

def load_tate() -> pd.DataFrame:
    d = pd.read_csv(SRC / "tate-collection" / "artist_data.csv", low_memory=False)
    nm = d.name.astype(str).str.replace(",", " ", regex=False)
    return pd.DataFrame({
        "src": "tate", "id": d.id.astype(str).values, "name": d.name.values,
        "key": [name_key(x) for x in nm], "block": [block_key(x, True) for x in d.name.astype(str)],
        "birth": pd.to_numeric(d.yearOfBirth, errors="coerce").values,
        "death": pd.to_numeric(d.yearOfDeath, errors="coerce").values,
    }).query("key != ''").reset_index(drop=True)

# ---------------------------------------------------------------- arbitrato sulle date
def adjudicate(a, b, tol=TOL):
    """-> (esito, prove). esito: 'corroborato' | 'conflitto' | 'non verificabile'."""
    ev, agree, clash = {}, 0, 0
    for field in ("birth", "death"):
        x, y = a[field], b[field]
        if pd.notna(x) and pd.notna(y):
            ev[field] = {a["src"]: int(x), b["src"]: int(y), "delta": int(abs(x - y))}
            if abs(x - y) <= tol: agree += 1
            else: clash += 1
    if clash: return "conflitto", ev
    if agree: return "corroborato", ev
    return "non verificabile", ev

def grade(sim, verdict):
    """Il grado di certezza non e' mai binario."""
    if verdict == "conflitto":                      return "contestato"
    if sim >= 99 and verdict == "corroborato":      return "certo"
    if sim >= 90 and verdict == "corroborato":      return "probabile"
    if verdict == "corroborato":                    return "possibile"
    if sim >= 99:                                   return "probabile"
    return "possibile"

# ---------------------------------------------------------------- riconciliazione
def reconcile(left: pd.DataFrame, right: pd.DataFrame):
    by_block = collections.defaultdict(list)
    for r in right.to_dict("records"):
        by_block[r["block"]].append(r)
    out = []
    for a in left.to_dict("records"):
        best = None
        for b in by_block.get(a["block"], ()):
            sim = 100 if a["key"] == b["key"] else fuzz.token_sort_ratio(a["key"], b["key"])
            if sim < SIM_MIN:
                continue
            verdict, ev = adjudicate(a, b)
            # un conflitto non elimina la coppia: la declassa
            rank = (sim + (10 if verdict == "corroborato" else 0)
                        - (40 if verdict == "conflitto" else 0))
            if best is None or rank > best[0]:
                best = (rank, b, sim, verdict, ev)
        if best:
            _, b, sim, verdict, ev = best
            out.append(dict(subject=a, object=b, sim=sim, verdict=verdict, evidence=ev))
    return out

def to_assertion(i, m):
    a, b = m["subject"], m["object"]
    return {
        "id": f"armoni:idlink/{i:06d}",
        "type": "IdentityAssertion",
        "relation": "sameAs",
        "subject": {"source": a["src"], "id": a["id"], "name": a["name"]},
        "object":  {"source": b["src"], "id": b["id"], "name": b["name"]},
        "method": f"blocco-cognome+fuzzy>={SIM_MIN}+arbitrato-date(tol={TOL}a)",
        "evidence": {"name_similarity": round(m["sim"], 1),
                     "date_verdict": m["verdict"], "dates": m["evidence"]},
        "certainty": grade(m["sim"], m["verdict"]),
        "status": "proposto",
        "generated_by": {"tool": "armoni-reconcile", "version": VERSION},
    }

# ---------------------------------------------------------------- esecuzione
def main():
    OUT.mkdir(exist_ok=True)
    moma, tate = load_moma(), load_tate()
    matches = reconcile(moma, tate)
    assertions = [to_assertion(i, m) for i, m in enumerate(matches, 1)]
    with open(OUT / "identity_assertions.jsonl", "w") as f:
        for x in assertions:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

    c = collections.Counter(x["certainty"] for x in assertions)
    v = collections.Counter(x["evidence"]["date_verdict"] for x in assertions)
    checkable = v["corroborato"] + v["conflitto"]
    err = 100 * v["conflitto"] / max(checkable, 1)
    rep = [
        "# Metriche di riconciliazione",
        f"\nGenerato il {datetime.date.today()} da `armoni-reconcile` {VERSION} "
        f"sulle fonti fissate in `data/MANIFEST.md`.\n",
        f"- artisti MoMA: **{len(moma)}** (anno di nascita noto: {100*pd.notna(moma.birth).mean():.0f}%)",
        f"- artisti Tate: **{len(tate)}** (anno di nascita noto: {100*pd.notna(tate.birth).mean():.0f}%)",
        f"- asserzioni di identita' emesse: **{len(assertions)}** "
        f"({100*len(assertions)/len(tate):.1f}% del roster Tate)\n",
        "## Grado di certezza\n",
        "| grado | n. | quota |", "| --- | ---: | ---: |",
    ]
    for g in ("certo", "probabile", "possibile", "contestato"):
        rep.append(f"| {g} | {c[g]} | {100*c[g]/max(len(assertions),1):.1f}% |")
    rep += [
        "\n## Arbitrato sulle date (giudice indipendente dal nome)\n",
        f"- corroborate da almeno una data concorde: **{v['corroborato']}**",
        f"- in conflitto su una data: **{v['conflitto']}**",
        f"- non verificabili (una delle due fonti non ha date): **{v['non verificabile']}**",
        f"\nTasso di conflitto sulle coppie verificabili: **{err:.1f}%**. "
        "Non è un tasso di errore: mescola omonimi veri e casi in cui le due "
        "istituzioni registrano date diverse per la stessa persona. Gli omonimi privi "
        "di date, inoltre, non vengono intercettati affatto.\n",
        "## Nessun legame viene scartato in silenzio\n",
        "Le coppie con date in conflitto restano nel file come asserzioni `contestato`. "
        "Alcune sono omonimi veri (la Tate ha due Henry Moore, 1831–1895 e 1898–1986); "
        "altre sono la stessa persona su cui le due istituzioni non concordano "
        "(Milton Avery, 1885 per il MoMA e 1893 per la Tate). Distinguerle è lavoro "
        "editoriale umano, non una soglia da tarare.\n",
        "## Asserzioni contestate\n",
        "| MoMA | Tate | nascita | morte |", "| --- | --- | --- | --- |",
    ]
    for x in assertions:
        if x["certainty"] != "contestato":
            continue
        d = x["evidence"]["dates"]
        fm = lambda k: (f"{d[k]['moma']} / {d[k]['tate']}" if k in d else "—")
        rep.append(f"| {x['subject']['name']} | {x['object']['name']} | {fm('birth')} | {fm('death')} |")
    (OUT / "metrics.md").write_text("\n".join(rep) + "\n")
    print("\n".join(rep[:22]))
    print(f"\n-> out/identity_assertions.jsonl ({len(assertions)} asserzioni)\n-> out/metrics.md")

if __name__ == "__main__":
    main()
