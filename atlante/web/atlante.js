{
const $ = s => document.querySelector(s);
const probe = document.createElement('i'); probe.style.display = 'none'; document.body.appendChild(probe);
const css = v => { probe.style.color = `var(${v})`; return getComputedStyle(probe).color; };
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmtY = y => y < 0 ? `${-y} a.C.` : String(y);
const PREC = {citta: 'città', paese: 'solo paese', regione: 'regione', zona: 'zona', istituzione: 'istituzione'};
// I livelli di precisione che portano un alone, cioè un'estensione sulla mappa.
// Deve restare uguale a comune.PRECISIONE_CON_ESTENSIONE: un test lo verifica.
// Prima la stessa domanda era scritta in due modi diversi dentro prepAloni —
// un elenco per i fili e un «diverso da luogo» per i contesti — ed è da lì che
// veniva il fatto che una zona dei contesti non avesse mai un alone.
const CON_ESTENSIONE = ['paese', 'regione', 'zona'];
const FILO = /^[a-z]+$/.test(new URLSearchParams(location.search).get('filo') || '') ? new URLSearchParams(location.search).get('filo') : 'blu';
// la lacca ha pezzi di scavo dal I millennio a.C. (Lelang, Han): il suo filo parte prima
const T0 = FILO === 'lacca' || FILO === 'confronto' ? -500 : 700, T1 = 2000, PASSO = T1 - T0 > 1600 ? 250 : 100;

const S = {corsie: 'wikidata', year: 1640, win: 25, proj: 'globo', rot: [-40, -28], k: 1, sel: null, place: null, q: '',
  L: {opere: 1, periodi: 0, confini: 1, origini: 1, sedi: 1, spostamenti: 0, mercati: 1, silenzio: 0, ipotetici: 1, dedotti: 0, vam: 1, letteratura: 1, contesti: 0, relazioni: 0}, CT: new Set(['movimento', 'scuola', 'stile', 'periodizzazione']), F: {met: 1, cma: 1, wd: 1, colbase: 1, emuseum: 1, aic: 1},
  tav: [], mode: 'ricerca', tappa: 0};
// CX: stili e movimenti (livello Contesti); APERTO: anni mostrati quando la fine non è dichiarata
const G = {on: {}, mem: {}};
let CX = [], cagg = [], CXR = null; const APERTO = 30, TIPI_CX = ['movimento', 'scuola', 'stile', 'periodizzazione'];
let QU = null, qmet = 'doc', LET = null, lagg = [], PO = null, VAM = null, vagg = [], NOD = [], O = [], LU = {}, PER = [], ANNI = [], TERRE = null, CONF = {}, act = [], agg = [];

const TAPPE = [
 {t: 'Blu su bianco, prima della porcellana', y: 850, w: 60, rot: [-44, -30], L: {}, hi: ['Iraq'],
  p: 'Nel IX secolo, fra le merci cinesi che raggiungono il mondo islamico ci sono anche terracotte e gres dipinti sotto coperta in blu di manganese e cobalto (Zhao 2015, §16). Nell\'Iraq abbaside si dipinge in blu su bianco, e il catalogo del Met intitola uno di questi pezzi «Bowl Emulating Chinese Stoneware»: l\'imitazione la dichiara il museo stesso.',
  nv: 'Che l\'invetriatura bianca opaca irachena nasca per imitare la ceramica bianca cinese è una lettura corrente, non verificata qui su una fonte.'},
 {t: 'Il cobalto viaggia verso est', y: 1340, w: 30, rot: [-90, -32], L: {letteratura: 1}, hi: ['China', 'Jingdezhen', 'Iran', 'Kashan'],
  p: 'Sotto la dinastia Yuan, a Jingdezhen, la porcellana dipinta sotto coperta prende la forma che chiamiamo blu e bianco. Per Ömür Tufan, responsabile delle porcellane di Topkapı, furono maestri ceramisti iraniani a insegnare ai cinesi la tecnica con il cobalto, e mercanti iraniani a portare in Cina il minerale (Tufan 2024, p. 124): è la sua tesi, scritta da Istanbul, e va letta come tale. Ad Ardabil restano 37 pezzi di questo secolo, soprattutto grandi piatti, e a Topkapı 40 (Medley 1986, par. 3; Tufan 2024, p. 125).',
  nv: 'L\'uso di cobalto importato dall\'Iran è sostenuto da gran parte della storiografia; qui è riportato solo nella versione di Tufan.'},
 {t: 'Il Quattrocento, ovunque', y: 1450, w: 25, rot: [-60, -12], L: {letteratura: 1}, hi: ['Vietnam', 'China', 'Egypt', 'Syria'],
  p: 'Nei dati, intorno al 1450, il Vietnam pesa quasi quanto la Cina, e il blu e bianco si imita anche in Egitto. Dal 1370 il blu e bianco vietnamita arriva anche in Africa orientale (Zhao 2015, §24). Ad Ardabil il blu e bianco del primo Quattrocento è il gruppo più grande, oltre 200 pezzi; dopo il 1436, con la fine delle spedizioni marittime cinesi, il commercio cala bruscamente: del tardo Quattrocento restano 25-30 pezzi (Medley 1986, par. 4 e 7).',
  nv: 'Il legame fra l\'ascesa delle esportazioni vietnamite e le restrizioni marittime dei Ming è un\'ipotesi diffusa, non verificata qui. Corea e Siria, che pure dipingono o imitano il blu e bianco in questo periodo secondo la storiografia, nei dati di questa finestra non compaiono.'},
 {t: 'Collezioni di corte: Tabriz, Ardabil, Istanbul', y: 1570, w: 50, rot: [-40, -36], L: {letteratura: 1}, hi: [],
  p: 'Nel 1516 il blu e bianco del Trecento della collezione reale di Tabriz finisce a Istanbul come bottino (Medley 1986, par. 3). Nel 1611 Shah Abbas I installa nel santuario di Ardabil un dono di 1.162 porcellane cinesi, circa 400 blu e bianche (par. 1-3). Topkapı ne conserva oggi circa 12.000, di cui 5.373 blu e bianche in inventario (Tufan 2024, p. 124). Le grandi raccolte di blu e bianco antico non nascono in Europa.'},
 {t: 'Iznik, il ricambio della corte', y: 1560, w: 30, rot: [-30, -38], L: {letteratura: 1}, hi: ['İznik', 'Kütahya'],
  p: 'Nel 1582, per la festa di circoncisione del principe Mehmed, le 397 porcellane cinesi prese dal tesoro non bastarono, e si comprarono al bazar 541 piatti di Iznik (Tufan 2024, p. 145, dal cronista Selânikî). Iznik non è soltanto imitazione: è ciò con cui la corte sostituisce la Cina quando la Cina non basta. Per molti pezzi di Iznik, però, il catalogo non nomina il colore: nei dati sono ipotetici.',
  nv: 'Che le botteghe di Iznik partano da modelli cinesi trasformandoli è una lettura corrente, non verificata qui.'},
 {t: 'Dalla porcellana kraak a Delft', y: 1640, w: 25, rot: [-50, -38], L: {mercati: 1, vam: 1}, hi: ['China', 'Netherlands', 'Delft'],
  p: 'Intorno al 1640 il catalogo del Met dichiara due destinazioni: porcellana cinese per il mercato giapponese e porcellana giapponese per quello europeo (le linee rosse tratteggiate). Il mercato europeo, nei cataloghi, si legge più nei luoghi di conservazione che nelle destinazioni dichiarate. I rombi del V&A mostrano dove si concentra la sua raccolta di questi decenni.',
  nv: 'Il ruolo della Compagnia olandese delle Indie orientali nel portare la porcellana kraak in Europa e la nascita di Delft come sua imitazione sono letture correnti, non verificate qui su una fonte.'},
 {t: 'Arita dopo la caduta dei Ming', y: 1675, w: 20, rot: [-120, -30], L: {mercati: 1, vam: 1}, hi: ['Japan', 'Arita'],
  p: 'Nei dati il Giappone cresce proprio in questi decenni: i pezzi giapponesi che iniziano fra il 1650 e il 1699 sono 127, contro gli 87 del cinquantennio precedente, e nei conteggi del V&A passano da circa 44 a circa 98.',
  nv: 'Che le fornaci di Arita entrino nell\'esportazione per supplire alla crisi della produzione cinese fra Ming e Qing, attraverso Nagasaki, è una lettura corrente, non verificata qui.'},
 {t: 'Il galeone di Manila', y: 1640, w: 70, rot: [120, -22], L: {letteratura: 1}, hi: ['Puebla City', 'Mexico'],
  p: 'Sulla costa della Baja California un galeone di Manila diretto verso est lascia un carico di porcellana kraak, datato 1575-1577; a Drakes Bay restano le porcellane di Francis Drake (1579) e del naufragio del San Agustín (1595) (Von der Porten 2015). I Miwok della baia ne trasformarono i frammenti in gioielli (Zhao 2015, §30). A Puebla, nei dati, tutti i pezzi sono ipotetici: nessun record nomina il blu.',
  nv: 'Che la maiolica blu di Puebla risponda alla porcellana arrivata con il galeone e alla Talavera spagnola è una lettura corrente, non verificata qui.'},
 {t: 'Chi divide il tempo', y: 1500, w: 25, rot: [-60, -30], L: {}, hi: [], po: true,
  p: 'Lo stesso «medioevo» finisce nel 1300 per Ephraim Emerton (1918), nel 1540 per Historic England, nel 1600 per la storiografia giapponese che Japan Search registra come 中世 (PeriodO; Japan Search). Le corsie del tempo non sono un orologio comune: sono asserzioni di qualcuno, in una lingua. Per la Cina le sole definizioni in una lingua dell\'Asia orientale vengono dal Giappone, e portano il suo sguardo.'},
 {t: 'Ciò che questi dati mostrano a fatica', y: 1450, w: 400, rot: [-40, 2], L: {silenzio: 1, sedi: 1, spostamenti: 1, letteratura: 1}, hi: [],
  p: 'Sulla costa swahili gli scavi trovano porcellana cinese, ma quasi ovunque sotto l\'1% dei frammenti: 0,12% a Shanga, 0,9% a Gedi (Zhao 2015, §31, n. 69); dalla fine del Duecento compare nelle moschee e nelle nicchie delle case (§29). I musei raccontano soprattutto la produzione e il collezionismo; il consumo si legge negli scavi e negli inventari, che non sono dataset. Mancano ancora l\'India, il Sud-est asiatico insulare, le città dell\'America spagnola.'}
];

/* ---------- dati ---------- */
const j = u => fetch(u).then(r => { if (!r.ok) throw new Error(u); return r.json(); });
/* Filo tematico: ?filo=lacca carica i dati in fili/lacca/. Il primo filo (blu e bianco) resta alla radice
   e ha strati suoi (V&A, letteratura, percorso, riepilogo di affidabilità) che gli altri fili non hanno ancora. */
const TAVK = 'armoni-tavolo' + (FILO === 'blu' ? '' : '-' + FILO);
const BASE = FILO === 'blu' ? '' : `fili/${FILO}/`, PRIMO = FILO === 'blu';
/* Confronto: due fili sullo stesso globo. Ogni pezzo porta il suo filo (fl); i luoghi si sommano. */
const CONFRONTO = FILO === 'confronto', FILI = CONFRONTO ? ['blu', 'lacca'] : [FILO], NOMI_FILO = {blu: 'blu e bianco', lacca: 'lacca'};
const baseDi = f => f === 'blu' ? '' : `fili/${f}/`;
const dati = nome => Promise.all(FILI.map(f => j(baseDi(f) + nome).then(v => nome === 'opere.json' && CONFRONTO ? v.map(x => ({...x, fl: f})) : v))).then(vs => vs.flat());
const solo1 = (u, d = null) => PRIMO ? j(u).catch(() => d) : Promise.resolve(d);
j('periodi_base.json').then(v => { PB = v; }).catch(() => {});
Promise.all([dati('opere.json'), dati('luoghi.json'), j('periodi.json'), j('confini/anni.json'), j('terre.json'), solo1('densita_vam.json'), j('periodo.json').catch(() => null), solo1('letteratura.json'), solo1('qualita.json'), j('contesti.json').catch(() => null), j('aree.json').catch(() => ({}))]).then(([o, l, p, a, t, v, po, le, qu, cx, ar]) => {
  QU = qu; AREE = ar || {};
  if (cx) { CXR = cx; CX = cx.elementi.map(e => ({...e, fv: e.quando.a ?? e.quando.da + APERTO})); }
  LET = le; if (LET) for (const x of LET.siti) LU['sito:' + x.id] = {...x, lat: +x.lat, lon: +x.lon};
  PO = po;  // i periodi partono dalle dinastie di Wikidata, che si leggono da sole
  for (const x of l) LU[x.id] = {...x, lat: +x.lat, lon: +x.lon};
  if (v) { VAM = v; for (const x of v.luoghi) if (!LU[x.id]) LU[x.id] = {...x, lat: +x.lat, lon: +x.lon}; }
  NOD = o.filter(x => x.inizio == null);
  O = o.filter(x => x.inizio != null).map(x => ({...x, o: LU[x.origine], s: LU[x.sede], m: LU[x.mercato],
    hay: [x.titolo, x.cultura, x.tecnica, LU[x.origine]?.nome, LU[x.sede]?.nome].filter(Boolean).join(' ').toLowerCase()}));  // anche i luoghi: «iznik» trova i pezzi fatti a Iznik
  PER = p.map(x => ({...x, inizio: +x.inizio, fine: +x.fine}));
  ANNI = a; $('#corsie').value = S.corsie; TERRE = topojson.feature(t, t.objects.land);
  caricaTavoli(); tavoloDaLink();
  // filtri per fonte e strati che in questo filo non hanno dati: nascosti, non spenti in silenzio
  const fonti = new Set(o.map(x => x.fonte));
  document.querySelectorAll('[data-f]').forEach(i => { if (!fonti.has(i.dataset.f)) i.closest('label').hidden = true; });
  if (!VAM) $('[data-l="vam"]').closest('label').hidden = true;
  if (!LET) $('[data-l="letteratura"]').closest('label').hidden = true;
  if (!VAM && !LET) $('[data-grp="quantita"]').hidden = true;
  if (!o.some(x => x.grado === 'ipotetico')) $('[data-l="ipotetici"]').closest('label').hidden = true;
  if (!PRIMO) { $('#m-percorso').disabled = true; $('#m-percorso').title = 'Il percorso in tappe per ora esiste solo per il filo blu e bianco'; }
  Promise.all(FILI.map(f => j(baseDi(f) + 'copertura.json').catch(() => null))).then(v => { COP = v.filter(Boolean); renderCopertura(); });
  infoLivelli(); pannelli(); sezLeggi(); leggiVista(); route(); update();
}).catch(e => { $('#ctx').innerHTML = `<p>Non riesco a caricare i dati (${esc(e.message)}).</p>`; });

/* Dettaglio secondo l'ingrandimento: confini e coste più fini si caricano solo quando servono.
   Finché il file dettagliato non è arrivato si disegna quello semplice. */
const FINE = {confini: 4, terre: 2.5, terre10: 12};
function confini(y) {
  if (!ANNI.length) return {anno: null, geo: null};  // i dati non sono ancora arrivati
  const a = ANNI.filter(v => v <= y).pop() ?? ANNI[0], fine = S.k >= FINE.confini, key = fine ? 'f' + a : a;
  if (!CONF[key]) { CONF[key] = 'caricamento'; j(`confini/${fine ? 'fini/' : ''}${a}.json`).then(t => { const k = Object.keys(t.objects)[0]; CONF[key] = topojson.feature(t, t.objects[k]); draw(); }).catch(() => { CONF[key] = null; }); }
  const ok = v => v && v !== 'caricamento';
  return {anno: a, geo: ok(CONF[key]) ? CONF[key] : ok(CONF[a]) ? CONF[a] : null};
}
let TERRE50 = null, TERRE10 = null;
function terre() {
  if (S.k < FINE.terre) return TERRE;
  if (S.k >= FINE.terre10) {  // coste 1:10 milioni, solo da molto vicino
    if (!TERRE10) { TERRE10 = 'caricamento'; j('terre10.json').then(t => { TERRE10 = topojson.feature(t, t.objects.land); draw(); }).catch(() => { TERRE10 = null; }); }
    if (TERRE10 && TERRE10 !== 'caricamento') return TERRE10;
  }
  if (!TERRE50) { TERRE50 = 'caricamento'; j('terre50.json').then(t => { TERRE50 = topojson.feature(t, t.objects.land); draw(); }).catch(() => { TERRE50 = null; }); }
  return TERRE50 && TERRE50 !== 'caricamento' ? TERRE50 : TERRE;
}

// luogo dichiarato; quello dedotto solo se lo strato e' acceso, e mai al posto del dichiarato
const luogo = x => x.o ? x.origine : S.L.dedotti && LU[x.origine_dedotta] ? x.origine_dedotta : null;
/* Ricerca nel filo per categorie: provenienza (macro-regione del luogo d'origine, la stessa dei contesti)
   e tipo di oggetto (letto dal nome nella scheda). '?' = senza luogo o tipo non riconosciuto. */
const CAT = {reg: '', tipo: '', ctx: ''};
let PB = {};  // concetti di periodo della base (armoni/periodi.py): qid → {n, a, b}
const regDi = x => LU[luogo(x)]?.macroregione || '?';
const passa = x => S.L.opere && S.F[x.fonte] && (S.L.ipotetici || x.grado === 'documentato') &&
  (!CAT.reg || regDi(x) === CAT.reg) && (!CAT.tipo || (x.tipo || '?') === CAT.tipo);
function filtra() {
  const q = S.q.toLowerCase();
  act = O.filter(x => x.inizio <= S.year + S.win && x.fine >= S.year - S.win && passa(x) && (!q || x.hay.includes(q)));
  const m = new Map();
  for (const x of act) { const id = luogo(x); if (!id) continue; const k = x.fl ? id + '|' + x.fl : id; const g = m.get(k) || {id, f: x.fl || '', l: LU[id], n: 0, doc: 0, inc: 0, ded: 0}; g.n++; if (x.grado === 'documentato') g.doc++; if (x.origine_incerta) g.inc++; if (!x.o) g.ded++; m.set(k, g); }
  agg = [...m.values()].sort((a, b) => b.n - a.n);
  const vm = new Map();
  if (VAM) for (const c of VAM.celle) if (c.d + 9 >= S.year - S.win && c.d <= S.year + S.win) vm.set(c.l, (vm.get(c.l) || 0) + c.n);
  const lm = new Map(); if (LET) for (const a of LET.asserzioni) if (a.fine >= S.year - S.win && a.inizio <= S.year + S.win) { const k = 'sito:' + a.sito_id; lm.set(k, [...(lm.get(k) || []), a]); }
  lagg = [...lm].map(([id, as]) => ({id, l: LU[id], as, n: as.length}));
  vagg = [...vm].map(([id, n]) => ({id, l: LU[id], n})).filter(g => g.n >= .5).sort((a, b) => b.n - a.n);
  if (!S.L.opere) { vagg = []; lagg = []; }  // V&A e letteratura parlano degli oggetti del filo
  cagg = S.L.contesti ? CX.filter(e => S.CT.has(e.tipo) && (!CAT.ctx || e.corsia === CAT.ctx) && e.quando.da <= S.year + S.win && e.fv >= S.year - S.win && (!q || (e.nome + ' ' + (e.nome_en || '')).toLowerCase().includes(q))) : [];
}

/* ---------- mappa ---------- */
const cv = $('#cv'), ctx = cv.getContext('2d'), fig = $('#fig');
/* Alone: per ciò che ha un'estensione (paesi, regioni, continenti) un disco trasparente grande quanto
   l'area vera, che pulsa piano. Sta su un canvas suo, sopra la mappa e senza clic, così pulsare non
   costringe a ridisegnare tutto. Le città non hanno alone. */
const av = $('#alone'), actx = av.getContext('2d');
let AREE = {}, ALONI = [], rafAlone = null, ultimoAlone = 0;
const RIDOTTO = matchMedia('(prefers-reduced-motion: reduce)');
function prepAloni(co, cel) {
  const v = new Map(), add = (id, c, col) => { const a = AREE[id]; if (a && !v.has(id + col)) { const h = [...id].reduce((n, ch) => (n * 31 + ch.charCodeAt(0)) >>> 0, 7);
    // ogni alone ha fase e ritmo suoi (2,4–3,6 s), ricavati dal nome: diversi fra loro, uguali da una visita all'altra
    v.set(id + col, {g: d3.geoCircle().center(c).radius(Math.sqrt(a.km2 / Math.PI) / 111.195)(), col, fase: (h % 628) / 100, ritmo: 2400 + (h >>> 10) % 1200}); } };
  if (S.L.origini) for (const g of agg) if (CON_ESTENSIONE.includes(g.l.precisione)) add(g.l.qid, [g.l.lon, g.l.lat], co);
  if (S.L.contesti) for (const e of cagg) for (const l of e.luoghi) if (CON_ESTENSIONE.includes(l.precisione)) add(l.id, [l.lon, l.lat], cel);
  ALONI = [...v.values()];
  if (!rafAlone) rafAlone = requestAnimationFrame(anima);
}
function disegnaAloni(t) {
  actx.clearRect(0, 0, W, H); if (!ALONI.length || !proj) return;
  // la pulsazione cambia solo la trasparenza, nulla si sposta: resta anche con «riduci movimento», più lenta e più tenue
  const lento = RIDOTTO.matches ? 1.7 : 1, pa = d3.geoPath(proj, actx);
  const forza = matchMedia('(prefers-color-scheme: dark)').matches ? .7 : .9;  // il giallo si vede molto sullo scuro e poco sul chiaro
  for (const a of ALONI) { const p = .5 + .5 * Math.sin(a.fase + t * 2 * Math.PI / (a.ritmo * lento)); actx.beginPath(); pa(a.g); actx.fillStyle = a.col; actx.globalAlpha = (.03 + .07 * p) * forza; actx.fill();
    actx.globalAlpha = (.12 + .28 * p) * forza; actx.lineWidth = 1; actx.strokeStyle = a.col; actx.stroke(); }
  actx.globalAlpha = 1;
}
function anima(t) {
  rafAlone = null;
  if (t - ultimoAlone > 40) { ultimoAlone = t; disegnaAloni(t); }  // circa 25 immagini al secondo bastano
  if (ALONI.length && !document.hidden) rafAlone = requestAnimationFrame(anima);
}
document.addEventListener('visibilitychange', () => { if (!document.hidden && !rafAlone) rafAlone = requestAnimationFrame(anima); });
let W = 0, H = 0, proj, path;
function setProj() {
  const R = Math.min(W, H) * 0.46;
  proj = S.proj === 'globo' ? d3.geoOrthographic().rotate(S.rot).scale(R * S.k).translate([W / 2, H / 2]).clipAngle(90)
    : d3.geoEqualEarth().rotate([S.rot[0], 0]).fitExtent([[12, 12], [W - 12, H - 12]], {type: 'Sphere'});
  if (S.proj !== 'globo' && S.k > 1) {  // carta piana: ingrandisce attorno al punto che si sta guardando
    proj.scale(proj.scale() * S.k); const p = proj([-S.rot[0], -S.rot[1]]), t = proj.translate();
    proj.translate([t[0] + W / 2 - p[0], t[1] + H / 2 - p[1]]);
  }
  path = d3.geoPath(proj, ctx);
}
const visibile = c => S.proj !== 'globo' || d3.geoDistance(c, [-S.rot[0], -S.rot[1]]) < Math.PI / 2;
const rr = g => g.l.precisione === 'citta' ? 2.5 + Math.sqrt(g.n) * 1.5 : 6 + Math.sqrt(g.n) * 2.1;

// spazio già occupato da un nome sulla mappa: chi arriva dopo non ci scrive sopra
let OCC = [];
const libero = b => !OCC.some(o => b[0] < o[2] && b[2] > o[0] && b[1] < o[3] && b[3] > o[1]);
/* Ventaglio: quando ci si avvicina, i segni di livelli diversi che cadono nello stesso punto (un luogo
   d'origine, i suoi conteggi V&A, uno scavo, un museo, i fenomeni nati lì) si aprono a raggiera attorno
   al punto vero, collegati da un filo. Il segno più grande resta al centro. Sotto VENTAGLIO volte di
   ingrandimento non si apre nulla: a scala mondo i segni restano sul loro punto. */
const VENTAGLIO = 2.5;
let OFF = new Map();
const P = (k, id, c) => { const p = proj(c), o = OFF.get(k + ':' + id); return o ? [p[0] + o[0], p[1] + o[1]] : p; };
function ventaglio() {
  OFF = new Map(); if (S.k < VENTAGLIO) return [];
  const it = [], add = (k, id, c, r) => { if (visibile(c)) { const [x, y] = proj(c); it.push({k, id, x, y, r}); } };
  if (S.L.origini) for (const g of agg) add('o' + g.f, g.id, [g.l.lon, g.l.lat], rr(g));
  if (S.L.vam) for (const g of vagg) add('v', g.id, [g.l.lon, g.l.lat], 3 + Math.sqrt(g.n) * 1.3);
  if (S.L.letteratura) for (const g of lagg) add('l', g.id, [g.l.lon, g.l.lat], 7);
  if (S.L.sedi) for (const k of new Set(act.map(x => x.sede).filter(Boolean))) { const l = LU[k]; if (l) add('s', k, [l.lon, l.lat], 5); }
  if (S.L.contesti) for (const e of cagg) for (const l of e.luoghi) add('m', e.id + '|' + l.id, [l.lon, l.lat], l.precisione === 'paese' ? 7 : 4.5);
  it.sort((a, b) => b.r - a.r);
  const gruppi = [];
  for (const m of it) { const g = gruppi.find(g => Math.hypot(g[0].x - m.x, g[0].y - m.y) < 6); g ? g.push(m) : gruppi.push([m]); }
  const fili = [];
  for (const g of gruppi) if (g.length > 1) {
    const [c, ...resto] = g, R = Math.max(c.r + Math.max(...resto.map(m => m.r)) + 8, resto.length * 5.5, 22);  // nessun segno tocca quello centrale
    resto.forEach((m, i) => { const a = -Math.PI / 2 + 2 * Math.PI * i / resto.length, dx = R * Math.cos(a), dy = R * Math.sin(a);
      OFF.set(m.k + ':' + m.id, [m.x - c.x + dx, m.y - c.y + dy]); fili.push([c.x, c.y, c.x + dx, c.y + dy]); });
  }
  return fili;
}
function draw() {
  OCC = [];
  if (!W) return;
  setProj();
  const fili = ventaglio();
  const co = css('--co'), c0 = co, cl = css('--lacca'), fe = css('--fe'), ink = css('--ink'), mute = css('--mute'), cel = css('--cel');
  ctx.clearRect(0, 0, W, H);
  ctx.beginPath(); path({type: 'Sphere'}); ctx.fillStyle = css('--glaze'); ctx.fill();
  ctx.lineWidth = 1.2; ctx.strokeStyle = co; ctx.globalAlpha = .55; ctx.stroke(); ctx.globalAlpha = 1;
  ctx.beginPath(); path(d3.geoGraticule10()); ctx.strokeStyle = co; ctx.globalAlpha = .08; ctx.lineWidth = .6; ctx.stroke();
  ctx.beginPath(); path(terre()); ctx.fillStyle = co; ctx.globalAlpha = .1; ctx.fill(); ctx.globalAlpha = 1;
  const cf = confini(S.year);
  if (S.L.confini && cf.geo) { ctx.beginPath(); path(cf.geo); ctx.strokeStyle = co; ctx.globalAlpha = .42; ctx.lineWidth = .7; ctx.stroke(); ctx.globalAlpha = 1; }
  const hi = S.mode === 'percorso' ? new Set(TAPPE[S.tappa].hi) : null;
  if (fili.length) { ctx.beginPath(); for (const [a, b, c2, d] of fili) { ctx.moveTo(a, b); ctx.lineTo(c2, d); } ctx.strokeStyle = mute; ctx.globalAlpha = .5; ctx.lineWidth = .8; ctx.stroke(); ctx.globalAlpha = 1; }
  if (S.L.spostamenti) {
    const m = new Map(); for (const x of act) if (x.o && x.s) { const k = x.origine + '>' + x.sede; m.set(k, (m.get(k) || 0) + 1); }
    for (const [k, n] of m) { const [a, b] = k.split('>'); ctx.beginPath(); path({type: 'LineString', coordinates: [[LU[a].lon, LU[a].lat], [LU[b].lon, LU[b].lat]]}); ctx.strokeStyle = co; ctx.globalAlpha = Math.min(.5, .06 + n / 120); ctx.lineWidth = 1 + Math.sqrt(n) / 3; ctx.stroke(); }
    ctx.globalAlpha = 1;
  }
  if (S.L.mercati) for (const x of act) if (x.m && x.o) { ctx.beginPath(); path({type: 'LineString', coordinates: [[x.o.lon, x.o.lat], [x.m.lon, x.m.lat]]}); ctx.strokeStyle = fe; ctx.setLineDash([4, 3]); ctx.lineWidth = 1.4; ctx.stroke(); ctx.setLineDash([]); }
  if (S.L.origini) for (const g of agg) {
    const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = P('o' + g.f, g.id, c), r = rr(g), co = g.f === 'lacca' ? cl : c0;
    const dim = hi && hi.size && !hi.has(g.id) ? .25 : 1;
    ctx.globalAlpha = dim; ctx.beginPath(); ctx.arc(x, y, r, 0, 7);
    if (g.f === 'lacca') { ctx.fillStyle = co; ctx.globalAlpha = dim * .1; ctx.fill(); ctx.globalAlpha = dim; if (g.l.precisione !== 'citta') ctx.setLineDash([5, 3]); ctx.strokeStyle = co; ctx.lineWidth = 2.4; ctx.stroke(); ctx.setLineDash([]); }
    else if (g.l.precisione === 'citta') { ctx.fillStyle = co; ctx.globalAlpha = dim * (.35 + .6 * g.doc / g.n); ctx.fill(); }
    else { ctx.fillStyle = co; ctx.globalAlpha = dim * .12; ctx.fill(); ctx.globalAlpha = dim; ctx.setLineDash([3, 3]); ctx.strokeStyle = co; ctx.lineWidth = 1.2; ctx.stroke(); ctx.setLineDash([]); }
    if (g.inc) { ctx.beginPath(); ctx.arc(x, y, r + 3, 0, 7); ctx.setLineDash([1, 3]); ctx.strokeStyle = ink; ctx.globalAlpha = dim * .7; ctx.stroke(); ctx.setLineDash([]); }
    if (S.L.silenzio && g.l.precisione !== 'citta') { ctx.beginPath(); ctx.arc(x, y, r + 16, 0, 7); ctx.fillStyle = mute; ctx.globalAlpha = .1; ctx.fill(); }
    if (S.place === g.id) { ctx.beginPath(); ctx.arc(x, y, r + 5, 0, 7); ctx.strokeStyle = fe; ctx.globalAlpha = 1; ctx.lineWidth = 2; ctx.stroke(); }
    ctx.globalAlpha = 1;
    if (r > (W < 520 ? 15 : 9) || (hi && hi.has(g.id))) { ctx.font = '500 12.5px "Instrument Sans",sans-serif'; const w = ctx.measureText(g.l.nome).width, bx = [x + r + 4, y - 8, x + r + 4 + w, y + 6];
      if (S.place === g.id || (hi && hi.has(g.id)) || libero(bx)) { OCC.push(bx); ctx.fillStyle = co; ctx.fillText(g.l.nome, x + r + 4, y + 4); } }
  }
  if (S.L.vam) for (const g of vagg) {
    const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = P('v', g.id, c), r = 3 + Math.sqrt(g.n) * 1.3;
    ctx.beginPath(); ctx.moveTo(x, y - r); ctx.lineTo(x + r, y); ctx.lineTo(x, y + r); ctx.lineTo(x - r, y); ctx.closePath();
    ctx.strokeStyle = fe; ctx.globalAlpha = .75; ctx.lineWidth = 1.1; ctx.stroke(); ctx.globalAlpha = 1;
  }
  if (S.L.letteratura) for (const g of lagg) {
    const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = P('l', g.id, c), r = 7;
    ctx.beginPath(); ctx.moveTo(x, y - r); ctx.lineTo(x + r * .9, y + r * .6); ctx.lineTo(x - r * .9, y + r * .6); ctx.closePath();
    ctx.fillStyle = ink; ctx.globalAlpha = .85; ctx.fill(); ctx.globalAlpha = 1;
    ctx.font = '12px "Instrument Sans",sans-serif'; const bx = [x + 10, y - 8, x + 10 + ctx.measureText(g.l.nome).width, y + 6];
    if (libero(bx)) { OCC.push(bx); ctx.fillStyle = ink; ctx.fillText(g.l.nome, x + 10, y + 4); }
  }
  if (S.L.contesti) drawContesti(ink, mute);
  if (S.L.sedi) for (const k of new Set(act.map(x => x.sede).filter(Boolean))) {
    const l = LU[k]; if (!l || !visibile([l.lon, l.lat])) continue; const [x, y] = P('s', k, [l.lon, l.lat]);
    ctx.fillStyle = ink; ctx.fillRect(x - 4, y - 4, 8, 8);
  }
  const sel = O.find(x => x.id === S.sel);
  if (sel && sel.o && visibile([sel.o.lon, sel.o.lat])) { const [x, y] = proj([sel.o.lon, sel.o.lat]); ctx.beginPath(); ctx.arc(x, y, 11, 0, 7); ctx.strokeStyle = fe; ctx.lineWidth = 2.5; ctx.stroke(); }
  evidenzia(fe);
  prepAloni(css('--alone'), css('--alone')); disegnaAloni(performance.now());
  chip(cf.anno);
}
/* Il segno scelto resta in risalto: doppio anello (chiaro fuori, colore d'accento dentro), leggibile su ogni sfondo. */
function evidenzia(fe) {
  if (!S.place) return;
  const punti = S.place.startsWith('mov:') ? (CX.find(e => e.id === S.place.slice(4))?.luoghi || []).map(l => [l.lon, l.lat, 10, 'm', S.place.slice(4) + '|' + l.id])
    : (() => { const id = S.place.replace(/^sito:/, ''), l = LU[id], g = agg.find(g => g.id === id); return l ? [[l.lon, l.lat, g ? rr(g) + 6 : 12]] : []; })();
  for (const [lon, lat, r, k, id] of punti) {
    if (!visibile([lon, lat])) continue; const [x, y] = k ? P(k, id, [lon, lat]) : proj([lon, lat]);
    ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.strokeStyle = css('--bg'); ctx.lineWidth = 6; ctx.stroke();
    ctx.beginPath(); ctx.arc(x, y, r, 0, 7); ctx.strokeStyle = fe; ctx.lineWidth = 2.5; ctx.stroke();
  }
}

/* Stili e movimenti: quadrati vuoti (luogo), quadrati tratteggiati più grandi (paese), solo nome in corsivo (regione).
   Nomi scritti per i più noti (versioni linguistiche su Wikidata), senza sovrapporsi. */
function drawContesti(ink, mute) {
  const cel = css('--cel');  // il contesto ha il suo colore: verde celadon, distinto dal cobalto delle opere
  const occ = OCC, sel = S.place && S.place.startsWith('mov:') ? S.place.slice(4) : null;
  // relazioni dichiarate: fra voci attive se il livello è acceso; quelle della voce scelta sempre, anche fuori finestra
  const att = new Map(cagg.map(e => [e.id, e])), tutte = new Map(CX.map(e => [e.id, e]));
  const linea = (a, b, forte) => { const p = a.luoghi[0], q = b.luoghi[0]; if (p.id === q.id) return; ctx.beginPath(); path({type: 'LineString', coordinates: [[p.lon, p.lat], [q.lon, q.lat]]});
    ctx.strokeStyle = cel; ctx.globalAlpha = forte ? .85 : .35; ctx.lineWidth = forte ? 1.6 : .9; ctx.setLineDash([1, 3]); ctx.stroke(); ctx.setLineDash([]); ctx.globalAlpha = 1; };
  if (S.L.relazioni) for (const e of cagg) for (const r of e.relazioni) if (r.verso === '>' && att.has(r.id)) linea(e, att.get(r.id), false);
  if (sel && tutte.has(sel)) for (const r of tutte.get(sel).relazioni) if (r.collocata && tutte.has(r.id)) linea(tutte.get(sel), tutte.get(r.id), true);
  ctx.font = 'italic 500 13px Newsreader,Georgia,serif'; let cnomi = 0;
  for (const e of cagg) for (const l of e.luoghi) {
    const c = [l.lon, l.lat]; if (!visibile(c)) continue; const [x, y] = P('m', e.id + '|' + l.id, c), r = l.precisione === 'paese' ? 7 : 4.5;
    ctx.strokeStyle = cel; ctx.lineWidth = e.id === sel ? 2.2 : 1; ctx.globalAlpha = e.id === sel ? 1 : .7;
    if (l.precisione !== 'regione') { if (l.precisione === 'paese') ctx.setLineDash([2, 2]); ctx.strokeRect(x - r, y - r, 2 * r, 2 * r); ctx.setLineDash([]); }
    const t = e.nome, w = ctx.measureText(t).width, bx = [x + r + 3, y - 9, x + r + 3 + w, y + 4];
    if (e.id === sel || (cnomi < (S.k >= VENTAGLIO ? 80 : W < 520 ? 6 : 18) && libero(bx) && ++cnomi)) {
      occ.push(bx); ctx.fillStyle = cel; ctx.globalAlpha = e.id === sel ? 1 : .8; ctx.fillText(t, bx[0], y + 3); }
    ctx.globalAlpha = 1;
  }
}
function chip(anno) {
  if (!O.length) { $('#chip').textContent = 'Carico opere, luoghi e confini…'; return; }
  const n = act.length, paese = act.filter(x => x.o && x.o.precisione !== 'citta').length, ipo = act.filter(x => x.grado === 'ipotetico').length;
  let h = S.L.opere ? `<b>${n}</b> pezzi attivi · confini del ${fmtY(anno)}` : `filo spento · confini del ${fmtY(anno)}`;
  if (S.L.silenzio && n) { const us = act.filter(x => x.fonte === 'met' || x.fonte === 'cma').length, sedi = new Set(act.map(x => x.sede).filter(Boolean)).size, pu = 100 * us / n;
    if (VAM && S.L.vam && S.L.opere) { const tv = vagg.reduce((a, g) => a + g.n, 0), cv = vagg.filter(g => g.l.precisione === 'citta').reduce((a, g) => a + g.n, 0); h += `<br>V&A (rombi, tutti conservati a Londra): ~${Math.round(tv)} pezzi, ${tv ? Math.round(100 * cv / tv) : 0}% localizzati per città`; }
    h += `<br>${Math.round(100 * paese / n)}% localizzati solo per paese · ${ipo} ipotetici · ${act.filter(x => !x.o).length} senza luogo<br>${sedi} sedi di conservazione · ${pu > 99 && pu < 100 ? pu.toFixed(1) : Math.round(pu)}% delle schede negli Stati Uniti<br>${NOD.filter(x => S.F[x.fonte]).length} pezzi senza data: esistono nei dati, non nel tempo`; }
  if (S.L.contesti) h += `<br>${cagg.length} fenomeni artistici in questa finestra (quadrati e nomi in corsivo)`;
  $('#chip').innerHTML = h;
}

function hit(px, py) {
  let best = null, bd = 1e9;
  for (const g of agg) { const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = P('o' + g.f, g.id, c), d = Math.hypot(x - px, y - py); if (d < rr(g) + 5 && d < bd) { bd = d; best = g; } }
  if (!best && S.L.letteratura) for (const g of lagg) { const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = P('l', g.id, c), d = Math.hypot(x - px, y - py); if (d < 11 && d < bd) { bd = d; best = {...g, let: true}; } }
  if (!best && S.L.vam) for (const g of vagg) { const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = P('v', g.id, c), d = Math.hypot(x - px, y - py); if (d < 3 + Math.sqrt(g.n) * 1.3 + 4 && d < bd) { bd = d; best = {...g, vam: true}; } }
  if (!best && S.L.contesti) for (const e of cagg) for (const l of e.luoghi) { const c = [l.lon, l.lat]; if (!visibile(c)) continue; const [x, y] = P('m', e.id + '|' + l.id, c), d = Math.hypot(x - px, y - py); if (d < 10 && d < bd) { bd = d; best = {id: 'mov:' + e.id, e, l, mov: true}; } }
  return best;
}

let drag = null;
cv.addEventListener('pointerdown', e => { drag = {x: e.clientX, y: e.clientY, r: [...S.rot], moved: 0}; cv.setPointerCapture(e.pointerId); cv.style.cursor = 'grabbing'; });
cv.addEventListener('pointermove', e => {
  const b = cv.getBoundingClientRect();
  if (drag) { const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag.moved = Math.max(drag.moved, Math.abs(dx) + Math.abs(dy));
    const f = 0.25 / S.k; S.rot = [drag.r[0] + dx * f, Math.max(-90, Math.min(90, drag.r[1] - dy * f))]; draw(); return; }
  const g = hit(e.clientX - b.left, e.clientY - b.top), tip = $('#tip');
  cv.style.cursor = g ? 'pointer' : 'grab';  // la mano diventa un dito sopra ciò che si può cliccare
  let pol = '';
  if (!g && S.L.confini) { const c = proj.invert([e.clientX - b.left, e.clientY - b.top]), cf = confini(S.year); if (c && cf.geo) { const f = cf.geo.features.find(f => f.properties.NAME && d3.geoContains(f, c)); if (f) pol = f.properties.NAME; } }
  if (g || pol) { tip.style.display = 'block'; tip.style.left = (e.clientX - b.left + 14) + 'px'; tip.style.top = (e.clientY - b.top + 10) + 'px';
    tip.innerHTML = g && g.mov ? `<b>${esc(g.e.nome)}</b> · ${g.e.tipo}${g.e.sottotipo ? ' (' + g.e.sottotipo + ')' : ''}<br><span class="sub">${fmtY(g.e.quando.da)}–${g.e.quando.a != null ? fmtY(g.e.quando.a) : 'fine non dichiarata'} · ${esc(g.l.oggi)}</span>` : g && g.let ? `<b>${esc(g.l.nome)}</b> · ${g.n} dati dalla letteratura<br><span class="sub">sito archeologico: consumo, non produzione</span>` : g && g.vam ? `<b>${esc(g.l.nome)}</b> · V&A ~${Math.round(g.n)} pezzi<br><span class="sub">solo conteggio aggregato</span>` : g ? `<b>${esc(g.l.nome)}</b> · ${g.n} pezzi<br><span class="sub">${PREC[g.l.precisione]}${g.inc ? ' · ' + g.inc + ' attribuzioni incerte' : ''}${g.ded ? ' · ' + g.ded + ' con luogo dedotto' : ''}</span>` : `${esc(pol)}<br><span class="sub">confini del ${fmtY(confini(S.year).anno)}</span>`; }
  else tip.style.display = 'none';
});
cv.addEventListener('pointerup', e => {
  if (drag && drag.moved < 4) { const b = cv.getBoundingClientRect(), g = hit(e.clientX - b.left, e.clientY - b.top); S.place = g ? g.id : null; S.intorno = null; S.sel = null; if (S.mode === 'ricerca') renderCtx(); draw(); }
  drag = null; cv.style.cursor = 'grab';
});
cv.addEventListener('pointerleave', () => { $('#tip').style.display = 'none'; });
// la rotella ingrandisce verso il punto sotto il cursore: il globo si sposta un po' verso di lui a ogni scatto
cv.addEventListener('wheel', e => { e.preventDefault(); const b = cv.getBoundingClientRect(), f = e.deltaY < 0 ? 1.15 : 1 / 1.15;
  const c = f > 1 && proj.invert ? proj.invert([e.clientX - b.left, e.clientY - b.top]) : null;
  if (c && Number.isFinite(c[0]) && S.k < ZMAX) { const t = 1 - 1 / f; S.rot = [S.rot[0] + t * angolo(-c[0] - S.rot[0]), S.rot[1] + t * (-c[1] - S.rot[1])]; }
  zoom(f); }, {passive: false});
const angolo = d => ((d + 540) % 360) - 180;  // la via più corta attorno al globo
const ZMAX = 200;
const zoom = f => { S.k = Math.max(.7, Math.min(ZMAX, S.k * f)); draw(); };
$('#zin').onclick = () => zoom(1.3); $('#zout').onclick = () => zoom(1 / 1.3);
const misura = () => { const d = devicePixelRatio || 1; W = fig.clientWidth; H = fig.clientHeight; for (const [c, x] of [[cv, ctx], [av, actx]]) { c.width = W * d; c.height = H * d; x.setTransform(d, 0, 0, d, 0, 0); } draw(); };
const roMap = new ResizeObserver(misura);
/* la prima schermata misura intestazione e tempo, così il globo prende tutto il resto */
const roAlti = new ResizeObserver(() => { const r = document.documentElement.style; r.setProperty('--hh', $('header').offsetHeight + 'px'); r.setProperty('--th', $('#tl').offsetHeight + 'px'); });
roAlti.observe($('header')); roAlti.observe($('#tl'));
roMap.observe(fig);

/* ---------- tempo ---------- */
const tls = $('#tls');
const dec = () => { const c = new Map(); for (const x of O) { if (!passa(x)) continue;
  for (let d = Math.max(T0, Math.floor(x.inizio / 10) * 10); d <= Math.min(T1, x.fine); d += 10) { const v = c.get(d) || [0, 0]; v[CONFRONTO ? +(x.fl === 'lacca') : x.grado === 'documentato' ? 0 : 1] += 1 / (1 + (x.fine - x.inizio) / 10); c.set(d, v); } } return c; };
/* Barra del tempo: solo il filo (istogramma dei pezzi per decennio). I periodi stanno in una sezione propria,
   sotto (drawPeriodi), accesa dallo strato «Periodi» dello sfondo comune. */
const asseX = w => d3.scaleLinear([T0, T1], [0, w]);
const tacche = (x, w, y) => { let s = ''; for (let t = Math.ceil((T0 + 1) / PASSO) * PASSO; t < T1; t += w < 520 ? 4 * PASSO : PASSO) s += `<text x="${x(t)}" y="${y}" font-size="10.5" fill="var(--mute)" text-anchor="middle">${fmtY(t)}</text>`; return s; };
function drawTl() {
  const w = tls.clientWidth, h = 62, x = asseX(w), c = dec(), mx = Math.max(...[...c.values()].map(v => v[0] + v[1]), 1), y = v => 40 * v / mx;
  tls.style.height = h + 'px';
  let s = `<rect x="${x(S.year - S.win)}" y="0" width="${x(S.year + S.win) - x(S.year - S.win)}" height="${h - 16}" fill="var(--fe)" opacity=".08"/>`;
  for (const [d, [a, b]] of c) s += `<rect x="${x(d)}" y="${42 - y(a + b)}" width="${Math.max(1, x(d + 10) - x(d) - 1)}" height="${y(b)}" fill="var(${CONFRONTO ? '--lacca' : '--co'})" opacity="${CONFRONTO ? .8 : .35}"/><rect x="${x(d)}" y="${42 - y(a)}" width="${Math.max(1, x(d + 10) - x(d) - 1)}" height="${y(a)}" fill="var(--co)"/>`;
  if (VAM && S.L.vam && S.L.opere) { const vd = new Map(); for (const k of VAM.celle) vd.set(k.d, (vd.get(k.d) || 0) + k.n); const vmx = Math.max(...vd.values(), 1);
    s += `<polyline fill="none" stroke="var(--fe)" stroke-width="1.4" points="${[...vd].filter(([d]) => d >= T0).sort((a, b) => a[0] - b[0]).map(([d, n]) => `${x(d + 5)},${42 - 40 * n / vmx}`).join(' ')}"/>`; }
  s += tacche(x, w, h - 3) + `<line x1="${x(S.year)}" x2="${x(S.year)}" y1="0" y2="${h - 14}" stroke="var(--fe)" stroke-width="2"/>`;
  tls.innerHTML = s; $('#yr').textContent = fmtY(S.year);
  tls.setAttribute('aria-valuemin', T0); tls.setAttribute('aria-valuemax', T1); tls.setAttribute('aria-valuenow', S.year);
  tls.setAttribute('aria-valuetext', `${fmtY(S.year)}, finestra più o meno ${S.win} anni`);
  const fuori = O.filter(o => o.fine < T0).length;
  $('#tlinfo').textContent = CONFRONTO ? `istogramma: pezzi per decennio, blu e bianco sotto e lacca sopra${fuori ? ` · ${fuori} pezzi prima del ${fmtY(T0)} fuori scala` : ''}`
    : `istogramma: pezzi per decennio (scuro documentati, chiaro ipotetici)${VAM && S.L.vam && S.L.opere ? '; linea rossa: V&A, scala propria' : ''}${fuori ? ` · ${fuori} pezzi prima del ${fmtY(T0)} fuori scala` : ''}`;
  drawPeriodi();
}
/* Periodi: una riga per area, sempre con il nome. Tre fonti a scelta; ogni riga si legge passandoci sopra. */
const tlc = $('#tlc');
let RIGHE_P = [];
function fontePeriodi() {
  if (S.corsie === 'periodo' && PO) return {tipo: 'densita', reg: REG_PO, periodi: PO.periodi.map(p => ({r: p.r, a: p.a, b: p.b, n: p.n})),
    titolo: 'Quanto è nominato il tempo', fonte: 'PeriodO', leg: 'Ogni riga è più scura dove più periodizzazioni pubblicate (da studiosi, musei, archivi) coprono quell\'anno; il numero: quante valgono per l\'anno scelto. Misura l\'attenzione degli studi, non la storia.'};
  if (S.corsie === 'contesti' && CX.length) { const c = corsieCX(); return {tipo: 'densita', reg: c.reg, periodi: CX.filter(e => S.CT.has(e.tipo)).map(e => ({r: e.corsia, a: e.quando.da, b: e.fv, n: e.nome})),
    titolo: 'Fenomeni artistici attivi', fonte: 'Wikidata', leg: `Ogni riga è più scura dove più contesti (${[...S.CT].map(t => TIPO_PL[t] || t).join(', ')}) sono attivi; il numero: quanti nell'anno scelto. Fine non dichiarata: ${APERTO} anni.`}; }
  return {tipo: 'barre', reg: [...new Set(PER.map(p => p.regione))], periodi: PER.map(p => ({r: p.regione, a: p.inizio, b: p.fine, n: p.nome, qid: p.qid})),
    titolo: 'Dinastie e periodi storici', fonte: 'Wikidata', leg: 'Le dinastie e i periodi storici di ogni area, con le date dichiarate su Wikidata; dove si sovrappongono vanno su più righe.'};
}
function drawPeriodi() {
  const sez = $('#periodi'); sez.hidden = !S.L.periodi; if (!S.L.periodi) return;
  const F = fontePeriodi(), w = tlc.clientWidth, x = asseX(w), gut = w > 520 ? 170 : 0, lh = 14, gap = 3, top = 4;
  RIGHE_P = [];
  if (F.tipo === 'barre') { for (const r of F.reg) { const sub = []; for (const p of F.periodi.filter(p => p.r === r).sort((a, b) => a.a - b.a)) { let k = sub.findIndex(f => f <= p.a); if (k < 0) { k = sub.length; sub.push(0); } sub[k] = p.b; (RIGHE_P[`${r}|${k}`] ||= {r, k, ps: []}).ps.push(p); } } RIGHE_P = Object.values(RIGHE_P); }
  else RIGHE_P = F.reg.map(r => ({r, k: 0, ps: F.periodi.filter(p => p.r === r)}));
  const h = top + RIGHE_P.length * (lh + gap) + 20;
  tlc.style.height = h + 'px';
  let s = `<rect x="${x(S.year - S.win)}" y="0" width="${x(S.year + S.win) - x(S.year - S.win)}" height="${h - 16}" fill="var(--fe)" opacity=".06"/>`;
  RIGHE_P.forEach(({r, k, ps}, i) => { const yy = top + i * (lh + gap), qui = ps.filter(p => p.a <= S.year && p.b >= S.year);
    s += `<rect x="0" y="${yy}" width="${w}" height="${lh}" fill="var(--riga)" opacity=".35"/>`;
    for (const p of ps) { const a = Math.max(x(Math.max(p.a, T0)), gut), b = x(Math.min(p.b, T1)); if (b <= a) continue;
      if (F.tipo === 'barre') { s += `<rect x="${a}" y="${yy}" width="${b - a}" height="${lh}" rx="2" fill="var(--co)" opacity=".18" stroke="var(--co)" stroke-opacity=".45"/>`;
        if (b - a > p.n.length * 5.6) s += `<text x="${a + 4}" y="${yy + 10.5}" font-size="10" fill="var(--ink)" pointer-events="none">${esc(p.n)}</text>`; }
      else s += `<rect x="${a}" y="${yy}" width="${b - a}" height="${lh}" fill="var(--co)" opacity=".07"/>`; }
    if (gut && k === 0) s += `<text x="2" y="${yy + 11}" font-size="11" fill="var(--ink)">${esc(r)}${F.tipo === 'densita' ? ` <tspan fill="var(--mute)">${qui.length}</tspan>` : ''}</text>`; });
  s += tacche(x, w, h - 3) + `<line x1="${x(S.year)}" x2="${x(S.year)}" y1="0" y2="${h - 14}" stroke="var(--fe)" stroke-width="2"/>`;
  tlc.innerHTML = s;
  $('#per-titolo').textContent = F.titolo; $('#per-fonte').textContent = 'fonte: ' + F.fonte; $('#per-leg').textContent = F.leg;
}
/* passando sopra una riga: l'area e che cosa c'è in quell'anno */
tlc.addEventListener('pointermove', e => { const b = tlc.getBoundingClientRect(), i = Math.floor((e.clientY - b.top - 4) / 17), R = RIGHE_P[i], tip = $('#tlctip');
  if (!R) { tip.hidden = true; return; } const yr = Math.round(T0 + (T1 - T0) * (e.clientX - b.left) / b.width), qui = R.ps.filter(p => p.a <= yr && p.b >= yr);
  tip.innerHTML = `<b>${esc(R.r)}</b> · ${fmtY(yr)}<br>${qui.length ? qui.slice(0, 5).map(p => esc(p.n)).join(' · ') + (qui.length > 5 ? ` e altri ${qui.length - 5}` : '') : '<span class="sub">niente in quest\'anno</span>'}`;
  tip.hidden = false; tip.style.left = Math.min(e.clientX - b.left + 12, b.width - 260) + 'px'; tip.style.top = (e.clientY - b.top + 14) + 'px'; });
tlc.addEventListener('pointerleave', () => { $('#tlctip').hidden = true; });
tlc.addEventListener('click', e => { const b = tlc.getBoundingClientRect(); setYear(T0 + (T1 - T0) * (e.clientX - b.left) / b.width); });
const REG_PO = ['Cina', 'Corea', 'Giappone', 'Sud-est asiatico', 'Iran e Asia centrale', 'Asia meridionale', 'Anatolia e Mediterraneo', 'Africa', 'Europa', 'Americhe'];
const LINGUE = {en: 'inglese', fr: 'francese', nl: 'olandese', ja: 'giapponese', tr: 'turco', de: 'tedesco', it: 'italiano', zh: 'cinese', es: 'spagnolo'};
// Corsie di densità: per ogni regione, quanti elementi coprono ogni anno (PeriodO, oppure stili e movimenti).
const ORD_CX = ['Asia orientale', 'Sud-Est asiatico', 'Asia meridionale', 'Asia centrale', 'Medio Oriente e Nord Africa', 'Africa subsahariana', 'Europa', 'Nord America', 'Mesoamerica e Caraibi', 'Sud America', 'Oceania'];
const regCX = () => [...ORD_CX, ...[...new Set(CX.map(e => e.corsia))].filter(r => !ORD_CX.includes(r)).sort()].filter(r => CX.some(e => e.corsia === r && S.CT.has(e.tipo)));
const corsieCX = () => ({reg: regCX(), periodi: CX.filter(e => S.CT.has(e.tipo)).map(e => ({r: e.corsia, a: e.quando.da, b: e.fv})), vuoto: '',
  info: `corsie: quanti fenomeni (${[...S.CT].join(', ')}; Wikidata) sono attivi in ogni anno, per macro-regione del luogo d'origine; il numero: quanti nell'anno scelto. Fine non dichiarata: ${APERTO} anni`});
function nominato() {  // nel pannello: solo un rimando alla sezione sotto
  if (!PO) return '';
  const n = PO.periodi.filter(p => p.a <= S.year && p.b >= S.year).length;
  return `<a class="giu" href="#nominato" data-scorri="nominato">${articolo(S.year)}${fmtY(S.year)}, nominato da chi: ${n} definizioni ↓</a>`;
}
let NOM_ANNO = null;
function sezNominato() {
  const el = $('#nominato'); if (!PO) { el.hidden = true; return; } if (NOM_ANNO === S.year) return; NOM_ANNO = S.year;
  const g = REG_PO.map(r => [r, PO.periodi.filter(p => p.r === r && p.a <= S.year && p.b >= S.year)]);
  el.innerHTML = `<div class="sezh"><h3 id="nom-t">${articolo(S.year)}${fmtY(S.year)}, nominato da chi</h3><button class="nasc" data-nascondi="nom" aria-label="Nascondi questa sezione">Nascondi</button></div>
  <p class="sub" style="max-width:80ch">I periodi di PeriodO che contengono l'anno scelto, per area: chi li ha definiti, in che lingua, con quali date. Più definizioni non vuol dire più storia, ma più studi. Una riga per fonte, prima le lingue diverse dall'inglese.</p>
  <div class="colonne">${g.map(([r, ps]) => { if (!ps.length) return `<div><h4>${esc(r)}</h4><p class="sub">Nessuna definizione in PeriodO per quest'anno: un silenzio delle fonti.</p></div>`;
    const lg = [...new Set(ps.map(p => LINGUE[p.lg] || p.lg))].join(', '), una = [...new Map(ps.map(p => [p.au, p])).values()].sort((p, q) => (p.lg === 'en') - (q.lg === 'en'));
    return `<div><h4>${esc(r)} <span class="sub" style="font:400 12px 'Instrument Sans',sans-serif">${ps.length} definizioni da ${una.length} fonti · ${esc(lg)}</span></h4>` + una.map(p => { const a = PO.autorita[p.au] || {};
      return `<p class="def">${esc(p.n)} <span class="sub">${fmtY(p.a)}–${fmtY(p.b)} · ${esc((a.chi ? a.chi + ', ' : '') + (a.titolo || ''))}${a.anno ? ' (' + a.anno + ')' : ''}</span></p>`; }).reduce((h, d, i, t) => h + (i === 6 && t.length > 7 ? `<details><summary class="sub">le altre ${t.length - 6} fonti</summary>` : '') + d + (i === t.length - 1 && t.length > 7 ? '</details>' : ''), '') + '</div>'; }).join('')}</div>`;
}
/* Come leggere: per esteso, una volta per filo */
function sezLeggi() {
  const sv = d => `<svg width="22" height="16" viewBox="0 0 22 16" aria-hidden="true">${d}</svg>`;
  const segni = [
    ...(CONFRONTO ? [[sv('<circle cx="11" cy="8" r="6" fill="var(--co)" opacity=".75"/>'), 'porcellana blu e bianca: luogo d\'origine'], [sv('<circle cx="11" cy="8" r="5.5" fill="none" stroke="var(--lacca)" stroke-width="2.4"/>'), 'lacca: luogo d\'origine']]
      : [[sv('<circle cx="11" cy="8" r="6" fill="var(--co)" opacity=".75"/>'), 'luogo d\'origine, una città: più pieno, più pezzi documentati']]),
    [sv('<circle cx="11" cy="8" r="6" fill="var(--co)" fill-opacity=".12" stroke="var(--co)" stroke-dasharray="3 3"/>'), 'luogo noto solo come paese o regione: il catalogo non dice di più'],
    [sv('<circle cx="11" cy="8" r="7" fill="none" stroke="var(--ink)" stroke-dasharray="1 3"/>'), 'attribuzione incerta, secondo il catalogo'],
    [sv('<circle cx="11" cy="8" r="7.5" fill="var(--alone)" opacity=".35"/>'), 'alone: quanto è grande il paese o la regione (le città non ne hanno)'],
    [sv('<rect x="7" y="4" width="8" height="8" fill="var(--ink)"/>'), 'dove i pezzi si trovano oggi'],
    [sv('<path d="M2 12 Q11 0 20 12" fill="none" stroke="var(--co)" stroke-width="1.6" opacity=".6"/>'), 'spostamento: dall\'origine al museo di oggi'],
    [sv('<path d="M2 8 H20" stroke="var(--fe)" stroke-width="1.4" stroke-dasharray="4 3"/>'), 'mercato di destinazione, solo dove il catalogo lo scrive'],
    ...(PRIMO ? [[sv('<path d="M11 2 L17 8 L11 14 L5 8 Z" fill="none" stroke="var(--fe)"/>'), 'V&A: solo conteggi per luogo e decennio'], [sv('<path d="M11 2 L17 13 L5 13 Z" fill="none" stroke="var(--ink)"/>'), 'consumo documentato negli scavi, con autore e pagina']] : []),
    [sv('<rect x="6" y="3" width="10" height="10" fill="none" stroke="var(--cel)" stroke-width="1.4"/>'), 'contesto (stile, movimento, scuola, dinastia): dove nasce'],
    [sv('<path d="M2 8 H20" stroke="var(--cel)" stroke-width="1.6" stroke-dasharray="1 3"/>'), 'relazione fra contesti, solo se Wikidata la dichiara'],
    [sv('<circle cx="11" cy="8" r="6" fill="none" stroke="var(--fe)" stroke-width="2"/>'), 'il luogo o il pezzo selezionato']];
  $('#leggi').innerHTML = `<div class="sezh"><h3 id="leggi-t">Come leggere l'atlante</h3><button class="nasc" data-nascondi="leg" aria-label="Nascondi questa sezione">Nascondi</button></div>
  <p class="sub">Tutto quello che compare ha una fonte; dove la fonte tace, l'atlante lo dice invece di riempire il vuoto.</p>
  <div class="colonne">
   <div><h4>I segni sulla mappa</h4>${segni.map(([g, t]) => `<div class="lv">${g}<span>${t}</span></div>`).join('')}</div>
   <div><h4>Quanto è sicuro un dato</h4>
    <p><b>Documentato</b>: il catalogo del museo dice esplicitamente ciò che fa entrare il pezzo nel filo (il blu, la lacca).</p>
    ${PRIMO ? '<p><b>Ipotetico</b>: la manifattura è nota per il blu e bianco, ma la scheda non nomina il colore. Si spegne con «Anche gli ipotetici».</p><p><b>Luogo dedotto</b>: per una parte delle schede del Museo nazionale di Tokyo il luogo è ricavato dalla categoria; è uno strato a parte, spento all\'inizio.</p>' : ''}
    <p><b>Chi dice ogni dato</b>: nella scheda di un pezzo un\'etichetta accanto a ogni campo distingue il catalogo del museo, una nostra lettura (con la regola) e Wikidata.</p></div>
   <div><h4>Accostare non è collegare</h4>
    <p>Due cose nello stesso luogo e nello stesso tempo sono accostate, non legate. I legami compaiono solo dove una fonte li dichiara: i mercati scritti nel catalogo, le relazioni fra contesti su Wikidata.</p>
    <p>«Cerca intorno» e il confronto fra fili sono strade per esplorare: ogni elenco dice con quale regola è stato fatto.</p></div>
   <div><h4>Che cosa manca</h4>
    <p>I numeri riflettono anche quanto ogni paese apre i suoi dati: la riga in fondo dice quali fonti mancano e quante schede sono state escluse, e perché.</p>
    <p>Lo strato «Silenzio delle fonti» mostra dove il dato è vago. Le date senza anni (solo un'epoca) usano gli anni convenzionali, e la scheda lo segnala.</p>
    <p><a href="fonti.html">Fonti e licenze</a> · <a href="relazioni.html">Le relazioni come grafo</a></p></div>
  </div>`;
}
const setYear = v => { S.year = Math.round(Math.max(T0, Math.min(T1, v))); update(); };
let tdrag = false;
const tx = e => { const b = tls.getBoundingClientRect(); return T0 + (T1 - T0) * (e.clientX - b.left) / b.width; };
tls.addEventListener('pointerdown', e => { e.preventDefault(); tdrag = true;  // niente selezione di testo trascinando sul tempo
  tls.setPointerCapture(e.pointerId); setYear(tx(e)); });
tls.addEventListener('pointermove', e => { if (tdrag) setYear(tx(e)); });
tls.addEventListener('pointerup', () => { tdrag = false; });
tls.addEventListener('keydown', e => { if (e.key === 'ArrowLeft') setYear(S.year - 5); if (e.key === 'ArrowRight') setYear(S.year + 5); });
new ResizeObserver(() => drawTl()).observe(tls);
$('#win').onchange = e => { S.win = +e.target.value; update(); };
/* scelte rapide della finestra; «tutto» apre la finestra sull'intero arco del filo */
document.querySelectorAll('[data-win]').forEach(b => b.onclick = () => {
  if (b.dataset.win === 'tutto') { S.win = Math.ceil((T1 - T0) / 2); S.year = Math.round((T0 + T1) / 2); } else S.win = +b.dataset.win;
  update(); });
/* salti per regione: girano il globo e ingrandiscono, senza filtrare */
const CENTRI_REG = {'Europa': [12, 48, 2.2], 'Medio Oriente e Nord Africa': [35, 28, 2], 'Asia centrale': [65, 42, 2.2], 'Asia meridionale': [79, 21, 2.2],
  'Asia orientale': [118, 34, 2], 'Sud-Est asiatico': [110, 8, 2], 'Africa subsahariana': [20, -3, 1.6], 'Nord America': [-98, 42, 1.7],
  'Mesoamerica e Caraibi': [-88, 17, 2.4], 'Sud America': [-60, -18, 1.6], 'Oceania': [140, -22, 1.7]};
$('#vaia').innerHTML = '<option value="">Vai a…</option><option value="mondo">tutto il mondo</option>' + Object.keys(CENTRI_REG).map(r => `<option>${r}</option>`).join('');
$('#vaia').onchange = e => { const r = e.target.value; e.target.value = ''; if (!r) return;
  if (r === 'mondo') { S.k = 1; } else { const [lon, lat, k] = CENTRI_REG[r]; S.rot = [-lon, -lat]; S.k = k; }
  draw(); };
/* pannelli richiudibili, ricordati da una visita all'altra */
const PANN = (() => { try { return JSON.parse(localStorage.getItem('armoni-pannelli') || '{}'); } catch (e) { return {}; } })();
function pannelli() {
  for (const [k, id, nome] of [['lay', '#chiudi-lay', 'sinistra'], ['ctx', '#chiudi-ctx', 'destra']]) {
    document.body.classList.toggle('senza-' + k, !!PANN[k]); const b = $(id);
    b.setAttribute('aria-pressed', !!PANN[k]); b.setAttribute('aria-label', (PANN[k] ? 'Mostra' : 'Nascondi') + ' il pannello di ' + nome);
    b.textContent = (k === 'lay') === !PANN[k] ? '‹' : '›'; }

  for (const [k] of RIQUADRI) if (k !== 'lay' && k !== 'ctx' && k !== 'per') document.body.classList.toggle('senza-' + k, !!PANN[k]);
  document.querySelectorAll('[data-riq]').forEach(i => { i.checked = i.dataset.riq === 'per' ? !!S.L.periodi : !PANN[i.dataset.riq]; });
  try { localStorage.setItem('armoni-pannelli', JSON.stringify(PANN)); } catch (e) { }
  requestAnimationFrame(() => draw());
}
/* Riquadri: ogni parte dell'interfaccia si mostra o si nasconde, e l'atlante se lo ricorda. PANN[k] vero = nascosto. */
const RIQUADRI = [['lay', 'Strumenti e livelli', 'il pannello di sinistra'], ['ctx', 'Risultati e schede', 'il pannello di destra'],
  ['tl', 'Barra del tempo', 'anno, finestra, istogramma'], ['ov', 'Legenda e «Vai a…»', 'sopra la mappa'], ['chip', 'Riepilogo sulla mappa', 'pezzi attivi e confini'],
  ['per', 'Periodi', 'sotto il tempo'], ['tav', 'Tavolo', 'sotto la mappa'], ['nom', 'L\'anno, nominato da chi', 'definizioni PeriodO'],
  ['leg', 'Come leggere l\'atlante', 'segni e gradi del dato'], ['cop', 'Copertura dei dati', 'la riga in fondo']];
$('#riqlista').innerHTML = RIQUADRI.map(([k, t, d]) => `<label class="chk"><input type="checkbox" data-riq="${k}"><span>${t}<small>${d}</small></span></label>`).join('');
$('#riqlista').addEventListener('change', e => { const k = e.target.dataset.riq; if (!k) return;
  if (k === 'per') { S.L.periodi = e.target.checked ? 1 : 0; syncChecks(); update(); } else PANN[k] = !e.target.checked; pannelli(); });
document.addEventListener('click', e => { const d = $('details.riq'); if (d.open && !e.target.closest('details.riq')) d.open = false; });
$('#riq-tutto').onclick = () => { for (const [k] of RIQUADRI) if (k !== 'per') PANN[k] = false; pannelli(); };
$('#riq-globo').onclick = () => { for (const [k] of RIQUADRI) if (k !== 'per') PANN[k] = true; PANN.tl = false; S.L.periodi = 0; syncChecks(); update(); pannelli(); };
document.addEventListener('click', e => { const n = e.target.closest('[data-nascondi]'); if (!n) return; const k = n.dataset.nascondi;
  if (k === 'per') { S.L.periodi = 0; syncChecks(); update(); } else PANN[k] = true; pannelli(); });
for (const [id, k] of [['#chiudi-lay', 'lay'], ['#chiudi-ctx', 'ctx']]) $(id).onclick = () => { PANN[k] = !PANN[k]; pannelli(); };
$('#tlinfobtn').onclick = () => { const i = $('#tlinfo'), o = i.hidden; i.hidden = !o; $('#tlinfobtn').setAttribute('aria-expanded', o); };
let timer = null;
$('#play').onclick = () => { const b = $('#play'); if (timer) { clearInterval(timer); timer = null; b.setAttribute('aria-pressed', 'false'); b.textContent = '▶ Scorri'; return; }
  b.setAttribute('aria-pressed', 'true'); b.textContent = '❚❚ Ferma'; timer = setInterval(() => setYear(S.year >= T1 ? T0 : S.year + 5), 140); };

/* ---------- contesto ---------- */
/* Scheda: accanto a ogni dato, chi lo dice. «catalogo» = il museo che conserva il pezzo, parola per parola;
   «ArMoni» = una nostra lettura del catalogo, con la regola; «Wikidata» = le coordinate e l'identità del luogo. */
const FONTE_LUNGA = {met: 'Met', cma: 'Cleveland', aic: 'Chicago', colbase: 'ColBase', wd: 'Wikidata', emuseum: 'eMuseum'};
const src = (t, tit = '') => `<span class="src${t === 'ArMoni' ? ' nostra' : ''}"${tit ? ` title="${esc(tit)}"` : ''}>${esc(t)}</span>`;
function scheda(x) {
  const o = x.o, inT = S.tav.some(c => c.id === x.id), cat = FONTE_LUNGA[x.fonte] || x.fonte;
  // l'intervallo è nostro quando la scheda dà solo un'epoca o un secolo (ColBase, eMuseum); è del catalogo quando dà gli anni
  const daEpoca = /\((?:epoca \(Wikidata\)|secolo|secolo ∩ epoca)\)$/.test(x.data_testo || '');
  const uguale = `${fmtY(x.inizio)}–${fmtY(x.fine)}` === (x.data_testo || '').trim();  // se coincide con la data del catalogo, non ripeterlo
  const convenz = daEpoca || /convenzional/.test(x.criterio) || (x.fonte === 'emuseum' && !/dichiarat[oa] nella descrizione/.test(x.criterio));
  return `<h2>${esc(x.titolo)}</h2>
  <div style="margin-top:8px"><span class="tag ${x.grado === 'documentato' ? 'doc' : 'ipo'}">${x.grado}</span>${x.origine_incerta ? '<span class="tag ipo">attribuzione incerta</span>' : ''}${!x.origine && x.origine_dedotta ? `<span class="tag ipo" title="${esc(x.criterio_luogo)}">luogo dedotto</span>` : ''}${x.fl ? `<span class="tag">${NOMI_FILO[x.fl]}</span>` : ''}</div>
  <p class="chi">Chi dice ogni dato: ${src(cat)} il catalogo del museo · ${src('ArMoni')} una nostra lettura, con la regola</p>
  <h3 class="sez">Il pezzo</h3>
  <div class="k">Cultura, come la scrive il catalogo ${src(cat)}</div><div class="v">${esc(x.cultura) || '—'}</div>
  <div class="k">Data ${src(cat)}</div><div class="v">${esc(x.data_testo) || '—'}</div>
  <div class="k"${uguale ? ' hidden' : ''}>Intervallo usato sulla barra del tempo ${convenz ? src('ArMoni', 'anni convenzionali dell\'epoca nominata dalla scheda') : src(cat)}</div><div class="v"${uguale ? ' hidden' : ''}>${fmtY(x.inizio)}–${fmtY(x.fine)}${convenz ? ` <span class="sub">· la scheda nomina solo ${daEpoca ? 'l\'epoca o il secolo: anni da Wikidata o dal secolo' : 'l\'epoca: anni convenzionali dei manuali'}</span>` : ''}</div>
  ${(x.periodi || []).length ? `<div class="k">Periodo, come lo scrive il catalogo ${src(cat)} ${src('ArMoni', 'riconosciuto fra le etichette di Wikidata in 17 lingue, compatibile con le date del pezzo')}</div><div class="v">${x.periodi.map(q => `${esc(PB[q]?.n || q)} <span class="sub">· ${PB[q] ? fmtY(PB[q].a) + '–' + fmtY(PB[q].b) + ' · ' : ''}<a href="https://www.wikidata.org/wiki/${q}">${q}</a>${CX.some(e => e.id === q) ? ` · <a href="#" data-place="mov:${q}">il contesto</a>` : ''}</span>`).join('<br>')}</div>` : ''}
  <div class="k">Tecnica ${src(cat)}</div><div class="v">${esc(x.tecnica) || '—'}</div>
  <div class="k">Tipo di oggetto ${src('ArMoni', 'letto per parole chiave dal nome')}</div><div class="v">${x.tipo ? `${esc(x.tipo)} <span class="sub">· dalla parola «${esc(x.tipo_parola)}» nel nome</span>` : '<span class="sub">non riconosciuto dal nome</span>'}</div>
  <h3 class="sez">Luoghi</h3>
  <div class="k">Luogo d'origine ${src('ArMoni', 'il nome di luogo letto nel testo del catalogo')} ${o ? src('Wikidata', 'identità e coordinate del luogo') : ''}</div><div class="v">${o ? `${esc(o.nome)} <span class="sub">· ${PREC[o.precisione]} · letto in «${esc(x.cultura || x.titolo)}» · <a href="https://www.wikidata.org/wiki/${o.qid}">${o.qid}</a></span>` : 'non determinabile dal record'}</div>
  ${x.m ? `<div class="k">Mercato di destinazione ${src(cat)}</div><div class="v">${esc(x.m.nome)} <span class="sub">· dichiarato dal catalogo</span></div>` : ''}
  <div class="k">Dove si trova oggi ${src(cat)}</div><div class="v">${x.s ? esc(x.s.nome) : 'sede senza coordinate'}</div>
  <h3 class="sez">Perché è qui, e la fonte</h3>
  <div class="k">Perché è nell'atlante ${src('ArMoni', 'regola di inclusione del filo')}</div><div class="v">${esc(x.criterio)}</div>
  <div class="k">Fonte e licenza</div><div class="v"><a href="${esc(x.url)}">scheda del museo</a>${x.wikidata ? ` · <a href="https://www.wikidata.org/wiki/${esc(x.wikidata)}">${esc(x.wikidata)}</a>` : ''} · ${esc(x.licenza)}</div>
  ${intornoPezzo(x)}
  <div class="acts"><button data-tav="${x.id}" ${inT ? 'disabled' : ''}>${inT ? 'Già sul tavolo' : 'Metti sul tavolo'}</button><button data-centra="${x.id}">Centra sul luogo</button><button data-back>Indietro</button></div>`;
}
/* Cerca intorno: strade di esplorazione a partire da un pezzo o da un contesto. Accostamenti nello spazio e nel
   tempo, mai relazioni: le liste dicono con quale regola sono state fatte. */
const MARGINE = 25;
const sovrap = (a0, a1, b0, b1) => a0 <= b1 + MARGINE && a1 >= b0 - MARGINE;
const regLuogo = id => LU[id]?.macroregione;
function trovaIntorno(k, x) {
  if (k === 'periodo') { const ps = new Set(x.periodi || []); return O.filter(y => y.id !== x.id && (y.periodi || []).some(q => ps.has(q))); }
  if (k === 'dichiarati') return O.filter(y => (y.periodi || []).includes(x.id) && passa(y));
  if (k === 'tipo') return O.filter(y => y.id !== x.id && y.tipo && y.tipo === x.tipo && (y.fl || '') === (x.fl || '') && sovrap(y.inizio, y.fine, x.inizio, x.fine) && luogo(y) && luogo(y) !== luogo(x));
  if (k === 'ctxdi') { const r = regLuogo(luogo(x)); return CX.filter(e => sovrap(e.quando.da, e.fv, x.inizio, x.fine) && e.luoghi.some(l => l.id === luogo(x) || (r && l.macroregione === r))); }
  if (k === 'opere') { const ids = new Set(x.luoghi.map(l => l.id)), rs = new Set(x.luoghi.map(l => l.macroregione).filter(Boolean));
    return O.filter(y => passa(y) && sovrap(y.inizio, y.fine, x.quando.da, x.fv) && (ids.has(luogo(y)) || rs.has(regLuogo(luogo(y))))); }
  if (k === 'ctxvicini') { const rs = new Set(x.luoghi.map(l => l.macroregione).filter(Boolean));
    return CX.filter(e => e.id !== x.id && sovrap(e.quando.da, e.fv, x.quando.da, x.fv) && e.luoghi.some(l => rs.has(l.macroregione))); }
  return [];
}
const REGOLA_INT = {
  periodo: x => `Pezzi che il loro catalogo dichiara dello stesso periodo (${(x.periodi || []).map(q => PB[q]?.n || q).join(', ')}): una dichiarazione delle fonti, non un accostamento.`,
  dichiarati: e => `Pezzi che il loro catalogo dichiara di questo periodo: una dichiarazione delle fonti, riconosciuta fra le etichette di Wikidata, non un accostamento.`,
  tipo: x => `Pezzi dello stesso tipo («${x.tipo}»), in date che si sovrappongono a quelle di questo (±${MARGINE} anni), fatti in altri luoghi.`,
  ctxdi: x => `Contesti attivi negli stessi anni (±${MARGINE}) nello stesso luogo o nella stessa macro-regione (${regLuogo(luogo(x)) || '—'}).`,
  opere: e => `Oggetti del filo fatti negli anni del fenomeno (±${MARGINE}), nello stesso luogo o nella stessa macro-regione.`,
  ctxvicini: e => `Altri contesti attivi negli stessi anni (±${MARGINE}) nella stessa macro-regione.`};
const NOMI_INT = {periodo: 'Stesso periodo, secondo i cataloghi', dichiarati: 'Oggetti che i cataloghi dichiarano di questo periodo', tipo: 'Stesso tipo, stessa epoca, altrove', ctxdi: 'Contesti qui e allora', opere: 'Oggetti del filo qui e allora', ctxvicini: 'Contesti vicini, negli stessi anni'};
function bottoniIntorno(voci) {
  return `<h3 class="sez">Cerca intorno</h3><p class="sub" style="margin:0 0 6px">Prima i legami che le fonti dichiarano; poi gli accostamenti nello spazio e nel tempo, che legami non sono.</p><div class="intorno">${voci.map(([k, n, extra]) => `<button ${['periodo', 'dichiarati'].includes(k) ? 'class="dich" ' : ''}${extra || `data-intorno="${k}"`} ${n === 0 ? 'disabled' : ''}>${NOMI_INT[k] || k}${n != null ? ` <span class="sub">${n}</span>` : ''}</button>`).join('')}</div>`;
}
function intornoPezzo(x) {
  const v = [...((x.periodi || []).length ? [['periodo', trovaIntorno('periodo', x).length]] : []), ['tipo', x.tipo ? trovaIntorno('tipo', x).length : 0], ['ctxdi', luogo(x) ? trovaIntorno('ctxdi', x).length : 0]];
  if (luogo(x)) v.push(['Tutti i pezzi di ' + (LU[luogo(x)]?.nome || 'questo luogo'), null, `data-place="${luogo(x)}"`]);
  if (!CONFRONTO && luogo(x)) v.push(['Questo luogo nel confronto fra fili', null, `data-confronto="${luogo(x)}"`]);
  return bottoniIntorno(v);
}
function intornoMov(e) {
  const dich = S.L.opere ? trovaIntorno('dichiarati', e).length : 0;
  return bottoniIntorno([...(dich ? [['dichiarati', dich]] : []), ['opere', S.L.opere ? trovaIntorno('opere', e).length : 0], ['ctxvicini', trovaIntorno('ctxvicini', e).length], ['Le sue relazioni nel grafo', null, `data-grafo="${e.id}"`]]);
}
function listaIntorno() {
  const {k, da} = S.intorno, x = da.startsWith('mov:') ? CX.find(e => e.id === da.slice(4)) : O.find(y => y.id === da); if (!x) return '';
  const xs = trovaIntorno(k, x), nome = x.titolo || x.nome, dimo = ['tipo', 'opere', 'periodo', 'dichiarati'].includes(k);
  const righe = dimo ? xs.sort((a, b) => a.inizio - b.inizio).slice(0, 200).map(y => `<div class="row" data-sel="${y.id}"><span>${esc(y.titolo)} <span class="sub">· ${esc(LU[luogo(y)]?.nome || 'senza luogo')}</span></span><span class="n sub">${fmtY(y.inizio)}–${fmtY(y.fine)}</span></div>`)
    : xs.sort((a, b) => a.quando.da - b.quando.da).map(e => `<div class="row" data-place="mov:${e.id}"><span><i>${esc(e.nome)}</i> <span class="sub">· ${e.tipo}, ${esc(e.luoghi[0].oggi)}</span></span><span class="n">${fmtY(e.quando.da)}</span></div>`);
  const per = new Map(); if (dimo) for (const y of xs) { const n = LU[luogo(y)]?.nome || '?'; per.set(n, (per.get(n) || 0) + 1); }
  return `<div class="sub">Cerca intorno a</div><h2 style="margin-top:2px">${esc(nome)}</h2><h3>${NOMI_INT[k]}: ${xs.length}</h3>
  <p class="sub" style="margin:0 0 8px">${REGOLA_INT[k](x)}${['periodo', 'dichiarati'].includes(k) ? '' : ' Stare vicini non vuol dire essere legati.'}</p>
  ${per.size ? `<p class="sub">${[...per].sort((a, b) => b[1] - a[1]).slice(0, 6).map(([n, c]) => `${esc(n)} ${c}`).join(' · ')}</p>` : ''}
  ${righe.join('') || '<p class="sub">Niente.</p>'}${xs.length > 200 && dimo ? `<p class="sub">e altri ${xs.length - 200}.</p>` : ''}
  <div class="acts"><button data-back>Indietro</button></div>`;
}
const PRECM = {luogo: 'luogo dentro un paese', paese: 'solo il paese', regione: 'regione o continente: nessuno Stato'};
const INVERSA = {'influenzato da': 'ha influenzato', 'parte di': 'comprende', 'caso particolare di': 'ha come caso particolare', segue: 'seguito da', sostituisce: 'sostituito da'};
const VIA = {territorio: 'nel paese', partecipante: 'il paese vi partecipa, combattuta altrove'};
function schedaMov(e) {
  const q = e.quando, fine = q.a != null ? fmtY(q.a) : 'fine non dichiarata';
  return `<h2>${esc(e.nome)}</h2><div class="sub" style="margin-top:4px">${e.tipo}${e.sottotipo ? ' (' + e.sottotipo + ')' : ''}${!['it', 'en'].includes(e.nome_lingua) ? ' · nome in ' + esc(e.nome_lingua) + ', l\'unico su Wikidata' : ''}${e.nome_en && e.nome_en !== e.nome ? ' · ' + esc(e.nome_en) : ''} · <a href="https://www.wikidata.org/wiki/${e.id}">${e.id}</a></div>
  ${e.descr ? `<p style="margin-top:10px">${esc(e.descr)}${e.descr_lingua === 'en' ? ' <span class="sub">(descrizione di Wikidata in inglese)</span>' : ''}</p>` : ''}
  <h3>Quando</h3><p><b>${fmtY(q.da)}–${fine}</b><br><span class="sub">${esc(q.metodo)}${q.a == null ? ` · sulla mappa resta visibile ${APERTO} anni` : ''}</span></p>
  <h3>Dove: oggi e allora</h3>${e.luoghi.map(l => `<div class="row" style="cursor:default;display:block"><span class="sub">${l.via}:</span> <b>${esc(l.oggi)}</b>${l.paese_oggi && l.paese_oggi !== l.oggi ? ' · ' + esc(l.paese_oggi) : ''} <span class="sub">(${PRECM[l.precisione]}${l.macroregione ? ' · ' + l.macroregione : ''})</span>
    ${l.stato_allora ? `<br>allora: <b>${esc(l.stato_allora)}</b> <span class="sub">nei confini del ${fmtY(l.istantanea)}, historical-basemaps</span>` : l.precisione !== 'regione' ? `<br><span class="sub">allora: nessuna carta dei confini entro 50 anni${l.istantanea ? ' (la più vicina è del ' + fmtY(l.istantanea) + ')' : ''}</span>` : ''}${l.nome_allora ? `<br>nome di allora: ${esc(l.nome_allora)}` : ''}</div>`).join('')}
  <h3>Relazioni dichiarate su Wikidata</h3>${e.relazioni.length ? e.relazioni.map(r => `<div class="row" ${r.collocata ? `data-place="mov:${r.id}"` : 'style="cursor:default"'}><span><span class="sub">${r.verso === '>' ? r.rel : INVERSA[r.rel]}</span> ${esc(r.nome)}</span><span class="n sub">${r.collocata ? '' : 'senza data o luogo'}</span></div>`).join('')
    : '<p class="sub">Nessuna. L\'atlante non ne deduce dalla vicinanza nello spazio o nel tempo.</p>'}
  <h3>Negli anni della nascita (±${CXR.finestra})</h3>${e.contesto.length ? e.contesto.map(c => `<div class="row" style="cursor:default;display:block">${esc(c.nome)} <span class="sub">· ${c.tipo}, ${fmtY(c.da)}–${fmtY(c.a)} · ${VIA[c.via]}</span></div>`).join('')
    : '<p class="sub">Nessuna guerra o rivoluzione registrata (solo eventi con almeno 20 versioni linguistiche su Wikidata: l\'assenza non è una prova).</p>'}
  <p class="sub" style="margin-top:14px;border-top:1px solid var(--line, #ccc);padding-top:8px">Accostamento nello spazio e nel tempo, non relazione: nessuna opera dell'atlante è attribuita a questa voce. Fonte: Wikidata (CC0).</p>
  ${intornoMov(e)}
  <div class="acts"><button data-back>Indietro</button></div>`;
}
// «l'820», «l'11», «il 1640»: l'articolo segue il suono del numero
const articolo = y => { const t = String(Math.abs(y)); return /^8/.test(t) || t === '11' ? "L'" : 'Il '; };
/* Con una ricerca attiva: quanti pezzi trova in tutto il tempo, quanti nella finestra, dove si addensano. */
function cercaInfo() {
  const q = S.q.trim().toLowerCase(); if (!q) return '';
  const tutti = O.filter(x => passa(x) && x.hay.includes(q));
  const fen = CX.filter(e => S.CT.has(e.tipo) && (!CAT.ctx || e.corsia === CAT.ctx) && (e.nome + ' ' + (e.nome_en || '')).toLowerCase().includes(q)).length;
  let picco = '';
  if (tutti.length) { const dec = new Map(); for (const x of tutti) { const d = Math.floor((x.inizio + x.fine) / 20) * 10; dec.set(d, (dec.get(d) || 0) + 1); }
    picco = [...dec].sort((a, b) => b[1] - a[1])[0][0]; }
  return `<div class="cerca" role="status"><b>«${esc(S.q.trim())}»</b>: ${[S.L.opere ? `${tutti.length} pezzi in tutto il tempo, ${act.length} in questa finestra` : '', S.L.contesti ? `${fen} fenomeni artistici in tutto il tempo, ${cagg.length} in questa finestra` : ''].filter(Boolean).join('; ') || 'accendi un filo o i contesti per cercare'}.
    <div class="acts" style="margin-top:8px">${picco !== '' && tutti.length > act.length && Math.abs(picco + 5 - S.year) > S.win ? `<button data-anno="${picco + 5}">Vai agli anni con più risultati (${fmtY(picco)}–${fmtY(picco + 9)})</button>` : ''}<button data-svuota>Togli la ricerca</button></div></div>`;
}
function renderCtx() {
  const c = $('#ctx'), sel = O.find(x => x.id === S.sel);
  if (sel) { c.innerHTML = scheda(sel); return; }
  if (S.intorno) { c.innerHTML = listaIntorno(); return; }
  if (S.place && S.place.startsWith('mov:')) { const e = CX.find(e => e.id === S.place.slice(4)); if (e) { c.innerHTML = schedaMov(e); return; } }
  if (S.place && S.place.startsWith('sito:')) { const g = lagg.find(g => g.id === S.place), l = LU[S.place];
    c.innerHTML = `<h2>${esc(l.nome)}</h2><div class="sub" style="margin-top:4px">sito archeologico · <a href="https://www.wikidata.org/wiki/${l.qid}">${l.qid}</a></div>
    <p class="sub" style="margin-top:10px">Qui la porcellana è stata usata, raccolta o conservata, non fatta. Numeri ricavati da pubblicazioni: ognuno con la sua pagina o il suo paragrafo.</p>
    ${(g ? g.as : []).map(a => { const f = LET.fonti[a.fonte_id] || {};
      return `<div class="row" style="cursor:default;display:block"><b>${esc(a.tipo)}</b> · ${a.inizio}–${a.fine}<br>${a.misura === 'presenza' ? 'presenza attestata' : ''}${a.frammenti ? esc(a.frammenti) + ' ' + esc(a.unita || 'frammenti') : ''}${a.percentuale ? ' · ' + esc(a.percentuale) + '%' : ''}${a.base ? ' <span class="sub">su ' + esc(a.base) + '</span>' : ''}
      <div class="sub">${esc(f.autori)} ${esc(f.anno)}, ${esc(a.pagina)}${a.nota ? ' — ' + esc(a.nota) : ''} · <a href="${esc(f.url)}">fonte</a></div></div>`; }).join('') || '<p class="sub">Nessun dato in questa finestra.</p>'}
    <div class="acts"><button data-back>Indietro</button></div>`; return; }
  if (S.place) { const g = agg.find(g => g.id === S.place), l = LU[S.place], xs = act.filter(x => luogo(x) === S.place).sort((a, b) => a.inizio - b.inizio);
    c.innerHTML = `<h2>${esc(l.nome)}</h2><div class="sub" style="margin-top:4px">${PREC[l.precisione]} · <a href="https://www.wikidata.org/wiki/${l.qid}">${l.qid}</a> · ${esc(l.metodo)}</div>
    <div class="big" style="margin:14px 0 2px">${xs.length}</div><div class="sub">pezzi fra ${fmtY(S.year - S.win)} e ${fmtY(S.year + S.win)}${g && g.inc ? ` · ${g.inc} con attribuzione incerta` : ''}</div>
    ${(() => { const v = vagg.find(v => v.id === S.place); return v ? `<p class="sub" style="margin-top:8px">V&A, nella stessa finestra: ~${Math.round(v.n)} pezzi (solo conteggio, nessuna scheda: condizioni d'uso del V&A).</p>` : ''; })()}
    <div style="margin-top:12px">${xs.slice(0, 200).map(x => `<div class="row" data-sel="${x.id}"><span>${x.fl ? `<span class="sub">${NOMI_FILO[x.fl]} · </span>` : ''}${esc(x.titolo)}</span><span class="n sub">${fmtY(x.inizio)}–${fmtY(x.fine)}</span></div>`).join('')}</div>
    <div class="acts"><button data-back>Indietro</button></div>`; return; }
  if (!S.L.opere) { c.innerHTML = cercaInfo() + filtriAttivi() + soloContesti(); return; }
  if (CONFRONTO) { c.innerHTML = cercaInfo() + filtriAttivi() + pannelloConfronto(); return; }
  const mx = agg[0]?.n || 1, n = act.length;
  c.innerHTML = cercaInfo() + filtriAttivi() + `<div class="sub">Fra ${fmtY(S.year - S.win)} e ${fmtY(S.year + S.win)}</div><div class="big" style="margin:4px 0">${n}</div>
  <div class="sub">pezzi da ${agg.length} luoghi · ${act.filter(x => x.grado === 'documentato').length} documentati</div>
  <h3 class="sez">Da dove</h3>
  ${agg.slice(0, 14).map(g => `<div class="row" data-place="${g.id}"><span>${esc(g.l.nome)} <span class="sub">${g.l.precisione === 'citta' ? '' : '· ' + PREC[g.l.precisione]}</span><div class="bar" style="width:${100 * g.n / mx}%"></div></span><span class="n">${g.n}</span></div>`).join('') || '<p class="sub">Nessun pezzo in questa finestra.</p>'}
  ${VAM && S.L.vam && S.L.opere && vagg.length ? `<h3 class="sez">V&A, solo conteggi</h3>${vagg.slice(0, 8).map(g => `<div class="row" data-place="${g.id}"><span>${esc(g.l.nome)} <span class="sub">${g.l.precisione === 'citta' ? '' : '· ' + PREC[g.l.precisione]}</span></span><span class="n">~${Math.round(g.n)}</span></div>`).join('')}` : ''}
  ${S.L.contesti ? `<h3 class="sez">Fenomeni artistici in questa finestra</h3>${cagg.length ? cagg.slice(0, 12).map(e => `<div class="row" data-place="mov:${e.id}"><span><i>${esc(e.nome)}</i> <span class="sub">· ${e.tipo}, ${esc(e.luoghi[0].oggi)}</span></span><span class="n">${fmtY(e.quando.da)}</span></div>`).join('') + (cagg.length > 12 ? `<p class="sub">e altri ${cagg.length - 12}: li trovi sulla mappa</p>` : '') : '<p class="sub">Nessuno con data e luogo su Wikidata in questa finestra, per i tipi scelti.</p>'}` : ''}
  ${nominato()}
  <p class="sub" style="margin-top:14px">Ogni punto è un luogo d'origine dichiarato dal catalogo. Il pieno indica una città; l'anello tratteggiato un paese, perché il record non dice di più. I pezzi «ipotetici» appartengono a una manifattura nota per il blu, ma il loro record non nomina il colore. Clicca un luogo per l'elenco, poi un pezzo per la scheda.</p><a class="giu" href="#leggi" data-scorri="leggi">Come leggere tutti i segni ↓</a>`;
}
// collegamenti per saltare: spostano il fuoco senza toccare l'indirizzo, che porta la vista
document.querySelectorAll('.salta').forEach(l => l.onclick = e => { e.preventDefault(); const t = $(l.getAttribute('href')); t.focus(); t.scrollIntoView({block: 'nearest'}); });
const CLIC = '[data-place],[data-sel],[data-go]:not(button)';
new MutationObserver(() => document.querySelectorAll(`#ctx :is(${CLIC}), #nar :is(${CLIC})`).forEach(el => { if (!el.hasAttribute('tabindex')) { el.tabIndex = 0; el.setAttribute('role', 'button'); } }))
  .observe(document.body, {childList: true, subtree: true});
