// scenes.js — 小宇 · 纸片 MV. One function per shot (see timeline.js), drawn in 960×540 units.
// Each shot gets (g, t, s): the canvas, the song time, and its entry in SHOTS (s.t0, s.t1).

const TIMES = {
  day: { sky: ['#86CBEE', '#B9E3F5', '#EAF7FA'], sea: ['#86C6EA', '#62AEDD', '#4594CB', '#3079B4'], sand: '#F4DDAE', walk: '#EFDCB8', line: '#DCC49A', hill: '#9CCF7E', hillDk: '#7DB868', rail: '#FFFFFF', glow: '#FFF2C0', cloud: '#FFFFFF' },
  sunset: { sky: ['#6A5AA8', '#F09A8A', '#FFD9A6'], sea: ['#C893B4', '#AA7AAA', '#8C6298', '#6E4C86'], sand: '#E8BE9A', walk: '#D8B0A0', line: '#C49888', hill: '#A07C8C', hillDk: '#86667A', rail: '#FBE8DC', glow: '#FFD8A0', cloud: '#FBD2C4' },
  night: { sky: ['#121840', '#222C64', '#36427E'], sea: ['#3E5292', '#30427E', '#24346A', '#1A2756'], sand: '#5A5878', walk: '#4A4E70', line: '#3E4262', hill: '#2E3E5A', hillDk: '#24324C', rail: '#A8B0D0', glow: '#FFE6A0', cloud: '#56608E' },
  dawn: { sky: ['#4A66A8', '#A6B8E0', '#FFE0CC'], sea: ['#94ACD8', '#7690C8', '#5C78B4', '#4662A0'], sand: '#E4CDBE', walk: '#C8BCC4', line: '#B0A4B0', hill: '#7A9A86', hillDk: '#628270', rail: '#F6EEF2', glow: '#FFF0C8', cloud: '#FFE8E0' },
};
const SUB_THEMES = {
  day: { paper: '#FBF4E6', dim: '#AFA096', lit: '#D8463A' },
  night: { paper: '#F4EEE0', dim: '#A49A9A', lit: '#3A56A8' },
  sunset: { paper: '#FCF0E4', dim: '#B4A098', lit: '#C8405A' },
};
const local = (t, s) => t - s.t0;
const talk = t => singing(t) ? 'open' : 'smile';
const step = t => beatPos(t) / 3;

// ---------------------------------------------------------------- scenery
function sky(g, stops, y1 = VH) { gradV(g, stops, 0, y1); }
function cloudP(g, x, y, s, col = '#FFFFFF', d = 1.2, seed = 1) {
  cut(g, col, d, q => { q.arc(x - 18 * s, y + 4 * s, 13 * s, 0, TAU); q.arc(x, y - 6 * s, 19 * s, 0, TAU); q.arc(x + 20 * s, y + 2 * s, 14 * s, 0, TAU); q.roundRect(x - 30 * s, y + 2 * s, 62 * s, 15 * s, 7 * s); });
  void seed;
}
function clouds(g, t, n, y0, y1, col, speed = 6, seed = 1) { for (let i = 0; i < n; i++) cloudP(g, ((t * speed * (1 + H(i + seed) * .6) + H(i * 3 + seed) * 1200) % 1240) - 140, y0 + H(i * 5 + seed) * (y1 - y0), .7 + H(i + 7 + seed) * .6, col, 1.2); }
function sunP(g, x, y, r, t, col = '#FFD45A', ray = '#FFE68A') {
  g.save(); g.translate(x, y); g.rotate(t * .15);
  cut(g, ray, .8, q => { for (let i = 0; i < 12; i++) { const a = i / 12 * TAU; q.moveTo(Math.cos(a - .12) * r * 1.1, Math.sin(a - .12) * r * 1.1); q.lineTo(Math.cos(a) * r * 1.6, Math.sin(a) * r * 1.6); q.lineTo(Math.cos(a + .12) * r * 1.1, Math.sin(a + .12) * r * 1.1); q.closePath(); } });
  g.restore();
  paperCircle(g, x, y, r, col, 1.2, 4);
}
function moonP(g, x, y, r) { cut(g, '#FBF2D0', 1.2, q => { q.arc(x, y, r, -1.9, 1.9 + Math.PI, false); q.arc(x + r * .45, y - r * .25, r * .82, 1.9 + Math.PI - .25, -1.9 + .25, true); q.closePath(); }); }
function fullMoon(g, x, y, r) { const gr = g.createRadialGradient(x, y, r * .8, x, y, r * 3); gr.addColorStop(0, 'rgba(255,246,210,0.35)'); gr.addColorStop(1, 'rgba(255,246,210,0)'); g.fillStyle = gr; g.fillRect(x - r * 3, y - r * 3, r * 6, r * 6); paperCircle(g, x, y, r, '#FBF2D0', 1.2, 8); cut(g, '#EFE2B8', 0, q => { q.arc(x - r * .3, y - r * .2, r * .18, 0, TAU); q.arc(x + r * .25, y + r * .3, r * .12, 0, TAU); }); }
function starsP(g, t, n, y1, seed = 1, x0 = 0, x1 = VW, col = '#FFF4C8') { for (let i = 0; i < n; i++) { const tw = .6 + .4 * Math.sin(t * (1 + H(i + seed)) * 2 + i), x = x0 + H(i * 3 + seed) * (x1 - x0), y = H(i * 7 + seed) * y1, r = (1.2 + H(i + 9) * 2.6) * tw; if (r > 2.2) paperStar(g, x, y, r * 1.3, col, .3, t * .3 + i); else cut(g, col, 0, q => q.arc(x, y, r * .6, 0, TAU)); } }
// a band of sea with a scalloped paper edge, sliding sideways
function waveBand(g, t, y, amp, wl, speed, col, d = 1, ph = 0, foam = null) {
  const off = ((t * speed + ph) % wl + wl) % wl;
  cut(g, col, d, q => { q.moveTo(-wl, VH + 10); q.lineTo(-wl, y); for (let x = -wl - off; x < VW + wl; x += wl) q.quadraticCurveTo(x + wl / 2, y - amp, x + wl, y); q.lineTo(VW + wl, VH + 10); q.closePath(); });
  if (foam) for (let x = -wl - off; x < VW + wl; x += wl) cut(g, foam, 0, q => q.ellipse(x + wl / 2, y - amp * .45, wl * .16, amp * .18 + .6, 0, 0, TAU));
}
function sea(g, t, P, top, bottom, o = {}) {
  const n = 4, hh = (bottom - top) / n;
  for (let i = 0; i < n; i++) waveBand(g, t, top + i * hh, 4 + i * 2, 60 + i * 26, (i % 2 ? -1 : 1) * (8 + i * 6), P.sea[i], .6 + i * .3, i * 40, i === n - 1 && o.foam ? '#FFFFFF' : null);
}
function hillTown(g, t, P, night = false) {
  paperBlob(g, 130, 520, 280, 230, P.hillDk, 1.4, 11, .02);
  paperBlob(g, 120, 530, 260, 210, P.hill, 1.2, 12, .02);
  const roofs = ['#E8735A', '#4E8FCF', '#F2BE4E', '#6FB07A', '#E58AA8'];
  for (let i = 0; i < 9; i++) {
    const hx = -10 + i * 36 + (i % 2) * 8, hy = 292 + Math.abs(i - 3.8) * 13 - (i % 3) * 7;
    paperRect(g, hx, hy, 28, 22, night ? '#5A5E86' : '#FBF4E6', .8, i);
    cut(g, roofs[i % 5], .8, q => poly(q, [[hx - 4, hy + 1], [hx + 14, hy - 13], [hx + 32, hy + 1]], i * 3));
    paperRect(g, hx + 9, hy + 7, 8, 8, night ? (H(i) > .3 ? P.glow : '#2A2E4A') : '#9CCBEA', 0, i);
  }
}
function lighthouseP(g, x, base, t, on, s = 1) {
  if (on) {
    const a = t * 1.2, dir = Math.cos(a), L = 460 * Math.abs(dir), sg = dir > 0 ? 1 : -1, ly = base - 150 * s;
    const gr = g.createLinearGradient(x, 0, x + sg * L, 0); gr.addColorStop(0, 'rgba(255,240,170,0.55)'); gr.addColorStop(1, 'rgba(255,240,170,0)');
    g.fillStyle = gr; g.beginPath(); g.moveTo(x, ly); g.lineTo(x + sg * L, ly - L * .12); g.lineTo(x + sg * L, ly + L * .12); g.closePath(); g.fill();
  }
  for (let i = 0; i < 6; i++) { const y0 = base - i * 22 * s, w0 = (16 - i * 1.2) * s, w1 = (16 - (i + 1) * 1.2) * s; cut(g, i % 2 ? '#E8735A' : '#FBF4E6', i ? 0 : 1.2, q => poly(q, [[x - w0, y0], [x + w0, y0], [x + w1, y0 - 22 * s], [x - w1, y0 - 22 * s]], i)); }
  paperRect(g, x - 12 * s, base - 142 * s, 24 * s, 6 * s, '#3A4A6A', .6, 4);
  paperRect(g, x - 9 * s, base - 160 * s, 18 * s, 18 * s, on ? '#FFF0A0' : '#E8E0C0', .6, 5);
  cut(g, '#E8735A', .8, q => poly(q, [[x - 13 * s, base - 160 * s], [x, base - 176 * s], [x + 13 * s, base - 160 * s]], 6));
}
function railing(g, y, col) { paperRect(g, -10, y, VW + 20, 5, col, .8, 1); paperRect(g, -10, y + 16, VW + 20, 5, col, .8, 2); for (let x = 8; x < VW; x += 44) paperRect(g, x, y - 2, 5, 30, col, .8, x); }
function seaside(g, t, tm, o = {}) {
  const P = TIMES[tm];
  sky(g, P.sky, 300);
  if (tm === 'day') { sunP(g, o.sunX ?? 800, o.sunY ?? 86, 30, t); clouds(g, t, 4, 30, 150, P.cloud, 6, 2); }
  if (tm === 'sunset') { sunP(g, 760, 280, 40, t, '#FFC060', '#FFD890'); clouds(g, t, 3, 50, 150, P.cloud, 4, 5); }
  if (tm === 'night') { starsP(g, t, 60, 260, 3); moonP(g, o.moonX ?? 760, 84, 22); }
  if (tm === 'dawn') { starsP(g, t, 20, 130, 5); }
  sea(g, t, P, 282, 410);
  hillTown(g, t, P, tm === 'night' || tm === 'dawn');
  paperBlob(g, 900, 380, 110, 70, P.hillDk, 1.2, 21, .05);
  lighthouseP(g, 900, 318, t, tm !== 'day', .9);
  if (o.promenade !== false) {
    paperRect(g, -10, 400, VW + 20, 150, P.walk, 1.6, 3);
    for (let y = 440; y < VH; y += 34) cut(g, P.line, 0, q => q.rect(-10, y, VW + 20, 2));
    railing(g, 378, P.rail);
  }
}
function beach(g, t, tm, o = {}) {
  const P = TIMES[tm];
  sky(g, P.sky, 270);
  if (tm === 'day') { sunP(g, 170, 80, 30, t); clouds(g, t, 4, 30, 140, P.cloud, 7, 4); }
  if (tm === 'sunset') sunP(g, 600, 262, 44, t, '#FFC060', '#FFD890');
  if (tm === 'night') { starsP(g, t, 70, 240, 7); if (o.moon !== false) moonP(g, 220, 80, 22); }
  sea(g, t, P, 258, 372, { foam: true });
  const sw = Math.sin(t * 1.3) * 6;
  cut(g, P.sand, 1.6, q => { q.moveTo(-10, 380 + sw); for (let x = 0; x <= VW + 40; x += 40) q.quadraticCurveTo(x - 20, 372 + sw + H(x) * 6, x, 380 + sw); q.lineTo(VW + 10, VH + 10); q.lineTo(-10, VH + 10); q.closePath(); });
  for (let i = 0; i < 10; i++) cut(g, mixHex(P.sand, '#FFFFFF', .4), .2, q => q.ellipse(H(i) * VW, 420 + H(i + 3) * 110, 5, 2.5, 0, 0, TAU));
}
function pier(g, t, dusk = 0) {
  const A = TIMES.sunset, B = TIMES.night;
  sky(g, skyMix(A.sky, B.sky, dusk * .85), 300);
  starsP(g, t, Math.round(60 * dusk), 220, 47);
  if (dusk < .75) sunP(g, 600, 272 + dusk * 50, 44, t, '#FFC060', '#FFD890');
  sea(g, t, { sea: A.sea.map((c, i) => mixHex(c, B.sea[i], dusk * .85)) }, 286, 540);
  paperRect(g, -20, 410, 880, 18, '#A87048', 1.6, 2); for (let x = 0; x < 860; x += 26) cut(g, '#8A5A38', 0, q => q.rect(x, 412, 2, 14));
  for (let x = 14; x < 860; x += 80) paperRect(g, x, 428, 10, 120, '#7A4E30', 1, x);
}
function room(g) { gradV(g, ['#3A3E6E', '#2E3260'], 0, 400); for (let x = 0; x < VW; x += 48) cut(g, 'rgba(255,255,255,0.04)', 0, q => q.rect(x, 0, 22, 400)); paperRect(g, -10, 400, VW + 20, 150, '#5A4A66', 1.4, 2); }

