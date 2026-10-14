// act1.js — 0:00–1:08. The window at dawn and the title; the plain; a box of puppies; golden face, white paws;
// homework, and the paw on 九九八十一; the collar.

// ---------------------------------------------------------------- 0:00 the nine-pane window at dawn
const WIN = { x: 127, y: 16, pw: 40, ph: 28 };                     // outer size 130 × 94
const winPane = i => ({ x: WIN.x + 3 + (i % 3) * (WIN.pw + 2), y: WIN.y + 3 + Math.floor(i / 3) * (WIN.ph + 2), w: WIN.pw, h: WIN.ph });
const paneOn = i => BEATMAP.phase + (3 + 3 * i) * BEAT;           // a pane lights every three beats: 1.55 s … 11.55 s
const DAWN_STEPS = [
  ['#070A1E', '#0E1634', '#18224A', '#22305C'],
  ['#0E1434', '#1E2650', '#34386A', '#4C4878'],
  ['#1A2250', '#3A3A72', '#6E5688', '#9A6A8C'],
  ['#2A3466', '#5A5288', '#A47096', '#E0948A'],
  ['#3E4C86', '#7A6CA2', '#D08E98', '#F6B48E', '#FFD9A6'],
  ['#5878B6', '#9A94C4', '#EAAEA2', '#FFD2A0', '#FFEDC4'],
];
function rooftops(g, x, y1, w, step) {
  const cols = ['#0A0E22', '#12163A', '#1E2048', '#2C2A52', '#3C3658', '#4C4462'];
  const c = cached('roofs' + step, 124, 34, (cg) => {
    const col = cols[step];
    const shapes = [[0, 18, 22], [20, 10, 16], [34, 22, 26], [58, 14, 18], [74, 6, 22], [94, 16, 30]];
    for (const [bx, top, bw] of shapes) rect(cg, bx, top, bw, 34 - top, col);
    // rooftop water tanks and an antenna, the way every Taiwanese roof has them
    rect(cg, 24, 4, 7, 6, col); rect(cg, 25, 3, 5, 1, col); rect(cg, 26, 10, 1, 2, col); rect(cg, 29, 10, 1, 2, col);
    rect(cg, 80, 0, 1, 6, col); rect(cg, 78, 2, 5, 1, col);
    rect(cg, 100, 10, 8, 6, col); rect(cg, 101, 9, 6, 1, col);
    if (step < 4) for (let i = 0; i < 40; i++) { const xx = R(H(i * 3) * 124), yy = 14 + R(H(i * 7) * 18); if (H(i * 11) > .55 - step * .1) rect(cg, xx, yy, 1, 1, step < 2 ? '#FFD98A' : '#C8A070'); }
  });
  g.drawImage(c, R(x), R(y1) - 34);
}
function cityDawn(g, x, y, w, h, k, t) {
  const step = Math.min(5, Math.floor(k * 6));
  grad(g, DAWN_STEPS[step], x, y, w, h);
  if (step < 3) stars(g, t, 24, y + h * .55, 4, x, w);
  if (k > .62) sun(g, x + 86, y + h - 8 - (k - .62) * 70, 7, { halo: '#FFC98A', rim: '#FFE2A2', core: '#FFF6DE' });
  rooftops(g, x, y + h, w, step);
}

// the city flat's wall with the nine-pane window, the collar on the latch and the cactus; k is daylight (0 night
// → 1 sunrise), lit[i] lights pane i. Shared by the opening, the rainy night, the dawn and the ending.
function windowRoom(g, t, k, lit, o = {}) {
  const fl = o.floorY || 190;
  room(g, { wall: mix('#1C2038', '#C9B49A', k * .9), wallD: mix('#151830', '#B8A288', k * .9), base: mix('#14162A', '#8E6E50', k), floor: mix('#1A1C30', '#A8805A', k), floorY: fl, planks: true, plankLine: mix('#12142A', '#8A6444', k) });
  // the light each lit pane throws on the floor
  for (let i = 0; i < 9; i++) if (lit[i] > 0 && o.squares !== false) {
    const p = winPane(i), fy = fl + 2 + Math.floor(i / 3) * 8, fx = p.x - 34 + Math.floor(i / 3) * 10;
    for (let j = 0; j < 6; j++) dith(g, fx - j * 2, fy + j, WIN.pw, 1, o.squareCol || '#FFD9A0', lit[i] * (o.squareA || .55) * clamp(k + .2));
  }
  for (let i = 0; i < 9; i++) if (lit[i] > 0) { const p = winPane(i); glow(g, p.x + p.w / 2, p.y + p.h / 2, 30, o.glowCol || '#FFD9A0', lit[i] * .2 * clamp(k + .3)); }
  nineWindow(g, WIN.x, WIN.y, WIN.pw, WIN.ph, {
    view: o.view || ((gg, x, y, w, h) => cityDawn(gg, x, y, w, h, k, t)),
    lit, litCol: o.litCol || '#FFE6B0', litA: o.litA ?? .18, dimCol: '#0A0C20', dimA: o.dimA ?? .55, frame: mix('#2A3448', '#6E9E8E', k), frameD: mix('#1A2234', '#46705F', k), frameL: mix('#3A4860', '#94C8B4', k),
    glint: false,
  });
  if (o.panes) o.panes(g);
  // a red collar with a gold tag hangs on the latch
  const lx = WIN.x + 65, ly = WIN.y + 94 + 3;
  rect(g, lx - 1, ly - 3, 3, 3, mix('#3A3036', '#8A8A92', k));
  if (o.collar !== false) {
    const red = mix('#3A1A22', '#D8423A', k), gold = mix('#4A4030', '#FFD447', k);
    rect(g, lx - 3, ly, 1, 7, red); rect(g, lx + 3, ly, 1, 7, red); rect(g, lx - 2, ly + 7, 5, 1, red); rect(g, lx - 2, ly - 1, 5, 1, red);
    disc(g, lx, ly + 10, 2, gold);
  }
  // a little cactus on the sill
  rect(g, WIN.x + 108, WIN.y + 88, 9, 6, mix('#3A2420', '#C0704A', k)); rect(g, WIN.x + 110, WIN.y + 80, 5, 8, mix('#1C3020', '#5E9A58', k)); px(g, WIN.x + 112, WIN.y + 79, mix('#3A2030', '#FF8FA0', k));
}

