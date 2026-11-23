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


def test_asserzioni_rispettano_l_accordo_comune():
    """L'accordo del protocollo diventa verificabile invece che fiduciario.

    Fino a oggi la coerenza fra i due moduli dipendeva dal fatto che li
    scrivesse la stessa persona. Questo test fallisce se il motore emette un
    grado fuori dal vocabolario dichiarato in comune.py, o se un'asserzione
    perde uno dei quattro attributi obbligatori del protocollo.
    """
    import sys as _s, pathlib as _p
    _s.path.insert(0, str(_p.Path(__file__).resolve().parent.parent))
    import comune
    asserzioni = [r.to_assertion(i, m) for i, m in enumerate(_tutte, 1)]
    assert asserzioni, "nessuna asserzione da verificare"
    guasti = []
    for x in asserzioni:
        guasti += ["%s: %s" % (x["id"], g)
                   for g in comune.problemi_asserzione(x, "motore/identita")]
        if x["relation"] not in comune.RELAZIONI:
            guasti.append("%s: relazione %r non dichiarata" % (x["id"], x["relation"]))
    assert not guasti, "%d asserzioni fuori accordo: %s" % (len(guasti), guasti[:3])


def test_il_blocco_non_assume_dove_sta_il_cognome():
    """CRITERIO DI VERIFICA SCRITTO IN ANTICIPO. Oggi FALLISCE apposta.

    `block_keys` sa dove sta il cognome perche' gliel'ha detto il formato: nella
    forma con virgola e' prima della virgola, nella forma estesa e' l'ultimo
    token. Sono le due convenzioni di MoMA e Tate, e nei loro roster funzionano.

    Non sono convenzioni universali. Dove il cognome viene per primo senza
    virgola — coreano, cinese, ungherese, e molti cataloghi che non traducono
    l'ordine — l'ultimo token e' il nome di battesimo, e le due forme dello
    stesso artista finiscono in blocchi che non si incontrano mai:

        Kim Jeong-hui  -> blocco {'hui'}      Kim, Jeong-hui -> blocco {'kim'}
        Qi Baishi      -> blocco {'baishi'}   Qi, Baishi     -> blocco {'qi'}

    E' lo stesso guasto di «Willem de Kooning» contro «Kooning, Willem de»,
    che e' stato risolto il 10/11 perche' era nei dati che avevamo. Questo non
    e' stato risolto perche' non e' nei dati che avevamo: MoMA e Tate scrivono
    i nomi dell'Asia orientale all'occidentale. Il difetto non e' meno reale,
    e' solo invisibile alle nostre fonti — e l'atlante e' pieno di cataloghi
    coreani e giapponesi.

    Per questo il test resta rosso: non e' un lavoro da fare ora (il motore e'
    in pausa), e' un limite da non dimenticare. La soluzione non e' un elenco
    piu' lungo di eccezioni: e' non dedurre affatto la posizione del cognome,
    e bloccare su tutti i token, pagando il costo in confronti. Da misurare
    quando ci sara' un campione su cui misurare.

    Nota: anche fra nomi europei l'inversione non regge
    ('de Kooning Willem' da' blocco {'willem'}). L'assunzione non e' «i nomi
    sono occidentali», e' «il formato dichiara dove sta il cognome».
    """
    coppie = [("Kim Jeong-hui", "Kim, Jeong-hui"),
              ("Qi Baishi", "Qi, Baishi")]
    for esteso, con_virgola in coppie:
        a = r.block_keys(esteso, False)
        b = r.block_keys(con_virgola, True)
        assert a & b, (f"{esteso!r} e {con_virgola!r} non si incontrano mai: "
                       f"{sorted(a)} contro {sorted(b)}")


test_il_blocco_non_assume_dove_sta_il_cognome.atteso_fallire = True