// ---------------------------------------------------------------- props
function seagull(g, x, y, T, s = 1, col = '#FFFFFF') { const f = Math.sin(T * 7) * 5 * s; cut(g, col, .6, q => { q.moveTo(x - 14 * s, y - f); q.quadraticCurveTo(x - 6 * s, y - 6 * s, x, y); q.quadraticCurveTo(x + 6 * s, y - 6 * s, x + 14 * s, y - f); q.quadraticCurveTo(x + 6 * s, y - 2 * s, x, y + 3 * s); q.quadraticCurveTo(x - 6 * s, y - 2 * s, x - 14 * s, y - f); q.closePath(); }); }
function sunhat(g, x, y, s = 1, rot = 0) {
  g.save(); g.translate(x, y); g.rotate(rot);
  cut(g, '#F2DDA8', 1, q => q.ellipse(0, 0, 38 * s, 9 * s, 0, 0, TAU));
  cut(g, '#F6E6BA', 1, q => { q.moveTo(-20 * s, 0); q.quadraticCurveTo(-20 * s, -22 * s, 0, -22 * s); q.quadraticCurveTo(20 * s, -22 * s, 20 * s, 0); q.closePath(); });
  cut(g, '#5A9AD8', .4, q => q.rect(-20 * s, -7 * s, 40 * s, 6 * s));
  cut(g, '#5A9AD8', .4, q => { q.moveTo(18 * s, -5 * s); q.lineTo(30 * s, 6 * s); q.lineTo(24 * s, 8 * s); q.closePath(); });
  g.restore();
}
function iceCream(g, x, y, col, s = 1) { cut(g, '#E0A060', .8, q => { q.moveTo(x - 9 * s, y); q.lineTo(x + 9 * s, y); q.lineTo(x, y + 26 * s); q.closePath(); }); stroke(g, '#C8884E', 1, q => { q.moveTo(x - 6 * s, y + 4 * s); q.lineTo(x + 3 * s, y + 14 * s); q.moveTo(x + 6 * s, y + 4 * s); q.lineTo(x - 3 * s, y + 14 * s); }); cut(g, col, 1, q => blob(q, x, y - 6 * s, 11 * s, 10 * s, 3, .08)); cut(g, 'rgba(255,255,255,.5)', 0, q => q.ellipse(x - 4 * s, y - 10 * s, 3 * s, 2 * s, 0, 0, TAU)); }
function guitar(g, x, y, s = 1) { g.save(); g.translate(x, y); g.rotate(-.35); cut(g, '#7A4A2A', .8, q => q.rect(-58 * s, -3 * s, 44 * s, 6 * s)); cut(g, '#5A3420', .6, q => q.rect(-66 * s, -5 * s, 10 * s, 10 * s)); cut(g, '#E09A50', 1.2, q => { q.arc(0, 0, 18 * s, 0, TAU); q.arc(18 * s, 0, 15 * s, 0, TAU); }); cut(g, '#4A2A18', 0, q => q.arc(4 * s, 0, 5 * s, 0, TAU)); g.restore(); }
function flowersP(g, x, y, s = 1) { for (const [dx, dy, c] of [[-8, -16, '#FF8FB0'], [4, -22, '#FFD860'], [10, -10, '#FFFFFF'], [-2, -28, '#E8436E']]) { stroke(g, '#4E9A4A', 2 * s, q => { q.moveTo(x, y); q.lineTo(x + dx * s, y + dy * s); }); for (let i = 0; i < 5; i++) cut(g, c, .4, q => q.arc(x + dx * s + Math.cos(i / 5 * TAU) * 3.5 * s, y + dy * s + Math.sin(i / 5 * TAU) * 3.5 * s, 3 * s, 0, TAU)); } cut(g, '#FBF4E6', .6, q => poly(q, [[x - 9 * s, y - 4 * s], [x + 9 * s, y - 4 * s], [x + 4 * s, y + 12 * s], [x - 4 * s, y + 12 * s]], 5)); }
function kiteP(g, x, y, T, s = 1) { cut(g, '#E8735A', 1, q => poly(q, [[x, y - 20 * s], [x + 15 * s, y], [x, y + 26 * s], [x - 15 * s, y]], 3)); cut(g, '#F2BE4E', 0, q => poly(q, [[x, y - 20 * s], [x + 15 * s, y], [x, y]], 4)); for (let i = 0; i < 4; i++) cut(g, ['#4E8FCF', '#F2BE4E'][i % 2], .4, q => { const bx = x + Math.sin(T * 4 + i) * 5 * s, by = y + (34 + i * 12) * s; q.moveTo(bx - 4 * s, by - 3 * s); q.lineTo(bx + 4 * s, by + 3 * s); q.lineTo(bx + 4 * s, by - 3 * s); q.lineTo(bx - 4 * s, by + 3 * s); q.closePath(); }); }
function balloonP(g, x, y, T, s = 1) { const sx = Math.sin(T * 2) * 4 * s; stroke(g, '#FFFFFF', 1.2, q => { q.moveTo(x, y); q.quadraticCurveTo(x + sx, y - 24 * s, x + sx, y - 44 * s); }); paperHeart(g, x + sx, y - 58 * s, 16 * s, '#E8436E', 1); }
function lanternP(g, x, y, s = 1, glow = true) { if (glow) { const gr = g.createRadialGradient(x, y, 2, x, y, 40 * s); gr.addColorStop(0, 'rgba(255,220,140,0.6)'); gr.addColorStop(1, 'rgba(255,220,140,0)'); g.fillStyle = gr; g.fillRect(x - 40 * s, y - 40 * s, 80 * s, 80 * s); } cut(g, '#FFB860', 1, q => q.ellipse(x, y, 11 * s, 14 * s, 0, 0, TAU)); for (const dx of [-5, 0, 5]) stroke(g, 'rgba(200,90,40,.5)', 1, q => { q.moveTo(x + dx * s, y - 13 * s); q.quadraticCurveTo(x + dx * 1.6 * s, y, x + dx * s, y + 13 * s); }); cut(g, '#8A4A2A', .4, q => { q.rect(x - 6 * s, y - 16 * s, 12 * s, 3 * s); q.rect(x - 6 * s, y + 13 * s, 12 * s, 3 * s); }); }
function padlockP(g, x, y, s = 1) { stroke(g, '#9AA0B0', 4 * s, q => { q.moveTo(x - 8 * s, y - 4 * s); q.lineTo(x - 8 * s, y - 12 * s); q.arc(x, y - 12 * s, 8 * s, Math.PI, 0); q.lineTo(x + 8 * s, y - 4 * s); }); cut(g, '#F2BE4E', 1, q => q.roundRect(x - 14 * s, y - 6 * s, 28 * s, 22 * s, 4 * s)); cut(g, INK, 0, q => { q.arc(x, y + 3 * s, 3 * s, 0, TAU); q.rect(x - 1.2 * s, y + 3 * s, 2.4 * s, 7 * s); }); }
function umbrellaP(g, hand, col, s = 1, h = 70) { const [x, y] = hand; stroke(g, INK, 2.2 * s, q => { q.moveTo(x, y + 4 * s); q.lineTo(x, y - h * s); q.moveTo(x, y + 4 * s); q.quadraticCurveTo(x, y + 10 * s, x - 5 * s, y + 8 * s); }); cut(g, col, 1.2, q => { const cy = y - h * s; q.moveTo(x - 46 * s, cy + 10 * s); q.quadraticCurveTo(x - 44 * s, cy - 30 * s, x, cy - 32 * s); q.quadraticCurveTo(x + 44 * s, cy - 30 * s, x + 46 * s, cy + 10 * s); for (let i = 3; i >= 0; i--) q.quadraticCurveTo(x - 46 * s + (i + .5) * 23 * s, cy + 2 * s, x - 46 * s + i * 23 * s, cy + 10 * s); q.closePath(); }); }
function bubbleP(g, x, y, w, h, tx, ty, col = '#FFFFFF') { cut(g, col, 1.2, q => { q.roundRect(x, y, w, h, 16); q.moveTo(tx - 10, y + h - 2); q.lineTo(tx, ty); q.lineTo(tx + 12, y + h - 2); q.closePath(); }); }
function qmarkP(g, x, y, size, col = '#FFFFFF', d = 1) { g.save(); g.font = `${size}px ${FONT}`; g.textAlign = 'center'; g.textBaseline = 'middle'; lift(g, d); g.fillStyle = col; g.fillText('？', x, y); flat(g); g.restore(); }
function paperText(g, str, x, y, size, col, o = {}) {
  g.save(); g.font = `${size}px ${FONT}`; g.textAlign = o.align || 'center'; g.textBaseline = 'middle';
  if (o.edge) { g.lineJoin = 'round'; g.lineWidth = size * .16; g.strokeStyle = o.edge; lift(g, o.d ?? 1.4); g.strokeText(str, x, y); flat(g); }
  else lift(g, o.d ?? 1);
  g.fillStyle = col; g.fillText(str, x, y); flat(g); g.restore();
}
// the little cloud he becomes: a paper puff with his face and his brown tuft
function cloudKid(g, x, y, s, o = {}, T = 0) {
  y += Math.sin(T * 2) * 3 * s;
  cut(g, '#6A4428', .8, q => { q.moveTo(x - 7 * s, y - 24 * s); q.lineTo(x - 3 * s, y - 38 * s); q.lineTo(x + 1 * s, y - 27 * s); q.lineTo(x + 7 * s, y - 36 * s); q.lineTo(x + 8 * s, y - 22 * s); q.closePath(); });
  cloudP(g, x, y, s, o.rain ? '#E6EEF8' : '#FFFFFF', 1.4);
  if (o.rain) cut(g, 'rgba(120,150,200,0.25)', 0, q => q.roundRect(x - 30 * s, y + 8 * s, 62 * s, 9 * s, 4 * s));
  const e = o.eyes || 'open', ey = y + 2 * s;
  for (const sd of [-1, 1]) {
    const ex = x + sd * 9 * s;
    if (e === 'closed') stroke(g, INK, 1.8 * s, q => { q.moveTo(ex - 3.5 * s, ey); q.quadraticCurveTo(ex, ey + 3 * s, ex + 3.5 * s, ey); });
    else if (e === 'happy') stroke(g, INK, 1.8 * s, q => { q.moveTo(ex - 3.5 * s, ey + 1.5 * s); q.quadraticCurveTo(ex, ey - 3 * s, ex + 3.5 * s, ey + 1.5 * s); });
    else if (e === 'strain') stroke(g, INK, 1.8 * s, q => { q.moveTo(ex - 3.5 * sd * s, ey - 3 * s); q.lineTo(ex + 3 * sd * s, ey); q.lineTo(ex - 3.5 * sd * s, ey + 3 * s); });
    else { const b = e === 'wide' ? 1.25 : 1; cut(g, INK, 0, q => q.ellipse(ex, ey, 2.8 * s * b, 3.6 * s * b, 0, 0, TAU)); cut(g, '#FFFFFF', 0, q => q.arc(ex - 1 * s, ey - 1.4 * s, 1.1 * s, 0, TAU)); }
    cut(g, 'rgba(248,140,150,0.55)', 0, q => q.ellipse(ex + sd * 7 * s, ey + 7 * s, 4 * s, 2.3 * s, 0, 0, TAU));
  }
  if (o.mouth === 'o') cut(g, '#7A3040', 0, q => q.arc(x, ey + 9 * s, 2.2 * s, 0, TAU));
  else stroke(g, INK, 1.6 * s, q => { q.moveTo(x - 3.5 * s, ey + 7.5 * s); q.quadraticCurveTo(x, ey + 11 * s, x + 3.5 * s, ey + 7.5 * s); });
}
// an origami paper boat with a heart on its sail; with o.face it is him, with o.rider he sits in it and rows
function paperBoat(g, x, y, s, T, o = {}) {
  y += Math.sin(T * 2.2) * 2.5 * s; const tilt = Math.sin(T * 1.6) * .04;
  g.save(); g.translate(x, y); g.rotate(tilt);
  if (o.lantern) { const gr = g.createRadialGradient(36 * s, -34 * s, 2, 36 * s, -34 * s, 40 * s); gr.addColorStop(0, 'rgba(255,220,140,0.6)'); gr.addColorStop(1, 'rgba(255,220,140,0)'); g.fillStyle = gr; g.fillRect(-10 * s, -80 * s, 90 * s, 90 * s); }
  if (!o.rider) {
    cut(g, '#F2E8D4', 1.2, q => poly(q, [[-20 * s, -14 * s], [0, -54 * s], [20 * s, -14 * s]], 3));
    cut(g, 'rgba(0,0,0,0.06)', 0, q => poly(q, [[0, -54 * s], [20 * s, -14 * s], [0, -14 * s]], 4));
    paperHeart(g, 0, -28 * s, 8 * s, '#E8436E', .5);
    if (o.face) cut(g, '#6A4428', .6, q => { q.moveTo(-5 * s, -52 * s); q.lineTo(-2 * s, -64 * s); q.lineTo(1 * s, -55 * s); q.lineTo(6 * s, -62 * s); q.lineTo(5 * s, -50 * s); q.closePath(); });
  }
  let P = null;
  if (o.rider) P = person(g, 'me', -6 * s, 4 * s, s * .55, { sit: true, back: o.back, aR: 'out', aL: 'out', eyes: o.eyes || 'happy', mouth: 'smile', look: o.look ?? 1 }, T);
  cut(g, '#FBF4E6', 1.4, q => poly(q, [[-44 * s, -16 * s], [44 * s, -16 * s], [28 * s, 8 * s], [-28 * s, 8 * s]], 7));
  cut(g, 'rgba(0,0,0,0.05)', 0, q => poly(q, [[-44 * s, -16 * s], [-28 * s, 8 * s], [-14 * s, -16 * s]], 8));
  cut(g, 'rgba(0,0,0,0.05)', 0, q => poly(q, [[44 * s, -16 * s], [28 * s, 8 * s], [14 * s, -16 * s]], 9));
  if (o.face) {
    const e = o.eyes || 'open';
    for (const sd of [-1, 1]) {
      const ex = sd * 10 * s + (o.look || 0) * 3 * s, ey = -6 * s;
      if (e === 'happy') stroke(g, INK, 1.8 * s, q => { q.moveTo(ex - 3.5 * s, ey + 1.5 * s); q.quadraticCurveTo(ex, ey - 3 * s, ex + 3.5 * s, ey + 1.5 * s); });
      else if (e === 'closed') stroke(g, INK, 1.8 * s, q => { q.moveTo(ex - 3.5 * s, ey); q.quadraticCurveTo(ex, ey + 3 * s, ex + 3.5 * s, ey); });
      else { const b = e === 'wide' ? 1.25 : 1; cut(g, INK, 0, q => q.ellipse(ex, ey, 2.6 * s * b, 3.3 * s * b, 0, 0, TAU)); cut(g, '#FFFFFF', 0, q => q.arc(ex - .9 * s, ey - 1.3 * s, 1 * s, 0, TAU)); }
      cut(g, 'rgba(248,140,150,0.5)', 0, q => q.ellipse(ex + sd * 7 * s, ey + 6 * s, 3.6 * s, 2 * s, 0, 0, TAU));
    }
    stroke(g, INK, 1.5 * s, q => { q.moveTo(-3 * s, 0); q.quadraticCurveTo(0, 3 * s, 3 * s, 0); });
  }
  if (o.lantern) { stroke(g, INK, 1.4, q => { q.moveTo(30 * s, -16 * s); q.lineTo(36 * s, -44 * s); }); lanternP(g, 38 * s, -38 * s, .5 * s, false); }
  if (o.rider && P && o.oars !== false) { const sw = Math.sin(T * 3) * 8 * s; stroke(g, '#C89A60', 2.4 * s, q => { q.moveTo(36 * s, -20 * s); q.lineTo(60 * s, 10 * s + sw); }); }
  g.restore();
}
function bikeP(g, x, y, T, s = 1) {
  const wheel = wx => { cut(g, '#3A3A48', .8, q => { q.arc(x + wx * s, y - 18 * s, 18 * s, 0, TAU); q.arc(x + wx * s, y - 18 * s, 14 * s, 0, TAU, true); }); for (let i = 0; i < 3; i++) { const a = T * 9 + i * Math.PI / 3; stroke(g, '#A8A8BC', 1.2, q => { q.moveTo(x + wx * s - Math.cos(a) * 14 * s, y - 18 * s - Math.sin(a) * 14 * s); q.lineTo(x + wx * s + Math.cos(a) * 14 * s, y - 18 * s + Math.sin(a) * 14 * s); }); } };
  wheel(-36); wheel(36);
  stroke(g, '#4E8FCF', 4 * s, q => { q.moveTo(x - 36 * s, y - 18 * s); q.lineTo(x - 4 * s, y - 18 * s); q.lineTo(x + 16 * s, y - 44 * s); q.lineTo(x - 14 * s, y - 44 * s); q.lineTo(x - 36 * s, y - 18 * s); q.moveTo(x - 4 * s, y - 18 * s); q.lineTo(x - 14 * s, y - 44 * s); q.moveTo(x + 16 * s, y - 44 * s); q.lineTo(x + 36 * s, y - 18 * s); q.moveTo(x + 16 * s, y - 44 * s); q.lineTo(x + 22 * s, y - 58 * s); });
  cut(g, INK, .5, q => q.roundRect(x - 22 * s, y - 50 * s, 18 * s, 5 * s, 2)); cut(g, '#8A8AA0', .5, q => q.rect(x - 52 * s, y - 44 * s, 26 * s, 4 * s)); cut(g, INK, .5, q => q.rect(x + 16 * s, y - 60 * s, 14 * s, 4 * s));
  cut(g, '#FFF2C0', .4, q => q.arc(x + 32 * s, y - 50 * s, 4 * s, 0, TAU));
}
function firework(g, t, k, i, cx, cy, col) {
  const a = t - k; if (a < 0) return;
  if (a < .3) { cut(g, '#FFF0C0', 0, q => q.arc(cx, cy + (1 - a / .3) * 200, 2.5, 0, TAU)); return; }
  const b = a - .3; if (b > 1.8) return;
  g.save(); g.globalAlpha = clamp(1.6 - b);
  for (let sI = 0; sI < 22; sI++) { const an = sI / 22 * TAU + i, r = 80 * eout(b / 1.2), x = cx + Math.cos(an) * r, y = cy + Math.sin(an) * r + b * b * 22; cut(g, col, .4, q => { q.save(); q.translate(x, y); q.rotate(an + b * 3); q.rect(-4, -1.5, 8, 3); q.restore(); }); if (sI % 2) paperStar(g, cx + Math.cos(an) * r * .55, cy + Math.sin(an) * r * .55 + b * b * 14, 3, '#FFFFFF', 0, an); }
  g.restore();
}
function fireworksIn(g, t, a, b, area) { const cols = ['#FF7AA0', '#FFD860', '#8FE0F0', '#C0A0F8', '#FFA06A']; kicksIn(a, Math.min(b, t)).slice(-6).forEach(k => { const i = Math.round(k * 100); firework(g, t, k, i, area[0] + H(i) * (area[2] - area[0]), area[1] + H(i + 1) * (area[3] - area[1]), cols[i % 5]); }); }
function rainDrops(g, t, n, x0, x1, y0, y1, col = '#6A9AE0', seed = 1, sp = 260) { for (let i = 0; i < n; i++) { const y = y0 + ((t * sp * (1 + H(i + seed) * .4) + H(i * 7 + seed) * (y1 - y0)) % (y1 - y0)), x = x0 + H(i * 3 + seed) * (x1 - x0); cut(g, col, .3, q => { q.moveTo(x, y - 7); q.quadraticCurveTo(x + 3.4, y + 1, x, y + 3.6); q.quadraticCurveTo(x - 3.4, y + 1, x, y - 7); }); } }
function petalsP(g, t, n, cols, seed = 3, wind = 1, sp = 1) { for (let i = 0; i < n; i++) { const y = (t * (24 + 18 * H(i + seed)) * sp + H(i * 5 + seed) * VH) % VH, x = ((H(i * 3 + seed) * VW + Math.sin(t * 1.3 + i) * 24 + t * 30 * wind * sp) % VW + VW) % VW; cut(g, cols[i % cols.length], .4, q => q.ellipse(x, y, 4.5, 2.6, t * 2 + i, 0, TAU)); } }
function windP(g, t, n, seed = 5, col = 'rgba(255,255,255,0.85)', y0 = 60, y1 = 420) { for (let i = 0; i < n; i++) { const x = ((t * 640 + H(i * 9 + seed) * 1800) % 1800) - 400, y = y0 + H(i + seed) * (y1 - y0); stroke(g, col, 2.2, q => { q.moveTo(x, y); q.bezierCurveTo(x + 40, y - 10, x + 70, y + 8, x + 110 + H(i) * 60, y - 4); }); } }
function sparkleP(g, x, y, r, col = '#FFFFFF', t = 0) { cut(g, col, .2, q => starPath(q, x, y, r, 4, .3, t)); }
// a big picture book of their story; page = how far the pages have flipped (0..3); close = 0..1
function storyBook(g, t, cx, cy, page, o = {}) {
  const w = 600, h = 300, close = o.close || 0, cw = w * (1 - close * .5), lx = cx - cw / 2, y = cy - h / 2;
  cut(g, '#C85A44', 2, q => q.roundRect(lx - 10, y - 8, cw + 20, h + 18, 10));
  if (close > .98) { paperHeart(g, cx, cy, 40, '#FFD860', 1); return; }
  cut(g, '#FBF6EA', 1, q => q.rect(lx, y, cw, h));
  const gr = g.createLinearGradient(cx - 30, 0, cx + 30, 0); gr.addColorStop(0, 'rgba(120,90,60,0)'); gr.addColorStop(.5, 'rgba(120,90,60,0.18)'); gr.addColorStop(1, 'rgba(120,90,60,0)'); g.fillStyle = gr; g.fillRect(cx - 30, y, 60, h);
  if (cw < 420) return;
  const pic = (px, py, pw, ph, n) => {
    g.save(); g.beginPath(); g.rect(px, py, pw, ph); g.clip();
    gradV(g, [['#A8DCF4', '#E2F4FA'], ['#C8DCEE', '#EEF4FA'], ['#FFD8A8', '#FFF0D8'], ['#FBF6EA', '#FBF6EA']][n], py, py + ph, px, pw);
    if (n === 0) { paperRect(g, px, py + ph - 40, pw, 40, '#EFDCB8', 1); person(g, 'me', px + pw * .34, py + ph - 14, .62, { eyes: 'wide', mouth: 'o' }, t); person(g, 'you', px + pw * .68, py + ph - 14, .62, { eyes: 'happy' }, t); sunhat(g, px + pw * .34, py + ph - 92, .55); }
    if (n === 1) { paperRect(g, px, py + ph - 40, pw, 40, '#9CCF7E', 1); cloudKid(g, px + pw / 2, py + 50, .8, { eyes: 'happy' }, t); rainDrops(g, t, 10, px + pw / 2 - 30, px + pw / 2 + 30, py + 70, py + ph - 40, '#6A9AE0', 3, 120); paperHeart(g, px + pw / 2, py + ph - 24, 12, '#6FB07A', .6); }
    if (n === 2) { paperRect(g, px, py + ph - 50, pw, 50, '#F4DDAE', 1); paperRect(g, px, py + ph - 80, pw, 30, '#62AEDD', .6); iceCream(g, px + pw * .35, py + ph - 80, '#FF9AB8'); iceCream(g, px + pw * .65, py + ph - 80, '#8FE0F0'); }
    g.restore();
  };
  const shown = Math.min(3, Math.floor(page)), pw = cw / 2 - 60, ph = h - 70;
  if (shown < 3) { pic(lx + 30, y + 35, pw, ph, shown); pic(cx + 30, y + 35, pw, ph, Math.min(2, shown + 1)); }
  else { pic(lx + 30, y + 35, pw, ph, 2); qmarkP(g, cx + cw / 4, cy, 120, '#E2D6C2', .6); }
  const f = page % 1;
  if (page < 3 && f > 0) { const ww = cw / 2 * Math.abs(1 - 2 * f), px = f < .5 ? cx : cx - ww; cut(g, '#FFFFFF', 1.6, q => q.rect(px, y - 4, ww, h + 8)); }
}

