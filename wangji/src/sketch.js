// sketch.js — 给我一个理由忘记 · 铅笔 MV. The present is drawn in pencil on warm paper; memories, lights and the one red
// winter coat are washed in with watercolour. Pencil lines "boil" like hand-drawn animation: they get a new wobble
// twelve times a second. The canvas is 1920×1080; shots draw in 960×540 units.

const VW = 960, VH = 540, SCALE = 2;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const eout = t => 1 - Math.pow(1 - clamp(t), 3);
const H = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const TAU = Math.PI * 2;
const PAPER = '#F3EEE4', GRAPH = '#3A3840', RED = '#B8323A', FONT = 'WangjiHand';
const hex = s => [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16)];
const mixHex = (a, b, p) => { const A = hex(a), B = hex(b); return '#' + A.map((v, i) => Math.round(lerp(v, B[i], clamp(p))).toString(16).padStart(2, '0')).join(''); };

// ---------------------------------------------------------------- pencil
let BOIL = 0;          // which wobble we are on (floor(t * 12)), set by drawFrame
let ALPHA = 1;         // a multiplier for everything drawn, for ghosts and fades
const J = i => H(i * 13.7 + BOIL * 7.31) - .5;
function withAlpha(a, fn) { const k = ALPHA; ALPHA *= clamp(a); if (ALPHA > .003) fn(); ALPHA = k; }
// points along shapes, dense enough for the wobble to read as a hand-drawn line
const linePts = (x0, y0, x1, y1, n = 0) => { n = n || Math.max(2, Math.round(Math.hypot(x1 - x0, y1 - y0) / 14)); return Array.from({ length: n + 1 }, (_, i) => [lerp(x0, x1, i / n), lerp(y0, y1, i / n)]); };
const ellPts = (cx, cy, rx, ry, a0 = 0, a1 = TAU, n = 0) => { n = n || Math.max(8, Math.round((rx + ry) * Math.abs(a1 - a0) / 14)); return Array.from({ length: n + 1 }, (_, i) => { const a = lerp(a0, a1, i / n); return [cx + Math.cos(a) * rx, cy + Math.sin(a) * ry]; }); };
const bezPts = (p0, p1, p2, p3, n = 10) => Array.from({ length: n + 1 }, (_, i) => { const t = i / n, u = 1 - t; return [u * u * u * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t * t * t * p3[0], u * u * u * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t * t * t * p3[1]]; });
// a smooth closed (or open) curve through control points (Catmull-Rom), sampled densely
function curvePts(P, closed = true, per = 5) {
  const n = P.length, out = [], at = i => P[closed ? (i + n) % n : clamp(i, 0, n - 1)];
  for (let i = 0; i < (closed ? n : n - 1); i++) {
    const p0 = at(i - 1), p1 = at(i), p2 = at(i + 1), p3 = at(i + 2);
    for (let k = 0; k < per; k++) { const t = k / per, t2 = t * t, t3 = t2 * t; out.push([0, 1].map(d => .5 * (2 * p1[d] + (-p0[d] + p2[d]) * t + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t2 + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t3))); }
  }
  if (!closed) out.push(P[n - 1]);
  return out;
}
const rectPts = (x, y, w, h) => [...linePts(x, y, x + w, y), ...linePts(x + w, y, x + w, y + h).slice(1), ...linePts(x + w, y + h, x, y + h).slice(1), ...linePts(x, y + h, x, y).slice(1)];
// a pencil line through pts: a firm pass and a lighter second pass, both with the current wobble
function pencil(g, pts, o = {}) {
  const passes = o.passes ?? 2, j = o.j ?? 1.3, seed = o.seed ?? 0;
  g.lineCap = 'round'; g.lineJoin = 'round';
  for (let p = 0; p < passes; p++) {
    g.beginPath();
    for (let i = 0; i < pts.length; i++) { const [x, y] = pts[i], jx = J(seed + i * 3.1 + p * 17) * j, jy = J(seed + i * 5.3 + p * 29 + 1) * j; i ? g.lineTo(x + jx, y + jy) : g.moveTo(x + jx, y + jy); }
    if (o.closed) g.closePath();
    g.strokeStyle = o.col || GRAPH; g.globalAlpha = ALPHA * (o.a ?? .78) * (p ? .5 : 1); g.lineWidth = (o.w ?? 1.25) * (p ? .7 : 1);
    g.stroke();
  }
  g.globalAlpha = ALPHA;
}
// fill a shape with plain paper, so a drawing in front hides what is drawn behind it
function solid(g, pts, tone = PAPER) { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); g.fillStyle = tone; g.globalAlpha = ALPHA; g.fill(); }
const pLine = (g, x0, y0, x1, y1, o) => pencil(g, linePts(x0, y0, x1, y1), o);
const pRect = (g, x, y, w, h, o = {}) => pencil(g, rectPts(x, y, w, h), { ...o, closed: true });
const pEll = (g, cx, cy, rx, ry, o = {}) => pencil(g, ellPts(cx, cy, rx, ry), { ...o, closed: true });
// shading: parallel pencil strokes inside a clip path
function hatch(g, clipFn, box, o = {}) {
  const [x0, y0, x1, y1] = box, ang = o.ang ?? -.95, sp = o.sp ?? 5, cx = (x0 + x1) / 2, cy = (y0 + y1) / 2, L = Math.hypot(x1 - x0, y1 - y0) / 2 + 4;
  g.save(); g.beginPath(); clipFn(g); g.clip();
  const c = Math.cos(ang), s = Math.sin(ang);
  g.lineCap = 'round'; g.strokeStyle = o.col || GRAPH; g.lineWidth = o.w ?? .8;
  for (let d = -L, k = 0; d < L; d += sp, k++) {
    const ox = cx - s * d, oy = cy + c * d, jx = J(k * 2.3 + (o.seed || 0)) * 2, jy = J(k * 4.1 + (o.seed || 0)) * 2;
    g.globalAlpha = ALPHA * (o.a ?? .32) * (.75 + .5 * H(k + (o.seed || 0)));
    g.beginPath(); g.moveTo(ox - c * L + jx, oy - s * L + jy); g.lineTo(ox + c * L - jx, oy + s * L - jy); g.stroke();
  }
  g.restore(); g.globalAlpha = ALPHA;
}
// ---------------------------------------------------------------- watercolour
// a wash: three slightly different, translucent fills of the same shape, and a darker wet edge
function wash(g, pts, col, o = {}) {
  const layers = o.layers ?? 3, a = o.a ?? .2, sp = o.spread ?? 2.6, seed = o.seed ?? 0, slow = Math.floor(BOIL / 3);
  g.fillStyle = col;
  for (let L = 0; L < layers; L++) {
    g.beginPath();
    pts.forEach(([x, y], i) => { const dx = (H(seed + i * 1.7 + L * 31 + slow * .13) - .5) * sp * 2, dy = (H(seed + i * 2.9 + L * 17 + 5) - .5) * sp * 2; i ? g.lineTo(x + dx, y + dy) : g.moveTo(x + dx, y + dy); });
    g.closePath(); g.globalAlpha = ALPHA * a; g.fill();
  }
  if (o.edge !== false) { g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); g.strokeStyle = col; g.globalAlpha = ALPHA * a * .9; g.lineWidth = 1.4; g.stroke(); }
  g.globalAlpha = ALPHA;
}
const wRect = (g, x, y, w, h, col, o) => wash(g, rectPts(x, y, w, h), col, o);
const wEll = (g, cx, cy, rx, ry, col, o) => wash(g, ellPts(cx, cy, rx, ry), col, o);
// a soft blot of colour, for lights in the dark and colour bleeding into the paper
function blot(g, x, y, r, col, a = .35) { const gr = g.createRadialGradient(x, y, 0, x, y, r); const [R, G, B] = hex(col); gr.addColorStop(0, `rgba(${R},${G},${B},${a * ALPHA})`); gr.addColorStop(.6, `rgba(${R},${G},${B},${a * .45 * ALPHA})`); gr.addColorStop(1, `rgba(${R},${G},${B},0)`); g.fillStyle = gr; g.fillRect(x - r, y - r, r * 2, r * 2); }
function heartPts(cx, cy, s, n = 40) { return Array.from({ length: n }, (_, i) => { const t = i / n * TAU; return [cx + 16 * Math.pow(Math.sin(t), 3) * s / 16, cy - (13 * Math.cos(t) - 5 * Math.cos(2 * t) - 2 * Math.cos(3 * t) - Math.cos(4 * t)) * s / 16]; }); }

