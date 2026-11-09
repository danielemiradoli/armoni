"""Scarica le fonti al commit fissato nel manifest. Niente copie nel repository:
le fonti CC0 gia' versionate su GitHub restano dove sono, noi ne fissiamo lo stato."""
import subprocess, hashlib, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DEST = ROOT / "data" / "sources"

SOURCES = {
    "moma-exhibitions": ("https://github.com/MuseumofModernArt/exhibitions.git",
                         "5e1ce97416613068832255bdc4ddccc0fec7c508"),
    "tate-collection":  ("https://github.com/tategallery/collection.git",
                         "a51d8afc988ed083557e2950f4d0b644e7719f4a"),
}

def sha256(p, blocks=1 << 20):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(blocks), b""):
            h.update(chunk)
    return h.hexdigest()

def fetch(name, url, commit):
    d = DEST / name
    if (d / ".git").exists():
        print(f"  {name}: gia' presente")
    else:
        d.mkdir(parents=True, exist_ok=True)
        for cmd in (["git", "init", "-q"],
                    ["git", "remote", "add", "origin", url],
                    ["git", "fetch", "-q", "--depth", "1", "origin", commit],
                    ["git", "checkout", "-q", "FETCH_HEAD"]):
            subprocess.run(cmd, cwd=d, check=True)
        print(f"  {name}: scaricata a {commit[:10]}")
    got = subprocess.run(["git", "rev-parse", "HEAD"], cwd=d,
                         capture_output=True, text=True).stdout.strip()
    assert got == commit, f"{name}: commit {got} invece di {commit}"

if __name__ == "__main__":
    print("Recupero delle fonti al commit fissato:")
    for n, (u, c) in SOURCES.items():
        fetch(n, u, c)
    print("\nImpronte dei file usati dalla pipeline:")
    for rel in ["moma-exhibitions/MoMAExhibitions1929to1989.csv",
                "tate-collection/artist_data.csv"]:
        p = DEST / rel
        if p.exists():
            print(f"  {rel}\n    sha256 {sha256(p)}")
        else:
            print(f"  {rel}  MANCANTE", file=sys.stderr)
