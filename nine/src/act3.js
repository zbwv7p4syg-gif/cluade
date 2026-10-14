// act3.js — 2:20–3:46. The ninth puzzle piece; a door of light; rain and nine memories on the glass; breath on his
// face; dawn; the nine squares of light become nine memories; walking through the years; a dog-shaped cloud; the end.

// ---------------------------------------------------------------- 2:20 the last piece of the puzzle
// the picture on the puzzle: the boy and the puppy on the plain at sunset
function puzzlePicture() {
  return cached('puzzlePic', 120, 90, (cg) => {
    const img = gradImage(120, 56, ['#86B2DC', '#E9D6AE', '#F6BC72', '#F49B5E']); cg.putImageData(img, 0, 0);
    disc(cg, 84, 54, 14, '#FFE3A0'); disc(cg, 83, 53, 12, '#FFF6DA');
    rect(cg, 0, 52, 120, 4, '#C2A6BC');
    rect(cg, 0, 56, 120, 34, '#9DB650'); for (let y = 58; y < 90; y += 4) rect(cg, 0, y, 120, 1, '#8EAA48');
    rect(cg, 0, 74, 120, 6, '#D6B985');
    human(cg, 52, 78, { age: 'kid', mouth: 'smile', blush: true }, 0);
    dog(cg, 68, 78, { size: 'pup', pose: 'sit', flip: true, collar: true, wag: 0, eyes: 'happy' }, 0);
  });
}
// a 3×3 jigsaw at (x, y), 40×30 pieces; `missing` leaves the middle piece out
function puzzle(g, x, y, missing, glowA = 0) {
  g.drawImage(puzzlePicture(), x, y);
  if (glowA > 0) dith(g, x, y, 120, 90, '#FFF6D8', glowA * .35);
  const seam = 'rgba(70,46,30,0.55)';
  for (let k = 1; k < 3; k++) {
    for (let j = 0; j < 90; j++) if (Math.abs(j % 30 - 15) > 2) px(g, x + k * 40, y + j, seam);
    for (let j = 0; j < 120; j++) if (Math.abs(j % 40 - 20) > 2) px(g, x + j, y + k * 30, seam);
    for (let j = 0; j < 3; j++) {                 // the round tabs, drawn as little arcs across each seam
      const sx = x + k * 40 + ((k + j) % 2 ? 1 : -3), sy = y + j * 30 + 13; rect(g, sx, sy, 3, 1, seam); rect(g, sx, sy + 4, 3, 1, seam); px(g, sx + ((k + j) % 2 ? 2 : 0), sy + 2, seam);
      const tx = x + j * 40 + 18, ty = y + k * 30 + ((k + j) % 2 ? 1 : -3); rect(g, tx, ty, 1, 3, seam); rect(g, tx + 4, ty, 1, 3, seam); px(g, tx + 2, ty + ((k + j) % 2 ? 2 : 0), seam);
    }
  }
  rect(g, x - 1, y - 1, 122, 1, INK); rect(g, x - 1, y + 90, 122, 1, INK); rect(g, x - 1, y, 1, 90, INK); rect(g, x + 120, y, 1, 90, INK);
  if (missing) { rect(g, x + 40, y + 30, 41, 31, '#B48A5E'); for (let j = y + 33; j < y + 60; j += 6) rect(g, x + 40, j, 41, 1, '#9A7048'); rect(g, x + 40, y + 30, 41, 1, INK); rect(g, x + 40, y + 30, 1, 31, INK); }
}
SCENES.puzzle = (g, t, lt) => {
  if (t < 144.8) {
    cityFlat(g, t, { wall: '#F2E4CC', wallD: '#E8D6B8' });
    for (let i = 0; i < 9; i++) { const c = i % 3, r = Math.floor(i / 3); for (let j = 0; j < 4; j++) dith(g, 200 + c * 20 - r * 6 - j * 2, 154 + r * 6 + j, 16, 1, '#FFE6B0', .55); }
    human(g, 150, 152, { age: 'man', pose: 'sitFloor', eyes: t > 143.6 ? 'wide' : 'open', armN: 'fwd', mouth: t > 143.6 ? 'o' : null }, t);
    // the puzzle on the floor, seen edge-on: a strip of picture with a gap in the middle
    rect(g, 172, 150, 36, 3, INK); rect(g, 173, 151, 34, 1, '#9DB650'); rect(g, 173, 150, 34, 1, '#F6BC72'); rect(g, 185, 150, 11, 3, '#C8A27A');
    if (t > 141.0 && t < 143.4) bubble(g, 154, 124, 14, 12, (x, y) => ptext(g, '?', x + 7, y, { col: INK }));
    // 九九 brings the missing piece in her mouth
    const come = seg(t, 141.6, 143.4), dropped = t > 143.6;
    const dx = lerp(300, 214, come);
    dog(g, dx, 152, { pose: come > 0 && come < 1 ? 'walk' : 'sit', phase: t * 2, flip: true, collar: true, wag: 1.2, eyes: dropped ? 'happy' : 'open', carry: dropped ? null : (cg, x, y) => { rect(cg, x - 9, y - 4, 7, 5, INK); rect(cg, x - 8, y - 3, 5, 3, '#F6BC72'); rect(cg, x - 8, y - 1, 5, 1, '#9DB650'); } }, t);
    if (dropped) { rect(g, 199, 149, 7, 4, INK); rect(g, 200, 150, 5, 2, '#F6BC72'); bubble(g, 154, 124, 14, 12, (x, y) => ptext(g, '!', x + 7, y, { col: '#E0503A' })); }
    return { zoom: 2, x: 104, y: 62 };
  }
  // top-down: the piece drops in, the picture glows, a hand and a white paw rest on it together
  rect(g, 0, 0, PW, PH, '#B48A5E'); for (let y = 4; y < PH; y += 9) rect(g, 0, y, PW, 1, '#9A7048');
  for (let i = 0; i < 40; i++) px(g, R(H(i) * PW), R(H(i * 3) * PH), '#A07A50');
  const drop = seg(t, 145.2, 145.8), done = drop >= 1, glowA = seg(t, 146.6, 147.2) - seg(t, 148.6, 150.1) * .5;
  puzzle(g, 132, 52, !done, glowA);
  if (!done) {
    const py = lerp(-40, 82, ein(drop)), pxx = lerp(260, 172, ein(drop));
    rect(g, pxx - 1, py - 1, 42, 32, INK); g.drawImage(puzzlePicture(), 40, 30, 40, 30, R(pxx), R(py), 40, 30);
  } else if (t < 146.2) for (let i = 0; i < 6; i++) { const a = i / 6 * Math.PI * 2; sparkle(g, 192 + Math.cos(a) * (24 + (t - 145.8) * 30), 97 + Math.sin(a) * (18 + (t - 145.8) * 20), 1); }
  if (glowA > 0) { lightPool(g, 192, 97, 90, '#FFE6A8', .25 * glowA, 3, .7); heart(g, 192, 34 - R(seg(t, 146.7, 147.4) * 4), '#FF7F8C'); }
  const rest = seg(t, 147.4, 148.2);
  if (rest > 0) {
    outlined(g, 138, lerp(230, 128, eout(rest)), 36, 90, cg => {
      rect(cg, 6, 14, 20, 18, SKIN); for (let k = 0; k < 4; k++) rect(cg, 7 + k * 5, 2 + (k === 0 || k === 3 ? 3 : 0), 4, 14, SKIN);
      for (let k = 1; k < 4; k++) rect(cg, 6 + k * 5, 8, 1, 8, SKIN_D); rect(cg, 26, 18, 6, 4, SKIN); rect(cg, 8, 32, 18, 58, '#6A8FC4'); rect(cg, 8, 32, 18, 3, '#4C6D9E');
    });
    outlined(g, 214, lerp(230, 128, eout(seg(t, 147.8, 148.6))), 36, 90, cg => {
      ellipse(cg, 18, 14, 13, 11, '#FFFFFF'); for (const tx of [11, 18, 25]) rect(cg, tx, 4, 1, 7, '#D6DAE6'); rect(cg, 8, 24, 20, 66, FUR_OLD.fur); rect(cg, 8, 24, 4, 66, FUR_OLD.furL);
    });
  }
};

