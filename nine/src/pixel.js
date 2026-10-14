// pixel.js — drawing helpers for 九分之九 · 像素 MV. Everything is drawn on a 384×216 canvas with whole-pixel
// rectangles, then scaled up 5× with nearest-neighbour (by CSS in the page, by ffmpeg in the video), so every
// art pixel is a crisp 5×5 block in the 1920×1080 frame. Transparency and fades are Bayer dithers, never alpha.

const PW = 384, PH = 216;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const eout = t => 1 - Math.pow(1 - clamp(t), 3);
const ein = t => Math.pow(clamp(t), 3);
const H = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const R = Math.round;
const BAYER = [0, 8, 2, 10, 12, 4, 14, 6, 3, 11, 1, 9, 15, 7, 13, 5];
const bayer = (x, y) => (BAYER[(y & 3) * 4 + (x & 3)] + .5) / 16;
const hex = s => [parseInt(s.slice(1, 3), 16), parseInt(s.slice(3, 5), 16), parseInt(s.slice(5, 7), 16)];
const toHex = c => '#' + c.map(v => R(clamp(v, 0, 255)).toString(16).padStart(2, '0')).join('');
const mix = (a, b, t) => { const A = hex(a), B = hex(b); return toHex(A.map((v, i) => lerp(v, B[i], clamp(t)))); };
const INK = '#2B1D16';
const PIX_FONT = 'NinePixel';

const canvases = {};
function scratch(name, w = PW, h = PH) {
  let c = canvases[name];
  if (!c || c.width !== w || c.height !== h) { c = canvases[name] = document.createElement('canvas'); c.width = w; c.height = h; }
  const g = c.getContext('2d'); g.imageSmoothingEnabled = false; return c;
}

// ---------------------------------------------------------------- shapes (whole pixels only)
function rect(g, x, y, w, h, col) { if (w <= 0 || h <= 0) return; g.fillStyle = col; g.fillRect(R(x), R(y), R(w), R(h)); }
function px(g, x, y, col) { g.fillStyle = col; g.fillRect(R(x), R(y), 1, 1); }
function disc(g, cx, cy, r, col) {
  g.fillStyle = col; cx = R(cx); cy = R(cy); r = Math.max(0, r);
  for (let y = -Math.floor(r); y <= Math.floor(r); y++) { const w = Math.floor(Math.sqrt(r * r - y * y) + .35); g.fillRect(cx - w, cy + y, w * 2 + 1, 1); }
}
function ellipse(g, cx, cy, rx, ry, col) {
  g.fillStyle = col; cx = R(cx); cy = R(cy);
  for (let y = -Math.floor(ry); y <= Math.floor(ry); y++) { const w = Math.floor(rx * Math.sqrt(Math.max(0, 1 - (y * y) / (ry * ry))) + .35); g.fillRect(cx - w, cy + y, w * 2 + 1, 1); }
}
function line(g, x0, y0, x1, y1, col) {
  g.fillStyle = col; x0 = R(x0); y0 = R(y0); x1 = R(x1); y1 = R(y1);
  const dx = Math.abs(x1 - x0), dy = -Math.abs(y1 - y0), sx = x0 < x1 ? 1 : -1, sy = y0 < y1 ? 1 : -1; let e = dx + dy;
  for (let n = 0; n < 2000; n++) { g.fillRect(x0, y0, 1, 1); if (x0 === x1 && y0 === y1) break; const e2 = 2 * e; if (e2 >= dy) { e += dy; x0 += sx; } if (e2 <= dx) { e += dx; y0 += sy; } }
}
// filled polygon by scanlines (pixel centres), so edges stay hard
function poly(g, pts, col) {
  g.fillStyle = col;
  const ys = pts.map(p => p[1]), y0 = Math.floor(Math.min(...ys)), y1 = Math.ceil(Math.max(...ys));
  for (let y = y0; y <= y1; y++) {
    const yc = y + .5, xs = [];
    for (let i = 0; i < pts.length; i++) {
      const [ax, ay] = pts[i], [bx, by] = pts[(i + 1) % pts.length];
      if ((ay <= yc && by > yc) || (by <= yc && ay > yc)) xs.push(ax + (yc - ay) / (by - ay) * (bx - ax));
    }
    xs.sort((a, b) => a - b);
    for (let i = 0; i + 1 < xs.length; i += 2) { const a = R(xs[i]), b = R(xs[i + 1]); if (b > a) g.fillRect(a, y, b - a, 1); }
  }
}
// a translucent rectangle as an ordered dither (how old consoles did transparency)
function dith(g, x, y, w, h, col, a = .5) {
  if (a <= 0) return; if (a >= 1) return rect(g, x, y, w, h, col);
  g.fillStyle = col; x = R(x); y = R(y); w = R(w); h = R(h);
  for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) if (bayer(x + i, y + j) < a) g.fillRect(x + i, y + j, 1, 1);
}
// dithered disc: a soft light pool or glow, denser in the middle
function glow(g, cx, cy, r, col, a = .5) {
  g.fillStyle = col; cx = R(cx); cy = R(cy);
  for (let y = -R(r); y <= R(r); y++) for (let x = -R(r); x <= R(r); x++) {
    const d = Math.sqrt(x * x + y * y) / r; if (d >= 1) continue;
    if (bayer(cx + x, cy + y) < a * (1 - d) * 1.6) g.fillRect(cx + x, cy + y, 1, 1);
  }
}

