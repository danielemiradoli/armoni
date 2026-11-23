"""Letture del testo dei cataloghi, comuni a tutte le fonti e a tutti i fili."""
import csv, re
from functools import lru_cache
from pathlib import Path

GAZ = Path(__file__).resolve().parent / 'gazzettiere'

# Il catalogo stesso dichiara l'attribuzione incerta: lo si conserva, non lo si risolve.
INCERTO = re.compile(r'possibl|probabl|\?|\bor\b|attributed', re.I)


def anno(x):
    try:
        return int(float(x))
    except (TypeError, ValueError):
        return None


def trova(tabella, testo):
    """Il primo luogo della tabella il cui schema compare nel testo. L'ordine della tabella conta."""
    for luogo, pat in tabella:
        if re.search(pat, testo, re.I):
            return luogo
    return None


@lru_cache(None)
def gazzettiere(*nomi):
    """Concatena, nell'ordine dato, le tabelle `gazzettiere/<nome>.csv` (luogo, regex)."""
    out = []
    for n in nomi:
        out += [(r['luogo'], r['regex']) for r in csv.DictReader(open(GAZ / f'{n}.csv', encoding='utf-8'))]
    return tuple(out)


def mercato(cultura):
    """«for the Dutch market» nel campo cultura: il mercato di destinazione dichiarato dal catalogo."""
    m = re.search(r'for (?:the )?([^,;()]*?)\bmarket', cultura, re.I)
    if not m:
        return None, ('export' in cultura.lower())
    return trova(gazzettiere('mercati'), m.group(1)), False
