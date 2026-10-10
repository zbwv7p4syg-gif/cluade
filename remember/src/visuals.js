// visuals.js — 我记得 · Claude Code 版. One function per shot (see timeline.js); shots dissolve on the sung
// phrase starts. The present is cool and blue, the remembered past is warm, grainy sepia.

const VW = 1280, VH = 720, TAU = Math.PI * 2;
const SERIF = 'NotoSerifSC, serif', F_EN = 'Fredoka, NotoSerifSC, sans-serif';
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const eout = t => 1 - Math.pow(1 - clamp(t), 3);
const H = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const pulse = (t, k = 7) => Math.exp(-Math.max(0, t - lastKick(t)) * k);          // 1 on a kick, decays after
const layer = document.createElement('canvas');

function glow(c, x, y, r, color, a = 1) {
  if (r <= 0 || a <= .001) return;
  const g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, color); g.addColorStop(1, 'rgba(0,0,0,0)');
  c.save(); c.globalAlpha *= clamp(a); c.fillStyle = g; c.fillRect(x - r, y - r, r * 2, r * 2); c.restore();
}
function vgrad(c, y0, y1, stops) { const g = c.createLinearGradient(0, y0, 0, y1); stops.forEach((s, i) => g.addColorStop(i / (stops.length - 1), s)); return g; }
function withCam(c, cx, cy, z, fn) { c.save(); c.translate(VW / 2, VH / 2); c.scale(z, z); c.translate(-cx, -cy); fn(); c.restore(); }
function veil(c, color, a) { if (a <= .001) return; c.save(); c.globalAlpha = clamp(a); c.fillStyle = color; c.fillRect(-50, -50, VW + 100, VH + 100); c.restore(); }
function rope(c, x1, y1, x2, y2, sag, w = 3) {
  c.save(); c.lineCap = 'round'; c.strokeStyle = INK; c.lineWidth = w + 2; c.beginPath(); c.moveTo(x1, y1); c.quadraticCurveTo((x1 + x2) / 2, Math.max(y1, y2) + sag, x2, y2); c.stroke();
  c.strokeStyle = '#D9B98A'; c.lineWidth = w; c.stroke(); c.restore();
}
function note(c, x, y, s, a) {
  c.save(); c.globalAlpha *= a; c.fillStyle = '#FFD98A'; c.strokeStyle = '#FFD98A'; c.lineWidth = 2.4 * s;
  c.beginPath(); c.ellipse(x, y, 7 * s, 5 * s, -.4, 0, TAU); c.fill(); c.beginPath(); c.moveTo(x + 6 * s, y - 2 * s); c.lineTo(x + 6 * s, y - 26 * s); c.quadraticCurveTo(x + 14 * s, y - 20 * s, x + 16 * s, y - 12 * s); c.stroke();
  c.restore(); glow(c, x, y - 8 * s, 30 * s, 'rgba(255,210,120,.35)', a);
}
function heart(c, x, y, s, a) {
  c.save(); c.globalAlpha *= a; c.translate(x, y); c.scale(s, s); c.beginPath(); c.moveTo(0, 6); c.bezierCurveTo(-14, -4, -8, -16, 0, -8); c.bezierCurveTo(8, -16, 14, -4, 0, 6);
  c.fillStyle = '#FF7FA0'; c.fill(); c.restore();
}
// old-film treatment for everything that is remembered
function memoryGrade(c, t, k = 1) {
  c.save();
  c.globalCompositeOperation = 'soft-light'; c.globalAlpha = .55 * k; c.fillStyle = '#E5A560'; c.fillRect(0, 0, VW, VH);
  c.globalCompositeOperation = 'source-over';
  const fr = Math.floor(t * 12);
  c.globalAlpha = .22 * k; c.fillStyle = '#3B2510';
  for (let i = 0; i < 160; i++) c.fillRect(H(fr * 977 + i) * VW, H(fr * 331 + i * 7) * VH, 1.6, 1.6);
  c.globalAlpha = .18 * k; c.fillStyle = '#FFF2D6';
  for (let i = 0; i < 90; i++) c.fillRect(H(fr * 613 + i * 3) * VW, H(fr * 89 + i * 11) * VH, 1.4, 1.4);
  if (H(fr * 17) > .7) { c.globalAlpha = .12 * k; c.fillStyle = '#4A2E14'; c.fillRect(H(fr * 5) * VW, 0, 1.2, VH); }
  c.globalAlpha = k; const v = c.createRadialGradient(640, 360, 260, 640, 360, 760); v.addColorStop(0, 'rgba(70,35,10,0)'); v.addColorStop(1, 'rgba(70,35,10,.55)'); c.fillStyle = v; c.fillRect(0, 0, VW, VH);
  c.restore();
}

// ---------------------------------------------------------------- the riverbed
function water(c, t, depth) {
  c.fillStyle = vgrad(c, 0, VH, ['#2F7E96', '#195069', '#0B2638']); c.fillRect(0, 0, VW, VH);
  veil(c, '#04101C', depth * .45);
  // light shafts from the surface
  c.save(); c.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 6; i++) {
    const x = 120 + i * 220 + Math.sin(t * .4 + i * 1.7) * 40, w = 40 + 30 * H(i + 3);
    const g = c.createLinearGradient(0, 0, 0, VH); g.addColorStop(0, `rgba(170,230,240,${.16 * (1 - depth * .6)})`); g.addColorStop(1, 'rgba(170,230,240,0)');
    c.fillStyle = g; c.beginPath(); c.moveTo(x, -10); c.lineTo(x + w, -10); c.lineTo(x + w + 160, VH); c.lineTo(x + 120, VH); c.closePath(); c.fill();
  }
  c.restore();
  // drifting motes
  c.fillStyle = 'rgba(210,240,245,.5)';
  for (let i = 0; i < 70; i++) { const x = (H(i) * VW + t * 8 * (H(i + 5) - .3)) % VW, y = (H(i + 9) * VH - t * 10 * H(i + 2) + VH * 4) % VH; c.globalAlpha = .25 + .4 * H(i + 1); c.fillRect(x, y, 2, 2); }
  c.globalAlpha = 1;
}
function riverbed(c, t, bedY, scroll = 0) {
  // papyrus on the bed: a river far older than anyone's memory
  for (let layerI = 0; layerI < 2; layerI++) {
    const par = layerI ? 1 : .55, col = layerI ? '#16323A' : '#1E4148';
    for (let i = 0; i < 14; i++) {
      const bx = ((i * 137 + layerI * 61 + 40 - scroll * par) % 1500 + 1500) % 1500 - 110, hgt = (120 + 110 * H(i + layerI * 20)) * (layerI ? 1 : .7), sw = Math.sin(t * .9 + i) * 12;
      c.strokeStyle = col; c.lineWidth = 4; c.beginPath(); c.moveTo(bx, bedY + 10); c.quadraticCurveTo(bx + sw * .3, bedY - hgt * .5, bx + sw, bedY - hgt); c.stroke();
      c.fillStyle = col; c.beginPath(); c.moveTo(bx + sw, bedY - hgt);
      for (let k = 0; k <= 8; k++) { const a = -Math.PI * .85 + k / 8 * Math.PI * .7; c.lineTo(bx + sw + Math.cos(a) * 34, bedY - hgt + Math.sin(a) * 30); }
      c.closePath(); c.fill();
    }
  }
  c.fillStyle = vgrad(c, bedY - 30, VH, ['#8E7A55', '#5E4F38']); c.beginPath(); c.moveTo(0, VH);
  for (let x = 0; x <= VW; x += 40) c.lineTo(x, bedY + Math.sin((x + scroll) * .01) * 10);
  c.lineTo(VW, VH); c.closePath(); c.fill();
  c.fillStyle = 'rgba(40,30,20,.35)'; for (let i = 0; i < 18; i++) { const x = ((i * 211 - scroll) % 1400 + 1400) % 1400 - 60; c.beginPath(); c.ellipse(x, bedY + 26 + H(i) * 40, 10 + 14 * H(i + 2), 5 + 4 * H(i + 3), 0, 0, TAU); c.fill(); }
}
function bubbles(c, t, x, y, n = 12, seed = 1) {
  c.save(); c.strokeStyle = 'rgba(220,245,250,.7)'; c.lineWidth = 1.5;
  for (let i = 0; i < n; i++) { const p = (t * .5 + H(i + seed)) % 1, bx = x + (H(i * 3 + seed) - .5) * 70 + Math.sin(t * 3 + i) * 8, by = y - p * 320; c.globalAlpha = .8 * (1 - p); c.beginPath(); c.arc(bx, by, 2 + 5 * H(i + seed * 2), 0, TAU); c.stroke(); }
  c.restore();
}
function soul(c, x, y, u, o, t) { glow(c, x, y - 5 * u, 15 * u, 'rgba(255,200,150,.35)', .8 + .2 * Math.sin(t * 2)); critter(c, x, y, u, { noShadow: true, ...o }, t); }
function rings(c, t, x, y, r, a) {
  if (a <= .001 || r <= 0) return;
  glow(c, x, y, r * 2.2, 'rgba(255,240,200,.5)', a);
  c.save(); c.globalAlpha *= a; c.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 4; i++) {
    const rr = r * (.45 + i * .22) * (1 + .05 * pulse(t)), rot = t * (i % 2 ? -.5 : .4) + i;
    c.strokeStyle = `rgba(255,${230 - i * 15},${190 - i * 25},${.8 - i * .12})`; c.lineWidth = 6 - i; c.setLineDash([rr * .35, rr * .12]); c.lineDashOffset = rot * rr;
    c.beginPath(); c.arc(x, y, rr, 0, TAU); c.stroke();
  }
  c.setLineDash([]); c.restore();
}
function bolt(c, seed, x0, a) {
  if (a <= .01) return;
  c.save(); c.globalAlpha = a; c.strokeStyle = '#F4FAFF'; c.lineWidth = 6; c.shadowColor = '#BFE6FF'; c.shadowBlur = 40; c.beginPath();
  let x = x0, y = -10; c.moveTo(x, y);
  for (let i = 0; i < 12; i++) { x += (H(seed * 13 + i) - .5) * 110; y += 30 + 20 * H(seed + i * 5); c.lineTo(x, y); }
  c.stroke(); c.restore();
}

