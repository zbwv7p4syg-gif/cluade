// scenes.js — 平凡的一天 · 像素 MV. One function per shot (see timeline.js), all in 480×270 pixels.
// Each shot gets (g, t, s): the canvas, the song time, and its entry in SHOTS (s.t0, s.t1, s.v).

const local = (t, s) => t - s.t0;
const walkPh = t => t * .85;
const TOD = {
  night: { sky: ['#0A1030', '#18244E', '#2A3A6A'], far: '#1A2448', mid: '#1E2C50', ground: '#2A3048', street: '#3A3E58', curb: '#4E5274', lit: .7, sea: '#1A2A5A', seaHi: '#8AA0E0', grass: '#22384A' },
  dawn: { sky: ['#2A3A70', '#B48AAE', '#FFD2A6'], far: '#5A5A8A', mid: '#6E6488', ground: '#5A5A70', street: '#8A8090', curb: '#A89AA8', lit: .4, sea: '#7A7AAE', seaHi: '#FFD8B8', grass: '#5A7A6A' },
  morning: { sky: ['#6AB8F0', '#A8DCF8', '#FFF4D8'], far: '#9AC0E0', mid: '#8CC08A', ground: '#9ACD6A', street: '#E8D8B8', curb: '#C8B898', lit: 0, sea: '#4A9AD8', seaHi: '#D8F0FF', grass: '#8CC86A' },
  day: { sky: ['#4AA6EE', '#8ED0F8', '#E2F6FF'], far: '#88B4DC', mid: '#7AB870', ground: '#8ACB5E', street: '#E8D8B8', curb: '#C8B898', lit: 0, sea: '#3A8AD0', seaHi: '#CFEFFF', grass: '#7EC05E' },
  dusk: { sky: ['#5A4A9A', '#F0907A', '#FFD49A'], far: '#8A6A9A', mid: '#9A7088', ground: '#A88A6A', street: '#D8B098', curb: '#B89080', lit: .25, sea: '#C87A8A', seaHi: '#FFD8A8', grass: '#8A9A5A' },
  evening: { sky: ['#1E2050', '#4A3A78', '#B0607A'], far: '#3A3060', mid: '#3A3858', ground: '#3A3A50', street: '#5A5068', curb: '#6E6480', lit: .6, sea: '#3A3A70', seaHi: '#E0A0B0', grass: '#34485A' },
};
const SUB = {
  day: { box: '#24365E', edge: '#4A6AA0', dim: '#9AB4D8', lit: '#FFFFFF' },
  dusk: { box: '#3A2448', edge: '#6A4478', dim: '#C8A0C0', lit: '#FFF0E0' },
  night: { box: '#121838', edge: '#33407A', dim: '#7F8CC0', lit: '#FFF4D8' },
};
const WALLS = ['#F4EEE4', '#F6D8C0', '#D8E8F0', '#F2E2A8', '#E8D0E0', '#D8ECD0'];
const ROOFS = ['#D8544A', '#3E82C8', '#E8A040', '#4E9A6A', '#B8607A', '#8A5A3A'];

// ---------------------------------------------------------------- scenery
let _gb = null;
function gradRect(g, stops, x, y, w, h, y0 = y, y1 = y + h) { if (!_gb) { _gb = document.createElement('canvas'); _gb.width = PW; _gb.height = PH; } grad(_gb.getContext('2d'), stops, y0, y1); g.drawImage(_gb, R(x), R(y), R(w), R(h), R(x), R(y), R(w), R(h)); }
function hills(g, P, sc, y, col, amp, seed, step = 60) { const i0 = Math.floor(sc / step) - 2; for (let i = i0; i < i0 + PW / step + 4; i++) disc(g, R(i * step - sc), R(y + H(i + seed) * amp), R(step * .75 + H(i * 3 + seed) * step * .4), col); void P; }
function smoke(g, t, x, y, n = 4) { for (let i = 0; i < n; i++) { const p = (t * .35 + i / n) % 1; disc(g, R(x + Math.sin(t + i * 2) * 3 + p * 10), R(y - p * 30), R(2 + p * 4), p > .7 ? '#E8E8F0' : '#F4F4F8'); } }
function house(g, x, base, w, h, o = {}) {
  x = R(x); const top = base - h, cx = x + R(w / 2), wall = o.wall || '#F4EEE4', roof = o.roof || '#D8544A';
  if (o.chimney) { rect(g, x + w - 14, top - 18, 7, 12, INK); rect(g, x + w - 13, top - 17, 5, 11, '#9A6A5A'); if (o.smoke != null) smoke(g, o.smoke, x + w - 11, top - 20); }
  for (let j = 0; j <= 13; j++) { const hw = R((w / 2 + 4) * j / 13); rect(g, cx - hw - 1, top - 14 + j, hw * 2 + 2, 1, INK); rect(g, cx - hw, top - 14 + j, hw * 2, 1, j % 4 === 3 ? mixHex(roof, '#000000', .2) : roof); }
  rect(g, x - 1, top - 1, w + 2, h + 1, INK); rect(g, x, top, w, h, wall);
  const lit = o.lit || 0;
  for (let wy = top + 6; wy < base - 16; wy += 14) for (let wx = x + 5; wx < x + w - 10; wx += 13) {
    const on = H(wx * 7 + wy * 3 + (o.seed || 0)) < lit;
    rect(g, wx - 1, wy - 1, 9, 9, INK); rect(g, wx, wy, 7, 7, on ? '#FFE08A' : o.night ? '#2A2E4A' : '#9ACDEA'); if (!on && !o.night) rect(g, wx, wy, 3, 2, '#E0F4FF');
    if (on) halo(g, wx + 3, wy + 3, 8, '#FFE08A', .6);
  }
  rect(g, cx - 5, base - 14, 10, 14, INK); rect(g, cx - 4, base - 13, 8, 13, '#8A5A3A'); rect(g, cx + 2, base - 7, 1, 1, '#F2C14E');
  if (o.flowers) for (let i = 0; i < 3; i++) { rect(g, x + 3 + i * 4, base - 3, 3, 3, '#B0603A'); rect(g, x + 3 + i * 4, base - 6, 3, 3, ['#FF7AA0', '#FFE060', '#FFFFFF'][i]); }
}
function houseRow(g, t, P, sc, base, o = {}) {
  const st = 64, i0 = Math.floor(sc / st) - 1;
  for (let i = i0; i < i0 + PW / st + 3; i++) {
    const w = 44 + R(H(i * 5) * 14), h = 32 + R(H(i * 7) * 30), x = i * st - sc + R(H(i) * 8);
    house(g, x, base, w, h, { wall: WALLS[(i % 6 + 6) % 6], roof: ROOFS[(i * 7 % 6 + 6) % 6], lit: P.lit, night: P.lit > .5, seed: i, chimney: H(i + 3) > .45, smoke: o.smoke ? t + i : null, flowers: true });
  }
}
function town(g, t, tod, sc = 0, o = {}) {
  const P = typeof tod === 'string' ? TOD[tod] : tod;
  grad(g, P.sky, 0, o.horizon ?? 190);
  if (o.stars) stars(g, t, o.stars, 120, 5);
  if (o.sun) sun(g, o.sun[0], o.sun[1], o.sun[2] || 16, o.sunCol, o.sunRim);
  if (o.moon) moon(g, o.moon[0], o.moon[1], 10);
  if (o.clouds) for (let i = 0; i < o.clouds; i++) cloud(g, R(((t * (4 + i) + i * 150 - sc * .1) % 640 + 640) % 640) - 90, 22 + i * 14, 1 + (i % 2) * .5, o.cloudCol || '#FFFFFF', o.cloudSh || '#D8E4F2');
  hills(g, P, sc * .15, 168, P.far, 14, 3, 70);
  hills(g, P, sc * .3, 184, P.mid, 12, 9, 50);
  if (o.river) { rect(g, 0, 186, PW, 12, P.sea); for (let i = 0; i < 18; i++) if (Math.sin(t * 2 + i) > 0) rect(g, R(((H(i) * PW + t * 8 - sc * .4) % PW + PW) % PW), 188 + (i % 4) * 2, 6, 1, P.seaHi); }
  houseRow(g, t, P, sc * .7, o.base ?? 214, { smoke: o.smoke });
  rect(g, 0, o.base ?? 214, PW, PH - (o.base ?? 214), P.street); rect(g, 0, o.base ?? 214, PW, 2, P.curb); for (let x = -24; x < PW + 24; x += 24) rect(g, R(x - (sc % 24)), (o.base ?? 214) + 26, 12, 1, P.curb);
}
function flowerPot(g, x, y, bloom, ci = 0) {
  x = R(x); y = R(y);
  rect(g, x - 5, y - 6, 11, 7, INK); rect(g, x - 4, y - 5, 9, 6, '#C8683A'); rect(g, x - 4, y - 5, 9, 1, '#E08850');
  rect(g, x, y - 12, 1, 6, '#3E8A3A'); rect(g, x - 3, y - 10, 3, 1, '#5AA04E'); rect(g, x + 1, y - 9, 3, 1, '#5AA04E');
  const c = ['#FF7AA0', '#FFE060', '#FFFFFF', '#E8546A', '#B58AE0'][ci % 5], r = R(1 + bloom * 3);
  if (bloom > 0) { disc(g, x, y - 14, r + 1, INK); disc(g, x, y - 14, r, c); rect(g, x, y - 14, 1, 1, '#FFD040'); }
  else rect(g, x - 1, y - 14, 3, 2, '#5AA04E');
}
// an orange tabby, in three poses
function cat(g, x, y, k, pose, T, flip = false) {
  x = R(x); y = R(y); const f = flip ? -1 : 1, O = '#E8A050', D = '#B86A30';
  const D2 = (dx, dy, r, c) => disc(g, x + f * dx * k, y + dy * k, R(r * k), c);
  if (pose === 'sleep') {
    D2(0, -3, 4.6, INK); D2(3.5, -3, 3, INK); D2(0, -3, 4, O); D2(3.5, -3, 2.5, O); rect(g, x + f * 2 * k, y - 5 * k, 3 * k, 1, D);
    rect(g, x + f * (flip ? -6 : 2) * k, y - 3 * k, 2 * k, 1, INK); rect(g, x - 4 * k, y - 1, 8 * k, 1, D);
    if (Math.floor(T * 1.5) % 2) ptext(g, 'z', x + f * 8 * k, y - 8 * k, { col: '#FFFFFF', outline: INK });
    return;
  }
  const tail = R(Math.sin(T * 3) * 2);
  if (pose === 'walk') { rect(g, x - 6 * k - 1, y - 7 * k - 1, 12 * k + 2, 5 * k + 2, INK); rect(g, x - 6 * k, y - 7 * k, 12 * k, 5 * k, O); const ph = Math.floor(T * 6) % 2; for (const lx of [-5, -3, 2, 4]) rect(g, x + f * lx * k, y - 2 * k - (ph && lx % 2 ? 1 : 0), k, 2 * k, D); D2(6, -8, 3.4, INK); D2(6, -8, 3, O); line(g, x - f * 6 * k, y - 6 * k, x - f * 9 * k, y - 10 * k + tail, INK); }
  else { D2(0, -4, 4.4, INK); D2(0, -4, 4, O); D2(1, -9, 3.4, INK); D2(1, -9, 3, O); line(g, x - f * 3 * k, y - 1, x - f * 7 * k, y - 4 * k + tail, INK); rect(g, x - 2 * k, y - 2 * k, 2 * k, 2 * k, D); }
  const hx = pose === 'walk' ? 6 : 1, hy = pose === 'walk' ? -8 : -9;
  for (const ex of [-1.2, 1.2]) { rect(g, x + f * (hx + ex * 1.6) * k - 1, y + (hy - 4.2) * k, 3, 3, INK); rect(g, x + f * (hx + ex * 1.6) * k, y + (hy - 3.5) * k, 1, 1, O); }
  rect(g, x + f * (hx - 1.2) * k, y + hy * k, 1, 1, INK); rect(g, x + f * (hx + 1.2) * k, y + hy * k, 1, 1, INK);
}
function windChime(g, x, y, T, ring) {
  g.save(); g.translate(x, y); g.scale(2, 2); x = 0; y = 0; line(g, x, y, x, y + 6, INK); rect(g, x - 6, y + 6, 13, 2, '#C89A60'); for (let i = 0; i < 4; i++) { const sw = R(Math.sin(T * 8 + i) * ring * 2); rect(g, x - 5 + i * 3 + sw, y + 8, 1, 6 + i * 2, '#B8C8D8'); } rect(g, x - 1, y + 16, 3, 4, '#E8546A'); if (ring > .2) for (let i = 0; i < 2; i++) { const p = (T * 1.5 + i * .5) % 1; note(g, R(x + 10 + p * 20), R(y + 6 - p * 14), '#FFFFFF'); }
  g.restore(); }