document.addEventListener('keydown', e => { const el = e.target.closest?.(CLIC); if (el && !/^(BUTTON|A|INPUT|SELECT|TEXTAREA)$/.test(el.tagName) && (e.key === 'Enter' || e.key === ' ')) { e.preventDefault(); el.click(); } });
document.addEventListener('click', e => {
  if (e.target.closest('[data-svuota]')) { S.q = ''; $('#q').value = ''; update(); return; }
  const tg = e.target.closest('[data-togli]'); if (tg) { const k = tg.dataset.togli; CAT[k] = ''; update(); return; }
  const cr = e.target.closest('[data-ctxreg]'); if (cr) { CAT.ctx = cr.dataset.ctxreg; update(); return; }
  const an = e.target.closest('[data-anno]'); if (an) { S.year = +an.dataset.anno; update(); return; }
  const t = e.target.closest('[data-sel],[data-place],[data-back],[data-tav],[data-centra],[data-go],[data-intorno],[data-grafo],[data-confronto]'); if (!t) return;
  if (t.dataset.intorno) { S.intorno = {k: t.dataset.intorno, da: S.sel || S.place}; S.sel = null; }
  else if (t.dataset.grafo) { location.href = 'relazioni.html?id=' + t.dataset.grafo; return; }
  else if (t.dataset.confronto) { location.href = location.pathname + '?filo=confronto#ricerca&y=' + S.year + '&w=' + S.win + '&p=' + encodeURIComponent(t.dataset.confronto); return; }
  else if (t.dataset.sel) { S.sel = t.dataset.sel; }
  else if (t.dataset.place) { S.place = t.dataset.place; S.sel = null; S.intorno = null; }
  else if ('back' in t.dataset) { if (S.sel) S.sel = null; else if (S.intorno) S.intorno = null; else S.place = null; }
  else if (t.dataset.tav) { addTav(t.dataset.tav); }
  else if (t.dataset.centra) { const x = O.find(o => o.id === t.dataset.centra); if (x.o) S.rot = [-x.o.lon, -x.o.lat]; }
  else if (t.dataset.go) { S.tappa = +t.dataset.go; applyTappa(); return; }
  renderCtx(); draw();
});