// ---------------------------------------------------------------- 2:30 one day you walked out of my life: a door of light
SCENES.leave = (g, t, lt) => {
  cityFlat(g, t, { night: true, wall: '#2E3450', wallD: '#2A2E48', base: '#22263A', floor: '#3E3A44', plank: '#34303A' });
  // the sofa, him asleep on it
  rect(g, 214, 128, 70, 22, INK); rect(g, 215, 129, 68, 8, '#5A4A6A'); rect(g, 215, 137, 68, 12, '#6A5A7A'); rect(g, 212, 132, 6, 18, '#4A3E58'); rect(g, 280, 132, 6, 18, '#4A3E58');
  human(g, 236, 137, { age: 'man', pose: 'lie', eyes: 'closed', outfit: 'sleep' }, t);
  // her bed, and after she goes, only the dent in it
  ellipse(g, 176, 150, 14, 4, INK); ellipse(g, 176, 150, 13, 3, '#8A3A44'); ellipse(g, 176, 149, 10, 2, '#A84A54');
  // the door of light opens on the wall: inside, the plain at sunset
  const open = eout(seg(t, 150.4, 151.2)) * (1 - ein(seg(t, 156.0, 156.6))), dw = R(26 * open), dx0 = 125 - R(dw / 2);
  if (dw > 0) {
    const view = scratch('leaveView'); { const vg = view.getContext('2d'); vg.save(); plainsBase(vg, t, 0, { poles: false }); vg.restore(); }
    rect(g, dx0 - 2, 102, dw + 4, 48, '#FFF2C8');
    g.drawImage(view, 238 - R(dw / 2), 96, dw, 46, dx0, 104, dw, 46);
    lightPool(g, 125, 128, 52, '#FFD890', .3 * open, 3, 1);
    lightPool(g, 140, 152, 46, '#FFD890', .35 * open, 3, .25);
  }
  // 九九 gets up, walks to the light, looks back once, and steps in
  let x = 176, pose = 'lie', flip = true, alpha = 1, look = 'fwd', wag = 0;
  if (t > 151.0) pose = 'stand';
  if (t > 151.4) { x = lerp(176, 128, seg(t, 151.4, 153.4)); pose = t < 153.4 ? 'walk' : 'stand'; }
  if (t > 153.4 && t < 154.4) { flip = false; wag = 1.5; look = 'fwd'; }
  if (t > 154.6) { alpha = 1 - seg(t, 154.6, 155.2); x = lerp(128, 122, seg(t, 154.6, 155.2)); pose = 'walk'; }
  if (alpha > 0) dog(g, x, 150, { pose, phase: t * 1.4, flip, collar: true, old: true, wag, look, alpha, eyes: t > 153.4 && t < 154.4 ? 'happy' : 'open' }, t);
  // on the other side she is young again, and runs off towards the sun
  const run = seg(t, 155.0, 156.2);
  if (run > 0 && run < 1 && dw > 4) {
    g.save(); g.beginPath(); g.rect(dx0, 104, dw, 46); g.clip();
    const rx = lerp(125, 132, run), ry = lerp(150, 128, run);
    if (run < .5) dog(g, rx, ry, { pose: 'run', phase: t * 3, collar: true, wag: 2 }, t);
    else if (run < .85) dog(g, rx, ry, { size: 'pup', pose: 'run', phase: t * 3, wag: 2 }, t);
    else { px(g, rx, ry - 2, '#E2A33C'); px(g, rx + 1, ry - 2, '#E2A33C'); }
    g.restore();
  }
  return { zoom: 2, x: 96, y: 60 };
};

