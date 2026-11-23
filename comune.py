"""L'accordo fra i moduli di ArMoni, in codice invece che in prosa.

`claude/protocollo_ingestione.md` dichiara che ogni dato di ArMoni porta quattro
attributi — fonte, metodo, grado, licenza — e che il grado usa «un vocabolario
fisso». Fino a oggi quell'accordo esisteva solo nel documento: i due moduli lo
rispettavano perche' li scriveva la stessa persona, non perche' qualcosa lo
verificasse. Questo file lo rende verificabile, e i test dei due moduli
falliscono se un modulo emette un termine che non ha dichiarato qui.

PERCHE' NON C'E' UN VOCABOLARIO UNICO DEI GRADI
-----------------------------------------------
La prima versione della proposta prevedeva di unificare i gradi dei due moduli
in una sola scala. Guardando i dati si vede che sarebbe stato un errore: i due
gradi non sono lo stesso campo con due nomi, rispondono a DOMANDE DIVERSE.

    motore   `certainty`  -> «questi due record sono la stessa persona?»
    atlante  `grado`      -> «questo pezzo appartiene a questo filo?»

Tradurre `ipotetico` in `possibile` avrebbe prodotto una scala sola a prezzo di
un significato solo apparente: esattamente il difetto che il protocollo cerca di
evitare, due cose diverse che sembrano parlarsi. Quindi qui si registra un
vocabolario PER DOMINIO, ciascuno con il significato dei suoi termini. Cio' che
si condivide e' la busta dell'asserzione e l'obbligo di dichiarare i termini,
non una scala unica.
"""

NS = "armoni:"

# I quattro attributi che il protocollo (§0) rende obbligatori per ogni dato.
CAMPI_ASSERZIONE = ("fonte", "metodo", "grado", "licenza")

# I due moduli chiamano gli stessi quattro attributi con nomi diversi, per
# ragioni storiche. Non si rinominano: l'atlante e' pubblicato e i suoi file
# sono gia' scaricabili, e un rinomino non aggiungerebbe nulla a nessun lettore.
# Si registra invece la corrispondenza, cosi' la busta e' verificabile su
# entrambi i lati senza toccare i dati.
CAMPI_LOCALI = {
    "motore/identita":     {"fonte": "fonte", "metodo": "method",
                            "grado": "certainty", "licenza": "licenza"},
    "atlante/appartenenza": {"fonte": "fonte", "metodo": "criterio",
                             "grado": "grado", "licenza": "licenza"},
}

# Vocabolari chiusi, uno per dominio. La chiave e' "<modulo>/<domanda>".
# Un modulo puo' emettere solo termini presenti qui: i test lo verificano.
# Aggiungere un termine e' lecito e si fa qui, deliberatamente, non di sfuggita
# nel codice che lo emette.
GRADI = {
    "motore/identita": {
        "certo":      "nome quasi identico e almeno una data concorde",
        "probabile":  "inferenza sostenuta da evidenze",
        "possibile":  "nessun giudice si e' pronunciato; NON e' fiducia bassa",
        "contestato": "fonti discordanti, nessuna prova di distinzione",
    },
    "atlante/appartenenza": {
        "documentato": "il catalogo dell'istituzione lo dichiara",
        "ipotetico":   "ricavato da genere o manifattura; il record non lo dichiara",
    },
    "atlante/datazione": {
        "dichiarato": "una fonte da' le date con quel significato",
        "dedotto":    "ricavato con una regola scritta e misurata",
    },
}

# Relazioni che il motore puo' asserire. Una non-identita' si emette solo con
# prova positiva di distinzione (decisione D1): il silenzio non e' una prova.
RELAZIONI = {
    "sameAs":        "stessa persona",
    "differentFrom": "persone diverse, affermato e non dedotto da un silenzio",
}

# Precisione della collocazione di un luogo.
# Nota: il protocollo §4 elenca «citta', paese, regione, zona, istituzione»;
# i dati dell'atlante usano «luogo, paese, regione». Qui si registra cio' che il
# codice emette davvero, non cio' che il documento dice. La differenza va
# sanata nel protocollo, non nascosta qui.
PRECISIONE_LUOGO = ("luogo", "paese", "regione")

TIPI_FENOMENO = ("movimento", "periodizzazione", "stile", "scuola")


def gradi(dominio: str) -> set[str]:
    """I termini ammessi per un dominio. Solleva se il dominio non esiste."""
    if dominio not in GRADI:
        raise KeyError(f"dominio non dichiarato in comune.GRADI: {dominio!r}. "
                       f"Dichiarati: {sorted(GRADI)}")
    return set(GRADI[dominio])


def grado_valido(dominio: str, termine: str) -> bool:
    return termine in gradi(dominio)


def problemi_asserzione(d: dict, dominio: str) -> list[str]:
    """Elenca cio' che manca o non va in un'asserzione. Lista vuota = a posto.

    Legge i campi con i nomi locali del dominio (CAMPI_LOCALI), cosi' funziona
    sulle asserzioni dei due moduli come sono, senza conversioni.

    Non solleva: restituisce i problemi perche' chi chiama possa contarli tutti
    e riportarli, invece di fermarsi al primo.
    """
    nomi = CAMPI_LOCALI.get(dominio)
    if nomi is None:
        raise KeyError(f"dominio non dichiarato in comune.CAMPI_LOCALI: {dominio!r}")
    out = []
    for campo in CAMPI_ASSERZIONE:
        if not d.get(nomi[campo]):
            out.append(f"manca {campo} (campo {nomi[campo]!r})")
    g = d.get(nomi["grado"])
    if g and not grado_valido(dominio, g):
        out.append(f"grado {g!r} fuori dal vocabolario di {dominio}: "
                   f"{sorted(gradi(dominio))}")
    return out
