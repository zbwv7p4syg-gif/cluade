// visuals.js — draws frame t. Every beat-driven effect reads SCORE from score.js.
// Frames are 1/30 s apart and 128 BPM beats don't fall on whole frames, so events are
// shown on the nearest frame (LOOK = half a frame): picture error ≤ 16.7 ms.

const VW = 1280, VH = 720, TAU = Math.PI * 2, LOOK = 1 / 60;
const F_BIG = '"QingKe", "NotoSC", sans-serif';
const F_EN = 'Fredoka, "NotoSC", sans-serif';
const F_SC = '"NotoSC", sans-serif';
const F_MONO = '"DejaVu Sans Mono", "NotoSC", monospace';
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
const frac = x => x - Math.floor(x);
function since(list, t) {
  t += LOOK; let lo = 0, hi = list.length - 1, best = -1;
  while (lo <= hi) { const m = (lo + hi) >> 1; if (list[m].t <= t) { best = m; lo = m + 1; } else hi = m - 1; }
  return best < 0 ? Infinity : t - list[best].t;
}
const lastEv = (list, t) => { t += LOOK; let e = null; for (const x of list) { if (x.t <= t) e = x; else break; } return e; };
const hit = (list, t, k = 10) => { const d = since(list, t); return d === Infinity ? 0 : Math.exp(-d * k); };
const beatPhase = t => frac((t + LOOK) / BEAT);      // 0 exactly on each beat

// ---------------------------------------------------------------- drawing helpers
function circ(x, y, r, fill) { ctx.beginPath(); ctx.arc(x, y, Math.max(0, r), 0, TAU); ctx.fillStyle = fill; ctx.fill(); }
function glow(x, y, r, color, a = 1) {
  if (r <= 0 || a <= 0.001) return;
  const g = ctx.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, color); g.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.save(); ctx.globalAlpha = clamp(a); ctx.fillStyle = g; ctx.fillRect(x - r, y - r, r * 2, r * 2); ctx.restore();
}
function text(s, x, y, size, color, font = F_BIG, weight = 400, align = 'center', stroke = null, sw = 0) {
  ctx.font = `${weight} ${size}px ${font}`; ctx.textAlign = align; ctx.textBaseline = 'middle';
  if (stroke) { ctx.lineJoin = 'round'; ctx.strokeStyle = stroke; ctx.lineWidth = sw; ctx.strokeText(s, x, y); }
  ctx.fillStyle = color; ctx.fillText(s, x, y);
}
const hsl = (h, s = 100, l = 60, a = 1) => `hsla(${((h % 360) + 360) % 360},${s}%,${l}%,${a})`;

// ---------------------------------------------------------------- sections
const SEC = t => t < bt(4) ? 'intro' : t < bt(8) ? 'groove' : t < bt(12) ? 'calm' : t < bt(16) ? 'build' : t < bt(24) ? 'drop' : t < bt(30) ? 'drop2' : 'outro';
function hue(t) {
  const s = SEC(t);
  if (s === 'groove') return 300 + 40 * Math.sin(t * .5);
  if (s === 'calm') return 230 + 20 * Math.sin(t * .3);
  if (s === 'build') return lerp(260, 350, seg(t, bt(12), bt(16)));
  if (s === 'drop') return [20, 190, 300, 50][Math.floor((t + LOOK - bt(16)) / BAR) % 4];
  if (s === 'drop2') return (Math.floor((t + LOOK - bt(24)) / BEAT) * 47) % 360;
  return 40;
}
function energy(t) {
  const s = SEC(t);
  return s === 'groove' ? .6 : s === 'calm' ? .15 : s === 'build' ? lerp(.2, .9, seg(t, bt(12), bt(15, 3))) : s === 'outro' ? lerp(1, .5, seg(t, bt(30), DUR)) : 1;
}

