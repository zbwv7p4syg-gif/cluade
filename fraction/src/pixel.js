// pixel.js — everything is drawn on a 480×270 canvas with whole-pixel rectangles, then scaled up 4× with
// nearest-neighbour (in the page by CSS, in the video by ffmpeg). No anti-aliased shapes, only fillRect.

const PW = 480, PH = 270;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const eout = t => 1 - Math.pow(1 - clamp(t), 3);
const H = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const R = Math.round;
const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
const bayer = (x, y) => (BAYER[(y & 3) * 4 + (x & 3)] + .5) / 16;
const hex = s => [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16)];
const INK = '#1C1426';
const PIX_FONT = 'FractionPixel';

function rect(g, x, y, w, h, col) { g.fillStyle = col; g.fillRect(R(x), R(y), R(w), R(h)); }
function disc(g, cx, cy, r, col) {
  g.fillStyle = col; cx = R(cx); cy = R(cy);
  for (let y = -r; y <= r; y++) { const w = Math.floor(Math.sqrt(r * r - y * y) + .35); g.fillRect(cx - w, cy + y, w * 2 + 1, 1); }
}
function line(g, x0, y0, x1, y1, col) {
  g.fillStyle = col; x0 = R(x0); y0 = R(y0); x1 = R(x1); y1 = R(y1);
  const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let e = dx + dy;
  for (;;) { g.fillRect(x0, y0, 1, 1); if (x0 === x1 && y0 === y1) break; const e2 = 2 * e; if (e2 >= dy) { e += dy; x0 += sx; } if (e2 <= dx) { e += dx; y0 += sy; } }
}
function ring(g, cx, cy, r, col) { g.fillStyle = col; for (let a = 0; a < 360; a += 360 / (r * 7 + 8)) g.fillRect(R(cx + Math.cos(a * Math.PI / 180) * r), R(cy + Math.sin(a * Math.PI / 180) * r), 1, 1); }
// a translucent rectangle drawn as a 50% checker, the way old consoles did transparency
function checker(g, x, y, w, h, col, density = .5) {
  g.fillStyle = col; x = R(x); y = R(y);
  for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) if (bayer(x + i, y + j) < density) g.fillRect(x + i, y + j, 1, 1);
}

// ---------------------------------------------------------------- dithered gradients (cached as ImageData)
const gradCache = new Map();
function grad(g, stops, y0 = 0, y1 = PH) {
  const key = stops.join() + '|' + y0 + '|' + y1;
  let img = gradCache.get(key);
  if (!img) {
    img = new ImageData(PW, PH); const d = img.data, cols = stops.map(hex), n = cols.length - 1;
    for (let y = 0; y < PH; y++) {
      const tt = clamp((y - y0) / (y1 - y0)) * n, i = Math.min(n - 1, Math.floor(tt)), fr = tt - i;
      for (let x = 0; x < PW; x++) { const c = fr > bayer(x, y) ? cols[i + 1] : cols[i], o = (y * PW + x) * 4; d[o] = c[0]; d[o + 1] = c[1]; d[o + 2] = c[2]; d[o + 3] = 255; }
    }
    gradCache.set(key, img);
  }
  g.putImageData(img, 0, 0);
}