function pannelloConfronto() {
  const per = new Map(); for (const g of agg) { const v = per.get(g.id) || {l: g.l, blu: 0, lacca: 0}; v[g.f] += g.n; per.set(g.id, v); }
  const tot = f => act.filter(x => x.fl === f).length, comuni = [...per].filter(([, v]) => v.blu && v.lacca).sort((a, b) => Math.min(b[1].blu, b[1].lacca) - Math.min(a[1].blu, a[1].lacca));
  const mx = Math.max(1, ...[...per.values()].map(v => Math.max(v.blu, v.lacca)));
  const riga = ([id, v]) => `<div class="row" data-place="${id}"><span>${esc(v.l.nome)} <span class="sub">${v.l.precisione === 'citta' ? '' : '· ' + PREC[v.l.precisione]}</span><div class="bar" style="width:${100 * v.blu / mx}%"></div><div class="bar lac" style="width:${100 * v.lacca / mx}%"></div></span><span class="n">${v.blu} · <span class="lacn">${v.lacca}</span></span></div>`;
  return `<div class="sub">Confronto fra ${fmtY(S.year - S.win)} e ${fmtY(S.year + S.win)}</div>
  <div class="conf"><div><div class="big">${tot('blu')}</div><div class="sub"><span class="seg-blu"></span>blu e bianco</div></div><div><div class="big lacn">${tot('lacca')}</div><div class="sub"><span class="seg-lac"></span>lacca</div></div></div>
  <h3 class="sez">Luoghi dove compaiono entrambi</h3>
  ${comuni.length ? comuni.slice(0, 12).map(riga).join('') : '<p class="sub">In questa finestra nessun luogo ha pezzi di tutti e due i fili.</p>'}
  <h3 class="sez">Solo un filo</h3>
  ${[...per].filter(([, v]) => !(v.blu && v.lacca)).sort((a, b) => (b[1].blu + b[1].lacca) - (a[1].blu + a[1].lacca)).slice(0, 10).map(riga).join('') || '<p class="sub">Nessuno.</p>'}
  <p class="sub" style="margin-top:14px">Dischi blu: porcellana blu e bianca. Anelli color lacca: lacca. Tratteggio: luogo noto solo come paese. Stesso luogo e stesso tempo vogliono dire che i due fili si incontrano lì nei cataloghi, non che siano legati: un legame compare solo dove una fonte lo dichiara. I numeri riflettono anche quanto ogni paese apre i suoi dati.</p><a class="giu" href="#leggi" data-scorri="leggi">Come leggere tutti i segni ↓</a>`;
}
function filtriAttivi() {
  const f = [S.L.opere && CAT.reg && ['reg', `provenienza: ${CAT.reg === '?' ? 'senza luogo' : CAT.reg}`], S.L.opere && CAT.tipo && ['tipo', `tipo: ${CAT.tipo === '?' ? 'non riconosciuto' : CAT.tipo}`],
    S.L.contesti && CAT.ctx && ['ctx', `contesti: ${CAT.ctx}`]].filter(Boolean);
  return f.length ? `<div class="filtri" aria-label="Filtri attivi">${f.map(([k, t]) => `<button data-togli="${k}" aria-label="Togli il filtro ${esc(t)}">${esc(t)} ✕</button>`).join('')}</div>` : '';
}
function soloContesti() {
  if (!S.L.contesti) return `<p>Filo e contesti sono spenti.</p><p class="sub">Accendi a sinistra gli oggetti di un filo, i contesti, o entrambi.</p>`;
  const per = new Map(); for (const e of cagg) per.set(e.corsia, (per.get(e.corsia) || 0) + 1);
  return `<div class="sub">Contesti fra ${fmtY(S.year - S.win)} e ${fmtY(S.year + S.win)}</div><div class="big ctxn" style="margin:4px 0">${cagg.length}</div>
  <div class="sub">fenomeni artistici attivi: ${[...S.CT].map(t => TIPO_PL[t] || t).join(', ')}</div>
  <h3 class="sez">Per regione</h3>
  ${[...per].sort((a, b) => b[1] - a[1]).map(([r, n]) => `<div class="row" data-ctxreg="${esc(r)}"><span>${esc(r)}<div class="bar ctxbar" style="width:${100 * n / cagg.length}%"></div></span><span class="n">${n}</span></div>`).join('') || '<p class="sub">Nessun fenomeno in questa finestra.</p>'}
  <h3 class="sez">Fenomeni</h3>
  ${[...cagg].sort((a, b) => a.quando.da - b.quando.da).slice(0, 60).map(e => `<div class="row" data-place="mov:${e.id}"><span><i>${esc(e.nome)}</i> <span class="sub">· ${e.tipo}, ${esc(e.luoghi[0].oggi)}</span></span><span class="n">${fmtY(e.quando.da)}</span></div>`).join('')}
  ${cagg.length > 60 ? `<p class="sub">e altri ${cagg.length - 60}: restringi la finestra, la regione o i tipi, oppure cerca per nome.</p>` : ''}
  <p class="sub" style="margin-top:14px">Ogni quadrato verde è un fenomeno nel luogo dove nasce, con le date dichiarate o dedotte dagli artisti (la scheda dice quale). Le relazioni compaiono solo dove Wikidata le scrive. Accendi un filo per accostarvi gli oggetti.</p><a class="giu" href="#leggi" data-scorri="leggi">Come leggere tutti i segni ↓</a>`;
}
const TIPO_PL = {movimento: 'movimenti', scuola: 'scuole', stile: 'stili', periodizzazione: 'dinastie'};
function categorie() { }  // le categorie ora sono faccette (renderFacette), ridisegnate a ogni aggiornamento
/* Faccette: per ogni categoria, barre con i conteggi nella finestra di tempo, contando con tutti gli altri
   filtri ma non con il proprio (così si vede che cosa si otterrebbe scegliendo). Un clic filtra, un altro toglie. */
