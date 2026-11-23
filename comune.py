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
    "nucleo/dichiarazione": {"fonte": "fonte", "metodo": "metodo",
                             "grado": "grado", "licenza": "licenza"},
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
    # aggiunti con il nucleo (armoni/asserzioni.py): da dove viene un dato di un pezzo
    "nucleo/dichiarazione": {
        "dichiarato": "il catalogo lo scrive; ArMoni lo riporta (eventualmente normalizzato con una regola dichiarata)",
        "dedotto":    "ricavato da ArMoni con una regola scritta e misurata; il catalogo non lo scrive",
    },
}

# Relazioni che il motore puo' asserire. Una non-identita' si emette solo con
# prova positiva di distinzione (decisione D1): il silenzio non e' una prova.
RELAZIONI = {
    "sameAs":        "stessa persona",
    "differentFrom": "persone diverse, affermato e non dedotto da un silenzio",
}

# Precisione della collocazione di un luogo: i cinque livelli del protocollo.
#
# ERRORE DICHIARATO (23/11/2026). La prima versione di questo file registrava
# solo tre livelli — «luogo, paese, regione» — con un commento che diceva che i
# cinque del protocollo erano un'aspirazione scritta e non la realta' del
# codice. Era falso. I fili dell'atlante usavano tutti e cinque i livelli da
# subito (`data/luoghi.csv`: citta 83, paese 45, regione 9, istituzione 8,
# zona 2). Avevo campionato un solo file, `web/contesti.json`, e generalizzato
# al progetto: lo stesso errore che questo progetto passa il tempo a cercare,
# commesso dentro il file che dovrebbe impedirlo.
#
# Il test che avevo scritto non l'ha preso perche' controllava anch'esso solo i
# contesti. Ora controlla anche `web/luoghi.json`.
PRECISIONE_LUOGO = ("citta", "zona", "paese", "regione", "istituzione")

# Transitorio, non canonico: il secchio unico che `atlante/src/contesti.py`
# assegnava a tutto cio' che sta dentro un paese, senza distinguere una citta'
# da un'area culturale da un museo. La suddivisione e' scritta e misurata
# (query `contesti_natura_luogo.rq`, 97% di copertura su 297 luoghi), e i dati
# prendono i valori fini al prossimo build dell'atlante. Fino a quel momento
# `luogo` resta ammesso SOLO nei contesti: un test lo confina la', cosi' la
# migrazione resta visibile invece di diventare permanente.
PRECISIONE_TRANSITORIA = ("luogo",)

# I livelli di precisione che possono portare un'ESTENSIONE, cioe' un alone
# sulla mappa. Una citta' e un'istituzione sono punti: la loro superficie
# amministrativa su Wikidata e' fuorviante (Zhangzhou 12.880 km2, Parigi 105).
#
# Prima questa idea non aveva un nome e stava scritta a mano in quattro posti,
# con tre risposte diverse alla stessa domanda: aree.py la chiedeva in un modo
# per i fili e in un altro per i contesti, e atlante.js in un terzo modo. Da qui
# veniva il fatto che una 'zona' dei contesti non avesse mai un alone. Un'idea
# sola con un nome solo e' piu' leggibile di quattro elenchi da tenere allineati
# a memoria.
PRECISIONE_CON_ESTENSIONE = ("paese", "regione", "zona")

# L'estensione si prende da una fonte che la dichiara (su Wikidata, P2046).
# Dove non e' dichiarata, l'unico ripiego legittimo e' il poligono del paese che
# contiene il punto, e SOLO quando il luogo e' esso stesso un paese: altrimenti
# non e' una stima imprecisa, e' l'estensione di un'altra cosa.
#
# Misurato il 23/11/2026 su aree.json: il ripiego era attivo su 23 luoghi di
# precisione 'regione', e sono tutti stati storici senza corrispondenza con uno
# Stato di oggi. Il regno di Gandhara prendeva l'area del Pakistan (871.410
# km2), il Regno Ahom quella dell'India (3.151.482). Un alone cosi' non e'
# approssimato: dice una cosa falsa, e la dice piu' spesso fuori dall'Europa,
# dove i confini di oggi somigliano meno a quelli di allora.
PRECISIONE_CON_RIPIEGO_PAESE = ("paese",)

TIPI_FENOMENO = ("movimento", "periodizzazione", "stile", "scuola")


# Non tutti i domini descrivono un'asserzione intera. Alcuni sono il vocabolario
# di UN CAMPO dentro un'altra asserzione: 'atlante/datazione' gradua il campo
# `quando.metodo` di un contesto, e non ha fonte e licenza proprie. Dichiararlo
# serve all'invariante qui sotto.
DOMINI_DI_CAMPO = ("atlante/datazione",)


def incoerenze() -> list[str]:
    """Controlla che questo file sia coerente con se stesso. Lista vuota = ok.

    Serve perche' due sessioni diverse modificano questo file senza vedersi: git
    fonde il testo, non il significato, e due aggiunte in righe lontane possono
    produrre un file che sembra sano e non lo e'. E' successo: 'atlante/datazione'
    e' stato aggiunto a GRADI e non a CAMPI_LOCALI, e `problemi_asserzione`
    sollevava su quel dominio. Nessuno se n'era accorto perche' nessuno lo
    chiamava con quel dominio: il difetto aspettava il primo che l'avrebbe fatto.
    """
    out = []
    for d in GRADI:
        if d not in CAMPI_LOCALI and d not in DOMINI_DI_CAMPO:
            out.append(f"{d}: in GRADI ma ne' in CAMPI_LOCALI ne' in DOMINI_DI_CAMPO")
    for d in CAMPI_LOCALI:
        if d not in GRADI:
            out.append(f"{d}: in CAMPI_LOCALI ma non in GRADI")
    for d in DOMINI_DI_CAMPO:
        if d not in GRADI:
            out.append(f"{d}: in DOMINI_DI_CAMPO ma non in GRADI")
        if d in CAMPI_LOCALI:
            out.append(f"{d}: non puo' essere sia di campo sia un'asserzione intera")
    return out


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
