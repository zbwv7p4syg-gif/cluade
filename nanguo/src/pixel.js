// pixel.js — 我不难过 · 像素 MV. Everything is drawn on a 480×270 canvas with whole-pixel rectangles and
// integer-scaled sprites, then scaled up 4× with nearest-neighbour (in the page by CSS, in the video by ffmpeg).

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
const mixHex = (a, b, p) => { const A = hex(a), B = hex(b); return '#' + A.map((v, i) => R(lerp(v, B[i], clamp(p))).toString(16).padStart(2, '0')).join(''); };
const qz = (p, n = 8) => Math.floor(clamp(p) * n) / n;              // palette changes in steps, like an old console
const INK = '#161226';
const PIX_FONT = 'NanguoPixel';

function rect(g, x, y, w, h, col) { g.fillStyle = col; g.fillRect(R(x), R(y), R(w), R(h)); }
function disc(g, cx, cy, r, col) {
  g.fillStyle = col; cx = R(cx); cy = R(cy); r = R(r);
  for (let y = -r; y <= r; y++) { const w = Math.floor(Math.sqrt(r * r - y * y) + .35); g.fillRect(cx - w, cy + y, w * 2 + 1, 1); }
}
function line(g, x0, y0, x1, y1, col) {
  g.fillStyle = col; x0 = R(x0); y0 = R(y0); x1 = R(x1); y1 = R(y1);
  const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let e = dx + dy;
  for (;;) { g.fillRect(x0, y0, 1, 1); if (x0 === x1 && y0 === y1) break; const e2 = 2 * e; if (e2 >= dy) { e += dy; x0 += sx; } if (e2 <= dx) { e += dx; y0 += sy; } }
}
function ring(g, cx, cy, r, col) { g.fillStyle = col; for (let a = 0; a < 360; a += 360 / (r * 7 + 8)) g.fillRect(R(cx + Math.cos(a * Math.PI / 180) * r), R(cy + Math.sin(a * Math.PI / 180) * r), 1, 1); }
// a translucent rectangle drawn as an ordered-dither checker, the way old consoles did transparency
function checker(g, x, y, w, h, col, density = .5) {
  if (density <= 0) return;
  g.fillStyle = col; x = R(x); y = R(y); w = R(w); h = R(h);
  if (density >= 1) { g.fillRect(x, y, w, h); return; }
  for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) if (bayer(x + i, y + j) < density) g.fillRect(x + i, y + j, 1, 1);
}
const blackout = (g, a) => { if (a > 0) checker(g, 0, 0, PW, PH, '#000000', a); };
const whiteout = (g, a) => { if (a > 0) checker(g, 0, 0, PW, PH, '#FFF8F0', a); };

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
    if (gradCache.size > 400) gradCache.clear();
    gradCache.set(key, img);
  }
  g.putImageData(img, 0, 0);
}
// a sky that steps between palettes, e.g. night → dawn, a few levels at a time
const skyMix = (a, b, p, n = 8) => a.map((c, i) => mixHex(c, b[i], qz(p, n)));

// ---------------------------------------------------------------- small scenery bits
function cloud(g, x, y, s, col = '#FFFFFF', shade = '#D8E4F2') {
  disc(g, x, y + 2, R(5 * s), shade); disc(g, x + 8 * s, y, R(7 * s), shade); disc(g, x + 17 * s, y + 2, R(5 * s), shade);
  disc(g, x, y + 1, R(5 * s), col); disc(g, x + 8 * s, y - 1, R(7 * s), col); disc(g, x + 17 * s, y + 1, R(5 * s), col);
  rect(g, x, y + 2, 17 * s, R(4 * s), col);
}
function stars(g, t, n, y1, seed = 1, x0 = 0, x1 = PW) {
  for (let i = 0; i < n; i++) {
    const tw = .5 + .5 * Math.sin(t * (1 + H(i + seed)) * 2 + i);
    if (tw < .25) continue;
    const x = R(x0 + H(i * 3 + seed) * (x1 - x0)), y = R(H(i * 7 + seed) * y1);
    rect(g, x, y, 1, 1, tw > .8 ? '#FFFFFF' : '#9FB0E0');
    if (H(i + 9) > .9 && tw > .85) { rect(g, x - 1, y, 3, 1, '#FFFFFF'); rect(g, x, y - 1, 1, 3, '#FFFFFF'); }
  }
}
function sparkle(g, x, y, s, col = '#FFFFFF') { x = R(x); y = R(y); rect(g, x - s, y, 2 * s + 1, 1, col); rect(g, x, y - s, 1, 2 * s + 1, col); }
// a soft glow made of concentric dithered discs
function halo(g, x, y, r, col, strength = 1) {
  x = R(x); y = R(y); g.fillStyle = col;
  for (let i = 3; i >= 1; i--) {
    const rr = R(r * i / 3), d = .5 / i * strength;
    for (let j = -rr; j <= rr; j++) { const w = Math.floor(Math.sqrt(rr * rr - j * j)); for (let q = -w; q <= w; q++) if (bayer(x + q, y + j) < d * .9) g.fillRect(x + q, y + j, 1, 1); }
  }
}
function heart(g, x, y, k, col = '#FF5C8A', hi = '#FFD0DE') {
  const rows = ['.XX.XX.', 'XXXXXXX', 'XXXXXXX', '.XXXXX.', '..XXX..', '...X...'];
  rows.forEach((r, j) => [...r].forEach((c, i) => { if (c === 'X') rect(g, x + (i - 3) * k, y + (j - 3) * k, k, k, col); }));
  if (hi) rect(g, x - 2 * k, y - 2 * k, k, k, hi);
}
// a big heart from the implicit curve, filled pixel by pixel; split > 0 pulls the halves apart along a zigzag
function bigHeart(g, cx, cy, s, col, dk = INK, o = {}) {
  cx = R(cx); cy = R(cy);
  const split = o.split || 0, crack = o.crack || 0;
  for (let j = -R(s * 1.25); j <= R(s * 1.1); j++) for (let i = -R(s * 1.25); i <= R(s * 1.25); i++) {
    const X = i / s, Y = -j / s + .15, f = Math.pow(X * X + Y * Y - 1, 3) - X * X * Y * Y * Y;
    if (f > 0) continue;
    const zig = ((Math.abs(j) >> 2) % 2 ? 2 : -2) * (s / 30);
    const side = i < zig ? -1 : 1;
    const X2 = (i + 1) / s, Y2 = -j / s + .15, X0 = (i - 1) / s, Yu = -(j - 1) / s + .15, Yd = -(j + 1) / s + .15;
    const edge = Math.pow(X2 * X2 + Y2 * Y2 - 1, 3) - X2 * X2 * Y2 * Y2 * Y2 > 0 || Math.pow(X0 * X0 + Y2 * Y2 - 1, 3) - X0 * X0 * Y2 * Y2 * Y2 > 0 ||
      Math.pow(X * X + Yu * Yu - 1, 3) - X * X * Yu * Yu * Yu > 0 || Math.pow(X * X + Yd * Yd - 1, 3) - X * X * Yd * Yd * Yd > 0;
    const ox = split ? side * split : 0, oy = split ? R(Math.abs(split) * .3) : 0;
    let c = edge ? dk : col;
    if (!edge && crack > 0 && Math.abs(i - zig) < 1 && Math.abs(j) < s * crack) c = dk;
    if (!edge && !split && X < -.25 && X > -.55 && Y > .45 && Y < .75 && o.shine !== false) c = '#FFFFFF';
    g.fillStyle = c; g.fillRect(cx + i + ox, cy + j + oy, 1, 1);
  }
}

