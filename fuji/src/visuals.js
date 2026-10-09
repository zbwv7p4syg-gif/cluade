// visuals.js — 富士山下 · Claude Code 版. One function per shot; shots dissolve into each other
// on the sung phrase starts from timeline.js.

const VW = 1280, VH = 720, TAU = Math.PI * 2;
const SERIF = 'NotoSerifSC, serif', F_EN = 'Fredoka, NotoSerifSC, sans-serif';
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eio = t => { t = clamp(t); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
const eout = t => 1 - Math.pow(1 - clamp(t), 3);
const H = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const layer = document.createElement('canvas');

function glow(c, x, y, r, color, a = 1) {
  if (r <= 0 || a <= .001) return;
  const g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, color); g.addColorStop(1, 'rgba(0,0,0,0)');
  c.save(); c.globalAlpha = clamp(a); c.fillStyle = g; c.fillRect(x - r, y - r, r * 2, r * 2); c.restore();
}
function vgrad(c, y0, y1, stops) { const g = c.createLinearGradient(0, y0, 0, y1); stops.forEach((s, i) => g.addColorStop(i / (stops.length - 1), s)); return g; }
function stars(c, t, n, x0, x1, y0, y1, a = 1) {
  for (let i = 0; i < n; i++) { c.globalAlpha = a * (.35 + .65 * (.5 + .5 * Math.sin(t * (.7 + H(i)) + i))); c.fillStyle = '#fff'; c.fillRect(lerp(x0, x1, H(i + 11)), lerp(y0, y1, H(i + 29)), 1.6, 1.6); }
  c.globalAlpha = 1;
}
// rain: slanted streaks falling through a region
function rain(c, t, o) {
  const { n = 200, x0 = 0, x1 = VW, y0 = -50, y1 = VH, sp = 900, len = 26, ang = .18, a = .35, seed = 1, w = 1.4, col = '200,215,240' } = o;
  c.save(); c.strokeStyle = `rgba(${col},${a})`; c.lineWidth = w; c.beginPath();
  const hgt = y1 - y0;
  for (let i = 0; i < n; i++) {
    const s = sp * (.75 + .5 * H(i + seed)), y = y0 + ((t * s + H(i + seed * 7) * hgt) % hgt), x = lerp(x0, x1, H(i * 3 + seed)) + (y - y0) * ang;
    c.moveTo(x, y); c.lineTo(x - len * ang, y - len);
  }
  c.stroke(); c.restore();
}
// soft flakes: rain that, in the lamplight, falls like snow
function flakes(c, t, o) {
  const { n = 90, x0 = 0, x1 = VW, y0 = -20, y1 = VH, sp = 60, r = 2.6, a = .9, seed = 3 } = o;
  const hgt = y1 - y0;
  for (let i = 0; i < n; i++) {
    const y = y0 + ((t * sp * (.6 + .8 * H(i + seed)) + H(i + seed * 5) * hgt) % hgt), x = lerp(x0, x1, H(i * 7 + seed)) + Math.sin(t * .8 + i) * 14;
    c.globalAlpha = a * (.5 + .5 * H(i + 2)); c.beginPath(); c.arc(x, y, r * (.6 + H(i + 9)), 0, TAU); c.fillStyle = '#F4F7FF'; c.fill();
  }
  c.globalAlpha = 1;
}
function fuji(c, cx, by, w, h, snowA = 1) {
  const top = by - h, tw = w * .085;
  const g = c.createLinearGradient(0, top, 0, by); g.addColorStop(0, '#3A4A72'); g.addColorStop(1, '#141B33');
  c.fillStyle = g; c.beginPath(); c.moveTo(cx - w / 2, by);
  c.quadraticCurveTo(cx - w * .2, by - h * .45, cx - tw, top); c.lineTo(cx + tw, top); c.quadraticCurveTo(cx + w * .2, by - h * .45, cx + w / 2, by); c.closePath(); c.fill();
  // snowcap with a ragged lower edge
  c.save(); c.clip(); c.globalAlpha = snowA;
  c.fillStyle = '#E9EFF9'; c.beginPath(); c.moveTo(cx - w * .5, top - 10);
  const sy = top + h * .34;
  for (let k = 0; k <= 16; k++) { const x = cx - w * .26 + k * w * .52 / 16, y = sy + (k % 2 ? -h * .07 : h * .02) + Math.sin(k * 1.7) * h * .03; c.lineTo(x, y); }
  c.lineTo(cx + w * .5, top - 10); c.closePath(); c.fill();
  c.fillStyle = 'rgba(160,180,220,.35)'; c.fillRect(cx, top, w, h);     // moon-shaded right flank
  c.restore();
}
function moon(c, x, y, r) { glow(c, x, y, r * 5, 'rgba(220,230,255,.35)'); c.beginPath(); c.arc(x, y, r, 0, TAU); c.fillStyle = '#F2F4FF'; c.fill(); }