// ============================================================================
//  The Claude Code terminal (bars 0–3), drawn to its own canvas so it can shatter
// ============================================================================
const termCv = document.createElement('canvas');
function drawTerminal(c, t) {
  const save = ctx; ctx = c;
  ctx.fillStyle = '#0b0b10'; ctx.fillRect(0, 0, VW, VH);
  // light leaking through from the party behind the wall, pulsing with the muffled kick
  const k = hit(SCORE.kick, t, 7), cr = SCORE.crack.filter(e => e.t <= t + LOOK).length;
  glow(640, 360, 700, hsl(300 + 40 * Math.sin(t), 90, 50, .5), .08 + .12 * k + cr * .06);
  rr(150, 70, 980, 580, 16, '#15141c', '#34303f');
  rr(150, 70, 980, 38, [16, 16, 0, 0], '#1f1d28');
  circ(176, 89, 7, '#ff5f57'); circ(198, 89, 7, '#febc2e'); circ(220, 89, 7, '#28c840');
  text('claude — ~/party', 640, 90, 15, '#8d88a0', F_MONO, 400);
  // welcome box
  ctx.strokeStyle = '#D97757'; ctx.lineWidth = 2; ctx.beginPath(); ctx.roundRect(186, 128, 500, 96, 10); ctx.stroke();
  clawd(ctx, 232, 205, 5.2, { phones: false, seed: 1 }, t);
  text('✻ Welcome to Claude Code!', 290, 158, 20, '#f0e9f5', F_MONO, 700, 'left');
  text('/help 查看帮助 · cwd: ~/party', 290, 192, 15, '#8d88a0', F_MONO, 400, 'left');
  // prompt, typed one character per 16th
  const chars = [...PROMPT.text], n = chars.filter((_, i) => bt(0, 0, i) <= t + LOOK).length;
  text('>', 190, 268, 22, '#D97757', F_MONO, 700, 'left');
  text(chars.slice(0, n).join(''), 218, 268, 22, '#ffffff', F_SC, 700, 'left');
  if (n < chars.length || Math.floor(t * 3) % 2 === 0) {
    ctx.font = `700 22px ${F_SC}`; const w = ctx.measureText(chars.slice(0, n).join('')).width;
    if (t < bt(1)) { ctx.fillStyle = '#e8e2f0'; ctx.fillRect(220 + w, 256, 11, 24); }
  }
  TERM_LINES.forEach((l, i) => {
    if (t + LOOK < l.t) return;
    const d = t + LOOK - l.t;
    ctx.save(); ctx.globalAlpha = clamp(d / .05); ctx.translate(-12 * Math.exp(-d * 20), 0);
    text(l.text, 190, 318 + i * 44, 22, l.color, F_SC, 700, 'left'); ctx.restore();
  });
  // cracks, each one appearing on its beat
  SCORE.crack.forEach((e, ci) => {
    const d = t + LOOK - e.t; if (d < 0) return;
    const grow = eout(d / .12), cx = 640 + (H(ci + 3) - .5) * 300, cy = 380 + (H(ci + 5) - .5) * 200;
    ctx.save(); ctx.globalCompositeOperation = 'lighter';
    for (let r = 0; r < 7; r++) {
      let x = cx, y = cy, a = r / 7 * TAU + H(ci * 9 + r);
      const L = (120 + H(ci * 13 + r) * 260) * grow * (1 + ci * .35);
      ctx.beginPath(); ctx.moveTo(x, y);
      for (let s = 0; s < 8; s++) { a += (H(ci * 31 + r * 7 + s) - .5) * .9; x += Math.cos(a) * L / 8; y += Math.sin(a) * L / 8; ctx.lineTo(x, y); }
      ctx.strokeStyle = hsl(300 + ci * 30, 100, 75, .9); ctx.lineWidth = 3; ctx.shadowColor = hsl(300 + ci * 30, 100, 60); ctx.shadowBlur = 16; ctx.stroke();
      ctx.strokeStyle = 'rgba(255,255,255,.9)'; ctx.lineWidth = 1.2; ctx.shadowBlur = 0; ctx.stroke();
    }
    ctx.restore();
    glow(cx, cy, 160, hsl(300 + ci * 30, 100, 65, .8), Math.exp(-d * 6));
  });
  ctx = save;
}
function rr(x, y, w, h, r, fill, stroke, lw = 2) {
  ctx.beginPath(); ctx.roundRect(x, y, w, h, r);
  if (fill) { ctx.fillStyle = fill; ctx.fill(); }
  if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = lw; ctx.stroke(); }
}
// shards: a jittered triangle grid over the screen
const SHARDS = (() => {
  const cols = 9, rows = 6, P = [];
  for (let j = 0; j <= rows; j++) for (let i = 0; i <= cols; i++) {
    const edge = i === 0 || j === 0 || i === cols || j === rows;
    P.push([i * VW / cols + (edge ? 0 : (H(i * 17 + j) - .5) * 90), j * VH / rows + (edge ? 0 : (H(i * 29 + j * 3) - .5) * 70)]);
  }
  const id = (i, j) => j * (cols + 1) + i, out = [];
  for (let j = 0; j < rows; j++) for (let i = 0; i < cols; i++) {
    const a = P[id(i, j)], b = P[id(i + 1, j)], c = P[id(i + 1, j + 1)], d = P[id(i, j + 1)];
    for (const tri of (H(i + j * 11) > .5 ? [[a, b, c], [a, c, d]] : [[a, b, d], [b, c, d]])) {
      const cx = (tri[0][0] + tri[1][0] + tri[2][0]) / 3, cy = (tri[0][1] + tri[1][1] + tri[2][1]) / 3;
      const dx = cx - 640, dy = cy - 380, L = Math.hypot(dx, dy) + 1, sp = 500 + H(out.length + 50) * 900;
      out.push({ tri, cx, cy, vx: dx / L * sp, vy: dy / L * sp - 200, w: (H(out.length + 90) - .5) * 14, z: .5 + H(out.length) * 1.2 });
    }
  }
  return out;
})();
function drawShards(t) {
  const d = t + LOOK - bt(4); if (d < 0 || d > 1.4) return;
  for (const s of SHARDS) {
    const x = s.vx * d, y = s.vy * d + 900 * d * d, sc = 1 + s.z * d * .8;
    ctx.save(); ctx.globalAlpha = 1 - seg(d, .7, 1.4);
    ctx.translate(s.cx + x, s.cy + y); ctx.rotate(s.w * d); ctx.scale(sc, sc); ctx.translate(-s.cx, -s.cy);
    ctx.beginPath(); ctx.moveTo(...s.tri[0]); ctx.lineTo(...s.tri[1]); ctx.lineTo(...s.tri[2]); ctx.closePath();
    ctx.save(); ctx.clip(); ctx.drawImage(termCv, 0, 0, VW, VH); ctx.restore();
    ctx.strokeStyle = 'rgba(255,255,255,.7)'; ctx.lineWidth = 1.5; ctx.stroke();
    ctx.restore();
  }
}

