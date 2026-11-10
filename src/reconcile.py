"""Armoni — strato di riconciliazione delle identita' fra collezioni.

Produce ASSERZIONI, non verdetti. Ogni legame porta metodo, prova, grado di certezza.
Un disaccordo fra due istituzioni non viene risolto d'ufficio ne' scartato in silenzio:
viene emesso come asserzione 'contestata'. Caso di riferimento: Milton Avery, nato 1885
per il MoMA e 1893 per la Tate.
"""
from __future__ import annotations
import pandas as pd, unicodedata, re, csv, json, pathlib, collections, datetime
from rapidfuzz import fuzz

VERSION = "0.1.0"
ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "data" / "sources", ROOT / "out"
RAW = ROOT / "data" / "raw"
# Soglie TARATE e lasciate dove erano. La taratura e' stata fatta davvero: griglia
# su meta' A-L del campione d'oro, verifica su meta' M-Z mai usata per tararla.
# Il criterio del piano e' soddisfatto da (75, 3), che sulla meta' di riporto da'
# richiamo 98,5% contro 97,3% a parita' di precisione. Non lo si adotta, perche'
# un controllo indipendente dal campione lo smentisce:
#
#   SIM  asserzioni  nella parte che l'oro giudica  fuori    contestate fuori
#    85        871              765                  106          19,8%
#    75       1052              772                  280          27,5%
#
# La parte giudicata dall'oro e' satura: da 85 a 75 guadagna 7 asserzioni e il
# tasso di contestazione non si muove di un decimo. Tutto il resto del guadagno,
# 174 asserzioni, cade dove l'oro tace, e li' una su quattro e' in conflitto sulle
# date. A vista: 'Henry Churchill = Churchill, Sir Winston', 'Ann Weaver =
# Weaver, Thomas', 'Sir Charles Barry = Barry, James'.
#
# La metrica migliora perche' misura solo la meta' facile del problema. Abbassare
# la soglia per inseguirla sarebbe una conclusione netta tratta da un campione
# sbilanciato. SIM_MIN resta 85 finche' non esiste un campione che giudichi anche
# i casi difficili.
SIM_MIN = 85      # similarita' minima del nome per considerare una coppia
# TOL non e' tarabile sui dati: fra 2 e 20 anni precisione e richiamo non si
# muovono di un decimo, perche' la tolleranza non decide QUALI coppie emettere ma
# solo come graduarle (da 91 a 65 asserzioni 'contestato'). Resta a 3 perche'
# nessuna misura giustifica spostarlo. Stessa logica di D2: nessuna soglia a
# priori fra 'contesa' e 'incompatibile'.
TOL = 3           # anni di tolleranza fra due date che dovrebbero coincidere
STOP = {"jr", "sir", "dame", "the", "of", "and", "om", "ch"}
# Particelle nobiliari e preposizioni: MoMA e Tate le collocano in posizioni diverse
# ("Willem de Kooning" / "Kooning, Willem de"), quindi non possono fare da chiave.
PARTICLES = {"de", "van", "von", "der", "den", "del", "della", "dell", "di", "da",
             "du", "la", "le", "el", "ten", "ter", "af", "av", "dos", "das", "do"}

# ---------------------------------------------------------------- normalizzazione
PAREN = re.compile(r"\([^)]*\)")

def tokens(s: str) -> list[str]:
    """Token normalizzati del nome.

    Due scelte che pesano sulla misura, entrambe verificate sul campione d'oro:

    - Il contenuto fra parentesi viene rimosso. Il MoMA lo usa per il nome
      anagrafico o per una variante ('Christo (Christo Javacheff)', 'Jean (Hans)
      Arp', 'L. S. Lowry (Lawrence Stephen Lowry)'), la Tate non lo usa mai.
      Confrontandolo, la similarita' di Lowry scendeva a 30. Rimuoverlo porta il
      richiamo dal 93,4% al 95,4% senza toccare la precisione.
    - Le iniziali puntate NON vengono scartate. Erano escluse dal filtro len > 1
      e questo buttava via informazione che distingue: tenerle fa scendere gli
      errori da 8 a 5. Un'iniziale e' una prova debole ma non e' rumore.
    """
    if not isinstance(s, str):
        return []
    s = PAREN.sub(" ", s)
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z ]", " ", s.lower())
    return [t for t in s.split() if t not in STOP and t]

