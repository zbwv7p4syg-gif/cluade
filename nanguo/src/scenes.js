// scenes.js — 我不难过 · 像素 MV. One function per shot (see timeline.js), all in 480×270 pixels.
// Each shot gets (g, t, s): the canvas, the song time, and its entry in SHOTS (s.t0, s.t1, s.v, extras).

const MOODS = [
  { sky: ['#0A0E26', '#161C44', '#26305E'], far: '#121632', farWin: '#C8B070', ground: '#20243A', wall: '#2E3456', wallLn: '#262B4A', rain: '#7F95C8', glow: '#FFE9A8', dark: '#0C0C1E', room: '#262A4A', roomLn: '#20243E' },
  { sky: ['#2A2050', '#8E4E86', '#F09A78'], far: '#3A2448', farWin: '#FFD8A0', ground: '#4A3550', wall: '#6A4A6A', wallLn: '#5E405E', rain: null, glow: '#FFD0A0', dark: '#1E1428', room: '#5A3E5A', roomLn: '#4E3450' },
  { sky: ['#1A2856', '#4E6CA8', '#E8B4A0'], far: '#26365E', farWin: '#FFE8B0', ground: '#3A4668', wall: '#4E5E84', wallLn: '#44527A', rain: null, glow: '#FFF0C8', dark: '#101A30', room: '#3E4A70', roomLn: '#36406A' },
];
const SUB_THEMES = [
  { box: '#141A3A', edge: '#33407A', dim: '#7F8CC0', lit: '#F4F6FF' },
  { box: '#2A1A34', edge: '#5A3A62', dim: '#B08AA8', lit: '#FFF0E0' },
  { box: '#18244A', edge: '#3A5084', dim: '#8EA2CC', lit: '#FFF4E4' },
];
const local = (t, s) => t - s.t0;
const talk = t => singing(t) ? 'open' : 'flat';