// ---------------------------------------------------------------- 2:37 thank you for once being my nine-ninths: rain, nine memories on the glass
const MEMORY_ICONS = [
  (g, x, y, c) => { rect(g, x - 6, y + 1, 12, 5, c); rect(g, x - 5, y + 2, 10, 3, '#2A2E48'); rect(g, x - 2, y - 3, 5, 4, c); px(g, x - 2, y - 4, c); px(g, x + 2, y - 4, c); },         // the box of puppies
  (g, x, y, c) => { pawPrint(g, x - 7, y - 3, c); rect(g, x + 1, y + 1, 7, 3, c); rect(g, x + 1, y, 3, 1, c); },                                                                      // a paw and a sneaker
  (g, x, y, c) => { ring(g, x, y, 5, c); px(g, x - 2, y, c); px(g, x + 2, y, c); rect(g, x, y - 8, 1, 3, c); },                                                                         // the tag
  (g, x, y, c) => { rect(g, x - 5, y - 6, 10, 12, c); rect(g, x - 4, y - 5, 8, 11, '#2A2E48'); rect(g, x - 2, y + 2, 4, 3, c); px(g, x - 1, y + 1, c); },                              // the door
  (g, x, y, c) => { ring(g, x, y + 1, 5, c); rect(g, x - 5, y - 4, 10, 1, c); px(g, x + 6, y - 2, c); px(g, x + 7, y - 3, c); },                                                     // the water jar and a tail
  (g, x, y, c) => { rect(g, x, y - 2, 1, 9, c); ring(g, x, y - 5, 3, c); rect(g, x - 7, y + 6, 14, 1, c); },                                                                          // the bus stop
  (g, x, y, c) => { ring(g, x - 2, y, 4, c); rect(g, x - 2, y - 4, 3, 8, '#2A2E48'); sparkle(g, x + 5, y - 3, 1, c); px(g, x + 3, y + 4, c); },                                    // moon and stars
  (g, x, y, c) => { rect(g, x - 5, y - 1, 10, 4, c); rect(g, x - 4, y, 8, 2, '#2A2E48'); rect(g, x - 2, y - 2, 3, 1, c); },                                                          // her slipper
  (g, x, y, c) => { rect(g, x - 5, y, 10, 5, c); for (let k = -3; k <= 3; k += 3) { rect(g, x + k, y - 4, 1, 3, c); px(g, x + k, y - 6, '#FFB860'); } },                                // the cake
];
function ring(g, cx, cy, r, col) { for (let a = 0; a < 64; a++) px(g, cx + R(Math.cos(a / 64 * Math.PI * 2) * r), cy + R(Math.sin(a / 64 * Math.PI * 2) * r), col); }
function rainOutside(g, x, y, w, h, t) {
  grad(g, ['#0A0E24', '#141A38', '#1E2648'], x, y, w, h);
  rooftops(g, x, y + h, w, 0);
  for (let i = 0; i < 40; i++) { const rx = x + ((i * 37) % w), ry = y + ((i * 53 + t * 140) % h); px(g, rx, ry, '#5A6A9A'); px(g, rx, ry + 1, '#3A4878'); }
}
SCENES.rainwin = (g, t, lt) => {
  const n = countIn(NINE_C, t), fade = seg(t, 163.6, 166.4);
  const lit = Array.from({ length: 9 }, (_, i) => (i < n ? 1 : 0) * (1 - fade * .7));
  windowRoom(g, t, .22, lit, {
    view: (gg, x, y, w, h) => rainOutside(gg, x, y, w, h, t), litCol: '#FFD9A0', litA: .22, dimA: .35, squares: false, glowCol: '#FFC880', floorY: 150,
    panes: gg => {
      for (let i = 0; i < 9; i++) {
        const p = winPane(i);
        // raindrops sliding down the glass
        for (let k = 0; k < 3; k++) { const dx = p.x + 4 + ((i * 13 + k * 11) % (p.w - 8)), dy = p.y + ((t * (8 + k * 3) + i * 7 + k * 9) % p.h); px(gg, dx, dy, '#8A9AC8'); px(gg, dx, dy - 1, '#5A6A9A'); }
        if (lit[i] > 0) MEMORY_ICONS[i](gg, p.x + p.w / 2, p.y + p.h / 2, mix('#6A6A8A', '#FFE6A8', lit[i]));
      }
      NINE_C.forEach((x, i) => { const a = seg(t, x, x + .4); if (a > 0 && a < 1) { const p = winPane(i); sparkle(gg, p.x + p.w - 4, p.y + 4, a < .5 ? 2 : 1, '#FFF6D8'); } });
    },
  });
  // under the window: her empty bed with the blue slipper; he sits against the wall
  ellipse(g, 236, 162, 22, 5, INK); ellipse(g, 236, 162, 21, 4, '#5A2A34'); ellipse(g, 236, 161, 16, 2, '#6E3440');
  rect(g, 228, 158, 10, 5, INK); rect(g, 229, 159, 8, 3, '#3A5A9A'); rect(g, 230, 159, 4, 1, '#B8C0D8');
  human(g, 150, 166, { age: 'man', pose: 'sitFloor', eyes: n >= 9 ? 'closed' : 'sad', outfit: 'man' }, t);
  rain(g, t, 30, '#3A4878', 1, PH, 200);
  grade(g, '#8A96D8', .15);
  return t < 162.6 ? { zoom: 2, x: 96, y: 6 } : null;
};