// ---------------------------------------------------------------- the street (world coordinates)
function car(c, x, y, o = {}) {      // side view, facing left; (x, y) = road contact under the middle
  c.save(); c.translate(x, y);
  c.fillStyle = 'rgba(0,0,0,.35)'; c.beginPath(); c.ellipse(0, 4, 170, 12, 0, 0, TAU); c.fill();
  c.lineWidth = 3; c.strokeStyle = '#0d1220';
  c.beginPath(); c.roundRect(-160, -78, 320, 62, 22); c.fillStyle = '#2F5D6E'; c.fill(); c.stroke();
  c.beginPath(); c.moveTo(-95, -78); c.quadraticCurveTo(-70, -130, -10, -132); c.lineTo(70, -132); c.quadraticCurveTo(110, -128, 125, -78); c.closePath(); c.fillStyle = '#2F5D6E'; c.fill(); c.stroke();
  c.fillStyle = '#9CC3D6'; c.globalAlpha = .55;
  c.beginPath(); c.moveTo(-80, -82); c.quadraticCurveTo(-62, -122, -12, -124); c.lineTo(20, -124); c.lineTo(20, -82); c.closePath(); c.fill();
  c.beginPath(); c.moveTo(30, -82); c.lineTo(30, -124); c.lineTo(68, -124); c.quadraticCurveTo(102, -120, 112, -82); c.closePath(); c.fill();
  c.globalAlpha = 1;
  if (o.door) { c.save(); c.translate(-20, -80); c.rotate(-.55 * o.door); c.fillStyle = '#2A5262'; c.fillRect(0, 0, 60, 62); c.restore(); }
  for (const wx of [-100, 100]) { c.beginPath(); c.arc(wx, -14, 26, 0, TAU); c.fillStyle = '#10141f'; c.fill(); c.beginPath(); c.arc(wx, -14, 11, 0, TAU); c.fillStyle = '#6A7A90'; c.fill(); }
  if (o.lights) { glow(c, -168, -50, 60, 'rgba(255,240,200,.9)', o.lights); c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createLinearGradient(-170, 0, -760, 0); g.addColorStop(0, `rgba(255,240,200,${.35 * o.lights})`); g.addColorStop(1, 'rgba(255,240,200,0)'); c.fillStyle = g; c.beginPath(); c.moveTo(-165, -58); c.lineTo(-760, -110); c.lineTo(-760, 30); c.lineTo(-165, -38); c.fill(); c.restore(); }
  if (o.brake) glow(c, 160, -50, 50, 'rgba(255,60,60,.9)', o.brake);
  c.restore();
}
function street(c, t, o = {}) {
  // sky + Fuji + moon (Fuji sits far above the street so the camera can tilt down from it)
  c.fillStyle = vgrad(c, -900, 560, ['#060A16', '#101A33', '#273454']); c.fillRect(-600, -1000, 3000, 1800);
  stars(c, t, 120, -400, 2200, -900, -100, .8);
  moon(c, 1380, -640, 46);
  fuji(c, 900, 420, 1700, 620, 1);
  // low cloud bands
  c.fillStyle = 'rgba(40,52,84,.6)'; for (let k = 0; k < 4; k++) { c.beginPath(); c.ellipse(((k * 600 + t * 12) % 2600) - 400, 120 + k * 40, 380, 40, 0, 0, TAU); c.fill(); }
  // city skyline with lit windows
  for (let i = 0; i < 26; i++) {
    const w = 60 + H(i) * 70, x = -200 + i * 90, h = 120 + H(i + 5) * 170;
    c.fillStyle = '#121828'; c.fillRect(x, 520 - h, w, h);
    for (let r = 0; r < h / 22 - 1; r++) for (let k = 0; k < w / 18 - 1; k++) if (H(i * 31 + r * 7 + k) < .28) { c.fillStyle = H(i + r + k) < .7 ? 'rgba(255,200,120,.65)' : 'rgba(160,200,255,.55)'; c.fillRect(x + 6 + k * 18, 520 - h + 8 + r * 22, 8, 11); }
  }
  // sidewalk, road, wet reflections
  c.fillStyle = '#273047'; c.fillRect(-600, 520, 3000, 42);
  c.fillStyle = vgrad(c, 562, 760, ['#161C2C', '#0E1220']); c.fillRect(-600, 562, 3000, 300);
  c.save(); c.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 26; i++) { if (H(i * 13) < .5) continue; const x = -160 + i * 90 + 20; c.fillStyle = 'rgba(255,190,110,.06)'; c.fillRect(x, 566, 14 + H(i) * 10, 150); }
  c.fillStyle = 'rgba(255,220,150,.10)'; c.fillRect(740, 566, 50, 170);                 // the lamp's reflection
  c.restore();
  // bus stop shelter
  c.fillStyle = 'rgba(150,180,210,.18)'; c.fillRect(520, 380, 160, 140); c.strokeStyle = '#3B4660'; c.lineWidth = 6; c.strokeRect(520, 380, 160, 140);
  c.fillStyle = '#3B4660'; c.fillRect(510, 370, 180, 14);
  // the street lamp and its cone of light
  c.fillStyle = '#2E3650'; c.fillRect(806, 200, 9, 322); c.fillRect(760, 196, 56, 9);
  glow(c, 768, 214, 120, 'rgba(255,224,160,.85)', .9);
  c.save(); c.globalCompositeOperation = 'lighter';
  const cone = c.createLinearGradient(0, 214, 0, 540); cone.addColorStop(0, 'rgba(255,224,160,.28)'); cone.addColorStop(1, 'rgba(255,224,160,.05)');
  c.fillStyle = cone; c.beginPath(); c.moveTo(752, 214); c.lineTo(784, 214); c.lineTo(900, 540); c.lineTo(630, 540); c.closePath(); c.fill();
  c.restore();
  // puddle ripples
  c.strokeStyle = 'rgba(200,215,240,.25)'; c.lineWidth = 1.5;
  for (let i = 0; i < 10; i++) { const p = (t * .9 + H(i)) % 1, x = 300 + H(i + 4) * 1100, y = 600 + H(i + 8) * 100; c.globalAlpha = 1 - p; c.beginPath(); c.ellipse(x, y, p * 40, p * 8, 0, 0, TAU); c.stroke(); }
  c.globalAlpha = 1;
}
const SHE = { x: 695, y: 542 }, U = 14;
function she(t, extra = {}) { return { look: LOOK_SIS, bow: true, seed: 4, eyes: 'normal', aL: .25, aR: .25, ...extra }; }
function he(t, extra = {}) { return { look: LOOK_BRO, seed: 7, eyes: 'normal', aL: .25, aR: .25, ...extra }; }
function breath(c, x, y, t, every = 1.7) { const p = (t % every) / every; if (p > .5) return; c.save(); c.globalAlpha = .45 * (1 - p * 2); c.fillStyle = '#EEF3FF'; c.beginPath(); c.ellipse(x - p * 40, y - p * 30, 6 + p * 30, 4 + p * 16, 0, 0, TAU); c.fill(); c.restore(); }

