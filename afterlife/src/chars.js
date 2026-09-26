// chars.js — the cast, all cut from paper: the Claude spark, the girl, grandma's photo,
// the notebook page and the paper plane.

const INK = '#2B2233', SPARK = '#DE6F52', BLUSH = '#F09A8C';

// ---------------------------------------------------------------- the spark
// o.eyes: 'closed' (happy arcs) | 'open' | 'sleep' | 'wide'; o.mouth: 'smile' | 'o' | 'flat';
// o.hands: [[x,y],[x,y]] in local units (R = 1) — two rays reach out to hold things
function spark(x, y, R, t, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(o.rot || 0);
  const n = 11, rays = [], wig = o.wiggle ?? 1;
  for (let i = 0; i < n; i++) {
    let a = -Math.PI / 2 + i / n * TAU + (H(i * 4.1) - .5) * .25 + Math.sin(t * 2.4 + i * 1.7) * .04 * wig;
    let L = R * (.74 + H(i * 9.3) * .3) * (1 + Math.sin(t * 3 + i) * .03 * wig), w = R * (.16 + H(i * 2.2) * .04);
    rays.push([capsule(0, 0, Math.cos(a) * L, Math.sin(a) * L, w * 1.1, w), SPARK]);
  }
  (o.hands || []).forEach(([hx, hy]) => rays.push([capsule(0, R * .1, hx * R, hy * R, R * .15, R * .13), SPARK]));
  rays.push([ell(0, 0, R * .5, R * .46), SPARK]);
  cutGroup(rays, { edge: Math.max(3, R * .035), seed: o.seed ?? 900 });
  // face
  const fy = R * .02, ex = R * .17, er = R * .08, lw = Math.max(2.5, R * .034), eyes = o.eyes || 'closed';
  for (const s of [-1, 1]) {
    if (eyes === 'closed') line(arcPts(s * ex, fy, er, Math.PI * 1.15, Math.PI * 1.85, 6), INK, lw);
    else if (eyes === 'sleep') line(arcPts(s * ex, fy - er * .6, er, Math.PI * .15, Math.PI * .85, 6), INK, lw);
    else if (eyes === 'wide') { dot(s * ex, fy, er * .75, INK); dot(s * ex + er * .25, fy - er * .3, er * .22, '#fff'); }
    else dot(s * ex, fy, er * .5, INK);
    ctx.globalAlpha = .8; dot(s * R * .3, fy + R * .12, R * .07, BLUSH); ctx.globalAlpha = 1;
  }
  const m = o.mouth || 'smile';
  if (m === 'smile') line(arcPts(0, fy + R * .1, R * .065, Math.PI * .15, Math.PI * .85, 6), INK, lw);
  else if (m === 'o') dot(0, fy + R * .15, R * .045, INK);
  else line([[-R * .04, fy + R * .12], [R * .04, fy + R * .12]], INK, lw);
  ctx.restore();
}

// ---------------------------------------------------------------- the girl
// head centre at (x, y), s = scale (head radius 100·s). o.eyes: 'open' | 'closed' | 'down' | 'up' | 'shut'
// o.mouth: 'smile' | 'o' | 'flat' | 'sad'; o.arms(list) drawn by the caller for flexibility
function girlBody(x, y, s) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
  cut([[-95, 150], [95, 150], [140, 330], [-140, 330]], '#2C9A88', { seed: 11, edge: 6 });
  cut([[-60, 108], [0, 150], [-10, 185], [-75, 150]], '#FBF6EA', { seed: 12, edge: 0 });
  cut([[60, 108], [0, 150], [10, 185], [75, 150]], '#FBF6EA', { seed: 13, edge: 0 });
  cut(rect(-26, 88, 52, 50), '#E7B08A', { seed: 14, edge: 0 });
  ctx.restore();
}
function girlHead(x, y, s, t, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(o.tilt || 0);
  const lx = o.look?.[0] || 0, ly = o.look?.[1] || 0;
  cut(rrect(-112, -112, 224, 225, 70), '#261F2E', { seed: 20 });          // bob
  cut(ell(0, 12, 80, 88), '#EDB68E', { seed: 21, edge: 0 });                // face
  cut([[-104, -40], [-96, -92], [-40, -118], [40, -118], [96, -92], [104, -40], [60, -52], [20, -34], [-10, -58], [-60, -40]], '#261F2E', { seed: 22, edge: 0 }); // bangs
  cut(xform(rect(-30, -9, 60, 18), 62, -70, 1, -.5), '#F2C230', { seed: 23, edge: 3 });  // hair clip
  const eyes = o.eyes || 'open', ey = 14 + ly * 10;
  for (const sx of [-1, 1]) {
    const ex = sx * 34 + lx * 12;
    if (eyes === 'open' || eyes === 'up' || eyes === 'down') dot(ex, ey + (eyes === 'up' ? -6 : eyes === 'down' ? 6 : 0), 7.5, INK);
    else if (eyes === 'closed') line(arcPts(ex, ey + 2, 11, Math.PI * 1.1, Math.PI * 1.9, 6), INK, 5);
    else line(arcPts(ex, ey - 4, 11, Math.PI * .1, Math.PI * .9, 6), INK, 5);
    if (o.tear && sx === 1) { const k = o.tear; ctx.globalAlpha = clamp(k * 3) * (1 - clamp((k - .85) * 6)); dot(ex + 4, ey + 16 + k * 44, 6, '#8FC8F2'); ctx.globalAlpha = 1; }
    ctx.globalAlpha = .85; dot(sx * 52 + lx * 8, 46 + ly * 6, 15, '#F0877E'); ctx.globalAlpha = 1;
  }
  const m = o.mouth || 'smile', my = 60 + ly * 8, mx = lx * 10;
  if (m === 'smile') line(arcPts(mx, my - 8, 13, Math.PI * .2, Math.PI * .8, 6), INK, 5);
  else if (m === 'o') { dot(mx, my, 9, '#9B3A3A'); }
  else if (m === 'sad') line(arcPts(mx, my + 8, 11, Math.PI * 1.2, Math.PI * 1.8, 6), INK, 5);
  else line([[mx - 10, my], [mx + 10, my]], INK, 5);
  ctx.restore();
}
// an arm from shoulder (sx, sy) to hand (hx, hy), sleeve teal, hand skin
function arm(sx, sy, hx, hy, s, seed = 30) {
  cut(capsule(sx, sy, hx, hy, 34 * s, 28 * s), '#2C9A88', { seed, edge: 5 * s });
  cut(ell(hx, hy, 30 * s, 28 * s), '#EDB68E', { seed: seed + 1, edge: 4 * s });
}

