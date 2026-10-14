// act2.js — 1:08–2:20. The puppy walks in and the house fills with colour; the window lights pane by pane;
// hide-and-seek; rice drying in the sun; waiting at the bus stop through days and nights; stars in the flooded
// paddies; a chin on his knee and her favourite slipper; the city flat; nine candles.

// pixels further than r from (cx, cy) lose their colour (a dithered edge), as if colour were spreading from there
function colorReveal(g, cx, cy, r, x0 = 0, y0 = 0, w = PW, h = PH) {
  const img = g.getImageData(x0, y0, w, h), d = img.data;
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const dx = x0 + x - cx, dy = (y0 + y - cy) * 1.3, dd = Math.sqrt(dx * dx + dy * dy), edge = clamp((dd - r) / 10);
    if (edge <= 0 || bayer(x0 + x, y0 + y) >= edge) continue;
    const o = (y * w + x) * 4, l = .3 * d[o] + .59 * d[o + 1] + .11 * d[o + 2];
    d[o] = l * .92; d[o + 1] = l * .95; d[o + 2] = l * 1.05;
  }
  g.putImageData(img, x0, y0);
}

// ---------------------------------------------------------------- 1:08 the puppy walks in, colour follows
SCENES.door = (g, t, lt) => {
  room(g, { wall: '#EAD9BC', wallD: '#E2CEAA', base: '#9C7652', floor: '#B8B2A0', floorY: 150, terrazzo: true });
  // the open door: the sunny courtyard outside
  doorway(g, 120, 104, 28, 46, '#5E9C8C', 1, (gg, x, y, w, h) => {
    grad(gg, SKIES.day, x, y, w, 24); rect(gg, x, y + 24, w, h - 24, '#E8DAB8'); disc(gg, x + 22, y + 22, 8, '#5E9A4E'); rect(gg, x, y + 30, w, 1, '#D6C49E');
  });
  for (let j = 0; j < 18; j++) dith(g, 120 + j * 2, 150 + j, 28 + j * 2, 1, '#FFF4D2', .5 - j * .02);
  // shoe rack with a small pair of white sneakers
  rect(g, 102, 136, 14, 14, '#8C5E3A'); rect(g, 102, 142, 14, 1, '#6A4228'); rect(g, 104, 139, 4, 2, '#FFFFFF'); rect(g, 109, 139, 4, 2, '#FFFFFF');
  // family photo and a calendar
  rect(g, 168, 92, 18, 14, INK); rect(g, 169, 93, 16, 12, '#F6EBD2'); for (const [fx, c] of [[172, '#4B8CC0'], [177, '#C46E7C'], [182, '#6E9E58']]) { rect(g, fx - 1, 99, 3, 5, c); rect(g, fx - 1, 96, 3, 3, SKIN); }
  rect(g, 252, 90, 14, 18, INK); rect(g, 253, 91, 12, 16, '#FFFDF4'); rect(g, 253, 91, 12, 4, '#D8423A');
  // the puppy: a silhouette in the bright doorway, then across the floor to him
  const walk = seg(t, 69.6, 72.6), jump = seg(t, 72.6, 73.0);
  const px0 = lerp(134, 222, walk), boyX = 238;
  if (jump <= 0) dog(g, px0, 150, { size: 'pup', pose: walk > 0 && walk < 1 ? 'walk' : 'stand', phase: t * 2.4, wag: 1.2, collar: true, silhouette: t < 69.5 ? '#6E6A62' : null }, t);
  human(g, boyX, 150, { age: 'kid', pose: 'squat', flip: true, armN: t > 71.5 ? 'hug' : 'down', armF: t > 71.5 ? 'hug' : 'down', eyes: t > 72.6 ? 'happy' : 'open', mouth: t > 71.5 ? 'open' : null, blush: t > 72.6 }, t);
  if (jump > 0) dog(g, lerp(222, boyX - 6, jump), lerp(150, 140, jump) - Math.sin(jump * Math.PI) * 8, { size: 'pup', pose: jump < 1 ? 'jump' : 'beg', wag: 2, collar: true, tongue: true, eyes: 'happy' }, t);
  if (t > 73.0) for (let i = 0; i < 3; i++) { const u = ((t - 73 + i * .4) % 1.2) / 1.2; heart(g, boyX - 8 + i * 6, 126 - u * 14, '#FF7F8C'); }
  // colour spreads from where the puppy is
  const r = t < 69.4 ? 0 : lerp(0, 260, ein(seg(t, 69.4, 73.4)) * .4 + seg(t, 69.4, 73.4) * .6);
  if (r < 250) colorReveal(g, px0, 146, r, 96, 60, 192, 108);
  return { zoom: 2, x: 96, y: 60 };
};

