// scenery.js — reusable background pieces: sky, sun, clouds, the plain, the brick farmhouse, the banyan, rooms,
// the nine-pane window, the city. Static pieces are painted once into cached canvases.

const cache = new Map();
function cached(key, w, h, paint) {
  let c = cache.get(key);
  if (!c) { c = document.createElement('canvas'); c.width = w; c.height = h; const cg = c.getContext('2d'); cg.imageSmoothingEnabled = false; paint(cg, w, h); cache.set(key, c); }
  return c;
}

// ---------------------------------------------------------------- sky things
const SKIES = {
  golden: ['#4C7FC0', '#86B2DC', '#E9D6AE', '#F6BC72', '#F49B5E'],
  day: ['#3A86D0', '#5DA6E2', '#8CC6F0', '#C4E6F8'],
  dusk: ['#2A3266', '#5A4A86', '#B66A84', '#F09A6E', '#F7C47E'],
  night: ['#080C22', '#101A3E', '#1C2A5A', '#2C3C72'],
  dawn: ['#1F2752', '#4A4A80', '#9A6E98', '#E89A84', '#FBD3A0'],
  grey: ['#5C6478', '#76809A', '#9AA2B6'],
};
function sun(g, x, y, r, o = {}) {
  const core = o.core || '#FFF6D6', rim = o.rim || '#FFE19A', halo = o.halo || '#FFD27A';
  for (let k = 3; k >= 1; k--) glow(g, x, y, r + k * 7, halo, .22 + (3 - k) * .1);
  disc(g, x, y, r, rim); disc(g, x - 1, y - 1, r - 2, core);
}
function moon(g, x, y, r, sky) { glow(g, x, y, r + 10, '#C8D4FF', .25); disc(g, x, y, r, '#FFF6D8'); disc(g, x + R(r * .55), y - R(r * .35), R(r * .85), sky); }
function cloud(g, x, y, w, col = '#FFFFFF', shade = '#DCE7F4') {
  x = R(x); y = R(y); const h = Math.max(3, R(w * .22));
  const blobs = [[.18, .55, .2], [.38, .3, .26], [.6, .38, .22], [.8, .6, .16]];
  for (const [bx, by, br] of blobs) disc(g, x + bx * w, y + by * h + 1, R(br * w * .62), shade);
  rect(g, x + R(w * .06), y + h - 1, R(w * .88), 2, shade);
  for (const [bx, by, br] of blobs) disc(g, x + bx * w, y + by * h - 1, R(br * w * .62) - 1, col);
  rect(g, x + R(w * .08), y + h - 3, R(w * .84), 2, col);
}
function streak(g, x, y, w, col) { rect(g, x + 2, y, w - 4, 1, col); rect(g, x, y + 1, w, 1, col); }
// an egret: white, slow wing beats
function egret(g, x, y, t, s = 1) {
  const up = Math.sin(t * 6) > 0; x = R(x); y = R(y);
  rect(g, x - 2, y, 5, 1, '#FFFFFF'); px(g, x + 3, y - 1, '#FFFFFF'); px(g, x + 4, y - 1, '#F2C84A');
  if (up) { rect(g, x - 1, y - 2, 1, 2, '#FFFFFF'); rect(g, x - 2, y - 3, 1, 1, '#FFFFFF'); }
  else { rect(g, x - 1, y + 1, 1, 2, '#E6EBF2'); rect(g, x - 2, y + 3, 1, 1, '#E6EBF2'); }
}

