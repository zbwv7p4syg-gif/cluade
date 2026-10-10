// chars.js — the two souls of 我记得, drawn on Clawd's body plan (the Claude Code mascot):
// a 10u × 6u block, four stubby legs, two slit eyes, stubby arms. (x, y) is the ground point between the feet;
// arm angle 0 = down, larger = raised. Orange is the one who remembers, pink is the one it keeps finding.

const INK = '#2B2233';
const LOOK_ME = { col: '#D97757', dk: '#A84D33', lt: '#F2A283' };
const LOOK_YOU = { col: '#F29BB8', dk: '#D0698D', lt: '#FCD2E0' };
const LOOK_HELPER = { col: '#EEF2F8', dk: '#C9D3E2', lt: '#FFFFFF' };

// o: { look, flip, dy, sq, rot, aL, aR, back, eyes, brows, mouth, smile, blush, walk, sitting, alpha,
//      swaddle, hat ('straw' | 'cap' | 'surgeon'), mask, pouch (0..1), bow, lookX, seed, noShadow }
function critter(c, x, y, u, o = {}, T = 0) {
  const L = o.look || LOOK_ME, dy = (o.dy || 0) * u, sq = o.sq || 0;
  c.save(); if (o.alpha != null) c.globalAlpha *= o.alpha;
  if (!o.noShadow) { c.save(); c.globalAlpha *= .18 * (1 - Math.min(.8, Math.abs(o.dy || 0) * .08)); c.beginPath(); c.ellipse(x, y + u * .2, u * 5.8, u * .9, 0, 0, Math.PI * 2); c.fillStyle = '#2a1a30'; c.fill(); c.restore(); }
  c.translate(x, y + dy); if (o.rot) c.rotate(o.rot);
  c.scale((o.flip ? -1 : 1) * (1 + sq * .6), 1 - sq);
  c.lineJoin = 'round'; c.lineCap = 'round'; c.strokeStyle = INK; c.lineWidth = Math.max(1, u * .17);
  const box = (bx, by, w, h, fill, r) => { c.beginPath(); c.roundRect(bx, by, w, h, r ?? Math.min(w, h) * .14); c.fillStyle = fill; c.fill(); c.stroke(); };
  if (!o.swaddle) {
    [-4, -2, 1, 3].forEach((lx, i) => {
      let h = 2.2; if (o.walk != null) { const ph = Math.sin((o.walk + (i % 2 ? .5 : 0)) * Math.PI * 2); if (ph > 0) h = 2.2 - ph * .9; }
      if (o.sitting) h = 1.2;
      box(lx * u, -2.4 * u, u, h * u, L.dk);
    });
    const arm = (side, a) => { c.save(); c.translate(side * 4.9 * u, -4.5 * u); c.rotate(side < 0 ? a : -a); box(side < 0 ? -2.2 * u : 0, -.5 * u, 2.2 * u, u, L.col); c.restore(); };
    arm(-1, o.aL ?? .2); arm(1, o.aR ?? .2);
  }
  box(-5 * u, -8 * u, 10 * u, 6 * u, L.col, u * .75);
  c.save(); c.beginPath(); c.roundRect(-5 * u, -8 * u, 10 * u, 6 * u, u * .75); c.clip();
  c.globalAlpha *= .5; c.beginPath(); c.ellipse(-1.6 * u, -6.6 * u, 3.4 * u, 1.3 * u, -.08, 0, Math.PI * 2); c.fillStyle = L.lt; c.fill();
  c.globalAlpha *= .6; c.fillStyle = L.dk; c.fillRect(-5 * u, -3.6 * u, 10 * u, 1.8 * u);
  c.restore();
  c.beginPath(); c.roundRect(-5 * u, -8 * u, 10 * u, 6 * u, u * .75); c.stroke();
  if (o.pouch) pouches(c, u, o.pouch);
  if (!o.back) face(c, u, o, T);
  if (o.mask) { c.save(); c.lineWidth = Math.max(1, u * .12); c.beginPath(); c.roundRect(-2.6 * u, -5.4 * u, 5.2 * u, 2.4 * u, .8 * u); c.fillStyle = '#BFE3E0'; c.fill(); c.stroke(); c.beginPath(); c.moveTo(-2.6 * u, -4.6 * u); c.lineTo(-5 * u, -6.2 * u); c.moveTo(2.6 * u, -4.6 * u); c.lineTo(5 * u, -6.2 * u); c.stroke(); c.restore(); }
  if (o.swaddle) swaddle(c, u);
  if (o.hat === 'straw') strawHat(c, u);
  if (o.hat === 'cap') skullcap(c, u);
  if (o.hat === 'surgeon') { c.save(); c.lineWidth = Math.max(1, u * .12); c.beginPath(); c.moveTo(-5.2 * u, -7.6 * u); c.quadraticCurveTo(-5 * u, -10.4 * u, 0, -10.4 * u); c.quadraticCurveTo(5 * u, -10.4 * u, 5.2 * u, -7.6 * u); c.closePath(); c.fillStyle = '#BFE3E0'; c.fill(); c.stroke(); c.restore(); }
  if (o.bow) bow(c, u);
  c.restore();
}

