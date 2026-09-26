// chars.js — 噜噜 (orange Clawd) and 噜妹儿 (pink Clawd).
// Same body plan as Clawd, the Claude Code mascot: a 10u × 6u block, four stubby legs, two slit eyes,
// stubby arms. (x, y) is the ground point between the feet; arm angle 0 = down, larger = raised.

const INK = '#2B2233';
const LOOK_BRO = { col: '#D97757', dk: '#A84D33', lt: '#F2A283' };
const LOOK_SIS = { col: '#F29BB8', dk: '#D0698D', lt: '#FCD2E0' };

function tangerine(c, x, y, r, leaf = true) {
  c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fillStyle = '#FF9A2E'; c.fill(); c.lineWidth = r * .14; c.strokeStyle = INK; c.stroke();
  c.beginPath(); c.ellipse(x - r * .35, y - r * .35, r * .3, r * .18, -.6, 0, Math.PI * 2); c.fillStyle = 'rgba(255,255,255,.55)'; c.fill();
  if (leaf) { c.beginPath(); c.ellipse(x + r * .45, y - r * 1.05, r * .55, r * .25, -.7, 0, Math.PI * 2); c.fillStyle = '#6CC05A'; c.fill(); c.stroke(); }
}

// o: { look, u, flip, dy, sq, rot, aL, aR, back, eyes, brows, mouth(0..1 open), vowel, blush, tears(0..1), walk, bonnet, dress, strap, fruit, towel }
function critter(c, x, y, u, o = {}, T = 0) {
  const L = o.look || LOOK_BRO, dy = (o.dy || 0) * u, sq = o.sq || 0;
  c.save();
  // soft contact shadow
  c.save(); c.globalAlpha = .18 * (1 - Math.min(.8, Math.abs(o.dy || 0) * .08)); c.beginPath(); c.ellipse(x, y + u * .2, u * 5.8, u * .9, 0, 0, Math.PI * 2); c.fillStyle = '#3a2350'; c.fill(); c.restore();
  c.translate(x, y + dy); if (o.rot) c.rotate(o.rot);
  c.scale((o.flip ? -1 : 1) * (o.sx ?? 1) * (1 + sq * .6), 1 - sq);
  c.lineJoin = 'round'; c.lineCap = 'round'; c.strokeStyle = INK; c.lineWidth = Math.max(1, u * .17);
  const box = (bx, by, w, h, fill, r) => { c.beginPath(); c.roundRect(bx, by, w, h, r ?? Math.min(w, h) * .14); c.fillStyle = fill; c.fill(); c.stroke(); };
  // legs
  [-4, -2, 1, 3].forEach((lx, i) => {
    let h = 2.2; if (o.walk != null) { const ph = Math.sin((o.walk + (i % 2 ? .5 : 0)) * Math.PI * 2); if (ph > 0) h = 2.2 - ph * .9; }
    if (o.sitting) h = 1.2;
    box(lx * u, -2.4 * u, u, h * u, L.dk);
  });
  // arms (behind the body)
  const arm = (side, a) => { c.save(); c.translate(side * 4.9 * u, -4.5 * u); c.rotate(side < 0 ? a : -a); box(side < 0 ? -2.2 * u : 0, -.5 * u, 2.2 * u, u, L.col); c.restore(); };
  if (!o.hugging) { arm(-1, o.aL ?? .2); arm(1, o.aR ?? .2); }
  // body
  box(-5 * u, -8 * u, 10 * u, 6 * u, L.col, u * .75);
  c.save(); c.beginPath(); c.roundRect(-5 * u, -8 * u, 10 * u, 6 * u, u * .75); c.clip();
  c.globalAlpha = .5; c.beginPath(); c.ellipse(-1.6 * u, -6.6 * u, 3.4 * u, 1.3 * u, -.08, 0, Math.PI * 2); c.fillStyle = L.lt; c.fill();
  c.globalAlpha = .3; c.fillStyle = L.dk; c.fillRect(-5 * u, -3.6 * u, 10 * u, 1.8 * u);
  c.globalAlpha = 1;
  // strawberry dress (噜妹儿)
  if (o.dress) {
    c.beginPath(); c.moveTo(-5.4 * u, -1.9 * u); c.lineTo(-4.6 * u, -4.1 * u); c.lineTo(4.6 * u, -4.1 * u); c.lineTo(5.4 * u, -1.9 * u); c.closePath();
    c.fillStyle = '#FFF1F4'; c.fill();
    for (let i = 0; i < 7; i++) { const sx = -4 * u + i * 1.35 * u, sy = -3.3 * u + (i % 2) * .8 * u; c.beginPath(); c.moveTo(sx, sy - .3 * u); c.quadraticCurveTo(sx + .35 * u, sy - .2 * u, sx, sy + .35 * u); c.quadraticCurveTo(sx - .35 * u, sy - .2 * u, sx, sy - .3 * u); c.fillStyle = '#E8445A'; c.fill(); c.fillStyle = '#5DB85A'; c.fillRect(sx - .15 * u, sy - .42 * u, .3 * u, .14 * u); }
    c.strokeStyle = '#E88AA6'; c.lineWidth = u * .18; c.beginPath(); for (let k = 0; k <= 12; k++) { const px = -5.3 * u + k * .88 * u; c.lineTo(px, -2 * u + (k % 2 ? -.25 * u : 0)); } c.stroke();
    c.strokeStyle = INK; c.lineWidth = Math.max(1, u * .17);
  }
  c.restore();
  c.beginPath(); c.roundRect(-5 * u, -8 * u, 10 * u, 6 * u, u * .75); c.stroke();
  // crossbody strap (噜噜)
  if (o.strap) {
    c.save(); c.strokeStyle = '#9ACB7A'; c.lineWidth = u * .45; c.beginPath();
    if (o.back) { c.moveTo(4.3 * u, -7.6 * u); c.lineTo(-4.4 * u, -2.9 * u); } else { c.moveTo(-4.3 * u, -7.6 * u); c.lineTo(3.8 * u, -2.9 * u); }
    c.stroke(); c.lineWidth = Math.max(1, u * .12); c.strokeStyle = INK; c.stroke();
    if (!o.back) { c.beginPath(); c.roundRect(3.1 * u, -3.4 * u, 1.9 * u, 1.6 * u, .5 * u); c.fillStyle = '#FFFFFF'; c.fill(); c.stroke(); c.beginPath(); c.arc(3.7 * u, -2.8 * u, .12 * u, 0, 7); c.arc(4.4 * u, -2.8 * u, .12 * u, 0, 7); c.fillStyle = INK; c.fill(); }
    c.restore();
  }
  if (!o.back) face(c, u, o, T);
  // hugging arms go in front
  if (o.hugging) { arm(-1, -1.2); arm(1, -1.2); }
  // hat and fruit
  if (o.bonnet) {
    c.save(); c.lineWidth = Math.max(1, u * .12);
    c.beginPath(); c.moveTo(-5.6 * u, -6.2 * u); c.quadraticCurveTo(-5.4 * u, -10.2 * u, 0, -10.3 * u); c.quadraticCurveTo(5.4 * u, -10.2 * u, 5.6 * u, -6.2 * u);
    c.quadraticCurveTo(0, -8.8 * u, -5.6 * u, -6.2 * u); c.fillStyle = '#FFFFFF'; c.fill(); c.stroke();
    for (let k = 0; k < 11; k++) { const a = Math.PI + k / 10 * Math.PI, fx = Math.cos(a) * 5.4 * u, fy = -7.6 * u + Math.sin(a) * 2.6 * u; c.beginPath(); c.arc(fx, fy, .75 * u, 0, 7); c.fillStyle = '#FFFFFF'; c.fill(); c.stroke(); }
    c.restore();
    tangerine(c, 0, -10.9 * u, 1.1 * u, true);
  } else if (o.fruit) tangerine(c, o.back ? -.5 * u : .5 * u, -8.9 * u, 1.05 * u, true);
  if (o.towel) { c.save(); c.translate(o.flip ? -1 : 1, 0); c.beginPath(); c.roundRect(-1.5 * u, -4.2 * u, 3 * u, 2.2 * u, .5 * u); c.fillStyle = '#FFFFFF'; c.fill(); c.stroke(); c.restore(); }
  c.restore();
}

