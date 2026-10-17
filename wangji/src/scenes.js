// scenes.js — 给我一个理由忘记 · 铅笔 MV. One function per shot (see timeline.js), drawn in 960×540 units.
// Each shot gets (g, t, s): the canvas, the song time, and its entry in SHOTS (s.t0, s.t1, s.v).

const local = (t, s) => t - s.t0;
const step = t => beatPos(t) / 4;
const INK2 = '#2E2E3C';

// ---------------------------------------------------------------- scenery
function nightSky(g, a = .5, y1 = VH, col = INK2) { wRect(g, -20, -20, VW + 40, y1 + 20, col, { a: a / 2, layers: 2, spread: 8, edge: false }); hatch(g, q => q.rect(0, 0, VW, y1), [0, 0, VW, y1], { a: .16, sp: 7, seed: 3 }); }
function greySky(g, y1 = 300) { hatch(g, q => q.rect(0, 0, VW, y1), [0, 0, VW, y1], { a: .22, sp: 5, seed: 1 }); hatch(g, q => q.rect(0, 0, VW, y1 * .6), [0, 0, VW, y1 * .6], { a: .16, sp: 6, ang: -.6, seed: 2 }); for (let i = 0; i < 6; i++) { const cx = H(i) * VW, cy = 40 + H(i + 3) * (y1 * .5); pencil(g, curvePts([[cx - 90, cy + 20], [cx - 50, cy - 10], [cx, cy - 22], [cx + 60, cy - 8], [cx + 100, cy + 20]], false, 5), { a: .5, seed: i }); } }
function skyline(g, sc, base, o = {}) {
  const st = o.step ?? 74, i0 = Math.floor(sc / st) - 1, seed = o.seed ?? 0;
  for (let i = i0; i < i0 + VW / st + 3; i++) {
    const hgt = (o.hmin ?? 90) + H(i * 7 + seed) * (o.hmax ?? 170), w = st - 8 - H(i + seed) * 16, x = i * st - sc;
    solid(g, rectPts(x, base - hgt, w, hgt), o.fill || PAPER);
    if (o.dark) wRect(g, x, base - hgt, w, hgt, INK2, { a: o.dark, layers: 1, edge: false, seed: i });
    pRect(g, x, base - hgt, w, hgt, { w: 1, seed: i });
    hatch(g, q => q.rect(x + w * .55, base - hgt, w * .45, hgt), [x, base - hgt, x + w, base], { a: .2, sp: 4.5, seed: i });
    for (let wy = base - hgt + 10, r = 0; wy < base - 12; wy += 16, r++) for (let wx = x + 7, c = 0; wx < x + w - 10; wx += 13, c++) {
      const lit = H(i * 31 + r * 7 + c * 3 + seed) < (o.lit ?? 0);
      g.globalAlpha = ALPHA * (lit ? .75 : .2); g.fillStyle = lit ? (H(i + r + c) > .5 ? '#F2C24E' : '#F0A848') : GRAPH; g.fillRect(wx, wy, 6, 8);
    }
    g.globalAlpha = ALPHA;
  }
}
function rainP(g, t, n, o = {}) {
  const sl = o.slant ?? .22, sp = o.sp ?? 560, len = o.len ?? 18;
  g.strokeStyle = o.col || '#4A4A5A'; g.lineWidth = o.w ?? .9; g.lineCap = 'round';
  for (let i = 0; i < n; i++) { const y = (t * sp * (1 + H(i) * .35) + H(i * 7) * (VH + 80)) % (VH + 80) - 40, x = H(i * 3) * (VW + 260) - 130 + (VH - y) * sl; g.globalAlpha = ALPHA * (o.a ?? .45) * (.6 + .4 * H(i + 2)); g.beginPath(); g.moveTo(x, y); g.lineTo(x - sl * len, y + len); g.stroke(); }
  g.globalAlpha = ALPHA;
}
function snowP(g, t, n, o = {}) { for (let i = 0; i < n; i++) { const y = (t * (24 + 18 * H(i)) + H(i * 5) * VH) % VH, x = ((H(i * 3) * VW + Math.sin(t + i) * 14 + t * (o.wind ?? 6)) % VW + VW) % VW, r = 1.5 + H(i + 4) * 2.2; g.globalAlpha = ALPHA * .9; g.fillStyle = '#FFFFFF'; g.beginPath(); g.arc(x, y, r, 0, TAU); g.fill(); g.globalAlpha = ALPHA * .35; g.strokeStyle = GRAPH; g.lineWidth = .6; g.stroke(); } g.globalAlpha = ALPHA; }
function lampP(g, x, base, hgt, on = 1) { pLine(g, x, base, x, base - hgt, { w: 1.6, seed: x }); pencil(g, [[x, base - hgt], [x + 14, base - hgt - 6], [x + 26, base - hgt]], { w: 1.3, seed: x + 1 }); pencil(g, ellPts(x + 26, base - hgt + 4, 6, 4), { closed: true, seed: x + 2 }); if (on) { blot(g, x + 26, base - hgt + 6, 60, '#F2C24E', .4 * on); blot(g, x + 26, base, 80, '#F2C24E', .15 * on); } }
function puddle(g, t, x, y, w, o = {}) { pencil(g, ellPts(x, y, w, w * .16), { closed: true, a: .55, seed: x }); if (o.wash) wEll(g, x, y, w, w * .16, o.wash, { a: .2, edge: false }); for (let k = 0; k < (o.ripples ?? 2); k++) { const p = ((t * .7 + k * .5 + (o.ph || 0)) % 1); pencil(g, ellPts(x + (o.dx || 0), y, w * .5 * p, w * .08 * p), { closed: true, a: .45 * (1 - p), seed: x + k }); } }
function umbrellaP(g, hx, hy, top, r, o = {}) {
  pLine(g, hx, hy + 6, hx, top, { w: 1.2, seed: hx });
  pencil(g, ellPts(hx - 4, hy + 6, 4, 4, 0, Math.PI, 5), { seed: hx + 1 });
  const dome = [...ellPts(hx, top + 6, r, r * .55, Math.PI, TAU, 12)];
  for (let k = 3; k >= 0; k--) dome.push(...ellPts(hx - r + (k + .5) * r / 2, top + 6, r / 4, 5, 0, Math.PI, 4).reverse());
  solid(g, dome); if (o.col) wash(g, dome, o.col, { a: .3, seed: hx });
  pencil(g, dome, { closed: true, w: 1.2, seed: hx + 2 }); for (let k = 1; k < 4; k++) pencil(g, [[hx, top + 6 - r * .55], [hx - r + k * r / 2, top + 6]], { a: .4, w: .8, seed: hx + k });
}
function bench(g, x, y, w = 200) { pLine(g, x - w / 2, y - 40, x + w / 2, y - 40, { w: 1.4 }); pLine(g, x - w / 2, y - 34, x + w / 2, y - 34, { w: 1.2 }); pLine(g, x - w / 2, y - 80, x + w / 2, y - 80, { w: 1.2 }); pLine(g, x - w / 2, y - 70, x + w / 2, y - 70, { w: 1 }); for (const sx of [-w / 2 + 14, w / 2 - 14]) { pLine(g, x + sx, y - 80, x + sx, y, { w: 1.3 }); } hatch(g, q => q.rect(x - w / 2, y - 40, w, 6), [x - w / 2, y - 40, x + w / 2, y - 34], { a: .3, sp: 3 }); }
function heartP(g, cx, cy, s, o = {}) { const pts = heartPts(cx, cy, s, 48); solid(g, pts, o.fill || PAPER); if (o.wash) wash(g, pts, o.wash, { a: o.a ?? .3 }); pencil(g, pts, { closed: true, w: o.w ?? 1.4, col: o.col, seed: o.seed ?? 5 }); return pts; }
function windowFrame(g, x, y, w, h, o = {}) { const t2 = 10; for (const r of [[x - t2, y - t2, w + 2 * t2, t2], [x - t2, y + h, w + 2 * t2, t2], [x - t2, y, t2, h], [x + w, y, t2, h]]) { solid(g, rectPts(...r)); pRect(g, ...r, { w: 1.2 }); hatch(g, q => q.rect(...r), [r[0], r[1], r[0] + r[2], r[1] + r[3]], { a: .22, sp: 3.5 }); } if (o.cross !== false) { pLine(g, x + w / 2, y, x + w / 2, y + h, { w: 2 }); pLine(g, x, y + h / 2, x + w, y + h / 2, { w: 2 }); } }
function drops(g, t, x, y, w, h, n = 40) {
  for (let i = 0; i < n; i++) {
    const sp = 18 + H(i) * 40, stick = Math.floor(t * .7 + H(i + 3) * 5) % 3 === 0, py = y + ((stick ? Math.floor(t * .7 + H(i + 3) * 5) * 13 : t * sp) + H(i * 7) * h) % h, px = x + H(i * 3) * w, r = 2 + H(i + 5) * 4;
    g.globalAlpha = ALPHA * .5; g.strokeStyle = '#6A6A7A'; g.lineWidth = r * .5; g.beginPath(); g.moveTo(px, py - r * 4); g.lineTo(px, py); g.stroke();
    g.globalAlpha = ALPHA * .8; g.fillStyle = 'rgba(255,255,255,0.6)'; g.beginPath(); g.arc(px, py, r, 0, TAU); g.fill(); pencil(g, ellPts(px, py, r, r * 1.1, 0, TAU, 8), { closed: true, w: .8, a: .7, passes: 1, seed: i });
    g.fillStyle = '#FFFFFF'; g.fillRect(px - r * .4, py - r * .5, r * .4, r * .4);
  }
  g.globalAlpha = ALPHA;
}
function write(g, str, x, y, size, t0, t, o = {}) {
  g.save(); g.font = `${size}px ${FONT}`; g.textBaseline = 'middle';
  const chars = [...str], tw = g.measureText(str).width; let cx = x - tw / 2;
  chars.forEach((ch, i) => { const a = seg(t, t0 + i * (o.gap ?? .18), t0 + i * (o.gap ?? .18) + .25); if (a > 0) { g.globalAlpha = ALPHA * a * (o.a ?? .9); g.fillStyle = o.col || GRAPH; g.fillText(ch, cx + (H(i + 3) - .5) * 2, y + (H(i + 9) - .5) * 4); } cx += g.measureText(ch).width; });
  g.restore(); g.globalAlpha = ALPHA;
}
function soundMarks(g, x, y, p, seed) { if (p <= 0 || p >= 1) return; for (let k = 0; k < 5; k++) { const a = -Math.PI / 2 + (k - 2) * .5, r0 = 10 + p * 30, r1 = r0 + 14; pencil(g, [[x + Math.cos(a) * r0, y + Math.sin(a) * r0], [x + Math.cos(a + .08) * (r0 + 7), y + Math.sin(a + .08) * (r0 + 7)], [x + Math.cos(a) * r1, y + Math.sin(a) * r1]], { w: 1.4, a: .8 * (1 - p), seed: seed + k }); } }
function phoneP(g, x, y, s, t, o = {}) {
  const w = 70 * s, h = 130 * s; solid(g, rectPts(x - w / 2, y - h / 2, w, h)); pencil(g, curvePts([[x - w / 2 + 8, y - h / 2], [x + w / 2 - 8, y - h / 2], [x + w / 2, y - h / 2 + 8], [x + w / 2, y + h / 2 - 8], [x + w / 2 - 8, y + h / 2], [x - w / 2 + 8, y + h / 2], [x - w / 2, y + h / 2 - 8], [x - w / 2, y - h / 2 + 8]], true, 3), { closed: true, w: 1.5 });
  wRect(g, x - w / 2 + 6 * s, y - h / 2 + 14 * s, w - 12 * s, h * .62, '#9AB8E0', { a: .25, edge: false });
  figure(g, 'you', x, y - h / 2 + 14 * s + h * .6, .42 * s, { color: true, eyes: 'closed', mouth: 'smile', blush: true }, t);
  if (o.bin != null) withAlpha(o.bin, () => { const bx = x + w / 2 - 18 * s, by = y + h / 2 - 22 * s; pRect(g, bx - 7 * s, by - 6 * s, 14 * s, 16 * s, { w: 1.2 }); pLine(g, bx - 9 * s, by - 8 * s, bx + 9 * s, by - 8 * s, { w: 1.2 }); for (const dx of [-3, 0, 3]) pLine(g, bx + dx * s, by - 3 * s, bx + dx * s, by + 7 * s, { w: .8 }); blot(g, bx, by, 16 * s, '#D84040', .25); });
}
function sketchbook(g, cx, cy, w, h) { solid(g, rectPts(cx - w / 2, cy - h / 2, w, h), '#F8F5EE'); pRect(g, cx - w / 2, cy - h / 2, w, h, { w: 1.4 }); for (let i = 0; i < 12; i++) pEll(g, cx - w / 2 + 30 + i * (w - 60) / 11, cy - h / 2, 5, 9, { w: 1, seed: i }); }
function eraserP(g, x, y, ang = -.3) { g.save(); g.translate(x, y); g.rotate(ang); const pts = rectPts(-22, -12, 44, 24); solid(g, pts); wash(g, pts, '#E89AA6', { a: .4 }); pencil(g, pts, { closed: true, w: 1.3 }); pLine(g, -6, -12, -6, 12, { w: 1 }); g.restore(); }
function rubbed(g, x, y, rx, ry, a) { if (a <= 0) return; const gr = g.createRadialGradient(x, y, 0, x, y, rx); gr.addColorStop(0, `rgba(248,245,238,${a * ALPHA})`); gr.addColorStop(.7, `rgba(248,245,238,${a * .85 * ALPHA})`); gr.addColorStop(1, 'rgba(248,245,238,0)'); g.save(); g.translate(x, y); g.scale(1, ry / rx); g.fillStyle = gr; g.fillRect(-rx, -rx, rx * 2, rx * 2); g.restore(); }
function room(g, o = {}) {
  pLine(g, 0, 400, VW, 400, { w: 1.4 }); for (let x = -40; x < VW; x += 80) pLine(g, x, 400, x - 60, VH, { a: .35, w: .8, seed: x });
  hatch(g, q => q.rect(0, 0, VW, 400), [0, 0, VW, 400], { a: o.dark ?? .16, sp: 6, seed: 7 });
}
function coatHanging(g, x, y, s = 1, sway = 0) {
  g.save(); g.translate(x, y); g.rotate(sway); g.scale(s, s);
  pencil(g, [[-8, -6], [0, -14], [8, -6]], { w: 1.4 }); pEll(g, 0, -18, 3, 3, { w: 1.2 });
  const coat = curvePts([[-6, -4], [-24, 6], [-26, 40], [-24, 110], [-22, 150], [22, 150], [24, 110], [26, 40], [24, 6], [6, -4]], true, 4);
  for (const sd of [-1, 1]) { const sl = curvePts([[sd * 24, 6], [sd * 36, 30], [sd * 36, 100], [sd * 30, 104], [sd * 26, 40]], true, 3); solid(g, sl); wash(g, sl, RED, { a: .4 }); pencil(g, sl, { closed: true, w: 1.1 }); }
  solid(g, coat); wash(g, coat, RED, { a: .45 }); wash(g, coat, RED, { a: .2, spread: 5 }); pencil(g, coat, { closed: true, w: 1.3 });
  pencil(g, [[-10, -4], [0, 22], [10, -4]], { w: 1.1 }); pLine(g, 0, 22, 0, 150, { w: .9, a: .5 }); for (const by of [40, 66, 92]) pEll(g, 4, by, 1.8, 1.8, { w: 1 });
  hatch(g, q => { q.beginPath(); coat.forEach(([a, b], i) => i ? q.lineTo(a + 6, b) : q.moveTo(a + 6, b)); q.closePath(); }, [-30, 0, 30, 150], { a: .2, sp: 5 });
  g.restore();
}