// ---------------------------------------------------------------- pixel text
function ptext(g, s, x, y, o = {}) {
  const size = o.size || 12, k = R(size / 12) || 1;
  g.font = `${size}px ${PIX_FONT}`; g.textBaseline = 'alphabetic';
  const w = g.measureText(s).width; let X = o.align === 'left' ? x : o.align === 'right' ? x - w : x - w / 2; X = R(X); y = R(y);
  // the outline is one screen pixel even for big text, so the strokes of dense glyphs stay apart
  if (o.shadow) { g.fillStyle = o.shadow; for (let i = 1; i <= k; i++) g.fillText(s, X + i, y + i + 1); }
  if (o.outline) { g.fillStyle = o.outline; for (const [dx, dy] of [[-1, 0], [1, 0], [0, -1], [0, 1], [-1, -1], [1, 1], [-1, 1], [1, -1]]) g.fillText(s, X + dx, y + dy); }
  g.fillStyle = o.col || '#FFFFFF'; g.fillText(s, X, y);
  return { x: X, w };
}
const textW = (g, s, size = 12) => { g.font = `${size}px ${PIX_FONT}`; return g.measureText(s).width; };

// ---------------------------------------------------------------- the three people (original characters)
// 我: dark bob, red scarf and hair clip, cream sweater, blue skirt.  你: short dark hair, blue hoodie.
// 她: long light-brown hair with a white flower, pink cardigan.
const CAST = {
  me: { hair: '#2B2236', hairHi: '#4F4166', skin: '#F7D7C2', skinSh: '#E2AE96', top: '#F2EADF', topSh: '#CFC0AE', bottom: '#4E6AA8', bottomSh: '#36508A', leg: '#3A3048', shoe: '#6A3A3A', scarf: '#E2445C', scarfDk: '#A82C46', style: 'bob', sx: 5 },
  you: { hair: '#1C1C28', hairHi: '#3E3E56', skin: '#F0CBAE', skinSh: '#D6A487', top: '#3D5D9E', topSh: '#2B457C', bottom: '#4A4C5C', bottomSh: '#383A48', leg: '#4A4C5C', shoe: '#ECECEC', style: 'short', sx: 6 },
  her: { hair: '#A8714E', hairHi: '#D29A6C', skin: '#FBE2D0', skinSh: '#EBBDA4', top: '#F3A9C2', topSh: '#D8849F', bottom: '#FFF6F2', bottomSh: '#E6D2D4', leg: '#FBE2D0', shoe: '#E07A9A', style: 'long', sx: 5 },
};
const EYE = '#221A2E', BLUSH = '#F2949E';
// head rows 0..13 as [from, to] column spans; columns are relative to the sprite's centre line
const HEAD = [[-4, 3], [-6, 5], [-7, 6], [-8, 7], [-8, 7], [-8, 7], [-8, 7], [-8, 7], [-8, 7], [-8, 7], [-8, 7], [-7, 6], [-6, 5], [-4, 3]];
// sprite canvas: columns -14..13, rows -3..31 (feet stand on row 31's bottom edge), plus a 1px border for the outline
const SPW = 30, SPH = 37, SPX = 15, SPY = 4;