// ---------------------------------------------------------------- 2:47 a dream at first light: her breath on my face
const OLDF = FUR_OLD;
SCENES.breath = (g, t, lt) => {
  grad(g, ['#5E5280', '#8E6E98', '#C8909E', '#EAB4A0'], 0, 0, PW, PH);
  for (let i = 0; i < 9; i++) { const c = i % 3, r = Math.floor(i / 3); dith(g, 40 + c * 24, 20 + r * 18, 20, 14, '#F6D8C0', .25); }
  // pillow
  ellipse(g, 120, 196, 150, 34, INK); ellipse(g, 120, 196, 148, 32, '#F4EEF2'); ellipse(g, 110, 206, 130, 18, '#E2D8E4');
  // his face in profile, asleep
  outlined(g, 40, 50, 150, 150, cg => {
    ellipse(cg, 70, 70, 54, 52, SKIN);
    ellipse(cg, 52, 50, 50, 40, HAIR); poly(cg, [[20, 40], [70, 18], [112, 38], [96, 52], [60, 46], [34, 70]], HAIR);
    rect(cg, 56, 30, 30, 4, HAIR_L);
    ellipse(cg, 50, 78, 8, 11, SKIN_D); ellipse(cg, 51, 78, 5, 8, SKIN);
    const smile = t > 169.6, open = t > 172.5;
    if (open) { rect(cg, 96, 66, 6, 6, EYE); rect(cg, 96, 66, 2, 2, '#FFFFFF'); } else { rect(cg, 94, 70, 12, 2, EYE); px(cg, 93, 69, EYE); px(cg, 106, 69, EYE); for (const k of [96, 100, 104]) px(cg, k, 72, EYE); }
    rect(cg, 92, 58, 14, 2, HAIR);
    poly(cg, [[118, 72], [126, 86], [118, 90]], SKIN); rect(cg, 118, 88, 4, 1, SKIN_D);
    if (smile) { rect(cg, 106, 100, 10, 2, '#B5574B'); px(cg, 105, 98, '#B5574B'); } else rect(cg, 108, 100, 7, 2, '#B5574B');
    ellipse(cg, 92, 88, 7, 4, smile ? '#F2A08F' : '#F2BCA8');
  });
  // her muzzle comes in from the right, and fades as he wakes
  const away = seg(t, 171.9, 172.7);
  outlined(g, 170, 14, 214, 170, cg => {
    poly(cg, [[120, 34], [136, -2], [156, 30]], OLDF.furD); poly(cg, [[150, 26], [176, -6], [190, 34]], OLDF.fur); poly(cg, [[160, 24], [175, 6], [182, 28]], '#E8A08A');
    ellipse(cg, 178, 74, 70, 52, OLDF.fur); ellipse(cg, 170, 56, 46, 22, OLDF.furL);
    rect(cg, 34, 70, 100, 40, '#E6DED2'); ellipse(cg, 40, 90, 16, 20, '#E6DED2'); rect(cg, 40, 104, 92, 14, '#D2CABE'); ellipse(cg, 128, 96, 30, 24, '#E6DED2');
    rect(cg, 22, 68, 24, 18, '#2A1A12'); rect(cg, 25, 65, 18, 3, '#2A1A12'); rect(cg, 28, 70, 7, 3, '#5A4A40'); rect(cg, 26, 80, 5, 4, '#140C08');
    line(cg, 44, 92, 50, 104, '#2A1A12'); line(cg, 50, 104, 96, 110, '#2A1A12');
    for (const [wx, wy] of [[62, 84], [70, 90], [78, 84], [66, 96], [80, 96], [90, 90]]) px(cg, wx, wy, '#8A7A6A');
    rect(cg, 140, 58, 16, 3, '#2A1A12'); px(cg, 139, 56, '#2A1A12'); px(cg, 156, 56, '#2A1A12'); rect(cg, 136, 48, 22, 2, '#D9D2C6');
    rect(cg, 128, 124, 8, 30, '#D8423A'); rect(cg, 136, 138, 6, 6, '#FFD447');
  }, INK, 1 - away);
  // a puff of warm breath on every beat
  for (let b = 0; b < 3; b++) {
    const bt = BEATMAP.phase + (beatAt(t) - b) * BEAT, a = (t - bt) / (BEAT * 3);
    if (bt < 166.8 || bt > 172.2 || a < 0 || a > 1) continue;
    const bx = lerp(190, 160, a), by = lerp(96, 128, a), col = a < .6 ? '#FFFFFF' : '#F6E8F0';
    for (const [dx, dy, r] of [[0, 0, 3], [-6, 3, 2], [-10, -2, 2], [-4, -5, 1]]) { const cx = bx + dx, cy = by + dy; for (let yy = -r; yy <= r; yy++) for (let xx = -r; xx <= r; xx++) if (xx * xx + yy * yy <= r * r && (xx * xx + yy * yy >= (r - 1) * (r - 1) || r < 2) && bayer(R(cx + xx), R(cy + yy)) < 1 - a * .8) px(g, cx + xx, cy + yy, col); }
  }
  vignette(g, '#FFF2F6', .7);
};