// ---------------------------------------------------------------- the plain
// mountains along the horizon (purple in the evening haze)
function mountains(g, hy, camX, col, col2, seed = 3) {
  const c = cached('mtn' + col + col2 + seed, PW * 2, 40, (cg, w, h) => {
    for (let x = 0; x < w; x++) {
      const a = Math.sin(x * .021 + seed) * 9 + Math.sin(x * .047 + seed * 2) * 5 + Math.sin(x * .11) * 1.5;
      const top = R(h - 14 - a);
      rect(cg, x, top, 1, h - top, col);
      const b = Math.sin(x * .033 + seed * 3) * 6 + Math.sin(x * .09) * 2, top2 = R(h - 6 - b);
      rect(cg, x, top2, 1, h - top2, col2);
    }
  });
  const off = ((R(camX * .1) % (PW * 2)) + PW * 2) % (PW * 2);
  g.drawImage(c, -off, hy - 40); g.drawImage(c, PW * 2 - off, hy - 40);
}
// tree lines and farm hamlets sitting on the horizon
function hamlets(g, hy, camX, dark, mid, roof, seed = 5, wall = '#E8DCC8') {
  const c = cached('ham' + dark + mid + roof + seed + wall, PW * 2, 22, (cg, w, h) => {
    for (let i = 0; i < 26; i++) {
      const x = R(H(i + seed) * w), r = 3 + R(H(i * 3 + seed) * 5);
      disc(cg, x, h - r + 1, r, dark); disc(cg, x - 1, h - r, r - 1, mid);
      if (H(i * 7 + seed) > .55) { const hx = x + r + 2; rect(cg, hx, h - 5, 7, 5, wall); rect(cg, hx - 1, h - 7, 9, 2, roof); if (wall !== '#E8DCC8' && H(i * 13) > .4) rect(cg, hx + 2, h - 4, 2, 2, '#FFD98A'); }
      if (H(i * 11 + seed) > .7) { rect(cg, x + 4, h - 14, 1, 14, dark); disc(cg, x + 4, h - 15, 2, mid); }   // betel palm
    }
  });
  const off = ((R(camX * .25) % (PW * 2)) + PW * 2) % (PW * 2);
  g.drawImage(c, -off, hy - 22); g.drawImage(c, PW * 2 - off, hy - 22);
}
// rice paddies as horizontal bands that get taller towards us; wind runs along them as brighter waves
function paddies(g, t, hy, y1, camX, pal, wind = 1) {
  let y = hy, k = 0;
  while (y < y1) {
    const bh = Math.min(y1 - y, 2 + R(k * 1.6)), par = .3 + k * .12, off = camX * par;
    rect(g, 0, y, PW, bh, k % 2 ? pal.a : pal.b);
    if (bh >= 3) {                                                   // rice texture + wind sheen
      for (let x = 0; x < PW; x++) {
        const wx = x + off, wave = Math.sin(wx * .045 - t * 2.4 * wind + k * .9) + Math.sin(wx * .013 - t * 1.1 * wind);
        if (wave > 1.15 && bayer(x, y + k) < (wave - 1.15) * 1.2) rect(g, x, y, 1, bh - 1, pal.hi);
        const tuft = ((R(wx) % 3) + 3) % 3 === 0;
        if (tuft) px(g, x, y + bh - 2 - (H(R(wx) + k * 99) > .5 ? 1 : 0), pal.lo);
      }
    }
    rect(g, 0, y + bh - 1, PW, 1, pal.ridge);
    y += bh; k++;
  }
}
// telephone poles and sagging wires, walking past at the camera's speed
function poles(g, camX, gy, spacing, col, wire, top = 46) {
  const off = ((R(camX) % spacing) + spacing) % spacing, xs = [];
  for (let x = -off - spacing; x < PW + spacing; x += spacing) xs.push(x);
  for (const x of xs) { rect(g, x, gy - top, 2, top, col); rect(g, x - 4, gy - top + 3, 10, 1, col); rect(g, x - 3, gy - top + 7, 8, 1, col); }
  for (let i = 0; i + 1 < xs.length; i++) for (const dy of [3, 7]) for (let x = xs[i]; x < xs[i + 1]; x++) {
    const u = (x - xs[i]) / spacing; px(g, x, gy - top + dy + R(Math.sin(u * Math.PI) * 4), wire);
  }
}
function grassTufts(g, t, gy, col, col2, seed = 1, wind = 1, camX = 0) {
  for (let i = 0; i < 70; i++) {
    const x = ((R(H(i + seed) * PW * 1.5 - camX) % (PW + 20)) + PW + 20) % (PW + 20) - 10, h = 2 + R(H(i * 5 + seed) * 4);
    const lean = R(Math.sin(t * 2.6 * wind + x * .05) * wind * 1.2);
    for (let j = 0; j < h; j++) px(g, x + R(lean * j / h), gy - j, j > h - 2 ? col2 : col);
  }
}