def name_key(s: str) -> str:
    return " ".join(sorted(tokens(s)))

def block_keys(s: str, comma_form: bool) -> frozenset[str]:
    """Chiavi di blocco: il cognome, al netto delle particelle.

    Un'unica chiave fissa non funziona. La Tate scrive 'Cognome, Nome' e mette la
    particella dentro il cognome ('Kooning, Willem de'); il MoMA scrive il nome per
    esteso ('Willem de Kooning'). Prendendo il primo token si ottiene 'de' da un lato
    e 'kooning' dall'altro, e le due liste non si incontrano mai: 15 coppie del
    campione d'oro con similarita' gia' 100 non venivano nemmeno confrontate.

    Nella forma con virgola si tengono TUTTI i token non-particella del cognome,
    perche' i due musei dissentono su dove cominci: 'Dunoyer de Segonzac' per la
    Tate, 'Segonzac' per il MoMA. Nella forma estesa basta l'ultimo token.

    Allargare oltre questo -- per esempio bloccando anche sui nomi di battesimo --
    e' stato misurato e scartato: recupera 11 coppie e ne sbaglia 29 in piu'.
    """
    if comma_form and "," in str(s):
        sur = [x for x in tokens(str(s).split(",")[0]) if x not in PARTICLES]
        if sur:
            return frozenset(sur)
    t = [x for x in tokens(s) if x not in PARTICLES] or tokens(s)
    return frozenset(t[-1:]) if t else frozenset()

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
        "block": [block_keys(x, False) for x in d.DisplayName],
        "birth": pd.to_numeric(d.ConstituentBeginDate, errors="coerce").values,
        "death": pd.to_numeric(d.ConstituentEndDate, errors="coerce").values,
    }).query("key != ''").reset_index(drop=True)

def load_tate() -> pd.DataFrame:
    d = pd.read_csv(SRC / "tate-collection" / "artist_data.csv", low_memory=False)
    nm = d.name.astype(str).str.replace(",", " ", regex=False)
    return pd.DataFrame({
        "src": "tate", "id": d.id.astype(str).values, "name": d.name.values,
        "key": [name_key(x) for x in nm],
        "block": [block_keys(x, True) for x in d.name.astype(str)],
        "birth": pd.to_numeric(d.yearOfBirth, errors="coerce").values,
        "death": pd.to_numeric(d.yearOfDeath, errors="coerce").values,
    }).query("key != ''").reset_index(drop=True)

# ---------------------------------------------------------------- identificativi esterni
TATE_NUM = re.compile(r"(\d+)$")

_EXT_CACHE = {}