SCENES.window = (g, t, lt) => {
  const k = seg(t, .5, 14);
  const lit = Array.from({ length: 9 }, (_, i) => seg(t, paneOn(i), paneOn(i) + .2));
  const memoryP = seg(t, 12.6, 13.8);                     // the middle pane starts to show the plain
  windowRoom(g, t, k, lit, {
    panes: gg => {
      if (memoryP <= 0) return;
      const p = winPane(4), mem = scratch('memory');
      drawShotInto(mem, 'plains', t);
      const mg = mem.getContext('2d'), img = mg.getImageData(p.x, p.y, p.w, p.h), d = img.data, cur = gg.getImageData(p.x, p.y, p.w, p.h), e = cur.data;
      for (let j = 0; j < p.h; j++) for (let i = 0; i < p.w; i++) if (bayer(p.x + i, p.y + j) < memoryP) { const q = (j * p.w + i) * 4; e[q] = d[q]; e[q + 1] = d[q + 1]; e[q + 2] = d[q + 2]; }
      gg.putImageData(cur, p.x, p.y);
    },
  });
  // the title: one character per pane, with the last four panes
  [...'几分之几'].forEach((ch, j) => {
    const a = seg(t, paneOn(5 + j), paneOn(5 + j) + .25); if (a <= 0) return;
    ptext(g, ch, 156 + j * 24, 130 - R((1 - eout(a)) * 6), { size: 24, col: '#FFF3D6', outline: INK, shadow: '#C9A070' });
  });
  const sub = seg(t, 12.2, 12.8);
  if (sub > 0) ptext(g, '一个男孩和一只狗的十五年', PW / 2, 160, { col: mix('#6E6070', '#F2DFC0', sub), outline: INK });
  // the middle pane opens into the memory
  const open = seg(t, 14.2, 15.95);
  if (open > 0) {
    const p = winPane(4), e = eio(open), x0 = R(lerp(p.x, 0, e)), y0 = R(lerp(p.y, 0, e)), x1 = R(lerp(p.x + p.w, PW, e)), y1 = R(lerp(p.y + p.h, PH, e));
    const mem = scratch('memory'); drawShotInto(mem, 'plains', t);
    g.drawImage(mem, x0, y0, x1 - x0, y1 - y0, x0, y0, x1 - x0, y1 - y0);
    rect(g, x0 - 2, y0 - 2, x1 - x0 + 4, 2, '#6E9E8E'); rect(g, x0 - 2, y1, x1 - x0 + 4, 2, '#6E9E8E'); rect(g, x0 - 2, y0, 2, y1 - y0, '#6E9E8E'); rect(g, x1, y0, 2, y1 - y0, '#6E9E8E');
  }
  fadeTo(g, '#000000', 1 - seg(t, 0, 1.4));
};
// render another shot into a scratch canvas (used for windows into other times)
function drawShotInto(c, name, t) {
  const sh = SHOTS.find(s => s.name === name), gg = c.getContext('2d');
  gg.save(); SCENES[name](gg, t, t - sh.t0, sh); gg.restore();
}