const FAC_APERTA = {};
const NOMI_CAT = {reg: {'?': 'senza luogo'}, tipo: {'?': 'non riconosciuto'}, ctx: {}};
function contaFiltro(k) {
  const q = S.q.toLowerCase(), c = new Map(), y0 = S.year - S.win, y1 = S.year + S.win;
  if (k === 'ctx') { for (const e of CX) if (S.CT.has(e.tipo) && e.quando.da <= y1 && e.fv >= y0 && (!q || (e.nome + ' ' + (e.nome_en || '')).toLowerCase().includes(q))) c.set(e.corsia, (c.get(e.corsia) || 0) + 1); return c; }
  const salva = CAT[k]; CAT[k] = '';
  for (const x of O) if (x.inizio <= y1 && x.fine >= y0 && passa(x) && (!q || x.hay.includes(q))) { const v = k === 'reg' ? regDi(x) : (x.tipo || '?'); c.set(v, (c.get(v) || 0) + 1); }
  CAT[k] = salva; return c;
}
function faccetta(k, titolo, el) {
  const c = contaFiltro(k), voci = [...c].sort((a, b) => (a[0] === '?') - (b[0] === '?') || b[1] - a[1]);
  if (CAT[k] && !c.has(CAT[k])) voci.unshift([CAT[k], 0]);
  const mx = Math.max(1, ...voci.map(v => v[1])), apri = FAC_APERTA[k], vis = apri ? voci : voci.slice(0, 6);
  el.innerHTML = `<div class="fh">${titolo}${CAT[k] ? ` <button class="lnk" data-fac="${k}" data-v="">tutte</button>` : ''}</div>` +
    (vis.map(([v, n]) => `<button class="fv${CAT[k] === v ? ' on' : ''}" data-fac="${k}" data-v="${esc(v)}" aria-pressed="${CAT[k] === v}"><span class="fl">${esc(NOMI_CAT[k][v] || v)}</span><span class="fn">${n.toLocaleString('it')}</span><span class="fb" style="width:${100 * n / mx}%"></span></button>`).join('') || '<p class="sub">Niente in questa finestra.</p>') +
    (voci.length > 6 ? `<button class="lnk" data-facapri="${k}">${apri ? 'meno' : `tutte le ${voci.length}`}</button>` : '');
}
function renderFacette() {
  if (S.L.opere) { faccetta('reg', 'Provenienza', $('#fac-reg')); faccetta('tipo', 'Tipo di oggetto <button class="info" data-infoper="tipo-nota" aria-label="Come è ricavato il tipo" aria-expanded="false">i</button>', $('#fac-tipo')); }
  if (S.L.contesti) faccetta('ctx', 'Provenienza', $('#fac-ctx'));
}
/* Conteggio accanto a ogni livello: quanto c'è di quel livello nella finestra (vuoto = trattino). */
function renderConteggi() {
  const n = {origini: act.filter(x => luogo(x)).length, sedi: new Set(act.map(x => x.sede).filter(Boolean)).size,
    spostamenti: act.filter(x => x.o && x.s && x.o !== x.s).length, mercati: act.filter(x => x.m).length,
    ipotetici: act.filter(x => x.grado === 'ipotetico').length, dedotti: act.filter(x => !x.o && x.origine_dedotta).length,
    vam: Math.round(vagg.reduce((a, g) => a + g.n, 0)), letteratura: lagg.length,
    contesti: cagg.length, relazioni: cagg.reduce((a, e) => a + e.relazioni.filter(r => r.verso === '>' && cagg.some(z => z.id === r.id)).length, 0)};
  const f = new Map(); for (const x of act) f.set(x.fonte, (f.get(x.fonte) || 0) + 1);
  document.querySelectorAll('[data-l],[data-f]').forEach(i => { const k = i.dataset.l || i.dataset.f, v = i.dataset.l ? n[k] : (f.get(k) || 0);
    const cnt = i.closest('label,.shead')?.querySelector('.cnt'); if (cnt) cnt.textContent = v == null ? '' : v ? v.toLocaleString('it') : '–'; });
}
/* Legenda: solo i segni accesi che in questa finestra hanno qualcosa da mostrare. */
let LEG_APERTA = false;
function renderLegenda() {
  const sv = (d, w = 22) => `<svg width="${w}" height="16" viewBox="0 0 ${w} 16" aria-hidden="true">${d}</svg>`, v = [];
  if (S.L.opere && S.L.origini && agg.length) {
    if (CONFRONTO) v.push([sv('<circle cx="11" cy="8" r="6" fill="var(--co)" opacity=".75"/>'), 'porcellana blu e bianca'], [sv('<circle cx="11" cy="8" r="5.5" fill="none" stroke="var(--lacca)" stroke-width="2.4"/>'), 'lacca']);
    else v.push([sv('<circle cx="11" cy="8" r="6" fill="var(--co)" opacity=".75"/>'), 'luogo d\'origine: città (più pieno, più documentato)']);
    v.push([sv('<circle cx="11" cy="8" r="6" fill="var(--co)" fill-opacity=".12" stroke="var(--co)" stroke-dasharray="3 3"/>'), 'solo paese o regione: il record non dice di più']);
    if (agg.some(g => g.inc)) v.push([sv('<circle cx="11" cy="8" r="7" fill="none" stroke="var(--ink)" stroke-dasharray="1 3"/>'), 'attribuzione incerta']);
    if (ALONI.length) v.push([sv('<circle cx="11" cy="8" r="7.5" fill="var(--alone)" opacity=".35"/>'), 'alone: estensione del paese o della regione']);
  }
  if (S.L.opere && S.L.sedi && act.some(x => x.sede)) v.push([sv('<rect x="7" y="4" width="8" height="8" fill="var(--ink)"/>'), 'dove si trovano oggi']);
  if (S.L.opere && S.L.spostamenti && act.some(x => x.o && x.s)) v.push([sv('<path d="M2 12 Q11 0 20 12" fill="none" stroke="var(--co)" stroke-width="1.6" opacity=".6"/>'), 'spostamento: dall\'origine al museo']);
  if (S.L.opere && S.L.mercati && act.some(x => x.m)) v.push([sv('<path d="M2 8 H20" stroke="var(--fe)" stroke-width="1.4" stroke-dasharray="4 3"/>'), 'mercato dichiarato']);
  if (S.L.opere && S.L.vam && vagg.length) v.push([sv('<path d="M11 2 L17 8 L11 14 L5 8 Z" fill="none" stroke="var(--fe)"/>'), 'V&A: solo conteggi']);
  if (S.L.opere && S.L.letteratura && lagg.length) v.push([sv('<path d="M11 2 L17 13 L5 13 Z" fill="none" stroke="var(--ink)"/>'), 'consumo, dalla letteratura']);
  if (S.L.contesti && cagg.length) { v.push([sv('<rect x="6" y="3" width="10" height="10" fill="none" stroke="var(--cel)" stroke-width="1.4"/>'), 'contesto: dove nasce (tratteggio: solo paese)']);
    if (S.L.relazioni) v.push([sv('<path d="M2 8 H20" stroke="var(--cel)" stroke-width="1.6" stroke-dasharray="1 3"/>'), 'relazione dichiarata da Wikidata']); }
  if (S.place) v.push([sv('<circle cx="11" cy="8" r="6" fill="none" stroke="var(--fe)" stroke-width="2"/>'), 'selezione']);
  $('#legbody').innerHTML = v.length ? v.map(([g, t]) => `<div class="lv">${g}<span>${t}</span></div>`).join('') : '<p class="sub">Nessun segno acceso in questa finestra.</p>';
  $('#legbtn').textContent = `Legenda (${v.length})`;
}
/* Copertura: in fondo, sempre visibile. Cosa c'è, cosa manca e perché. */
let COP = [];
const NOMI_FONTE = {met: 'Met', cma: 'Cleveland', aic: 'Chicago', colbase: 'ColBase', emuseum: 'musei coreani', wd: 'Wikidata'};
function renderCopertura() {
  if (!COP.length) return;
  const pezzi = COP.reduce((a, c) => a + c.pezzi, 0), sd = COP.reduce((a, c) => a + c.senza_data, 0), fonti = new Set(COP.flatMap(c => Object.keys(c.fonti)));
  const escl = new Map(); for (const c of COP) for (const e of c.esclusi) escl.set(e.motivo, (escl.get(e.motivo) || 0) + e.n);
  const manc = [...new Map(COP.flatMap(c => c.mancanti).map(m => [m.fonte, m])).values()];
  $('#cop').innerHTML = `<b>${CONFRONTO ? 'Due fili' : 'Filo ' + NOMI_FILO[FILO]}:</b> ${pezzi.toLocaleString('it')} pezzi da ${fonti.size} fonti (${[...fonti].map(f => NOMI_FONTE[f] || f).join(', ')}) · ${sd.toLocaleString('it')} senza data, fuori dalla barra del tempo`
    + [...escl].map(([m, n]) => ` · <span title="esclusi">esclusi ${n.toLocaleString('it')}: ${esc(m)}</span>`).join('')
    + manc.map(m => ` · <span class="manca" title="${esc(m.esito)} — ${esc(m.prossimo)}">manca: ${esc(m.fonte.split(' (')[0])}</span>`).join('')
    + ` · <a href="fonti.html">fonti e licenze</a>`;
}
function segnaposto() {
  $('#q').placeholder = S.L.opere && S.L.contesti ? 'Cerca nel filo e nei contesti' : S.L.opere ? 'Cerca nel filo: titolo, luogo, tecnica' : S.L.contesti ? 'Cerca nei contesti' : 'Accendi un filo o i contesti';
}