// ============================================================================
//  The club
// ============================================================================
function camera(t) {
  let cx = 640, cy = 360, z = 1, rot = 0;
  const s = SEC(t);
  if (s === 'groove') { z = lerp(1.18, 1, eout(seg(t, bt(4), bt(4) + .7))) + .06 * seg(t, bt(4, 2), bt(8)); }
  else if (s === 'calm') { z = lerp(1.0, 1.12, eio(seg(t, bt(8), bt(12)))); cy = lerp(360, 350, seg(t, bt(8), bt(12))); cx = 640 + Math.sin(t * .4) * 20; }
  else if (s === 'build') { const p = eio(seg(t, bt(12), bt(15, 3))); z = lerp(1.12, 1.55, p); cy = lerp(350, 385, p); }
  else if (s === 'drop' || s === 'drop2') {
    z = 1 + .035 * hit(SCORE.kick, t, 10);
    const k = hit(SCORE.kick, t, 14), bi = Math.floor((t + LOOK) / BEAT);
    cx += (H(bi) - .5) * 14 * k; cy += (H(bi + 7) - .5) * 14 * k;
    if (s === 'drop2') rot = Math.sin((t - bt(24)) * Math.PI / BAR) * .025;
    const sp = surfPos(t); if (sp) { cx = lerp(640, sp.x, sp.w * .6); }
  } else { z = lerp(1, 1.08, seg(t, bt(30), DUR)); cy = 350; }
  return { cx, cy, z, rot };
}
// Clawd crowd-surfing in drop 2
function surfPos(t) {
  if (t < SURF.up || t >= SURF.back + BEAT) return null;
  let x, y, rot, w;
  if (t < SURF.start) { const p = seg(t, SURF.up, SURF.start); x = lerp(640, 330, p); y = lerp(432, 560, p) - Math.sin(p * Math.PI) * 160; rot = -1.3 * p; w = p; }
  else if (t < SURF.end) { const p = seg(t, SURF.start, SURF.end); x = lerp(330, 950, p); y = 560 - Math.abs(Math.sin((t + LOOK) / BEAT * Math.PI)) * 14; rot = -1.3 + Math.sin(t * 5) * .15; w = 1; }
  else { const p = seg(t, SURF.end, SURF.back); x = lerp(950, 640, eio(p)); y = lerp(560, 432, p) - Math.sin(p * Math.PI) * 200; rot = lerp(-1.3, 0, p); w = 1 - p; }
  if (t >= SURF.back) return null;
  return { x, y, rot, w };
}

function drawLED(t, x, y, w, h) {
  ctx.save(); ctx.beginPath(); ctx.roundRect(x, y, w, h, 10); ctx.clip();
  ctx.fillStyle = '#05040a'; ctx.fillRect(x, y, w, h);
  const s = SEC(t), cx = x + w / 2, cy = y + h / 2, hu = hue(t), k = hit(SCORE.kick, t, 8);
  if (s === 'groove') {
    for (let i = 0; i < 32; i++) {
      const bh = (0.25 + 0.5 * k * (0.6 + H(i + Math.floor(t * 8)) * .4) + 0.25 * hit(SCORE.ohat, t, 10) * H(i * 3)) * h * .55;
      ctx.fillStyle = hsl(hu + i * 4, 100, 60, .9); ctx.fillRect(x + 20 + i * (w - 40) / 32, y + h - 16 - bh, (w - 40) / 32 - 4, bh);
    }
    text('CLAUDE CODE', cx, cy - 40, 64, '#fff', F_EN, 700, 'center', hsl(hu, 100, 50, .8), 8 + 8 * k);
  } else if (s === 'calm') {
    for (let l = 0; l < 3; l++) {
      ctx.strokeStyle = hsl(hu + l * 40, 90, 65, .6); ctx.lineWidth = 3; ctx.beginPath();
      for (let i = 0; i <= w; i += 8) ctx.lineTo(x + i, cy + Math.sin(i * .012 + t * (0.8 + l * .3) + l) * (30 + l * 12));
      ctx.stroke();
    }
    text('深呼吸', cx, cy, 54, 'rgba(255,255,255,.85)', F_BIG);
  } else if (s === 'build') {
    const p = seg(t, bt(12), bt(15, 3));
    const spin = '✻✶✳✢'[Math.floor(t * 8) % 4];
    text(`${spin} 酝酿中……`, cx, cy - 55, 40, '#ffb38a', F_SC, 700);
    rr(x + 70, cy + 5, w - 140, 34, 17, 'rgba(255,255,255,.12)');
    rr(x + 70, cy + 5, Math.max(34, (w - 140) * p), 34, 17, hsl(hu, 100, 60));
    text(`${Math.floor(p * 100)}%`, cx, cy + 72, 30, '#fff', F_EN, 700);
  } else if (s === 'drop' || s === 'drop2') {
    for (const e of SCORE.kick) {
      const d = t + LOOK - e.t; if (d < 0 || d > 1) continue;
      ctx.strokeStyle = hsl(hu + d * 120, 100, 60, 1 - d); ctx.lineWidth = 10 * (1 - d); ctx.beginPath(); ctx.arc(cx, cy, d * w * .6, 0, TAU); ctx.stroke();
    }
    const sp = surfPos(t);
    if (sp && t > SURF.start - BEAT) {
      text('⏵⏵ 自动模式已开启', cx, cy - 30, 44, '#7ee787', F_SC, 700);
      text('Clawd 正在人群里冲浪……', cx, cy + 34, 28, '#fff', F_SC, 700);
    } else {
      ctx.save(); ctx.translate(cx, cy); ctx.rotate(t * 1.5); ctx.scale(1 + .25 * k, 1 + .25 * k);
      text('✻', 0, 6, 150, hsl(hu, 100, 65), F_SC, 700); ctx.restore();
    }
  } else {
    text('谢谢大家！', cx, cy, 70, '#fff', F_BIG, 400, 'center', hsl(40, 100, 45), 10);
  }
  // LED pixel grid
  ctx.fillStyle = 'rgba(0,0,0,.28)';
  for (let i = x; i < x + w; i += 5) ctx.fillRect(i, y, 1.5, h);
  for (let j = y; j < y + h; j += 5) ctx.fillRect(x, j, w, 1.5);
  ctx.restore();
  ctx.strokeStyle = '#26232f'; ctx.lineWidth = 8; ctx.beginPath(); ctx.roundRect(x, y, w, h, 10); ctx.stroke();
}

