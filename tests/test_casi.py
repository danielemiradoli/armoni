"""I casi di riferimento. Eseguire dopo src/fetch.py:  python3 tests/test_casi.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
import reconcile as r

_tutte = r.reconcile(r.load_moma(), r.load_tate())
links = {m["subject"]["name"]: m for m in _tutte}
_diff = [m for m in _tutte if m["relation"] == "differentFrom"]

def test_henry_moore_e_lo_scultore():
    assert links["Henry Moore"]["object"]["birth"] == 1898

def test_kandinsky_recuperato_dal_fuzzy():
    m = links["Vasily Kandinsky"]
    assert m["object"]["name"] == "Kandinsky, Wassily" and m["verdict"] == "corroborato"

def test_avery_contestato_non_scartato():
    assert r.grade(links["Milton Avery"]["sim"], links["Milton Avery"]["verdict"]) == "contestato"

def test_de_kooning_particella_nobiliare():
    """Causa A: 'Willem de Kooning' contro 'Kooning, Willem de'. Il primo token
    cadeva su 'de' da un lato e su 'kooning' dall'altro, e le due liste non si
    incontravano mai nonostante la similarita' del nome fosse gia' 100."""
    assert links["Willem de Kooning"]["object"]["name"] == "Kooning, Willem de"


def test_graeser_scarto_26_anni_resta_la_stessa_persona():
    """Il campione d'oro conferma Camille Graeser come una sola persona nonostante
    uno scarto di 26 anni sulla nascita. Serve da guardia contro la tentazione di
    fissare una soglia a priori fra 'contesa' e 'incompatibile': la soglia a 20
    anni proposta in D2 avrebbe classificato questo caso come persona diversa.
    La coppia deve restare emessa, graduata 'contestato' e non scartata."""
    m = links["Camille Graeser"]
    assert m["object"]["name"] == "Graeser, Camille"
    assert abs(m["subject"]["birth"] - m["object"]["birth"]) == 26
    assert r.grade(m["sim"], m["verdict"]) == "contestato"


def test_campione_esteso_contiene_negative_confermate():
    """Il criterio di accettazione del punto 1 della sezione 4: il campione deve
    contenere casi di persone diverse con prova positiva di distinzione, non solo
    coppie positive. Senza negative la precisione non e' misurabile sui casi
    difficili e qualunque misura tende al 100% per costruzione."""
    import gold
    ids = gold.add_moma_column(
        gold.load_identities(),
        gold.ROOT / "data" / "sources" / "moma-exhibitions" / "MoMAExhibitions1929to1989.csv")
    quint = [(m["subject"]["id"], m["object"]["id"], r.grade(m["sim"], m["verdict"]),
              m["subject"]["name"], m["object"]["name"]) for m in links.values()]
    h = gold.score_hard(quint, ids)
    assert h["conteggi"]["diversa"] > 0, "nessuna negativa solida: campione inutile"
    assert h["sup"] < 100.0, "la precisione non puo' tornare a essere 100% per costruzione"


def test_differentfrom_solo_con_prova_positiva():
    """D1 come approvata: una non-identita' si emette solo con prova positiva.
    Ogni differentFrom deve portare o la smentita esplicita del campione d'oro
    o identificativi esterni/item distinti. Nessuna puo' poggiare sul silenzio."""
    assert _diff, "nessuna differentFrom emessa"
    for m in _diff:
        d = m["evidence"].get("distinctness")
        assert d, f"{m['subject']['name']} senza prova"
        assert "oro" in d or "item" in d, f"{m['subject']['name']}: prova vuota"


def test_differentfrom_non_tocca_duo_e_duplicati():
    """I due modi in cui la prova di distinzione sbaglia, tenuti fuori.

    Bernd Becher contro 'Becher, Prof. Bernd': l'item Tate e' il duo
    'Bernd and Hilla Becher', quindi e' un disaccordo sulla granularita'.
    Ryszard Otreba: due item, stessa persona, stessa nascita, duplicato non fuso.
    Dire differentFrom su questi direbbe che una persona non e' se stessa."""
    emessi = {m["subject"]["name"] for m in _diff}
    for nome in ("Bernd Becher", "Ryszard K. Otreba", "Anne Poirier", "Fionnuala Boyd"):
        assert nome not in emessi, f"{nome} non doveva uscire come differentFrom"


def test_contestato_resta_sameAs():
    """Il grado 'contestato' continua a significare 'coppia contesa', non
    'coppia sbagliata': chi ha una prova di distinzione esce come differentFrom,
    chi non ce l'ha resta sameAs contestato. Milton Avery e' il caso di
    riferimento: date discordi, stessa persona, nessuna prova del contrario."""
    m = links["Milton Avery"]
    assert m["relation"] == "sameAs" and m["certainty"] == "contestato"


def test_nome_in_cirillico_non_deve_sparire():
    """CRITERIO DI VERIFICA SCRITTO PRIMA DELLA MODIFICA. Oggi FALLISCE apposta.

    `tokens()` passa per `encode("ascii", "ignore")` e poi filtra `[^a-z ]`.
    Un nome in scrittura non latina si riduce a stringa vuota, `name_key`
    restituisce "", e `load_moma`/`load_tate` eliminano la riga con
    `.query("key != '\'')`. L'artista sparisce dal roster: non compare fra le
    asserzioni, non compare fra gli errori, e non entra nemmeno nel
    denominatore del richiamo. Non e' un abbinamento mancato, e' un record che
    per la pipeline non e' mai esistito.

    Oggi non si manifesta perche' MoMA e Tate traslitterano gia' alla fonte.
    Il contatore in `out/metrics.md` segna zero. Si aprirebbe al primo catalogo
    che non traslittera.

    Il test resta rosso di proposito: il multilingua non e' il collo di
    bottiglia attuale, che e' il campione sui casi difficili. Quando si
    affrontera', questo e' il criterio da soddisfare, e la riga sotto deve
    diventare verde senza essere riscritta.
    """
    assert r.name_key("Казимир Малевич"), \
        "name_key perde i nomi in cirillico e il record sparisce dal roster"


test_nome_in_cirillico_non_deve_sparire.atteso_fallire = True


if __name__ == "__main__":
    rossi = []
    for name, f in list(globals().items()):
        if not name.startswith("test_"):
            continue
        atteso = getattr(f, "atteso_fallire", False)
        try:
            f()
        except AssertionError as e:
            if atteso:
                print(f"ROSSO ATTESO  {name}\n              {e}")
            else:
                rossi.append(name)
                print(f"FALLITO       {name}\n              {e}")
        else:
            if atteso:
                rossi.append(name)
                print(f"VERDE INATTESO {name} — se e' stato risolto, togliere "
                      f"atteso_fallire e aggiornare out/metrics.md")
            else:
                print("ok", name)
    # Un rosso atteso non fa fallire la serie: e' un criterio di verifica gia'
    # scritto per un lavoro non ancora fatto. Un rosso inatteso si', e anche un
    # verde inatteso, perche' vuol dire che il criterio non e' piu' aggiornato.
    raise SystemExit(1 if rossi else 0)
