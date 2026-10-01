// visuals.js — the film, shot by shot. Everything is drawn from the time t and SCORE, so any
// frame can be rendered on its own (and the render is identical every time).

const beatPulse = t => Math.exp(-((t % BEAT + BEAT) % BEAT) * 7);
function cam(cx, cy, z) { ctx.setTransform(z, 0, 0, z, VW / 2 - cx * z, VH / 2 - cy * z); }
function inked(who, t) { let n = 0; for (const e of SCORE.pencil) if (e.who === who) n += clamp((t - e.t) / e.dur); return n; }
function bg(color) { ctx.fillStyle = color; ctx.fillRect(-400, -400, VW + 800, VH + 800); }

// ---------------------------------------------------------------- night sky + town
function nightSky(t, o = {}) {
  bg('#232B66');
  const bands = [[120, '#27306F'], [330, '#2C357B'], [560, '#262E6C'], [760, '#2E387F']];
  bands.forEach(([y, col], i) => {
    const p = [[-300, y + 30]];
    for (let x = -300; x <= VW + 300; x += 110) p.push([x, y + Math.sin(x * .004 + i * 2) * 26 + (H(x + i) - .5) * 14]);
    p.push([VW + 300, VH + 400], [-300, VH + 400]);
    cut(p, col, { edge: 3.5, seed: 200 + i * 10, tex: .18, jag: 5 });
  });
  for (let i = 0; i < 46; i++) {
    const x = H(i * 3.1) * VW * 1.2 - VW * .1, y = H(i * 5.7) * 820, tw = .6 + .4 * Math.sin(t * 3 + i * 2.3);
    ctx.globalAlpha = tw;
    if (i % 3 === 0) cut(star(x, y, 13, 6, 5, H(i) * 2), '#F5D66B', { edge: 0, seed: 300 + i, tex: 0 });
    else if (i % 3 === 1) { line([[x - 9, y], [x + 9, y]], '#F3EEDD', 3, { seed: i }); line([[x, y - 9], [x, y + 9]], '#F3EEDD', 3, { seed: i + 1 }); }
    else dot(x, y, 3, '#F5D66B');
    ctx.globalAlpha = 1;
  }
  if (o.moon !== false) { const [mx, my] = o.moon || [1660, 150]; cut(ell(mx, my, 62, 62), '#F3E2A6', { seed: 350, edge: 4 }); cut(ell(mx + 30, my - 18, 56, 56), '#27306F', { seed: 351, edge: 0, tex: .3 }); }
}
const HOUSES = [
  { x: 880, w: 150, h: 300 }, { x: 1020, w: 120, h: 400, tower: 1 }, { x: 1130, w: 190, h: 260 }, { x: 1310, w: 130, h: 360 },
  { x: 1430, w: 170, h: 280, cat: 1 }, { x: 1590, w: 120, h: 420, tower: 1 }, { x: 1700, w: 200, h: 300 }, { x: 1890, w: 160, h: 360 },
];
function town(t) {
  HOUSES.forEach((h, i) => {
    const y0 = VH + 40 - h.h, col = i % 2 ? '#283170' : '#1F2759';
    const roofH = h.tower ? 110 : 80;
    cutGroup([[rect(h.x, y0, h.w, h.h + 60), col], [[[h.x - 14, y0 + 4], [h.x + h.w / 2, y0 - roofH], [h.x + h.w + 14, y0 + 4]], '#1A1F4C']], { edge: 4, seed: 400 + i * 10, tex: .25 });
    for (let r = 0; r < 4; r++) for (let c = 0; c < Math.floor(h.w / 55); c++) {
      if (H(i * 31 + r * 7 + c) < .35) continue;
      const lit = .75 + .25 * Math.sin(t * 1.5 + i + r * 2 + c);
      ctx.globalAlpha = lit; cut(rect(h.x + 22 + c * 55, y0 + 40 + r * 70, 26, 30), '#F6C85A', { edge: 0, seed: 450 + i * 20 + r * 4 + c, tex: .3 }); ctx.globalAlpha = 1;
    }
    if (h.cat) {
      const cx = h.x + h.w * .7, cy = y0 - 22;
      cutGroup([[ell(cx, cy, 24, 22), '#15183A'], [ell(cx + 4, cy - 30, 17, 16), '#15183A'], [[[cx - 8, cy - 40], [cx - 4, cy - 56], [cx + 4, cy - 42]], '#15183A'], [[[cx + 6, cy - 42], [cx + 14, cy - 56], [cx + 18, cy - 38]], '#15183A'],
        [capsule(cx + 20, cy + 10, cx + 46 + Math.sin(t * 2) * 6, cy - 12, 4), '#15183A']], { edge: 2.5, seed: 480 });
    }
  });
}
// the girl's house, left of the town; the window shows windowScene() shrunk down
const WIN = { x: 180, y: 520, w: 470, h: 302 };
function houseWorld(t, win) {
  nightSky(t);
  town(t);
  cutGroup([[rect(-60, 380, 960, 800), '#4B3B8C'], [xform(rect(-40, -26, 1000, 52), 440, 380, 1, -.015), '#2A2560']], { edge: 6, seed: 500, tex: .25 });
  ctx.save(); ctx.globalAlpha = .18;
  for (let r = 0; r < 12; r++) for (let k = 0; k < 7; k++) { const x = 20 + k * 120 + (r % 2) * 40, y = 440 + r * 52; line([[x, y], [x + 18, y - 6], [x + 32, y + 3], [x + 50, y - 5], [x + 70, y + 2]], '#D8CFF2', 3, { seed: r * 9 + k }); }
  ctx.restore();
  for (let i = 0; i < 9; i++) { const y = 450 + i * 70, x = 60 + Math.sin(i * 1.3) * 16; cut(ell(x + (i % 2 ? 22 : -22), y, 16, 11, i % 2 ? .6 : -.6), '#6EAF6A', { seed: 520 + i, edge: 3 }); }
  line(Array.from({ length: 12 }, (_, i) => [60 + Math.sin(i * .9) * 16, 420 + i * 60]), '#4E8A4E', 5, { seed: 530 });
  cut(rect(WIN.x - 26, WIN.y - 26, WIN.w + 52, WIN.h + 52), '#F4E9CF', { seed: 540, edge: 5 });
  ctx.save(); ctx.beginPath(); ctx.rect(WIN.x, WIN.y, WIN.w, WIN.h); ctx.clip();
  ctx.translate(WIN.x, WIN.y); ctx.scale(WIN.w / 1400, WIN.w / 1400); ctx.translate(-260, -60);
  windowScene(t, win);
  ctx.restore();
  cut(rect(WIN.x - 40, WIN.y + WIN.h, WIN.w + 80, 30), '#35296E', { seed: 545, edge: 5 });
}