function cup(g, x, y, T) { rect(g, x - 1, y - 8, 10, 9, INK); rect(g, x, y - 7, 8, 7, '#FFFFFF'); rect(g, x + 1, y - 7, 6, 2, '#C8884E'); rect(g, x + 8, y - 6, 2, 1, INK); rect(g, x + 9, y - 6, 1, 4, INK); rect(g, x + 8, y - 3, 2, 1, INK); for (let i = 0; i < 3; i++) { const p = (T * .6 + i / 3) % 1; rect(g, R(x + 2 + i * 2 + Math.sin(T * 3 + i) * 1.5), R(y - 10 - p * 12), 1, 2, '#FFFFFF'); } }
function sunbeam(g, x0, x1, y0, y1, a) { for (let y = y0; y < y1; y++) { const f = (y - y0) / (y1 - y0), xa = lerp(x0, x0 + 80, f), xb = lerp(x1, x1 + 80, f); checker(g, xa, y, xb - xa, 1, '#FFF0B8', a); } }
function motes(g, t, x, y, w, h, n = 16) { for (let i = 0; i < n; i++) { const px = R(x + ((H(i) * w + t * 4 * (H(i + 2) - .3)) % w + w) % w), py = R(y + ((H(i + 5) * h + Math.sin(t + i) * 6 - t * 3) % h + h) % h); if (Math.sin(t * 2 + i) > 0) rect(g, px, py, 1, 1, '#FFF8D8'); } }
function pigeon(g, x, y, T, i) { const peck = Math.floor(T * 2 + i) % 3 === 0; rect(g, x - 3, y - 4, 6, 4, INK); rect(g, x - 2, y - 3, 4, 3, '#A8A8B8'); rect(g, x + 2, y - (peck ? 3 : 6), 3, 3, INK); rect(g, x + 3, y - (peck ? 2 : 5), 1, 1, '#E0E0E8'); rect(g, x - 1, y, 1, 1, '#E8804A'); rect(g, x + 1, y, 1, 1, '#E8804A'); }
function fountain(g, x, y, T) { rect(g, x - 30, y - 10, 61, 10, INK); rect(g, x - 29, y - 9, 59, 8, '#C8C0B8'); rect(g, x - 26, y - 9, 53, 3, '#7AB0E0'); rect(g, x - 3, y - 30, 7, 20, INK); rect(g, x - 2, y - 29, 5, 19, '#D8D0C8'); for (let i = 0; i < 10; i++) { const p = (T * 1.2 + i / 10) % 1, sd = i % 2 ? 1 : -1; rect(g, R(x + sd * p * 22), R(y - 32 - Math.sin(p * Math.PI) * 18 + p * 20), 1, 2, '#BFE6FF'); } }
function bike(g, x, y, T, s = 1) {
  const sp = T * 18, X = v => x + R(v * s), Y = v => y - R(v * s), fr = (a, b, c, d) => { line(g, X(a), Y(b), X(c), Y(d), '#3AA08A'); line(g, X(a), Y(b) + 1, X(c), Y(d) + 1, '#3AA08A'); };
  for (const wx of [-19, 19]) { const r = R(8 * s); ring(g, X(wx), Y(8), r, INK); ring(g, X(wx), Y(8), r - 1, '#3A3A48'); ring(g, X(wx), Y(8), r - 2, INK); for (let a = 0; a < 3; a++) { const an = sp + a * Math.PI / 3, q = r - 3; line(g, X(wx) - R(Math.cos(an) * q), Y(8) - R(Math.sin(an) * q), X(wx) + R(Math.cos(an) * q), Y(8) + R(Math.sin(an) * q), '#9A9AB0'); } }
  fr(-19, 8, -2, 8); fr(-2, 8, 8, 20); fr(-19, 8, -6, 20); fr(-6, 20, 8, 20); fr(8, 20, 19, 8); fr(12, 26, 8, 20); rect(g, X(10), Y(27), R(6 * s), 2, INK); rect(g, X(-9), Y(22), R(7 * s), 2, INK);
  rect(g, X(12), Y(24), R(9 * s), R(6 * s), INK); rect(g, X(12) + 1, Y(24) + 1, R(9 * s) - 2, R(6 * s) - 2, '#C8884E'); rect(g, X(13), Y(28), 2, 3, '#FF7AA0'); rect(g, X(16), Y(29), 2, 4, '#FFE060');
}
function lanterns(g, x0, x1, y, T, n = 8, sway = 1) { for (let i = 0; i <= 20; i++) { const f = i / 20; rect(g, R(lerp(x0, x1, f)), R(y + Math.sin(f * Math.PI) * 14), 1, 1, INK); } for (let i = 0; i < n; i++) { const f = (i + .5) / n, lx = R(lerp(x0, x1, f) + Math.sin(T * 1.5 + i) * sway), ly = R(y + Math.sin(f * Math.PI) * 14 + 2); halo(g, lx, ly + 4, 10, '#FFD880', .8); rect(g, lx, ly, 1, 2, INK); rect(g, lx - 3, ly + 2, 7, 7, INK); rect(g, lx - 2, ly + 3, 5, 5, ['#FF9A50', '#FFD860', '#FF7AA0'][i % 3]); } }
function guitar(g, x, y) { x = R(x); y = R(y); rect(g, x - 26, y - 2, 22, 3, INK); rect(g, x - 25, y - 1, 20, 1, '#6A4228'); rect(g, x - 30, y - 3, 5, 5, INK); disc(g, x, y, 8, INK); disc(g, x + 8, y - 1, 7, INK); disc(g, x, y, 7, '#D8944A'); disc(g, x + 8, y - 1, 6, '#D8944A'); disc(g, x + 3, y, 2, '#3A2418'); }
function glass(g, x, y, col = '#F2C14E') { rect(g, x - 3, y - 9, 7, 10, INK); rect(g, x - 2, y - 8, 5, 8, '#E8F4FF'); rect(g, x - 2, y - 5, 5, 5, col); rect(g, x - 2, y - 8, 1, 3, '#FFFFFF'); }
function phoneS(g, x, y, ring, T) { const sh = ring ? R(Math.sin(T * 40)) : 0; rect(g, x - 5 + sh, y - 9, 11, 18, INK); rect(g, x - 4 + sh, y - 8, 9, 15, ring ? '#BFE6FF' : '#3A3A4A'); if (ring) { rect(g, x - 2 + sh, y - 5, 5, 5, '#F08A4A'); for (const sd of [-1, 1]) for (let i = 0; i < 3; i++) rect(g, x + sd * (9 + i * 3) + sh, y - 4 + i, 1, 3, '#FFFFFF'); } }
function speech(g, x, y, w, h, tx, ty, icon, T) { bubble(g, x, y, w, h, tx, ty); icon(g, x + w / 2, y + h / 2, T); }
const ICONS = [
  (g, x, y) => { disc(g, x, y, 4, '#FFC94A'); for (let a = 0; a < 8; a++) rect(g, x + R(Math.cos(a * .785) * 6), y + R(Math.sin(a * .785) * 6), 1, 1, '#FFC94A'); },
  (g, x, y, T) => cat(g, x, y + 4, 1, 'sit', T),
  (g, x, y) => { rect(g, x - 5, y - 2, 9, 5, '#5A9AD8'); rect(g, x + 4, y - 4, 1, 9, '#5A9AD8'); rect(g, x - 2, y - 1, 1, 1, INK); },
  (g, x, y) => note(g, x, y + 2, '#E8546A'),
  (g, x, y) => heart(g, x, y, 1, '#FF5C8A', null),
  (g, x, y) => sparkle(g, x, y, 4, '#F2C14E'),
  (g, x, y) => { rect(g, x - 5, y + 1, 11, 4, '#C8884E'); rect(g, x - 4, y - 3, 9, 4, '#F4E0B0'); },
];