// ---------------------------------------------------------------- the paper
let _paper = null;
function paper(g, tone = PAPER) {
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.fillStyle = tone; g.fillRect(0, 0, VW * SCALE, VH * SCALE); g.restore();
}
function paperGrain(g) {
  if (!_paper) {
    _paper = document.createElement('canvas'); _paper.width = VW * SCALE; _paper.height = VH * SCALE;
    const q = _paper.getContext('2d');
    for (let i = 0; i < 70; i++) { const x = H(i * 3.3) * _paper.width, y = H(i * 5.7) * _paper.height, r = 60 + H(i) * 220, gr = q.createRadialGradient(x, y, 0, x, y, r); gr.addColorStop(0, 'rgba(150,120,80,0.035)'); gr.addColorStop(1, 'rgba(150,120,80,0)'); q.fillStyle = gr; q.fillRect(x - r, y - r, r * 2, r * 2); }
    for (let i = 0; i < 30000; i++) { q.fillStyle = H(i + .2) > .5 ? 'rgba(90,70,50,0.06)' : 'rgba(255,255,255,0.08)'; q.fillRect(H(i * 1.7) * _paper.width, H(i * 2.3) * _paper.height, 1.5, 1.5); }
    for (let i = 0; i < 5000; i++) { const x = H(i) * _paper.width, y = H(i + .5) * _paper.height, a = H(i + .3) * TAU, l = 3 + H(i + .7) * 9; q.strokeStyle = 'rgba(110,90,70,0.045)'; q.lineWidth = 1; q.beginPath(); q.moveTo(x, y); q.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); q.stroke(); }
    const v = q.createRadialGradient(_paper.width / 2, _paper.height / 2, _paper.height * .5, _paper.width / 2, _paper.height / 2, _paper.height * 1.05);
    v.addColorStop(0, 'rgba(60,40,30,0)'); v.addColorStop(1, 'rgba(60,40,30,0.22)'); q.fillStyle = v; q.fillRect(0, 0, _paper.width, _paper.height);
  }
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.drawImage(_paper, 0, 0); g.restore();
}
function fade(g, col, a) { if (a <= 0) return; g.save(); g.globalAlpha = clamp(a); g.fillStyle = col; g.fillRect(0, 0, VW, VH); g.restore(); g.globalAlpha = ALPHA; }

