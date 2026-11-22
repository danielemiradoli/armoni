{
const $ = s => document.querySelector(s);
const probe = document.createElement('i'); probe.style.display = 'none'; document.body.appendChild(probe);
const css = v => { probe.style.color = `var(${v})`; return getComputedStyle(probe).color; };
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmtY = y => y < 0 ? `${-y} a.C.` : String(y);
const PREC = {citta: 'città', paese: 'solo paese', regione: 'regione', zona: 'zona', istituzione: 'istituzione'};
const T0 = 700, T1 = 2000;

const S = {corsie: 'wikidata', year: 1640, win: 25, proj: 'globo', rot: [-40, -28], k: 1, sel: null, place: null, q: '',
  L: {confini: 1, origini: 1, sedi: 1, spostamenti: 0, mercati: 1, silenzio: 0, ipotetici: 1, dedotti: 0, vam: 1, letteratura: 1, contesti: 0, relazioni: 0}, CT: new Set(['movimento', 'scuola', 'stile', 'periodizzazione']), F: {met: 1, cma: 1, wd: 1, colbase: 1},
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
Promise.all([j('opere.json'), j('luoghi.json'), j('periodi.json'), j('confini/anni.json'), j('terre.json'), j('densita_vam.json').catch(() => null), j('periodo.json').catch(() => null), j('letteratura.json').catch(() => null), j('qualita.json').catch(() => null), j('contesti.json').catch(() => null)]).then(([o, l, p, a, t, v, po, le, qu, cx]) => {
  QU = qu;
  if (cx) { CXR = cx; CX = cx.elementi.map(e => ({...e, fv: e.quando.a ?? e.quando.da + APERTO})); }
  LET = le; if (LET) for (const x of LET.siti) LU['sito:' + x.id] = {...x, lat: +x.lat, lon: +x.lon};
  PO = po; if (PO) S.corsie = 'periodo';
  for (const x of l) LU[x.id] = {...x, lat: +x.lat, lon: +x.lon};
  if (v) { VAM = v; for (const x of v.luoghi) if (!LU[x.id]) LU[x.id] = {...x, lat: +x.lat, lon: +x.lon}; }
  NOD = o.filter(x => x.inizio == null);
  O = o.filter(x => x.inizio != null).map(x => ({...x, o: LU[x.origine], s: LU[x.sede], m: LU[x.mercato],
    hay: (x.titolo + ' ' + x.cultura + ' ' + x.tecnica).toLowerCase()}));
  PER = p.map(x => ({...x, inizio: +x.inizio, fine: +x.fine}));
  ANNI = a; if (PO) $('#corsie').value = 'periodo'; TERRE = topojson.feature(t, t.objects.land);
  try { S.tav = JSON.parse(localStorage.getItem('armoni-tavolo') || '[]').filter(c => O.some(x => x.id === c.id)); } catch (e) { S.tav = []; }
  route(); update();
}).catch(e => { $('#ctx').innerHTML = `<p>Non riesco a caricare i dati (${esc(e.message)}).</p>`; });

function confini(y) {
  const a = ANNI.filter(v => v <= y).pop() ?? ANNI[0];
  if (!CONF[a]) { CONF[a] = 'caricamento'; j(`confini/${a}.json`).then(t => { const k = Object.keys(t.objects)[0]; CONF[a] = topojson.feature(t, t.objects[k]); draw(); }).catch(() => { CONF[a] = null; }); }
  return {anno: a, geo: CONF[a] && CONF[a] !== 'caricamento' ? CONF[a] : null};
}

// luogo dichiarato; quello dedotto solo se lo strato e' acceso, e mai al posto del dichiarato
const luogo = x => x.o ? x.origine : S.L.dedotti && LU[x.origine_dedotta] ? x.origine_dedotta : null;
function filtra() {
  const q = S.q.toLowerCase();
  act = O.filter(x => x.inizio <= S.year + S.win && x.fine >= S.year - S.win && S.F[x.fonte] &&
    (S.L.ipotetici || x.grado === 'documentato') && (!q || x.hay.includes(q)));
  const m = new Map();
  for (const x of act) { const id = luogo(x); if (!id) continue; const g = m.get(id) || {id, l: LU[id], n: 0, doc: 0, inc: 0, ded: 0}; g.n++; if (x.grado === 'documentato') g.doc++; if (x.origine_incerta) g.inc++; if (!x.o) g.ded++; m.set(id, g); }
  agg = [...m.values()].sort((a, b) => b.n - a.n);
  const vm = new Map();
  if (VAM) for (const c of VAM.celle) if (c.d + 9 >= S.year - S.win && c.d <= S.year + S.win) vm.set(c.l, (vm.get(c.l) || 0) + c.n);
  const lm = new Map(); if (LET) for (const a of LET.asserzioni) if (a.fine >= S.year - S.win && a.inizio <= S.year + S.win) { const k = 'sito:' + a.sito_id; lm.set(k, [...(lm.get(k) || []), a]); }
  lagg = [...lm].map(([id, as]) => ({id, l: LU[id], as, n: as.length}));
  vagg = [...vm].map(([id, n]) => ({id, l: LU[id], n})).filter(g => g.n >= .5).sort((a, b) => b.n - a.n);
  cagg = S.L.contesti ? CX.filter(e => S.CT.has(e.tipo) && e.quando.da <= S.year + S.win && e.fv >= S.year - S.win && (!q || (e.nome + ' ' + (e.nome_en || '')).toLowerCase().includes(q))) : [];
}

/* ---------- mappa ---------- */
const cv = $('#cv'), ctx = cv.getContext('2d'), fig = $('#fig');
let W = 0, H = 0, proj, path;
function setProj() {
  const R = Math.min(W, H) * 0.46;
  proj = S.proj === 'globo' ? d3.geoOrthographic().rotate(S.rot).scale(R * S.k).translate([W / 2, H / 2]).clipAngle(90)
    : d3.geoEqualEarth().rotate([S.rot[0], 0]).fitExtent([[12, 12], [W - 12, H - 12]], {type: 'Sphere'});
  if (S.proj !== 'globo') proj.scale(proj.scale() * S.k);
  path = d3.geoPath(proj, ctx);
}
const visibile = c => S.proj !== 'globo' || d3.geoDistance(c, [-S.rot[0], -S.rot[1]]) < Math.PI / 2;
const rr = g => g.l.precisione === 'citta' ? 2.5 + Math.sqrt(g.n) * 1.5 : 6 + Math.sqrt(g.n) * 2.1;

function draw() {
  if (!W) return;
  setProj();
  const co = css('--co'), fe = css('--fe'), ink = css('--ink'), mute = css('--mute');
  ctx.clearRect(0, 0, W, H);
  ctx.beginPath(); path({type: 'Sphere'}); ctx.fillStyle = css('--glaze'); ctx.fill();
  ctx.lineWidth = 1.2; ctx.strokeStyle = co; ctx.globalAlpha = .55; ctx.stroke(); ctx.globalAlpha = 1;
  ctx.beginPath(); path(d3.geoGraticule10()); ctx.strokeStyle = co; ctx.globalAlpha = .08; ctx.lineWidth = .6; ctx.stroke();
  ctx.beginPath(); path(TERRE); ctx.fillStyle = co; ctx.globalAlpha = .1; ctx.fill(); ctx.globalAlpha = 1;
  const cf = confini(S.year);
  if (S.L.confini && cf.geo) { ctx.beginPath(); path(cf.geo); ctx.strokeStyle = co; ctx.globalAlpha = .42; ctx.lineWidth = .7; ctx.stroke(); ctx.globalAlpha = 1; }
  const hi = S.mode === 'percorso' ? new Set(TAPPE[S.tappa].hi) : null;
  if (S.L.spostamenti) {
    const m = new Map(); for (const x of act) if (x.o && x.s) { const k = x.origine + '>' + x.sede; m.set(k, (m.get(k) || 0) + 1); }
    for (const [k, n] of m) { const [a, b] = k.split('>'); ctx.beginPath(); path({type: 'LineString', coordinates: [[LU[a].lon, LU[a].lat], [LU[b].lon, LU[b].lat]]}); ctx.strokeStyle = co; ctx.globalAlpha = Math.min(.5, .06 + n / 120); ctx.lineWidth = 1 + Math.sqrt(n) / 3; ctx.stroke(); }
    ctx.globalAlpha = 1;
  }
  if (S.L.mercati) for (const x of act) if (x.m && x.o) { ctx.beginPath(); path({type: 'LineString', coordinates: [[x.o.lon, x.o.lat], [x.m.lon, x.m.lat]]}); ctx.strokeStyle = fe; ctx.setLineDash([4, 3]); ctx.lineWidth = 1.4; ctx.stroke(); ctx.setLineDash([]); }
  if (S.L.origini) for (const g of agg) {
    const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = proj(c), r = rr(g);
    const dim = hi && hi.size && !hi.has(g.id) ? .25 : 1;
    ctx.globalAlpha = dim; ctx.beginPath(); ctx.arc(x, y, r, 0, 7);
    if (g.l.precisione === 'citta') { ctx.fillStyle = co; ctx.globalAlpha = dim * (.35 + .6 * g.doc / g.n); ctx.fill(); }
    else { ctx.fillStyle = co; ctx.globalAlpha = dim * .12; ctx.fill(); ctx.globalAlpha = dim; ctx.setLineDash([3, 3]); ctx.strokeStyle = co; ctx.lineWidth = 1.2; ctx.stroke(); ctx.setLineDash([]); }
    if (g.inc) { ctx.beginPath(); ctx.arc(x, y, r + 3, 0, 7); ctx.setLineDash([1, 3]); ctx.strokeStyle = ink; ctx.globalAlpha = dim * .7; ctx.stroke(); ctx.setLineDash([]); }
    if (S.L.silenzio && g.l.precisione !== 'citta') { ctx.beginPath(); ctx.arc(x, y, r + 16, 0, 7); ctx.fillStyle = mute; ctx.globalAlpha = .1; ctx.fill(); }
    if (S.place === g.id) { ctx.beginPath(); ctx.arc(x, y, r + 5, 0, 7); ctx.strokeStyle = fe; ctx.globalAlpha = 1; ctx.lineWidth = 2; ctx.stroke(); }
    ctx.globalAlpha = 1;
    if (r > (W < 520 ? 15 : 9) || (hi && hi.has(g.id))) { ctx.font = '12px "Instrument Sans",sans-serif'; ctx.fillStyle = ink; ctx.fillText(g.l.nome, x + r + 4, y + 4); }
  }
  if (S.L.vam) for (const g of vagg) {
    const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = proj(c), r = 3 + Math.sqrt(g.n) * 1.3;
    ctx.beginPath(); ctx.moveTo(x, y - r); ctx.lineTo(x + r, y); ctx.lineTo(x, y + r); ctx.lineTo(x - r, y); ctx.closePath();
    ctx.strokeStyle = fe; ctx.globalAlpha = .75; ctx.lineWidth = 1.1; ctx.stroke(); ctx.globalAlpha = 1;
  }
  if (S.L.letteratura) for (const g of lagg) {
    const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = proj(c), r = 7;
    ctx.beginPath(); ctx.moveTo(x, y - r); ctx.lineTo(x + r * .9, y + r * .6); ctx.lineTo(x - r * .9, y + r * .6); ctx.closePath();
    ctx.fillStyle = ink; ctx.globalAlpha = .85; ctx.fill(); ctx.globalAlpha = 1;
    ctx.font = '12px "Instrument Sans",sans-serif'; ctx.fillStyle = ink; ctx.fillText(g.l.nome, x + 10, y + 4);
  }
  if (S.L.contesti) drawContesti(ink, mute);
  if (S.L.sedi) for (const k of new Set(act.map(x => x.sede).filter(Boolean))) {
    const l = LU[k]; if (!l || !visibile([l.lon, l.lat])) continue; const [x, y] = proj([l.lon, l.lat]);
    ctx.fillStyle = ink; ctx.fillRect(x - 4, y - 4, 8, 8);
  }
  const sel = O.find(x => x.id === S.sel);
  if (sel && sel.o && visibile([sel.o.lon, sel.o.lat])) { const [x, y] = proj([sel.o.lon, sel.o.lat]); ctx.beginPath(); ctx.arc(x, y, 11, 0, 7); ctx.strokeStyle = fe; ctx.lineWidth = 2.5; ctx.stroke(); }
  chip(cf.anno);
}

/* Stili e movimenti: quadrati vuoti (luogo), quadrati tratteggiati più grandi (paese), solo nome in corsivo (regione).
   Nomi scritti per i più noti (versioni linguistiche su Wikidata), senza sovrapporsi. */
function drawContesti(ink, mute) {
  const occ = [], sel = S.place && S.place.startsWith('mov:') ? S.place.slice(4) : null;
  // relazioni dichiarate: fra voci attive se il livello è acceso; quelle della voce scelta sempre, anche fuori finestra
  const att = new Map(cagg.map(e => [e.id, e])), tutte = new Map(CX.map(e => [e.id, e]));
  const linea = (a, b, forte) => { const p = a.luoghi[0], q = b.luoghi[0]; if (p.id === q.id) return; ctx.beginPath(); path({type: 'LineString', coordinates: [[p.lon, p.lat], [q.lon, q.lat]]});
    ctx.strokeStyle = ink; ctx.globalAlpha = forte ? .85 : .35; ctx.lineWidth = forte ? 1.6 : .9; ctx.setLineDash([1, 3]); ctx.stroke(); ctx.setLineDash([]); ctx.globalAlpha = 1; };
  if (S.L.relazioni) for (const e of cagg) for (const r of e.relazioni) if (r.verso === '>' && att.has(r.id)) linea(e, att.get(r.id), false);
  if (sel && tutte.has(sel)) for (const r of tutte.get(sel).relazioni) if (r.collocata && tutte.has(r.id)) linea(tutte.get(sel), tutte.get(r.id), true);
  ctx.font = 'italic 500 13px Newsreader,Georgia,serif';
  for (const e of cagg) for (const l of e.luoghi) {
    const c = [l.lon, l.lat]; if (!visibile(c)) continue; const [x, y] = proj(c), r = l.precisione === 'paese' ? 7 : 4.5;
    ctx.strokeStyle = ink; ctx.lineWidth = e.id === sel ? 2.2 : 1; ctx.globalAlpha = e.id === sel ? 1 : .7;
    if (l.precisione !== 'regione') { if (l.precisione === 'paese') ctx.setLineDash([2, 2]); ctx.strokeRect(x - r, y - r, 2 * r, 2 * r); ctx.setLineDash([]); }
    const t = e.nome, w = ctx.measureText(t).width, bx = [x + r + 3, y - 9, x + r + 3 + w, y + 4];
    if (e.id === sel || (occ.length < (W < 520 ? 6 : 18) && !occ.some(o => bx[0] < o[2] && bx[2] > o[0] && bx[1] < o[3] && bx[3] > o[1]))) {
      occ.push(bx); ctx.fillStyle = ink; ctx.globalAlpha = e.id === sel ? 1 : .8; ctx.fillText(t, bx[0], y + 3); }
    ctx.globalAlpha = 1;
  }
}
function chip(anno) {
  const n = act.length, paese = act.filter(x => x.o && x.o.precisione !== 'citta').length, ipo = act.filter(x => x.grado === 'ipotetico').length;
  let h = `<b>${n}</b> pezzi attivi · confini del ${fmtY(anno)}`;
  if (S.L.silenzio && n) { const us = act.filter(x => x.fonte === 'met' || x.fonte === 'cma').length, sedi = new Set(act.map(x => x.sede).filter(Boolean)).size, pu = 100 * us / n;
    if (VAM && S.L.vam) { const tv = vagg.reduce((a, g) => a + g.n, 0), cv = vagg.filter(g => g.l.precisione === 'citta').reduce((a, g) => a + g.n, 0); h += `<br>V&A (rombi, tutti conservati a Londra): ~${Math.round(tv)} pezzi, ${tv ? Math.round(100 * cv / tv) : 0}% localizzati per città`; }
    h += `<br>${Math.round(100 * paese / n)}% localizzati solo per paese · ${ipo} ipotetici · ${act.filter(x => !x.o).length} senza luogo<br>${sedi} sedi di conservazione · ${pu > 99 && pu < 100 ? pu.toFixed(1) : Math.round(pu)}% delle schede negli Stati Uniti<br>${NOD.filter(x => S.F[x.fonte]).length} pezzi senza data: esistono nei dati, non nel tempo`; }
  if (S.L.contesti) h += `<br>${cagg.length} fenomeni artistici in questa finestra (quadrati e nomi in corsivo)`;
  $('#chip').innerHTML = h;
}

function hit(px, py) {
  let best = null, bd = 1e9;
  for (const g of agg) { const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = proj(c), d = Math.hypot(x - px, y - py); if (d < rr(g) + 5 && d < bd) { bd = d; best = g; } }
  if (!best && S.L.letteratura) for (const g of lagg) { const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = proj(c), d = Math.hypot(x - px, y - py); if (d < 11 && d < bd) { bd = d; best = {...g, let: true}; } }
  if (!best && S.L.vam) for (const g of vagg) { const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = proj(c), d = Math.hypot(x - px, y - py); if (d < 3 + Math.sqrt(g.n) * 1.3 + 4 && d < bd) { bd = d; best = {...g, vam: true}; } }
  if (!best && S.L.contesti) for (const e of cagg) for (const l of e.luoghi) { const c = [l.lon, l.lat]; if (!visibile(c)) continue; const [x, y] = proj(c), d = Math.hypot(x - px, y - py); if (d < 10 && d < bd) { bd = d; best = {id: 'mov:' + e.id, e, l, mov: true}; } }
  return best;
}

let drag = null;
cv.addEventListener('pointerdown', e => { drag = {x: e.clientX, y: e.clientY, r: [...S.rot], moved: 0}; cv.setPointerCapture(e.pointerId); });
cv.addEventListener('pointermove', e => {
  const b = cv.getBoundingClientRect();
  if (drag) { const dx = e.clientX - drag.x, dy = e.clientY - drag.y; drag.moved = Math.max(drag.moved, Math.abs(dx) + Math.abs(dy));
    const f = 0.25 / S.k; S.rot = [drag.r[0] + dx * f, Math.max(-90, Math.min(90, drag.r[1] - dy * f))]; draw(); return; }
  const g = hit(e.clientX - b.left, e.clientY - b.top), tip = $('#tip');
  let pol = '';
  if (!g && S.L.confini) { const c = proj.invert([e.clientX - b.left, e.clientY - b.top]), cf = confini(S.year); if (c && cf.geo) { const f = cf.geo.features.find(f => f.properties.NAME && d3.geoContains(f, c)); if (f) pol = f.properties.NAME; } }
  if (g || pol) { tip.style.display = 'block'; tip.style.left = (e.clientX - b.left + 14) + 'px'; tip.style.top = (e.clientY - b.top + 10) + 'px';
    tip.innerHTML = g && g.mov ? `<b>${esc(g.e.nome)}</b> · ${g.e.tipo}${g.e.sottotipo ? ' (' + g.e.sottotipo + ')' : ''}<br><span class="sub">${fmtY(g.e.quando.da)}–${g.e.quando.a != null ? fmtY(g.e.quando.a) : 'fine non dichiarata'} · ${esc(g.l.oggi)}</span>` : g && g.let ? `<b>${esc(g.l.nome)}</b> · ${g.n} dati dalla letteratura<br><span class="sub">sito archeologico: consumo, non produzione</span>` : g && g.vam ? `<b>${esc(g.l.nome)}</b> · V&A ~${Math.round(g.n)} pezzi<br><span class="sub">solo conteggio aggregato</span>` : g ? `<b>${esc(g.l.nome)}</b> · ${g.n} pezzi<br><span class="sub">${PREC[g.l.precisione]}${g.inc ? ' · ' + g.inc + ' attribuzioni incerte' : ''}${g.ded ? ' · ' + g.ded + ' con luogo dedotto' : ''}</span>` : `${esc(pol)}<br><span class="sub">confini del ${fmtY(confini(S.year).anno)}</span>`; }
  else tip.style.display = 'none';
});
cv.addEventListener('pointerup', e => {
  if (drag && drag.moved < 4) { const b = cv.getBoundingClientRect(), g = hit(e.clientX - b.left, e.clientY - b.top); S.place = g ? g.id : null; S.sel = null; if (S.mode === 'ricerca') renderCtx(); draw(); }
  drag = null;
});
cv.addEventListener('pointerleave', () => { $('#tip').style.display = 'none'; });
cv.addEventListener('wheel', e => { e.preventDefault(); zoom(e.deltaY < 0 ? 1.15 : 1 / 1.15); }, {passive: false});
const zoom = f => { S.k = Math.max(.7, Math.min(8, S.k * f)); draw(); };
$('#zin').onclick = () => zoom(1.3); $('#zout').onclick = () => zoom(1 / 1.3);
const misura = () => { const d = devicePixelRatio || 1; W = fig.clientWidth; H = fig.clientHeight; cv.width = W * d; cv.height = H * d; ctx.setTransform(d, 0, 0, d, 0, 0); draw(); };
const roMap = new ResizeObserver(misura);
roMap.observe(fig);

/* ---------- tempo ---------- */
const tls = $('#tls');
const dec = () => { const c = new Map(); for (const x of O) { if (!S.F[x.fonte] || (!S.L.ipotetici && x.grado !== 'documentato')) continue;
  for (let d = Math.max(T0, Math.floor(x.inizio / 10) * 10); d <= Math.min(T1, x.fine); d += 10) { const v = c.get(d) || [0, 0]; v[x.grado === 'documentato' ? 0 : 1] += 1 / (1 + (x.fine - x.inizio) / 10); c.set(d, v); } } return c; };
function drawTl() {
  const w = tls.clientWidth, lh = 12, top = 46, righe = [];
  if (S.corsie === 'periodo' && PO) return drawTlPO(w, {reg: REG_PO, periodi: PO.periodi, vuoto: 'nessun periodo in PeriodO',
    info: `corsie: quante definizioni di periodo PeriodO coprono ogni anno, per regione (il numero: quante valgono per l'anno scelto)`});
  if (S.corsie === 'contesti' && CX.length) return drawTlPO(w, corsieCX());
  for (const r of [...new Set(PER.map(p => p.regione))]) {  // periodi sovrapposti nella stessa regione vanno su sotto-corsie
    const sub = [];
    for (const p of PER.filter(p => p.regione === r).sort((a, b) => a.inizio - b.inizio)) { let k = sub.findIndex(f => f <= p.inizio); if (k < 0) { k = sub.length; sub.push(0); } sub[k] = p.fine; righe.push({r, k, p}); }
  }
  const nr = new Map(); let acc = 0; for (const x of righe) { const key = x.r + x.k; if (!nr.has(key)) nr.set(key, acc++); }
  const h = top + acc * (lh + 2) + 18;
  tls.style.height = h + 'px';
  const x = d3.scaleLinear([T0, T1], [0, w]), c = dec(), mx = Math.max(...[...c.values()].map(v => v[0] + v[1]), 1), y = v => 40 * v / mx;
  let s = '';
  for (const [d, [a, b]] of c) s += `<rect x="${x(d)}" y="${42 - y(a + b)}" width="${Math.max(1, x(d + 10) - x(d) - 1)}" height="${y(b)}" fill="var(--co)" opacity=".35"/><rect x="${x(d)}" y="${42 - y(a)}" width="${Math.max(1, x(d + 10) - x(d) - 1)}" height="${y(a)}" fill="var(--co)"/>`;
  if (VAM && S.L.vam) { const vd = new Map(); for (const c of VAM.celle) vd.set(c.d, (vd.get(c.d) || 0) + c.n); const vmx = Math.max(...vd.values(), 1);
    s += `<polyline fill="none" stroke="var(--fe)" stroke-width="1.4" points="${[...vd].filter(([d]) => d >= T0).sort((a, b) => a[0] - b[0]).map(([d, n]) => `${x(d + 5)},${42 - 40 * n / vmx}`).join(' ')}"/>`; }
  s += `<rect x="${x(S.year - S.win)}" y="0" width="${x(S.year + S.win) - x(S.year - S.win)}" height="${h - 16}" fill="var(--fe)" opacity=".08"/>`;
  for (const {r, k, p} of righe) { const yy = top + nr.get(r + k) * (lh + 2);
    if (w > 520 && k === 0 && righe.find(z => z.r === r).p === p) s += `<text x="2" y="${yy + 10}" font-size="10.5" fill="var(--mute)">${esc(r)}</text>`;
    { const x0 = Math.max(x(p.inizio), w > 520 ? 120 : 0), x1 = x(Math.min(p.fine, T1)); if (x1 <= x0) continue;
      s += `<g><title>${esc(p.nome)} ${p.inizio}–${p.fine} (Wikidata ${p.qid})</title><rect x="${x0}" y="${yy}" width="${x1 - x0}" height="${lh}" rx="2" fill="var(--co)" opacity=".16" stroke="var(--co)" stroke-opacity=".4"/>`;
      if (x1 - x0 > p.nome.length * 5.6) s += `<text x="${x0 + 4}" y="${yy + 9.5}" font-size="10" fill="var(--ink)">${esc(p.nome)}</text>`; s += '</g>'; } }
  for (let t = 800; t < T1; t += w < 520 ? 400 : 100) s += `<text x="${x(t)}" y="${h - 3}" font-size="10.5" fill="var(--mute)" text-anchor="middle">${t}</text>`;
  s += `<line x1="${x(S.year)}" x2="${x(S.year)}" y1="0" y2="${h - 14}" stroke="var(--fe)" stroke-width="2"/>`;
  tls.innerHTML = s;
  $('#yr').textContent = fmtY(S.year);
  const fuori = O.filter(o => o.fine < T0).length;
  $('#tlinfo').textContent = `istogramma: pezzi per decennio (scuro documentati, chiaro ipotetici${VAM && S.L.vam ? '; linea rossa: V&A, scala propria' : ''}) · corsie: periodi secondo Wikidata${fuori ? ` · ${fuori} pezzi prima del ${T0} fuori scala` : ''}`;
}
const REG_PO = ['Cina', 'Corea', 'Giappone', 'Sud-est asiatico', 'Iran e Asia centrale', 'Asia meridionale', 'Anatolia e Mediterraneo', 'Africa', 'Europa', 'Americhe'];
const LINGUE = {en: 'inglese', fr: 'francese', nl: 'olandese', ja: 'giapponese', tr: 'turco', de: 'tedesco', it: 'italiano', zh: 'cinese', es: 'spagnolo'};
// Corsie di densità: per ogni regione, quanti elementi coprono ogni anno (PeriodO, oppure stili e movimenti).
const ORD_CX = ['Asia orientale', 'Sud-Est asiatico', 'Asia meridionale', 'Asia centrale', 'Medio Oriente e Nord Africa', 'Africa subsahariana', 'Europa', 'Nord America', 'Mesoamerica e Caraibi', 'Sud America', 'Oceania'];
const regCX = () => [...ORD_CX, ...[...new Set(CX.map(e => e.corsia))].filter(r => !ORD_CX.includes(r)).sort()].filter(r => CX.some(e => e.corsia === r && S.CT.has(e.tipo)));
const corsieCX = () => ({reg: regCX(), periodi: CX.filter(e => S.CT.has(e.tipo)).map(e => ({r: e.corsia, a: e.quando.da, b: e.fv})), vuoto: '',
  info: `corsie: quanti fenomeni (${[...S.CT].join(', ')}; Wikidata) sono attivi in ogni anno, per macro-regione del luogo d'origine; il numero: quanti nell'anno scelto. Fine non dichiarata: ${APERTO} anni`});
function drawTlPO(w, src) {
  const REG_PO = src.reg, P = src.periodi;
  const lh = 13, top = 46, h = top + REG_PO.length * (lh + 3) + 18, x = d3.scaleLinear([T0, T1], [0, w]), x0 = w > 520 ? 205 : 0;
  tls.style.height = h + 'px';
  const c = dec(), mx = Math.max(...[...c.values()].map(v => v[0] + v[1]), 1);
  let s = '';
  for (const [d, [a, b]] of c) s += `<rect x="${x(d)}" y="${42 - 40 * (a + b) / mx}" width="${Math.max(1, x(d + 10) - x(d) - 1)}" height="${40 * b / mx}" fill="var(--co)" opacity=".35"/><rect x="${x(d)}" y="${42 - 40 * a / mx}" width="${Math.max(1, x(d + 10) - x(d) - 1)}" height="${40 * a / mx}" fill="var(--co)"/>`;
  if (VAM && S.L.vam) { const vd = new Map(); for (const k of VAM.celle) vd.set(k.d, (vd.get(k.d) || 0) + k.n); const vmx = Math.max(...vd.values(), 1);
    s += `<polyline fill="none" stroke="var(--fe)" stroke-width="1.4" points="${[...vd].filter(([d]) => d >= T0).sort((a, b) => a[0] - b[0]).map(([d, n]) => `${x(d + 5)},${42 - 40 * n / vmx}`).join(' ')}"/>`; }
  s += `<rect x="${x(S.year - S.win)}" y="0" width="${x(S.year + S.win) - x(S.year - S.win)}" height="${h - 16}" fill="var(--fe)" opacity=".08"/>`;
  REG_PO.forEach((r, i) => { const yy = top + i * (lh + 3), ps = P.filter(p => p.r === r), qui = ps.filter(p => p.a <= S.year && p.b >= S.year);
    if (w > 520) s += `<text x="2" y="${yy + 10}" font-size="10.5" fill="var(--mute)">${esc(r)} <tspan fill="var(--ink)">${qui.length}</tspan></text>`;
    for (const p of ps) { const a = Math.max(x(Math.max(p.a, T0)), x0), b = x(Math.min(p.b, T1)); if (b > a) s += `<rect x="${a}" y="${yy}" width="${b - a}" height="${lh}" fill="var(--co)" opacity=".07"/>`; }
    if (!ps.length && src.vuoto) s += `<text x="${x0 + 4}" y="${yy + 10}" font-size="10" fill="var(--mute)">${src.vuoto}</text>`; });
  for (let t = 800; t < T1; t += w < 520 ? 400 : 100) s += `<text x="${x(t)}" y="${h - 3}" font-size="10.5" fill="var(--mute)" text-anchor="middle">${t}</text>`;
  s += `<line x1="${x(S.year)}" x2="${x(S.year)}" y1="0" y2="${h - 14}" stroke="var(--fe)" stroke-width="2"/>`;
  tls.innerHTML = s; $('#yr').textContent = fmtY(S.year);
  $('#tlinfo').textContent = `${src.info}${VAM && S.L.vam ? ' · linea rossa: V&A' : ''}`;
}
function nominato() {
  if (!PO) return '';
  const g = REG_PO.map(r => [r, PO.periodi.filter(p => p.r === r && p.a <= S.year && p.b >= S.year)]).filter(([, ps]) => ps.length);
  return `<h3 style="margin:18px 0 6px">Il ${fmtY(S.year)}, nominato da chi</h3><p class="sub">Periodi di PeriodO che contengono l'anno, con la fonte che li definisce e la lingua del nome.</p>` +
    g.map(([r, ps]) => { const lg = [...new Set(ps.map(p => LINGUE[p.lg] || p.lg))].join(', ');
      const una = [...new Map(ps.map(p => [p.au, p])).values()].sort((p, q) => (p.lg === 'en') - (q.lg === 'en'));  // una per autorità, prima le lingue non inglesi
      return `<div class="k">${esc(r)} · ${ps.length} definizioni da ${una.length} fonti · in ${esc(lg)}</div>` + una.slice(0, 4).map(p => { const a = PO.autorita[p.au] || {};
        return `<div class="v" style="font-size:14px">${esc(p.n)} <span class="sub">${p.a}–${p.b} · ${esc(((a.chi ? a.chi + ', ' : '') + a.titolo).slice(0, 70))}${a.anno ? ' (' + a.anno + ')' : ''}</span></div>`; }).join('') + (una.length > 4 ? `<div class="sub">e altre ${una.length - 4} fonti</div>` : ''); }).join('');
}
const setYear = v => { S.year = Math.round(Math.max(T0, Math.min(T1, v))); update(); };
let tdrag = false;
const tx = e => { const b = tls.getBoundingClientRect(); return T0 + (T1 - T0) * (e.clientX - b.left) / b.width; };
tls.addEventListener('pointerdown', e => { tdrag = true; tls.setPointerCapture(e.pointerId); setYear(tx(e)); });
tls.addEventListener('pointermove', e => { if (tdrag) setYear(tx(e)); });
tls.addEventListener('pointerup', () => { tdrag = false; });
tls.addEventListener('keydown', e => { if (e.key === 'ArrowLeft') setYear(S.year - 5); if (e.key === 'ArrowRight') setYear(S.year + 5); });
new ResizeObserver(() => drawTl()).observe(tls);
$('#win').onchange = e => { S.win = +e.target.value; update(); };
let timer = null;
$('#play').onclick = () => { const b = $('#play'); if (timer) { clearInterval(timer); timer = null; b.setAttribute('aria-pressed', 'false'); b.textContent = '▶ Scorri'; return; }
  b.setAttribute('aria-pressed', 'true'); b.textContent = '❚❚ Ferma'; timer = setInterval(() => setYear(S.year >= T1 ? T0 : S.year + 5), 140); };

/* ---------- contesto ---------- */
function scheda(x) {
  const o = x.o, inT = S.tav.some(c => c.id === x.id);
  return `<h2>${esc(x.titolo)}</h2>
  <div style="margin-top:8px"><span class="tag ${x.grado === 'documentato' ? 'doc' : 'ipo'}">${x.grado}</span>${x.origine_incerta ? '<span class="tag ipo">attribuzione incerta</span>' : ''}${!x.origine && x.origine_dedotta ? `<span class="tag ipo" title="${esc(x.criterio_luogo)}">luogo dedotto</span>` : ''}${x.mercato ? '<span class="tag fe">per un mercato</span>' : ''}</div>
  <div class="k">Cultura, come la scrive il catalogo</div><div class="v">${esc(x.cultura) || '—'}</div>
  <div class="k">Data</div><div class="v">${esc(x.data_testo) || '—'} <span class="sub">(intervallo ${fmtY(x.inizio)}–${fmtY(x.fine)})</span></div>
  <div class="k">Tecnica</div><div class="v">${esc(x.tecnica) || '—'}</div>
  <div class="k">Luogo d'origine</div><div class="v">${o ? `${esc(o.nome)} <span class="sub">· ${PREC[o.precisione]} · <a href="https://www.wikidata.org/wiki/${o.qid}">${o.qid}</a></span>` : 'non determinabile dal record'}</div>
  ${x.m ? `<div class="k">Mercato di destinazione</div><div class="v">${esc(x.m.nome)} <span class="sub">· dichiarato dal catalogo</span></div>` : ''}
  <div class="k">Dove si trova oggi</div><div class="v">${x.s ? esc(x.s.nome) : 'sede senza coordinate'}</div>
  <div class="k">Perché è nell'atlante</div><div class="v">${esc(x.criterio)}</div>
  <div class="k">Fonte e licenza</div><div class="v"><a href="${esc(x.url)}">scheda del museo</a>${x.wikidata ? ` · <a href="https://www.wikidata.org/wiki/${esc(x.wikidata)}">${esc(x.wikidata)}</a>` : ''} · ${esc(x.licenza)}</div>
  <div class="acts"><button data-tav="${x.id}" ${inT ? 'disabled' : ''}>${inT ? 'Già sul tavolo' : 'Metti sul tavolo'}</button><button data-centra="${x.id}">Centra sul luogo</button><button data-back>Indietro</button></div>`;
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
  <div class="acts"><button data-back>Indietro</button></div>`;
}
function renderCtx() {
  const c = $('#ctx'), sel = O.find(x => x.id === S.sel);
  if (sel) { c.innerHTML = scheda(sel); return; }
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
    <div style="margin-top:12px">${xs.slice(0, 200).map(x => `<div class="row" data-sel="${x.id}"><span>${esc(x.titolo)}</span><span class="n sub">${fmtY(x.inizio)}–${fmtY(x.fine)}</span></div>`).join('')}</div>
    <div class="acts"><button data-back>Indietro</button></div>`; return; }
  const mx = agg[0]?.n || 1, n = act.length;
  c.innerHTML = `<div class="sub">Fra ${fmtY(S.year - S.win)} e ${fmtY(S.year + S.win)}</div><div class="big" style="margin:4px 0">${n}</div>
  <div class="sub">pezzi da ${agg.length} luoghi · ${act.filter(x => x.grado === 'documentato').length} documentati</div>
  <h3 style="margin:18px 0 6px">Da dove</h3>
  ${agg.slice(0, 14).map(g => `<div class="row" data-place="${g.id}"><span>${esc(g.l.nome)} <span class="sub">${g.l.precisione === 'citta' ? '' : '· ' + PREC[g.l.precisione]}</span><div class="bar" style="width:${100 * g.n / mx}%"></div></span><span class="n">${g.n}</span></div>`).join('') || '<p class="sub">Nessun pezzo in questa finestra.</p>'}
  ${VAM && S.L.vam && vagg.length ? `<h3 style="margin:18px 0 6px">V&A, solo conteggi</h3>${vagg.slice(0, 8).map(g => `<div class="row" data-place="${g.id}"><span>${esc(g.l.nome)} <span class="sub">${g.l.precisione === 'citta' ? '' : '· ' + PREC[g.l.precisione]}</span></span><span class="n">~${Math.round(g.n)}</span></div>`).join('')}` : ''}
  ${S.L.contesti ? `<h3 style="margin:18px 0 6px">Fenomeni artistici in questa finestra</h3>${cagg.length ? cagg.slice(0, 12).map(e => `<div class="row" data-place="mov:${e.id}"><span><i>${esc(e.nome)}</i> <span class="sub">· ${e.tipo}, ${esc(e.luoghi[0].oggi)}</span></span><span class="n">${fmtY(e.quando.da)}</span></div>`).join('') + (cagg.length > 12 ? `<p class="sub">e altri ${cagg.length - 12}: li trovi sulla mappa</p>` : '') : '<p class="sub">Nessuno con data e luogo su Wikidata in questa finestra, per i tipi scelti.</p>'}` : ''}
  ${nominato()}
  <h3 style="margin:18px 0 6px">Come leggere</h3>
  <p class="sub">Ogni punto è un luogo d'origine dichiarato dal catalogo. Il pieno indica una città; l'anello tratteggiato un paese, perché il record non dice di più. I pezzi «ipotetici» appartengono a una manifattura nota per il blu, ma il loro record non nomina il colore. Clicca un luogo per l'elenco, poi un pezzo per la scheda.</p>`;
}
document.addEventListener('click', e => {
  const t = e.target.closest('[data-sel],[data-place],[data-back],[data-tav],[data-centra],[data-go]'); if (!t) return;
  if (t.dataset.sel) { S.sel = t.dataset.sel; }
  else if (t.dataset.place) { S.place = t.dataset.place; S.sel = null; }
  else if ('back' in t.dataset) { if (S.sel) S.sel = null; else S.place = null; }
  else if (t.dataset.tav) { addTav(t.dataset.tav); }
  else if (t.dataset.centra) { const x = O.find(o => o.id === t.dataset.centra); if (x.o) S.rot = [-x.o.lon, -x.o.lat]; }
  else if (t.dataset.go) { S.tappa = +t.dataset.go; applyTappa(); return; }
  renderCtx(); draw();
});

/* ---------- tavolo ---------- */
const salva = () => { try { localStorage.setItem('armoni-tavolo', JSON.stringify(S.tav)); } catch (e) {} };
function addTav(id) { if (S.tav.some(c => c.id === id)) return; const i = S.tav.length; S.tav.push({id, x: 16 + (i % 5) * 246, y: 14 + Math.floor(i / 5) * 180, nota: ''}); salva(); renderTav(); $('#tavolo').classList.add('open'); }
function renderTav() {
  $('#tavn').textContent = S.tav.length;
  const b = $('#board');
  b.innerHTML = S.tav.length ? S.tav.map((c, i) => { const x = O.find(o => o.id === c.id);
    return `<div class="card" data-i="${i}" style="left:${c.x}px;top:${c.y}px"><div class="ch"><span class="num">${i + 1}</span><b>${esc(x.titolo.slice(0, 48))}</b><button class="x" data-rm="${i}" aria-label="Togli dal tavolo">×</button></div>
    <div class="cb"><div class="sub">${esc(x.o ? x.o.nome : '—')} · ${fmtY(x.inizio)}–${fmtY(x.fine)} · ${x.grado}</div><textarea data-nota="${i}" placeholder="Nota">${esc(c.nota)}</textarea></div></div>`; }).join('')
    : '<p class="empty">Il tavolo è vuoto. Apri la scheda di un pezzo e scegli «Metti sul tavolo»: qui potrai accostare opere di luoghi ed epoche diverse, spostarle e annotarle. Il tavolo resta solo in questo browser.</p>';
  const ax = $('#tavax'), w = ax.clientWidth || 600, xs = S.tav.map(c => O.find(o => o.id === c.id));
  if (!xs.length) { ax.innerHTML = ''; return; }
  const lo = Math.min(...xs.map(x => x.inizio)) - 20, hi = Math.max(...xs.map(x => x.fine)) + 20, sc = d3.scaleLinear([lo, hi], [24, w - 24]);
  ax.innerHTML = xs.map((x, i) => `<line x1="${sc(x.inizio)}" x2="${Math.max(sc(x.fine), sc(x.inizio) + 2)}" y1="${10 + (i % 4) * 8}" y2="${10 + (i % 4) * 8}" stroke="var(--co)" stroke-width="4" stroke-linecap="round"/><text x="${sc(x.inizio) - 4}" y="${14 + (i % 4) * 8}" font-size="10" fill="var(--fe)" text-anchor="end">${i + 1}</text>`).join('')
    + sc.ticks(6).map(t => `<text x="${sc(t)}" y="52" font-size="10.5" fill="var(--mute)" text-anchor="middle">${t}</text>`).join('');
}
let cd = null;
$('#board').addEventListener('pointerdown', e => { const h = e.target.closest('.ch'); if (!h || e.target.closest('button')) return; const card = h.parentElement, i = +card.dataset.i; cd = {i, card, x: e.clientX - S.tav[i].x, y: e.clientY - S.tav[i].y}; h.setPointerCapture(e.pointerId); });
$('#board').addEventListener('pointermove', e => { if (!cd) return; const c = S.tav[cd.i]; c.x = Math.max(0, e.clientX - cd.x); c.y = Math.max(0, e.clientY - cd.y); cd.card.style.left = c.x + 'px'; cd.card.style.top = c.y + 'px'; });
$('#board').addEventListener('pointerup', () => { if (cd) { cd = null; salva(); } });
$('#board').addEventListener('input', e => { if (e.target.dataset.nota) { S.tav[+e.target.dataset.nota].nota = e.target.value; salva(); } });
$('#board').addEventListener('click', e => { const r = e.target.closest('[data-rm]'); if (r) { S.tav.splice(+r.dataset.rm, 1); salva(); renderTav(); renderCtx(); } });
$('#tavbtn').onclick = () => { renderTav(); $('#tavolo').classList.toggle('open'); };
$('#tavclose').onclick = () => $('#tavolo').classList.remove('open');
$('#tavclear').onclick = () => { S.tav = []; salva(); renderTav(); renderCtx(); };
$('#tavcopy').onclick = async () => { const t = S.tav.map((c, i) => { const x = O.find(o => o.id === c.id); return `${i + 1}. ${x.titolo} — ${x.cultura}, ${x.data_testo} [${x.grado}] ${x.url}${c.nota ? '\n   nota: ' + c.nota : ''}`; }).join('\n');
  const b = $('#tavcopy'); try { await navigator.clipboard.writeText(t); b.textContent = 'Copiato'; } catch (e) { b.textContent = 'Copia non consentita qui'; } setTimeout(() => { b.textContent = 'Copia elenco'; }, 1800); };

/* ---------- percorso ---------- */
let Lr = null;
function applyTappa() {
  const t = TAPPE[S.tappa]; if (!Lr) Lr = {...S.L};
  S.year = t.y; S.win = t.w; S.rot = [...t.rot]; S.k = 1; S.place = null; S.sel = null;
  S.L = {confini: 1, origini: 1, sedi: 0, spostamenti: 0, mercati: 0, silenzio: 0, ipotetici: 1, dedotti: 0, vam: 0, letteratura: 0, contesti: 0, relazioni: 0, ...t.L}; G.on = {}; G.mem = {};
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
  if (!QU) { $('#qual').innerHTML = '<p>Riepilogo non disponibile.</p>'; return; }
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
  S.mode = location.hash === '#percorso' ? 'percorso' : location.hash === '#qualita' ? 'qualita' : 'ricerca';
  document.body.classList.toggle('percorso', S.mode === 'percorso');
  document.body.classList.toggle('qualita', S.mode === 'qualita');
  $('#m-qualita').setAttribute('aria-pressed', S.mode === 'qualita');
  if (S.mode === 'qualita') { renderQual(); return; }
  $('#m-ricerca').setAttribute('aria-pressed', S.mode === 'ricerca'); $('#m-percorso').setAttribute('aria-pressed', S.mode === 'percorso');
  if (S.mode === 'percorso') applyTappa(); else { if (Lr) { S.L = Lr; Lr = null; } syncChecks(); update(); }
  requestAnimationFrame(misura);  // dopo il cambio di griglia la mappa ha nuove misure
}
window.addEventListener('hashchange', route);
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
    i.checked = G.on[g] !== false; i.indeterminate = false; $(`[data-gn="${g}"]`).textContent = G.on[g] === false ? 'spenta' : `${n} di ${f.length} attivi`; });
};
document.querySelectorAll('[data-l]').forEach(i => i.onchange = () => { S.L[i.dataset.l] = i.checked ? 1 : 0; const g = i.closest('[data-grp]')?.dataset.grp; if (g && i.checked) G.on[g] = true; syncChecks(); update(); });
document.querySelectorAll('[data-g]').forEach(i => i.onchange = () => { const g = i.dataset.g;
  if (i.checked) { G.on[g] = true; const m = G.mem[g]; if (m) for (const k of figli(g)) S.L[k] = m[k]; }
  else { G.on[g] = false; G.mem[g] = Object.fromEntries(figli(g).map(k => [k, S.L[k]])); for (const k of figli(g)) S.L[k] = 0; }
  syncChecks(); update(); });