// ---------------------------------------------------------------- 1:15 thank you for being my nine-ninths
SCENES.panes = (g, t, lt) => {
  room(g, { wall: '#E6CFA8', wallD: '#D8BC90', base: '#8C6440', floor: '#B48A5E', floorY: 170, planks: true, plankLine: '#9A7048' });
  const n = countIn(NINE_A, t), full = seg(t, NINE_A_END - .1, NINE_A_END + .3), fade = seg(t, 83.4, 84.6);
  const lit = Array.from({ length: 9 }, (_, i) => i < n ? 1 : 0);
  // light on the wall and squares on the floor
  for (let i = 0; i < 9; i++) if (lit[i]) {
    const c = i % 3, r = Math.floor(i / 3);
    glow(g, 133 + 3 + c * 42 + 20, 28 + 3 + r * 28 + 13, 28, '#FFE2A0', .22 + full * .1);
    for (let j = 0; j < 7; j++) dith(g, 150 + c * 40 - r * 8 - j * 3, 176 + r * 12 + j, 34, 1, '#FFE6A8', .55 + full * .25);
  }
  const view = scratch('paneView'); { const vg = view.getContext('2d'); vg.save(); plainsBase(vg, t, 0, { poles: false }); vg.restore(); }
  nineWindow(g, 133, 28, 40, 26, {
    view: (gg, x, y, w, h) => gg.drawImage(view, 128, 52, w, h, x, y, w, h),
    lit, litCol: '#FFF0C0', litA: .2 + full * .35, dimCol: '#2A2030', dimA: .55, glint: false,
  });
  // the pane that just lit gets a sparkle
  NINE_A.forEach((x, i) => { const a = seg(t, x, x + .35); if (a > 0 && a < 1) { const c = i % 3, r = Math.floor(i / 3); sparkle(g, 136 + c * 42 + 34, 31 + r * 28 + 4, a < .5 ? 2 : 1, '#FFFFFF'); } });
  if (full > 0) for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2 + t; sparkle(g, 198 + Math.cos(a) * 80, 72 + Math.sin(a) * 50, 1, '#FFF6D8'); }
  // the window seat, the boy and the puppy looking at each other
  rect(g, 118, 146, 148, 4, '#7A4E30'); rect(g, 118, 146, 148, 1, '#A0714A'); rect(g, 122, 150, 140, 20, '#8C5E3A'); rect(g, 122, 150, 140, 1, '#6A4228');
  human(g, 176, 147, { age: 'kid', pose: 'sit', eyes: n >= 9 ? 'happy' : 'open', mouth: 'smile', blush: n >= 9, armN: n >= 9 ? 'fwd' : 'down' }, t);
  dog(g, 210, 146, { size: 'pup', pose: 'sit', flip: true, collar: true, wag: 1, look: 'up', eyes: n >= 9 ? 'happy' : 'open', tongue: n >= 9 }, t);
  if (fade > 0) fadeTo(g, '#FFF0D0', fade * .5);
};

