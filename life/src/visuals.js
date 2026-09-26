// visuals.js — draws frame t (seconds). Every beat-driven effect reads SCORE / WORDS from score.js,
// the same lists the synthesizer plays, so picture and sound cannot drift apart.

const VW = 1280, VH = 720, TAU = Math.PI * 2;
const SERIF = '"NotoSerifSC", "Noto Color Emoji", serif';
let ctx;

// ---------------------------------------------------------------- math
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eout = t => 1 - Math.pow(1 - clamp(t), 3);
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const back = t => { t = clamp(t); const c = 2.2; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
const H = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const within = (t, a, b) => t >= a && t < b;
// time since the most recent event (at or before t) in a sorted list; Infinity if none yet
function since(list, t) {
  let lo = 0, hi = list.length - 1, best = -1;
  while (lo <= hi) { const m = (lo + hi) >> 1; if (list[m].t <= t + 1e-9) { best = m; lo = m + 1; } else hi = m - 1; }
  return best < 0 ? Infinity : t - list[best].t;
}
const lastEvent = (list, t) => { let e = null; for (const x of list) { if (x.t <= t + 1e-9) e = x; else break; } return e; };
const hit = (list, t, k = 10) => { const d = since(list, t); return d === Infinity ? 0 : Math.exp(-d * k); };

// ---------------------------------------------------------------- drawing
function circ(x, y, r, fill) { ctx.beginPath(); ctx.arc(x, y, Math.max(0, r), 0, TAU); ctx.fillStyle = fill; ctx.fill(); }
function glow(x, y, r, color, a = 1) {
  if (r <= 0 || a <= 0) return;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, color); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.save(); ctx.globalAlpha = clamp(a); ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2); ctx.restore();
}
function vgrad(stops, y0 = 0, y1 = VH) { const g = ctx.createLinearGradient(0, y0, 0, y1); stops.forEach((c, i) => g.addColorStop(i / (stops.length - 1), c)); return g; }
function text(s, x, y, size, color, weight = 900, align = 'center', stroke = null, sw = 0) {
  ctx.font = `${weight} ${size}px ${SERIF}`; ctx.textAlign = align; ctx.textBaseline = 'middle';
  if (stroke) { ctx.lineJoin = 'round'; ctx.strokeStyle = stroke; ctx.lineWidth = sw; ctx.strokeText(s, x, y); }
  ctx.fillStyle = color; ctx.fillText(s, x, y);
}
// a word that slams in exactly on its beat: starts big, snaps to size within ~0.12 s
function slam(s, x, y, size, t, t0, t1 = Infinity, o = {}) {
  if (t < t0 || t >= t1) return;
  const d = t - t0, sc = 1 + (o.from ?? 0.7) * Math.exp(-d * 16), a = clamp(d / 0.04) * (1 - seg(t, t1 - 0.12, t1));
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(sc, sc);
  if (o.rot) ctx.rotate(o.rot * Math.exp(-d * 10));
  if (o.glow) { ctx.shadowColor = o.glow; ctx.shadowBlur = 30; }
  text(s, 0, 0, size, o.color || '#fff', o.weight ?? 900, 'center', o.stroke, o.sw);
  ctx.restore();
}
// a line typed one character per 8th note (times from charTimes)
function typedLine(line, x, y, size, t, t1, o = {}) {
  const ts = charTimes(line), chars = [...line.text];
  if (t < ts[0] || t >= t1) return;
  ctx.font = `${o.weight ?? 700} ${size}px ${SERIF}`;
  const widths = chars.map(c => ctx.measureText(c).width), total = widths.reduce((a, b) => a + b, 0);
  let cx = x - total / 2;
  const fade = 1 - seg(t, t1 - 0.3, t1);
  chars.forEach((c, i) => {
    if (t >= ts[i]) {
      const d = t - ts[i], sc = 1 + 0.5 * Math.exp(-d * 18);
      ctx.save(); ctx.globalAlpha = clamp(d / 0.03) * fade; ctx.translate(cx + widths[i] / 2, y - 10 * Math.exp(-d * 12)); ctx.scale(sc, sc);
      if (o.glow) { ctx.shadowColor = o.glow; ctx.shadowBlur = 24; }
      text(c, 0, 0, size, o.color || '#fff', o.weight ?? 700);
      ctx.restore();
    }
    cx += widths[i];
  });
}
function stars(t, n, seed, a = 1, twk = SCORE.hat) {
  const tw = hit(twk, t, 8);
  for (let i = 0; i < n; i++) {
    const x = H(seed + i) * VW, y = H(seed + i * 3) * VH * 0.75, r = 0.6 + H(seed + i * 7) * 1.6;
    ctx.globalAlpha = a * (0.3 + 0.5 * (0.5 + 0.5 * Math.sin(t * (1 + H(i) * 2) + i)) + (i % 5 === 0 ? 0.4 * tw : 0));
    circ(x, y, r, '#fff');
  }
  ctx.globalAlpha = 1;
}
// ECG trace: the waveform scrolls left from a head at x = hx; spikes are the heart events
function ecgShape(d, strong) {
  const g = (x, m, s) => Math.exp(-((x - m) ** 2) / (2 * s * s));
  if (d < -0.05 || d > 0.4) return 0;
  return (strong ? 1 : 0.55) * (-0.18 * g(d, 0.0, 0.006) + 1.0 * g(d, 0.018, 0.008) - 0.35 * g(d, 0.036, 0.008) + 0.12 * g(d, 0.2, 0.04));
}
function ecg(t, hx, y, amp, color, alpha = 1, speed = 320) {
  ctx.save(); ctx.globalAlpha = alpha; ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.shadowColor = color; ctx.shadowBlur = 14; ctx.lineJoin = 'round';
  ctx.beginPath();
  for (let x = 0; x <= hx; x += 2) {
    const tau = t - (hx - x) / speed; let v = 0;
    for (const h of SCORE.heart) { const d = tau - h.t; if (d > -0.06 && d < 0.45) v += ecgShape(d, h.strong); }
    ctx.lineTo(x, y - v * amp);
  }
  ctx.stroke();
  const hv = SCORE.heart.reduce((v, h) => v + ecgShape(t - h.t, h.strong), 0);
  ctx.shadowBlur = 0; glow(hx, y - hv * amp, 40 + 60 * hit(SCORE.heart, t, 8), color, 0.8); circ(hx, y - hv * amp, 5, '#fff');
  ctx.restore();
}

