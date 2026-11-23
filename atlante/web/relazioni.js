// ArMoni · Relazioni: grafo dei legami fra contesti dichiarati su Wikidata.
// Principio: un legame compare solo dove una fonte lo dichiara. Qui la fonte è sempre Wikidata.
'use strict';
const $ = s => document.querySelector(s);
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c]));
const fmtY = y => y < 0 ? `${-y} a.C.` : String(y);
const APERTO = 50;  // anni contati dall'inizio quando Wikidata non dà una fine
const RIDOTTO = matchMedia('(prefers-reduced-motion: reduce)');

// Tipi di relazione: frase diretta, frase inversa, tratto (in pixel sullo schermo)
const REL = {
  'influenzato da':      {inv: 'ha influenzato',            dash: [],             tratto: 'continuo'},
  'parte di':            {inv: 'comprende',                 dash: [6, 4],         tratto: 'tratteggiato'},
  'caso particolare di': {inv: 'ha come caso particolare',  dash: [1.2, 3.2],     tratto: 'punteggiato'},
  'segue':               {inv: 'è seguito da',              dash: [9, 3, 1.2, 3], tratto: 'tratto e punto'},
  'sostituisce':         {inv: 'è sostituito da',           dash: [16, 4],        tratto: 'tratteggio lungo'},
};
const RELK = Object.keys(REL);
// Forme dei nodi per tipo di contesto
const TIPI = {movimento: 'quadrato', scuola: 'triangolo', stile: 'rombo', periodizzazione: 'cerchio'};
const TIPIK = Object.keys(TIPI);
const PLURALE = {movimento: 'movimenti', scuola: 'scuole', stile: 'stili', periodizzazione: 'periodizzazioni'};

function forma(ctx, f, x, y, r) {
  ctx.beginPath();
  if (f === 'quadrato') { const s = r * 0.86; ctx.rect(x - s, y - s, 2 * s, 2 * s); }
  else if (f === 'triangolo') { const s = r * 1.18; ctx.moveTo(x, y - s); ctx.lineTo(x + s * 0.93, y + s * 0.6); ctx.lineTo(x - s * 0.93, y + s * 0.6); ctx.closePath(); }
  else if (f === 'rombo') { const s = r * 1.15; ctx.moveTo(x, y - s); ctx.lineTo(x + s, y); ctx.lineTo(x, y + s); ctx.lineTo(x - s, y); ctx.closePath(); }
  else ctx.arc(x, y, r, 0, 2 * Math.PI);
}
// Piccolo SVG per legenda e filtri
function iconaForma(f, nc) {
  const a = nc ? 'fill="var(--mute)" fill-opacity=".55"' : 'fill="var(--cel)"';
  const p = f === 'quadrato' ? '<rect x="2.5" y="2.5" width="9" height="9"/>' : f === 'triangolo' ? '<path d="M7 1.5 12.6 11.3H1.4Z"/>'
    : f === 'rombo' ? '<path d="M7 1 13 7 7 13 1 7Z"/>' : `<circle cx="7" cy="7" r="${nc ? 3.5 : 5.2}"/>`;
  return `<svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true"><g ${a}>${p}</g></svg>`;
}
function iconaTratto(k) {
  const d = REL[k].dash.length ? `stroke-dasharray="${REL[k].dash.join(' ')}"` : '';
  return `<svg width="38" height="10" viewBox="0 0 38 10" aria-hidden="true"><line x1="1" y1="5" x2="30" y2="5" stroke="var(--ink)" stroke-width="1.6" stroke-linecap="round" ${d}/><path d="M37 5 29.5 1.5V8.5Z" fill="var(--ink)"/></svg>`;
}

// Colori: le variabili CSS usano light-dark(), quindi le risolvo passando da un elemento nascosto
const C = {};
function leggiColori() {
  const el = document.createElement('i'); el.style.display = 'none'; document.body.appendChild(el);
  for (const k of ['bg', 'ink', 'mute', 'line', 'cel', 'fe', 'edge', 'panel']) { el.style.color = `var(--${k})`; C[k] = getComputedStyle(el).color; }
  el.remove();
}