// ---------------------------------------------------------------- 1:25 eyes shut, he still walks straight to you
function waterJar(g, x, y) { ellipse(g, x, y - 11, 14, 12, INK); ellipse(g, x, y - 11, 13, 11, '#5E4A3E'); ellipse(g, x - 4, y - 15, 5, 4, '#7A6252'); rect(g, x - 11, y - 22, 22, 2, INK); rect(g, x - 10, y - 22, 20, 1, '#3A3A48'); }
SCENES.hide = (g, t, lt) => {
  courtyard(g, t, { sky: SKIES.day, chickens: false });
  const count = Math.min(9, Math.max(0, Math.floor((t - 85.1) / BEAT) + 1)), go = seg(t, 88.9, 90.2), found = t > 90.2;
  // 九九 behind the water jar: only the wagging tail gives her away
  if (!found) dog(g, 268, 172, { pose: 'sit', collar: true, wag: 1.6, flip: true }, t);
  waterJar(g, 262, 176);
  if (found) dog(g, 250, 172 - R(Math.max(0, Math.sin((t - 90.2) * 9)) * 4), { pose: t < 90.6 ? 'jump' : 'beg', flip: true, collar: true, wag: 2, tongue: true, eyes: 'happy' }, t);
  const bx = lerp(176, 238, eio(go));
  human(g, bx, 174, { age: 'kid', look: go > 0 ? 'side' : 'front', pose: go > 0 && go < 1 ? 'walk' : 'stand', phase: t * 2, armN: go > 0 ? 'fwd' : 'cover', armF: go > 0 ? 'fwd' : 'cover', eyes: found ? 'happy' : 'closed', mouth: found ? 'open' : count >= 9 ? 'open' : 'smile', blush: found }, t);
  // he counts to nine
  if (count > 0 && go < .5) {
    const num = String(count), a = ((t - 85.1) / BEAT) % 1;
    ptext(g, count === 9 ? '9！' : num, bx, 136 - R(eout(Math.min(1, a * 3)) * 4), { col: count === 9 ? '#FFCB45' : '#FFFFFF', outline: INK });
  }
  if (found) for (let i = 0; i < 2; i++) heart(g, 244 + i * 10, 140 - ((t * 10 + i * 5) % 12), '#FF7F8C');
  return { zoom: 2, x: 138, y: 96 };
};

// ---------------------------------------------------------------- 1:32 a clear southern day: rice drying in the courtyard
SCENES.grain = (g, t, lt) => {
  grad(g, SKIES.day, 0, 0, PW, 96);
  glow(g, 320, 26, 22, '#FFFFFF', .5); disc(g, 320, 26, 7, '#FFFDF0');
  for (let i = 0; i < 4; i++) cloud(g, ((i * 110 + t * (3 + i)) % 500) - 80, 14 + (i % 2) * 22, 50 + i * 8);
  hamlets(g, 96, 0, '#4E7A3E', '#5E9A4A', '#A85A44', 9);
  rect(g, 0, 96, PW, 40, '#7FB04E');
  farmhouse(g, 118, 72);
  for (const x of [40, 64, 330, 352]) { rect(g, x, 60, 2, 76, '#8A7A5A'); for (let k = 0; k < 5; k++) line(g, x + 1, 60, x + 1 + Math.cos(k * 1.3 + Math.sin(t)) * 9, 58 + Math.sin(k * 1.3) * 4, '#4E8A3E'); }
  // the courtyard covered in grain, raked into stripes
  rect(g, 0, 136, PW, PH - 136, '#E9C65A');
  for (let y = 139; y < PH; y += 4) for (let x = 0; x < PW; x += 2) px(g, x, y + R(Math.sin(x * .05 + y) * 1), '#D6AE44');
  for (let i = 0; i < 300; i++) px(g, R(H(i) * PW), 136 + R(H(i * 3) * 80), '#F6DC86');
  // 九九 runs through it, leaving a trail of paw prints
  const run = seg(t, 92.0, 94.6), dx = lerp(-20, 290, run), dy = 188;
  for (let x = -20; x < dx - 8; x += 7) { const k = R((x + 20) / 7); rect(g, x, dy - 1 + (k % 2) * 3, 3, 2, '#B88A30'); }
  const lying = t > 94.6;
  dog(g, dx, dy, { pose: lying ? 'lie' : 'run', phase: t * 3, collar: true, wag: lying ? 1.5 : .5, tongue: true, eyes: lying ? 'happy' : 'open' }, t);
  const tx = lerp(-60, 254, seg(t, 92.4, 95.6)), sitting = t > 95.6;
  human(g, tx, 190, { age: 'teen', pose: sitting ? 'sitFloor' : 'run', phase: t * 2.6, armN: sitting ? 'up' : 'fwd', armF: 'fwd', eyes: 'happy', mouth: 'open' }, t);
  if (t > 95.8) for (let i = 0; i < 3; i++) sparkle(g, 240 + i * 22, 168 - ((t * 7 + i * 4) % 10), 1, '#FFFFFF');
};