function face(c, u, o, T) {
  const e = o.eyes || 'normal', blink = e === 'normal' && ((T * .9 + (o.seed || 0)) % 3.3) < .12;
  c.save(); c.lineWidth = Math.max(1.2, u * .28); c.strokeStyle = INK;
  for (const ex of [-3, 2]) {
    const X = ex * u + (o.lookX || 0) * u * .4, Y = -7 * u + (o.lookY || 0) * u * .3, cx = X + .5 * u;
    if ((e === 'normal' || e === 'teary' || e === 'wide') && !blink) {
      const w = e === 'wide' ? 1.25 : 1, h = e === 'teary' ? 1.9 : e === 'wide' ? 2.2 : 2;
      c.fillStyle = INK; c.beginPath(); c.roundRect(cx - .5 * w * u, Y + (2 - h) * u / 2, w * u, h * u, u * .2); c.fill();
      c.fillStyle = '#FFF5E2'; c.beginPath(); c.ellipse(cx - .12 * u, Y + .45 * u, u * (e === 'teary' ? .28 : .18), u * (e === 'teary' ? .36 : .26), 0, 0, 7); c.fill();
      if (e === 'teary') { c.fillStyle = 'rgba(140,200,255,.8)'; c.beginPath(); c.ellipse(cx, Y + 1.95 * u, u * .62, u * .22, 0, 0, 7); c.fill(); }
    } else if (blink || e === 'closed') { c.beginPath(); c.moveTo(X - .2 * u, Y + 1.3 * u); c.quadraticCurveTo(cx, Y + 1.8 * u, X + 1.2 * u, Y + 1.3 * u); c.stroke(); }
    else if (e === 'happy') { c.beginPath(); c.moveTo(X - .4 * u, Y + 1.6 * u); c.quadraticCurveTo(cx, Y + .2 * u, X + 1.4 * u, Y + 1.6 * u); c.stroke(); }
    else if (e === 'sad') { c.beginPath(); c.moveTo(X - .4 * u, Y + 1.1 * u); c.quadraticCurveTo(cx, Y + 1.9 * u, X + 1.4 * u, Y + 1.1 * u); c.stroke(); }
  }
  if (o.brows === 'sad') { c.lineWidth = u * .22; for (const [a, b] of [[-3.4, -2.1], [3.4, 2.1]]) { c.beginPath(); c.moveTo(a * u, -7.9 * u); c.lineTo(b * u + .5 * u, -8.5 * u); c.stroke(); } }
  if (o.brows === 'up') { c.lineWidth = u * .22; for (const a of [-3, 2]) { c.beginPath(); c.moveTo(a * u - .1 * u, -8.2 * u); c.quadraticCurveTo(a * u + .5 * u, -8.8 * u, a * u + 1.1 * u, -8.2 * u); c.stroke(); } }
  c.restore();
  if (o.blush) { c.save(); c.globalAlpha *= .55 * o.blush; for (const bx of [-3.7, 3.7]) { c.beginPath(); c.ellipse(bx * u, -4.9 * u, .85 * u, .42 * u, 0, 0, 7); c.fillStyle = '#FF6F91'; c.fill(); } c.restore(); }
  if (o.mask) return;
  const k = o.mouth || 0, my = -4.4 * u;
  c.save(); c.strokeStyle = INK; c.lineWidth = Math.max(1, u * .2);
  if (k > .05) {
    const w = .8 * u, h = u * k + .12 * u;
    c.beginPath(); c.ellipse(0, my + h * .3, w, h, 0, 0, 7); c.fillStyle = '#5A1F2E'; c.fill(); c.stroke();
    if (h > .5 * u) { c.beginPath(); c.ellipse(0, my + h * .75, w * .55, h * .3, 0, 0, 7); c.fillStyle = '#FF8FA3'; c.fill(); }
  } else if (o.smile) { c.beginPath(); c.moveTo(-1 * u, my - .1 * u); c.quadraticCurveTo(0, my + .9 * u * o.smile, 1 * u, my - .1 * u); c.stroke(); }
  else if (o.pout) { c.beginPath(); c.moveTo(-.6 * u, my + .3 * u); c.quadraticCurveTo(0, my - .3 * u, .6 * u, my + .3 * u); c.stroke(); }
  c.restore();
}