// arm shapes for the right arm (the left one is mirrored). Each is a list of [col, row, w, h, part] with part
// 's' sleeve, 'd' sleeve shade, 'h' hand. a = the hand's anchor (sprite coords) for things held.
function armShape(pose, sx, T) {
  const s = sx;
  switch (pose) {
    case 'out': return { r: [[s - 1, 16, 7, 1, 's'], [s - 1, 17, 7, 1, 'd'], [s + 6, 16, 2, 2, 'h']], a: [s + 7, 17] };
    case 'reach': return { r: [[s - 1, 15, 2, 2, 's'], [s, 17, 2, 2, 's'], [s + 1, 19, 2, 1, 's'], [s + 1, 20, 2, 1, 'd'], [s + 3, 19, 2, 2, 'h']], a: [s + 4, 20] };
    case 'up': return { r: [[s - 1, 14, 3, 2, 's'], [s + 2, 7, 2, 8, 's'], [s + 2, 5, 2, 2, 'h']], a: [s + 3, 5] };
    case 'wave': return Math.floor(T * 5) % 2 ? armShape('up', sx, T) : { r: [[s - 1, 14, 3, 2, 's'], [s + 2, 9, 2, 6, 's'], [s + 3, 7, 2, 2, 's'], [s + 4, 5, 2, 2, 'h']], a: [s + 5, 5] };
    case 'hold': return { r: [[s - 1, 15, 2, 4, 's'], [1, 19, s - 1, 1, 's'], [1, 20, s - 1, 1, 'd'], [-1, 19, 2, 2, 'h']], a: [0, 19] };
    case 'chest': return { r: [[s - 1, 15, 2, 2, 's'], [1, 17, s - 1, 1, 's'], [1, 18, s - 1, 1, 'd'], [-1, 16, 2, 2, 'h']], a: [0, 16] };
    case 'umb': return { r: [[s - 1, 15, 2, 3, 's'], [s - 2, 18, 2, 1, 'd'], [s - 3, 17, 2, 2, 'h']], a: [s - 2, 17] };
    case 'phone': return { r: [[s - 1, 15, 2, 3, 's'], [1, 18, s - 1, 1, 's'], [0, 17, 2, 2, 'h']], a: [1, 17] };
    case 'face': return { r: [[s - 1, 15, 2, 1, 's'], [s - 2, 12, 2, 3, 's'], [2, 8, 3, 4, 'h']], a: [3, 9] };
    case 'wipe': return { r: [[s - 1, 15, 2, 1, 's'], [s, 12, 2, 3, 's'], [4, 9, 2, 3, 'h']], a: [5, 10] };
    case 'shh': return { r: [[s - 1, 15, 2, 1, 's'], [2, 13, s - 1, 2, 's'], [0, 9, 1, 3, 'h'], [0, 12, 3, 2, 'h']], a: [0, 10] };
    case 'stop': return { r: [[s - 1, 13, 2, 3, 's'], [s, 12, 2, 1, 's'], [s + 1, 9, 3, 3, 'h']], a: [s + 2, 10] };
    case 'behind': return { r: [[s - 1, 15, 2, 3, 's']], a: [s, 18] };
    case 'pocket': return { r: [[s - 1, 15, 2, 5, 's'], [s - 1, 20, 1, 1, 'd']], a: [s, 20] };
    case 'hug': return { r: [[s - 1, 15, 2, 2, 's'], [s, 17, 11, 2, 's'], [s, 19, 11, 1, 'd'], [s + 11, 17, 2, 3, 'h']], a: [s + 12, 18] };
    default: return { r: [[s - 1, 15, 2, 6, 's'], [s - 1, 15, 1, 6, 'd'], [s - 1, 21, 2, 1, 'h']], a: [s, 21] };
  }
}