// ---------- Stato ----------
let N = [], E = [], byId = new Map(), adj = new Map();
let visN = [], visE = [], visSet = new Set();
let sel = null, hover = null, trovati = new Set();
let tr = d3.zoomIdentity, W = 0, H = 0, dpr = 1;
const F = {rel: new Set(RELK), tipo: new Set(TIPIK), reg: '', da: null, a: null};
const canvas = $('#c'), ctx = canvas.getContext('2d');
let sim;
const R = n => n.r / Math.sqrt(Math.max(1, tr.k));  // raggio nel mondo: ingrandendo, i nodi crescono meno dello zoom

// ---------- Dati ----------
fetch('contesti.json').then(r => { if (!r.ok) throw new Error(r.status); return r.json(); }).then(prepara).catch(err => {
  $('#conta').textContent = 'Non riesco a leggere contesti.json (' + err.message + ').';
});

function prepara(dati) {
  const el = dati.elementi, ids = new Map(el.map(e => [e.id, e]));
  const vista = new Map();  // legami senza doppioni: lo stesso legame è registrato su entrambi i capi
  const nc = new Map();
  for (const e of el) for (const r of e.relazioni) {
    const [s, t] = r.verso === '>' ? [e.id, r.id] : [r.id, e.id];
    const k = s + '|' + r.rel + '|' + t;
    if (!vista.has(k)) vista.set(k, {s, t, rel: r.rel});
    if (!ids.has(r.id) && !nc.has(r.id)) nc.set(r.id, r.nome);
  }
  const usati = new Set(); for (const l of vista.values()) { usati.add(l.s); usati.add(l.t); }
  for (const id of usati) {
    const e = ids.get(id);
    if (e) N.push({id, nome: e.nome, en: e.nome_en, tipo: e.tipo, descr: e.descr, quando: e.quando, luoghi: e.luoghi, corsia: e.corsia,
      da: e.quando.da, fine: e.quando.a ?? e.quando.da + APERTO, coll: true});
    else N.push({id, nome: nc.get(id) || id, coll: false});
  }
  N.forEach(n => byId.set(n.id, n));
  E = [...vista.values()].map(l => ({source: byId.get(l.s), target: byId.get(l.t), rel: l.rel}));
  for (const n of N) adj.set(n, []);
  for (const l of E) { adj.get(l.source).push(l); adj.get(l.target).push(l); }
  for (const n of N) { n.grado = adj.get(n).length; n.r = n.coll ? 3.6 + 2.2 * Math.sqrt(n.grado) : 3; }
  N.sort((a, b) => a.grado - b.grado);  // i più legati si disegnano per ultimi, sopra gli altri
  const nColl = N.filter(n => n.coll).length;
  $('#conta').innerHTML = `Le relazioni sono soltanto quelle dichiarate da Wikidata, e nessuna è dedotta da ArMoni: <b>${E.length} relazioni fra ${N.length} fenomeni</b> <span class="sub">(${nColl} collocati nell'atlante, ${N.length - nColl} citati da Wikidata ma non collocati, in grigio).</span> <span class="sub" id="visibili"></span>`;
  costruisciFiltri(dati);
  leggiURL();
  avvia();
}