function withCam(c, cx, cy, z, fn) { c.save(); c.translate(VW / 2, VH / 2); c.scale(z, z); c.translate(-cx, -cy); fn(); c.restore(); }

// ---------------------------------------------------------------- shots
const SHOT_FN = {
  fuji(c, t) {
    c.fillStyle = vgrad(c, 0, VH, ['#05070F', '#0E1630', '#233157']); c.fillRect(0, 0, VW, VH);
    stars(c, t, 220, 0, VW, 0, 420);
    moon(c, 1010, 150, 38);
    const s = 1 + .03 * seg(t, 0, 5.13);
    c.save(); c.translate(640, 640); c.scale(s, s); c.translate(-640, -640);
    fuji(c, 640, 770, 1500, 420);
    c.fillStyle = 'rgba(40,52,84,.55)'; for (let k = 0; k < 3; k++) { c.beginPath(); c.ellipse(((k * 520 + t * 18) % 1900) - 300, 560 + k * 30, 420, 34, 0, 0, TAU); c.fill(); }
    c.restore();
  },
  tilt(c, t) {
    const p = eio(seg(t, 5.13, 9.2));
    withCam(c, lerp(900, 800, p), lerp(-230, 400, p), lerp(.62, .92, p), () => street(c, t));
    rain(c, t, { n: 180, a: .3 * seg(t, 6, 8) });
  },
  alone(c, t) {
    const p = seg(t, 9.41, 13.69);
    withCam(c, 760, lerp(420, 430, p), lerp(1.45, 1.6, p), () => {
      street(c, t);
      critter(c, SHE.x, SHE.y, U, she(t, { eyes: t > 11.5 ? 'sad' : 'normal', lookX: -.3, brows: 'sad' }), t);
      breath(c, SHE.x - 10, SHE.y - 60, t);
    });
    rain(c, t, { n: 260, a: .35 });
  },
  car(c, t) {
    const p = eout(seg(t, 13.69, 17.3)), cx = lerp(1900, 1000, p);
    withCam(c, 900, 470, 1.0, () => {
      street(c, t);
      critter(c, SHE.x, SHE.y, U, she(t, { eyes: 'sad', lookX: t > 15.5 ? 1 : 0, brows: 'sad' }), t);
      car(c, cx, 660, { lights: 1, brake: t > 16.8 ? 1 : 0 });
    });
    rain(c, t, { n: 260, a: .35 });
  },
  walk(c, t) {
    const p = seg(t, 18.6, 21.6), x = lerp(980, 860, eio(p)), walking = p > 0 && p < 1;
    withCam(c, lerp(880, 800, eio(seg(t, 17.97, 22.25))), 455, lerp(1.2, 1.5, eio(seg(t, 17.97, 22.25))), () => {
      street(c, t);
      car(c, 1000, 660, { lights: .7, door: seg(t, 18.0, 18.5) * (1 - seg(t, 19.4, 19.8)) });
      critter(c, SHE.x, SHE.y, U, she(t, { eyes: 'sad', lookX: t > 20.6 ? .9 : -.2, brows: 'sad' }), t);
      critter(c, x, 542 + (walking ? 0 : 0), U, he(t, { coatOn: 1, walk: walking ? (t - 18.6) / .5 : null, flip: true, dy: walking ? -.25 * Math.abs(Math.sin((t - 18.6) * 2 * Math.PI)) : 0, lookX: -.9 }), t);
    });
    rain(c, t, { n: 260, a: .35 });
  },
  snowrain(c, t) {
    const p = seg(t, 22.25, 26.53);
    withCam(c, 778, 452, lerp(2.05, 2.25, eio(p)), () => {
      street(c, t);
      critter(c, SHE.x, SHE.y, U, she(t, { eyes: 'teary', brows: 'sad', tears: lerp(.4, 1, p), frown: 1, sq: .02 * Math.sin(t * 24), lookX: .2 }), t);
      critter(c, 860, 542, U, he(t, { coatOn: 1, brows: 'up', lookX: -.9, frown: .5 }), t);
      breath(c, SHE.x - 8, SHE.y - 64, t, 1.4);
    });
    // in the lamplight the rain falls slowly, like snow
    flakes(c, t, { n: 120, x0: 300, x1: 1000, sp: 55, r: 3.2 });
    rain(c, t, { n: 120, a: .18 });
  },
  coat(c, t) {
    const p = seg(t, 26.53, 30.75), off = seg(t, 26.9, 27.7), on = eout(seg(t, 27.5, 28.5));
    withCam(c, 778, 452, lerp(2.25, 2.4, eio(p)), () => {
      street(c, t);
      const lift = Math.sin(seg(t, 27.4, 28.4) * Math.PI);
      critter(c, SHE.x, SHE.y, U, she(t, { eyes: t > 28.4 ? 'teary' : 'teary', brows: t > 28.6 ? null : 'sad', tears: lerp(1, .3, seg(t, 28, 30)), coatDrape: on, lookX: t > 28.2 ? .8 : .1, blush: seg(t, 28.6, 29.4) * .6, smile: t > 29 ? .25 : 0 }), t);
      critter(c, 860, 542, U, he(t, { coatOn: 1 - off, aL: .3 + 2.2 * lift, aR: .3 + 2.2 * lift, lookX: -.9, smile: t > 28.6 ? .5 : 0 }), t);
      breath(c, SHE.x - 8, SHE.y - 64, t, 1.6);
    });
    flakes(c, t, { n: 110, x0: 300, x1: 1000, sp: 55, r: 3.2 });
  },
  memory(c, t) {
    // a small, faraway rented room: moving boxes, a train passing outside
    c.fillStyle = vgrad(c, 0, VH, ['#2B2420', '#3A2F28']); c.fillRect(0, 0, VW, VH);
    c.fillStyle = '#1B2236'; c.fillRect(760, 110, 360, 260); c.strokeStyle = '#6D5A48'; c.lineWidth = 10; c.strokeRect(760, 110, 360, 260);
    for (const tt of [31.6, 33.8]) { const d = t - tt; if (d < 0 || d > 1.4) continue; for (let k = 0; k < 7; k++) { const x = 1140 - d * 900 + k * 110; c.fillStyle = 'rgba(255,220,150,.75)'; c.fillRect(Math.max(760, Math.min(1110, x)), 250, Math.max(0, Math.min(60, 1120 - x)), 26); } }
    c.fillStyle = '#4E4038'; c.fillRect(0, 560, VW, 160);
    for (const [x, y, w, h] of [[150, 420, 190, 140], [330, 470, 150, 90], [180, 330, 140, 90]]) { c.fillStyle = '#B98B5A'; c.fillRect(x, y, w, h); c.fillStyle = 'rgba(0,0,0,.18)'; c.fillRect(x, y + h * .45, w, h * .1); }
    c.font = `700 22px ${SERIF}`; c.fillStyle = '#5A3E22'; c.textAlign = 'center'; c.fillText('搬家', 245, 500);
    // he sits on a box, looking at her photo on his phone
    c.fillStyle = '#B98B5A'; c.fillRect(560, 470, 170, 90);
    const sigh = Math.sin(seg(t, 33, 34.4) * Math.PI) * .06;
    critter(c, 645, 478, 15, he(t, { eyes: 'sad', aR: 1.05, aL: .9, lookX: .5, sq: sigh }), t);
    const px = 700, py = 360;
    c.fillStyle = '#16161C'; c.beginPath(); c.roundRect(px, py, 46, 78, 8); c.fill();
    c.fillStyle = '#FFE3EC'; c.fillRect(px + 4, py + 6, 38, 64);
    critter(c, px + 23, py + 58, 3.2, she(t, { eyes: 'happy', shadowless: true }), t);
    glow(c, px + 23, py + 40, 90, 'rgba(255,220,235,.6)', .7);
    // old-film treatment: warm wash, grain, soft rounded frame
    c.fillStyle = 'rgba(160,110,60,.18)'; c.fillRect(0, 0, VW, VH);
    for (let i = 0; i < 260; i++) { c.fillStyle = `rgba(255,240,220,${.05 + .08 * H(i + Math.floor(t * 24) * 7)})`; c.fillRect(H(i + Math.floor(t * 24)) * VW, H(i * 3 + Math.floor(t * 24)) * VH, 2, 2); }
    const v = c.createRadialGradient(640, 360, 220, 640, 360, 760); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(20,10,0,.75)'); c.fillStyle = v; c.fillRect(0, 0, VW, VH);
  },
  drive(c, t) {
    // through the windshield, at night, in the rain
    c.fillStyle = '#05070C'; c.fillRect(0, 0, VW, VH);
    c.save(); c.beginPath(); c.moveTo(150, 90); c.lineTo(1130, 90); c.quadraticCurveTo(1200, 300, 1230, 560); c.lineTo(50, 560); c.quadraticCurveTo(80, 300, 150, 90); c.closePath(); c.clip();
    c.fillStyle = vgrad(c, 90, 560, ['#0C1224', '#1A2238']); c.fillRect(0, 0, VW, VH);
    for (let i = 0; i < 26; i++) { const x = ((H(i) * 1500 - (t - 35.9) * (90 + H(i + 3) * 160)) % 1500 + 1500) % 1500 - 100, y = 140 + H(i + 6) * 200; glow(c, x, y, 26 + H(i + 9) * 30, H(i + 2) < .6 ? 'rgba(255,190,110,.8)' : 'rgba(150,200,255,.7)', .7); }
    // passing street lights sweep across the cabin once per quiet beat
    const sweep = pulseBeat(t);
    c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = 'rgba(255,200,130,.12)'; c.fillRect(lerp(1300, -300, sweep), 90, 220, 480); c.restore();
    critter(c, 430, 660, 26, he(t, { lookX: .1, eyes: 'normal' }), t);
    critter(c, 860, 660, 26, she(t, { coatDrape: 1, lookX: .9, eyes: t > 38 ? 'sad' : 'normal' }), t);
    // raindrops on the glass
    for (let i = 0; i < 90; i++) { const x = 60 + H(i) * 1160, y = 100 + ((H(i + 4) * 460 + (t - 35.9) * 18 * H(i + 7)) % 460); c.beginPath(); c.arc(x, y, 1.5 + H(i + 2) * 3, 0, TAU); c.fillStyle = 'rgba(210,225,255,.35)'; c.fill(); }
    // wipers, one sweep per quiet beat
    const a = .08 + 1.35 * Math.sin(sweep * Math.PI);
    for (const [px, len] of [[560, 440], [1060, 440]]) { c.save(); c.translate(px, 556); c.rotate(Math.PI + a); c.strokeStyle = '#05070C'; c.lineWidth = 9; c.lineCap = 'round'; c.beginPath(); c.moveTo(0, 0); c.lineTo(len, 0); c.stroke(); c.restore(); }
    c.restore();
    c.fillStyle = '#0B0E16'; c.fillRect(0, 560, VW, 160);
    glow(c, 640, 600, 180, 'rgba(90,150,255,.35)'); c.fillStyle = 'rgba(120,180,255,.6)'; c.fillRect(600, 590, 80, 6);
  },
  flowers(c, t) {
    if (t < 42.6) {   // the back seat: a bouquet that won't be given
      c.fillStyle = vgrad(c, 0, VH, ['#141826', '#0B0E18']); c.fillRect(0, 0, VW, VH);
      c.fillStyle = '#232A3E'; c.beginPath(); c.roundRect(120, 330, 1040, 330, 60); c.fill();
      c.fillStyle = '#1C2234'; c.beginPath(); c.roundRect(150, 140, 980, 220, 50); c.fill();
      const cx = 640, cy = 470, s = 1 + .03 * seg(t, 40.48, 42.6);
      c.save(); c.translate(cx, cy); c.scale(s, s); c.rotate(-.25);
      c.fillStyle = '#F6D7E0'; c.beginPath(); c.moveTo(-60, 40); c.lineTo(220, -10); c.lineTo(220, 90); c.closePath(); c.fill();
      c.strokeStyle = '#4C8A50'; c.lineWidth = 6; for (let k = 0; k < 6; k++) { c.beginPath(); c.moveTo(150, 40); c.lineTo(-40 + k * 8, -60 + k * 24); c.stroke(); }
      for (let k = 0; k < 9; k++) { const fx = -70 + (k % 3) * 34, fy = -70 + Math.floor(k / 3) * 40; for (let pe = 0; pe < 6; pe++) { c.beginPath(); c.ellipse(fx + Math.cos(pe) * 12, fy + Math.sin(pe) * 12, 11, 7, pe, 0, TAU); c.fillStyle = k % 2 ? '#F5A3BC' : '#FFF2F6'; c.fill(); } c.beginPath(); c.arc(fx, fy, 6, 0, TAU); c.fillStyle = '#F2C35C'; c.fill(); }
      c.fillStyle = '#E8436E'; c.fillRect(100, 10, 30, 50);
      c.restore();
      const sweep = pulseBeat(t); c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = 'rgba(255,200,130,.10)'; c.fillRect(lerp(1300, -300, sweep), 0, 240, VH); c.restore();
    } else {          // the misted side window: a heart drawn with a finger, then a plaster over it
      const lights = cc => { cc.fillStyle = '#0A0E18'; cc.fillRect(0, 0, VW, VH); for (let i = 0; i < 30; i++) { const x = ((H(i) * 1500 - (t - 42.6) * 120) % 1500 + 1500) % 1500 - 100; glow(cc, x, 200 + H(i + 6) * 320, 40 + H(i) * 50, H(i + 2) < .6 ? 'rgba(255,190,110,.7)' : 'rgba(150,200,255,.6)', .6); } };
      lights(c);
      c.fillStyle = 'rgba(190,200,220,.42)'; c.fillRect(0, 0, VW, VH);       // mist on the glass
      const p = seg(t, 42.8, 43.9), pts = [];
      for (let k = 0; k <= 120; k++) { const a = k / 120 * TAU; pts.push([640 + 16 * Math.pow(Math.sin(a), 3) * 9, 330 - (13 * Math.cos(a) - 5 * Math.cos(2 * a) - 2 * Math.cos(3 * a) - Math.cos(4 * a)) * 9]); }
      const drawn = pts.slice(0, Math.max(1, Math.floor(p * 121)));
      c.save(); c.beginPath(); for (const [x, y] of drawn) { c.moveTo(x + 10, y); c.arc(x, y, 10, 0, TAU); } c.clip(); lights(c); c.restore();   // the finger wipes the mist away
      const b = eout(seg(t, 44.0, 44.4));
      if (b > 0) { c.save(); c.translate(640, 300); c.rotate(-.5); c.scale(b, b); c.fillStyle = '#F2D2B0'; c.beginPath(); c.roundRect(-90, -24, 180, 48, 22); c.fill(); c.fillStyle = '#E5BE96'; c.fillRect(-30, -20, 60, 40); c.fillStyle = 'rgba(150,110,80,.5)'; for (let k = 0; k < 6; k++) c.fillRect(-22 + (k % 3) * 18, -12 + Math.floor(k / 3) * 16, 4, 4); c.restore(); }
      for (let i = 0; i < 26; i++) { const y = ((H(i + 3) * 720 + (t - 42.6) * 60 * H(i)) % 720); c.fillStyle = 'rgba(220,230,250,.45)'; c.fillRect(H(i) * VW, y, 2, 20); }
    }
  },
  petals(c, t) {
    const p = seg(t, 44.76, 49.6), z = lerp(1, 1.14, eio(p));
    c.fillStyle = vgrad(c, 0, VH, ['#060A16', '#121C38', '#2A3658']); c.fillRect(0, 0, VW, VH);
    c.save(); c.translate(640, 380); c.scale(z, z); c.translate(-640, -380);
    stars(c, t, 120, 0, VW, 0, 300); moon(c, 930, 130, 30);
    fuji(c, 640, 470, 980, 300);
    c.fillStyle = '#0D111C'; c.beginPath(); c.moveTo(0, 720); c.lineTo(600, 470); c.lineTo(680, 470); c.lineTo(1280, 720); c.fill();
    c.strokeStyle = 'rgba(255,230,160,.5)'; c.lineWidth = 4; c.setLineDash([30, 30]); c.lineDashOffset = -t * 200; c.beginPath(); c.moveTo(640, 720); c.lineTo(640, 470); c.stroke(); c.setLineDash([]);
    c.restore();
    // petals rise and swirl, then settle and turn into snow
    for (let i = 0; i < 70; i++) {
      const d = t - 44.76 - H(i) * 1.2; if (d < 0) continue;
      const k = seg(d, 1.2, 3.2), ang = d * (1 + H(i + 2)) + i, x = 640 + Math.cos(ang) * (80 + d * 120) * (1 - k * .3) + (H(i + 5) - .5) * 600 * k, y = 660 - d * 160 + k * (d * 160 - 80 + H(i + 8) * 500);
      c.save(); c.translate(x, y); c.rotate(ang); c.globalAlpha = .9 * (1 - seg(d, 3.6, 4.6));
      c.fillStyle = k < .5 ? '#F7A8C2' : '#F4F7FF'; c.beginPath(); c.ellipse(0, 0, lerp(8, 3, k), lerp(5, 3, k), 0, 0, TAU); c.fill(); c.restore();
    }
    flakes(c, t, { n: 60, sp: 40, r: 2.2, a: seg(t, 46.5, 48.5) });
    c.fillStyle = '#05070C'; c.beginPath(); c.moveTo(0, 0); c.lineTo(VW, 0); c.lineTo(VW, 60); c.quadraticCurveTo(640, 20, 0, 60); c.fill(); c.fillRect(0, 640, VW, 80);
  },
  home(c, t) {
    const up = eio(seg(t, 52.2, 54.1));
    c.fillStyle = vgrad(c, 0, VH, ['#070B18', '#16203C', '#2A3658']); c.fillRect(0, 0, VW, VH);
    c.save(); c.translate(0, up * 420);
    stars(c, t, 140, 0, VW, -400, 200); moon(c, 1000, -260, 34); fuji(c, 640, 330, 1000, 330);
    // her small house, the window lights up when she is inside
    c.fillStyle = '#20283F'; c.fillRect(300, 320, 360, 230); c.fillStyle = '#18203A'; c.beginPath(); c.moveTo(270, 330); c.lineTo(480, 210); c.lineTo(690, 330); c.fill();
    const inside = seg(t, 52.4, 52.9);
    c.fillStyle = `rgba(255,${lerp(150, 205, inside)},${lerp(80, 130, inside)},${.35 + .55 * inside})`; c.fillRect(540, 380, 80, 70); glow(c, 580, 415, 140, 'rgba(255,200,120,.6)', .3 + .5 * inside);
    const door = seg(t, 51.9, 52.2) * (1 - seg(t, 52.35, 52.6));
    c.fillStyle = '#3A2A24'; c.fillRect(380, 420, 80, 130); c.fillStyle = 'rgba(255,200,120,.8)'; c.fillRect(380, 420, 80 * door, 130);
    c.fillStyle = '#2A3248'; c.fillRect(-50, 550, 1400, 40); c.fillStyle = '#121726'; c.fillRect(-50, 590, 1400, 200);
    critter(c, 1012, 583, 5.5, he(t, { lookX: -.8, aL: t > 51.6 && t < 52.4 ? 2.1 + .3 * Math.sin(t * 14) : .25, eyes: t > 52.6 ? 'happy' : 'normal' }), t);
    car(c, 980, 660, { lights: .5 });
    // she walks from the car to her door in his coat, turns, waves, goes in
    const w = seg(t, 49.9, 51.4), x = lerp(860, 440, eio(w));
    if (t < 52.4) critter(c, x, 548, 13, she(t, { coatDrape: 1, walk: w > 0 && w < 1 ? (t - 49.9) / .5 : null, flip: w < 1, eyes: t > 51.5 ? 'normal' : 'sad', lookX: t > 51.5 ? .9 : -.6, aR: t > 51.5 && t < 52.2 ? 2.2 + .3 * Math.sin(t * 14) : .25 }), t);
    c.restore();
    flakes(c, t, { n: 90, sp: 45, r: 2.6, a: .9 });
  },
};