// ---------------------------------------------------------------- scenery bits
function cloud(g, x, y, s, col = '#FFFFFF', shade = '#D8E4F2') {
  disc(g, x, y + 2, R(5 * s), shade); disc(g, x + 8 * s, y, R(7 * s), shade); disc(g, x + 17 * s, y + 2, R(5 * s), shade);
  disc(g, x, y + 1, R(5 * s), col); disc(g, x + 8 * s, y - 1, R(7 * s), col); disc(g, x + 17 * s, y + 1, R(5 * s), col);
  rect(g, x, y + 2, 17 * s, R(4 * s), col);
}
function grassRow(g, t, y, col, seed, wind = 1, step = 5) {
  for (let x = (seed * 3) % step; x < PW; x += step) {
    const h = 2 + R(3 * H(x + seed)), lean = R(Math.sin(t * 3 + x * .07) * wind);
    g.fillStyle = col; g.fillRect(x, y - h, 1, h); g.fillRect(x + lean, y - h - 1, 1, 1);
  }
}
function stars(g, t, n, y1, seed = 1) {
  for (let i = 0; i < n; i++) {
    const tw = .5 + .5 * Math.sin(t * (1 + H(i + seed)) * 2 + i);
    if (tw < .25) continue;
    const x = R(H(i * 3 + seed) * PW), y = R(H(i * 7 + seed) * y1);
    rect(g, x, y, 1, 1, tw > .8 ? '#FFFFFF' : '#9FB0E0');
    if (H(i + 9) > .9 && tw > .85) { rect(g, x - 1, y, 3, 1, '#FFFFFF'); rect(g, x, y - 1, 1, 3, '#FFFFFF'); }
  }
}
function sparkle(g, x, y, s, col = '#FFFFFF') { x = R(x); y = R(y); rect(g, x - s, y, 2 * s + 1, 1, col); rect(g, x, y - s, 1, 2 * s + 1, col); }
function heart(g, x, y, k, col = '#FF5C8A') {
  const rows = ['.XX.XX.', 'XXXXXXX', 'XXXXXXX', '.XXXXX.', '..XXX..', '...X...'];
  rows.forEach((r, j) => [...r].forEach((c, i) => { if (c === 'X') rect(g, x + (i - 3) * k, y + (j - 3) * k, k, k, col); }));
  rect(g, x - 2 * k, y - 2 * k, k, k, '#FFD0DE');
}

// ---------------------------------------------------------------- the two Clawds
const ME = { col: '#D97757', dk: '#A84D33', lt: '#F2A283' };
const YOU = { col: '#F29BB8', dk: '#D0698D', lt: '#FCD2E0' };
const FRIEND = { col: '#7DBE7A', dk: '#4E8E4E', lt: '#B4E0AE' };
const PASSERS = [{ col: '#8FA8D8', dk: '#5C76A8', lt: '#C2D2F0' }, { col: '#E0C060', dk: '#B0903A', lt: '#F2DE9A' }, { col: '#B58ED0', dk: '#82609E', lt: '#D8C0EA' }, { col: '#9AA0A8', dk: '#6E747C', lt: '#C8CCD2' }];
const AGED = { col: '#C98E76', dk: '#986050', lt: '#E2B8A4' };