// ---------------------------------------------------------------- inside the window (1920 × 1080 space)
function windowScene(t, o = {}) {
  bg('#4B3B8C');
  cut(rect(260, 60, 1400, 900), '#F5C443', { seed: 600, edge: 0, tex: .25 });
  const glow = ctx.createRadialGradient(960, 480, 50, 960, 480, 700); glow.addColorStop(0, 'rgba(255,240,190,.55)'); glow.addColorStop(1, 'rgba(255,240,190,0)');
  ctx.fillStyle = glow; ctx.fillRect(260, 60, 1400, 900);
  if (o.rays) { ctx.globalAlpha = o.rays; dashes(960, 470, 230, 290, 9, '#FFF2B8', 8, -Math.PI * .95 / 1, { jit: .2 }); ctx.globalAlpha = 1; }
  // a doodle of the spark pinned on the wall
  ctx.save(); ctx.translate(1370, 240); ctx.rotate(.06); notePage(170, 190, 610, { edge: 4 }); ctx.restore();
  spark(1370, 240, 60, t, { seed: 611, wiggle: .3 });
  // plant
  cut([[1400, 780], [1500, 780], [1485, 890], [1415, 890]], '#C4683F', { seed: 620, edge: 5 });
  line([[1450, 780], [1446, 700], [1452, 640]], '#3C8A45', 7, { seed: 621 });
  cut(ell(1418, 720, 26, 12, -.5), '#4FA35A', { seed: 622, edge: 3 }); cut(ell(1484, 700, 26, 12, .5), '#4FA35A', { seed: 623, edge: 3 });
  cut(star(1452, 630, 30, 16, 6, 0), '#E2463F', { seed: 624, edge: 4 }); dot(1452, 630, 8, '#F2C230');
  // curtains
  cut([[260, 60], [520, 60], [430, 260], [400, 600], [470, 960], [260, 960]], '#EC8FAA', { seed: 630, edge: 5 });
  cut([[1660, 60], [1400, 60], [1490, 260], [1520, 600], [1450, 960], [1660, 960]], '#EC8FAA', { seed: 631, edge: 5 });
  // the girl
  const gy = 510 + (o.bob || 0);
  girlBody(960, gy, 1.4);
  if (o.behind) o.behind();
  girlHead(960, gy, 1.4, t, o.girl || {});
  cut(rect(200, 900, 1520, 200), '#3E2F78', { seed: 640, edge: 6 });
  if (o.front) o.front();
  // frame
  ctx.save(); ctx.beginPath(); ctx.rect(-500, -500, 3000, 2200); ctx.rect(260, 60, 1400, 900); ctx.clip('evenodd');
  cut(rect(230, 30, 1460, 960), '#F4E9CF', { seed: 650, edge: 0, tex: .3 }); ctx.restore();
}

// ---------------------------------------------------------------- shots
const SHOT = {};

SHOT.town = (t, lt, d) => {
  const k = eio(seg(lt, .6, d));
  cam(lerp(960, 560, k), lerp(540, 640, k), lerp(1, 1.45, k));
  houseWorld(t, { girl: { eyes: 'down', mouth: 'flat' }, front: () => photo(960, 830, 1.3, .03) });
  spark(1340, 210, 140, t, { eyes: 'closed', seed: 700 });
};

SHOT.photo = (t, lt, d) => {
  const z = lerp(1.0, 1.12, eio(lt / d)); cam(960, 520, z);
  const up = eio(seg(lt, 2.5, 3.1)), tear = seg(lt, .9, 2.3);
  windowScene(t, {
    girl: up < .5 ? { eyes: 'down', mouth: 'sad', tear, look: [0, .35] } : { eyes: 'up', mouth: 'o', look: [.25, -.6], tilt: -.05 },
    rays: up * .9,
    front: () => {
      const py = lerp(830, 870, up);
      photo(960, py, 1.3, .03 + Math.sin(t * 2) * .01);
      cut(ell(862, py + 30, 32, 30), '#EDB68E', { seed: 660, edge: 4 }); cut(ell(1058, py + 30, 32, 30), '#EDB68E', { seed: 661, edge: 4 });
    },
  });
  // a question mark pops up as she looks at the sky
  const q = back(seg(lt, 3.1, 3.45));
  if (q > 0) {
    ctx.save(); ctx.translate(680, 250); ctx.scale(q, q); ctx.rotate(-.1 + Math.sin(t * 3) * .05);
    cut(ell(0, 0, 90, 85), '#FBF7EC', { seed: 670, edge: 5 }); cut(ell(80, 90, 16, 16), '#FBF7EC', { seed: 671, edge: 4 }); cut(ell(112, 126, 9, 9), '#FBF7EC', { seed: 672, edge: 3 });
    ctx.font = `130px ${FONT}`; ctx.fillStyle = '#2B4EA2'; ctx.textAlign = 'center'; ctx.fillText('？', 0, 45); ctx.textAlign = 'left';
    ctx.restore();
  }
};