// ---------------------------------------------------------------- shots
const SCENES = {
  title(g, t, s) {
    const u = local(t, s);
    seaside(g, t, 'day');
    for (let i = 0; i < 4; i++) seagull(g, ((u * 44 + i * 120) % 1120) - 80, 130 + i * 20 + Math.sin(t * 2 + i) * 6, t + i, .9);
    if (u > 5.4) person(g, 'me', lerp(-40, 330, seg(u, 5.5, 10.3)), 470, 1.4, { walk: step(t), look: 1, eyes: 'happy', mouth: 'smile', aL: 'swing', aR: 'swing' }, t);
    const pop = eout(seg(u, 1.6, 2.2));
    if (pop > 0) { g.save(); g.translate(480, 170); g.scale(pop, pop); g.rotate(-.04); paperText(g, '小宇', 0, 0, 120, '#E8735A', { edge: '#FFFFFF', d: 2 }); g.restore(); }
    if (u > 3.6) { g.save(); g.globalAlpha = seg(u, 3.6, 4.2); paperText(g, '张震岳 · 纸片 MV', 480, 250, 30, '#3A5A8A', { edge: '#FFFFFF' }); g.restore(); }
    fade(g, '#1A1418', 1 - seg(u, .2, 2));
  },
  surprise(g, t, s) {
    const u = local(t, s), land = 3.4;
    seaside(g, t, 'day');
    const wx = lerp(170, 420, eout(seg(u, 0, 2.2)));
    const P = person(g, 'me', wx, 470, 1.7, { walk: u < 2.2 ? step(t) : null, look: u > 1.6 && u < land ? 1 : 0, eyes: u > land ? 'wide' : 'open', mouth: u > land ? 'open' : 'smile', aL: u > land ? 'up' : 'swing', aR: u < 2.2 ? 'swing' : 'down' }, t);
    if (u > 1.1 && u < land + .3) windP(g, t, 8, 3);
    if (P) {
      const f = eio(seg(u, 1.2, land));
      const hx = u < land ? lerp(1040, P.top[0], f) + Math.sin(u * 5) * 60 * (1 - f) : P.top[0], hy = u < land ? lerp(140, P.top[1] + 6, f) - Math.sin(f * Math.PI) * 90 : P.top[1] + 6;
      if (u > 1.2) sunhat(g, hx, hy, 1.1, u < land ? Math.sin(u * 9) * .6 : -.08);
      if (u > land) { const a = eout(seg(u, land, land + .25)); g.save(); g.translate(P.top[0] + 70, P.top[1] - 30); g.scale(a, a); paperText(g, '！', 0, 0, 64, '#F2BE4E', { edge: '#FFFFFF' }); g.restore(); for (let i = 0; i < 4; i++) sparkleP(g, P.top[0] - 80 + i * 50, P.top[1] - 20 + (i % 2) * 30, 7 + (i % 2) * 4, '#FFFFFF', t); }
    }
  },
  meet(g, t, s) {
    const u = local(t, s), worn = u > 3.4;
    seaside(g, t, 'day');
    const slow = seg(u, 1.6, 2.4);
    if (slow > 0) petalsP(g, t * .3, 30, ['#FFB8CC', '#FFFFFF', '#FFD8E4'], 4, .4);
    const A = person(g, 'me', 400, 470, 1.7, { aR: worn ? 'down' : 'out', eyes: u > 1.6 ? 'happy' : 'wide', mouth: 'smile', blush: u > 2, look: 1 }, t);
    const B = person(g, 'you', lerp(1040, 600, eout(seg(u, 0, 1.6))), 470, 1.7, { walk: u < 1.6 ? beatPos(t) / 2 : null, aL: u > 2.4 && !worn ? 'reach' : 'down', eyes: u > 2 ? 'happy' : 'open', mouth: 'smile', blush: u > 2, look: -1 }, t);
    if (A && !worn) sunhat(g, A.R[0] + 14, A.R[1] - 4, 1.1, -.2);
    if (B && worn) sunhat(g, B.top[0], B.top[1] + 6, 1.1, .06);
    if (slow > 0) for (let i = 0; i < 12; i++) if ((Math.floor(t * 3 + i) % 3) && H(i + 9) < slow) sparkleP(g, 260 + H(i) * 440 + Math.sin(t * .4 + i) * 10, 130 + H(i + 4) * 200, 5 + (i % 3) * 2, i % 3 ? '#FFFFFF' : '#FFD0E0', t * .3);
    if (u > 2.6) { const a = eout(seg(u, 2.6, 2.9)); paperHeart(g, 500, 230 + Math.sin(t * 3) * 4, 18 * a, '#F26A8A', 1.2); }
  },
  eyes(g, t, s) {
    const u = local(t, s);
    sky(g, ['#8ACCF0', '#C4E6F6', '#F0F9FC']);
    clouds(g, t, 5, 40, 420, '#FFFFFF', 10, 9);
    const blink = u > 3.1 && u < 3.32;
    const P = person(g, 'you', 480, 980, 7.4, { eyes: blink ? 'closed' : 'sparkle', mouth: 'smile', blush: true }, t);
    if (P && !blink) for (const sd of [-1, 1]) {
      // the sky and a tiny him reflected in each eye
      const ex = P.face[0] + sd * 9 * 7.4, ey = P.face[1] + 2 * 7.4;
      cloudP(g, ex - 4, ey - 12, .28, 'rgba(255,255,255,0.85)', 0);
      cut(g, '#F4C04E', 0, q => q.roundRect(ex + 2, ey + 6, 7, 10, 2)); cut(g, '#F6D2B4', 0, q => q.arc(ex + 5.5, ey + 2, 4, 0, TAU)); cut(g, '#6A4428', 0, q => q.arc(ex + 5.5, ey - .5, 4, Math.PI, 0));
      if (Math.floor(t * 3 + sd) % 4 === 0) sparkleP(g, ex + 30, ey - 40, 10, '#FFFFFF', t);
    }
    for (let i = 0; i < 8; i++) if (Math.floor(t * 4 + i) % 3 === 0) sparkleP(g, 100 + H(i) * 760, 60 + H(i + 3) * 200, 6 + (i % 3) * 3, '#FFFFFF', t);
  },
  dream(g, t, s) {
    const u = local(t, s);
    room(g);
    cut(g, '#1A2050', 1.4, q => q.rect(660, 60, 200, 160)); starsP(g, t, 14, 150, 5, 670, 850); moonP(g, 800, 110, 20);
    paperRect(g, 656, 136, 208, 8, '#8A6A5A', 1, 3); paperRect(g, 756, 56, 8, 168, '#8A6A5A', 1, 4);
    paperRect(g, 110, 300, 26, 160, '#8A5A44', 1.4, 5); paperRect(g, 120, 360, 480, 70, '#8A5A44', 1.4, 6);
    cut(g, '#FBF4E6', 1.2, q => q.roundRect(140, 318, 120, 50, 20));
    g.save(); g.beginPath(); g.rect(0, 0, VW, 352); g.clip(); person(g, 'me', 205, 470, 1.6, { eyes: 'closed', mouth: 'smile', blush: u > 1.5 }, t); g.restore();
    cut(g, '#6AA0D8', 1.6, q => { q.moveTo(150, 352); q.quadraticCurveTo(380, 336, 600, 352); q.lineTo(600, 420); q.lineTo(150, 420); q.closePath(); });
    for (let x = 170; x < 600; x += 60) cut(g, '#5A8CC8', 0, q => q.rect(x, 356, 26, 60));
    for (let i = 0; i < 3; i++) { const p = (u * .6 + i / 3) % 1; g.save(); g.globalAlpha = Math.sin(p * Math.PI); paperText(g, 'Z', 280 + p * 60 + i * 8, 300 - p * 80, 22 + i * 8, '#FFFFFF'); g.restore(); }
    const gr = eout(seg(u, .3, 1.1));
    if (gr > 0) {
      g.save(); g.translate(500, 170); g.scale(gr, gr);
      cut(g, '#30347A', 2, q => { q.arc(-110, 10, 70, 0, TAU); q.arc(-30, -40, 86, 0, TAU); q.arc(80, -20, 80, 0, TAU); q.arc(120, 40, 60, 0, TAU); q.arc(0, 50, 80, 0, TAU); });
      if (gr > .95) { starsP(g, t, 18, 120, 9, -160, 160); person(g, 'you', 0, 100, 1.05, { eyes: 'sparkle', mouth: 'smile', blush: true, aR: 'wave' }, t); }
      g.restore();
      for (let i = 0; i < 3; i++) paperCircle(g, 350 - i * 30, 280 + i * 12, 10 - i * 3, '#30347A', 1, i);
    }
  },
  becloud(g, t, s) {
    const u = local(t, s), turn = 1.3;
    sky(g, TIMES.day.sky);
    clouds(g, t, 4, 40, 200, '#FFFFFF', 7, 11);
    paperBlob(g, 480, 760, 560, 360, '#7DB868', 1.8, 3, .01);
    paperBlob(g, 480, 780, 540, 350, '#9CCF7E', 1.4, 4, .01);
    for (let i = 0; i < 18; i++) { const x = 140 + H(i) * 680, y = 440 + H(i + 4) * 90; for (let k = 0; k < 5; k++) cut(g, ['#FFFFFF', '#FFD860', '#FF8FB0'][i % 3], .3, q => q.arc(x + Math.cos(k / 5 * TAU) * 3.5, y + Math.sin(k / 5 * TAU) * 3.5, 3, 0, TAU)); }
    if (u < turn) person(g, 'me', 480, 450, 1.7, { aL: 'up', aR: 'up', eyes: 'closed', mouth: 'smile' }, t);
    const burst = seg(u, turn - .3, turn + .6);
    if (burst > 0 && burst < 1) for (let i = 0; i < 18; i++) { const a = i / 18 * TAU, r = burst * 150; g.save(); g.globalAlpha = 1 - burst; paperStar(g, 480 + Math.cos(a) * r, 330 + Math.sin(a) * r * .7, 9, i % 2 ? '#FFFFFF' : '#FFE08A', .5, a); g.restore(); }
    if (u >= turn) cloudKid(g, 480 + Math.sin(u * 1.5) * 20, lerp(350, 160, eio(seg(u, turn + .2, 5.2))), 2.2, { eyes: u < turn + 1 ? 'wide' : 'happy' }, t);
    fade(g, '#FFFFFF', Math.max(0, 1 - Math.abs(u - turn) / .25) * .9);
  },
  drift(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0;
    sky(g, TIMES.day.sky, 420);
    windP(g, t, 7, 9, 'rgba(255,255,255,0.8)', 40, 260);
    paperRect(g, -10, 400, VW + 20, 150, '#9CCF7E', 1.6, 2);
    paperRect(g, 600, 240, 280, 170, '#FBF4E6', 1.6, 3);
    cut(g, '#4E8FCF', 1.4, q => poly(q, [[580, 246], [740, 150], [900, 246]], 4));
    for (const wx of [630, 790]) { paperRect(g, wx, 280, 56, 46, '#B4DCF2', .8, wx); cut(g, '#FBF4E6', 0, q => { q.rect(wx + 26, 280, 4, 46); q.rect(wx, 301, 56, 4); }); }
    paperRect(g, 712, 330, 50, 80, '#5A9AD8', 1, 7);
    for (let i = 0; i < 10; i++) for (let k = 0; k < 5; k++) cut(g, ['#FF8FB0', '#FFD860', '#FFFFFF'][i % 3], .3, q => q.arc(600 + i * 30 + Math.cos(k / 5 * TAU) * 4, 404 + Math.sin(k / 5 * TAU) * 4, 3.5, 0, TAU));
    for (let x = 0; x < 560; x += 28) paperRect(g, x, 372, 10, 36, '#FFFFFF', .8, x); paperRect(g, -10, 384, 570, 6, '#FFFFFF', .6, 9);
    const cx = v => v < 1.6 ? lerp(-100, 400, eout(v / 1.6)) : v < 3.4 ? lerp(400, 500, (v - 1.6) / 1.8) : lerp(500, 1120, Math.pow(seg(v, 3.4, d), 1.6));
    person(g, 'you', 460, 480, 1.3, { aR: u > 1.4 && u < 4 ? 'wave' : 'down', eyes: 'open', mouth: 'smile', look: clamp((cx(u) - 460) / 120, -1, 1) }, t);
    cloudKid(g, cx(u), 140, 1.6, { eyes: u > 1.8 && u < 3.6 ? 'strain' : u > 3.6 ? 'closed' : 'open', mouth: u > 1.8 && u < 3.6 ? 'o' : 'smile' }, t);
  },
  drizzle(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0;
    sky(g, ['#8CA8D4', '#B4CCE8', '#E6EEF8'], 420);
    if (u > d - 1.9) { const a = eout(seg(u, d - 1.9, d - .5)); ['#E8735A', '#F2A050', '#F2D860', '#8CC57A', '#6AAAD8', '#A88AD8'].forEach((c, i) => cut(g, c, .6, q => { q.arc(480, 470, 380 - i * 14, Math.PI, Math.PI + Math.PI * a); q.arc(480, 470, 366 - i * 14, Math.PI + Math.PI * a, Math.PI, true); q.closePath(); })); }
    paperRect(g, -10, 400, VW + 20, 150, '#9CCF7E', 1.6, 2);
    const burst = .4 + .6 * kickPulse(t, 3);
    rainDrops(g, t, Math.round(60 * seg(u, .5, 1.5) * burst), 340, 620, 200, 470, '#5A8AD8', 3, 280);
    cloudKid(g, 480, 150, 3, { rain: true, eyes: u < 1.4 ? 'strain' : 'happy', mouth: u < 1.4 ? 'o' : 'smile' }, t);
    person(g, 'you', 480, 480, 1.7, { aL: 'up', aR: 'up', eyes: 'closed', mouth: 'smile', blush: true }, t);
  },
  bloom(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, cx = 480, cy = 330, S = 150;
    sky(g, ['#A6C8EC', '#D0E4F6', '#F4F8FC']);
    rainDrops(g, t, 60, 300, 660, 120, 480, '#5A8AD8', 5, 300);
    cloudKid(g, 480, 96, 2.2, { rain: true, eyes: 'happy' }, t);
    // her heart is a field: dry earth at first, then green from the middle out, then flowers
    cut(g, '#B88A5A', 2, q => heartPath(q, cx, cy, S));
    for (let i = 0; i < 14; i++) stroke(g, '#9A6E44', 2, q => { const x = cx + (H(i) - .5) * S * 1.4, y = cy + (H(i + 3) - .6) * S * 1.1; q.moveTo(x, y); q.lineTo(x + 14, y + 6); q.lineTo(x + 22, y + 2); });
    const grow = eio(seg(u, .3, d - .8));
    if (grow > 0) { cut(g, '#7DB868', 1.2, q => heartPath(q, cx, cy + (1 - grow) * 10, S * grow * .98)); cut(g, '#9CCF7E', .8, q => heartPath(q, cx, cy + (1 - grow) * 14, S * grow * .82)); }
    for (let i = 0; i < 40; i++) {
      const fx = (H(i) - .5) * 1.6, fy = (H(i + 9) - .55) * 1.4, r = Math.hypot(fx, fy * 1.2);
      if (r > grow * .9 || !(Math.pow(fx * fx + (-fy + .15) * (-fy + .15) - 1, 3) - fx * fx * Math.pow(-fy + .15, 3) <= 0)) continue;
      const a = eout(seg(grow, r / .9, r / .9 + .15)), x = cx + fx * S * .8, y = cy + fy * S * .8;
      stroke(g, '#4E8A44', 2, q => { q.moveTo(x, y + 8); q.lineTo(x, y + 8 - 10 * a); });
      for (let k = 0; k < 5; k++) cut(g, ['#FF8FB0', '#FFFFFF', '#FFD860', '#E8436E'][i % 4], .3, q => q.arc(x + Math.cos(k / 5 * TAU) * 4 * a, y - 2 - 10 * a + 10 + Math.sin(k / 5 * TAU) * 4 * a - 8, 3.4 * a, 0, TAU));
    }
  },
  future(g, t, s) {
    const u = local(t, s), turn = u > 2.6;
    beach(g, t, 'day');
    for (let i = 0; i < 4; i++) { const x = 140 + i * 230 + Math.sin(t * .6 + i) * 10; cloudP(g, x, 200, 1.7, 'rgba(255,255,255,0.92)', 1); qmarkP(g, x, 196 + Math.sin(t + i) * 3, 58, '#9AB6D8', .6); }
    person(g, 'me', 430, 486, 1.7, turn ? { look: 1, eyes: 'happy', mouth: 'open', aL: 'out', aR: 'out' } : { back: true }, t);
    person(g, 'you', 540, 486, 1.7, turn ? { look: -1, eyes: 'happy', mouth: 'smile', blush: true, aL: 'out', aR: 'out' } : { back: true }, t);
  },
  fun(g, t, s) {
    const u = local(t, s);
    beach(g, t, 'day');
    for (let i = 0; i < 3; i++) seagull(g, ((u * 50 + i * 140) % 1120) - 80, 110 + i * 20, t + i, .8);
    const hop = i => (beatPhase(t + i * .25) < .3 ? -12 : 0);
    const A = person(g, 'me', 380, 486, 1.7, { aR: 'up', eyes: 'happy', mouth: 'grin', dy: hop(0) }, t);
    const B = person(g, 'you', 580, 486, 1.7, { aL: 'up', eyes: 'happy', mouth: 'smile', blush: true, dy: hop(1) }, t);
    if (A) iceCream(g, A.R[0], A.R[1] - 10, '#FF9AB8');
    if (B) iceCream(g, B.L[0], B.L[1] - 10, '#8FE0F0');
    const p = (u * .8) % 1, side = Math.floor(u * .8) % 2, bx = lerp(side ? 580 : 380, side ? 380 : 580, p), by = 250 - Math.sin(p * Math.PI) * 110;
    g.save(); g.translate(bx, by); g.rotate(u * 4);
    cut(g, '#FFFFFF', 1.4, q => q.arc(0, 0, 20, 0, TAU)); cut(g, '#E8735A', 0, q => { q.moveTo(0, 0); q.arc(0, 0, 20, 0, TAU / 3); q.closePath(); }); cut(g, '#4E8FCF', 0, q => { q.moveTo(0, 0); q.arc(0, 0, 20, TAU / 3, TAU * 2 / 3); q.closePath(); }); cut(g, '#F2BE4E', 0, q => q.arc(0, 0, 5, 0, TAU));
    g.restore();
  },
  ending(g, t, s) {
    const u = local(t, s);
    sky(g, ['#FFD49A', '#FFE8C0', '#FFF6E4']);
    for (let i = 0; i < 14; i++) if (Math.floor(t * 4 + i) % 3) sparkleP(g, H(i) * VW, H(i + 3) * 400, 5, '#FFFFFF', t);
    paperRect(g, -10, 470, VW + 20, 80, '#E8C890', 1.6, 2);
    storyBook(g, t, 480, 220, Math.min(3, u * .75));
    const done = u > 4;
    person(g, 'me', 210, 500, 1.2, { look: 1, eyes: done ? 'happy' : 'open', mouth: done ? 'smile' : 'o', aL: done ? 'out' : 'down', aR: done ? 'out' : 'down' }, t);
    person(g, 'you', 750, 500, 1.2, { look: -1, eyes: done ? 'happy' : 'open', mouth: done ? 'smile' : 'o', aL: done ? 'out' : 'down', aR: done ? 'out' : 'down' }, t);
  },
  missing(g, t, s) {
    const u = local(t, s);
    sky(g, TIMES.night.sky, 440); starsP(g, t, 70, 420, 11);
    // the stars are joined by thread, one stitch at a time, into her
    const pts = [[660, 60], [632, 76], [620, 108], [628, 140], [644, 160], [676, 160], [692, 140], [700, 108], [688, 76], [660, 60], [612, 128], [600, 200], [628, 184], [608, 280], [712, 280], [692, 184], [720, 200], [708, 128]];
    const n = Math.min(pts.length - 1, u * 4.2);
    for (let i = 0; i < Math.floor(n); i++) if (i !== 9) stroke(g, 'rgba(200,214,255,0.8)', 1.6, q => { q.moveTo(pts[i][0], pts[i][1]); q.lineTo(pts[i + 1][0], pts[i + 1][1]); });
    const k = Math.floor(n); if (n % 1 > 0 && k !== 9 && k < pts.length - 1) { const a = pts[k], b = pts[k + 1], f = n % 1; stroke(g, 'rgba(200,214,255,0.8)', 1.6, q => { q.moveTo(a[0], a[1]); q.lineTo(lerp(a[0], b[0], f), lerp(a[1], b[1], f)); }); }
    pts.forEach(([x, y], i) => { if (i <= n + 1) paperStar(g, x, y, 7 + (Math.floor(t * 3 + i) % 3 === 0 ? 2 : 0), '#FFF4C8', .5, i); });
    if (n > 16) { paperCircle(g, 692, 70, 9, '#FFFFFF', .5, 3); }
    paperRect(g, -10, 430, VW + 20, 120, '#3A4060', 1.6, 2); for (let x = 0; x < VW; x += 60) cut(g, '#323858', 0, q => q.rect(x, 432, 2, 110));
    person(g, 'me', 300, 460, 1.7, { sit: true, eyes: n > 16 ? 'happy' : 'open', mouth: 'smile', blush: n > 16, look: 1 }, t);
  },
  game(g, t, s) {
    const u = local(t, s), off = u > 2.8, cx = 600;
    gradV(g, ['#1E1438', '#2E2050']); for (let i = 0; i < 6; i++) cut(g, ['#FF6EC8', '#6EE0FF', '#FFE06E'][i % 3], .6, q => q.roundRect(40 + i * 160, 60, 100, 6, 3));
    paperRect(g, -10, 420, VW + 20, 130, '#2E2246', 1.6, 2);
    cut(g, '#7A4AC0', 2, q => q.roundRect(cx - 110, 100, 220, 340, 14)); cut(g, '#9A6AE0', 0, q => q.roundRect(cx - 110, 100, 220, 34, 14));
    paperText(g, 'GAME', cx, 118, 26, '#FFE06E', { d: .4 });
    cut(g, '#1A1A30', 1, q => q.roundRect(cx - 86, 146, 172, 126, 8));
    if (!off) {
      const gr = g.createRadialGradient(cx, 210, 10, cx, 210, 130); gr.addColorStop(0, '#2A4A8A'); gr.addColorStop(1, '#14204A'); g.fillStyle = gr; g.fillRect(cx - 82, 150, 164, 118);
      for (let i = 0; i < 3; i++) paperHeart(g, cx - 44 + i * 44, 190, 12, '#FF6E9A', .5);
      if (Math.floor(t * 3) % 2) paperText(g, 'PLAY?', cx, 244, 24, '#FFFFFF', { d: .3 });
    } else if (u < 3.05) { for (let i = 0; i < 120; i++) cut(g, '#FFFFFF', 0, q => q.rect(cx - 82 + H(i * 7 + Math.round(t * 60)) * 160, 150 + H(i * 3 + Math.round(t * 60)) * 114, 4, 2)); }
    else { const w = 164 * clamp(1 - (u - 3.05) * 3); if (w > 0) cut(g, '#FFFFFF', 0, q => q.rect(cx - w / 2, 208, w, 3)); }
    cut(g, '#5A3A90', 1, q => q.rect(cx - 110, 300, 220, 50)); stroke(g, INK, 4, q => { q.moveTo(cx - 60, 324); q.lineTo(cx - 60, 304); }); paperCircle(g, cx - 60, 302, 8, '#E8436E', .5, 1); paperCircle(g, cx + 20, 324, 9, '#6EE0FF', .5, 2); paperCircle(g, cx + 54, 324, 9, '#FFE06E', .5, 3);
    const pullX = off ? lerp(cx + 150, cx + 240, seg(u, 2.6, 2.9)) : cx + 150;
    stroke(g, INK, 4, q => { q.moveTo(cx + 110, 410); q.quadraticCurveTo(cx + 130, 440, pullX - 12, 432); });
    cut(g, '#9A9AB0', .8, q => q.roundRect(pullX - 14, 422, 18, 20, 3)); cut(g, '#E8E8F0', 1, q => q.rect(cx + 160, 410, 22, 34));
    const shake = u > 1.6 && u < 2.6 ? (Math.floor(u * 6) % 2 ? 1 : -1) : 1;
    if (!off) { const gr2 = g.createRadialGradient(300, 330, 10, 300, 330, 150); gr2.addColorStop(0, 'rgba(110,224,255,0.25)'); gr2.addColorStop(1, 'rgba(110,224,255,0)'); g.fillStyle = gr2; g.fillRect(150, 180, 300, 300); }
    person(g, 'me', off ? cx + 250 : 300, 486, 1.7, { eyes: off ? 'happy' : 'open', mouth: off ? 'smile' : 'flat', look: shake, aR: u > 2.4 && u < 3.2 ? 'out' : 'down', walk: u > 2.0 && u < 2.6 ? beatPos(t) / 2 : null }, t);
  },
  sincere(g, t, s) {
    const u = local(t, s);
    seaside(g, t, 'sunset');
    const A = person(g, 'me', 390, 490, 2.1, { aL: 'hold', aR: 'hold', eyes: 'open', mouth: 'smile', look: 1, blush: true }, t);
    person(g, 'you', 620, 490, 2.1, { eyes: u > 1.5 ? 'sparkle' : 'wide', mouth: u > 2 ? 'smile' : 'o', blush: u > 1.5, look: -1 }, t);
    if (A) { const b = 1 + .1 * Math.sin(t * 7), hx = (A.L[0] + A.R[0]) / 2, hy = (A.L[1] + A.R[1]) / 2 - 24; const gr = g.createRadialGradient(hx, hy, 4, hx, hy, 90); gr.addColorStop(0, 'rgba(255,190,200,0.55)'); gr.addColorStop(1, 'rgba(255,190,200,0)'); g.fillStyle = gr; g.fillRect(hx - 90, hy - 90, 180, 180); paperHeart(g, hx, hy, 30 * b, '#E8436E', 1.6); }
  },
  unsaid(g, t, s) {
    const u = local(t, s), back = seg(u, 2.2, 3.2);
    seaside(g, t, 'day');
    person(g, 'you', 820, 410, 1, { back: true }, t);
    const A = person(g, 'me', 400, 494, 2.1, { eyes: u > 3.4 ? 'closed' : 'open', mouth: u > 3.2 ? 'none' : 'flat', look: 1 }, t);
    if (A) {
      if (back < 1) { const sc = 1 - back; g.save(); g.translate(A.face[0] + 110, A.face[1] - 120 + back * 100); g.scale(sc, sc); bubbleP(g, -80, -60, 160, 110, -60, 90); padlockP(g, 0, -10, 2.2); g.restore(); }
      if (u > 3.2) { const mx = A.face[0], my = A.face[1] + 12 * 2.1, z = seg(u, 3.2, 3.9); cut(g, '#D8D8E4', .6, q => q.roundRect(mx - 22, my - 5, 44, 10, 4)); for (let x = -18; x < 18; x += 4) cut(g, '#9A9AB0', 0, q => q.rect(mx + x, my - 2, 2, 4)); cut(g, '#F2BE4E', .6, q => q.roundRect(mx - 22 + z * 38, my - 8, 8, 16, 2)); }
    }
  },
  quiz(g, t, s) {
    const u = local(t, s), fall = seg(u, 1.8, 4.6);
    gradV(g, ['#2E2260', '#5A3A8A', '#9A6AB0']);
    starsP(g, t, 30, 500, 13, 0, VW, '#D8C0F0');
    cut(g, '#8A6A4A', 2, q => q.roundRect(270, 30, 420, 230, 8)); cut(g, '#2E5A44', 0, q => q.rect(282, 42, 396, 206));
    qmarkP(g, 480, 76, 44, '#F4F4E8', 0);
    ['A', 'B', 'C', 'D'].forEach((c, i) => { const x = 330 + (i % 2) * 200, y = 140 + Math.floor(i / 2) * 60; stroke(g, '#F4F4E8', 2.4, q => q.rect(x - 12, y - 12, 24, 24)); if (Math.floor(t * 4) % 4 === i) cut(g, '#FFE08A', 0, q => q.rect(x - 7, y - 7, 14, 14)); g.save(); g.font = `32px ${FONT}`; g.fillStyle = '#F4F4E8'; g.textBaseline = 'middle'; g.fillText(c, x + 28, y + 2); g.restore(); });
    const open = eout(seg(u, 1.4, 1.9));
    paperRect(g, -10, 430, VW + 20, 120, '#3E2E66', 1.6, 2);
    if (open > 0) cut(g, '#100A22', 0, q => q.ellipse(560, 450, 140 * open, 26 * open, 0, 0, TAU));
    g.save(); if (fall > 0) { g.beginPath(); g.rect(0, 0, VW, 452); g.clip(); }
    person(g, 'you', 560, 486 + fall * fall * 300, 1.7, { eyes: fall > 0 ? 'wide' : 'open', mouth: fall > 0 ? 'open' : 'flat', aL: fall > 0 ? 'up' : 'down', aR: fall > 0 ? 'up' : 'down', look: -1 }, t);
    g.restore();
    if (fall > 0) ['A', 'B', 'C', 'D'].forEach((c, i) => { const a = fall - i * .08; if (a > 0 && a < 1) paperText(g, c, 500 + i * 40, 320 + a * 140 + Math.sin(t * 6 + i) * 8, 34, '#FFE08A', { d: .8 }); });
    person(g, 'me', 220, 490, 1.7, { eyes: fall > 0 ? 'wide' : 'open', mouth: fall > 0 ? 'open' : 'flat', look: 1, aR: fall > .2 ? 'shh' : 'down' }, t);
  },
  selfish(g, t, s) {
    const u = local(t, s), grow = eio(seg(u, .2, 3)) * (1 - eio(seg(u, 3.6, 6.2))), push = u > 3.2;
    seaside(g, t, 'sunset');
    person(g, 'you', 830, 410, 1, { back: true }, t);
    person(g, 'me', 380 - grow * 30, 490, 1.8 + 1.4 * grow, { tint: '#2A2238', tintEyes: '#FFFFFF', aR: 'reach', alpha: .55 + .35 * grow, look: 1 }, t);
    person(g, 'me', 480, 490, 1.8, { eyes: push ? 'closed' : 'sad', mouth: 'flat', look: push ? -1 : 0, aL: push ? 'stop' : 'down' }, t);
  },
  hide(g, t, s) {
    const u = local(t, s), p = eio(seg(u, 0, 2.6)), A = TIMES.sunset, B = TIMES.night;
    sky(g, skyMix(A.sky, B.sky, p), 300);
    g.save(); g.globalAlpha = p; starsP(g, t, 60, 260, 3); g.restore();
    sea(g, t, { sea: A.sea.map((c, i) => mixHex(c, B.sea[i], p)) }, 282, 410);
    paperRect(g, -10, 400, VW + 20, 150, mixHex(A.walk, B.walk, p), 1.6, 3); railing(g, 378, mixHex(A.rail, B.rail, p));
    person(g, 'you', 830, 410, 1, { back: true, alpha: 1 - seg(u, 1.4, 3) }, t);
    person(g, 'me', 380, 490, 1.8, { tint: '#2A2238', tintEyes: '#FFFFFF', alpha: .55 * (1 - seg(u, .4, 2.6)) }, t);
    person(g, 'me', 480, 490, 1.8, { eyes: 'down', mouth: 'smile', aL: 'behind', aR: 'behind' }, t);
  },
  beboat(g, t, s) {
    const u = local(t, s), turn = 1.4, P = TIMES.night;
    sky(g, P.sky, 310); starsP(g, t, 60, 280, 13); fullMoon(g, 720, 90, 30);
    sea(g, t, P, 300, 560);
    paperBlob(g, 60, 520, 260, 110, '#2E4A3A', 1.6, 5, .03);
    if (u < turn) person(g, 'me', 170, 440, 1.6, { eyes: 'closed', mouth: 'smile', aL: 'up', aR: 'up' }, t);
    const burst = seg(u, turn - .3, turn + .6);
    if (burst > 0 && burst < 1) for (let i = 0; i < 16; i++) { const a = i / 16 * TAU, r = burst * 130; g.save(); g.globalAlpha = 1 - burst; paperStar(g, 300 + Math.cos(a) * r, 400 + Math.sin(a) * r * .6, 8, i % 2 ? '#FFFFFF' : '#FFE08A', .5, a); g.restore(); }
    if (u >= turn) paperBoat(g, lerp(300, 500, eout(seg(u, turn, 5.4))), 440, 1.8, t, { face: true, eyes: 'happy', lantern: true });
    if (u >= turn) waveBand(g, t, 452, 6, 70, 20, P.sea[3], .6, 30);
    fade(g, '#FFFFFF', Math.max(0, 1 - Math.abs(u - turn) / .25) * .8);
  },
  lake(g, t, s) {
    const u = local(t, s), cx = 480, cy = 250, S = 190;
    gradV(g, ['#3A6A4A', '#2E5A3E']);
    for (let i = 0; i < 26; i++) { const x = H(i * 3) * VW, y = H(i * 5) * VH; if (Math.hypot((x - cx) / 1.25, y - cy) < S * 1.05) continue; paperCircle(g, x, y, 16, '#2A5A34', 1.2, i); paperCircle(g, x - 4, y - 4, 9, '#4A8A50', 0, i + 1); }
    cut(g, '#3A76C0', 2, q => heartPath(q, cx, cy, S)); cut(g, '#4A88D0', 0, q => heartPath(q, cx, cy - 6, S * .9));
    for (let i = 0; i < 24; i++) { const x = cx + (H(i) - .5) * S * 1.4, y = cy + (H(i + 1) - .6) * S; if (Math.sin(t * 2 + i) > 0) stroke(g, 'rgba(200,230,255,0.7)', 2, q => { q.moveTo(x, y); q.quadraticCurveTo(x + 8, y - 3, x + 16, y); }); }
    const hp = (sc, th) => [cx + 16 * Math.pow(Math.sin(th), 3) * sc / 16 * 1.1, cy - (13 * Math.cos(th) - 5 * Math.cos(2 * th) - 2 * Math.cos(3 * th) - Math.cos(4 * th)) * sc / 16 * .95 - S * .1];
    // piers all round, every one closed
    for (let i = 0; i < 6; i++) {
      const th = i / 6 * TAU + .5, [px, py] = hp(S * 1.05, th), [qx, qy] = hp(S * .82, th);
      stroke(g, '#8A5A34', 7, q => { q.moveTo(px, py); q.lineTo(qx, qy); });
      const near = Math.abs(((u * .55) % TAU) - th) < .3;
      paperCircle(g, qx, qy, near ? 13 : 11, '#E8436E', .8, i); stroke(g, '#FFFFFF', 3, q => { q.moveTo(qx - 5, qy - 5); q.lineTo(qx + 5, qy + 5); q.moveTo(qx + 5, qy - 5); q.lineTo(qx - 5, qy + 5); });
    }
    const th = u * .55, [bx, by] = hp(S * .62, th), [nx] = hp(S * .62, th + .05);
    for (let i = 1; i < 10; i++) { const [wx, wy] = hp(S * .62, th - i * .045); cut(g, 'rgba(220,240,255,0.7)', 0, q => q.arc(wx, wy + 4, 2, 0, TAU)); }
    g.save(); g.translate(bx, by); g.scale(nx > bx ? 1 : -1, 1); paperBoat(g, 0, 0, .5, t, { face: true }); g.restore();
  },
  search(g, t, s) {
    const u = local(t, s), P = TIMES.night, spot = u > 3.2;
    sky(g, P.sky, 300); starsP(g, t, 60, 280, 17); moonP(g, 160, 80, 20);
    for (let i = 0; i < 9; i++) { paperRect(g, 740 + i * 18, 268 - (i % 3) * 8, 15, 18 + (i % 3) * 8, '#2A3458', .4, i); if (Math.floor(t * 2 + i) % 3) cut(g, '#FFE08A', 0, q => q.rect(744 + i * 18, 274, 5, 5)); }
    lighthouseP(g, 880, 292, t, true, .8);
    sea(g, t, P, 290, 560);
    const look = Math.sin(u * 2.2);
    paperBoat(g, 340, 450, 1.9, t, { face: true, eyes: spot ? 'wide' : 'open', look: spot ? 1 : look, lantern: true });
    waveBand(g, t, 462, 6, 70, 20, P.sea[3], .6, 30);
    if (spot) for (let i = 0; i < 3; i++) sparkleP(g, 430 + i * 22, 290 - (i % 2) * 18, 9, '#FFE08A', t);
  },
  harbor(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, P = TIMES.dawn;
    sky(g, P.sky, 300);
    const gr = g.createRadialGradient(800, 290, 10, 800, 290, 220); gr.addColorStop(0, 'rgba(255,232,200,0.8)'); gr.addColorStop(1, 'rgba(255,232,200,0)'); g.fillStyle = gr; g.fillRect(560, 70, 480, 440);
    for (let i = 0; i < 7; i++) { const hx = 600 + i * 50, hh = 70 + (i % 3) * 18; paperRect(g, hx, 290 - hh, 44, hh, ['#FBF4E6', '#F6DCC8', '#E8E0F0'][i % 3], .8, i); cut(g, '#FFE08A', 0, q => q.rect(hx + 15, 290 - hh + 18, 14, 14)); }
    lighthouseP(g, 920, 290, t, true, .8);
    sea(g, t, P, 284, 560);
    paperRect(g, 600, 312, 380, 12, '#A87048', 1.2, 2); for (let x = 610; x < VW; x += 40) paperRect(g, x, 324, 6, 40, '#7A4E30', .8, x);
    person(g, 'you', 680, 318, .75, { aR: 'wave', eyes: 'happy' }, t);
    lanternP(g, 700, 262, .8);
    paperBoat(g, lerp(120, 460, eout(seg(u, 0, d))), 450, 1.7, t, { face: true, eyes: 'happy', lantern: true });
    waveBand(g, t, 462, 6, 70, 20, P.sea[3], .6, 30);
    for (let i = 0; i < 3; i++) seagull(g, ((u * 50 + i * 120) % 1120) - 80, 110 + i * 24, t + i, .7, '#FBF4F4');
  },
  interlude(g, t, s) {
    const u = local(t, s), night = eio(seg(u, 8.5, 13)), A = TIMES.sunset, B = TIMES.night;
    sky(g, skyMix(A.sky, B.sky, night), 270);
    if (night < .7) sunP(g, 600, 262 + night * 60, 44, t, '#FFC060', '#FFD890');
    g.save(); g.globalAlpha = night; starsP(g, t, 70, 240, 7); g.restore();
    sea(g, t, { sea: A.sea.map((c, i) => mixHex(c, B.sea[i], night)) }, 258, 372, { foam: true });
    cut(g, mixHex(A.sand, B.sand, night), 1.6, q => { q.moveTo(-10, 380); for (let x = 0; x <= VW + 40; x += 40) q.quadraticCurveTo(x - 20, 372 + H(x) * 6, x, 380); q.lineTo(VW + 10, VH + 10); q.lineTo(-10, VH + 10); q.closePath(); });
    // sky lanterns rise from the beach as night falls, then fireworks over the sea
    if (u > 10) for (let i = 0; i < 16; i++) { const a = u - 10 - H(i) * 3; if (a < 0) continue; const y = 470 - a * (26 + 16 * H(i + 2)); if (y > -40) lanternP(g, 80 + H(i + 1) * 800 + Math.sin(a + i) * 16, y, .7 + H(i + 4) * .4); }
    if (u > 15.5) fireworksIn(g, t, s.t0 + 15.5, s.t1, [140, 60, 820, 180]);
    const look = u > 15;
    const P2 = person(g, 'me', 420, 470, 1.7, look ? { sit: true, back: true } : { sit: true, aR: 'hold', aL: 'hold', eyes: 'closed', mouth: 'smile' }, t);
    person(g, 'you', 530, 470, 1.7, look ? { sit: true, back: true } : { sit: true, eyes: 'closed', mouth: 'smile', blush: true, look: -1 }, t);
    if (P2 && !look) { guitar(g, P2.R[0] + 6, P2.R[1] + 2, 1.1); for (let i = 0; i < 4; i++) { const p = (u * .5 + i / 4) % 1; g.save(); g.globalAlpha = Math.sin(p * Math.PI); noteShape(g, 440 + i * 26 + Math.sin(t * 3 + i) * 10, 330 - p * 170, 16, '#FFFFFF'); g.restore(); } }
    fade(g, '#FFFFFF', seg(u, 20.6, 21.25) * .85);
  },
  ride(g, t, s) {
    const u = local(t, s), P = TIMES.night, sc = u * 300;
    sky(g, P.sky, 290); starsP(g, t, 50, 240, 19); moonP(g, 800, 70, 20);
    fireworksIn(g, t, s.t0 - 3, s.t1, [80, 40, 600, 140]);
    sea(g, t, P, 270, 400);
    paperRect(g, -10, 396, VW + 20, 16, '#7A7E9E', 1.2, 2); for (let x = -80; x < VW + 80; x += 80) paperRect(g, x - (sc * .9) % 80, 384, 5, 20, '#9A9EBE', .6, 3);
    paperRect(g, -10, 412, VW + 20, 140, '#2E3248', 1.4, 4); for (let x = -80; x < VW + 80; x += 80) cut(g, '#E8E0C8', 0, q => q.rect(x - sc % 80, 486, 40, 4));
    for (let i = -1; i < 4; i++) { const lx = i * 360 - (sc * 1.2) % 360 + 120; paperRect(g, lx, 230, 6, 182, '#5A5E7E', 1, i); paperRect(g, lx - 14, 226, 34, 8, '#5A5E7E', 1, i + 3); const gr = g.createRadialGradient(lx + 3, 240, 2, lx + 3, 240, 70); gr.addColorStop(0, 'rgba(255,230,160,0.55)'); gr.addColorStop(1, 'rgba(255,230,160,0)'); g.fillStyle = gr; g.fillRect(lx - 70, 170, 146, 140); }
    const by = 500 + (beatPhase(t) < .5 ? -2 : 0);
    bikeP(g, 480, by, t, 1.5);
    person(g, 'me', 494, by - 58, 1.5, { sit: true, aR: 'out', eyes: 'happy', mouth: 'open' }, t);
    person(g, 'you', 424, by - 52, 1.5, { sit: true, aL: u > 2 ? 'wave' : 'down', eyes: 'happy', mouth: 'smile', blush: true }, t);
    windP(g, t, 5, 9, 'rgba(180,190,230,0.6)', 300, 460);
  },
  wheel(g, t, s) {
    const u = local(t, s), P = TIMES.night;
    gradV(g, P.sky); starsP(g, t, 50, 400, 23);
    fireworksIn(g, t, s.t0 - 2, s.t1, [80, 40, 880, 160]);
    if (u < 1.8) {
      const cx = 520, cy = 240, r = 176, rot = t * .25;
      stroke(g, '#7A7E9E', 8, q => { q.moveTo(cx, cy); q.lineTo(cx - 100, 520); q.moveTo(cx, cy); q.lineTo(cx + 100, 520); });
      for (let i = 0; i < 12; i++) { const a = rot + i / 12 * TAU; stroke(g, '#9A9EBE', 2.4, q => { q.moveTo(cx, cy); q.lineTo(cx + Math.cos(a) * r, cy + Math.sin(a) * r); }); }
      g.beginPath(); g.arc(cx, cy, r, 0, TAU); lift(g, 1); g.strokeStyle = '#C8CCE8'; g.lineWidth = 6; g.stroke(); flat(g);
      for (let i = 0; i < 24; i++) { const a = rot + i / 24 * TAU; if ((i + Math.floor(t * 4)) % 3) cut(g, ['#FF7AA0', '#FFD860', '#6EE0FF'][i % 3], 0, q => q.arc(cx + Math.cos(a) * r, cy + Math.sin(a) * r, 3.5, 0, TAU)); }
      for (let i = 0; i < 8; i++) { const a = rot + i / 8 * TAU, gx = cx + Math.cos(a) * r, gy = cy + Math.sin(a) * r; cut(g, ['#E8436E', '#F2BE4E', '#4E8FCF', '#6FB07A'][i % 4], 1, q => q.roundRect(gx - 16, gy, 32, 28, 8)); cut(g, '#FFE8B0', 0, q => q.rect(gx - 10, gy + 6, 20, 9)); }
      cut(g, '#1E2238', 1.4, q => q.rect(-10, 480, VW + 20, 70)); for (let i = 0; i < 30; i++) cut(g, ['#FF7AA0', '#FFD860', '#6EE0FF'][i % 3], 0, q => q.arc(H(i) * VW, 490 + H(i + 1) * 40, 3, 0, TAU));
      return;
    }
    // inside their gondola
    cut(g, '#E8436E', 2.4, q => q.roundRect(140, 50, 680, 450, 40));
    g.save(); g.beginPath(); g.roundRect(186, 90, 588, 230, 20); g.clip(); gradV(g, P.sky, 90, 320); for (let i = 0; i < 60; i++) cut(g, ['#FFE08A', '#FF9AB8', '#8FE0F0'][i % 3], 0, q => q.arc(186 + H(i) * 588, 260 + H(i + 2) * 60, 2.5, 0, TAU)); fireworksIn(g, t, s.t0 - 2, s.t1, [260, 120, 700, 200]); g.restore();
    cut(g, '#C83058', 0, q => q.rect(478, 90, 6, 230));
    cut(g, '#B8305A', 1, q => q.rect(140, 420, 680, 80));
    const A = person(g, 'me', 380, 470, 1.7, { sit: true, eyes: 'happy', mouth: 'grin', look: 1, aR: 'hold' }, t);
    person(g, 'you', 580, 470, 1.7, { sit: true, eyes: 'happy', mouth: 'smile', blush: true, look: -1 }, t);
    if (A) { stroke(g, '#F4F4F4', 2, q => { q.moveTo(A.R[0], A.R[1]); q.lineTo(A.R[0], A.R[1] - 20); }); paperBlob(g, A.R[0], A.R[1] - 34, 16, 14, '#FFB8D8', 1, 4, .12); }
  },
  cinema(g, t, s) {
    const u = local(t, s), turn = u > 3, P = TIMES.night;
    if (!turn) {
      beach(g, t, 'night', { moon: false });
      cut(g, '#F4E8D8', 2, q => q.rect(260, 50, 440, 240)); g.save(); g.beginPath(); g.rect(270, 60, 420, 220); g.clip(); gradV(g, TIMES.sunset.sky, 60, 280, 270, 420); sunP(g, 480, 270, 34, t, '#FFC060', '#FFD890'); g.restore();
      if (u > .8) paperText(g, 'END', 480, 170, 54, '#FFFFFF', { d: .6 });
      paperRect(g, 300, 290, 6, 90, '#5A4A3A', 1, 1); paperRect(g, 654, 290, 6, 90, '#5A4A3A', 1, 2);
      const gr = g.createLinearGradient(0, 540, 0, 290); gr.addColorStop(0, 'rgba(255,240,200,0.35)'); gr.addColorStop(1, 'rgba(255,240,200,0)'); g.fillStyle = gr; g.beginPath(); g.moveTo(470, 560); g.lineTo(270, 290); g.lineTo(690, 290); g.lineTo(490, 560); g.closePath(); g.fill();
      cut(g, '#E8436E', 1.4, q => q.rect(330, 470, 300, 80)); for (let x = 330; x < 630; x += 30) cut(g, '#FFFFFF', 0, q => q.rect(x, 470, 15, 80));
      person(g, 'me', 430, 520, 1.6, { sit: true, back: true }, t); person(g, 'you', 530, 520, 1.6, { sit: true, back: true }, t);
      return;
    }
    // reverse shot: the light of the screen flickers on them, and they are looking at each other
    gradV(g, ['#121638', '#1E2450']); starsP(g, t, 30, 280, 31);
    const fl = .35 + .1 * Math.sin(t * 13) + .05 * Math.sin(t * 31), gr = g.createRadialGradient(480, 300, 20, 480, 300, 420); gr.addColorStop(0, `rgba(255,232,200,${fl})`); gr.addColorStop(1, 'rgba(255,232,200,0)'); g.fillStyle = gr; g.fillRect(0, 0, VW, VH);
    paperRect(g, -10, 430, VW + 20, 120, '#3A3A5E', 1.6, 2);
    person(g, 'me', 410, 500, 2.1, { sit: true, eyes: 'happy', mouth: 'smile', look: 1, blush: true }, t);
    person(g, 'you', 550, 500, 2.1, { sit: true, eyes: 'happy', mouth: 'smile', look: -1, blush: true }, t);
    paperHeart(g, 480, 220 + Math.sin(t * 3) * 4, 20, '#F26A8A', 1.2);
  },
  plane(g, t, s) {
    const u = local(t, s), P = TIMES.night;
    gradV(g, P.sky); starsP(g, t, 50, 320, 37); fullMoon(g, 480, 80, 24);
    paperRect(g, -30, 140, 330, 420, '#3E3E66', 2, 1); paperRect(g, 660, 140, 330, 420, '#3E3E66', 2, 2);
    const win = (x, on) => { cut(g, on ? '#FFE8A8' : '#1E2040', 1, q => q.rect(x, 220, 140, 120)); };
    win(120, 1); win(700, u > 3.1);
    g.save(); g.beginPath(); g.rect(120, 220, 140, 120); g.clip(); person(g, 'me', 190, 460, 1.6, { aR: u < .8 ? 'up' : 'wave', eyes: 'happy', mouth: 'smile', look: 1 }, t); g.restore();
    if (u > 3.1) { g.save(); g.beginPath(); g.rect(700, 220, 140, 120); g.clip(); person(g, 'you', 770, 460, 1.6, { aL: 'up', eyes: 'sparkle', mouth: 'smile', blush: true, look: -1 }, t); g.restore(); }
    for (const x of [114, 694]) { paperRect(g, x, 334, 152, 10, '#8A6A5A', 1, x); paperRect(g, x + 70, 216, 6, 128, '#8A6A5A', .6, x + 1); }
    // the paper plane with a heart flies across the street between their windows
    const f = seg(u, .8, 3.3);
    if (f > 0 && u < 4.2) {
      const px = lerp(240, 744, f), py = 240 - Math.sin(f * Math.PI) * 140 + Math.sin(f * 12) * 8;
      stroke(g, 'rgba(255,255,255,0.4)', 1.4, q => { for (let i = 0; i < 20; i++) { const ff = Math.max(0, f - i * .012); const x = lerp(240, 744, ff), y = 240 - Math.sin(ff * Math.PI) * 140 + Math.sin(ff * 12) * 8 + 6; i ? q.lineTo(x, y) : q.moveTo(x, y); } });
      g.save(); g.translate(px, py); g.rotate(Math.cos(f * Math.PI) * -.4);
      cut(g, '#FFFFFF', 1.4, q => poly(q, [[-24, -4], [26, 0], [-24, 10]], 2)); cut(g, '#E6ECF6', 0, q => poly(q, [[-24, 10], [26, 0], [-14, 4]], 3));
      paperHeart(g, -6, -12, 7, '#F26A8A', .5); g.restore();
    }
    if (u > 3.3) for (let i = 0; i < 5; i++) sparkleP(g, 770 + Math.cos(i * 1.3) * 60, 240 + Math.sin(i * 1.3) * 36, 6, '#FFFFFF', t);
  },
  onward(g, t, s) {
    const u = local(t, s), sc = u * 90;
    sky(g, TIMES.day.sky, 300); sunP(g, 820, 80, 30, t);
    clouds(g, t, 4, 30, 160, '#FFFFFF', 60, 3);
    sea(g, t, TIMES.day, 282, 410);
    paperRect(g, -10, 400, VW + 20, 150, '#EFDCB8', 1.6, 3);
    for (let x = -88; x < VW + 88; x += 88) cut(g, '#DCC49A', 0, q => q.rect(x - sc % 88, 400, 2, 150));
    paperRect(g, -10, 378, VW + 20, 5, '#FFFFFF', .8, 1); paperRect(g, -10, 394, VW + 20, 5, '#FFFFFF', .8, 2); for (let x = -44; x < VW + 44; x += 44) paperRect(g, x - sc % 44, 376, 5, 30, '#FFFFFF', .8, 3);
    // calendar pages and leaves blow past; he keeps walking, whistling
    for (let i = 0; i < 10; i++) { const x = VW + 40 - ((t * (240 + 160 * H(i)) + H(i) * 1300) % 1360), y = 120 + H(i + 3) * 300 + Math.sin(t * 3 + i) * 20; g.save(); g.translate(x, y); g.rotate(t * 3 + i); if (i % 2) { cut(g, '#FFFFFF', 1.2, q => q.rect(-12, -14, 24, 28)); cut(g, '#E8436E', 0, q => q.rect(-12, -14, 24, 7)); } else cut(g, '#8CC57A', .8, q => q.ellipse(0, 0, 9, 4, 0, 0, TAU)); g.restore(); }
    windP(g, t, 6, 13);
    person(g, 'me', 440, 490, 1.8, { walk: step(t), eyes: 'happy', mouth: singing(t) ? 'open' : 'smile', look: 1, aL: 'swing', aR: 'swing' }, t);
    for (let i = 0; i < 3; i++) { const p = (u * .6 + i / 3) % 1; g.save(); g.globalAlpha = Math.sin(p * Math.PI); noteShape(g, 500 + p * 80, 280 - p * 100, 16, '#FFFFFF'); g.restore(); }
  },
  everyday(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0, i = Math.min(6, Math.floor(u / (d / 7)));
    const days = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
    const skies = [TIMES.day.sky, ['#8A9AB8', '#AABACC', '#D0D8E4'], TIMES.day.sky, ['#86CBEE', '#B9E3F5', '#FFF6D8'], TIMES.night.sky, TIMES.sunset.sky, ['#8AD0F2', '#C0E8F8', '#F0FAFF']][i];
    sky(g, skies, 380);
    if (i === 4) starsP(g, t, 30, 300, 41);
    paperRect(g, -10, 370, VW + 20, 180, i === 4 ? '#4A4E70' : '#EFDCB8', 1.6, 2);
    paperRect(g, 460, 80, 440, 300, i === 4 ? '#5A5A86' : '#FBF4E6', 2, 3);
    const open = i % 2 === 0 || i === 5;
    cut(g, open ? '#FFE8A8' : '#5A9AD8', 1, q => q.rect(612, 160, 124, 210));
    if (open) person(g, 'you', 674, 372, 1.6, { eyes: 'happy', mouth: 'smile', blush: true, look: -1 }, t);
    else paperCircle(g, 718, 270, 5, '#F2BE4E', .4, 3);
    for (let j = 0; j < 3; j++) { cut(g, '#C8603A', .8, q => poly(q, [[496 + j * 34, 346], [520 + j * 34, 346], [516 + j * 34, 370], [500 + j * 34, 370]], j)); for (let k = 0; k < 5; k++) cut(g, ['#FF8FB0', '#FFD860', '#E8436E'][j], .3, q => q.arc(508 + j * 34 + Math.cos(k / 5 * TAU) * 5, 336 + Math.sin(k / 5 * TAU) * 5, 4.5, 0, TAU)); }
    const P = person(g, 'me', 390, 500, 1.7, { aR: 'out', eyes: 'happy', mouth: 'smile', look: 1, dy: u % (d / 7) < .1 ? -8 : 0 }, t);
    if (P) { const [hx, hy] = P.R; [() => flowersP(g, hx + 4, hy - 4, 1.4), () => umbrellaP(g, [hx, hy], '#E8436E', 1.1), () => { stroke(g, '#FFFFFF', 1.2, q => { q.moveTo(hx, hy); q.lineTo(hx + 60, hy - 120); }); kiteP(g, hx + 60, hy - 140, t, 1.2); }, () => iceCream(g, hx + 4, hy - 12, '#FF9AB8', 1.2), () => lanternP(g, hx + 4, hy + 6, 1), () => guitar(g, hx + 20, hy, 1), () => balloonP(g, hx + 4, hy, t, 1.1)][i](); }
    if (i === 1) rainDrops(g, t, 50, 0, VW, 0, 520, '#8AA8D8', 3, 320);
    g.save(); g.translate(76, 58); g.rotate(-.06); cut(g, '#FFFFFF', 1.2, q => q.rect(-54, -24, 108, 48)); cut(g, '#E8436E', 0, q => q.rect(-54, -24, 108, 10)); paperText(g, days[i], 0, 6, 30, INK, { d: 0 }); g.restore();
  },
  closebook(g, t, s) {
    const u = local(t, s), shut = eio(seg(u, .6, 1.4)), away = eio(seg(u, 1.6, 2.6));
    sky(g, ['#FFD49A', '#FFE8C0', '#FFF6E4']);
    paperRect(g, -10, 470, VW + 20, 80, '#E8C890', 1.6, 2);
    if (away < 1) storyBook(g, t, 480, lerp(220, -200, away), 3, { close: shut });
    const hold = u > 2.4, dx = eio(seg(u, 2, 3)) * 120;
    person(g, 'me', 300 + dx, 500, 1.7, { aR: hold ? 'reach' : u < 1.4 ? 'up' : 'down', eyes: 'happy', mouth: 'smile', look: 1 }, t);
    person(g, 'you', 660 - dx, 500, 1.7, { aL: hold ? 'reach' : 'down', eyes: hold ? 'happy' : 'open', mouth: 'smile', blush: hold, look: -1 }, t);
    if (hold) for (let i = 0; i < 4; i++) { const p = (u * .5 + i / 4) % 1; g.save(); g.globalAlpha = Math.sin(p * Math.PI); paperHeart(g, 480 + Math.sin(i * 2 + t) * 60, 340 - p * 160, 9, '#F27A9A', .6); g.restore(); }
  },
  together(g, t, s) {
    const u = local(t, s);
    pier(g, t, 0);
    cloudKid(g, 240 + Math.sin(t * .5) * 20, 110, 1.3, { eyes: 'happy' }, t);
    paperBoat(g, 900, 440, .8, t, {});
    const hold = u > .8;
    person(g, 'me', 430, 430, 1.6, { aR: hold ? 'reach' : 'down', eyes: 'happy', mouth: 'smile', look: 1, blush: true }, t);
    person(g, 'you', 526, 430, 1.6, { aL: hold ? 'reach' : 'down', eyes: 'happy', mouth: 'smile', look: -1, blush: true }, t);
    if (hold) for (let i = 0; i < 5; i++) { const p = (u * .4 + i / 5) % 1; g.save(); g.globalAlpha = Math.sin(p * Math.PI); paperHeart(g, 478 + Math.sin(i * 2 + t) * 80, 270 - p * 170, 8, '#F27A9A', .6); g.restore(); }
  },
  doubt(g, t, s) {
    const u = local(t, s), d = s.t1 - s.t0;
    pier(g, t, seg(u, 0, d));
    paperBoat(g, 900, 440, .8, t, {});
    const back = eio(seg(u, .8, 2.2));
    person(g, 'me', 430, 430, 1.6, { aR: u < 5 ? 'reach' : 'down', eyes: u > 2 ? 'sad' : 'open', mouth: 'flat', look: 1 }, t);
    person(g, 'you', 526 + back * 80, 430, 1.6, { aL: u < .8 ? 'reach' : 'hold', aR: u < .8 ? 'down' : 'hold', eyes: 'down', mouth: 'flat', look: -1, walk: back > 0 && back < 1 ? beatPos(t) / 2 : null }, t);
    if (u < 6.3) petalsP(g, t, 14, ['#FFB8CC', '#FFFFFF'], 7, 1.6);
  },
  leave(g, t, s) {
    const u = local(t, s);
    pier(g, t, 1);
    // he passes behind her on the way to his boat, so he is drawn first
    if (u < 3.4) {
      const wx = u < 1.8 ? 430 : lerp(430, 830, seg(u, 1.8, 3.4));
      person(g, 'me', wx, 430, 1.6, u < 1.8 ? { eyes: 'happy', mouth: 'smile', look: 1, aL: 'wave' } : { back: true, walk: step(t) * 1.5 }, t);
      paperBoat(g, 900, 440, .8, t, {});
    } else {
      const a = eio(seg(u, 3.4, 7.2));
      paperBoat(g, lerp(900, 880, a), lerp(440, 318, a), lerp(1.3, .5, a), t, { rider: true, back: true, lantern: true });
    }
    person(g, 'you', 606, 430, 1.6, { eyes: u > 4 ? 'closed' : 'sad', mouth: 'flat', look: 1, aL: 'hold', aR: 'hold' }, t);
  },
  end(g, t, s) {
    const u = local(t, s), P = TIMES.night;
    sky(g, P.sky, 300); starsP(g, t, 90, 280, 43);
    fullMoon(g, 600, 140, 54);
    cloudKid(g, lerp(320, 840, seg(u, 0, 16)), 120, .7, { eyes: 'closed' }, t);
    sea(g, t, P, 292, 560);
    const bx = lerp(760, 900, seg(u, 0, 16));
    paperBoat(g, bx, 300, .35, t, { lantern: true });
    paperRect(g, -20, 420, 320, 14, '#5A4A54', 1.4, 2); for (let x = 10; x < 300; x += 60) paperRect(g, x, 434, 8, 110, '#4A3A44', 1, x);
    person(g, 'you', 240, 422, .7, { back: true }, t);
    const pop = eout(seg(u, 3, 3.6));
    if (pop > 0) { g.save(); g.translate(480, 250); g.scale(pop, pop); paperText(g, '小宇', 0, 0, 110, '#FBF2D0', { edge: '#2A3266', d: 2 }); g.restore(); }
    if (u > 5.2) { g.save(); g.globalAlpha = seg(u, 5.2, 5.8); paperText(g, '张震岳 · 纸片 MV', 480, 326, 28, '#FBF2D0', { edge: '#2A3266' }); g.restore(); }
    fade(g, '#1A1418', seg(u, 13, 16.5));
  },
};

