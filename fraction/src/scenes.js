// scenes.js — 几分之几 · 像素 MV. One function per shot (see timeline.js), all in 480×270 pixels.

const mixHex = (a, b, p) => { const A = hex(a), B = hex(b); return '#' + A.map((v, i) => R(lerp(v, B[i], p)).toString(16).padStart(2, '0')).join(''); };
const qz = (p, n = 8) => Math.floor(clamp(p) * n) / n;              // palette changes in steps, like an old console
const kickPulse = (t, k = 8) => Math.exp(-Math.max(0, t - lastKick(t)) * k);
const beatHop = (t, h = 1) => (beatPhase(t) < .5 ? -h : 0);
const blackout = (g, a) => { if (a > 0) checker(g, 0, 0, PW, PH, '#000000', a); };
const whiteout = (g, a) => { if (a > 0) checker(g, 0, 0, PW, PH, '#FFF8E8', a); };

// ---------------------------------------------------------------- props
function sun(g, x, y, r, col = '#FFE27A', rim = '#FFC94A') { halo(g, x, y, r * 1.8, col); disc(g, x, y, r, rim); disc(g, x, y, r - 2, col); rect(g, x - R(r * .5), y - R(r * .5), R(r * .35), 2, '#FFF6C8'); }
function bird(g, x, y, T) { const up = Math.floor(T * 5) % 2; rect(g, x - 2, y - up, 2, 1, INK); rect(g, x + 1, y - up, 2, 1, INK); rect(g, x, y, 1, 1, INK); }
function busStop(g, x, y) { rect(g, x, y - 46, 2, 46, '#5A6070'); disc(g, x + 1, y - 48, 6, INK); disc(g, x + 1, y - 48, 5, '#3A78D0'); rect(g, x - 1, y - 49, 5, 2, '#FFFFFF'); }
function bus(g, x, y) {
  rect(g, x - 1, y - 39, 112, 34, INK); rect(g, x, y - 38, 110, 32, '#F2C14E'); rect(g, x, y - 18, 110, 4, '#E07A3A');
  for (let i = 0; i < 5; i++) { rect(g, x + 6 + i * 20, y - 34, 14, 11, '#9ED0F0'); rect(g, x + 6 + i * 20, y - 34, 14, 2, '#D8F0FF'); }
  for (const wx of [20, 88]) { disc(g, x + wx, y - 4, 6, INK); disc(g, x + wx, y - 4, 3, '#8A8A9A'); }
}
function vending(g, x, y) { rect(g, x - 1, y - 51, 30, 51, INK); rect(g, x, y - 50, 28, 50, '#D83A3A'); rect(g, x + 3, y - 46, 22, 22, '#BFE6FF'); for (let i = 0; i < 3; i++) for (let j = 0; j < 2; j++) rect(g, x + 5 + i * 7, y - 44 + j * 10, 4, 7, ['#F2C14E', '#7DBE7A', '#8FA8D8'][i]); rect(g, x + 5, y - 18, 18, 4, INK); }
function soda(g, x, y) { rect(g, x - 1, y - 5, 4, 6, INK); rect(g, x, y - 4, 2, 4, '#3AB0D8'); }
function popsicle(g, x, y) { rect(g, x, y - 1, 1, 4, '#E8C890'); rect(g, x - 2, y - 8, 5, 7, INK); rect(g, x - 1, y - 7, 3, 6, '#8FE0F0'); rect(g, x - 1, y - 7, 1, 2, '#FFFFFF'); }
function umbrella(g, x, y, col) { for (let j = 0; j < 7; j++) rect(g, x - 15 + j * 2, y - 7 + j, 31 - j * 4, 1, j === 0 ? INK : col); rect(g, x - 16, y - 7, 33, 1, INK); for (let i = -15; i <= 15; i += 5) rect(g, x + i, y - 7, 1, 2, INK); rect(g, x, y - 7, 1, 18, INK); }
function palm(g, x, y, s) {
  for (let i = 0; i < 40 * s; i++) rect(g, x + R(Math.sin(i / 14) * 4 * s), y - i, R(4 * s), 1, i % 4 ? '#6B4A2E' : '#5A3C24');
  const tx = x + R(Math.sin(40 * s / 14) * 4 * s) + 2, ty = y - R(40 * s);
  for (const a of [-2.6, -2.0, -1.2, -.5, .1]) for (let r = 0; r < 18 * s; r++) rect(g, tx + R(Math.cos(a) * r), ty + R(Math.sin(a) * r * .6 + r * r * .012), 2, 2, '#2E7A4A');
}
function building(g, x, w, top, base, col, lit, seed, T) {
  rect(g, x, top, w, base - top, col);
  for (let wy = top + 5; wy < base - 6; wy += 9) for (let wx = x + 4; wx < x + w - 5; wx += 8) {
    const on = H(wx * 13 + wy * 7 + seed) < lit; rect(g, wx, wy, 4, 5, on ? (H(wx + wy) > .5 ? '#FFE08A' : '#FFC86A') : '#2A2440');
  }
}
function bike(g, x, y, T, s = 1) {
  const sp = T * 18, X = v => x + R(v * s), Y = v => y - R(v * s), fr = (a, b, c, d) => { line(g, X(a), Y(b), X(c), Y(d), '#3A9AD8'); line(g, X(a), Y(b) + 1, X(c), Y(d) + 1, '#3A9AD8'); };
  for (const wx of [-19, 19]) {
    const r = R(8 * s); ring(g, X(wx), Y(8), r, INK); ring(g, X(wx), Y(8), r - 1, '#3A3A48'); ring(g, X(wx), Y(8), r - 2, INK);
    for (let a = 0; a < 3; a++) { const an = sp + a * Math.PI / 3, q = r - 3; line(g, X(wx) - R(Math.cos(an) * q), Y(8) - R(Math.sin(an) * q), X(wx) + R(Math.cos(an) * q), Y(8) + R(Math.sin(an) * q), '#9A9AB0'); }
  }
  fr(-19, 8, -2, 8); fr(-2, 8, 8, 20); fr(-19, 8, -6, 20); fr(-6, 20, 8, 20); fr(8, 20, 19, 8); fr(12, 26, 8, 20); rect(g, X(10), Y(27), R(6 * s), 2, INK);
  rect(g, X(-9), Y(22), R(7 * s), 2, INK); rect(g, X(-24), Y(20), R(12 * s), 2, '#5A5A6A');   // seat, rack
}
function train(g, x, y, cars, faceAt) {
  for (let c = 0; c < cars; c++) {
    const cx = x + c * 146; if (cx > PW + 10 || cx + 144 < -10) continue;
    rect(g, cx - 1, y - 57, 146, 52, INK); rect(g, cx, y - 56, 144, 50, '#ECEFF4'); rect(g, cx, y - 26, 144, 6, '#3A78D0'); rect(g, cx, y - 56, 144, 3, '#C8D0DC');
    for (let i = 0; i < 5; i++) { rect(g, cx + 8 + i * 27, y - 48, 20, 15, '#3E4E70'); rect(g, cx + 8 + i * 27, y - 48, 20, 3, '#6E80A8'); }
    if (faceAt && c === faceAt.car) clawd(g, cx + 8 + faceAt.win * 27 + 10, y - 31, 1.5, { look: YOU, bow: true, aR: 'wave', eyes: 'happy' }, faceAt.T);
    rect(g, cx + 60, y - 50, 1, 44, '#B0B8C8');
    for (const wx of [24, 120]) { disc(g, cx + wx, y - 4, 5, INK); disc(g, cx + wx, y - 4, 2, '#7A7A8A'); }
  }
  // the nose of the front car
  rect(g, x - 9, y - 50, 9, 44, INK); rect(g, x - 8, y - 49, 8, 42, '#ECEFF4'); rect(g, x - 7, y - 44, 6, 12, '#3E4E70'); rect(g, x - 6, y - 14, 4, 3, '#FFE08A');
}
function rain(g, t, n, col = '#8FA8D8', y1 = PH, seed = 1) {
  for (let i = 0; i < n; i++) { const sp = 240 + 120 * H(i + seed), x = R(H(i * 3 + seed) * (PW + 40)) - R(((t * sp + H(i * 7) * y1) % y1) * .15), y = R((t * sp + H(i * 7 + seed) * y1) % y1); rect(g, x, y, 1, 4, col); }
}
function snow(g, t, n, seed = 2) { for (let i = 0; i < n; i++) { const y = R((t * (14 + 10 * H(i + seed)) + H(i * 5 + seed) * PH) % PH), x = R((H(i * 3 + seed) * PW + Math.sin(t + i) * 6 + PW) % PW); rect(g, x, y, H(i) > .7 ? 2 : 1, H(i) > .7 ? 2 : 1, '#FFFFFF'); } }
function leaves(g, t, n, cols, seed = 3) { for (let i = 0; i < n; i++) { const y = R((t * (20 + 16 * H(i + seed)) + H(i * 5 + seed) * PH) % PH), x = R((H(i * 3 + seed) * PW + Math.sin(t * 1.3 + i) * 14 - t * 8 + PW * 9) % PW); rect(g, x, y, 2, 1, cols[i % cols.length]); rect(g, x + (Math.floor(t * 4 + i) % 2), y + 1, 1, 1, cols[i % cols.length]); } }
function seeds(g, t, n, t0, seed = 4) {
  for (let i = 0; i < n; i++) { const a = t - t0 - H(i) * 1.5; if (a < 0) continue; const x = R((60 + H(i * 3 + seed) * 300 + a * (40 + 30 * H(i))) % (PW + 20)), y = R(220 - a * (10 + 14 * H(i + 2)) + Math.sin(a * 2 + i) * 8); if (y < -5) continue; rect(g, x, y, 1, 1, '#FFFFFF'); rect(g, x - 1, y - 1, 3, 1, '#F4F4F4'); rect(g, x, y + 1, 1, 2, '#D8D8C8'); }
}
function windLines(g, t, n, seed = 5) { for (let i = 0; i < n; i++) { const x = R(((t * 380 + H(i * 9 + seed) * 900) % 900) - 200), y = R(40 + H(i + seed) * 190 + Math.sin(t * 3 + i) * 3); rect(g, x, y, 14 + R(12 * H(i)), 1, '#FFFFFF'); } }
function treeOnHill(g, x, y, foliage, T, bare = false) {
  rect(g, x - 3, y - 40, 7, 40, '#6B4A2E'); rect(g, x - 3, y - 40, 2, 40, '#7E5A3A');
  line(g, x, y - 30, x - 16, y - 46, '#6B4A2E'); line(g, x + 1, y - 34, x + 18, y - 50, '#6B4A2E');
  if (bare) { line(g, x - 16, y - 46, x - 22, y - 56, '#6B4A2E'); line(g, x + 18, y - 50, x + 22, y - 62, '#6B4A2E'); return; }
  const sw = R(Math.sin(T * 1.5));
  for (const [dx, dy, r] of [[-18, -52, 15], [16, -56, 16], [0, -66, 18], [-6, -48, 13], [10, -46, 12]]) disc(g, x + dx + sw, y + dy, r + 1, INK);
  for (const [dx, dy, r] of [[-18, -52, 15], [16, -56, 16], [0, -66, 18], [-6, -48, 13], [10, -46, 12]]) disc(g, x + dx + sw, y + dy, r, foliage[0]);
  for (const [dx, dy, r] of [[-20, -56, 8], [12, -62, 9], [-3, -72, 10]]) disc(g, x + dx + sw, y + dy, r, foliage[1]);
}
function bench(g, x, y) { rect(g, x - 34, y - 12, 68, 3, '#8A5A3A'); rect(g, x - 34, y - 22, 68, 3, '#8A5A3A'); rect(g, x - 30, y - 12, 2, 12, '#5A3A24'); rect(g, x + 28, y - 12, 2, 12, '#5A3A24'); rect(g, x - 30, y - 22, 2, 10, '#5A3A24'); rect(g, x + 28, y - 22, 2, 10, '#5A3A24'); }
// tiny memory icons, 9×9, for the pieces scene and the bridge
const ICONS = [
  (g, x, y) => { disc(g, x, y, 3, '#FFC94A'); for (let a = 0; a < 8; a++) rect(g, x + R(Math.cos(a * .785) * 5), y + R(Math.sin(a * .785) * 5), 1, 1, '#FFC94A'); },
  (g, x, y) => { ring(g, x - 2, y + 1, 3, INK); ring(g, x + 3, y + 1, 3, INK); line(g, x - 2, y + 1, x + 1, y - 2, '#3A9AD8'); line(g, x + 1, y - 2, x + 3, y + 1, '#3A9AD8'); },
  (g, x, y) => popsicle(g, x, y + 3),
  (g, x, y) => sparkle(g, x, y, 4, '#FFE08A'),
  (g, x, y) => heart(g, x, y + 1, 1),
];