function desk(t) {
  bg('#B7804A');
  const g = ctx.createRadialGradient(960, 520, 100, 960, 520, 820); g.addColorStop(0, 'rgba(255,220,150,.55)'); g.addColorStop(1, 'rgba(255,220,150,0)');
  ctx.fillStyle = g; ctx.fillRect(-400, -400, VW + 800, VH + 800);
  cut(ell(960, 520, 760, 520), '#C99058', { seed: 800, edge: 0, tex: .25 });
  // pencils lying around
  cut(capsule(160, 940, 420, 880, 12), '#E24B4B', { seed: 801, edge: 4 }); cut(capsule(1540, 120, 1800, 170, 12), '#F2C230', { seed: 802, edge: 4 });
}
function notebook(w, h, seed = 810) {
  cut(rect(-w / 2 - 40, -h / 2 - 30, w + 80, h + 70), '#5A3B8E', { seed, edge: 6 });
  notePage(w, h, seed + 1);
  for (let i = 0; i < 16; i++) { const x = -w / 2 + 50 + i * (w - 100) / 15; line(arcPts(x, -h / 2 - 2, 14, Math.PI * .9, Math.PI * 2.1, 8), '#3A3048', 5, { seed: seed + 10 + i }); }
}
SHOT.write = (t, lt, d) => {
  const shown = inked('girl', t), lift = eio(seg(lt, 4.25, 4.8));
  desk(t);
  const W = 1300, HH = 760, rot = -.03 - lift * .03, sc = 1 + lift * .08;
  // page transform so we can find the pen on screen
  const L1 = [...QUESTION].slice(0, 4).join(''), L2 = [...QUESTION].slice(4).join('');
  let penLocal = null;
  const camX = 960 + clamp(shown - 1, 0, 8) * 6;
  cam(camX, 540 - lift * 20, 1.04 + seg(lt, 0, 4) * .06);
  ctx.save(); ctx.translate(960, 560); ctx.rotate(rot); ctx.scale(sc, sc);
  notebook(W, HH);
  const r1 = hand(L1, -480, -70, 190, '#2B4EA2', Math.min(shown, 4), { seed: 1 });
  const r2 = hand(L2, -480, 190, 190, '#2B4EA2', shown - 4, { seed: 2 });
  penLocal = r2.pen || r1.pen;
  if (!penLocal) { // between characters: hover towards the next one
    const i = Math.floor(shown + 1e-6);
    penLocal = i < 4 ? [r1.end + 10, -110] : i < 9 ? [(shown >= 4 ? r2.end : -480) + 10, 150] : [r2.end + 40, 150 - 80 * lift];
  }
  const [px, py] = penLocal, hop = shown % 1 === 0 ? Math.sin(t * 20) * 4 : 0;
  // pen and arm (the arm comes from the lower right)
  ctx.rotate(-rot);
  const ax = px + 40, ay = py + 60 + hop;
  cut(capsule(ax + 700, ay + 700, ax + 30, ay + 40, 70, 58), '#2C9A88', { seed: 830, edge: 7 });
  cut(capsule(px, py + hop, px + 130, py - 120 + hop, 10, 12), '#2F5BB8', { seed: 831, edge: 4 });
  cut(ell(ax + 20, ay + 20, 56, 50), '#EDB68E', { seed: 832, edge: 5 });
  ctx.restore();
};

// fold keyframes (6 points each): sheet -> corners folded -> narrow -> plane from above
const FOLD = [
  [[-260, -350], [0, -350], [260, -350], [260, 350], [0, 350], [-260, 350]],
  [[-260, -90], [0, -350], [260, -90], [260, 350], [0, 350], [-260, 350]],
  [[-130, 40], [0, -350], [130, 40], [110, 350], [0, 350], [-110, 350]],
  [[-300, 260], [0, -400], [300, 260], [40, 300], [0, 340], [-40, 300]],
];
function foldShape(k) { const i = Math.min(2, Math.floor(k)), u = eio(k - i); return FOLD[i].map((p, j) => [lerp(p[0], FOLD[i + 1][j][0], u), lerp(p[1], FOLD[i + 1][j][1], u)]); }
SHOT.fold = (t, lt, d) => {
  desk(t); cam(960, 540, 1.05);
  const k = eio(seg(lt, .3, .6)) + eio(seg(lt, .9, 1.2)) + eio(seg(lt, 1.5, 1.8)), rise = eio(seg(lt, 1.85, 2.4));
  const pts = foldShape(k);
  ctx.save(); ctx.translate(960, 540 - rise * 30); ctx.scale(1 + rise * .15, 1 + rise * .15); ctx.rotate(Math.sin(lt * 3) * .02);
  if (k >= 2.5) { ctx.globalAlpha = rise; dashes(0, 0, 420, 500, 12, '#FFE7A8', 9, 0, { jit: .15 }); ctx.globalAlpha = 1; }
  cut(pts, '#FBF7EC', { seed: 850, edge: 6, tex: .25 });
  if (k < 1) {
    ctx.save(); ctx.globalAlpha = 1 - k; trace(pts); ctx.clip();
    hand('人死后，', -210, -150, 110, '#2B4EA2', 9, { seed: 1 }); hand('会去哪里？', -210, 0, 110, '#2B4EA2', 9, { seed: 2 });
    ctx.restore();
  }
  if (k > .3 && k < 2) { // the folded flaps
    const fk = clamp(k), p = pts;
    ctx.globalAlpha = clamp(fk * 2);
    cut([[p[0][0], p[0][1]], [p[1][0], p[1][1]], [0, p[0][1] + 60 * fk]], '#E9E2D2', { seed: 851, edge: 2 });
    cut([[p[2][0], p[2][1]], [p[1][0], p[1][1]], [0, p[2][1] + 60 * fk]], '#E9E2D2', { seed: 852, edge: 2 });
    ctx.globalAlpha = 1;
  }
  line([[pts[1][0], pts[1][1] + 10], [pts[4][0], pts[4][1] - 10]], '#C9C0AE', 3, { seed: 853 });
  // hands on the sides
  const ly = lerp(0, 200, clamp(k - 1.5)) - rise * 60;
  cut(capsule(-700, 700, pts[0][0] - 30, ly + 60, 70, 58), '#2C9A88', { seed: 854, edge: 7 }); cut(ell(pts[0][0] - 20, ly + 40, 54, 48), '#EDB68E', { seed: 855, edge: 5 });
  cut(capsule(700, 700, pts[2][0] + 30, ly + 60, 70, 58), '#2C9A88', { seed: 856, edge: 7 }); cut(ell(pts[2][0] + 20, ly + 40, 54, 48), '#EDB68E', { seed: 857, edge: 5 });
  ctx.restore();
};

