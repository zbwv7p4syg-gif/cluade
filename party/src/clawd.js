// clawd.js — Clawd, the Claude Code mascot, in flat style (10u × 6u body, four stubby legs,
// two slit eyes, stubby arms; proportions after JohnHeibel/PDoomVideo's clawd.js), now wearing DJ headphones.
// (x, y) is the ground point between the feet. Arm angle 0 = down-ish, larger = raised.

const CL = { ink: '#2B2233', clay: '#D97757', dk: '#A84D33', lt: '#F2A283', cream: '#FFF5E2', rose: '#E27A92' };

function clawd(c, x, y, u, o = {}, T = 0) {
  const dy = (o.dy || 0) * u, sq = o.sq || 0;
  c.save();
  c.translate(x, y + dy);
  if (o.rot) c.rotate(o.rot);
  c.scale((o.flip ? -1 : 1) * (1 + sq * .6), 1 - sq);
  c.lineJoin = 'round'; c.strokeStyle = CL.ink; c.lineWidth = Math.max(1, u * .17);
  const box = (bx, by, w, h, fill) => { c.beginPath(); c.roundRect(bx, by, w, h, Math.min(w, h) * .12); c.fillStyle = fill; c.fill(); c.stroke(); };
  if (o.legs !== false) [-4, -2, 1, 3].forEach((lx, i) => {
    const kick = o.kick ? Math.max(0, Math.sin((o.kick + (i % 2 ? .5 : 0)) * Math.PI * 2)) * .8 : 0;
    box(lx * u, -2.4 * u, u, (2.2 - kick) * u, CL.dk);
  });
  const arm = (side, a) => {
    c.save(); c.translate(side * 4.9 * u, -4.5 * u); c.rotate(side < 0 ? a : -a);
    box(side < 0 ? -2.2 * u : 0, -.5 * u, 2.2 * u, u, CL.clay); c.restore();
  };
  arm(-1, o.aL ?? .2); arm(1, o.aR ?? .2);
  box(-5 * u, -8 * u, 10 * u, 6 * u, CL.clay);
  c.save(); c.beginPath(); c.roundRect(-5 * u, -8 * u, 10 * u, 6 * u, u * .7); c.clip();
  c.globalAlpha = .45; c.beginPath(); c.ellipse(-1.6 * u, -6.5 * u, 3.4 * u, 1.3 * u, -.08, 0, Math.PI * 2); c.fillStyle = CL.lt; c.fill();
  c.globalAlpha = .35; c.fillStyle = CL.dk; c.fillRect(-5 * u, -3.7 * u, 10 * u, 1.8 * u);
  if (o.rim) { c.globalAlpha = .5 * o.rim.a; c.fillStyle = o.rim.color; c.fillRect(-5 * u, -8 * u, 10 * u, 1.1 * u); }
  c.restore();
  c.beginPath(); c.roundRect(-5 * u, -8 * u, 10 * u, 6 * u, u * .72); c.stroke();
  // eyes
  const e = o.eyes || 'normal', blink = e === 'normal' && ((T * .9 + (o.seed || 0)) % 3.3) < .12;
  c.save(); c.lineWidth = Math.max(1.2, u * .3); c.lineCap = 'round';
  for (const ex of [-3, 2]) {
    const X = ex * u, Y = -7 * u, cx = X + .5 * u;
    if (e === 'normal' && !blink) { c.fillStyle = CL.ink; c.beginPath(); c.roundRect(X, Y, u, 2 * u, u * .12); c.fill(); c.beginPath(); c.ellipse(X + .32 * u, Y + .42 * u, u * .17, u * .25, 0, 0, Math.PI * 2); c.fillStyle = CL.cream; c.fill(); }
    else if (e === 'normal' && blink) { c.beginPath(); c.moveTo(X - .2 * u, Y + 1.5 * u); c.lineTo(X + 1.2 * u, Y + 1.5 * u); c.stroke(); }
    else if (e === 'happy') { c.beginPath(); c.moveTo(X - .4 * u, Y + 1.7 * u); c.lineTo(cx, Y + .5 * u); c.lineTo(X + 1.4 * u, Y + 1.7 * u); c.stroke(); }
    else if (e === 'closed') { c.beginPath(); c.moveTo(X - .4 * u, Y + 1.2 * u); c.quadraticCurveTo(cx, Y + 2 * u, X + 1.4 * u, Y + 1.2 * u); c.stroke(); }
    else if (e === 'x') { c.beginPath(); c.moveTo(X - .3 * u, Y + .2 * u); c.lineTo(X + 1.3 * u, Y + 1.8 * u); c.moveTo(X + 1.3 * u, Y + .2 * u); c.lineTo(X - .3 * u, Y + 1.8 * u); c.stroke(); }
    else if (e === 'shades') { /* drawn below as one bar */ }
    else if (e === 'star') {
      c.beginPath(); for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4 - Math.PI / 2, r = i % 2 ? u * .45 : u * 1.25; c.lineTo(cx + Math.cos(a) * r, Y + u + Math.sin(a) * r); }
      c.closePath(); c.fillStyle = '#FFE08A'; c.fill(); c.lineWidth = u * .12; c.stroke();
    }
  }
  if (e === 'shades') {
    c.fillStyle = CL.ink; c.beginPath(); c.roundRect(-4.6 * u, -7.5 * u, 9.2 * u, 2.2 * u, .6 * u); c.fill();
    c.strokeStyle = o.shadeColor || '#8ff'; c.lineWidth = u * .18; c.beginPath(); c.moveTo(-3.9 * u, -7 * u); c.lineTo(-2.4 * u, -7.1 * u); c.stroke();
  }
  c.restore();
  if (o.mouth === 'open') { c.beginPath(); c.moveTo(-1.2 * u, -4.8 * u); c.lineTo(1.2 * u, -4.8 * u); c.quadraticCurveTo(0, -3.0 * u, -1.2 * u, -4.8 * u); c.fillStyle = '#4A1F2A'; c.fill(); c.stroke(); }
  // DJ headphones
  if (o.phones !== false) {
    c.save(); c.lineWidth = u * .55; c.strokeStyle = '#1b1b24'; c.beginPath(); c.arc(0, -7.6 * u, 5.4 * u, Math.PI * 1.08, Math.PI * 1.92); c.stroke();
    c.lineWidth = Math.max(1, u * .17); c.strokeStyle = CL.ink;
    for (const s of [-1, 1]) { c.beginPath(); c.roundRect(s * 5.2 * u - 0.9 * u, -7.4 * u, 1.8 * u, 2.6 * u, .6 * u); c.fillStyle = '#23232e'; c.fill(); c.stroke();
      c.beginPath(); c.roundRect(s * 5.2 * u - 0.5 * u, -6.9 * u, 1 * u, 1.6 * u, .4 * u); c.fillStyle = o.cupColor || '#D97757'; c.fill(); }
    c.restore();
  }
  c.restore();
}
