// paper.js — 小宇 · 纸片 MV. Everything looks cut from coloured paper: flat shapes with slightly uneven edges, a soft
// shadow under every piece, and a fibre texture over the frame. The canvas is 1920×1080; shots draw in 960×540 units.

const VW = 960, VH = 540, SCALE = 2;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const eout = t => 1 - Math.pow(1 - clamp(t), 3);
const ein = t => Math.pow(clamp(t), 3);
const H = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const TAU = Math.PI * 2;
const INK = '#3A2E3A';
const FONT = 'XiaoyuPaper';
const hex = s => [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16)];
const mixHex = (a, b, p) => { const A = hex(a), B = hex(b); return '#' + A.map((v, i) => Math.round(lerp(v, B[i], clamp(p))).toString(16).padStart(2, '0')).join(''); };

// ---------------------------------------------------------------- the paper look
// depth d: how far a piece floats above the one below it (bigger, softer shadow)
function lift(g, d = 1) { g.shadowColor = 'rgba(58,34,48,0.30)'; g.shadowBlur = 5 * d * SCALE; g.shadowOffsetX = 1.2 * d * SCALE; g.shadowOffsetY = 2.2 * d * SCALE; }
function flat(g) { g.shadowColor = 'rgba(0,0,0,0)'; g.shadowBlur = 0; g.shadowOffsetX = 0; g.shadowOffsetY = 0; }
// cut a shape out of paper: build the path with fn, fill it with a shadow under it
function cut(g, col, d, fn) { g.beginPath(); fn(g); if (d) lift(g, d); g.fillStyle = col; g.fill(); flat(g); }
// a closed smooth curve through the midpoints of pts
function smooth(g, pts) {
  const n = pts.length, m = i => [(pts[i][0] + pts[(i + 1) % n][0]) / 2, (pts[i][1] + pts[(i + 1) % n][1]) / 2];
  const p = m(n - 1); g.moveTo(p[0], p[1]);
  for (let i = 0; i < n; i++) { const q = m(i); g.quadraticCurveTo(pts[i][0], pts[i][1], q[0], q[1]); }
  g.closePath();
}
// a roundish piece with a hand-cut wobble
function blob(g, cx, cy, rx, ry, seed = 1, wob = .05, n = 22) {
  const pts = [];
  for (let i = 0; i < n; i++) { const a = i / n * TAU, r = 1 + (H(seed * 31 + i) - .5) * 2 * wob; pts.push([cx + Math.cos(a) * rx * r, cy + Math.sin(a) * ry * r]); }
  smooth(g, pts);
}
// straight cut edges with a tiny wobble; long edges are split so they are not perfectly straight
function poly(g, pts, seed = 0, jit = .7) {
  const out = [];
  for (let i = 0; i < pts.length; i++) {
    const [x0, y0] = pts[i], [x1, y1] = pts[(i + 1) % pts.length], L = Math.hypot(x1 - x0, y1 - y0), n = Math.max(1, Math.round(L / 40));
    for (let k = 0; k < n; k++) { const f = k / n; out.push([lerp(x0, x1, f) + (H(seed + i * 7.3 + k) - .5) * jit, lerp(y0, y1, f) + (H(seed + i * 3.1 + k + 9) - .5) * jit]); }
  }
  out.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath();
}
const rectP = (g, x, y, w, h, seed = 0, jit = .7) => poly(g, [[x, y], [x + w, y], [x + w, y + h], [x, y + h]], seed, jit);
const paperRect = (g, x, y, w, h, col, d = 1, seed = 0) => cut(g, col, d, q => rectP(q, x, y, w, h, seed));
const paperBlob = (g, cx, cy, rx, ry, col, d = 1, seed = 1, wob = .05) => cut(g, col, d, q => blob(q, cx, cy, rx, ry, seed, wob));
const paperCircle = (g, cx, cy, r, col, d = 1, seed = 1) => cut(g, col, d, q => blob(q, cx, cy, r, r, seed, .025, 20));
function heartPath(g, cx, cy, s) {
  g.moveTo(cx, cy + s * .95);
  g.bezierCurveTo(cx - s * 1.25, cy + s * .2, cx - s * 1.1, cy - s * .95, cx - s * .45, cy - s * .9);
  g.bezierCurveTo(cx - s * .15, cy - s * .88, cx, cy - s * .6, cx, cy - s * .45);
  g.bezierCurveTo(cx, cy - s * .6, cx + s * .15, cy - s * .88, cx + s * .45, cy - s * .9);
  g.bezierCurveTo(cx + s * 1.1, cy - s * .95, cx + s * 1.25, cy + s * .2, cx, cy + s * .95);
  g.closePath();
}
const paperHeart = (g, cx, cy, s, col, d = 1) => { cut(g, col, d, q => heartPath(q, cx, cy, s)); cut(g, 'rgba(255,255,255,0.35)', 0, q => q.ellipse(cx - s * .55, cy - s * .45, s * .18, s * .12, -.6, 0, TAU)); };
function starPath(g, cx, cy, r, n = 5, inner = .45, rot = -Math.PI / 2) { for (let i = 0; i < n * 2; i++) { const a = rot + i / (n * 2) * TAU, rr = i % 2 ? r * inner : r; i ? g.lineTo(cx + Math.cos(a) * rr, cy + Math.sin(a) * rr) : g.moveTo(cx + Math.cos(a) * rr, cy + Math.sin(a) * rr); } g.closePath(); }
const paperStar = (g, cx, cy, r, col, d = .6, rot) => cut(g, col, d, q => starPath(q, cx, cy, r, 5, .45, rot));
// a flat line, like a thread or a pencil stroke
function stroke(g, col, w, fn) { g.beginPath(); fn(g); g.strokeStyle = col; g.lineWidth = w; g.lineCap = 'round'; g.lineJoin = 'round'; g.stroke(); }
function gradV(g, stops, y0 = 0, y1 = VH, x = 0, w = VW) { const gr = g.createLinearGradient(0, y0, 0, y1); stops.forEach((c, i) => gr.addColorStop(i / (stops.length - 1), c)); g.fillStyle = gr; g.fillRect(x, y0, w, y1 - y0); }
const skyMix = (a, b, p) => a.map((c, i) => mixHex(c, b[i], p));