// ---------------------------------------------------------------- 1:37 he leaves on the bus; 九九 waits through days and nights
function bus(g, x, y, t, o = {}) {
  x = R(x); y = R(y);
  if (o.flip) { g.save(); g.translate(2 * x + 64, 0); g.scale(-1, 1); bus(g, x, y, t, { ...o, flip: false }); g.restore(); return; }
  rect(g, x - 1, y - 27, 66, 24, INK); rect(g, x, y - 26, 64, 22, '#F4F1E6'); rect(g, x, y - 13, 64, 5, '#3E9A6A'); rect(g, x, y - 8, 64, 2, '#2E7A52');
  for (let i = 0; i < 6; i++) rect(g, x + 4 + i * 10, y - 23, 8, 8, o.night ? '#FFE2A0' : '#8EC4E0');
  rect(g, x + 58, y - 23, 5, 13, o.night ? '#FFE2A0' : '#8EC4E0');
  for (const wx of [x + 12, x + 50]) { disc(g, wx, y - 3, 4, INK); disc(g, wx, y - 3, 3, '#3A3A44'); px(g, wx, y - 3, '#B8BCC8'); }
  if (o.night) { rect(g, x + 63, y - 9, 2, 2, '#FFF6C8'); for (let k = 0; k < 6; k++) dith(g, x + 66 + k * 6, y - 11 - k, 6, 4 + k * 2, '#FFF2B0', .5 - k * .07); }
  if (o.wave) { rect(g, x + 4, y - 23, 8, 8, SKIN); rect(g, x + 5, y - 24, 6, 3, HAIR); if (Math.floor(t * 5) % 2) rect(g, x + 2, y - 25, 1, 3, SKIN); }
}
SCENES.busstop = (g, t, lt) => {
  // one day every three beats
  const day = (t - 98.7) / (BEAT * 3), u = day < 0 ? .2 : ((day % 1) + 1) % 1, k = Math.floor(day);
  const ph = t > 102.8 ? 'night' : u < .4 ? 'day' : u < .52 ? 'dusk' : u < .9 ? 'night' : 'dawn';
  const night = ph === 'night';
  grad(g, SKIES[ph], 0, 0, PW, 110);
  if (ph === 'day' || ph === 'dusk' || ph === 'dawn') { const su = ph === 'day' ? u / .4 : ph === 'dusk' ? 1 : 0; disc(g, 30 + su * 320, 80 - Math.sin(su * Math.PI) * 60, 7, '#FFF6D8'); }
  if (night) { stars(g, t, 40, 100, 7); const mu = t > 102.8 ? .7 : (u - .52) / .38; moon(g, 40 + mu * 300, 70 - Math.sin(mu * Math.PI) * 50, 6, SKIES.night[1]); }
  const pal = night ? { a: '#2E4A3A', b: '#34523E', hi: '#3E6048', lo: '#24382E', ridge: '#3A4A3E' } : ph === 'day' ? { a: '#7FB04E', b: '#8CBA56', hi: '#B8D872', lo: '#5E8A3A', ridge: '#A8B86A' } : { a: '#8A8A4E', b: '#969652', hi: '#C8B070', lo: '#6A6A3A', ridge: '#A89868' };
  hamlets(g, 110, 0, night ? '#1C2A24' : '#4E7A3E', night ? '#24342C' : '#5E9A4A', night ? '#3A2A2A' : '#A85A44', 13, night ? '#2A2E3E' : '#E8DCC8');
  paddies(g, t, 110, 150, 0, pal, 1);
  rect(g, 0, 150, PW, 16, night ? '#3A3E4A' : '#7E808A'); for (let x = 0; x < PW; x += 16) rect(g, x, 157, 8, 1, night ? '#8A8A70' : '#E8E2C8');
  rect(g, 0, 166, PW, PH - 166, night ? '#26382C' : '#6E9A44');
  grassTufts(g, t, 176, night ? '#1E2E24' : '#5A843A', night ? '#2E4434' : '#8FBA5A', 3);
  if (night) fireflies(g, t, 8, 0, 112, PW, 50, 3);
  // weather on some of the days
  if (k === 1 || k === 4) rain(g, t, 60, night ? '#5A6A9A' : '#B8CCE8', 1, PH);
  if (k === 2) for (let i = 0; i < 10; i++) { const lx = (i * 41 + t * 30) % PW, ly = (i * 23 + t * 40) % 150; rect(g, lx, ly, 2, 1, '#E89A4A'); }
  // the stop: a round blue sign
  rect(g, 150, 116, 2, 36, '#8A8E9A'); disc(g, 151, 114, 7, INK); disc(g, 151, 114, 6, '#3A7AC8'); rect(g, 147, 112, 8, 4, '#FFFFFF'); px(g, 148, 116, '#FFFFFF'); px(g, 153, 116, '#FFFFFF');
  // her shadow swings round like a sundial
  if (!night) { const sa = (ph === 'day' ? u / .4 : .9) * Math.PI; ellipse(g, 172 - Math.cos(sa) * 10, 166, 8, 2, '#4E6A34'); }
  const back = t > 103.4;
  dog(g, 172, 165, { pose: back ? 'beg' : 'sit', collar: true, wag: back ? 2.2 : (lastKick(t) > t - .3 ? 1 : .2), look: back ? 'up' : 'fwd', eyes: back ? 'happy' : 'open', tongue: back }, t);
  // the bus leaves at the start and brings him back at night
  const leave = seg(t, 97.6, 99.2), ret = seg(t, 102.9, 103.3);
  if (leave < 1) bus(g, lerp(176, 420, ein(leave)), 165, t, { wave: true });
  if (t > 102.9) {
    const bx = t < 104.4 ? lerp(400, 196, eout(ret)) : 196 + (t - 104.4) * 60;
    bus(g, bx, 165, t, { night: true, flip: true });
    if (t > 103.3) human(g, 190, 165, { age: 'teen', look: 'side', flip: true, eyes: back ? 'sad' : 'closed', bag: true, armN: 'down' }, t);
    if (t > 103.5) bubble(g, 192, 138, 26, 13, (x, y) => ptext(g, '58', x + 13, y, { col: '#E0503A' }));
  }
  if (night) grade(g, '#7A8AD8', .25);
};

