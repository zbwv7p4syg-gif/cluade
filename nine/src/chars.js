// chars.js — the two characters, drawn from parts on a small scratch canvas (facing right), then outlined in
// one pass (every empty pixel that touches the silhouette becomes ink) and stamped onto the frame.
//   我 (the boy): kid → teen → man. Same round head, white sneakers, a little taller each time.
//   九九 (the dog): a yellow village dog with four white paws, "金色的侧脸踩着全白球鞋".

const SKIN = '#F6CFA8', SKIN_D = '#DFA67E', HAIR = '#2E2420', HAIR_L = '#55443A', EYE = '#2B1D16', BLUSH = '#F3A08F';
const SHOE = '#FFFFFF', SHOE_D = '#C8CCD8';
const OUTFITS = {
  kid: { shirt: '#6FB3E3', shirtD: '#4B8CC0', pants: '#3C4A6E', pantsD: '#2C3756' },
  teen: { shirt: '#F4F4EE', shirtD: '#C8CDD8', pants: '#33415F', pantsD: '#26304A' },
  man: { shirt: '#6A8FC4', shirtD: '#4C6D9E', pants: '#BCA27A', pantsD: '#957D58' },
  dad: { shirt: '#6E9E58', shirtD: '#527A42', pants: '#4A4A58', pantsD: '#36363F' },
  sleep: { shirt: '#F0E2C8', shirtD: '#D2BF9C', pants: '#8EA4C8', pantsD: '#6F84A8' },
  mom: { shirt: '#E8909C', shirtD: '#C46E7C', pants: '#5A5A78', pantsD: '#44445C' },
  farmer: { shirt: '#D8D0BC', shirtD: '#B4AA92', pants: '#5E6E8C', pantsD: '#485670' },
};
// the bodies; heads are 10 wide, the man's is one row taller
const BUILD = {
  kid: { shirtH: 5, legH: 3, shorts: true, bodyW: 7, headH: 9 },
  teen: { shirtH: 6, legH: 5, shorts: false, bodyW: 7, headH: 9 },
  man: { shirtH: 7, legH: 6, shorts: false, bodyW: 8, headH: 10 },
};
// heads, facing right (3/4 view) and facing front. h hair, H hair light, s skin, k skin shade
const HEADS = {
  kid: {
    side: ['..hhhhhh..', '.hhHHhhhh.', 'hhHhhhhhhh', 'hhhhhhhhhh', 'hhhhhshhhs', 'hhhsssssss', 'hhksssssss', '.hhsssssss', '..kssssss.'],
    front: ['..hhhhhh..', '.hhHHhhhh.', 'hhHhhhhhhh', 'hhhhhhhhhh', 'hhhshhhshh', 'hsssssssss', 'hsssssssss', '.ssssssss.', '..ssssss..'],
  },
  teen: {
    side: ['.h.hh.h...', '.hhhhhhhh.', 'hhHHhhhhhh', 'hhhhhhhhhh', 'hhhhhhshhs', 'hhhsssssss', 'hhksssssss', '.hhsssssss', '..kssssss.'],
    front: ['.h.hh.h...', '.hhhhhhhh.', 'hhHHhhhhhh', 'hhhhhhhhhh', 'hhhshhhhsh', 'hsssssssss', 'hsssssssss', '.ssssssss.', '..ssssss..'],
  },
  man: {
    side: ['..hhhhhh..', '.hhHHhhhhh', 'hhHhhhhhhh', 'hhhhhhhhhh', 'hhhhhhhsss', 'hhhsssssss', 'hhksssssss', 'hhksssssss', '.kksssssss', '..kssssss.'],
    front: ['..hhhhhh..', '.hhHHhhhh.', 'hhHhhhhhhh', 'hhhhhhhhhh', 'hhhhhhsssh', 'hsssssssss', 'hsssssssss', 'hsssssssss', '.ssssssss.', '..ssssss..'],
  },
};
const HEAD_COL = { h: HAIR, H: HAIR_L, s: SKIN, k: SKIN_D };