// ---------------------------------------------------------------- the red-brick farmhouse (三合院, front view)
function farmhouse(g, x, y, s = {}) {
  const c = cached('farm', 150, 64, (cg) => {
    const brick = '#B9573E', brickD = '#97432F', brickL = '#D07757', roofC = '#7E3B2C', roofL = '#A85440', tile = '#5E2C22';
    // wings
    for (const wx of [0, 106]) {
      rect(cg, wx, 30, 44, 34, brick);
      for (let j = 0; j < 34; j += 3) for (let i = (j / 3) % 2 ? 0 : 3; i < 44; i += 6) rect(cg, wx + i, 30 + j, 5, 1, brickL);
      for (let j = 2; j < 34; j += 3) rect(cg, wx, 30 + j, 44, 1, brickD);
      rect(cg, wx - 2, 24, 48, 6, roofC); rect(cg, wx - 2, 24, 48, 1, roofL); for (let i = 0; i < 48; i += 3) rect(cg, wx - 2 + i, 27, 1, 3, tile);
      rect(cg, wx + 14, 40, 14, 12, '#7FB7A8'); rect(cg, wx + 14, 40, 14, 1, '#5B8E82');           // teal window with bars
      for (let i = 2; i < 14; i += 3) rect(cg, wx + 14 + i, 40, 1, 12, '#3D5E58');
    }
    // central hall, taller, with the swallow-tail ridge
    rect(cg, 40, 22, 70, 42, brick);
    for (let j = 0; j < 42; j += 3) for (let i = (j / 3) % 2 ? 0 : 3; i < 70; i += 6) rect(cg, 40 + i, 22 + j, 5, 1, brickL);
    for (let j = 2; j < 42; j += 3) rect(cg, 40, 22 + j, 70, 1, brickD);
    poly(cg, [[34, 22], [116, 22], [110, 12], [40, 12]], roofC); rect(cg, 40, 12, 70, 1, roofL);
    for (let i = 36; i < 114; i += 3) rect(cg, i, 15, 1, 7, tile);
    rect(cg, 42, 9, 66, 3, '#6E3326'); poly(cg, [[42, 9], [36, 3], [38, 3], [46, 9]], '#6E3326'); poly(cg, [[108, 9], [114, 3], [112, 3], [104, 9]], '#6E3326');
    // door with red couplets
    rect(cg, 64, 36, 22, 28, '#5A3A28'); rect(cg, 66, 38, 8, 26, '#7A4E32'); rect(cg, 76, 38, 8, 26, '#7A4E32');
    rect(cg, 59, 36, 3, 20, '#D8423A'); rect(cg, 88, 36, 3, 20, '#D8423A'); rect(cg, 66, 32, 18, 3, '#D8423A');
    rect(cg, 60, 39, 1, 1, '#F7D46A'); rect(cg, 60, 44, 1, 1, '#F7D46A'); rect(cg, 89, 41, 1, 1, '#F7D46A'); rect(cg, 89, 47, 1, 1, '#F7D46A');
    rect(cg, 47, 40, 10, 10, '#7FB7A8'); rect(cg, 93, 40, 10, 10, '#7FB7A8');
    for (const wx of [47, 93]) for (let i = 2; i < 10; i += 3) rect(cg, wx + i, 40, 1, 10, '#3D5E58');
    disc(cg, 61, 30, 2, '#E8423A'); disc(cg, 89, 30, 2, '#E8423A');                                  // lanterns
  });
  g.drawImage(c, R(x), R(y));
}
// the banyan: a huge canopy, aerial roots, leaves trembling in the wind
function banyan(g, x, gy, t, o = {}) {
  const dark = o.dark || '#2F5A32', mid = o.mid || '#3F7A3C', light = o.light || '#6FA04A', hi = o.hi || '#A8C85A', trunk = o.trunk || '#6A4A32';
  const c = cached('banyan' + dark + hi, 140, 110, (cg) => {
    rect(cg, 60, 50, 14, 60, trunk); rect(cg, 60, 50, 3, 60, '#8A6648'); rect(cg, 52, 100, 30, 10, trunk);
    poly(cg, [[60, 64], [40, 52], [44, 50], [62, 60]], trunk); poly(cg, [[72, 60], [96, 48], [98, 52], [74, 66]], trunk);
    for (let i = 0; i < 9; i++) rect(cg, 36 + i * 9 + R(H(i) * 4), 52, 1, 20 + R(H(i * 3) * 30), '#7E5E44');
    const blobs = [[70, 30, 30], [40, 38, 22], [100, 38, 24], [55, 20, 20], [88, 18, 20], [22, 50, 14], [120, 50, 14], [70, 46, 22]];
    for (const [bx, by, r] of blobs) disc(cg, bx, by + 2, r, dark);
    for (const [bx, by, r] of blobs) disc(cg, bx - 2, by - 1, r - 3, mid);
    for (const [bx, by, r] of blobs) disc(cg, bx - 6, by - 6, R(r * .5), light);
    for (let i = 0; i < 160; i++) { const a = H(i) * 6.28, d = H(i * 3) * 46, xx = 70 + Math.cos(a) * d * 1.3, yy = 32 + Math.sin(a) * d * .7; px(cg, xx, yy, H(i * 7) > .5 ? hi : light); }
  });
  g.drawImage(c, R(x) - 70, R(gy) - 110);
  // a few leaves shimmer
  for (let i = 0; i < 18; i++) if (Math.sin(t * 5 + i * 2.1) > .6) px(g, R(x) - 50 + R(H(i * 13) * 100), R(gy) - 100 + R(H(i * 17) * 50), hi);
}