// ---------------------------------------------------------------- one frame
const XF = .35;
const NO_XF = new Set(['eyes', 'becloud', 'beboat']);
const THEME_OF = { dream: 'night', missing: 'night', game: 'night', quiz: 'night', hide: 'night', beboat: 'night', lake: 'night', search: 'night', harbor: 'night', ride: 'night', wheel: 'night', cinema: 'night', plane: 'night', leave: 'night', end: 'night', ending: 'sunset', sincere: 'sunset', selfish: 'sunset', interlude: 'sunset', closebook: 'sunset', together: 'sunset', doubt: 'sunset' };
let bufA = null, bufB = null;
function shotInto(g, i, t) { g.setTransform(SCALE, 0, 0, SCALE, 0, 0); g.globalAlpha = 1; SCENES[SHOTS[i].name](g, t, SHOTS[i]); }
function drawFrame(g, t) {
  t = clamp(t, 0, DUR - 1e-4);
  if (!bufA) { bufA = document.createElement('canvas'); bufB = document.createElement('canvas'); bufA.width = bufB.width = VW * SCALE; bufA.height = bufB.height = VH * SCALE; }
  const i = shotIndex(t), s = SHOTS[i];
  if (i > 0 && t - s.t0 < XF && !NO_XF.has(s.name)) {
    shotInto(bufA.getContext('2d'), i - 1, t); shotInto(bufB.getContext('2d'), i, t);
    g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.drawImage(bufA, 0, 0); g.globalAlpha = eio((t - s.t0) / XF); g.drawImage(bufB, 0, 0); g.globalAlpha = 1;
  } else shotInto(g, i, t);
  grain(g);
  g.setTransform(SCALE, 0, 0, SCALE, 0, 0);
  subtitle(g, t, SUB_THEMES[THEME_OF[s.name] || 'day']);
}