// ---------------------------------------------------------------- sprite plumbing
// a scratch sprite canvas: (OX, OY) is the character's centre and ground line
const SW = 64, SHt = 56, OX = 32, OY = 48;
function spriteBegin(name) { const c = scratch(name, SW, SHt), cg = c.getContext('2d'); cg.clearRect(0, 0, SW, SHt); return { c, cg }; }
function outlinePass(cg, w, h, col = INK) {
  const img = cg.getImageData(0, 0, w, h), d = img.data, a = new Uint8Array(w * h);
  for (let i = 0; i < w * h; i++) a[i] = d[i * 4 + 3] > 0 ? 1 : 0;
  const c = hex(col);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = y * w + x; if (a[i]) continue;
    if ((x > 0 && a[i - 1]) || (x < w - 1 && a[i + 1]) || (y > 0 && a[i - w]) || (y < h - 1 && a[i + w])) { d[i * 4] = c[0]; d[i * 4 + 1] = c[1]; d[i * 4 + 2] = c[2]; d[i * 4 + 3] = 255; }
  }
  cg.putImageData(img, 0, 0);
}
// stamp a sprite: flip mirrors around the centre column, rot = -90 lays it on its back (head to the left),
// alpha < 1 lets only part of the pixels through (an ordered-dither fade that stays put on screen)
function stamp(g, c, x, y, o = {}) {
  let src = c, ox = OX, oy = OY, w = c.width, h = c.height;
  if (o.rot === -90) {
    const r = scratch('rot', h, w), rg = r.getContext('2d'); rg.clearRect(0, 0, h, w);
    rg.save(); rg.translate(0, w); rg.rotate(-Math.PI / 2); rg.drawImage(c, 0, 0); rg.restore();
    src = r; [ox, oy] = [oy, w - 1 - ox]; [w, h] = [h, w];
    oy += 1;
  }
  if (o.flip) {
    const f = scratch('flip' + w + 'x' + h, w, h), fg = f.getContext('2d'); fg.clearRect(0, 0, w, h);
    fg.save(); fg.translate(w, 0); fg.scale(-1, 1); fg.drawImage(src, 0, 0); fg.restore();
    src = f; ox = w - 1 - ox;
  }
  const X = R(x) - ox, Y = R(y) - oy;
  if (o.alpha != null && o.alpha < 1) {
    if (o.alpha <= 0) return;
    const sg = src.getContext('2d'), img = sg.getImageData(0, 0, w, h), d = img.data;
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) if (bayer(X + i, Y + j) >= o.alpha) d[(j * w + i) * 4 + 3] = 0;
    const t = scratch('alphaTmp' + w + 'x' + h, w, h); t.getContext('2d').putImageData(img, 0, 0); src = t;
  }
  if (o.silhouette) {
    const sg = src.getContext('2d'), img = sg.getImageData(0, 0, w, h), d = img.data, c2 = hex(o.silhouette);
    for (let i = 0; i < d.length; i += 4) if (d[i + 3]) { d[i] = c2[0]; d[i + 1] = c2[1]; d[i + 2] = c2[2]; }
    const t = scratch('silTmp' + w + 'x' + h, w, h); t.getContext('2d').putImageData(img, 0, 0); src = t;
  }
  g.drawImage(src, X, Y);
}