// ---------------------------------------------------------------- helpers for the shots
let _gbuf = null;
// a dithered gradient limited to a rectangle (putImageData ignores clipping, so go through a scratch canvas)
function gradRect(g, stops, x, y, w, h, y0 = y, y1 = y + h) {
  if (!_gbuf) { _gbuf = document.createElement('canvas'); _gbuf.width = PW; _gbuf.height = PH; }
  const b = _gbuf.getContext('2d'); grad(b, stops, y0, y1);
  g.drawImage(_gbuf, R(x), R(y), R(w), R(h), R(x), R(y), R(w), R(h));
}
// sun rays around (cx, cy), drawn straight into the frame as the background
function rays(g, cx, cy, n, a, b, rot, edge = null, edgeK = 0) {
  const img = g.createImageData(PW, PH), d = img.data, A = hex(a), B = hex(b), E = edge ? hex(edge) : null;
  for (let y = 0; y < PH; y++) for (let x = 0; x < PW; x++) {
    const an = Math.atan2(y - cy, x - cx) + rot, s = ((an / (Math.PI * 2) * n) % 1 + 1) % 1;
    let c = s < .5 ? A : B;
    if (E) { const dx = (x - PW / 2) / (PW / 2), dy = (y - PH / 2) / (PH / 2), r = Math.sqrt(dx * dx * .8 + dy * dy); if (r - .55 > bayer(x, y) * (1.6 - edgeK)) c = E; }
    const o = (y * PW + x) * 4; d[o] = c[0]; d[o + 1] = c[1]; d[o + 2] = c[2]; d[o + 3] = 255;
  }
  g.putImageData(img, 0, 0);
}
// a skyline of blocks at world positions, so windows don't flicker when it scrolls
function skyline(g, sc, top, base, col, lit, seed, win = '#FFE08A', off = '#1A1E3A', step = 48) {
  const i0 = Math.floor(sc / step) - 1;
  for (let i = i0; i < i0 + PW / step + 3; i++) {
    const x = R(i * step - sc), h = R(H(i * 7 + seed) * (base - top) * .6 + (base - top) * .3), w = step - 4 - R(H(i + seed) * 10);
    rect(g, x, base - h, w, h, col);
    for (let wy = base - h + 5, r = 0; wy < base - 6; wy += 9, r++) for (let wx = 4, c = 0; wx < w - 5; wx += 8, c++) rect(g, x + wx, wy, 3, 4, H(i * 31 + r * 7 + c * 3 + seed) < lit ? win : off);
  }
}
function houseFront(g, x, base, w, h, M, o = {}) {
  x = R(x); const top = base - h, cx = x + R(w / 2), roof = o.roof || '#5A3442', wall = o.wall || M.wall;
  for (let j = 0; j <= 16; j++) { const hw = R((w / 2 + 6) * j / 16); rect(g, cx - hw - 1, top - 17 + j, hw * 2 + 2, 1, INK); rect(g, cx - hw, top - 17 + j, hw * 2, 1, j % 4 === 3 ? '#4A2836' : roof); }
  rect(g, x - 1, top - 1, w + 2, h + 1, INK); rect(g, x, top, w, h, wall);
  for (let y = top + 6; y < base; y += 6) rect(g, x, y, w, 1, o.wallLn || M.wallLn);
  const win = (wx, lit) => { rect(g, wx - 1, top + 11, 24, 20, INK); rect(g, wx, top + 12, 22, 18, lit ? M.glow : '#1C2038'); if (lit) checker(g, wx, top + 12, 22, 18, '#FFFFFF', .12); rect(g, wx + 10, top + 12, 2, 18, INK); rect(g, wx, top + 20, 22, 2, INK); };
  win(x + 10, o.litL); win(x + w - 32, o.litR);
  if (o.door !== false) { rect(g, cx - 11, base - 36, 22, 36, INK); rect(g, cx - 10, base - 35, 20, 35, o.open ? '#FFD890' : '#5A3A2E'); if (!o.open) { rect(g, cx - 7, base - 32, 14, 12, '#4A2E24'); rect(g, cx + 5, base - 18, 2, 2, '#E8C060'); } }
  if (o.porch) { rect(g, cx - 2, base - 44, 5, 5, INK); rect(g, cx - 1, base - 43, 3, 3, '#FFF2C0'); halo(g, cx, base - 41, 16, '#FFE9A8', .8); }
}
// the night street in front of his house; sc scrolls the world to the left
function street(g, t, v, sc = 0, o = {}) {
  const M = MOODS[v];
  grad(g, M.sky, 0, 190);
  if (o.moon) moon(g, o.moon[0], o.moon[1], 9);
  if (v === 2) stars(g, t, 24, 80, 4);
  skyline(g, sc * .3, 120, 192, M.far, v === 1 ? .12 : .22, 50, M.farWin, '#1A1E3A');
  rect(g, 0, 190, PW, 80, M.ground);
  for (let i = Math.floor(sc / 150) - 1; i < sc / 150 + 4; i++) {
    const hx = i * 150 - sc + 20, his = i === 2;
    houseFront(g, hx, 206, 112, 64, M, { litL: his ? o.hisLit ?? 1 : H(i + 3) > (o.dark ?? .5), litR: H(i + 9) > (o.dark ?? .5), porch: his, open: his && o.open, roof: his ? '#6A3A4A' : i % 2 ? '#4A3A5A' : '#5A3442' });
  }
  rect(g, 0, 206, PW, 8, '#3A3E58'); rect(g, 0, 206, PW, 1, '#4E5274');
  rect(g, 0, 214, PW, 56, '#1A1C2E');
  for (let x = -40; x < PW + 40; x += 40) rect(g, R(x - sc % 40), 246, 18, 2, '#3A3C52');
  for (let i = Math.floor(sc / 200) - 1; i < sc / 200 + 4; i++) lamp(g, R(i * 200 - sc + 95), 214, 84, o.lamps ?? 1, M.glow);
  if (M.rain || o.rain) { for (let i = 0; i < 9; i++) { const px = R(((i * 97 + 30 - sc) % 600 + 600) % 600 - 60); checker(g, px, 222 + (i % 3) * 13, 26, 2, '#4A5280', .5); } }
}
function rainFor(g, t, v, n = 120, o = {}) { const M = MOODS[v]; if (M.rain && n > 0) { rain(g, t, n, M.rain, PH, 1, o.slant ?? .15); if (o.splash !== false) splashes(g, t, R(n / 10), 224, 268, '#6A7CA8'); } }
// two-shot backgrounds: his porch at night (0), a riverside at dusk (1), a street before dawn (2)
function backdrop(g, t, v, o = {}) {
  const M = MOODS[v];
  if (v === 0) {
    grad(g, M.sky, 0, 200);
    skyline(g, 0, 100, 200, M.far, .2, 30, M.farWin, '#181C38');
    rect(g, 0, 196, PW, 74, '#1E2238');
    lamp(g, 60, 200, 92, 1, M.glow);
    const wx = o.wallX ?? 262, dx = o.doorX ?? 326;
    g.save(); g.beginPath(); g.rect(0, 0, wx, 244); g.clip(); rain(g, t, 80, M.rain); g.restore();
    rect(g, wx, 0, PW - wx, 244, M.wall); for (let y = 6; y < 244; y += 7) rect(g, wx, y, PW - wx, 1, M.wallLn);
    rect(g, wx - 3, 0, 3, 244, INK); rect(g, wx - 8, 0, PW, 10, '#4A2E3E'); rect(g, wx - 8, 10, PW, 2, INK);
    rect(g, dx - 3, 66, 86, 180, INK); rect(g, dx, 69, 80, 177, '#FFD890'); checker(g, dx, 69, 80, 177, '#FFF2C8', .35);
    rect(g, dx + 46, 96, 22, 16, '#C89A60'); rect(g, dx + 48, 98, 18, 12, '#E8B878');
    halo(g, dx + 40, 50, 30, '#FFE9A8', .9); rect(g, dx + 36, 46, 9, 6, INK); rect(g, dx + 37, 47, 7, 4, '#FFF2C0');
    rect(g, 0, 244, PW, 26, '#3A3048'); for (let x = 0; x < PW; x += 24) rect(g, x, 244, 1, 26, '#30283E');
    for (let j = 0; j < 20; j++) checker(g, dx - j * 2, 244 + j, 80 + j * 4, 1, '#FFD890', .3);
  } else if (v === 1) {
    grad(g, M.sky, 0, 170);
    sun(g, 380, 150, 18, '#FFE0A0', '#FFB070');
    for (let i = 0; i < 3; i++) cloud(g, R(((t * 3 + i * 170) % 640) - 80), 34 + i * 18, 1 + (i % 2) * .5, '#E8A0A8', '#C47A92');
    skyline(g, 0, 118, 168, '#3A2448', .1, 70, '#FFD8A0', '#2A1A38');
    rect(g, 0, 166, PW, 40, '#C8708A'); for (let y = 168; y < 206; y += 3) for (let x = 0; x < PW; x += 14) if (H(x + y * 3 + Math.floor(t * 3)) > .7) rect(g, x, y, 5, 1, y < 182 ? '#FFC8A0' : '#A85A7A');
    rect(g, 0, 206, PW, 64, '#4A3550');
    rect(g, 0, 196, PW, 3, '#2A1A30'); for (let x = 6; x < PW; x += 26) rect(g, x, 196, 3, 14, '#2A1A30'); rect(g, 0, 206, PW, 2, '#5E4466');
    for (let x = 0; x < PW; x += 30) rect(g, x, 230, 15, 1, '#5A4060');
  } else {
    grad(g, M.sky, 0, 200);
    stars(g, t, 24, 70, 6);
    skyline(g, 0, 110, 200, M.far, .18, 90, M.farWin, '#1E2A4E');
    rect(g, 0, 196, PW, 74, M.ground); rect(g, 0, 196, PW, 2, '#56628A');
    lamp(g, 80, 200, 92, 1, M.glow); lamp(g, 410, 200, 92, 1, M.glow);
    for (let x = 0; x < PW; x += 36) rect(g, x, 236, 18, 2, '#4C5880');
  }
}
// her room: a big window on the left (its sky drawn by skyFn), a window seat, a lamp and a calendar
function room(g, t, v, skyFn, o = {}) {
  const M = MOODS[v], wx = 54, wy = 34, ww = 176, wh = 150;
  rect(g, 0, 0, PW, PH, M.room); for (let x = 0; x < PW; x += 16) rect(g, x, 0, 1, 210, M.roomLn);
  g.save(); g.beginPath(); g.rect(wx, wy, ww, wh); g.clip(); skyFn(g, wx, wy, ww, wh); g.restore();
  rect(g, wx - 4, wy - 4, ww + 8, 4, INK); rect(g, wx - 4, wy + wh, ww + 8, 4, INK); rect(g, wx - 4, wy, 4, wh, INK); rect(g, wx + ww, wy, 4, wh, INK);
  rect(g, wx + ww / 2 - 2, wy, 4, wh, INK); rect(g, wx, wy + wh / 2 - 2, ww, 4, INK);
  rect(g, wx - 3, wy - 3, ww + 6, 1, '#8A7A9A');
  // curtains
  for (const [cx, dir] of [[wx - 22, 1], [wx + ww + 4, -1]]) { rect(g, cx, wy - 10, 18, wh + 26, '#C8667E'); for (let i = 0; i < 18; i += 5) rect(g, cx + i, wy - 10, 1, wh + 26, '#A84E66'); rect(g, cx - 1, wy - 10, 1, wh + 26, INK); rect(g, cx + 18, wy - 10, 1, wh + 26, INK); void dir; }
  rect(g, wx - 30, wy - 14, ww + 60, 4, '#6A5060');
  // window seat and floor
  rect(g, 0, 210, PW, 60, '#4A3A4A'); for (let x = 0; x < PW; x += 40) rect(g, x, 210, 1, 60, '#3E3040');
  rect(g, wx - 10, wy + wh + 4, ww + 20, 8, '#E8D8C8'); rect(g, wx - 10, wy + wh + 12, ww + 20, 26, '#B89A88'); rect(g, wx - 11, wy + wh + 3, ww + 22, 1, INK);
  // desk, lamp and calendar on the right
  rect(g, 330, 170, 130, 6, '#8A5A3A'); rect(g, 340, 176, 6, 34, '#6A4228'); rect(g, 444, 176, 6, 34, '#6A4228');
  const lampOn = o.lampOn ?? 1;
  if (lampOn) halo(g, 420, 140, 46, '#FFD890', .9);
  rect(g, 418, 140, 3, 30, '#3E3A48'); rect(g, 408, 128, 22, 12, INK); rect(g, 409, 129, 20, 10, lampOn ? '#FFE09A' : '#8A8070'); rect(g, 412, 168, 14, 3, '#3E3A48');
  rect(g, 352, 152, 30, 18, INK); rect(g, 353, 153, 28, 16, '#F2EADF'); rect(g, 356, 156, 22, 10, '#7AA0D8');
  const day = o.day ?? 12;
  rect(g, 360, 60, 48, 56, INK); rect(g, 361, 61, 46, 54, '#F4F0E8'); rect(g, 361, 61, 46, 12, '#D8344C'); for (let i = 0; i < 4; i++) rect(g, 366 + i * 11, 58, 2, 6, '#8A8A9A');
  ptext(g, String(day), 384, 102, { size: 24, col: INK });
  if (o.plant != null) { const p = o.plant; rect(g, 196, wy + wh - 8, 18, 12, '#B0603A'); for (let i = 0; i < p; i++) { rect(g, 204 + (i % 2 ? 2 : -3), wy + wh - 10 - i * 4, 4, 2, '#5AA04E'); } rect(g, 204, wy + wh - 10 - p * 4, 1, p * 4, '#3E7A3A'); }
}
function windowSky(v, t) {
  const M = MOODS[v];
  return (g, x, y, w, h) => {
    gradRect(g, M.sky, x, y, w, h, y, y + h);
    if (v === 0) { skyline(g, 40, y + h - 70, y + h, '#141836', .3, 13, '#E8C878', '#1A1E3A', 30); for (let i = 0; i < 26; i++) { const sx = x + R(H(i * 3) * w), sy = y + R(((t * (8 + 6 * H(i)) + H(i + 5) * h) % h)); rect(g, sx, sy, 1, 5, '#8FA8D8'); rect(g, sx, sy + 5, 2, 2, '#B8CCF0'); } }
    if (v === 1) { sun(g, x + w * .7, y + h * .72, 14, '#FFE0A0', '#FFB070'); skyline(g, 10, y + h - 50, y + h, '#3A2448', .1, 17, '#FFD8A0', '#2A1A38', 30); }
    if (v === 2) { stars(g, t, 12, y + h * .5, 8, x, x + w); skyline(g, 25, y + h - 60, y + h, '#26365E', .25, 19, '#FFE8B0', '#1E2A4E', 30); }
  };
}
// the clasped hands close-up; sep 0 = holding, 1 = let go and apart
function handsClose(g, t, v, sep = 0) {
  const M = MOODS[v];
  grad(g, [M.dark, M.sky[1], M.sky[2]], 0, PH);
  for (let i = 0; i < 18; i++) bokeh(g, H(i) * PW, H(i + 4) * 200 + 10, 6 + H(i + 7) * 16, i % 3 ? M.glow : '#8FA8D8', .14 + .08 * Math.sin(t + i));
  if (M.rain) rain(g, t, 60, M.rain);
  const breathe = R(Math.sin(t * 2) * 1), open = eio(sep), dxL = -R(open * 70), dxR = R(open * 80), y0 = 112 + breathe;
  const box = (x, y, w, h, col) => { rect(g, x - 2, y - 2, w + 4, h + 4, INK); rect(g, x, y, w, h, col); };
  // her sleeve and hand from the left
  box(-10 + dxL, y0 + 6, 190, 54, '#F2EADF'); rect(g, -10 + dxL, y0 + 46, 190, 14, '#CFC0AE'); box(160 + dxL, y0 + 2, 26, 62, '#E2445C');
  box(186 + dxL, y0 + 10, 56, 44, '#F7D7C2'); rect(g, 186 + dxL, y0 + 44, 56, 10, '#E2AE96');
  if (open > .3) for (let i = 0; i < 4; i++) box(240 + dxL, y0 + 12 + i * 10, 18 - i * 2, 7, '#F7D7C2');
  box(206 + dxL, y0 - 6 + R(open * 8), 26, 14, '#F7D7C2');  // her thumb over his hand
  // his sleeve and hand from the right, wrapped over hers
  box(300 + dxR, y0 - 2, 200, 60, '#3D5D9E'); rect(g, 300 + dxR, y0 + 44, 200, 14, '#2B457C'); box(284 + dxR, y0 - 4, 22, 64, '#2B457C');
  if (open < .3) { box(222, y0 + 4, 66, 50, '#F0CBAE'); for (let i = 0; i < 3; i++) rect(g, 236 + i * 14, y0 + 6, 2, 46, '#C8987E'); rect(g, 222, y0 + 44, 66, 10, '#D6A487'); }
  else { box(246 + dxR, y0 + 4, 42, 50, '#F0CBAE'); for (let i = 0; i < 4; i++) box(228 + dxR, y0 + 8 + i * 11, 18 + i, 8, '#F0CBAE'); }
  if (open < .3) box(208 + dxL, y0 - 6, 24, 14, '#F7D7C2');
}
// a gentle, glowing picture of the other girl inside a thought bubble that comes out of him
function dreamBubble(g, t, cx, cy, w, h, grow) {
  const s = eout(grow); if (s <= 0) return;
  const W = R(w * s), Hh = R(h * s), x = R(cx - W / 2), y = R(cy - Hh / 2);
  const bumps = [];
  for (let i = 0; i < 10; i++) { const a = i / 10 * Math.PI * 2; bumps.push([cx + Math.cos(a) * W * .46, cy + Math.sin(a) * Hh * .42, Math.min(W, Hh) * .22]); }
  for (const [bx, by, r] of bumps) disc(g, bx, by, r + 2, INK);
  rect(g, x + 8, y + 8, W - 16, Hh - 16, INK);
  for (const [bx, by, r] of bumps) disc(g, bx, by, r, '#FFE4EC');
  rect(g, x + 10, y + 10, W - 20, Hh - 20, '#FFE4EC');
  g.save(); g.beginPath(); g.rect(x + 12, y + 12, W - 24, Hh - 24); g.clip();
  halo(g, cx, cy + 10, Math.min(W, Hh) * .45, '#FFB8CC', .9);
  for (let i = 0; i < 12; i++) { const fx = x + 16 + i * ((W - 32) / 11), fy = y + Hh - 16; rect(g, fx, fy - 6, 1, 6, '#5AA04E'); rect(g, fx - 1, fy - 9, 3, 3, ['#FF8FB0', '#FFFFFF', '#FFD860'][i % 3]); }
  if (s > .8) {
    const P = person(g, 'her', cx, y + Hh - 12, 3, { eyes: 'happy', mouth: 'smile', blush: true, aR: 'hold', aL: 'hold', glow: '#FFFFFF' }, t);
    if (P) { rect(g, P.R[0] - 6, P.R[1] - 9, 12, 10, INK); rect(g, P.R[0] - 5, P.R[1] - 8, 10, 8, '#F2EADF'); rect(g, P.R[0] - 5, P.R[1] - 8, 10, 2, '#C88A5A');
      for (let i = 0; i < 3; i++) rect(g, P.R[0] - 3 + i * 3, P.R[1] - 14 - R((t * 8 + i * 3) % 8), 1, 3, '#FFFFFF'); }
    for (let i = 0; i < 5; i++) { const p = (t * .4 + i / 5) % 1; heart(g, R(x + 24 + H(i) * (W - 48)), R(y + Hh - 20 - p * (Hh - 30)), 1, '#FF7FA0', null); }
    petals(g, t, 18, ['#FFB0C8', '#FFFFFF'], 5);
  }
  g.restore();
  for (let i = 0; i < 3; i++) if (grow > .2 + i * .15) { const r = 2 + i * 2; disc(g, cx + w * .38 + 12 - i * 14, cy + h * .5 + 18 - i * 12, r + 1, INK); disc(g, cx + w * .38 + 12 - i * 14, cy + h * .5 + 18 - i * 12, r, '#FFE4EC'); }
}
// a cross of two sticking plasters over a heart
function plaster(g, x, y, k) {
  const L = 7 * k, w = 2 * k;
  for (const sgn of [1, -1]) for (let i = -L; i <= L; i++) rect(g, x + i - 1, y + sgn * i - 1, w + 2, w + 2, INK);
  for (const sgn of [1, -1]) for (let i = -L; i <= L; i++) rect(g, x + i, y + sgn * i, w, w, Math.abs(i) < 2 * k ? '#E8B888' : '#F4D8B0');
  for (const [dx, dy] of [[-4, -4], [4, 4], [-4, 4], [4, -4]]) rect(g, x + dx * k / 1.4 + k / 2, y + dy * k / 1.4 + k / 2, 1, 1, '#C89868');
}
function scarfTail(g, x, y, k, t, dir = 1, n = 6, strong = 1) {
  for (let i = 0; i < n; i++) { const yy = y + R(Math.sin(t * 12 + i * .9) * k * strong * (i / n) * 2); rect(g, x + dir * i * 2 * k - 1, yy - 1, 2 * k + 2, k + 2, INK); }
  for (let i = 0; i < n; i++) { const yy = y + R(Math.sin(t * 12 + i * .9) * k * strong * (i / n) * 2); rect(g, x + dir * i * 2 * k, yy, 2 * k, k, i % 2 ? '#E2445C' : '#C83650'); }
}
function bike(g, x, y, T, s = 1) {
  const sp = T * 18, X = v => x + R(v * s), Y = v => y - R(v * s), fr = (a, b, c, d) => { line(g, X(a), Y(b), X(c), Y(d), '#E2445C'); line(g, X(a), Y(b) + 1, X(c), Y(d) + 1, '#E2445C'); };
  for (const wx of [-19, 19]) {
    const r = R(8 * s); ring(g, X(wx), Y(8), r, INK); ring(g, X(wx), Y(8), r - 1, '#3A3A48'); ring(g, X(wx), Y(8), r - 2, INK);
    for (let a = 0; a < 3; a++) { const an = sp + a * Math.PI / 3, q = r - 3; line(g, X(wx) - R(Math.cos(an) * q), Y(8) - R(Math.sin(an) * q), X(wx) + R(Math.cos(an) * q), Y(8) + R(Math.sin(an) * q), '#9A9AB0'); }
  }
  fr(-19, 8, -2, 8); fr(-2, 8, 8, 20); fr(-19, 8, -6, 20); fr(-6, 20, 8, 20); fr(8, 20, 19, 8); fr(12, 26, 8, 20); rect(g, X(10), Y(27), R(6 * s), 2, INK);
  rect(g, X(-9), Y(22), R(7 * s), 2, INK); rect(g, X(14), Y(24), R(8 * s), R(6 * s), '#C89A60'); rect(g, X(14), Y(24), R(8 * s), 1, INK);
}
// the four characters of a sung line, broken into pixels and blown away (read from the user's .lrc at render time)
let _windPix = null;
function windPixels(g, text) {
  if (_windPix && _windPix.text === text) return _windPix.px;
  const c = document.createElement('canvas'); c.width = PW; c.height = PH; const q = c.getContext('2d');
  const n = [...text].length;
  [...text].forEach((ch, i) => ptext(q, ch, R(240 + (i - (n - 1) / 2) * 84), 128, { size: 48, col: '#FFFFFF' }));
  const d = q.getImageData(0, 0, PW, PH).data, px = [];
  for (let y = 0; y < PH; y++) for (let x = 0; x < PW; x++) if (d[(y * PW + x) * 4 + 3] > 128) px.push([x, y]);
  _windPix = { text, px }; void g; return px;
}
function lyricAt(t) { if (typeof USER_LYRICS === 'undefined') return ''; let s = ''; for (const L of USER_LYRICS) if (L.t <= t + .05) s = L.text; return s; }