// ---------------------------------------------------------------- grandma's photo
function photo(x, y, s, rot = 0) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  cut(rect(-80, -100, 160, 200), '#A8743F', { seed: 40 });
  cut(rect(-64, -84, 128, 168), '#F4E6C8', { seed: 41, edge: 0 });
  cut(ell(0, -58, 26, 20), '#C9C4CC', { seed: 42, edge: 0 });                   // bun
  cut(ell(0, -12, 44, 42), '#C9C4CC', { seed: 43, edge: 0 });                   // hair
  cut(ell(0, 4, 36, 38), '#EDB68E', { seed: 44, edge: 0 });                     // face
  cut([[-42, 84], [-48, 50], [-20, 38], [20, 38], [48, 50], [42, 84]], '#B04A5A', { seed: 45, edge: 0 });
  for (const sx of [-1, 1]) { line(ell(sx * 15, 0, 10, 9, 0, 14), INK, 3, { close: true }); line(arcPts(sx * 15, 2, 5, Math.PI * 1.1, Math.PI * 1.9, 4), INK, 3); ctx.globalAlpha = .8; dot(sx * 24, 16, 6, '#F0877E'); ctx.globalAlpha = 1; }
  line([[-5, 0], [5, 0]], INK, 2.5); line(arcPts(0, 16, 9, Math.PI * .2, Math.PI * .8, 5), INK, 3);
  ctx.restore();
}

// ---------------------------------------------------------------- paper plane (side view), nose at +x
function planeShape() { return [[70, 0], [-50, -30], [-34, 2], [-56, 22]]; }
function plane(x, y, s, rot, seed = 60) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  cut([[70, 0], [-50, -30], [-34, 2]], '#FBF8F0', { seed, edge: 3, tex: .4 });
  cut([[70, 0], [-34, 2], [-56, 22]], '#DCD6CB', { seed: seed + 1, edge: 3, tex: .4 });
  line([[70, 0], [-34, 2]], '#B8B0A2', 2);
  ctx.restore();
}
function trail(pts, color = 'rgba(251,246,234,.8)') {
  ctx.save(); ctx.setLineDash([14, 14]); ctx.strokeStyle = color; ctx.lineWidth = 4; ctx.lineCap = 'round';
  ctx.beginPath(); pts.forEach(([x, y], i) => i ? ctx.lineTo(x, y) : ctx.moveTo(x, y)); ctx.stroke(); ctx.restore();
}

// ---------------------------------------------------------------- a lined note (w × h centred at 0,0)
function notePage(w, h, seed = 70, o = {}) {
  cut(rect(-w / 2, -h / 2, w, h), '#FBF7EC', { seed, edge: o.edge ?? 6, tex: .25 });
  ctx.save(); ctx.globalAlpha = .55;
  for (let y = -h / 2 + h * .22; y < h / 2 - 8; y += h * .13) line([[-w / 2 + 6, y], [w / 2 - 6, y]], '#8DB3DA', Math.max(1.5, w / 260), { seed: y, j: .6 });
  line([[-w / 2 + w * .12, -h / 2 + 4], [-w / 2 + w * .12, h / 2 - 4]], '#E28B8B', Math.max(1.5, w / 240), { seed: 3, j: .6 });
  ctx.restore();
}