// ---------------------------------------------------------------- 我
// o: { age, flip, pose: stand|walk|run|sit|sitFloor|squat|lie, phase, armN/armF: down|fwd|up|wave|hold|hug|cover|back,
//      look: side|front, eyes: open|closed|happy|sad|wide, mouth: smile|open|o|flat, blush, hat, bag, alpha, outfit, silhouette }
function human(g, x, y, o = {}, T = 0) {
  const age = o.age || 'kid', B = BUILD[age], C = OUTFITS[o.outfit || age], { c, cg } = spriteBegin('human');
  const P = (px0, py0, w, h, col) => rect(cg, OX + px0, OY + py0, w, h, col);
  const pose = o.pose || 'stand';
  let ph = o.phase != null ? o.phase : 0, step = 0, bob = 0;
  if (pose === 'walk' || pose === 'run') { step = Math.floor(((ph % 1) + 1) % 1 * 4); bob = step % 2 ? -1 : 0; }
  const shoeH = 2, legH = B.legH, bw = B.bodyW, bl = -4;           // body spans x = bl .. bl + bw - 1
  let hip = -shoeH - legH + bob;                                   // top of the legs
  if (pose === 'sit') hip = -1;                                     // y is the seat; legs dangle forward
  if (pose === 'squat') hip = -shoeH - 2;
  if (pose === 'sitFloor') hip = -2;
  const shortsH = B.shorts ? 2 : 0, shirtBot = hip - shortsH, shirtTop = shirtBot - B.shirtH, headTop = shirtTop - B.headH + 1;
  const legCol = B.shorts ? SKIN : C.pants, legColD = B.shorts ? SKIN_D : C.pantsD;

  // ---- legs and shoes
  const shoe = (sx, sy) => { P(sx, sy, 3, 1, SHOE); P(sx, sy + 1, 3, 1, SHOE_D); };
  if (pose === 'sit') {
    P(bl + 1, hip - 1, bw + 1, 2, C.pants);                                  // thighs on the seat
    P(bl + bw - 1, hip + 1, 2, legH - 1, legCol); shoe(bl + bw - 1, hip + legH);
  } else if (pose === 'sitFloor') {
    P(bl + 1, -3, bw + 4, 3, legColD); P(bl + 1, -3, bw + 4, 2, legCol);
    P(bl + bw + 4, -5, 2, 3, SHOE); P(bl + bw + 4, -2, 2, 2, SHOE_D);
  } else if (pose === 'squat') {
    P(bl + 1, hip, bw, 2, C.pants); P(bl + bw - 3, hip - 2, 4, 2, C.pants);
    shoe(bl + 1, -2); shoe(bl + bw - 3, -2);
  } else {
    let bx = -3, fx = 0, bLift = 0, fLift = 0;
    if (step === 1) { bx -= 1; fx += 1; fLift = pose === 'run' ? 2 : 1; }
    if (step === 3) { bx += 1; fx -= 1; bLift = pose === 'run' ? 2 : 1; }
    if (pose === 'run' && step % 2) { bx -= 1; fx += 1; }
    P(bx, hip, 2, legH - bLift, legColD); shoe(bx - (step === 3 ? 0 : 0), -shoeH - bLift);
    P(fx, hip, 2, legH - fLift, legCol); shoe(fx, -shoeH - fLift);
  }
  if (B.shorts) { P(bl, hip - 2, bw, 2, C.pants); P(bl, hip - 1, bw, 1, C.pantsD); }
  else if (pose !== 'sit' && pose !== 'sitFloor') P(bl, hip - 1, bw, 1, C.pantsD);

  // ---- arms (far arm behind the body, near arm in front)
  const arm = (pose_, near) => {
    const ax = near ? bl + bw : bl - 1, top = shirtTop + 1, col = near ? C.shirt : C.shirtD, sk = near ? SKIN : SKIN_D;
    switch (pose_) {
      case 'fwd': P(ax, top, 1, 1, col); P(ax + 1, top + 1, 3, 1, col); P(ax + 4, top + 1, 1, 1, sk); break;
      case 'up': P(ax, top - 4, 1, 5, col); P(ax, top - 5, 1, 1, sk); break;
      case 'wave': { const w = Math.floor(T * 5) % 2; P(ax + w, top - 4, 1, 5, col); P(ax + w, top - 5, 1, 1, sk); break; }
      case 'hold': P(ax, top, 1, 2, col); P(ax + 1, top + 2, 2, 1, col); P(ax + 3, top + 2, 1, 1, sk); break;
      case 'hug': P(ax, top, 1, 2, col); P(ax + 1, top + 1, 3, 1, col); P(ax + 4, top + 1, 1, 1, sk); break;
      case 'back': P(ax - (near ? 2 : 0), top, 1, 3, col); break;
      case 'cover': P(ax, top - 1, 1, 2, col); break;
      case 'none': break;
      default: P(ax, top, 1, 3, col); P(ax, top + 3, 1, 1, sk);
    }
  };
  arm(o.armF || 'down', false);
  // ---- shirt
  P(bl, shirtTop, bw, B.shirtH, C.shirt); P(bl, shirtTop, 1, B.shirtH, C.shirtD); P(bl, shirtBot - 1, bw, 1, C.shirtD);
  if (age === 'teen') { P(bl + bw - 3, shirtTop, 1, 2, C.shirtD); }                        // collar
  if (age === 'man') { P(bl + bw - 3, shirtTop, 2, 1, C.shirtD); P(bl + 3, shirtTop + 2, 1, B.shirtH - 3, C.shirtD); }
  if (o.bag) { P(bl - 3, shirtTop + 1, 3, B.shirtH - 1, '#C8553D'); P(bl - 3, shirtTop + 1, 3, 1, '#E37B5B'); }
  arm(o.armN || 'down', true);

  // ---- head
  const look = o.look || 'side', rows = HEADS[age][look];
  rows.forEach((r, j) => [...r].forEach((ch, i) => { if (ch !== '.') P(-5 + i, headTop + j, 1, 1, HEAD_COL[ch]); }));
  const ey = headTop + 5, ex = look === 'side' ? [0, 3] : [-2, 1], eyes = o.eyes || 'open';
  const blink = eyes === 'open' && ((T * .8 + (o.seed || 0)) % 3.3) < .13;
  for (const e of ex) {
    if (eyes === 'closed' || blink) P(e, ey + 1, 2, 1, EYE);
    else if (eyes === 'happy') { P(e, ey, 2, 1, EYE); }
    else if (eyes === 'sad') { P(e, ey + 1, 1, 1, EYE); P(e + 1, ey, 1, 1, EYE); }
    else if (eyes === 'wide') P(e, ey - 1, 1, 3, EYE);
    else P(e, ey, 1, 2, EYE);
  }
  if (o.blush) { P(ex[0] - 1, ey + 2, 1, 1, BLUSH); P(ex[1] + 2 > 4 ? 4 : ex[1] + 2, ey + 2, 1, 1, BLUSH); }
  const mx = look === 'side' ? 2 : -1, my = ey + (age === 'man' ? 3 : 2) + 1;
  if (o.mouth === 'smile') { P(mx, my, 2, 1, '#B5574B'); }
  else if (o.mouth === 'open') { P(mx, my, 2, 2, '#B5574B'); }
  else if (o.mouth === 'o') { P(mx + 1, my, 1, 1, '#B5574B'); }
  if (o.armN === 'cover' || o.armF === 'cover') { P(ex[0] - 1, ey - 1, 3, 3, SKIN); P(ex[1], ey - 1, 3, 3, SKIN); P(ex[0] - 1, ey + 1, 3, 1, SKIN_D); P(ex[1], ey + 1, 3, 1, SKIN_D); }
  if (o.long) { P(-6, headTop + 3, 2, B.headH + 1, HAIR); P(-5, headTop + B.headH, 3, 2, HAIR); }
  if (o.helmet) { P(-5, headTop - 1, 10, 4, o.helmet); P(-4, headTop - 2, 8, 1, o.helmet); P(-3, headTop - 1, 2, 1, '#FFFFFF'); P(-5, headTop + 3, 11, 1, INK); }
  if (o.hat === 'straw') { P(-7, headTop + 2, 14, 1, '#E3BC72'); P(-4, headTop - 1, 8, 3, '#EFCD86'); P(-4, headTop + 1, 8, 1, '#C0503A'); }
  if (o.grey) { P(-4, headTop + 1, 2, 1, '#B8B2AA'); P(1, headTop, 2, 1, '#B8B2AA'); }

  outlinePass(cg, SW, SHt);
  if (pose === 'lie') stamp(g, c, x, y, { rot: -90, alpha: o.alpha, flip: o.flip, silhouette: o.silhouette });
  else stamp(g, c, x, y, { flip: o.flip, alpha: o.alpha, silhouette: o.silhouette });
}

