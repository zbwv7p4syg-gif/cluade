// scenes.js — 小宇 · 像素 MV. One function per shot (see timeline.js), all in 480×270 pixels.
// Each shot gets (g, t, s): the canvas, the song time, and its entry in SHOTS (s.t0, s.t1).

const TIMES = {
  day: { sky: ['#4AA6EE', '#8ED0F8', '#E2F6FF'], sea: '#3A86CC', seaDk: '#2A6AAE', seaHi: '#CFEFFF', hill: '#7DBE6A', hillDk: '#5E9E52', walk: '#EAD9B8', walkDk: '#CDB894', rail: '#F6F6F6', glow: '#FFF2C0', sand: '#F2DCA8', sandDk: '#DCC08A' },
  sunset: { sky: ['#4A3A8A', '#E8807A', '#FFD49A'], sea: '#7A5A9A', seaDk: '#5A4080', seaHi: '#FFC89A', hill: '#7A5A6A', hillDk: '#5A4058', walk: '#C8A090', walkDk: '#A88070', rail: '#F2D8C8', glow: '#FFD8A0', sand: '#E0B090', sandDk: '#C09078' },
  night: { sky: ['#080C26', '#141E4C', '#26346C'], sea: '#14204C', seaDk: '#0C163A', seaHi: '#8AA0E0', hill: '#1E2A40', hillDk: '#141E30', walk: '#3A4058', walkDk: '#2C3148', rail: '#8A92B8', glow: '#FFE8A8', sand: '#3A3A58', sandDk: '#2C2C48' },
  dawn: { sky: ['#2E4A8E', '#8AA4DA', '#FFD8C0'], sea: '#4A6AA8', seaDk: '#34528E', seaHi: '#FFE0C8', hill: '#5A7A6A', hillDk: '#44604E', walk: '#B8B0B8', walkDk: '#9A92A0', rail: '#F0E8F0', glow: '#FFF0C8', sand: '#D8C0B0', sandDk: '#BCA498' },
};
const SUB_THEMES = {
  day: { box: '#24365E', edge: '#4A6AA0', dim: '#9AB4D8', lit: '#FFFFFF' },
  night: { box: '#121838', edge: '#33407A', dim: '#7F8CC0', lit: '#FFF4D8' },
  sunset: { box: '#3A2448', edge: '#6A4478', dim: '#C8A0C0', lit: '#FFF0E0' },
};
const local = (t, s) => t - s.t0;
const talk = t => singing(t) ? 'open' : 'smile';

// ---------------------------------------------------------------- helpers for the shots
let _gbuf = null;
// a dithered gradient limited to a rectangle (putImageData ignores clipping, so go through a scratch canvas)
function gradRect(g, stops, x, y, w, h, y0 = y, y1 = y + h) {
  if (!_gbuf) { _gbuf = document.createElement('canvas'); _gbuf.width = PW; _gbuf.height = PH; }
  const b = _gbuf.getContext('2d'); grad(b, stops, y0, y1);
  g.drawImage(_gbuf, R(x), R(y), R(w), R(h), R(x), R(y), R(w), R(h));
}
// sun rays around (cx, cy), drawn straight into the frame as the background
function rays(g, cx, cy, n, a, b, rot) {
  const img = g.createImageData(PW, PH), d = img.data, A = hex(a), B = hex(b);
  for (let y = 0; y < PH; y++) for (let x = 0; x < PW; x++) {
    const s = (((Math.atan2(y - cy, x - cx) + rot) / (Math.PI * 2) * n) % 1 + 1) % 1, c = s < .5 ? A : B, o = (y * PW + x) * 4;
    d[o] = c[0]; d[o + 1] = c[1]; d[o + 2] = c[2]; d[o + 3] = 255;
  }
  g.putImageData(img, 0, 0);
}
const inHeart = (i, j, s) => { const X = i / s, Y = -j / s + .15; return Math.pow(X * X + Y * Y - 1, 3) - X * X * Y * Y * Y <= 0; };
// a point on the heart curve, t in radians, scaled to about s pixels across half the width
const heartPt = (cx, cy, s, th) => [cx + 16 * Math.pow(Math.sin(th), 3) * s / 16, cy - (13 * Math.cos(th) - 5 * Math.cos(2 * th) - 2 * Math.cos(3 * th) - Math.cos(4 * th)) * s / 16];