// ============================================================================
//  问 (0 – 9.6 s)
// ============================================================================
function sQuestion(t) {
  ctx.fillStyle = '#06070b'; ctx.fillRect(0, 0, VW, VH);
  const hb = hit(SCORE.heart.filter(h => h.strong), t, 6);
  glow(640, 470, 520, 'rgba(92,255,200,.10)', 0.5 + hb);
  const titleOut = seg(t, bt(3, 0), bt(3, 1));
  ctx.save(); ctx.globalAlpha = 1 - titleOut; ctx.translate(0, -40 * eio(titleOut));
  WORDS.title.forEach(([c, ct], i) => slam(c, 640 + (i - 2) * 130, 250, 120, t, ct, Infinity, { glow: 'rgba(255,255,255,.35)', rot: (i % 2 ? .12 : -.12) }));
  slam('是什么？', 640, 380, 50, t, WORDS.titleQ, Infinity, { weight: 700, color: '#bfc6d6', from: .4 });
  ctx.restore();
  const eAlpha = 1 - seg(t, bt(3, 2), bt(4, 0));
  ecg(t, 640, 500, 150, '#5cffc8', eAlpha);
  // bar 3: the last heartbeat becomes a point of light — a life begins
  if (t >= bt(3, 0)) {
    const p = eout(seg(t, bt(3, 0), bt(4, 0)));
    const r = 6 + 8 * p + 3 * hit(SCORE.piano, t, 6);
    glow(640, lerp(470, 430, p), 90 + 40 * p, 'rgba(255,236,190,.9)', p); circ(640, lerp(470, 430, p), r, '#fff7e6');
    typedLine(WORDS.birthLine, 640, 250, 54, t, bt(4, 0), { weight: 400, color: '#f3ead8', glow: 'rgba(255,230,180,.5)' });
  }
}