function caption(c, t) {
  const cap = CAPTIONS.find(([a, b]) => t >= a && t < b); if (!cap) return;
  const [a, b, s] = cap, k = seg(t, a, a + .5) * (1 - seg(t, b - .5, b));
  c.save(); c.globalAlpha = k; c.font = `500 30px ${SERIF}`; c.textAlign = 'center'; c.textBaseline = 'middle';
  c.shadowColor = 'rgba(0,0,0,.8)'; c.shadowBlur = 12; c.fillStyle = '#F4F1EA'; c.fillText(s, 640, 655); c.restore();
}
function titles(c, t) {
  if (t > 1.4 && t < 5.4) {
    const k = seg(t, 1.6, 2.8) * (1 - seg(t, 4.6, 5.3));
    c.save(); c.globalAlpha = k; c.textAlign = 'center'; c.textBaseline = 'middle'; c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 20;
    c.font = `700 92px ${SERIF}`; c.fillStyle = '#F6F3EC'; c.fillText('富 士 山 下', 640, 190);
    c.font = `500 26px ${F_EN}`; c.fillStyle = '#C9D3EA'; c.fillText('Claude Code 版', 640, 262); c.restore();
  }
  if (t > 5.6 && t < 9.4) { const k = seg(t, 5.8, 6.6) * (1 - seg(t, 8.6, 9.3)); c.save(); c.globalAlpha = k; c.font = `500 24px ${SERIF}`; c.textAlign = 'center'; c.shadowColor = 'rgba(0,0,0,.8)'; c.shadowBlur = 10; c.fillStyle = '#E9ECF5'; c.fillText('背景音乐 · 陈奕迅《富士山下》', 640, 660); c.restore(); }
  if (t > 52.8) { const k = seg(t, 52.9, 53.5); c.save(); c.globalAlpha = k; c.font = `700 54px ${SERIF}`; c.textAlign = 'center'; c.shadowColor = 'rgba(0,0,0,.8)'; c.shadowBlur = 16; c.fillStyle = '#F6F3EC'; c.fillText('富 士 山 下', 640, 330); c.restore(); }
}

