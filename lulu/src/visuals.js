// visuals.js — the remake, shot for shot. Room in world coordinates, a camera per shot,
// the room drawn to its own layer so close-ups can blur it (shallow depth of field).

const VW = 1280, VH = 720, TAU = Math.PI * 2;
const F_CN = 'NotoSC, sans-serif', F_EN = 'Fredoka, NotoSC, sans-serif';
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const eout = t => 1 - Math.pow(1 - clamp(t), 3);
const back = t => { t = clamp(t); const c = 1.9; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
const H = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
let ctx;
const roomCv = document.createElement('canvas');

// ---------------------------------------------------------------- the room (world units)
function rr(c, x, y, w, h, r, fill, stroke, lw = 3) { c.beginPath(); c.roundRect(x, y, w, h, r); if (fill) { c.fillStyle = fill; c.fill(); } if (stroke) { c.strokeStyle = stroke; c.lineWidth = lw; c.stroke(); } }
function drawRoom(c, t) {
  // bedroom wall
  let g = c.createLinearGradient(0, -200, 0, 640); g.addColorStop(0, '#E4D6F3'); g.addColorStop(1, '#CDB8EA');
  c.fillStyle = g; c.fillRect(-300, -300, 2600, 1000);
  // kitchen seen through a big arch
  c.save(); c.beginPath(); c.roundRect(900, 70, 1060, 560, [170, 170, 0, 0]); c.clip();
  g = c.createLinearGradient(0, 70, 0, 620); g.addColorStop(0, '#DCCBF2'); g.addColorStop(1, '#C8B2E8'); c.fillStyle = g; c.fillRect(900, 70, 1060, 560);
  // window + light
  rr(c, 1760, 150, 130, 190, 12, '#CFEFFF', '#FFFFFF', 8); c.fillStyle = '#FFFFFF'; c.fillRect(1822, 150, 6, 190);
  // upper cabinets
  for (let i = 0; i < 4; i++) { rr(c, 1000 + i * 180, 150, 170, 140, 12, '#86B9E8', '#6A9ED0', 3); rr(c, 1000 + i * 180 + 145, 205, 10, 32, 5, '#F6F1FF'); }
  // hood
  c.fillStyle = '#C9CDD8'; c.beginPath(); c.moveTo(1285, 170); c.lineTo(1415, 170); c.lineTo(1440, 262); c.lineTo(1260, 262); c.closePath(); c.fill();
  // lower cabinets, counter, oven
  for (let i = 0; i < 5; i++) rr(c, 945 + i * 188, 505, 180, 125, 10, i === 2 ? '#8FC3EC' : '#96D0B0', '#6C9FC8', 3);
  rr(c, 1318, 530, 124, 80, 8, '#2C3550'); rr(c, 1330, 542, 100, 50, 6, '#48557A');
  rr(c, 935, 480, 960, 26, 8, '#F7F3FB', '#D8CDE8', 2);
  c.fillStyle = '#3B3346'; c.fillRect(1290, 474, 150, 8);
  // green microwave, a little plant
  rr(c, 1600, 410, 110, 72, 10, '#A6D9A0', '#7DB57A', 3); rr(c, 1612, 422, 66, 48, 6, '#2F3B3A');
  rr(c, 1080, 440, 34, 40, 6, '#F4A3B8'); c.fillStyle = '#6CC05A'; c.beginPath(); c.ellipse(1097, 432, 18, 12, 0, 0, TAU); c.fill();
  // pot + steam (the steam sometimes curls into a ✻)
  rr(c, 1305, 425, 100, 55, 14, '#FF8A3D', '#2B2233', 3); rr(c, 1298, 418, 114, 12, 6, '#E86F2A', '#2B2233', 3);
  c.strokeStyle = '#2B2233'; c.lineWidth = 6; c.beginPath(); c.moveTo(1405, 440); c.lineTo(1450, 432); c.stroke();
  c.strokeStyle = 'rgba(255,255,255,.75)'; c.lineWidth = 5; c.lineCap = 'round';
  for (let k = 0; k < 3; k++) { const ph = (t * .6 + k / 3) % 1; c.globalAlpha = Math.sin(ph * Math.PI) * .8; c.beginPath(); for (let j = 0; j < 14; j++) { const yy = 405 - ph * 120 - j * 6; c.lineTo(1330 + k * 25 + Math.sin(j * .6 + t * 3 + k) * 8, yy); } c.stroke(); }
  c.globalAlpha = 1;
  // stool
  rr(c, 1300, 560, 110, 18, 6, '#E0A36B', '#2B2233', 3); c.fillStyle = '#C98A55'; c.fillRect(1312, 578, 12, 50); c.fillRect(1386, 578, 12, 50);
  c.restore();
  // arch trim
  c.strokeStyle = '#F2EAFB'; c.lineWidth = 14; c.beginPath(); c.roundRect(900, 70, 1060, 560, [170, 170, 0, 0]); c.stroke();
  // bedroom: window with curtains
  rr(c, 90, 120, 220, 250, 14, '#D8F1FF', '#FFFFFF', 10); c.fillStyle = '#FFFFFF'; c.fillRect(196, 120, 8, 250);
  c.fillStyle = '#FFF6E8'; c.beginPath(); c.moveTo(60, 100); c.quadraticCurveTo(110, 250, 70, 400); c.lineTo(40, 400); c.lineTo(40, 100); c.fill();
  c.beginPath(); c.moveTo(340, 100); c.quadraticCurveTo(290, 250, 330, 400); c.lineTo(360, 400); c.lineTo(360, 100); c.fill();
  // picture frames: a strawberry and a tangerine
  rr(c, 420, 140, 110, 120, 8, '#FFF3E6', '#F2B7C8', 8);
  c.fillStyle = '#E8445A'; c.beginPath(); c.moveTo(475, 170); c.quadraticCurveTo(510, 180, 475, 235); c.quadraticCurveTo(440, 180, 475, 170); c.fill();
  rr(c, 560, 150, 100, 110, 8, '#FFF3E6', '#F2B7C8', 8); tangerine(c, 610, 210, 26, true);
  // bed
  rr(c, 150, 390, 480, 200, [90, 90, 10, 10], '#F7B6CB', '#E48FAB', 4);
  for (let r = 0; r < 2; r++) for (let k = 0; k < 5; k++) { c.beginPath(); c.arc(215 + k * 85 + (r ? 42 : 0), 445 + r * 50, 6, 0, TAU); c.fillStyle = '#E48FAB'; c.fill(); }
  rr(c, 120, 545, 560, 80, 22, '#F9C9D8', '#E8A0B8', 4);
  rr(c, 170, 515, 170, 48, 22, '#FFFFFF', '#EBD6E4', 3);
  // teddy bear on the pillow
  c.fillStyle = '#C98E62'; for (const [x, y, r] of [[205, 492, 10], [237, 492, 10], [221, 510, 20], [221, 545, 24]]) { c.beginPath(); c.arc(x, y, r, 0, TAU); c.fill(); }
  c.fillStyle = '#2B2233'; c.beginPath(); c.arc(214, 508, 2.6, 0, TAU); c.arc(228, 508, 2.6, 0, TAU); c.fill();
  // nightstand + lamp
  rr(c, 720, 520, 120, 105, 10, '#FFF1F6', '#E8C8D8', 3);
  c.fillStyle = '#FFE9B8'; c.beginPath(); c.moveTo(745, 430); c.lineTo(815, 430); c.lineTo(830, 485); c.lineTo(730, 485); c.closePath(); c.fill(); c.fillStyle = '#E0C49A'; c.fillRect(775, 485, 10, 35);
  const lg = c.createRadialGradient(780, 470, 0, 780, 470, 220); lg.addColorStop(0, 'rgba(255,230,170,.45)'); lg.addColorStop(1, 'rgba(255,230,170,0)'); c.fillStyle = lg; c.fillRect(560, 250, 440, 440);
  // floor
  g = c.createLinearGradient(0, 625, 0, 1000); g.addColorStop(0, '#EAD9EE'); g.addColorStop(1, '#D9C3E3'); c.fillStyle = g; c.fillRect(-300, 625, 2600, 500);
  c.strokeStyle = 'rgba(160,120,170,.18)'; c.lineWidth = 2; for (let k = 0; k < 8; k++) { c.beginPath(); c.moveTo(-300, 650 + k * k * 8); c.lineTo(2300, 650 + k * k * 8); c.stroke(); }
  c.fillStyle = 'rgba(255,170,200,.45)'; c.beginPath(); c.ellipse(420, 690, 330, 45, 0, 0, TAU); c.fill();
  // warm window light
  const wl = c.createRadialGradient(200, 250, 0, 200, 250, 700); wl.addColorStop(0, 'rgba(255,245,220,.35)'); wl.addColorStop(1, 'rgba(255,245,220,0)'); c.fillStyle = wl; c.fillRect(-300, -300, 1400, 1300);
}

// ---------------------------------------------------------------- characters over time
const SIS_BED = { x: 440, y: 560 }, BRO_STOOL = { x: 1355, y: 562 }, BRO_FLOOR_END = 690;
function mouthOf(who, t) { const s = speaking(who, t); return s ? { mouth: s.k, vowel: s.s.v } : { mouth: 0 }; }
function sister(t) {
  const o = { look: LOOK_SIS, bonnet: true, dress: true, seed: 5, sitting: true, eyes: 'normal', aL: .3, aR: .3, ...mouthOf('sis', t) };
  let x = SIS_BED.x, y = SIS_BED.y;
  if (t < 2.07) { o.lookX = .9; o.eyes = t > .5 ? 'teary' : 'normal'; o.brows = 'sad'; o.frown = 1; o.tears = .25 * seg(t, .8, 2); o.sq = .02 * Math.sin(t * 20); }
  else if (t < 5.47) { o.eyes = 'teary'; o.brows = 'sad'; o.frown = 1; o.tears = lerp(.3, 1, seg(t, 2.07, 3.8)); o.sq = .03 * Math.sin(t * 26); o.lookX = .2; }
  else if (t < 9.07) { o.eyes = 'teary'; o.brows = 'sad'; o.frown = 1; o.tears = lerp(1, .5, seg(t, 5.5, 9)); o.lookX = lerp(.9, .6, seg(t, 6, 8.5)); o.sq = .02 * Math.sin(t * 22); }
  else {
    o.sitting = t < 9.3; o.brows = t < 10 ? 'sad' : null; o.eyes = t < 10.4 ? 'teary' : 'happy'; o.tears = .5 * (1 - seg(t, 9.2, 10.4)); o.blush = seg(t, 9.8, 10.3);
    o.lookX = .6; o.aL = o.aR = lerp(.3, 2.4, eout(seg(t, 9.5, 9.9))) + .12 * Math.sin(t * 6);
    if (!o.mouth) o.smile = .6;
    const hop = SCORE.hop.find(h => h.who === 'sis').t, hugT = SCORE.hug[0].t;
    if (t >= hop) { const p = seg(t, hop, hugT); x = lerp(SIS_BED.x + 30, 598, eio(p)); y = lerp(SIS_BED.y, 604, p) - Math.sin(p * Math.PI) * 70; o.aL = o.aR = 2.8; }
    if (t >= hugT) {
      const d = t - hugT; o.hugging = true; x = 598; y = 606; o.rot = .1 + .06 * Math.sin(d * 3.2); o.sq = .12 * Math.exp(-d * 6) * Math.cos(d * 25);
      o.eyes = 'happy'; o.blush = 1; o.lookX = .3;
      const his = speaking('bro', t); if (his && t > 12) { o.mouth = .55 * his.k; o.vowel = 'a'; }
    }
  }
  return { x, y, u: 13, o };
}
function brother(t) {
  const o = { look: LOOK_BRO, fruit: true, strap: true, seed: 2, eyes: 'normal', aL: .3, aR: .3, ...mouthOf('bro', t) };
  let x = BRO_STOOL.x, y = BRO_STOOL.y;
  const turn = SCORE.turn[0].t, hop = SCORE.hop.find(h => h.who === 'bro').t, s0 = SCORE.step[0].t, s1 = SCORE.step[SCORE.step.length - 1].t + .2;
  if (t < turn) { o.back = true; o.aR = 1.35 + .28 * Math.sin(t * 6); o.aL = .35; o.dy = -.12 * Math.abs(Math.sin(t * 3)); }
  else if (t < turn + .12) { o.back = true; o.sx = lerp(1, .15, seg(t, turn, turn + .12)); }
  else if (t < 5.47) { o.sx = lerp(.15, 1, eout(seg(t, turn + .12, turn + .3))); o.eyes = 'wide'; o.brows = 'up'; o.lookX = -1; o.aR = .9; if (!o.mouth) o.frown = 0; }
  else {
    o.lookX = -.8; o.smile = .5;
    if (t < hop) { o.towel = true; o.aL = o.aR = .9 + .25 * Math.sin(t * 18); }
    else if (t < s0) { const p = seg(t, hop, s0); x = lerp(BRO_STOOL.x, 1300, p); y = lerp(BRO_STOOL.y, 625, p) - Math.sin(p * Math.PI) * 50; o.aL = o.aR = 2.2; }
    else if (t < s1) { const p = seg(t, s0, s1); x = lerp(1300, BRO_FLOOR_END, p); y = 625; o.walk = (t - s0) / .56; o.dy = -.3 * Math.abs(Math.sin((t - s0) / .28 * Math.PI)); o.aL = .3 + .4 * Math.sin((t - s0) / .28 * Math.PI); o.aR = .3 - .4 * Math.sin((t - s0) / .28 * Math.PI); o.flip = true; }
    else { x = BRO_FLOOR_END; y = 625; o.aL = .3; o.aR = .3; o.lookX = -.9; }
    if (t >= 9.07) {
      x = 690; y = 625; o.lookX = -.7; o.eyes = t < 9.6 ? 'normal' : 'happy'; o.smile = .8;
      const hugT = SCORE.hug[0].t;
      if (t > 10.3 && t < hugT) { o.aL = o.aR = lerp(.3, 2.2, seg(t, 10.3, 10.7)); }
      if (t >= hugT) { const d = t - hugT; o.hugging = true; x = 712; o.rot = -.1 - .05 * Math.sin(d * 3.2); o.eyes = 'happy'; o.blush = .8; o.sq = -.08 * Math.exp(-d * 6) * Math.cos(d * 25); }
    }
  }
  return { x, y, u: 13, o };
}

// ---------------------------------------------------------------- cameras
function camera(t) {
  const s = shotAt(t), p = seg(t, s.t0, s.t1);
  switch (s.name) {
    case 'wide': return { cx: 905, cy: 430, z: lerp(.8, .83, p), blur: 0, px: 0 };
    case 'sisCU': return { cx: 440, cy: 468, z: lerp(3.2, 3.55, eio(p)), blur: 7, px: 0 };
    case 'broMS': return { cx: 1350, cy: 470, z: lerp(2.2, 2.35, p), blur: 4, px: 0 };
    case 'walk': return { cx: lerp(1040, 760, eio(seg(t, 6.0, 8.8))), cy: 440, z: lerp(.95, 1.05, p), blur: 0, px: 0 };
    default: { // the hug: a slow push-in, with the background sliding the other way to suggest an orbit
      const q = seg(t, 9.07, 15.07);
      return { cx: lerp(610, 655, eio(q)), cy: lerp(470, 490, q), z: lerp(1.75, 2.15, eio(q)), blur: 2.5, px: lerp(70, -70, eio(q)) };
    }
  }
}

// ---------------------------------------------------------------- hearts, subtitles, end
function hearts(t) {
  const hugT = SCORE.hug[0].t;
  for (let i = 0; i < 16; i++) {
    const t0 = hugT + i * .3, d = t - t0; if (d < 0 || d > 2.4) continue;
    const x = 655 + (H(i) - .5) * 220 + Math.sin(d * 3 + i) * 14, y = 480 - d * 90, s = back(seg(d, 0, .25)) * (1 - seg(d, 1.8, 2.4)) * (7 + H(i + 3) * 6);
    ctx.fillStyle = ['#FF6F91', '#FF9EB5', '#FFC1D2'][i % 3]; ctx.beginPath();
    for (let k = 0; k <= 24; k++) { const a = k / 24 * TAU; ctx.lineTo(x + 16 * Math.pow(Math.sin(a), 3) * s / 16, y - (13 * Math.cos(a) - 5 * Math.cos(2 * a) - 2 * Math.cos(3 * a) - Math.cos(4 * a)) * s / 16); }
    ctx.fill();
  }
}
function subtitle(t) {
  const L = LINES.find(l => t >= l.t0 - .08 && t < l.t1 + .35); if (!L) return;
  ctx.font = `900 46px ${F_CN}`; ctx.textAlign = 'center'; ctx.textBaseline = 'middle'; ctx.lineJoin = 'round';
  ctx.strokeStyle = '#1b1320'; ctx.lineWidth = 10; ctx.strokeText(L.text, 640, 640);
  ctx.fillStyle = '#FFE14D'; ctx.fillText(L.text, 640, 640);
}
function endCard(t) {
  if (t < 15.07) return;
  const p = eout(seg(t, 15.07, 15.5));
  ctx.fillStyle = `rgba(255,236,244,${.78 * p})`; ctx.fillRect(0, 0, VW, VH);
  ctx.save(); ctx.globalAlpha = p; ctx.translate(640, 330); const s = back(seg(t, 15.07, 15.4)); ctx.scale(s, s);
  ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
  ctx.font = `900 76px ${F_CN}`; ctx.lineJoin = 'round'; ctx.strokeStyle = '#D0698D'; ctx.lineWidth = 12; ctx.strokeText('噜噜和噜妹儿', 0, -20); ctx.fillStyle = '#FFFFFF'; ctx.fillText('噜噜和噜妹儿', 0, -20);
  ctx.font = `700 34px ${F_EN}`; ctx.fillStyle = '#A84D33'; ctx.fillText('✻ Claude Code 版', 0, 58);
  ctx.restore();
  if (t > DUR - .35) { ctx.fillStyle = `rgba(255,255,255,${seg(t, DUR - .35, DUR)})`; ctx.fillRect(0, 0, VW, VH); }
}

function drawFrame(c, t, scale) {
  ctx = c; t = clamp(t, 0, DUR - 1e-4);
  if (roomCv.width !== c.canvas.width) { roomCv.width = c.canvas.width; roomCv.height = c.canvas.height; }
  const cam = camera(t), rc = roomCv.getContext('2d');
  // room layer (blurred in close-ups)
  rc.setTransform(scale, 0, 0, scale, 0, 0);
  rc.save(); rc.translate(640, 360); rc.scale(cam.z, cam.z); rc.translate(-cam.cx + cam.px / cam.z, -cam.cy); drawRoom(rc, t); rc.restore();
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.filter = cam.blur ? `blur(${cam.blur * scale}px)` : 'none';
  ctx.drawImage(roomCv, 0, 0); ctx.filter = 'none';
  // characters, sharp
  ctx.setTransform(scale, 0, 0, scale, 0, 0);
  ctx.save(); ctx.translate(640, 360); ctx.scale(cam.z, cam.z); ctx.translate(-cam.cx, -cam.cy);
  const sis = sister(t), bro = brother(t);
  const hugging = t >= SCORE.hug[0].t;
  // draw the one further back first; while hugging, 噜妹儿 is in front
  const order = hugging ? [bro, sis] : [bro, sis];
  for (const ch of order) critter(ctx, ch.x, ch.y, ch.u, ch.o, t);
  if (t >= SCORE.hug[0].t) hearts(t);
  ctx.restore();
  // a soft vignette, subtitles, end card
  const v = ctx.createRadialGradient(640, 360, 300, 640, 360, 820); v.addColorStop(0, 'rgba(60,30,80,0)'); v.addColorStop(1, 'rgba(60,30,80,.28)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, VW, VH);
  subtitle(t);
  endCard(t);
}