// ============================================================================
//  童年 (9.6 – 19.2 s): one hop per beat, a footprint on every landing
// ============================================================================
function childPos(t) {
  const t0 = bt(4), k = (t - t0) / BEAT, i = Math.floor(k), f = k - i;
  const xAt = n => 140 + clamp(n, 0, 16) * 62;
  const trip = within(t, bt(6, 2), bt(7, 0));
  const hopH = trip ? 0 : 46;
  return { x: lerp(xAt(i), xAt(i + 1), eio(f)), y: 560 - Math.sin(f * Math.PI) * hopH, f, i, trip };
}
function sChildhood(t) {
  const t0 = bt(4), p = seg(t, t0, bt(8));
  ctx.fillStyle = vgrad(['#2b2350', '#ff9eaa', '#ffd9a8']); ctx.fillRect(0, 0, VW, VH);
  ctx.fillStyle = `rgba(6,7,11,${1 - seg(t, t0, t0 + BEAT)})`; ctx.fillRect(0, 0, VW, VH);
  // the sun rises through the section
  const sy = lerp(640, 250, eout(p));
  glow(980, sy, 260, 'rgba(255,230,160,.9)'); circ(980, sy, 70, '#ffe6a6');
  stars(t, 50, 11, 1 - p);
  // balloons that bob on the snare
  const sn = hit(SCORE.snare, t, 7);
  [['#ff6f91', 200, 180], ['#6fc3ff', 330, 130], ['#ffd166', 1120, 170], ['#9b8cff', 1210, 250]].forEach(([c, x, y], i) => {
    const by = y + Math.sin(t * 1.5 + i) * 10 - sn * 8;
    ctx.strokeStyle = 'rgba(80,60,80,.5)'; ctx.lineWidth = 1.5; ctx.beginPath(); ctx.moveTo(x, by + 34); ctx.quadraticCurveTo(x - 10, by + 80, x + 4, by + 130); ctx.stroke();
    ctx.beginPath(); ctx.ellipse(x, by, 26 * (1 + .08 * sn), 32, 0, 0, TAU); ctx.fillStyle = c; ctx.fill();
    circ(x - 8, by - 10, 6, 'rgba(255,255,255,.5)');
  });
  // ground
  ctx.fillStyle = '#7a5c8e'; ctx.fillRect(0, 572, VW, 150);
  ctx.fillStyle = '#9a79ad'; ctx.fillRect(0, 572, VW, 6);
  // footprints: one per landed beat
  const kicks = SCORE.kick.filter(k => k.t >= t0 && k.t < bt(8));
  kicks.forEach((k, n) => {
    if (k.t > t + 1e-9) return;
    const x = 140 + n * 62, a = 0.55 * (1 - seg(t, k.t + 3, k.t + 6)), s = back(seg(t, k.t, k.t + 0.15));
    ctx.save(); ctx.globalAlpha = a; ctx.translate(x, 590 + (n % 2 ? 8 : -2)); ctx.scale(s, s);
    ctx.beginPath(); ctx.ellipse(0, 0, 10, 5, 0, 0, TAU); ctx.fillStyle = '#4b3560'; ctx.fill();
    circ(-9, -6, 2.5, '#4b3560'); circ(-3, -8, 2.5, '#4b3560'); circ(4, -8, 2.5, '#4b3560');
    ctx.restore();
  });
  // the little light: grows up while it hops
  const c = childPos(t), grow = lerp(10, 18, p), kd = hit(SCORE.kick, t, 14);
  let sx = 1 + .25 * kd, sy2 = 1 - .25 * kd, ry = c.y;
  if (c.trip) { const d = t - bt(6, 2); sx = 1.5 - .5 * seg(d, 0, .8); sy2 = .5 + .5 * seg(d, 0, .8); ry = 560 + 6; }
  glow(c.x, ry - grow, grow * 6, 'rgba(255,240,200,.85)');
  ctx.save(); ctx.translate(c.x, ry); ctx.scale(sx, sy2); circ(0, -grow, grow, '#fff8ea'); ctx.restore();
  if (c.trip && t - bt(6, 2) < .5) text('!', c.x + 26, ry - 60, 40, '#fff', 900);
  // words: small line on beat 1, big line on beat 3
  WORDS.childhood.forEach(([ta, a, tb, b], i) => {
    const end = i < 3 ? WORDS.childhood[i + 1][0] : bt(8);
    slam(a, 640, 170, 42, t, ta, end, { weight: 700, color: '#fff3e0', from: .4 });
    slam(b, 640, 260, 96, t, tb, end, { color: '#ffffff', stroke: 'rgba(90,50,90,.55)', sw: 10, rot: .1 });
  });
}