// ---------------------------------------------------------------- shots
const SCENES = {
  dawn(g, t, s) {
    const u = local(t, s), p = qz(seg(u, 0, 7.5), 10);
    const P = { ...TOD.night, sky: skyMix(TOD.night.sky, TOD.dawn.sky, p * 1.0, 10), far: mixHex(TOD.night.far, TOD.morning.far, p), mid: mixHex(TOD.night.mid, TOD.morning.mid, p), sea: mixHex(TOD.night.sea, TOD.dawn.sea, p), seaHi: '#FFD8B8', lit: .7 - p * .5 };
    grad(g, P.sky, 0, 190);
    stars(g, t, R(120 * (1 - p)), 150, 3);
    if (p < .5) moon(g, 90, R(40 + p * 60), 8);
    sun(g, 360, R(lerp(206, 150, eio(seg(u, 2.5, 8)))), 14, '#FFE6A0', '#FFC27A');
    for (let i = 0; i < 3; i++) cloud(g, R(((t * 5 + i * 170) % 640) - 90), 34 + i * 16, 1.2, mixHex('#5A5A8A', '#FFE4D0', p), mixHex('#3A3A6A', '#F4B8A8', p));
    hills(g, P, u * 2, 136, P.far, 16, 3, 80);
    // the river, the bridge and a little train crossing it
    rect(g, 0, 150, PW, 16, P.sea); for (let i = 0; i < 14; i++) if (Math.sin(t * 2 + i) > 0) rect(g, R((H(i) * PW + t * 6) % PW), 152 + (i % 5) * 3, 5, 1, P.seaHi);
    rect(g, 40, 144, 280, 3, '#5A4A5A'); for (let x = 50; x < 320; x += 24) rect(g, x, 147, 3, 10, '#5A4A5A');
    const tx = R(lerp(-120, 560, seg(u, 1, 7.8)));
    for (let c = 0; c < 4; c++) { const cx2 = tx - c * 26; rect(g, cx2 - 1, 132, 24, 12, INK); rect(g, cx2, 133, 22, 10, c ? '#3E82C8' : '#D8544A'); for (let w = 0; w < 3; w++) rect(g, cx2 + 3 + w * 6, 135, 4, 3, P.lit > .3 ? '#FFE08A' : '#BFE6FF'); }
    if (u > 1) for (let i = 0; i < 4; i++) { const p2 = ((u - 1) * .5 + i / 4) % 1; disc(g, R(tx + 18 - p2 * 30), R(128 - p2 * 16), R(2 + p2 * 3), '#E8E8F0'); }
    hills(g, P, u * 4, 206, P.mid, 10, 9, 56);
    // rooftops: windows light up one by one, the chimneys start to smoke
    const st = 52;
    for (let i = 0; i < 11; i++) { const w = 40 + R(H(i * 5) * 12), h = 30 + R(H(i * 7) * 28), x = i * st - 20 + R(H(i) * 8) - R(u * 6); house(g, x, 232, w, h, { wall: mixHex(WALLS[i % 6], '#2A2E4A', .55 * (1 - p)), roof: mixHex(ROOFS[i * 7 % 6], '#1A1E30', .5 * (1 - p)), lit: H(i + 11) < seg(u, 1 + i * .4, 3 + i * .4) ? 1 : 0, night: p < .6, seed: i, chimney: H(i + 3) > .4, smoke: u > 4 ? t + i : null }); }
    rect(g, 0, 232, PW, 38, mixHex('#2A3048', '#C8B898', p)); rect(g, 0, 232, PW, 2, mixHex('#4E5274', '#E8D8B8', p));
    cat(g, R(lerp(150, 230, seg(u, 3, 6.5))), 254, 2, u > 3 && u < 6.5 ? 'walk' : 'sit', t);
    for (let i = 0; i < 5; i++) if (u > 3.5) bird(g, R(((u - 3.5) * 26 + i * 18) % 520) - 20, 70 + i * 6 + R(Math.sin(t * 2 + i) * 3), t + i, mixHex(INK, '#5A4A5A', p));
    const chars = [...'平凡的一天'], shown = Math.ceil(seg(u, 1.6, 4.2) * 5);
    if (shown > 0) ptext(g, chars.slice(0, shown).join(''), 240, 80, { size: 48, col: '#FFF6E0', outline: INK, shadow: '#C86A5A' });
    if (u > 4.6) ptext(g, '毛不易 · 像素 MV', 240, 104, { col: '#FFF6E0', outline: INK });
    blackout(g, 1 - seg(u, 0, 1.6));
  },
  bedroom(g, t, s) {
    const u = local(t, s), p = seg(u, 0, s.t1 - s.t0);
    bedroomBg(g, t, p * .8);
    bed(g, true, t, 'closed');
    cat(g, 120, 186, 2, 'sleep', t);
    // the clock creeps towards half past seven
    const m = lerp(22, 29.6, p), hA = (7 + m / 60) / 12 * Math.PI * 2, mA = m / 60 * Math.PI * 2;
    clockFace(g, 404, 120, 18, hA, mA, Math.floor(u) * Math.PI / 30);
    rect(g, 384, 142, 41, 30, INK); rect(g, 385, 143, 39, 28, '#C8884E');
    ptext(g, `7:${String(Math.floor(m)).padStart(2, '0')}`, 404, 162, { col: '#FFE9A8', outline: INK });
  },
  wake(g, t, s) {
    const u = local(t, s);
    bedroomBg(g, t, .85);
    const up = u > 1.2;
    bed(g, !up, t, 'closed');
    if (up) person(g, 'me', 200, 214, 3, { sit: true, aL: u < 4.5 ? 'up' : 'down', aR: u < 4.5 ? 'up' : 'down', eyes: u < 3 ? 'closed' : 'happy', mouth: u < 3 ? 'open' : 'smile' }, t);
    clockFace(g, 404, 120, 18, (7.5 / 12) * Math.PI * 2, Math.PI, Math.floor(u) * Math.PI / 30);
    rect(g, 384, 142, 41, 30, INK); rect(g, 385, 143, 39, 28, '#C8884E'); ptext(g, '7:30', 404, 162, { col: '#FFE9A8', outline: INK });
    if (u > 1.2 && u < 2.4) for (let i = 0; i < 6; i++) sparkle(g, 404 + R(Math.cos(i) * 26), 120 + R(Math.sin(i) * 26), 1, '#FFFFFF');
    cat(g, 120, 186, 2, u < 2.6 ? 'sleep' : 'sit', t);
    if (u > 2.6 && u < 4) ptext(g, '喵', 140, 150, { col: '#FFFFFF', outline: INK });
  },
  chime(g, t, s) {
    const u = local(t, s), open = eio(seg(u, 1.5, 2.8));
    rect(g, 0, 0, PW, PH, '#F2E4CC'); for (let x = 0; x < PW; x += 16) rect(g, x, 0, 1, 270, '#EAD8BC');
    const wx = 120, wy = 30, ww = 240, wh = 170;
    g.save(); g.beginPath(); g.rect(wx, wy, ww, wh); g.clip();
    grad(g, TOD.morning.sky, wy, wy + wh);
    for (let i = 0; i < 5; i++) cloud(g, R(((t * 8 + i * 110) % 560) - 80), wy + 20 + (i % 3) * 30, .9 + (i % 2) * .5);
    hills(g, TOD.morning, 0, wy + wh - 20, '#9CC48A', 8, 4, 40); for (let i = 0; i < 6; i++) house(g, wx + i * 44 - 10, wy + wh + 6, 34, 24, { wall: WALLS[i], roof: ROOFS[i], seed: i });
    g.restore();
    // the two window panes swing open
    const pw = R(ww / 2 * (1 - open * .8));
    for (const [px, d] of [[wx, 1], [wx + ww - pw, -1]]) { rect(g, px, wy, pw, wh, '#A8D0E8'); checker(g, px, wy, pw, wh, '#FFFFFF', .2); rect(g, px, wy, pw, 3, INK); rect(g, px, wy + wh - 3, pw, 3, INK); rect(g, d > 0 ? px + pw - 3 : px, wy, 3, wh, INK); void d; }
    rect(g, wx - 6, wy - 6, ww + 12, 6, '#FFFFFF'); rect(g, wx - 6, wy + wh, ww + 12, 8, '#FFFFFF'); rect(g, wx - 6, wy, 6, wh, '#FFFFFF'); rect(g, wx + ww, wy, 6, wh, '#FFFFFF'); rect(g, wx - 7, wy + wh + 8, ww + 14, 1, INK);
    windChime(g, 240, wy, t, u < 1.6 ? .9 : .5 + .5 * kickPulse(t, 3));
    person(g, 'me', 240, 300, 4, { aL: 'up', aR: open > .5 ? 'up' : 'down', eyes: 'happy', mouth: 'smile', back: false }, t);
    flowerPot(g, 160, wy + wh + 8, 1, 0); flowerPot(g, 320, wy + wh + 8, 1, 1);
  },
  laundry(g, t, s) {
    const u = local(t, s), hug = u > 2.6;
    grad(g, TOD.day.sky, 0, 200); sun(g, 410, 40, 16);
    for (let i = 0; i < 4; i++) cloud(g, R(((t * 6 + i * 150) % 640) - 90), 26 + i * 12, 1 + (i % 2) * .4);
    hills(g, TOD.day, 0, 170, TOD.day.far, 10, 5, 70); houseRow(g, t, TOD.day, 40, 196, {});
    rect(g, 0, 196, PW, 74, '#C8A888'); rect(g, 0, 196, PW, 3, '#A8886A'); for (let x = 0; x < PW; x += 30) rect(g, x, 199, 1, 71, '#B89878');
    // the washing line
    line(g, 30, 110, 450, 116, INK); rect(g, 28, 106, 3, 92, '#8A6A4A'); rect(g, 450, 112, 3, 86, '#8A6A4A');
    const clothes = [[70, '#FFFFFF', 's'], [130, '#7EC0E8', 't'], [200, '#F2C14E', 's'], [330, '#E8546A', 't'], [400, '#FFFFFF', 's']];
    clothes.forEach(([cx, col, kind], i) => { const sw = R(Math.sin(t * 2.4 + i) * 3), y = 111; rect(g, cx - 12 + sw - 1, y - 1, 26, kind === 's' ? 28 : 22, INK); rect(g, cx - 12 + sw, y, 24, kind === 's' ? 26 : 20, col); if (kind === 's') { rect(g, cx - 18 + sw, y, 6, 10, col); rect(g, cx + 12 + sw, y, 6, 10, col); } rect(g, cx - 1, y - 3, 2, 4, '#E8804A'); });
    const P = person(g, 'me', 270, 250, 3, { aL: hug ? 'chest' : 'up', aR: hug ? 'chest' : 'up', eyes: hug ? 'closed' : 'happy', mouth: 'smile', blush: hug }, t);
    if (P && hug) { rect(g, P.R[0] - 14, P.R[1] - 8, 28, 22, INK); rect(g, P.R[0] - 13, P.R[1] - 7, 26, 20, '#FFFFFF'); for (let i = 0; i < 5; i++) { const p = (u * .6 + i / 5) % 1; sparkle(g, R(P.R[0] - 30 + i * 15), R(P.R[1] - 30 - p * 40), 1 + (i % 2), '#FFF4C0'); } heart(g, P.R[0] + 30, P.R[1] - 50 + R(Math.sin(t * 3) * 2), 1, '#FF7AA0'); }
  },
  soft(g, t, s) {
    const u = local(t, s);
    bedroomBg(g, t, .9, true);
    // a cushion by the window, the cat asleep on it, a cup of tea
    rect(g, 70, 196, 90, 16, INK); rect(g, 71, 197, 88, 14, '#E8A0B0'); rect(g, 71, 197, 88, 3, '#F8C0CC');
    cat(g, 112, 198, 2, 'sleep', t);
    rect(g, 260, 186, 120, 6, '#B88A5A'); rect(g, 266, 192, 4, 30, '#8A6A4A'); rect(g, 370, 192, 4, 30, '#8A6A4A');
    cup(g, 300, 186, t);
    rect(g, 330, 178, 26, 8, INK); rect(g, 331, 179, 24, 6, '#7AA8D8'); rect(g, 331, 179, 24, 1, '#FFFFFF');
    person(g, 'me', 220, 226, 3, { sit: true, eyes: 'closed', mouth: 'smile', aR: 'hold', aL: 'down', look: 1 }, t);
    motes(g, t, 60, 40, 220, 160, 26);
    for (let i = 0; i < 3; i++) { const sw = R(Math.sin(t * .8 + i) * 2); rect(g, 52 + sw, 20 + i, 1, 150, '#F8D8E0'); }
  },
  flowers(g, t, s) {
    const u = local(t, s), sc = u * 34;
    town(g, t, 'morning', sc, { sun: [400, 40, 16], clouds: 4 });
    // at every corner a pot of flowers, opening as he passes
    for (let i = -1; i < 9; i++) { const x = R(i * 60 - sc % 60 + 30), wx = Math.floor(sc / 60) + i, d = 260 - x, bloom = clamp(1 - (d - 10) / 60); flowerPot(g, x, 222, d < 70 ? bloom : x < 260 ? 1 : 0, (wx % 5 + 5) % 5); flowerPot(g, x + 18, 224, d < 50 ? bloom : x < 240 ? 1 : 0, (wx + 2) % 5 + 0); }
    for (let i = 0; i < 6; i++) { const p = ((u * .5 + H(i)) % 1); rect(g, R(240 + H(i + 2) * 200 - p * 120), R(200 - p * 80), 2, 1, ['#FF7AA0', '#FFFFFF', '#FFE060'][i % 3]); }
    person(g, 'me', 260, 252, 3, { walk: walkPh(t), eyes: 'happy', mouth: 'smile', look: 1 }, t);
  },
  lovesong(g, t, s) {
    const u = local(t, s);
    town(g, t, 'morning', 120, { clouds: 3, sun: [420, 36, 14] });
    // the record shop
    const sx = 150, sw2 = 200;
    rect(g, sx - 1, 90, sw2 + 2, 125, INK); rect(g, sx, 91, sw2, 124, '#F4E8D8');
    for (let i = 0; i < 10; i++) rect(g, sx + i * 20, 84, 20, 14, i % 2 ? '#FFFFFF' : '#3EA08A'); rect(g, sx - 2, 97, sw2 + 4, 2, INK);
    ptext(g, '恋曲', sx + sw2 / 2, 80, { col: '#FFE9A8', outline: INK });
    rect(g, sx + 12, 108, 110, 80, INK); rect(g, sx + 13, 109, 108, 78, '#FFE6B0'); halo(g, sx + 66, 148, 50, '#FFF0C0', .7);
    // a gramophone in the window and a couple dancing inside
    rect(g, sx + 30, 168, 20, 10, '#8A5A3A'); for (let j = 0; j < 10; j++) rect(g, sx + 40 + j, 166 - j * 1.5, 2 + j, 2, '#E8B040');
    person(g, 'girl', sx + 78, 188, 1, { eyes: 'closed', mouth: 'smile', aR: 'out', dy: R(Math.sin(t * 4)) }, t);
    person(g, 'friend', sx + 96, 188, 1, { eyes: 'closed', mouth: 'smile', aL: 'out', flip: true, dy: R(Math.sin(t * 4 + 1)) }, t);
    rect(g, sx + 140, 120, 40, 95, INK); rect(g, sx + 141, 121, 38, 94, '#8A5A3A'); rect(g, sx + 170, 166, 3, 3, '#F2C14E');
    for (let i = 0; i < 6; i++) { const p = (u * .4 + i / 6) % 1, x = R(sx + 50 + p * 160 + Math.sin(t * 2 + i) * 10), y = R(150 - p * 110); if (i % 2) heart(g, x, y, 1, '#FF7AA0', null); else note(g, x, y, '#E8546A'); }
    person(g, 'me', 400, 252, 3, { eyes: 'happy', mouth: 'smile', look: -1, dy: beatPhase(t) < .5 ? -2 : 0 }, t);
  },
  nearby(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0;
    // the town seen from above, like a map
    rect(g, 0, 0, PW, PH, '#9ACD6A'); for (let i = 0; i < 200; i++) rect(g, R(H(i) * PW), R(H(i + 4) * PH), 2, 1, i % 2 ? '#8ABE5A' : '#AAD87A');
    rect(g, 0, 150, PW, 22, '#5AA0D8'); for (let i = 0; i < 20; i++) if (Math.sin(t * 2 + i) > 0) rect(g, R(H(i) * PW), 154 + (i % 3) * 5, 6, 1, '#BFE6FF');
    rect(g, 230, 146, 30, 30, '#C8A878');
    for (const [x, y, w] of [[0, 96, PW], [236, 0, 18], [0, 210, PW], [120, 96, 14], [360, 96, 14]]) rect(g, x, y, w || 14, w === PW ? 14 : PH, '#E8D8B8');
    const blocks = [[30, 40], [100, 30], [300, 40], [380, 30], [40, 120], [150, 120], [300, 120], [390, 120], [40, 228], [150, 228], [300, 228], [390, 228]];
    blocks.forEach(([x, y], i) => { rect(g, x - 1, y - 1, 52, 32, INK); rect(g, x, y, 50, 30, ROOFS[i % 6]); rect(g, x, y, 50, 4, mixHex(ROOFS[i % 6], '#FFFFFF', .3)); });
    for (let i = 0; i < 14; i++) { const x = R(H(i * 3) * PW), y = R(H(i * 5) * PH); disc(g, x, y, 5, INK); disc(g, x, y, 4, '#4E9A4A'); }
    // home → bakery, a short dotted walk
    const path = [[75, 72], [75, 103], [243, 103], [243, 217], [325, 217], [325, 236]];
    const L = path.slice(1).reduce((a, p, i) => a + Math.hypot(p[0] - path[i][0], p[1] - path[i][1]), 0), f = eio(seg(u, .6, d - 1.2)) * L;
    let acc = 0, pos = path[0];
    for (let i = 1; i < path.length; i++) { const [x0, y0] = path[i - 1], [x1, y1] = path[i], l = Math.hypot(x1 - x0, y1 - y0); for (let q = 0; q < Math.min(l, f - acc); q += 6) rect(g, R(x0 + (x1 - x0) * q / l), R(y0 + (y1 - y0) * q / l), 2, 2, '#E8546A'); if (f > acc) pos = [lerp(x0, x1, clamp((f - acc) / l)), lerp(y0, y1, clamp((f - acc) / l))]; acc += l; }
    house(g, 55, 74, 40, 30, { wall: '#F4EEE4', roof: '#D8544A' }); ptext(g, '家', 75, 64, { col: '#FFFFFF', outline: INK });
    house(g, 305, 238, 40, 30, { wall: '#F2E2A8', roof: '#8A5A3A' }); ptext(g, '面包', 325, 228, { col: '#FFFFFF', outline: INK });
    person(g, 'me', pos[0], pos[1] + 4, 1, { walk: walkPh(t) * 2, eyes: 'happy' }, t);
    if (f >= L - 1) for (let i = 0; i < 6; i++) sparkle(g, 325 + R(Math.cos(i) * 24), 216 + R(Math.sin(i) * 14), 1 + (i % 2), '#FFFFFF');
  },
  kindness(g, t, s) {
    const u = local(t, s);
    town(g, t, 'day', 60, { clouds: 3, sun: [60, 36, 14] });
    // neighbours: everyone has a smile for someone
    const pairs = [['grandpa', 70, 'wave'], ['kid', 116, 'up'], ['aunt', 330, 'wave'], ['girl', 400, 'down'], ['friend', 450, 'wave']];
    pairs.forEach(([w, x, arm], i) => { const P = person(g, w, x, 246 - (i % 2) * 8, 2, { eyes: 'happy', mouth: 'smile', aR: arm, look: x < 240 ? 1 : -1, walk: i === 3 ? walkPh(t) : null }, t); if (P && Math.floor(u * 1.4 + i) % 3 === 0) heart(g, R(P.face[0]), R(P.face[1] - 24 - ((u * 10 + i * 4) % 10)), 1, '#FF7AA0', null); });
    // he helps the aunt with her heavy bag
    rect(g, 360, 226, 14, 16, INK); rect(g, 361, 227, 12, 14, '#F2E2A8'); rect(g, 362, 222, 3, 5, '#5AA04E'); rect(g, 368, 223, 3, 4, '#E8546A');
    person(g, 'me', 240, 252, 3, { eyes: 'happy', mouth: 'smile', aL: 'wave', look: -1 }, t);
    for (let i = 0; i < 5; i++) pigeon(g, 160 + i * 14, 262, t, i);
  },
  ordinary(g, t, s) {
    const u = local(t, s), v = s.v, tod = ['dusk', 'night', 'morning'][v];
    town(g, t, tod, 0, { sun: v === 0 ? [380, 120, 18] : v === 2 ? [80, 60, 18] : null, moon: v === 1 ? [400, 40] : null, stars: v === 1 ? 80 : 0, clouds: v === 1 ? 0 : 3, cloudCol: v === 0 ? '#FFE4D0' : '#FFFFFF', cloudSh: v === 0 ? '#F4B8A8' : '#D8E4F2', smoke: v === 2 });
    // the square: a clock tower, the fountain and the pigeons
    rect(g, 220, 70, 40, 144, INK); rect(g, 221, 71, 38, 143, '#E8D0B0'); for (let j = 0; j < 12; j++) rect(g, 216 + j * 2, 70 - j, 48 - j * 4, 1, '#B8605A');
    clockFace(g, 240, 100, 13, ((u / 30 + (v === 1 ? 9 : v === 2 ? 7.5 : 17.5)) / 12) * Math.PI * 2, (u / 2.5) * Math.PI * 2, null);
    if (v === 1) { lamp(g, 120, 214, 80, 1); lamp(g, 360, 214, 80, 1); }
    fountain(g, 240, 252, t);
    for (let i = 0; i < 6; i++) pigeon(g, R(90 + i * 22 + (v === 1 ? 0 : Math.sin(t + i) * 3)), 262, t, i);
    person(g, 'me', 320, 256, 3, { eyes: 'happy', mouth: 'smile', aR: v === 1 ? 'down' : 'hold', look: -1 }, t);
    person(g, v === 1 ? 'friend' : 'grandpa', 160, 256, 2, { eyes: 'happy', mouth: 'smile', walk: walkPh(t) }, t);
  },
  askyou(g, t, s) {
    const u = local(t, s), v = s.v, tod = ['dusk', 'night', 'morning'][v];
    const P = TOD[tod];
    grad(g, P.sky, 0, PH);
    if (v === 1) stars(g, t, 80, 200, 7); else for (let i = 0; i < 3; i++) cloud(g, R(((t * 5 + i * 170) % 640) - 90), 30 + i * 20, 1.3, v === 0 ? '#FFE4D0' : '#FFFFFF', v === 0 ? '#F4B8A8' : '#D8E4F2');
    houseRow(g, t, P, 0, 270, {});
    person(g, 'me', 240, 330, 8, { eyes: 'happy', mouth: u > .5 ? 'smile' : 'open', blush: true, aR: 'wave' }, t);
    for (let i = 0; i < 5; i++) if (Math.floor(t * 4 + i) % 3) sparkle(g, R(80 + H(i) * 320), R(40 + H(i + 3) * 100), 1 + (i % 2), '#FFFFFF');
  },
  slowhome(g, t, s) {
    const u = local(t, s), v = s.v, sc = u * 18;
    const tod = ['dusk', 'night', 'dusk'][v];
    town(g, t, tod, sc, { sun: v === 1 ? null : [400, 150, 18], moon: v === 1 ? [80, 40] : null, stars: v === 1 ? 60 : 0, clouds: v === 1 ? 0 : 2, cloudCol: '#FFE4D0', cloudSh: '#F4B8A8' });
    if (v === 1) for (let i = -1; i < 4; i++) lamp(g, R(i * 160 - (sc * .7) % 160 + 60), 214, 80, 1);
    // a bus leaves with people running for it; he does not hurry
    if (v === 0) { const bx = R(lerp(300, 560, seg(u, .5, 4))); rect(g, bx - 1, 168, 112, 44, INK); rect(g, bx, 169, 110, 42, '#F2C14E'); for (let i = 0; i < 5; i++) rect(g, bx + 6 + i * 20, 174, 14, 12, '#9ED0F0'); for (const wx of [20, 88]) { disc(g, bx + wx, 212, 6, INK); disc(g, bx + wx, 212, 3, '#8A8A9A'); } for (let i = 0; i < 2; i++) person(g, i ? 'girl' : 'grandpa', R(lerp(200, 520, seg(u, .3 + i * .3, 4.5))), 244 + i * 10, 2, { walk: t * 3 + i, eyes: 'wide', mouth: 'open', aR: 'up', look: 1 }, t); }
    else { person(g, 'friend', R(lerp(240, 120, seg(u, 0, 3))), 244, 2, { aR: 'wave', eyes: 'happy', mouth: 'smile', look: 1 }, t); }
    person(g, 'me', 260, 256, 3, { walk: walkPh(t) * .6, aL: 'behind', aR: 'behind', eyes: 'happy', mouth: 'smile', look: 1 }, t);
    // the snail keeps him company
    const nx = R(300 + u * 4); rect(g, nx, 254, 10, 3, '#C8B898'); disc(g, nx + 3, 251, 4, INK); disc(g, nx + 3, 251, 3, '#C8884E'); rect(g, nx + 9, 248, 1, 5, INK); rect(g, nx + 11, 248, 1, 5, INK);
  },
  idle(g, t, s) {
    const u = local(t, s), v = s.v;
    if (v === 1) { grad(g, TOD.night.sky, 0, PH); stars(g, t, 160, 260, 13); for (const a0 of [1.4, 4.3, 7.1]) { const a = u - a0; if (a > 0 && a < .9) for (let j = 0; j < 14; j++) rect(g, R(380 - a * 280 + j * 2), R(30 + a * 70 - j * .5), 2, 1, j < 3 ? '#FFFFFF' : '#9FB0E0'); } }
    else { grad(g, v === 2 ? ['#F8C890', '#FFE0B0', '#FFF6E0'] : TOD.day.sky, 0, PH); for (let i = 0; i < 6; i++) { const cx = R(((t * 10 + i * 110) % 640) - 90); cloud(g, cx, 24 + (i % 3) * 30, 1.2 + (i % 2) * .6, v === 2 ? '#FFF0E0' : '#FFFFFF', v === 2 ? '#F8D0B0' : '#D8E4F2'); } }
    // lying in the grass with hands behind his head, watching the clouds go by
    if (v === 1) { rect(g, 0, 200, PW, 70, '#3A3A52'); rect(g, 0, 200, PW, 2, '#5A5A78'); for (let i = 0; i < 6; i++) house(g, i * 80 - 10, 210, 50, 30, { wall: '#4A4E6A', roof: '#2A2E4A', lit: .5, night: true, seed: i }); }
    else { disc(g, 240, 470, 280, v === 2 ? '#8AB060' : '#6CB050'); disc(g, 240, 474, 276, v === 2 ? '#A0C870' : '#86CB62'); for (let i = 0; i < 40; i++) { const x = R(H(i) * PW), y = R(206 + H(i + 4) * 60); rect(g, x, y, 1, 3, '#5E9E52'); if (i % 3 === 0) rect(g, x - 1, y - 2, 3, 2, ['#FFFFFF', '#FFD860', '#FF8FB0'][i % 3]); } }
    lying(g, 170, 236, v === 1 ? 'night' : 'day', t);
    if (v !== 1) { const p = (u * .25) % 1; for (let i = 0; i < 6; i++) rect(g, R(270 + p * 160 + i * 6), R(200 - p * 120 + Math.sin(t * 2 + i) * 6), 1, 1, '#FFFFFF'); }
    if (v === 0) cat(g, 390, 236, 2, 'sleep', t);
  },
  breeze(g, t, s) {
    const u = local(t, s), v = s.v, tod = ['dusk', 'night', 'morning'][v];
    const P = TOD[tod];
    grad(g, P.sky, 0, 200);
    if (v === 1) { stars(g, t, 90, 160, 17); moon(g, 380, 40, 11); } else sun(g, v === 0 ? 380 : 90, v === 0 ? 150 : 50, 18, v === 0 ? '#FFE0A0' : '#FFE27A', v === 0 ? '#FFB070' : '#FFC94A');
    hills(g, P, 0, 168, P.far, 12, 3, 70);
    rect(g, 0, 176, PW, 94, P.sea); for (let i = 0; i < 30; i++) if (Math.sin(t * 2 + i) > 0) rect(g, R((H(i) * PW + t * 6) % PW), 180 + (i % 8) * 10, 6 + (i % 3) * 3, 1, P.seaHi);
    // the bridge, and the wind in his hair
    rect(g, 0, 214, PW, 10, '#B88A6A'); rect(g, 0, 214, PW, 2, '#D8AA8A'); for (let x = 6; x < PW; x += 30) rect(g, x, 196, 3, 18, '#8A5A3A'); rect(g, 0, 196, PW, 2, '#8A5A3A');
    if (v === 1) lamp(g, 100, 214, 70, 1);
    const P2 = person(g, 'me', 260, 214, 4, { eyes: 'closed', mouth: 'smile', look: -1, aL: 'behind', aR: 'behind' }, t);
    if (P2) for (let i = 0; i < 4; i++) { const sw = R(Math.sin(t * 6 + i) * 2); rect(g, R(P2.face[0]) + 26 + i * 3, R(P2.face[1]) - 26 + sw + i, 4, 1, CAST.me.hair); }
    windLines(g, t * .5, 10, 3, v === 1 ? '#8A9AD0' : '#FFFFFF', 60, 200);
    petals(g, t * .6, 14, v === 1 ? ['#9FB0E0'] : ['#FFB0C8', '#FFFFFF'], 5, -1);
  },
  ride(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, sc = u * 120, p = seg(u, 0, d);
    const sky = skyMix(TOD.day.sky, ['#F8B880', '#FFD4A0', '#FFF0D0'], p, 6);
    grad(g, sky, 0, 180); sun(g, R(lerp(420, 380, p)), R(lerp(40, 120, p)), 18, '#FFE6A0', '#FFC27A');
    for (let i = 0; i < 4; i++) cloud(g, R(((t * 10 + i * 160 - sc * .1) % 660 + 660) % 660) - 100, 24 + i * 14, 1.2);
    hills(g, TOD.day, sc * .1, 150, mixHex('#88B4DC', '#C8A0A8', p), 14, 3, 80);
    rect(g, 0, 166, PW, 30, mixHex('#5AA0D8', '#E8A07A', p)); for (let i = 0; i < 24; i++) if (Math.sin(t * 2 + i) > 0) rect(g, R(((H(i) * PW - sc * .3) % PW + PW) % PW), 170 + (i % 5) * 5, 6, 1, '#FFF0D0');
    for (let i = 0; i < 3; i++) { const dx = R(((i * 180 - sc * .35) % 640 + 640) % 640) - 60; rect(g, dx, 182, 6, 3, '#FFFFFF'); rect(g, dx + 5, 179, 3, 3, '#FFFFFF'); rect(g, dx + 8, 180, 2, 1, '#F2A040'); }
    rect(g, 0, 196, PW, 74, mixHex('#86CB62', '#A8A060', p)); rect(g, 0, 226, PW, 16, '#D8C098'); rect(g, 0, 226, PW, 1, '#B8A078');
    for (let i = -1; i < 8; i++) { const x = R(i * 80 - sc % 80); rect(g, x, 206, 2, 20, '#6A4A3A'); disc(g, x + 1, 198, 10, INK); disc(g, x + 1, 198, 9, i % 2 ? '#5E9E52' : '#7AB860'); }
    for (let i = 0; i < 40; i++) { const x = R(((H(i) * 900 - sc * 1.2) % 900 + 900) % 900) - 200, y = R(246 + H(i + 4) * 22); rect(g, x, y, 1, 2, '#5E9E52'); if (i % 3 === 0) rect(g, x - 1, y - 2, 3, 2, ['#FFFFFF', '#FFD860', '#FF8FB0'][i % 3]); }
    const kx = R(380 + Math.sin(t) * 10), ky = R(60 + Math.sin(t * 1.3) * 8); line(g, 270, 200, kx, ky + 8, '#FFFFFF'); for (let j = 0; j < 9; j++) rect(g, kx - (j < 5 ? j : 8 - j), ky - 4 + j, 1 + 2 * (j < 5 ? j : 8 - j), 1, j < 5 ? '#E8546A' : '#F2C14E');
    const by = 240 + (beatPhase(t) < .5 ? -1 : 0);
    bike(g, 236, by, t, 1.4);
    person(g, 'me', 242, by - 22, 2, { sit: true, aR: 'out', aL: u % 6 > 3 ? 'wave' : 'out', eyes: 'happy', mouth: 'smile' }, t);
    for (let i = 0; i < 3; i++) bird(g, R(((u * 26 + i * 30) % 520)) - 20, 60 + i * 9, t + i);
  },
  sunset(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, sy = R(lerp(130, 168, eio(seg(u, 0, d))));
    grad(g, ['#5A4A9A', '#F0907A', '#FFD49A'], 0, 172);
    sun(g, 300, sy, 22, '#FFE0A0', '#FFB070');
    hills(g, TOD.dusk, 0, 160, '#8A6A9A', 12, 3, 70);
    // the sun melts into the river
    rect(g, 0, 170, PW, 100, '#C87A8A'); rect(g, 0, 170, PW, 1, '#FFD8A8');
    for (let i = 0; i < 22; i++) { const w = R(30 - i * 1.1 + Math.sin(t * 3 + i) * 3); rect(g, 300 - w, 172 + i * 4, w * 2, 2, i % 2 ? '#FFE0A0' : '#FFC080'); }
    for (let i = 0; i < 30; i++) if (Math.sin(t * 2 + i) > 0) rect(g, R(H(i) * PW), R(176 + H(i + 3) * 90), 5, 1, '#E8A0A8');
    rect(g, 0, 236, 200, 34, '#6A5A50'); for (let x = 0; x < 200; x += 5) rect(g, x, 234 + (x % 3), 1, 3, '#8A9A5A');
    person(g, 'me', 110, 244, 3, { sit: true, eyes: 'happy', mouth: 'smile', back: true }, t);
    cat(g, 150, 244, 2, 'sit', t, true);
    for (let i = 0; i < 4; i++) bird(g, R(((u * 18 + i * 40) % 520)) - 20, 80 + i * 8, t + i, '#5A3A5A');
  },
  market(g, t, s) {
    const u = local(t, s);
    grad(g, TOD.evening.sky, 0, 200);
    for (let i = 0; i < 9; i++) building(g, i * 56 - 10, 50, 110 + R(H(i) * 40), 200, '#3A3058', .4, i, '#FFD880', '#2A2440');
    rect(g, 0, 200, PW, 70, '#5A4A5A');
    lanterns(g, 0, PW, 30, t, 12, 1);
    // three stalls: fish, vegetables, fruit
    const stalls = [['鱼', '#5A9AD8', ['#8AB0D8', '#A8C8E8']], ['菜', '#4E9A4A', ['#5AA04E', '#E8546A', '#F2C14E']], ['果', '#E8804A', ['#E8546A', '#F2C14E', '#F08A4A']]];
    stalls.forEach(([name, col, goods], i) => {
      const x = 30 + i * 150;
      rect(g, x - 1, 120, 122, 8, INK); for (let j = 0; j < 6; j++) rect(g, x + j * 20, 121, 20, 6, j % 2 ? '#FFFFFF' : col);
      rect(g, x + 4, 128, 2, 90, '#6A4A3A'); rect(g, x + 114, 128, 2, 90, '#6A4A3A');
      rect(g, x - 1, 180, 122, 30, INK); rect(g, x, 181, 120, 28, '#B88A5A');
      for (let k = 0; k < 12; k++) disc(g, x + 8 + (k % 6) * 20, 176 + Math.floor(k / 6) * 6, 4, goods[k % goods.length]);
      ptext(g, name, x + 60, 152, { col: '#FFFFFF', outline: INK });
      halo(g, x + 60, 140, 40, '#FFD880', .5);
    });
    person(g, 'aunt', 210, 180, 2, { eyes: 'happy', mouth: 'smile', aR: 'wave' }, t);
    const P = person(g, 'me', R(lerp(120, 300, eio(seg(u, 0, 5)))), 258, 3, { walk: u < 5 ? walkPh(t) : null, eyes: 'happy', mouth: 'smile', aR: 'hold', look: 1 }, t);
    if (P) { const full = seg(u, 1, 5); rect(g, P.R[0] - 9, P.R[1] - 4, 18, 16, INK); rect(g, P.R[0] - 8, P.R[1] - 3, 16, 14, '#F4E8D8'); if (full > .2) rect(g, P.R[0] - 6, P.R[1] - 8, 3, 5, '#5AA04E'); if (full > .5) disc(g, P.R[0] + 2, P.R[1] - 5, 3, '#E8546A'); if (full > .8) rect(g, P.R[0] + 4, P.R[1] - 10, 2, 7, '#F2E2A8'); }
    for (let i = 0; i < 3; i++) person(g, ['girl', 'grandpa', 'kid'][i], R(((u * 20 * (i % 2 ? 1 : -1) + i * 170) % 560 + 560) % 560 - 40), 240, 2, { walk: t + i, flip: i % 2 === 0, eyes: 'happy' }, t);
  },
  call(g, t, s) {
    const u = local(t, s), ans = u > 2.2;
    grad(g, TOD.evening.sky, 0, PH);
    rect(g, 239, 0, 2, PH, INK);
    // left: him with the shopping, the phone ringing; right: his friend at the gate
    g.save(); g.beginPath(); g.rect(0, 0, 239, PH); g.clip();
    for (let i = 0; i < 5; i++) building(g, i * 56 - 10, 50, 120 + R(H(i + 3) * 40), 210, '#3A3058', .4, i + 3, '#FFD880', '#2A2440');
    rect(g, 0, 210, 239, 60, '#5A4A5A'); lanterns(g, 0, 239, 40, t, 6, 1);
    const A = person(g, 'me', 120, 250, 3, { aR: ans ? 'phone' : 'down', eyes: ans ? 'happy' : 'wide', mouth: ans ? talkMouth(t) : 'open' }, t);
    if (A) phoneS(g, ans ? A.R[0] : 150, ans ? A.R[1] - 4 : 230, !ans, t);
    g.restore();
    g.save(); g.beginPath(); g.rect(241, 0, 239, PH); g.clip();
    stars(g, t, 30, 120, 21, 241, PW);
    rect(g, 241, 210, 239, 60, '#3A3A50'); house(g, 300, 210, 120, 90, { wall: '#D8C8B0', roof: '#8A5A3A', lit: .8, night: true, seed: 9 }); lanterns(g, 270, 450, 90, t, 5);
    rect(g, 270, 150, 4, 60, '#6A4A3A'); rect(g, 446, 150, 4, 60, '#6A4A3A'); rect(g, 266, 146, 188, 6, '#8A5A3A');
    const B = person(g, 'friend', 360, 250, 3, { aR: 'phone', aL: u > 3 ? 'wave' : 'down', eyes: 'happy', mouth: talkMouth(t + .3) }, t);
    if (B) phoneS(g, B.R[0], B.R[1] - 4, false, t);
    g.restore();
  },
  chat(g, t, s) {
    const u = local(t, s);
    grad(g, TOD.evening.sky, 0, 200); stars(g, t, 40, 120, 23);
    for (let i = 0; i < 9; i++) building(g, i * 56 - 10, 50, 120 + R(H(i + 7) * 40), 210, '#3A3058', .45, i + 7, '#FFD880', '#2A2440');
    rect(g, 0, 210, PW, 60, '#4A4058'); lamp(g, 120, 210, 80, 1); lamp(g, 380, 210, 80, 1);
    // talk without end: bubbles take turns, one topic after another
    const k = Math.floor(u / .55), left = k % 2 === 0, f = (u % .55) / .55;
    person(g, 'me', 200, 250, 3, { eyes: 'happy', mouth: left && f < .7 ? talkMouth(t) : 'smile', look: 1, aR: left ? 'out' : 'down' }, t);
    person(g, 'friend', 290, 250, 3, { eyes: 'happy', mouth: !left && f < .7 ? talkMouth(t) : 'grin', look: -1, aL: !left ? 'wave' : 'down' }, t);
    for (let j = Math.max(0, k - 2); j <= k; j++) { const old = k - j, lf = j % 2 === 0, by = 80 - old * 30 + R(f * 6) * (old === 0 ? 0 : 1); if (by < -20) continue; speech(g, lf ? 140 : 280, by, 40, 26, lf ? 196 : 292, by + 34, ICONS[j % ICONS.length], t); }
    if (u > 4) for (let i = 0; i < 3; i++) ptext(g, '哈', 245 + i * 12, 150 - i * 6 - R((u * 10) % 6), { col: '#FFE9A8', outline: INK });
  },
  courtyard(g, t, s) { courtyardScene(g, t, local(t, s), 0); },
  cheers(g, t, s) { courtyardScene(g, t, local(t, s), 1); },
  notomorrow(g, t, s) {
    const u = local(t, s);
    grad(g, TOD.night.sky, 0, PH); stars(g, t, 150, 200, 29); moon(g, 400, 40, 10);
    rect(g, 0, 210, PW, 60, '#3A3448');
    for (let x = 10; x < PW; x += 60) { rect(g, x, 150, 2, 60, '#6A4A3A'); } rect(g, 0, 160, PW, 2, '#6A4A3A');
    // tomorrow's map blows away; he leans back and looks at the sky instead
    const a = seg(u, 1, 5.5), mx = R(lerp(250, 520, a) + Math.sin(u * 3) * 10), my = R(lerp(170, 30, a));
    if (a < 1) { rect(g, mx - 16, my - 11, 32, 22, INK); rect(g, mx - 15, my - 10, 30, 20, '#F4E8C8'); line(g, mx - 12, my - 6, mx + 2, my + 4, '#E8546A'); line(g, mx + 2, my + 4, mx + 12, my - 4, '#E8546A'); ptext(g, '明天', mx, my + 6, { col: INK }); for (let i = 0; i < 3; i++) qmark(g, mx + 20 + i * 10, my - 18 - i * 6, 1, '#FFFFFF'); }
    windLines(g, t * .5, 6, 3, '#8A9AD0', 60, 180);
    person(g, 'me', 220, 236, 3, { sit: true, eyes: u > 2 ? 'happy' : 'open', mouth: 'smile', aL: u > 2 ? 'behind' : 'out', aR: u > 2 ? 'behind' : 'down', look: u < 2 ? 1 : 0 }, t);
    person(g, 'friend', 280, 236, 3, { sit: true, eyes: 'closed', mouth: 'smile', aL: 'behind', aR: 'behind' }, t);
    cat(g, 330, 236, 2, 'sleep', t);
  },
  nightwind(g, t, s) {
    const u = local(t, s);
    courtyardBg(g, t, 1.6);
    for (let i = 0; i < 24; i++) { const x = R(40 + H(i) * 400 + Math.sin(t * .7 + i) * 20), y = R(60 + H(i + 3) * 160 + Math.cos(t * .9 + i) * 10); if (Math.sin(t * 3 + i * 2) > 0) { rect(g, x, y, 1, 1, '#FFF08A'); halo(g, x, y, 3, '#FFF08A', .6); } }
    table(g, t, false);
    for (const [w, x] of [['friend', 160], ['me', 240], ['girl', 320]]) person(g, w, x, 236, 3, { sit: true, eyes: 'closed', mouth: 'smile', blush: true }, t);
    windLines(g, t * .3, 6, 3, '#C8B0D8', 40, 140);
    petals(g, t * .3, 12, ['#FFB0C8', '#FFFFFF'], 9, 1);
    void u;
  },
  perfect(g, t, s) {
    const u = local(t, s);
    grad(g, ['#FFD49A', '#FFE8C0', '#FFF6E4'], 0, PH);
    for (let i = 0; i < 20; i++) if (Math.floor(t * 4 + i) % 3) sparkle(g, R(H(i) * PW), R(H(i + 3) * 230), 1 + (i % 2), '#FFFFFF');
    // the whole day pinned up in photographs
    rect(g, 30, 30, 420, 2, '#8A5A3A');
    const pics = [[70, 0, '#A8DCF8'], [150, 1, '#F2E2A8'], [230, 2, '#2A2E62'], [310, 3, '#F7B8C8'], [390, 0, '#FFC890']];
    pics.forEach(([x, sc, bg], i) => { const a = u - i * .25; if (a < 0) return; const y = 80 + R(Math.sin(t + i) * 3) + R((1 - eout(clamp(a * 3))) * -40); line(g, x, 31, x, y - 26, '#8A5A3A'); rect(g, x - 2, y - 28, 4, 4, '#E8546A'); polaroid(g, x, y, 3, t, sc, bg); });
    rect(g, 0, 200, PW, 70, '#E8C890');
    person(g, 'me', 200, 252, 3, { eyes: 'happy', mouth: 'grin', aL: 'up', aR: 'up', blush: true }, t);
    person(g, 'friend', 280, 252, 3, { eyes: 'happy', mouth: 'smile', aR: 'wave' }, t);
    cat(g, 330, 252, 2, 'sit', t, true);
  },
  offer(g, t, s) {
    const u = local(t, s);
    grad(g, ['#FFC890', '#FFE0B0', '#FFF6E0'], 0, PH);
    for (let i = 0; i < 3; i++) cloud(g, R(((t * 5 + i * 170) % 640) - 90), 30 + i * 20, 1.3, '#FFF0E0', '#F8D0B0');
    const P = person(g, 'me', 240, 330, 8, { eyes: 'happy', mouth: 'smile', blush: true, aR: u > .4 ? 'out' : 'down' }, t);
    if (P && u > .4) { const x = P.R[0] + 4, y = P.R[1]; rect(g, x, y - 26, 2, 26, '#3E8A3A'); rect(g, x - 6, y - 16, 6, 2, '#5AA04E'); for (let i = 0; i < 6; i++) disc(g, x + 1 + R(Math.cos(i) * 6), y - 32 + R(Math.sin(i) * 6), 4, '#FF7AA0'); disc(g, x + 1, y - 32, 3, '#FFD040'); }
    for (let i = 0; i < 6; i++) if (Math.floor(t * 4 + i) % 3) sparkle(g, R(60 + H(i) * 360), R(30 + H(i + 3) * 120), 1 + (i % 2), '#FFFFFF');
  },
  simple(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, p = eio(seg(u, .8, d - 1.2));
    grad(g, ['#D8E8F8', '#EEF4FC', '#FFFFFF'], 0, PH);
    // a scribble of knots and worries pulls straight into one simple line home
    const n = 160;
    let prev = null;
    for (let i = 0; i <= n; i++) {
      const f = i / n, x = lerp(40, 440, f), y = 130, kn = (1 - p) * 60;
      const px = x + Math.sin(f * 37) * kn * 1.2 + Math.cos(f * 13) * kn * .6, py = y + Math.cos(f * 29) * kn + Math.sin(f * 19) * kn * .5;
      if (prev) line(g, R(prev[0]), R(prev[1]), R(px), R(py), p > .95 ? '#E8546A' : INK); prev = [px, py];
    }
    if (u < d * .5) for (let i = 0; i < 6; i++) { const a = u + i; rect(g, R(60 + H(i) * 360 + a * 20), R(40 + H(i + 2) * 40 - a * 8), 10, 12, '#FFFFFF'); rect(g, R(60 + H(i) * 360 + a * 20), R(40 + H(i + 2) * 40 - a * 8), 10, 2, '#E8546A'); }
    if (p > .95) { house(g, 410, 130, 40, 30, { wall: '#F4EEE4', roof: '#D8544A' }); cup(g, 60, 130, t); }
    person(g, 'me', R(lerp(40, 380, p > .95 ? seg(u, d - 1.2, d) : 0)), 250, 3, { eyes: p > .9 ? 'happy' : 'wide', mouth: p > .9 ? 'smile' : 'open', walk: p > .95 ? walkPh(t) : null, look: 1 }, t);
    rect(g, 0, 250, PW, 20, '#C8D8E8');
  },
  horizon(g, t, s) {
    const u = local(t, s);
    grad(g, ['#4A7AC8', '#F8B890', '#FFF0C8'], 0, 180);
    sun(g, 360, 150, 22, '#FFF4C8', '#FFE08A'); halo(g, 360, 150, 80, '#FFFFFF', .7);
    // far away on the next hill, a little town shining in the morning
    for (let i = 0; i < 7; i++) house(g, 300 + i * 18, 160, 14, 12 + (i % 3) * 4, { wall: WALLS[i % 6], roof: ROOFS[i % 6] });
    for (let i = 0; i < 10; i++) if (Math.floor(t * 4 + i) % 3) sparkle(g, R(300 + H(i) * 130), R(120 + H(i + 3) * 40), 1, '#FFFFFF');
    disc(g, 240, 520, 360, '#7AB060'); disc(g, 240, 524, 356, '#8CC86A');
    for (let i = 0; i < 30; i++) { const x = R(H(i) * PW), y = R(200 + H(i + 4) * 66); rect(g, x, y, 1, 3, '#5E9E52'); if (i % 3 === 0) rect(g, x - 1, y - 2, 3, 2, ['#FFFFFF', '#FFD860', '#FF8FB0'][i % 3]); }
    const k = u < 3 ? 3 : 2, y = R(lerp(256, 214, seg(u, 0, 7)));
    person(g, 'me', R(lerp(170, 220, seg(u, 0, 7))), y, k, { back: true, walk: walkPh(t), aR: 'out' }, t);
    person(g, 'friend', R(lerp(214, 256, seg(u, 0, 7))), y, k, { back: true, walk: walkPh(t) + .5, aL: 'out' }, t);
    cat(g, R(lerp(250, 290, seg(u, 0, 7))), y, 2, 'walk', t);
    for (let i = 0; i < 4; i++) bird(g, R(((u * 20 + i * 30) % 520)) - 20, 60 + i * 8, t + i);
  },
  goodnight(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0;
    if (u < 9) {
      // back in his room: the lamp goes off, the cat curls up
      bedroomBg(g, t, 0, false, true);
      bed(g, true, t, 'closed');
      cat(g, 120, 186, 2, 'sleep', t);
      if (u < 3) halo(g, 404, 150, 50, '#FFD880', .9);
      rect(g, 398, 150, 3, 30, '#3E3A48'); rect(g, 390, 140, 20, 12, INK); rect(g, 391, 141, 18, 10, u < 3 ? '#FFE09A' : '#6A6A7A');
      blackout(g, u > 3 ? .35 : 0);
      if (u > 3) for (let i = 0; i < 3; i++) { const p = (u * .4 + i / 3) % 1; ptext(g, 'Z', R(230 + p * 30 + i * 4), R(150 - p * 40), { col: '#FFFFFF', outline: INK }); }
      return;
    }
    // the whole town goes to sleep under the stars; the title again
    const a = u - 9;
    grad(g, TOD.night.sky, 0, 190); stars(g, t, 140, 160, 31); moon(g, 380, 40, 12);
    hills(g, TOD.night, 0, 160, TOD.night.far, 16, 3, 80);
    rect(g, 0, 176, PW, 14, TOD.night.sea); for (let i = 0; i < 14; i++) if (Math.sin(t * 2 + i) > 0) rect(g, R(H(i) * PW), 178 + (i % 5) * 2, 5, 1, '#8AA0E0');
    hills(g, TOD.night, 0, 186, TOD.night.mid, 10, 9, 56);
    for (let i = 0; i < 11; i++) { const w = 40 + R(H(i * 5) * 12), h = 30 + R(H(i * 7) * 28), x = i * 52 - 20 + R(H(i) * 8); house(g, x, 232, w, h, { wall: mixHex(WALLS[i % 6], '#2A2E4A', .55), roof: mixHex(ROOFS[i * 7 % 6], '#1A1E30', .5), lit: H(i + 5) > seg(a, 0, 6) ? 1 : 0, night: true, seed: i, chimney: H(i + 3) > .4 }); }
    rect(g, 0, 232, PW, 38, '#2A3048'); rect(g, 0, 232, PW, 2, '#4E5274');
    const chars = [...'平凡的一天'], shown = Math.ceil(seg(a, 2, 4.5) * 5);
    if (shown > 0) ptext(g, chars.slice(0, shown).join(''), 240, 96, { size: 48, col: '#FFF6E0', outline: INK, shadow: '#3A4A8A' });
    if (a > 5) ptext(g, '毛不易 · 像素 MV', 240, 120, { col: '#FFF6E0', outline: INK });
    blackout(g, seg(u, d - 4, d - .2));
  },
};
const talkMouth = t => singing(t) ? 'open' : 'smile';
// his bedroom in the morning: the window, the plant, the sunbeam on the floor; light 0..1
function bedroomBg(g, t, light, sitting = false, night = false) {
  rect(g, 0, 0, PW, PH, night ? '#2A2E4E' : mixHex('#5A5A86', '#F2E4CC', light)); for (let x = 0; x < PW; x += 16) rect(g, x, 0, 1, 200, night ? '#262A46' : mixHex('#52527C', '#EAD8BC', light));
  rect(g, 0, 200, PW, 70, night ? '#3A3448' : mixHex('#5A4A5A', '#C8A07A', light)); for (let x = 0; x < PW; x += 40) rect(g, x, 200, 1, 70, night ? '#342E40' : mixHex('#524254', '#B8906A', light));
  const wx = 40, wy = 30, ww = 130, wh = 110;
  if (night) { grad(g, TOD.night.sky, 0, PH); rect(g, 0, 0, wx, PH, '#2A2E4E'); rect(g, wx + ww, 0, PW, PH, '#2A2E4E'); rect(g, wx, 0, ww, wy, '#2A2E4E'); rect(g, wx, wy + wh, ww, PH, '#2A2E4E'); rect(g, 0, 200, PW, 70, '#3A3448'); stars(g, t, 20, wy + wh, 9, wx, wx + ww); moon(g, wx + 100, wy + 26, 8); }
  else { gradRect(g, skyMix(TOD.dawn.sky, TOD.morning.sky, light, 8), wx, wy, ww, wh); cloud(g, R(wx + 20 + (t * 3) % 80), wy + 30, .8); }
  rect(g, wx - 4, wy - 4, ww + 8, 4, '#FFFFFF'); rect(g, wx - 4, wy + wh, ww + 8, 6, '#FFFFFF'); rect(g, wx - 4, wy, 4, wh, '#FFFFFF'); rect(g, wx + ww, wy, 4, wh, '#FFFFFF'); rect(g, wx + ww / 2 - 1, wy, 3, wh, '#FFFFFF');
  rect(g, wx - 18, wy - 8, 16, wh + 20, '#8CC0E0'); rect(g, wx + ww + 2, wy - 8, 16, wh + 20, '#8CC0E0');
  flowerPot(g, wx + 30, wy + wh, 1, 0); flowerPot(g, wx + 100, wy + wh, 1, 4);
  if (!night && light > .2) { sunbeam(g, wx + 10, wx + ww - 10, wy + wh + 6, 268, .25 * light); motes(g, t, wx, wy + wh, 200, 70, 14); }
  rect(g, 300, 40, 60, 40, INK); rect(g, 302, 42, 56, 36, '#F4F0E8'); rect(g, 306, 46, 22, 28, '#A8DCF8'); rect(g, 332, 46, 22, 28, '#FFC890');
  void sitting;
}
function bed(g, inBed, t, eyes) {
  rect(g, 160, 150, 10, 64, '#8A5A3A'); rect(g, 160, 186, 200, 28, INK); rect(g, 161, 187, 198, 26, '#8A5A3A');
  rect(g, 170, 170, 46, 18, INK); rect(g, 171, 171, 44, 16, '#FFFFFF');
  if (inBed) { g.save(); g.beginPath(); g.rect(0, 0, PW, 182); g.clip(); person(g, 'me', 200, 240, 3, { eyes, mouth: 'smile' }, t); g.restore(); }
  rect(g, inBed ? 190 : 230, inBed ? 178 : 180, inBed ? 166 : 126, 12, INK); rect(g, inBed ? 191 : 231, inBed ? 179 : 181, inBed ? 164 : 124, 10, '#7EC0E8'); for (let x = inBed ? 196 : 236; x < 352; x += 12) rect(g, x, inBed ? 180 : 182, 6, 8, '#9ED0F0');
}
// lying on his back: head and shoulders, body stretched along the ground (drawn sideways with rects)
function lying(g, X, Y, mode, T) {
  const L = CAST.me; g.save(); g.translate(X, Y); g.scale(3, 3); const x = 0, y = 0;
  rect(g, x - 1, y - 9, 66, 12, INK); rect(g, x, y - 8, 40, 10, L.top); rect(g, x + 40, y - 8, 24, 10, L.bottom); rect(g, x + 64, y - 7, 6, 8, INK); rect(g, x + 64, y - 6, 5, 6, L.shoe);
  rect(g, x + 22, y - 6, 4, 4, L.tee);
  disc(g, x - 8, y - 6, 9, INK); disc(g, x - 8, y - 6, 8, L.skin); rect(g, x - 16, y - 14, 10, 16, L.hair); rect(g, x - 17, y - 13, 1, 14, INK);
  rect(g, x - 9, y - 9, 2, 1, INK); rect(g, x - 9, y - 4, 2, 1, INK); rect(g, x - 4, y - 7, 1, 2, INK);
  rect(g, x - 22, y - 12, 8, 4, L.skin); rect(g, x - 22, y - 2, 8, 4, L.skin);
  if (mode === 'night') for (let i = 0; i < 2; i++) sparkle(g, x - 6 + i * 6, y - 20, 1, '#FFFFFF');
  g.restore(); void T;
}
function table(g, t, full) {
  rect(g, 120, 200, 240, 8, INK); rect(g, 121, 201, 238, 6, '#F4F0E8'); for (let x = 121; x < 359; x += 12) rect(g, x, 201, 6, 6, '#F8C0C8');
  rect(g, 130, 208, 4, 40, '#8A5A3A'); rect(g, 346, 208, 4, 40, '#8A5A3A');
  for (const [x, c] of [[160, '#E8804A'], [210, '#5AA04E'], [270, '#F2C14E'], [320, '#E8546A']]) { rect(g, x - 12, 196, 24, 5, INK); rect(g, x - 11, 197, 22, 3, '#FFFFFF'); disc(g, x, 194, 6, c); }
  if (full) for (const x of [180, 240, 300]) glass(g, x, 198, ['#F2C14E', '#E8546A', '#F2C14E'][x % 3]);
  void t;
}
function courtyardBg(g, t, dark) {
  grad(g, TOD.night.sky, 0, 180); stars(g, t, 80, 140, 27);
  rect(g, 0, 120, PW, 80, '#6A5A70'); for (let y = 124; y < 200; y += 8) for (let x = (y % 16) ? 0 : 10; x < PW; x += 20) rect(g, x, y, 18, 6, '#7A6A80');
  for (let i = 0; i < 14; i++) { const x = 10 + i * 34; disc(g, x, 186, 12, INK); disc(g, x, 186, 11, '#3E7A4A'); for (let k = 0; k < 4; k++) disc(g, x - 6 + k * 4, 180 + (k % 2) * 6, 2, ['#FF7AA0', '#FFFFFF', '#FFE060', '#E8546A'][(i + k) % 4]); }
  rect(g, 0, 198, PW, 72, '#4A3E52');
  lanterns(g, 0, PW, 20, t, 10, dark);
}
function courtyardScene(g, t, u, part) {
  courtyardBg(g, t, 1);
  halo(g, 240, 190, 120, '#FFD880', .5);
  table(g, t, true);
  if (part === 0) {
    // friends arrive and sit down one after another
    const who = [['friend', 160], ['girl', 320], ['aunt', 380], ['me', 240]];
    who.forEach(([w, x], i) => { const a = seg(u, i * 1.2, i * 1.2 + 1); if (a <= 0) return; person(g, w, R(lerp(x < 240 ? -20 : 500, x, eout(a))), 236, 3, { sit: a >= 1, walk: a < 1 ? t * 2 : null, eyes: 'happy', mouth: 'smile', look: x < 240 ? 1 : -1 }, t); });
    return;
  }
  // a little tipsy: glasses up, a guitar, songs and laughter
  const up = beatPhase(t) < .5;
  const A = person(g, 'friend', 160, 236, 3, { sit: true, aR: 'up', eyes: 'happy', mouth: 'grin', blush: true, dy: up ? -2 : 0 }, t);
  const B = person(g, 'me', 240, 236, 3, { sit: true, aR: 'hold', aL: 'hold', eyes: 'happy', mouth: 'open', blush: true }, t);
  person(g, 'girl', 320, 236, 3, { sit: true, aL: 'up', eyes: 'happy', mouth: 'smile', blush: true, dy: !up ? -2 : 0 }, t);
  person(g, 'aunt', 380, 236, 3, { sit: true, aR: 'wave', eyes: 'happy', mouth: 'grin', blush: true }, t);
  if (A) glass(g, A.R[0], A.R[1] - 4, '#F2C14E');
  if (B) guitar(g, B.R[0] + 4, B.R[1] + 2);
  for (let i = 0; i < 5; i++) { const p = (u * .5 + i / 5) % 1; note(g, R(200 + i * 20 + Math.sin(t * 3 + i) * 6), R(150 - p * 100), ['#FFE9A8', '#FF7AA0'][i % 2]); }
}