// ---------- Filtri ----------
function costruisciFiltri() {
  const cr = d3.rollup(E, v => v.length, l => l.rel);
  $('#f-rel').insertAdjacentHTML('beforeend', RELK.map(k => `<label class="chk"><input type="checkbox" data-rel="${k}" checked> ${iconaTratto(k)} <span>${k}</span><span class="n">${cr.get(k) || 0}</span></label>`).join(''));
  const ct = d3.rollup(N.filter(n => n.coll), v => v.length, n => n.tipo);
  $('#f-tipo').insertAdjacentHTML('beforeend', TIPIK.map(k => `<label class="chk"><input type="checkbox" data-tipo="${k}" checked> ${iconaForma(TIPI[k])} <span>${PLURALE[k]}</span><span class="n">${ct.get(k) || 0}</span></label>`).join(''));
  const reg = d3.rollup(N.filter(n => n.coll), v => v.length, n => n.corsia);
  $('#f-reg').insertAdjacentHTML('beforeend', [...reg].sort((a, b) => b[1] - a[1]).map(([k, v]) => `<option value="${esc(k)}">${esc(k)} (${v})</option>`).join(''));
  document.querySelectorAll('[data-rel]').forEach(i => i.onchange = () => { i.checked ? F.rel.add(i.dataset.rel) : F.rel.delete(i.dataset.rel); aggiorna(); });
  document.querySelectorAll('[data-tipo]').forEach(i => i.onchange = () => { i.checked ? F.tipo.add(i.dataset.tipo) : F.tipo.delete(i.dataset.tipo); aggiorna(); });
  $('#f-reg').onchange = e => { F.reg = e.target.value; aggiorna(); };
  const anno = v => v.trim() === '' || !Number.isFinite(+v) ? null : Math.round(+v);
  $('#f-da').onchange = e => { F.da = anno(e.target.value); aggiorna(); };
  $('#f-a').onchange = e => { F.a = anno(e.target.value); aggiorna(); };
  $('#f-reset').onclick = () => {
    F.rel = new Set(RELK); F.tipo = new Set(TIPIK); F.reg = ''; F.da = F.a = null;
    document.querySelectorAll('[data-rel],[data-tipo]').forEach(i => { i.checked = true; });
    $('#f-reg').value = ''; $('#f-da').value = $('#f-a').value = '';
    aggiorna();
  };
  $('#leg').innerHTML = `<div><b>Contesti</b>${TIPIK.map(k => `<span>${iconaForma(TIPI[k])} ${k} (${TIPI[k]})</span>`).join('')}<span>${iconaForma('cerchio', true)} non collocato nell'atlante</span></div>
   <div><b>Relazioni, secondo Wikidata</b>${RELK.map(k => `<span>${iconaTratto(k)} ${k} (${REL[k].tratto})</span>`).join('')}</div>
   <div style="max-width:190px"><b>Come si legge</b><span style="white-space:normal">A → B: «A è influenzato da B», «A è parte di B», «A segue B». La grandezza conta i legami.</span></div>`;
  document.getElementById('nomi').innerHTML = N.map(n => `<option value="${esc(n.nome)}"></option>`).join('');
}

function passa(n) {
  if (!n.coll) return true;  // decidono i vicini
  if (!F.tipo.has(n.tipo)) return false;
  if (F.reg && n.corsia !== F.reg) return false;
  if (F.da != null && n.fine < F.da) return false;
  if (F.a != null && n.da > F.a) return false;
  return true;
}
function filtra() {
  const ok = new Set(N.filter(n => n.coll && passa(n)));
  if (sel && sel.coll) ok.add(sel);  // la selezione resta visibile
  visE = E.filter(l => F.rel.has(l.rel) && (ok.has(l.source) || !l.source.coll) && (ok.has(l.target) || !l.target.coll)
    && (l.source.coll || l.target.coll || false));
  // un legame fra due capi non collocati non esiste nei dati, ma per sicurezza lo escludo sopra
  visSet = new Set(); for (const l of visE) { visSet.add(l.source); visSet.add(l.target); }
  if (sel) visSet.add(sel);
  visN = N.filter(n => visSet.has(n));
  const nc = visN.filter(n => n.coll).length;
  const tutti = visE.length === E.length && visN.length === N.length;
  const v = $('#visibili'); if (v) v.textContent = tutti ? '' : `Con i filtri: ${visE.length} relazioni fra ${visN.length} fenomeni (${nc} collocati).`;
  $('#vuoto').style.display = visE.length ? 'none' : 'flex';
}

