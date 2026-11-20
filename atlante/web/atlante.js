{
const $ = s => document.querySelector(s);
const probe = document.createElement('i'); probe.style.display = 'none'; document.body.appendChild(probe);
const css = v => { probe.style.color = `var(${v})`; return getComputedStyle(probe).color; };
const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const fmtY = y => y < 0 ? `${-y} a.C.` : String(y);
const PREC = {citta: 'città', paese: 'solo paese', regione: 'regione', zona: 'zona', istituzione: 'istituzione'};
const T0 = 700, T1 = 2000;

const S = {corsie: 'wikidata', year: 1640, win: 25, proj: 'globo', rot: [-40, -28], k: 1, sel: null, place: null, q: '',
  L: {confini: 1, origini: 1, sedi: 1, spostamenti: 0, mercati: 1, silenzio: 0, ipotetici: 1, vam: 1}, F: {met: 1, cma: 1, wd: 1, colbase: 1},
  tav: [], mode: 'ricerca', tappa: 0};
let PO = null, VAM = null, vagg = [], NOD = [], O = [], LU = {}, PER = [], ANNI = [], TERRE = null, CONF = {}, act = [], agg = [];

const TAPPE = [
 {t: 'Blu su bianco, prima della porcellana', y: 850, w: 60, rot: [-44, -30], L: {}, hi: ['Iraq'],
  p: 'Nell\'Iraq abbaside del IX secolo i vasai dipingono in blu di cobalto su un\'invetriatura bianca opaca, cercando l\'effetto delle ceramiche bianche cinesi che arrivavano per mare. Il blu e bianco non comincia in Cina: comincia altrove, come imitazione della Cina.'},
 {t: 'Il cobalto viaggia verso est', y: 1340, w: 30, rot: [-90, -32], L: {}, hi: ['China', 'Jingdezhen', 'Iran', 'Kashan'],
  p: 'Sotto la dinastia Yuan, a Jingdezhen, la porcellana dipinta sotto coperta prende la forma che chiamiamo blu e bianco. La storiografia corrente lega questo passaggio al cobalto importato dall\'Iran e ai grandi piatti destinati ai mercati del mondo islamico.'},
 {t: 'Il Quattrocento, ovunque', y: 1450, w: 25, rot: [-75, -18], L: {}, hi: ['Vietnam', 'China', 'Egypt', 'Syria'],
  p: 'Nello stesso mezzo secolo il blu e bianco si dipinge in Cina, in Vietnam, in Corea, e si imita in Egitto e in Siria. Un\'ipotesi diffusa collega l\'ascesa delle esportazioni vietnamite alle restrizioni marittime dei Ming.'},
 {t: 'Iznik risponde', y: 1530, w: 30, rot: [-30, -38], L: {}, hi: ['İznik', 'Kütahya'],
  p: 'Per la corte ottomana le botteghe di Iznik dipingono in blu su un impasto silicico bianco, partendo dai modelli cinesi e trasformandoli. Qui il dato è fragile: per gran parte dei pezzi di Iznik il catalogo non nomina il colore.'},
 {t: 'Dalla porcellana kraak a Delft', y: 1640, w: 25, rot: [-50, -38], L: {mercati: 1}, hi: ['China', 'Netherlands', 'Delft'],
  p: 'Le navi della Compagnia olandese delle Indie orientali portano in Europa la porcellana cinese detta kraak; le manifatture di Delft la imitano su terracotta smaltata. È un\'imitazione che diventa un linguaggio proprio.'},
 {t: 'Arita dopo la caduta dei Ming', y: 1675, w: 20, rot: [-120, -30], L: {mercati: 1}, hi: ['Japan', 'Arita'],
  p: 'Con la crisi della produzione cinese nel passaggio dai Ming ai Qing, le fornaci giapponesi di Arita entrano nel commercio di esportazione attraverso Nagasaki. Nei dati, il Giappone cresce proprio in questi decenni.'},
 {t: 'Il galeone di Manila e Puebla', y: 1710, w: 40, rot: [100, -18], L: {}, hi: ['Puebla City', 'Mexico'],
  p: 'Attraverso il Pacifico la porcellana cinese arriva nella Nuova Spagna; a Puebla i vasai dipingono in blu una maiolica che risponde a quella e alla Talavera spagnola. Tutti i pezzi di Puebla in questi dati sono ipotetici: nessun record nomina il blu.'},
 {t: 'Ciò che questi dati non mostrano', y: 1600, w: 400, rot: [-40, 2], L: {silenzio: 1, sedi: 1, spostamenti: 1}, hi: [],
  p: 'Con ColBase metà delle schede è conservata in Giappone, ma quasi metà dei pezzi giapponesi non ha luogo d\'origine nel record, e molti non hanno data. Wikidata aggiunge poche sedi in Brasile e a Macao. La costa swahili, dove la porcellana cinese fu murata in moschee e tombe, il Sud-est asiatico insulare, i luoghi del consumo nelle Americhe: qui sono vuoti delle fonti, non vuoti della storia.'}
];

/* ---------- dati ---------- */
const j = u => fetch(u).then(r => { if (!r.ok) throw new Error(u); return r.json(); });
Promise.all([j('opere.json'), j('luoghi.json'), j('periodi.json'), j('confini/anni.json'), j('terre.json'), j('densita_vam.json').catch(() => null), j('periodo.json').catch(() => null)]).then(([o, l, p, a, t, v, po]) => {
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

function filtra() {
  const q = S.q.toLowerCase();
  act = O.filter(x => x.inizio <= S.year + S.win && x.fine >= S.year - S.win && S.F[x.fonte] &&
    (S.L.ipotetici || x.grado === 'documentato') && (!q || x.hay.includes(q)));
  const m = new Map();
  for (const x of act) { if (!x.o) continue; const g = m.get(x.origine) || {id: x.origine, l: x.o, n: 0, doc: 0, inc: 0}; g.n++; if (x.grado === 'documentato') g.doc++; if (x.origine_incerta) g.inc++; m.set(x.origine, g); }
  agg = [...m.values()].sort((a, b) => b.n - a.n);
  const vm = new Map();
  if (VAM) for (const c of VAM.celle) if (c.d + 9 >= S.year - S.win && c.d <= S.year + S.win) vm.set(c.l, (vm.get(c.l) || 0) + c.n);
  vagg = [...vm].map(([id, n]) => ({id, l: LU[id], n})).filter(g => g.n >= .5).sort((a, b) => b.n - a.n);
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
    if (r > 9 || (hi && hi.has(g.id))) { ctx.font = '12px "Instrument Sans",sans-serif'; ctx.fillStyle = ink; ctx.fillText(g.l.nome, x + r + 4, y + 4); }
  }
  if (S.L.vam) for (const g of vagg) {
    const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = proj(c), r = 3 + Math.sqrt(g.n) * 1.3;
    ctx.beginPath(); ctx.moveTo(x, y - r); ctx.lineTo(x + r, y); ctx.lineTo(x, y + r); ctx.lineTo(x - r, y); ctx.closePath();
    ctx.strokeStyle = fe; ctx.globalAlpha = .75; ctx.lineWidth = 1.1; ctx.stroke(); ctx.globalAlpha = 1;
  }
  if (S.L.sedi) for (const k of new Set(act.map(x => x.sede).filter(Boolean))) {
    const l = LU[k]; if (!l || !visibile([l.lon, l.lat])) continue; const [x, y] = proj([l.lon, l.lat]);
    ctx.fillStyle = ink; ctx.fillRect(x - 4, y - 4, 8, 8);
  }
  const sel = O.find(x => x.id === S.sel);
  if (sel && sel.o && visibile([sel.o.lon, sel.o.lat])) { const [x, y] = proj([sel.o.lon, sel.o.lat]); ctx.beginPath(); ctx.arc(x, y, 11, 0, 7); ctx.strokeStyle = fe; ctx.lineWidth = 2.5; ctx.stroke(); }
  chip(cf.anno);
}

function chip(anno) {
  const n = act.length, paese = act.filter(x => x.o && x.o.precisione !== 'citta').length, ipo = act.filter(x => x.grado === 'ipotetico').length;
  let h = `<b>${n}</b> pezzi attivi · confini del ${fmtY(anno)}`;
  if (S.L.silenzio && n) { const us = act.filter(x => x.fonte === 'met' || x.fonte === 'cma').length, sedi = new Set(act.map(x => x.sede).filter(Boolean)).size, pu = 100 * us / n;
    if (VAM && S.L.vam) { const tv = vagg.reduce((a, g) => a + g.n, 0), cv = vagg.filter(g => g.l.precisione === 'citta').reduce((a, g) => a + g.n, 0); h += `<br>V&A (rombi, tutti conservati a Londra): ~${Math.round(tv)} pezzi, ${tv ? Math.round(100 * cv / tv) : 0}% localizzati per città`; }
    h += `<br>${Math.round(100 * paese / n)}% localizzati solo per paese · ${ipo} ipotetici · ${act.filter(x => !x.o).length} senza luogo<br>${sedi} sedi di conservazione · ${pu > 99 && pu < 100 ? pu.toFixed(1) : Math.round(pu)}% delle schede negli Stati Uniti<br>${NOD.filter(x => S.F[x.fonte]).length} pezzi senza data: esistono nei dati, non nel tempo`; }
  $('#chip').innerHTML = h;
}

function hit(px, py) {
  let best = null, bd = 1e9;
  for (const g of agg) { const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = proj(c), d = Math.hypot(x - px, y - py); if (d < rr(g) + 5 && d < bd) { bd = d; best = g; } }
  if (!best && S.L.vam) for (const g of vagg) { const c = [g.l.lon, g.l.lat]; if (!visibile(c)) continue; const [x, y] = proj(c), d = Math.hypot(x - px, y - py); if (d < 3 + Math.sqrt(g.n) * 1.3 + 4 && d < bd) { bd = d; best = {...g, vam: true}; } }
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
    tip.innerHTML = g && g.vam ? `<b>${esc(g.l.nome)}</b> · V&A ~${Math.round(g.n)} pezzi<br><span class="sub">solo conteggio aggregato</span>` : g ? `<b>${esc(g.l.nome)}</b> · ${g.n} pezzi<br><span class="sub">${PREC[g.l.precisione]}${g.inc ? ' · ' + g.inc + ' attribuzioni incerte' : ''}</span>` : `${esc(pol)}<br><span class="sub">confini del ${fmtY(confini(S.year).anno)}</span>`; }
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
const roMap = new ResizeObserver(() => { const d = devicePixelRatio || 1; W = fig.clientWidth; H = fig.clientHeight; cv.width = W * d; cv.height = H * d; ctx.setTransform(d, 0, 0, d, 0, 0); draw(); });
roMap.observe(fig);

/* ---------- tempo ---------- */
const tls = $('#tls');
const dec = () => { const c = new Map(); for (const x of O) { if (!S.F[x.fonte] || (!S.L.ipotetici && x.grado !== 'documentato')) continue;
  for (let d = Math.max(T0, Math.floor(x.inizio / 10) * 10); d <= Math.min(T1, x.fine); d += 10) { const v = c.get(d) || [0, 0]; v[x.grado === 'documentato' ? 0 : 1] += 1 / (1 + (x.fine - x.inizio) / 10); c.set(d, v); } } return c; };
function drawTl() {
  const w = tls.clientWidth, lh = 12, top = 46, righe = [];
  if (S.corsie === 'periodo' && PO) return drawTlPO(w);
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
function drawTlPO(w) {
  const lh = 13, top = 46, h = top + REG_PO.length * (lh + 3) + 18, x = d3.scaleLinear([T0, T1], [0, w]), x0 = w > 520 ? 150 : 0;
  tls.style.height = h + 'px';
  const c = dec(), mx = Math.max(...[...c.values()].map(v => v[0] + v[1]), 1);
  let s = '';
  for (const [d, [a, b]] of c) s += `<rect x="${x(d)}" y="${42 - 40 * (a + b) / mx}" width="${Math.max(1, x(d + 10) - x(d) - 1)}" height="${40 * b / mx}" fill="var(--co)" opacity=".35"/><rect x="${x(d)}" y="${42 - 40 * a / mx}" width="${Math.max(1, x(d + 10) - x(d) - 1)}" height="${40 * a / mx}" fill="var(--co)"/>`;
  if (VAM && S.L.vam) { const vd = new Map(); for (const k of VAM.celle) vd.set(k.d, (vd.get(k.d) || 0) + k.n); const vmx = Math.max(...vd.values(), 1);
    s += `<polyline fill="none" stroke="var(--fe)" stroke-width="1.4" points="${[...vd].filter(([d]) => d >= T0).sort((a, b) => a[0] - b[0]).map(([d, n]) => `${x(d + 5)},${42 - 40 * n / vmx}`).join(' ')}"/>`; }
  s += `<rect x="${x(S.year - S.win)}" y="0" width="${x(S.year + S.win) - x(S.year - S.win)}" height="${h - 16}" fill="var(--fe)" opacity=".08"/>`;
  REG_PO.forEach((r, i) => { const yy = top + i * (lh + 3), ps = PO.periodi.filter(p => p.r === r), qui = ps.filter(p => p.a <= S.year && p.b >= S.year);
    if (w > 520) s += `<text x="2" y="${yy + 10}" font-size="10.5" fill="var(--mute)">${esc(r)} <tspan fill="var(--ink)">${qui.length}</tspan></text>`;
    for (const p of ps) { const a = Math.max(x(Math.max(p.a, T0)), x0), b = x(Math.min(p.b, T1)); if (b > a) s += `<rect x="${a}" y="${yy}" width="${b - a}" height="${lh}" fill="var(--co)" opacity=".07"/>`; }
    if (!ps.length) s += `<text x="${x0 + 4}" y="${yy + 10}" font-size="10" fill="var(--mute)">nessun periodo in PeriodO</text>`; });
  for (let t = 800; t < T1; t += w < 520 ? 400 : 100) s += `<text x="${x(t)}" y="${h - 3}" font-size="10.5" fill="var(--mute)" text-anchor="middle">${t}</text>`;
  s += `<line x1="${x(S.year)}" x2="${x(S.year)}" y1="0" y2="${h - 14}" stroke="var(--fe)" stroke-width="2"/>`;
  tls.innerHTML = s; $('#yr').textContent = fmtY(S.year);
  $('#tlinfo').textContent = `corsie: quante definizioni di periodo PeriodO coprono ogni anno, per regione (il numero: quante valgono per l'anno scelto)${VAM && S.L.vam ? ' · linea rossa: V&A' : ''}`;
}
function nominato() {
  if (!PO) return '';
  const g = REG_PO.map(r => [r, PO.periodi.filter(p => p.r === r && p.a <= S.year && p.b >= S.year)]).filter(([, ps]) => ps.length);
  return `<h3 style="margin:18px 0 6px">Il ${fmtY(S.year)}, nominato da chi</h3><p class="sub">Periodi di PeriodO che contengono l'anno, con la fonte che li definisce e la lingua del nome.</p>` +
    g.map(([r, ps]) => { const lg = [...new Set(ps.map(p => LINGUE[p.lg] || p.lg))].join(', ');
      return `<div class="k">${esc(r)} · ${ps.length} definizioni · in ${esc(lg)}</div>` + ps.slice(0, 3).map(p => { const a = PO.autorita[p.au] || {};
        return `<div class="v" style="font-size:14px">${esc(p.n)} <span class="sub">${p.a}–${p.b} · ${esc(((a.chi ? a.chi + ', ' : '') + a.titolo).slice(0, 70))}${a.anno ? ' (' + a.anno + ')' : ''}</span></div>`; }).join('') + (ps.length > 3 ? `<div class="sub">e altre ${ps.length - 3}</div>` : ''); }).join('');
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
  <div style="margin-top:8px"><span class="tag ${x.grado === 'documentato' ? 'doc' : 'ipo'}">${x.grado}</span>${x.origine_incerta ? '<span class="tag ipo">attribuzione incerta</span>' : ''}${x.mercato ? '<span class="tag fe">per un mercato</span>' : ''}</div>
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
function renderCtx() {
  const c = $('#ctx'), sel = O.find(x => x.id === S.sel);
  if (sel) { c.innerHTML = scheda(sel); return; }
  if (S.place) { const g = agg.find(g => g.id === S.place), l = LU[S.place], xs = act.filter(x => x.origine === S.place).sort((a, b) => a.inizio - b.inizio);
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
  S.L = {confini: 1, origini: 1, sedi: 0, spostamenti: 0, mercati: 0, silenzio: 0, ipotetici: 1, ...t.L};
  update();
  const inHi = act.filter(x => t.hi.includes(x.origine)), ipo = inHi.filter(x => x.grado === 'ipotetico').length;
  const dati = t.hi.length ? `Fra ${fmtY(t.y - t.w)} e ${fmtY(t.y + t.w)} i dati contengono <b>${act.length}</b> pezzi; <b>${inHi.length}</b> vengono dai luoghi evidenziati${ipo ? `, di cui ${ipo} ipotetici` : ''}.`
    : `<b>${O.length}</b> pezzi con data, ${NOD.length} senza. Il ${Math.round(100 * O.filter(x => x.o && x.o.precisione !== 'citta').length / O.length)}% è localizzato solo per paese; il ${Math.round(100 * O.filter(x => x.fonte === 'met' || x.fonte === 'cma').length / O.length)}% è conservato negli Stati Uniti.`;
  $('#nar').innerHTML = `<div class="step">Tappa ${S.tappa + 1} di ${TAPPE.length} · ${fmtY(t.y)}</div><h2>${esc(t.t)}</h2><p>${t.p}</p><div class="dati">${dati}</div>
  <div class="acts"><button data-go="${Math.max(0, S.tappa - 1)}" ${S.tappa ? '' : 'disabled'}>← Precedente</button><button data-go="${Math.min(TAPPE.length - 1, S.tappa + 1)}" ${S.tappa < TAPPE.length - 1 ? '' : 'disabled'}>Successiva →</button></div>
  <div class="dots">${TAPPE.map((_, i) => `<button data-go="${i}" aria-pressed="${i === S.tappa}" aria-label="Tappa ${i + 1}">${i + 1}</button>`).join('')}</div>
  <p class="nota">Testi redazionali scritti da Claude e da verificare con la bibliografia: indicano direzioni note della storiografia, non sono fonti. I numeri sono calcolati sui dati.</p>`;
}
function route() {
  S.mode = location.hash === '#percorso' ? 'percorso' : 'ricerca';
  document.body.classList.toggle('percorso', S.mode === 'percorso');
  $('#m-ricerca').setAttribute('aria-pressed', S.mode === 'ricerca'); $('#m-percorso').setAttribute('aria-pressed', S.mode === 'percorso');
  if (S.mode === 'percorso') applyTappa(); else { if (Lr) { S.L = Lr; Lr = null; } syncChecks(); update(); }
}
window.addEventListener('hashchange', route);
$('#m-ricerca').onclick = () => { location.hash = 'ricerca'; };
$('#m-percorso').onclick = () => { location.hash = 'percorso'; };

/* ---------- controlli ---------- */
const syncChecks = () => { document.querySelectorAll('[data-l]').forEach(i => { i.checked = !!S.L[i.dataset.l]; }); };
document.querySelectorAll('[data-l]').forEach(i => i.onchange = () => { S.L[i.dataset.l] = i.checked ? 1 : 0; update(); });
document.querySelectorAll('[data-f]').forEach(i => i.onchange = () => { S.F[i.dataset.f] = i.checked ? 1 : 0; update(); });
for (const p of ['globo', 'piano']) $('#p-' + p).onclick = () => { S.proj = p; S.k = 1; $('#p-globo').setAttribute('aria-pressed', p === 'globo'); $('#p-piano').setAttribute('aria-pressed', p === 'piano'); draw(); };
let qt; $('#q').oninput = e => { clearTimeout(qt); qt = setTimeout(() => { S.q = e.target.value.trim(); update(); }, 180); };
$('#win').value = String(S.win);
$('#corsie').onchange = e => { S.corsie = e.target.value; drawTl(); };
function update() { if (!O.length) return; const ws = $('#win'); if (![...ws.options].some(o => +o.value === S.win)) ws.add(new Option(String(S.win))); ws.value = String(S.win); filtra(); draw(); drawTl(); if (S.mode === 'ricerca') renderCtx(); renderTavCount(); }
const renderTavCount = () => { $('#tavn').textContent = S.tav.length; };
new MutationObserver(() => { draw(); drawTl(); }).observe(document.documentElement, {attributes: true, attributeFilter: ['data-theme']});
}