// ============================================================================
//  青春 (19.2 – 28.8 s): a hard cut and a word on every single kick
// ============================================================================
const YOUTH_BG = ['#ff3d6e', '#ffb800', '#00b8ff', '#7c4dff', '#00d69a', '#ff6a00'];
function sYouth(t) {
  const i = clamp(Math.floor((t - bt(8)) / BEAT), 0, 15), d = t - WORDS.youth[i][0];
  const bg = YOUTH_BG[i % YOUTH_BG.length], kd = hit(SCORE.kick, t, 9), oh = hit(SCORE.ohat, t, 12);
  ctx.fillStyle = bg; ctx.fillRect(0, 0, VW, VH);
  const z = 1 + .06 * kd;
  ctx.save(); ctx.translate(640, 360); ctx.scale(z, z); ctx.translate(-640, -360);
  // background graphics change with every cut
  ctx.save(); ctx.globalAlpha = .22; ctx.fillStyle = '#fff';
  const kind = i % 4;
  if (kind === 0) for (let k = 0; k < 5; k++) { ctx.beginPath(); ctx.arc(640, 360, 120 + k * 110 + d * 300, 0, TAU); ctx.lineWidth = 18; ctx.strokeStyle = '#fff'; ctx.stroke(); }
  else if (kind === 1) { ctx.translate(640, 360); ctx.rotate(-.5 + d * .4); for (let k = -8; k < 8; k++) ctx.fillRect(k * 110, -800, 50, 1600); }
  else if (kind === 2) for (let k = 0; k < 40; k++) { const a = k / 40 * TAU; ctx.beginPath(); ctx.moveTo(640, 360); ctx.lineTo(640 + Math.cos(a) * 1200, 360 + Math.sin(a) * 1200); ctx.lineTo(640 + Math.cos(a + .06) * 1200, 360 + Math.sin(a + .06) * 1200); ctx.fill(); }
  else for (let k = 0; k < 30; k++) circ(H(k + i * 50) * VW, H(k + i * 70) * VH, 10 + H(k) * 50 * (1 + d), '#fff');
  ctx.restore();
  // the comet — life at full speed, crossing once per bar
  const bp = ((t - bt(8)) % BAR) / BAR, cx = lerp(-100, 1380, bp), cy = 560 - Math.sin(bp * Math.PI) * 120;
  for (let k = 0; k < 18; k++) { ctx.globalAlpha = (1 - k / 18) * .6; circ(cx - k * 16, cy + Math.sin(bp * Math.PI * 2) * k * 2, 14 - k * .6, '#fff'); }
  ctx.globalAlpha = 1; glow(cx, cy, 90, 'rgba(255,255,255,.9)'); circ(cx, cy, 16, '#fff');
  // the word of this beat
  const w = WORDS.youth[i][1];
  if (w === '火焰') {
    const f = 1 + .08 * Math.sin(t * 30);
    ctx.save(); ctx.translate(640, 330); ctx.scale(f * back(seg(d, 0, .2)), f * back(seg(d, 0, .2)));
    ctx.fillStyle = '#fff3c4'; ctx.beginPath(); ctx.moveTo(0, -150); ctx.bezierCurveTo(90, -60, 110, 40, 0, 110); ctx.bezierCurveTo(-110, 40, -90, -60, 0, -150); ctx.fill();
    ctx.fillStyle = '#ffd24a'; ctx.beginPath(); ctx.moveTo(0, -60); ctx.bezierCurveTo(50, 0, 60, 60, 0, 100); ctx.bezierCurveTo(-60, 60, -50, 0, 0, -60); ctx.fill();
    ctx.restore();
    slam(w, 640, 520, 110, t, WORDS.youth[i][0], bt(12), { stroke: 'rgba(0,0,0,.35)', sw: 14 });
  } else slam(w, 640, 350, w.length > 2 ? 150 : 190, t, WORDS.youth[i][0], WORDS.youth[i][0] + BEAT, { stroke: 'rgba(0,0,0,.25)', sw: 16, rot: (i % 2 ? .08 : -.08) });
  // tiny offbeat sparkle on the open hats
  if (oh > .05) { ctx.globalAlpha = oh; for (let k = 0; k < 6; k++) circ(H(k + i * 9) * VW, H(k + i * 13) * VH, 6, '#fff'); ctx.globalAlpha = 1; }
  ctx.restore();
  ctx.fillStyle = `rgba(255,255,255,${.35 * hit(SCORE.crash, t, 6)})`; ctx.fillRect(0, 0, VW, VH);
}