const XFADE = .45;
function drawFrame(main, t, scale) {
  t = clamp(t, 0, DUR - 1e-4);
  if (layer.width !== main.canvas.width) { layer.width = main.canvas.width; layer.height = main.canvas.height; }
  const i = shotIndex(t), s = SHOTS[i];
  main.setTransform(scale, 0, 0, scale, 0, 0); main.globalAlpha = 1;
  // dissolve from the previous shot across the first XFADE seconds of this one
  if (i > 0 && t - s.t0 < XFADE) {
    SHOT_FN[SHOTS[i - 1].name](main, t);
    const lc = layer.getContext('2d'); lc.setTransform(scale, 0, 0, scale, 0, 0); lc.clearRect(0, 0, VW, VH);
    SHOT_FN[s.name](lc, t);
    main.setTransform(1, 0, 0, 1, 0, 0); main.globalAlpha = eio((t - s.t0) / XFADE); main.drawImage(layer, 0, 0); main.globalAlpha = 1;
    main.setTransform(scale, 0, 0, scale, 0, 0);
  } else SHOT_FN[s.name](main, t);
  const v = main.createRadialGradient(640, 360, 300, 640, 360, 820); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,.35)'); main.fillStyle = v; main.fillRect(0, 0, VW, VH);
  caption(main, t); titles(main, t);
  if (t < 1.5) { main.fillStyle = `rgba(0,0,0,${1 - seg(t, .2, 1.5)})`; main.fillRect(0, 0, VW, VH); }
  if (t > DUR - .9) { main.fillStyle = `rgba(0,0,0,${seg(t, DUR - .9, DUR - .05)})`; main.fillRect(0, 0, VW, VH); }
}