// newborn: a cream blanket wrapped round everything below the eyes' line
function swaddle(c, u) {
  c.save(); c.lineWidth = Math.max(1, u * .15); c.strokeStyle = INK;
  c.beginPath(); c.moveTo(-6 * u, -3.2 * u); c.quadraticCurveTo(-6.4 * u, .2 * u, -3 * u, .6 * u); c.lineTo(3 * u, .6 * u); c.quadraticCurveTo(6.4 * u, .2 * u, 6 * u, -3.2 * u);
  c.quadraticCurveTo(0, -1.8 * u, -6 * u, -3.2 * u); c.closePath(); c.fillStyle = '#FFF4E0'; c.fill(); c.stroke();
  c.beginPath(); c.moveTo(-6 * u, -3.2 * u); c.quadraticCurveTo(-1 * u, -3.6 * u, 3.2 * u, -.2 * u); c.stroke();
  c.fillStyle = 'rgba(242,155,184,.55)'; for (let i = 0; i < 5; i++) { c.beginPath(); c.arc((-4 + i * 2) * u, (-1 + (i % 2) * .6) * u, .32 * u, 0, 7); c.fill(); }
  c.restore();
}
function strawHat(c, u) {
  c.save(); c.lineWidth = Math.max(1, u * .14); c.strokeStyle = INK;
  c.beginPath(); c.ellipse(0, -8 * u, 7.4 * u, 1.3 * u, 0, 0, 7); c.fillStyle = '#E8C46A'; c.fill(); c.stroke();
  c.beginPath(); c.moveTo(-3.6 * u, -8.2 * u); c.quadraticCurveTo(-3.4 * u, -11.2 * u, 0, -11.3 * u); c.quadraticCurveTo(3.4 * u, -11.2 * u, 3.6 * u, -8.2 * u); c.closePath(); c.fillStyle = '#E8C46A'; c.fill(); c.stroke();
  c.fillStyle = '#B5432F'; c.fillRect(-3.55 * u, -9.2 * u, 7.1 * u, .9 * u);
  c.restore();
}
// a black melon-rind skullcap with a red knot: the old-fashioned grown-up
function skullcap(c, u) {
  c.save(); c.lineWidth = Math.max(1, u * .14); c.strokeStyle = INK;
  c.beginPath(); c.moveTo(-4.6 * u, -7.7 * u); c.quadraticCurveTo(-4.4 * u, -10.6 * u, 0, -10.7 * u); c.quadraticCurveTo(4.4 * u, -10.6 * u, 4.6 * u, -7.7 * u); c.closePath(); c.fillStyle = '#2E2A36'; c.fill(); c.stroke();
  c.strokeStyle = 'rgba(255,255,255,.18)'; for (const a of [-2.2, 0, 2.2]) { c.beginPath(); c.moveTo(a * u * .5, -10.6 * u); c.quadraticCurveTo(a * u, -9.4 * u, a * u * 1.6, -7.8 * u); c.stroke(); }
  c.beginPath(); c.arc(0, -10.9 * u, .55 * u, 0, 7); c.fillStyle = '#C8322B'; c.fill();
  c.restore();
}
// a cloth bag tied at the waist, bulging with jujubes as k → 1
function pouches(c, u, k) {
  c.save(); c.lineWidth = Math.max(1, u * .13); c.strokeStyle = INK;
  c.beginPath(); c.moveTo(-5 * u, -2.9 * u); c.lineTo(4.6 * u, -2.9 * u); c.lineWidth = u * .5; c.strokeStyle = '#6E7F94'; c.stroke(); c.lineWidth = Math.max(1, u * .13); c.strokeStyle = INK;
  const rx = (1.5 + .9 * k) * u, ry = (1.3 + .7 * k) * u, bx = 5.4 * u, by = -2.6 * u;
  for (let j = 0; j < Math.round(k * 4); j++) jujube(c, bx + (j - 1.5) * .8 * u, by - ry * .75 - (j % 2) * .3 * u, .55 * u, j - 1.5);
  c.beginPath(); c.ellipse(bx, by, rx, ry, 0, 0, Math.PI * 2); c.fillStyle = '#7B8FA6'; c.fill(); c.stroke();
  c.beginPath(); c.moveTo(bx - rx * .9, by - ry * .35); c.quadraticCurveTo(bx, by + ry * .2, bx + rx * .9, by - ry * .35); c.stroke();
  c.restore();
}
function bow(c, u) {
  c.save(); c.translate(2.6 * u, -8.3 * u); c.rotate(.18); c.lineWidth = Math.max(1, u * .14); c.strokeStyle = INK; c.fillStyle = '#E8436E';
  for (const s of [-1, 1]) { c.beginPath(); c.moveTo(0, 0); c.quadraticCurveTo(s * 2.4 * u, -1.9 * u, s * 2.6 * u, 0); c.quadraticCurveTo(s * 2.4 * u, 1.7 * u, 0, 0); c.fill(); c.stroke(); }
  c.beginPath(); c.arc(0, 0, .55 * u, 0, 7); c.fillStyle = '#C92F57'; c.fill(); c.stroke();
  c.restore();
}