const spriteCache = new Map();
function buildSprite(L, o) {
  const cv = document.createElement('canvas'); cv.width = SPW; cv.height = SPH;
  const g = cv.getContext('2d');
  const P = (c, r, w, h, col) => { g.fillStyle = col; g.fillRect(c + SPX, r + SPY, w, h); };
  const S = (r, a, b, col) => P(a, r, b - a + 1, 1, col);
  const style = L.style, sx = L.sx, back = o.back;
  // legs and shoes
  const lift = o.legs === 'walkL' ? 1 : 0, liftR = o.legs === 'walkR' ? 1 : 0;
  if (o.legs === 'sit') { S(23, -3, -2, L.leg); S(24, -3, -2, L.leg); S(25, -3, -2, L.leg); S(23, 1, 2, L.leg); S(24, 1, 2, L.leg); S(25, 1, 2, L.leg); S(26, -4, -2, L.shoe); S(27, -4, -2, L.shoe); S(26, 1, 3, L.shoe); S(27, 1, 3, L.shoe); }
  else {
    for (let r = 22; r <= 28; r++) { S(r - lift, -3, -2, L.leg); S(r - liftR, 1, 2, L.leg); }
    S(29 - lift, -4, -2, L.shoe); S(30 - lift, -4, -2, L.shoe); S(29 - liftR, 1, 3, L.shoe); S(30 - liftR, 1, 3, L.shoe);
  }
  // long hair hangs behind the body
  if (style === 'long') { for (let r = 5; r <= 22; r++) { const taper = r > 20 ? 1 : 0; S(r, -10 + taper, -7, L.hair); S(r, 6, 9 - taper, L.hair); } S(10, -10, -10, L.hairHi); S(14, 9, 9, L.hairHi); }
  // torso
  if (style === 'short') {
    for (let r = 15; r <= 22; r++) S(r, -5, 4, L.top);
    for (let r = 15; r <= 22; r++) S(r, 4, 4, L.topSh);
    S(14, -4, 3, L.topSh); S(20, -3, 2, L.topSh);
    P(-2, 15, 1, 3, '#E8E8F0'); P(1, 15, 1, 3, '#E8E8F0');
  } else {
    for (let r = 15; r <= 20; r++) S(r, -4, 3, L.top);
    for (let r = 15; r <= 20; r++) S(r, 3, 3, L.topSh);
    const sk = style === 'long' ? [[20, -5, 4], [21, -5, 4], [22, -6, 5], [23, -6, 5], [24, -7, 6]] : [[20, -5, 4], [21, -5, 4], [22, -6, 5], [23, -6, 5]];
    for (const [r, a, b] of sk) { S(r, a, b, L.bottom); S(r, b, b, L.bottomSh); }
    if (style === 'bob') for (const c of [-3, 0, 3]) P(c, 21, 1, 3, L.bottomSh);
    if (style === 'long') { P(-1, 16, 1, 1, '#FFFFFF'); P(-1, 18, 1, 1, '#FFFFFF'); }
  }
  // neck
  S(14, -2, 1, L.skinSh);
  // arms
  const arm = (side, pose) => {
    const A = armShape(pose, sx, o.T || 0);
    for (const [c, r, w, h, part] of A.r) { const col = part === 'h' ? L.skin : part === 'd' ? L.topSh : L.top; P(side > 0 ? c : -c - w, r, w, h, col); }
  };
  // head
  HEAD.forEach(([a, b], r) => S(r, a, b, back ? L.hair : L.skin));
  if (!back) S(13, -4, 3, L.skinSh);
  const hair = (r, a, b) => S(r, a, b, L.hair);
  if (style === 'bob') {
    for (let r = 0; r <= 4; r++) hair(r, HEAD[r][0], HEAD[r][1]);
    if (!back) { hair(5, -8, -5); hair(5, -3, -2); hair(5, 0, 1); hair(5, 3, 7); hair(6, -8, -6); hair(6, 5, 7); for (let r = 7; r <= 12; r++) { hair(r, -8, -7); hair(r, 6, 7); } }
    hair(12, -9, -7); hair(12, 6, 8); hair(13, -9, -6); hair(13, 5, 8);
    S(1, -3, -1, L.hairHi); S(2, -5, -4, L.hairHi);
    if (back) S(4, -6, 5, L.hairHi);
    P(back ? -6 : 4, 3, 2, 2, L.scarf);
  } else if (style === 'short') {
    for (let r = 0; r <= 4; r++) hair(r, HEAD[r][0], HEAD[r][1]);
    P(-5, -1, 2, 1, L.hair); P(-1, -1, 2, 1, L.hair); P(3, -1, 1, 1, L.hair);
    if (!back) { hair(5, -8, -2); hair(5, 5, 7); hair(6, -8, -6); hair(6, 6, 7); for (let r = 7; r <= 9; r++) { hair(r, -8, -8); hair(r, 7, 7); } P(-9, 9, 1, 2, L.skin); P(8, 9, 1, 2, L.skin); }
    else { P(-9, 9, 1, 2, L.skin); P(8, 9, 1, 2, L.skin); }
    S(1, -3, 0, L.hairHi);
  } else {
    for (let r = 0; r <= 4; r++) hair(r, HEAD[r][0], HEAD[r][1]);
    if (!back) { hair(5, -8, -2); hair(5, 1, 7); hair(6, -8, -5); hair(6, 4, 7); hair(7, -8, -6); hair(7, 5, 7); for (let r = 8; r <= 13; r++) { hair(r, -8, -7); hair(r, 6, 7); } }
    S(1, -3, 0, L.hairHi); S(2, -5, -4, L.hairHi);
    const fx = back ? -8 : 5;
    P(fx + 1, 1, 1, 1, '#FFFFFF'); P(fx, 2, 3, 1, '#FFFFFF'); P(fx + 1, 3, 1, 1, '#FFFFFF'); P(fx + 1, 2, 1, 1, '#FFD860');
  }
  // the scarf
  if (style === 'bob' && !o.noScarf) { S(14, -5, 4, L.scarf); S(15, -5, 4, L.scarf); S(14, -4, -2, '#F27A8A'); P(back ? -4 : 2, 16, 2, 3, L.scarfDk); }
  // arms go over the body
  arm(-1, o.aL || 'down'); arm(1, o.aR || 'down');
  // outline: every empty pixel that touches the figure turns ink
  const img = g.getImageData(0, 0, SPW, SPH), d = img.data, out = new Uint8Array(SPW * SPH);
  for (let y = 0; y < SPH; y++) for (let x = 0; x < SPW; x++) {
    if (d[(y * SPW + x) * 4 + 3]) continue;
    for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) { const X = x + dx, Y = y + dy; if (X >= 0 && Y >= 0 && X < SPW && Y < SPH && d[(Y * SPW + X) * 4 + 3]) { out[y * SPW + x] = 1; break; } }
  }
  const ink = hex(o.tint ? o.tintDk || o.tint : INK);
  for (let i = 0; i < SPW * SPH; i++) if (out[i]) { d[i * 4] = ink[0]; d[i * 4 + 1] = ink[1]; d[i * 4 + 2] = ink[2]; d[i * 4 + 3] = 255; }
  g.putImageData(img, 0, 0);
  // the face
  if (!back) {
    const s = o.look || 0, e = o.eyes || 'open';
    for (const ex of [-5 + s, 3 + s]) {
      if (e === 'closed') P(ex, 9, 2, 1, EYE);
      else if (e === 'down') { P(ex, 9, 2, 1, EYE); P(ex, 8, 2, 1, L.skinSh); }
      else if (e === 'happy') { P(ex, 8, 2, 1, EYE); P(ex - 1, 9, 1, 1, EYE); P(ex + 2, 9, 1, 1, EYE); }
      else if (e === 'sad') { P(ex, 9, 2, 1, EYE); P(ex < 0 ? ex : ex + 1, 8, 1, 1, EYE); P(ex < 0 ? ex + 1 : ex, 7, 1, 1, L.hair === L.skin ? EYE : L.skinSh); }
      else if (e === 'wide') { P(ex, 7, 2, 3, EYE); P(ex, 7, 1, 1, '#FFFFFF'); }
      else { P(ex, 8, 2, 2, EYE); P(ex, 8, 1, 1, '#FFFFFF'); }
    }
    const m = o.mouth || 'none';
    if (m === 'smile') { P(-1 + s, 11, 2, 1, EYE); P(-2 + s, 10, 1, 1, EYE); P(1 + s, 10, 1, 1, EYE); }
    else if (m === 'grin') { P(-2 + s, 11, 4, 1, EYE); P(-1 + s, 12, 2, 1, EYE); P(-1 + s, 11, 2, 1, '#FFFFFF'); }
    else if (m === 'flat') P(-1 + s, 11, 2, 1, EYE);
    else if (m === 'frown') { P(-1 + s, 11, 2, 1, EYE); P(-2 + s, 12, 1, 1, EYE); P(1 + s, 12, 1, 1, EYE); }
    else if (m === 'open') { P(-1 + s, 11, 2, 2, EYE); P(-1 + s, 12, 2, 1, '#C8566A'); }
    else if (m === 'tremble') { P(-2 + s, 11, 1, 1, EYE); P(-1 + s, 12, 1, 1, EYE); P(0 + s, 11, 1, 1, EYE); P(1 + s, 12, 1, 1, EYE); }
    if (o.blush) { P(-7 + s, 11, 2, 1, BLUSH); P(5 + s, 11, 2, 1, BLUSH); }
  }
  // one colour silhouettes (the shadow of him in her days)
  if (o.tint) {
    const im = g.getImageData(0, 0, SPW, SPH), q = im.data, tc = hex(o.tint);
    for (let i = 0; i < SPW * SPH; i++) if (q[i * 4 + 3] && !out[i]) { q[i * 4] = tc[0]; q[i * 4 + 1] = tc[1]; q[i * 4 + 2] = tc[2]; }
    g.putImageData(im, 0, 0);
  }
  return cv;
}
function ditherSprite(cv, a) {
  const c2 = document.createElement('canvas'); c2.width = SPW; c2.height = SPH;
  const g2 = c2.getContext('2d'); g2.drawImage(cv, 0, 0);
  const im = g2.getImageData(0, 0, SPW, SPH), d = im.data;
  for (let y = 0; y < SPH; y++) for (let x = 0; x < SPW; x++) if (bayer(x, y) >= a) d[(y * SPW + x) * 4 + 3] = 0;
  g2.putImageData(im, 0, 0); return c2;
}
// Draw a person standing with feet at (x, y), k screen pixels per sprite pixel (integer).
// o: { aL, aR, walk (phase, cycles per step pair), sit, eyes, mouth, blush, back, look (-1|0|1), flip, alpha, glow,
//      tears, tint, noScarf, dy }
// Returns screen positions of both hands (for umbrellas, lanterns, photos) and of the face.
function person(g, who, x, y, k, o = {}, T = 0) {
  const L = CAST[who]; k = Math.max(1, R(k));
  let legs = o.sit ? 'sit' : 'stand', bob = 0;
  if (o.walk != null) { const f = Math.floor((((o.walk % 1) + 1) % 1) * 4); legs = f === 1 ? 'walkL' : f === 3 ? 'walkR' : 'stand'; bob = f % 2 ? 0 : 1; }
  let eyes = o.eyes || 'open';
  if (eyes === 'open' && ((T * .8 + (o.seed || 0)) % 3.3) < .1) eyes = 'closed';
  const wave = (o.aL === 'wave' || o.aR === 'wave') ? Math.floor(T * 5) % 2 : 0;
  const key = [who, legs, eyes, o.mouth, o.blush ? 1 : 0, o.back ? 1 : 0, o.look || 0, o.aL, o.aR, wave, o.tint, o.noScarf ? 1 : 0].join('|');
  let cv = spriteCache.get(key);
  if (!cv) { cv = buildSprite(L, { legs, eyes, mouth: o.mouth, blush: o.blush, back: o.back, look: o.look, aL: o.aL, aR: o.aR, T: wave ? 0 : .3, tint: o.tint, tintDk: o.tintDk, noScarf: o.noScarf }); spriteCache.set(key, cv); }
  const a = o.alpha == null ? 1 : clamp(o.alpha);
  if (a <= .02) return null;
  if (a < 1) { const ak = key + '|a' + R(a * 16); let dc = spriteCache.get(ak); if (!dc) { dc = ditherSprite(cv, R(a * 16) / 16); spriteCache.set(ak, dc); } cv = dc; }
  x = R(x); y = R(y + (o.dy || 0) - bob * k);
  const sy = o.sit ? 3 * k : 0;            // sitting figures are drawn so their feet stay at y
  if (o.glow) halo(g, x, y - sy - 18 * k, 24 * k, o.glow);
  g.imageSmoothingEnabled = false;
  if (o.flip) { g.save(); g.translate(x, 0); g.scale(-1, 1); g.drawImage(cv, -SPX * k, y + sy - (SPY + 31) * k, SPW * k, SPH * k); g.restore(); }
  else g.drawImage(cv, x - SPX * k, y + sy - (SPY + 31) * k, SPW * k, SPH * k);
  const at = (c, r) => [x + (o.flip ? -1 - c : c) * k + (o.flip ? -k / 2 : k / 2), y + sy + (r - 31) * k];
  const ra = armShape(o.aR || 'down', L.sx, T).a, la = armShape(o.aL || 'down', L.sx, T).a;
  const res = { R: at(ra[0], ra[1]), L: at(-1 - la[0], la[1]), face: at(-.5, 8), k, flip: o.flip };
  if (o.tears && !o.back) tears(g, x, y + sy, k, o, T);
  return res;
}
// tears run from both eyes down the cheeks
function tears(g, x, y, k, o, T) {
  const s = o.look || 0, f = o.flip ? -1 : 1, n = o.tears === true ? 1 : o.tears;
  for (const [i, ex] of [[0, -5 + s], [1, 3 + s]]) {
    const cx = x + (o.flip ? -1 - (ex + (i ? 1 : 0)) : ex + (i ? 1 : 0)) * k;
    for (let d = 0; d < 2 * n; d++) {
      const ph = ((T * 1.3 + d / (2 * n) + i * .37) % 1);
      const ty = y + (10 - 31) * k + ph * 6 * k;
      rect(g, cx, ty, Math.max(1, R(k * .7)), Math.max(1, k), '#9AD8FF');
    }
    rect(g, cx, y + (10 - 31) * k, Math.max(1, R(k * .7)), k, '#CFEFFF');
  }
  void f;
}