/* ---------- tavolo ---------- */
/* Tavoli: più tavoli con un nome, per filo, nella memoria del browser; si salvano su file, si riaprono da file
   e viaggiano in un link. Le schede di pezzi che il filo non ha (più) restano, segnate, e non si perdono. */
const TK = f => 'armoni-tavoli-' + f;
let TAV = {attivo: 'Tavolo 1', tavoli: {'Tavolo 1': []}};
const leggiStore = f => { try { const v = JSON.parse(localStorage.getItem(TK(f)) || 'null'); if (v && v.tavoli) return v; } catch (e) { } return null; };
function caricaTavoli() {
  TAV = leggiStore(FILO) || (() => { let vecchio = []; try { vecchio = JSON.parse(localStorage.getItem(TAVK) || '[]'); } catch (e) { } return {attivo: 'Tavolo 1', tavoli: {'Tavolo 1': vecchio}}; })();
  if (!TAV.tavoli[TAV.attivo]) TAV.attivo = Object.keys(TAV.tavoli)[0] || (TAV.tavoli['Tavolo 1'] = [], 'Tavolo 1');
  S.tav = TAV.tavoli[TAV.attivo]; salva(true);
}
let ultimoSalvataggio = null;
const salva = (zitto) => { TAV.tavoli[TAV.attivo] = S.tav; try { localStorage.setItem(TK(FILO), JSON.stringify(TAV)); ultimoSalvataggio = new Date(); } catch (e) { statoTav('Non riesco a salvare in questo browser (memoria piena o navigazione privata): usa «Salva su file».'); return; } if (!zitto) statoTav(); };
function statoTav(msg) {
  const el = $('#tavstato'); if (!el) return;
  el.textContent = msg || (ultimoSalvataggio ? `Salvato in questo browser alle ${ultimoSalvataggio.toLocaleTimeString('it', {hour: '2-digit', minute: '2-digit'})} · per non perderlo altrove: «Salva su file» o «Link del tavolo»` : '');
}
function menuTavoli() {
  const nomi = Object.keys(TAV.tavoli);
  $('#tavsel').innerHTML = nomi.map(n => `<option${n === TAV.attivo ? ' selected' : ''}>${esc(n)}</option>`).join('');
  $('#tavdel').disabled = nomi.length < 2 && !S.tav.length;
}
const nomeLibero = n => { let k = n, i = 2; while (TAV.tavoli[k]) k = `${n} (${i++})`; return k; };
function usaTavolo(n) { TAV.attivo = n; S.tav = TAV.tavoli[n]; salva(true); renderTav(); renderTavCount(); renderCtx(); }
$('#tavsel').onchange = e => usaTavolo(e.target.value);
$('#tavnew').onclick = () => { const n = prompt('Nome del nuovo tavolo', nomeLibero('Tavolo ' + (Object.keys(TAV.tavoli).length + 1))); if (!n || !n.trim()) return; const k = nomeLibero(n.trim()); TAV.tavoli[k] = []; usaTavolo(k); };
$('#tavren').onclick = () => { const n = prompt('Nuovo nome del tavolo', TAV.attivo); if (!n || !n.trim() || n.trim() === TAV.attivo) return; const k = nomeLibero(n.trim());
  TAV.tavoli[k] = TAV.tavoli[TAV.attivo]; delete TAV.tavoli[TAV.attivo]; usaTavolo(k); };
