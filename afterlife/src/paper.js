// paper.js — a small cut-paper kit for Canvas. Every shape is a polygon; cut() draws it as a
// piece of coloured paper with a torn white edge, crayon grain, and a little stop-motion "boil"
// (the tear pattern changes 8 times a second, like re-shot paper cut-outs).

const VW = 1920, VH = 1080, TAU = Math.PI * 2;
const FONT = 'KuaiLe, sans-serif';
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const eout = t => 1 - Math.pow(1 - clamp(t), 3);
const back = t => { t = clamp(t); const c = 2.2; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
const H = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
let ctx, BOIL = 0, SEED = 0;

// ---------------------------------------------------------------- shapes (point lists)
function ell(cx, cy, rx, ry = rx, rot = 0, n = 0) {
  n = n || Math.max(16, Math.round((rx + ry) / 5)); const c = Math.cos(rot), s = Math.sin(rot), p = [];
  for (let i = 0; i < n; i++) { const a = i / n * TAU, x = Math.cos(a) * rx, y = Math.sin(a) * ry; p.push([cx + x * c - y * s, cy + x * s + y * c]); }
  return p;
}
function rect(x, y, w, h) { return [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]; }
function rrect(x, y, w, h, r) {
  const p = [], arc = (cx, cy, a0) => { for (let i = 0; i <= 5; i++) { const a = a0 + i / 5 * Math.PI / 2; p.push([cx + Math.cos(a) * r, cy + Math.sin(a) * r]); } };
  arc(x + w - r, y + r, -Math.PI / 2); arc(x + w - r, y + h - r, 0); arc(x + r, y + h - r, Math.PI / 2); arc(x + r, y + r, Math.PI);
  return p;
}
function capsule(x1, y1, x2, y2, r1, r2 = r1) {
  const a = Math.atan2(y2 - y1, x2 - x1), p = [];
  for (let i = 0; i <= 8; i++) { const q = a + Math.PI / 2 + i / 8 * Math.PI; p.push([x1 + Math.cos(q) * r1, y1 + Math.sin(q) * r1]); }
  for (let i = 0; i <= 8; i++) { const q = a - Math.PI / 2 + i / 8 * Math.PI; p.push([x2 + Math.cos(q) * r2, y2 + Math.sin(q) * r2]); }
  return p;
}
function star(cx, cy, R, r = R * .45, n = 5, rot = -Math.PI / 2) {
  const p = []; for (let i = 0; i < n * 2; i++) { const a = rot + i / (n * 2) * TAU, q = i % 2 ? r : R; p.push([cx + Math.cos(a) * q, cy + Math.sin(a) * q]); } return p;
}
function xform(pts, x, y, s = 1, rot = 0) { const c = Math.cos(rot), sn = Math.sin(rot); return pts.map(([a, b]) => [x + (a * c - b * sn) * s, y + (a * sn + b * c) * s]); }

// subdivide and jitter an outline so it reads as torn paper
function rough(pts, amp, seed, step = 12) {
  const out = []; let k = 0;
  for (let i = 0; i < pts.length; i++) {
    const [x0, y0] = pts[i], [x1, y1] = pts[(i + 1) % pts.length], L = Math.hypot(x1 - x0, y1 - y0), n = Math.max(1, Math.round(L / step));
    for (let j = 0; j < n; j++) { const u = j / n; k++; out.push([lerp(x0, x1, u) + (H(seed + k * 1.37) - .5) * amp, lerp(y0, y1, u) + (H(seed + k * 2.71 + 5) - .5) * amp]); }
  }
  return out;
}
function trace(pts) { ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.closePath(); }

// ---------------------------------------------------------------- textures
let GRAIN, CRAYON;
function makeTextures() {
  GRAIN = document.createElement('canvas'); GRAIN.width = VW; GRAIN.height = VH;
  const g = GRAIN.getContext('2d'), img = g.createImageData(VW, VH), d = img.data;
  let s = 12345; const r = () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
  for (let i = 0; i < d.length; i += 4) { const v = 225 + r() * 30; d[i] = v; d[i + 1] = v - 3; d[i + 2] = v - 10; d[i + 3] = 255; }
  g.putImageData(img, 0, 0);
  // paper fibres
  for (let i = 0; i < 2600; i++) { const x = r() * VW, y = r() * VH, a = r() * TAU, l = 6 + r() * 26; g.strokeStyle = `rgba(${r() < .5 ? '120,100,80' : '255,255,255'},${.08 + r() * .12})`; g.lineWidth = .6 + r(); g.beginPath(); g.moveTo(x, y); g.quadraticCurveTo(x + Math.cos(a + 1) * l * .5, y + Math.sin(a + 1) * l * .5, x + Math.cos(a) * l, y + Math.sin(a) * l); g.stroke(); }
  // soft blotches
  for (let i = 0; i < 90; i++) { const x = r() * VW, y = r() * VH, R = 60 + r() * 200, gr = g.createRadialGradient(x, y, 0, x, y, R); gr.addColorStop(0, `rgba(150,120,90,${r() * .07})`); gr.addColorStop(1, 'rgba(150,120,90,0)'); g.fillStyle = gr; g.fillRect(x - R, y - R, 2 * R, 2 * R); }
  CRAYON = document.createElement('canvas'); CRAYON.width = CRAYON.height = 320;
  const c = CRAYON.getContext('2d');
  for (let i = 0; i < 1400; i++) { const x = r() * 320, y = r() * 320, l = 8 + r() * 30, a = -0.9 + (r() - .5) * .5; c.strokeStyle = r() < .55 ? `rgba(255,255,255,${.1 + r() * .25})` : `rgba(0,0,0,${.05 + r() * .12})`; c.lineWidth = 1 + r() * 2.5; c.beginPath(); c.moveTo(x, y); c.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); c.stroke(); }
}