// ---------- Simulazione ----------
function avvia() {
  leggiColori(); ridimensiona();
  filtra();
  // posizioni iniziali: a spirale, per un avvio stabile e ripetibile
  N.forEach((n, i) => { const a = i * 2.4, r = 9 * Math.sqrt(i + 1); n.x = r * Math.cos(a); n.y = r * Math.sin(a); });
  sim = d3.forceSimulation(visN)
    .force('link', d3.forceLink(visE).distance(l => 26 + l.source.r + l.target.r).strength(0.55))
    .force('charge', d3.forceManyBody().strength(n => n.coll ? -70 - 10 * n.grado : -28).distanceMax(420).theta(0.9))
    .force('collide', d3.forceCollide(n => n.r + 2))
    .force('x', d3.forceX(0).strength(0.045)).force('y', d3.forceY(0).strength(0.045))
    .alphaDecay(0.035).on('tick', disegna).on('end', () => { if (daAdattare) { daAdattare = false; adatta(); } });
  assesta(true);
  const z = d3.zoom().scaleExtent([0.15, 8]).on('zoom', e => { tr = e.transform; disegna(); });
  const drag = d3.drag().subject(e => { return trova(e.sourceEvent); })
    .on('start', e => { if (!RIDOTTO.matches) sim.alphaTarget(0.15).restart(); e.subject.fx = e.subject.x; e.subject.fy = e.subject.y; })
    .on('drag', e => { const [x, y] = tr.invert(d3.pointer(e.sourceEvent, canvas)); e.subject.fx = x; e.subject.fy = y; if (RIDOTTO.matches) { sim.tick(); disegna(); } })
    .on('end', e => { sim.alphaTarget(0); e.subject.fx = e.subject.fy = null; });
  z.on('start.utente', e => { if (e.sourceEvent) daAdattare = false; });
  d3.select(canvas).call(drag).call(z).on('dblclick.zoom', null);
  window._zoom = z;
  canvas.addEventListener('pointermove', e => {
    const n = trova(e); if (n !== hover) { hover = n; canvas.classList.toggle('su', !!n); disegna(); }
    const t = $('#tip');
    if (n) { const r = canvas.getBoundingClientRect(); t.style.display = 'block';
      t.innerHTML = `${esc(n.nome)}<br><span class="sub">${n.coll ? `${n.tipo}, ${fmtY(n.da)}${n.quando.a != null ? '–' + fmtY(n.quando.a) : ''}` : 'non collocato nell\'atlante'} · ${n.grado} legam${n.grado === 1 ? 'e' : 'i'}</span>`;
      const x = e.clientX - r.left + 14, y = e.clientY - r.top + 14; t.style.left = Math.min(x, r.width - t.offsetWidth - 8) + 'px'; t.style.top = Math.min(y, r.height - t.offsetHeight - 8) + 'px'; }
    else t.style.display = 'none';
  });
  canvas.addEventListener('pointerleave', () => { hover = null; $('#tip').style.display = 'none'; disegna(); });
  canvas.addEventListener('click', e => { const n = trova(e); seleziona(n, !!n); });
  canvas.addEventListener('keydown', e => {
    const passo = 60, sc = d3.select(canvas);
    const m = {ArrowLeft: [passo, 0], ArrowRight: [-passo, 0], ArrowUp: [0, passo], ArrowDown: [0, -passo]}[e.key];
    if (m) { e.preventDefault(); sc.call(z.translateBy, m[0] / tr.k, m[1] / tr.k); }
    else if (e.key === '+' || e.key === '=') { e.preventDefault(); sc.call(z.scaleBy, 1.3); }
    else if (e.key === '-') { e.preventDefault(); sc.call(z.scaleBy, 1 / 1.3); }
    else if (e.key === '0') { e.preventDefault(); adatta(); }
  });
  $('#z-piu').onclick = () => d3.select(canvas).transition().duration(RIDOTTO.matches ? 0 : 250).call(z.scaleBy, 1.4);
  $('#z-meno').onclick = () => d3.select(canvas).transition().duration(RIDOTTO.matches ? 0 : 250).call(z.scaleBy, 1 / 1.4);
  $('#z-adatta').onclick = () => adatta();
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && sel && document.activeElement !== $('#q')) seleziona(null); });
  // ricerca
  const q = $('#q');
  q.addEventListener('input', () => {
    const s = q.value.trim().toLowerCase();
    trovati = new Set(s.length < 2 ? [] : visN.filter(n => n.nome.toLowerCase().includes(s) || (n.en || '').toLowerCase().includes(s)));
    const esatto = N.find(n => n.nome.toLowerCase() === s);
    if (esatto) seleziona(esatto, true); else disegna();
  });
  q.addEventListener('keydown', e => {
    if (e.key !== 'Enter') return;
    const s = q.value.trim().toLowerCase(); if (!s) return;
    const cand = N.filter(n => n.nome.toLowerCase().includes(s) || (n.en || '').toLowerCase().includes(s))
      .sort((a, b) => (b.nome.toLowerCase().startsWith(s) - a.nome.toLowerCase().startsWith(s)) || (visSet.has(b) - visSet.has(a)) || b.grado - a.grado);
    if (cand[0]) seleziona(cand[0], true);
    else { $('#pan').innerHTML = `<p class="sub">Nessun fenomeno con relazioni si chiama «${esc(q.value)}».</p>`; }
  });
  RIDOTTO.addEventListener?.('change', () => assesta(false));
  matchMedia('(prefers-color-scheme: dark)').addEventListener?.('change', () => { leggiColori(); disegna(); });
  new ResizeObserver(() => { ridimensiona(); disegna(); }).observe($('#fig'));

  pannelloVuoto();
  if (avvio.id && byId.has(avvio.id)) seleziona(byId.get(avvio.id), true);
  else { if (avvio.id) $('#pan').insertAdjacentHTML('afterbegin', `<p class="sub">Il fenomeno ${esc(avvio.id)} non ha relazioni dichiarate su Wikidata, o non è fra i contesti dell'atlante.</p>`); adatta(true); }
}