function seagull(g, x, y, T, col = '#FFFFFF') { const up = Math.floor(T * 4) % 2; x = R(x); y = R(y); rect(g, x - 4, y - up * 2, 3, 1, col); rect(g, x - 2, y - 1 + up, 2, 1, col); rect(g, x, y, 1, 1, col); rect(g, x + 1, y - 1 + up, 2, 1, col); rect(g, x + 2, y - up * 2, 3, 1, col); }
function waves(g, t, y0, y1, P, n = 60) { for (let i = 0; i < n; i++) { const y = R(y0 + H(i + 2) * (y1 - y0)), x = R(((H(i) * PW + t * (6 + 10 * H(i + 1))) % (PW + 30)) - 15); if (Math.sin(t * 2 + i) > -.2) rect(g, x, y, 4 + R(H(i + 5) * 8), 1, H(i + 3) > .5 ? P.seaHi : P.seaDk); } }
function lighthouse(g, x, base, t, on) {
  x = R(x);
  for (let j = 0; j < 64; j++) { const w = R(7 - j * .05); rect(g, x - w - 1, base - j, w * 2 + 3, 1, INK); rect(g, x - w, base - j, w * 2 + 1, 1, Math.floor(j / 10) % 2 ? '#E04A3A' : '#F6F6F6'); }
  rect(g, x - 7, base - 66, 15, 3, INK); rect(g, x - 5, base - 76, 11, 10, INK); rect(g, x - 4, base - 75, 9, 8, on ? '#FFF2A0' : '#D8D0A0');
  for (let j = 0; j < 5; j++) rect(g, x - 5 + j, base - 80 + j, 11 - 2 * j, 1, '#E04A3A'); rect(g, x, base - 82, 1, 2, INK);
  if (on) {
    const a = t * 1.3, dir = Math.cos(a), L = R(220 * Math.abs(dir)), sgn = dir > 0 ? 1 : -1;
    halo(g, x, base - 71, 16, '#FFF2A0');
    for (let i = 4; i < L; i++) { const w = R(1 + i * .12); checker(g, x + sgn * i, base - 71 - w, 1, w * 2 + 1, '#FFF2A0', .3 * (1 - i / L)); }
  }
}
// the seaside town: sky, sea, a town on the hill to the left, the lighthouse on the right, a promenade in front
function seaside(g, t, tm, o = {}) {
  const P = TIMES[tm];
  grad(g, P.sky, 0, 148);
  if (tm === 'day') { sun(g, o.sunX ?? 404, o.sunY ?? 44, 16); for (let i = 0; i < 4; i++) cloud(g, R(((t * 4 + i * 150) % 640) - 90), 20 + i * 13, 1 + (i % 2) * .4); }
  if (tm === 'sunset') sun(g, 380, 140, 20, '#FFE0A0', '#FFB070');
  if (tm === 'dawn') { halo(g, 380, 150, 70, '#FFE8C8', .8); stars(g, t, 20, 60, 5); }
  if (tm === 'night') { stars(g, t, 90, 130, 3); moon(g, o.moonX ?? 380, 40, 10); }
  // the town on the hill
  disc(g, 70, 236, 130, P.hillDk); disc(g, 70, 240, 128, P.hill);
  const roofs = ['#E04A3A', '#3A78D0', '#F2C14E', '#7DBE6A', '#E07A9A'];
  for (let i = 0; i < 9; i++) {
    const hx = R(-10 + i * 19 + (i % 2) * 5), hy = R(150 + Math.abs(i - 3.5) * 7 - (i % 3) * 4);
    rect(g, hx - 1, hy - 1, 16, 14, INK); rect(g, hx, hy, 14, 12, tm === 'night' ? '#4A4A6A' : '#F4EEE4'); for (let j = 0; j < 5; j++) rect(g, hx - 1 + j, hy - 5 + j, 16 - 2 * j, 1, roofs[i % 5]);
    rect(g, hx + 4, hy + 4, 4, 4, tm === 'night' || tm === 'dawn' ? (H(i) > .3 ? P.glow : '#2A2A40') : '#7AB0E0');
  }
  rect(g, 130, 140, PW - 130, 66, P.sea); rect(g, 130, 140, PW - 130, 1, P.seaHi);
  waves(g, t, 143, 204, P, 50);
  if (tm === 'sunset' || tm === 'dawn') for (let i = 0; i < 10; i++) rect(g, 366 + R(H(i + Math.floor(t * 4)) * 26), 144 + i * 6, 8 + i * 2, 1, P.seaHi);
  if (tm === 'night') for (let i = 0; i < 10; i++) rect(g, 372 + R(H(i + Math.floor(t * 4)) * 14), 144 + i * 6, 4 + i, 1, '#F4F0D8');
  disc(g, 452, 186, 40, P.hillDk); rect(g, 412, 186, 80, 20, P.hillDk);
  lighthouse(g, 452, 150, t, tm !== 'day');
  if (o.promenade !== false) {
    rect(g, 0, 200, PW, 70, P.walk); for (let x = 0; x < PW; x += 24) rect(g, x, 214, 1, 56, P.walkDk); for (let y = 222; y < PH; y += 16) rect(g, 0, y, PW, 1, P.walkDk);
    rect(g, 0, 190, PW, 2, P.rail); rect(g, 0, 198, PW, 2, P.rail); for (let x = 4; x < PW; x += 20) rect(g, x, 190, 2, 12, P.rail); rect(g, 0, 200, PW, 1, INK);
  }
}
function beach(g, t, tm, o = {}) {
  const P = TIMES[tm];
  grad(g, P.sky, 0, 132);
  if (tm === 'day') { sun(g, 90, 40, 16); for (let i = 0; i < 4; i++) cloud(g, R(((t * 5 + i * 160) % 660) - 100), 18 + i * 12, 1 + (i % 2) * .5); }
  if (tm === 'sunset') sun(g, 300, 128, 22, '#FFE0A0', '#FFB070');
  if (tm === 'night') { stars(g, t, 110, 120, 7); if (o.moon !== false) moon(g, 110, 40, 10); }
  rect(g, 0, 128, PW, 56, P.sea); rect(g, 0, 128, PW, 1, P.seaHi); waves(g, t, 131, 182, P, 46);
  if (tm === 'sunset') for (let i = 0; i < 10; i++) rect(g, 286 + R(H(i + Math.floor(t * 4)) * 28), 132 + i * 5, 8 + i * 2, 1, P.seaHi);
  const sw = R(Math.sin(t * 1.4) * 4);
  rect(g, 0, 184 + sw, PW, 86 - sw, P.sand); rect(g, 0, 184 + sw, PW, 3, '#FFFFFF'); for (let x = 0; x < PW; x += 6) rect(g, x, 187 + sw + (x % 4 ? 0 : 1), 3, 1, '#FFFFFF');
  for (let i = 0; i < 30; i++) rect(g, R(H(i) * PW), R(200 + H(i + 3) * 70), 2, 1, P.sandDk);
}
function room(g) {
  rect(g, 0, 0, PW, PH, '#2A2E52'); for (let x = 0; x < PW; x += 16) rect(g, x, 0, 1, 200, '#24284A');
  rect(g, 0, 200, PW, 70, '#3A3450');
}
// the little cloud he becomes: a puff with his face and his brown tuft of hair
function cloudKid(g, x, y, k, o = {}, T = 0) {
  x = R(x); y = R(y + Math.sin(T * 2) * k * .6);
  const body = o.rain ? '#E8EEF8' : '#FFFFFF', shade = o.rain ? '#B4C4E0' : '#D2E2F4';
  const puffs = [[-7, 1, 5], [-2, -3, 6], [4, -2, 6], [8, 2, 4], [0, 2, 6]];
  rect(g, x - 2 * k - 1, y - 11 * k - 1, k + 2, 3 * k + 2, INK); rect(g, x - k - 1, y - 12 * k - 1, k + 2, 4 * k + 2, INK); rect(g, x + k - 1, y - 11 * k - 1, k + 2, 3 * k + 2, INK);
  for (const [dx, dy, r] of puffs) disc(g, x + dx * k, y + dy * k, r * k + 1, INK);
  for (const [dx, dy, r] of puffs) disc(g, x + dx * k, y + dy * k, r * k, shade);
  for (const [dx, dy, r] of puffs) disc(g, x + dx * k, y + (dy - .9) * k, r * k - R(k * .7), body);
  rect(g, x - 2 * k, y - 11 * k, k, 3 * k, '#5A3A22'); rect(g, x - k, y - 12 * k, k, 4 * k, '#5A3A22'); rect(g, x + k, y - 11 * k, k, 3 * k, '#5A3A22'); rect(g, x - k, y - 12 * k, k, 1, '#86603C');
  const e = o.eyes || 'open', ey = y - k;
  for (const ex of [x - 4 * k, x + 2 * k]) {
    if (e === 'closed') rect(g, ex, ey + k, 2 * k, Math.max(1, R(k / 2)), INK);
    else if (e === 'happy') { rect(g, ex, ey, 2 * k, Math.max(1, R(k / 2)), INK); rect(g, ex - R(k / 2), ey + R(k / 2), Math.max(1, R(k / 2)), Math.max(1, R(k / 2)), INK); rect(g, ex + 2 * k, ey + R(k / 2), Math.max(1, R(k / 2)), Math.max(1, R(k / 2)), INK); }
    else if (e === 'strain') { rect(g, ex, ey, 2 * k, Math.max(1, R(k / 2)), INK); rect(g, ex + (ex < x ? 0 : k), ey + k, k, Math.max(1, R(k / 2)), INK); }
    else { rect(g, ex, ey, 2 * k, 2 * k, INK); rect(g, ex, ey, R(k / 2) || 1, R(k / 2) || 1, '#FFFFFF'); }
  }
  rect(g, x - 6 * k, y + 2 * k, 2 * k, k, '#F8A8B8'); rect(g, x + 4 * k, y + 2 * k, 2 * k, k, '#F8A8B8');
  if (o.mouth === 'o') rect(g, x - k / 2, y + 2 * k, k, k, INK);
  else { rect(g, x - k, y + 2 * k, 2 * k, Math.max(1, R(k / 2)), INK); }
}
// a little wooden boat with a heart on its sail; y is the waterline. With him rowing unless o.empty.
function boat(g, x, y, k, T, o = {}) {
  x = R(x); y = R(y + Math.sin(T * 2.2) * k * .7);
  const mx = x + 3 * k;
  rect(g, mx - 1, y - 30 * k - 1, k + 2, 27 * k + 2, INK); rect(g, mx, y - 30 * k, k, 27 * k, '#8A5A34');
  for (let r = 0; r < 22 * k; r++) { const w = R(r * .5); rect(g, mx + k, y - 29 * k + r, w + 1, 1, INK); if (w > 1) rect(g, mx + k, y - 29 * k + r, w, 1, r < 2 ? INK : '#FFFFFF'); }
  heart(g, mx + k + R(5.5 * k), y - 13 * k, Math.max(1, R(k / 2) + (k > 2 ? 1 : 0)), '#E8436E', null);
  if (o.flag) rect(g, mx, y - 33 * k, 4 * k, 2 * k, '#F2C14E');
  if (!o.empty) {
    const P = person(g, 'me', x - 5 * k, y + k, k, { sit: true, aR: o.arm || 'out', aL: o.armL || 'out', eyes: o.eyes || 'open', mouth: o.mouth || 'smile', look: o.look ?? 1, blush: o.blush, back: o.back }, T);
    if (P && o.oars !== false) { const sw = R(Math.sin(T * 3) * 2 * k); line(g, P.R[0], P.R[1], P.R[0] + 6 * k, y + 3 * k + sw, '#C89A60'); line(g, P.L[0], P.L[1], P.L[0] - 6 * k, y + 3 * k - sw, '#C89A60'); }
    if (P && o.scope) { rect(g, P.R[0] - 1, P.R[1] - 3, 9 * k / 2 + 2, 4, INK); rect(g, P.R[0], P.R[1] - 2, 9 * k / 2, 2, '#E8C060'); }
  }
  for (let j = 0; j < 5; j++) { const w = R((13 - j * 1.2) * k); rect(g, x - w - 1, y - 4 * k + j * k - 1, w * 2 + 2, k + 2, INK); }
  for (let j = 0; j < 5; j++) { const w = R((13 - j * 1.2) * k); rect(g, x - w, y - 4 * k + j * k, w * 2, k, j === 0 ? '#C8884E' : j % 2 ? '#A8683A' : '#B87444'); }
  if (o.lantern) { halo(g, x + 12 * k, y - 8 * k, 8 * k, '#FFE8A0'); rect(g, x + 12 * k - 1, y - 9 * k - 1, 2 * k + 2, 3 * k + 2, INK); rect(g, x + 12 * k, y - 9 * k, 2 * k, 3 * k, '#FFE08A'); }
  for (let i = 0; i < 4; i++) { const ph = (T * .8 + i / 4) % 1; rect(g, x - R(16 * k + ph * 30 * k), y + k + i % 2, R(6 * k * (1 - ph)) + 1, 1, '#FFFFFF'); }
}
function tinyBoat(g, x, y, dir) { x = R(x); y = R(y); rect(g, x - 4, y - 1, 9, 4, INK); rect(g, x - 3, y, 7, 2, '#A8683A'); rect(g, x, y - 6, 1, 6, INK); for (let j = 0; j < 5; j++) rect(g, x + (dir > 0 ? 1 : -j), y - 6 + j, j, 1, '#FFFFFF'); rect(g, x + (dir > 0 ? 2 : -2), y - 3, 1, 1, '#E8436E'); }
// her sun hat; (x, y) is the middle of the brim, s the size of one hat pixel
function sunhat(g, x, y, s = 2) {
  x = R(x); y = R(y);
  rect(g, x - 9 * s - 1, y - 1, 18 * s + 2, 2 * s + 2, INK); rect(g, x - 5 * s - 1, y - 4 * s - 1, 10 * s + 2, 4 * s + 2, INK);
  rect(g, x - 9 * s, y, 18 * s, 2 * s, '#F4E2B0'); rect(g, x - 9 * s, y + s, 18 * s, s, '#DCC08A'); rect(g, x - 5 * s, y - 4 * s, 10 * s, 4 * s, '#F4E2B0');
  rect(g, x - 5 * s, y - s, 10 * s, s, '#5A9AD8'); rect(g, x + 5 * s, y - s, s, 3 * s, '#5A9AD8');
}
function iceCream(g, x, y, col) { x = R(x); y = R(y); for (let j = 0; j < 8; j++) rect(g, x - 3 + R(j * .4), y + j, 7 - R(j * .8), 1, j % 2 ? '#C8884E' : '#E0A060'); disc(g, x, y - 3, 5, INK); disc(g, x, y - 3, 4, col); rect(g, x - 2, y - 6, 2, 1, '#FFFFFF'); }
function guitar(g, x, y) { x = R(x); y = R(y); rect(g, x - 26, y - 2, 22, 3, INK); rect(g, x - 25, y - 1, 20, 1, '#6A4228'); rect(g, x - 30, y - 3, 5, 5, INK); disc(g, x, y, 8, INK); disc(g, x + 8, y - 1, 7, INK); disc(g, x, y, 7, '#D8944A'); disc(g, x + 8, y - 1, 6, '#D8944A'); disc(g, x + 3, y, 2, '#3A2418'); }
function flowers(g, x, y) { for (const [dx, dy, c] of [[-3, -6, '#FF8FB0'], [2, -8, '#FFD860'], [5, -4, '#FFFFFF'], [-1, -10, '#E8436E']]) { rect(g, x + dx, y + dy + 2, 1, 8 - dy / 2, '#4E9A4A'); rect(g, x + dx - 1, y + dy - 1, 3, 3, c); } rect(g, x - 4, y + 4, 9, 3, '#F6F6F6'); }
function kite(g, x, y, T) { for (let j = 0; j < 9; j++) rect(g, x - (j < 5 ? j : 8 - j), y - 4 + j, 1 + 2 * (j < 5 ? j : 8 - j), 1, j < 5 ? '#E8436E' : '#F2C14E'); for (let j = 0; j < 4; j++) rect(g, x + R(Math.sin(T * 4 + j) * 2), y + 6 + j * 3, 1, 2, '#FFFFFF'); }
function balloon(g, x, y, T) { const sx = R(Math.sin(T * 2) * 2); line(g, x, y, x + sx, y - 22, '#FFFFFF'); heart(g, x + sx, y - 28, 2, '#E8436E'); }
function lantern(g, x, y) { halo(g, x, y, 12, '#FFE8A0'); rect(g, x - 3, y - 4, 7, 9, INK); rect(g, x - 2, y - 3, 5, 7, '#FFE08A'); rect(g, x - 1, y - 7, 3, 3, INK); }
function padlock(g, x, y, k) { ring(g, x, y - 3 * k, 2 * k, INK); ring(g, x, y - 3 * k, 2 * k - 1, INK); rect(g, x - 3 * k - 1, y - 2 * k - 1, 6 * k + 3, 5 * k + 2, INK); rect(g, x - 3 * k, y - 2 * k, 6 * k + 1, 5 * k, '#F2C14E'); rect(g, x, y - k, 1, 2 * k, INK); }
function bike(g, x, y, T, s = 1) {
  const sp = T * 18, X = v => x + R(v * s), Y = v => y - R(v * s), fr = (a, b, c, d) => { line(g, X(a), Y(b), X(c), Y(d), '#3A9AD8'); line(g, X(a), Y(b) + 1, X(c), Y(d) + 1, '#3A9AD8'); };
  for (const wx of [-19, 19]) {
    const r = R(8 * s); ring(g, X(wx), Y(8), r, INK); ring(g, X(wx), Y(8), r - 1, '#3A3A48'); ring(g, X(wx), Y(8), r - 2, INK);
    for (let a = 0; a < 3; a++) { const an = sp + a * Math.PI / 3, q = r - 3; line(g, X(wx) - R(Math.cos(an) * q), Y(8) - R(Math.sin(an) * q), X(wx) + R(Math.cos(an) * q), Y(8) + R(Math.sin(an) * q), '#9A9AB0'); }
  }
  fr(-19, 8, -2, 8); fr(-2, 8, 8, 20); fr(-19, 8, -6, 20); fr(-6, 20, 8, 20); fr(8, 20, 19, 8); fr(12, 26, 8, 20); rect(g, X(10), Y(27), R(6 * s), 2, INK);
  rect(g, X(-9), Y(22), R(7 * s), 2, INK); rect(g, X(-24), Y(20), R(12 * s), 2, '#5A5A6A');
  halo(g, X(22), Y(22), 10, '#FFF2C0'); rect(g, X(21), Y(23), 3, 3, '#FFF2C0');
}
function firework(g, t, k, i, cx, cy, col) {
  const a = t - k; if (a < 0) return;
  if (a < .25) { rect(g, cx, R(cy + (1 - a / .25) * 110), 1, 4, '#FFF0C0'); return; }
  const b = a - .25; if (b > 1.6) return;
  for (let s = 0; s < 26; s++) { const an = s / 26 * Math.PI * 2, r = 44 * eout(b / 1.1), x = R(cx + Math.cos(an) * r), y = R(cy + Math.sin(an) * r + b * b * 14); if (H(s + i) < 1 - b / 1.6) rect(g, x, y, 2, 2, col); rect(g, R(cx + Math.cos(an) * r * .6), R(cy + Math.sin(an) * r * .6 + b * b * 10), 1, 1, '#FFFFFF'); }
}
function fireworksIn(g, t, a, b, area) {
  const cols = ['#FF5C8A', '#FFE08A', '#8FE0F0', '#B58EF0', '#FF9E5A'];
  kicksIn(a, Math.min(b, t)).slice(-6).forEach(k => { const i = R(k * 100); firework(g, t, k, i, R(area[0] + H(i) * (area[2] - area[0])), R(area[1] + H(i + 1) * (area[3] - area[1])), cols[i % 5]); });
}
// a big picture book of their story; page = how far the pages have flipped (0..n), blank = last page is empty
function storyBook(g, t, cx, cy, page, o = {}) {
  const w = o.w || 300, h = o.h || 150, x = R(cx - w / 2), y = R(cy - h / 2), close = o.close || 0;
  const cw = R(w * (1 - close * .5)), lx = R(cx - cw / 2);
  rect(g, lx - 4, y - 3, cw + 8, h + 8, INK); rect(g, lx - 3, y - 2, cw + 6, h + 6, '#B8503A');
  if (close > .98) { rect(g, lx, y, cw, h, '#D8644A'); heart(g, cx, cy, 4, '#FFE08A', null); return; }
  rect(g, lx, y, cw, h, '#FBF6EA'); rect(g, R(cx) - 1, y, 2, h, '#D8CCB8'); checker(g, R(cx) - 8, y, 16, h, '#E8DCC8', .5);
  const pic = (px, py, pw, ph, n) => {
    g.save(); g.beginPath(); g.rect(px, py, pw, ph); g.clip();
    rect(g, px, py, pw, ph, ['#BFE6FF', '#CFE8F8', '#FFE0B0', '#F8F4EC'][n] || '#F8F4EC');
    if (n === 0) { rect(g, px, py + ph - 10, pw, 10, '#EAD9B8'); person(g, 'me', px + pw * .35, py + ph - 4, 1, { eyes: 'wide' }, t); person(g, 'you', px + pw * .65, py + ph - 4, 1, { eyes: 'happy' }, t); sunhat(g, px + pw * .35, py + ph - 34, 1); }
    if (n === 1) { rect(g, px, py + ph - 12, pw, 12, '#7DBE6A'); cloudKid(g, px + pw / 2, py + 20, 1, { eyes: 'happy' }, t); for (let i = 0; i < 8; i++) rect(g, px + pw / 2 - 10 + i * 3, py + 30 + (i * 7 + R(t * 20)) % 20, 1, 3, '#5A9AD8'); heart(g, px + pw / 2, py + ph - 8, 1, '#4E9A4A', null); }
    if (n === 2) { rect(g, px, py + ph - 14, pw, 14, '#F2DCA8'); rect(g, px, py + ph - 26, pw, 12, '#3A86CC'); iceCream(g, px + pw * .35, py + ph - 26, '#FF9AB8'); iceCream(g, px + pw * .65, py + ph - 26, '#8FE0F0'); }
    g.restore(); rect(g, px - 1, py - 1, pw + 2, 1, INK); rect(g, px - 1, py + ph, pw + 2, 1, INK); rect(g, px - 1, py, 1, ph, INK); rect(g, px + pw, py, 1, ph, INK);
  };
  const shown = Math.min(3, Math.floor(page));
  if (cw > 200) {
    if (shown < 3) { pic(lx + 18, y + 16, cw / 2 - 36, h - 34, shown); pic(R(cx) + 18, y + 16, cw / 2 - 36, h - 34, shown + 1 > 2 ? 3 : shown + 1); }
    else { pic(lx + 18, y + 16, cw / 2 - 36, h - 34, 2); qmark(g, R(cx + cw / 4), y + h / 2 - 22, 6, '#C8BCA8'); }
    // a page turning from right to left
    const f = page % 1; if (page < 3 && f > 0) { const pw = R(cw / 2 * Math.abs(1 - 2 * f)), px = f < .5 ? R(cx) : R(cx) - pw; rect(g, px, y - 2, pw, h + 4, '#FFFFFF'); rect(g, f < .5 ? px + pw - 1 : px, y - 2, 1, h + 4, '#C8BCA8'); }
  }
}