// moving-head beams: sweep smoothly, and in the drops snap to a new fan shape on every kick
const FANS = [[-.5, -.35, -.2, -.05, .05, .2, .35, .5], [.4, .2, 0, -.2, .2, 0, -.2, -.4], [-.3, .3, -.3, .3, -.3, .3, -.3, .3], [0, 0, 0, 0, 0, 0, 0, 0]];
function beams(t) {
  const s = SEC(t), E = energy(t), hu = hue(t);
  if (s === 'intro') return;
  ctx.save(); ctx.globalCompositeOperation = 'lighter';
  for (let k = 0; k < 8; k++) {
    const hx = 100 + k * 154, hy = 52;
    let a;
    if (s === 'drop' || s === 'drop2') { const bi = Math.floor((t + LOOK) / BEAT); a = FANS[bi % 4][k] * 1.1 + Math.sin(t * 2 + k) * .05; }
    else if (s === 'calm') a = (k - 3.5) * .06 + Math.sin(t * .3 + k) * .05;
    else a = Math.sin(t * (s === 'build' ? lerp(.8, 4, seg(t, bt(12), bt(16))) : 1) + k * .8) * .5;
    const len = 800, wd = s === 'calm' ? 50 : 70, ex = hx + Math.sin(a) * len, ey = hy + Math.cos(a) * len;
    const g = ctx.createLinearGradient(hx, hy, ex, ey);
    const al = (s === 'calm' ? .12 : .08 + .22 * E) * (1 + .8 * hit(SCORE.kick, t, 9) * E);
    g.addColorStop(0, hsl(hu + k * (s === 'drop2' ? 45 : 8), 100, 65, al)); g.addColorStop(1, hsl(hu, 100, 50, 0));
    ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(hx - 4, hy); ctx.lineTo(hx + 4, hy);
    ctx.lineTo(ex + Math.cos(a) * wd, ey - Math.sin(a) * wd); ctx.lineTo(ex - Math.cos(a) * wd, ey + Math.sin(a) * wd); ctx.closePath(); ctx.fill();
  }
  ctx.restore();
}
function lasers(t) {
  const s = SEC(t); if (!(s === 'drop' || s === 'drop2' || (s === 'build' && t > bt(15)) || (s === 'outro' && t < bt(30, 3)))) return;
  const bi = Math.floor((t + LOOK) / BEAT), hu = s === 'drop2' ? (bi * 70) % 360 : 140;
  ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.lineCap = 'round';
  for (const [ox, oy, dir] of [[470, 468, -1], [810, 468, 1], [10, 30, 1], [1270, 30, -1]]) {
    for (let k = 0; k < 6; k++) {
      const a = (dir > 0 ? 0 : Math.PI) + dir * ((bi % 2 ? .15 : -.1) + k * .09 + Math.sin(t * 3 + k) * .04) * (oy > 100 ? -1 : 1) * (oy > 100 ? 1.8 : -1.2);
      const ex = ox + Math.cos(a) * 1600, ey = oy + Math.sin(a) * 1600;
      ctx.strokeStyle = hsl(hu + k * 12, 100, 60, .35); ctx.lineWidth = 6; ctx.beginPath(); ctx.moveTo(ox, oy); ctx.lineTo(ex, ey); ctx.stroke();
      ctx.strokeStyle = hsl(hu + k * 12, 100, 85, .9); ctx.lineWidth = 1.6; ctx.stroke();
    }
  }
  ctx.restore();
}
function speakers(t) {
  const k = hit(SCORE.kick, t, 10) * (SEC(t) === 'calm' ? 0 : 1);
  for (const x0 of [30, 1090]) {
    for (let j = 0; j < 2; j++) {
      rr(x0, 250 + j * 140, 160, 132, 8, '#15131c', '#2a2633', 3);
      circ(x0 + 80, 316 + j * 140, 48 * (1 + .09 * k), '#0c0b11'); circ(x0 + 80, 316 + j * 140, 40 * (1 + .12 * k), '#22202b'); circ(x0 + 80, 316 + j * 140, 14, '#34313e');
    }
  }
}
function booth(t) {
  // decks
  for (const [px, dirn] of [[525, 1], [755, -1]]) {
    ctx.beginPath(); ctx.ellipse(px, 404, 62, 15, 0, 0, TAU); ctx.fillStyle = '#1a1822'; ctx.fill();
    ctx.beginPath(); ctx.ellipse(px, 402, 52, 12, 0, 0, TAU); ctx.fillStyle = '#0d0c12'; ctx.fill();
    const a = t * 7 * dirn; ctx.strokeStyle = '#D97757'; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(px, 402); ctx.lineTo(px + Math.cos(a) * 48, 402 + Math.sin(a) * 11); ctx.stroke();
  }
  // laptop lid facing the crowd
  ctx.beginPath(); ctx.moveTo(605, 404); ctx.lineTo(611, 356); ctx.lineTo(669, 356); ctx.lineTo(675, 404); ctx.closePath(); ctx.fillStyle = '#2a2833'; ctx.fill();
  glow(640, 380, 40, 'rgba(217,119,87,.9)', .6 + .4 * hit(SCORE.kick, t, 8)); text('✻', 640, 382, 26, '#F2A283', F_SC, 700);
  // front panel
  const g = ctx.createLinearGradient(0, 405, 0, 520); g.addColorStop(0, '#1d1a26'); g.addColorStop(1, '#0c0b11');
  rr(430, 405, 420, 110, [6, 6, 0, 0], g, '#2d2938', 2);
  const hu = hue(t), k = hit(SCORE.kick, t, 8) * energy(t);
  for (let i = 0; i < 20; i++) { ctx.fillStyle = hsl(hu + i * 9 + t * 60, 100, 55, .35 + .65 * k); ctx.fillRect(446 + i * 19.5, 418, 13, 5); }
  text('CLAUDE CODE', 640, 460, 30, 'rgba(255,255,255,.9)', F_EN, 700);
  text('✻ DJ CLAWD ✻', 640, 492, 16, '#F2A283', F_EN, 600);
}
function clawdPose(t) {
  const s = SEC(t), f = beatPhase(t), bar = (t + LOOK) / BAR;
  const o = { seed: 2, eyes: 'shades', aL: .45, aR: .45, dy: 0, sq: 0, rot: 0, shadeColor: hsl(hue(t), 100, 70) };
  if (s === 'groove') { o.dy = -.35 * Math.sin(f * Math.PI); o.sq = .06 * Math.exp(-f * 8); o.aL = .55 + .18 * Math.sin((t + LOOK) / STEP * Math.PI); o.aR = frac(bar) < .25 ? 2.6 : .4; }
  if (s === 'calm') { o.eyes = 'closed'; o.rot = Math.sin(t * Math.PI / BAR) * .06; o.aL = 2.2 + Math.sin(t * 1.6) * .25; o.aR = 2.2 - Math.sin(t * 1.6) * .25; }
  if (s === 'build') {
    const p = seg(t, bt(12), bt(15, 3));
    o.eyes = p > .6 ? 'normal' : 'closed'; o.aR = lerp(1, 2.9, p); o.aL = .5 + hit(SCORE.roll, t, 20) * .3; o.sq = .12 * p;
    if (t + LOOK >= bt(15, 3)) { const q = seg(t + LOOK, bt(15, 3), bt(16)); o.dy = -5 * Math.sin(q * Math.PI * .5); o.aL = o.aR = 2.9; o.sq = -.08; o.eyes = 'star'; }
  }
  if (s === 'drop' || s === 'drop2') {
    o.dy = -3.2 * 4 * f * (1 - f); o.sq = .16 * Math.exp(-f * 12) - .06 * Math.sin(f * Math.PI);
    o.aL = 2.6 + .25 * Math.sin(f * TAU); o.aR = 2.6 - .25 * Math.sin(f * TAU); o.mouth = 'open';
    o.eyes = t + LOOK < bt(17) || within(t + LOOK, bt(24), bt(25)) ? 'star' : 'shades';
  }
  if (s === 'outro') { o.eyes = 'happy'; o.mouth = 'open'; o.aL = o.aR = 2.8; const p = seg(t, bt(30), bt(30, 1)); o.dy = -2 * Math.sin(p * Math.PI); }
  return o;
}