// Con movimento ridotto la simulazione non si anima: si calcola tutta subito e si disegna una volta
function assesta(primo) {
  sim.nodes(visN); sim.force('link').links(visE);
  if (RIDOTTO.matches) { sim.stop(); sim.alpha(1); for (let i = 0; i < 260; i++) sim.tick(); sim.alpha(0.001); disegna(); }
  else if (primo) { sim.stop(); for (let i = 0; i < 300; i++) sim.tick(); sim.alpha(0.04).restart(); }
  else sim.alpha(0.5).restart();
}
let daAdattare = false;  // dopo un cambio di filtri, si reinquadra quando il grafo si ferma
function aggiorna() {
  filtra();
  trovati = new Set([...trovati].filter(n => visSet.has(n)));
  assesta(false);
  disegna();
  if (sel) return;
  if (RIDOTTO.matches) adatta(true); else daAdattare = true;
}

function ridimensiona() {
  const r = canvas.getBoundingClientRect(); dpr = window.devicePixelRatio || 1;
  W = r.width; H = r.height; canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
  if (!adattato) tr = d3.zoomIdentity.translate(W / 2, H / 2);
}
let adattato = false;
function inquadra(nodi, kmin, kmax, subito) {
  if (!nodi.length) return;
  const leg = $('#leg').offsetHeight + 24, top = 56, h = Math.max(120, H - leg - top);
  const [x0, x1] = d3.extent(nodi, n => n.x), [y0, y1] = d3.extent(nodi, n => n.y);
  const k = Math.max(kmin, Math.min(kmax, 0.9 * Math.min(W / (x1 - x0 + 60), h / (y1 - y0 + 60))));
  const t = d3.zoomIdentity.translate(W / 2, top + h / 2).scale(k).translate(-(x0 + x1) / 2, -(y0 + y1) / 2);
  adattato = true;
  d3.select(canvas).transition().duration(subito || RIDOTTO.matches ? 0 : 450).call(window._zoom.transform, t);
}
function adatta(subito) { inquadra(visN, 0.15, 4, subito); }
function centra(n) {
  const v = [n]; for (const l of adj.get(n)) for (const m of [l.source, l.target]) if (visSet.has(m)) v.push(m);
  inquadra(v, 1.2, 3);
}