// ---------------------------------------------------------------- dithered gradients (cached as ImageData)
const gradCache = new Map();
function gradImage(w, h, stops, dir = 'v') {
  const key = w + 'x' + h + dir + stops.join();
  let img = gradCache.get(key);
  if (!img) {
    img = new ImageData(w, h); const d = img.data, cols = stops.map(hex), n = cols.length - 1;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const tt = clamp((dir === 'v' ? y / Math.max(1, h - 1) : x / Math.max(1, w - 1))) * n, i = Math.min(n - 1, Math.floor(tt)), fr = tt - i;
      const c = fr > bayer(x, y) ? cols[i + 1] : cols[i], o = (y * w + x) * 4; d[o] = c[0]; d[o + 1] = c[1]; d[o + 2] = c[2]; d[o + 3] = 255;
    }
    if (gradCache.size > 400) gradCache.clear();
    gradCache.set(key, img);
  }
  return img;
}
// vertical gradient in a box; putImageData ignores transforms, so x/y are absolute canvas pixels
function grad(g, stops, x = 0, y = 0, w = PW, h = PH, dir = 'v') {
  x = R(x); y = R(y); w = R(w); h = R(h); if (w <= 0 || h <= 0) return;
  const img = gradImage(w, h, stops, dir), sx = Math.max(0, -x), sy = Math.max(0, -y);
  g.putImageData(img, x, y, sx, sy, Math.min(w, PW - x) - sx, Math.min(h, PH - y) - sy);
}

// ---------------------------------------------------------------- whole-frame passes on ImageData
// dithered fade of the whole frame towards a colour (a = 0..1)
function fadeTo(g, col, a) {
  if (a <= 0) return; if (a >= 1) return rect(g, 0, 0, PW, PH, col);
  const img = g.getImageData(0, 0, PW, PH), d = img.data, c = hex(col);
  for (let y = 0; y < PH; y++) for (let x = 0; x < PW; x++) if (bayer(x, y) < a) { const o = (y * PW + x) * 4; d[o] = c[0]; d[o + 1] = c[1]; d[o + 2] = c[2]; }
  g.putImageData(img, 0, 0);
}
// colour grade: pull every pixel towards a tint (memories, dusk, night), keeping the dither crisp
function grade(g, col, a, desat = 0) {
  if (a <= 0 && desat <= 0) return;
  const img = g.getImageData(0, 0, PW, PH), d = img.data, c = hex(col);
  for (let o = 0; o < d.length; o += 4) {
    let r = d[o], gg = d[o + 1], b = d[o + 2];
    if (desat) { const l = .3 * r + .59 * gg + .11 * b; r = lerp(r, l, desat); gg = lerp(gg, l, desat); b = lerp(b, l, desat); }
    d[o] = lerp(r, r * c[0] / 255, a); d[o + 1] = lerp(gg, gg * c[1] / 255, a); d[o + 2] = lerp(b, b * c[2] / 255, a);
  }
  g.putImageData(img, 0, 0);
}
// pixel dissolve between two finished frames
function ditherMix(g, a, b, p, cell = 2) {
  const A = a.getContext('2d').getImageData(0, 0, PW, PH), B = b.getContext('2d').getImageData(0, 0, PW, PH), d = A.data, e = B.data;
  for (let y = 0; y < PH; y++) for (let x = 0; x < PW; x++) if (bayer(Math.floor(x / cell), Math.floor(y / cell)) < p) { const q = (y * PW + x) * 4; d[q] = e[q]; d[q + 1] = e[q + 1]; d[q + 2] = e[q + 2]; }
  g.putImageData(A, 0, 0);
}
// banded light: pixels inside r are pushed towards col in a few hard steps (no dither, so it holds up at 2×)
function lightPool(g, cx, cy, r, col, strength = .5, levels = 3, sy = 1) {
  const x0 = Math.max(0, R(cx - r)), y0 = Math.max(0, R(cy - r * sy)), x1 = Math.min(PW, R(cx + r)), y1 = Math.min(PH, R(cy + r * sy));
  if (x1 <= x0 || y1 <= y0 || strength <= 0) return;
  const img = g.getImageData(x0, y0, x1 - x0, y1 - y0), d = img.data, c = hex(col), w = x1 - x0;
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) {
    const dx = (x - cx) / r, dy = (y - cy) / (r * sy), q = 1 - Math.sqrt(dx * dx + dy * dy); if (q <= 0) continue;
    const k = Math.ceil(q * levels) / levels * strength, o = ((y - y0) * w + (x - x0)) * 4;
    d[o] = lerp(d[o], c[0], k); d[o + 1] = lerp(d[o + 1], c[1], k); d[o + 2] = lerp(d[o + 2], c[2], k);
  }
  g.putImageData(img, x0, y0);
}
// a vignette of dithered dark corners
function vignette(g, col = '#140C10', a = .5) {
  const key = 'vig' + col + a;
  let c = canvases[key];
  if (!c) {
    c = scratch(key); const cg = c.getContext('2d'); cg.fillStyle = col;
    for (let y = 0; y < PH; y++) for (let x = 0; x < PW; x++) {
      const dx = (x - PW / 2) / (PW / 2), dy = (y - PH / 2) / (PH / 2), d = Math.sqrt(dx * dx * .7 + dy * dy * .9);
      if (bayer(x, y) < (d - .72) * 2.2 * a) cg.fillRect(x, y, 1, 1);
    }
  }
  g.drawImage(c, 0, 0);
}

