"""I casi di riferimento. Eseguire dopo src/fetch.py:  python3 tests/test_casi.py"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src"))
import reconcile as r

links = {m["subject"]["name"]: m for m in r.reconcile(r.load_moma(), r.load_tate())}

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


if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f(); print("ok", name)