SHOT.throw = (t, lt, d) => {
  cam(960, 540, 1.02);
  const rel = 1.08, wind = eio(seg(lt, .2, .9)), fly = seg(lt, rel, rel + .8), swing = eout(seg(lt, rel - .12, rel + .15));
  const sh = [1100, 745];
  const hx = lerp(lerp(1190, 1240, wind), 1330, swing), hy = lerp(lerp(560, 600, wind), 330, swing);
  let px = hx + 10, py = hy - 40, prot = -.5;
  if (fly > 0) { const u = eout(fly); px = lerp(hx + 10, 1900, u); py = lerp(hy - 40, -120, u) + Math.sin(u * 4) * 30; prot = -.55; }
  windowScene(t, {
    girl: lt < rel ? { eyes: 'up', mouth: 'smile', look: [.4, -.4] } : { eyes: 'up', mouth: 'o', look: [.6, -.8], tilt: -.08 },
    front: () => {
      cut(ell(862, 880, 32, 30), '#EDB68E', { seed: 662, edge: 4 });
      arm(sh[0], sh[1], hx, hy, 1.4, 663);
      if (fly > 0) trail([[hx, hy - 40], [lerp(hx, px, .5), lerp(hy, py, .5) + 20], [px - 40, py + 10]]);
      if (fly < 1) plane(px, py, 1.4 * (1 - fly * .5), prot, 664);
    },
  });
};

SHOT.fly = (t, lt, d) => {
  const u = eio(lt / d);
  cam(lerp(860, 1100, u), 540, 1.0);
  nightSky(t); town(t);
  spark(1560, 220, 150, t, { eyes: 'closed', seed: 700 });
  // a loop-the-loop on the way
  const path = s => { const x = lerp(-150, 1440, s), y = lerp(860, 300, s) - Math.sin(s * Math.PI) * 180; const lp = seg(s, .45, .65); return [x + Math.sin(lp * TAU) * 110 - lp * 0, y - (1 - Math.cos(lp * TAU)) * 110]; };
  const pts = []; for (let s = 0; s <= u; s += .01) pts.push(path(s));
  if (pts.length > 1) trail(pts);
  const [x, y] = path(u), [x2, y2] = path(Math.min(1, u + .01));
  plane(x, y, 1.1, Math.atan2(y2 - y, x2 - x), 664);
};

function heldNote(x, y, w, h, rot, t, o = {}) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot);
  notePage(w, h, 870);
  if (o.q) { hand('人死后，', -w * .36, -h * .05, w * .15, '#2B4EA2', 9, { seed: 1 }); hand('会去哪里？', -w * .36, h * .3, w * .15, '#2B4EA2', 9, { seed: 2 }); }
  ctx.restore();
}
SHOT.catch = (t, lt, d) => {
  const z = lerp(1, 1.08, eio(lt / d)); cam(960, 520, z);
  nightSky(t, { moon: [1700, 120] });
  const cT = 1.2, open = eio(seg(lt, 1.35, 1.9)), bang = SCORE.ding[0].t - SHOTS.find(s => s.name === 'catch').t0;
  // thinking dots on beats before the "!"
  const thinking = lt > 2.4 && lt < bang;
  const eyes = lt < cT ? 'open' : lt < cT + .5 ? 'wide' : lt < 2.4 ? 'open' : thinking ? 'sleep' : 'wide';
  const R = 330, sy = 470 + (lt > bang ? -30 * Math.exp(-(lt - bang) * 6) * Math.sin((lt - bang) * 30) : 0);
  const hands = open > 0 ? [[-.6, 1.05], [.6, 1.05]] : [];
  spark(960, sy, R, t, { eyes, mouth: lt < cT ? 'smile' : lt < 2.4 ? 'o' : thinking ? 'flat' : 'o', hands, seed: 710 });
  if (open > 0) {
    const w = lerp(160, 470, open), h = lerp(100, 360, open);
    heldNote(960, sy + R * .95, w, h, -.03, t, { q: open > .6 });
    for (const s of [-1, 1]) cut(ell(960 + s * R * .62, sy + R * 1.02, R * .15, R * .14), SPARK, { seed: 715 + s, edge: 5 });
  } else {
    const u = eout(seg(lt, 0, cT)), px = lerp(-100, 960, u), py = lerp(900, sy + R * .9, u) - Math.sin(u * Math.PI) * 200;
    trail([[lerp(-100, px, .3), lerp(900, py, .3) - 120], [px - 60, py + 10]]);
    plane(px, py, 1.3 * (1 - u * .2), -.3 + u * .3, 664);
    if (lt > cT) { ctx.globalAlpha = 1 - seg(lt, cT, cT + .3); dashes(960, sy + R * .9, 60, 130, 10, '#FBF6EA', 6); ctx.globalAlpha = 1; }
  }
  if (thinking) for (let i = 0; i < 3; i++) { const on = seg(lt, 2.4 + i * .5, 2.5 + i * .5); if (on > 0) cut(ell(1300 + i * 50, 200 - i * 60, (14 + i * 6) * back(on)), '#DE6F52', { seed: 720 + i, edge: 4 }); }
  if (lt >= bang) {
    const s = back(seg(lt, bang, bang + .25));
    ctx.save(); ctx.translate(1320, 170); ctx.scale(s, s); ctx.rotate(.15);
    cut(capsule(0, -90, 0, 20, 26, 16), SPARK, { seed: 730, edge: 5 }); cut(ell(0, 70, 22, 22), SPARK, { seed: 731, edge: 5 });
    ctx.restore();
    ctx.globalAlpha = 1 - seg(lt, bang, bang + .5); dashes(960, sy, R * 1.15, R * 1.4, 14, '#F5D66B', 8); ctx.globalAlpha = 1;
  }
};

