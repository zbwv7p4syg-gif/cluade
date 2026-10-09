// render.js — a small software raycaster for Level 0 (yellow wallpaper, damp carpet, fluorescent panels),
// drawn at 480×270 and then dressed up as camcorder footage: tape colour bleed, scanlines, grain,
// tracking glitches, bloom, and the on-screen display.

const RW = 480, RH = 270, TS = 64, FOV = 78 * Math.PI / 180, WH = 1.35, EYE = .8, FOGK = .06;
const VW = 1920, VH = 1080;
const lowCv = document.createElement('canvas'); lowCv.width = RW; lowCv.height = RH;
const lg = lowCv.getContext('2d'), lowImg = lg.createImageData(RW, RH);
const outPx = new Uint32Array(lowImg.data.buffer), px = new Uint32Array(RW * RH), zbuf = new Float32Array(RW);
const emit = new Float32Array(MAPW * MAPH);
const F_MONO = '"DejaVu Sans Mono", "Liberation Mono", monospace', F_CN = 'KuaiLe, sans-serif';

// ---------------------------------------------------------------- procedural textures
const T = { wall: new Uint8Array(TS * TS * 3), floor: new Uint8Array(TS * TS * 3), ceil: new Uint8Array(TS * TS * 3) };
const vnoise = (x, y, s) => { const xi = Math.floor(x), yi = Math.floor(y), u = smooth(x - xi), v = smooth(y - yi), h = (a, b) => H(((a % 16) + 16) % 16 * 31.7 + ((b % 16) + 16) % 16 * 57.3 + s * 13.1);
  return lerp(lerp(h(xi, yi), h(xi + 1, yi), u), lerp(h(xi, yi + 1), h(xi + 1, yi + 1), u), v); };
function makeTextures() {
  for (let v = 0; v < TS; v++) for (let u = 0; u < TS; u++) {
    const i = (v * TS + u) * 3, n = (H(u * 3.1 + v * 91.7) - .5);
    // wallpaper: pale yellow with a darker stripe, a dashed band beside it, water stains and a baseboard
    let r = 204, g = 184, b = 98;
    const m = u % 16;
    if (m < 2) { r = 176; g = 156; b = 78; }
    else if (m >= 6 && m < 10 && (v % 8) < 5) { r = 212; g = 193; b = 108; }
    const stain = clamp(vnoise(u / 9, v / 9, 1) * 1.3 - .45) * .28 + clamp(vnoise(u / 5 + 8, v / 14, 2) - .55) * .35 * (v / TS);
    r -= stain * 90; g -= stain * 96; b -= stain * 70;
    if (v < 3) { r *= .72; g *= .72; b *= .7; }
    if (v >= 57) { r = 104; g = 86; b = 54; if (v === 57) { r = 70; g = 58; b = 36; } }
    T.wall.set([r + n * 14, g + n * 14, b + n * 12], i);
    // carpet: dense dark fibres, damp patches
    const damp = clamp(vnoise(u / 12, v / 12, 3) * 1.4 - .4) * .35, f = (H(u * 7.7 + v * 13.3 + 5) - .5) * 34;
    T.floor.set([142 - damp * 90 + f, 120 - damp * 80 + f, 64 - damp * 40 + f * .6], i);
    // ceiling tile with a grid seam
    const seam = u < 2 || v < 2 ? 1 : 0;
    T.ceil.set([seam ? 128 : 198 + n * 10, seam ? 124 : 192 + n * 10, seam ? 96 : 152 + n * 8], i);
  }
}