// ---------------------------------------------------------------- pixel text (Nine Pixel, 12 px grid)
// Glyphs are rasterised once into a thresholded canvas (no grey anti-aliasing), with an optional 1 px outline.
const textCache = new Map();
function textSprite(s, size, col, outline, shadow) {
  const key = [s, size, col, outline, shadow].join('|');
  let c = textCache.get(key);
  if (c) return c;
  const m = scratch('textMeasure', 8, 8).getContext('2d'); m.font = `${size}px ${PIX_FONT}`;
  const w = Math.ceil(m.measureText(s).width), h = size + 4, pad = 2;
  const mask = scratch('textMask', w + pad * 2, h + pad * 2), mg = mask.getContext('2d');
  mg.clearRect(0, 0, mask.width, mask.height); mg.font = `${size}px ${PIX_FONT}`; mg.textBaseline = 'alphabetic'; mg.fillStyle = '#fff';
  mg.fillText(s, pad, pad + size - Math.round(size / 12));
  const md = mg.getImageData(0, 0, mask.width, mask.height).data, W = mask.width, Hh = mask.height;
  const on = (x, y) => x >= 0 && y >= 0 && x < W && y < Hh && md[(y * W + x) * 4 + 3] >= 128;
  c = document.createElement('canvas'); c.width = W + 1; c.height = Hh + 1;
  const cg = c.getContext('2d'), out = cg.createImageData(W + 1, Hh + 1), od = out.data;
  const put = (x, y, rgb) => { const o = (y * (W + 1) + x) * 4; od[o] = rgb[0]; od[o + 1] = rgb[1]; od[o + 2] = rgb[2]; od[o + 3] = 255; };
  const fc = hex(col), oc = outline && hex(outline), sc = shadow && hex(shadow);
  for (let y = 0; y < Hh + 1; y++) for (let x = 0; x < W + 1; x++) {
    if (on(x, y)) put(x, y, fc);
    else if (oc && (on(x - 1, y) || on(x + 1, y) || on(x, y - 1) || on(x, y + 1) || on(x - 1, y - 1) || on(x + 1, y + 1) || on(x - 1, y + 1) || on(x + 1, y - 1))) put(x, y, oc);
    else if (sc && on(x - 1, y - 1)) put(x, y, sc);
  }
  cg.putImageData(out, 0, 0);
  c.textW = w; c.pad = pad;
  if (textCache.size > 3000) textCache.clear();
  textCache.set(key, c);
  return c;
}
const textW = (s, size = 12) => { const m = scratch('textMeasure', 8, 8).getContext('2d'); m.font = `${size}px ${PIX_FONT}`; return Math.ceil(m.measureText(s).width); };
// y is the top of the 12 px glyph box
function ptext(g, s, x, y, o = {}) {
  if (!s) return { x, w: 0 };
  const size = o.size || 12, c = textSprite(s, size, o.col || '#FFFFFF', o.outline || null, o.shadow || null);
  let X = o.align === 'left' ? x : o.align === 'right' ? x - c.textW : x - c.textW / 2; X = R(X);
  g.drawImage(c, X - c.pad, R(y) - c.pad);
  return { x: X, w: c.textW };
}