// ---------------------------------------------------------------- 2:53 the dawn I can't go back to
SCENES.dawn = (g, t, lt) => {
  const k = .72 + seg(t, 173, 178) * .22, sq = seg(t, 177.2, 180.4);
  windowRoom(g, t, k, Array(9).fill(1), { squareA: .5 + sq * .45, litA: .1, floorY: 150 });
  // her bed under the window, empty but for the slipper, the nine squares of light on it
  ellipse(g, 186, 164, 24, 5, INK); ellipse(g, 186, 164, 23, 4, '#8A3A44'); ellipse(g, 186, 163, 18, 2, '#A84A54');
  rect(g, 178, 160, 10, 5, INK); rect(g, 179, 161, 8, 3, '#5A8AD8'); rect(g, 180, 161, 4, 1, '#FFFFFF');
  const awake = t > 174.4, reach = t > 176.6;
  human(g, 128, 170, { age: 'man', pose: 'sitFloor', outfit: 'sleep', eyes: awake ? (t > 178 ? 'sad' : 'open') : 'closed', armN: reach ? 'fwd' : 'down' }, t);
  if (sq > 0) lightPool(g, 180, 162, 70, '#FFF0C8', sq * .5, 4, .35);
  return t > 178.6 ? { zoom: 2, x: 92, y: 92 } : null;
};

