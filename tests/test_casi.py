"""I tre casi che il README dichiara. Eseguire dopo src/fetch.py:  python3 tests/test_casi.py"""
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

if __name__ == "__main__":
    for name, f in list(globals().items()):
        if name.startswith("test_"):
            f(); print("ok", name)