// ---------------------------------------------------------------- the eight answers
function heartPts(cx, cy, s) { const p = []; for (let i = 0; i < 40; i++) { const a = i / 40 * TAU; p.push([cx + 16 * Math.pow(Math.sin(a), 3) * s, cy - (13 * Math.cos(a) - 5 * Math.cos(2 * a) - 2 * Math.cos(3 * a) - Math.cos(4 * a)) * s]); } return p; }
function miniNote(x, y, s, col, seed) { cutGroup([[ell(x, y + 50 * s, 22 * s, 16 * s, -.4), col], [rect(x + 14 * s, y - 40 * s, 8 * s, 90 * s), col], [[[x + 22 * s, y - 40 * s], [x + 50 * s, y - 15 * s], [x + 22 * s, y - 15 * s]], col]], { edge: 3, seed }); }
const PROPS = {
  star(t, lt, p) {
    for (let i = 0; i < 12; i++) { const a = i / 12 * TAU, r = 380 + H(i) * 120; ctx.globalAlpha = .6 + .4 * Math.sin(t * 5 + i); cut(star(960 + Math.cos(a) * r * 1.4, 520 + Math.sin(a) * r * .8, 22 + H(i * 3) * 18, 10, 5, i), i % 2 ? '#FBF6EA' : '#F6D35A', { seed: 1010 + i, edge: 3 }); ctx.globalAlpha = 1; }
    spark(960, 330 - p * 20, 150, t, { eyes: 'closed', seed: 1000, hands: [[-.9, 1.1], [.9, 1.1]] });
    cut(star(960, 590, 300, 150, 5, -Math.PI / 2 + Math.sin(t * 2) * .05), '#F6CE4B', { seed: 1001, edge: 8 });
    line(arcPts(920, 600, 14, Math.PI * 1.1, Math.PI * 1.9, 5), INK, 6); line(arcPts(1000, 600, 14, Math.PI * 1.1, Math.PI * 1.9, 5), INK, 6); line(arcPts(960, 625, 16, Math.PI * .2, Math.PI * .8, 5), INK, 6);
  },
  sea(t, lt, p) {
    const rock = Math.sin(t * 4) * .08;
    spark(960, 400 + Math.sin(t * 4) * 12, 150, t, { eyes: 'closed', seed: 1100, rot: rock });
    ctx.save(); ctx.translate(960, 560 + Math.sin(t * 4) * 12); ctx.rotate(rock);
    cut([[-230, -70], [230, -70], [160, 60], [-160, 60]], '#E6E1D6', { seed: 1101, edge: 5 });
    cut([[-120, -70], [-40, -170], [10, -70]], '#D8D2C4', { seed: 1102, edge: 4 });
    ctx.globalAlpha = .45; for (let r = 0; r < 4; r++) line([[-150 + r * 10, -40 + r * 22], [150 - r * 10, -40 + r * 22]], '#6B6458', 5, { seed: 1103 + r, j: 3 }); ctx.globalAlpha = 1;
    ctx.restore();
    const wave = []; for (let i = 0; i <= 16; i++) { const x = -60 + i * 128; wave.push([x, 620 + Math.sin(i * 1.3 + t * 5) * 22 - Math.sin(i / 16 * Math.PI) * 80]); }
    cut([...wave, [1980, 1200], [-60, 1200]], '#6FA8DC', { seed: 1104, edge: 7 });
    cut([...wave.map(([x, y]) => [x, y + 60]), [1980, 1200], [-60, 1200]], '#2F5FA8', { seed: 1105, edge: 0 });
    for (let i = 0; i < 5; i++) line(arcPts(560 + i * 200, 800 + (i % 2) * 60, 30, Math.PI, TAU, 6), '#A6CBEF', 5, { seed: 1106 + i });
  },
  tree(t, lt, p) {
    ctx.save(); ctx.translate(0, -50);
    cut(capsule(960, 900, 960, 560, 50, 36), '#8A5A34', { seed: 1200, edge: 6 });
    cut(ell(960, 920, 260, 30), '#5E9E4E', { seed: 1201, edge: 4 });
    spark(960, 200 - p * 25, 140, t, { eyes: 'closed', seed: 1202 });
    const sway = Math.sin(t * 3) * 8;
    cutGroup([[ell(820 + sway, 540, 170, 160), '#4E9A4A'], [ell(1100 + sway, 540, 170, 160), '#4E9A4A'], [ell(960 + sway, 420, 190, 170), '#6BB35A']], { edge: 7, seed: 1203 });
    for (let i = 0; i < 9; i++) cut(ell(800 + H(i) * 330 + sway, 380 + H(i * 7) * 280, 20, 20), '#E2463F', { seed: 1210 + i, edge: 3 });
    for (let i = 0; i < 3; i++) { const u = (lt * .8 + i / 3) % 1; ctx.globalAlpha = 1 - u; cut(ell(700 + i * 260 + u * 60, 400 + u * 300, 18, 9, u * 4), '#8BC66E', { seed: 1220 + i, edge: 2 }); ctx.globalAlpha = 1; }
    ctx.restore();
  },
  book(t, lt, p) {
    spark(960, 420 - p * 20, 160, t, { eyes: 'closed', seed: 1300, mouth: 'o' });
    cut([[520, 560], [960, 600], [1400, 560], [1420, 900], [960, 930], [500, 900]], '#C0392B', { seed: 1301, edge: 7 });
    cut([[540, 540], [960, 585], [960, 900], [540, 870]], '#FBF6EA', { seed: 1302, edge: 3 });
    cut([[1380, 540], [960, 585], [960, 900], [1380, 870]], '#F4EEDE', { seed: 1303, edge: 3 });
    ctx.globalAlpha = .4; for (let r = 0; r < 7; r++) { line([[580, 600 + r * 38], [920, 630 + r * 38]], '#555', 6, { seed: 1304 + r, j: 3 }); line([[1000, 630 + r * 38], [1340, 600 + r * 38]], '#555', 6, { seed: 1320 + r, j: 3 }); } ctx.globalAlpha = 1;
    const letters = [['从', '#E2463F'], ['前', '#2F5BB8'], ['有', '#F2B430'], ['个', '#3F9C62']];
    letters.forEach(([c, col], i) => {
      const u = back(seg(lt, .05 + i * .12, .35 + i * .12)), x = 600 + i * 240, y = 560 - u * (300 + (i % 2) * 60) + Math.sin(t * 5 + i) * 8;
      if (u <= 0) return;
      ctx.save(); ctx.translate(x, y); ctx.rotate((H(i) - .5) * .5); ctx.font = `150px ${FONT}`; ctx.lineWidth = 14; ctx.strokeStyle = '#FBF6EA'; ctx.lineJoin = 'round'; ctx.strokeText(c, -75, 50); ctx.fillStyle = col; ctx.fillText(c, -75, 50); ctx.restore();
    });
  },
  song(t, lt, p) {
    const bob = i => Math.sin(t * 10.5 + i * 2) * 14;
    cutGroup([[ell(640, 800 + bob(0), 72, 52, -.4), '#E2463F'], [rect(690, 380 + bob(0), 24, 420), '#E2463F'], [[[714, 380 + bob(0)], [800, 470 + bob(0)], [790, 560 + bob(0)], [714, 470 + bob(0)]], '#E2463F']], { edge: 6, seed: 1400 });
    cutGroup([[ell(1080, 820 + bob(1), 70, 50, -.4), '#2F4FA8'], [ell(1330, 780 + bob(1), 70, 50, -.4), '#2F4FA8'], [rect(1128, 440 + bob(1), 24, 380), '#2F4FA8'], [rect(1378, 400 + bob(1), 24, 380), '#2F4FA8'],
      [[[1128, 440 + bob(1)], [1402, 400 + bob(1)], [1402, 460 + bob(1)], [1128, 500 + bob(1)]], '#2F4FA8']], { edge: 6, seed: 1410 });
    spark(960, 380 - p * 40, 160, t, { eyes: 'closed', mouth: 'o', seed: 1420 });
    for (let i = 0; i < 3; i++) { const u = (lt * 1.2 + i / 3) % 1; ctx.globalAlpha = 1 - u; miniNote(1100 + i * 60 + u * 80, 250 - u * 160, .8, '#2B2233', 1430 + i); ctx.globalAlpha = 1; }
  },
  food(t, lt, p) {
    for (let i = 0; i < 3; i++) line(Array.from({ length: 14 }, (_, j) => [840 + i * 120 + Math.sin(j * .7 + t * 4 + i) * 20, 560 - j * 22 - (lt * 60 % 30)]), '#FBF6EA', 10, { seed: 1500 + i, j: 2 });
    spark(960, 250, 140, t, { eyes: 'closed', mouth: 'o', seed: 1510, rot: Math.sin(t * 3) * .05 });
    const dump = (x, y, s, r, sd) => { ctx.save(); ctx.translate(x, y); ctx.rotate(r); ctx.scale(s, s); cut([...arcPts(0, 0, 110, Math.PI, TAU, 12, 80), [110, 10], [-110, 10]], '#F7EEDC', { seed: sd, edge: 4 }); for (let k = 0; k < 5; k++) line([[-60 + k * 30, -50 + Math.abs(k - 2) * 8], [-54 + k * 30, -20]], '#D9C6A5', 5, { seed: sd + k }); ctx.restore(); };
    dump(840, 600, .9, -.2, 1520); dump(1080, 600, .9, .2, 1530); dump(960, 560, 1, 0, 1540);
    cut([...arcPts(960, 640, 360, 0, Math.PI, 16, 250), [600, 640]], '#FBF8F0', { seed: 1550, edge: 7 });
    cut(rect(600, 626, 720, 30), '#3D6FC4', { seed: 1551, edge: 0 });
    for (let i = 0; i < 6; i++) cut(ell(700 + i * 104, 740 + Math.sin(i * 1.4) * 10, 20, 20), '#3D6FC4', { seed: 1552 + i, edge: 0 });
    cut(rect(880, 880, 160, 30), '#E8E2D4', { seed: 1560, edge: 4 });
  },
  wind(t, lt, p) {
    line([[1180, 950], [1170, 700], [1150, 500]], '#4F8A44', 12, { seed: 1600 });
    for (let i = 0; i < 18; i++) { const a = i / 18 * TAU; line([[1150, 480], [1150 + Math.cos(a) * 100, 480 + Math.sin(a) * 100]], '#FBF6EA', 5, { seed: 1601 + i }); dot(1150 + Math.cos(a) * 100, 480 + Math.sin(a) * 100, 9, '#FBF6EA'); }
    dot(1150, 480, 26, '#C9B89A');
    for (let i = 0; i < 10; i++) {
      const u = (lt * .9 + H(i)) % 1, x = 1200 + u * 700 + H(i * 3) * 80, y = 450 - u * 300 + Math.sin(u * 8 + i) * 50 + (H(i * 5) - .5) * 260;
      ctx.globalAlpha = 1 - u * .6; line([[x, y], [x - 30, y + 26]], '#FBF6EA', 4, { seed: 1620 + i }); dashes(x, y, 0, 18, 6, '#FBF6EA', 3); ctx.globalAlpha = 1;
    }
    spark(620, 460, 170, t, { eyes: 'closed', mouth: 'o', seed: 1630, rot: -.1 });
    for (let i = 0; i < 3; i++) { const u = (lt * 1.5 + i / 3) % 1; ctx.globalAlpha = Math.sin(u * Math.PI); line(Array.from({ length: 10 }, (_, j) => [800 + u * 200 + j * 30, 420 + i * 60 + Math.sin(j * .8 + i) * 12]), '#FBF6EA', 7, { seed: 1640 + i }); ctx.globalAlpha = 1; }
  },
  heart(t, lt, p) {
    const hp = heartPts(960, 560, 20 * (1 + p * .06));
    spark(960, 300, 150, t, { eyes: 'closed', seed: 1700 });
    cut(hp, '#E0444E', { seed: 1701, edge: 9 });
    line(arcPts(910, 560, 16, Math.PI * 1.1, Math.PI * 1.9, 5), INK, 7); line(arcPts(1010, 560, 16, Math.PI * 1.1, Math.PI * 1.9, 5), INK, 7); line(arcPts(960, 590, 18, Math.PI * .2, Math.PI * .8, 5), INK, 7);
    ctx.globalAlpha = .85; dot(875, 595, 16, BLUSH); dot(1045, 595, 16, BLUSH); ctx.globalAlpha = 1;
    for (let i = 0; i < 5; i++) { const u = (lt * .9 + i / 5) % 1, x = 520 + i * 220 + Math.sin(u * 6 + i) * 20, y = 900 - u * 700; ctx.globalAlpha = Math.sin(u * Math.PI); cut(heartPts(x, y, 2.4), '#E0444E', { seed: 1710 + i, edge: 3 }); ctx.globalAlpha = 1; }
  },
};
const DASH = { star: '#FBF6EA', sea: '#2F5FA8', tree: '#C0392B', book: '#C0392B', song: '#2B2233', food: '#B0703A', wind: '#FBF6EA', heart: '#C0392B' };
SHOT.ans = (t, lt, d, s) => {
  const a = s.ans, pop = back(seg(lt, 0, .22)), p = beatPulse(t);
  bg(a.bg); cam(960, 540, 1);
  cut(rect(-100, -100, VW + 200, VH + 200), a.bg, { seed: 990, edge: 0, tex: .22 });
  ctx.globalAlpha = .8; dashes(960, 520, 470 + p * 20, 560 + p * 30, 16, DASH[a.key], 9, s.i * .3, { jit: .25 }); ctx.globalAlpha = 1;
  ctx.save(); ctx.translate(960, 540); ctx.scale(.86 + pop * .14, .86 + pop * .14); ctx.translate(-960, -540);
  PROPS[a.key](t, lt, p);
  ctx.restore();
  hand(a.text, 960, 1025, 92, '#2B2233', seg(lt, .05, .5) * [...a.text].length, { align: 'center', seed: s.i });
};