// ---------------------------------------------------------------- the two people (original characters)
// 我: long dark hair, a long grey coat.  你: short messy hair, the red winter coat he loved.
const CAST = {
  me: { hair: '#2E2A30', coat: '#8E8E9A', coatC: '#7A86A8', long: true },
  you: { hair: '#2C2824', coat: RED, coatC: RED, long: false },
};
const POSE = {
  down: [.12, .05], self: [.35, -2.05], chest: [.28, -2.3], reach: [.8, 1.05], up: [2.6, 2.85], phone: [.3, -2.55], face: [.55, -2.85],
  hold: [.25, -1.3], pocket: [.1, -.25], umb: [.35, -1.05], out: [1.3, 1.45], wave: [2.3, 2.6], hand: [.5, .5], behind: [-.2, -.2],
};
// Draw a person with feet at (x, y), s = scale (1 = 180 units tall).
// o: { aL, aR, walk (phase), sit, back, look (-1..1), tilt, eyes ('open'|'closed'|'down'|'none'), mouth, color (watercolour fills), alpha }
// Returns the hands, the head and the middle of the chest.
function figure(g, who, x, y, s, o = {}, T = 0) {
  const L = CAST[who], out = {};
  withAlpha(o.alpha ?? 1, () => {
    g.save(); g.translate(x, y); g.scale(s * (o.flip ? -1 : 1), s);
    const tw = (px, py) => { const m = g.getTransform(); return [(m.a * px + m.c * py + m.e) / SCALE, (m.b * px + m.d * py + m.f) / SCALE]; };
    const col = o.color, sit = o.sit, up = sit ? -36 : 0;
    const ph = o.walk != null ? o.walk * TAU : null, sw = ph != null ? Math.sin(ph) : 0;
    const bob = ph != null ? -Math.abs(Math.cos(ph)) * 2 : 0;
    g.translate(0, bob);
    const hipY = -88 - up, shY = -146 - up, headY = -168 - up, w = .9;
    // long hair behind
    if (L.long) { const hp = [...bezPts([-12, headY - 6], [-20, headY + 10], [-19, headY + 34], [-15, headY + 44], 8), ...bezPts([15, headY + 44], [19, headY + 34], [20, headY + 10], [12, headY - 6], 8)]; wash(g, hp, L.hair, { a: .38, seed: 3 }); pencil(g, hp, { w, seed: 2 }); }
    // legs
    for (const sd of [-1, 1]) {
      const swing = sd * sw * (sd < 0 ? 1 : 1), kx = sd * 7 + (ph != null ? swing * 9 : 0), fx = sd * 8 + (ph != null ? swing * 15 : 0), lift = ph != null ? Math.max(0, sd * Math.cos(ph)) * 4 : 0;
      const pts = sit ? [[sd * 7, hipY], [sd * 10, hipY + 6], [sd * 10, -2]] : [[sd * 6, hipY], [kx, -46 - lift], [fx, -3 - lift]];
      const wd = [5, 3.6, 2.8];
      pencil(g, pts.map(([a, b], i) => [a - wd[i], b]), { w, seed: 10 + sd }); pencil(g, pts.map(([a, b], i) => [a + wd[i], b]), { w, seed: 12 + sd });
      const [ex, ey] = pts[pts.length - 1];
      pencil(g, ellPts(ex + sd * 2, ey + 1, 7, 3.2, Math.PI, TAU), { w, seed: 14 + sd }); pLine(g, ex - 5 + sd * 2, ey + 1.5, ex + 9 + sd * 2, ey + 1.5, { w, seed: 16 + sd });
      const legPts = [...pts.map(([a, b], i) => [a - wd[i], b]), ...pts.slice().reverse().map(([a, b], i) => [a + wd[2 - i], b])];
      solid(g, legPts); wash(g, legPts, '#4A4A56', { a: col ? .22 : .1, seed: 20 + sd, edge: false });
    }
    // arms behind
    const arm = (sd, pose) => {
      const [a1, a2] = pose === 'wave' ? [2.3, 2.6 + .4 * Math.sin(T * 9)] : (POSE[pose] || POSE.down), sx = sd * 16, sy = shY + 3;
      const ex = sx + sd * Math.sin(a1) * 30, ey = sy + Math.cos(a1) * 30, hx = ex + sd * Math.sin(a2) * 27, hy = ey + Math.cos(a2) * 27;
      const n1 = [Math.cos(a1) * 4.5 * sd, -Math.sin(a1) * 4.5], n2 = [Math.cos(a2) * 4 * sd, -Math.sin(a2) * 4];
      const sleeve = [[sx - n1[0], sy - n1[1]], [ex - n1[0], ey - n1[1]], [hx - n2[0] * .8, hy - n2[1] * .8], [hx + n2[0] * .8, hy + n2[1] * .8], [ex + n1[0], ey + n1[1]], [sx + n1[0], sy + n1[1]]];
      solid(g, sleeve); wash(g, sleeve, col ? L.coatC : L.coat, { a: col ? .3 : .1, seed: 30 + sd });
      pencil(g, [sleeve[0], sleeve[1], sleeve[2]], { w, seed: 32 + sd }); pencil(g, [sleeve[5], sleeve[4], sleeve[3]], { w, seed: 34 + sd });
      pEll(g, hx + sd * Math.sin(a2) * 3, hy + Math.cos(a2) * 3, 3.6, 4.2, { w: .9, seed: 36 + sd });
      if (col) wEll(g, hx + sd * Math.sin(a2) * 3, hy + Math.cos(a2) * 3, 3.4, 4, '#F0C0A0', { a: .3, edge: false });
      out[(sd < 0) !== !!o.flip ? 'L' : 'R'] = tw(hx + sd * Math.sin(a2) * 3, hy + Math.cos(a2) * 3);
    };
    if (o.aL === 'behind') arm(-1, 'behind'); if (o.aR === 'behind') arm(1, 'behind');
    // the coat
    const hem = L.long ? -44 - up * .6 : -56 - up * .4;
    const half = L.long ? [[6, shY - 3], [16, shY + 2], [17, shY + 18], [12, hipY - 12], [15, hipY + 4], [22, hem]] : [[7, shY - 3], [19, shY + 2], [20, shY + 18], [17, hipY - 8], [19, hipY + 10], [20, hem]];
    const coat = curvePts([...half.map(([a, b]) => [-a, b]), ...half.slice().reverse()], true, 4);
    solid(g, coat); wash(g, coat, col ? L.coatC : L.coat, { a: col ? .3 : .1, seed: 40 });
    pencil(g, coat, { w: 1.15, closed: true, seed: 41 });
    if (!o.back) { pLine(g, 0, shY + 14, 0, hem - 1, { w: .8, a: .45, seed: 42 }); pencil(g, [[-7, shY - 2], [0, shY + 14], [7, shY - 2]], { w: .9, seed: 43 }); if (L.long) pLine(g, -12, hipY - 12, 12, hipY - 12, { w: .9, a: .55, seed: 45 }); else for (const by of [shY + 26, shY + 42, hipY - 2]) pEll(g, 2.5, by, 1, 1, { w: .9, a: .6, seed: by }); }
    if (!L.long) hatch(g, q => { q.beginPath(); coat.forEach(([a, b], i) => i ? q.lineTo(a + 4, b) : q.moveTo(a + 4, b)); q.closePath(); }, [-24, shY, 24, -56], { a: .18, sp: 6, seed: 44 });
    out.chest = tw(0, shY + 18);
    // neck and head
    pLine(g, -3.5, shY - 1, -3.5, headY + 11, { w, seed: 50 }); pLine(g, 3.5, shY - 1, 3.5, headY + 11, { w, seed: 51 });
    g.save(); g.translate(0, headY); g.rotate(o.tilt || 0);
    const lk = clamp(o.look || 0, -1, 1);
    solid(g, ellPts(lk * 1.5, 0, 11, 13)); solid(g, [[-3.5, 11], [3.5, 11], [3.5, 20], [-3.5, 20]]);
    if (col && !o.back) wEll(g, lk * 1.5, 1, 10.5, 12.5, '#F0C0A0', { a: .22, edge: false, seed: 52 });
    pencil(g, ellPts(lk * 1.5, 0, 11, 13), { w: 1.15, closed: true, seed: 53 });
    // hair
    if (L.long) {
      const top = [...ellPts(lk, -2, 12.5, 14, Math.PI * .95, TAU * 1.02, 12)];
      const hp = o.back ? ellPts(lk * .5, 0, 12.5, 14) : [...top, ...bezPts([12 + lk, 2], [6 + lk * 2, -9], [-2 + lk * 2, -9], [-10 + lk, 3], 6)];
      wash(g, hp, L.hair, { a: .45, seed: 54 }); pencil(g, hp, { w: 1, closed: true, seed: 55 });
      hatch(g, q => { q.beginPath(); hp.forEach(([a, b], i) => i ? q.lineTo(a, b) : q.moveTo(a, b)); q.closePath(); }, [-14, -16, 14, 6], { ang: -1.3, sp: 2.6, a: .4, seed: 56 });
    } else {
      const hp = o.back ? ellPts(lk * .5, -1, 12, 13.5) : [...ellPts(lk, -3, 12, 12, Math.PI * .98, TAU * 1.01, 12), [11 + lk, -4], [8 + lk * 2, -8], [5 + lk * 2, -4], [1 + lk * 2, -9], [-4 + lk * 2, -5], [-8 + lk, -9], [-11 + lk, -2]];
      wash(g, hp, L.hair, { a: .45, seed: 57 }); pencil(g, hp, { w: 1, closed: true, seed: 58 });
      hatch(g, q => { q.beginPath(); hp.forEach(([a, b], i) => i ? q.lineTo(a, b) : q.moveTo(a, b)); q.closePath(); }, [-14, -18, 14, 2], { ang: -1.2, sp: 2.6, a: .4, seed: 59 });
    }
    // a quiet face: eyes and a mouth, nothing more
    if (!o.back) {
      const e = o.eyes || 'open', ey = 2, my = 8.5;
      for (const sd of [-1, 1]) {
        const ex = sd * 4.6 + lk * 3.5;
        if (e === 'closed') pencil(g, ellPts(ex, ey - 1, 2.6, 1.6, .15 * Math.PI, .85 * Math.PI, 5), { w: 1, seed: 60 + sd });
        else if (e === 'down') { pencil(g, ellPts(ex, ey, 2.6, 1.4, .1 * Math.PI, .9 * Math.PI, 5), { w: 1, seed: 60 + sd }); pLine(g, ex - 2.6, ey - .6, ex + 2.6, ey - .6, { w: .8, a: .5, seed: 62 + sd }); }
        else if (e === 'open') { g.fillStyle = GRAPH; g.globalAlpha = ALPHA * .85; g.beginPath(); g.ellipse(ex, ey, 1.4, 1.8, 0, 0, TAU); g.fill(); g.globalAlpha = ALPHA; }
        if (o.tear && sd > 0) { const p = (T * .6) % 1; wash(g, ellPts(ex, ey + 4 + p * 10, 1.4, 2.2), '#6A9AD0', { a: .5, edge: false, layers: 2, spread: .4 }); }
      }
      const m = o.mouth || 'flat', mx = lk * 3;
      if (m === 'smile') pencil(g, ellPts(mx, my - 2, 3, 2.2, .2 * Math.PI, .8 * Math.PI, 6), { w: 1, seed: 64 });
      else if (m === 'sad') pencil(g, ellPts(mx, my + 2, 2.6, 1.8, 1.2 * Math.PI, 1.8 * Math.PI, 6), { w: 1, seed: 64 });
      else if (m === 'open') pEll(g, mx, my, 1.6, 1.8, { w: 1, seed: 64 });
      else if (m === 'laugh') { pencil(g, [[mx - 3.4, my - 1], ...ellPts(mx, my - 1, 3.4, 3, 0, Math.PI, 6), [mx - 3.4, my - 1]], { w: 1, seed: 64 }); if (col) wEll(g, mx, my + .6, 2.4, 1.6, '#C85A6A', { a: .5, edge: false }); }
      else if (m === 'flat') pLine(g, mx - 2.4, my, mx + 2.4, my, { w: .9, seed: 64 });
      if (col && o.blush) for (const sd of [-1, 1]) blot(g, sd * 7 + lk * 3, 6, 4, '#E07A8A', .45);
    }
    out.head = tw(0, 0);
    g.restore();
    // arms in front
    if (o.aL !== 'behind') arm(-1, o.aL || 'down'); if (o.aR !== 'behind') arm(1, o.aR || 'down');
    g.restore();
  });
  return out;
}
// a passer-by in the crowd: a few quick pencil strokes, no face
function passer(g, x, y, s, seed, walk, o = {}) {
  g.save(); g.translate(x, y); g.scale(s * (o.flip ? -1 : 1), s);
  const sw = walk != null ? Math.sin(walk * TAU) : 0, a = o.a ?? .55;
  pEll(g, 0, -168, 10, 12, { w: 1, a, seed });
  const hem = -60 - H(seed) * 22, coat = curvePts([[-6, -152], [-17, -146], [-18, -120], [-15, -100], [-18, hem], [18, hem], [15, -100], [18, -120], [17, -146], [6, -152]], true, 3);
  solid(g, coat); wash(g, coat, o.col || '#9A9AA6', { a: .14, seed });
  pencil(g, coat, { w: 1, a, closed: true, seed: seed + 1 });
  for (const sd of [-1, 1]) pencil(g, [[sd * 17, -142], [sd * (20 + sw * 3), -112], [sd * (19 - sw * 4), -84]], { w: 1.1, a, seed: seed + 8 + sd });
  for (const sd of [-1, 1]) pencil(g, [[sd * 7, -62], [sd * 7 + sd * sw * 9, -30], [sd * 8 + sd * sw * 15, 0]], { w: 1.4, a, seed: seed + 2 + sd });
  if (o.umb) { pencil(g, ellPts(14, -196, 42, 20, Math.PI, TAU, 10), { w: 1.1, a, seed: seed + 5 }); pLine(g, -28, -196, 56, -196, { w: 1, a, seed: seed + 6 }); pLine(g, 14, -196, 14, -128, { w: 1, a, seed: seed + 7 }); if (o.umbCol) wash(g, [...ellPts(14, -196, 42, 20, Math.PI, TAU, 10)], o.umbCol, { a: .25, seed }); }
  g.restore();
}

