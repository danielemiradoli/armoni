"""Il modello di riferimento della base: CIDOC CRM (ISO 21127), nella forma pratica di Linked Art.

Ogni tipo di entità e ogni relazione di ArMoni è definita qui, una volta sola, con la sua corrispondenza
nello standard. Nessuna voce nomina una fonte: le fonti entrano attraverso i lettori (armoni/fonti) e
si adattano a queste voci, mai il contrario (Progetto: claude/principio_universalita.md).

Due livelli, entrambi conformi:
- la base (out/armoni.sqlite) tiene ogni asserzione con fonte, metodo, grado, licenza e prova. In CIDOC CRM
  ogni riga è un E13 Attribute Assignment: chi afferma (P14), su che cosa (P140), quale relazione (P177),
  che cosa (P141), su quale base (P16/P70).
- lo scambio (armoni/linkedart.py) segue il profilo Linked Art, che chiede di usare l'AttributeAssignment
  solo quando serve: ciò che la fonte dichiara diventa la proprietà diretta; ciò che ArMoni deduce, o tiene
  per ipotesi, resta un AttributeAssignment esplicito, con il metodo scritto. La distinzione fra dichiarato
  e dedotto, che è il cuore della base, sopravvive così anche fuori da ArMoni.

Le voci segnate `estensione` non hanno ancora una proprietà diretta in Linked Art: sono espresse come
AttributeAssignment con un tipo di proprietà di ArMoni, dichiarato come tale.
"""
AAT = 'http://vocab.getty.edu/aat/'

# tipo di entità ArMoni → classe CIDOC CRM, classe Linked Art
ENTITA = {
    'oggetto':  dict(crm='E22 Human-Made Object', la='HumanMadeObject'),
    'luogo':    dict(crm='E53 Place', la='Place'),
    'periodo':  dict(crm='E4 Period', la='Period'),
    'gruppo':   dict(crm='E74 Group', la='Group'),          # istituzioni, botteghe, manifatture
    'persona':  dict(crm='E21 Person', la='Person'),        # artefici (dal motore delle identità)
    'tipo':     dict(crm='E55 Type', la='Type'),            # tipi, materiali, tecniche (Getty AAT)
    'filo':     dict(crm='E78 Curated Holding', la='Set'),  # un filo è un insieme curato di pezzi
    'fonte':    dict(crm='E73 Information Object', la='DigitalObject'),   # il catalogo da cui viene il dato
    'autorita': dict(crm='E73 Information Object', la='LinguisticObject'),  # chi ha definito un concetto (PeriodO)
}

# relazione ArMoni → percorso in CIDOC CRM, percorso in Linked Art, tipi ammessi per soggetto e oggetto.
# `valore`: la relazione può portare un testo al posto di un'entità (ciò che la fonte scrive, non ancora collegato);
# in Linked Art quel testo diventa una dichiarazione (Statement) del tipo AAT indicato.
RELAZIONI = {
    'membro_di': dict(
        crm='P46i forms part of → E78', la='member_of', soggetto='oggetto', oggetto=('filo',),
        descrizione='il pezzo fa parte di un filo'),
    'produzione.luogo': dict(
        crm='P108i was produced by → E12 Production → P7 took place at → E53', la='produced_by.took_place_at',
        soggetto='oggetto', oggetto=('luogo',), descrizione='dove il pezzo è stato fatto'),
    'produzione.data': dict(
        crm='P108i → E12 → P4 has time-span → E52 Time-Span', la='produced_by.timespan',
        soggetto='oggetto', oggetto=(), valore=True, descrizione='quando il pezzo è stato fatto (anni inizio/fine)'),
    'produzione.periodo': dict(
        crm='P108i → E12 → P10 falls within → E4 Period', la='produced_by.during',
        soggetto='oggetto', oggetto=('periodo',), valore=True, dichiarazione=AAT + '300435432',  # Period Statement
        descrizione='il periodo in cui il pezzo è stato fatto, come lo nomina il catalogo'),
    'produzione.artefice': dict(
        crm='P108i → E12 → P14 carried out by → E39 Actor', la='produced_by.carried_out_by',
        soggetto='oggetto', oggetto=('persona', 'gruppo'), valore=True, dichiarazione=AAT + '300435436',  # Production Statement
        descrizione='chi ha fatto il pezzo (persona, bottega, manifattura)'),
    'custode': dict(
        crm='P50 has current keeper → E39 Actor', la='current_custodian',
        soggetto='oggetto', oggetto=('gruppo',), descrizione='l\'istituzione che oggi conserva il pezzo'),
    'classificato_come': dict(
        crm='P2 has type → E55 Type', la='classified_as',
        soggetto='oggetto', oggetto=('tipo',), valore=True,  # testo finché il tipo non è collegato a Getty AAT
        descrizione='che genere di oggetto è (vaso, piatto, scatola…)'),
    'mercato_destinazione': dict(
        crm='E13 Attribute Assignment, P177 = «destinato al mercato di» (tipo di proprietà ArMoni)', la='attributed_by',
        soggetto='oggetto', oggetto=('luogo',), estensione=True,
        descrizione='il mercato per cui il pezzo è stato fatto, se il catalogo lo dichiara'),
    'periodo.definizione': dict(
        crm='E13 Attribute Assignment: un\'autorità assegna al periodo un P4 time-span e una P7 copertura',
        la='attributed_by (assigned_property: timespan; used_specific_object: l\'autorità)',
        soggetto='periodo', oggetto=('autorita',), valore=True,
        descrizione='come un\'autorità (PeriodO) definisce il periodo: anni e area'),
}


def tipo_entita(ident):
    """`luogo:Jingdezhen` → 'luogo'."""
    return (ident or '').split(':', 1)[0]


def problemi_modello(a):
    """Che cosa non torna fra un'asserzione e il modello."""
    r = RELAZIONI.get(a.get('relazione'))
    if not r:
        return [f"relazione {a.get('relazione')!r} fuori dal modello"]
    p = []
    if tipo_entita(a.get('soggetto')) != r['soggetto']:
        p.append(f"{a['relazione']}: soggetto {tipo_entita(a.get('soggetto'))!r}, atteso {r['soggetto']!r}")
    if a.get('oggetto') and tipo_entita(a['oggetto']) not in r['oggetto']:
        p.append(f"{a['relazione']}: oggetto {tipo_entita(a['oggetto'])!r}, attesi {r['oggetto']}")
    if not a.get('oggetto') and not r.get('valore'):
        p.append(f"{a['relazione']}: richiede un'entità, non un testo")
    return p