// ---------------------------------------------------------------- rooms
// floor and wall; terrazzo for the old house, planks for the city flat
function room(g, o = {}) {
  const fy = o.floorY || 160;
  grad(g, [o.wall || '#EAD9BC', o.wallD || '#E0CCA8'], 0, 0, PW, fy);
  rect(g, 0, fy - 4, PW, 4, o.base || '#B58E62');
  rect(g, 0, fy, PW, PH - fy, o.floor || '#B9B3A0');
  if (o.terrazzo) for (let i = 0; i < 900; i++) px(g, R(H(i) * PW), fy + R(H(i * 3) * (PH - fy)), ['#8E8878', '#D7D2C2', '#A7A08C', '#7E9A8A'][i % 4]);
  if (o.planks) for (let j = fy; j < PH; j += 6) { rect(g, 0, j, PW, 1, o.plankLine || '#8A6444'); for (let i = (j * 7) % 60; i < PW; i += 60) rect(g, i, j, 1, 6, o.plankLine || '#8A6444'); }
}
// the nine-pane window. o.view(g) paints what is outside (clipped to the glass), o.lit[i] lights pane i (0..1),
// panes are numbered left to right, top to bottom
function nineWindow(g, x, y, pw, ph, o = {}) {
  const fr = o.frame || '#5E9C8C', frD = o.frameD || '#3F6E62', frL = o.frameL || '#86C2B0', b = 3, m = 2;
  const W = pw * 3 + m * 2 + b * 2, Hh = ph * 3 + m * 2 + b * 2;
  x = R(x); y = R(y);
  if (o.view) { g.save(); g.beginPath(); g.rect(x + b, y + b, W - 2 * b, Hh - 2 * b); g.clip(); o.view(g, x + b, y + b, W - 2 * b, Hh - 2 * b); g.restore(); }
  const lit = o.lit || [];
  for (let i = 0; i < 9; i++) {
    const cx = x + b + (i % 3) * (pw + m), cy = y + b + Math.floor(i / 3) * (ph + m), a = clamp(lit[i] || 0);
    if (o.dimCol && a < 1) dith(g, cx, cy, pw, ph, o.dimCol, (1 - a) * (o.dimA ?? .6));
    if (a > 0 && o.litCol) dith(g, cx, cy, pw, ph, o.litCol, a * (o.litA ?? .3));
    if (a > 0 && a < 1) { rect(g, cx, cy, pw, 1, '#FFF8DC'); rect(g, cx, cy + ph - 1, pw, 1, '#FFF8DC'); rect(g, cx, cy, 1, ph, '#FFF8DC'); rect(g, cx + pw - 1, cy, 1, ph, '#FFF8DC'); }
    if (o.glint !== false) for (let k = 0; k < Math.min(pw, ph) / 2; k += 2) { px(g, cx + 3 + k, cy + ph - 4 - k, o.glintCol || '#FFFFFF'); px(g, cx + 7 + k, cy + ph - 4 - k, o.glintCol || '#FFFFFF'); }
  }
  // frame
  rect(g, x, y, W, b, fr); rect(g, x, y + Hh - b, W, b, fr); rect(g, x, y, b, Hh, fr); rect(g, x + W - b, y, b, Hh, fr);
  for (let k = 1; k < 3; k++) { rect(g, x + b + k * pw + (k - 1) * m, y, m, Hh, fr); rect(g, x, y + b + k * ph + (k - 1) * m, W, m, fr); }
  rect(g, x, y, W, 1, frL); rect(g, x, y, 1, Hh, frL); rect(g, x, y + Hh - 1, W, 1, frD); rect(g, x + W - 1, y, 1, Hh, frD);
  if (o.sill !== false) { rect(g, x - 4, y + Hh, W + 8, 3, o.sillCol || frL); rect(g, x - 4, y + Hh + 3, W + 8, 1, frD); }
  return { W, H: Hh };
}
function doorway(g, x, y, w, h, col = '#7A5236', open = 1, inside = null) {
  rect(g, x - 3, y - 3, w + 6, h + 3, col);
  if (inside) { g.save(); g.beginPath(); g.rect(x, y, w, h); g.clip(); inside(g, x, y, w, h); g.restore(); }
  const dw = R(w * (1 - open));
  if (dw > 0) { rect(g, x, y, dw, h, '#A0714A'); rect(g, x + 2, y + 4, dw - 4, h - 8, '#8A603E'); px(g, x + dw - 3, y + h / 2, '#F2D16A'); }
}
// a city of lit windows at night
function city(g, t, hy, camX = 0, o = {}) {
  const c = cached('city' + (o.seed || 1), PW * 2, 110, (cg, w, h) => {
    let x = 0, i = 0;
    while (x < w) {
      const bw = 18 + R(H(i * 3 + 1) * 30), bh = 30 + R(H(i * 5 + 2) * 70), col = ['#1C2246', '#232B55', '#2A3260'][i % 3];
      rect(cg, x, h - bh, bw, bh, col); rect(cg, x, h - bh, bw, 1, '#3A4478');
      for (let yy = h - bh + 4; yy < h - 3; yy += 5) for (let xx = x + 3; xx < x + bw - 3; xx += 4) if (H(xx * 13 + yy * 7) > .45) rect(cg, xx, yy, 2, 2, H(xx + yy) > .3 ? '#FFD98A' : '#9FD0F0');
      x += bw + 1; i++;
    }
  });
  const off = ((R(camX * .3) % (PW * 2)) + PW * 2) % (PW * 2);
  g.drawImage(c, -off, hy - 110); g.drawImage(c, PW * 2 - off, hy - 110);
}

// ---------------------------------------------------------------- weather and light
function rain(g, t, n, col = '#9CB4D8', slant = 1, y1 = PH, speed = 260) {
  for (let i = 0; i < n; i++) {
    const x0 = H(i) * (PW + 60), y = ((H(i * 3) * y1 + t * speed * (.8 + H(i * 7) * .4)) % (y1 + 20)) - 10, x = x0 - (y / 4) * slant;
    line(g, x, y, x - slant, y + 4, col);
  }
}
function fireflies(g, t, n, x0, y0, w, h, seed = 1) {
  for (let i = 0; i < n; i++) {
    const on = Math.sin(t * (1.2 + H(i + seed)) * 2 + i * 3) > .2; if (!on) continue;
    const x = x0 + R((H(i * 3 + seed) * w + Math.sin(t * .6 + i) * 6 + w) % w), y = y0 + R((H(i * 5 + seed) * h + Math.cos(t * .5 + i * 1.3) * 4 + h) % h);
    px(g, x, y, '#F6FF9A'); if (Math.sin(t * 3 + i) > .7) glow(g, x, y, 3, '#D8F06A', .4);
  }
}