// ---------------------------------------------------------------- subtitles: the user's own .lrc lines, written in pencil
// The written words fill in with watercolour at the pace of the sung syllables that analyze.py timed with Whisper.
function subtitleAt(t) {
  if (typeof USER_LYRICS === 'undefined' || !USER_LYRICS.length) return null;
  for (let i = USER_LYRICS.length - 1; i >= 0; i--) {
    const L = USER_LYRICS[i], next = USER_LYRICS[i + 1];
    if (t >= L.t - .2) {
      const end = Math.min(next ? next.t - .08 : DUR, L.t + 10);
      if (t > end || !L.text) return null;
      const n = [...L.text].length;
      let ws = BEATMAP.words.filter(w => w >= L.t - .35 && w < end - .1);
      if (ws.length < 2 || ws.length < n / 4) ws = [L.t, Math.min(end - .4, L.t + n * .45)];
      return { text: L.text, show: L.t - .2, end, words: ws, idx: i };
    }
  }
  return null;
}
function subtitle(g, t, th) {
  const s = subtitleAt(t); if (!s) return;
  const chars = [...s.text], w = s.words;
  let p = 0;
  for (let i = 0; i < w.length; i++) if (t >= w[i]) { const nx = w[i + 1] ?? (w[i] + .6); p = (i + clamp((t - w[i]) / Math.max(.15, Math.min(1.2, nx - w[i])))) / w.length; }
  const outA = clamp((s.end - t) / .3);
  g.save(); g.font = `40px ${FONT}`; g.textBaseline = 'middle';
  const tw = g.measureText(s.text).width, cx = VW / 2, cy = VH - 48;
  withAlpha(outA, () => {
    // a rubbed-clean patch of paper behind the words, so they read over any drawing
    const gr = g.createRadialGradient(cx, cy, 10, cx, cy, tw * .62 + 30); gr.addColorStop(0, `rgba(243,238,228,${.86 * ALPHA})`); gr.addColorStop(.75, `rgba(243,238,228,${.7 * ALPHA})`); gr.addColorStop(1, 'rgba(243,238,228,0)');
    g.save(); g.translate(cx, cy); g.scale(1, .32); g.fillStyle = gr; g.fillRect(-tw - 60, -tw - 60, tw * 2 + 120, tw * 2 + 120); g.restore();
    // the words are written one after another, as if by hand
    let x = cx - tw / 2;
    for (let i = 0; i < chars.length; i++) {
      const cw = g.measureText(chars[i]).width, a = seg(t, s.show + i * .045, s.show + i * .045 + .16);
      if (a > 0) { g.globalAlpha = ALPHA * a * .92; g.fillStyle = th.ink; g.fillText(chars[i], x + (H(s.idx * 7 + i) - .5) * 1.5, cy + 1 + (H(s.idx * 3 + i) - .5) * 2.5); }
      x += cw;
    }
    if (p > 0) {
      g.save(); g.beginPath(); g.rect(cx - tw / 2 - 2, cy - 30, tw * p + 2, 60); g.clip();
      x = cx - tw / 2;
      for (let i = 0; i < chars.length; i++) { const cw = g.measureText(chars[i]).width; g.globalAlpha = ALPHA * .9; g.fillStyle = th.lit; g.fillText(chars[i], x + (H(s.idx * 7 + i) - .5) * 1.5, cy + 1 + (H(s.idx * 3 + i) - .5) * 2.5); x += cw; }
      g.restore();
      pencil(g, linePts(cx - tw / 2, cy + 22, cx - tw / 2 + tw * p, cy + 22 + (H(s.idx) - .5) * 3), { col: th.lit, a: .45, w: 1.4, passes: 1, seed: s.idx });
    }
  });
  g.restore(); g.globalAlpha = ALPHA;
}