// ---------------------------------------------------------------- one frame
const XF = .35;
const NO_XF = new Set(['askyou', 'cheers']);
const THEME = { dawn: 'night', bedroom: 'night', sunset: 'dusk', market: 'dusk', call: 'dusk', chat: 'night', courtyard: 'night', cheers: 'night', notomorrow: 'night', nightwind: 'night', goodnight: 'night', ride: 'dusk', perfect: 'dusk', offer: 'dusk', horizon: 'dusk' };
let bufA = null, bufB = null;
function shotInto(g, i, t) { g.setTransform(1, 0, 0, 1, 0, 0); g.imageSmoothingEnabled = false; SCENES[SHOTS[i].name](g, t, SHOTS[i]); }
function themeOf(s) { if (THEME[s.name]) return THEME[s.name]; if (['ordinary', 'askyou', 'slowhome', 'idle', 'breeze'].includes(s.name)) return ['dusk', 'night', 'day'][s.v]; return 'day'; }
function drawFrame(g, t) {
  t = clamp(t, 0, DUR - 1e-4);
  if (!bufA) { bufA = document.createElement('canvas'); bufB = document.createElement('canvas'); bufA.width = bufB.width = PW; bufA.height = bufB.height = PH; }
  const i = shotIndex(t), s = SHOTS[i];
  if (i > 0 && t - s.t0 < XF && !NO_XF.has(s.name)) { shotInto(bufA.getContext('2d'), i - 1, t); shotInto(bufB.getContext('2d'), i, t); ditherMix(g, bufA, bufB, (t - s.t0) / XF); }
  else shotInto(g, i, t);
  subtitle(g, t, SUB[themeOf(s)]);
}