// ---- the crowd: three rows of silhouettes
const CROWD = (() => {
  const out = [];
  [[20, 600, .8], [17, 650, 1], [13, 712, 1.3]].forEach(([n, y, s], r) => {
    for (let i = 0; i < n; i++) out.push({ r, x: (i + .5) * VW / n + (H(r * 50 + i) - .5) * 40, y, s: s * (.9 + H(r * 70 + i) * .2), amp: .7 + H(r * 90 + i) * .6, ph: H(r * 33 + i), phone: H(r * 11 + i) });
  });
  return out;
})();
function drawCrowd(t) {
  const s = SEC(t), f = beatPhase(t), hu = hue(t), E = energy(t), sp = surfPos(t);
  for (const p of CROWD) {
    let dx = 0, dy = 0, arms = 'down', phone = false;
    if (s === 'groove') { dy = 7 * Math.exp(-f * 6) * p.s; arms = p.ph > .75 && frac((t + LOOK) / BAR) < .5 ? 'one' : 'down'; }
    if (s === 'calm') { dx = Math.sin(t * Math.PI / BAR + p.x * .004) * 12; phone = p.phone < seg(t, bt(8), bt(10.5)); arms = phone ? 'phone' : 'down'; }
    if (s === 'build') {
      const cr = seg(t, bt(13), bt(15, 3)); dy = cr * 26 * p.s; phone = t < bt(13) && p.phone < 1;
      arms = t + LOOK >= bt(15) ? 'up' : phone ? 'phone' : 'down';
      if (t + LOOK >= bt(15, 3)) dy = lerp(26 * p.s, -30 * p.s * p.amp, eout(seg(t + LOOK, bt(15, 3), bt(16))));
    }
    if (s === 'drop' || s === 'drop2') { dy = -46 * p.s * p.amp * 4 * f * (1 - f); arms = 'up'; }
    if (s === 'outro') { const q = seg(t + LOOK, bt(30), bt(30, 1)); dy = -60 * p.s * p.amp * Math.sin(q * Math.PI); arms = 'up'; }
    if (sp && sp.w > .5 && Math.abs(p.x - sp.x) < 150 && p.r < 2) arms = 'reach';
    const x = p.x + dx, y = p.y + dy, S = p.s, hr = 17 * S;
    const shade = ['#1a1428', '#120e1d', '#0a0812'][p.r];
    ctx.fillStyle = shade; ctx.strokeStyle = shade; ctx.lineCap = 'round';
    // arms
    ctx.lineWidth = 9 * S;
    const shL = [x - 20 * S, y - 10 * S], shR = [x + 20 * S, y - 10 * S], wave = Math.sin(t * 8 + p.ph * 6) * 8 * S;
    const armTo = (sh, side) => {
      if (arms === 'up') return [sh[0] + side * 16 * S + wave * side, sh[1] - 62 * S];
      if (arms === 'reach') return [sh[0] + side * 6 * S, sh[1] - 70 * S];
      if (arms === 'one' && side > 0) return [sh[0] + 12 * S, sh[1] - 60 * S];
      if (arms === 'phone' && side > 0) return [sh[0] + 4 * S, sh[1] - 56 * S];
      return null;
    };
    for (const [sh, side] of [[shL, -1], [shR, 1]]) { const h = armTo(sh, side); if (h) { ctx.beginPath(); ctx.moveTo(...sh); ctx.lineTo(...h); ctx.stroke(); circ(h[0], h[1], 6 * S, shade); if (arms === 'phone' && side > 0) { glow(h[0], h[1] - 10 * S, 34 * S, 'rgba(230,240,255,.9)', .8); ctx.fillStyle = '#eef4ff'; ctx.fillRect(h[0] - 4 * S, h[1] - 18 * S, 8 * S, 13 * S); ctx.fillStyle = shade; } } }
    // body + head
    ctx.beginPath(); ctx.roundRect(x - 26 * S, y - 14 * S, 52 * S, 200, 18 * S); ctx.fill();
    circ(x, y - 30 * S, hr, shade);
    // rim light from the stage
    ctx.save(); ctx.globalAlpha = .35 + .5 * E * hit(SCORE.kick, t, 6);
    ctx.strokeStyle = hsl(hu + p.x * .05, 100, 65); ctx.lineWidth = 2;
    ctx.beginPath(); ctx.arc(x, y - 30 * S, hr, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke();
    ctx.restore();
  }
}
// ---- CO2 jets, flames, confetti
function effects(t) {
  for (const e of SCORE.hiss) {
    const d = t + LOOK - e.t; if (d < 0 || d > 1.1) continue;
    for (const x of [330, 950]) {
      const h = 420 * eout(d / .25), a = 1 - seg(d, .5, 1.1);
      const g = ctx.createLinearGradient(0, 470, 0, 470 - h); g.addColorStop(0, `rgba(255,255,255,${.8 * a})`); g.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = g; ctx.beginPath(); ctx.moveTo(x - 10, 470); ctx.lineTo(x + 10, 470); ctx.lineTo(x + 60, 470 - h); ctx.lineTo(x - 60, 470 - h); ctx.fill();
    }
  }
  for (const e of SCORE.pyro) {
    const d = t + LOOK - e.t; if (d < 0 || d > .8) continue;
    for (const x of [240, 1040]) {
      const h = 260 * eout(d / .12) * (1 - seg(d, .45, .8)), fl = Math.sin(t * 60 + x) * 10;
      glow(x, 470 - h * .5, 260, 'rgba(255,140,40,.8)', 1 - d / .8);
      for (const [c, wmul] of [['#ff5a1f', 1], ['#ffb02e', .65], ['#fff1b0', .3]]) {
        ctx.fillStyle = c; ctx.beginPath(); ctx.moveTo(x - 36 * wmul, 470); ctx.quadraticCurveTo(x - 40 * wmul + fl, 470 - h * .6, x + fl * .5, 470 - h * wmul);
        ctx.quadraticCurveTo(x + 40 * wmul - fl, 470 - h * .6, x + 36 * wmul, 470); ctx.fill();
      }
    }
  }
  for (const [ci, e] of SCORE.confetti.entries()) {
    const d = t + LOOK - e.t; if (d < 0 || d > 5) continue;
    for (let i = 0; i < 160; i++) {
      const side = i % 2 ? 1 : -1, x0 = side > 0 ? 330 : 950, v = 700 + H(i + ci * 300) * 700, a = -Math.PI / 2 + side * (.1 + H(i * 3 + ci) * .7);
      const drag = 1 - Math.exp(-d * 2.2);
      const x = x0 + Math.cos(a) * v * drag / 2.2 + Math.sin(d * 3 + i) * 20, y = 470 + Math.sin(a) * v * drag / 2.2 + 90 * d * d;
      if (y > 760) continue;
      ctx.save(); ctx.translate(x, y); ctx.rotate(d * (4 + H(i) * 8)); ctx.scale(1, Math.sin(d * 9 + i));
      ctx.fillStyle = hsl(H(i + 5) * 360, 100, 60); ctx.fillRect(-6, -3, 12, 6); ctx.restore();
    }
  }
}

function club(t) {
  const hu = hue(t), E = energy(t), cam = camera(t);
  ctx.fillStyle = '#05040a'; ctx.fillRect(0, 0, VW, VH);
  ctx.save(); ctx.translate(640, 360); ctx.rotate(cam.rot); ctx.scale(cam.z, cam.z); ctx.translate(-cam.cx, -cam.cy);
  const bg = ctx.createLinearGradient(0, 0, 0, 520); bg.addColorStop(0, '#07060d'); bg.addColorStop(1, hsl(hu, 60, 10));
  ctx.fillStyle = bg; ctx.fillRect(-200, -200, 1680, 1120);
  glow(640, 250, 700, hsl(hu, 100, 50, .35), .3 + .5 * E * hit(SCORE.kick, t, 5));
  drawLED(t, 300, 70, 680, 260);
  // truss + heads
  ctx.fillStyle = '#23202b'; ctx.fillRect(-100, 30, 1480, 16);
  ctx.strokeStyle = '#34303e'; ctx.lineWidth = 2; ctx.beginPath(); for (let x = -100; x < 1380; x += 30) { ctx.moveTo(x, 30); ctx.lineTo(x + 15, 46); ctx.lineTo(x + 30, 30); } ctx.stroke();
  for (let k = 0; k < 8; k++) { rr(100 + k * 154 - 12, 44, 24, 18, 4, '#2c2935'); circ(100 + k * 154, 60, 6, hsl(hue(t) + k * 8, 100, 75, .9)); }
  beams(t);
  // stage
  ctx.fillStyle = '#0e0c15'; ctx.fillRect(-100, 470, 1480, 80);
  ctx.fillStyle = hsl(hu, 100, 60, .4 + .6 * hit(SCORE.kick, t, 8) * E); ctx.fillRect(-100, 470, 1480, 4);
  speakers(t);
  effects(t);
  // Clawd: at the decks, or surfing the crowd
  const sp = surfPos(t), pose = clawdPose(t);
  if (!sp) clawd(ctx, 640, 432, 19, pose, t);
  booth(t);
  lasers(t);
  drawCrowd(t);
  if (sp) clawd(ctx, sp.x, sp.y, 17, { ...pose, eyes: 'happy', mouth: 'open', rot: sp.rot, dy: 0, aL: 2.4 + Math.sin(t * 9) * .4, aR: 2.4 - Math.sin(t * 9) * .4 }, t);
  ctx.restore();
  // strobes on the claps in the drops, flashes on impacts
  if (SEC(t) === 'drop' || SEC(t) === 'drop2') { ctx.fillStyle = `rgba(255,255,255,${.28 * hit(SCORE.clap, t, 22)})`; ctx.fillRect(0, 0, VW, VH); }
  ctx.fillStyle = `rgba(255,255,255,${.75 * hit(SCORE.impact, t, 7)})`; ctx.fillRect(0, 0, VW, VH);
  // vignette
  const v = ctx.createRadialGradient(640, 360, 300, 640, 360, 800); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.55)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, VW, VH);
}