// ---------------------------------------------------------------- 九九
const FUR = { fur: '#E2A33C', furL: '#F7CD72', furD: '#B8772D', cream: '#FBE8BE', white: '#FFFFFF', whiteD: '#D6DAE6' };
const FUR_OLD = { fur: '#D9A050', furL: '#EDCB8E', furD: '#AE7A3E', cream: '#E9E3D8', white: '#F6F6F2', whiteD: '#CFD2DA', grey: '#C9C3BA' };
// o: { size: pup|adult, pose: stand|walk|run|sit|lie|sleep|beg|jump, phase, flip, eyes: open|closed|happy, tongue, wag (0..1 speed),
//      collar, old, look: fwd|up|back, alpha, carry: fn(g, x, y) (thing in the mouth), silhouette }
function dog(g, x, y, o = {}, T = 0) {
  const F = o.fur || (o.old ? FUR_OLD : FUR), pup = o.size === 'pup', { c, cg } = spriteBegin('dog');
  const P = (px0, py0, w, h, col) => rect(cg, OX + px0, OY + py0, w, h, col);
  const pose = o.pose || 'stand', ph = (((o.phase || 0) % 1) + 1) % 1;
  // proportions
  const legH = pup ? 2 : 4, bodyH = pup ? 4 : 5, bodyL = pup ? 7 : 14, headW = pup ? 7 : 8, headH = pup ? 6 : 6;
  let bob = 0, frame = 0;
  if (pose === 'walk') { frame = Math.floor(ph * 4); bob = frame % 2 ? 0 : -0; }
  if (pose === 'run') { frame = Math.floor(ph * 4); bob = frame === 1 || frame === 2 ? -1 : 0; }
  if (pose === 'jump') bob = -3;
  const sit = pose === 'sit', lie = pose === 'lie' || pose === 'sleep', beg = pose === 'beg';
  const bodyBot = (lie ? 0 : -legH) + bob, bodyTop = bodyBot - bodyH, bx0 = -Math.floor(bodyL / 2);
  // ---- tail (curled up over the back), wags left-right
  const wagN = o.wag ? Math.floor(T * 8 * o.wag) % 2 : 0, tx = bx0 - 1, ty = bodyTop + (sit ? 3 : 0);
  if (pose !== 'sleep') {
    if (pup) { P(tx - 1, ty - 2 + wagN, 1, 3, F.fur); P(tx - 2 + wagN, ty - 3, 1, 1, F.fur); }
    else {
      P(tx - 1, ty - 1, 2, 2, F.fur); P(tx - 2, ty - 3, 2, 2, F.fur); P(tx - 1 - wagN, ty - 5, 2, 2, F.fur); P(tx + (wagN ? -1 : 1), ty - 5, 1, 1, F.furL);
      P(tx - 1 - wagN, ty - 5, 1, 1, F.cream);
    }
  }
  // ---- legs: far pair first (darker), white paws at the bottom
  const legs = [];                                  // [x, isFront, isFar]
  const fl = bx0 + bodyL - (pup ? 3 : 4), bl_ = bx0 + 1;
  legs.push([bl_ + 2, false, true], [fl + 1, true, true], [bl_, false, false], [fl - 1, true, false]);
  const leg = (lx, front, far, i) => {
    const col = far ? F.furD : F.fur, pawC = far ? F.whiteD : F.white;
    let dx = 0, lift = 0, len = legH;
    if (pose === 'walk') { const k = (frame + (i % 2 ? 2 : 0) + (front ? 1 : 0)) % 4; dx = [0, 1, 0, -1][k]; lift = k === 1 ? 1 : 0; }
    if (pose === 'run') { const ext = frame === 1 || frame === 2; dx = front ? (ext ? 2 : -1) : (ext ? -2 : 1); lift = ext ? 0 : 1; }
    if (pose === 'jump') { dx = front ? 1 : -1; lift = 1; }
    if (lie) {                                            // legs stretched forward along the ground
      if (front) { P(lx + 1, -2, 4, 2, col); P(lx + 4, -2, 2, 2, pawC); }
      else { P(lx - 1, -2, 3, 2, col); P(lx - 2, -1, 2, 1, pawC); }
      return;
    }
    if (sit && !pup) {                                    // grown dog sitting: short straight front legs, hind paws forward
      if (front) { P(lx, -7, 2, 6, col); P(lx, -2, 3, 2, pawC); }
      else P(lx + 4, -2, 4, 2, pawC);
      return;
    }
    if (sit && !front) {                                  // haunch on the ground
      P(lx, -3, 4, 3, col); P(lx + 3, -1, 2, 1, pawC); return;
    }
    if (beg && !front) { P(lx + 3, -legH - 1, 2, legH + 1, col); P(lx + 3, -1, 3, 1, pawC); return; }
    if (beg && front) { P(lx + 3, bodyTop - 2, 3, 2, col); P(lx + 5, bodyTop - 3, 2, 2, pawC); return; }
    const top = bodyBot - 1, ly = top, h = (sit ? legH + (pup ? 2 : 3) : len) - lift;
    P(lx + dx, ly, 2, h - (pup ? 1 : 2) + 1, col);
    P(lx + dx, ly + h - (pup ? 1 : 2) + 1 - 0, pup ? 2 : 3, pup ? 1 : 2, pawC);   // the white "sneakers"
  };
  legs.forEach(([lx, front, far], i) => { if (far) leg(lx, front, far, i); });
  // ---- body
  let bTop = bodyTop, bBot = bodyBot;
  if (sit && !pup) {
    ellipse(cg, OX + bx0 + 4, OY - 4, 5, 4, F.fur);
    poly(cg, [[OX + bx0 + 1, OY - 2], [OX + bx0 + 3, OY - 9], [OX + bx0 + bodyL - 5, OY - 13], [OX + bx0 + bodyL - 1, OY - 11], [OX + bx0 + bodyL - 1, OY - 4], [OX + bx0 + bodyL - 3, OY - 2]], F.fur);
    P(bx0 + 3, -8, 4, 1, F.furL); P(bx0 + bodyL - 4, -11, 3, 7, F.cream);
  }
  else if (sit) { P(bx0 + 2, bTop - 2, bodyL - 4, bodyH + 1, F.fur); P(bx0, bTop + 1, bodyL - 3, bodyH, F.fur); P(bx0 + bodyL - 5, bTop - 2, 3, bodyH + 3, F.cream); }
  else if (beg) { P(bx0 + 3, bTop - 4, bodyL - 6, bodyH + 4, F.fur); P(bx0 + bodyL - 5, bTop - 3, 3, bodyH + 2, F.cream); }
  else if (pose === 'sleep') { ellipse(cg, OX - 1, OY - 3, bodyL / 2 + 1, 3, F.fur); }
  else {
    P(bx0 + 1, bTop, bodyL - 2, bodyH, F.fur); P(bx0, bTop + 1, bodyL, bodyH - 2, F.fur);
    P(bx0 + 1, bTop, bodyL - 3, 1, F.furL);                                    // sunlit back
    P(bx0 + 2, bBot - 1, bodyL - 5, 1, F.furD);                                 // belly shade
    P(bx0 + bodyL - (pup ? 3 : 4), bTop + 2, pup ? 2 : 3, bodyH - 2, F.cream);   // chest
  }
  legs.forEach(([lx, front, far], i) => { if (!far) leg(lx, front, far, i); });
  // ---- head
  let hx = bx0 + bodyL - (pup ? 4 : 3), hy = bTop - headH + (pup ? 3 : 2);
  if (sit && !pup) { hx = bx0 + bodyL - 5; hy = -13 - headH + 2; }
  else if (sit) { hx -= 1; hy -= 3; }
  if (beg) { hx -= 2; hy -= 5; }
  if (lie) { hy += 0; }
  if (pose === 'sleep') { hx = bx0 + bodyL - 4; hy = -headH + 1; }
  if (o.look === 'up') hy -= 1;
  const sn = pup ? 2 : 3;                                          // snout length
  // ears (pointy, slightly folded at the tip for the pup)
  if (pup) { P(hx + 1, hy - 1, 3, 1, F.fur); P(hx + 1, hy, 2, 3, F.furD); }
  else { P(hx + 1, hy - 3, 2, 3, F.fur); P(hx + 1, hy - 3, 1, 1, F.furD); P(hx + 2, hy - 2, 1, 2, '#E58C6E'); P(hx + 4, hy - 2, 2, 2, F.furD); }
  P(hx, hy + 1, headW, headH - 1, F.fur); P(hx + 1, hy, headW - 2, headH, F.fur);
  P(hx + 1, hy, headW - 3, 1, F.furL);
  if (pup) { P(hx + 1, hy, 2, 3, F.furD); P(hx + 2, hy + 3, 1, 1, F.furD); }
  // snout and nose
  const snY = hy + headH - (pup ? 3 : 3);
  P(hx + headW - 1, snY, sn, pup ? 2 : 3, F.cream); P(hx + headW - 2, snY + (pup ? 2 : 3), sn, 1, F.cream);
  P(hx + headW - 1 + sn - 1, snY, 1, 1, EYE);
  if (o.old) { P(hx + headW - 2, snY - 1, sn + 1, 1, F.grey); P(hx + 3, hy + 1, 2, 1, F.grey); }
  // eye
  const eyX = hx + headW - (pup ? 3 : 4), eyY = hy + (pup ? 2 : 2), eyes = o.eyes || 'open';
  const blink = eyes === 'open' && ((T * .7 + (o.seed || 1.3)) % 2.9) < .12;
  if (eyes === 'closed' || pose === 'sleep' || blink) P(eyX, eyY + 1, 2, 1, EYE);
  else if (eyes === 'happy') { P(eyX, eyY, 1, 1, EYE); P(eyX + 1, eyY - 1, 1, 1, EYE); }
  else { P(eyX, eyY, 1, 2, EYE); P(eyX + 1, eyY, 1, 1, EYE); }
  if (o.tongue) P(hx + headW, snY + (pup ? 2 : 3), 2, pup ? 1 : 2, '#F27D8E');
  if (o.blush) P(eyX - 1, eyY + 2, 1, 1, '#F2A28C');
  // collar
  if (o.collar) { P(hx - 1, hy + headH - 1, 2, pup ? 2 : 3, '#D8423A'); P(hx, hy + headH + (pup ? 1 : 2), 1, 1, '#FFD447'); }
  if (o.hat) { P(hx + 1, hy - 5, 3, 1, '#FF6F7F'); P(hx + 2, hy - 7, 2, 2, '#FFCB45'); P(hx + 2, hy - 8, 1, 1, '#FFFFFF'); P(hx + 1, hy - 6, 1, 1, '#5FB7E8'); P(hx, hy - 4, 5, 1, '#5FB7E8'); }
  if (o.carry) o.carry(cg, OX + hx + headW + sn - 1, OY + snY + 2);

  outlinePass(cg, SW, SHt);
  stamp(g, c, x, y, { flip: o.flip, alpha: o.alpha, silhouette: o.silhouette });
}