// ---------------------------------------------------------------- shots
const SCENES = {
  title(g, t, s) {
    const u = local(t, s);
    street(g, t, 0, 0, { dark: .45 });
    const wx = lerp(-24, 318, eio(seg(u, 10.5, 19.8))), walking = u > 10.5 && u < 19.8;
    const P = person(g, 'me', wx, 238, 2, { walk: walking ? beatPos(t) / 2 : null, aR: 'umb', look: 1 }, t);
    if (P) umbrellaIn(g, P.R, '#E2445C', '#A82C46', 38, 22);
    rainFor(g, t, 0, 150);
    const chars = [...'我不难过'], ty = seg(u, 3, 5) * (1 - seg(u, 13, 14.2)), shown = Math.ceil(ty * 4);
    if (shown > 0) ptext(g, chars.slice(0, shown).join(''), 240, 84, { size: 48, col: '#F4F0FF', outline: INK, shadow: '#5A4A8A' });
    if (u > 6 && u < 13.4) ptext(g, '孙燕姿 · 像素 MV', 240, 108, { col: '#C8D0F0', outline: INK });
    blackout(g, 1 - seg(u, .3, 3));
  },
  door(g, t, s) {
    const u = local(t, s), M = MOODS[0];
    grad(g, M.sky, 0, 200);
    rect(g, 0, 190, 200, 80, '#1E2238'); lamp(g, 50, 200, 90, 1, M.glow);
    rect(g, 196, 0, PW, 236, M.wall); for (let y = 6; y < 236; y += 7) rect(g, 196, y, PW, 1, M.wallLn); rect(g, 193, 0, 3, 236, INK);
    const open = eio(seg(u, 2.0, 2.6)), dx = 300, dw = 84;
    rect(g, dx - 4, 54, dw + 8, 186, INK); rect(g, dx, 58, dw, 182, '#FFD890'); checker(g, dx, 58, dw, 182, '#FFF2C8', .35);
    if (open > .1) person(g, 'you', dx + 44, 240, 3, { eyes: u > 2.8 ? 'down' : 'open', mouth: 'none', look: -1, alpha: seg(u, 2.1, 2.5) }, t);
    const pw = R(dw * (1 - open * .82));
    rect(g, dx, 58, pw, 182, '#6A4232'); rect(g, dx + 8, 70, Math.max(0, pw - 16), 60, '#5A3428'); rect(g, dx + 8, 140, Math.max(0, pw - 16), 86, '#5A3428');
    if (pw > 20) { rect(g, dx + pw - 12, 150, 4, 4, '#E8C060'); rect(g, dx + 30, 88, Math.min(24, pw - 36), 20, '#FFD890'); }
    rect(g, dx + 34, 34, 16, 12, INK); rect(g, dx + 36, 36, 12, 8, '#FFF2C0'); halo(g, dx + 42, 40, 34, '#FFE9A8');
    rect(g, 196, 236, PW, 34, '#3A3048');
    if (open > 0) for (let j = 0; j < 30; j++) checker(g, dx - j * 2, 240 + j, dw + j * 4, 1, '#FFD890', .35 * open);
    const knock = u > .4 && u < 1.9 && (Math.floor((u - .4) / .32) % 2 === 0);
    person(g, 'me', 236, 244, 3, { look: 1, aR: knock ? 'out' : 'down', eyes: u > 2.4 ? 'wide' : 'open' }, t);
    if (knock) for (let i = 0; i < 3; i++) rect(g, dx - 8 - i * 2, 160 + i * 8 - 8, 5, 1, '#FFFFFF');
    // her closed umbrella leans on the wall
    for (let j = 0; j < 60; j++) { const w = R(1 + j / 60 * 4); rect(g, 206 - w - 1 - R(j * .15), 236 - 60 + j - 1, w * 2 + 2, 2, INK); }
    for (let j = 0; j < 60; j++) { const w = R(1 + j / 60 * 4); rect(g, 206 - w - R(j * .15), 236 - 60 + j, w * 2, 1, j % 12 < 2 ? '#A82C46' : '#E2445C'); }
    rect(g, 206, 168, 1, 8, INK); rect(g, 207, 166, 3, 1, INK); rect(g, 210, 167, 1, 3, INK);
    g.save(); g.beginPath(); g.rect(0, 0, 193, PH); g.clip(); rain(g, t, 80, M.rain); g.restore();
  },
  silence(g, t, s) {
    const u = local(t, s);
    backdrop(g, t, 0);
    person(g, 'you', 366, 240, 4, { eyes: 'down', mouth: 'flat', look: -1 }, t);
    person(g, 'me', 190, 240, 4, { eyes: 'down', mouth: 'flat', look: 1, aR: 'behind', aL: 'behind' }, t);
    const dt = (a) => Math.min(3, Math.floor(Math.max(0, u - a) / .3));
    if (u > .3) { bubble(g, 150, 70, 56, 24, 190, 112); dots(g, 162, 82, dt(.3), INK, 3); }
    if (u > 1.5) { bubble(g, 330, 62, 56, 24, 360, 104); dots(g, 342, 74, dt(1.5), INK, 3); }
  },
  wait(g, t, s) {
    const u = local(t, s), p = u / (s.t1 - s.t0);
    street(g, t, 0, 0, { moon: [R(lerp(40, 440, p)), R(60 - Math.sin(p * Math.PI) * 30)], dark: .2 + p * .9, hisLit: p < .8 ? 1 : 0, lamps: 1 });
    const P = person(g, 'me', 152, 238, 2, { look: 1, aR: 'umb', eyes: u > 2.5 ? 'down' : 'open' }, t);
    if (P) umbrellaIn(g, P.R, '#E2445C', '#A82C46', 38, 22);
    rainFor(g, t, 0, 110);
  },
  clock(g, t, s) {
    const u = local(t, s), M = MOODS[0];
    rect(g, 0, 0, PW, PH, M.wall); for (let y = 6; y < 236; y += 7) rect(g, 0, y, PW, 1, M.wallLn);
    rect(g, 300, 30, 110, 206, INK); rect(g, 304, 34, 102, 202, '#6A4232'); rect(g, 314, 48, 82, 70, '#5A3428'); rect(g, 314, 130, 82, 94, '#5A3428');
    rect(g, 0, 236, PW, 34, '#3A3048'); rect(g, 280, 228, 150, 8, '#4A4058');
    const spin = u * 3.2 + u * u * .25, tick = Math.floor(beatPos(t)) * Math.PI / 15;
    halo(g, 150, 118, 92, '#8FA8D8', .5);
    clockFace(g, 150, 118, 72, spin / 12 + 2, spin, tick);
    person(g, 'me', 355, 232, 3, { sit: true, aL: 'hold', aR: 'hold', eyes: 'down', mouth: 'flat' }, t);
    rain(g, t, 40, '#5A6898');
    if (u > 2.6) { bubble(g, 300, 66, 50, 22, 350, 104); dots(g, 311, 77, Math.min(3, Math.floor((u - 2.6) / .3)), INK, 3); }
  },
  tell(g, t, s) {
    const u = local(t, s);
    backdrop(g, t, s.v);
    person(g, 'you', 352, 240, 4, { eyes: 'open', mouth: talk(t), look: -1 }, t);
    person(g, 'me', 132, 330, 6, { back: true, aR: 'behind' }, t);
    const gr = eout(seg(u, .2, .6));
    if (gr > 0) {
      const bw = R(110 * gr), bx = 300 - bw / 2;
      bubble(g, bx, 46, bw, 30, 350, 108);
      if (gr > .9) for (let i = 0; i < 3; i++) for (let x = 0; x < 80; x += 2) rect(g, bx + 15 + x, 54 + i * 6 + R(Math.sin(x * .3 + t * 8 + i) * 1.4), 2, 1, i === 1 ? '#D8849F' : '#8A86A8');
    }
  },
  gentle(g, t, s) {
    const u = local(t, s);
    backdrop(g, t, s.v);
    checker(g, 0, 0, PW, PH, '#000000', .5);
    person(g, 'you', 392, 240, 3, { eyes: 'happy', mouth: 'smile', blush: true, look: -1 }, t);
    dreamBubble(g, t, 210, 118, 270, 170, seg(u, 0, .7));
  },
  hands(g, t, s) { handsClose(g, t, s.v, 0); },
  heart(g, t, s) {
    const u = local(t, s), v = s.v, M = MOODS[v];
    grad(g, [M.dark, M.sky[0], M.sky[1]], 0, PH);
    if (M.rain) rain(g, t, 50, '#3A4A7A');
    const beat = 1 + .04 * kickPulse(t, 5);
    halo(g, 240, 120, 110, '#FF9AB0', .5);
    bigHeart(g, 240, 112, R(56 * beat), '#D8486A', INK);
    bigHeart(g, 240, 112, R(44 * beat), '#F07A92', '#D8486A', { shine: false });
    person(g, 'her', 240, 146, 2, { eyes: 'happy', mouth: 'smile', blush: true, alpha: seg(u, .3, 1.6), glow: '#FFFFFF' }, t);
    person(g, 'me', 240, 146, 2, { eyes: 'open', mouth: 'flat', alpha: 1 - seg(u, .1, 1.2) }, t);
    const out = seg(u, 1.0, 2.0);
    if (out > 0) person(g, 'me', 92, 238, 2, { eyes: u > 3 ? 'down' : 'sad', mouth: 'flat', look: 1, alpha: out }, t);
  },
  understand(g, t, s) {
    const u = local(t, s), v = s.v;
    room(g, t, v, windowSky(v, t), { day: [12, 26, 3][v], plant: [3, 5, 7][v] });
    const nod = [2.0, 4.6].some(a => u > a && u < a + .45) ? 3 : 0;
    const P = person(g, 'me', 150, 200, 3, { sit: true, aL: 'hold', aR: 'hold', eyes: nod ? 'closed' : u > 3 ? 'down' : 'sad', mouth: u > 3.2 ? 'smile' : 'flat', dy: nod }, t);
    if (P) polaroid(g, P.R[0] - 1, P.R[1] - 6, 1, t, 1, MOODS[v].sky[2]);
    if (v === 0) rain(g, t, 0);
  },
  notthere(g, t, s) {
    const u = local(t, s), v = s.v, M = MOODS[v];
    rect(g, 0, 0, PW, PH, M.dark);
    for (let y = 0; y < 236; y++) { const w = R(20 + y * .45); checker(g, 230 - w, y, w * 2, 1, '#FFF2D0', .16); }
    for (let j = 0; j < 14; j++) { const w = R(Math.sqrt(1 - Math.pow(j / 14, 2)) * 120); checker(g, 230 - w, 232 + j - 7, w * 2, 1, '#FFF2D0', .3); }
    for (let i = 0; i < 20; i++) rect(g, R(170 + H(i) * 120 + Math.sin(t + i) * 4), R((H(i + 3) * 230 - t * 6 * (1 + H(i))) % 230 + 230) % 230, 1, 1, '#FFF2D0');
    person(g, 'me', 210, 238, 3, { eyes: 'down', mouth: 'flat', aL: 'behind', aR: 'behind', look: 1 }, t);
    const ghost = .3 * (v ? 1 - seg(u, 1, (s.t1 - s.t0) - .5) : 1);
    person(g, 'you', 290, 238, 3, { tint: '#3A4470', tintDk: '#6A78B0', alpha: ghost }, t);
  },
  lonely(g, t, s) {
    const u = local(t, s), v = s.v, M = MOODS[v], d = s.t1 - s.t0;
    // left: him alone in his room, the phone the only light
    g.save(); g.beginPath(); g.rect(0, 0, 238, PH); g.clip();
    rect(g, 0, 0, 238, PH, '#1A1E36'); for (let x = 0; x < 238; x += 14) rect(g, x, 0, 1, 210, '#161A30');
    gradRect(g, M.sky, 40, 40, 90, 80); moon(g, 108, 64, 8); rect(g, 38, 38, 94, 2, INK); rect(g, 38, 120, 94, 2, INK); rect(g, 38, 38, 2, 84, INK); rect(g, 130, 38, 2, 84, INK); rect(g, 84, 38, 2, 84, INK);
    rect(g, 0, 210, 238, 60, '#2A2438'); rect(g, 20, 196, 150, 18, '#4A4A6A'); rect(g, 20, 192, 150, 4, '#8A8AAA');
    const phoneOn = u < d - .7;
    const P = person(g, 'you', 104, 222, 3, { sit: true, aR: 'phone', eyes: 'down', mouth: 'flat' }, t);
    if (P) { if (phoneOn) halo(g, P.R[0], P.R[1] - 4, 26, '#8FC8FF'); rect(g, P.R[0] - 3, P.R[1] - 8, 7, 11, INK); rect(g, P.R[0] - 2, P.R[1] - 7, 5, 9, phoneOn ? '#BFE6FF' : '#2A2A3A'); }
    if (u > .6 && u < d - 1.2) { bubble(g, 120, 140, 34, 16, 116, 170); dots(g, 126, 147, 1 + Math.floor(u * 3) % 3, '#8A86A8', 2); }
    g.restore();
    // right: her, far away, working late with her back to us
    g.save(); g.beginPath(); g.rect(242, 0, 238, PH); g.clip();
    rect(g, 242, 0, 238, PH, '#2A2A40'); for (let x = 242; x < PW; x += 14) rect(g, x, 0, 1, 210, '#24243A');
    rect(g, 242, 210, 238, 60, '#3A3040');
    halo(g, 400, 150, 50, '#FFD890', .9);
    rect(g, 300, 176, 160, 6, '#8A5A3A'); rect(g, 306, 182, 5, 30, '#6A4228'); rect(g, 448, 182, 5, 30, '#6A4228');
    rect(g, 420, 146, 3, 30, '#3E3A48'); rect(g, 410, 136, 22, 10, INK); rect(g, 411, 137, 20, 8, '#FFE09A');
    for (let i = 0; i < 4; i++) rect(g, 316, 168 - i * 6, 28, 5, ['#D8344C', '#3A78D0', '#F2C14E', '#7DBE7A'][i]);
    clockFace(g, 300, 70, 22, Math.PI * 2 * (1 + u / 40), Math.PI * 2 * u / 4, null);
    person(g, 'me', 380, 232, 3, { back: true, sit: true }, t);
    g.restore();
    rect(g, 238, 0, 4, PH, INK);
  },
  dontlook(g, t, s) {
    const u = local(t, s), v = s.v, turned = u > .6;
    backdrop(g, t, v);
    person(g, 'you', 176, 240, 4, { eyes: 'sad', mouth: s.bubbleAt && u > s.bubbleAt ? talk(t) : 'flat', look: 1, aR: u > 1 ? 'reach' : 'down' }, t);
    person(g, 'me', 318, 240, 4, turned ? { back: true } : { eyes: 'sad', mouth: 'flat', look: -1 }, t);
    if (s.bubbleAt && u > s.bubbleAt) { bubble(g, 132, 52, 70, 40, 178, 112); heart(g, 167, 72, 3, '#FF5C8A'); }
    if (v === 0) rainFor(g, t, 0, 30, { splash: false });
  },
  loved(g, t, s) {
    const u = local(t, s), v = s.v;
    if (s.full) {
      backdrop(g, t, v);
      person(g, 'you', 176, 240, 4, { eyes: 'sad', mouth: talk(t), look: 1 }, t);
      person(g, 'me', 318, 240, 4, { eyes: u > 2.2 ? 'closed' : 'sad', mouth: u > 2.2 ? 'smile' : 'flat', look: -1, aL: u > 2.2 ? 'stop' : 'down' }, t);
      bubble(g, 120, 44, 96, 64, 178, 112);
      heart(g, 168, 77, 6, '#FF5C8A');
      if (u > 1.4) plaster(g, 168, 74, 2);
      return;
    }
    const M = MOODS[v];
    grad(g, [M.dark, M.sky[1], M.sky[2]], 0, PH);
    for (let i = 0; i < 16; i++) if (Math.floor(t * 6 + i) % 3) sparkle(g, R(H(i) * PW), R(H(i + 7) * 220), 1 + (i % 2), '#FFE4EC');
    bubble(g, 150, 34, 180, 160, 240, 210);
    heart(g, 240, 112, 16, '#FF5C8A');
    if (u > .25) plaster(g, 240, 106, 5);
  },
  fine(g, t, s) {
    const u = local(t, s), v = s.v, d = s.t1 - s.t0;
    const cols = [['#FFE27A', '#FFD04A', '#14183A'], ['#FFC8A0', '#FFB088', '#2A1A34'], ['#FFE8C0', '#FFD8A8', '#18244A']][v];
    const crack = seg(u, d - .7, d);
    rays(g, 240, 130, 16, crack > .5 ? mixHex(cols[0], '#8A8AA0', .6) : cols[0], crack > .5 ? mixHex(cols[1], '#6A6A80', .6) : cols[1], t * .3, cols[2], .2 + crack * .6);
    if (v === 0) { g.save(); g.beginPath(); g.rect(0, 0, 70, PH); g.rect(410, 0, 70, PH); g.clip(); rain(g, t, 60, '#7F95C8'); g.restore(); }
    for (let i = 0; i < 14; i++) if (Math.floor(t * 6 + i) % 3) sparkle(g, R(120 + H(i) * 240), R(30 + H(i + 7) * 180), 1 + (i % 2));
    person(g, 'me', 240, 240, 4, { eyes: 'happy', mouth: crack > .5 ? 'smile' : 'grin', blush: true, aR: 'wave', dy: R(Math.sin(t * 8)) }, t);
  },
  tears(g, t, s) {
    const u = local(t, s), v = s.v, M = MOODS[v], d = s.t1 - s.t0;
    grad(g, [M.dark, M.sky[0], M.sky[1]], 0, PH);
    if (M.rain) rain(g, t, 90, '#4A5A8A');
    else for (let i = 0; i < 20; i++) checker(g, R(H(i) * PW) - 8, R(H(i + 2) * PH) - 8, 16, 16, M.glow, .08);
    person(g, 'me', 240, 304, 9, { eyes: u > d * .6 ? 'closed' : 'happy', mouth: u > d * .5 ? 'tremble' : 'smile', blush: true, tears: 2 }, t);
  },
  why(g, t, s) {
    const u = local(t, s), v = s.v, M = MOODS[v];
    grad(g, [M.dark, M.sky[0], M.sky[1]], 0, PH);
    if (M.rain) rain(g, t, 140, '#5A6A9A');
    person(g, 'me', 240, 242, 4, { eyes: 'closed', mouth: 'frown', aR: 'wipe', tears: true }, t);
    [[150, 70, .05], [314, 56, .3], [356, 120, .55], [118, 136, .75]].forEach(([x, y, a], i) => { if (u > a) qmark(g, x, y - R(Math.min(1, (u - a) * 8) * 4), 3 + (i % 2), '#FFFFFF'); });
  },
  leave(g, t, s) {
    const u = local(t, s), v = s.v, d = s.t1 - s.t0, sc = u * 34;
    street(g, t, v, sc, { dark: .55 });
    // he stays at his door, getting left behind
    const hx = 2 * 150 - sc + 20 + 56;
    if (hx > -30) person(g, 'you', hx, 206, 1, { eyes: 'open', look: 1 }, t);
    const P = person(g, 'me', 260, 238, 2, { walk: beatPos(t) / 2, aR: v === 0 ? 'umb' : 'down', look: 1, eyes: u > 2 ? 'closed' : 'open' }, t);
    if (P && v === 0) umbrellaIn(g, P.R, '#E2445C', '#A82C46', 38, 22);
    if (v === 0) rainFor(g, t, 0, R(140 * (1 - .6 * seg(u, 1, d))));
  },
  free(g, t, s) {
    const u = local(t, s), v = s.v, M = MOODS[v], d = s.t1 - s.t0;
    grad(g, M.sky, 0, 200);
    const open = eout(seg(u, .2, 1.8));
    if (v === 0) { stars(g, t, R(120 * open), 170, 3); moon(g, 360, 56, 12); }
    else { sun(g, 360, 160, 20, '#FFE0A0', '#FFB070'); for (let i = 0; i < 6; i++) bird(g, R(200 + u * 60 + i * 18) % 520, R(80 + i * 6 + Math.sin(t * 2 + i) * 3), t + i, '#3A2448'); }
    for (let i = 0; i < 4; i++) { const side = i % 2 ? 1 : -1, cx = 240 + side * (40 + open * 260) + (i > 1 ? side * 60 : 0); cloud(g, R(cx - 40), 30 + i * 24, 2.2, v ? '#C47A92' : '#2E3866', v ? '#9A5A7A' : '#232C56'); }
    disc(g, 240, 460, 250, v ? '#4A3050' : '#1A1E36'); disc(g, 240, 464, 246, v ? '#5A3A5E' : '#232844');
    windLines(g, t, 10, 5, v ? '#FFE0D0' : '#8FA8D8', 40, 200);
    person(g, 'me', 240, 226, 3, { aL: u > .8 ? 'up' : 'umb', aR: u > .8 ? 'up' : 'down', eyes: 'closed', mouth: 'smile' }, t);
    scarfTail(g, 252, 226 - 16 * 3, 3, t, 1, 7, 1.4);
    if (v === 0) { const a = seg(u, .5, d); if (a > 0) { const ux = R(lerp(222, 520, a)), uy = R(lerp(170, -20, a) + Math.sin(a * 12) * 10); umbrella(g, ux, uy, '#E2445C', '#A82C46', 14); rect(g, ux, uy + 7, 1, 20, INK); } }
    if (v === 0 && u < 1.2) rain(g, t, R(120 * (1 - u / 1.2)), M.rain);
  },
  memories(g, t, s) {
    const u = local(t, s), v = s.v, M = MOODS[v];
    grad(g, [M.dark, M.sky[0], M.sky[1]], 0, PH);
    stars(g, t, 60, 200, 21);
    halo(g, 240, 160, 80, M.glow, .6);
    person(g, 'me', 240, 238, 3, { eyes: 'open', mouth: 'smile', look: 0, aL: 'chest', aR: 'chest' }, t);
    const spots = [[110, 70], [370, 64], [70, 160], [410, 160], [170, 30], [310, 28]];
    spots.forEach(([x, y], i) => { const a = u - i * .32; if (a < 0) return; const pop = a < .15 ? 1 : 2; polaroid(g, x + R(Math.sin(t + i) * 4), y + R(Math.cos(t * .8 + i) * 4) - R(a * 4), pop, t, i % 4, ['#7AA0D8', '#F2B48C', '#2A2E62', '#F7B8C8'][i % 4]); });
  },
  shadow(g, t, s) {
    const u = local(t, s), v = s.v, d = s.t1 - s.t0, part = Math.min(2, Math.floor(u / (d / 3))), M = MOODS[v];
    const ghost = { tint: '#4A5A9A', tintDk: '#7A8AC8', alpha: .4 + .1 * Math.sin(t * 3) };
    if (part === 0) {
      rect(g, 0, 0, PW, PH, '#E8D8C0'); for (let x = 0; x < PW; x += 20) rect(g, x, 0, 1, 160, '#DCCAB0');
      gradRect(g, M.sky, 300, 30, 120, 80); rect(g, 298, 28, 124, 2, INK); rect(g, 298, 110, 124, 2, INK); rect(g, 298, 28, 2, 84, INK); rect(g, 420, 28, 2, 84, INK); rect(g, 359, 28, 2, 84, INK);
      rect(g, 0, 160, PW, 16, '#8A5A3A'); rect(g, 0, 176, PW, 94, '#B88A68'); for (let x = 30; x < PW; x += 70) rect(g, x, 186, 50, 60, '#A87A58');
      rect(g, 380, 140, 22, 20, INK); rect(g, 381, 141, 20, 18, '#D8344C'); for (let i = 0; i < 3; i++) rect(g, 388 + i * 3, 128 - R((t * 10 + i * 4) % 10), 1, 4, '#FFFFFF');
      person(g, 'you', 290, 230, 3, ghost, t);
      const P = person(g, 'me', 210, 230, 3, { aR: 'hold', aL: 'hold', eyes: 'down', mouth: 'flat', look: 1 }, t);
      if (P) { rect(g, P.R[0] - 4, P.R[1] - 8, 9, 9, INK); rect(g, P.R[0] - 3, P.R[1] - 7, 7, 7, '#F2EADF'); }
    } else if (part === 1) {
      rect(g, 0, 0, PW, PH, '#3A4A6A');
      g.save(); g.beginPath(); g.rect(40, 40, 400, 110); g.clip(); gradRect(g, M.sky, 40, 40, 400, 110); skyline(g, u * 160, 80, 150, M.far, .3, 44, M.farWin, '#1A1E3A'); g.restore();
      for (let x = 40; x <= 440; x += 100) rect(g, x - 2, 38, 4, 114, INK); rect(g, 38, 38, 404, 3, INK); rect(g, 38, 150, 404, 3, INK);
      rect(g, 0, 190, PW, 80, '#2A3450'); rect(g, 120, 186, 240, 10, '#5A6A9A'); rect(g, 120, 150, 240, 36, '#4A5A8A'); rect(g, 120, 150, 240, 3, '#6A7AAA');
      person(g, 'me', 200, 222, 3, { sit: true, eyes: 'open', look: -1, mouth: 'flat', dy: R(Math.sin(t * 9)) }, t);
      person(g, 'you', 280, 222, 3, { ...ghost, sit: true }, t);
      rect(g, 230, 0, 3, 40, '#8A8AAA'); rect(g, 210, 36, 44, 4, '#8A8AAA');
    } else {
      street(g, t, v, 200 + u * 30, { dark: .4 });
      person(g, 'you', 296, 238, 2, { ...ghost, walk: beatPos(t) / 2 }, t);
      person(g, 'me', 240, 238, 2, { walk: beatPos(t) / 2, eyes: 'open', look: 1, mouth: 'flat' }, t);
      if (v === 0) rain(g, t, 30, M.rain);
    }
  },
  strong(g, t, s) {
    const u = local(t, s), v = s.v, M = MOODS[v], d = s.t1 - s.t0, calm = seg(u, d - 1.6, d - .4), w = 1 - calm;
    grad(g, M.sky, 0, 210);
    if (v === 0) { if (calm > 0) moon(g, 360, 52, 11); } else sun(g, 380, 170, 18, '#FFE0A0', '#FFB070');
    for (let i = 0; i < 6; i++) cloud(g, R(((i * 120 - t * 120 * w - t * 10) % 720 + 720) % 720) - 120, 20 + i * 18, 1.6, v ? '#B86A8A' : '#2A3462', v ? '#9A5A7A' : '#202A54');
    disc(g, 240, 470, 260, v ? '#4A3050' : '#1A1E36'); disc(g, 240, 474, 256, v ? '#5A3A5E' : '#262C4A');
    if (calm > 0) halo(g, 240, 170, 60, M.glow, calm);
    if (w > .05) { windLines(g, t, R(26 * w), 7, v ? '#FFE0D0' : '#9FB0E0', 20, 230); petals(g, t * (1 + 3 * w), R(40 * w), v ? ['#FFB0C8', '#F2A0A0'] : ['#6A8A5A', '#8AA06A'], 9, 8 * w); }
    if (v === 0 && w > .05) rain(g, t, R(150 * w), M.rain, PH, 3, -1.2);
    person(g, 'me', 240, 232, 3, { eyes: 'open', mouth: 'flat', look: 0 }, t);
    scarfTail(g, 252, 232 - 16 * 3, 3, t, 1, 8, 1.6 * w + .3);
  },
  alone(g, t, s) {
    const u = local(t, s), v = s.v, M = MOODS[v];
    grad(g, [M.dark, M.sky[0], M.sky[1]], 0, 240);
    stars(g, t, 220, 220, 31);
    const a = seg(u, .2, 1.0); if (a > 0 && a < 1) for (let j = 0; j < 16; j++) rect(g, R(340 - a * 160 + j * 2), R(40 + a * 50 - j * .5), 2, 1, j < 3 ? '#FFFFFF' : '#9FB0E0');
    disc(g, 380, 520, 290, v ? '#2A1A30' : '#0E1024');
    person(g, 'me', 356, 236, 1, { sit: true, eyes: 'open' }, t);
  },
  lantern(g, t, s) {
    const u = local(t, s), v = s.v, M = MOODS[v], rel = s.release ?? 2.6;
    grad(g, v ? ['#1E1438', '#5A3466', '#C8708A'] : M.sky, 0, 220);
    stars(g, t, v ? 60 : 110, 180, 41);
    disc(g, 240, 470, 250, v ? '#2A1A30' : '#141830'); disc(g, 240, 474, 246, v ? '#3A2440' : '#1C2038');
    const up = u > rel, a = Math.max(0, u - rel);
    const P = person(g, 'me', 240, 232, 3, { aL: up ? 'up' : 'hold', aR: up ? 'up' : 'hold', eyes: up ? 'open' : 'closed', mouth: 'smile', blush: !up }, t);
    if (!P) return;
    // the lantern rises from her hands to become one more star
    const fly = (s.t1 - s.t0) - rel, q = eio(clamp(a / fly)), x0 = P.R[0], y0 = P.R[1] - 4;
    const lx = up ? R(lerp(x0, 300, q) + Math.sin(a * 1.6) * 10 * Math.min(1, a)) : x0, ly = up ? R(lerp(y0 - 30, 34, q)) : y0;
    const k = q > .55 ? 1 : 2;
    if (q < .9) { halo(g, lx, ly, k * 11, '#FFC870', .9); heart(g, lx, ly, k, '#FF9A50', '#FFE8B0'); }
    else { halo(g, lx, ly, 8, '#FFE8B0', .7); sparkle(g, lx, ly, 2 + (Math.floor(t * 4) % 2), '#FFE8B0'); }
  },
  interlude(g, t, s) {
    const u = local(t, s);
    // days pass at her window: the sky steps through night, dawn, day and dusk
    const SKY = [['#0A0E26', '#161C44', '#26305E'], ['#1A2856', '#4E6CA8', '#E8B4A0'], ['#3E8EDE', '#79B8F0', '#CDE8FA'], ['#2A2050', '#8E4E86', '#F09A78']];
    const step = Math.floor(u / 1.9), k0 = step % 4, f = (u % 1.9) / 1.9;
    const sky = u < 9.4 ? skyMix(SKY[k0], SKY[(k0 + 1) % 4], seg(f, .6, 1), 4) : SKY[3];
    const raining = u < 1.9;
    room(g, t, 1, (q, x, y, w, h) => {
      gradRect(q, sky, x, y, w, h, y, y + h);
      skyline(q, 30, y + h - 60, y + h, '#2A2440', .2, 21, '#FFD8A0', '#1E1A30', 30);
      if (raining) for (let i = 0; i < 26; i++) { const sx = x + R(H(i * 3) * w), sy = y + R(((t * (8 + 6 * H(i)) + H(i + 5) * h) % h)); rect(q, sx, sy, 1, 5, '#8FA8D8'); }
    }, { day: 12 + Math.min(step, 5) * 2, plant: 3 + Math.min(step, 5), lampOn: k0 === 0 || k0 === 3 || u > 9.4 ? 1 : 0 });
    const look = u > 9.4;
    const P = person(g, 'me', 150, 200, 3, { sit: true, aL: 'hold', aR: 'hold', look: look ? 0 : -1, eyes: look ? 'down' : 'open', mouth: u > 11 ? 'smile' : 'flat' }, t);
    if (!P) return;
    // then we fall into the photo in her hands
    const z = seg(u, 11.4, 14.6), kz = Math.max(1, Math.floor(Math.pow(z, 1.6) * 26) + 1);
    if (z <= 0) polaroid(g, P.R[0] - 1, P.R[1] - 6, 1, t, 1, '#F09A78');
    else { const cx = R(lerp(P.R[0], 240, eio(z))), cy = R(lerp(P.R[1] - 6, 135, eio(z))); if (kz > 1) checker(g, 0, 0, PW, PH, '#000000', Math.min(.75, z)); polaroid(g, cx, cy, kz, t, 1, '#F09A78'); }
    whiteout(g, seg(u, 14.6, 15.3));
  },
  hug(g, t, s) {
    const u = local(t, s);
    grad(g, ['#C8705A', '#F4B870', '#FCE0A8'], 0, PH);
    for (let i = 0; i < 16; i++) bokeh(g, H(i) * PW, H(i + 1) * 200, 8 + H(i + 3) * 16, '#FFF0C8', .2);
    snow(g, t, 50, 4, '#FFF0C8');
    const close = eio(seg(u, 1.6, 2.2)), gap = R(lerp(38, 30, close));
    const yx = 240 + gap / 2 + 4, mx = 240 - gap / 2 - 4;
    person(g, 'you', yx, 240, 4, { eyes: 'closed', mouth: 'smile', look: -1, flip: true }, t);
    person(g, 'me', mx, 240, 4, { eyes: 'closed', mouth: 'smile', blush: true, aR: 'hug', look: 1 }, t);
    rect(g, yx - 7 * 4 - 2, 240 - 14 * 4 - 2, (yx - mx) - 8 + 4, 2 * 4 + 4, INK); rect(g, yx - 7 * 4, 240 - 14 * 4, (yx - mx) - 8, 2 * 4, '#3D5D9E');
    rect(g, mx - 5 * 4 - 2, 240 - 14 * 4 - 2, 12, 8 + 4, INK); rect(g, mx - 5 * 4, 240 - 14 * 4, 8, 8, '#F0CBAE');
    for (let i = 0; i < 6; i++) { const p = (t * .5 + i / 6) % 1; heart(g, R(240 + Math.sin(i * 2 + t) * 60), R(140 - p * 120), 1 + (close > .5 && i % 2 ? 1 : 0), '#FF7FA0', null); }
  },
  touched(g, t, s) {
    const u = local(t, s);
    grad(g, ['#7A3A4A', '#C8705A', '#F4B870'], 0, PH);
    const pulse = 1 + .08 * Math.sin(u * 9);
    halo(g, 240, 128, R(110 * pulse), '#FFF0C8');
    bigHeart(g, 240, 120, R(36 * pulse), '#FFB0A0', '#FF7A7A');
    for (let i = 0; i < 18; i++) { const a = i / 18 * Math.PI * 2, r = 50 + ((u * 60 + i * 13) % 90); sparkle(g, R(240 + Math.cos(a) * r), R(124 + Math.sin(a) * r * .7), 1 + (i % 2), '#FFF8E0'); }
  },
  chest(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0;
    grad(g, [mixHex('#7A3A4A', '#2A2050', qz(u / d, 4)), mixHex('#C8705A', '#5A3466', qz(u / d, 4)), mixHex('#F4B870', '#B06A8A', qz(u / d, 4))], 0, PH);
    snow(g, t, 30, 8, '#FFE8C8');
    const P = person(g, 'me', 240, 300, 6, { aL: 'chest', aR: 'chest', eyes: 'closed', mouth: 'smile', blush: true }, t);
    if (P) { const sh = 1 - seg(u, .8, d - .3); halo(g, P.R[0], P.R[1], R(20 + 30 * sh), '#FFE8B0'); if (sh > .3) heart(g, P.R[0], P.R[1] + 2, 2, '#FF7A7A', '#FFE8B0'); else heart(g, P.R[0], P.R[1] + 2, 1, '#FF7A7A', null); }
  },
  notyourfault(g, t, s) {
    const u = local(t, s);
    grad(g, ['#2A2050', '#5A3466', '#B06A8A'], 0, 200);
    stars(g, t, 40, 120, 51);
    rect(g, 0, 196, PW, 74, '#3A2840'); rect(g, 0, 196, PW, 2, '#5A4060');
    person(g, 'you', 196, 240, 4, { eyes: 'down', mouth: 'frown', look: 1 }, t);
    const shake = u > .3 && u < 2.4 ? (Math.floor(u * 5) % 2 ? 1 : -1) : -1;
    person(g, 'me', 300, 240, 4, { eyes: 'closed', mouth: 'smile', look: shake, aL: u > 2.4 ? 'reach' : 'down' }, t);
  },
  roadend(g, t, s) {
    grad(g, ['#3A2A5E', '#C8708A', '#FFB070'], 0, 150);
    sun(g, 300, 150, 22, '#FFE0A0', '#FFB070');
    rect(g, 0, 148, PW, 122, '#5A4A8A'); for (let y = 150; y < 270; y += 4) for (let x = 0; x < PW; x += 18) if (H(x * 3 + y + Math.floor(t * 3)) > .65) rect(g, x, y, 6, 1, y < 180 ? '#FFC8A0' : '#7A6AA8');
    rect(g, 290, 150, 20, 80, '#FFD8A0'); checker(g, 280, 150, 40, 100, '#FFD8A0', .3);
    for (let y = 0; y < 90; y++) { const w = R(30 + y * 2.2); rect(g, 0, 180 + y, 140 + y * 1.6, 1, '#3A2A40'); rect(g, 60 - w / 4, 180 + y, w, 1, '#5A5068'); }
    rect(g, 116, 170, 3, 16, '#E8E8F0'); rect(g, 104, 160, 28, 12, INK); rect(g, 105, 161, 26, 10, '#D8344C'); rect(g, 109, 165, 18, 2, '#FFFFFF');
    person(g, 'me', 86, 186, 1, { back: true }, t); person(g, 'you', 98, 186, 1, { back: true }, t);
  },
  wind(g, t, s) {
    const u = local(t, s);
    grad(g, ['#4A78C0', '#9AC0E8', '#FCE8C8'], 0, PH);
    for (let i = 0; i < 4; i++) cloud(g, R(((i * 150 - t * 60) % 660 + 660) % 660) - 90, 30 + i * 20, 1.5);
    rect(g, 0, 220, PW, 50, '#7DB86A'); for (let x = 0; x < PW; x += 5) rect(g, x + R(Math.sin(t * 6 + x) * 2), 214 + (x % 3), 1, 6, '#5A9A4A');
    const text = [...(lyricAt(t) || '？！？！')].slice(0, 4).join('');
    const px = windPixels(g, text);
    const dtOf = i => u - .5 - (px[i][0] / PW) * .7 - H(i) * .2;
    g.fillStyle = INK;
    for (let i = 0; i < px.length; i++) if (dtOf(i) <= 0) g.fillRect(px[i][0] + 2, px[i][1] + 2, 1, 1);
    for (let i = 0; i < px.length; i++) {
      const [x, y] = px[i], dt = dtOf(i);
      if (dt <= 0) { rect(g, x, y, 1, 1, '#FFFFFF'); continue; }
      if (H(i * 3) < dt * .5) continue;
      const nx = x + dt * dt * 200 + dt * 50, ny = y - dt * 26 + Math.sin(dt * 5 + y * .2) * 8 * dt;
      if (nx < PW) rect(g, nx, ny, 1 + (H(i) > .8 ? 1 : 0), 1, H(i + 1) > .7 ? '#FFE0E8' : '#FFFFFF');
    }
    petals(g, t * 2, 40, ['#FF9AB0', '#FFFFFF', '#FFD860'], 11, 8);
    windLines(g, t, 12, 3);
  },
  happy(g, t, s) {
    const u = local(t, s);
    grad(g, ['#3E8EDE', '#79B8F0', '#CDE8FA'], 0, 180);
    sun(g, 400, 54, 22);
    for (let i = 0; i < 4; i++) cloud(g, R(((t * 8 + i * 160) % 660) - 100), 30 + i * 14, 1 + (i % 2) * .5);
    const sc = u * 120;
    rect(g, 0, 160, PW, 30, '#7DB86A'); for (let i = -1; i < 8; i++) disc(g, R(i * 80 - (sc * .4) % 80), 166, 24, '#6CA85A');
    rect(g, 0, 186, PW, 84, '#9ACD5A');
    for (let i = 0; i < 160; i++) { const wx = H(i) * 900, x = R(((wx - sc * (1 + (i % 3) * .3)) % 900 + 900) % 900) - 200, y = R(190 + H(i + 4) * 76); rect(g, x, y - 3, 1, 3, '#5A9A4A'); rect(g, x - 1, y - 5, 3, 2, ['#FF8FB0', '#FFFFFF', '#FFD860', '#E2445C'][i % 4]); }
    rect(g, 0, 232, PW, 14, '#D8B878'); rect(g, 0, 232, PW, 1, '#C8A868');
    const by = 244 + (beatPhase(t) < .5 ? -1 : 0);
    bike(g, 230, by, t, 1.4);
    person(g, 'me', 236, by - 22, 2, { sit: true, aL: u > 4 ? 'wave' : 'out', aR: 'out', eyes: 'happy', mouth: 'grin', blush: true }, t);
    scarfTail(g, 222, by - 22 - 30, 2, t, -1, 7, 1.2);
    for (let i = 0; i < 3; i++) bird(g, R(((u * 30 + i * 40) % 520)) - 20, 70 + i * 9 + R(Math.sin(t * 2 + i) * 3), t + i);
    for (let i = 0; i < 4; i++) { const p = (u * .4 + i / 4) % 1; note(g, R(260 + i * 30 + Math.sin(t * 3 + i) * 6), R(170 - p * 90), '#FFFFFF'); }
  },
  shh(g, t, s) {
    const u = local(t, s), hush = u > 1.3;
    backdrop(g, t, 2);
    person(g, 'you', 180, 240, 4, { eyes: hush ? 'wide' : 'sad', mouth: hush ? 'flat' : talk(t), look: 1 }, t);
    person(g, 'me', 306, 240, 4, { eyes: hush ? 'happy' : 'open', mouth: hush ? 'smile' : 'flat', look: -1, aR: hush ? 'shh' : 'down' }, t);
    if (!hush && u > .2) { bubble(g, 136, 62, 60, 24, 180, 112); ptext(g, '……？', 166, 79, { col: INK }); }
    if (hush) for (let i = 0; i < 3; i++) sparkle(g, 344 + i * 8, 100 - i * 6, 1, '#FFFFFF');
  },
  fork(g, t, s) { forkScene(g, t, local(t, s), 'stand'); },
  split(g, t, s) { forkScene(g, t, local(t, s), 'walk'); },
  blessing(g, t, s) {
    const u = local(t, s);
    backdrop(g, t, 2);
    rain(g, t, 40, '#B8C8E8');
    const wx = R(lerp(400, 360, seg(u, 0, 2.2)));
    const P = person(g, 'you', wx + 14, 222, 2, { eyes: 'happy', mouth: 'smile', look: -1, aL: 'umb', flip: true, walk: beatPos(t) / 2 }, t);
    person(g, 'her', wx - 14, 222, 2, { eyes: 'happy', mouth: 'smile', blush: true, look: 1, walk: beatPos(t) / 2 + .5 }, t);
    if (P) umbrellaIn(g, P.L, '#F3A9C2', '#D8849F', 38, 26);
    person(g, 'me', 150, 244, 4, { eyes: u > 1 ? 'happy' : 'open', mouth: 'smile', look: 1, aL: 'behind', aR: 'behind' }, t);
  },
  drag(g, t, s) {
    const u = local(t, s), stop = u > 2.5;
    grad(g, ['#2A3A6A', '#4E6CA8', '#9AB0D8'], 0, PH);
    rect(g, 0, 0, PW, PH, '#4E5E84'); for (let x = 0; x < PW; x += 16) rect(g, x, 0, 1, PH, '#44527A');
    const day = stop ? 1 + Math.floor(2.5 * 9) % 31 : 1 + Math.floor(u * 9) % 31, flip = stop ? 0 : (u * 9) % 1;
    rect(g, 70, 40, 130, 160, INK); rect(g, 72, 42, 126, 156, '#F4F0E8'); rect(g, 72, 42, 126, 30, '#D8344C');
    for (let i = 0; i < 5; i++) rect(g, 84 + i * 24, 34, 4, 14, '#8A8A9A');
    ptext(g, String(day), 135, 160, { size: 60, col: INK });
    if (flip > 0) { const h = R(126 * (1 - flip)); rect(g, 72, 72, 126, h, '#FFFFFF'); rect(g, 72, 72 + h, 126, 2, '#C8C0B8'); }
    const spin = stop ? 2.5 * 7 : u * 7;
    clockFace(g, 340, 110, 62, spin / 6, spin * 2, stop ? null : spin * 4);
    const P = person(g, 'me', 250, 244, 3, { eyes: stop ? 'closed' : 'open', mouth: stop ? 'smile' : 'flat', aR: stop ? 'stop' : 'down', look: 1 }, t);
    if (stop && u < 2.9 && P) for (let i = 0; i < 5; i++) sparkle(g, P.R[0] + 10 + i * 6, P.R[1] - 10 + (i % 2) * 8, 1);
  },
  letgo(g, t, s) {
    const u = local(t, s);
    if (u < 2.4) { handsClose(g, t, 2, seg(u, .5, 2.3)); return; }
    backdrop(g, t, 2);
    const a = u - 2.4, mx = R(lerp(270, 540, seg(a, .3, 2.6)));
    person(g, 'you', 180, 240, 4, { eyes: 'sad', mouth: 'flat', look: 1, aR: 'reach' }, t);
    person(g, 'me', mx, 240, 4, { walk: a > .3 ? beatPos(t) / 2 : null, eyes: 'open', mouth: 'flat', look: 1 }, t);
  },
  forward(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, p = u / d, sc = u * 50;
    const sky = skyMix(['#1A2856', '#4E6CA8', '#E8B4A0'], ['#4A6AB0', '#E89A80', '#FFD8A0'], p, 6);
    grad(g, sky, 0, 190);
    halo(g, 440, 196, R(60 + p * 60), '#FFE0A0', .6 + p * .4);
    stars(g, t, R(30 * (1 - p)), 80, 61);
    for (let i = -1; i < 8; i++) disc(g, R(i * 90 - (sc * .3) % 90), 210, 50, mixHex('#2A3A64', '#5A5A8A', p));
    rect(g, 0, 196, PW, 74, mixHex('#3A4A6A', '#6A6A8A', p));
    for (let i = -1; i < 6; i++) { const x = R(i * 120 - sc % 120); rect(g, x, 150, 3, 70, '#2A2E4A'); rect(g, x - 8, 154, 19, 2, '#2A2E4A'); }
    line(g, 0, 156, PW, 158, '#2A2E4A');
    rect(g, 0, 226, PW, 14, '#8A7A8A'); for (let x = -40; x < PW + 40; x += 40) rect(g, R(x - sc % 40), 232, 18, 2, '#C8B8C0');
    person(g, 'me', 220, 238, 3, { walk: beatPos(t) / 2, eyes: 'open', mouth: u > 2.5 ? 'smile' : 'flat', look: 1 }, t);
    scarfTail(g, 208, 238 - 16 * 3, 3, t, -1, 6, .8);
  },
  release(g, t, s) {
    const u = local(t, s), rise = eout(seg(u, 0, 1.6));
    rays(g, 400, R(lerp(190, 140, rise)), 20, '#FFE8A8', '#FFD488', -t * .2, '#FFB88A', .3);
    halo(g, 400, R(lerp(190, 140, rise)), 70, '#FFFFFF');
    sun(g, 400, R(lerp(190, 140, rise)), 24, '#FFF4C8', '#FFE08A');
    disc(g, 220, 480, 280, '#7A9A5A'); disc(g, 220, 484, 276, '#8AB064');
    const off = u > .7;
    person(g, 'me', 220, 232, 3, { aL: 'up', aR: 'up', eyes: 'closed', mouth: 'grin', blush: true, noScarf: off }, t);
    if (!off) scarfTail(g, 232, 232 - 16 * 3, 3, t, 1, 6, 1);
    else { const a = u - .7, sx = R(232 + a * 90 + a * a * 20), sy = R(184 - a * 50 + Math.sin(a * 4) * 10); scarfTail(g, sx, sy, 3, t, 1, 7, 1.6); }
    for (let i = 0; i < 14; i++) { const a = u - .4 - H(i) * 1.2; if (a < 0) continue; bird(g, R(140 + H(i + 2) * 160 + a * (40 + 30 * H(i))), R(196 - a * (26 + 22 * H(i + 1)) + Math.sin(a * 3 + i) * 3), t + i, '#4A3A5A'); }
    whiteout(g, (1 - seg(u, 0, .5)) * .6);
  },
  end(g, t, s) {
    const u = local(t, s);
    grad(g, ['#79B8F0', '#BFE0F8', '#FFF0D8'], 0, 160);
    sun(g, 400, 60, 18, '#FFF4C8', '#FFE08A');
    for (let i = 0; i < 3; i++) cloud(g, R(((t * 5 + i * 190) % 660) - 100), 40 + i * 16, 1.2);
    rect(g, 0, 156, PW, 114, '#9ACD5A');
    for (let y = 0; y < 114; y++) { const w = R(4 + y * 1.1); rect(g, 240 - w, 156 + y, w * 2, 1, '#E8D8B0'); }
    for (let i = 0; i < 80; i++) { const x = R(H(i) * PW), y = R(162 + H(i + 4) * 100); if (Math.abs(x - 240) > 10 + (y - 156) * 1.2) { rect(g, x, y - 2, 1, 2, '#5A9A4A'); rect(g, x - 1, y - 3, 3, 1, ['#FF8FB0', '#FFFFFF', '#FFD860'][i % 3]); } }
    const p = eio(seg(u, 0, 11)), k = p < .4 ? 3 : p < .75 ? 2 : 1, y = R(lerp(250, 168, p));
    person(g, 'me', 240, y, k, { back: true, walk: beatPos(t) / 2, noScarf: true }, t);
    for (let i = 0; i < 4; i++) bird(g, R(((u * 20 + i * 50) % 520)) - 20, 50 + i * 8, t + i);
    const chars = [...'我不难过'], shown = Math.ceil(seg(u, 2.5, 4.5) * 4);
    if (shown > 0) ptext(g, chars.slice(0, shown).join(''), 240, 96, { size: 48, col: '#FFFFFF', outline: INK, shadow: '#7A90C0' });
    if (u > 5.5) ptext(g, '孙燕姿 · 像素 MV', 240, 120, { col: '#FFFFFF', outline: INK });
    blackout(g, seg(u, 12, 15));
  },
};
// the fork in the road at dawn: they stand where it splits, then walk apart and the red thread snaps
function forkScene(g, t, u, mode) {
  const sky = ['#22346A', '#6A80B8', '#F2C0A0'];
  grad(g, sky, 0, 130);
  halo(g, 240, 132, 70, '#FFE0B0', .7);
  rect(g, 0, 128, PW, 142, '#5A7A5A'); for (let i = 0; i < 6; i++) rect(g, 0, 132 + i * i * 3, PW, 1, '#4E6E4E');
  // two roads from the bottom to the horizon, one to each side
  for (let y = 128; y < PH; y++) {
    const q = (y - 128) / (PH - 128), split = clamp((.62 - q) / .62), w = R(4 + q * 70);
    if (q > .62) rect(g, 240 - w, y, w * 2, 1, '#C8B898');
    else { for (const side of [-1, 1]) { const cx = R(240 + side * split * split * 190), ww = R(3 + q * 60); rect(g, cx - ww, y, ww * 2, 1, '#C8B898'); } }
  }
  rect(g, 238, 150, 3, 60, '#6A4A3A'); rect(g, 206, 152, 32, 10, '#E8D8B8'); rect(g, 202, 155, 4, 4, '#E8D8B8'); rect(g, 241, 166, 32, 10, '#E8D8B8'); rect(g, 273, 169, 4, 4, '#E8D8B8');
  rect(g, 206, 152, 32, 1, INK); rect(g, 241, 166, 32, 1, INK);
  if (mode === 'stand') {
    const turn = u > 1.6;
    const A = person(g, 'you', 214, 240, 2, { eyes: turn ? 'down' : 'open', mouth: 'flat', look: turn ? -1 : 1, aR: 'reach' }, t);
    const B = person(g, 'me', 266, 240, 2, { eyes: turn ? 'down' : 'open', mouth: 'flat', look: turn ? 1 : -1, aL: 'reach' }, t);
    if (A && B) line(g, A.R[0], A.R[1], B.L[0], B.L[1], '#E2445C');
    return;
  }
  const p = eio(seg(u, .2, 3.0)), snap = u > 1.7;
  const yy = R(lerp(240, 170, p)), k = p < .5 ? 2 : 1;
  const A = person(g, 'you', R(lerp(214, 70, p)), yy, k, { walk: beatPos(t) / 2, look: -1, eyes: 'down' }, t);
  const B = person(g, 'me', R(lerp(266, 410, p)), yy, k, { walk: beatPos(t) / 2 + .5, look: 1, eyes: 'open' }, t);
  if (!A || !B) return;
  if (!snap) line(g, A.R[0], A.R[1], B.L[0], B.L[1], '#E2445C');
  else {
    const a = Math.min(1, (u - 1.7) * 3), mxp = (A.R[0] + B.L[0]) / 2, myp = (A.R[1] + B.L[1]) / 2;
    line(g, A.R[0], A.R[1], R(lerp(mxp - 6, A.R[0] + 4, a)), R(myp + 10 * a), '#E2445C');
    line(g, B.L[0], B.L[1], R(lerp(mxp + 6, B.L[0] - 4, a)), R(myp + 10 * a), '#E2445C');
    if (u < 2.1) sparkle(g, mxp, myp, 4, '#FFFFFF');
  }
}