// ---------------------------------------------------------------- the plain (shared with later shots)
const PAL_GOLD = { a: '#8EAA48', b: '#9DB650', hi: '#D8DC80', lo: '#6F8C3A', ridge: '#BBA86C' };
function plainsBase(g, t, camX, o = {}) {
  const hy = o.hy || 118;
  grad(g, o.sky || SKIES.golden, 0, 0, PW, hy);
  if (o.clouds !== false) { streak(g, 30 - camX * .02, 40, 70, '#F7D7B0'); streak(g, 280 - camX * .02, 28, 50, '#F8E2C2'); streak(g, 150 - camX * .02, 62, 90, '#F6C49A'); streak(g, 330 - camX * .02, 78, 40, '#F2B48C'); }
  if (o.sky2) o.sky2(g);
  mountains(g, hy, camX, o.mtn || '#C2A6BC', o.mtn2 || '#B094B0');
  if (o.sun !== false) sun(g, (o.sunX ?? 252) - camX * .05, o.sunY ?? hy + 6, o.sunR || 36, { halo: '#FFC878', rim: '#FFE3A0', core: '#FFF6DA' });
  hamlets(g, hy, camX, o.ham || '#4E6A3A', o.ham2 || '#5E7E44', '#A85A44');
  rect(g, 0, hy - 1, PW, 1, o.glare || '#FFE6A8');
  paddies(g, t, hy, o.roadY || 160, camX, o.pal || PAL_GOLD, o.wind || 1);
  if (o.sun !== false) { const gx = (o.sunX ?? 252) - camX * .05; for (let j = 0; j < 14; j++) dith(g, gx - 30 + j * 2, hy + j * 3, 60 - j * 4, 2, '#FFE9A8', .45 - j * .03); }
  if (o.poles !== false) poles(g, camX, o.roadY || 160, 120, o.pole || '#5A4636', o.wire || '#3A2E26', 50);
  const ry = o.roadY || 160;
  rect(g, 0, ry, PW, 12, o.road || '#D6B985'); rect(g, 0, ry, PW, 1, '#B8986A'); rect(g, 0, ry + 11, PW, 1, '#B8986A');
  for (let x = -((R(camX) % 9) + 9) % 9; x < PW; x += 9) { px(g, x, ry + 4, '#C4A574'); px(g, x + 4, ry + 8, '#C4A574'); }
  rect(g, 0, ry + 12, PW, PH - ry - 12, o.verge || '#74913F');
  dith(g, 0, ry + 12, PW, 6, '#5E7A34', .5);
  grassTufts(g, t, ry + 20, '#5E7A34', '#9DB85A', 2, o.wind || 1, camX);
  grassTufts(g, t, PH - 6, '#56722F', '#8FAE4E', 5, o.wind || 1, camX * 1.3);
}
function scooter(g, x, gy, t, riders) {
  x = R(x); const b = Math.floor(t * 6) % 2 ? 0 : -1, y = gy + b;
  const red = '#C8473C', redD = '#9A3028', redL = '#E56A58';
  disc(g, x - 11, gy - 4, 4, INK); disc(g, x - 11, gy - 4, 3, '#3A3A44'); px(g, x - 11, gy - 4, '#B8BCC8');
  disc(g, x + 12, gy - 4, 4, INK); disc(g, x + 12, gy - 4, 3, '#3A3A44'); px(g, x + 12, gy - 4, '#B8BCC8');
  poly(g, [[x - 18, y - 13], [x - 2, y - 13], [x - 2, y - 6], [x - 16, y - 5]], INK);
  poly(g, [[x - 17, y - 12], [x - 3, y - 12], [x - 3, y - 7], [x - 15, y - 6]], red); rect(g, x - 16, y - 12, 12, 1, redL); rect(g, x - 16, y - 8, 13, 1, redD);
  rect(g, x - 16, y - 15, 13, 3, INK); rect(g, x - 15, y - 14, 11, 2, '#2A2A30');
  rect(g, x - 3, y - 7, 11, 3, INK); rect(g, x - 2, y - 6, 9, 1, '#9AA0AC');
  riders && riders(x, y);
  rect(g, x + 7, y - 20, 6, 16, INK); rect(g, x + 8, y - 19, 4, 14, red); rect(g, x + 8, y - 19, 1, 14, redL);
  rect(g, x + 4, y - 22, 9, 2, INK); rect(g, x + 12, y - 17, 3, 3, INK); rect(g, x + 13, y - 16, 2, 1, '#FFF2B0');
  rect(g, x + 9, y - 5, 6, 2, INK); rect(g, x + 10, y - 5, 4, 1, redD);
}

SCENES.plains = (g, t, lt) => {
  const sx = -40 + Math.max(0, t - 17.2) * 34, camX = Math.max(lt * 3, sx - 176);
  const wind = 1 + 1.4 * seg(t, 22.4, 24.5);
  plainsBase(g, t, camX, { wind });
  for (let i = 0; i < 3; i++) { const ex = 420 - ((t - 16) * (14 + i * 3) + i * 70) - camX * .2, ey = 46 + i * 13 + Math.sin(t + i) * 2; if (ex > -10 && ex < PW + 10) egret(g, ex, ey, t + i * .3); }
  const x = sx - camX;
  if (x > -40 && x < PW + 40) scooter(g, x, 170, t, (X, Y) => {
    human(g, X - 9, Y - 13, { age: 'man', outfit: 'dad', pose: 'sit', armN: 'fwd', armF: 'fwd', helmet: '#D8423A', mouth: 'smile' }, t);
    human(g, X + 3, Y - 6, { age: 'kid', armN: t > 23.6 ? 'up' : 'fwd', armF: 'fwd', helmet: '#F2C84A', mouth: t > 23.6 ? 'open' : 'smile', eyes: t > 23.6 ? 'happy' : 'open', blush: true }, t);
  });
  // the wind made visible: a few seeds and petals drifting across
  if (wind > 1.2) for (let i = 0; i < 14; i++) { const u = ((t * (40 + i * 6) + i * 53) % (PW + 40)) - 20, v = 70 + (i * 37) % 90 + Math.sin(t * 3 + i) * 4; px(g, u, v, i % 3 ? '#FFF3D6' : '#F7C2C8'); }
};