// ---------------------------------------------------------------- the cut
// o.edge: width of the white torn border (0 = none); o.tex: crayon grain strength; o.seed: tear pattern
function cut(pts, fill, o = {}) {
  const edge = o.edge ?? 7, seed = (o.seed ?? SEED++) * 13.7 + BOIL * 101.3;
  if (edge > 0) {
    const w = rough(pts, edge * 1.1, seed, 8);
    trace(w); ctx.fillStyle = o.edgeColor || '#FBF6EA'; ctx.strokeStyle = ctx.fillStyle; ctx.lineWidth = edge * 1.7; ctx.lineJoin = 'round'; ctx.stroke(); ctx.fill();
  }
  const p = rough(pts, o.jag ?? 2.2, seed + 50, 14);
  trace(p); ctx.fillStyle = fill; ctx.fill();
  if ((o.tex ?? .45) > 0) {
    ctx.save(); ctx.clip(); ctx.globalAlpha = o.tex ?? .45; ctx.fillStyle = ctx.createPattern(CRAYON, 'repeat');
    const bb = bounds(p); ctx.fillRect(bb[0], bb[1], bb[2] - bb[0], bb[3] - bb[1]); ctx.restore();
  }
  return p;
}
function bounds(p) { let a = 1e9, b = 1e9, c = -1e9, d = -1e9; for (const [x, y] of p) { a = Math.min(a, x); b = Math.min(b, y); c = Math.max(c, x); d = Math.max(d, y); } return [a, b, c, d]; }
// several shapes that share one white border (cut from one sheet)
function cutGroup(list, o = {}) {
  const edge = o.edge ?? 7, seed0 = (o.seed ?? SEED) * 13.7 + BOIL * 101.3;
  list.forEach(([pts], i) => { const w = rough(pts, edge * 1.1, seed0 + i * 7, 8); trace(w); ctx.fillStyle = ctx.strokeStyle = '#FBF6EA'; ctx.lineWidth = edge * 1.7; ctx.lineJoin = 'round'; ctx.stroke(); ctx.fill(); });
  list.forEach(([pts, fill], i) => cut(pts, fill, { edge: 0, seed: (o.seed ?? SEED) + i * 3, tex: o.tex }));
  SEED += list.length + 1;
}
// crayon line (for faces, hatching, doodles)
function line(pts, color, w, o = {}) {
  const seed = (o.seed ?? SEED++) + BOIL * 3.1, j = o.j ?? 1.2;
  ctx.strokeStyle = color; ctx.lineWidth = w; ctx.lineCap = ctx.lineJoin = 'round';
  ctx.beginPath(); pts.forEach(([x, y], i) => { const dx = (H(seed + i) - .5) * j, dy = (H(seed + i + 9) - .5) * j; i ? ctx.lineTo(x + dx, y + dy) : ctx.moveTo(x + dx, y + dy); }); if (o.close) ctx.closePath(); ctx.stroke();
}
function arcPts(cx, cy, r, a0, a1, n = 10, ry = r) { const p = []; for (let i = 0; i <= n; i++) { const a = lerp(a0, a1, i / n); p.push([cx + Math.cos(a) * r, cy + Math.sin(a) * ry]); } return p; }
function dot(x, y, r, color) { ctx.fillStyle = color; ctx.beginPath(); ctx.ellipse(x, y, r, r * 1.05, 0, 0, TAU); ctx.fill(); }

// handwriting: text revealed character by character; k = how much of the current char is inked (0..1)
function hand(text, x, y, size, color, shown, o = {}) {
  ctx.font = `${size}px ${FONT}`; ctx.fillStyle = color; ctx.textBaseline = 'alphabetic';
  const chars = [...text]; let cx = x, pen = null;
  const total = chars.reduce((s, c) => s + ctx.measureText(c).width + (o.sp ?? 0), 0) - (o.sp ?? 0);
  if (o.align === 'center') cx = x - total / 2;
  chars.forEach((c, i) => {
    const w = ctx.measureText(c).width, k = clamp(shown - i), wob = (H(i * 3.3 + (o.seed || 0)) - .5) * size * .05, rot = (H(i * 7.1 + (o.seed || 0)) - .5) * .08;
    if (k > 0) {
      ctx.save(); ctx.translate(cx + w / 2, y + wob); ctx.rotate(rot);
      if (k < 1) { ctx.beginPath(); ctx.rect(-w / 2 - 4, -size, (w + 8) * k, size * 1.4); ctx.clip(); pen = [cx + w * k, y - size * .35]; }
      ctx.fillText(c, -w / 2, 0); ctx.restore();
    }
    cx += w + (o.sp ?? 0);
  });
  return { pen, end: cx, total };
}

// light rays / action dashes around a point, pulsing on the beat
function dashes(cx, cy, r0, r1, n, color, w, rot = 0, o = {}) {
  for (let i = 0; i < n; i++) {
    const a = rot + i / n * TAU + (H(i + BOIL * .3) - .5) * .06, rr0 = r0 * (o.jit ? 1 + (H(i * 3) - .5) * o.jit : 1), rr1 = r1 * (o.jit ? 1 + (H(i * 5) - .5) * o.jit : 1);
    line([[cx + Math.cos(a) * rr0, cy + Math.sin(a) * rr0], [cx + Math.cos(a) * rr1, cy + Math.sin(a) * rr1]], color, w, { seed: i });
  }
}