function face(c, u, o, T) {
  const e = o.eyes || 'normal', blink = e === 'normal' && ((T * .9 + (o.seed || 0)) % 3.3) < .12;
  c.save(); c.lineWidth = Math.max(1.2, u * .28); c.strokeStyle = INK;
  for (const ex of [-3, 2]) {
    const X = ex * u + (o.lookX || 0) * u * .4, Y = -7 * u, cx = X + .5 * u;
    if ((e === 'normal' || e === 'teary' || e === 'wide') && !blink) {
      const w = e === 'wide' ? 1.25 : 1, h = e === 'teary' ? 1.9 : e === 'wide' ? 2.2 : 2;
      c.fillStyle = INK; c.beginPath(); c.roundRect(cx - .5 * w * u, Y + (2 - h) * u / 2, w * u, h * u, u * .2); c.fill();
      c.fillStyle = '#FFF5E2'; c.beginPath(); c.ellipse(cx - .12 * u, Y + .45 * u, u * (e === 'teary' ? .28 : .18), u * (e === 'teary' ? .36 : .26), 0, 0, 7); c.fill();
      if (e === 'teary') {
        c.beginPath(); c.ellipse(cx + .2 * u, Y + 1.4 * u, u * .12, u * .15, 0, 0, 7); c.fill();
        c.fillStyle = 'rgba(140,200,255,.8)'; c.beginPath(); c.ellipse(cx, Y + 1.95 * u, u * .62, u * .22, 0, 0, 7); c.fill();
      }
    } else if (blink) { c.beginPath(); c.moveTo(X - .2 * u, Y + 1.5 * u); c.lineTo(X + 1.2 * u, Y + 1.5 * u); c.stroke(); }
    else if (e === 'happy') { c.beginPath(); c.moveTo(X - .4 * u, Y + 1.6 * u); c.quadraticCurveTo(cx, Y + .2 * u, X + 1.4 * u, Y + 1.6 * u); c.stroke(); }
    else if (e === 'sad') { c.beginPath(); c.moveTo(X - .4 * u, Y + 1.1 * u); c.quadraticCurveTo(cx, Y + 1.9 * u, X + 1.4 * u, Y + 1.1 * u); c.stroke(); }
  }
  if (o.brows === 'sad') { c.lineWidth = u * .22; for (const [a, b] of [[-3.4, -2.1], [3.4, 2.1]]) { c.beginPath(); c.moveTo(a * u, -7.9 * u); c.lineTo(b * u + (a < 0 ? .5 : .5) * u, -8.5 * u); c.stroke(); } }
  if (o.brows === 'up') { c.lineWidth = u * .22; for (const a of [-3, 2]) { c.beginPath(); c.moveTo(a * u - .1 * u, -8.2 * u); c.quadraticCurveTo(a * u + .5 * u, -8.8 * u, a * u + 1.1 * u, -8.2 * u); c.stroke(); } }
  c.restore();
  // blush
  if (o.blush) { c.save(); c.globalAlpha = .55 * o.blush; for (const bx of [-3.7, 3.7]) { c.beginPath(); c.ellipse(bx * u, -4.9 * u, .85 * u, .42 * u, 0, 0, 7); c.fillStyle = '#FF6F91'; c.fill(); } c.restore(); }
  // mouth: shape by vowel, openness by the syllable envelope
  const k = o.mouth || 0, v = o.vowel || 'a', my = -4.4 * u;
  c.save(); c.strokeStyle = INK; c.lineWidth = Math.max(1, u * .2);
  if (k > .05) {
    const w = (v === 'u' || v === 'o' ? .55 : v === 'n' ? .5 : 1.1) * u, h = (v === 'n' ? .15 : v === 'i' ? .45 : 1.0) * u * k + .12 * u;
    c.beginPath(); c.ellipse(0, my + h * .3, w, h, 0, 0, 7); c.fillStyle = '#5A1F2E'; c.fill(); c.stroke();
    if (h > .5 * u) { c.beginPath(); c.ellipse(0, my + h * .75, w * .55, h * .3, 0, 0, 7); c.fillStyle = '#FF8FA3'; c.fill(); }
  } else if (o.smile) { c.beginPath(); c.moveTo(-1 * u, my - .1 * u); c.quadraticCurveTo(0, my + .9 * u * o.smile, 1 * u, my - .1 * u); c.stroke(); }
  else if (o.frown) { c.beginPath(); c.moveTo(-.7 * u, my + .3 * u); c.quadraticCurveTo(0, my - .35 * u, .7 * u, my + .3 * u); c.stroke(); }
  c.restore();
  // tear streams
  if (o.tears) {
    c.save(); c.globalAlpha = .75 * o.tears; c.fillStyle = 'rgba(140,200,255,.9)';
    for (const ex of [-2.5, 2.5]) { c.beginPath(); c.roundRect(ex * u - .18 * u, -5 * u, .36 * u, 2.4 * u * o.tears, .18 * u); c.fill(); }
    c.restore();
  }
}