document.querySelectorAll('[data-gt]').forEach(b => b.onclick = () => { const d = b.closest('.grp'), o = d.classList.toggle('open'); b.setAttribute('aria-expanded', o); });
document.querySelectorAll('[data-ct]').forEach(i => i.onchange = () => { S.CT[i.checked ? 'add' : 'delete'](i.dataset.ct); update(); });
document.querySelectorAll('[data-f]').forEach(i => i.onchange = () => { S.F[i.dataset.f] = i.checked ? 1 : 0; update(); });
for (const p of ['globo', 'piano']) $('#p-' + p).onclick = () => { S.proj = p; S.k = 1; $('#p-globo').setAttribute('aria-pressed', p === 'globo'); $('#p-piano').setAttribute('aria-pressed', p === 'piano'); draw(); };
let qt; $('#q').oninput = e => { clearTimeout(qt); qt = setTimeout(() => { S.q = e.target.value.trim(); update(); }, 180); };
$('#win').value = String(S.win);
$('#corsie').onchange = e => { S.corsie = e.target.value; drawTl(); };
function update() { if (!O.length) return; const ws = $('#win'); if (![...ws.options].some(o => +o.value === S.win)) ws.add(new Option(String(S.win))); ws.value = String(S.win); filtra(); draw(); drawTl(); if (S.mode === 'ricerca') renderCtx(); renderTavCount(); }
const renderTavCount = () => { $('#tavn').textContent = S.tav.length; };
new MutationObserver(() => { draw(); drawTl(); }).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});