// ---------------------------------------------------------------- 1:44 even when I'm stuck, there's you and the night sky
SCENES.paddies = (g, t, lt) => {
  const hy = 104;
  grad(g, ['#05081A', '#0C1434', '#18265A', '#2A3A72'], 0, 0, PW, hy);
  // the milky way: a slanted band of dithered light and dense stars
  for (let x = 0; x < PW; x++) { const cy = 20 + x * .18, w = 16 + Math.sin(x * .03) * 5; for (let y = R(cy - w); y < cy + w; y++) if (y >= 0 && y < hy && bayer(x, y) < .22 * (1 - Math.abs(y - cy) / w)) px(g, x, y, '#6A72B0'); }
  stars(g, t, 120, hy, 11);
  moon(g, 318, 30, 8, '#0E1636');
  const shoot = seg(t, 107.4, 108.0);
  if (shoot > 0 && shoot < 1) { const sx = lerp(80, 200, shoot), sy = lerp(14, 54, shoot); for (let k = 0; k < 12; k++) px(g, sx - k * 2, sy - k * .7, k < 3 ? '#FFFFFF' : '#9FB0E0'); }
  hamlets(g, hy, 0, '#070A18', '#0A0E22', '#1A1424', 21, '#141830');
  for (let i = 0; i < 8; i++) px(g, R(H(i * 9) * PW), hy - 2 - R(H(i * 5) * 4), '#FFD98A');
  // the flooded paddies hold the whole sky, broken by slow ripples
  const img = g.getImageData(0, 0, PW, hy), sd = img.data, out = g.getImageData(0, hy, PW, PH - hy), od = out.data;
  for (let y = 0; y < PH - hy; y++) {
    const sy = hy - 1 - y; if (sy < 0) break;
    const shift = R(Math.sin(y * .5 - t * 3) * (y / 40));
    for (let x = 0; x < PW; x++) { const sx = clamp(x + shift, 0, PW - 1), si = (sy * PW + sx) * 4, oi = (y * PW + x) * 4; od[oi] = sd[si] * .62; od[oi + 1] = sd[si + 1] * .66; od[oi + 2] = sd[si + 2] * .78; }
  }
  g.putImageData(out, 0, hy);
  // rows of young rice and the raised ridge they sit on
  for (let r = 0; r < 6; r++) for (let x = (r * 3) % 9; x < PW; x += 9) px(g, x, hy + 6 + r * r * 3, '#2E5A3A');
  rect(g, 0, 156, PW, 6, '#232B4A'); rect(g, 0, 156, PW, 1, '#46508A');
  fireflies(g, t, 14, 0, 110, PW, 44, 5);
  // the two of them in silhouette, with a thin edge of moonlight
  for (const [col, dy] of [['#7A86C8', -1], ['#080A16', 0]]) {
    human(g, 178, 157 + dy, { age: 'teen', pose: 'sitFloor', silhouette: col }, t);
    dog(g, 208, 157 + dy, { pose: 'sit', flip: true, look: 'up', wag: .6, silhouette: col }, t);
  }
  if (t > 108.2) for (let i = 0; i < 2; i++) { const a = seg(t, 108.2 + i * .3, 109.4 + i * .3); if (a > 0 && a < 1) sparkle(g, 196, 132 - a * 10, 1, '#FFF6D8'); }
};