def load_external_ids() -> dict:
    """ULAN (P245) e VIAF (P214) per ogni ID MoMA e ogni ID Tate, da Wikidata.

    Chiavi ('moma', id) e ('tate', id). L'ID Tate su Wikidata e' uno slug
    ('berthe-morisot-1663'): la chiave di join e' il numero finale. Un item puo'
    avere piu' valori per la stessa proprieta', e si tengono tutti: la domanda da
    porre e' se i due insiemi si sovrappongono, non se coincidono.
    """
    if _EXT_CACHE:
        return _EXT_CACHE
    out = collections.defaultdict(
        lambda: {"item": set(), "label": set(), "ulan": set(), "viaf": set()})
    for fn, col, src in (("wikidata_moma.csv", "momaId", "moma"),
                         ("wikidata_tate.csv", "tateId", "tate")):
        path = RAW / fn
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                raw = row[col].strip()
                if src == "tate":
                    m = TATE_NUM.search(raw)
                    raw = m.group(1) if m else ""
                if not raw:
                    continue
                out[(src, raw)]["item"].add(row["item"].strip())
                if row.get("itemLabel", "").strip():
                    out[(src, raw)]["label"].add(row["itemLabel"].strip())
                for field in ("ulan", "viaf"):
                    v = row[field].strip()
                    if v:
                        out[(src, raw)][field].add(v)
    # La colonna WikidataID del CSV MoMA copre 230 artisti che la query P2174 non
    # vede. Porta solo l'item, non ULAN ne' VIAF: dove quelli esistono coincidono
    # al 100% con Wikidata, quindi come giudice non aggiungerebbero nulla.
    src_csv = SRC / "moma-exhibitions" / "MoMAExhibitions1929to1989.csv"
    if src_csv.exists():
        d = pd.read_csv(src_csv, encoding="windows-1252", low_memory=False)
        d = d[(d.ExhibitionRole == "Artist") & (d.ConstituentType == "Individual")]
        d = d.dropna(subset=["ConstituentID"]).drop_duplicates("ConstituentID")
        for row in d.itertuples():
            if pd.notna(row.WikidataID):
                out[("moma", str(int(row.ConstituentID)))]["item"].add(str(row.WikidataID).strip())
    _EXT_CACHE.update(out)
    return _EXT_CACHE


def external_verdict(a, b, ids):
    """Terzo giudice, indipendente sia dal nome sia dalle date.

    Serve al secchio cieco: le coppie in cui almeno una delle due istituzioni non
    registra date e l'arbitrato non puo' pronunciarsi. ULAN e VIAF illuminano circa
    un terzo di quel secchio; sul resto nessuna fonte si pronuncia e lo si dichiara,
    invece di colmarlo con una stima.
    """
    ka, kb = ids.get((a["src"], a["id"])), ids.get((b["src"], b["id"]))
    if not ka or not kb:
        return "non verificabile", {}
    ev, agree, clash = {}, 0, 0
    for field in ("ulan", "viaf"):
        xa, xb = ka[field], kb[field]
        if xa and xb:
            same = bool(xa & xb)
            ev[field] = {a["src"]: sorted(xa), b["src"]: sorted(xb), "concordi": same}
            agree += same
            clash += not same
    if clash:
        return "conflitto", ev
    if agree:
        return "corroborato", ev
    return "non verificabile", ev




# ---------------------------------------------------------------- non-identita'
DUO = re.compile(r"\band\b|&", re.I)

def is_duo(rec, ids_entry) -> bool:
    """Il record designa un duo o un collettivo?

    Si guarda il nome di catalogo E l'etichetta Wikidata, perche' spesso solo la
    seconda lo dice: la Tate scrive 'Becher, Prof. Bernd', ma l'item e'
    'Bernd and Hilla Becher'. Con il solo nome di catalogo si emetteva una
    non-identita' fra Bernd Becher e il duo che lo comprende.

    L'euristica e' deliberatamente troppo larga: 'Bob and Roberta Smith' e' lo
    pseudonimo di una persona sola, e viene escluso lo stesso. Astenersi su un
    caso in piu' costa meno che affermare una non-identita' falsa.
    """
    if DUO.search(rec.get("name") or ""):
        return True
    return any(DUO.search(x) for x in (ids_entry or {}).get("label", ()))


def looks_like_duplicate(a, b) -> bool:
    """Firma del duplicato Wikidata non fuso: stesso nome e stessa data di nascita.

    Ryszard K. Otreba e Ryszard Otreba stanno su due item distinti, entrambi con
    identificativo esterno, entrambi nati nel 1932. Non sono due persone: sono due
    schede della stessa. Omonimi veri con lo stesso anno di nascita esistono, ma
    sono rari, e qui si tratta di affermare una NON-identita': davanti a questa
    firma conviene tacere.
    """
    if a.get("key") and a["key"] == b.get("key"):
        pass
    elif fuzz.token_set_ratio(a.get("key") or "", b.get("key") or "") < 95:
        return False
    x, y = a.get("birth"), b.get("birth")
    return pd.notna(x) and pd.notna(y) and abs(x - y) <= TOL