// the paper grain: fibres and specks, made once, laid over every frame
let _grain = null;
function grain(g) {
  if (!_grain) {
    _grain = document.createElement('canvas'); _grain.width = VW * SCALE; _grain.height = VH * SCALE;
    const q = _grain.getContext('2d');
    for (let i = 0; i < 9000; i++) { const x = H(i) * _grain.width, y = H(i + .5) * _grain.height, a = H(i + .3) * TAU, l = 2 + H(i + .7) * 7; q.strokeStyle = H(i + .9) > .5 ? 'rgba(90,60,40,0.045)' : 'rgba(255,255,255,0.07)'; q.lineWidth = 1; q.beginPath(); q.moveTo(x, y); q.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); q.stroke(); }
    for (let i = 0; i < 26000; i++) { q.fillStyle = H(i + .2) > .5 ? 'rgba(80,50,40,0.05)' : 'rgba(255,255,255,0.06)'; q.fillRect(H(i * 1.7) * _grain.width, H(i * 2.3) * _grain.height, 1.5, 1.5); }
    const v = q.createRadialGradient(_grain.width / 2, _grain.height / 2, _grain.height * .45, _grain.width / 2, _grain.height / 2, _grain.height * 1.05);
    v.addColorStop(0, 'rgba(40,20,30,0)'); v.addColorStop(1, 'rgba(40,20,30,0.28)'); q.fillStyle = v; q.fillRect(0, 0, _grain.width, _grain.height);
  }
  g.save(); g.setTransform(1, 0, 0, 1, 0, 0); g.drawImage(_grain, 0, 0); g.restore();
}
function fade(g, col, a) { if (a <= 0) return; g.save(); g.globalAlpha = clamp(a); g.fillStyle = col; g.fillRect(0, 0, VW, VH); g.restore(); }