// ---------------------------------------------------------------- small motifs
function sparkle(g, x, y, s, col = '#FFFFFF') { x = R(x); y = R(y); rect(g, x - s, y, 2 * s + 1, 1, col); rect(g, x, y - s, 1, 2 * s + 1, col); }
const PAW = ['.x.x.', 'x...x', '.xxx.', '.xxx.'];
function pawPrint(g, x, y, col, k = 1) { PAW.forEach((r, j) => [...r].forEach((ch, i) => { if (ch === 'x') rect(g, x + i * k, y + j * k, k, k, col); })); }
function heart(g, x, y, col = '#FF6F7F') {
  ['.xx.xx.', 'xxxxxxx', 'xxxxxxx', '.xxxxx.', '..xxx..', '...x...'].forEach((r, j) => [...r].forEach((c, i) => { if (c === 'x') px(g, x + i - 3, y + j - 3, col); }));
  px(g, x - 2, y - 2, '#FFD0D6');
}
function stars(g, t, n, y1, seed = 1, x0 = 0, w = PW) {
  for (let i = 0; i < n; i++) {
    const tw = .5 + .5 * Math.sin(t * (1 + H(i + seed)) * 2 + i * 1.7);
    if (tw < .2) continue;
    const x = x0 + R(H(i * 3 + seed) * w), y = R(H(i * 7 + seed) * y1);
    px(g, x, y, tw > .75 ? '#FFFFFF' : '#A9B6E8');
    if (H(i + 9 + seed) > .93 && tw > .8) sparkle(g, x, y, 1, '#FFFFFF');
  }
}

// ---------------------------------------------------------------- subtitles: the user's .lrc lines
// Each character drops into place one after another; "九分之九" is gold. While the line is sung, a trail of
// paw prints walks along underneath, one step per beat, as if 九九 were following the words.
function subtitleAt(t) {
  if (typeof USER_LYRICS === 'undefined') return null;
  const L = USER_LYRICS;
  for (let i = L.length - 1; i >= 0; i--) {
    if (t >= L[i].t - .15) {
      if (!L[i].text) return null;
      const end = Math.min(L[i + 1] ? L[i + 1].t - .05 : DUR, L[i].t + 7);
      return t <= end ? { text: L[i].text, t0: L[i].t, end } : null;
    }
  }
  return null;
}
function subtitle(g, t) {
  const s = subtitleAt(t); if (!s) return;
  const chars = [...s.text], tw = textW(s.text), x0 = R((PW - tw) / 2), y0 = PH - 27;
  const gold = new Set(); for (let k = s.text.indexOf('九分之九'); k >= 0; k = s.text.indexOf('九分之九', k + 1)) for (let j = 0; j < 4; j++) gold.add(k + j);
  const out = clamp((s.end - t) / .3);
  const wide = c => c.charCodeAt(0) > 0x2e7f ? 12 : 6;
  let x = x0;
  chars.forEach((c, i) => {
    const appear = s.t0 - .15 + i * .045, a = seg(t, appear, appear + .12);
    if (a > 0) {
      const dy = R((1 - eout(a)) * -4);
      const col = gold.has(i) ? '#FFCB45' : '#FFF6E2';
      if (out >= 1 || bayer(x, y0) < out) ptext(g, c, x, y0 + dy, { col, outline: INK, align: 'left' });
    }
    x += wide(c);
  });
  // paw trail: one print per beat from the start of the line to its end
  const steps = Math.max(1, Math.floor((s.end - s.t0) / BEATMAP.beat)), done = Math.floor((t - s.t0) / BEATMAP.beat) + 1;
  const n = clamp(done, 0, steps), span = tw - 4;
  for (let k = 0; k < n; k++) {
    const kx = x0 + 2 + R(span * (k + .5) / steps) - 2, ky = PH - 11 + (k % 2 ? 2 : 0);
    if (out < 1 && bayer(kx, ky) >= out) continue;
    pawPrint(g, kx, ky, k === n - 1 ? '#FFCB45' : '#E8D9B8');
  }
}

// ---------------------------------------------------------------- the dog-tag age label
// A bone-shaped tag that slides in from the left: "九九 · 两个月". Time in this story is counted in dog years.
function boneTag(g, text, t, t0, t1) {
  const a = seg(t, t0, t0 + .5), b = seg(t, t1 - .5, t1); if (a <= 0 || b >= 1) return;
  const w = textW(text) + 10, x = R(8 - (1 - eout(a)) * (w + 30) - ein(b) * (w + 30)), y = 8;
  const bone = (col, o) => {
    disc(g, x + 1, y + 2, 4 + o, col); disc(g, x + 1, y + 11, 4 + o, col); disc(g, x + w - 1, y + 2, 4 + o, col); disc(g, x + w - 1, y + 11, 4 + o, col);
    rect(g, x, y - 1 - o + 1, w, 15 + 2 * o - 2, col);
  };
  bone(INK, 1); bone('#FFF3D6', 0);
  rect(g, x + 2, y + 13, w - 4, 1, '#E3C99A');
  ptext(g, text, x + w / 2, y + 1, { col: '#6B3F22' });
}