def distinctness(a, b, ids):
    """Prova POSITIVA che i due record sono persone diverse -> (grado, prove).

    Restituisce None quando la prova non c'e'. Il silenzio non e' una prova: una
    coppia su cui nessuna fonte si pronuncia resta 'sameAs' contestato, non
    diventa 'differentFrom'. Questa e' la decisione D1 come approvata.

    Due forme di prova, entrambe richiedono un identificativo esterno su ENTRAMBI
    i lati:
      certo     - ULAN o VIAF presenti su entrambi i lati e disgiunti. Due archivi
                  di autorita' assegnano identita' diverse.
      probabile - item Wikidata distinti, senza conflitto diretto di
                  identificativo ma con un ancoraggio esterno su entrambi i lati.

    Tre esclusioni, tutte sostanziali:
      - item distinti ma identificativo esterno CONDIVISO: e' un duplicato
        Wikidata non fuso, non due persone;
      - identificativo esterno assente su un lato: il duplicato non si puo'
        escludere, e asserire sarebbe di nuovo asserire sul silenzio;
      - duo e collettivi: la Tate cataloga 'Poirier, Anne and Patrick' come
        scheda unica e il MoMA Anne Poirier come persona. Dire 'differentFrom'
        direbbe che Anne Poirier non e' Anne Poirier. E' un disaccordo sulla
        granularita' e va trattato con una relazione sua, non con una
        non-identita'.
    """
    ka, kb = ids.get((a["src"], a["id"])), ids.get((b["src"], b["id"]))
    if not ka or not kb or not ka["item"] or not kb["item"]:
        return None
    if ka["item"] & kb["item"]:
        return None                                   # stesso item: stessa persona
    if (ka["ulan"] & kb["ulan"]) or (ka["viaf"] & kb["viaf"]):
        return None                                   # duplicato Wikidata non fuso
    if is_duo(a, ka) or is_duo(b, kb):
        return None                                   # granularita', non identita'
    if not ((ka["ulan"] or ka["viaf"]) and (kb["ulan"] or kb["viaf"])):
        return None                                   # nessun ancoraggio esterno
    if looks_like_duplicate(a, b):
        return None                                   # firma da duplicato non fuso

    ev = {"item": {a["src"]: sorted(ka["item"]), b["src"]: sorted(kb["item"])}}
    grado = "probabile"
    for field in ("ulan", "viaf"):
        if ka[field] and kb[field]:
            ev[field] = {a["src"]: sorted(ka[field]), b["src"]: sorted(kb[field])}
            grado = "certo"
    return grado, ev


def load_gold_pairs() -> dict:
    """Le coppie (momaId, tateId) del campione d'oro, indicizzate nei due versi."""
    per_m, per_t = collections.defaultdict(set), collections.defaultdict(set)
    path = RAW / "wikidata_gold.csv"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                mo, slug = row["momaId"].strip(), row["tateId"].strip()
                g = TATE_NUM.search(slug)
                if mo and g:
                    per_m[mo].add(g.group(1))
                    per_t[g.group(1)].add(mo)
    return {"per_moma": dict(per_m), "per_tate": dict(per_t)}