SHOT.reply = (t, lt, d) => {
  cam(960, 520, 1.06);
  nightSky(t, { moon: [1700, 120] });
  const fold = eio(seg(lt, .9, 1.35)), toss = seg(lt, 1.7, 2.4), R = 320;
  const hands = fold < 1 ? [[-.6, 1.05], [.55, .8]] : [[.55, .95 - toss * .6]];
  spark(960, 460, R, t, { eyes: 'open', mouth: lt < 1.6 ? 'flat' : 'smile', hands, seed: 710, rot: toss * .1 });
  if (fold < 1) {
    const w = lerp(470, 150, fold), h = lerp(360, 90, fold);
    ctx.save(); ctx.translate(960, 460 + R * .95); ctx.rotate(-.03);
    cut(rect(-w / 2, -h / 2, w, h), '#FBF7EC', { seed: 880, edge: 6, tex: .3 });
    // scribbles (the back of the note) — you can't read it yet
    const n = inked('scribble', t);
    for (let i = 0; i < Math.min(6, Math.ceil(n)); i++) { const k = clamp(n - i), y = -h * .35 + (i % 3) * h * .25, x0 = -w * .38 + Math.floor(i / 3) * w * .02; ctx.globalAlpha = 1 - fold; line(Array.from({ length: Math.max(2, Math.round(10 * k)) }, (_, j) => [x0 + j * w * .075, y + Math.sin(j * 2.3 + i) * h * .05]), '#D65A3A', 6, { seed: 881 + i }); ctx.globalAlpha = 1; }
    ctx.restore();
    for (const s of [-1]) cut(ell(960 + s * R * .62, 460 + R * 1.02, R * .15, R * .14), SPARK, { seed: 716, edge: 5 });
    // pencil in the right hand
    const wr = Math.sin(lt * 18) * 10 * (lt < .9 ? 1 : 0);
    cut(capsule(960 + R * .45 + wr, 460 + R * .9, 960 + R * .75 + wr, 460 + R * .5, 11, 13), '#2F5BB8', { seed: 882, edge: 4 });
    cut(ell(960 + R * .55 + wr, 460 + R * .8, R * .14, R * .13), SPARK, { seed: 717, edge: 5 });
  } else {
    const u = eout(toss), px = lerp(960 + R * .6, -150, u), py = lerp(460 + R * .4, 900, u) - Math.sin(u * Math.PI) * 150;
    if (u > 0) trail([[960 + R * .6, 460 + R * .4], [lerp(960 + R * .6, px, .5), lerp(460 + R * .4, py, .5) - 100], [px + 40, py]]);
    plane(px, py, 1.3, Math.PI + .35, 890);
  }
};