// ---------------------------------------------------------------- 3:00 nine squares of light, nine memories
// [shot, moment, crop x, crop y]: each tile replays 2.4 s of that shot from the given moment
const MEMS = [
  ['litter', 34.8, 66, 124], ['paws', 46.8, 168, 124], ['paper', 61.9, 120, 112],
  ['door', 73.2, 200, 98], ['hide', 90.3, 140, 100], ['busstop', 103.6, 128, 104],
  ['paddies', 107.3, 132, 94], ['doorstep', 116.9, 120, 110], ['birthday', 134.4, 130, 100],
];
const tileAt = i => ({ x: 3 + (i % 3) * 127, y: 3 + Math.floor(i / 3) * 71 });
SCENES.grid = (g, t, lt) => {
  rect(g, 0, 0, PW, PH, '#2B1D16');
  const tile = scratch('tile'), tg = tile.getContext('2d');
  MEMS.forEach(([name, t0, cx, cy], i) => {
    const appear = 180.9 + i * BEAT * 1.5, a = seg(t, appear, appear + .35), { x, y } = tileAt(i);
    if (a <= 0) { rect(g, x, y, 124, 68, '#FFE9B8'); dith(g, x, y, 124, 68, '#FFF8E0', .5); return; }
    renderShot(tg, shotByName(name), t0 + ((t - appear) % 2.4));
    if (a < 1) { const img = tg.getImageData(cx, cy, 124, 68), d = img.data; for (let j = 0; j < 68; j++) for (let q = 0; q < 124; q++) if (bayer(q >> 1, j >> 1) >= a) { const o = (j * 124 + q) * 4; d[o] = 255; d[o + 1] = 233; d[o + 2] = 184; } tg.putImageData(img, cx, cy); }
    g.drawImage(tile, cx, cy, 124, 68, x, y, 124, 68);
  });
  // when all nine are there, a gold frame steps from memory to memory on the beat
  if (t > 186.4) {
    const k = ((beatAt(t) % 9) + 9) % 9, { x, y } = tileAt(k);
    rect(g, x - 2, y - 2, 128, 2, '#FFCB45'); rect(g, x - 2, y + 68, 128, 2, '#FFCB45'); rect(g, x - 2, y, 2, 68, '#FFCB45'); rect(g, x + 124, y, 2, 68, '#FFCB45');
  }
};