// ---------------------------------------------------------------- one frame
const XF = .3;
const NO_XF = new Set(['tears', 'why', 'touched', 'release']);
const THEME_OF = { hug: 1, touched: 1, chest: 1, notyourfault: 1, roadend: 1, wind: 1, happy: 1, shh: 2, fork: 2, split: 2, blessing: 2, drag: 2, letgo: 2, forward: 2, release: 2, end: 2 };
let bufA = null, bufB = null;
function shotInto(g, i, t) { g.setTransform(1, 0, 0, 1, 0, 0); g.imageSmoothingEnabled = false; SCENES[SHOTS[i].name](g, t, SHOTS[i]); }
function memoryFrame(g) {
  // the second verse is remembered: dark rounded corners like an old photo
  for (let y = 0; y < PH; y++) for (const side of [0, 1]) {
    const dy = Math.min(y, PH - 1 - y); if (dy > 26) continue;
    const w = R(26 - Math.sqrt(Math.max(0, 26 * 26 - (26 - dy) * (26 - dy))));
    if (w > 0) rect(g, side ? PW - w : 0, y, w, 1, '#1A0E1E');
  }
  checker(g, 0, 0, PW, 3, '#1A0E1E', .5); checker(g, 0, PH - 3, PW, 3, '#1A0E1E', .5);
}
function drawFrame(g, t) {
  t = clamp(t, 0, DUR - 1e-4);
  if (!bufA) { bufA = document.createElement('canvas'); bufB = document.createElement('canvas'); bufA.width = bufB.width = PW; bufA.height = bufB.height = PH; }
  const i = shotIndex(t), s = SHOTS[i];
  if (i > 0 && t - s.t0 < XF && !NO_XF.has(s.name)) {
    const a = bufA.getContext('2d'), b = bufB.getContext('2d');
    shotInto(a, i - 1, t); if (SHOTS[i - 1].v === 1 && !THEME_OF[SHOTS[i - 1].name] && SHOTS[i - 1].name !== 'interlude') memoryFrame(a);
    shotInto(b, i, t); if (s.v === 1 && !THEME_OF[s.name] && s.name !== 'interlude') memoryFrame(b);
    ditherMix(g, bufA, bufB, (t - s.t0) / XF);
  } else { shotInto(g, i, t); if (s.v === 1 && !THEME_OF[s.name] && s.name !== 'interlude') memoryFrame(g); }
  subtitle(g, t, SUB_THEMES[THEME_OF[s.name] ?? s.v]);
}