// ============================================================================
//  低谷 (28.8 – 38.4 s): rain; every drip you hear is a ripple you see
// ============================================================================
function sValley(t) {
  const t0 = bt(12), black = t >= bt(15, 3);
  ctx.fillStyle = vgrad(['#10151f', '#1c2433', '#252c3a']); ctx.fillRect(0, 0, VW, VH);
  // rain streaks (faster during the build)
  const speed = lerp(900, 1800, seg(t, bt(14), bt(15, 3)));
  ctx.strokeStyle = 'rgba(170,190,220,.25)'; ctx.lineWidth = 1.5; ctx.beginPath();
  for (let k = 0; k < 160; k++) { const x = H(k + 700) * 1400 - 60, y = ((t * speed * (0.7 + H(k) * .6) + H(k + 3) * 900) % 900) - 100; ctx.moveTo(x, y); ctx.lineTo(x - 8, y + 26); }
  ctx.stroke();
  ctx.fillStyle = '#141a24'; ctx.fillRect(0, 580, VW, 140);
  // ripples = drips
  for (const dr of SCORE.drip) {
    const d = t - dr.t; if (d < 0 || d > 1.2) continue;
    const x = 80 + dr.x * 1120, y = 600 + (dr.m % 5) * 18;
    ctx.save(); ctx.globalAlpha = 1 - d / 1.2; ctx.strokeStyle = '#a9c4ea'; ctx.lineWidth = 2;
    for (const k of [0, .25]) { const r = Math.max(0, d - k) * 90; ctx.beginPath(); ctx.ellipse(x, y, r, r * .28, 0, 0, TAU); ctx.stroke(); }
    ctx.restore();
    if (d < .12) { ctx.fillStyle = `rgba(200,220,255,${1 - d / .12})`; ctx.fillRect(x - 1, y - 60 + d * 500, 2, 16); }
  }
  // the light walks on, dimmer — one step per half-time kick
  const steps = SCORE.kick.filter(k => k.t >= t0 && k.t < bt(15));
  const n = steps.filter(k => k.t <= t).length, last = steps[n - 1];
  const f = last ? eio(seg(t, last.t, last.t + .35)) : 0;
  const x = 380 + (Math.max(0, n - 1) + f) * 70, dim = 1 - .5 * seg(t, t0, bt(14));
  glow(x, 540, 90 * dim, 'rgba(160,190,255,.6)'); circ(x, 540, 16, `rgba(220,230,255,${.5 + .5 * dim})`);
  // words, softly — but still on their beats
  WORDS.valley.forEach(([tw, w], i) => {
    const end = i === 0 ? bt(13) : i === 1 ? bt(14) : bt(15);
    const y = i === 3 ? 330 : 250, xx = i === 2 ? 540 : i === 3 ? 760 : 640;
    slam(w, xx, y, 64, t, tw, end, { weight: 400, color: '#cfd8e8', from: .15 });
  });
  // the build: shake with the snare roll
  if (t >= bt(15) && !black) {
    const sh = hit(SCORE.snare, t, 20) * seg(t, bt(15), bt(15, 3)) * 8;
    ctx.save(); ctx.translate((H(Math.floor(t * 60)) - .5) * sh, (H(Math.floor(t * 60) + 1) - .5) * sh);
    typedLine(WORDS.valleyTurn, 640, 300, 72, t, bt(15, 3), { weight: 700, color: '#ffffff', glow: 'rgba(255,240,200,.8)' });
    glow(640, 300, 500 * seg(t, bt(15), bt(15, 3)), 'rgba(255,240,200,.35)');
    ctx.restore();
  }
  if (black) { ctx.fillStyle = '#000'; ctx.fillRect(0, 0, VW, VH); }
}