// ---------------------------------------------------------------- props
function umbrella(g, x, y, col, dk, w = 15) {
  // canopy centred on x with its top at y; the shaft runs down from the canopy to the hand
  for (let j = 0; j < 6; j++) { const hw = R(w * Math.sqrt(1 - Math.pow((5 - j) / 6, 2))); rect(g, x - hw, y + j, hw * 2 + 1, 1, j === 0 ? dk : col); }
  rect(g, x - w - 1, y + 6, w * 2 + 3, 1, dk);
  for (let i = -w; i <= w; i += R(w / 2.5)) rect(g, x + i, y + 6, 1, 2, dk);
  for (let j = 0; j < 6; j++) { const hw = R(w * Math.sqrt(1 - Math.pow((5 - j) / 6, 2))); rect(g, x - hw - 1, y + j, 1, 1, INK); rect(g, x + hw + 1, y + j, 1, 1, INK); }
  rect(g, x - R(w * .4), y - 1, R(w * .8) + 1, 1, INK); rect(g, x, y - 3, 1, 3, INK);
  rect(g, x - R(w * .5), y + 1, R(w * .3), 1, '#FFFFFF');
}
function umbrellaIn(g, hand, col, dk, h = 34, w = 15) { const [hx, hy] = hand; rect(g, hx, hy - h, 1, h + 1, INK); rect(g, hx - 2, hy + 1, 3, 1, INK); umbrella(g, hx, hy - h - 6, col, dk, w); }
function rain(g, t, n, col = '#8FA8D8', y1 = PH, seed = 1, slant = .15) {
  for (let i = 0; i < n; i++) { const sp = 240 + 120 * H(i + seed), y = (t * sp + H(i * 7 + seed) * y1) % y1, x = R(H(i * 3 + seed) * (PW + 40) - y * slant); rect(g, x, R(y), 1, 4, col); }
}
function splashes(g, t, n, y0, y1, col = '#6A7CA8', seed = 3) { for (let i = 0; i < n; i++) { const p = ((t * 1.4 + H(i + seed)) % 1); const x = R(H(i * 3 + seed) * PW), y = R(y0 + H(i + seed + 1) * (y1 - y0)); if (p < .5) { rect(g, x - R(p * 6), y, 1, 1, col); rect(g, x + R(p * 6), y, 1, 1, col); } } }
function petals(g, t, n, cols, seed = 3, wind = 1) { for (let i = 0; i < n; i++) { const y = R((t * (16 + 14 * H(i + seed)) + H(i * 5 + seed) * PH) % PH), x = R((H(i * 3 + seed) * PW + Math.sin(t * 1.3 + i) * 12 + t * 14 * wind + PW * 9) % PW); rect(g, x, y, 2, 1, cols[i % cols.length]); rect(g, x + (Math.floor(t * 4 + i) % 2), y + 1, 1, 1, cols[i % cols.length]); } }
function snow(g, t, n, seed = 2, col = '#FFFFFF') { for (let i = 0; i < n; i++) { const y = R((t * (12 + 10 * H(i + seed)) + H(i * 5 + seed) * PH) % PH), x = R((H(i * 3 + seed) * PW + Math.sin(t + i) * 6 + PW) % PW); rect(g, x, y, H(i) > .7 ? 2 : 1, H(i) > .7 ? 2 : 1, col); } }
function bird(g, x, y, T, col = INK) { const up = Math.floor(T * 5) % 2; rect(g, x - 2, y - up, 2, 1, col); rect(g, x + 1, y - up, 2, 1, col); rect(g, x, y, 1, 1, col); }
function windLines(g, t, n, seed = 5, col = '#FFFFFF', y0 = 30, y1 = 220) { for (let i = 0; i < n; i++) { const x = R(((t * 380 + H(i * 9 + seed) * 900) % 900) - 200), y = R(y0 + H(i + seed) * (y1 - y0) + Math.sin(t * 3 + i) * 3); rect(g, x, y, 14 + R(12 * H(i)), 1, col); } }
function moon(g, x, y, r, sky) { halo(g, x, y, r * 3, '#F4F0D8', .6); disc(g, x, y, r, '#F4F0D8'); if (sky) disc(g, x + R(r * .45), y - R(r * .3), r - 1, sky); else { rect(g, x - R(r * .4), y - R(r * .2), 2, 2, '#DCD6BC'); rect(g, x + R(r * .2), y + R(r * .3), 3, 2, '#DCD6BC'); } }
function sun(g, x, y, r, col = '#FFE27A', rim = '#FFC94A') { halo(g, x, y, r * 1.8, col); disc(g, x, y, r, rim); disc(g, x, y, r - 2, col); rect(g, x - R(r * .5), y - R(r * .5), R(r * .35), 2, '#FFF6C8'); }
function building(g, x, w, top, base, col, lit, seed, winOn = '#FFE08A', winOff = '#262040') {
  rect(g, x, top, w, base - top, col);
  for (let wy = top + 5; wy < base - 6; wy += 9) for (let wx = x + 4; wx < x + w - 5; wx += 8) {
    const on = H(wx * 13 + wy * 7 + seed) < lit; rect(g, wx, wy, 4, 5, on ? (H(wx + wy) > .5 ? winOn : '#FFC86A') : winOff);
  }
}
function bench(g, x, y, col = '#8A5A3A', dk = '#5A3A24') { rect(g, x - 34, y - 12, 68, 3, col); rect(g, x - 34, y - 22, 68, 3, col); rect(g, x - 30, y - 12, 2, 12, dk); rect(g, x + 28, y - 12, 2, 12, dk); rect(g, x - 30, y - 22, 2, 10, dk); rect(g, x + 28, y - 22, 2, 10, dk); }
function lamp(g, x, y, h, on = 1, cone = '#FFE9A8') {
  rect(g, x, y - h, 3, h, '#3E4258'); rect(g, x - 7, y - h - 2, 17, 4, '#3E4258'); rect(g, x - 4, y - h + 2, 11, 2, on ? '#FFF2C0' : '#6A6A7A');
  if (on) for (let yy = y - h + 4; yy < y; yy++) { const w = R((yy - (y - h + 4)) * .42); checker(g, x + 1 - w, yy, w * 2 + 1, 1, cone, .2 * on); }
}
// speech bubble with a tail pointing down at (tx, ty)
function bubble(g, x, y, w, h, tx, ty, col = '#FFFFFF') {
  x = R(x); y = R(y); w = R(w); h = R(h);
  rect(g, x + 1, y - 1, w - 2, h + 2, INK); rect(g, x - 1, y + 1, w + 2, h - 2, INK); rect(g, x, y, w, h, INK);
  rect(g, x + 1, y, w - 2, h, col); rect(g, x, y + 1, w, h - 2, col);
  const bx = clamp(tx, x + 4, x + w - 8);
  for (let j = 0; j < 5; j++) { const xx = R(lerp(bx, tx, j / 5)); rect(g, xx - 1, y + h - 1 + j, 6 - j, 1, col); rect(g, xx - 2, y + h - 1 + j, 1, 1, INK); rect(g, xx + 5 - j, y + h - 1 + j, 1, 1, INK); }
}
// a dithered disc, for out-of-focus lights
function bokeh(g, cx, cy, r, col, density) { cx = R(cx); cy = R(cy); r = R(r); g.fillStyle = col; for (let y = -r; y <= r; y++) { const w = Math.floor(Math.sqrt(r * r - y * y)); for (let x = -w; x <= w; x++) if (bayer(cx + x, cy + y) < density) g.fillRect(cx + x, cy + y, 1, 1); } }
function dots(g, x, y, n, col = INK, k = 2) { for (let i = 0; i < n; i++) rect(g, x + i * k * 2, y, k, k, col); }
function qmark(g, x, y, k, col = '#FFFFFF') {
  const rows = ['.XXX.', 'X...X', '...X.', '..X..', '.....', '..X..'];
  rows.forEach((r, j) => [...r].forEach((c, i) => { if (c === 'X') { rect(g, x + (i - 2) * k - 1, y + j * k - 1, k + 2, k + 2, INK); } }));
  rows.forEach((r, j) => [...r].forEach((c, i) => { if (c === 'X') rect(g, x + (i - 2) * k, y + j * k, k, k, col); }));
}
// a polaroid with a tiny picture of the two of them; k scales the whole thing (used for the zoom in the interlude)
function polaroid(g, cx, cy, k, T, scene = 0, bg = '#7AA0D8') {
  const w = 22 * k, h = 26 * k, x = R(cx - w / 2), y = R(cy - h / 2);
  rect(g, x - 1, y - 1, w + 2, h + 2, INK); rect(g, x, y, w, h, '#F6F2EA');
  photoPic(g, x + 2 * k, y + 2 * k, 18 * k, 18 * k, k, T, scene, bg);
}
function photoPic(g, x, y, w, h, k, T, scene = 0, bg = '#7AA0D8') {
  g.save(); g.beginPath(); g.rect(R(x), R(y), R(w), R(h)); g.clip();
  rect(g, x, y, w, h, bg);
  const gy = y + h;
  if (scene === 0) { rect(g, x, gy - 4 * k, w, 4 * k, '#5A8A5A'); }
  if (scene === 1) { rect(g, x, gy - 5 * k, w, 5 * k, '#E8D8B0'); disc(g, x + w * .75, y + h * .3, 3 * k, '#FFE27A'); }
  if (scene === 2) { stars(g, T, 8, h, 5, x, x + w); }
  if (scene === 3) { rect(g, x, gy - 4 * k, w, 4 * k, '#D88AA0'); for (let i = 0; i < 4; i++) rect(g, x + (i * 5 + 1) * k, y + (i * 3 + 2) * k, k, k, '#FFFFFF'); }
  const pk = Math.max(1, R(k / 2.2));
  if (k >= 2) { person(g, 'me', x + w * .36, gy - (scene === 0 ? 2 : 1) * k, pk, { eyes: 'happy', mouth: 'smile', blush: true }, T); person(g, 'you', x + w * .66, gy - (scene === 0 ? 2 : 1) * k, pk, { eyes: 'happy', mouth: 'smile' }, T); }
  else { rect(g, x + w * .3, gy - 9, 3, 7, '#E2445C'); rect(g, x + w * .3, gy - 12, 3, 3, '#2B2236'); rect(g, x + w * .62, gy - 10, 3, 8, '#3D5D9E'); rect(g, x + w * .62, gy - 13, 3, 3, '#1C1C28'); }
  if (scene === 3 || scene === 1) heart(g, R(x + w * .51), R(y + h * .25), Math.max(1, R(k / 2)), '#FF5C8A', null);
  g.restore();
}
function clockFace(g, cx, cy, r, hA, mA, sA, face = '#F4EEDC', rim = '#8A5A3A') {
  disc(g, cx, cy, r + 3, INK); disc(g, cx, cy, r + 2, rim); disc(g, cx, cy, r, face);
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; const l = i % 3 ? 1 : 3; for (let q = 0; q < l; q++) rect(g, R(cx + Math.sin(a) * (r - 2 - q)), R(cy - Math.cos(a) * (r - 2 - q)), i % 3 ? 1 : 2, i % 3 ? 1 : 2, INK); }
  const hand = (a, len, col, wd) => { for (let q = 0; q < len; q++) rect(g, R(cx + Math.sin(a) * q), R(cy - Math.cos(a) * q), wd, wd, col); };
  hand(hA, r * .5, INK, 2); hand(mA, r * .8, INK, 2); if (sA != null) hand(sA, r * .85, '#D8344C', 1);
  disc(g, cx, cy, 2, '#D8344C');
}