SHOT.back = (t, lt, d) => {
  const u = eio(lt / d);
  cam(lerp(1000, 620, u), lerp(520, 620, u), lerp(1, 1.3, u));
  houseWorld(t, { girl: { eyes: 'up', mouth: 'o', look: [.4, -.6] } });
  spark(1340, 210, 140, t, { eyes: 'closed', seed: 700 });
  const path = s => [lerp(1260, WIN.x + WIN.w * .6, s) + Math.sin(s * 9) * 40 * (1 - s), lerp(300, WIN.y + WIN.h * .4, s) - Math.sin(s * Math.PI) * 120];
  const pts = []; for (let s = 0; s <= u; s += .01) pts.push(path(s)); if (pts.length > 1) trail(pts);
  const [x, y] = path(u), [x2, y2] = path(Math.min(1, u + .01));
  plane(x, y, lerp(.9, .5, u), Math.atan2(y2 - y, x2 - x), 890);
};

SHOT.got = (t, lt, d) => {
  cam(960, 540, 1.02);
  const c = .6, u = eout(seg(lt, 0, c)), open = eio(seg(lt, 1.1, 1.7));
  windowScene(t, {
    girl: lt < c ? { eyes: 'up', mouth: 'o', look: [.5, -.7] } : lt < 1.1 ? { eyes: 'open', mouth: 'o', look: [.3, 0] } : { eyes: 'down', mouth: 'smile', look: [0, .3] },
    rays: lt > c ? .9 : 0,
    front: () => {
      if (open <= 0) {
        const px = lerp(1900, 1250, u), py = lerp(-100, 380, u);
        if (lt < c) trail([[1900, -100], [px + 60, py - 40]]);
        cut(ell(862, 880, 32, 30), '#EDB68E', { seed: 662, edge: 4 });
        arm(1100, 745, lerp(1200, 1250, u), lerp(560, 400, u), 1.4, 663);
        plane(px, py, 1.3, Math.PI * .8, 890);
        if (lt > c) { ctx.globalAlpha = 1 - seg(lt, c, c + .35); dashes(1250, 400, 70, 140, 10, '#FFF6D0', 7); ctx.globalAlpha = 1; }
      } else {
        heldNote(960, 820, lerp(160, 460, open), lerp(90, 300, open), .02, t, {});
        cut(ell(lerp(900, 750, open), 860, 32, 30), '#EDB68E', { seed: 665, edge: 4 }); cut(ell(lerp(1020, 1170, open), 860, 32, 30), '#EDB68E', { seed: 666, edge: 4 });
      }
    },
  });
};