// ---------------------------------------------------------------- sprites: the tall dark thing and (later) a small orange one
function sprite(w, h, draw) { const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d')); return c; }
let SPR = null;
function makeSprites() {
  const thing = (body, edge, eyes) => g => {
    g.fillStyle = body; g.fillRect(14, 4, 36, 52);                 // a long, blocky body
    g.fillRect(6, 20, 6, 74); g.fillRect(52, 20, 6, 74);           // arms that reach nearly to the floor
    for (const x of [18, 26, 36, 44]) g.fillRect(x, 56, 5, 70);   // four thin legs
    g.fillStyle = edge; g.fillRect(14, 4, 36, 2); g.fillRect(14, 4, 2, 52);
    if (eyes) { g.fillStyle = '#F4FFE8'; g.fillRect(23, 22, 5, 10); g.fillRect(37, 22, 5, 10); }
  };
  SPR = {
    dark: sprite(64, 128, thing('#0c0b08', '#26231a', false)),
    night: sprite(64, 128, thing('#0a1a0a', '#1d3a1d', true)),
    clawd: sprite(80, 64, g => {
      g.fillStyle = '#D97757'; g.fillRect(8, 2, 64, 44); g.fillRect(0, 14, 8, 12); g.fillRect(72, 14, 8, 12);
      for (const x of [14, 28, 44, 58]) g.fillRect(x, 46, 8, 14);
      g.fillStyle = '#3A2A24'; g.fillRect(24, 12, 7, 11); g.fillRect(49, 12, 7, 11);
      g.fillStyle = 'rgba(255,255,255,.14)'; g.fillRect(8, 2, 64, 3);
    }),
  };
}

// ---------------------------------------------------------------- the raycaster
function renderWorld(cam, t) {
  const dirX = Math.cos(cam.yaw), dirY = Math.sin(cam.yaw), L = Math.tan(FOV / 2), planeX = -dirY * L, planeY = dirX * L, focal = RW / 2 / L;
  const hz = RH / 2 + cam.horizonOff, lvl = cam.night ? .34 : cam.lvl;
  const fogR = 126, fogG = 112, fogB = 52;
  for (let cy = 0; cy < MAPH; cy++) for (let cx = 0; cx < MAPW; cx++) emit[cy * MAPW + cx] = (cx % 3 === 0 && (cy & 1) === 0) ? panelOn(cy * 64 + cx, t) * (cam.lvl > .5 ? 1 : cam.lvl * .6) : 0;
  // floor and ceiling, one row at a time
  for (let y = 0; y < RH; y++) {
    const floor = y > hz, dy = floor ? y - hz + .5 : hz - y - .5;
    if (dy < .4) { const c = 0xFF000000 | (fogB * lvl * .5 | 0) << 16 | (fogG * lvl * .5 | 0) << 8 | (fogR * lvl * .5 | 0); for (let x = 0; x < RW; x++) px[y * RW + x] = c; continue; }
    const rd = (floor ? EYE : WH - EYE) * focal / dy, fogF = Math.exp(-rd * FOGK), br = lvl * (.3 + .7 * fogF), fa = lvl * (1 - fogF) * .5;
    const ar = fogR * fa, ag = fogG * fa, ab = fogB * fa, tex = floor ? T.floor : T.ceil;
    const stepX = rd * 2 * planeX / RW, stepY = rd * 2 * planeY / RW;
    let fx = cam.x + rd * (dirX - planeX), fy = cam.y + rd * (dirY - planeY);
    for (let x = 0; x < RW; x++, fx += stepX, fy += stepY) {
      const cx = Math.floor(fx), cy = Math.floor(fy), u = fx - cx, v = fy - cy;
      let r, g, b;
      const e = !floor && cx >= 0 && cy >= 0 && cx < MAPW && cy < MAPH && u > .08 && u < .92 && v > .3 && v < .7 ? emit[cy * MAPW + cx] : -1;
      if (!floor && e >= 0 && (cx % 3 === 0 && (cy & 1) === 0)) { const k = e; r = (118 + 137 * k) * Math.max(.5, fogF) + ar; g = (116 + 136 * k) * Math.max(.5, fogF) + ag; b = (96 + 124 * k) * Math.max(.5, fogF) + ab; if (cam.night) { r *= .35; g *= .35; b *= .35; } }
      else { const ti = (((v * TS) | 0) * TS + ((u * TS) | 0)) * 3; r = tex[ti] * br + ar; g = tex[ti + 1] * br + ag; b = tex[ti + 2] * br + ab; }
      px[y * RW + x] = 0xFF000000 | (b > 255 ? 255 : b | 0) << 16 | (g > 255 ? 255 : g | 0) << 8 | (r > 255 ? 255 : r | 0);
    }
  }
  // walls, one column at a time
  for (let x = 0; x < RW; x++) {
    const camX = 2 * x / RW - 1, rdx = dirX + planeX * camX, rdy = dirY + planeY * camX;
    let mx = Math.floor(cam.x), my = Math.floor(cam.y), side = 0;
    const ddx = Math.abs(1 / rdx), ddy = Math.abs(1 / rdy);
    let sx, sy, sdx, sdy;
    if (rdx < 0) { sx = -1; sdx = (cam.x - mx) * ddx; } else { sx = 1; sdx = (mx + 1 - cam.x) * ddx; }
    if (rdy < 0) { sy = -1; sdy = (cam.y - my) * ddy; } else { sy = 1; sdy = (my + 1 - cam.y) * ddy; }
    for (let i = 0; i < 80; i++) { if (sdx < sdy) { sdx += ddx; mx += sx; side = 0; } else { sdy += ddy; my += sy; side = 1; } if (isWall(mx, my)) break; }
    const perp = Math.max(.05, side === 0 ? sdx - ddx : sdy - ddy);
    zbuf[x] = perp;
    let wx = side === 0 ? cam.y + perp * rdy : cam.x + perp * rdx; wx -= Math.floor(wx);
    let tx = (wx * TS) | 0; if ((side === 0 && rdx > 0) || (side === 1 && rdy < 0)) tx = TS - 1 - tx;
    const lh = focal / perp, top = hz - (WH - EYE) * lh, bot = hz + EYE * lh, total = bot - top;
    const fogF = Math.exp(-perp * FOGK), br = lvl * (.3 + .7 * fogF) * (side ? .8 : 1), fa = lvl * (1 - fogF) * .5;
    const ar = fogR * fa, ag = fogG * fa, ab = fogB * fa;
    for (let y = Math.max(0, Math.ceil(top)), y1 = Math.min(RH - 1, Math.floor(bot)); y <= y1; y++) {
      const ti = ((((y - top) / total * TS) & 63) * TS + tx) * 3, r = T.wall[ti] * br + ar, g = T.wall[ti + 1] * br + ag, b = T.wall[ti + 2] * br + ab;
      px[y * RW + x] = 0xFF000000 | (b > 255 ? 255 : b | 0) << 16 | (g > 255 ? 255 : g | 0) << 8 | (r > 255 ? 255 : r | 0);
    }
  }
  // tape colour bleed (red and blue slip a pixel apart); night-vision turns everything green
  const night = cam.night;
  for (let y = 0; y < RH; y++) for (let x = 0; x < RW; x++) {
    const i = y * RW + x, rr = px[Math.min(RW - 1, x + 1) + y * RW] & 255, gg = (px[i] >> 8) & 255, bb = (px[Math.max(0, x - 1) + y * RW] >> 16) & 255;
    if (night) { let l = (rr * .3 + gg * .59 + bb * .11) * 2.4 + (H(i + t * 99) - .5) * 40; l = l < 0 ? 0 : l > 255 ? 255 : l; outPx[i] = 0xFF000000 | (l * .3 | 0) << 16 | (l | 0) << 8 | (l * .25 | 0); }
    else outPx[i] = 0xFF000000 | bb << 16 | gg << 8 | rr;
  }
  lg.putImageData(lowImg, 0, 0);
  return { dirX, dirY, planeX, planeY, L, focal, hz };
}

// a billboard standing on the floor; returns where its head ended up on the 480×270 frame
function drawSprite(spr, wx, wy, hWorld, wWorld, cam, r, alpha) {
  const relX = wx - cam.x, relY = wy - cam.y, inv = 1 / (r.planeX * r.dirY - r.dirX * r.planeY);
  const a = inv * (r.dirY * relX - r.dirX * relY), depth = inv * (-r.planeY * relX + r.planeX * relY);
  if (depth < .25) return null;
  const sxc = RW / 2 * (1 + a / depth), scale = r.focal / depth, w = wWorld * scale, h = hWorld * scale, bottom = r.hz + EYE * scale, top = bottom - h;
  lg.imageSmoothingEnabled = false; lg.globalAlpha = alpha;
  for (let x = Math.max(0, Math.floor(sxc - w / 2)); x < Math.min(RW, sxc + w / 2); x++) {
    if (depth >= zbuf[x]) continue;
    lg.drawImage(spr, Math.min(spr.width - 1, ((x - (sxc - w / 2)) / w * spr.width) | 0), 0, 1, spr.height, x, top, 1, h);
  }
  lg.globalAlpha = 1;
  return { x: sxc, top, depth };
}

// ---------------------------------------------------------------- the camcorder
let NOISE = null, SCAN = null;
function makeFilm() {
  NOISE = [];
  for (let k = 0; k < 6; k++) {
    const c = document.createElement('canvas'); c.width = c.height = 480; const g = c.getContext('2d'), im = g.createImageData(480, 480), p = new Uint32Array(im.data.buffer);
    for (let i = 0; i < p.length; i++) { const v = H(i * .37 + k * 1000) < .5 ? 255 : 0, a = (H(i * 1.7 + k * 77) * 46) | 0; p[i] = a << 24 | v << 16 | v << 8 | v; }
    g.putImageData(im, 0, 0); NOISE.push(c);
  }
  SCAN = document.createElement('canvas'); SCAN.width = 4; SCAN.height = 4; const g = SCAN.getContext('2d'); g.fillStyle = 'rgba(0,0,0,.28)'; g.fillRect(0, 2, 4, 2);
}
function glitchBands(c, t, strength) {
  const n = 1 + Math.floor(strength * 5);
  for (let i = 0; i < n; i++) {
    const y = Math.floor(H(Math.floor(t * 30) * 5.1 + i) * VH), h = 8 + Math.floor(H(i * 3 + Math.floor(t * 30)) * 70), dx = (H(i + Math.floor(t * 30) * 2.3) - .5) * 140 * strength;
    c.drawImage(c.canvas, 0, y, VW, h, dx, y, VW, h);
  }
}
const pad = (n, w = 2) => String(Math.floor(n)).padStart(w, '0');

function drawFrame(c, t) {
  t = clamp(t, 0, DUR - 1e-4);
  const cam = poseAt(t), r = renderWorld(cam, t), fig = figureAt(t);
  // the figure
  let head = null;
  if (fig && (cam.lvl > .02 || cam.night)) {
    if (fig.clawd) head = drawSprite(SPR.clawd, fig.x, fig.y, .42, .52, cam, r, 1);
    else drawSprite(fig.night ? SPR.night : SPR.dark, fig.x, fig.y, .92, .46, cam, r, fig.night ? 1 : .94);
  }
  c.setTransform(1, 0, 0, 1, 0, 0); c.globalCompositeOperation = 'source-over'; c.globalAlpha = 1; c.filter = 'none';
  c.fillStyle = '#000'; c.fillRect(0, 0, VW, VH);
  c.save(); c.translate(VW / 2, VH / 2); c.rotate(cam.roll); c.scale(1.05, 1.05); c.imageSmoothingEnabled = true; c.drawImage(lowCv, -VW / 2, -VH / 2, VW, VH); c.restore();
  // bloom from the lights
  if (!cam.night) { c.globalCompositeOperation = 'lighter'; c.filter = 'blur(18px)'; c.globalAlpha = .2 * clamp(cam.lvl); c.drawImage(lowCv, 0, 0, VW, VH); c.filter = 'none'; c.globalAlpha = 1; c.globalCompositeOperation = 'source-over'; }
  // glitches: around every flicker, and a slow tracking band
  let gl = 0; for (const [a, d] of FLICKS) if (t >= a && t < a + d) gl = Math.max(gl, d > .8 ? .8 : .35);
  if (t >= T_BLACKOUT[0] - .3 && t < T_BLACKOUT[1] + .15) gl = 1;
  if (gl > 0) glitchBands(c, t, gl);
  const band = (t * 140) % 1500 - 200; if (band < VH) { c.fillStyle = 'rgba(255,255,255,.035)'; c.fillRect(0, band, VW, 90); glitchBands(c, t, .12); }
  // scanlines, grain, vignette
  c.fillStyle = c.createPattern(SCAN, 'repeat'); c.fillRect(0, 0, VW, VH);
  const n = NOISE[Math.floor(t * 30) % 6]; c.globalAlpha = cam.night ? 1 : .8; const ox = -Math.floor(H(Math.floor(t * 30)) * 480), oy = -Math.floor(H(Math.floor(t * 30) + 9) * 480);
  for (let y = oy; y < VH; y += 480) for (let x = ox; x < VW; x += 480) c.drawImage(n, x, y);
  c.globalAlpha = 1;
  const vg = c.createRadialGradient(VW / 2, VH / 2, VH * .45, VW / 2, VH / 2, VH * 1.0); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,.55)'); c.fillStyle = vg; c.fillRect(0, 0, VW, VH);

  // Clawd's speech bubble
  if (head && t > 36.0 && t < 37.8) {
    const bx = head.x / RW * VW, by = head.top / RH * VH - 70, text = t < 36.9 ? '哼！' : '别关灯', pop = Math.min(1, (t - (t < 36.9 ? 36.0 : 36.9)) / .12);
    c.save(); c.translate(bx, by); c.scale(pop, pop); c.fillStyle = 'rgba(250,246,236,.96)'; c.strokeStyle = '#3A2A24'; c.lineWidth = 5;
    c.beginPath(); c.roundRect(-130, -62, 260, 100, 30); c.fill(); c.stroke(); c.beginPath(); c.moveTo(-18, 36); c.lineTo(0, 70); c.lineTo(18, 36); c.fillStyle = 'rgba(250,246,236,.96)'; c.fill(); c.stroke();
    c.fillStyle = '#3A2A24'; c.font = `66px ${F_CN}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(text, 0, -12); c.restore();
  }

  // on-screen display
  const tape = 'rgba(240,240,230,.92)', end = t > 37.9;
  c.font = `34px ${F_MONO}`; c.textBaseline = 'alphabetic'; c.textAlign = 'left'; c.shadowColor = 'rgba(0,0,0,.7)'; c.shadowBlur = 4;
  if (!end) {
    if (Math.floor(t * 1.6) % 2 === 0 || t < .5) { c.fillStyle = '#ff3b30'; c.beginPath(); c.arc(112, 92, 13, 0, 7); c.fill(); }
    c.fillStyle = tape; c.fillText('REC', 138, 104); c.textAlign = 'right'; c.fillText('SP', VW - 120, 104);
    c.strokeStyle = tape; c.lineWidth = 3; c.strokeRect(VW - 240, 70, 44, 24); c.fillStyle = tape; c.fillRect(VW - 237, 73, 28, 18); c.fillRect(VW - 196, 77, 4, 10);
    c.textAlign = 'left'; const sec = 12 + t; c.fillText(`OCT 04 1996`, 112, VH - 130); c.fillText(`23:47:${pad(sec % 60)}`, 112, VH - 90);
    c.textAlign = 'right'; c.fillText(`0:${pad(t / 60 % 60)}:${pad(t % 60)}`, VW - 112, VH - 90);
    if (t > 4.5 && t < 8) { const a = Math.min(smooth((t - 4.5) / .5), 1 - smooth((t - 7.4) / .6)); c.globalAlpha = a; c.textAlign = 'center'; c.font = `46px ${F_MONO}`; c.fillText('LEVEL 0', VW / 2, VH - 200); c.font = `54px ${F_CN}`; c.fillText('后室 · 大厅', VW / 2, VH - 135); c.globalAlpha = 1; }
  }
  c.shadowBlur = 0;

  // blackouts at either end and the end card
  const fade = Math.max(1 - smooth(t / .6), smooth((t - 37.6) / .3));
  if (fade > 0) { c.fillStyle = `rgba(0,0,0,${fade})`; c.fillRect(0, 0, VW, VH); }
  if (t >= 38.2) {
    c.fillStyle = '#000'; c.fillRect(0, 0, VW, VH);
    c.globalAlpha = .6; c.drawImage(NOISE[Math.floor(t * 30) % 6], 0, 0, VW, VH); c.globalAlpha = 1;
    c.textAlign = 'center'; c.textBaseline = 'middle';
    c.globalAlpha = smooth((t - 38.3) / .5); c.fillStyle = tape; c.font = `64px ${F_MONO}`; c.fillText('THE BACKROOMS', VW / 2, VH / 2 - 150); c.font = `40px ${F_MONO}`; c.fillText('LEVEL 0', VW / 2, VH / 2 - 90);
    c.globalAlpha = smooth((t - 39.0) / .5); c.fillStyle = '#E8D58A'; c.font = `78px ${F_CN}`; c.fillText('后室没有出口。', VW / 2, VH / 2 + 40);
    c.globalAlpha = smooth((t - 39.9) / .5); c.fillStyle = '#F0A070'; c.fillText('但总有人替你留着灯。', VW / 2, VH / 2 + 150);
    c.globalAlpha = 1;
  }
}