// ---------------------------------------------------------------- shots
const SCENES = {
  title(g, t) {
    const p = qz(seg(t, 1.5, 14), 10);
    grad(g, [mixHex('#0C0A24', '#4A6FB0', p), mixHex('#1E1840', '#F4A27A', p), mixHex('#3A2A50', '#FFD9A0', p)], 0, 190);
    stars(g, t, R(80 * (1 - p)), 150);
    sun(g, 300, R(lerp(205, 150, eio(seg(t, 2, 14)))), 20);
    rect(g, 0, 188, PW, 82, mixHex('#1A2A20', '#6FA050', p));
    for (let i = 0; i < 6; i++) rect(g, 0, 192 + i * i * 2.4, PW, 1, mixHex('#22362A', '#7FB45A', p));
    grassRow(g, t, 270, mixHex('#10180F', '#4E7E3A', p), 2, 1, 3);
    for (let i = 0; i < 3; i++) if (t > 6) bird(g, R(((t - 6) * 18 + i * 22) % 520) - 20, 110 + i * 7 + R(Math.sin(t + i) * 2), t + i);
    const ty = seg(t, 3.5, 5.5), chars = [...'几分之几'];
    if (ty > 0) { ptext(g, chars.slice(0, Math.ceil(ty * 4)).join(''), 240, 96, { size: 36, col: '#FFF4D6', outline: INK, shadow: '#7A3A2A' }); }
    if (t > 6) ptext(g, '卢广仲 · 像素 MV', 240, 120, { col: '#FFE9C8', outline: INK });
    blackout(g, 1 - seg(t, .5, 2.5));
  },
  field(g, t) {
    grad(g, ['#3E8EDE', '#79B8F0', '#CDE8FA'], 0, 175);
    sun(g, 392, 74, 32);
    for (let i = 0; i < 4; i++) cloud(g, R(((t * 6 + i * 140) % 640) - 100), 30 + i * 12, 1 + (i % 2) * .4);
    rect(g, 0, 170, PW, 14, '#7DB86A'); for (let x = 0; x < PW; x += 30) disc(g, x + 10, 172, 9, '#6CA85A');
    rect(g, 0, 182, PW, 88, '#9ACD5A'); for (let i = 0; i < 7; i++) rect(g, 0, 186 + i * 5, PW, 1, '#8ABE4E');
    // heat shimmer on the horizon
    for (let y = 176; y < 184; y += 2) rect(g, R(Math.sin(t * 6 + y) * 3), y, PW, 1, '#A8D86A');
    rect(g, 0, 214, PW, 10, '#D8B878'); rect(g, 0, 214, PW, 1, '#C8A868');
    rect(g, 0, 236, PW, 34, '#7A7A84'); for (let x = 0; x < PW; x += 24) rect(g, x, 252, 12, 2, '#E8E8E8');
    busStop(g, 372, 222);
    const gust = t > 22.66;
    grassRow(g, t, 214, '#6CA84A', 7, gust ? 3 : 1);
    // he walks along the path until the second line, then stops by his friend
    const wx = lerp(70, 300, eio(seg(t, 16.3, 22.4))), walking = t < 22.4;
    const leave = t > 26.2;
    if (!leave) clawd(g, 352, 222, 4, { look: FRIEND, tear: gust, aR: gust ? 'wave' : 'down', eyes: gust ? 'closed' : 'open', seed: 2 }, t);
    clawd(g, wx, 222, 4, { walk: walking ? beatPos(t) / 2 : null, aR: t > 26.4 ? 'wave' : 'down', eyes: gust ? 'open' : 'happy', dy: walking ? beatHop(t) : 0 }, t);
    // the bus pulls in for the friend and leaves
    const bx = t < 23.6 ? 560 : t < 26.2 ? lerp(560, 330, eout(seg(t, 23.6, 25.0))) : lerp(330, -140, Math.pow(seg(t, 26.2, 29.2), 1.7));
    if (t > 23.6) bus(g, R(bx), 268);
    if (gust) { windLines(g, t, 16); seeds(g, t, 40, 22.66); }
    if (t > 26.6) clawd(g, R(bx) + 48, 256, 1.2, { look: FRIEND, aR: 'wave', eyes: 'happy' }, t);
  },
  clouds(g, t) {
    grad(g, ['#5AA2E8', '#9BD0F6', '#E4F4FC'], 0, 200);
    for (let i = 0; i < 5; i++) cloud(g, R(((t * 4 + i * 120) % 620) - 80), 26 + (i % 3) * 22, 1.3 + (i % 2) * .6);
    disc(g, 240, 420, 230, '#78B85A'); disc(g, 240, 424, 226, '#8ACB64');
    for (let i = 0; i < 40; i++) { const x = R(40 + H(i) * 400), y = R(208 + H(i + 4) * 60); if (y > 196 + Math.abs(x - 240) * .3) rect(g, x, y, 1, 2, '#6CA84A'); }
    // a kite on the wind, the string to his hand
    const kx = 330 + R(Math.sin(t * .9) * 16), ky = 70 + R(Math.sin(t * 1.3) * 8);
    line(g, 263, 178, kx, ky + 8, '#F4F4F4');
    for (let j = 0; j < 9; j++) rect(g, kx - (j < 5 ? j : 8 - j), ky - 4 + j, 1 + 2 * (j < 5 ? j : 8 - j), 1, j < 5 ? '#E8436E' : '#F2C14E');
    for (let j = 0; j < 4; j++) rect(g, kx + R(Math.sin(t * 4 + j) * 2), ky + 6 + j * 3, 1, 2, '#FFFFFF');
    clawd(g, 236, 200, 4, { sit: true, aR: 'out', eyes: t > 33 ? 'happy' : 'open', blush: .5 }, t);
    for (let i = 0; i < 2; i++) { const bx = R(120 + i * 220 + Math.sin(t * .7 + i * 3) * 40), by = R(150 + Math.cos(t * 1.1 + i) * 20), up = Math.floor(t * 8 + i) % 2; rect(g, bx - 2, by - up, 2, 2, '#FFE08A'); rect(g, bx + 1, by - up, 2, 2, '#FFE08A'); rect(g, bx, by, 1, 2, INK); }
    // the song takes a breath before the drums: everything dims
    blackout(g, Math.pow(seg(t, 38.4, 41.7), 1.3) * .92);
  },
  meet(g, t) {
    grad(g, ['#F28C5C', '#F7B267', '#FCDCA0'], 0, 200);
    sun(g, 430, 150, 24, '#FFE9A0', '#FFC86A');
    const bl = ['#A85A4A', '#B86A52', '#9A5248'];
    for (let i = 0; i < 9; i++) building(g, i * 56 - 10, 50, 70 + R(H(i) * 60), 210, bl[i % 3], .25, i, t);
    rect(g, 0, 208, PW, 22, '#C9A07A'); rect(g, 0, 208, PW, 1, '#E8C8A0'); rect(g, 0, 230, PW, 40, '#6A5A64'); for (let x = 0; x < PW; x += 26) rect(g, x - R(t * 60) % 26 + 26, 248, 12, 2, '#E8D8C8');
    vending(g, 60, 222);
    // she walks in from the light in white sneakers
    const sx = lerp(520, 300, eio(seg(t, 42.3, 47.6))), walking = t < 47.6;
    for (let j = 0; j < 4; j++) rect(g, R(sx - 40 - j * 8), 220 + j, 40, 1, '#B07A5A');            // long shadow
    clawd(g, sx, 222, 4, { look: YOU, bow: true, shoes: true, walk: walking ? beatPos(t) / 2 : null, eyes: t > 48.6 ? 'happy' : 'open', flip: true }, t);
    rect(g, R(sx) + 20, 190, 1, 24, '#FFE08A'); rect(g, R(sx) + 20, 192, 1, 2, '#FFFFFF');      // the golden edge of her
    clawd(g, 124, 222, 4, { eyes: t > 44 ? 'wide' : 'open', hold: (g2, hx, hy) => soda(g2, hx, hy + 4), aR: 'out' }, t);
    // the world keeps going: people and bikes rush past both of them
    if (t > 49.38) {
      const k = seg(t, 49.38, 50.2);
      for (let i = 0; i < 9; i++) {
        const dir = i % 2 ? 1 : -1, sp = 220 + 90 * H(i), x = R(dir > 0 ? ((t - 49.38) * sp + H(i) * 600) % 640 - 80 : 560 - ((t - 49.38) * sp + H(i) * 600) % 640), y = i % 3 === 0 ? 260 : 236;
        if (k < 1 && H(i + 3) > k) continue;
        checker(g, x - dir * 26, y - 16, 22, 14, '#FFFFFF', .25);
        clawd(g, x, y, i % 3 === 0 ? 3.4 : 2.4, { look: PASSERS[i % 4], walk: t * 4 + i, flip: dir < 0 }, t);
      }
    }
  },
  sure(g, t) {
    const kp = kickPulse(t);
    if (t < 59.32) {
      grad(g, ['#F7B267', '#F79D65', '#E66F5C'], 0, PH);
      for (let i = 0; i < 30; i++) rect(g, R((H(i) * PW + t * 30 * (H(i + 2) - .5)) % PW + PW) % PW, R(H(i + 5) * PH), 2, 2, '#FFD0A0');
      clawd(g, 240, 204, 13, { eyes: 'wide', blush: seg(t, 57, 58.5) }, t);
      heart(g, 240 + R(Math.sin(t * 2) * 6), 40, 3 + R(kp * 2));
    } else if (t < 64.9) {
      grad(g, ['#FCD2E0', '#F7B8C8', '#F29BB8'], 0, PH);
      for (let i = 0; i < 14; i++) if (Math.floor(t * 6 + i) % 3) sparkle(g, R(H(i) * PW), R(H(i + 7) * 200), 1 + (i % 2));
      clawd(g, 240, 204, 13, { look: YOU, bow: true, eyes: t > 60.4 ? 'happy' : 'open', blush: seg(t, 60.4, 61.2), smile: t > 60.4 }, t);
    } else {
      grad(g, ['#FFE3A8', '#FCC8B0', '#F7B8C8'], 0, PH);
      const c = eio(seg(t, 64.9, 67.6));
      clawd(g, lerp(150, 200, c), 220, 6, { eyes: 'happy', blush: 1 }, t);
      clawd(g, lerp(330, 280, c), 220, 6, { look: YOU, bow: true, shoes: true, eyes: 'happy', blush: 1 }, t);
      if (c > .4) heart(g, 240, 120 + R(Math.sin(t * 4) * 3), 3);
      for (let i = 0; i < 24; i++) if (H(i + Math.floor(t * 8)) < seg(t, 65, 68.4)) sparkle(g, R(H(i * 3) * PW), R(H(i * 5) * PH), 2);
      whiteout(g, Math.pow(seg(t, 67.6, 68.5), 1.5));
    }
  },
  ride(g, t) {
    grad(g, ['#FF9E7A', '#FFC48C', '#FFE3A8'], 0, 150);
    sun(g, 360, 148, 30, '#FFF0B0', '#FFC86A');
    for (const [x, w, h] of [[60, 80, 10], [150, 50, 6], [420, 90, 12]]) { rect(g, x, 150 - h, w, h, '#B86A72'); }
    rect(g, 0, 150, PW, 60, '#4A78C0');
    for (let y = 152; y < 210; y += 4) for (let x = 0; x < PW; x += 16) if (H(x * 3 + y + Math.floor(t * 4)) > .6) rect(g, (x + R(t * 10 * (y - 140) / 40)) % PW, y, 4 + R((y - 150) / 10), 1, y < 170 ? '#FFD8A0' : '#7AA8E0');
    for (let i = 0; i < 6; i++) rect(g, 345 + R(H(i + Math.floor(t * 5)) * 30), 154 + i * 8, 6 + i * 2, 1, '#FFF0B0');
    const sc = t * 140;
    rect(g, 0, 208, PW, 6, '#C8B8A0'); for (let x = -40; x < PW + 40; x += 40) rect(g, x - R(sc * .9) % 40, 202, 2, 8, '#8A7A6A');
    rect(g, 0, 214, PW, 56, '#5A5A6A'); for (let x = -40; x < PW + 40; x += 40) rect(g, x - R(sc) % 40, 246, 20, 2, '#F2E8D0');
    // the two of them on one bike; the road dashes and palms rush past
    const by = 240 + beatHop(t, 1);
    bike(g, 236, by, t, 1.6);
    clawd(g, 248, by - 30, 3, { sit: true, aR: 'out', eyes: 'happy' }, t);
    clawd(g, 206, by - 28, 3, { look: YOU, bow: true, sit: true, shoes: true, aL: t > 75.04 ? 'wave' : 'down', eyes: 'happy', blush: 1 }, t);
    for (let i = 0; i < 4; i++) { const x = R(((i * 170 - sc * 1.4) % 680 + 680) % 680) - 100; palm(g, x, 270, 1.6); }
  },
  night(g, t) {
    grad(g, ['#0B1030', '#1B2550', '#2E3A70'], 0, 165); stars(g, t, 70, 150, 3);
    disc(g, 120, 50, 12, '#F4F0D8'); disc(g, 125, 47, 10, '#0B1030');
    rect(g, 0, 160, PW, 42, '#1E2A58'); for (let i = 0; i < 26; i++) if (H(i + Math.floor(t * 3)) > .4) rect(g, 110 + R(H(i * 3) * 22), 164 + i * 1.5, 4 + R(H(i) * 8), 1, '#F4F0D8');
    for (let i = 0; i < 6; i++) rect(g, R((i * 90 + t * 12) % PW), 166 + i * 6, 30, 1, '#2E3E78');
    rect(g, 0, 200, PW, 70, '#3A3550'); rect(g, 0, 200, PW, 2, '#5A5478');
    if (t < 91.92) {
      // eyes shut, he still sees her beside him
      clawd(g, 206, 238, 4, { eyes: 'closed', blush: .5 }, t);
      clawd(g, 268, 238, 4, { look: YOU, bow: true, shoes: true, eyes: 'happy', alpha: .25 + .65 * eio(seg(t, 83, 86.5)), glow: '#FFB8D0' }, t);
      for (let i = 0; i < 14; i++) { const x = R(100 + H(i) * 300 + Math.sin(t * .8 + i) * 20), y = R(150 + H(i + 3) * 70 + Math.cos(t + i) * 10); if (Math.sin(t * 3 + i * 2) > 0) rect(g, x, y, 1, 1, '#FFF08A'); }
    } else {
      // ice lollies on a bench by the seaside shop
      rect(g, 300, 150, 120, 60, '#2A2440'); rect(g, 296, 144, 128, 8, '#E8436E'); for (let x = 296; x < 424; x += 16) rect(g, x, 152, 8, 4, '#FFFFFF');
      halo(g, 360, 175, 46, '#FFE08A'); rect(g, 312, 160, 96, 30, '#FFE08A');
      ptext(g, '冰', 360, 182, { col: '#3A78D0' });
      bench(g, 225, 240);
      clawd(g, 204, 232, 4, { sit: true, eyes: 'happy', aR: 'out', hold: (g2, hx, hy) => popsicle(g2, hx, hy) }, t);
      clawd(g, 246, 232, 4, { look: YOU, bow: true, sit: true, shoes: true, eyes: 'happy', blush: 1, flip: true, aR: 'out', hold: (g2, hx, hy) => popsicle(g2, hx, hy) }, t);
    }
  },
  rain(g, t) {
    grad(g, ['#141A30', '#232C4A', '#2E3858'], 0, 200);
    for (let i = 0; i < 8; i++) building(g, i * 64 - 20, 56, 40 + R(H(i + 20) * 70), 200, '#1C2238', .3, i + 20, t);
    rect(g, 0, 200, PW, 70, '#2A2E40'); for (let x = 0; x < PW; x += 30) rect(g, x, 232, 16, 2, '#4A4E62');
    // street lamp and its cone of light
    rect(g, 360, 120, 3, 112, '#4A4E62'); rect(g, 352, 118, 18, 4, '#4A4E62'); rect(g, 356, 122, 10, 3, '#FFE9A8');
    for (let y = 125; y < 232; y++) { const w = R((y - 125) * .45); checker(g, 361 - w, y, w * 2, 1, '#FFE9A8', .22); }
    // a signpost at the crossroads
    rect(g, 120, 150, 3, 82, '#6A6E80'); rect(g, 96, 152, 28, 8, '#3A9A5A'); rect(g, 92, 154, 4, 4, '#3A9A5A'); rect(g, 123, 164, 28, 8, '#3A9A5A'); rect(g, 151, 166, 4, 4, '#3A9A5A');
    const look = t < 101 ? (Math.floor(beatPos(t) / 2) % 2 ? 1 : -1) : 1, mx = t < 101 ? 150 : lerp(150, 330, eio(seg(t, 101, 103.6)));
    umbrella(g, R(mx), 190, '#3A78D0');
    clawd(g, mx, 232, 4, { flip: look < 0, eyes: t < 101 ? 'open' : 'happy', walk: t > 101 && t < 103.6 ? beatPos(t) / 2 : null }, t);
    umbrella(g, 378, 190, '#E8436E');
    clawd(g, 378, 232, 4, { look: YOU, bow: true, shoes: true, eyes: 'happy', aL: t > 102.5 ? 'wave' : 'down' }, t);
    rain(g, t, 160);
    for (let i = 0; i < 6; i++) { const p = ((t * 1.3 + H(i)) % 1); ring(g, R(60 + H(i * 3) * 380), 250 + R(H(i) * 14), R(1 + p * 5), '#5A6488'); }
  },
  roof(g, t) {
    grad(g, ['#080A20', '#141C44', '#2A2E62'], 0, 190); stars(g, t, 140, 180, 7);
    // a shooting star at each phrase and on some kicks
    for (const s0 of [104.4, 108.1, 110.9, 114.2]) { const a = t - s0; if (a > 0 && a < .8) { const x = R(380 - a * 300), y = R(30 + a * 90); for (let j = 0; j < 14; j++) rect(g, x + j * 2, y - j * .6, 2, 1, j < 3 ? '#FFFFFF' : '#9FB0E0'); } }
    for (let i = 0; i < 10; i++) building(g, i * 50 - 10, 46, 170 + R(H(i + 40) * 30), 230, '#141830', .35, i + 40, t);
    rect(g, 0, 214, PW, 56, '#3A3A52'); rect(g, 0, 214, PW, 2, '#5A5A78');
    rect(g, 380, 150, 46, 64, '#4A4A64'); rect(g, 376, 146, 54, 6, '#5A5A78'); for (let y = 160; y < 214; y += 10) rect(g, 380, y, 46, 1, '#3A3A52');
    rect(g, 70, 140, 2, 74, '#6A6A80'); rect(g, 62, 150, 18, 1, '#6A6A80'); if (Math.floor(t * 2) % 2) rect(g, 70, 138, 2, 2, '#FF5050');
    const lean = eio(seg(t, 110.86, 112.2));
    clawd(g, 216, 220, 4, { sit: true, eyes: lean > .5 ? 'happy' : 'open', blush: lean }, t);
    clawd(g, lerp(266, 254, lean), 220, 4, { look: YOU, bow: true, sit: true, shoes: true, eyes: lean > .5 ? 'closed' : 'open', blush: lean }, t);
    if (lean > .5) heart(g, 236, 160 + R(Math.sin(t * 3) * 2), 1);
  },
  fireworks(g, t) {
    grad(g, ['#080A20', '#1A1A4A', '#3A2A62'], 0, 190); stars(g, t, 60, 160, 9);
    for (let i = 0; i < 12; i++) building(g, i * 42 - 10, 40, 150 + R(H(i + 60) * 50), 230, '#141830', .4, i + 60, t);
    const cols = ['#FF5C8A', '#FFE08A', '#8FE0F0', '#B58EF0', '#FF9E5A'];
    kicksIn(116.2, t).slice(-6).forEach((k, j) => {
      const a = t - k, i = R(k * 100), cx = R(80 + H(i) * 320), cy = R(50 + H(i + 1) * 70), col = cols[i % 5];
      if (a < .25) { rect(g, cx, R(cy + (1 - a / .25) * 120), 1, 4, '#FFF0C0'); return; }
      const b = a - .25; if (b > 1.6) return;
      for (let s = 0; s < 26; s++) { const an = s / 26 * Math.PI * 2, r = 46 * eout(b / 1.1), x = R(cx + Math.cos(an) * r), y = R(cy + Math.sin(an) * r + b * b * 14); if (H(s + i) < 1 - b / 1.6) rect(g, x, y, 2, 2, col); rect(g, R(cx + Math.cos(an) * r * .6), R(cy + Math.sin(an) * r * .6 + b * b * 10), 1, 1, '#FFFFFF'); }
    });
    rect(g, 0, 214, PW, 56, '#3A3A52'); rect(g, 0, 214, PW, 2, '#5A5A78');
    const up = t > 120.2;
    clawd(g, 214, 214, 4, { aL: up ? 'up' : 'down', aR: up ? 'up' : 'down', eyes: 'happy', dy: up ? beatHop(t, 2) : 0 }, t);
    clawd(g, 266, 214, 4, { look: YOU, bow: true, shoes: true, aL: up ? 'up' : 'down', aR: up ? 'up' : 'down', eyes: 'happy', dy: up ? beatHop(t + .2, 2) : 0 }, t);
  },
  pieces(g, t) {
    grad(g, ['#140E30', '#22184A', '#3A2A66'], 0, PH); stars(g, t, 80, PH, 11);
    // he is a grid of eight pieces; one by one they turn into hers
    const k = 12, cx = 240, gy = 214, x0 = cx - 5 * k, y0 = gy - 8 * k, cw = 30, ch = 36;
    const glow = seg(t, 139.4, 140.4) * (1 - seg(t, 149, 150.2) * .5);
    if (glow > 0) halo(g, cx, gy - 4 * k, 110, '#FFE9A8');
    const hugX = eio(seg(t, 146.4, 147.6));
    clawd(g, cx - 40 * hugX, gy, k * (1 - .5 * hugX), { eyes: t > 139.4 ? 'happy' : 'open', blush: glow }, t);
    if (hugX < 1) {
      const fly = [123.3, 124.1, 124.9, 125.7, 130.04];
      for (let c = 0; c < 8; c++) {
        const col = c % 4, row = Math.floor(c / 4), px = x0 + col * cw, py = y0 + row * ch;
        if (c < 5 && t >= fly[c]) {
          const a = eout(seg(t, fly[c], fly[c] + .5));
          rect(g, px + 2, py + 2, cw - 4, ch - 4, a < 1 ? mixHex('#D97757', '#F29BB8', a) : '#F29BB8'); rect(g, px + 2, py + 2, cw - 4, 2, '#FCD2E0');
          // eyes stay on top of the pieces
          ICONS[c](g, px + cw / 2, py + ch / 2 + (row ? 4 : 10));
          // the memory flies in from the edge as a little polaroid
          if (a < 1) { const fx = R(lerp(c % 2 ? 470 : 10, px + cw / 2, a)), fy = R(lerp(20 + c * 40, py + ch / 2, a)); rect(g, fx - 8, fy - 9, 16, 18, '#F4F0E8'); rect(g, fx - 6, fy - 7, 12, 10, '#3A2A66'); ICONS[c](g, fx, fy - 2); }
        } else rect(g, px + 2, py + 2, cw - 4, 1, '#C0623E');
        rect(g, px, py, 1, ch, '#A84D33'); rect(g, px, py, cw, 1, '#A84D33');
      }
      for (const ex of [-3, 2]) rect(g, cx + ex * k, gy - 7 * k, k, 2 * k, INK);
      if (t > 139.4) { for (const ex of [-3, 2]) rect(g, cx + ex * k, gy - 7 * k, k, 2 * k, '#F29BB8'); for (const ex of [-3, 2]) { rect(g, cx + ex * k, gy - 6 * k, k, 2, INK); rect(g, cx + ex * k - 2, gy - 6 * k + 2, 2, 2, INK); rect(g, cx + ex * k + k, gy - 6 * k + 2, 2, 2, INK); } }
      if (glow > 0) for (let i = 0; i < 10; i++) if (Math.floor(t * 6 + i) % 2) sparkle(g, R(cx - 80 + H(i) * 160), R(gy - 110 + H(i + 3) * 110), 2, '#FFE9A8');
    } else {
      clawd(g, cx + 40, gy, 6, { look: YOU, bow: true, shoes: true, eyes: 'happy', blush: 1, aL: 'hug' }, t);
      for (let i = 0; i < 5; i++) { const p = ((t - 147) * .5 + i / 5) % 1; heart(g, R(cx - 30 + i * 15), R(gy - 70 - p * 80), 1, '#FF7FA0'); }
    }
  },
  station(g, t) {
    grad(g, ['#5E4B8B', '#C77DA0', '#F2B48C'], 0, 175);
    for (let i = 0; i < 8; i++) building(g, i * 62 - 20, 54, 110 + R(H(i + 80) * 40), 180, '#6A4A70', .2, i + 80, t);
    rect(g, 0, 176, PW, 50, '#4A4050'); rect(g, 0, 214, PW, 4, '#2A2430'); rect(g, 0, 222, PW, 4, '#2A2430');
    // the train arrives, waits, and pulls away to the left
    const tx = t < 154.3 ? lerp(520, 40, eout(seg(t, 150.3, 152.4))) : 40 - 260 * Math.pow(t - 154.3, 2);
    const boarded = t > 153.2;
    train(g, R(tx), 222, 3, boarded && t < 156.5 ? { car: 1, win: 1, T: t } : null);
    // the platform and its roof
    rect(g, 0, 226, PW, 44, '#9A92A0'); rect(g, 0, 226, PW, 3, '#F2C14E'); for (let x = 0; x < PW; x += 32) rect(g, x, 236, 1, 34, '#8A8290');
    rect(g, 0, 0, PW, 14, '#3A3040'); for (let x = 30; x < PW; x += 120) rect(g, x, 14, 4, 212, '#5A5060');
    const sx = lerp(270, 200, eio(seg(t, 151.6, 153.1)));
    if (!boarded) clawd(g, sx, 238, 4, { look: YOU, bow: true, shoes: true, walk: t > 151.6 ? beatPos(t) / 2 : null, eyes: 'happy', flip: true }, t);
    const run = seg(t, 154.6, 156.4), mx = t < 156.66 ? lerp(320, 210, eout(run)) : 240;
    if (t < 156.66) clawd(g, mx, 238, 4, { aR: 'wave', eyes: t > 155.6 ? 'closed' : 'open', walk: run > 0 && run < 1 ? t * 3 : null }, t);
    else clawd(g, mx, 238, 4, { eyes: 'closed', blush: .4, hold: (g2, hx, hy) => shard(g2, R(hx - 18), hy + 4, 2, t) }, t);
    if (t > 156.66) for (let i = 0; i < 20; i++) rect(g, R((H(i) * PW + t * 6) % PW), R((H(i + 2) * 200 + t * 10) % 220), 1, 1, '#FFE0F0');
  },
  apart(g, t) {
    if (t < 173.06) {
      grad(g, ['#0E1228', '#1A2040', '#262E52'], 0, 210);
      for (let i = 0; i < 8; i++) building(g, i * 64 - 20, 56, 70 + R(H(i + 100) * 60), 210, '#141A30', .22, i + 100, t);
      rect(g, 0, 208, PW, 62, '#22263A');
      // the bus stop shelter
      rect(g, 160, 120, 4, 112, '#5A6070'); rect(g, 316, 120, 4, 112, '#5A6070'); rect(g, 150, 114, 180, 8, '#3A78D0');
      checker(g, 164, 122, 152, 90, '#8FA8D8', .18);
      bench(g, 240, 232);
      clawd(g, 222, 228, 4, { sit: true, eyes: 'closed' }, t);
      const ghost = (.55 + .2 * kickPulse(t)) * (1 - seg(t, 170.5, 172.6)) * seg(t, 163.8, 165.5);
      if (ghost > .05) clawd(g, 260, 228, 4, { look: YOU, bow: true, sit: true, shoes: true, eyes: 'closed', blush: 1, alpha: ghost, glow: '#FFB8D0' }, t);
      rain(g, t, 180, '#6A80B0');
    } else if (t < 179.9) {
      grad(g, ['#05060F', '#0E1028', '#1A1A40'], 0, PH); stars(g, t, 120, PH, 13);
      // two windows in two cities, drifting further apart
      const gap = R(12 + Math.pow(t - 173.06, 1.4) * 14);
      for (const [side, look] of [[-1, ME], [1, YOU]]) {
        const wx = 240 + side * (gap / 2 + 66) - 60, wy = 70;
        rect(g, wx - 2, wy - 2, 124, 104, INK); rect(g, wx, wy, 120, 100, '#2A2440'); checker(g, wx + 20, wy + 10, 80, 86, '#FFE08A', .18); checker(g, wx + 38, wy + 30, 44, 66, '#FFE08A', .22);
        rect(g, wx + 59, wy, 2, 100, INK); rect(g, wx, wy + 49, 120, 2, INK);
        clawd(g, wx + 60, wy + 98, 4, look === YOU ? { look: YOU, bow: true, eyes: 'closed' } : { eyes: 'closed' }, t);
      }
      for (let i = 0; i < 10; i++) rect(g, 240 + R((H(i) - .5) * gap), R((t * 80 + H(i + 4) * PH) % PH), 1, 3, '#FFFFFF');
    } else {
      grad(g, ['#05060F', '#120E30', '#2A1A50'], 0, PH);
      // the memories rush past like a starfield, faster on every kick
      const sp = 1 + 2 * kickPulse(t, 5);
      for (let i = 0; i < 60; i++) {
        const z = ((t - 179.9) * .5 * sp + H(i)) % 1, a = H(i + 7) * Math.PI * 2, r = z * z * 320, x = R(240 + Math.cos(a) * r), y = R(135 + Math.sin(a) * r);
        if (i % 6 === 0 && z > .3) ICONS[i % 5](g, x, y); else rect(g, x, y, z > .6 ? 2 : 1, z > .6 ? 2 : 1, z > .5 ? '#FFFFFF' : '#9FB0E0');
      }
      clawd(g, 240, 168, 4, { eyes: 'closed', hold: (g2, hx, hy) => shard(g2, R(hx - 18), hy + 4, 2, t) }, t);
      whiteout(g, Math.pow(seg(t, 185.6, 186.42), 1.5));
    }
  },
  seasons(g, t) {
    const S = t < 193.22 ? 0 : t < 199.78 ? 1 : t < 205.62 ? 2 : 3;
    const skies = [['#3E8EDE', '#79B8F0', '#CDE8FA'], ['#C8784A', '#E8A870', '#F6D8A8'], ['#7A8AA8', '#A8B8D0', '#DCE4F0'], ['#F28C5C', '#F7B267', '#FCDCA0']];
    const grounds = [['#8ACB64', '#78B85A'], ['#C8A050', '#B08A40'], ['#EEF2F8', '#D8E0EC'], ['#8ACB64', '#78B85A']];
    const fol = [['#4E9A4A', '#6CB85A'], ['#D8743A', '#F2A04A'], null, ['#5AA04E', '#7AC060']];
    grad(g, skies[S], 0, 200);
    if (S === 3) sun(g, 380, 130, 22, '#FFE9A0', '#FFC86A');
    rect(g, 0, 196, PW, 74, grounds[S][1]); disc(g, 240, 420, 236, grounds[S][0]);
    treeOnHill(g, 300, 200, fol[S], t, S === 2);
    bench(g, 238, 214);
    const aged = S >= 2;
    clawd(g, 220, 210, 4, { look: aged ? AGED : ME, sit: true, aged, cane: aged, eyes: S === 3 ? 'happy' : 'closed',
      hold: S === 3 ? (g2, hx, hy) => shard(g2, R(hx - 18), hy + 4, 2, t) : null }, t);
    // the empty seat beside him; for a moment in the last summer she is there again
    const ghost = S === 3 ? seg(t, 207.5, 209) * (1 - seg(t, 211.6, 213.4)) * .5 : 0;
    if (ghost > .03) clawd(g, 262, 210, 4, { look: YOU, bow: true, sit: true, shoes: true, eyes: 'happy', alpha: ghost, glow: '#FFB8D0' }, t);
    if (S === 1) leaves(g, t, 50, ['#D8743A', '#F2A04A', '#B5432F']);
    if (S === 2) snow(g, t, 120);
    if (S === 0 || S === 3) for (let i = 0; i < 3; i++) bird(g, R(((t - 186) * 16 + i * 30) % 520) - 20, 60 + i * 8, t + i);
  },
  end(g, t) {
    const p = qz(seg(t, 214.1, 221), 8);
    grad(g, [mixHex('#F28C5C', '#2A1A40', p), mixHex('#F7B267', '#6A3A60', p), mixHex('#FCDCA0', '#C8705A', p)], 0, 188);
    sun(g, 300, R(lerp(150, 196, seg(t, 214.1, 222))), 20);
    rect(g, 0, 188, PW, 82, mixHex('#6FA050', '#2A3A2A', p));
    for (let i = 0; i < 6; i++) rect(g, 0, 192 + i * i * 2.4, PW, 1, mixHex('#7FB45A', '#34482E', p));
    treeOnHill(g, 400, 192, ['#4E7E3A', '#5E9048'], t); bench(g, 360, 196);
    clawd(g, 352, 190, 1.5, { look: AGED, sit: true, aged: true, eyes: 'closed' }, t);
    grassRow(g, t, 270, '#3E6A30', 2, 1, 3);
    const ty = seg(t, 215.5, 217.2), chars = [...'几分之几'];
    if (ty > 0) ptext(g, chars.slice(0, Math.ceil(ty * 4)).join(''), 200, 96, { size: 36, col: '#FFF4D6', outline: INK, shadow: '#7A3A2A' });
    if (t > 217.6) ptext(g, '卢广仲 · 像素 MV', 200, 120, { col: '#FFE9C8', outline: INK });
    blackout(g, seg(t, 222.4, 225.2));
  },
};