def gold_contradiction(a, b, gold_pairs):
    """L'oro assegna esplicitamente uno dei due a un partner diverso.

    Oggi questo insieme e' VUOTO: le 8 coppie che l'oro smentiva sono quelle che
    il vincolo di reciprocita' ha eliminato. Il criterio resta codificato come
    guardia: se una modifica futura le fa rientrare, escono come 'differentFrom'
    e non tornano silenziosamente 'sameAs'.
    """
    if not gold_pairs:
        return None
    by_m = gold_pairs.get("per_moma", {})
    by_t = gold_pairs.get("per_tate", {})
    if a["id"] in by_m and b["id"] not in by_m[a["id"]]:
        return {"oro": {"moma": a["id"], "partner_atteso": sorted(by_m[a["id"]])}}
    if b["id"] in by_t and a["id"] not in by_t[b["id"]]:
        return {"oro": {"tate": b["id"], "partner_atteso": sorted(by_t[b["id"]])}}
    return None

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
def reconcile(left: pd.DataFrame, right: pd.DataFrame, mutual: bool = True,
              external: bool = True, distinct: bool = True):
    """Abbina i due roster.

    mutual=True impone la RECIPROCITA': una coppia sopravvive solo se ciascuno dei
    due e' il miglior candidato dell'altro. Senza questo vincolo il confronto e'
    unilaterale e il pretendente giusto non viene mai messo a confronto con quello
    sbagliato: 'Don Walker' si prendeva 'Walker, John' perche' nessuno chiedeva a
    'Walker, John' chi preferisse, e la risposta era 'John Walker'. Sette degli
    otto errori trovati dal campione d'oro sono di questa forma, piu' i 9 artisti
    Tate legati a due artisti MoMA diversi.
    """
    by_block = collections.defaultdict(list)
    rows = right.to_dict("records")
    for i, r in enumerate(rows):
        for k in r["block"]:
            by_block[k].append(i)

    ids = load_external_ids() if external else {}
    scored = []
    for a in left.to_dict("records"):
        cand = set()
        for k in a["block"]:
            cand.update(by_block.get(k, ()))
        for b in (rows[i] for i in cand):
            # token_set_ratio, non token_sort_ratio: quando i token di un nome sono
            # un sottoinsieme dell'altro ('Ivan Le Lorraine Albright' contro
            # 'Albright, Ivan') il sort penalizza i token in piu' e il set no.
            sim = 100 if a["key"] == b["key"] else fuzz.token_set_ratio(a["key"], b["key"])
            if sim < SIM_MIN:
                continue
            verdict, ev = adjudicate(a, b, TOL)
            ev, judge = {"dates": ev}, "date"
            if verdict == "non verificabile" and ids:
                # solo sul secchio cieco: dove le date parlano, decidono loro
                verdict, xev = external_verdict(a, b, ids)
                ev["external"] = xev
                judge = "identificativi" if verdict != "non verificabile" else "nessuno"
            # un conflitto non elimina la coppia: la declassa
            rank = (sim + (10 if verdict == "corroborato" else 0)
                        - (40 if verdict == "conflitto" else 0))
            scored.append((rank, a, b, sim, verdict, ev, judge))

    best_l, best_r = {}, {}
    for rank, a, b, sim, verdict, ev, judge in scored:
        if best_l.get(a["id"], (-1,))[0] < rank:
            best_l[a["id"]] = (rank, a, b, sim, verdict, ev, judge)
        if best_r.get(b["id"], (-1,))[0] < rank:
            best_r[b["id"]] = (rank, a, b, sim, verdict, ev, judge)

    gold_pairs = load_gold_pairs() if distinct else {}
    out = []
    for aid, (rank, a, b, sim, verdict, ev, judge) in best_l.items():
        if mutual and best_r[b["id"]][1]["id"] != aid:
            continue
        relation, certainty = "sameAs", grade(sim, verdict)
        if distinct and ids:
            # D1: si emette una non-identita' SOLO con prova positiva.
            # L'assenza di prova lascia l'asserzione com'e'.
            duo = is_duo(a, ids.get((a["src"], a["id"]))) or \
                  is_duo(b, ids.get((b["src"], b["id"])))
            contra = None if duo else gold_contradiction(a, b, gold_pairs)
            proof = distinctness(a, b, ids)
            if contra:
                relation, certainty = "differentFrom", "certo"
                ev["distinctness"] = contra
            elif proof:
                relation, certainty = "differentFrom", proof[0]
                ev["distinctness"] = proof[1]
        out.append(dict(subject=a, object=b, sim=sim, verdict=verdict,
                        evidence=ev, judge=judge,
                        relation=relation, certainty=certainty))
    return out