// ---------------------------------------------------------------- shots
const SCENES = {
  title(g, t, s) {
    const u = local(t, s);
    nightSky(g, .7);
    for (let i = 0; i < 26; i++) blot(g, 80 + H(i) * 800, 120 + H(i + 4) * 280, 30 + H(i + 2) * 50, ['#F2C24E', '#F08850', '#7AA0E0', '#E06A8A'][i % 4], .45 + .15 * Math.sin(t + i));
    drops(g, t, 40, 30, 880, 480, 60);
    windowFrame(g, 40, 30, 880, 480);
    rainP(g, t, 20, { a: .25 });
    write(g, '给我一个理由忘记', 480, 230, 78, 2.5, u, { col: '#F3EEE4', gap: .22 });
    if (u > 5.6) write(g, 'A-Lin', 480, 300, 34, 5.6, u, { col: '#F3EEE4' });
    if (u > 6.4) write(g, '铅笔 MV', 480, 340, 26, 6.4, u, { col: '#D8D0C4' });
    fade(g, PAPER, 1 - seg(u, 0, 2));
  },
  cityrain(g, t, s) {
    const u = local(t, s);
    nightSky(g, .55, 360);
    skyline(g, 200 + u * 14, 360, { lit: .3, hmax: 200, seed: 2, step: 90, dark: .12 });
    skyline(g, u * 26, 420, { lit: .35, hmin: 60, hmax: 130, seed: 5 });
    pLine(g, 0, 420, VW, 420, { w: 1.4 }); hatch(g, q => q.rect(0, 420, VW, 120), [0, 420, VW, VH], { a: .2, sp: 5, ang: -.2 });
    for (let i = 0; i < 6; i++) puddle(g, t, 80 + i * 170, 470 + (i % 2) * 24, 60, { wash: '#F2C24E', ph: i * .3 });
    rainP(g, t, 100, { a: .5 }); rainP(g, t + 5, 80, { a: .6, col: '#F3EEE4', w: 1.1 });
  },
  crossing(g, t, s) {
    const u = local(t, s);
    greySky(g, 240);
    skyline(g, 40, 260, { lit: 0, hmin: 40, hmax: 80, seed: 9, step: 60 });
    pLine(g, 0, 260, VW, 260, { w: 1.2 });
    for (let i = 0; i < 8; i++) { const y0 = 300 + i * 0, x0 = 100 + i * 100; pencil(g, [[x0, 330], [x0 + 60, 330], [x0 + 80, 470], [x0 - 10, 470]], { closed: true, a: .5, seed: i }); hatch(g, q => { q.moveTo(x0, 330); q.lineTo(x0 + 60, 330); q.lineTo(x0 + 80, 470); q.lineTo(x0 - 10, 470); q.closePath(); }, [x0 - 10, 330, x0 + 80, 470], { a: .15, sp: 4, seed: i }); void y0; }
    // a pedestrian light, the only colour on the street
    pLine(g, 860, 420, 860, 220, { w: 1.6 }); pRect(g, 846, 220, 28, 48, { w: 1.2 }); wEll(g, 860, 254, 8, 9, '#4AB070', { a: .45 }); blot(g, 860, 254, 24, '#4AB070', .35);
    for (let i = 0; i < 10; i++) { const dir = i % 2 ? 1 : -1, sp = 70 + H(i) * 50, x = dir > 0 ? ((u * sp + H(i) * 1200) % 1200) - 120 : 1080 - ((u * sp + H(i) * 1200) % 1200), y = 380 + (i % 3) * 40; if (Math.abs(x - 480) < 60) continue; passer(g, x, y, .95 + (i % 3) * .12, i * 7, u * 1.2 + i, { flip: dir < 0, umb: true, a: .5 }); }
    const P = figure(g, 'me', 480, 460, 1.25, { aR: 'umb', eyes: 'down', mouth: 'flat' }, t);
    if (P) umbrellaP(g, P.R[0], P.R[1], P.head[1] - 60, 60);
    rainP(g, t, 110, { a: .45 });
  },
  stopping(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, lower = eio(seg(u, 3.4, 5.2));
    greySky(g, 260);
    skyline(g, 40, 300, { lit: 0, hmin: 50, hmax: 110, seed: 9, step: 70 });
    pLine(g, 0, 300, VW, 300, { w: 1.2 }); hatch(g, q => q.rect(0, 300, VW, 240), [0, 300, VW, VH], { a: .12, sp: 6, ang: -.15 });
    puddle(g, t, 480, 470, 120, { ripples: u < d - 2 ? 2 : 1 });
    const P = figure(g, 'me', 480, 460, 1.4, { aR: lower > .5 ? 'down' : 'umb', eyes: u > 5.5 ? 'open' : 'down', mouth: 'flat', tilt: -lower * .12 }, t);
    if (P) { if (lower < .5) umbrellaP(g, P.R[0], P.R[1], P.head[1] - 60 + lower * 120, 60); else { pLine(g, P.R[0], P.R[1], P.R[0] + 6, P.R[1] + 70, { w: 1.4 }); pencil(g, [[P.R[0], P.R[1] + 10], [P.R[0] + 10, P.R[1] + 60], [P.R[0] - 6, P.R[1] + 60]], { closed: true, seed: 3 }); } }
    rainP(g, t, Math.round(120 * (1 - seg(u, 0, d - 1.5))), { a: .45 });
  },
  graysky(g, t, s) {
    const u = local(t, s);
    greySky(g, 380);
    pLine(g, 0, 380, VW, 380, { w: 1.2 }); skyline(g, 0, 380, { lit: 0, hmin: 30, hmax: 70, seed: 11, step: 50 });
    puddle(g, t, 560, 470, 160, { ripples: 1, ph: .3 });
    pencil(g, ellPts(560, 470, 150, 22, Math.PI * 1.05, Math.PI * 1.95, 10), { a: .3, seed: 4 });
    const dropY = 80 + ((u * 160) % 400); if (u > 1.2 && dropY < 466) { pEll(g, 560, dropY, 2.5, 3.5, { w: 1 }); }
    figure(g, 'me', 380, 470, 1.15, { eyes: 'open', mouth: 'flat', tilt: -.22, look: .3 }, t);
  },
  smiley(g, t, s) {
    const u = local(t, s);
    // a memory: colour seeps into the paper
    wRect(g, -20, -20, VW + 40, VH + 40, '#F2C878', { a: .14, edge: false, spread: 10 });
    blot(g, 300, 250, 300, '#F2B860', .25);
    for (let i = 0; i < 10; i++) blot(g, H(i) * VW, H(i + 2) * 300, 40, ['#F2C24E', '#F08850'][i % 2], .3);
    const wx = 500, wy = 60, ww = 420, wh = 300;
    wRect(g, wx, wy, ww, wh, '#C8D4E0', { a: .45, edge: false });
    windowFrame(g, wx, wy, ww, wh, { cross: false });
    // the smiley he draws in the mist with a finger
    const p = seg(u, 1, 4.2), face = ellPts(710, 190, 70, 70, -Math.PI / 2, -Math.PI / 2 + TAU * clamp(p * 1.6), 40);
    const smile = ellPts(710, 200, 38, 30, .15 * Math.PI, .15 * Math.PI + .7 * Math.PI * clamp(p * 4 - 2.6), 12);
    g.save(); g.lineCap = 'round'; g.lineWidth = 9; g.strokeStyle = `rgba(255,252,240,${.85 * ALPHA})`; for (const pts of [face, smile]) { if (pts.length < 2) continue; g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke(); } g.restore();
    if (p > .55) for (const sd of [-1, 1]) { g.fillStyle = `rgba(255,252,240,${.85 * ALPHA})`; g.beginPath(); g.arc(710 + sd * 24, 170, 6, 0, TAU); g.fill(); }
    const A = figure(g, 'you', 470, 470, 1.45, { color: true, aR: p < 1 && u > .8 ? 'out' : 'down', eyes: 'open', mouth: 'smile', look: 1 }, t);
    figure(g, 'me', 330, 470, 1.45, { color: true, eyes: u > 3 ? 'closed' : 'open', mouth: u > 3 ? 'laugh' : 'smile', look: 1, blush: true }, t);
    void A;
  },
  footsteps(g, t, s) {
    const u = local(t, s), sc = u * 40;
    nightSky(g, .62, 330);
    skyline(g, sc * .4, 330, { lit: .06, seed: 13, dark: .15 });
    pLine(g, 0, 330, VW, 330, { w: 1.2 }); for (let x = -60; x < VW + 60; x += 120) pLine(g, x - sc % 120, 400, x - sc % 120 + 50, 400, { w: 1.4, a: .5 });
    hatch(g, q => q.rect(0, 330, VW, 210), [0, 330, VW, VH], { a: .2, sp: 5, ang: -.2 });
    lampP(g, 760 - (sc % 700), 330, 200, 1);
    const ph = step(t);
    figure(g, 'me', 420, 470, 1.35, { walk: ph, eyes: 'down', mouth: 'flat', look: 1, aL: 'pocket', aR: 'pocket' }, t);
    // each footstep rings out
    const k = Math.floor(ph * 2), f = ph * 2 - k;
    soundMarks(g, 412 + (k % 2 ? 12 : -12), 468, f * 1.3, k);
    for (let i = 1; i < 4; i++) { const fx = 420 - i * 54 - (ph * 2 % 1) * 54; pencil(g, ellPts(fx, 476 + (i % 2) * 6, 7, 3), { closed: true, a: .4 / i, seed: i }); }
  },
  lonely(g, t, s) {
    const u = local(t, s);
    hatch(g, q => q.rect(0, 0, VW, VH), [0, 0, VW, VH], { a: .06, sp: 9 });
    pencil(g, curvePts([[400, 120], [450, 90], [520, 96], [560, 120], [530, 140], [440, 140]], true, 4), { a: .5 });
    hatch(g, q => { q.ellipse(480, 118, 80, 26, 0, 0, TAU); }, [400, 90, 560, 145], { a: .3, sp: 3 });
    figure(g, 'me', 480, 460, 1.25 + u * .02, { aL: 'self', aR: 'self', eyes: 'closed', mouth: 'sad' }, t);
  },
  lightsoff(g, t, s) {
    const u = local(t, s), off = u > 2.8;
    nightSky(g, .6);
    // the carnival city: colour, music, fireworks
    for (let i = 0; i < 30; i++) blot(g, H(i) * VW, 140 + H(i + 4) * 300, 30 + H(i + 2) * 60, ['#E05A9A', '#5A8AE0', '#F2C24E', '#5AD0C0', '#F08850'][i % 5], .4 + .25 * Math.sin(t * 3 + i));
    for (let k = 0; k < 3; k++) { const a = (u * .7 + k / 3) % 1, cx = 140 + k * 300, cy = 110 + k * 20; for (let i = 0; i < 14; i++) { const an = i / 14 * TAU, r = a * 70; pLine(g, cx + Math.cos(an) * r * .6, cy + Math.sin(an) * r * .6, cx + Math.cos(an) * r, cy + Math.sin(an) * r, { col: ['#E05A9A', '#F2C24E', '#5AD0C0'][k], a: .7 * (1 - a), passes: 1 }); } }
    skyline(g, 0, 540, { lit: .5, hmin: 160, hmax: 260, seed: 21, step: 120, dark: .1 });
    // her window in the middle of it
    const bx = 400, by = 170;
    solid(g, rectPts(bx, by, 160, 370)); pRect(g, bx, by, 160, 370, { w: 1.4 }); hatch(g, q => q.rect(bx, by, 160, 370), [bx, by, bx + 160, 540], { a: .22, sp: 4 });
    const wx = bx + 30, wy = by + 40;
    if (!off) { wRect(g, wx, wy, 100, 120, '#F2C24E', { a: .4 }); blot(g, wx + 50, wy + 60, 90, '#F2C24E', .35); } else wRect(g, wx, wy, 100, 120, INK2, { a: .45 });
    pRect(g, wx, wy, 100, 120, { w: 1.3 });
    g.save(); g.beginPath(); g.rect(wx, wy, 100, 120); g.clip();
    const P = figure(g, 'me', wx + 50, wy + 230, 1.1, { aR: u > 1.8 && u < 3 ? 'up' : 'down', eyes: off ? 'closed' : 'down', mouth: 'flat', alpha: off ? .35 : 1 }, t);
    if (P) { const pull = u > 1.8 && u < 3 ? Math.min(8, (u - 1.8) * 30) : 0; pLine(g, wx + 72, wy, wx + 72, wy + 40 + pull, { w: 1, a: .7 }); pEll(g, wx + 72, wy + 44 + pull, 3, 3, { w: 1 }); }
    g.restore();
    for (let i = 0; i < 4; i++) { const p = (u * .5 + i / 4) % 1; noteP(g, 700 + i * 40, 300 - p * 120, 22, '#E05A9A', Math.sin(p * Math.PI)); }
  },
  crowd(g, t, s) {
    const u = local(t, s), v = s.v;
    if (v) { greySky(g, 260); } else nightSky(g, .45, 300);
    skyline(g, 0, 300, { lit: v ? 0 : .25, hmin: 60, hmax: 140, seed: 17 + v, step: 80 });
    pLine(g, 0, 300, VW, 300, { w: 1.2 }); hatch(g, q => q.rect(0, 300, VW, 240), [0, 300, VW, VH], { a: .1, sp: 6, ang: -.15 });
    for (let lane = 0; lane < 3; lane++) for (let i = 0; i < 8; i++) {
      const dir = (lane + i) % 2 ? 1 : -1, sp = 160 + H(i + lane * 9) * 120, x = dir > 0 ? ((u * sp + H(i * 3 + lane) * 1300) % 1300) - 170 : 1130 - ((u * sp + H(i * 3 + lane) * 1300) % 1300), y = 360 + lane * 50, sc = .75 + lane * .17;
      if (lane === 2 && Math.abs(x - 480) < 50) continue;
      passer(g, x, y, sc, i * 11 + lane, u * 2 + i, { flip: dir < 0, a: .45 + lane * .1 });
      if (lane < 2) pLine(g, x - dir * 50, y - 100 * sc, x - dir * 90, y - 100 * sc, { a: .25, passes: 1 });
    }
    figure(g, 'me', 480, 470, 1.25, { eyes: 'down', mouth: 'flat', aL: v ? 'pocket' : 'down', aR: v ? 'pocket' : 'down' }, t);
    if (v) snowP(g, t, 70);
  },
  alone(g, t, s) {
    const u = local(t, s), v = s.v, d = s.t1 - s.t0, gone = eio(seg(u, .2, d - .6));
    withAlpha(1 - gone, () => {
      if (v) greySky(g, 260); else nightSky(g, .45, 300);
      skyline(g, 0, 300, { lit: v ? 0 : .25, hmin: 60, hmax: 140, seed: 17 + v, step: 80 });
      for (let lane = 0; lane < 3; lane++) for (let i = 0; i < 7; i++) { const x = 60 + i * 140 + lane * 40, y = 360 + lane * 50; if (Math.abs(x - 480) < 60) continue; passer(g, x, y, .75 + lane * .17, i * 11 + lane, null, { a: .5 }); }
    });
    // the eraser has been over everything except her
    for (let i = 0; i < 8; i++) rubbed(g, 120 + i * 100, 300 + (i % 3) * 40, 140, 60, gone * .5);
    pLine(g, 0, 470, VW, 470, { w: 1, a: .3 });
    figure(g, 'me', 480, 470, 1.25, { eyes: 'down', mouth: 'flat', aL: v ? 'pocket' : 'self', aR: v ? 'pocket' : 'self' }, t);
    if (v) snowP(g, t, 50);
  },
  smile(g, t, s) { smileScene(g, t, local(t, s)); },
  heartcry(g, t, s) { heartcryScene(g, t, local(t, s), s.v); },
  smilecry(g, t, s) { const u = local(t, s); if (u < 3.1) smileScene(g, t, u); else heartcryScene(g, t, u - 3.1, 1); },
  erase(g, t, s) {
    const u = local(t, s), v = s.v, d = s.t1 - s.t0;
    if (v) snowP(g, t, 30);
    sketchbook(g, 480, 250, 560, 400);
    figure(g, 'you', 480, 690, 2.8, { eyes: 'closed', mouth: 'smile' }, t);
    // she rubs him out, but the lines come back
    const rub = seg(u, .3, 2.2), back = seg(u, 2.2, d - .2), ex = 480 + Math.sin(u * 9) * 90 * (rub > 0 && back === 0 ? 1 : 0), ey = 200 + Math.cos(u * 5) * 30;
    rubbed(g, 480, 220, 160, 140, rub * (1 - back) * .95);
    if (back > 0) withAlpha(back, () => figure(g, 'you', 480, 690, 2.8, { eyes: 'closed', mouth: 'smile', alpha: back }, t));
    for (let i = 0; i < 18; i++) if (rub > 0) { const x = 400 + H(i) * 180, y = 330 + H(i + 4) * 60; pEll(g, x, y, 2, 1.4, { w: .8, a: .5, passes: 1, seed: i }); }
    eraserP(g, back > 0 ? 730 : ex, back > 0 ? 400 : ey, back > 0 ? .4 : -.3 + Math.sin(u * 9) * .2);
    if (back > 0) pencil(g, linePts(700, 120, 820, 60), { w: 2, a: .6 });
    void v;
  },
  coatwrap(g, t, s) {
    const u = local(t, s), v = s.v;
    // a memory in colour: snow, and his red coat round her shoulders
    if (v) { wRect(g, -20, -20, VW + 40, VH + 40, '#2E3A6A', { a: .28, edge: false, spread: 10 }); for (let i = 0; i < 24; i++) blot(g, H(i) * VW, 80 + H(i + 4) * 300, 30, ['#F2C24E', '#E05A9A', '#5A8AE0'][i % 3], .4); }
    else { wRect(g, -20, -20, VW + 40, 360, '#9AC0E8', { a: .25, edge: false, spread: 10 }); for (const [x, y] of [[160, 380], [800, 360]]) { pLine(g, x, y, x, y - 160, { w: 2 }); pencil(g, curvePts([[x - 70, y - 120], [x - 40, y - 210], [x, y - 240], [x + 50, y - 200], [x + 70, y - 120]], true, 4), { closed: true }); } }
    pLine(g, 0, 400, VW, 400, { w: 1.2 }); wRect(g, -20, 400, VW + 40, 160, '#FFFFFF', { a: .5, edge: false });
    figure(g, 'you', 560, 470, 1.5, { color: true, eyes: 'closed', mouth: 'smile', look: -1, aL: 'out', blush: true }, t);
    figure(g, 'me', 440, 470, 1.5, { color: true, eyes: 'closed', mouth: 'smile', look: 1, blush: true, aL: 'self', aR: 'self' }, t);
    // the coat draped over her
    const drape = curvePts([[408, 264], [426, 252], [454, 252], [472, 264], [478, 330], [472, 374], [408, 374], [402, 330]], true, 4);
    wash(g, drape, RED, { a: .42 }); wash(g, drape, RED, { a: .2, spread: 4 }); pencil(g, drape, { closed: true, w: 1.3 });
    hatch(g, q => { q.beginPath(); drape.forEach(([a, b], i) => i ? q.lineTo(a, b) : q.moveTo(a, b)); q.closePath(); }, [400, 250, 480, 376], { a: .15, sp: 5 });
    snowP(g, t, 80, { wind: 4 });
    for (let i = 0; i < 3; i++) { const p = (u * .5 + i / 3) % 1; heartP(g, 500 + i * 30 + Math.sin(t + i) * 8, 220 - p * 90, 8, { wash: '#E06A7A', w: 1 }); }
  },
  delete(g, t, s) {
    const u = local(t, s), v = s.v, hover = Math.sin(u * 7) * 3;
    hatch(g, q => q.rect(0, 0, VW, VH), [0, 0, VW, VH], { a: .08, sp: 8 });
    if (v) {
      // an old photo she tries to tear
      const tear = Math.min(.25, seg(u, 1, 2.6) * .25) * (1 - seg(u, 3.2, 4));
      for (const sd of [-1, 1]) { g.save(); g.translate(480 + sd * tear * 60, 240); g.rotate(sd * tear * .4); g.beginPath(); g.rect(sd < 0 ? -160 : 0, -110, 160, 220); g.clip(); solid(g, rectPts(-150, -110, 300, 220), '#F8F5EE'); pRect(g, -150, -110, 300, 220, { w: 1.4 }); wRect(g, -130, -90, 260, 150, '#F2C878', { a: .3 }); figure(g, 'me', -40, 60, .62, { color: true, eyes: 'closed', mouth: 'smile' }, t); figure(g, 'you', 40, 60, .62, { color: true, eyes: 'closed', mouth: 'smile' }, t); g.restore(); }
      figure(g, 'me', 180, 640, 2.2, { aR: 'hold', eyes: 'down', mouth: 'sad', look: 1 }, t);
      return;
    }
    phoneP(g, 480, 240, 1.8, t, { bin: 1 });
    // her thumb hovers over the bin, and does not press
    const tx = 560 + hover, ty = 330 + Math.min(0, -seg(u, 2.6, 3.6) * 40);
    solid(g, ellPts(tx, ty + 40, 18, 46)); pencil(g, ellPts(tx, ty + 40, 18, 46, Math.PI * 1.05, Math.PI * 1.95, 10), { w: 1.3 }); pLine(g, tx - 18, ty + 40, tx - 22, ty + 140, { w: 1.3 }); pLine(g, tx + 18, ty + 40, tx + 24, ty + 140, { w: 1.3 });
  },
  decision(g, t, s) {
    const u = local(t, s), v = s.v, a = eio(seg(u, .2, s.t1 - s.t0));
    if (v) greySky(g, 280); else nightSky(g, .55, 280);
    pLine(g, 0, 280, VW, 280, { w: 1.2 }); pLine(g, 480, 280, 480, VH, { w: 1, a: .4 }); pLine(g, 0, 400, VW, 400, { a: .4 });
    hatch(g, q => q.rect(0, 280, VW, 260), [0, 280, VW, VH], { a: .12, sp: 6 });
    const A = figure(g, 'me', 450 - a * 240, 450, 1.1, { back: true, walk: step(t), aR: 'umb' }, t);
    const B = figure(g, 'you', 510 + a * 240, 450, 1.1, { back: true, walk: step(t) + .5, aL: 'umb' }, t);
    if (A) umbrellaP(g, A.R[0], A.R[1], A.head[1] - 50, 48);
    if (B) umbrellaP(g, B.L[0], B.L[1], B.head[1] - 50, 48);
    if (v) snowP(g, t, 60); else rainP(g, t, 120, { a: .45 });
  },
  thread(g, t, s) {
    const u = local(t, s), v = s.v, pull = eio(seg(u, .3, s.t1 - s.t0));
    if (v === 1) snowP(g, t, 30); if (v === 2) rainP(g, t, 50, { a: .3 });
    const P = figure(g, 'me', 300, 470, 1.6, { aR: 'reach', aL: 'chest', eyes: 'closed', mouth: 'sad', look: 1 }, t);
    if (P) {
      // a red thread out of her heart: the more she pulls, the longer it gets
      const pts = [P.chest]; const L = 160 + pull * 700;
      for (let i = 1; i <= 30; i++) { const f = i / 30; pts.push([P.chest[0] + f * L, P.chest[1] + Math.sin(f * 9 + t * 2) * 10 * (1 - f) + f * 30]); }
      pencil(g, pts, { col: RED, w: 1.8, a: .9, j: .8 });
      blot(g, P.chest[0], P.chest[1], 22, RED, .35);
    }
  },
  clearer(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, p = eio(seg(u, 0, d - .3)), v = s.v;
    if (v === 1) snowP(g, t, 30); if (v === 2) rainP(g, t, 50, { a: .3 });
    // his outline is a blur at first and comes into focus, in colour
    for (let k = 0; k < 4; k++) { const off = (1 - p) * 26, a = (1 - p) * .25; withAlpha(a, () => figure(g, 'you', 480 + Math.cos(k * 1.6) * off, 470 + Math.sin(k * 1.6) * off * .4, 1.55, { eyes: 'closed', mouth: 'smile' }, t)); }
    withAlpha(.2 + .8 * p, () => figure(g, 'you', 480, 470, 1.55, { color: p > .5, eyes: p > .6 ? 'open' : 'closed', mouth: 'smile' }, t));
  },
  distance(g, t, s) { distanceScene(g, t, local(t, s), s.v); },
  empty(g, t, s) { emptyScene(g, t, local(t, s), s.v); },
  distempty(g, t, s) { const u = local(t, s); if (u < 2.7) distanceScene(g, t, u, s.v); else emptyScene(g, t, u - 2.7, s.v); },
  inheart(g, t, s) {
    const u = local(t, s), v = s.v, d = s.t1 - s.t0;
    if (v === 1) snowP(g, t, 40);
    const spread = v === 2 ? eio(seg(u, 2.5, d - 1)) : 0;
    if (spread > 0) { const r = spread * 900; for (const [c, k] of [['#F2C878', 1], ['#9AC0E8', .8], ['#E8A0A8', .6]]) blot(g, 480, 300, r * k, c, .45); }
    const P = figure(g, 'me', 480, 700, 2.7, { aL: 'chest', aR: 'chest', eyes: 'closed', mouth: 'smile', color: spread > .4, blush: spread > .4 }, t);
    if (P) {
      const glow = .5 + .2 * Math.sin(u * 2.5);
      blot(g, P.chest[0], P.chest[1], 80 + 20 * glow, '#F2B860', .5 * glow + .2);
      // inside: a small picture of him, in colour
      const cx = P.chest[0], cy = P.chest[1] - 6, r = 46 + seg(u, .4, 1.6) * 10;
      g.save(); g.beginPath(); heartPts(cx, cy, r, 40).forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); g.clip();
      wRect(g, cx - r * 1.4, cy - r * 1.4, r * 2.8, r * 2.8, v === 1 ? '#C8D8F0' : '#F2D8A0', { a: .5, edge: false });
      figure(g, 'you', cx, cy + r * .95, r / 70, { color: true, eyes: 'closed', mouth: 'smile', blush: true }, t);
      g.restore();
      pencil(g, heartPts(cx, cy, r, 48), { closed: true, col: RED, w: 1.6 });
    }
  },
  seasons(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, snow = seg(u, d * .55, d * .7);
    room(g, { dark: .2 });
    const wx = 260, wy = 60, ww = 440, wh = 300;
    solid(g, rectPts(wx, wy, ww, wh));
    g.save(); g.beginPath(); g.rect(wx, wy, ww, wh); g.clip();
    wRect(g, wx - 10, wy - 10, ww + 20, wh + 20, '#B8C8D8', { a: .35, edge: false, spread: 6 });
    greySky(g, 360);
    // the tree outside: rain, then the leaves fall, then the first snow
    const tx = 520, ty = 370;
    for (const dx of [-7, 7]) pencil(g, curvePts([[tx + dx, ty], [tx + dx * .8 - 4, ty - 90], [tx + dx * .6 - 8, ty - 160]], false, 5), { w: 1.6 });
    hatch(g, q => q.rect(tx - 7, ty - 160, 14, 160), [tx - 8, ty - 160, tx + 8, ty], { a: .4, sp: 3 });
    for (const [a, l] of [[-.8, 120], [-.3, 140], [.3, 130], [.85, 110], [-1.2, 90], [1.2, 80]]) pencil(g, curvePts([[tx - 6, ty - 150], [tx - 6 + Math.sin(a) * l * .5, ty - 150 - Math.cos(a) * l * .55], [tx - 6 + Math.sin(a) * l, ty - 150 - Math.cos(a) * l]], false, 5), { w: 2, seed: a * 10 });
    const leaves = 1 - seg(u, d * .2, d * .55);
    for (let i = 0; i < 70; i++) { const a = H(i) * TAU, r = 30 + H(i + 3) * 110, x = tx - 6 + Math.cos(a) * r, y = ty - 250 + Math.sin(a) * r * .55; if (H(i + 7) < leaves) wEll(g, x, y, 11, 6, ['#E0904A', '#C86A3A', '#E8B050'][i % 3], { a: .55, edge: false, layers: 2 }); }
    if (leaves < 1) for (let i = 0; i < 18; i++) { const p = ((u * .3 + H(i)) % 1); wEll(g, tx - 180 + H(i + 2) * 360 + Math.sin(u * 2 + i) * 20, wy + p * wh, 10, 5, ['#E0904A', '#C86A3A'][i % 2], { a: .5 * (1 - snow), edge: false, layers: 2 }); }
    if (u < d * .2) rainP(g, t, 60, { a: .35 });
    if (snow > 0) withAlpha(snow, () => { snowP(g, t, 90); wRect(g, wx, ty - 6, ww, 30, '#FFFFFF', { a: .6, edge: false }); });
    g.restore();
    windowFrame(g, wx, wy, ww, wh);
    figure(g, 'me', 480, 730, 2.2, { back: true }, t);
  },
  places(g, t, s) {
    const u = local(t, s), sc = u * 70;
    greySky(g, 200);
    // shops along the street; at each one the two of them are still there, in colour
    for (let i = -1; i < 6; i++) {
      const x = i * 300 - sc % 300 + 40, k = Math.floor(sc / 300) + i;
      solid(g, rectPts(x, 140, 240, 270)); pRect(g, x, 140, 240, 270, { w: 1.3, seed: k }); hatch(g, q => q.rect(x, 140, 240, 40), [x, 140, x + 240, 180], { a: .3, sp: 4, seed: k });
      pRect(g, x + 20, 220, 200, 150, { w: 1.1, seed: k + 1 });
      wRect(g, x + 22, 222, 196, 146, '#C8D4E0', { a: .25, edge: false });
      const near = 1 - Math.abs((x + 120) - 480) / 360;
      if (near > 0) withAlpha(clamp(near * 1.4) * .75, () => { figure(g, 'me', x + 90, 370, .7, { color: true, sit: k % 2 === 0, eyes: 'closed', mouth: 'smile', look: 1 }, t); figure(g, 'you', x + 150, 370, .7, { color: true, sit: k % 2 === 0, eyes: 'open', mouth: 'laugh', look: -1 }, t); });
    }
    pLine(g, 0, 410, VW, 410, { w: 1.3 }); hatch(g, q => q.rect(0, 410, VW, 130), [0, 410, VW, VH], { a: .1, sp: 6 });
    figure(g, 'me', 470, 480, 1.25, { walk: step(t), eyes: 'down', mouth: 'flat', look: -.6, aL: 'pocket', aR: 'pocket' }, t);
    snowP(g, t, 50);
  },
  laugh(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, turn = u > 1.6, gone = seg(u, d - 1.8, d - .3);
    greySky(g, 280);
    pLine(g, 0, 380, VW, 380, { w: 1.2 }); wRect(g, -20, 380, VW + 40, 180, '#FFFFFF', { a: .5, edge: false });
    // his carefree laugh, in colour, going round and round in the snow
    withAlpha(.85 * (1 - gone), () => {
      blot(g, 620, 300, 160, '#F2C878', .35);
      figure(g, 'you', 620, 440, 1.4, { color: true, aL: 'out', aR: 'out', eyes: 'closed', mouth: 'laugh', flip: Math.floor(u * 2.5) % 2 === 1, blush: true }, t);
      for (let i = 0; i < 6; i++) { const p = (u * .6 + i / 6) % 1, a = i / 6 * TAU + u; noteP(g, 620 + Math.cos(a) * (60 + p * 80), 260 - p * 120 + Math.sin(a) * 20, 20, i % 2 ? '#E0904A' : RED, Math.sin(p * Math.PI)); }
    });
    figure(g, 'me', 280, 460, 1.3, turn ? { eyes: u > 3 ? 'open' : 'closed', mouth: 'flat', look: 1 } : { back: true }, t);
    snowP(g, t, 80);
  },
  home(g, t, s) {
    const u = local(t, s), open = eio(seg(u, .2, 1.2)), lamp = u > 3;
    room(g, { dark: .3 });
    // one chair, one cup, one bed
    pRect(g, 600, 300, 160, 100, { w: 1.2 }); pLine(g, 600, 320, 760, 320, { a: .5 }); hatch(g, q => q.rect(600, 300, 160, 100), [600, 300, 760, 400], { a: .15, sp: 5 });
    pRect(g, 80, 320, 120, 10, { w: 1.2 }); pLine(g, 92, 330, 92, 400); pLine(g, 188, 330, 188, 400); pRect(g, 126, 300, 20, 20, { w: 1 }); pencil(g, ellPts(148, 310, 5, 6, -Math.PI / 2, Math.PI / 2, 5), { w: 1 });
    pLine(g, 230, 330, 230, 400); pLine(g, 270, 330, 270, 400); pRect(g, 225, 322, 50, 10); pLine(g, 270, 322, 270, 270); pLine(g, 230, 322, 230, 270); pLine(g, 230, 270, 270, 270);
    pLine(g, 420, 140, 420, 240, { a: .6 }); pencil(g, [[400, 240], [440, 240], [430, 270], [410, 270]], { closed: true });
    if (lamp) { blot(g, 420, 260, 140, '#F2C24E', .4); blot(g, 420, 300, 260, '#F2C24E', .12); }
    // the door opens and light from the corridor falls across the floor
    const dx = 800, dw = 110;
    solid(g, rectPts(dx, 120, dw, 280)); pRect(g, dx, 120, dw, 280, { w: 1.4 });
    if (open > 0) { wash(g, [[dx, 400], [dx + dw * open, 400], [dx - 60 - 140 * open, VH], [dx - 200 * open, VH]], '#F2D8A0', { a: .35, edge: false }); wRect(g, dx, 120, dw * open, 280, '#F2D8A0', { a: .5, edge: false }); }
    pencil(g, [[dx + dw * open, 120], [dx + dw * open + 10, 130], [dx + dw * open + 10, 390], [dx + dw * open, 400]], { w: 1.2 });
    const wx = lerp(860, 700, eio(seg(u, 1, 3)));
    figure(g, 'me', wx, 450, 1.25, { walk: u > 1 && u < 3 ? step(t) : null, eyes: 'down', mouth: 'flat', look: -1, aR: lamp ? 'down' : 'hold' }, t);
  },
  afraid(g, t, s) {
    const u = local(t, s);
    room(g, { dark: .3 });
    blot(g, 300, 260, 160, '#F2C24E', .25);
    figure(g, 'me', 380, 980, 4.6, { eyes: 'open', mouth: 'open', look: 1, aL: 'chest' }, t);
    // a hint of red at the edge of the frame
    blot(g, 960, 260, 120 + u * 30, RED, .25 + u * .08);
  },
  coat(g, t, s) {
    const u = local(t, s), touch = u > 2.4, hold = u > 3.8;
    room(g, { dark: .3 });
    const wx = 120, wy = 70; solid(g, rectPts(wx, wy, 220, 240)); g.save(); g.beginPath(); g.rect(wx, wy, 220, 240); g.clip(); greySky(g, 320); snowP(g, t, 40); g.restore(); windowFrame(g, wx, wy, 220, 240);
    blot(g, 640, 250, 150, RED, .12);
    coatHanging(g, 640, 110, 1.35, Math.sin(u * 1.4) * .02);
    const P = figure(g, 'me', hold ? 560 : lerp(400, 540, eio(seg(u, 0, 2.4))), 470, 1.45, { walk: u < 2.4 ? step(t) : null, aR: touch ? (hold ? 'chest' : 'reach') : 'down', aL: hold ? 'chest' : 'down', eyes: hold ? 'closed' : 'open', mouth: hold ? 'sad' : 'flat', look: 1, tilt: hold ? .15 : 0, tear: hold }, t);
    if (P && hold) { const sl = curvePts([[P.R[0] - 6, P.R[1] - 10], [P.R[0] + 40, P.R[1] - 30], [640 + 36 * 1.35, 110 + 60 * 1.35], [P.R[0] + 4, P.R[1] + 6]], true, 3); wash(g, sl, RED, { a: .35 }); pencil(g, sl, { closed: true, w: 1.1 }); }
  },
  storm(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, k = seg(u, 0, d - 2);
    nightSky(g, .5 + .2 * k);
    skyline(g, 0, 330, { lit: .1, seed: 31, dark: .2 });
    pLine(g, 0, 330, VW, 330, { w: 1.2 }); hatch(g, q => q.rect(0, 330, VW, 210), [0, 330, VW, VH], { a: .22, sp: 5, ang: -.2 });
    for (let i = 0; i < 5; i++) puddle(g, t, 120 + i * 180, 450 + (i % 2) * 30, 70, { ripples: 3, ph: i * .2 });
    figure(g, 'me', 480, 470, 1.3, { eyes: 'closed', mouth: 'flat', tilt: .1, aL: 'self', aR: 'self' }, t);
    rainP(g, t, Math.round(60 + 160 * k), { a: .45, slant: .3 + .3 * k, sp: 650 }); rainP(g, t + 7, Math.round(60 + 200 * k), { a: .7, slant: .3 + .3 * k, sp: 700, col: '#F3EEE4', w: 1.3, len: 26 });
    // lightning on some of the loud hits
    const lk = lastKick(t), a = t - lk;
    if (k > .3 && a < .25 && H(Math.round(lk * 10)) > .55) { const x0 = 200 + H(Math.round(lk * 10) + 1) * 560; const pts = [[x0, 0]]; for (let i = 1; i < 8; i++) pts.push([x0 + (H(i + lk) - .5) * 60, i * 40]); pencil(g, pts, { w: 3, col: '#FFFFFF', a: 1 - a * 4 }); pencil(g, pts, { w: 1.2, a: 1 - a * 4 }); fade(g, '#FFFFFF', (1 - a * 4) * .4); }
  },
  noerase(g, t, s) {
    const u = local(t, s), col = eio(seg(u, .6, 3.6));
    sketchbook(g, 480, 250, 560, 400);
    if (col > 0) { const r = col * 300; blot(g, 480, 260, r, '#F2C878', .35); }
    figure(g, 'you', 480, 690, 2.8, { eyes: col > .6 ? 'open' : 'closed', mouth: 'smile', color: col > .3, blush: col > .6 }, t);
    eraserP(g, 760, 420, .9);
    pencil(g, [[700, 470], [760, 520], [800, 530]], { w: 1.2, a: .5 });
  },
  farewell(g, t, s) {
    const u = local(t, s), a = eio(seg(u, 0, s.t1 - s.t0));
    nightSky(g, .6, 340);
    skyline(g, 0, 340, { lit: .1, seed: 33, dark: .25 });
    pLine(g, 0, 340, VW, 340, { w: 1.2 }); hatch(g, q => q.rect(0, 340, VW, 200), [0, 340, VW, VH], { a: .22, sp: 5 });
    puddle(g, t, 600, 470, 140, { ripples: 3 });
    figure(g, 'you', lerp(560, 780, a), lerp(470, 420, a), lerp(1.3, .95, a), { back: true, walk: step(t), color: true }, t);
    figure(g, 'me', 300, 470, 1.35, { aR: 'reach', eyes: 'open', mouth: 'open', look: 1 }, t);
    rainP(g, t, 160, { a: .5, slant: .35, sp: 700 }); rainP(g, t + 7, 220, { a: .7, slant: .35, sp: 760, col: '#F3EEE4', w: 1.3, len: 26 });
  },
  keep(g, t, s) {
    const u = local(t, s), bin = 1 - seg(u, .8, 2.8);
    hatch(g, q => q.rect(0, 0, VW, VH), [0, 0, VW, VH], { a: .07, sp: 8 });
    const P = figure(g, 'me', 480, 800, 3.4, { aL: 'chest', aR: 'chest', eyes: 'closed', mouth: 'flat', tilt: -.08 }, t);
    if (P) { blot(g, P.chest[0], P.chest[1], 90, '#F2B860', .45); phoneP(g, P.chest[0], P.chest[1] + 20, .9, t, { bin }); }
  },
  wait(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, k = Math.floor(u / (d / 4)) % 4;
    // she waits at the stop while the seasons turn behind her
    if (k === 0) rainP(g, t, 100, { a: .4 }); if (k === 1) for (let i = 0; i < 20; i++) wEll(g, H(i) * VW, (t * 60 + H(i + 2) * VH) % VH, 6, 3.5, '#E0904A', { a: .5, edge: false, layers: 2 }); if (k === 2) snowP(g, t, 90); if (k === 3) { blot(g, 800, 100, 160, '#F2C878', .45); }
    pLine(g, 0, 440, VW, 440, { w: 1.3 });
    pLine(g, 300, 440, 300, 180, { w: 1.6 }); pLine(g, 660, 440, 660, 180, { w: 1.6 }); pRect(g, 280, 160, 400, 24, { w: 1.4 }); hatch(g, q => q.rect(280, 160, 400, 24), [280, 160, 680, 184], { a: .3, sp: 3 });
    clockFaceS(g, 620, 230, 26, u * 14);
    bench(g, 480, 440, 260);
    figure(g, 'me', 470, 446, 1.3, { sit: true, aL: 'hold', aR: 'hold', eyes: 'open', mouth: 'flat' }, t);
  },
  missyou(g, t, s) {
    const u = local(t, s), p = seg(u, .4, 3.8);
    // the window is misted over; where her finger goes, the city shows through, in colour
    const wx = 120, wy = 40, ww = 720, wh = 420;
    g.save(); g.beginPath(); g.rect(wx, wy, ww, wh); g.clip();
    for (let i = 0; i < 26; i++) blot(g, wx + H(i) * ww, wy + 100 + H(i + 4) * 300, 40, ['#F2C24E', '#F08850', '#7AA0E0', '#E06A8A'][i % 4], .5);
    skyline(g, 30, wy + wh, { lit: .4, hmin: 80, hmax: 220, seed: 41, step: 90, dark: .1 });
    g.restore();
    const hp = heartPts(480, 230, 120, 80), n = Math.floor(p * hp.length);
    g.save(); g.beginPath(); g.rect(wx, wy, ww, wh);
    // the mist everywhere except along her finger's line
    g.fillStyle = `rgba(226,228,232,${.86 * ALPHA})`; g.fill(); g.restore();
    if (n > 1) { g.save(); g.beginPath(); g.rect(wx, wy, ww, wh); g.clip(); g.globalCompositeOperation = 'destination-out'; g.lineWidth = 26; g.lineCap = 'round'; g.beginPath(); hp.slice(0, n).forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.stroke(); g.restore(); }
    if (n > 1) { g.save(); g.beginPath(); g.rect(wx, wy, ww, wh); g.clip(); g.globalCompositeOperation = 'destination-over'; for (let i = 0; i < 26; i++) blot(g, wx + H(i) * ww, wy + 100 + H(i + 4) * 300, 40, ['#F2C24E', '#F08850', '#7AA0E0', '#E06A8A'][i % 4], .6); g.fillStyle = '#3A3A4A'; g.fillRect(wx, wy, ww, wh); g.restore(); }
    drops(g, t, wx, wy, ww, wh, 24);
    windowFrame(g, wx, wy, ww, wh, { cross: false });
    const tip = hp[Math.max(0, n - 1)];
    if (p > 0 && p < 1) { solid(g, ellPts(tip[0] + 6, tip[1] + 18, 8, 20)); pencil(g, ellPts(tip[0] + 6, tip[1] + 18, 8, 20, Math.PI * 1.1, Math.PI * 1.9, 8), { w: 1.2 }); pLine(g, tip[0] - 2, tip[1] + 20, tip[0] - 10, tip[1] + 140); pLine(g, tip[0] + 14, tip[1] + 20, tip[0] + 30, tip[1] + 140); }
  },
  end(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, c = eio(seg(u, 0, 9));
    // morning: colour comes into the drawing of the city
    blot(g, 760, 180, 700 * c + 60, '#F2C878', .45);
    blot(g, 300, 120, 500 * c, '#9AC0E8', .35);
    skyline(g, 0, 440, { lit: .15, hmin: 80, hmax: 200, seed: 51, step: 90 });
    if (c > .2) withAlpha(c, () => { for (let i = 0; i < 12; i++) blot(g, 40 + i * 80, 330 + H(i) * 60, 90, ['#E8A0A8', '#9AC0E8', '#F2C878', '#A8D0A0'][i % 4], .35); });
    pLine(g, 0, 440, VW, 440, { w: 1.3 });
    for (let i = 0; i < 5; i++) { const x = ((u * 30 + i * 140) % 1100) - 60, y = 120 + i * 18 + Math.sin(u * 2 + i) * 6, f = Math.sin(u * 6 + i) * 5; pencil(g, [[x - 10, y - f], [x, y], [x + 10, y - f]], { w: 1.2 }); }
    figure(g, 'me', 480, 470, 1.2, { back: true, color: c > .5 }, t);
    write(g, '给我一个理由忘记', 480, 210, 70, 4.5, u, { gap: .2 });
    if (u > 7) write(g, 'A-Lin', 480, 272, 32, 7, u);
    fade(g, PAPER, seg(u, d - 4.5, d - .3));
  },
};
// a music note in pencil
function noteP(g, x, y, sz, col = GRAPH, a = 1) { withAlpha(a, () => { wEll(g, x - sz * .3, y + sz * .5, sz * .32, sz * .24, col, { a: .6, layers: 2, edge: false }); pencil(g, ellPts(x - sz * .3, y + sz * .5, sz * .32, sz * .24), { closed: true, col, w: 1.2, passes: 1 }); pencil(g, [[x, y + sz * .5], [x, y - sz * .5], [x + sz * .35, y - sz * .2]], { col, w: 1.3, passes: 1 }); }); }
function clockFaceS(g, cx, cy, r, a) { solid(g, ellPts(cx, cy, r, r)); pEll(g, cx, cy, r, r, { w: 1.4 }); pLine(g, cx, cy, cx + Math.sin(a) * r * .8, cy - Math.cos(a) * r * .8, { w: 1.2 }); pLine(g, cx, cy, cx + Math.sin(a / 12) * r * .5, cy - Math.cos(a / 12) * r * .5, { w: 1.8 }); }
function smileScene(g, t, u) {
  // friends round a table; she smiles with them
  blot(g, 480, 200, 260, '#F2C24E', .22);
  pLine(g, 140, 360, 820, 360, { w: 1.4 }); pLine(g, 160, 368, 800, 368, { w: 1 }); hatch(g, q => q.rect(140, 360, 680, 10), [140, 360, 820, 370], { a: .3, sp: 3 });
  for (const [x, sd] of [[220, 1], [330, 1], [640, 1], [750, -1]]) passer(g, x, 470, 1.05, x, null, { a: .5, flip: sd < 0 });
  for (const x of [260, 380, 580, 700]) { pencil(g, [[x - 8, 330], [x - 6, 360], [x + 6, 360], [x + 8, 330]], { w: 1 }); wRect(g, x - 7, 340, 14, 18, '#E0A050', { a: .3, edge: false }); }
  figure(g, 'me', 480, 470, 1.3, { eyes: 'closed', mouth: 'smile', aR: 'hold' }, t);
  void u;
}
function heartcryScene(g, t, u, v) {
  // inside her: a pencil heart, and it is raining in it
  withAlpha(.25, () => figure(g, 'me', 480, 1000, 4, { eyes: 'closed', mouth: 'sad' }, t));
  const pts = heartP(g, 480, 250, 150, { w: 2 });
  g.save(); g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y)); g.closePath(); g.clip();
  rainP(g, t, 90, { a: .55, slant: .1 });
  const lvl = 380 - seg(u, 0, 4.4) * 70 - (v ? 30 : 0);
  wash(g, [[300, lvl], ...Array.from({ length: 13 }, (_, i) => [300 + i * 30, lvl + Math.sin(t * 2 + i) * 4]), [660, 420], [300, 420]], '#5A8AD0', { a: .3 });
  g.restore();
  pencil(g, pts, { closed: true, w: 2 });
}
function distanceScene(g, t, u, v) {
  if (v === 1) snowP(g, t, 30); if (v === 2) rainP(g, t, 40, { a: .3 });
  const a = eio(seg(u, 0, 2.5)), lx = lerp(260, 90, a), rx = lerp(700, 870, a);
  pLine(g, 0, 460, VW, 460, { w: 1, a: .4 });
  figure(g, 'me', lx, 460, 1, { eyes: 'down', mouth: 'flat', look: 1 }, t);
  figure(g, 'you', rx, 460, 1, { back: true, color: true }, t);
  // the distance, measured with a ruler
  const y = 300; pLine(g, lx + 40, y, rx - 40, y, { w: 1.2 }); for (let x = lx + 40, i = 0; x < rx - 40; x += 20, i++) pLine(g, x, y, x, y - (i % 5 ? 6 : 14), { w: .9, seed: i });
  pencil(g, [[lx + 52, y - 8], [lx + 40, y], [lx + 52, y + 8]], { w: 1.2 }); pencil(g, [[rx - 52, y - 8], [rx - 40, y], [rx - 52, y + 8]], { w: 1.2 });
}
function emptyScene(g, t, u, v) {
  if (v === 1) snowP(g, t, 30); if (v === 2) rainP(g, t, 40, { a: .3 });
  bench(g, 480, 450, 300);
  figure(g, 'me', 400, 456, 1.3, { sit: true, eyes: 'down', mouth: 'flat', look: 1, aL: 'hold', aR: 'hold' }, t);
  // where he used to sit: a dotted outline that keeps fading
  g.save(); g.setLineDash([3, 5]); withAlpha(.6 * (1 - seg(u, .4, 2.6)), () => figure(g, 'you', 560, 456, 1.3, { sit: true, back: false, eyes: 'none', mouth: 'none' }, t)); g.restore();
}