// ============================================================================
//  答案 (38.4 – 48 s): fireworks on beats 1 & 3, the answer typed on the 8ths
// ============================================================================
function firework(e, t) {
  const d = t - e.t; if (d < 0 || d > 2.2) return;
  const x = 180 + e.x * 920, y = 130 + e.y * 220, hue = Math.floor(e.hue * 360), n = 64;
  if (d < .08) glow(x, y, 300, `hsla(${hue},100%,80%,.9)`, 1 - d / .08);
  for (let k = 0; k < n; k++) {
    const a = k / n * TAU, sp = 230 * (0.75 + H(k + e.t * 10) * .5), dd = Math.min(d, 1.4);
    const px = x + Math.cos(a) * sp * (1 - Math.exp(-dd * 3)) , py = y + Math.sin(a) * sp * (1 - Math.exp(-dd * 3)) + 40 * d * d;
    ctx.globalAlpha = clamp(1 - d / 2.2) * (d > 1 ? (0.5 + 0.5 * Math.sin(d * 40 + k)) : 1);
    circ(px, py, 4.6 - 1.8 * d, `hsl(${(hue + k * 3) % 360},100%,${70 + 20 * Math.exp(-d * 4)}%)`);
  }
  ctx.globalAlpha = 1;
}
function sAnswer(t) {
  const t0 = bt(16), p = seg(t, t0, bt(20));
  ctx.fillStyle = vgrad(['#060a1f', '#141a45', '#2a1d4f']); ctx.fillRect(0, 0, VW, VH);
  stars(t, 140, 31, 1);
  const kd = hit(SCORE.kick, t, 9), z = 1 + .03 * kd;
  ctx.save(); ctx.translate(640, 360); ctx.scale(z, z); ctx.translate(-640, -360);
  for (const e of SCORE.boom) firework(e, t);
  // city silhouette whose windows light up bar by bar
  for (let k = 0; k < 26; k++) {
    const w = 40 + H(k + 900) * 40, h = 60 + H(k + 901) * 150, x = k * 50 - 10;
    ctx.fillStyle = '#0a0c1c'; ctx.fillRect(x, 720 - h, w, h);
    for (let r = 0; r < h / 22 - 1; r++) for (let c = 0; c < 2; c++) if (H(k * 31 + r * 7 + c) < p * 1.1) { ctx.fillStyle = 'rgba(255,214,140,.8)'; ctx.fillRect(x + 8 + c * 16, 720 - h + 10 + r * 22, 8, 10); }
  }
  // the light, now bright and warm, rises like a lantern
  const ly = lerp(600, 440, eout(p)), r = 22 + 6 * kd;
  glow(640, ly, 220 + 80 * kd, 'rgba(255,214,140,.8)'); circ(640, ly, r, '#fff6e0');
  ctx.restore();
  ctx.fillStyle = `rgba(255,255,255,${.3 * hit(SCORE.crash, t, 7)})`; ctx.fillRect(0, 0, VW, VH);
  WORDS.answer.forEach((l, i) => typedLine(l, 640, 300, 66, t, l.t0 + BAR, { weight: 700, color: '#ffffff', glow: 'rgba(255,200,120,.9)' }));
  // the previous line drifts up and stays faintly
  WORDS.answer.forEach((l, i) => {
    if (t < l.t0 + BAR || i === 3) return;
    const k = Math.floor((t - l.t0) / BAR);
    ctx.globalAlpha = .35 * (1 - seg(t, bt(19, 3), bt(20))); text(l.text, 640, 300 - 70 * k, 30, '#ffe7c4', 400); ctx.globalAlpha = 1;
  });
}