$('#tavdel').onclick = () => { if (!confirm(`Eliminare il tavolo «${TAV.attivo}» con ${S.tav.length} schede? Non si può annullare: se vuoi tenerne una copia, prima «Salva su file».`)) return;
  delete TAV.tavoli[TAV.attivo]; if (!Object.keys(TAV.tavoli).length) TAV.tavoli['Tavolo 1'] = []; usaTavolo(Object.keys(TAV.tavoli)[0]); };
/* su file: le schede con titolo e link al museo, così il file si legge anche senza ArMoni */
function fileTavolo() {
  return {armoni: 'tavolo', versione: 1, filo: FILO, nome: TAV.attivo, salvato: new Date().toISOString(), origine: location.origin + location.pathname,
    schede: S.tav.map(c => { const x = O.find(o => o.id === c.id); return {...c, titolo: x?.titolo, museo: x?.url}; })};
}
$('#tavsave').onclick = () => { const a = document.createElement('a'), d = new Date().toISOString().slice(0, 10);
  a.href = URL.createObjectURL(new Blob([JSON.stringify(fileTavolo(), null, 1)], {type: 'application/json'}));
  a.download = `armoni-tavolo-${TAV.attivo.replace(/[^\p{L}\p{N}]+/gu, '-').toLowerCase()}-${d}.json`; a.click(); setTimeout(() => URL.revokeObjectURL(a.href), 2000);
  statoTav(`Salvato su file: ${a.download}`); };
$('#tavopen').onclick = () => $('#tavfile').click();
$('#tavfile').onchange = async e => { const f = e.target.files[0]; e.target.value = ''; if (!f) return;
  try { riceviTavolo(JSON.parse(await f.text()), 'dal file ' + f.name); } catch (err) { statoTav('Il file non è un tavolo di ArMoni leggibile.'); } };
function riceviTavolo(d, da) {
  if (!d || d.armoni !== 'tavolo' || !Array.isArray(d.schede)) { statoTav('Il file non è un tavolo di ArMoni.'); return; }
  const schede = d.schede.filter(c => c && typeof c.id === 'string').map(c => ({id: c.id, x: +c.x || 0, y: +c.y || 0, nota: String(c.nota || ''), vista: c.vista, quando: c.quando, ...(c.titolo ? {titolo: String(c.titolo)} : {}), ...(c.museo ? {museo: String(c.museo)} : {})}));
  const f = d.filo && /^[a-z]+$/.test(d.filo) ? d.filo : FILO;
  if (f !== FILO) { const st = leggiStore(f) || {attivo: 'Tavolo 1', tavoli: {}}; let k = d.nome || 'Tavolo ricevuto', i = 2; while (st.tavoli[k]) k = `${d.nome} (${i++})`;
    st.tavoli[k] = schede; st.attivo = k; try { localStorage.setItem(TK(f), JSON.stringify(st)); } catch (e) { }
    statoTav(`Il tavolo «${k}» è del filo ${NOMI_FILO[f] || f}: l'ho messo fra i suoi tavoli. Cambia filo dal menu per aprirlo.`); return; }
  const n0 = d.nome || 'Tavolo ricevuto', k = TAV.tavoli[n0] && !TAV.tavoli[n0].length ? n0 : nomeLibero(n0); TAV.tavoli[k] = schede; usaTavolo(k);  // un tavolo vuoto con lo stesso nome si riusa
  const mancano = schede.filter(c => !O.some(o => o.id === c.id)).length;
  statoTav(`Aperto «${k}» ${da}: ${schede.length} schede${mancano ? `, ${mancano} di pezzi che qui non ci sono (restano segnate)` : ''}.`);
  mostraTavolo();
}
/* nel link: id, posizione e nota di ogni scheda, compressi; si apre ovunque e diventa un tavolo nuovo */
const b64u = b => btoa(String.fromCharCode(...new Uint8Array(b))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
const ub64 = s => Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0));
async function comprimi(t) { const s = new Blob([t]).stream().pipeThrough(new CompressionStream('deflate-raw')); return b64u(await new Response(s).arrayBuffer()); }
async function decomprimi(z) { const s = new Blob([ub64(z)]).stream().pipeThrough(new DecompressionStream('deflate-raw')); return new Response(s).text(); }
$('#tavlink').onclick = async () => {
  const d = {armoni: 'tavolo', versione: 1, filo: FILO, nome: TAV.attivo, schede: S.tav.map(c => ({id: c.id, x: Math.round(c.x), y: Math.round(c.y), nota: c.nota}))};
  const u = new URL(location.pathname, location.origin); if (!PRIMO) u.searchParams.set('filo', FILO); u.searchParams.set('tavolo', await comprimi(JSON.stringify(d))); u.hash = 'ricerca';
  try { await navigator.clipboard.writeText(u.href); statoTav(`Link del tavolo copiato (${u.href.length} caratteri): chi lo apre trova «${TAV.attivo}» fra i suoi tavoli, con le note.`); }
  catch (e) { prompt('Copia il link del tavolo', u.href); }
};
async function tavoloDaLink() {
  const q = new URLSearchParams(location.search), z = q.get('tavolo'); if (!z) return;
  q.delete('tavolo'); history.replaceState(null, '', location.pathname + (q.toString() ? '?' + q : '') + location.hash);
  try { riceviTavolo(JSON.parse(await decomprimi(z)), 'da un link'); } catch (e) { statoTav('Il link del tavolo non si legge: forse è stato tagliato copiandolo.'); mostraTavolo(); }
}
/* Ogni scheda del tavolo ricorda da dove viene: il pezzo (si riapre nella sua scheda, sul suo luogo e nel suo
   tempo), la vista in cui l'hai trovato, e la scheda del museo. Così navigando non si perde nulla. */