// Clawd on a pixel grid: x = centre, y = ground under the feet, k = pixels per body unit (body is 10×6 units).
// o: { look, walk, dy, flip, eyes: 'open'|'closed'|'happy'|'wide', aL/aR: 'down'|'up'|'out'|'wave', blush, bow, shoes,
//      sit, tear, aged, cane, alpha(dither), glow, hold: fn(g, hx, hy) }
function clawd(g, x, y, k, o = {}, T = 0) {
  const L = o.look || ME; x = R(x); y = R(y + (o.dy || 0));
  const f = o.flip ? -1 : 1, parts = [];
  const P = (ux, uy, uw, uh, col) => { let px = ux * k; const w = uw * k; if (f < 0) px = -px - w; parts.push([x + R(px), y + R(uy * k), Math.max(1, R(w)), Math.max(1, R(uh * k)), col]); };
  const px1 = 1 / k;
  // legs
  [-4, -2, 1, 3].forEach((lx, i) => {
    let lift = 0; if (o.walk != null) { const ph = ((o.walk + (i % 2 ? .5 : 0)) % 1 + 1) % 1; lift = ph < .5 ? Math.max(px1, .5) : 0; }
    if (o.sit) P(lx, -2, 1, 1.2, L.dk);           // sitting: short legs hanging under the body
    else P(lx, -2 - lift, 1, 2, L.dk);
    if (o.shoes) P(lx, o.sit ? -1.5 : -lift - .7, 1, .7, '#FFFFFF');
  });
  // arms
  const arm = (side, pose) => {
    const ax = side < 0 ? -7 : 5;
    if (pose === 'up') P(side < 0 ? -6 : 5, -10, 1, 3, L.col);
    else if (pose === 'out') P(ax, -5.5, 2, 1, L.col);
    else if (pose === 'wave') { if (Math.floor(T * 6) % 2) P(side < 0 ? -6 : 5, -10, 1, 3, L.col); else P(side < 0 ? -7 : 6, -9.5, 1, 3, L.col); }
    else if (pose === 'hug') P(side < 0 ? -6 : 3, -5, 3, 1, L.col);
    else P(side < 0 ? -6 : 5, -5, 1, 2, L.col);
  };
  arm(-1, o.aL || 'down'); arm(1, o.aR || 'down');
  // body
  P(-5, -8, 10, 6, L.col);
  // outline pass, then fills
  g.save(); if (o.alpha != null && o.alpha < 1) { /* dithered fade handled below */ }
  const draw = (pass) => {
    for (const [px, py, w, h, col] of parts) {
      if (pass === 0) { g.fillStyle = INK; g.fillRect(px - 1, py - 1, w + 2, h + 2); }
      else { g.fillStyle = col; g.fillRect(px, py, w, h); }
    }
  };
  const ghost = o.alpha != null && o.alpha < 1;
  if (ghost) { // draw into a scratch canvas, then copy only the pixels the dither lets through
    const sc = scratch(), sg = sc.getContext('2d'); sg.clearRect(0, 0, PW, PH);
    const saved = g; g = sg; draw(0); draw(1); details(); g = saved;
    const a = clamp(o.alpha), img = sg.getImageData(0, 0, PW, PH), d = img.data;
    for (let j = 0; j < PH; j++) for (let i = 0; i < PW; i++) { const q = (j * PW + i) * 4; if (d[q + 3] && bayer(i, j) >= a) d[q + 3] = 0; }
    sg.putImageData(img, 0, 0); g.drawImage(sc, 0, 0);
  } else { if (o.glow) halo(g, x, y - 5 * k, 9 * k, o.glow); draw(0); draw(1); details(); }
  g.restore();

  function details() {
    const D = (ux, uy, uw, uh, col) => { let px = ux * k; const w = uw * k; if (f < 0) px = -px - w; g.fillStyle = col; g.fillRect(x + R(px), y + R(uy * k), Math.max(1, R(w)), Math.max(1, R(uh * k))); };
    D(-5, -8, 10, px1 * Math.max(1, R(k * .5)), L.lt);                  // top highlight
    D(-5, -2 - px1 * Math.max(1, R(k * .5)), 10, px1 * Math.max(1, R(k * .5)), L.dk);  // bottom shade
    const eyes = o.eyes || 'open', blink = eyes === 'open' && ((T * .9 + (o.seed || 0)) % 3.1) < .12;
    for (const ex of [-3, 2]) {
      if (eyes === 'closed' || blink) D(ex - .2, -6, 1.4, px1, INK);
      else if (eyes === 'happy') { D(ex, -6.7, 1, px1, INK); D(ex - px1, -6.7 + px1, px1, px1, INK); D(ex + 1, -6.7 + px1, px1, px1, INK); }
      else if (eyes === 'wide') { D(ex - .2, -7.3, 1.4, 2.6, INK); if (k >= 3) D(ex, -7.1, px1, px1, '#FFFFFF'); }
      else { D(ex, -7, 1, 2, INK); if (k >= 4) D(ex, -7, px1, px1, '#FFFFFF'); }
    }
    if (o.blush) { D(-4.6, -4.6, 1.2, Math.max(px1, .5), '#FF7FA0'); D(3.4, -4.6, 1.2, Math.max(px1, .5), '#FF7FA0'); }
    if (o.smile) { D(-.8, -4.4, 1.6, px1, INK); D(-1, -4.4 - px1, px1, px1, INK); D(.8 - 0, -4.4 - px1, px1, px1, INK); }
    if (o.bow) { D(1.6, -9.4, 1.3, 1.4, '#E8436E'); D(3.5, -9.4, 1.3, 1.4, '#E8436E'); D(2.9, -9.1, .7, .8, '#B92A52'); }
    if (o.tear) { const ty = ((T * 2) % 1) * 2; D(-3, -5 + ty, Math.max(px1, .5), Math.max(px1, .7), '#8CD0FF'); D(2.4, -5 + ((ty + 1) % 2), Math.max(px1, .5), Math.max(px1, .7), '#8CD0FF'); }
    if (o.aged) { D(-3.6, -8.7, 1.8, Math.max(px1, .5), '#F4F4F4'); D(1.8, -8.7, 1.8, Math.max(px1, .5), '#F4F4F4'); }
    if (o.cane) { D(6.3, -6, .6, 6, '#7A5A3A'); D(5.5, -6.3, 1.4, .6, '#7A5A3A'); }
    if (o.hold) o.hold(g, x + R(f * 6.5 * k), y - R(5 * k));
  }
}
let _scratch = null;
function scratch() { if (!_scratch) { _scratch = document.createElement('canvas'); _scratch.width = PW; _scratch.height = PH; } return _scratch; }
// a soft glow made of concentric dithered discs
function halo(g, x, y, r, col) { for (let i = 3; i >= 1; i--) { const rr = R(r * i / 3); const d = .5 / i; for (let j = -rr; j <= rr; j++) { const w = Math.floor(Math.sqrt(rr * rr - j * j)); g.fillStyle = col; for (let q = -w; q <= w; q++) if (bayer(x + q, y + j) < d * .9) g.fillRect(R(x + q), R(y + j), 1, 1); } } }