// ---------------------------------------------------------------- the two paper puppets (original characters)
// 我: a boy with messy brown hair, a yellow T-shirt with a little cloud on it, jeans and red sneakers.
// 你: a girl with long black hair and a white flower, in a light-blue dress.
const CAST = {
  me: { skin: '#F6D2B4', skinSh: '#E8B898', hair: '#6A4428', hairHi: '#8A6040', top: '#F4C04E', topSh: '#DCA43A', leg: '#4A6EA8', shoe: '#E2553E', boy: true },
  you: { skin: '#FCE2CE', skinSh: '#F0C8B0', hair: '#2E2638', hairHi: '#4C4258', top: '#A6D6F0', topSh: '#86BCE0', leg: '#FCE2CE', shoe: '#FFFFFF', boy: false },
};
// arm poses: [upper arm angle, forearm angle], measured from straight down, positive = away from the body
const ARMS = {
  down: [.14, .08], out: [1.35, 1.5], reach: [.85, 1.15], up: [2.7, 2.95], hold: [.28, -1.25], chest: [.32, -2.05],
  face: [.62, -2.7], shh: [.48, -2.75], stop: [1.2, 2.45], behind: [-.25, -.3], phone: [.3, -1.85], umb: [.38, -.75], hug: [1.25, 1.9],
};
function armAngles(pose, T, side) {
  if (pose === 'wave') return [2.35, 2.55 + .45 * Math.sin(T * 11 + side)];
  if (pose === 'swing') return [.14 + .3 * Math.sin(T), .2 + .35 * Math.sin(T)];
  return ARMS[pose] || ARMS.down;
}
// Draw a puppet with its feet at (x, y). s: scale (1 = about 125 units tall).
// o: { aL, aR, walk (phase), sit, eyes, mouth, blush, back, look (-1..1), flip, alpha, tears, tint, dy, lean }
// Returns the hands (L, R), the face and the top of the head, in shot units.
function person(g, who, x, y, s, o = {}, T = 0) {
  const L = CAST[who], tint = o.tint;
  const C = c => tint || c;
  const out = {};
  g.save();
  if (o.alpha != null) g.globalAlpha *= clamp(o.alpha);
  const walk = o.walk != null ? Math.sin(o.walk * TAU) : 0, bob = o.walk != null ? -Math.abs(Math.cos(o.walk * TAU)) * 2.2 : 0;
  g.translate(x, y + (o.dy || 0) + bob * s); g.scale(s * (o.flip ? -1 : 1), s);
  if (o.lean) g.rotate(o.lean);
  const sit = !!o.sit, hipY = sit ? -18 : -34, shY = hipY - 38, headY = shY - 28;
  const toWorld = (px, py) => { const m = g.getTransform(); return [(m.a * px + m.c * py + m.e) / SCALE, (m.b * px + m.d * py + m.f) / SCALE]; };
  const d = 1.1;
  // long hair hangs behind everything
  if (!L.boy) cut(g, C(L.hair), d, q => { q.moveTo(-25, headY - 4); q.quadraticCurveTo(-30, headY + 30, -27, shY + 30); q.quadraticCurveTo(0, shY + 38, 27, shY + 30); q.quadraticCurveTo(30, headY + 30, 25, headY - 4); q.closePath(); });
  // legs
  const leg = (side) => {
    const ang = sit ? side * .18 : side * .04 + (side < 0 ? walk : -walk) * .38, len = sit ? 19 : 34;
    g.save(); g.translate(side * 8, hipY); g.rotate(-ang);
    cut(g, C(L.leg), d, q => q.roundRect(-5, -2, 10, len + 2, 5));
    if (L.boy) cut(g, C('#3E5E94'), 0, q => q.rect(-5, len - 6, 10, 3));
    cut(g, C(L.shoe), d, q => q.ellipse(side * 2.5, len + 1, 7.5, 4.6, 0, 0, TAU));
    g.restore();
  };
  leg(-1); leg(1);
  // arms that go behind the body
  const arm = (side, pose) => {
    const [a1, a2] = armAngles(pose, T, side), sx = side * 15;
    g.save(); g.translate(sx, shY + 5);
    const u = [Math.sin(a1) * side * 15, Math.cos(a1) * 15], f = [u[0] + Math.sin(a2) * side * 14, u[1] + Math.cos(a2) * 14];
    stroke(g, C(L.skin), 8.5, q => { q.moveTo(u[0], u[1]); q.lineTo(f[0], f[1]); });
    if (!tint) { lift(g, .8); stroke(g, C(L.skin), 8.5, q => { q.moveTo(u[0], u[1]); q.lineTo(f[0], f[1]); }); flat(g); }
    cut(g, C(L.top), d * .8, q => { q.moveTo(-5, -4); q.lineTo(5, -4); q.lineTo(u[0] + 5.5, u[1] * .7 + 1); q.lineTo(u[0] - 5.5, u[1] * .7 + 1); q.closePath(); });
    cut(g, C(L.skin), d * .6, q => q.arc(f[0], f[1], 5.2, 0, TAU));
    out[side < 0 ? (o.flip ? 'R' : 'L') : (o.flip ? 'L' : 'R')] = toWorld(f[0], f[1]);
    g.restore();
  };
  const behindL = (o.aL || 'down') === 'behind', behindR = (o.aR || 'down') === 'behind';
  if (behindL) arm(-1, 'behind'); if (behindR) arm(1, 'behind');
  // body: a T-shirt for him, a dress for her
  if (L.boy) {
    cut(g, C(L.top), d, q => { q.moveTo(-17, shY); q.quadraticCurveTo(0, shY - 4, 17, shY); q.lineTo(19, hipY + 2); q.quadraticCurveTo(0, hipY + 5, -19, hipY + 2); q.closePath(); });
    cut(g, C(L.leg), 0, q => q.rect(-18.5, hipY - 2, 37, 5));
    if (!tint) { cut(g, '#FFFFFF', .3, q => { q.arc(-4, shY + 18, 4.2, 0, TAU); q.arc(2, shY + 16, 5, 0, TAU); q.arc(7, shY + 19, 3.6, 0, TAU); q.rect(-4, shY + 18, 11, 4.6); }); }
  } else {
    cut(g, C(L.top), d, q => { q.moveTo(-14, shY); q.quadraticCurveTo(0, shY - 4, 14, shY); q.lineTo(13, shY + 18); q.lineTo(-13, shY + 18); q.closePath(); });
    cut(g, C(L.top), d, q => { q.moveTo(-13, shY + 16); q.lineTo(13, shY + 16); q.quadraticCurveTo(26, hipY + 4, 27, hipY + 10); q.quadraticCurveTo(0, hipY + 16, -27, hipY + 10); q.quadraticCurveTo(-26, hipY + 4, -13, shY + 16); q.closePath(); });
    if (!tint) { cut(g, C(L.topSh), 0, q => q.rect(-13, shY + 15, 26, 3)); for (const yy of [shY + 6, shY + 11]) cut(g, '#FFFFFF', 0, q => q.arc(0, yy, 1.3, 0, TAU)); }
  }
  // neck and head
  cut(g, C(L.skinSh), 0, q => q.rect(-4.5, shY - 7, 9, 9));
  if (L.boy) for (const sd of [-1, 1]) cut(g, C(L.skin), d * .6, q => q.arc(sd * 23, headY + 2, 5, 0, TAU));
  cut(g, C(o.back ? L.hair : L.skin), d, q => blob(q, 0, headY, 24, 23, who === 'me' ? 3 : 5, .02));
  out.face = toWorld(0, headY); out.top = toWorld(0, headY - 26);
  // hair
  if (L.boy) {
    cut(g, C(L.hair), d * .7, q => {
      q.moveTo(-25, headY + 2); q.quadraticCurveTo(-28, headY - 22, -6, headY - 27); q.lineTo(-4, headY - 34); q.lineTo(2, headY - 27); q.lineTo(9, headY - 32); q.lineTo(11, headY - 25);
      q.quadraticCurveTo(28, headY - 20, 25, headY + 2);
      if (o.back) { q.quadraticCurveTo(26, headY + 18, 0, headY + 20); q.quadraticCurveTo(-26, headY + 18, -25, headY + 2); }
      else { q.lineTo(20, headY - 6); q.lineTo(15, headY - 12); q.lineTo(9, headY - 5); q.lineTo(3, headY - 13); q.lineTo(-4, headY - 6); q.lineTo(-10, headY - 13); q.lineTo(-16, headY - 5); q.lineTo(-20, headY - 10); }
      q.closePath();
    });
    if (!tint) cut(g, L.hairHi, 0, q => q.ellipse(-8, headY - 19, 6, 2.2, -.3, 0, TAU));
  } else {
    cut(g, C(L.hair), d * .7, q => {
      q.moveTo(-26, headY + 16); q.quadraticCurveTo(-29, headY - 26, 0, headY - 26); q.quadraticCurveTo(29, headY - 26, 26, headY + 16);
      if (o.back) { q.quadraticCurveTo(0, headY + 26, -26, headY + 16); }
      else { q.lineTo(21, headY + 14); q.quadraticCurveTo(21, headY - 6, 3, headY - 12); q.quadraticCurveTo(-4, headY - 2, -12, headY - 6); q.quadraticCurveTo(-20, headY - 2, -21, headY + 14); }
      q.closePath();
    });
    if (!tint) { cut(g, L.hairHi, 0, q => q.ellipse(-9, headY - 19, 7, 2.4, -.3, 0, TAU)); for (let i = 0; i < 5; i++) cut(g, '#FFFFFF', .5, q => q.ellipse(17 + Math.cos(i / 5 * TAU) * 3.6, headY - 17 + Math.sin(i / 5 * TAU) * 3.6, 3, 3, 0, 0, TAU)); cut(g, '#F6CE4A', 0, q => q.arc(17, headY - 17, 2, 0, TAU)); }
  }
  // arms in front
  if (!behindL) arm(-1, o.aL || 'down'); if (!behindR) arm(1, o.aR || 'down');
  // the face
  if (!o.back) {
    if (tint) { if (o.tintEyes) for (const sd of [-1, 1]) cut(g, o.tintEyes, 0, q => q.ellipse(sd * 9, headY + 2, 3.4, 2.2, 0, 0, TAU)); }
    else face(g, L, headY, o, T);
  }
  g.restore();
  return out;
}
function face(g, L, hy, o, T) {
  const lk = clamp(o.look || 0, -1, 1) * 4, ey = hy + 2, my = hy + 12;
  let e = o.eyes || 'open';
  if (e === 'open' && ((T * .8 + (o.seed || 0)) % 3.4) < .12) e = 'closed';
  const line = (fn, w = 1.8) => stroke(g, INK, w, fn);
  for (const sd of [-1, 1]) {
    const ex = sd * 9 + lk;
    if (e === 'closed') line(q => { q.moveTo(ex - 4, ey); q.quadraticCurveTo(ex, ey + 3.5, ex + 4, ey); });
    else if (e === 'happy') line(q => { q.moveTo(ex - 4, ey + 1.5); q.quadraticCurveTo(ex, ey - 3.5, ex + 4, ey + 1.5); });
    else if (e === 'down') { line(q => { q.moveTo(ex - 4, ey + 1); q.quadraticCurveTo(ex, ey + 3.5, ex + 4, ey + 1); }); line(q => { q.moveTo(ex - 4, ey - 4 + (sd < 0 ? 1.2 : 0)); q.lineTo(ex + 4, ey - 4 + (sd > 0 ? 1.2 : 0)); }, 1.3); }
    else if (e === 'sad') { cut(g, INK, 0, q => q.ellipse(ex, ey + .6, 2.6, 3.2, 0, 0, TAU)); line(q => { q.moveTo(ex - 4, ey - 6 + (sd > 0 ? 2 : 0)); q.lineTo(ex + 4, ey - 6 + (sd < 0 ? 2 : 0)); }, 1.4); }
    else if (e === 'strain') line(q => { q.moveTo(ex - 4 * sd, ey - 3); q.lineTo(ex + 3 * sd, ey); q.lineTo(ex - 4 * sd, ey + 3); });
    else if (e === 'sparkle') { cut(g, '#2C3A66', 0, q => q.ellipse(ex, ey, 4.6, 6, 0, 0, TAU)); cut(g, '#5A8AD0', 0, q => q.ellipse(ex, ey + 2.6, 3.2, 2.4, 0, 0, TAU)); cut(g, '#FFFFFF', 0, q => q.arc(ex - 1.6, ey - 2.4, 1.8, 0, TAU)); cut(g, '#FFFFFF', 0, q => q.arc(ex + 1.8, ey + 2.2, .9, 0, TAU)); }
    else { const big = e === 'wide' ? 1.3 : 1; cut(g, INK, 0, q => q.ellipse(ex, ey, 3 * big, 3.9 * big, 0, 0, TAU)); cut(g, '#FFFFFF', 0, q => q.arc(ex - 1, ey - 1.5 * big, 1.2 * big, 0, TAU)); }
  }
  if (o.blush) for (const sd of [-1, 1]) cut(g, 'rgba(248,140,150,0.55)', 0, q => q.ellipse(sd * 15 + lk * .6, hy + 9, 4.6, 2.6, 0, 0, TAU));
  const m = o.mouth || 'smile', mx = lk * .8;
  if (m === 'smile') line(q => { q.moveTo(mx - 4, my - 1); q.quadraticCurveTo(mx, my + 3, mx + 4, my - 1); }, 1.6);
  else if (m === 'grin') { cut(g, '#7A3040', 0, q => { q.moveTo(mx - 6, my - 2); q.quadraticCurveTo(mx, my + 8, mx + 6, my - 2); q.closePath(); }); cut(g, '#F27A8A', 0, q => q.ellipse(mx, my + 2.4, 2.6, 1.4, 0, 0, TAU)); }
  else if (m === 'open') cut(g, '#7A3040', 0, q => q.ellipse(mx, my + .5, 2.8, 3.2, 0, 0, TAU));
  else if (m === 'o') cut(g, '#7A3040', 0, q => q.arc(mx, my, 2, 0, TAU));
  else if (m === 'flat') line(q => { q.moveTo(mx - 3.5, my); q.lineTo(mx + 3.5, my); }, 1.5);
  else if (m === 'frown') line(q => { q.moveTo(mx - 4, my + 1.5); q.quadraticCurveTo(mx, my - 2, mx + 4, my + 1.5); }, 1.6);
  else if (m === 'tremble') line(q => { q.moveTo(mx - 5, my); for (let i = 1; i <= 5; i++) q.lineTo(mx - 5 + i * 2, my + (i % 2 ? -1.5 : 1.5)); }, 1.4);
  if (o.tears) for (const sd of [-1, 1]) for (let k = 0; k < 2; k++) { const p = (T * 1.2 + k * .5 + (sd > 0 ? .3 : 0)) % 1; cut(g, '#8CCBF0', 0, q => { const tx = sd * 10 + lk, ty = ey + 5 + p * 22; q.moveTo(tx, ty - 3); q.quadraticCurveTo(tx + 2.4, ty + 1, tx, ty + 2.6); q.quadraticCurveTo(tx - 2.4, ty + 1, tx, ty - 3); }); }
  void L;
}