// ---------------------------------------------------------------- the courtyard: a box of puppies under the banyan
const MOTHER = { fur: '#3A3230', furL: '#56494A', furD: '#272022', cream: '#C99A62', white: '#C99A62', whiteD: '#A07A4E' };
function courtyard(g, t, o = {}) {
  grad(g, o.sky || ['#6E9ED0', '#A6C4E0', '#F2D8AA', '#F6BC76'], 0, 0, PW, 92);
  hamlets(g, 92, 0, '#56703E', '#688A4A', '#A85A44', 9);
  rect(g, 0, 92, PW, 46, '#8FAA4E'); dith(g, 0, 92, PW, 46, '#A6BE5C', .3);
  rect(g, 0, 134, PW, PH - 134, '#D4C09C');
  for (let x = 0; x < PW; x += 32) rect(g, x, 134, 1, PH - 134, '#C2AC84');
  for (let y = 150; y < PH; y += 22) rect(g, 0, y, PW, 1, '#C2AC84');
  farmhouse(g, 170, 70);
  for (let j = 0; j < 22; j++) { const w = R(70 * Math.sqrt(1 - Math.pow((j - 11) / 11, 2))); dith(g, 92 - w, 148 + j, w * 2, 1, '#A89070', .45); }   // the banyan's shade
  // potted plants and a water jar by the house
  for (const [px0, c] of [[176, '#4E8A44'], [190, '#6EAA52'], [330, '#4E8A44']]) { rect(g, px0, 128, 8, 6, '#B0603E'); disc(g, px0 + 4, 124, 5, c); }
  ellipse(g, 346, 128, 9, 8, '#5E5A66'); ellipse(g, 346, 122, 8, 2, '#3A3A48'); rect(g, 338, 121, 17, 1, '#8A8696');
  banyan(g, 78, 150, t);
  if (o.chickens !== false) for (let i = 0; i < 3; i++) chicken(g, 236 + i * 30 + Math.sin(t * .4 + i) * 10, 170 + (i % 2) * 7, t + i * 1.7, i % 2 === 0);
}
// a chicken that pecks at the ground now and then
function chicken(g, x, y, t, flip) {
  const peck = Math.sin(t * 2.3) > .7;
  outlined(g, x - 8, y - 12, 16, 14, cg => {
    const f = v => flip ? 15 - v : v, P = (a, b, w, h, c) => rect(cg, flip ? 16 - a - w : a, b, w, h, c);
    P(3, 5, 8, 5, '#FFFFFF'); P(2, 4, 3, 3, '#F2F2F2'); P(4, 9, 6, 1, '#E2E2E2');
    if (peck) { P(10, 8, 3, 3, '#FFFFFF'); P(13, 10, 1, 1, '#F2A93A'); P(11, 7, 1, 1, '#E04A3A'); }
    else { P(10, 2, 3, 4, '#FFFFFF'); P(13, 3, 1, 1, '#F2A93A'); P(11, 1, 1, 1, '#E04A3A'); P(11, 3, 1, 1, INK); }
    P(5, 10, 1, 2, '#F2A93A'); P(8, 10, 1, 2, '#F2A93A');
  });
}
function puppyBox(g, x, y, t, pups = 3, frontOnly = false) {
  const cols = [['#3A3434', '#24201F'], ['#9A6A44', '#6E4A2E'], ['#EDE6DA', '#C9BFAE']];
  outlined(g, x - 8, y - 14, 46, 32, cg => {
    if (!frontOnly) rect(cg, 8, 14, 30, 4, '#B5844E');     // the back wall of the box
    for (let i = 0; i < pups; i++) {
      const hx = 12 + i * 8, bob = R(Math.sin(t * 5 + i * 2) * 1.2), hy = 10 + bob, [c, d] = cols[i];
      rect(cg, hx, hy, 7, 6, c); rect(cg, hx + 1, hy - 1, 5, 1, c); rect(cg, hx, hy, 2, 3, d); rect(cg, hx + 5, hy, 2, 3, d);
      px(cg, hx + 2, hy + 2, INK); px(cg, hx + 4, hy + 2, INK); px(cg, hx + 3, hy + 4, '#2A1A12');
    }
    rect(cg, 8, 17, 30, 14, '#C99A62'); rect(cg, 8, 17, 30, 1, '#E2BA82'); rect(cg, 8, 30, 30, 1, '#A87C48');
    poly(cg, [[8, 17], [1, 12], [3, 11], [9, 15]], '#B98A52'); poly(cg, [[38, 17], [45, 13], [44, 11], [37, 15]], '#B98A52');
    rect(cg, 18, 22, 10, 4, '#B07E48');
  });
}
SCENES.litter = (g, t, lt) => {
  courtyard(g, t);
  dog(g, 26, 168, { pose: 'lie', fur: MOTHER, eyes: t % 6 < 3 ? 'closed' : 'open', wag: .3 }, t);
  // dad and the farmer chat by the house
  human(g, 296, 150, { age: 'man', outfit: 'dad', look: 'front', mouth: Math.floor(t * 3) % 2 ? 'open' : 'smile', armN: 'down' }, t);
  human(g, 320, 150, { age: 'man', outfit: 'farmer', flip: true, hat: 'straw', armN: Math.floor(t * 1.5) % 2 ? 'wave' : 'down', grey: true }, t + 1);
  const hop = seg(t, 31.0, 31.6), walk = seg(t, 31.6, 34.0), inBox = t < 31.0;
  puppyBox(g, 52, 152, t, 3);
  const boyX = 132, boyY = 174;
  // the yellow one: in the box, hops out, waddles over, sits at his sneakers
  if (inBox) {
    const bob = R(Math.sin(t * 6) * 1.5);
    dog(g, 76, 150 + bob, { size: 'pup', pose: 'beg', wag: 1 }, t);
    puppyBox(g, 52, 152, t, 0, true);                        // the front of the box hides its legs
  } else {
    let x, y, pose = 'walk';
    if (hop < 1) { x = lerp(78, 92, hop); y = lerp(150, 172, hop) - Math.sin(hop * Math.PI) * 10; pose = 'jump'; }
    else if (walk < 1) { x = lerp(92, boyX - 14, walk); y = 172 + (walk < .08 ? 0 : 0); }
    else { x = boyX - 14; y = 172; pose = 'sit'; }
    const up = t > 34.3;
    dog(g, x, y, { size: 'pup', pose, phase: (t - 31.6) * 2.2, wag: pose === 'sit' ? 1.4 : .6, look: up ? 'up' : 'fwd', eyes: t > 35.9 ? 'happy' : 'open' }, t);
    if (t > 35.4 && t < 37.6) heart(g, x + 2, y - 16 - R(seg(t, 35.4, 36.2) * 3), '#FF7F8C');
  }
  human(g, boyX, boyY, { age: 'kid', pose: 'squat', flip: true, eyes: t > 35.8 ? 'happy' : 'open', mouth: t > 35.8 ? 'smile' : null, blush: t > 35.8, armN: 'hold' }, t);
  // no words needed: a bubble with three dots that never become words
  if (t > 34.4 && t < 37.0) bubble(g, boyX - 2, boyY - 24, 22, 10, (bx, by) => { const n = Math.min(3, Math.floor((t - 34.4) / .35) + 1); for (let i = 0; i < n; i++) rect(g, bx + 5 + i * 5, by + 4, 2, 2, INK); });
  // a banyan leaf drifts down onto the puppy's head
  const lf = seg(t, 37.4, 39.6);
  if (lf > 0) { const lx = lerp(70, boyX - 13, lf) + Math.sin(lf * 9) * 6, ly = lerp(96, 160, lf); rect(g, lx, ly, 3, 2, '#6FA04A'); px(g, lx + 3, ly, '#4E7A34'); }
  // the song holds its breath: the iris closes on the two of them
  const ir = seg(t, 39.8, 41.9);
  if (ir > 0) iris(g, boyX - 10, 160, lerp(260, 0, eio(ir)));
};