// ---------------------------------------------------------------- overlays: shouts, subtitles, countdown, title
function slam(s, x, y, size, t, t0, t1, o = {}) {
  const tt = t + LOOK; if (tt < t0 || tt >= t1) return;
  const d = tt - t0, sc = 1 + (o.from ?? .8) * Math.exp(-d * 14), a = clamp(d / .03) * (1 - seg(tt, t1 - .12, t1));
  ctx.save(); ctx.globalAlpha = a; ctx.translate(x, y); ctx.scale(sc, sc); ctx.rotate((o.rot || 0) * Math.exp(-d * 8));
  if (o.glitch) { const j = 10 * Math.exp(-d * 5); ctx.globalCompositeOperation = 'lighter'; text(s, -j, 0, size, 'rgba(255,0,90,.8)', o.font || F_BIG); text(s, j, 0, size, 'rgba(0,240,255,.8)', o.font || F_BIG); ctx.globalCompositeOperation = 'source-over'; }
  text(s, 0, 0, size, o.color || '#fff', o.font || F_BIG, 400, 'center', o.stroke || 'rgba(0,0,0,.6)', o.sw ?? 12);
  ctx.restore();
}
function subtitle(s, t, t0, t1) {
  const tt = t + LOOK; if (tt < t0 || tt >= t1) return;
  const a = seg(tt, t0, t0 + .3) * (1 - seg(tt, t1 - .3, t1));
  ctx.save(); ctx.globalAlpha = a; ctx.font = `700 30px ${F_SC}`; const w = ctx.measureText(s).width + 56;
  rr(640 - w / 2, 628, w, 56, 28, 'rgba(10,8,18,.6)'); text(s, 640, 657, 30, '#fff', F_SC, 700); ctx.restore();
}
function overlays(t) {
  SHOUTS.forEach(([a, b, s], i) => slam(s, 640, i === 0 ? 360 : 330, i === 0 ? 170 : 150, t, a, b, { glitch: true, rot: i === 1 ? -.08 : .06 }));
  COUNTDOWN.forEach(([ct, s]) => slam(s, 640, 330, 260, t, ct, ct + BEAT, { from: 1.2, stroke: hsl(350, 100, 45), sw: 16 }));
  subtitle('节奏慢下来……', t, bt(8, 2), bt(10));
  subtitle('举起你的光', t, bt(10), bt(12));
  subtitle('要来了……', t, bt(12), bt(14));
  subtitle('全场，蹲下——', t, bt(14), bt(15));
  subtitle('Clawd 冲进了人群！', t, SURF.up, SURF.end);
  if (t + LOOK >= bt(15, 3) && t + LOOK < bt(16)) {        // the silent beat: black, Clawd's star eyes only
    const q = seg(t + LOOK, bt(15, 3), bt(16));
    ctx.fillStyle = `rgba(0,0,0,${.92})`; ctx.fillRect(0, 0, VW, VH);
    for (const ex of [-1, 1]) { glow(640 + ex * 60, 330, 60 + 40 * q, 'rgba(255,224,138,.9)'); text('✦', 640 + ex * 60, 332, 60 + 30 * q, '#FFE08A', F_SC, 700); }
  }
  if (t + LOOK >= bt(30, 2)) {
    const p = back(seg(t + LOOK, bt(30, 2), bt(30, 3))), fade = 1 - seg(t, DUR - .6, DUR);
    ctx.save(); ctx.globalAlpha = fade; ctx.fillStyle = `rgba(5,4,10,${.82 * seg(t + LOOK, bt(30, 2), bt(31))})`; ctx.fillRect(0, 0, VW, VH);
    ctx.translate(640, 250); ctx.scale(p, p);
    text('CLAUDE CODE', 0, -30, 84, '#fff', F_EN, 700, 'center', '#D97757', 12);
    text('电音派对', 0, 70, 96, '#FFE08A', F_BIG, 400, 'center', 'rgba(0,0,0,.6)', 12);
    ctx.restore();
    if (t + LOOK >= bt(31)) {
      const tp = [...'> /exit'], n = tp.filter((_, i) => bt(31, 0, i) <= t + LOOK).length;
      ctx.save(); ctx.globalAlpha = fade;
      text(tp.slice(0, n).join(''), 470, 470, 30, '#e8e2f0', F_MONO, 700, 'left');
      if (t + LOOK >= bt(31, 2)) text('✻ 派对不会结束的～', 640, 530, 34, '#F2A283', F_SC, 700);
      ctx.restore();
    }
  }
}