// a glowing pink shard: one eighth of him that is hers
function shard(g, x, y, s, T) {
  halo(g, x, y, 10 * s, '#FFB8D0');
  rect(g, x - 2 * s, y - 2 * s, 4 * s, 4 * s, INK); rect(g, x - 2 * s + 1, y - 2 * s + 1, 4 * s - 2, 4 * s - 2, '#F29BB8'); rect(g, x - 2 * s + 1, y - 2 * s + 1, 2 * s - 1, s, '#FCD2E0');
  if (Math.floor(T * 4) % 2) sparkle(g, x + 3 * s, y - 3 * s, 1);
}

// ---------------------------------------------------------------- pixel text
function ptext(g, s, x, y, o = {}) {
  const size = o.size || 12, k = size / 12;
  g.font = `${size}px ${PIX_FONT}`; g.textBaseline = 'alphabetic';
  const w = g.measureText(s).width; let X = o.align === 'left' ? x : o.align === 'right' ? x - w : x - w / 2; X = R(X); y = R(y);
  if (o.outline) { g.fillStyle = o.outline; for (const [dx, dy] of [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, 1], [-1, 1], [1, -1]]) g.fillText(s, X + dx * k, y + dy * k); }
  if (o.shadow) { g.fillStyle = o.shadow; g.fillText(s, X + k, y + k); }
  g.fillStyle = o.col || '#FFFFFF'; g.fillText(s, X, y);
  return { x: X, w };
}
const textW = (g, s, size = 12) => { g.font = `${size}px ${PIX_FONT}`; return g.measureText(s).width; };