// ---------------------------------------------------------------- 1:51 who am I to you, that you'd do all this
function slipper(g, x, y) { rect(g, x - 1, y - 1, 10, 5, INK); rect(g, x, y, 8, 3, '#5A8AD8'); rect(g, x + 1, y, 4, 1, '#FFFFFF'); }
SCENES.doorstep = (g, t, lt) => {
  if (t < 119.7) {
    // night porch: brick wall, a warm lamp, moths
    rect(g, 0, 0, PW, 150, '#4A2A26');
    for (let j = 0; j < 150; j += 3) for (let i = (j / 3) % 2 ? 0 : 3; i < PW; i += 6) rect(g, i, j, 5, 1, '#5E3630');
    rect(g, 168, 70, 50, 80, '#2A1C18'); rect(g, 170, 72, 22, 78, '#3E2A22'); rect(g, 194, 72, 22, 78, '#3E2A22');
    rect(g, 160, 70, 4, 50, '#A8322C'); rect(g, 222, 70, 4, 50, '#A8322C');
    glow(g, 193, 62, 56, '#9A5A3A', .3); glow(g, 193, 62, 26, '#E8A060', .22); disc(g, 193, 62, 3, '#FFF2C0'); rect(g, 191, 56, 5, 3, '#3A3A44');
    for (let i = 0; i < 3; i++) { const a = t * (3 + i) + i * 2; px(g, 193 + Math.cos(a) * (6 + i * 3), 62 + Math.sin(a * 1.3) * 5, '#E8E0D0'); }
    rect(g, 0, 150, PW, 6, '#2E2A28'); rect(g, 140, 150, 110, 6, '#8A8478'); rect(g, 140, 150, 110, 1, '#A8A296'); rect(g, 0, 156, PW, PH - 156, '#3A3632');
    // he sits head down; she comes, leans on his knee, fetches her slipper
    const sad = t < 117.6;
    human(g, 184, 151, { age: 'teen', pose: 'sit', eyes: sad ? 'sad' : 'happy', mouth: sad ? null : 'open', armN: t > 117.8 ? 'fwd' : 'hold', armF: 'hold' }, t);
    let dx, pose = 'walk', flip = true, carry = null;
    if (t < 113.0) dx = lerp(290, 214, seg(t, 110.9, 113.0));
    else if (t < 114.6) { dx = 214; pose = 'sit'; }
    else if (t < 115.4) { dx = lerp(214, 300, seg(t, 114.6, 115.4)); flip = false; }
    else if (t < 117.0) { dx = lerp(300, 216, seg(t, 116.0, 117.0)); carry = t < 117.0 && t > 115.9; if (t < 116.0) dx = 300; }
    else { dx = 216; pose = 'sit'; }
    if (t > 117.0) slipper(g, 202, 160);
    dog(g, dx, 162, { pose, phase: t * 2.4, flip, collar: true, look: pose === 'sit' ? 'up' : 'fwd', wag: pose === 'sit' ? 1.2 : .6, carry: carry ? (cg, x, y) => slipper(cg, x - 10, y - 2) : null, eyes: t > 117.6 ? 'happy' : 'open' }, t);
    if (t > 113.3 && t < 114.6) heart(g, 206, 130, '#FF7F8C');
    if (t > 118.2) for (let i = 0; i < 3; i++) heart(g, 196 + i * 8, 128 - ((t * 8 + i * 4) % 10), '#FF7F8C');
    return { zoom: 2, x: 104, y: 70 };
  }
  // dawn: he leaves home for the city, and this time she comes too
  const camX = (t - 119.7) * 20;
  plainsBase(g, t, camX, { sky: SKIES.dawn, sunX: 300, sunY: 120, sunR: 20, pal: { a: '#6E8A5E', b: '#7A9664', hi: '#B8B88A', lo: '#56704A', ridge: '#9A8A78' }, mtn: '#7A6A94', mtn2: '#6A5C88', verge: '#5E7A4E', road: '#C2A886' });
  const wx = 150 + (t - 119.7) * 6;
  human(g, wx, 171, { age: 'man', pose: 'walk', phase: t * 1.6, bag: true, armN: 'hold', mouth: 'smile' }, t);
  rect(g, wx + 4, 160, 9, 10, INK); rect(g, wx + 5, 161, 7, 8, '#7A5236'); rect(g, wx + 7, 158, 3, 2, INK);
  dog(g, wx + 26, 171, { pose: 'walk', phase: t * 2, collar: true, wag: .8 }, t);
  fadeTo(g, '#FFFFFF', seg(t, 122.4, 123.4) * .8);
};