// ---------------------------------------------------------------- one frame
const XF = .4;
let bufA = null, bufB = null;
function shotInto(g, i, t) { g.setTransform(1, 0, 0, 1, 0, 0); g.imageSmoothingEnabled = false; SCENES[SHOTS[i].name](g, t); }
function drawFrame(g, t) {
  t = clamp(t, 0, DUR - 1e-4);
  if (!bufA) { bufA = document.createElement('canvas'); bufB = document.createElement('canvas'); bufA.width = bufB.width = PW; bufA.height = bufB.height = PH; }
  const i = shotIndex(t), s = SHOTS[i];
  if (i > 0 && t - s.t0 < XF && !['sure', 'ride', 'seasons', 'meet'].includes(s.name)) {
    shotInto(bufA.getContext('2d'), i - 1, t); shotInto(bufB.getContext('2d'), i, t);
    ditherMix(g, bufA, bufB, (t - s.t0) / XF);
  } else shotInto(g, i, t);
  // the pie: how much of him is hers
  const n = slicesAt(t), showPie = (t > 68.51 && t < 163.44) || (t > 205.62 && t < 214.08);
  if (showPie && s.name !== 'pieces') { pie(g, t, 16, 16, 9, n, 8, t > 150.22 ? 1 : 0); if (SLICES.some(x => t >= x && t < x + .4)) sparkle(g, 16, 16, 12, '#FFFFFF'); }
  subtitle(g, t);
}