// ---------------------------------------------------------------- inside the light
function brightRoom(c, t, k = 1) {
  c.fillStyle = '#FFF6E6'; c.fillRect(0, 0, VW, VH);
  const g = c.createRadialGradient(640, 300, 80, 640, 360, 900); g.addColorStop(0, '#FFFDF6'); g.addColorStop(1, '#EFCFA0'); c.fillStyle = g; c.fillRect(0, 0, VW, VH);
  c.fillStyle = 'rgba(214,170,110,.25)'; c.fillRect(0, 575, VW, VH);
  c.fillStyle = 'rgba(255,255,255,.7)';
  for (let i = 0; i < 40; i++) { const x = (H(i) * VW + Math.sin(t * .3 + i) * 30), y = (H(i + 4) * VH - t * 12 * (.4 + H(i + 2)) + VH * 6) % VH; c.globalAlpha = .3 + .5 * H(i + 8); c.beginPath(); c.arc(x, y, 1.5 + 2.5 * H(i + 3), 0, TAU); c.fill(); }
  c.globalAlpha = 1;
}
function scissors(c, x, y, s, open, rot) {
  c.save(); c.translate(x, y); c.rotate(rot); c.lineWidth = 3; c.strokeStyle = INK;
  for (const sd of [-1, 1]) {
    c.save(); c.rotate(sd * open * .45);
    c.beginPath(); c.moveTo(0, 0); c.quadraticCurveTo(60 * s, sd * -10 * s, 110 * s, sd * -3 * s); c.quadraticCurveTo(60 * s, sd * 8 * s, 0, sd * 6 * s); c.closePath(); c.fillStyle = '#DDE3EA'; c.fill(); c.stroke();
    c.beginPath(); c.ellipse(-34 * s, sd * 14 * s, 22 * s, 13 * s, sd * .3, 0, TAU); c.lineWidth = 8 * s; c.strokeStyle = '#E8836B'; c.stroke(); c.lineWidth = 3; c.strokeStyle = INK;
    c.restore();
  }
  c.beginPath(); c.arc(0, 0, 5 * s, 0, TAU); c.fillStyle = INK; c.fill(); c.restore();
}

// ---------------------------------------------------------------- the nursery (now)
function nursery(c, t, lampK = 1) {
  c.fillStyle = vgrad(c, 0, VH, ['#1B2443', '#252F52', '#2C2A48']); c.fillRect(0, 0, VW, VH);
  c.fillStyle = '#2B2440'; c.fillRect(0, 600, VW, VH - 600);
  c.fillStyle = 'rgba(255,255,255,.04)'; for (let x = 30; x < VW; x += 90) c.fillRect(x, 0, 30, 600);       // wallpaper stripes
  // window + moon
  c.save(); c.beginPath(); c.roundRect(860, 110, 280, 300, 12); c.fillStyle = vgrad(c, 110, 410, ['#0E1430', '#26355E']); c.fill(); c.clip();
  glow(c, 1030, 210, 120, 'rgba(240,235,210,.45)'); c.beginPath(); c.arc(1030, 210, 38, 0, TAU); c.fillStyle = '#F6F0D8'; c.fill();
  c.fillStyle = '#fff'; for (let i = 0; i < 20; i++) { c.globalAlpha = .4 + .6 * (.5 + .5 * Math.sin(t * 1.3 + i)); c.fillRect(870 + H(i) * 260, 120 + H(i + 3) * 280, 1.6, 1.6); } c.globalAlpha = 1;
  c.restore();
  c.lineWidth = 10; c.strokeStyle = '#3A3256'; c.beginPath(); c.roundRect(860, 110, 280, 300, 12); c.moveTo(1000, 110); c.lineTo(1000, 410); c.moveTo(860, 260); c.lineTo(1140, 260); c.stroke();
  c.fillStyle = '#5A4A7E'; c.beginPath(); c.moveTo(830, 90); c.quadraticCurveTo(880, 250, 840, 440); c.lineTo(820, 440); c.lineTo(820, 90); c.fill();
  c.beginPath(); c.moveTo(1170, 90); c.quadraticCurveTo(1120, 250, 1160, 440); c.lineTo(1180, 440); c.lineTo(1180, 90); c.fill();
  // the lamp
  const fl = 1 + .06 * Math.sin(t * 9) * Math.sin(t * 3.3);
  glow(c, 190, 380, 420 * fl, 'rgba(255,190,110,.45)', lampK);
  c.fillStyle = '#4A3A30'; c.fillRect(184, 420, 12, 180); c.beginPath(); c.ellipse(190, 600, 50, 10, 0, 0, TAU); c.fill();
  c.beginPath(); c.moveTo(140, 420); c.lineTo(240, 420); c.lineTo(214, 340); c.lineTo(166, 340); c.closePath(); c.fillStyle = '#F2C27A'; c.fill();
}
function cradle(c, x, y, rot, front) {
  c.save(); c.translate(x, y); c.rotate(rot); c.lineWidth = 4; c.strokeStyle = INK;
  if (!front) { c.beginPath(); c.ellipse(0, -95, 170, 24, 0, 0, TAU); c.fillStyle = '#6E4A30'; c.fill(); c.stroke(); }
  else {
    c.beginPath(); c.moveTo(-170, -95); c.quadraticCurveTo(-160, 10, 0, 14); c.quadraticCurveTo(160, 10, 170, -95); c.closePath(); c.fillStyle = '#B07D55'; c.fill(); c.stroke();
    c.strokeStyle = 'rgba(60,35,20,.4)'; for (let i = -4; i <= 4; i++) { c.beginPath(); c.moveTo(i * 34, -92); c.lineTo(i * 30, 4); c.stroke(); }
    c.strokeStyle = INK; c.beginPath(); c.moveTo(-200, 40); c.quadraticCurveTo(0, 90, 200, 40); c.lineWidth = 8; c.stroke();
  }
  c.restore();
}
function moonWindow(c, t, glowK) {
  c.fillStyle = vgrad(c, 0, VH, ['#0E1430', '#2A2D55', '#5B4466']); c.fillRect(0, 0, VW, VH);
  const R = 150 + 30 * glowK;
  glow(c, 640, 300, R * 3.4, 'rgba(255,200,120,.45)', .6 + .4 * glowK);
  c.beginPath(); c.arc(640, 300, R, 0, TAU); c.fillStyle = '#F7D58C'; c.fill();
  c.fillStyle = 'rgba(200,150,80,.25)'; for (const [dx, dy, r] of [[-40, -30, 26], [50, 20, 18], [-10, 60, 14], [30, -60, 10]]) { c.beginPath(); c.arc(640 + dx, 300 + dy, r, 0, TAU); c.fill(); }
}
function leaf(c, x, y, s, rot, col) { c.save(); c.translate(x, y); c.rotate(rot); c.beginPath(); c.ellipse(0, 0, 11 * s, 5 * s, 0, 0, TAU); c.fillStyle = col; c.fill(); c.strokeStyle = 'rgba(80,40,10,.5)'; c.lineWidth = 1; c.beginPath(); c.moveTo(-10 * s, 0); c.lineTo(10 * s, 0); c.stroke(); c.restore(); }
function fallingLeaves(c, t, n, seed, a = 1, sp = 60) {
  const cols = ['#E39B3A', '#C9622F', '#E8C04E', '#B5432F'];
  for (let i = 0; i < n; i++) { const p = (t * sp * (.6 + .6 * H(i + seed)) / VH + H(i * 3 + seed)) % 1, x = H(i * 7 + seed) * (VW + 200) - 100 + Math.sin(t * 1.4 + i) * 40 - p * 120, y = p * (VH + 80) - 40; c.globalAlpha = a; leaf(c, x, y, .9 + .6 * H(i + 2), t * 2 + i, cols[i % 4]); }
  c.globalAlpha = 1;
}