// ---------------------------------------------------------------- the subtitle box
// The sung line's words were timed by analyze.py; the highlight sweeps across the subtitle at the same pace.
function subtitleAt(t) {
  const lines = BEATMAP.lines;
  if (typeof USER_LYRICS !== 'undefined' && USER_LYRICS.length) {
    for (let i = USER_LYRICS.length - 1; i >= 0; i--) {
      const L = USER_LYRICS[i], next = USER_LYRICS[i + 1];
      if (t >= L.t - .2) {
        const end = Math.min(next ? next.t - .1 : DUR, L.t + 9);
        if (t > end || !L.text) return null;
        const ws = lines.flatMap(l => l.w).filter(w => w >= L.t - .3 && w < end);
        return { text: L.text, show: L.t - .2, end, words: ws.length ? ws : [L.t, end - .5] };
      }
    }
    return null;
  }
  for (let i = lines.length - 1; i >= 0; i--) {
    const L = lines[i], next = lines[i + 1];
    if (t >= L.t0 - .3) {
      const end = Math.min(next ? next.t0 - .25 : DUR, L.t1 + 1.6);
      return t <= end ? { text: SUBS[i], show: L.t0 - .3, end, words: L.w } : null;
    }
  }
  return null;
}
function subtitle(g, t) {
  const s = subtitleAt(t); if (!s) return;
  const chars = [...s.text], n = chars.length;
  // progress of the singing through the line: whole words sung, plus how far into the current one
  const w = s.words; let p = 0;
  for (let i = 0; i < w.length; i++) { if (t >= w[i]) { const nx = w[i + 1] ?? (w[i] + .6); p = (i + clamp((t - w[i]) / Math.max(.15, nx - w[i]))) / w.length; } }
  const typed = Math.min(n, Math.floor((t - s.show) / .035) + 1), lit = Math.round(p * n);
  const out = clamp((s.end - t) / .25);
  const full = s.text, tw = textW(g, full), bw = R(tw + 16), bh = 20, bx = R((PW - bw) / 2), by = PH - bh - 7;
  // dialog box
  rect(g, bx - 1, by - 1, bw + 2, bh + 2, INK); rect(g, bx, by, bw, bh, '#2A2245'); rect(g, bx + 1, by + 1, bw - 2, 1, '#4A3F72');
  rect(g, bx, by, 1, 1, INK); rect(g, bx + bw - 1, by, 1, 1, INK); rect(g, bx, by + bh - 1, 1, 1, INK); rect(g, bx + bw - 1, by + bh - 1, 1, 1, INK);
  if (out < 1) checker(g, bx, by, bw, bh, '#2A2245', 1 - out);
  const shown = chars.slice(0, typed).join(''), x0 = R((PW - tw) / 2), base = by + 15;
  ptext(g, shown, x0, base, { col: '#8F86B8', align: 'left' });
  if (lit > 0) ptext(g, chars.slice(0, Math.min(lit, typed)).join(''), x0, base, { col: '#FFE9A8', align: 'left' });
  // a little ♪ that bobs on the beat while the line is sung
  if (p > 0 && p < 1) { const bob = beatPhase(t) < .5 ? 0 : 1; note(g, bx + bw - 7, by - 3 - bob, '#FFE9A8'); }
}
function note(g, x, y, col) { rect(g, x, y - 5, 1, 6, col); rect(g, x - 2, y, 3, 2, col); rect(g, x + 1, y - 5, 2, 1, col); rect(g, x + 2, y - 4, 1, 1, col); }

// ---------------------------------------------------------------- the pie in the corner: how much of him is her
function pie(g, t, x, y, r, n, total = 8, memory = 0) {
  const fill = memory ? '#E8C8A0' : '#F29BB8', edge = memory ? '#B8946A' : '#D0698D';
  for (let j = -r - 1; j <= r + 1; j++) for (let i = -r - 1; i <= r + 1; i++) {
    const d = Math.sqrt(i * i + j * j); if (d > r + .5) continue;
    let col;
    if (d > r - .6) col = INK;
    else { const a = (Math.atan2(i, -j) + Math.PI * 2) % (Math.PI * 2), sl = Math.floor(a / (Math.PI * 2 / total)); col = sl < n ? fill : ME.col; if (Math.abs(a - (sl * Math.PI * 2 / total)) * d < .7) col = sl < n ? edge : ME.dk; }
    rect(g, x + i, y + j, 1, 1, col);
  }
  ptext(g, `${n}/${total}`, x + r + 5, y + 5, { col: '#FFFFFF', outline: INK, align: 'left' });
}

// ---------------------------------------------------------------- pixel dissolve between two finished frames
function ditherMix(g, a, b, p) {
  const A = a.getContext('2d').getImageData(0, 0, PW, PH), B = b.getContext('2d').getImageData(0, 0, PW, PH), d = A.data, e = B.data;
  for (let y = 0; y < PH; y++) for (let x = 0; x < PW; x++) if (bayer(x >> 1, y >> 1) < p) { const q = (y * PW + x) * 4; d[q] = e[q]; d[q + 1] = e[q + 1]; d[q + 2] = e[q + 2]; }
  g.putImageData(A, 0, 0);
}