let termFrozen = false;
function drawFrame(c, t, scale) {
  ctx = c; t = clamp(t, 0, DUR - 1e-4);
  if (termCv.width !== c.canvas.width) { termCv.width = c.canvas.width; termCv.height = c.canvas.height; termFrozen = false; }
  const tc = termCv.getContext('2d');
  ctx.setTransform(scale, 0, 0, scale, 0, 0); ctx.globalAlpha = 1;
  if (t + LOOK < bt(4)) {
    tc.setTransform(scale, 0, 0, scale, 0, 0); drawTerminal(tc, t); termFrozen = false;
    const k = hit(SCORE.kick, t, 12), cr = since(SCORE.crack, t), shake = (cr < .25 ? 10 * Math.exp(-cr * 14) : 0) + 3 * seg(t, bt(3), bt(4)) * Math.sin(t * 90);
    ctx.fillStyle = '#000'; ctx.fillRect(0, 0, VW, VH);
    ctx.save(); ctx.translate(640 + shake * (H(Math.floor(t * 60)) - .5), 360 + shake * (H(Math.floor(t * 60) + 1) - .5) - 2 * k); ctx.scale(1 + .006 * k, 1 + .006 * k); ctx.translate(-640, -360);
    ctx.drawImage(termCv, 0, 0, VW, VH); ctx.restore();
  } else {
    if (!termFrozen) { tc.setTransform(scale, 0, 0, scale, 0, 0); drawTerminal(tc, bt(4) - LOOK - 1e-4); termFrozen = true; }
    club(t);
    drawShards(t);
  }
  overlays(t);
}