def to_assertion(i, m):
    a, b = m["subject"], m["object"]
    return {
        "id": f"armoni:idlink/{i:06d}",
        "type": "IdentityAssertion",
        "relation": m.get("relation", "sameAs"),
        "subject": {"source": a["src"], "id": a["id"], "name": a["name"]},
        "object":  {"source": b["src"], "id": b["id"], "name": b["name"]},
        "method": f"blocco-cognome-senza-particelle+token_set>={SIM_MIN}"
                  f"+arbitrato-date(tol={TOL}a)+reciprocita",
        "evidence": {"name_similarity": round(m["sim"], 1),
                     "verdict": m["verdict"], "judge": m["judge"],
                     "dates": m["evidence"]["dates"],
                     "external_ids": m["evidence"].get("external", {}),
                     "distinctness": m["evidence"].get("distinctness", {})},
        "certainty": m.get("certainty") or grade(m["sim"], m["verdict"]),
        "status": "proposto",
        "generated_by": {"tool": "armoni-reconcile", "version": VERSION},
    }

def _gold_section(assertions) -> str:
    """Precisione e richiamo contro i collegamenti MoMA<->Tate fatti a mano su
    Wikidata, con la riserva che li rende leggibili."""
    import sys
    sys.path.insert(0, str(ROOT / "src"))
    try:
        import gold
        moma, tate = load_moma(), load_tate()
        ev = gold.evaluable(gold.load_pairs(), set(moma.id), set(tate.id))
        names = dict(zip(tate.id, tate.name))
    except Exception as e:
        return f"Non calcolata: {e}\n"
    triple = [(x["subject"]["id"], x["object"]["id"], x["certainty"]) for x in assertions]
    tutto = gold.score(triple, ev)
    rip = gold.score(triple, ev, "riporto", names)
    return (
        f"Campione: i collegamenti MoMA<->Tate fatti a mano su Wikidata.\n\n"
        f"| | tutto il campione | sola meta' di riporto |\n"
        f"| --- | ---: | ---: |\n"
        f"| coppie d'oro valutabili | {tutto['oro']} | {rip['oro']} |\n"
        f"| asserzioni su cui l'oro ha un verdetto | {tutto['giudicate']} | {rip['giudicate']} |\n"
        f"| sbagliate | {tutto['giudicate']-tutto['corrette']} | {rip['giudicate']-rip['corrette']} |\n"
        f"| **precisione** | **{tutto['precisione']:.1f}%** | **{rip['precisione']:.1f}%** |\n"
        f"| **richiamo** | **{tutto['richiamo']:.1f}%** | **{rip['richiamo']:.1f}%** |\n\n"
        f"La colonna di destra e' quella da citare: la meta' M-Z del campione non e'\n"
        f"stata usata per tarare nulla. La taratura e' avvenuta sulla meta' A-L.\n\n"
        f"**Questa precisione non e' la precisione del sistema.** Il campione d'oro\n"
        f"giudica gli artisti che qualcuno su Wikidata ha avuto motivo di collegare:\n"
        f"i famosi, i facili. Su {len(assertions)} asserzioni emesse ne giudica\n"
        f"{tutto['giudicate']}, cioe' il {100*tutto['giudicate']/max(len(assertions),1):.0f}%; "
        f"sul resto nessuna fonte indipendente si pronuncia.\n"
        f"Meta' delle coppie d'oro riguarda inoltre artisti MoMA mai esposti nella\n"
        f"finestra 1929-1989, ed e' esclusa dal conteggio. La formulazione corretta e':\n"
        f"*{tutto['precisione']:.0f}% di precisione sulla parte del problema che Wikidata\n"
        f"e' in grado di giudicare.*\n\n"
        f"Quanto questo conti si vede abbassando SIM_MIN da 85 a 75: la parte giudicata\n"
        f"dall'oro guadagna 7 asserzioni e la metrica migliora, mentre 174 asserzioni\n"
        f"compaiono dove l'oro tace, con una su quattro in conflitto sulle date.\n"
        f"La soglia e' rimasta a 85 per questo.\n\n"
        + _hard_section(assertions, gold))