// ---------------------------------------------------------------- the past (warm)
function jujubeTree(c, x, y, s, t, shake = 0) {
  c.save(); c.translate(x, y); c.lineCap = 'round';
  c.strokeStyle = '#5B3A22'; c.lineWidth = 34 * s; c.beginPath(); c.moveTo(0, 0); c.quadraticCurveTo(-20 * s, -120 * s, 10 * s, -220 * s); c.stroke();
  c.lineWidth = 16 * s; for (const [bx, by, ex, ey] of [[0, -150, -130, -260], [5, -180, 140, -280], [10, -210, -30, -330]]) { c.beginPath(); c.moveTo(bx * s, by * s); c.quadraticCurveTo((bx + ex) / 2 * s, (by + ey) / 2 * s - 30 * s, ex * s, ey * s); c.stroke(); }
  const sx = Math.sin(t * 30) * 6 * shake * s;
  const blobs = [[-150, -280, 110], [140, -300, 120], [-20, -360, 130], [-90, -210, 90], [90, -220, 95], [10, -260, 110]];
  for (const [i, [bx, by, r]] of blobs.entries()) { c.beginPath(); c.arc(bx * s + sx, by * s, r * s, 0, TAU); c.fillStyle = i % 2 ? '#8E9A3A' : '#A7A845'; c.fill(); }
  for (const [i, [bx, by, r]] of blobs.entries()) { c.beginPath(); c.arc(bx * s - 20 * s + sx, by * s - 25 * s, r * .55 * s, 0, TAU); c.fillStyle = 'rgba(232,200,90,.45)'; c.fill(); }
  for (let i = 0; i < 46; i++) { const b = blobs[i % blobs.length], a = H(i) * TAU, rr = Math.sqrt(H(i + 50)) * b[2] * .85; jujube(c, (b[0] + Math.cos(a) * rr) * s + sx, (b[1] + Math.sin(a) * rr) * s, 8 * s, H(i + 3) - .5); }
  c.restore();
}
function sunsetSky(c, t, warm = 1) {
  c.fillStyle = vgrad(c, 0, VH, warm > .5 ? ['#F3C77B', '#EFA35C', '#D7774A'] : ['#F6DE9C', '#F1C376', '#E3A55E']); c.fillRect(0, 0, VW, VH);
}
function hills(c, t, yBase, col, amp, freq, off) {
  c.fillStyle = col; c.beginPath(); c.moveTo(0, VH);
  for (let x = 0; x <= VW; x += 20) c.lineTo(x, yBase + Math.sin(x * freq + off) * amp + Math.sin(x * freq * 2.3 + off * 1.7) * amp * .35);
  c.lineTo(VW, VH); c.closePath(); c.fill();
}
function roofs(c, x0, y0, s, col) {
  for (let i = 0; i < 6; i++) { const x = x0 + i * 46 * s, w = (36 + 12 * H(i)) * s, h = (22 + 10 * H(i + 1)) * s; c.fillStyle = col; c.fillRect(x, y0 - h, w, h); c.beginPath(); c.moveTo(x - 6 * s, y0 - h); c.lineTo(x + w / 2, y0 - h - 14 * s); c.lineTo(x + w + 6 * s, y0 - h); c.fill(); }
}
// one stretch of the old lane, in world x (scrolls)
function lane(c, t, scroll) {
  c.fillStyle = vgrad(c, 0, 300, ['#F0B977', '#E7A867']); c.fillRect(0, 0, VW, 300);
  // far roofs
  for (let i = -1; i < 9; i++) { const x = i * 220 - (scroll * .4) % 220; c.fillStyle = '#B98A62'; c.beginPath(); c.moveTo(x, 210); c.lineTo(x + 40, 160); c.lineTo(x + 180, 160); c.lineTo(x + 220, 210); c.fill(); }
  // walls with tiled eaves and doors
  for (let i = -1; i < 6; i++) {
    const wx = i * 360 - scroll % 360;
    c.fillStyle = '#EFE3CC'; c.fillRect(wx, 210, 360, 400);
    c.fillStyle = 'rgba(120,90,60,.12)'; c.fillRect(wx, 520, 360, 90);
    c.fillStyle = '#4E4B55'; c.beginPath(); c.moveTo(wx - 10, 230); c.lineTo(wx + 370, 230); c.lineTo(wx + 360, 196); c.lineTo(wx, 196); c.fill();
    c.strokeStyle = '#3A3842'; c.lineWidth = 2; for (let k = 0; k < 18; k++) { c.beginPath(); c.moveTo(wx + k * 20, 198); c.lineTo(wx + k * 20 + 2, 230); c.stroke(); }
    // a wooden door
    c.fillStyle = '#7A4A2C'; c.fillRect(wx + 130, 360, 100, 250); c.strokeStyle = '#4A2A18'; c.lineWidth = 3; c.strokeRect(wx + 130, 360, 100, 250); c.beginPath(); c.moveTo(wx + 180, 360); c.lineTo(wx + 180, 610); c.stroke();
    c.fillStyle = '#E2B65A'; c.beginPath(); c.arc(wx + 170, 480, 5, 0, TAU); c.arc(wx + 190, 480, 5, 0, TAU); c.fill();
    c.fillStyle = '#C8322B'; c.fillRect(wx + 120, 335, 120, 20);                   // red lintel
    // red lantern swinging on the beat
    const lx = wx + 300, sw = Math.sin(beatPos(t) * Math.PI) * .12;
    c.save(); c.translate(lx, 232); c.rotate(sw); c.strokeStyle = INK; c.lineWidth = 2; c.beginPath(); c.moveTo(0, 0); c.lineTo(0, 40); c.stroke();
    glow(c, 0, 75, 70, 'rgba(255,120,60,.5)', .7 + .3 * pulse(t));
    c.beginPath(); c.ellipse(0, 75, 26, 34, 0, 0, TAU); c.fillStyle = '#D8352A'; c.fill(); c.stroke(); c.fillStyle = '#E2B65A'; c.fillRect(-12, 38, 24, 6); c.fillRect(-12, 106, 24, 6);
    c.strokeStyle = '#E2B65A'; c.beginPath(); c.moveTo(0, 112); c.lineTo(0, 132); c.stroke(); c.restore();
  }
  // stone slab road
  c.fillStyle = '#A99B86'; c.fillRect(0, 600, VW, VH - 600);
  c.strokeStyle = 'rgba(70,60,50,.35)'; c.lineWidth = 2;
  for (let r = 0; r < 4; r++) { const y = 600 + r * 32; c.beginPath(); c.moveTo(0, y); c.lineTo(VW, y); c.stroke(); for (let i = -1; i < 14; i++) { const x = i * 110 + (r % 2) * 55 - scroll % 110; c.beginPath(); c.moveTo(x, y); c.lineTo(x, y + 32); c.stroke(); } }
}