// ---------------------------------------------------------------- shots
const SCENES = {
  title(g, t, s) {
    const u = local(t, s);
    seaside(g, t, 'day');
    for (let i = 0; i < 4; i++) seagull(g, R(((u * 22 + i * 60) % 560)) - 40, 64 + i * 10 + R(Math.sin(t * 2 + i) * 3), t + i);
    const wx = lerp(-20, 170, seg(u, 5.5, 10.3));
    if (u > 5.4) person(g, 'me', wx, 244, 2, { walk: beatPos(t) / 2, look: 1, eyes: 'happy', mouth: 'smile' }, t);
    const shown = Math.ceil(seg(u, 1.6, 3) * 2);
    if (shown > 0) ptext(g, [...'小宇'].slice(0, shown).join(''), 240, 88, { size: 48, col: '#FFFFFF', outline: INK, shadow: '#3A6AA8' });
    if (u > 3.6) ptext(g, '张震岳 · 像素 MV', 240, 112, { col: '#FFFFFF', outline: INK });
    blackout(g, 1 - seg(u, .2, 2));
  },
  surprise(g, t, s) {
    const u = local(t, s), land = 3.4;
    seaside(g, t, 'day');
    const wx = lerp(90, 210, eout(seg(u, 0, 2.2)));
    const P = person(g, 'me', wx, 246, 3, { walk: u < 2.2 ? beatPos(t) / 2 : null, look: u > 1.6 && u < land ? 1 : 0, eyes: u > land ? 'wide' : 'open', mouth: u > land ? 'open' : 'smile' }, t);
    if (u > 1.2 && u < land + .3) windLines(g, t, 14, 3, '#FFFFFF', 40, 200);
    if (P) {
      const hx = u < land ? lerp(520, P.face[0], eio(seg(u, 1.2, land))) + Math.sin(u * 5) * 30 * (1 - seg(u, 1.2, land)) : P.face[0];
      const hy = u < land ? lerp(70, P.face[1] - 22, eio(seg(u, 1.2, land))) - Math.sin(seg(u, 1.2, land) * Math.PI) * 50 : P.face[1] - 22;
      if (u > 1.2) sunhat(g, hx, hy, 2);
      if (u > land) { rect(g, P.face[0] + 34, P.face[1] - 52, 4, 14, INK); rect(g, P.face[0] + 35, P.face[1] - 51, 2, 12, '#FFE08A'); rect(g, P.face[0] + 34, P.face[1] - 34, 4, 4, INK); rect(g, P.face[0] + 35, P.face[1] - 33, 2, 2, '#FFE08A'); for (let i = 0; i < 4; i++) sparkle(g, P.face[0] - 40 + i * 26, P.face[1] - 40 + (i % 2) * 10, 1 + (i % 2)); }
    }
  },
  meet(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0;
    seaside(g, t, 'day');
    const sx = lerp(520, 300, eout(seg(u, 0, 1.6))), worn = u > 3.4;
    const A = person(g, 'me', 210, 246, 3, { aR: worn ? 'down' : 'out', eyes: u > 1.6 ? 'happy' : 'wide', mouth: 'smile', blush: u > 2, look: 1 }, t);
    const B = person(g, 'you', sx, 246, 3, { walk: u < 1.6 ? beatPos(t) : null, aL: u > 2.4 && !worn ? 'reach' : 'down', eyes: u > 2 ? 'happy' : 'open', mouth: 'smile', blush: u > 2, look: -1 }, t);
    if (A && !worn) sunhat(g, A.R[0] + 6, A.R[1] - 4, 2);
    if (B && worn) sunhat(g, B.face[0], B.face[1] - 22, 2);
    // the moment slows down: sparkles and petals hang in the air
    const slow = seg(u, 1.6, 2.4);
    if (slow > 0) { for (let i = 0; i < 18; i++) { const x = R(120 + H(i) * 260 + Math.sin(t * .4 + i) * 6), y = R(70 + H(i + 4) * 130 + Math.cos(t * .3 + i) * 4); if ((Math.floor(t * 3 + i) % 3) && H(i + 9) < slow) sparkle(g, x, y, 1 + (i % 2), i % 3 ? '#FFFFFF' : '#FFC8D8'); } petals(g, t * .25, 24, ['#FFB0C8', '#FFFFFF'], 4); }
    if (u > 2.6) heart(g, 255, 130 + R(Math.sin(t * 3) * 2), 2, '#FF5C8A');
    void d;
  },
  eyes(g, t, s) {
    const u = local(t, s);
    grad(g, ['#7AC0F4', '#BFE4FA', '#F2FAFF'], 0, PH);
    for (let i = 0; i < 4; i++) cloud(g, R(((t * 6 + i * 150) % 640) - 90), 26 + i * 40, 1.6, '#FFFFFF', '#E0EEF8');
    const blink = u > 3.1 && u < 3.35;
    const k = 9, x = 240, y = 306;
    person(g, 'you', x, y, k, { eyes: blink ? 'closed' : 'sparkle', mouth: 'smile', blush: true }, t);
    if (!blink) for (const ex of [-5, 3]) {
      // the sky and a tiny him reflected in each eye
      const X = x + ex * k, Y = y + (7 - 31) * k;
      rect(g, X + 4, Y + 4, 10, 4, '#8EC8F4'); rect(g, X + 6, Y + 3, 6, 2, '#FFFFFF');
      rect(g, X + 8, Y + 12, 2, 3, '#F2C14E'); rect(g, X + 8, Y + 10, 2, 2, '#5A3A22');
      if (Math.floor(t * 3 + ex) % 4 === 0) sparkle(g, X + k * 2 + 4, Y - 2, 2);
    }
    for (let i = 0; i < 10; i++) if (Math.floor(t * 5 + i) % 3 === 0) sparkle(g, R(60 + H(i) * 360), R(30 + H(i + 3) * 120), 1 + (i % 2));
  },
  dream(g, t, s) {
    const u = local(t, s);
    room(g);
    rect(g, 330, 30, 100, 80, INK); gradRect(g, TIMES.night.sky, 334, 34, 92, 72); moon(g, 402, 56, 9); rect(g, 378, 30, 4, 80, INK); rect(g, 330, 68, 100, 4, INK);
    rect(g, 60, 180, 240, 10, '#6A4A3A'); rect(g, 52, 150, 12, 70, '#6A4A3A'); rect(g, 64, 170, 230, 20, '#F4F0E8');
    g.save(); g.beginPath(); g.rect(0, 0, PW, 182); g.clip(); person(g, 'me', 104, 236, 3, { eyes: 'closed', mouth: 'smile', blush: u > 1.5 }, t); g.restore();
    rect(g, 64, 178, 236, 34, '#5A9AD8'); for (let x = 64; x < 300; x += 12) rect(g, x, 178, 6, 34, '#4A86C4'); rect(g, 64, 178, 236, 2, INK);
    for (let i = 0; i < 3; i++) { const p = (u * .6 + i / 3) % 1; ptext(g, 'Z', R(140 + p * 30 + i * 4), R(150 - p * 40), { size: 12 + i * 12 > 36 ? 24 : 12, col: '#FFFFFF', outline: INK }); }
    // the dream: her, among the stars
    const gr = eout(seg(u, .3, 1.2));
    if (gr > 0) {
      const cx = 250, cy = 86, W = R(150 * gr), Hh = R(100 * gr);
      for (const [dx, dy, r] of [[-.4, -.2, .32], [0, -.35, .36], [.4, -.15, .3], [-.25, .25, .3], [.25, .25, .32]]) disc(g, cx + dx * W, cy + dy * Hh, r * Math.min(W, Hh * 1.4) + 2, INK);
      for (const [dx, dy, r] of [[-.4, -.2, .32], [0, -.35, .36], [.4, -.15, .3], [-.25, .25, .3], [.25, .25, .32]]) disc(g, cx + dx * W, cy + dy * Hh, r * Math.min(W, Hh * 1.4), '#3A3A7A');
      if (gr > .9) { stars(g, t, 30, 150, 9, cx - 70, cx + 70); person(g, 'you', cx, cy + 40, 2, { eyes: 'sparkle', mouth: 'smile', blush: true, aR: 'wave', glow: '#FFE8F0' }, t); }
      for (let i = 0; i < 3; i++) disc(g, 160 - i * 16, 140 + i * 8, 4 - i, '#3A3A7A');
    }
  },
  becloud(g, t, s) {
    const u = local(t, s), turn = 1.3;
    grad(g, TIMES.day.sky, 0, 200);
    for (let i = 0; i < 3; i++) cloud(g, R(((t * 4 + i * 180) % 640) - 90), 30 + i * 22, 1.3);
    disc(g, 240, 470, 270, '#5E9E52'); disc(g, 240, 474, 266, '#7DBE6A');
    for (let i = 0; i < 40; i++) { const x = R(H(i) * PW), y = R(214 + H(i + 4) * 60); rect(g, x, y, 1, 3, '#5E9E52'); if (i % 4 === 0) rect(g, x - 1, y - 2, 3, 2, ['#FFFFFF', '#FFD860', '#FF8FB0'][i % 3]); }
    if (u < turn) person(g, 'me', 240, 230, 3, { aL: 'up', aR: 'up', eyes: 'closed', mouth: 'smile' }, t);
    const burst = seg(u, turn - .3, turn + .5);
    if (burst > 0 && burst < 1) for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2, r = burst * 70; sparkle(g, R(240 + Math.cos(a) * r), R(170 + Math.sin(a) * r * .7), 2, i % 2 ? '#FFFFFF' : '#FFE08A'); }
    if (u >= turn) { const up = eio(seg(u, turn + .2, 5.2)); cloudKid(g, 240 + Math.sin(u * 1.5) * 10, lerp(180, 80, up), 3, { eyes: u < turn + 1 ? 'wide' : 'happy' }, t); }
    whiteout(g, Math.max(0, 1 - Math.abs(u - turn) / .25) * .8);
  },
  drift(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0;
    grad(g, TIMES.day.sky, 0, 200);
    windLines(g, t, 12, 9, '#FFFFFF', 20, 130);
    // her house and garden
    rect(g, 0, 200, PW, 70, '#7DBE6A'); for (let x = 0; x < PW; x += 6) rect(g, x, 198 + (x % 4 ? 0 : 1), 2, 3, '#5E9E52');
    rect(g, 300, 120, 140, 82, INK); rect(g, 302, 122, 136, 80, '#F4EEE4'); for (let j = 0; j < 30; j++) rect(g, 296 + j * 2, 120 - j, 148 - j * 4, 1, j % 5 ? '#3A78D0' : '#2A5AA8');
    rect(g, 316, 140, 30, 24, INK); rect(g, 318, 142, 26, 20, '#BFE6FF'); rect(g, 396, 140, 30, 24, INK); rect(g, 398, 142, 26, 20, '#BFE6FF'); rect(g, 356, 166, 26, 36, INK); rect(g, 358, 168, 22, 34, '#5A9AD8');
    for (let i = 0; i < 8; i++) rect(g, 300 + i * 18, 196, 3, 6, ['#FF8FB0', '#FFD860', '#FFFFFF'][i % 3]);
    rect(g, 0, 196, 280, 2, '#F6F6F6'); for (let x = 6; x < 280; x += 14) rect(g, x, 186, 3, 14, '#F6F6F6');
    person(g, 'you', 230, 240, 2, { aR: u > 1.4 && u < 4 ? 'wave' : 'down', eyes: 'open', mouth: 'smile', look: R(clamp((cx(u) - 230) / 60, -1, 1)) }, t);
    function cx(v) { return v < 1.6 ? lerp(-50, 200, eout(v / 1.6)) : v < 3.4 ? lerp(200, 250, (v - 1.6) / 1.8) : lerp(250, 560, Math.pow(seg(v, 3.4, d), 1.6)); }
    cloudKid(g, cx(u), 70, 2, { eyes: u > 1.8 && u < 3.6 ? 'strain' : u > 3.6 ? 'closed' : 'open', mouth: u > 1.8 && u < 3.6 ? 'o' : 'smile' }, t);
  },
  drizzle(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0;
    grad(g, ['#7A9AC8', '#A8C4E4', '#E2EEF8'], 0, 200);
    rect(g, 0, 200, PW, 70, '#7DBE6A'); for (let x = 0; x < PW; x += 6) rect(g, x, 198 + (x % 4 ? 0 : 1), 2, 3, '#5E9E52');
    // rain comes in little showers, on the beat
    const burst = .4 + .6 * kickPulse(t, 3);
    for (let i = 0; i < R(150 * seg(u, .5, 1.5) * burst); i++) { const y = R((t * (130 + 40 * H(i)) + H(i * 7) * 170) % 170) + 96, x = R(160 + H(i * 3) * 160); rect(g, x, y, 1, 5, '#3A6AC0'); rect(g, x, y + 5, 1, 1, '#FFFFFF'); }
    for (let i = 0; i < 8; i++) { const p = (t * 1.6 + H(i)) % 1; if (p < .5) ring(g, R(180 + H(i + 3) * 120), R(232 + H(i) * 20), R(1 + p * 8), '#BFE6FF'); }
    if (u > d - 1.8) { const a = seg(u, d - 1.8, d - .6); ['#E04A3A', '#F2A040', '#F2D840', '#7DBE6A', '#5A9AD8', '#9A6AD0'].forEach((c, i) => { for (let q = 0; q < 180 * a; q += 2) { const an = Math.PI + q / 180 * Math.PI; rect(g, R(240 + Math.cos(an) * (150 - i * 4)), R(210 + Math.sin(an) * (110 - i * 4)), 2, 2, c); } }); }
    cloudKid(g, 240, 70, 4, { rain: true, eyes: u < 1.4 ? 'strain' : 'happy', mouth: u < 1.4 ? 'o' : 'smile' }, t);
    person(g, 'you', 240, 244, 3, { aL: 'up', aR: 'up', eyes: 'closed', mouth: 'smile', blush: true }, t);
  },
  bloom(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, cx = 240, cy = 168, S = 66;
    grad(g, ['#9AC4EC', '#CDE4F6', '#F2F8FC'], 0, PH);
    for (let i = 0; i < 90; i++) { const y = R((t * 150 + H(i * 7) * 200) % 200) + 50, x = R(150 + H(i * 3) * 180); rect(g, x, y, 1, 5, '#3A6AC0'); }
    cloudKid(g, 240, 48, 3, { rain: true, eyes: 'happy' }, t);
    bigHeart(g, cx, cy, S, '#A87A4A', INK, { shine: false });
    const grow = eio(seg(u, .4, d - .6)) * S * 1.4;
    for (let j = -R(S * 1.25); j <= R(S * 1.1); j++) for (let i = -R(S * 1.25); i <= R(S * 1.25); i++) {
      if (!inHeart(i, j, S - 2)) continue;
      const r = Math.sqrt(i * i + j * j * 1.2);
      if (r < grow) rect(g, cx + i, cy + j, 1, 1, bayer(cx + i, cy + j) < .2 ? '#6CB05A' : '#7DC46A');
      else if ((i * 7 + j * 13) % 23 === 0) rect(g, cx + i, cy + j, 2, 1, '#8A5E36');
    }
    for (let i = 0; i < 70; i++) {
      const fx = R((H(i) - .5) * S * 2), fy = R((H(i + 9) - .5) * S * 2);
      if (!inHeart(fx, fy, S - 6) || Math.sqrt(fx * fx + fy * fy * 1.2) > grow - 6) continue;
      rect(g, cx + fx, cy + fy - 3, 1, 3, '#3E7A3A'); rect(g, cx + fx - 1, cy + fy - 5, 3, 2, ['#FF8FB0', '#FFFFFF', '#FFD860', '#E8436E'][i % 4]);
    }
  },
  future(g, t, s) {
    const u = local(t, s), turn = u > 2.6;
    beach(g, t, 'day');
    for (let i = 0; i < 4; i++) { const x = 70 + i * 110 + R(Math.sin(t * .6 + i) * 6); checker(g, x - 34, 90, 70, 44, '#FFFFFF', .45); qmark(g, x, 92 + R(Math.sin(t + i) * 2), 4, '#FFFFFF'); }
    checker(g, 0, 110, PW, 24, '#FFFFFF', .35);
    person(g, 'me', 214, 246, 3, turn ? { look: 1, eyes: 'happy', mouth: 'open', aL: 'out', aR: 'out' } : { back: true }, t);
    person(g, 'you', 268, 246, 3, turn ? { look: -1, eyes: 'happy', mouth: 'smile', blush: true, aL: 'out', aR: 'out' } : { back: true }, t);
  },
  fun(g, t, s) {
    const u = local(t, s);
    beach(g, t, 'day');
    for (let i = 0; i < 3; i++) seagull(g, R(((u * 30 + i * 70) % 560)) - 40, 50 + i * 10, t + i);
    const hop = i => (beatPhase(t + i * .25) < .3 ? -6 : 0);
    const A = person(g, 'me', 190, 244, 3, { aR: 'up', eyes: 'happy', mouth: 'open', dy: hop(0) }, t);
    const B = person(g, 'you', 290, 244, 3, { aL: 'up', eyes: 'happy', mouth: 'smile', blush: true, dy: hop(1) }, t);
    if (A) iceCream(g, A.R[0], A.R[1] - 6, '#FF9AB8');
    if (B) iceCream(g, B.L[0], B.L[1] - 6, '#8FE0F0');
    const p = (u * .8) % 1, side = Math.floor(u * .8) % 2, bx = R(lerp(side ? 290 : 190, side ? 190 : 290, p)), by = R(140 - Math.sin(p * Math.PI) * 60);
    disc(g, bx, by, 9, INK); disc(g, bx, by, 8, '#FFFFFF'); rect(g, bx - 8, by - 2, 16, 4, '#E8436E'); rect(g, bx - 2, by - 8, 4, 16, '#5A9AD8'); rect(g, bx - 4, by - 6, 2, 2, '#FFFFFF');
    for (let i = 0; i < 12; i++) { const a = (t * 1.5 + H(i)) % 1; rect(g, R(170 + H(i + 2) * 140 + a * 10), R(240 - a * 16), 2, 2, '#CFEFFF'); }
  },
  ending(g, t, s) {
    const u = local(t, s);
    grad(g, ['#FFD49A', '#FFE8C0', '#FFF6E4'], 0, PH);
    for (let i = 0; i < 20; i++) if (Math.floor(t * 4 + i) % 3) sparkle(g, R(H(i) * PW), R(H(i + 3) * 200), 1, '#FFFFFF');
    rect(g, 0, 236, PW, 34, '#E8C890');
    storyBook(g, t, 240, 116, Math.min(3, u * .75));
    const done = u > 4;
    person(g, 'me', 120, 250, 2, { look: 1, eyes: done ? 'happy' : 'open', mouth: done ? 'smile' : 'none', aL: done ? 'out' : 'down', aR: done ? 'out' : 'down' }, t);
    person(g, 'you', 360, 250, 2, { look: -1, eyes: done ? 'happy' : 'open', mouth: done ? 'smile' : 'none', aL: done ? 'out' : 'down', aR: done ? 'out' : 'down' }, t);
  },
  missing(g, t, s) {
    const u = local(t, s);
    grad(g, TIMES.night.sky, 0, 220); stars(g, t, 120, 200, 11);
    // the stars join up, one line at a time, into her
    const pts = [[330, 30], [316, 38], [310, 54], [314, 70], [322, 80], [338, 80], [346, 70], [350, 54], [344, 38], [330, 30], [306, 64], [300, 100], [314, 92], [304, 140], [356, 140], [346, 92], [360, 100], [350, 64]];
    const n = Math.min(pts.length - 1, u * 4.2);
    for (let i = 0; i < Math.floor(n); i++) if (i !== 9) line(g, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], '#8FA8E0');
    if (n % 1 > 0 && Math.floor(n) !== 9) { const a = pts[Math.floor(n)], b = pts[Math.floor(n) + 1], f = n % 1; line(g, a[0], a[1], R(lerp(a[0], b[0], f)), R(lerp(a[1], b[1], f)), '#8FA8E0'); }
    pts.forEach(([x, y], i) => { if (i <= n + 1) { rect(g, x - 1, y - 1, 3, 3, '#FFFFFF'); if (Math.floor(t * 3 + i) % 3 === 0) sparkle(g, x, y, 2); } });
    if (n > 16) { halo(g, 330, 84, 60, '#8FA8E0', .6); sparkle(g, 346, 34, 3, '#FFE8F0'); }
    rect(g, 0, 214, PW, 56, '#2A3048'); rect(g, 0, 214, PW, 3, '#4A5070'); for (let x = 0; x < PW; x += 30) rect(g, x, 217, 1, 53, '#232840');
    person(g, 'me', 150, 222, 3, { sit: true, eyes: n > 16 ? 'happy' : 'open', mouth: 'smile', blush: n > 16, look: 1 }, t);
  },
  game(g, t, s) {
    const u = local(t, s), off = u > 2.8;
    rect(g, 0, 0, PW, PH, '#160E2A'); for (let i = 0; i < 6; i++) { rect(g, 20 + i * 80, 30, 50, 2, ['#FF5CC8', '#5CE0FF', '#FFE05C'][i % 3]); }
    rect(g, 0, 210, PW, 60, '#241A3A'); for (let x = 0; x < PW; x += 20) for (let y = 210; y < PH; y += 20) if (((x + y) / 20) % 2) rect(g, x, y, 20, 20, '#2C2246');
    const cx = 300;
    rect(g, cx - 56, 50, 112, 172, INK); rect(g, cx - 54, 52, 108, 168, '#6A3AA8'); rect(g, cx - 54, 52, 108, 14, '#8A5AD0'); ptext(g, 'GAME', cx, 64, { col: '#FFE05C' });
    rect(g, cx - 44, 72, 88, 66, INK);
    if (!off) {
      rect(g, cx - 42, 74, 84, 62, '#102040');
      for (let i = 0; i < 3; i++) heart(g, cx - 24 + i * 24, 92, 2, '#FF5C8A', null);
      if (Math.floor(t * 3) % 2) ptext(g, 'PLAY?', cx, 124, { col: '#FFFFFF' });
      halo(g, cx, 105, 60, '#5CE0FF', .4);
    } else if (u < 3.05) { for (let y = 74; y < 136; y++) for (let x = cx - 42; x < cx + 42; x += 2) if (H(x * 7 + y * 13 + R(t * 60)) > .5) rect(g, x, y, 2, 1, '#FFFFFF'); }
    else { rect(g, cx - 42, 74, 84, 62, '#0A0A14'); const w = R(84 * clamp(1 - (u - 3.05) * 3)); if (w > 0) rect(g, cx - w / 2, 104, w, 2, '#FFFFFF'); }
    rect(g, cx - 54, 150, 108, 26, '#4A2A80'); rect(g, cx - 30, 152, 4, 12, INK); disc(g, cx - 28, 152, 4, '#E8436E'); disc(g, cx + 10, 162, 4, '#5CE0FF'); disc(g, cx + 26, 162, 4, '#FFE05C');
    // the plug and its cable
    const pullX = off ? R(lerp(cx + 70, cx + 120, seg(u, 2.6, 2.9))) : cx + 70;
    line(g, cx + 54, 206, pullX - 6, 214, INK); rect(g, pullX - 6, 210, 8, 8, INK); rect(g, pullX - 5, 211, 6, 6, '#8A8AA0'); rect(g, cx + 76, 202, 10, 16, '#D8D8E0'); rect(g, cx + 79, 206, 1, 3, INK); rect(g, cx + 82, 206, 1, 3, INK);
    const shake = u > 1.6 && u < 2.6 ? (Math.floor(u * 6) % 2 ? 1 : -1) : 1;
    if (!off) halo(g, 150, 180, 40, '#5CE0FF', .3);
    const P = person(g, 'me', off ? cx + 120 : 150, 250, 3, { eyes: off ? 'happy' : 'open', mouth: off ? 'smile' : 'flat', look: shake, aR: u > 2.4 && u < 3.2 ? 'out' : 'down', walk: u > 2.0 && u < 2.6 ? beatPos(t) : null }, t);
    void P;
  },
  sincere(g, t, s) {
    const u = local(t, s);
    seaside(g, t, 'sunset');
    const A = person(g, 'me', 196, 246, 4, { aL: 'hold', aR: 'hold', eyes: 'open', mouth: 'smile', look: 1, blush: true }, t);
    person(g, 'you', 316, 246, 4, { eyes: u > 1.5 ? 'sparkle' : 'wide', mouth: u > 2 ? 'smile' : 'none', blush: u > 1.5, look: -1 }, t);
    if (A) { const b = 1 + .12 * Math.sin(t * 7); halo(g, A.R[0], A.R[1] - 10, R(34 * b), '#FFC8C8'); bigHeart(g, A.R[0], A.R[1] - 12, R(12 * b), '#E8436E', INK); }
  },
  unsaid(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, back = seg(u, 2.2, 3.2);
    seaside(g, t, 'day');
    person(g, 'you', 410, 210, 2, { back: true }, t);
    const A = person(g, 'me', 200, 248, 4, { eyes: u > 3.4 ? 'closed' : 'open', mouth: u > 3.2 ? 'none' : 'flat', look: 1 }, t);
    if (A) {
      if (back < 1) { const sc = 1 - back, w = R(80 * sc), h = R(56 * sc), bx = A.face[0] + 10, by = A.face[1] - 80 + R(back * 60); if (w > 8) { bubble(g, bx, by, w, h, A.face[0] + 4, A.face[1] - 10); padlock(g, bx + w / 2, by + h / 2 + 2, Math.max(1, R(4 * sc))); } }
      if (u > 3.2) { const mx = A.face[0], my = A.face[1] + 3 * 4 + 2; rect(g, mx - 12, my - 1, 24, 5, INK); rect(g, mx - 11, my, 22, 3, '#C8C8D8'); for (let x = -10; x < 10; x += 2) rect(g, mx + x, my + 1, 1, 1, INK); rect(g, mx + R(lerp(-11, 9, seg(u, 3.2, 3.9))), my - 2, 3, 7, '#F2C14E'); }
    }
    void d;
  },
  quiz(g, t, s) {
    const u = local(t, s), fall = seg(u, 1.8, 4.6);
    grad(g, ['#2A1E5A', '#5A3A8A', '#9A6AB0'], 0, PH);
    for (let i = 0; i < 30; i++) rect(g, R(H(i) * PW), R(H(i + 2) * PH), 1, 1, '#C8A8E8');
    rect(g, 140, 18, 200, 112, INK); rect(g, 142, 20, 196, 108, '#2E5A44'); rect(g, 142, 20, 196, 4, '#8A6A4A'); rect(g, 142, 124, 196, 4, '#8A6A4A');
    qmark(g, 240, 28, 2, '#F4F4E8');
    ['A', 'B', 'C', 'D'].forEach((c, i) => { const x = 168 + (i % 2) * 96, y = 66 + Math.floor(i / 2) * 30; rect(g, x - 1, y - 9, 12, 12, '#F4F4E8'); rect(g, x, y - 8, 10, 10, '#2E5A44'); ptext(g, c, x + 24, y + 2, { col: '#F4F4E8' }); if (Math.floor(t * 4) % 4 === i) rect(g, x + 2, y - 6, 6, 6, '#FFE08A'); });
    // the floor opens into a big question mark
    const open = eout(seg(u, 1.4, 1.9));
    rect(g, 0, 214, PW, 56, '#3A2A5E');
    if (open > 0) { const w = R(70 * open); for (let j = 0; j < 20; j++) { const ww = R(w * Math.sqrt(1 - Math.pow(j / 20, 2))); rect(g, 280 - ww, 214 + j - 2, ww * 2, 1, '#0A0618'); } }
    const fy = R(244 + fall * fall * 140);
    g.save(); g.beginPath(); g.rect(0, 0, PW, fall > 0 ? 226 : PH); g.clip();
    person(g, 'you', 280, fy, 3, { eyes: fall > 0 ? 'wide' : 'open', mouth: fall > 0 ? 'open' : 'flat', aL: fall > 0 ? 'up' : 'down', aR: fall > 0 ? 'up' : 'down', look: -1 }, t);
    g.restore();
    if (fall > 0) ['A', 'B', 'C', 'D'].forEach((c, i) => { const a = fall - i * .08; if (a > 0 && a < 1) ptext(g, c, 252 + i * 18, R(160 + a * 80 + Math.sin(t * 6 + i) * 4), { col: '#FFE08A', outline: INK }); });
    person(g, 'me', 110, 248, 3, { eyes: fall > 0 ? 'wide' : 'open', mouth: fall > 0 ? 'open' : 'flat', look: 1, aR: fall > .2 ? 'shh' : 'down' }, t);
  },
  selfish(g, t, s) {
    const u = local(t, s), grow = eio(seg(u, .2, 3)) * (1 - eio(seg(u, 3.6, 6.2))), push = u > 3.2;
    seaside(g, t, 'sunset');
    person(g, 'you', 420, 206, 2, { back: true }, t);
    const sk = R(3 + 2 * grow);
    person(g, 'me', 186 - R(grow * 10), 248, sk, { tint: '#1E1A30', tintDk: '#3A3456', aR: 'reach', alpha: .55 + .4 * grow, look: 1 }, t);
    const ex = 186 - R(grow * 10), ey = 248 - 23 * sk;
    rect(g, ex - 5 * sk, ey, 2 * sk, sk, '#FFFFFF'); rect(g, ex + 3 * sk, ey, 2 * sk, sk, '#FFFFFF');
    person(g, 'me', 240, 248, 3, { eyes: push ? 'closed' : 'sad', mouth: 'flat', look: push ? -1 : 0, aL: push ? 'stop' : 'down', flip: false }, t);
  },
  hide(g, t, s) {
    const u = local(t, s), p = seg(u, 0, 2.6), P = TIMES.night;
    grad(g, skyMix(TIMES.sunset.sky, P.sky, p, 5), 0, 148);
    stars(g, t, R(110 * p), 130, 3);
    rect(g, 0, 140, PW, 66, mixHex(TIMES.sunset.sea, P.sea, qz(p, 5))); waves(g, t, 143, 204, P, 40);
    rect(g, 0, 200, PW, 70, mixHex(TIMES.sunset.walk, P.walk, qz(p, 5))); rect(g, 0, 190, PW, 2, P.rail); rect(g, 0, 198, PW, 2, P.rail); for (let x = 4; x < PW; x += 20) rect(g, x, 190, 2, 12, P.rail);
    person(g, 'you', 420, 206, 2, { back: true, alpha: 1 - seg(u, 1.4, 3) }, t);
    person(g, 'me', 176, 248, 3, { tint: '#1E1A30', tintDk: '#3A3456', alpha: .55 * (1 - seg(u, .4, 2.6)) }, t);
    person(g, 'me', 240, 248, 3, { eyes: 'down', mouth: 'smile', aL: 'behind', aR: 'behind' }, t);
  },
  beboat(g, t, s) {
    const u = local(t, s), turn = 1.4, P = TIMES.night;
    grad(g, P.sky, 0, 150); stars(g, t, 100, 140, 13); moon(g, 360, 44, 12);
    rect(g, 0, 148, PW, 122, '#162452'); waves(g, t, 150, 268, P, 70);
    for (let i = 0; i < 14; i++) rect(g, 350 + R(H(i + Math.floor(t * 4)) * 22), 152 + i * 8, 6 + i, 1, '#F4F0D8');
    rect(g, 0, 214, 120, 56, '#2A3A30'); for (let x = 0; x < 120; x += 5) rect(g, x, 212 + (x % 3), 1, 4, '#3A5A40');
    if (u < turn) person(g, 'me', 90, 222, 3, { eyes: 'closed', mouth: 'smile', aL: 'up', aR: 'up' }, t);
    const burst = seg(u, turn - .3, turn + .5);
    if (burst > 0 && burst < 1) for (let i = 0; i < 16; i++) { const a = i / 16 * Math.PI * 2, r = burst * 60; sparkle(g, R(150 + Math.cos(a) * r), R(200 + Math.sin(a) * r * .6), 2, i % 2 ? '#FFFFFF' : '#FFE08A'); }
    if (u >= turn) boat(g, lerp(160, 250, eout(seg(u, turn, 5.4))), 226, 2, t, { eyes: 'happy', lantern: true });
    whiteout(g, Math.max(0, 1 - Math.abs(u - turn) / .25) * .7);
  },
  lake(g, t, s) {
    const u = local(t, s), cx = 240, cy = 128, S = 92;
    rect(g, 0, 0, PW, PH, '#3A6A4A'); for (let i = 0; i < 260; i++) rect(g, R(H(i) * PW), R(H(i + 5) * PH), 2, 1, i % 2 ? '#4A7A5A' : '#2E5A3E');
    for (let i = 0; i < 26; i++) { const x = R(H(i * 3) * PW), y = R(H(i * 5) * PH); if (inHeart(x - cx, y - cy, S + 14)) continue; disc(g, x, y, 7, INK); disc(g, x, y, 6, '#2E6A3A'); disc(g, x - 2, y - 2, 3, '#4E8A4A'); }
    bigHeart(g, cx, cy, S, '#3A76C0', INK, { shine: false });
    for (let i = 0; i < 40; i++) { const x = R((H(i) - .5) * S * 2), y = R((H(i + 1) - .5) * S * 2); if (inHeart(x, y, S - 8) && Math.sin(t * 2 + i) > 0) rect(g, cx + x, cy + y, 5, 1, '#8ABCF0'); }
    // piers all round, every one of them closed
    for (let i = 0; i < 6; i++) {
      const th = i / 6 * Math.PI * 2 + .5, [px, py] = heartPt(cx, cy, S * 1.04, th), [qx, qy] = heartPt(cx, cy, S * .84, th);
      line(g, px, py, qx, qy, '#8A5A34'); line(g, px + 1, py, qx + 1, qy, '#8A5A34');
      const near = Math.abs(((u * .55 + 0) % (Math.PI * 2)) - th) < .3;
      rect(g, qx - 4, qy - 4, 9, 9, INK); rect(g, qx - 3, qy - 3, 7, 7, near ? '#FF5050' : '#E8436E'); line(g, qx - 2, qy - 2, qx + 2, qy + 2, '#FFFFFF'); line(g, qx + 2, qy - 2, qx - 2, qy + 2, '#FFFFFF');
    }
    const th = u * .55, [bx, by] = heartPt(cx, cy, S * .66, th), [nx] = heartPt(cx, cy, S * .66, th + .05);
    for (let i = 1; i < 10; i++) { const [wx, wy] = heartPt(cx, cy, S * .66, th - i * .04); rect(g, wx, wy + 2, 1, 1, '#CFE6FF'); }
    tinyBoat(g, bx, by, nx > bx ? 1 : -1);
  },
  search(g, t, s) {
    const u = local(t, s), P = TIMES.night, spot = u > 3.2;
    grad(g, P.sky, 0, 150); stars(g, t, 100, 140, 17); moon(g, 90, 40, 9);
    rect(g, 0, 146, PW, 124, '#14204C'); waves(g, t, 148, 268, P, 70);
    for (let i = 0; i < 9; i++) { rect(g, 380 + i * 9, 140 - (i % 3) * 3, 7, 6 + (i % 3) * 3, '#1A2448'); if (Math.floor(t * 2 + i) % 3) rect(g, 382 + i * 9, 142, 2, 2, '#FFE08A'); }
    lighthouse(g, 436, 146, t, true);
    boat(g, 170, 230, 2, t, { scope: true, arm: 'out', oars: false, eyes: spot ? 'wide' : 'open', look: 1, lantern: true });
    if (spot) { for (let i = 0; i < 3; i++) sparkle(g, 214 + i * 10, 140 - (i % 2) * 8, 2, '#FFE08A'); }
  },
  harbor(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, P = TIMES.dawn;
    grad(g, P.sky, 0, 140); halo(g, 400, 140, 80, '#FFE8C8', .8);
    rect(g, 0, 136, PW, 134, P.sea); waves(g, t, 138, 268, P, 70);
    for (let i = 0; i < 7; i++) { const hx = 300 + i * 26; rect(g, hx - 1, 96 - (i % 3) * 8, 24, 42 + (i % 3) * 8, INK); rect(g, hx, 97 - (i % 3) * 8, 22, 40 + (i % 3) * 8, ['#F4EEE4', '#F2D8C0', '#E8E0F0'][i % 3]); rect(g, hx + 7, 108, 7, 7, '#FFE08A'); }
    lighthouse(g, 462, 136, t, true);
    rect(g, 300, 150, 180, 6, '#8A5A34'); for (let x = 304; x < PW; x += 20) rect(g, x, 156, 3, 20, '#6A4228');
    person(g, 'you', 340, 152, 1, { aR: 'wave', eyes: 'happy' }, t);
    lantern(g, 346, 136);
    boat(g, lerp(60, 250, eout(seg(u, 0, d))), 232, 2, t, { eyes: 'happy', mouth: 'smile', blush: true, lantern: true });
    for (let i = 0; i < 3; i++) seagull(g, R(((u * 26 + i * 60) % 560)) - 40, 50 + i * 12, t + i, '#F4F4F4');
  },
  interlude(g, t, s) {
    const u = local(t, s), night = seg(u, 8.5, 13);
    const sky = skyMix(TIMES.sunset.sky, TIMES.night.sky, night, 6);
    grad(g, sky, 0, 132);
    if (night < .6) sun(g, 300, R(126 + night * 30), 22, '#FFE0A0', '#FFB070');
    stars(g, t, R(120 * night), 120, 7);
    rect(g, 0, 128, PW, 56, mixHex(TIMES.sunset.sea, TIMES.night.sea, qz(night, 6))); waves(g, t, 131, 182, night > .5 ? TIMES.night : TIMES.sunset, 46);
    rect(g, 0, 184, PW, 86, mixHex(TIMES.sunset.sand, TIMES.night.sand, qz(night, 6))); rect(g, 0, 184, PW, 3, '#FFFFFF');
    // lanterns rise from the beach as night falls, then fireworks over the sea
    if (u > 10) for (let i = 0; i < 18; i++) { const a = u - 10 - H(i) * 3; if (a < 0) continue; const x = R(40 + H(i + 1) * 400 + Math.sin(a + i) * 8), y = R(220 - a * (12 + 8 * H(i + 2))); if (y > -10) { halo(g, x, y, 8, '#FFC870', .8); rect(g, x - 2, y - 3, 5, 6, INK); rect(g, x - 1, y - 2, 3, 4, '#FFD880'); } }
    if (u > 15.5) fireworksIn(g, t, s.t0 + 15.5, s.t1, [60, 30, 420, 90]);
    const look = u > 15;
    const A = person(g, 'me', 210, 238, 3, look ? { sit: true, back: true } : { sit: true, aR: 'hold', aL: 'hold', eyes: 'closed', mouth: 'smile' }, t);
    person(g, 'you', 262, 238, 3, look ? { sit: true, back: true } : { sit: true, eyes: 'closed', mouth: 'smile', blush: true, look: -1 }, t);
    if (A && !look) { guitar(g, A.R[0] + 2, A.R[1] + 2); for (let i = 0; i < 4; i++) { const p = (u * .5 + i / 4) % 1; note(g, R(220 + i * 14 + Math.sin(t * 3 + i) * 6), R(170 - p * 90), '#FFFFFF'); } }
    whiteout(g, seg(u, 20.6, 21.25) * .8);
  },
  ride(g, t, s) {
    const u = local(t, s), P = TIMES.night, sc = u * 150;
    grad(g, P.sky, 0, 140); stars(g, t, 80, 120, 19); moon(g, 400, 36, 10);
    fireworksIn(g, t, s.t0 - 3, s.t1, [40, 20, 300, 70]);
    rect(g, 0, 136, PW, 66, P.sea); waves(g, t, 138, 200, P, 40); for (let i = 0; i < 10; i++) rect(g, 392 + R(H(i + Math.floor(t * 4)) * 16), 140 + i * 6, 4 + i, 1, '#F4F0D8');
    rect(g, 0, 200, PW, 8, '#6A6E8A'); for (let x = -40; x < PW + 40; x += 40) rect(g, R(x - (sc * .9) % 40), 194, 2, 8, '#8A8EAA');
    rect(g, 0, 208, PW, 62, '#2A2E44'); for (let x = -40; x < PW + 40; x += 40) rect(g, R(x - sc % 40), 244, 20, 2, '#E8E0C8');
    for (let i = -1; i < 4; i++) lamp(g, R(i * 180 - (sc * 1.2) % 180 + 60), 208, 90, 1, P.glow);
    const by = 254 + (beatPhase(t) < .5 ? -1 : 0);
    bike(g, 236, by, t, 1.6);
    person(g, 'me', 248, by - 30, 3, { sit: true, aR: 'out', eyes: 'happy', mouth: 'open' }, t);
    person(g, 'you', 208, by - 28, 3, { sit: true, aL: u > 2 ? 'wave' : 'down', eyes: 'happy', mouth: 'smile', blush: true }, t);
    windLines(g, t, 8, 9, '#8A92B8', 150, 230);
  },
  wheel(g, t, s) {
    const u = local(t, s), P = TIMES.night;
    grad(g, P.sky, 0, PH); stars(g, t, 80, 200, 23);
    fireworksIn(g, t, s.t0 - 2, s.t1, [40, 20, 440, 80]);
    if (u < 1.8) {
      const cx = 260, cy = 120, r = 88, rot = t * .25;
      rect(g, cx - 2, cy, 4, 140, '#6A6E8A'); line(g, cx, cy, cx - 50, 260, '#6A6E8A'); line(g, cx, cy, cx + 50, 260, '#6A6E8A');
      for (let i = 0; i < 12; i++) { const a = rot + i / 12 * Math.PI * 2; line(g, cx, cy, R(cx + Math.cos(a) * r), R(cy + Math.sin(a) * r), '#8A8EAA'); }
      ring(g, cx, cy, r, '#B8BCD8'); ring(g, cx, cy, r - 1, '#B8BCD8');
      for (let i = 0; i < 24; i++) { const a = rot + i / 24 * Math.PI * 2; if ((i + Math.floor(t * 4)) % 3) rect(g, R(cx + Math.cos(a) * r), R(cy + Math.sin(a) * r), 2, 2, ['#FF5C8A', '#FFE08A', '#5CE0FF'][i % 3]); }
      for (let i = 0; i < 8; i++) { const a = rot + i / 8 * Math.PI * 2, gx = R(cx + Math.cos(a) * r), gy = R(cy + Math.sin(a) * r); rect(g, gx - 7, gy, 14, 12, INK); rect(g, gx - 6, gy + 1, 12, 10, ['#E8436E', '#F2C14E', '#5A9AD8', '#7DBE6A'][i % 4]); rect(g, gx - 4, gy + 3, 8, 4, '#FFE8B0'); }
      rect(g, 0, 240, PW, 30, '#1A1E34'); for (let i = 0; i < 30; i++) rect(g, R(H(i) * PW), 244 + R(H(i + 1) * 20), 2, 2, ['#FF5C8A', '#FFE08A', '#5CE0FF'][i % 3]);
      return;
    }
    // inside their gondola
    rect(g, 70, 30, 340, 220, INK); rect(g, 74, 34, 332, 212, '#E8436E');
    g.save(); g.beginPath(); g.rect(96, 52, 288, 120); g.clip(); gradRect(g, P.sky, 96, 52, 288, 120); for (let i = 0; i < 60; i++) rect(g, R(96 + H(i) * 288), R(130 + H(i + 2) * 42), 2, 2, ['#FFE08A', '#FF9AB8', '#8FE0F0'][i % 3]); fireworksIn(g, t, s.t0 - 2, s.t1, [120, 60, 360, 100]); g.restore();
    rect(g, 94, 50, 292, 2, INK); rect(g, 94, 172, 292, 4, INK); rect(g, 238, 50, 4, 124, INK);
    rect(g, 74, 210, 332, 36, '#B8305A');
    const A = person(g, 'me', 190, 230, 3, { sit: true, eyes: 'happy', mouth: 'open', look: 1, aR: 'hold' }, t);
    person(g, 'you', 290, 230, 3, { sit: true, eyes: 'happy', mouth: 'smile', blush: true, look: -1 }, t);
    if (A) { rect(g, A.R[0], A.R[1] - 2, 1, 10, '#F4F4F4'); disc(g, A.R[0], A.R[1] - 8, 7, INK); disc(g, A.R[0], A.R[1] - 8, 6, '#FFB8D8'); rect(g, A.R[0] - 3, A.R[1] - 12, 3, 2, '#FFFFFF'); }
  },
  cinema(g, t, s) {
    const u = local(t, s), turn = u > 3, P = TIMES.night;
    if (!turn) {
      grad(g, P.sky, 0, 132); stars(g, t, 80, 120, 29);
      rect(g, 0, 128, PW, 56, P.sea); waves(g, t, 131, 182, P, 40);
      rect(g, 0, 184, PW, 86, P.sand);
      rect(g, 130, 30, 220, 120, INK); rect(g, 134, 34, 212, 112, '#F4E8D8');
      gradRect(g, TIMES.sunset.sky, 138, 38, 204, 104); sun(g, 240, 128, 14, '#FFE0A0', '#FFB070');
      if (u > .8) ptext(g, 'END', 240, 96, { size: 24, col: '#FFFFFF', outline: INK });
      rect(g, 150, 150, 3, 40, INK); rect(g, 327, 150, 3, 40, INK);
      for (let j = 0; j < 80; j++) { const w = R(6 + j * 1.3); checker(g, 240 - w, 270 - j, w * 2, 1, '#FFF2C8', .12); }
      rect(g, 170, 236, 140, 34, '#E8436E'); for (let x = 170; x < 310; x += 14) rect(g, x, 236, 7, 34, '#F4F4F4');
      person(g, 'me', 216, 262, 3, { sit: true, back: true }, t); person(g, 'you', 264, 262, 3, { sit: true, back: true }, t);
      return;
    }
    // reverse shot: the screen light flickers on them, and they are looking at each other
    rect(g, 0, 0, PW, PH, '#0E1230'); stars(g, t, 50, 140, 31);
    const fl = .25 + .1 * Math.sin(t * 13) + .05 * Math.sin(t * 31);
    halo(g, 240, 150, 150, '#FFE8C8', fl * 2.6);
    rect(g, 0, 214, PW, 56, '#2A2A48');
    person(g, 'me', 206, 244, 4, { sit: true, eyes: 'happy', mouth: 'smile', look: 1, blush: true }, t);
    person(g, 'you', 274, 244, 4, { sit: true, eyes: 'happy', mouth: 'smile', look: -1, blush: true }, t);
    heart(g, 240, 104 + R(Math.sin(t * 3) * 2), 2, '#FF5C8A');
  },
  plane(g, t, s) {
    const u = local(t, s), P = TIMES.night;
    grad(g, P.sky, 0, PH); stars(g, t, 90, 160, 37); moon(g, 240, 40, 10);
    const house = (x, w, lit) => { rect(g, x - 2, 70, w + 4, 202, INK); rect(g, x, 72, w, 200, '#3A3A5E'); for (let y = 80; y < 270; y += 7) rect(g, x, y, w, 1, '#323254'); return lit; };
    house(-10, 160, 1); house(330, 160, 1);
    const win = (x, y, on) => { rect(g, x - 3, y - 3, 76, 66, INK); rect(g, x, y, 70, 60, on ? '#FFE8A8' : '#1E2040'); checker(g, x, y, 70, 60, '#FFFFFF', on ? .1 : 0); };
    win(60, 110, 1); win(350, 110, u > 3.1);
    g.save(); g.beginPath(); g.rect(60, 110, 70, 60); g.clip(); const A = person(g, 'me', 95, 230, 3, { aR: u < .8 ? 'up' : 'wave', eyes: 'happy', mouth: 'smile', look: 1 }, t); g.restore();
    if (u > 3.1) { g.save(); g.beginPath(); g.rect(350, 110, 70, 60); g.clip(); person(g, 'you', 385, 230, 3, { aL: 'up', eyes: 'sparkle', mouth: 'smile', blush: true, look: -1 }, t); g.restore(); }
    rect(g, 60, 168, 70, 4, '#6A4A3A'); rect(g, 350, 168, 70, 4, '#6A4A3A');
    // the paper plane with a heart flies across the street between their windows
    const f = seg(u, .8, 3.3);
    if (f > 0 && u < 4.2) {
      const px = R(lerp(120, 372, f)), py = R(120 - Math.sin(f * Math.PI) * 70 + Math.sin(f * 12) * 4);
      rect(g, px - 7, py - 1, 15, 4, INK); for (let j = 0; j < 4; j++) rect(g, px - 6 + j * 2, py - j, 12 - j * 3, 1, '#FFFFFF'); rect(g, px - 6, py + 1, 13, 1, '#D8E0F0');
      heart(g, px - 1, py - 5, 1, '#FF5C8A', null);
      for (let i = 1; i < 8; i++) { const ff = Math.max(0, f - i * .03); rect(g, R(lerp(120, 372, ff)) - 6, R(120 - Math.sin(ff * Math.PI) * 70) + 2, 1, 1, '#FFE8F0'); }
    }
    if (u > 3.3) for (let i = 0; i < 5; i++) sparkle(g, 385 + R(Math.cos(i * 1.3) * 30), 120 + R(Math.sin(i * 1.3) * 18), 1);
    void A;
  },
  onward(g, t, s) {
    const u = local(t, s), sc = u * 46;
    grad(g, TIMES.day.sky, 0, 148); sun(g, 410, 40, 16);
    for (let i = 0; i < 4; i++) cloud(g, R(((t * 30 + i * 160) % 660) - 100), 20 + i * 14, 1.2);
    rect(g, 0, 140, PW, 60, '#3A86CC'); waves(g, t, 142, 198, TIMES.day, 40);
    rect(g, 0, 200, PW, 70, '#EAD9B8'); for (let x = -24; x < PW + 24; x += 24) rect(g, R(x - sc % 24), 214, 1, 56, '#CDB894');
    rect(g, 0, 190, PW, 2, '#F6F6F6'); rect(g, 0, 198, PW, 2, '#F6F6F6'); for (let x = -20; x < PW + 20; x += 20) rect(g, R(x - sc % 20), 190, 2, 12, '#F6F6F6');
    // calendar pages and leaves blow past; he keeps walking, whistling
    for (let i = 0; i < 12; i++) { const x = R(PW + 20 - ((t * (120 + 80 * H(i)) + H(i) * 600) % 640)), y = R(60 + H(i + 3) * 160 + Math.sin(t * 3 + i) * 10); if (i % 2) { rect(g, x - 1, y - 1, 12, 14, INK); rect(g, x, y, 10, 12, '#FFFFFF'); rect(g, x, y, 10, 3, '#E8436E'); rect(g, x + 3, y + 5, 4, 4, '#8A8A9A'); } else { rect(g, x, y, 3, 2, '#7DBE6A'); rect(g, x + 1, y + 2, 1, 1, '#5E9E52'); } }
    windLines(g, t, 10, 13, '#FFFFFF', 40, 220);
    person(g, 'me', 220, 248, 3, { walk: beatPos(t) / 2, eyes: 'happy', mouth: singing(t) ? 'open' : 'smile', look: 1 }, t);
    for (let i = 0; i < 3; i++) { const p = (u * .6 + i / 3) % 1; note(g, R(244 + p * 40), R(150 - p * 50), '#FFFFFF'); }
  },
  everyday(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, i = Math.min(6, Math.floor(u / (d / 7)));
    const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    const skies = [TIMES.day.sky, ['#6A7A98', '#9AAAC4', '#C8D4E4'], TIMES.day.sky, ['#4AA6EE', '#8ED0F8', '#FFF6D8'], TIMES.night.sky, TIMES.sunset.sky, ['#5AB0F0', '#A8DCF8', '#F0FAFF']][i];
    grad(g, skies, 0, 180);
    if (i === 4) stars(g, t, 60, 150, 41);
    rect(g, 0, 180, PW, 90, i === 4 ? '#3A4058' : '#EAD9B8');
    // her front door
    rect(g, 230, 40, 220, 146, INK); rect(g, 232, 42, 216, 144, i === 4 ? '#4A4A6A' : '#F4EEE4'); for (let y = 48; y < 186; y += 7) rect(g, 232, y, 216, 1, i === 4 ? '#424262' : '#E8E0D4');
    const open = i % 2 === 0 || i === 5;
    rect(g, 306, 82, 64, 104, INK); rect(g, 308, 84, 60, 102, open ? '#FFE8A8' : '#5A9AD8');
    if (open) person(g, 'you', 338, 186, 3, { eyes: 'happy', mouth: 'smile', blush: true, look: -1 }, t);
    else { rect(g, 312, 88, 52, 94, '#5A9AD8'); rect(g, 356, 134, 4, 4, '#F2C14E'); }
    for (let j = 0; j < 3; j++) { rect(g, 250 + j * 16, 172, 10, 12, '#C8603A'); rect(g, 251 + j * 16, 166, 8, 6, ['#FF8FB0', '#FFD860', '#E8436E'][j]); }
    const P = person(g, 'me', 200, 250, 3, { aR: 'out', eyes: 'happy', mouth: 'smile', look: 1, dy: u % (d / 7) < .1 ? -4 : 0 }, t);
    if (P) { const [hx, hy] = P.R; [() => flowers(g, hx + 2, hy - 2), () => umbrellaIn(g, [hx, hy], '#E8436E', '#A82C46', 50, 20), () => kite(g, hx + 30, hy - 60, t), () => iceCream(g, hx + 2, hy - 6, '#FF9AB8'), () => lantern(g, hx + 2, hy), () => guitar(g, hx + 10, hy), () => balloon(g, hx + 2, hy, t)][i](); if (i === 2) line(g, hx, hy, hx + 30, hy - 54, '#FFFFFF'); }
    if (i === 1) rain(g, t, 90, '#8FA8D8');
    rect(g, 12, 12, 54, 22, INK); rect(g, 14, 14, 50, 18, '#FFFFFF'); rect(g, 14, 14, 50, 4, '#E8436E'); ptext(g, days[i], 39, 30, { col: INK });
  },
  closebook(g, t, s) {
    const u = local(t, s), shut = eio(seg(u, .6, 1.4)), away = eio(seg(u, 1.6, 2.6));
    grad(g, ['#FFD49A', '#FFE8C0', '#FFF6E4'], 0, PH);
    rect(g, 0, 236, PW, 34, '#E8C890');
    if (away < 1) storyBook(g, t, lerp(240, 240, away), lerp(116, -80, away), 3, { close: shut });
    const hold = u > 2.4, dx = R(eio(seg(u, 2, 3)) * 30);
    const A = person(g, 'me', 150 + dx, 250, 3, { aR: hold ? 'reach' : u < 1.4 ? 'up' : 'down', eyes: 'happy', mouth: 'smile', look: 1 }, t);
    const B = person(g, 'you', 330 - dx, 250, 3, { aL: hold ? 'reach' : 'down', eyes: hold ? 'happy' : 'open', mouth: 'smile', blush: hold, look: -1 }, t);
    if (A && B && hold) { for (let i = 0; i < 4; i++) { const p = (u * .5 + i / 4) % 1; heart(g, R(240 + Math.sin(i * 2 + t) * 30), R(170 - p * 80), 1, '#FF7FA0', null); } }
  },
  together(g, t, s) {
    const u = local(t, s);
    pier(g, t, 'sunset');
    cloudKid(g, 120 + Math.sin(t * .5) * 10, 60, 2, { eyes: 'happy' }, t);
    boat(g, 420, 226, 1, t, { empty: true });
    const hold = u > .8;
    person(g, 'me', 214, 222, 3, { aR: hold ? 'reach' : 'down', eyes: 'happy', mouth: 'smile', look: 1, blush: true }, t);
    person(g, 'you', 262, 222, 3, { aL: hold ? 'reach' : 'down', eyes: 'happy', mouth: 'smile', look: -1, blush: true }, t);
    if (hold) for (let i = 0; i < 5; i++) { const p = (u * .4 + i / 5) % 1; heart(g, R(238 + Math.sin(i * 2 + t) * 40), R(150 - p * 90), 1, '#FF7FA0', null); }
  },
  doubt(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, dusk = seg(u, 0, d);
    pier(g, t, 'sunset', dusk);
    boat(g, 420, 226, 1, t, { empty: true });
    const back = eio(seg(u, .8, 2.2)), still = u > 6.3;
    person(g, 'me', 214, 222, 3, { aR: u < 5 ? 'reach' : 'down', eyes: u > 2 ? 'sad' : 'open', mouth: 'flat', look: 1 }, t);
    person(g, 'you', 262 + R(back * 40), 222, 3, { aL: u < .8 ? 'reach' : 'hold', aR: u < .8 ? 'down' : 'hold', eyes: 'down', mouth: 'flat', look: -1, walk: back > 0 && back < 1 ? beatPos(t) : null }, t);
    if (!still) petals(g, t, 14, ['#FFB0C8', '#FFFFFF'], 7, 3);
  },
  leave(g, t, s) {
    const u = local(t, s);
    pier(g, t, 'sunset', 1);
    // he passes behind her on the way to his boat, so he is drawn first
    if (u < 3.4) {
      const wx = u < 1.8 ? 236 : lerp(236, 410, seg(u, 1.8, 3.4));
      person(g, 'me', wx, 222, 3, u < 1.8 ? { eyes: 'happy', mouth: 'smile', look: 1, aL: 'wave' } : { back: true, walk: beatPos(t) / 2 }, t);
      boat(g, 420, 226, 1, t, { empty: true });
    } else {
      const a = eio(seg(u, 3.4, 7.2)), k = a < .5 ? 2 : 1;
      boat(g, lerp(420, 436, a), lerp(226, 160, a), k, t, { back: true, lantern: true, oars: true });
    }
    person(g, 'you', 302, 222, 3, { eyes: u > 4 ? 'closed' : 'sad', mouth: 'flat', look: 1, aL: 'hold', aR: 'hold' }, t);
  },
  end(g, t, s) {
    const u = local(t, s), P = TIMES.night;
    grad(g, P.sky, 0, 150); stars(g, t, 160, 140, 43);
    moon(g, 300, 70, 26);
    cloudKid(g, R(lerp(160, 420, seg(u, 0, 16))), 60, 1, { eyes: 'closed' }, t);
    rect(g, 0, 146, PW, 124, P.sea); waves(g, t, 148, 268, P, 70);
    for (let i = 0; i < 18; i++) rect(g, 288 + R(H(i + Math.floor(t * 4)) * 26), 150 + i * 6, 6 + i, 1, '#F4F0D8');
    const bx = R(lerp(380, 450, seg(u, 0, 16)));
    halo(g, bx, 146, 6, '#FFE8A0'); rect(g, bx - 3, 146, 7, 2, INK); rect(g, bx, 140, 1, 6, INK); rect(g, bx + 1, 141, 3, 4, '#FFFFFF'); rect(g, bx - 4, 143, 2, 2, '#FFE08A');
    rect(g, 0, 214, 150, 6, '#4A3A44'); for (let x = 6; x < 150; x += 24) rect(g, x, 220, 4, 50, '#3A2A34');
    person(g, 'you', 120, 214, 1, { back: true }, t);
    const shown = Math.ceil(seg(u, 3, 4.4) * 2);
    if (shown > 0) ptext(g, [...'小宇'].slice(0, shown).join(''), 240, 120, { size: 48, col: '#FFFFFF', outline: INK, shadow: '#3A4A8A' });
    if (u > 5.2) ptext(g, '张震岳 · 像素 MV', 240, 142, { col: '#FFFFFF', outline: INK });
    blackout(g, seg(u, 13, 16.5));
  },
};
// the wooden pier at sunset; dusk 0..1 darkens it toward night
function pier(g, t, tm, dusk = 0) {
  const A = TIMES.sunset, B = TIMES.night, P = dusk > .5 ? B : A;
  grad(g, skyMix(A.sky, B.sky, dusk * .8, 5), 0, 150);
  if (dusk < .7) sun(g, 300, R(138 + dusk * 30), 22, '#FFE0A0', '#FFB070');
  stars(g, t, R(80 * dusk), 120, 47);
  rect(g, 0, 146, PW, 124, mixHex(A.sea, B.sea, qz(dusk * .8, 5))); waves(g, t, 148, 268, P, 70);
  if (dusk < .7) for (let i = 0; i < 14; i++) rect(g, 286 + R(H(i + Math.floor(t * 4)) * 28), 150 + i * 7, 8 + i * 2, 1, A.seaHi);
  rect(g, 0, 214, 440, 10, '#8A5A34'); rect(g, 0, 214, 440, 2, '#B8844E'); for (let x = 0; x < 440; x += 12) rect(g, x, 216, 1, 8, '#6A4228');
  for (let x = 8; x < 440; x += 40) rect(g, x, 224, 5, 46, '#5A3A24');
  void tm;
}