// ---------------------------------------------------------------- 0:42 the golden side face, then the white "sneakers"
const BIG = { fur: '#E2A33C', furL: '#F7CD72', furD: '#B8772D', cream: '#FBE8BE', white: '#FFFFFF', whiteD: '#D6DAE6', nose: '#2A1A12', pink: '#E9A08A' };
function rimPass(cg, w, h, dx, dy, col, col2) {
  const img = cg.getImageData(0, 0, w, h), d = img.data, a = i => d[i * 4 + 3] > 0;
  const c = hex(col), c2 = col2 && hex(col2), mark = new Uint8Array(w * h);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = y * w + x; if (!a(i)) continue;
    const x1 = x + dx, y1 = y + dy, out1 = x1 < 0 || y1 < 0 || x1 >= w || y1 >= h || !a(y1 * w + x1);
    const x2 = x + 2 * dx, y2 = y + 2 * dy, out2 = x2 < 0 || y2 < 0 || x2 >= w || y2 >= h || !a(y2 * w + x2);
    if (out1) mark[i] = 1; else if (out2 && c2) mark[i] = 2;
  }
  for (let i = 0; i < w * h; i++) if (mark[i]) { const cc = mark[i] === 1 ? c : c2; d[i * 4] = cc[0]; d[i * 4 + 1] = cc[1]; d[i * 4 + 2] = cc[2]; }
  cg.putImageData(img, 0, 0);
}
// the big puppy, facing right, in a 384 × 432 frame: round head at the top, chubby body, short legs,
// white paws with a grey "sole" so they look like little sneakers, standing on the ground at y ≈ 400
function bigPuppy(blink, pawUp) {
  return cached('bigpup' + blink + pawUp, 384, 432, (cg) => {
    const F = BIG;
    const paw = (x, y, rx, col, sole) => { ellipse(cg, x, y, rx, 12, col); rect(cg, x - rx + 3, y + 8, rx * 2 - 6, 2, sole); for (const k of [-.4, 0, .4]) rect(cg, R(x + k * rx), y - 6, 1, 7, sole); };
    // far legs (darker)
    poly(cg, [[98, 318], [132, 318], [128, 386], [104, 386]], F.furD); paw(116, 388, 19, F.whiteD, '#B8BCCB');
    poly(cg, [[222, 280], [256, 280], [252, 384], [228, 384]], F.furD); paw(240, 386, 20, F.whiteD, '#B8BCCB');
    // body, haunch, chest
    ellipse(cg, 126, 262, 98, 64, F.fur); ellipse(cg, 110, 222, 70, 20, F.furL);
    ellipse(cg, 74, 300, 42, 46, F.fur); poly(cg, [[46, 318], [98, 318], [92, 388], [52, 388]], F.fur); paw(72, 390, 26, F.white, '#C6CAD6');
    ellipse(cg, 212, 220, 60, 58, F.fur); ellipse(cg, 244, 232, 26, 42, F.cream);
    const py = pawUp ? -9 : 0;
    poly(cg, [[172, 262], [220, 262], [214, 388 + py], [180, 388 + py]], F.fur); poly(cg, [[174, 262], [180, 262], [184, 388 + py], [182, 388 + py]], F.furL); paw(198, 392 + py, 27, F.white, '#C6CAD6');
    // head
    poly(cg, [[250, 82], [276, 34], [292, 96]], F.furD);
    ellipse(cg, 232, 122, 64, 56, F.fur); ellipse(cg, 216, 92, 40, 22, F.furL);
    ellipse(cg, 286, 150, 30, 20, F.cream); ellipse(cg, 252, 158, 30, 22, F.cream);
    poly(cg, [[182, 94], [200, 24], [240, 78]], F.fur); poly(cg, [[194, 84], [204, 42], [228, 78]], F.pink); poly(cg, [[196, 32], [212, 28], [214, 46]], F.furD);
    rect(cg, 306, 132, 16, 12, F.nose); rect(cg, 308, 130, 12, 2, F.nose); rect(cg, 309, 134, 5, 2, '#5A4A40');
    line(cg, 314, 144, 312, 154, F.nose); line(cg, 312, 154, 292, 158, F.nose);
    rect(cg, 296, 158, 9, 7, '#F27D8E'); rect(cg, 300, 160, 1, 4, '#D45E70');
    if (blink) rect(cg, 260, 116, 18, 3, F.nose);
    else { ellipse(cg, 268, 112, 9, 11, F.nose); rect(cg, 263, 104, 5, 5, '#FFFFFF'); rect(cg, 272, 117, 3, 3, '#FFFFFF'); }
    for (const [x, y] of [[254, 96], [259, 95], [264, 95], [269, 96]]) px(cg, x, y, F.furD);
    ellipse(cg, 240, 136, 6, 3, '#F4A88E');
    for (let i = 0; i < 160; i++) { const x = 40 + R(H(i) * 260), y = 70 + R(H(i * 3) * 260); const id = cg.getImageData(x, y, 1, 1).data; if (id[3] && id[0] > 200 && id[2] < 120) px(cg, x, y, H(i * 7) > .5 ? F.furD : F.furL); }
    rimPass(cg, 384, 432, -1, -1, '#FFF6C8', '#FCE08E');
    outlinePass(cg, 384, 432, '#5A3418');
  });
}
SCENES.paws = (g, t, lt) => {
  const vy = R(216 * eio(seg(t, 45.3, 46.5)));
  const bg = cached('pawsBg', 384, 432, (cg) => {
    const img = gradImage(384, 300, ['#E58A5A', '#F4A764', '#F9C47E', '#FCDDA2', '#FFEFC8']); cg.putImageData(img, 0, 0);
    sun(cg, 108, 120, 44, { halo: '#FFD58C', rim: '#FFEBB4', core: '#FFFBEA' });
    hamlets(cg, 300, 0, '#B07A52', '#C48E62', '#A65440', 11);
    rect(cg, 0, 300, 384, 132, '#D9C29C'); dith(cg, 0, 300, 384, 20, '#E8D2A8', .5);
    for (let y = 330; y < 432; y += 26) rect(cg, 0, y, 384, 1, '#C7AE86');
    dith(cg, 0, 396, 384, 18, '#B49A74', .5);
  });
  g.drawImage(bg, 0, -vy);
  // flare dots from the sun
  for (let i = 1; i <= 3; i++) glow(g, 108 + i * 50, 120 - vy + i * 34, 4 + i * 2, '#FFF2C8', .25);
  const blink = t > 43.7 && t < 43.85, pawUp = (t > 47.5 && t < 47.8) || (t > 48.3 && t < 48.6);
  g.drawImage(bigPuppy(blink, pawUp), 0, -vy);
  // the boy's white sneakers, toes towards the puppy
  outlined(g, 262, 216 - vy, 122, 200, cg => {
    const sneaker = (ox, oy, dim) => {
      const W = dim ? '#E2E4EC' : '#FFFFFF', Wd = dim ? '#C2C6D2' : '#D6DAE6';
      rect(cg, ox + 36, -2, 28, oy - 40, dim ? '#DDA67E' : SKIN); rect(cg, ox + 36, -2, 5, oy - 40, dim ? '#C99070' : SKIN_D); rect(cg, ox + 36, oy - 46, 30, 20, dim ? '#E6E6EA' : '#F6F6F8');
      poly(cg, [[ox + 2, oy + 2], [ox + 8, oy - 22], [ox + 40, oy - 30], [ox + 66, oy - 26], [ox + 70, oy + 2]], W);
      rect(cg, ox, oy - 2, 72, 6, Wd); rect(cg, ox, oy + 3, 72, 2, '#A9AEBB');
      for (let i = 0; i < 4; i++) rect(cg, ox + 16 + i * 6, oy - 24 + i, 5, 1, '#9AA0B0');
      rect(cg, ox + 4, oy - 8, 10, 1, Wd);
    };
    sneaker(36, 178, true); sneaker(10, 184, false);
  });
  for (let i = 0; i < 12; i++) { const mx = (i * 37 + t * 9) % 384, my = (i * 53 - t * 6 + 432) % 300; if (my - vy > -5) px(g, mx, my - vy, '#FFF6D8'); }
  if (pawUp) heart(g, 230, 340 - vy, '#FF7F8C');
};