// ---------------------------------------------------------------- 3:13 walking through the years together
const WALK = [
  { t: 193.0, sky: SKIES.golden, age: 'kid', size: 'pup', pal: PAL_GOLD },
  { t: 195.5, sky: SKIES.day, age: 'kid', pal: { a: '#7FB04E', b: '#8CBA56', hi: '#B8D872', lo: '#5E8A3A', ridge: '#A8B86A' } },
  { t: 198.0, sky: SKIES.dusk, age: 'teen', pal: { a: '#8A8A4E', b: '#969652', hi: '#C8B070', lo: '#6A6A3A', ridge: '#A89868' } },
  { t: 200.5, sky: SKIES.night, age: 'man', pal: { a: '#2E4A3A', b: '#34523E', hi: '#3E6048', lo: '#24382E', ridge: '#3A4A3E' }, city: true },
  { t: 203.0, sky: SKIES.dawn, age: 'man', old: true, pal: { a: '#6E8A5E', b: '#7A9664', hi: '#B8B88A', lo: '#56704A', ridge: '#9A8A78' } },
];
function walkCam(t) { const u = t - 203.6; return t < 203.6 ? (t - 193) * 34 : 360.4 + (u < .8 ? 34 * u - 17 * u * u / .8 : 13.6); }
function walkBg(gg, t, st) {
  const camX = walkCam(t), night = !!st.city;
  plainsBase(gg, t, camX, { sky: st.sky, pal: st.pal, sun: st.sky !== SKIES.night && st.sky !== SKIES.day, sunX: st.sky === SKIES.dawn ? 320 : 252, sunR: st.sky === SKIES.dawn ? 18 : 30, clouds: !night,
    mtn: night ? '#1C2244' : undefined, mtn2: night ? '#161C3A' : undefined, ham: night ? '#101828' : undefined, ham2: night ? '#141E30' : undefined, glare: night ? '#2A3460' : undefined,
    verge: night ? '#26382C' : undefined, road: night ? '#5A5A64' : undefined, pole: night ? '#1A1A24' : undefined, wire: night ? '#121218' : undefined,
    sky2: night ? (g2 => { stars(g2, t, 50, 100, 5); moon(g2, 300, 30, 7, SKIES.night[1]); city(g2, t, 118, camX, { seed: 3 }); }) : null });
  if (st.sky === SKIES.day) for (let i = 0; i < 3; i++) cloud(gg, ((i * 140 - camX * .1) % 460 + 460) % 460 - 60, 16 + i * 10, 46);
}
SCENES.walk = (g, t, lt) => {
  let si = 0; while (si + 1 < WALK.length && t >= WALK[si + 1].t) si++;
  const st = WALK[si], mixP = si > 0 ? seg(t, st.t, st.t + .5) : 1;
  if (mixP < 1) { const a = scratch('walkA'), b = scratch('walkB'); walkBg(a.getContext('2d'), t, WALK[si - 1]); walkBg(b.getContext('2d'), t, st); ditherMix(g, a, b, mixP); }
  else walkBg(g, t, st);
  const camX = walkCam(t), stopW = walkCam(203.6) + 150;
  const manX = t < 203.6 ? 176 : Math.min(360.4 + 176 + 34 * (t - 203.6), 360.4 + 176 + 34 * .7) - camX, manWalk = t < 204.3;
  const dogX = t < 203.6 ? 150 : stopW - camX, dogSit = t > 203.8, fade = seg(t, 204.7, 205.3);
  const night = !!st.city;
  if (fade < 1) dog(g, dogX, 171, { size: st.size, old: st.old, pose: dogSit ? 'sit' : 'walk', phase: t * 2.2, collar: true, wag: dogSit ? 1.4 : .7, eyes: dogSit ? 'happy' : 'open', alpha: 1 - fade, tongue: !dogSit }, t);
  human(g, manX, 171, { age: st.age, pose: manWalk ? 'walk' : 'stand', phase: t * 1.8, flip: t > 204.4, mouth: 'smile', eyes: t > 204.4 ? 'sad' : 'open', armN: t > 204.6 ? 'wave' : 'down' }, t);
  // a burst of sparkles each time the years change them
  WALK.forEach(w => { const a = seg(t, w.t, w.t + .5); if (a > 0 && a < 1 && w.t > 193) for (let i = 0; i < 6; i++) { const an = i / 6 * Math.PI * 2; sparkle(g, 164 + Math.cos(an) * a * 26, 158 + Math.sin(an) * a * 14, 1, '#FFF6D8'); } });
  // she rises as light
  if (fade > 0) for (let i = 0; i < 10; i++) { const u = clamp(fade * 1.4 - i * .04), sx = dogX - 6 + (i * 5) % 14 + Math.sin(t * 4 + i) * 2, sy = 166 - u * 70 - (i % 3) * 4; if (u > 0 && u < 1) px(g, sx, sy, i % 2 ? '#FFE6A8' : '#FFFFFF'); }
  if (night) grade(g, '#9AA8E8', .15);
};