// ---------------------------------------------------------------- one frame
const XF = .3;
const NO_XF = new Set(['eyes', 'becloud', 'beboat']);
const THEME_OF = { title: 'day', surprise: 'day', meet: 'day', eyes: 'day', dream: 'night', becloud: 'day', drift: 'day', drizzle: 'day', bloom: 'day', future: 'day', fun: 'day', ending: 'sunset', missing: 'night', game: 'night', sincere: 'sunset', unsaid: 'day', quiz: 'night', selfish: 'sunset', hide: 'night', beboat: 'night', lake: 'night', search: 'night', harbor: 'night', interlude: 'sunset', ride: 'night', wheel: 'night', cinema: 'night', plane: 'night', onward: 'day', everyday: 'day', closebook: 'sunset', together: 'sunset', doubt: 'sunset', leave: 'night', end: 'night' };
let bufA = null, bufB = null;
function shotInto(g, i, t) { g.setTransform(1, 0, 0, 1, 0, 0); g.imageSmoothingEnabled = false; SCENES[SHOTS[i].name](g, t, SHOTS[i]); }
function drawFrame(g, t) {
  t = clamp(t, 0, DUR - 1e-4);
  if (!bufA) { bufA = document.createElement('canvas'); bufB = document.createElement('canvas'); bufA.width = bufB.width = PW; bufA.height = bufB.height = PH; }
  const i = shotIndex(t), s = SHOTS[i];
  if (i > 0 && t - s.t0 < XF && !NO_XF.has(s.name)) {
    shotInto(bufA.getContext('2d'), i - 1, t); shotInto(bufB.getContext('2d'), i, t);
    ditherMix(g, bufA, bufB, (t - s.t0) / XF);
  } else shotInto(g, i, t);
  subtitle(g, t, SUB_THEMES[THEME_OF[s.name] || 'day']);
}