// ---------------------------------------------------------------- 2:03 the city flat: 九九 walks into my life again
function cityFlat(g, t, o = {}) {
  room(g, { wall: o.wall || '#F2EEE6', wallD: o.wallD || '#E6E0D4', base: o.base || '#B8A890', floor: o.floor || '#C8A27A', floorY: 150, planks: true, plankLine: o.plank || '#A88458' });
  return nineWindow(g, 208, 70, 18, 14, {
    view: (gg, x, y, w, h) => { if (o.night) { grad(gg, SKIES.night, x, y, w, h); stars(gg, t, 10, y + 20, 3, x, w); city(gg, t, y + h + 40, 40, { seed: 2 }); } else { grad(gg, SKIES.day, x, y, w, h); cloud(gg, x + 6 + (t % 40), y + 6, 18); city(gg, t, y + h + 40, 40, { seed: 2 }); } },
    frame: '#F6F6F2', frameD: '#C8C8C0', frameL: '#FFFFFF', lit: o.lit, litCol: o.litCol, litA: o.litA, dimCol: o.dimCol, dimA: o.dimA, glint: !o.night,
  });
}
SCENES.movein = (g, t, lt) => {
  cityFlat(g, t);
  // the sunlit squares under the window: her spot from now on
  for (let i = 0; i < 9; i++) { const c = i % 3, r = Math.floor(i / 3); for (let j = 0; j < 4; j++) dith(g, 200 + c * 20 - r * 6 - j * 2, 154 + r * 6 + j, 16, 1, '#FFF2C8', .6); }
  doorway(g, 112, 104, 26, 46, '#9A9A92', 1, (gg, x, y, w, h) => { rect(gg, x, y, w, h, '#8A8C94'); rect(gg, x, y + h - 10, w, 10, '#6E7078'); rect(gg, x + 4, y + 6, 6, 10, '#B8BCC8'); });
  // moving boxes
  for (const [bx, by, bw, bh] of [[146, 134, 18, 16], [150, 120, 14, 14], [168, 140, 14, 10]]) { rect(g, bx - 1, by - 1, bw + 2, bh + 2, INK); rect(g, bx, by, bw, bh, '#C99A62'); rect(g, bx, by, bw, 1, '#E2BA82'); rect(g, bx + R(bw / 2) - 1, by, 2, bh, '#B5844E'); }
  const dw = seg(t, 124.0, 127.4), lie = t > 127.6;
  const dx = t < 125.6 ? lerp(124, 176, seg(t, 124.0, 125.6)) : t < 126.2 ? 176 : lerp(176, 232, seg(t, 126.2, 127.4));
  const sniff = t > 125.6 && t < 126.2;
  dog(g, dx, 152, { pose: lie ? 'lie' : sniff ? 'stand' : dw > 0 ? 'walk' : 'stand', phase: t * 2.2, collar: true, wag: 1, eyes: lie ? 'happy' : 'open' }, t);
  if (sniff) { const k = Math.floor(t * 8) % 2; px(g, dx + 15, 146 + k, '#FFFFFF'); }
  const mw = seg(t, 124.8, 126.6), hold = t < 127.0;
  human(g, lerp(118, 190, mw), 151, { age: 'man', pose: mw > 0 && mw < 1 ? 'walk' : 'stand', phase: t * 1.8, armN: hold ? 'hold' : 'down', armF: hold ? 'hold' : 'down', mouth: 'smile', eyes: lie ? 'happy' : 'open' }, t);
  if (hold) { const hx = lerp(118, 190, mw) + 6; rect(g, hx - 1, 131, 14, 11, INK); rect(g, hx, 132, 12, 9, '#C99A62'); rect(g, hx, 132, 12, 1, '#E2BA82'); }
  else { rect(g, 199, 139, 14, 12, INK); rect(g, 200, 140, 12, 10, '#C99A62'); }
  if (lie) heart(g, 236, 132 - R(seg(t, 127.6, 128.4) * 4), '#FF7F8C');
  return { zoom: 2, x: 96, y: 60 };
};