function trova(ev) {
  if (!ev) return null;
  const [px, py] = d3.pointer(ev, canvas), [x, y] = tr.invert([px, py]);
  let best = null, bd = Infinity;
  for (const n of visN) { const d = Math.hypot(n.x - x, n.y - y), lim = R(n) + 4 / tr.k; if (d < lim && d < bd) { bd = d; best = n; } }
  return best;
}

// ---------- Disegno ----------
function disegna() {
  if (!W) return;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
  ctx.save(); ctx.translate(tr.x, tr.y); ctx.scale(tr.k, tr.k);
  const k = tr.k, vic = new Set();
  const fuoco = sel || hover;
  if (fuoco) { vic.add(fuoco); for (const l of adj.get(fuoco)) if (visSet.has(l.source) && visSet.has(l.target)) { vic.add(l.source); vic.add(l.target); } }
  // archi, raggruppati per tipo (un solo setLineDash per gruppo)
  ctx.lineCap = 'round';
  for (const pass of [0, 1]) for (const rk of RELK) {
    const g = visE.filter(l => l.rel === rk && (pass === 1) === !!(fuoco && (l.source === fuoco || l.target === fuoco)));
    if (!g.length) continue;
    ctx.setLineDash(REL[rk].dash.map(d => d / k));
    ctx.strokeStyle = pass ? C.ink : C.edge; ctx.fillStyle = ctx.strokeStyle;
    ctx.globalAlpha = pass ? 0.95 : fuoco ? 0.18 : 0.7;
    ctx.lineWidth = (pass ? 1.7 : 1.1) / k;
    for (const l of g) freccia(l, k);
  }
  ctx.setLineDash([]); ctx.globalAlpha = 1;
  // nodi
  for (const n of visN) {
    const spento = fuoco && !vic.has(n);
    ctx.globalAlpha = spento ? 0.25 : 1;
    forma(ctx, n.coll ? TIPI[n.tipo] : 'cerchio', n.x, n.y, R(n));
    if (n.coll) { ctx.fillStyle = C.cel; ctx.fill(); ctx.lineWidth = 1 / k; ctx.strokeStyle = C.bg; ctx.stroke(); }
    else { ctx.fillStyle = C.mute; ctx.globalAlpha *= 0.6; ctx.fill(); }
  }
  ctx.globalAlpha = 1;
  // anelli: trovati (ricerca), selezione (rosso ferro)
  for (const n of trovati) { forma(ctx, n.coll ? TIPI[n.tipo] : 'cerchio', n.x, n.y, R(n) + 4 / k); ctx.lineWidth = 1.5 / k; ctx.strokeStyle = C.ink; ctx.setLineDash([2 / k, 2 / k]); ctx.stroke(); }
  ctx.setLineDash([]);
  if (sel && visSet.has(sel)) { forma(ctx, sel.coll ? TIPI[sel.tipo] : 'cerchio', sel.x, sel.y, R(sel) + 4 / k); ctx.lineWidth = 2.5 / k; ctx.strokeStyle = C.fe; ctx.stroke(); }
  // etichette: i più legati, sempre; tutti quando si ingrandisce; vicini della selezione
  ctx.textAlign = 'center'; ctx.textBaseline = 'top';
  const fs = 12.5 / k, pochi = visN.length < 80, soglia = pochi || k > 2.2 ? 0 : k > 1.3 ? 4 : 9;
  ctx.font = `500 ${fs}px Newsreader, Georgia, serif`;
  ctx.lineJoin = 'round';
  // candidati in ordine di importanza; un'etichetta che si sovrappone a una già scritta si omette
  const cand = [];
  for (const n of visN) {
    const forte = vic.has(n) || trovati.has(n);
    if (fuoco ? !forte && !(n.grado >= soglia && k > 1.3) : !(n.grado >= soglia && (n.coll || pochi || k > 2.2)) && !trovati.has(n)) continue;
    cand.push([n === sel ? 3 : n === hover ? 2.5 : trovati.has(n) ? 2 : forte ? 1 : 0, n, forte]);
  }
  cand.sort((a, b) => b[0] - a[0] || b[1].grado - a[1].grado);
  const posti = [], pad = 2 / k;
  for (const [, n, forte] of cand) {
    const w = ctx.measureText(n.nome).width, y = n.y + R(n) + 2 / k;
    const r = [n.x - w / 2 - pad, y - pad, n.x + w / 2 + pad, y + fs * 1.15 + pad];
    if (posti.some(q => r[0] < q[2] && r[2] > q[0] && r[1] < q[3] && r[3] > q[1])) continue;
    posti.push(r);
    ctx.globalAlpha = fuoco && !forte ? 0.35 : 1;
    ctx.lineWidth = 3 / k; ctx.strokeStyle = C.bg; ctx.strokeText(n.nome, n.x, y);
    ctx.fillStyle = n === sel ? C.fe : n.coll ? C.ink : C.mute; ctx.fillText(n.nome, n.x, y);
  }
  ctx.globalAlpha = 1;
  ctx.restore();
}
function freccia(l, k) {
  const s = l.source, t = l.target, dx = t.x - s.x, dy = t.y - s.y, d = Math.hypot(dx, dy) || 1;
  const ux = dx / d, uy = dy / d, a = 7 / k, w = 3.2 / k;
  const ex = t.x - ux * (R(t) + 1.5 / k), ey = t.y - uy * (R(t) + 1.5 / k);
  const sx = s.x + ux * R(s), sy = s.y + uy * R(s);
  if (d < R(s) + R(t) + a) return;
  ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(ex - ux * a * 0.8, ey - uy * a * 0.8); ctx.stroke();
  const dash = ctx.getLineDash(); ctx.setLineDash([]);
  ctx.beginPath(); ctx.moveTo(ex, ey); ctx.lineTo(ex - ux * a - uy * w, ey - uy * a + ux * w); ctx.lineTo(ex - ux * a + uy * w, ey - uy * a - ux * w); ctx.closePath(); ctx.fill();
  ctx.setLineDash(dash);
}