// ---------------------------------------------------------------- subtitles: the user's own .lrc lines on a strip of paper
// The lit part sweeps across the line at the pace of the sung syllables that analyze.py timed with Whisper.
function subtitleAt(t) {
  if (typeof USER_LYRICS === 'undefined' || !USER_LYRICS.length) return null;
  for (let i = USER_LYRICS.length - 1; i >= 0; i--) {
    const L = USER_LYRICS[i], next = USER_LYRICS[i + 1];
    if (t >= L.t - .2) {
      const end = Math.min(next ? next.t - .08 : DUR, L.t + 9);
      if (t > end || !L.text) return null;
      const n = [...L.text].length;
      let ws = BEATMAP.words.filter(w => w >= L.t - .35 && w < end - .1);
      if (ws.length < 2 || ws.length < n / 4) ws = [L.t, Math.min(end - .4, L.t + n * .42)];
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
  const inA = eout(seg(t, s.show, s.show + .3)), outA = clamp((s.end - t) / .25);
  g.save(); g.font = `30px ${FONT}`; g.textBaseline = 'middle';
  const tw = g.measureText(s.text).width, bw = tw + 56, bh = 50, cx = VW / 2, cy = VH - 46 + (1 - inA) * 16;
  g.globalAlpha = inA * outA;
  g.translate(cx, cy); g.rotate((H(s.idx) - .5) * .03);
  // a torn strip of paper with a bit of tape
  cut(g, th.paper, 1.2, q => { const pts = []; const n = 14; for (let i = 0; i <= n; i++) pts.push([-bw / 2 + i / n * bw, -bh / 2 + (H(s.idx * 9 + i) - .5) * 3]); for (let i = n; i >= 0; i--) pts.push([-bw / 2 + i / n * bw, bh / 2 + (H(s.idx * 5 + i + 30) - .5) * 4]); pts.forEach(([x, y], i) => i ? q.lineTo(x, y) : q.moveTo(x, y)); q.closePath(); });
  cut(g, 'rgba(255,248,220,0.6)', .3, q => { q.save(); q.translate(-bw / 2 + 8, -bh / 2 + 2); q.rotate(-.5); q.rect(-14, -6, 28, 12); q.restore(); });
  // characters drop in one by one, then the sung part lights up
  let x = -tw / 2;
  for (let i = 0; i < chars.length; i++) {
    const cw = g.measureText(chars[i]).width, a = eout(seg(t, s.show + i * .03, s.show + i * .03 + .18));
    g.save(); g.translate(x + cw / 2, (1 - a) * -10); g.globalAlpha *= a; g.fillStyle = th.dim; g.textAlign = 'center'; g.fillText(chars[i], 0, 2); g.restore();
    x += cw;
  }
  if (p > 0) { g.save(); g.beginPath(); g.rect(-tw / 2 - 2, -bh / 2, tw * p + 2, bh); g.clip(); g.fillStyle = th.lit; g.textAlign = 'left'; g.fillText(s.text, -tw / 2, 2); g.restore(); }
  if (p > 0 && p < 1) { const bob = Math.sin(t * 7) * 2.5; noteShape(g, bw / 2 - 2, -bh / 2 - 6 + bob, 9, th.lit); }
  g.restore();
}
function noteShape(g, x, y, s, col) { cut(g, col, .5, q => { q.ellipse(x - s * .35, y + s * .55, s * .42, s * .3, -.4, 0, TAU); q.rect(x - .06 * s, y - s * .6, s * .14, s * 1.15); q.moveTo(x - .06 * s, y - s * .6); q.quadraticCurveTo(x + s * .5, y - s * .45, x + s * .45, y - s * .05); q.lineTo(x + .08 * s, y - s * .3); q.closePath(); }); }