function addTav(id) { if (S.tav.some(c => c.id === id)) return; const i = S.tav.length;
  S.tav.push({id, x: 16 + (i % 5) * 276, y: 14 + Math.floor(i / 5) * 290, nota: '', vista: vistaURL(), quando: new Date().toISOString().slice(0, 10)}); salva(); renderTav(); renderTavCount(); }
function apriPezzo(id) {
  const x = O.find(o => o.id === id); if (!x) return;
  S.mode = 'ricerca'; S.intorno = null; S.sel = id; S.place = luogo(x);
  const mezzo = Math.round((x.inizio + x.fine) / 2); S.year = Math.max(T0, Math.min(T1, mezzo)); S.win = Math.max(S.win, Math.min(100, Math.ceil((x.fine - x.inizio) / 2)));
  const l = LU[luogo(x)]; if (l) S.rot = [-l.lon, -l.lat];
  $('#tavolo').classList.remove('open'); if (location.hash.split('&')[0] !== '#ricerca') location.hash = '#ricerca'; update(); window.scrollTo({top: 0, behavior: RIDOTTO.matches ? 'auto' : 'smooth'});
  $('#ctx').scrollTop = 0; $('#ctx').focus?.();
}
function renderTav() {
  $('#tavn').textContent = S.tav.length;
  const b = $('#board');
  menuTavoli(); statoTav();
  b.innerHTML = S.tav.length ? S.tav.map((c, i) => { const x = O.find(o => o.id === c.id);
    if (!x) return `<article class="card manca" data-i="${i}" style="left:${c.x}px;top:${c.y}px"><div class="ch"><span class="num">${i + 1}</span><b class="tt">${esc(c.titolo || c.id)}</b><button class="x" data-rm="${i}" aria-label="Togli dal tavolo">×</button></div><div class="cb"><p class="sub">Questo pezzo non è nel filo che stai guardando (o non è più nei dati). La scheda resta sul tavolo.</p>${c.nota ? `<p>${esc(c.nota)}</p>` : ''}${c.museo ? `<a href="${esc(c.museo)}" target="_blank" rel="noopener">Museo ↗</a>` : ''}</div></article>`;
    const l = LU[luogo(x)], cat = FONTE_LUNGA[x.fonte] || x.fonte;
    return `<article class="card" data-i="${i}" style="left:${c.x}px;top:${c.y}px" aria-label="Scheda ${i + 1} del tavolo: ${esc(x.titolo)}">
    <div class="ch"><span class="num">${i + 1}</span><b class="tt" title="${esc(x.titolo)}">${esc(x.titolo)}</b><button class="x" data-rm="${i}" aria-label="Togli dal tavolo">×</button></div>
    <div class="cb">
     <div class="tags"><span class="tag ${x.grado === 'documentato' ? 'doc' : 'ipo'}">${x.grado}</span>${x.fl ? `<span class="tag">${NOMI_FILO[x.fl]}</span>` : ''}${x.tipo ? `<span class="tag">${esc(x.tipo)}</span>` : ''}</div>
     <dl>
      <dt>Da dove</dt><dd>${l ? `${esc(l.nome)} <span class="sub">· ${PREC[l.precisione]}</span>` : '<span class="sub">luogo non determinabile</span>'}</dd>
      <dt>Quando</dt><dd>${esc(x.data_testo) || '—'}${`${fmtY(x.inizio)}–${fmtY(x.fine)}` === (x.data_testo || '').trim() ? '' : ` <span class="sub">· ${fmtY(x.inizio)}–${fmtY(x.fine)}</span>`}</dd>
      ${x.cultura && x.cultura !== x.data_testo ? `<dt>Cultura</dt><dd>${esc(x.cultura)}</dd>` : ''}
      ${x.tecnica ? `<dt>Tecnica</dt><dd class="lim">${esc(x.tecnica)}</dd>` : ''}
      <dt>Oggi</dt><dd>${esc(x.museo || (x.s ? x.s.nome : '—'))} <span class="sub">· ${esc(cat)}</span></dd>
     </dl>
     <textarea data-nota="${i}" placeholder="Nota" aria-label="Nota sulla scheda ${i + 1}">${esc(c.nota)}</textarea>
     <div class="cacts"><button data-apri="${x.id}">Apri la scheda</button>${c.vista ? `<a href="${esc(c.vista)}" data-vista="${i}" title="La vista dell'atlante in cui l'hai messa sul tavolo${c.quando ? ', il ' + c.quando : ''}">Vista d'origine</a>` : ''}<a href="${esc(x.url)}" target="_blank" rel="noopener">Museo ↗</a></div>
    </div></article>`; }).join('')
    : '<p class="empty">Il tavolo è vuoto. Apri la scheda di un pezzo e scegli «Metti sul tavolo»: qui potrai accostare opere di luoghi ed epoche diverse, spostarle e annotarle. Ogni scheda riporta al pezzo, alla vista in cui l\'hai trovato e al museo. Il tavolo resta solo in questo browser.</p>';
  requestAnimationFrame(() => { b.style.height = Math.max(340, ...[...b.querySelectorAll('.card')].map(c => c.offsetTop + c.offsetHeight + 24)) + 'px'; });  // la lavagna cresce con le schede
  const ax = $('#tavax'), w = ax.clientWidth || 600, xs = S.tav.map(c => O.find(o => o.id === c.id)).filter(Boolean);
  if (!xs.length) { ax.innerHTML = ''; return; }
  const lo = Math.min(...xs.map(x => x.inizio)) - 20, hi = Math.max(...xs.map(x => x.fine)) + 20, sc = d3.scaleLinear([lo, hi], [24, w - 24]);
  ax.innerHTML = xs.map((x, i) => `<g data-apri="${x.id}" style="cursor:pointer"><title>${esc(x.titolo)} — apri la scheda</title><line x1="${sc(x.inizio)}" x2="${Math.max(sc(x.fine), sc(x.inizio) + 2)}" y1="${10 + (i % 4) * 8}" y2="${10 + (i % 4) * 8}" stroke="var(--co)" stroke-width="4" stroke-linecap="round"/><text x="${sc(x.inizio) - 4}" y="${14 + (i % 4) * 8}" font-size="10" fill="var(--fe)" text-anchor="end">${i + 1}</text></g>`).join('')
    + sc.ticks(6).map(t => `<text x="${sc(t)}" y="52" font-size="10.5" fill="var(--mute)" text-anchor="middle">${fmtY(t)}</text>`).join('');
}
let cd = null;
$('#board').addEventListener('pointerdown', e => { const h = e.target.closest('.ch'); if (!h || e.target.closest('button')) return; const card = h.parentElement, i = +card.dataset.i; cd = {i, card, x: e.clientX - S.tav[i].x, y: e.clientY - S.tav[i].y}; h.setPointerCapture(e.pointerId); });
$('#board').addEventListener('pointermove', e => { if (!cd) return; const c = S.tav[cd.i]; c.x = Math.max(0, e.clientX - cd.x); c.y = Math.max(0, e.clientY - cd.y); cd.card.style.left = c.x + 'px'; cd.card.style.top = c.y + 'px'; });
$('#board').addEventListener('pointerup', () => { if (cd) { cd = null; salva(); const b = $('#board'); b.style.height = Math.max(340, ...[...b.querySelectorAll('.card')].map(c => c.offsetTop + c.offsetHeight + 24)) + 'px'; } });
$('#board').addEventListener('input', e => { if (e.target.dataset.nota) { S.tav[+e.target.dataset.nota].nota = e.target.value; salva(); } });
$('#board').addEventListener('click', e => { const r = e.target.closest('[data-rm]'); if (r) { S.tav.splice(+r.dataset.rm, 1); salva(); renderTav(); renderCtx(); return; }
  const a = e.target.closest('[data-apri]'); if (a) { apriPezzo(a.dataset.apri); return; }
  const v = e.target.closest('[data-vista]'); if (v) { e.preventDefault(); const c = S.tav[+v.dataset.vista], u = new URL(c.vista, location.href);
    if (u.pathname === location.pathname && u.search === location.search) { location.hash = u.hash; window.scrollTo({top: 0}); } else location.href = u.href; } });
$('#tavax').addEventListener('click', e => { const a = e.target.closest('[data-apri]'); if (a) apriPezzo(a.dataset.apri); });
$('#tavbtn').onclick = () => { renderTav(); mostraTavolo(); };
$('#tavclose').onclick = () => window.scrollTo({top: 0, behavior: RIDOTTO.matches ? 'auto' : 'smooth'});
function mostraTavolo() { $('#tavolo').classList.add('open'); $('#tavolo').scrollIntoView({behavior: RIDOTTO.matches ? 'auto' : 'smooth', block: 'start'}); }
$('#tavclear').onclick = () => { if (S.tav.length && !confirm(`Togliere tutte le ${S.tav.length} schede dal tavolo «${TAV.attivo}»?`)) return; S.tav.length = 0; salva(); renderTav(); renderCtx(); };
$('#tavcopy').onclick = async () => { const t = S.tav.map((c, i) => { const x = O.find(o => o.id === c.id); return `${i + 1}. ${x.titolo} — ${x.cultura}, ${x.data_testo} [${x.grado}]\n   museo: ${x.url}${c.vista ? '\n   in ArMoni: ' + c.vista : ''}${c.nota ? '\n   nota: ' + c.nota : ''}`; }).join('\n');
  const b = $('#tavcopy'); try { await navigator.clipboard.writeText(t); b.textContent = 'Copiato'; } catch (e) { b.textContent = 'Copia non consentita qui'; } setTimeout(() => { b.textContent = 'Copia elenco'; }, 1800); };

/* ---------- percorso ---------- */
let Lr = null;
function applyTappa() {
  const t = TAPPE[S.tappa]; if (!Lr) Lr = {...S.L};
  S.year = t.y; S.win = t.w; S.rot = [...t.rot]; S.k = 1; S.place = null; S.sel = null;
  CAT.reg = CAT.tipo = CAT.ctx = '';  // il racconto vale sull'intero filo
  if (t.po) { S.corsie = 'periodo'; $('#corsie').value = 'periodo'; }
  S.L = {opere: 1, periodi: t.po ? 1 : 0, confini: 1, origini: 1, sedi: 0, spostamenti: 0, mercati: 0, silenzio: 0, ipotetici: 1, dedotti: 0, vam: 0, letteratura: 0, contesti: 0, relazioni: 0, ...t.L}; G.on = {}; G.mem = {};
  update();
  const inHi = act.filter(x => t.hi.includes(x.origine)), ipo = inHi.filter(x => x.grado === 'ipotetico').length;
  const poDati = () => { if (!PO) return 'PeriodO non caricato.'; return 'Nel ' + fmtY(t.y) + ': ' + REG_PO.map(r => { const ps = PO.periodi.filter(p => p.r === r && p.a <= t.y && p.b >= t.y); if (!ps.length) return ''; const lg = {}; for (const p of ps) lg[p.lg] = (lg[p.lg] || 0) + 1;
    return `<b>${esc(r)}</b> ${ps.length} (${Object.entries(lg).map(([l, n]) => (LINGUE[l] || l) + ' ' + n).join(', ')})`; }).filter(Boolean).join(' · ') + '.'; };
  const dati = t.po ? poDati() : t.hi.length ? `Fra ${fmtY(t.y - t.w)} e ${fmtY(t.y + t.w)} i dati contengono <b>${act.length}</b> pezzi; <b>${inHi.length}</b> vengono dai luoghi evidenziati${ipo ? `, di cui ${ipo} ipotetici` : ''}.`
    : `<b>${O.length}</b> pezzi con data, ${NOD.length} senza. Il ${Math.round(100 * O.filter(x => x.o && x.o.precisione !== 'citta').length / O.length)}% è localizzato solo per paese; il ${Math.round(100 * O.filter(x => x.fonte === 'met' || x.fonte === 'cma').length / O.length)}% è conservato negli Stati Uniti.`;
  $('#nar').innerHTML = `<div class="step">Tappa ${S.tappa + 1} di ${TAPPE.length} · ${fmtY(t.y)}</div><h2>${esc(t.t)}</h2><p>${esc(t.p)}</p>${t.nv ? `<p class="nv"><b>Da verificare.</b> ${esc(t.nv)}</p>` : ''}<div class="dati">${dati}</div>
  <div class="acts"><button data-go="${Math.max(0, S.tappa - 1)}" ${S.tappa ? '' : 'disabled'}>← Precedente</button><button data-go="${Math.min(TAPPE.length - 1, S.tappa + 1)}" ${S.tappa < TAPPE.length - 1 ? '' : 'disabled'}>Successiva →</button></div>
  <div class="dots">${TAPPE.map((_, i) => `<button data-go="${i}" aria-pressed="${i === S.tappa}" aria-label="Tappa ${i + 1}">${i + 1}</button>`).join('')}</div>
  <p class="nota">Testi scritti da Claude. Le frasi con un riferimento tra parentesi rimandano a pagina o paragrafo della fonte, letta per intero; quanto sta in «Da verificare» non ha ancora una fonte. I numeri sono calcolati sui dati. Fonti: Zhao 2015, <i>Afriques</i> 06; Medley 1986, <i>Encyclopaedia Iranica</i>; Tufan 2024, <i>Millî Saraylar</i> 26; Von der Porten 2015, SHA; PeriodO; Japan Search.</p>`;
}
function renderQual() {
  if (!QU) { $('#qual').innerHTML = PRIMO ? '<p>Riepilogo non disponibile.</p>' : '<p>Il riepilogo di affidabilità per regione e secolo per ora esiste solo per il filo blu e bianco. Le metriche di questo filo sono in <code>out/filo_' + FILO + '.md</code> nel repository.</p>'; return; }
  const M = {doc: ['% documentati', c => c.doc / c.n, 'il record nomina il blu'], citta: ['% localizzati per città', c => c.citta / c.n, 'il luogo d\'origine è una città, non un paese'],
    n: ['pezzi', c => c.n, 'quanti pezzi con luogo e data'], vam: ['V&A (conteggi)', c => c.vam, 'pezzi del V&A, solo conteggi']};
  const [nome, f, spiega] = M[qmet], cel = new Map(QU.celle.filter(c => c.n || c.vam >= .5).map(c => [c.r + c.s, c]));
  const mx = qmet === 'n' || qmet === 'vam' ? Math.max(...QU.celle.map(f), 1) : 1;
  const col = v => `color-mix(in srgb, var(--co) ${Math.round(100 * Math.sqrt(v / mx))}%, transparent)`;
  $('#qual').innerHTML = `<h2>Dove l'atlante regge, e dove no</h2>
  <p>Per regione d'origine e secolo (punto medio della datazione). Lo schema che emerge: in Asia il colore è quasi sempre dichiarato ma il luogo raramente è una città; in Europa e Anatolia il contrario. Asia meridionale e Africa sono vuote nei cataloghi museali: l'Africa compare solo grazie alle ${QU.letteratura} asserzioni bibliografiche.</p>
  <div class="qsel" role="group" aria-label="Misura">${Object.entries(M).map(([k, m]) => `<button data-qm="${k}" aria-pressed="${k === qmet}">${m[0]}</button>`).join('')}</div>
  <p class="sub" style="margin-top:6px">Colore della cella: ${esc(spiega)}. Testo piccolo: pezzi della cella.</p>
  <div class="scroll"><table class="qt"><thead><tr><th>regione</th>${QU.secoli.map(s => `<th>${s}</th>`).join('')}</tr></thead><tbody>
  ${QU.regioni.map(r => `<tr><td>${esc(r)}</td>${QU.secoli.map(s => { const c = cel.get(r + s); if (!c || !(c.n || c.vam)) return '<td>—</td>';
    const v = c.n ? f(c) : (qmet === 'vam' ? c.vam : null); if (v == null) return `<td><small>V&A ~${Math.round(c.vam)}</small></td>`;
    const txt = qmet === 'n' ? c.n : qmet === 'vam' ? '~' + Math.round(c.vam) : Math.round(100 * v) + '%';
    const sc = Math.sqrt(v / mx) > .55;  // su fondo scuro il testo passa al colore del fondo pagina
    return `<td style="background:${col(v)}${sc ? ';color:var(--bg)' : ''}">${txt}<small${sc ? ' style="color:var(--bg);opacity:.85"' : ''}>${c.n} pezzi</small></td>`; }).join('')}</tr>`).join('')}
  </tbody></table></div>
  <p class="sub" style="margin-top:12px">Fuori dalla tabella: ${Object.entries(QU.fuori).map(([k, v]) => `${esc(k)} ${v}`).join(' · ')}. Regione dal paese su Wikidata (P17).</p>${(QU.mancanti || []).length ? `<h3 style="margin-top:18px">Fonti cercate e non raggiunte</h3><p class="sub">Un vuoto nella tabella può essere un vuoto delle fonti, non della storia.</p><ul>${QU.mancanti.map(m => `<li><b>${esc(m.fonte)}</b> · ${esc(m.regione)}, ${esc(m.ultimo_tentativo)}<br>${esc(m.esito)}. Ripiego: ${esc(m.ripiego_misurato)}. Prossimo passo: ${esc(m.prossimo_passo)}.</li>`).join('')}</ul>` : ''}`;
}
function route() {
  const m = location.hash.slice(1).split('&')[0];  // dopo il modo possono seguire i parametri di una vista condivisa
  S.mode = m === 'percorso' && PRIMO ? 'percorso' : m === 'qualita' ? 'qualita' : 'ricerca';
  document.body.classList.toggle('percorso', S.mode === 'percorso');
  document.body.classList.toggle('qualita', S.mode === 'qualita');
  document.body.classList.toggle('ricerca', S.mode === 'ricerca');
  for (const m of ['ricerca', 'percorso', 'qualita']) $('#m-' + m).setAttribute('aria-pressed', S.mode === m);
  if (S.mode !== 'ricerca') $('#tavolo').classList.remove('open');  // negli altri modi il pulsante del Tavolo non c'è
  if (S.mode === 'qualita') { renderQual(); return; }
  if (S.mode === 'percorso') applyTappa(); else { if (Lr) { S.L = Lr; Lr = null; } syncChecks(); update(); }
  requestAnimationFrame(misura);  // dopo il cambio di griglia la mappa ha nuove misure
}
window.addEventListener('hashchange', () => { if (location.hash.includes('&y=')) leggiVista(); route(); });
$('#m-ricerca').onclick = () => { location.hash = 'ricerca'; };
$('#m-percorso').onclick = () => { location.hash = 'percorso'; };
$('#m-qualita').onclick = () => { location.hash = 'qualita'; };
document.addEventListener('click', e => { const b = e.target.closest('[data-qm]'); if (b) { qmet = b.dataset.qm; renderQual(); } });

/* ---------- controlli ---------- */
/* Cartelle di livelli: spegnere una cartella ne ricorda le voci; riaccenderla le rimette com'erano.
   Accendere una voce dentro una cartella spenta riaccende la cartella. */
const figli = g => [...document.querySelectorAll(`[data-grp="${g}"] [data-l]:not([data-keep])`)].map(i => i.dataset.l);
const syncChecks = () => {
  document.querySelectorAll('[data-l]').forEach(i => { i.checked = !!S.L[i.dataset.l]; });
  document.querySelectorAll('[data-g]').forEach(i => { const g = i.dataset.g, f = figli(g), n = f.filter(k => S.L[k]).length;
    i.checked = G.on[g] !== false; i.indeterminate = false; $(`[data-gn="${g}"]`).textContent = G.on[g] === false ? 'spenta' : `${n}/${f.length}`; });
};
document.querySelectorAll('[data-l]').forEach(i => i.onchange = () => { S.L[i.dataset.l] = i.checked ? 1 : 0; if (i.dataset.l === 'periodi') requestAnimationFrame(pannelli); if (i.dataset.l === 'ipotetici') categorie(); const g = i.closest('[data-grp]')?.dataset.grp; if (g && i.checked) G.on[g] = true; syncChecks(); update(); });
document.querySelectorAll('[data-g]').forEach(i => i.onchange = () => { const g = i.dataset.g;
  if (i.checked) { G.on[g] = true; const m = G.mem[g]; if (m) for (const k of figli(g)) S.L[k] = m[k]; }
  else { G.on[g] = false; G.mem[g] = Object.fromEntries(figli(g).map(k => [k, S.L[k]])); for (const k of figli(g)) S.L[k] = 0; }
  syncChecks(); update(); });
document.querySelectorAll('[data-gt]').forEach(b => b.onclick = () => { const d = b.closest('.grp'), o = d.classList.toggle('open'); b.setAttribute('aria-expanded', o); });
document.querySelectorAll('[data-ct]').forEach(i => i.onchange = () => { S.CT[i.checked ? 'add' : 'delete'](i.dataset.ct); categorie(); update(); });
document.querySelectorAll('[data-f]').forEach(i => i.onchange = () => { S.F[i.dataset.f] = i.checked ? 1 : 0; categorie(); update(); });
/* faccette, «i» e legenda: un solo ascoltatore sul pannello e sulla mappa */
document.addEventListener('click', e => {
  const sc = e.target.closest('[data-scorri]'); if (sc) { e.preventDefault(); document.getElementById(sc.dataset.scorri).scrollIntoView({behavior: RIDOTTO.matches ? 'auto' : 'smooth', block: 'start'}); return; }
  const b = e.target.closest('[data-fac]'); if (b) { const k = b.dataset.fac, v = b.dataset.v; CAT[k] = CAT[k] === v ? '' : v; update(); return; }
  const a = e.target.closest('[data-facapri]'); if (a) { FAC_APERTA[a.dataset.facapri] = !FAC_APERTA[a.dataset.facapri]; renderFacette(); return; }
  const inf = e.target.closest('[data-infoper]'); if (inf) { e.preventDefault(); e.stopPropagation(); const n = document.getElementById(inf.dataset.infoper), o = n.hidden; n.hidden = !o; inf.setAttribute('aria-expanded', o); }
}, true);
$('#cop').onclick = e => { if (!e.target.closest('a')) { const c = $('#cop'); c.classList.toggle('aperta'); c.title = c.classList.contains('aperta') ? '' : 'clic per leggere tutto'; } };
$('#legbtn').onclick = () => { LEG_APERTA = !LEG_APERTA; $('#legbody').hidden = !LEG_APERTA; $('#legbtn').setAttribute('aria-expanded', LEG_APERTA); };
/* «i» per livello: la riga resta nome + interruttore + conteggio; fonte, metodo e limiti si aprono a richiesta. */
function infoLivelli() {
  let n = 0;
  document.querySelectorAll('#lay label.chk').forEach(l => {
    const sm = l.querySelector('small'), sp = l.querySelector('span'); if (!sp) return;
    const cnt = document.createElement('span'); cnt.className = 'cnt'; cnt.setAttribute('aria-label', 'quanti in questa finestra');
    if (!sm) { sp.after(cnt); return; }
    const id = 'nota-' + (++n); sm.id = id; sm.hidden = true; sm.classList.add('nota');
    const b = document.createElement('button'); b.className = 'info'; b.textContent = 'i'; b.dataset.infoper = id; b.setAttribute('aria-expanded', 'false');
    b.setAttribute('aria-label', 'Che cosa mostra: ' + sp.firstChild.textContent.trim());
    sp.after(cnt, b); b.after(sm);
  });
  document.querySelectorAll('.shead').forEach(h => { if (!h.querySelector('.cnt')) { const c = document.createElement('span'); c.className = 'cnt'; h.append(c); } });
}
for (const p of ['globo', 'piano']) $('#p-' + p).onclick = () => { S.proj = p; S.k = 1; $('#p-globo').setAttribute('aria-pressed', p === 'globo'); $('#p-piano').setAttribute('aria-pressed', p === 'piano'); draw(); };
let qt; $('#q').oninput = e => { clearTimeout(qt); qt = setTimeout(() => { S.q = e.target.value.trim(); update(); }, 180); };
$('#win').value = String(S.win);
$('#corsie').onchange = e => { S.corsie = e.target.value; drawTl(); };
function update() { if (!O.length) return; document.querySelectorAll('[data-win]').forEach(b => b.setAttribute('aria-pressed', b.dataset.win === 'tutto' ? S.win >= (T1 - T0) / 2 : +b.dataset.win === S.win)); const ws = $('#win'); if (![...ws.options].some(o => +o.value === S.win)) ws.add(new Option(String(S.win))); ws.value = String(S.win); filtra(); segnaposto(); draw(); drawTl(); if (S.mode === 'ricerca') renderCtx(); renderTavCount(); renderFacette(); renderConteggi(); renderLegenda(); if (S.mode === 'ricerca') sezNominato(); }
const renderTavCount = () => { $('#tavn').textContent = S.tav.length; };
new MutationObserver(() => { draw(); drawTl(); }).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});

/* ── Guida: visita dell'interfaccia e domande da provare ─────────────────────────────
   La visita evidenzia una zona alla volta; le domande impostano da sole la vista che risponde.
   Si apre da sola alla prima visita (se il browser lo permette) e sempre dal pulsante «Guida». */
/* Vista condivisibile: modo, anno, finestra, rotazione, livelli, tipi, corsie, scheda aperta, tappa.
   Scritta nell'indirizzo solo quando serve (commenti, link); letta una volta all'apertura. */
function vistaURL() {
  const r = S.rot.map(x => Math.round(x)).join(','), l = [...Object.keys(S.L).filter(k => S.L[k]), ...(S.L.opere ? [] : ['nofilo'])].join(',');
  let h = `${S.mode}&y=${S.year}&w=${S.win}&r=${r}&l=${l}&ct=${[...S.CT].join(',')}&c=${S.corsie || ''}`;
  if (S.place) h += '&p=' + encodeURIComponent(S.place);
  if (S.sel) h += '&s=' + encodeURIComponent(S.sel);
  for (const [k, p] of [['reg', 'cr'], ['tipo', 'ct2'], ['ctx', 'cx']]) if (CAT[k]) h += `&${p}=${encodeURIComponent(CAT[k])}`;
  if (S.mode === 'percorso') h += '&t=' + S.tappa;
  return location.origin + location.pathname + (PRIMO ? '' : '?filo=' + FILO) + '#' + h;
}
/* Incorpora: la vista attuale dentro un'altra pagina (un museo, un partner). Solo globo e tempo,
   con il link alla vista completa: chi incorpora mostra, ArMoni resta la fonte. */
const INCORPORATA = new URLSearchParams(location.search).get('incorpora') === '1';
if (INCORPORATA) { document.body.classList.add('incorpora'); $('#apri-intera').onclick = e => { e.preventDefault(); window.open(vistaURL().replace(/[?&]incorpora=1/, ''), '_blank', 'noopener'); }; }
function codiceIncorpora() {
  const u = new URL(vistaURL()); u.searchParams.set('incorpora', '1');
  return `<iframe src="${u.href}" title="ArMoni · Atlante" width="100%" height="560" style="border:1px solid #dde1ec;border-radius:8px" loading="lazy"></iframe>`;
}
$('#incorporabtn').onclick = () => { $('#inc-codice').value = codiceIncorpora(); $('#inc-dlg').showModal(); $('#inc-codice').select(); };
$('#inc-copia').onclick = async () => { try { await navigator.clipboard.writeText($('#inc-codice').value); $('#inc-copia').textContent = 'Copiato'; } catch (e) { $('#inc-codice').select(); document.execCommand('copy'); $('#inc-copia').textContent = 'Copiato'; } setTimeout(() => { $('#inc-copia').textContent = 'Copia il codice'; }, 1800); };
function leggiVista() {
  const q = new URLSearchParams(location.hash.slice(1).split('&').slice(1).join('&'));
  if (!q.has('y')) return;
  const n = (k, d) => Number.isFinite(+q.get(k)) && q.get(k) !== '' ? +q.get(k) : d;
  S.year = n('y', S.year); S.win = n('w', S.win);
  const r = (q.get('r') || '').split(',').map(Number); if (r.length === 2 && r.every(Number.isFinite)) S.rot = r;
  if (q.has('l')) { const on = new Set(q.get('l').split(',')); for (const k of Object.keys(S.L)) S.L[k] = on.has(k) ? 1 : 0;
    S.L.opere = on.has('nofilo') ? 0 : 1; }  // le viste salvate prima dei due strumenti avevano sempre il filo acceso
  for (const [k, p] of [['reg', 'cr'], ['tipo', 'ct2'], ['ctx', 'cx']]) if (q.get(p)) CAT[k] = q.get(p);
  if (q.get('ct')) { S.CT = new Set(q.get('ct').split(',').filter(t => TIPI_CX.includes(t))); document.querySelectorAll('[data-ct]').forEach(i => { i.checked = S.CT.has(i.dataset.ct); }); }
  if (q.get('c')) { S.corsie = q.get('c'); $('#corsie').value = S.corsie; }
  if (q.get('p')) S.place = q.get('p');
  S.sel = q.get('s') || null;
  if (q.has('t')) S.tappa = Math.max(0, Math.min(TAPPE.length - 1, n('t', 0)));
}
const MODULO = 'https://tally.so/r/Z92Jpz';
$('#commentabtn').onclick = () => window.open(`${MODULO}?vista=${encodeURIComponent(vistaURL())}&schermo=${innerWidth}x${innerHeight}`, '_blank', 'noopener');

const VISITA = [
  {s: 'header .seg', t: 'Tre modi di usare l\'atlante', p: '<b>Ricerca</b>: esplori liberamente, scegliendo anno, luoghi e livelli. <b>Percorso</b>: un racconto in tappe, con le fonti di ogni frase. <b>Affidabilità</b>: che cosa sanno i dati, e dove tacciono.'},
  {s: '#fig', t: 'Il globo', p: 'Trascina per ruotarlo; per avvicinarti usa + e −, oppure la rotella, che ingrandisce verso il punto sotto il cursore. Più ti avvicini, più coste e confini diventano dettagliati. Un clic su un segno apre la sua scheda a destra. <b>Cerchi e nomi blu</b>: pezzi per luogo d\'origine (pieno: città; anello: solo il paese). <b>Rombi rossi</b>: quantità al V&amp;A. <b>Triangoli</b>: scavi archeologici. <b>Quadratini pieni</b>: musei di oggi. <b>Quadrati e nomi in corsivo verdi</b>: stili, movimenti, scuole, dinastie. Un <b>alone</b> che pulsa piano mostra quanto è grande ciò che ha un\'estensione: un paese, una regione.'},
  {s: '#tl', t: 'Il tempo', p: 'Clicca o trascina sulla barra per scegliere l\'anno; con «finestra ±» decidi quanti anni guardare insieme; «Scorri» fa avanzare il tempo da solo. Sotto, le <b>corsie</b>: chi divide il tempo e come lo chiama (PeriodO), le dinastie, i fenomeni artistici per regione.'},
  {s: '#lay', t: 'Due strumenti e uno sfondo', p: 'In alto i due strumenti di contenuto: il <b>filo</b> (gli oggetti di un tema, in blu, con la ricerca per provenienza e tipo) e i <b>contesti</b> (stili, movimenti, scuole, dinastie, in verde). Si accendono da soli o insieme: i contesti senza filo sono una ricerca a sé. Sovrapposti <b>accostano</b>, non collegano: le relazioni compaiono solo dove una fonte le dichiara. Sotto, lo sfondo comune: confini storici e silenzio delle fonti.'},
  {s: '#ctx', t: 'Il pannello di destra', p: 'Senza nulla di scelto, riassume la finestra: quanti pezzi, da dove, quali fenomeni, chi nomina quegli anni. Con un luogo o una voce scelti, mostra la scheda: ogni dato con la sua fonte e il suo grado di certezza. «Indietro» torna al riassunto.'},
  {s: '#q', t: 'Cerca', p: 'Filtra opere e fenomeni per parola: un titolo, una cultura, una tecnica, un nome.'},
  {s: '#tavbtn', t: 'Il Tavolo', p: 'Dalla scheda di un pezzo puoi metterlo sul Tavolo, per tenere insieme cose lontane e confrontarle. Il Tavolo resta in questo browser.'},
  {s: null, t: 'Un principio, per leggere tutto il resto', p: 'L\'atlante non decide che cosa è vero: riporta che cosa dice ogni fonte, con quale certezza, e mostra dove le fonti tacciono. Un vuoto sulla mappa può essere un vuoto della storia o un vuoto dei dati: la vista Affidabilità aiuta a distinguerli.'},
];
const DOMANDE = [
  {t: 'Da dove arriva la porcellana blu e bianca che oggi sta nei musei, intorno al 1640?', y: 1640, w: 25, rot: [-60, -30], L: {origini: 1, sedi: 1, spostamenti: 1, mercati: 1}},
  {t: 'Che cosa succedeva nell\'arte, nel mondo, mentre Delft imitava la porcellana cinese?', y: 1650, w: 25, rot: [-40, -35], L: {origini: 1, contesti: 1}},
  {t: 'Quali dinastie regnavano in Asia nel 1450?', y: 1450, w: 10, rot: [-90, -25], L: {contesti: 1}, CT: ['periodizzazione'], corsie: 'contesti'},
  {t: 'Che cosa viene prima e dopo la dinastia Song, secondo le fonti?', y: 980, w: 40, rot: [-110, -32], L: {contesti: 1, relazioni: 1}, CT: ['periodizzazione'], place: 'mov:Q7462'},
  {t: 'Chi decide come si chiama un\'epoca? Il 1500, nominato da storici diversi', y: 1500, w: 25, rot: [-60, -30], L: {origini: 1}, corsie: 'periodo'},
  {t: 'Dove gli scavi hanno trovato porcellana cinese, lontano dalla Cina?', y: 1450, w: 100, rot: [-40, 0], L: {letteratura: 1}},
  {t: 'Quanto sono affidabili questi dati, e dove tacciono?', modo: '#qualita'},
  {t: 'Preferisco un racconto guidato, tappa per tappa', modo: '#percorso'},
];
function vai(d) {
  chiudiGuida();
  if (d.modo) { location.hash = d.modo; return; }
  Lr = null; if (location.hash !== '#ricerca') location.hash = '#ricerca';
  S.year = d.y; S.win = d.w; S.rot = [...d.rot]; S.k = 1; S.sel = null; S.place = d.place || null;
  S.L = {opere: 1, periodi: 0, confini: 1, origini: 0, sedi: 0, spostamenti: 0, mercati: 0, silenzio: 0, ipotetici: 1, dedotti: 0, vam: 0, letteratura: 0, contesti: 0, relazioni: 0, ...d.L};
  S.CT = new Set(d.CT || TIPI_CX); document.querySelectorAll('[data-ct]').forEach(i => { i.checked = S.CT.has(i.dataset.ct); });
  if (d.corsie) { S.corsie = d.corsie; $('#corsie').value = d.corsie; S.L.periodi = 1; syncChecks?.(); }
  G.on = {}; G.mem = {}; syncChecks(); update();
}
const gd = document.createElement('div'); gd.id = 'guida'; gd.hidden = true; document.body.appendChild(gd);
let passo = 0, ultimoFuoco = null;
function chiudiGuida() { gd.hidden = true; gd.innerHTML = ''; ultimoFuoco?.focus(); }
function apriGuida(scheda = 'visita') {
  ultimoFuoco = document.activeElement; gd.hidden = false;
  if (scheda === 'visita' && location.hash === '#qualita') location.hash = '#ricerca';
  scheda === 'visita' ? mostraPasso() : mostraDomande();
}
function cornice(corpo) {
  gd.innerHTML = `<div class="gd-ombra"></div><div class="gd-luce" hidden></div><div class="gd-card" role="dialog" aria-modal="true" aria-labelledby="gd-t">
    <div class="gd-tabs" role="tablist"><button role="tab" data-gs="visita">Come si usa</button><button role="tab" data-gs="domande">Domande da provare</button><button class="gd-x" data-gx aria-label="Chiudi la guida">×</button></div>${corpo}</div>`;
  gd.querySelectorAll('[data-gs]').forEach(b => b.onclick = () => { passo = 0; b.dataset.gs === 'visita' ? mostraPasso() : mostraDomande(); });
  gd.querySelector('[data-gx]').onclick = chiudiGuida;
}
function mostraPasso() {
  const v = VISITA[passo];
  cornice(`<div class="gd-step">${passo + 1} di ${VISITA.length}</div><h2 id="gd-t">${v.t}</h2><p>${v.p}</p>
    <div class="acts"><button data-gp="-1" ${passo ? '' : 'disabled'}>← Indietro</button>${passo < VISITA.length - 1 ? '<button data-gp="1" class="pri">Avanti →</button>' : '<button data-gd class="pri">Prova una domanda →</button>'}</div>`);
  gd.querySelector('[data-gs="visita"]').setAttribute('aria-selected', 'true');
  gd.querySelectorAll('[data-gp]').forEach(b => b.onclick = () => { passo += +b.dataset.gp; mostraPasso(); });
  gd.querySelector('[data-gd]')?.addEventListener('click', mostraDomande);
  const luce = gd.querySelector('.gd-luce'), el = v.s && document.querySelector(v.s), card = gd.querySelector('.gd-card');
  if (el && el.offsetParent !== null) {
    el.scrollIntoView({block: 'nearest'}); const r = el.getBoundingClientRect();
    Object.assign(luce.style, {left: r.left - 4 + 'px', top: r.top - 4 + 'px', width: r.width + 8 + 'px', height: r.height + 8 + 'px'}); luce.hidden = false;
    gd.querySelector('.gd-ombra').hidden = true;
    // la scheda della guida si mette dal lato opposto alla zona evidenziata
    card.classList.toggle('in-alto', r.top + r.height / 2 > innerHeight / 2);
  }
  card.querySelector('.pri, [data-gp]')?.focus();
}
function mostraDomande() {
  cornice(`<h2 id="gd-t">Domande da provare</h2><p class="sub">Ogni domanda imposta da sola anno, luogo e livelli. Poi la vista è tua: cambiala come vuoi.</p>
    <div class="gd-dom">${DOMANDE.map((d, i) => `<button data-gq="${i}">${esc(d.t)}</button>`).join('')}</div>`);
  gd.querySelector('[data-gs="domande"]').setAttribute('aria-selected', 'true');
  gd.querySelectorAll('[data-gq]').forEach(b => b.onclick = () => vai(DOMANDE[+b.dataset.gq]));
  gd.querySelector('[data-gq]').focus();
}
document.addEventListener('keydown', e => { if (e.key === 'Escape' && !gd.hidden) chiudiGuida(); });
gd.addEventListener('keydown', e => {
  if (e.key === 'Tab') { const f = [...gd.querySelectorAll('button:not([disabled])')]; const i = f.indexOf(document.activeElement);
    if (e.shiftKey && i <= 0) { f.at(-1).focus(); e.preventDefault(); } else if (!e.shiftKey && i === f.length - 1) { f[0].focus(); e.preventDefault(); } }
});
$('#guidabtn').onclick = () => apriGuida();
addEventListener('resize', () => { if (!gd.hidden && gd.querySelector('.gd-step')) mostraPasso(); });
// chi arriva da una vista condivisa la vede subito, senza la guida davanti
try { if (!location.hash.includes('&y=') && !localStorage.getItem('armoni-guida-vista')) { localStorage.setItem('armoni-guida-vista', '1'); setTimeout(() => apriGuida(), 900); } } catch (e) { /* senza memoria del browser la guida resta sul pulsante */ }
$('#filo').value = FILO;
$('#filo').onchange = e => { const f = e.target.value; location.href = location.pathname + (f === 'blu' ? '' : '?filo=' + f) + '#ricerca'; };
}