// ---------------------------------------------------------------- 2:10 nine candles for nine years
SCENES.birthday = (g, t, lt) => {
  const n = countIn(NINE_B, t), out = t > 138.6;
  cityFlat(g, t, { night: true, wall: '#3A3E58', wallD: '#343850', base: '#2A2C3E', floor: '#5A4A44', plank: '#4A3C38' });
  const lightR = out ? 0 : 14 + n * 6 + R(Math.sin(t * 13));
  // the low table and the cake
  rect(g, 160, 146, 64, 3, '#6A4A38'); rect(g, 164, 149, 3, 8, '#4A3428'); rect(g, 217, 149, 3, 8, '#4A3428');
  rect(g, 179, 134, 26, 12, INK); rect(g, 180, 135, 24, 10, '#FFF6EE'); rect(g, 180, 139, 24, 2, '#F2B8C8');
  for (let i = 0; i < 5; i++) { rect(g, 181 + i * 5, 135, 2, 2, '#E04A4A'); }
  for (let i = 0; i < 9; i++) {
    const cx = 181 + i * 2.75, lit = i < n && !out;
    rect(g, R(cx), 129, 1, 5, i % 2 ? '#7AB8F0' : '#F2A0C0');
    if (lit) { const f = Math.floor(t * 10 + i) % 2; px(g, R(cx), 127 - f, '#FFF2A0'); px(g, R(cx), 128, '#FF9A3A'); }
  }
  if (out) for (let i = 0; i < 9; i++) { const u = (t - 138.6) * 1.2; if (u < 1.2) px(g, 181 + i * 2.75 + Math.sin(u * 6 + i) * 2, 126 - u * 14, '#B8B8C8'); }
  // him on the left, her in a party hat on the right
  human(g, 162, 152, { age: 'man', pose: 'sit', eyes: t > 136.8 ? 'happy' : 'open', mouth: t > 135.4 && t < 138 ? 'open' : 'smile', armN: 'down' }, t);
  dog(g, 224, 152, { pose: 'sit', flip: true, collar: true, hat: true, wag: 1, look: 'fwd', eyes: n >= 9 ? 'happy' : 'open', tongue: t > 139 }, t);
  if (t > 135.4 && t < 138.0) { const k = Math.floor((t - 135.4) / (BEAT * 2)); ptext(g, '♪', 168 + (k % 2) * 4, 112 - ((t * 12) % 6), { col: '#FFCB45', outline: INK }); }
  if (t > 138.2 && t < 138.7) for (let k = 0; k < 3; k++) line(g, 210 - k * 3, 128 + k * 2, 206 - k * 3, 128 + k * 2, '#E8E8F0');
  if (lightR > 0) lightPool(g, 192, 130, lightR + 20, '#FFC070', .45, 4, .8);
  if (out) grade(g, '#5A5A8A', seg(t, 138.6, 139.0) * .4);
  return { zoom: 2, x: 96, y: 66 };
};