// paint something into a scratch canvas, outline it like the characters, stamp it at (x, y)
function outlined(g, x, y, w, h, paint, ink = INK, alpha = 1) {
  if (alpha <= 0) return;
  const c = scratch('ol' + w + 'x' + h, w, h), cg = c.getContext('2d'); cg.clearRect(0, 0, w, h);
  paint(cg); outlinePass(cg, w, h, ink);
  if (alpha < 1) {
    const img = cg.getImageData(0, 0, w, h), d = img.data, X = R(x), Y = R(y);
    for (let j = 0; j < h; j++) for (let i = 0; i < w; i++) if (bayer(X + i, Y + j) >= alpha) d[(j * w + i) * 4 + 3] = 0;
    cg.putImageData(img, 0, 0);
  }
  g.drawImage(c, R(x), R(y));
}
// a speech bubble whose tail points at (x, y); dots = how many of "..." are typed
function bubble(g, x, y, w, h, draw) {
  const bx = R(x - w / 2), by = R(y - h - 3);
  rect(g, bx - 1, by, w + 2, h, INK); rect(g, bx, by - 1, w, h + 2, INK); rect(g, bx, by, w, h, '#FFFFFF');
  rect(g, x - 1, by + h, 3, 1, '#FFFFFF'); px(g, x, by + h + 1, '#FFFFFF'); px(g, x - 2, by + h, INK); px(g, x + 2, by + h, INK); px(g, x - 1, by + h + 1, INK); px(g, x + 1, by + h + 1, INK); px(g, x, by + h + 2, INK);
  draw(bx, by);
}
// close everything outside a circle (the old cartoon iris)
function iris(g, cx, cy, r, col = '#0C0A10') {
  if (r <= 0) return rect(g, 0, 0, PW, PH, col);
  for (let y = 0; y < PH; y++) {
    const dy = y - cy, w = r * r - dy * dy;
    if (w <= 0) { rect(g, 0, y, PW, 1, col); continue; }
    const s = Math.sqrt(w); rect(g, 0, y, R(cx - s), 1, col); rect(g, R(cx + s), y, PW - R(cx + s), 1, col);
  }
}
