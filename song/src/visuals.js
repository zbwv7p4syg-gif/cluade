// visuals.js — "Claude 听见了音乐": a 13.8 s animation built around the uploaded track.
// Everything is driven by BEATMAP (analyze.py): the fitted 140 BPM grid for structure and camera,
// the detected low hits (kick / 808) for stomps and bass pulses, the mid hits for sparks,
// and the band envelopes for glow. Rendered at 60 fps; LOOK shows each hit on its nearest frame.

const VW = 1280, VH = 720, TAU = Math.PI * 2, LOOK = 1 / 120;
const F_EN = 'Fredoka, NotoSC, sans-serif', F_CN = 'NotoSC, sans-serif';
const B = BEATMAP, BEAT = B.beat, BAR = BEAT * 4, DUR = B.duration;
const barT = (bar, beat = 0) => B.phase + (bar * 4 + beat) * BEAT;   // bar 0 starts on the first beat
const KICKS = B.kicks.map(t => ({ t })), MIDS = B.mids;
const DROP = barT(4), PICKUP = barT(3, 3), OUTRO = barT(7);
let ctx;

// ---------------------------------------------------------------- helpers
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eout = t => 1 - Math.pow(1 - clamp(t), 3);
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const back = t => { t = clamp(t); const c = 2.2; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
const H = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const frac = x => x - Math.floor(x);
function since(list, t) {
  t += LOOK; let lo = 0, hi = list.length - 1, best = -1;
  while (lo <= hi) { const m = (lo + hi) >> 1; if (list[m].t <= t) { best = m; lo = m + 1; } else hi = m - 1; }
  return best < 0 ? Infinity : t - list[best].t;
}
const lastIndex = (list, t) => { t += LOOK; let i = -1; for (let k = 0; k < list.length && list[k].t <= t; k++) i = k; return i; };
const hit = (list, t, k = 10) => { const d = since(list, t); return d === Infinity ? 0 : Math.exp(-d * k); };
const beatPhase = t => frac((t + LOOK - B.phase) / BEAT);
const env = (band, t) => { const a = B.env[band], x = clamp(t * 60, 0, a.length - 1.001), i = Math.floor(x); return lerp(a[i], a[i + 1], x - i); };

function circ(x, y, r, fill) { ctx.beginPath(); ctx.arc(x, y, Math.max(0, r), 0, TAU); ctx.fillStyle = fill; ctx.fill(); }
function glow(x, y, r, color, a = 1) {
  if (r <= 0 || a <= 0.001) return;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, color); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.save(); ctx.globalAlpha = clamp(a); ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2); ctx.restore();
}
function text(s, x, y, size, color, font = F_CN, weight = 700, stroke = null, sw = 0) {
  ctx.font = `${weight} ${size}px ${font}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  if (stroke) { ctx.lineJoin = 'round'; ctx.strokeStyle = stroke; ctx.lineWidth = sw; ctx.strokeText(s, x, y); }
  ctx.fillStyle = color; ctx.fillText(s, x, y);
}
const hsl = (h, s = 100, l = 60, a = 1) => `hsla(${((h % 360) + 360) % 360},${s}%,${l}%,${a})`;
function star(x, y, r, fill, rot = 0) {
  ctx.beginPath(); for (let i = 0; i < 8; i++) { const a = rot + i * Math.PI / 4 - Math.PI / 2, rad = i % 2 ? r * .38 : r; ctx.lineTo(x + Math.cos(a) * rad, y + Math.sin(a) * rad); }
  ctx.closePath(); ctx.fillStyle = fill; ctx.fill();
}

// ---------------------------------------------------------------- Clawd's moves
function pose(t) {
  const f = beatPhase(t), kick = hit(KICKS, t, 14);
  const o = { seed: 3, eyes: 'normal', aL: .35, aR: .35, dy: 0, sq: .14 * kick, rot: 0, cupColor: '#D97757' };
  if (t < barT(2)) {                                   // listening: a nod on every beat
    o.dy = -.35 * Math.sin(f * Math.PI); o.eyes = t < barT(0, 2) ? 'normal' : 'closed';
    o.aL = .35; o.aR = 2.2 + .15 * Math.sin(t * 3);    // a hand on the headphones
  } else if (t < PICKUP - BEAT) {                      // grooving: sway, arms on the beat
    const b = Math.floor((t + LOOK - B.phase) / BEAT) % 2;
    o.rot = (b ? .1 : -.1) * (1 - f * .6); o.dy = -.6 * Math.sin(f * Math.PI); o.eyes = 'happy';
    o.aL = b ? 2.5 : .5; o.aR = b ? .5 : 2.5;
  } else if (t < PICKUP) {                             // crouch before the jump
    const p = seg(t, PICKUP - BEAT, PICKUP); o.sq = .28 * eout(p); o.aL = o.aR = lerp(.5, -.2, p); o.eyes = 'closed';
  } else if (t < DROP) {                               // the pickup: bass comes in, Clawd jumps into the drop
    const p = seg(t + LOOK, PICKUP, DROP); o.dy = -9 * 4 * p * (1 - p); o.sq = -.1 * Math.sin(p * Math.PI); o.aL = o.aR = 2.9; o.eyes = 'star'; o.rot = p * TAU;
  } else if (t < OUTRO) {                              // full section: a jump on every beat, landing on the grid
    o.dy = -3.2 * 4 * f * (1 - f); o.sq = .18 * Math.exp(-f * 12) + .1 * kick;
    o.aL = 2.6 + .3 * Math.sin(f * TAU); o.aR = 2.6 - .3 * Math.sin(f * TAU); o.mouth = 'open';
    o.eyes = t + LOOK < DROP + BEAT ? 'star' : 'happy';
  } else {                                             // bass drops out: float
    const p = seg(t, OUTRO, DUR); o.dy = -1.6 * eout(p) - .3 * Math.sin(t * 3); o.rot = Math.sin(t * 2) * .05; o.eyes = t > 13.1 ? 'happy' : 'closed';
    o.aL = o.aR = lerp(2.6, 1.6, eout(p)) + .2 * Math.sin(t * 4); o.sq = 0;
  }
  return o;
}

// ---------------------------------------------------------------- shared layers
// mid hits: little sound blocks that pop out of the headphones, height by brightness
function soundBlocks(t, cx, cy, u) {
  MIDS.forEach((m, i) => {
    const d = t + LOOK - m.t; if (d < 0 || d > 1.4) return;
    const side = i % 2 ? 1 : -1, x = cx + side * (6 * u + d * 150 * (0.6 + m.b)), y = cy - 7 * u - d * (60 + 160 * m.b) + 60 * d * d;
    const s = back(seg(d, 0, .15)) * (1 - seg(d, 1, 1.4)), hu = lerp(20, 320, m.b);
    ctx.save(); ctx.translate(x, y); ctx.rotate(side * d * 2); ctx.scale(s, s);
    glow(0, 0, 26, hsl(hu, 100, 65, .8)); ctx.beginPath(); ctx.roundRect(-9, -9, 18, 18, 5); ctx.fillStyle = hsl(hu, 100, 70); ctx.fill();
    ctx.restore();
  });
}
function kickRings(t, cx, cy, hue, scale = 1) {
  for (const k of KICKS) {
    const d = t + LOOK - k.t; if (d < 0 || d > .8) continue;
    ctx.strokeStyle = hsl(hue, 100, 70, (1 - d / .8) * .8); ctx.lineWidth = 6 * (1 - d / .8);
    ctx.beginPath(); ctx.ellipse(cx, cy, d * 700 * scale, d * 160 * scale, 0, 0, TAU); ctx.stroke();
  }
}
function flash(t, at, k = 7, a = .8) { const d = t + LOOK - at; if (d >= 0 && d < 1) { ctx.fillStyle = `rgba(255,255,255,${a * Math.exp(-d * k)})`; ctx.fillRect(0, 0, VW, VH); } }
function shake(t, amt) { const k = hit(KICKS, t, 16), i = lastIndex(KICKS, t); return [(H(i) - .5) * amt * k, (H(i + 9) - .5) * amt * k]; }

// ============================================================================
//  bars 0–3: in a dark room, Claude hears the first notes
// ============================================================================
function sListen(t) {
  const wake = seg(t, barT(2), PICKUP), lowE = env('low', t);
  ctx.fillStyle = `rgb(${lerp(8, 24, wake)},${lerp(7, 14, wake)},${lerp(14, 38, wake)})`; ctx.fillRect(0, 0, VW, VH);
  const z = lerp(1.25, 1.0, eio(seg(t, 0, barT(2)))) + .02 * hit(KICKS, t, 10);
  ctx.save(); ctx.translate(640, 400); ctx.scale(z, z); ctx.translate(-640, -400);
  // equalizer wall, rising as the song wakes up
  for (let i = 0; i < 40; i++) {
    const band = i < 13 ? 'low' : i < 27 ? 'mid' : 'high', v = env(band, t - (i % 13) * .012);
    const h = (40 + 260 * v) * (.25 + .75 * wake), x = 40 + i * 30;
    ctx.fillStyle = hsl(lerp(260, 330, i / 40), 90, 60, .25 + .4 * wake); ctx.fillRect(x, 470 - h, 20, h);
  }
  // dance floor: tiles light up on the low hits
  const idx = lastIndex(KICKS, t);
  for (let r = 0; r < 5; r++) for (let c = -7; c <= 7; c++) {
    const y0 = 470 + r * r * 9 + r * 26, y1 = 470 + (r + 1) * (r + 1) * 9 + (r + 1) * 26, w0 = 70 + r * 22, w1 = 70 + (r + 1) * 22;
    let a = .06;
    for (let k = Math.max(0, idx - 6); k <= idx; k++) {
      const d = t + LOOK - KICKS[k].t, pick = Math.floor(H(k * 7) * 75);
      if (pick === (r * 15 + c + 7)) a = Math.max(a, .9 * Math.exp(-d * 3));
    }
    const hu = 300 + c * 6 + r * 10;
    ctx.fillStyle = hsl(hu, 100, 60, a); ctx.beginPath();
    ctx.moveTo(640 + c * w0 - w0 / 2 + 1, y0); ctx.lineTo(640 + c * w0 + w0 / 2 - 1, y0); ctx.lineTo(640 + c * w1 + w1 / 2 - 1, y1); ctx.lineTo(640 + c * w1 - w1 / 2 + 1, y1); ctx.fill();
  }
  kickRings(t, 640, 520, 300, .8);
  glow(640, 420, 320, 'rgba(217,119,87,.5)', .25 + .5 * lowE);
  const p = pose(t);
  clawd(ctx, 640, 520, 18, p, t);
  soundBlocks(t, 640, 520 + p.dy * 18, 18);
  ctx.restore();
  if (t + LOOK >= PICKUP) flash(t, PICKUP, 10, .35);
}

// ============================================================================
//  bar 4: neon rooftops
// ============================================================================
function sCity(t) {
  const [sx, sy] = shake(t, 16), low = env('low', t), mid = env('mid', t);
  ctx.fillStyle = 'rgb(12,8,34)'; ctx.fillRect(0, 0, VW, VH);
  ctx.save(); ctx.translate(sx, sy);
  const g = ctx.createLinearGradient(0, 0, 0, 720); g.addColorStop(0, '#120a3a'); g.addColorStop(1, '#ff3d8b'); ctx.fillStyle = g; ctx.globalAlpha = .6 + .3 * low; ctx.fillRect(-50, -50, 1380, 820); ctx.globalAlpha = 1;
  glow(1000, 170, 220, 'rgba(255,230,190,.7)', .6 + .4 * low); circ(1000, 170, 70, '#ffe9c9');
  for (let layer = 0; layer < 2; layer++) {
    const bounce = 1 + (layer ? .08 : .04) * hit(KICKS, t, 9);
    for (let i = 0; i < 16; i++) {
      const w = 70 + H(i + layer * 40) * 70, x = i * 86 - 30 + layer * 40, h = (layer ? 180 : 280) + H(i + 7 + layer * 40) * 160;
      const top = 720 - h * bounce;
      ctx.fillStyle = layer ? '#0c0718' : '#21114a'; ctx.fillRect(x, top, w, 800);
      for (let r = 0; r < h / 26 - 1; r++) for (let c = 0; c < w / 22 - 1; c++) {
        if (H(i * 97 + r * 11 + c + layer * 500) < .3 + .5 * mid) { ctx.fillStyle = hsl([320, 190, 50][(r + c + i) % 3], 100, 65, .85); ctx.fillRect(x + 8 + c * 22, top + 12 + r * 26, 10, 12); }
      }
    }
  }
  // neon sign flickers on the mid hits
  const nf = .4 + .6 * hit(MIDS, t, 8);
  ctx.save(); ctx.shadowColor = '#ff4fd8'; ctx.shadowBlur = 30 * nf; text('CLAUDE', 330, 190, 90, `rgba(255,120,230,${nf})`, F_EN, 700); ctx.restore();
  // rooftop + Clawd
  ctx.fillStyle = '#07040f'; ctx.fillRect(360, 560, 560, 200);
  kickRings(t, 640, 560, 320, 1);
  const p = pose(t); clawd(ctx, 640, 560, 20, p, t); soundBlocks(t, 640, 560 + p.dy * 20, 20);
  ctx.restore();
}

// ============================================================================
//  bar 5: riding a comet through space
// ============================================================================
function sSpace(t) {
  const [sx, sy] = shake(t, 14), low = env('low', t), d0 = t - barT(5);
  ctx.fillStyle = '#04030d'; ctx.fillRect(0, 0, VW, VH);
  glow(300, 200, 500, 'rgba(123,92,168,.5)'); glow(1000, 560, 500, 'rgba(58,156,152,.4)');
  ctx.save(); ctx.translate(640 + sx, 360 + sy);
  // warp stars: speed follows the bass
  for (let i = 0; i < 220; i++) {
    const a = H(i) * TAU, r0 = 30 + H(i + 3) * 600, r = (r0 + d0 * (400 + 900 * low) * (0.4 + H(i + 5))) % 700;
    const x = Math.cos(a) * r, y = Math.sin(a) * r * .6, L = 8 + r * .06 * (1 + 2 * low);
    ctx.strokeStyle = `rgba(255,255,255,${clamp(r / 300)})`; ctx.lineWidth = 1 + r / 400; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + Math.cos(a) * L, y + Math.sin(a) * L * .6); ctx.stroke();
  }
  ctx.restore();
  // planets
  circ(180 + d0 * 20, 560, 90, '#e2476e'); ctx.strokeStyle = 'rgba(255,220,180,.7)'; ctx.lineWidth = 6; ctx.beginPath(); ctx.ellipse(180 + d0 * 20, 560, 150, 30, -.3, 0, TAU); ctx.stroke();
  circ(1120 - d0 * 30, 150, 50, '#3a9c98');
  ctx.save(); ctx.translate(sx, sy);
  // the comet Clawd rides: a big spark that pulses on every low hit
  const cx = 640 + Math.sin(d0 * 2) * 40, cy = 420 + Math.cos(d0 * 3) * 14, k = hit(KICKS, t, 8);
  for (let i = 0; i < 30; i++) { ctx.globalAlpha = (1 - i / 30) * .5; circ(cx - 30 - i * 14, cy + 30 + i * 6, 40 - i, hsl(20 + i * 3, 100, 60)); }
  ctx.globalAlpha = 1;
  glow(cx, cy + 20, 220 + 80 * k, 'rgba(255,170,110,.9)'); star(cx, cy + 20, 70 * (1 + .25 * k), '#ffb07a', d0 * 3); star(cx, cy + 20, 34, '#fff3e0', -d0 * 4);
  for (const kk of KICKS) { const d = t + LOOK - kk.t; if (d < 0 || d > .7) continue; ctx.strokeStyle = hsl(30, 100, 70, 1 - d / .7); ctx.lineWidth = 5; ctx.beginPath(); ctx.arc(cx, cy + 20, 70 + d * 500, 0, TAU); ctx.stroke(); }
  const p = pose(t); clawd(ctx, cx, cy - 14, 16, { ...p, noShadow: true }, t); soundBlocks(t, cx, cy - 14 + p.dy * 16, 16);
  ctx.restore();
}

// ============================================================================
//  bar 6: synthwave grid, Clawd and two clones in unison
// ============================================================================
function sGrid(t) {
  const [sx, sy] = shake(t, 12), low = env('low', t), d0 = t - barT(6);
  ctx.fillStyle = '#0b0620'; ctx.fillRect(0, 0, VW, VH);
  ctx.save(); ctx.translate(sx, sy);
  const g = ctx.createLinearGradient(0, 0, 0, 400); g.addColorStop(0, '#0b0620'); g.addColorStop(1, '#5a1a6e'); ctx.fillStyle = g; ctx.fillRect(-50, -50, 1380, 460);
  // striped sun
  ctx.save(); ctx.beginPath(); ctx.arc(640, 380, 200 + 20 * low, Math.PI, TAU); ctx.clip();
  const sg = ctx.createLinearGradient(0, 180, 0, 380); sg.addColorStop(0, '#ffd66b'); sg.addColorStop(1, '#ff3d8b'); ctx.fillStyle = sg; ctx.fillRect(400, 150, 480, 240);
  ctx.fillStyle = '#0b0620'; for (let k = 0; k < 7; k++) ctx.fillRect(400, 290 + k * 14, 480, 3 + k * 1.2);
  ctx.restore();
  ctx.fillStyle = '#2a0f45'; ctx.beginPath(); ctx.moveTo(-50, 380); [[150, 300], [300, 360], [420, 280], [560, 380], [760, 380], [880, 290], [1020, 350], [1150, 270], [1330, 380]].forEach(p => ctx.lineTo(...p)); ctx.lineTo(1330, 380); ctx.fill();
  // grid floor: rows scroll one row per beat, lines flash on the low hits
  ctx.fillStyle = '#120828'; ctx.fillRect(-50, 380, 1380, 400);
  const k = hit(KICKS, t, 9), f = beatPhase(t);
  ctx.strokeStyle = hsl(300, 100, 65, .5 + .5 * k); ctx.lineWidth = 2 + 2 * k;
  for (let c = -16; c <= 16; c++) { ctx.beginPath(); ctx.moveTo(640 + c * 12, 380); ctx.lineTo(640 + c * 160, 760); ctx.stroke(); }
  for (let r = 0; r < 12; r++) { const q = (r + f) / 12, y = 380 + Math.pow(q, 2.2) * 380; ctx.beginPath(); ctx.moveTo(-50, y); ctx.lineTo(1330, y); ctx.stroke(); }
  // three Clawds, in unison
  const p = pose(t);
  [[380, 560, 15, -1], [900, 560, 15, 1], [640, 600, 20, 0]].forEach(([x, y, u, side], i) => {
    glow(x, y - 4 * u, 160, hsl(300 + i * 40, 100, 60, .5), .4 + .5 * k);
    clawd(ctx, x, y, u, { ...p, flip: side > 0, cupColor: ['#7ff0e0', '#ffd66b', '#D97757'][i] }, t);
  });
  soundBlocks(t, 640, 600 + p.dy * 20, 20);
  ctx.restore();
}

// ============================================================================
//  bar 7: the bass drops out — Claude floats up into the light
// ============================================================================
function sFloat(t) {
  const p = seg(t, OUTRO, DUR), hi = env('high', t);
  const g = ctx.createLinearGradient(0, 0, 0, 720); g.addColorStop(0, '#ffd9c4'); g.addColorStop(.6, '#f2a6c8'); g.addColorStop(1, '#9d8cf0');
  ctx.fillStyle = g; ctx.fillRect(0, 0, VW, VH);
  glow(640, 300, 600, 'rgba(255,255,240,.9)', .5 + .3 * hi);
  for (let i = 0; i < 6; i++) { const x = ((i * 260 + (t - OUTRO) * 30) % 1500) - 150, y = 560 + (i % 2) * 70; for (const [dx, dy, r] of [[0, 0, 60], [60, -20, 70], [120, 0, 55]]) circ(x + dx, y + dy + (1 - p) * 40, r, 'rgba(255,255,255,.75)'); }
  // slow particles: each mid hit leaves a soft sparkle
  MIDS.forEach((m, i) => { const d = t + LOOK - m.t; if (d < 0 || m.t < OUTRO - .5) return; for (let k = 0; k < 6; k++) { const a = k / 6 * TAU + i; ctx.globalAlpha = Math.exp(-d * 1.5); star(640 + Math.cos(a) * (60 + d * 120), 400 + Math.sin(a) * (60 + d * 120) - d * 40, 7, '#fff', d); } });
  ctx.globalAlpha = 1;
  const po = pose(t); clawd(ctx, 640, 590, 22, { ...po, noShadow: true }, t);
  // title on the grid: letters one per 8th from beat 2 of the last bar
  const title = [...'Claude'], t0 = barT(7, 1);
  ctx.font = `700 96px ${F_EN}`;
  const ws = title.map(c => ctx.measureText(c).width), total = ws.reduce((p, q) => p + q, 0);
  let x0 = 640 - total / 2;
  title.forEach((c, i) => {
    const ct = t0 + i * BEAT / 2, d = t + LOOK - ct, cx = x0 + ws[i] / 2; x0 += ws[i]; if (d < 0) return;
    const s = back(seg(d, 0, .18));
    ctx.save(); ctx.translate(cx, 96); ctx.scale(s, s); text(c, 0, 0, 96, '#fff', F_EN, 700, '#D97757', 12); ctx.restore();
  });
  if (t + LOOK >= barT(7, 3)) { const d = t + LOOK - barT(7, 3); ctx.globalAlpha = clamp(d / .2); text('听见音乐的样子 ✻', 640, 176, 34, '#7a3a2a', F_CN, 700); ctx.globalAlpha = 1; }
}

function drawFrame(c, t, scale) {
  ctx = c; t = clamp(t, 0, DUR - 1e-4);
  ctx.setTransform(scale, 0, 0, scale, 0, 0); ctx.globalAlpha = 1;
  const tt = t + LOOK;
  if (tt < DROP) sListen(t);
  else if (tt < barT(5)) sCity(t);
  else if (tt < barT(6)) sSpace(t);
  else if (tt < OUTRO) sGrid(t);
  else sFloat(t);
  // hard cuts on the bar downbeats, each with a flash; the last low hit gets one too
  for (const at of [DROP, barT(5), barT(6)]) flash(t, at, 8, .7);
  flash(t, OUTRO, 3, .5);
  const lastLow = B.kicks[B.kicks.length - 1];
  if (lastLow > OUTRO) flash(t, lastLow, 6, .45);
  // captions
  const cap = (s, a, b, y = 660, size = 30) => { if (tt < a || tt >= b) return; ctx.save(); ctx.globalAlpha = seg(tt, a, a + .15) * (1 - seg(tt, b - .15, b)); ctx.font = `700 ${size}px ${F_CN}`; const w = ctx.measureText(s).width + 50; ctx.beginPath(); ctx.roundRect(640 - w / 2, y - 28, w, 56, 28); ctx.fillStyle = 'rgba(10,8,20,.55)'; ctx.fill(); text(s, 640, y, size, '#fff'); ctx.restore(); };
  cap('♪ Claude 正在听……', barT(0, 1), barT(2));
  cap('它开始跟着节奏动了', barT(2), PICKUP - .05);
  if (tt >= PICKUP && tt < DROP) { const d = tt - PICKUP, s = 1 + .8 * Math.exp(-d * 14); ctx.save(); ctx.translate(640, 200); ctx.scale(s, s); text('来了！', 0, 0, 120, '#fff', F_CN, 900, '#D97757', 14); ctx.restore(); }
  // fade out at the very end
  if (t > DUR - .15) { ctx.fillStyle = `rgba(0,0,0,${seg(t, DUR - .15, DUR)})`; ctx.fillRect(0, 0, VW, VH); }
}