// ---------------------------------------------------------------- shots
const ME = (extra = {}) => ({ look: LOOK_ME, seed: 7, aL: .25, aR: .25, ...extra });
const YOU = (extra = {}) => ({ look: LOOK_YOU, bow: true, seed: 3, aL: .25, aR: .25, ...extra });

const CS = .95;                                   // suitcase scale: bigger than the soul dragging it
const SHOT_FN = {
  river(c, t) {
    const d = eio(seg(t, 0, 4.6));
    water(c, t, d);
    // the surface, falling away overhead
    const sy = lerp(70, -260, d);
    c.save(); c.globalAlpha = 1 - d; c.strokeStyle = 'rgba(220,250,255,.7)'; c.lineWidth = 3; c.beginPath();
    for (let x = 0; x <= VW; x += 16) c.lineTo(x, sy + Math.sin(x * .02 + t * 2) * 6); c.stroke(); glow(c, 640, sy - 60, 600, 'rgba(220,250,255,.35)'); c.restore();
    const bedY = lerp(1000, 610, d);
    riverbed(c, t, bedY);
    // the suitcase sinks first and drags the soul down with it; it lands on the kick at 4.27 s
    const land = 4.27, fall = eio(seg(t, .2, land)), csY = t < land ? lerp(330, bedY - 45 * CS, fall) : bedY - 45 * CS, csX = 520 + Math.sin(t * .8) * 10 * (1 - fall);
    const rot = t < land ? Math.sin(t * 1.3) * .08 : 0;
    const mx = t < land ? csX + 70 : lerp(csX + 70, 720, eio(seg(t, land, 5.3))), my = t < land ? csY - 200 + Math.sin(t * 1.7) * 8 : lerp(csY - 200, bedY + 4, eio(seg(t, land, 5.1)));
    const u = 9.5, hand = [mx - 4.9 * u - 1.6 * u, my - 4.5 * u + 1.4 * u];
    rope(c, hand[0], hand[1], csX, csY - 105 * CS, t < land ? 10 : 40);
    suitcase(c, csX, csY, CS, rot, t);
    if (t > land) { const p = seg(t, land, land + 1.2); c.save(); c.globalAlpha = (1 - p) * .7; c.fillStyle = '#B9A47A'; for (let i = 0; i < 9; i++) { c.beginPath(); c.arc(csX + (i - 4) * 22 * (1 + p), bedY + 4 - p * 30 * H(i), 14 + 18 * p, 0, TAU); c.fill(); } c.restore(); }
    bubbles(c, t, mx, my - 60, 14, 2);
    soul(c, mx, my, u, ME({ eyes: t > land && t < land + .4 ? 'wide' : 'normal', lookY: t < land ? 1 : 0, lookX: t > 5 ? -1 : .3, aL: t < land ? -.5 : .4, aR: .9 + .3 * Math.sin(t * 3), dy: t < land ? Math.sin(t * 2) * .2 : 0, sq: t > land + .8 && t < land + 1.1 ? .08 : 0 }), t);
    // title
    const k = seg(t, .5, 1.6) * (1 - seg(t, 4.2, 5.2));
    if (k > 0) { c.save(); c.globalAlpha = k; c.textAlign = 'center'; c.textBaseline = 'middle'; c.shadowColor = 'rgba(0,20,30,.7)'; c.shadowBlur = 24;
      c.font = `700 96px ${SERIF}`; c.fillStyle = '#F4F1EA'; c.fillText('我 记 得', 640, 200);
      c.font = `500 24px ${SERIF}`; c.fillStyle = '#CFE6EC'; c.fillText('Claude Code 版 · 背景音乐 赵雷《我记得》', 640, 275); c.restore(); }
  },
  storm(c, t) {
    water(c, t, 1);
    // flashes on each kick of the phrase from 6.0 s
    let flash = 0, bi = 0; for (const k of kicksIn(5.95, 7.7)) { bi++; if (t >= k) flash = Math.max(flash, Math.exp(-(t - k) * 7)); }
    if (flash > 0) { veil(c, '#DDF2FF', flash * .45); bolt(c, Math.floor(lastKick(t) * 100), 300 + H(Math.floor(lastKick(t) * 10)) * 700, flash); }
    const walkEnd = 9.6, sc = 170 * (Math.min(t, walkEnd) - 6) - 60 * eio(seg(t, 9.0, 9.9)) + 260 * eio(seg(t, 12.9, 14.6));
    riverbed(c, t, 610, sc);
    // rings of light ahead
    const rr = 150 * eout(seg(t, 7.68, 9.6)) * (1 + 7 * Math.pow(seg(t, 13.9, 14.86), 2));
    rings(c, t, 1020 - 140 * eio(seg(t, 12.9, 14.6)), 380, rr, seg(t, 7.68, 8.6));
    // the soul drags the suitcase along the bed
    const walking = t < 9.4 || (t > 12.9 && t < 14.6), u = 9.5, mx = 560 + 120 * eio(seg(t, 12.9, 14.6)), my = 614;
    const csX = mx - 270 + 20 * Math.sin(t * 3) * (walking ? 1 : 0), csY = 610 - 45 * CS + (walking ? Math.abs(Math.sin(t * 6)) * -4 : 0);
    rope(c, mx - 4.9 * u - 1.6 * u, my - 4.5 * u + 1.4 * u, csX + 20, csY - 105 * CS, 18);
    suitcase(c, csX, csY, CS, walking ? -.06 : 0, t);
    bubbles(c, t, mx, my - 70, 8, 5);
    const look = t > 11.0 && t < 12.2 ? -1 : 1, wide = flash > .3;
    soul(c, mx, my, u, ME({ walk: walking ? beatPos(t) / 2 : null, eyes: wide ? 'wide' : 'normal', lookX: look, aL: .5, aR: wide ? 2.2 : .3, sq: wide ? .05 : 0, rot: walking ? .05 : 0 }), t);
    if (t > 10 && t < 12.7) { const k = seg(t, 10, 10.4) * (1 - seg(t, 12.3, 12.7)); c.save(); c.globalAlpha = k; c.font = `700 52px ${F_EN}`; c.fillStyle = '#FFE9C8'; c.textAlign = 'center'; c.fillText('?', mx + 30, my - 110 - 6 * Math.sin(t * 4)); c.restore(); }
    veil(c, '#FFF8EA', Math.pow(seg(t, 14.1, 14.86), 1.5));
  },
  light(c, t) {
    brightRoom(c, t);
    const u0 = 12, shrink = eio(seg(t, 21.6, 23.3)), u = lerp(u0, 8, shrink), mx = 470, my = 590;
    // the helpers waiting in the light
    const helpers = [[860, 0], [1000, 1], [1140, 2]];
    const towelGo = eio(seg(t, 21.0, 21.7)) * (1 - eio(seg(t, 23.0, 23.5)));
    for (const [hx, i] of helpers) {
      const a = seg(t, 14.9 + i * .35, 15.9 + i * .35), x = i === 1 ? lerp(hx, mx + 140, towelGo) : hx, bob = Math.max(0, Math.sin(beatPos(t) * Math.PI)) * .25;
      critter(c, x, my, 11, { look: LOOK_HELPER, hat: 'surgeon', mask: true, alpha: a, dy: -bob, seed: i * 2, eyes: 'happy', aL: i === 1 && towelGo > .5 ? 2.0 : .3, aR: i === 0 && t > 17.9 && t < 19.4 ? 1.4 : .3, flip: i === 1 && towelGo > 0 }, t);
    }
    // the rope, cut by the scissors on the first kick after 18.35 s
    const snip = kicksIn(18.35, 19.2)[0] ?? 18.45, cut = t >= snip;
    const csGone = eio(seg(t, 19.68, 21.3)), csX = lerp(180, 1320, csGone), csY = lerp(590 - 45 * CS, 120, csGone) - Math.sin(csGone * Math.PI) * 60, csS = lerp(CS, .35, csGone);
    const hand = [mx - 4.9 * u - 1.6 * u, my - 4.5 * u + 1.4 * u], hand0 = [mx - 6.5 * u0, my - 3.1 * u0], cutX = (hand0[0] + 200) / 2, cutY = 545;
    if (!cut) rope(c, hand[0], hand[1], csX + 20, csY - 105 * csS, 30);
    else {
      const p = eout(seg(t, snip, snip + .5));
      rope(c, csX + 20, csY - 105 * csS, csGone > 0 ? csX + 20 : cutX - 8, csGone > 0 ? csY - 105 * csS + 70 * csS : lerp(cutY, 580, p), 6);
      c.save(); c.globalAlpha = 1 - seg(t, 20.6, 21.2); rope(c, hand[0], hand[1], cutX + 8, lerp(cutY, 588, p), 6); c.restore();
    }
    if (csGone < 1) { glow(c, csX, csY - 40, 180 * csS, 'rgba(255,230,170,.6)', csGone); suitcase(c, csX, csY, csS, Math.sin(t * 2) * .1 * csGone, t); }
    if (t > 17.9 && t < 19.6) {
      const into = eout(seg(t, 17.92, snip - .05)), away = eio(seg(t, snip + .25, 19.6)), rot = 1.35, sS = 1.3;
      const sxp = cutX - Math.cos(rot) * 100 * sS + away * 500, syp = cutY - Math.sin(rot) * 100 * sS - (1 - into) * 320 - away * 300;
      const open = t < snip ? .6 + .3 * Math.sin((t - 17.92) * 9) : Math.max(0, .05 * (1 - seg(t, snip, snip + .2)));
      scissors(c, sxp, syp, sS, open, rot);
      if (t > snip && t < snip + .3) { const q = seg(t, snip, snip + .3); c.save(); c.globalAlpha = 1 - q; c.strokeStyle = '#E8836B'; c.lineWidth = 3; for (let i = 0; i < 8; i++) { const a = i / 8 * TAU, r0 = 14, r1 = 14 + 50 * q; c.beginPath(); c.moveTo(cutX + Math.cos(a) * r0, cutY + Math.sin(a) * r0); c.lineTo(cutX + Math.cos(a) * r1, cutY + Math.sin(a) * r1); c.stroke(); } c.restore(); }
    }
    const watching = csGone > 0 && csGone < 1, rubbing = t > 21.6 && t < 23.2;
    critter(c, mx, my, u, ME({ eyes: rubbing ? 'closed' : watching ? 'sad' : t < 17.9 ? 'wide' : 'normal', lookX: watching ? 1 : t > 17.9 && t < 19.68 ? -1 : .6, lookY: watching ? -1 : 0, aR: watching ? 2.0 + .2 * Math.sin(t * 8) : .3, aL: .4, blush: rubbing ? .8 : 0, smile: rubbing ? .6 : 0 }), t);
    if (rubbing || (t > 21.3 && t < 23.4)) { const k = seg(t, 21.3, 21.6) * (1 - seg(t, 23.1, 23.4)), wob = Math.sin(t * 16) * 2.2 * u; c.save(); c.globalAlpha = k; c.translate(mx + wob, my - 8.6 * u); c.rotate(Math.sin(t * 16) * .15); c.beginPath(); c.roundRect(-5.5 * u, -1.8 * u, 11 * u, 3 * u, 1.2 * u); c.fillStyle = '#FFFFFF'; c.fill(); c.strokeStyle = INK; c.lineWidth = 2.5; c.stroke(); c.strokeStyle = '#9CC9E6'; c.beginPath(); c.moveTo(-5 * u, .2 * u); c.lineTo(5 * u, .2 * u); c.stroke(); c.restore(); }
    veil(c, '#FFF8EA', 1 - seg(t, 14.86, 15.7));
  },
  closing(c, t) {
    const dark = eio(seg(t, 24.9, 27.4));
    brightRoom(c, t); veil(c, '#0B0E1C', dark * .96);
    // the way back: a ring that closes
    const r = 170 * (1 - eio(seg(t, 23.9, 26.1)));
    rings(c, t, 300, 390, r, 1);
    if (r > 1) { c.save(); c.globalAlpha = r / 170; c.fillStyle = '#FFF2D0'; c.beginPath(); c.arc(300, 390, r * .45, 0, TAU); c.fill(); c.restore(); }
    // tiny pictures of the old life swirl into it and vanish
    for (let i = 0; i < 6; i++) {
      const p = seg(t, 23.6 + i * .25, 25.6 + i * .25); if (p <= 0 || p >= 1) continue;
      const a = i * 1.1 + p * 5, rad = lerp(260, 0, eio(p)), x = 300 + Math.cos(a) * rad, y = 390 + Math.sin(a) * rad * .7;
      c.save(); c.globalAlpha = 1 - p; if (i % 3 === 0) jujube(c, x, y, 12); else if (i % 3 === 1) coin(c, x, y, 13, p * 3); else leaf(c, x, y, 1.4, a, '#E39B3A'); c.restore();
    }
    const u = 8, mx = lerp(760, 690, eio(seg(t, 24.2, 25.2)));
    glow(c, mx, 560, 160, 'rgba(255,190,140,.3)', dark);
    critter(c, mx, 600, u, ME({ eyes: t > 25.6 ? 'sad' : 'normal', lookX: -1, aL: t > 24.2 && t < 26.2 ? 1.8 : .3, walk: t > 24.2 && t < 25.2 ? (t - 24.2) * 2 : null }), t);
  },
  voice(c, t) {
    const z = lerp(1, 1.12, eio(seg(t, 28.16, 41.98)));
    withCam(c, 640, 380, z, () => {
      nursery(c, t);
      const rock = t > 37.12 ? .07 * Math.sin((t - 37.12) * 2.4) : 0;
      cradle(c, 640, 600, rock, false);
      // the newborn: eyes shut, then open towards the voice
      const eyes = t < 30 ? 'closed' : t > 34.0 && t < 36.2 ? 'wide' : 'normal';
      c.save(); c.translate(640, 600); c.rotate(rock); critter(c, 0, -85, 10, ME({ swaddle: true, eyes, lookX: t < 33.6 ? -1 : -.6, lookY: t > 33.6 ? -.6 : 0, blush: seg(t, 34.2, 35.2), smile: t > 37.5 ? .5 : 0, noShadow: true }), t); c.restore();
      cradle(c, 640, 600, rock, true);
      // memory flicker when it recognises her
      if (t > 34.1 && t < 35.9) {
        const k = seg(t, 34.1, 34.4) * (1 - seg(t, 35.4, 35.9)) * (.75 + .25 * Math.sin(t * 40));
        c.save(); c.globalAlpha = k; c.beginPath(); c.arc(820, 330, 86, 0, TAU); c.fillStyle = '#E9B877'; c.fill(); c.clip();
        jujubeTree(c, 820, 430, .32, t); critter(c, 770, 420, 3.6, ME({ hat: 'straw', noShadow: true }), t); critter(c, 860, 420, 2.4, YOU({ noShadow: true }), t);
        c.restore(); c.save(); c.globalAlpha = k * .8; c.strokeStyle = '#FFE3B0'; c.lineWidth = 4; c.beginPath(); c.arc(820, 330, 86, 0, TAU); c.stroke(); c.restore();
        for (let i = 0; i < 3; i++) { c.save(); c.globalAlpha = k; c.fillStyle = '#FFE3B0'; c.beginPath(); c.arc(720 + i * 28, 420 - i * 30, 6 + i * 3, 0, TAU); c.fill(); c.restore(); }
      }
      // her humming: one note per beat, drifting in from the dark
      const nb0 = Math.ceil(beatPos(28.3)), nb1 = Math.floor(beatPos(t));
      for (let b = Math.max(nb0, nb1 - 10); b <= nb1; b++) {
        if (b % 2) continue;
        const t0 = BEATMAP.phase + b * BEATMAP.beat, age = t - t0, from = t0 > 34 ? [430, 360] : [-20, 360];
        if (age < 0 || age > 3.4) continue;
        const p = age / 3.4; note(c, lerp(from[0], 600, p) + 20 * Math.sin(b), from[1] - 60 * Math.sin(p * 3 + b) - p * 60, .9, Math.min(1, age * 3) * (1 - p));
      }
      // she leans in
      const enter = eout(seg(t, 33.0, 34.3));
      if (enter > 0) critter(c, lerp(-200, 360, enter), 640, 17, YOU({ eyes: 'happy', smile: t > 34 ? 1 : .5, rot: .1, aR: t > 37.1 ? 1.1 + .15 * Math.sin((t - 37.12) * 2.4) : .6, blush: .6, mouth: t > 37.1 ? .25 + .15 * Math.sin(t * 5) : 0 }), t);
    });
  },
  babble(c, t) {
    withCam(c, 640, 360, 1.04, () => {
      nursery(c, t);
      veil(c, '#1B2443', .25);
      critter(c, 420, 700, 26, YOU({ eyes: t > 47.6 && t < 49.1 ? 'normal' : 'happy', brows: t > 47.6 && t < 49.1 ? 'up' : null, smile: 1, mouth: t < 47 ? Math.max(0, Math.sin(beatPos(t) * Math.PI / 2)) * .5 : 0, rot: t > 49.1 ? .08 * eio(seg(t, 49.1, 49.8)) : 0, aR: 1.5, lookX: 1, blush: .7 }), t);
      const nuzzle = eio(seg(t, 49.1, 49.8)), bx = 655 - 30 * nuzzle, by = 555 + Math.sin(t * 2) * 4;
      const talk = t > 42.4 && t < 46.9, mouth = talk ? Math.max(0, 1 - beatPhase(t) * 2) : 0;
      critter(c, bx, by, 14, ME({ swaddle: true, noShadow: true, eyes: t > 47.6 && t < 49.1 ? 'sad' : nuzzle > .5 ? 'happy' : 'normal', lookX: -.6, mouth, pout: t > 47.6 && t < 49.1, blush: nuzzle }), t);
      // what it wants to say: pictures of the old life, a new one every two beats
      const pop = 47.6, cloudK = seg(t, 42.2, 42.8) * (t < pop ? 1 : 0);
      if (cloudK > 0) {
        c.save(); c.globalAlpha = cloudK; c.fillStyle = '#FFF8EC'; c.strokeStyle = INK; c.lineWidth = 3;
        for (const [x, y, r] of [[1000, 230, 95], [920, 250, 70], [1080, 250, 70], [960, 180, 70], [1050, 180, 65]]) { c.beginPath(); c.arc(x, y, r, 0, TAU); c.fill(); }
        for (const [x, y, r] of [[860, 365, 16], [800, 410, 10]]) { c.beginPath(); c.arc(x, y, r, 0, TAU); c.fill(); c.stroke(); }
        const idx = ((Math.floor(beatPos(t) / 2) % 5) + 5) % 5, pk = eout(seg(beatPos(t) % 2, 0, .4));
        c.save(); c.translate(1000, 230); c.scale(pk, pk);
        if (idx === 0) jujubeTree(c, 0, 80, .35, t);
        else if (idx === 1) jujube(c, 0, 0, 40, .2);
        else if (idx === 2) coin(c, 0, 0, 44, 0);
        else if (idx === 3) { critter(c, -30, 50, 5, ME({ hat: 'cap', noShadow: true }), t); critter(c, 45, 50, 3, YOU({ noShadow: true }), t); }
        else suitcase(c, 0, 30, .45, 0, t);
        c.restore(); c.restore();
      }
      if (t >= pop && t < pop + .6) { const p = seg(t, pop, pop + .6); c.save(); c.globalAlpha = 1 - p; c.fillStyle = '#FFF8EC'; for (let i = 0; i < 14; i++) { const a = i / 14 * TAU; c.beginPath(); c.arc(1000 + Math.cos(a) * 160 * eout(p), 230 + Math.sin(a) * 110 * eout(p), 12 * (1 - p) + 3, 0, TAU); c.fill(); } c.restore(); }
      // what comes out: babble
      if (talk || (t > 42.4 && t < 47.6)) {
        for (let b = Math.ceil(beatPos(42.4)); b <= Math.floor(beatPos(Math.min(t, 46.9))); b++) {
          const t0 = BEATMAP.phase + b * BEATMAP.beat, age = t - t0; if (age < 0 || age > 1.3) continue;
          const p = age / 1.3; c.save(); c.globalAlpha = Math.min(1, age * 6) * (1 - p); c.font = `700 ${34 + 10 * eout(Math.min(1, age * 4))}px ${SERIF}`; c.textAlign = 'center'; c.fillStyle = '#FFE9C8';
          c.fillText(b % 2 ? '呀' : '咿', bx - 40 + 50 * H(b) - p * 50, by - 170 - p * 90 - (b % 3) * 14); c.restore();
        }
      }
      if (nuzzle > 0) for (let i = 0; i < 5; i++) { const p = ((t - 49.3) * .5 + i / 5) % 1; if (t > 49.3) heart(c, 600 + Math.sin(i * 2 + t) * 50, 450 - p * 200, 1.2, (1 - p) * nuzzle); }
    });
  },
  window(c, t) {
    const z = 1 + 2.4 * Math.pow(seg(t, 53.6, 55.66), 2.2), build = seg(t, 51.02, 55.66);
    withCam(c, 640, lerp(380, 300, seg(t, 53.6, 55.66)), z, () => {
      moonWindow(c, t, build);
      fallingLeaves(c, t, Math.floor(6 + 30 * build), 7, .9, 40 + 80 * build);
      // window frame
      c.strokeStyle = '#1A1630'; c.lineWidth = 26; c.strokeRect(250, 40, 780, 640); c.lineWidth = 14; c.beginPath(); c.moveTo(640, 40); c.lineTo(640, 680); c.stroke();
      c.fillStyle = '#1A1630'; c.fillRect(0, 0, 250, VH); c.fillRect(1030, 0, 250, VH);
      c.fillStyle = '#231C3A'; c.fillRect(200, 640, 880, 80);
      // her from behind, the little one looking over her shoulder at the moon
      critter(c, 540, 720, 20, YOU({ back: true, aR: 1.3, noShadow: true }), t);
      critter(c, 600, 575, 11, ME({ swaddle: true, noShadow: true, eyes: t > 52.6 ? 'closed' : 'normal', lookY: -1, smile: t > 52.6 ? .5 : 0 }), t);
    });
    veil(c, '#FFE2A8', Math.pow(seg(t, 54.6, 55.66), 1.6));
  },
  grove(c, t) {
    const sc = (t - 55.66) * 125 + 30 * eio(seg(t, 59.0, 60.84));
    sunsetSky(c, t, 0);
    hills(c, t, 470, '#D9A35F', 22, .004, 1);
    // the hill with the tree, revealed past the forest
    c.save(); c.translate(1700 - sc * 1.2, 0); hills(c, t, 520, '#C7904E', 40, .003, 2); jujubeTree(c, 0, 470, .45, t); c.restore();
    c.fillStyle = '#B9874B'; c.fillRect(0, 600, VW, VH - 600);
    // forest: three parallax rows of trunks that thin out towards the hillside
    for (const [par, col, wid, n, cap] of [[.45, '#B98955', 16, 18, '#D8A954'], [.75, '#8E6239', 26, 14, '#C99033'], [1.15, '#5E3D22', 46, 10, '#A8702A']]) {
      for (let i = 0; i < n; i++) {
        const wx = i * (1500 / n) + H(i * 9 + wid) * 60, x = wx - sc * par; if (x < -100 || x > VW + 100) continue;
        if (wx > 1300) continue;
        c.fillStyle = col; c.fillRect(x, -10, wid, 620 + (par > 1 ? 80 : 0));
        c.beginPath(); c.arc(x + wid / 2, 40 + H(i) * 60, 70 + 40 * par, 0, TAU); c.fillStyle = cap; c.globalAlpha = .9; c.fill(); c.globalAlpha = 1;
      }
    }
    // sunbeams through the trees
    c.save(); c.globalCompositeOperation = 'lighter'; for (let i = 0; i < 4; i++) { const x = 200 + i * 300 - (sc * .3) % 300; c.fillStyle = 'rgba(255,230,160,.10)'; c.beginPath(); c.moveTo(x, 0); c.lineTo(x + 60, 0); c.lineTo(x + 260, 620); c.lineTo(x + 160, 620); c.fill(); } c.restore();
    // the two of them, long ago: a grown-up in a straw hat and a little one in a bow
    const bp = beatPos(t);
    critter(c, 560, 640, 12, ME({ hat: 'straw', walk: bp / 2, lookX: -.6, smile: .8 }), t);
    critter(c, 380, 640, 7, YOU({ walk: bp, dy: -Math.abs(Math.sin(bp * Math.PI)) * 1.4, eyes: 'happy', smile: 1, aL: 1.6, aR: 1.6 }), t);
    fallingLeaves(c, t, 14, 3, .9, 50);
    memoryGrade(c, t);
    veil(c, '#FFE2A8', 1 - seg(t, 55.66, 56.7));
  },
  jujube(c, t) {
    sunsetSky(c, t, 0);
    hills(c, t, 470, '#D9A35F', 20, .004, 1);
    hills(c, t, 560, '#C08A4A', 30, .003, 4);
    c.fillStyle = '#B07D45'; c.fillRect(0, 630, VW, VH - 630);
    const K = kicksIn(60.84, 64.64), kp = pulse(t, 9);
    jujubeTree(c, 690, 640, .95, t, t > 60.84 ? kp : 0);
    // a jujube shower on every kick: they fall, bounce once, and the little one runs to catch them
    const ground = 650, g = 1500, drops = [];
    K.forEach((k, j) => { for (let m = 0; m < 4; m++) drops.push({ k, x: 540 + 300 * H(j * 4 + m), y0: 300 + 110 * H(j * 4 + m + 40), s: j * 4 + m }); });
    for (const d of drops) {
      const a = t - d.k; if (a < 0) continue;
      let y = d.y0 + .5 * g * a * a, rot = a * 6;
      const tHit = Math.sqrt(2 * (ground - d.y0) / g);
      if (a > tHit) { const b = a - tHit, v = g * tHit * .25; y = ground - Math.max(0, v * b - .5 * g * b * b); rot = tHit * 6; }
      jujube(c, d.x, Math.min(y, ground), 10, rot);
    }
    // the grown-up swings the pole into the branches on each kick
    const sw = kp, mx = 470, u = 12;
    c.save(); c.translate(mx + 4 * u, 640 - 6 * u); c.rotate(-1.05 + sw * .35); c.strokeStyle = '#7A5A2E'; c.lineWidth = 9; c.lineCap = 'round'; c.beginPath(); c.moveTo(0, 0); c.lineTo(360, 0); c.stroke(); c.strokeStyle = INK; c.lineWidth = 2; c.stroke(); c.restore();
    critter(c, mx, 640, u, ME({ hat: 'straw', aR: 1.9 - sw * .4, aL: 1.0, lookX: 1, lookY: -1, eyes: 'happy', smile: .9, sq: sw * .06 }), t);
    const last = drops.filter(d => d.k <= t).slice(-1)[0], target = last ? last.x : 760;
    const kx = 760 + (target - 760) * eio(seg(t, 61, 61.8)) + Math.sin(t * 3) * 30, bp = beatPos(t);
    critter(c, kx, 645, 7, YOU({ walk: bp, aL: 2.4, aR: 2.4, eyes: 'happy', smile: 1, mouth: kp * .6, dy: -Math.abs(Math.sin(bp * Math.PI)) * 1.2, pouch: seg(t, 61.5, 64.4) }), t);
    fallingLeaves(c, t, 18, 11, .95, 70 + 60 * kp);
    memoryGrade(c, t);
  },
  pockets(c, t) {
    c.fillStyle = vgrad(c, 0, VH, ['#F2B26A', '#E98A4C', '#C45A3A']); c.fillRect(0, 0, VW, VH);
    glow(c, 930, 470, 420, 'rgba(255,220,150,.6)'); c.beginPath(); c.arc(930, 470, 120, 0, TAU); c.fillStyle = '#FFD98C'; c.fill();
    roofs(c, 1010, 600, 1, '#9A5A3A');
    hills(c, t, 600, '#8E4E30', 26, .0035, 2);
    // a ridge they sit on, then walk along
    c.fillStyle = '#6E3A24'; c.beginPath(); c.moveTo(0, VH); c.lineTo(0, 560); c.quadraticCurveTo(500, 520, 1280, 640); c.lineTo(1280, VH); c.fill();
    const ridge = x => { const p = x / 1280; return (1 - p) * (1 - p) * 560 + 2 * (1 - p) * p * 520 + p * p * 640; };
    const go = eio(seg(t, 67.2, 69.48)), bp = beatPos(t), sitting = t < 67.2;
    const ax = lerp(430, 760, go), kx = lerp(300, 650, go);
    // a jujube tossed up and caught, every two beats while they sit
    if (sitting) { const ph = (bp / 2) % 1, x = ax - 10, y = ridge(ax) - 100 - Math.sin(ph * Math.PI) * 150; jujube(c, x, y, 10, ph * 6); }
    const chew = sitting ? Math.max(0, Math.sin(((bp / 2) % 1) * TAU)) : 0;
    critter(c, ax, ridge(ax), 12, ME({ hat: 'straw', sitting, walk: sitting ? null : bp / 2, pouch: 1, eyes: 'happy', mouth: chew * .7, aR: sitting ? 1.3 : .3, lookY: sitting ? -1 : 0 }), t);
    critter(c, kx, ridge(kx), 7, YOU({ sitting, walk: sitting ? null : bp, pouch: 1, eyes: 'happy', smile: 1, mouth: sitting ? .3 + .3 * Math.sin(t * 9) : 0, dy: sitting ? 0 : -Math.abs(Math.sin(bp * Math.PI)) * 1.2 }), t);
    fallingLeaves(c, t, 10, 21, .8, 45);
    memoryGrade(c, t);
  },
  lane(c, t) {
    const walkK = 1 - eio(seg(t, 77.4, 78.44)), sc = 72 * (t - 69.48) * (t < 77.4 ? 1 : 1) - 20 * (1 - walkK);
    lane(c, t, sc);
    const bp = beatPos(t), close = eio(seg(t, 74.64, 76.4));
    const ax = 720, kx = lerp(420, 560, close);
    critter(c, ax, 640, 13, ME({ hat: 'cap', walk: walkK > .1 ? bp / 2 : null, lookX: t > 75.4 ? -1 : .6, smile: t > 75.4 ? .9 : .3, eyes: t > 75.4 ? 'happy' : 'normal' }), t);
    critter(c, kx, 645, 7, YOU({ walk: bp, dy: -Math.abs(Math.sin(bp * Math.PI)) * (1.3 + close * .6), eyes: 'normal', lookX: 1, lookY: -.6, aR: 1.4 + close * .8, aL: .6, smile: .6 }), t);
    memoryGrade(c, t);
  },
  coins(c, t) {
    lane(c, t, 72 * (77.4 - 69.48) - 20);
    const ax = 720, kx = 560;
    // one coin per beat, arcing from his hand to her hands; a flash when she catches it
    const b0 = Math.ceil(beatPos(78.5)), b1 = Math.floor(beatPos(Math.min(t, 81.8)));
    let caught = 0, lastCatch = -9;
    for (let b = b0; b <= b1; b++) {
      const t0 = BEATMAP.phase + b * BEATMAP.beat, fl = BEATMAP.beat * .95, p = (t - t0) / fl;
      if (p >= 1) { caught++; lastCatch = Math.max(lastCatch, t0 + fl); continue; }
      const x = lerp(ax - 70, kx + 10, p), y = lerp(520, 545, p) - Math.sin(p * Math.PI) * 170;
      coin(c, x, y, 17, p * 3);
    }
    const hop = Math.exp(-Math.max(0, t - lastCatch) * 8);
    critter(c, ax, 640, 13, ME({ hat: 'cap', lookX: -1, aL: 1.6 + .5 * Math.max(0, 1 - beatPhase(t) * 3), eyes: 'happy', smile: 1 }), t);
    critter(c, kx, 645, 7, YOU({ eyes: 'happy', smile: lerp(.6, 1.2, Math.min(1, caught / 6)), aL: 2.2, aR: 2.2, dy: -hop * 1.6, blush: .8, mouth: hop * .6 }), t);
    // her little stack of coins
    for (let i = 0; i < caught; i++) { c.save(); c.translate(kx + 62, 646 - i * 6); c.scale(1, .35); coin(c, (i % 2) * 3, 0, 16, 0); c.restore(); }
    if (hop > .05) { c.save(); c.globalAlpha = hop; c.strokeStyle = '#FFE08A'; c.lineWidth = 3; for (let i = 0; i < 8; i++) { const a = i / 8 * TAU, r = 30 + 30 * (1 - hop); c.beginPath(); c.moveTo(kx + 10 + Math.cos(a) * r * .5, 545 + Math.sin(a) * r * .5); c.lineTo(kx + 10 + Math.cos(a) * r, 545 + Math.sin(a) * r); c.stroke(); } c.restore(); }
    memoryGrade(c, t);
  },
  now(c, t) {
    withCam(c, 640, 360, lerp(1.02, 1.1, eio(seg(t, 82.1, 85.88))), () => {
      nursery(c, t);
      veil(c, '#1B2443', .2);
      // a copper coin on a red string, hanging over them
      const sw = Math.sin(t * 1.6) * .12;
      c.save(); c.translate(745, -10); c.rotate(sw); c.strokeStyle = '#C8322B'; c.lineWidth = 3; c.beginPath(); c.moveTo(0, 0); c.lineTo(0, 300); c.stroke(); glow(c, 0, 318, 60, 'rgba(255,200,120,.4)'); coin(c, 0, 318, 20, 0); c.restore();
      critter(c, 420, 700, 26, YOU({ eyes: 'happy', smile: 1, aR: 1.2, lookX: 1, blush: .7 }), t);
      critter(c, 655, 560, 14, ME({ swaddle: true, noShadow: true, eyes: 'normal', lookX: .4, lookY: -1, smile: .8, blush: .6 }), t);
      // a little arm out of the blanket, reaching for the coin
      const reach = eout(seg(t, 82.8, 83.8));
      c.save(); c.translate(707, 482); c.rotate(-1.0 - .35 * reach + .05 * Math.sin(t * 4)); c.beginPath(); c.roundRect(-4, -7, 22 + 20 * reach, 14, 7); c.fillStyle = LOOK_ME.col; c.fill(); c.strokeStyle = INK; c.lineWidth = 2.2; c.stroke(); c.restore();
    });
    const k = seg(t, 83.7, 84.5);
    if (k > 0) { c.save(); c.globalAlpha = k; c.textAlign = 'center'; c.textBaseline = 'middle'; c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 20; c.font = `700 72px ${SERIF}`; c.fillStyle = '#F6F3EC'; c.fillText('我 记 得', 640, 150); c.restore(); }
  },
};