SHOT.read = (t, lt, d) => {
  desk(t);
  cam(960, lerp(560, 600, eio(lt / d)), lerp(1.0, 1.1, eio(lt / d)));
  ctx.save(); ctx.translate(960, 540); ctx.rotate(-.025 + Math.sin(t * 1.5) * .006);
  cut(capsule(-1100, 800, -640, 380, 90, 70), '#2C9A88', { seed: 900, edge: 7 }); cut(capsule(1100, 800, 640, 380, 90, 70), '#2C9A88', { seed: 901, edge: 7 });
  notePage(1360, 860, 902);
  hand('人死后，会去哪里？', -540, -260, 84, '#2B4EA2', 9, { seed: 5 });
  const n = inked('spark', t), L1 = [...ANSWER[0]].length;
  hand(ANSWER[0], -540, -40, 132, '#D65A3A', Math.min(n, L1), { seed: 6 });
  hand(ANSWER[1], -540, 180, 132, '#D65A3A', n - L1, { seed: 7 });
  const sig = back(seg(lt, 4.1, 4.4));
  if (sig > 0) { ctx.save(); ctx.translate(470, 320); ctx.scale(sig, sig); spark(0, 0, 70, t, { eyes: 'closed', seed: 910, wiggle: .5 }); ctx.restore(); }
  cut(ell(-640, 370, 70, 64), '#EDB68E', { seed: 903, edge: 5 }); cut(ell(640, 370, 70, 64), '#EDB68E', { seed: 904, edge: 5 });
  ctx.restore();
};

SHOT.end = (t, lt, d) => {
  const u = eio(seg(lt, 0, 2.4));
  cam(lerp(620, 960, u), lerp(620, 540, u), lerp(1.3, 1, u));
  houseWorld(t, { girl: { eyes: 'closed', mouth: 'smile' }, rays: .9, front: () => { photo(700, 860, 1, -.08); heldNote(1180, 870, 360, 230, .06, t, {}); } });
  // the spark waves
  spark(1340, 210, 140, t, { eyes: 'closed', seed: 700, rot: Math.sin(t * 4) * .12 });
  // a new star by the moon
  const tw = SCORE.twinkle.map(e => e.t - SHOTS[SHOTS.length - 1].t0), s = back(seg(lt, tw[0], tw[0] + .35)), glow = Math.exp(-Math.max(0, lt - tw[0]) * 2) + Math.exp(-Math.max(0, lt - tw[1]) * 3) * (lt > tw[1]);
  if (s > 0) {
    const sx = 1530, sy = 110;
    ctx.globalAlpha = clamp(glow); dashes(sx, sy, 50, 90 + glow * 20, 10, '#F5D66B', 5); ctx.globalAlpha = 1;
    cut(star(sx, sy, 38 * s * (1 + .1 * Math.sin(t * 4)), 16 * s, 5, -Math.PI / 2 + Math.sin(t) * .1), '#F9DC6E', { seed: 950, edge: 4 });
  }
  const tt = seg(lt, 2.6, 3.2);
  if (tt > 0) {
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalAlpha = tt; hand('人死后，会去哪里？', 620, 150, 84, '#FBF6EA', 9, { align: 'center', seed: 9 });
    hand('写给每一个想念的人', 620, 235, 48, '#F5D66B', 9 * seg(lt, 3.0, 3.6), { align: 'center', seed: 10 }); ctx.globalAlpha = 1;
  }
};

// ---------------------------------------------------------------- frame
function drawFrame(c, t) {
  ctx = c; t = clamp(t, 0, DUR - 1e-4);
  BOIL = Math.floor(t * 8); SEED = 0;
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  const s = shotAt(t);
  SHOT[s.name](t, t - s.t0, s.t1 - s.t0, s);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1;
  ctx.globalCompositeOperation = 'multiply'; ctx.globalAlpha = .55; ctx.drawImage(GRAIN, 0, 0); ctx.globalAlpha = 1; ctx.globalCompositeOperation = 'source-over';
  const v = ctx.createRadialGradient(VW / 2, VH / 2, VH * .5, VW / 2, VH / 2, VH * 1.1); v.addColorStop(0, 'rgba(40,20,20,0)'); v.addColorStop(1, 'rgba(40,20,20,.28)');
  ctx.fillStyle = v; ctx.fillRect(0, 0, VW, VH);
  const fade = Math.max(1 - seg(t, 0, .5), seg(t, DUR - 1.2, DUR));
  if (fade > 0) { ctx.fillStyle = `rgba(20,18,40,${fade})`; ctx.fillRect(0, 0, VW, VH); }
}