// ---------- Pannello ----------
function pannelloVuoto() {
  $('#pan').innerHTML = `<h3 style="margin-top:0">Come si usa</h3>
   <p>Fai clic su un fenomeno per leggere la sua scheda e i suoi legami. Trascina per spostare il grafo, usa la rotella o i pulsanti per ingrandire; con la tastiera, dal grafo, frecce, + e −.</p>
   <p>Ogni freccia è un'affermazione di Wikidata, e la scheda la riporta come tale. Dove Wikidata tace, il grafo non disegna nulla: l'assenza di un legame non vuol dire che il legame non esista.</p>
   <p class="sub">I nodi grigi sono fenomeni che Wikidata cita in un legame ma ai quali non dà data o luogo: per questo non sono nell'atlante.</p>`;
}
function seleziona(n, centrare) {
  sel = n || null;
  const u = new URL(location.href);
  if (sel) u.searchParams.set('id', sel.id); else u.searchParams.delete('id');
  history.replaceState(null, '', u);
  if (!sel) { pannelloVuoto(); aggiorna(); return; }
  if (!visSet.has(sel)) aggiorna(); else { filtra(); disegna(); }
  scheda(sel);
  if (centrare) centra(sel);
}
function scheda(n) {
  const wd = `https://www.wikidata.org/wiki/${encodeURIComponent(n.id)}`;
  const leg = adj.get(n).slice().sort((a, b) => RELK.indexOf(a.rel) - RELK.indexOf(b.rel));
  const righe = leg.map(l => {
    const dir = l.source === n, altro = dir ? l.target : l.source;
    const frase = dir ? l.rel : REL[l.rel].inv;
    const nascosto = !visSet.has(altro) || !F.rel.has(l.rel);
    return `<button type="button" class="rel${altro.coll ? '' : ' nc'}" data-id="${esc(altro.id)}">${iconaTratto(l.rel)} <span class="sub">${esc(frase)}</span> <i>${esc(altro.nome)}</i>${altro.coll ? '' : ' <span class="sub">· non collocato nell\'atlante</span>'}${nascosto ? ' <span class="sub">· nascosto dai filtri</span>' : ''}</button>`;
  }).join('');
  let h = `<button type="button" class="chiudi" id="chiudi" aria-label="Chiudi la scheda">Chiudi</button>
   <h2>${esc(n.nome)}</h2>`;
  if (n.coll) {
    const q = n.quando, luoghi = [...new Set(n.luoghi.map(l => l.oggi).filter(Boolean))];
    h += `${n.en && n.en !== n.nome ? `<div class="en">${esc(n.en)}</div>` : ''}
     <div class="tipo">${iconaForma(TIPI[n.tipo])} ${esc(n.tipo)}${n.descr ? ` · <span class="sub">${esc(n.descr)}</span>` : ''}</div>
     <div class="k">Date</div><div class="v">${q.a != null ? `${fmtY(q.da)}–${fmtY(q.a)}` : `dal ${fmtY(q.da)} <span class="sub">(fine non dichiarata)</span>`}</div>
     <div class="sub">${esc(q.metodo)}</div>
     <div class="k">Luogo, con il nome di oggi</div><div class="v">${luoghi.length ? luoghi.map(esc).join('; ') : '<span class="sub">non indicato</span>'}</div>
     <div class="k">Macro-regione</div><div class="v">${esc(n.corsia)}</div>`;
  } else {
    h += `<div class="tipo" style="color:var(--mute)">${iconaForma('cerchio', true)} non collocato nell'atlante</div>
     <p class="sub">Wikidata lo cita in un legame con un fenomeno dell'atlante, ma non gli dà una data o un luogo che permettano di collocarlo.</p>`;
  }
  h += `<h3>Relazioni, secondo Wikidata (${leg.length})</h3>
   <p class="sub" style="margin:0 0 4px">Secondo Wikidata, ${esc(n.nome)}…</p>${righe}
   <div class="acts">${n.coll ? `<a class="pri" href="index.html#ricerca&y=${n.da}&w=50&l=confini,origini,contesti,relazioni&p=mov:${encodeURIComponent(n.id)}">Apri nell'atlante</a>` : ''}
   <a href="${wd}" target="_blank" rel="noopener">${esc(n.id)} su Wikidata ↗</a></div>`;
  const p = $('#pan'); p.innerHTML = h; p.scrollTop = 0;
  $('#chiudi').onclick = () => { seleziona(null); canvas.focus(); };
  p.querySelectorAll('.rel').forEach(b => b.onclick = () => seleziona(byId.get(b.dataset.id), true));
}

// ---------- Parametri URL ----------
const avvio = {};
function leggiURL() {
  const q = new URLSearchParams(location.search);
  if (q.get('id') && /^Q\d+$/.test(q.get('id'))) avvio.id = q.get('id');
  const y = q.get('y'), w = q.get('w');
  if (y !== null && y !== '' && Number.isFinite(+y)) {
    const ww = w !== null && w !== '' && Number.isFinite(+w) ? Math.abs(+w) : 50;
    F.da = Math.round(+y - ww); F.a = Math.round(+y + ww);
    $('#f-da').value = F.da; $('#f-a').value = F.a;
  }
}