function caption(c, t) {
  const cap = CAPTIONS.find(([a, b]) => t >= a && t < b); if (!cap) return;
  const [a, b, s] = cap, k = seg(t, a, a + .4) * (1 - seg(t, b - .4, b));
  c.save(); c.globalAlpha = k; c.font = `500 29px ${SERIF}`; c.textAlign = 'center'; c.textBaseline = 'middle';
  c.lineJoin = 'round'; c.lineWidth = 6; c.strokeStyle = 'rgba(24,18,34,.7)'; c.strokeText(s, 640, 684);
  c.shadowColor = 'rgba(0,0,0,.85)'; c.shadowBlur = 12; c.fillStyle = '#F7F2E8'; c.fillText(s, 640, 684); c.restore();
}

const XFADE = .45;
function drawFrame(main, t, scale) {
  t = clamp(t, 0, DUR - 1e-4);
  if (layer.width !== main.canvas.width) { layer.width = main.canvas.width; layer.height = main.canvas.height; }
  const i = shotIndex(t), s = SHOTS[i];
  main.setTransform(scale, 0, 0, scale, 0, 0); main.globalAlpha = 1;
  if (i > 0 && t - s.t0 < XFADE) {
    SHOT_FN[SHOTS[i - 1].name](main, t);
    const lc = layer.getContext('2d'); lc.setTransform(scale, 0, 0, scale, 0, 0); lc.globalAlpha = 1; lc.clearRect(0, 0, VW, VH);
    SHOT_FN[s.name](lc, t);
    main.setTransform(1, 0, 0, 1, 0, 0); main.globalAlpha = eio((t - s.t0) / XFADE); main.drawImage(layer, 0, 0); main.globalAlpha = 1;
    main.setTransform(scale, 0, 0, scale, 0, 0);
  } else SHOT_FN[s.name](main, t);
  const v = main.createRadialGradient(640, 360, 300, 640, 360, 820); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.3)'); main.fillStyle = v; main.fillRect(0, 0, VW, VH);
  caption(main, t);
  if (t < 1) veil(main, '#000', 1 - seg(t, .05, 1));
  if (t > DUR - 1.2) veil(main, '#000', seg(t, DUR - 1.2, DUR - .05));
}