// ---------------------------------------------------------------- 0:49 the world keeps working; he does his homework
SCENES.homework = (g, t, lt) => {
  room(g, { wall: '#EBDDBF', wallD: '#E4D3B2', base: '#9C7652', floor: '#B8B2A0', floorY: 150, terrazzo: true });
  // kitchen door: mum at the stove, steam rising
  rect(g, 30, 84, 56, 66, '#8A6C50'); rect(g, 33, 87, 50, 63, '#6E5A48'); rect(g, 33, 124, 50, 26, '#7A6656');
  rect(g, 38, 118, 40, 7, '#4A4A52'); rect(g, 50, 110, 14, 8, '#B8BCC8'); rect(g, 48, 110, 18, 1, '#8A8E9A');
  for (let i = 0; i < 4; i++) { const u = ((t * .7 + i * .25) % 1); disc(g, 57 + Math.sin(u * 8 + i) * 3, 106 - u * 22, 1 + R(u * 2), '#F2F2F6'); }
  human(g, 70, 148, { age: 'man', outfit: 'mom', long: true, flip: true, armN: Math.floor(t * 2) % 2 ? 'fwd' : 'hold', armF: 'fwd' }, t);
  // TV cabinet, the cartoon flickers
  rect(g, 96, 122, 30, 28, '#8C5E3A'); rect(g, 98, 124, 26, 11, '#A0714A'); rect(g, 98, 137, 26, 11, '#A0714A');
  rect(g, 99, 104, 24, 18, '#3A3A44'); rect(g, 101, 106, 20, 13, ['#6FA8D8', '#F2C84A', '#78B0DC', '#E87A6A'][Math.floor(t * 3) % 4]); rect(g, 108, 100, 1, 4, '#3A3A44'); rect(g, 113, 98, 1, 6, '#3A3A44');
  // clock: the second hand ticks on every beat
  disc(g, 160, 80, 8, INK); disc(g, 160, 80, 7, '#FFFDF4');
  for (let k = 0; k < 12; k++) px(g, 160 + R(Math.cos(k * Math.PI / 6) * 5), 80 + R(Math.sin(k * Math.PI / 6) * 5), '#8A7A6A');
  line(g, 160, 80, 160, 75, INK); line(g, 160, 80, 163, 81, INK);
  const sa = beatAt(t) * Math.PI / 30 - Math.PI / 2; line(g, 160, 80, 160 + R(Math.cos(sa) * 6), 80 + R(Math.sin(sa) * 6), '#D8423A');
  // window with iron bars and a tree that sways in the wind
  rect(g, 236, 80, 46, 40, '#6E9E8E'); grad(g, SKIES.day, 239, 83, 40, 34);
  const sway = R(Math.sin(t * 1.8) * 2);
  disc(g, 258 + sway, 104, 12, '#4E8A44'); disc(g, 252 + sway, 99, 7, '#6EAA52'); rect(g, 257, 110, 3, 7, '#6A4A32');
  for (let x = 242; x < 280; x += 5) rect(g, x, 83, 1, 34, '#3D5E58');
  rect(g, 234, 120, 50, 2, '#86C2B0');
  // calendar
  rect(g, 290, 86, 16, 20, INK); rect(g, 291, 87, 14, 18, '#FFFDF4'); rect(g, 291, 87, 14, 4, '#D8423A'); px(g, 297, 96, '#3A3A44'); px(g, 298, 96, '#3A3A44'); px(g, 298, 97, '#3A3A44'); px(g, 297, 98, '#3A3A44'); px(g, 298, 99, '#3A3A44');
  // ceiling fan
  rect(g, 191, 60, 2, 4, '#7A6A5A'); disc(g, 192, 65, 2, '#B8AE9C');
  if (Math.floor(t * 12) % 2) rect(g, 176, 66, 33, 1, '#C8BCA4'); else { rect(g, 184, 65, 17, 2, '#C8BCA4'); }
  // ants marching along the skirting board, each carrying a crumb
  for (let i = 0; i < 7; i++) { const ax = ((t * 8 + i * 9) % 90) + 214; px(g, ax, 148, '#2A2420'); px(g, ax + 1, 148, '#2A2420'); if (i % 2 === 0) px(g, ax + 1, 147, '#FFF6E2'); }
  // the low table, the boy writing, the puppy napping beside him
  const wake = t > 53.6, leap = seg(t, 54.8, 55.6);
  if (leap <= 0) dog(g, 236, 156, { size: 'pup', pose: wake ? 'sit' : 'sleep', look: wake ? 'up' : 'fwd', wag: wake ? 1.2 : 0, flip: true }, t);
  human(g, 192, 150, { age: 'kid', look: 'front', armN: Math.floor(t * 5) % 2 ? 'hold' : 'fwd', armF: 'hold', eyes: t % 4 < .2 ? 'closed' : 'open' }, t);
  rect(g, 162, 146, 66, 3, '#7A4E30'); rect(g, 162, 146, 66, 1, '#A0714A'); rect(g, 166, 149, 3, 9, '#6A4228'); rect(g, 221, 149, 3, 9, '#6A4228');
  rect(g, 180, 144, 20, 2, '#FFFDF4'); rect(g, 203, 142, 1, 3, '#F2C84A');
  if (leap > 0) dog(g, lerp(236, 214, leap), lerp(156, 146, leap) - Math.sin(leap * Math.PI) * 10, { size: 'pup', pose: 'jump', flip: true, wag: 1 }, t);
  for (let j = 0; j < 14; j++) dith(g, 238 - j * 2 - lt, 152 + j, 30, 1, '#FFF2C8', .35);
  // the camera drifts from the kitchen to the table
  return { zoom: 2, x: lerp(20, 112, eio(seg(t, 49.4, 54.2))), y: 62 };
};