// ---------------------------------------------------------------- subtitles: the user's own .lrc lines
// The highlight sweeps across the line at the pace of the sung syllables that analyze.py timed with Whisper.
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
      return { text: L.text, show: L.t - .2, end, words: ws };
    }
  }
  return null;
}
function subtitle(g, t, theme) {
  const s = subtitleAt(t); if (!s) return;
  const chars = [...s.text], n = chars.length, w = s.words;
  let p = 0;
  for (let i = 0; i < w.length; i++) if (t >= w[i]) { const nx = w[i + 1] ?? (w[i] + .6); p = (i + clamp((t - w[i]) / Math.max(.15, Math.min(1.2, nx - w[i])))) / w.length; }
  const typed = Math.min(n, Math.floor((t - s.show) / .035) + 1), lit = Math.round(p * n);
  const out = clamp((s.end - t) / .2);
  const th = theme || { box: '#1A1630', edge: '#3E3866', dim: '#8C86B0', lit: '#FFF0F4' };
  const tw = textW(g, s.text), bw = R(tw + 18), bh = 20, bx = R((PW - bw) / 2), by = PH - bh - 6;
  rect(g, bx - 1, by - 1, bw + 2, bh + 2, INK); rect(g, bx, by, bw, bh, th.box); rect(g, bx + 1, by + 1, bw - 2, 1, th.edge);
  rect(g, bx - 1, by - 1, 1, 1, '#00000000');
  if (out < 1) checker(g, bx, by, bw, bh, th.box, 1 - out);
  const x0 = R((PW - tw) / 2), base = by + 15;
  ptext(g, chars.slice(0, typed).join(''), x0, base, { col: th.dim, align: 'left' });
  if (lit > 0) ptext(g, chars.slice(0, Math.min(lit, typed)).join(''), x0, base, { col: th.lit, align: 'left' });
  if (p > 0 && p < 1) { const bob = beatPhase(t) < .5 ? 0 : 1; note(g, bx + bw - 6, by - 3 - bob, th.lit); }
}
function note(g, x, y, col) { rect(g, x, y - 5, 1, 6, col); rect(g, x - 2, y, 3, 2, col); rect(g, x + 1, y - 5, 2, 1, col); rect(g, x + 2, y - 4, 1, 1, col); }

// ---------------------------------------------------------------- pixel dissolve between two finished frames
function ditherMix(g, a, b, p) {
  const A = a.getContext('2d').getImageData(0, 0, PW, PH), B = b.getContext('2d').getImageData(0, 0, PW, PH), d = A.data, e = B.data;
  for (let y = 0; y < PH; y++) for (let x = 0; x < PW; x++) if (bayer(x >> 1, y >> 1) < p) { const q = (y * PW + x) * 4; d[q] = e[q]; d[q + 1] = e[q + 1]; d[q + 2] = e[q + 2]; }
  g.putImageData(A, 0, 0);
}