// ============================================================================
//  传承 (48 – 57.6 s): the light passes on — a new light on every beat
// ============================================================================
const NODES = (() => {
  const out = [{ x: 640, y: 470, parent: -1 }];
  for (let i = 0; i < 16; i++) {
    const parent = Math.floor(H(i + 40) * out.length * .8), P = out[parent];
    const a = -Math.PI / 2 + (H(i + 50) - .5) * 2.6, r = 110 + H(i + 60) * 90;
    out.push({ x: clamp(P.x + Math.cos(a) * r * 1.4, 80, 1200), y: clamp(P.y + Math.sin(a) * r * .8 + 20, 330, 640), parent });
  }
  return out;
})();
function sLegacy(t) {
  const t0 = bt(20), p = seg(t, t0, bt(24));
  ctx.fillStyle = vgrad(['#3b2c5e', '#e38b6f', '#ffd49a']); ctx.fillRect(0, 0, VW, VH);
  ctx.fillStyle = `rgba(42,29,79,${1 - seg(t, t0, t0 + BEAT * 2)})`; ctx.fillRect(0, 0, VW, VH);
  glow(640, 720, 700, 'rgba(255,230,170,.8)', .6 + .4 * p);
  // gentle hills
  ctx.fillStyle = 'rgba(80,50,90,.45)'; ctx.beginPath(); ctx.moveTo(0, 720); for (let x = 0; x <= VW; x += 20) ctx.lineTo(x, 660 + Math.sin(x * .006 + 1) * 24); ctx.lineTo(VW, 720); ctx.fill();
  // lights passed on — each one appears exactly on its bell
  for (const nd of SCORE.node) {
    if (t < nd.t) continue;
    const N = NODES[nd.i + 1], P = NODES[N.parent], d = t - nd.t, q = eout(seg(d, 0, .25));
    ctx.save(); ctx.strokeStyle = 'rgba(255,248,230,.6)'; ctx.lineWidth = 2; ctx.shadowColor = '#fff3d0'; ctx.shadowBlur = 10;
    ctx.beginPath(); ctx.moveTo(P.x, P.y); ctx.lineTo(lerp(P.x, N.x, q), lerp(P.y, N.y, q)); ctx.stroke(); ctx.restore();
    const r = 9 * back(seg(d, .15, .4)) * (1 + .15 * Math.sin(t * 3 + nd.i));
    glow(N.x, N.y, 50 + 40 * Math.exp(-d * 5), 'rgba(255,240,200,.8)'); circ(N.x, N.y, r, '#fffaf0');
  }
  const r0 = 24 + 4 * hit(SCORE.node, t, 6);
  glow(640, 470, 200, 'rgba(255,230,180,.9)'); circ(640, 470, r0, '#fffaf0');
  typedLine(WORDS.legacy[0], 640, 150, 58, t, bt(24) - .2, { weight: 700, color: '#fffaf2', glow: 'rgba(120,60,40,.6)' });
  typedLine(WORDS.legacy[1], 640, 240, 70, t, bt(24) - .2, { weight: 900, color: '#ffffff', glow: 'rgba(120,60,40,.7)' });
}

// ============================================================================
//  尾声 (57.6 – 60 s): one more heartbeat
// ============================================================================
function sOutro(t) {
  ctx.fillStyle = '#06070b'; ctx.fillRect(0, 0, VW, VH);
  ecg(t, 640, 470, 130, '#ffd9a0', 1 - seg(t, 59.3, 59.95));
  ctx.save(); ctx.globalAlpha = 1 - seg(t, 59.3, 59.95);
  slam('人生的意义', 640, 250, 76, t, WORDS.outro.title, Infinity, { glow: 'rgba(255,220,160,.5)', from: .3 });
  slam('—— 愿你，活出自己的答案', 640, 340, 30, t, WORDS.outro.sub, Infinity, { weight: 400, color: '#e8dcc8', from: .2 });
  ctx.restore();
}

function drawFrame(c, t, scale) {
  ctx = c; t = clamp(t, 0, DUR - 1e-4);
  ctx.setTransform(scale, 0, 0, scale, 0, 0); ctx.globalAlpha = 1;
  if (t < bt(4)) sQuestion(t);
  else if (t < bt(8)) sChildhood(t);
  else if (t < bt(12)) sYouth(t);
  else if (t < bt(16)) sValley(t);
  else if (t < bt(20)) sAnswer(t);
  else if (t < bt(24)) sLegacy(t);
  else sOutro(t);
}