def test_le_particelle_dichiarate_sono_solo_europee():
    """Guardia su un'assunzione, non su un guasto. Verde: constata e ricorda.

    `PARTICLES` elenca 21 particelle, tutte europee, e `STOP` elenca onorifici
    anglosassoni — 'om' e 'ch' sono due onorificenze britanniche. Non c'e'
    nulla di arabo ('al', 'ibn', 'bin', 'abu'), di persiano, di indonesiano.

    La conseguenza misurabile: 'al-Bawwab, Ibn' produce la chiave di blocco
    'al', che non e' un cognome ma un articolo. Ogni nome arabo traslitterato
    con 'al-' finirebbe nello stesso blocco, che diventerebbe enorme e inutile.

    Il test non pretende di correggere: fissa l'elenco di oggi, cosi' chi lo
    allunga lo fa deliberatamente e con una misura, invece di aggiungere la
    particella che serve al caso che ha davanti — che e' il modo in cui una
    regola nata da poche fonti si cristallizza senza che nessuno lo decida.
    """
    assert "al" not in r.PARTICLES, "se 'al' entra, serve la misura sul costo del blocco"
    assert r.block_keys("al-Bawwab, Ibn", True) == frozenset({"al", "bawwab"})
    assert {"om", "ch", "sir", "dame"} <= r.STOP


def test_nome_in_cirillico_non_deve_sparire():
    """Era il criterio di verifica scritto prima della modifica, e restava rosso
    di proposito. Verde dal 23/11/2026.

    Prima `tokens()` passava per `encode("ascii", "ignore")`: su una scrittura
    non latina non restituiva una versione imprecisa del nome, restituiva la
    stringa vuota, e il caricatore eliminava la riga. Il record non compariva
    ne' fra le asserzioni ne' fra gli errori, e mancava anche dal denominatore
    del richiamo: nessuna misura poteva accorgersene.
    """
    assert r.name_key("Казимир Малевич") == "казимир малевич"
    for nome in ("葛飾 北斎", "김정희", "محمد", "Θεοτοκόπουλος"):
        assert r.name_key(nome), f"{nome} si riduce a chiave vuota"
        assert r.block_keys(nome, False), f"{nome} non ha chiavi di blocco"


def test_un_record_non_latino_resta_nel_roster():
    """Piu' forte del precedente: non basta che la chiave non sia vuota, il
    record deve sopravvivere al caricatore. E' il punto esatto in cui spariva.
    """
    r._record_dropped("moma", ["Казимир Малевич", "葛飾 北斎", "Pablo Picasso"])
    assert r.DROPPED["moma"]["illeggibile"] == []
    assert r.DROPPED["moma"]["senza_nome"] == []
    # cio' che si scarta ancora, e deve restare scartato
    r._record_dropped("moma", ["1234 ---", "", None])
    assert len(r.DROPPED["moma"]["illeggibile"]) == 1
    assert len(r.DROPPED["moma"]["senza_nome"]) == 2


def test_le_chiavi_latine_non_cambiano():
    """Guardia di non-regressione sul ripiegamento latino.

    La prima stesura della correzione sostituiva con uno spazio le lettere
    latine che non si ripiegano su ASCII, invece di eliminarle: 'Molgaard'
    diventava due token, e 11 nomi scandinavi cambiavano chiave. L'ha preso il
    confronto con la linea di base, non la lettura del codice. Questi valori
    bloccano quel comportamento.
    """
    atteso = {
        "Nicolas de Staël":           "de nicolas stael",
        "Jean (Hans) Arp":            "arp jean",
        "L. S. Lowry":                "l lowry s",
        "Mølgaard-Nielsen":           "mlgaard nielsen",   # 'o' barrata eliminata
        "Jørgen Ditzel":              "ditzel jrgen",
        "Willem de Kooning":          "de kooning willem",
    }
    for nome, chiave in atteso.items():
        assert r.name_key(nome) == chiave, f"{nome}: {r.name_key(nome)!r} != {chiave!r}"


def test_comune_e_coerente_con_se_stesso():
    """Due sessioni modificano comune.py senza vedersi: git fonde il testo, non
    il significato. Questo test sta in ENTRAMBI i moduli di proposito, cosi' chi
    tocca l'accordo lo scopre da qualunque lato stia lavorando.
    """
    import sys as _s, pathlib as _p
    _s.path.insert(0, str(_p.Path(__file__).resolve().parent.parent))
    import comune
    assert not comune.incoerenze(), comune.incoerenze()


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