// ---------------------------------------------------------------- one frame
const XF = .4;
const NO_XF = new Set(['heartcry']);
const MEMORY = new Set(['smiley', 'coatwrap', 'laugh']);
let bufA = null, bufB = null;
function shotInto(g, i, t) { g.setTransform(1, 0, 0, 1, 0, 0); g.setLineDash([]); paper(g); g.setTransform(SCALE, 0, 0, SCALE, 0, 0); ALPHA = 1; g.globalAlpha = 1; SCENES[SHOTS[i].name](g, t, SHOTS[i]); }
function drawFrame(g, t) {
  t = clamp(t, 0, DUR - 1e-4); BOIL = Math.floor(t * 12);
  if (!bufA) { bufA = document.createElement('canvas'); bufB = document.createElement('canvas'); bufA.width = bufB.width = VW * SCALE; bufA.height = bufB.height = VH * SCALE; }
  const i = shotIndex(t), s = SHOTS[i];
  if (i > 0 && t - s.t0 < XF && !NO_XF.has(s.name)) {
    shotInto(bufA.getContext('2d'), i - 1, t); shotInto(bufB.getContext('2d'), i, t);
    g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.drawImage(bufA, 0, 0); g.globalAlpha = eio((t - s.t0) / XF); g.drawImage(bufB, 0, 0); g.globalAlpha = 1;
  } else { g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; shotInto(g, i, t); }
  paperGrain(g);
  g.setTransform(SCALE, 0, 0, SCALE, 0, 0); ALPHA = 1;
  subtitle(g, t, { ink: GRAPH, lit: MEMORY.has(s.name) ? '#C8642A' : RED });
}