// ---------------------------------------------------------------- 0:56 九九乘法表, and a paw on 九九八十一
const NINES = ['一九得九', '二九十八', '三九二十七', '四九三十六', '五九四十五', '六九五十四', '七九六十三', '八九七十二', '九九八十一'];
function pencilHand(g, x, y) {
  x = R(x); y = R(y);
  outlined(g, x - 4, y - 40, 40, 44, cg => {
    for (let k = 0; k < 26; k++) { rect(cg, 4 + k * .6, 38 - k * 1.2, 3, 2, '#F2C84A'); }
    rect(cg, 19, 6, 4, 4, '#F29CA8'); rect(cg, 3, 37, 3, 3, '#E8C8A0'); px(cg, 4, 40, '#3A3A44');
    ellipse(cg, 14, 26, 9, 7, SKIN); rect(cg, 8, 30, 8, 2, SKIN_D);
  });
}
SCENES.paper = (g, t, lt) => {
  rect(g, 0, 0, PW, PH, '#9A6A44'); for (let y = 3; y < PH; y += 7) rect(g, 0, y, PW, 1, '#8C5E3A');
  rect(g, 104, 0, 184, PH, '#7E5636');
  rect(g, 100, 0, 184, PH, '#FBF5E4');
  for (let y = 36; y < PH; y += 15) rect(g, 100, y, 184, 1, '#C6D7EC');
  rect(g, 124, 0, 1, PH, '#EDA8A8');
  ptext(g, '九九乘法表', 192, 8, { col: '#4A4A58' }); rect(g, 158, 22, 68, 1, '#4A4A58');
  const start = 56.0, step = BEAT / 2;
  let hand = null;
  NINES.forEach((s, i) => {
    const a = seg(t, start + i * step, start + i * step + step * .9); if (a <= 0) return;
    const y = 24 + 15 * (i + 1) - 13, full = textW(s), wv = R(full * a);
    g.save(); g.beginPath(); g.rect(132, y - 2, wv, 16); g.clip(); ptext(g, s, 132, y, { col: '#4A4A58', align: 'left' }); g.restore();
    if (a < 1) hand = [132 + wv, y + 11];
  });
  const lastY = 24 + 15 * 9 - 13;
  // the puppy peeks over the edge of the table, then the paw comes down on the last line
  const peek = seg(t, 57.9, 58.6) - seg(t, 61.9, 62.4);
  if (peek > 0) outlined(g, 186, PH - R(22 * eout(peek)), 52, 30, cg => {
    rect(cg, 2, 2, 6, 10, BIG.fur); rect(cg, 44, 2, 6, 10, BIG.fur); px(cg, 4, 1, BIG.furD); px(cg, 46, 1, BIG.furD);
    ellipse(cg, 26, 18, 22, 14, BIG.fur); ellipse(cg, 26, 24, 10, 6, BIG.cream);
    rect(cg, 17, 13, 3, 4, INK); rect(cg, 32, 13, 3, 4, INK); px(cg, 17, 13, '#FFFFFF'); px(cg, 32, 13, '#FFFFFF'); rect(cg, 24, 21, 5, 3, INK);
  });
  const stampT = 59.32, down = seg(t, stampT - .25, stampT), up = seg(t, stampT + .35, stampT + .7);
  if (t > stampT) { for (const [dx, dy, r] of [[0, 0, 7], [-9, -9, 3], [-3, -12, 3], [4, -12, 3], [10, -9, 3]]) { disc(g, 160 + dx, lastY + 8 + dy, r, '#C49A6A'); glow(g, 160 + dx, lastY + 8 + dy, r + 1, '#B08458', .5); } }
  if (down > 0 && up < 1) {
    const py = lerp(PH + 10, lastY - 6, eout(down)) + lerp(0, PH, ein(up));
    outlined(g, 136, py - 20, 48, 52, cg => { ellipse(cg, 24, 24, 20, 16, '#FFFFFF'); ellipse(cg, 24, 48, 16, 14, BIG.fur); for (const tx of [16, 24, 32]) rect(cg, tx, 8, 1, 8, '#D6DAE6'); });
  }
  // the boy circles 九九 and writes the name next to it
  const circ = seg(t, 60.4, 61.0), write = seg(t, 61.1, 61.8);
  if (circ > 0) { const n = R(circ * 40); for (let k = 0; k < n; k++) { const a = k / 40 * Math.PI * 2 - 2; px(g, 146 + Math.cos(a) * 18, lastY + 6 + Math.sin(a) * 9, '#E0503A'); } }
  if (write > 0) {
    g.save(); g.beginPath(); g.rect(190, lastY - 18, R(64 * write), 20); g.clip();
    ptext(g, '就叫九九！', 192, lastY - 16, { col: '#E0503A', align: 'left' }); g.restore();
  }
  if (t > 61.8) heart(g, 262, lastY - 10, '#E0503A');
  if (circ > 0 && circ < 1) hand = [146 + Math.cos(circ * Math.PI * 2 - 2) * 18, lastY + 6 + Math.sin(circ * Math.PI * 2 - 2) * 9];
  if (write > 0 && write < 1) hand = [192 + 60 * write, lastY - 4];
  if (hand) pencilHand(g, hand[0], hand[1]);
};