// ---------------------------------------------------------------- 3:25 the plain again; one cloud looks just like her
function dogCloud(g, x, y, t) {
  const wag = Math.floor(beatPos(t)) % 2;
  for (const [col, dy] of [['#F0BCA8', 2], ['#FFF4EC', 0]]) {
    ellipse(g, x, y + dy, 26, 8, col); disc(g, x + 26, y - 8 + dy, 9, col); ellipse(g, x + 36, y - 5 + dy, 6, 4, col);
    poly(g, [[x + 19, y - 14 + dy], [x + 23, y - 24 + dy], [x + 28, y - 15 + dy]], col);
    for (const lx of [-16, -8, 10, 18]) disc(g, x + lx, y + 9 + dy, 3, col);
    disc(g, x - 29, y - 9 - wag * 2 + dy, 5, col); disc(g, x - 25, y - 4 + dy, 3, col);
  }
  px(g, x + 30, y - 10, '#C8A4A0'); px(g, x + 41, y - 6, '#C8A4A0');
}
SCENES.sunset = (g, t, lt) => {
  const camX = 40 + lt * 1.2;
  plainsBase(g, t, camX, { wind: 1.6, sunY: 124 + lt * .6, sky2: gg => dogCloud(gg, 140 + lt * 2.4, 40, t) });
  const wave = t > 209.6;
  human(g, 156, 171, { age: 'man', armN: wave ? 'wave' : 'hold', mouth: wave ? 'smile' : null, eyes: t > 211 ? 'happy' : 'open', blush: t > 211 }, t);
  if (!wave) { rect(g, 160, 157, 1, 4, '#D8423A'); rect(g, 163, 157, 1, 4, '#D8423A'); rect(g, 160, 161, 4, 1, '#D8423A'); px(g, 162, 163, '#FFD447'); }
  if (wave) for (let i = 0; i < 4; i++) { const a = ((t - 209.6) * .8 + i * .25) % 1; sparkle(g, 140 + lt * 2.4 + Math.cos(i * 1.7) * 40, 40 + Math.sin(i * 2.3) * 14, a < .5 ? 1 : 0, '#FFFFFF'); }
};

// ---------------------------------------------------------------- 3:34 the window at dusk, the title, a dedication
SCENES.end = (g, t, lt) => {
  const k = .55 - seg(t, 214.1, 223) * .5;
  const lit = Array.from({ length: 9 }, (_, i) => 1 - seg(t, 214.6 + (8 - i) * BEAT * 2, 214.9 + (8 - i) * BEAT * 2));
  windowRoom(g, t, k, lit, {
    panes: gg => { const p = winPane(4); for (const [dx, dy] of [[0, 0]]) pawPrint(gg, p.x + 17 + dx, p.y + 18 + dy, '#E8E4F0'); },
  });
  [...'九分之九'].forEach((ch, j) => {
    const a = seg(t, 216.0 + j * BEAT, 216.3 + j * BEAT); if (a <= 0) return;
    ptext(g, ch, 156 + j * 24, 130 - R((1 - eout(a)) * 6), { size: 24, col: '#FFF3D6', outline: INK, shadow: '#8A6A50' });
  });
  const l1 = seg(t, 218.4, 219.2), l2 = seg(t, 220.0, 220.8);
  if (l1 > 0) ptext(g, '献给每一个陪我们长大的它', PW / 2, 160, { col: mix('#3A3448', '#F2DFC0', l1), outline: INK });
  if (l2 > 0) ptext(g, '音乐 · 卢广仲', PW / 2, 176, { col: mix('#3A3448', '#B8A8B0', l2), outline: INK });
  fadeTo(g, '#000000', seg(t, 223.6, 226.0));
};