def _hard_section(assertions, gold) -> str:
    """Il campione esteso, che giudica anche i casi difficili."""
    try:
        ids = gold.add_moma_column(
            gold.load_identities(),
            ROOT / "data" / "sources" / "moma-exhibitions" / "MoMAExhibitions1929to1989.csv")
        quint = [(x["subject"]["id"], x["object"]["id"], x["certainty"],
                  x["subject"]["name"], x["object"]["name"]) for x in assertions]
        h = gold.score_hard(quint, ids)
    except Exception as e:
        return f"Campione esteso non calcolato: {e}\n"
    c, per = h["conteggi"], h["per_grado"]
    righe = [
        "### Campione esteso: anche i casi difficili\n",
        "Il campione sopra contiene solo coppie positive: dice quando due record sono",
        "la stessa persona, mai quando sono persone diverse. Le negative si ricavano",
        "dalla distinzione a livello di item su Wikidata (ID MoMA su un item, ID Tate",
        "su un altro = due persone diverse affermate, non dedotte da un silenzio).\n",
        "| esito | n. |", "| --- | ---: |",
        f"| stessa persona | {c['stessa']} |",
        f"| persona diversa, solida | {c['diversa']} |",
        f"| persona diversa, duplicato Wikidata non escludibile | {c['diversa-incerta']} |",
        f"| granularita' diversa (duo contro individuo) | {c['diversa-duo']} |",
        f"| nessun item su almeno un lato | {c['muto']} |",
        "",
        f"**Precisione fra {h['inf']:.1f}% e {h['sup']:.1f}%.** Non un numero ma un intervallo:",
        "contando tutte le negative si ha il limite inferiore, contando solo quelle",
        "solide il superiore. Il campione positivo da solo direbbe 100,0%, che era il",
        "limite superiore di un intervallo di cui non mostrava l'altro capo.\n",
        "Questo campione ha due modi propri di sbagliare, entrambi dichiarati: i duo",
        "d'artisti, che la Tate registra come scheda unica e il MoMA come persone",
        "(granularita', non errore di abbinamento); e i duplicati Wikidata non fusi,",
        "escludibili solo quando i due item portano un ULAN o un VIAF.\n",
        "| grado | stessa | diversa | incerta | duo | muto |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for gr in ("certo", "probabile", "possibile", "contestato"):
        p = per[gr]
        if sum(p.values()):
            righe.append(f"| {gr} | {p['stessa']} | {p['diversa']} | "
                         f"{p['diversa-incerta']} | {p['diversa-duo']} | {p['muto']} |")
    righe += [
        "",
        "I quattro gradi si separano nettamente, ed e' la conferma piu' utile: `certo`",
        "regge, `contestato` e' davvero una coppia contesa, e `possibile` non contiene",
        "nemmeno un caso confermato come stessa persona. Quel grado va riesaminato.\n",
    ]
    return "\n".join(righe)


# ---------------------------------------------------------------- esecuzione
def main():
    OUT.mkdir(exist_ok=True)
    moma, tate = load_moma(), load_tate()
    matches = reconcile(moma, tate)
    assertions = [to_assertion(i, m) for i, m in enumerate(matches, 1)]
    with open(OUT / "identity_assertions.jsonl", "w") as f:
        for x in assertions:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")

    same = [x for x in assertions if x["relation"] == "sameAs"]
    diff = [x for x in assertions if x["relation"] == "differentFrom"]
    c = collections.Counter(x["certainty"] for x in same)
    v = collections.Counter(x["evidence"]["verdict"] for x in same)
    j = collections.Counter(x["evidence"]["judge"] for x in same)
    checkable = v["corroborato"] + v["conflitto"]
    err = 100 * v["conflitto"] / max(checkable, 1)
    rep = [
        "# Metriche di riconciliazione",
        f"\nGenerato il {datetime.date.today()} da `armoni-reconcile` {VERSION} "
        f"sulle fonti fissate in `data/MANIFEST.md`.\n",
        f"- artisti MoMA: **{len(moma)}** (anno di nascita noto: {100*pd.notna(moma.birth).mean():.0f}%)",
        f"- artisti Tate: **{len(tate)}** (anno di nascita noto: {100*pd.notna(tate.birth).mean():.0f}%)",
        f"- asserzioni `sameAs`: **{len(same)}** "
        f"({100*len(same)/len(tate):.1f}% del roster Tate)",
        f"- asserzioni `differentFrom`: **{len(diff)}** (vedi in fondo)\n",
        "## Grado di certezza delle `sameAs`\n",
        "| grado | n. | quota |", "| --- | ---: | ---: |",
    ]
    for g in ("certo", "probabile", "possibile", "contestato"):
        rep.append(f"| {g} | {c[g]} | {100*c[g]/max(len(same),1):.1f}% |")
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
        "## Misura contro il campione di riferimento\n",
        _gold_section(same),
        "## Asserzioni contestate\n",
        "| MoMA | Tate | nascita | morte |", "| --- | --- | --- | --- |",
    ]
    for x in same:
        if x["certainty"] != "contestato":
            continue
        d = x["evidence"]["dates"]
        fm = lambda k: (f"{d[k]['moma']} / {d[k]['tate']}" if k in d else "—")
        rep.append(f"| {x['subject']['name']} | {x['object']['name']} | {fm('birth')} | {fm('death')} |")
    rep += [
        "\n## Non-identita' (`differentFrom`)\n",
        "Decisione D1, approvata il 10/11/2026. Si emette una non-identita' **solo",
        "con prova positiva di distinzione**: il silenzio di una fonte non e' una",
        "prova, e una coppia su cui nessuno si pronuncia resta `sameAs` contestata.",
        "Due forme di prova:\n",
        "- il campione d'oro assegna esplicitamente uno dei due record a un partner",
        "  diverso (grado `certo`);",
        "- gli item Wikidata sono distinti e ULAN o VIAF sono presenti e disgiunti",
        "  su entrambi i lati (`certo`), oppure i soli item sono distinti con un",
        "  ancoraggio esterno su entrambi i lati (`probabile`).\n",
        "Tre casi in cui ci si astiene, tutti sostanziali: identificativo esterno",
        "condiviso fra item distinti (duplicato Wikidata non fuso); identificativo",
        "assente su un lato (il duplicato non si puo' escludere); duo e collettivi,",
        "riconosciuti anche dall'etichetta Wikidata e non solo dal nome di catalogo",
        "('Becher, Prof. Bernd' per la Tate, ma l'item e' 'Bernd and Hilla Becher').",
        "Si tace inoltre davanti alla firma del duplicato non fuso: stesso nome e",
        "stessa data di nascita su item diversi, come i due Ryszard Otreba.\n",
        "| MoMA | Tate | grado | prova |", "| --- | --- | --- | --- |",
    ]
    for x in diff:
        d = x["evidence"]["distinctness"]
        prova = ("oro" if "oro" in d
                 else "+".join(k for k in ("ulan", "viaf") if k in d) or "item")
        rep.append(f"| {x['subject']['name']} | {x['object']['name']} "
                   f"| {x['certainty']} | {prova} |")
    (OUT / "metrics.md").write_text("\n".join(rep) + "\n")
    print("\n".join(rep[:22]))
    print(f"\n-> out/identity_assertions.jsonl ({len(assertions)} asserzioni)\n-> out/metrics.md")

if __name__ == "__main__":
    main()