// ---------------------------------------------------------------- 1:02 a red collar, a tag that says 九九
SCENES.collar = (g, t, lt) => {
  if (t < 65.3) {
    rect(g, 0, 0, PW, PH, BIG.fur);
    for (let i = 0; i < 90; i++) { const x = R(H(i) * PW), y = R(H(i * 3) * PH), l = 6 + R(H(i * 5) * 10); line(g, x, y, x + 3, y + l, H(i * 7) > .5 ? BIG.furD : BIG.furL); }
    poly(g, [[0, 70], [PW, 62], [PW, 84], [0, 92]], INK); poly(g, [[0, 72], [PW, 64], [PW, 82], [0, 90]], '#D8423A');
    for (let x = 4; x < PW; x += 6) { px(g, x, 75 - R(x * 8 / PW), '#F2A0A0'); px(g, x, 86 - R(x * 8 / PW), '#F2A0A0'); }
    const rx = 192, ry = 86;
    disc(g, rx, ry + 4, 7, INK); disc(g, rx, ry + 4, 6, '#C9CED8'); disc(g, rx, ry + 4, 3, '#D8423A');
    const u = t - 62.4, ang = .32 * Math.sin(u * 4.6) * Math.exp(-u * .5) + .05 * Math.sin(u * 9) * (lastKick(t) > t - .2 ? 1 : 0);
    const tx = rx + Math.sin(ang) * 40, ty = ry + 4 + Math.cos(ang) * 40;
    line(g, rx, ry + 8, tx, ty - 30, '#B8BCC8');
    disc(g, tx, ty, 33, INK); disc(g, tx, ty, 32, '#D8A42A'); disc(g, tx - 1, ty - 1, 30, '#FFD447');
    for (let k = 0; k < 16; k++) { const a = -2.4 + k * .09; px(g, tx + Math.cos(a) * 26, ty + Math.sin(a) * 26, '#FFF2A8'); }
    ptext(g, '九九', tx, ty - 13, { size: 24, col: '#9A6A1A', shadow: '#FFF2A8' });
    const bx = rx + 18, by = ry + 14 + R(Math.sin(u * 6) * 2);
    disc(g, bx, by, 6, INK); disc(g, bx, by, 5, '#F2C84A'); rect(g, bx - 3, by + 1, 7, 1, '#9A6A1A'); px(g, bx - 2, by - 2, '#FFF6C8');
    if (beatPhase(t) < .18) { sparkle(g, tx + 16, ty - 16, 2); sparkle(g, bx + 7, by - 6, 1); }
    vignette(g, '#5A2E10', .6);
    return;
  }
  // the courtyard: the puppy chases its own tail, the bell rings on every kick
  courtyard(g, t);
  const u = t - 65.3, a = u * 5.5, x = 196 + Math.cos(a) * 10, y = 176 + Math.sin(a) * 3;
  dog(g, x, y, { size: 'pup', pose: 'run', phase: u * 3, flip: Math.sin(a) > 0, collar: true, wag: 2, tongue: true }, t);
  human(g, 160, 178, { age: 'kid', look: 'front', eyes: 'happy', mouth: 'open', blush: true, armN: Math.floor(t * 4) % 2 ? 'up' : 'wave', armF: Math.floor(t * 4) % 2 ? 'wave' : 'up' }, t);
  human(g, 300, 150, { age: 'man', outfit: 'dad', look: 'front', mouth: 'smile' }, t);
  const k = t - lastKick(t);
  if (k < .35) { const ny = y - 16 - R(k * 20); ptext(g, '♪', x + 8, ny, { col: '#FFCB45', outline: INK }); }
  fadeTo(g, '#FFFFFF', seg(t, 67.9, 68.5) * .9);
  return { zoom: 2, x: 104, y: 98 };
};