/* ── Guida: visita dell'interfaccia e domande da provare ─────────────────────────────
   La visita evidenzia una zona alla volta; le domande impostano da sole la vista che risponde.
   Si apre da sola alla prima visita (se il browser lo permette) e sempre dal pulsante «Guida». */
const VISITA = [
  {s: 'header .seg', t: 'Tre modi di usare l\'atlante', p: '<b>Ricerca</b>: esplori liberamente, scegliendo anno, luoghi e livelli. <b>Percorso</b>: un racconto in tappe, con le fonti di ogni frase. <b>Affidabilità</b>: che cosa sanno i dati, e dove tacciono.'},
  {s: '#fig', t: 'Il globo', p: 'Trascina per ruotarlo, usa + e − per avvicinarti. Un clic su un segno apre la sua scheda a destra. <b>Cerchi</b>: pezzi per luogo d\'origine (pieno: città; anello: solo il paese). <b>Rombi</b>: quantità al V&amp;A. <b>Triangoli</b>: scavi archeologici. <b>Quadrati e nomi in corsivo</b>: stili, movimenti, scuole, dinastie.'},
  {s: '#tl', t: 'Il tempo', p: 'Clicca o trascina sulla barra per scegliere l\'anno; con «finestra ±» decidi quanti anni guardare insieme; «Scorri» fa avanzare il tempo da solo. Sotto, le <b>corsie</b>: chi divide il tempo e come lo chiama (PeriodO), le dinastie, i fenomeni artistici per regione.'},
  {s: '#lay', t: 'Livelli, in cartelle', p: 'Ogni cartella si accende e si spegne in blocco, e ricorda come l\'avevi lasciata; il nome la apre. Ogni voce dice che cosa mostra. I livelli si <b>sovrappongono per accostare</b>: vedere due cose nello stesso luogo e nello stesso tempo non significa che siano collegate. Le relazioni compaiono solo dove una fonte le dichiara.'},
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
  S.L = {confini: 1, origini: 0, sedi: 0, spostamenti: 0, mercati: 0, silenzio: 0, ipotetici: 1, dedotti: 0, vam: 0, letteratura: 0, contesti: 0, relazioni: 0, ...d.L};
  S.CT = new Set(d.CT || TIPI_CX); document.querySelectorAll('[data-ct]').forEach(i => { i.checked = S.CT.has(i.dataset.ct); });
  if (d.corsie) { S.corsie = d.corsie; $('#corsie').value = d.corsie; }
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
gd.addEventListener('keydown', e => {
  if (e.key === 'Escape') chiudiGuida();
  if (e.key === 'Tab') { const f = [...gd.querySelectorAll('button:not([disabled])')]; const i = f.indexOf(document.activeElement);
    if (e.shiftKey && i <= 0) { f.at(-1).focus(); e.preventDefault(); } else if (!e.shiftKey && i === f.length - 1) { f[0].focus(); e.preventDefault(); } }
});
$('#guidabtn').onclick = () => apriGuida();
addEventListener('resize', () => { if (!gd.hidden && gd.querySelector('.gd-step')) mostraPasso(); });
try { if (!localStorage.getItem('armoni-guida-vista')) { localStorage.setItem('armoni-guida-vista', '1'); setTimeout(() => apriGuida(), 900); } } catch (e) { /* senza memoria del browser la guida resta sul pulsante */ }
}