// ---------------------------------------------------------------- props
function jujube(c, x, y, r, rot = 0) {
  c.save(); c.translate(x, y); c.rotate(rot);
  c.beginPath(); c.ellipse(0, 0, r * .82, r, 0, 0, 7); c.fillStyle = '#B3261E'; c.fill(); c.lineWidth = Math.max(1, r * .14); c.strokeStyle = INK; c.stroke();
  c.beginPath(); c.ellipse(r * .25, r * .2, r * .45, r * .55, 0, 0, 7); c.fillStyle = '#E8B04A'; c.globalAlpha *= .7; c.fill(); c.globalAlpha /= .7;
  c.beginPath(); c.ellipse(-r * .3, -r * .35, r * .18, r * .3, -.4, 0, 7); c.fillStyle = 'rgba(255,255,255,.6)'; c.fill();
  c.strokeStyle = '#5B3A1E'; c.lineWidth = Math.max(1, r * .18); c.beginPath(); c.moveTo(0, -r); c.lineTo(r * .15, -r * 1.35); c.stroke();
  c.restore();
}
// a copper coin with a square hole; spin = 0..1 squashes it as it flips
function coin(c, x, y, r, spin = 0) {
  const sx = Math.max(.08, Math.abs(Math.cos(spin * Math.PI)));
  c.save(); c.translate(x, y); c.scale(sx, 1);
  c.beginPath(); c.arc(0, 0, r, 0, 7); c.fillStyle = '#C88A3A'; c.fill(); c.lineWidth = Math.max(1, r * .12); c.strokeStyle = '#6B4218'; c.stroke();
  c.beginPath(); c.arc(0, 0, r * .78, 0, 7); c.strokeStyle = 'rgba(107,66,24,.6)'; c.lineWidth = Math.max(1, r * .06); c.stroke();
  c.fillStyle = '#4A2E12'; c.fillRect(-r * .26, -r * .26, r * .52, r * .52);
  c.beginPath(); c.ellipse(-r * .45, -r * .4, r * .22, r * .12, -.6, 0, 7); c.fillStyle = 'rgba(255,230,170,.7)'; c.fill();
  c.restore();
}
// an old leather suitcase, bigger than whoever is dragging it; its stickers are the places it has been
function suitcase(c, x, y, s, rot = 0, T = 0) {
  c.save(); c.translate(x, y); c.rotate(rot); c.lineJoin = 'round'; c.lineWidth = 3; c.strokeStyle = INK;
  c.beginPath(); c.roundRect(-55 * s, -110 * s, 110 * s, 22 * s, 8 * s); c.lineWidth = 6 * s; c.stroke(); c.lineWidth = 3;   // handle
  c.beginPath(); c.roundRect(-95 * s, -95 * s, 190 * s, 140 * s, 16 * s); c.fillStyle = '#8C5A3C'; c.fill(); c.stroke();
  c.fillStyle = 'rgba(255,220,180,.18)'; c.beginPath(); c.roundRect(-88 * s, -88 * s, 176 * s, 34 * s, 10 * s); c.fill();
  for (const bx of [-55, 45]) { c.fillStyle = '#5E3A26'; c.fillRect(bx * s, -95 * s, 12 * s, 140 * s); c.strokeRect(bx * s, -95 * s, 12 * s, 140 * s); c.fillStyle = '#E2B65A'; c.fillRect((bx - 2) * s, -25 * s, 16 * s, 12 * s); }
  for (const [cx, cy] of [[-95, -95], [95, -95], [-95, 45], [95, 45]]) { c.beginPath(); c.arc(cx * s, cy * s, 9 * s, 0, 7); c.fillStyle = '#E2B65A'; c.fill(); c.stroke(); }
  // stickers: a pyramid, a jujube, a coin, a moon — earlier lives
  c.save(); c.translate(-20 * s, 10 * s); c.rotate(-.15); c.fillStyle = '#F3E3C2'; c.beginPath(); c.roundRect(-22 * s, -18 * s, 44 * s, 34 * s, 4 * s); c.fill(); c.stroke();
  c.beginPath(); c.moveTo(-14 * s, 10 * s); c.lineTo(0, -12 * s); c.lineTo(14 * s, 10 * s); c.closePath(); c.fillStyle = '#D9A441'; c.fill(); c.restore();
  c.save(); c.translate(72 * s, -40 * s); c.rotate(.2); c.beginPath(); c.arc(0, 0, 17 * s, 0, 7); c.fillStyle = '#F3E3C2'; c.fill(); c.stroke(); jujube(c, 0, 2 * s, 9 * s); c.restore();
  c.save(); c.translate(-72 * s, -40 * s); c.beginPath(); c.arc(0, 0, 16 * s, 0, 7); c.fillStyle = '#2F3D66'; c.fill(); c.stroke(); c.beginPath(); c.arc(4 * s, -2 * s, 8 * s, 0, 7); c.fillStyle = '#F3E3C2'; c.fill(); c.restore();
  coin(c, 75 * s, 25 * s, 12 * s);
  c.restore();
}
