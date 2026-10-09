// world.js — the one timeline. The map of Level 0, the route the camera walks, the speed it walks at,
// when the lights flicker, when something stands behind the camera, and the footsteps that follow
// from the distance walked. render.js draws from it and audio.js sounds from it.

const DUR = 41.5;
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const lerp = (a, b, t) => a + (b - a) * t;
const smooth = t => { t = clamp(t); return t * t * (3 - 2 * t); };
const H = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

// ---------------------------------------------------------------- the map (1 cell = 2 m, ceiling 1.35 cells)
const MAPW = 32, MAPH = 20;
const MAP = new Uint8Array(MAPW * MAPH).fill(1);
const ROOMS = [[1, 1, 10, 7], [12, 1, 20, 7], [22, 1, 30, 7], [1, 9, 13, 14], [15, 9, 22, 14], [24, 9, 30, 14], [1, 16, 9, 18], [11, 16, 22, 18], [24, 16, 30, 18]];
const DOORS = [[11, 4, 11, 5], [21, 3, 21, 4], [4, 8, 5, 8], [17, 8, 18, 8], [26, 8, 27, 8], [23, 10, 23, 11], [3, 15, 4, 15], [17, 15, 18, 15], [26, 15, 27, 15], [10, 16, 10, 18], [23, 17, 23, 18]];
const PILLARS = [[5, 2], [8, 2], [8, 6], [14, 2], [18, 2], [14, 6], [18, 6], [24, 2], [29, 2], [24, 6], [29, 7], [6, 10], [9, 13], [12, 13],
                 [18, 13], [21, 13], [20, 9], [26, 13], [29, 13], [29, 9], [7, 18], [2, 16], [14, 18], [18, 18], [21, 16]];
for (const [x0, y0, x1, y1] of [...ROOMS, ...DOORS]) for (let y = y0; y <= y1; y++) for (let x = x0; x <= x1; x++) MAP[y * MAPW + x] = 0;
for (const [x, y] of PILLARS) MAP[y * MAPW + x] = 1;
const isWall = (x, y) => x < 0 || y < 0 || x >= MAPW || y >= MAPH || MAP[y * MAPW + x] === 1;

// ---------------------------------------------------------------- the route (corners rounded, parametrised by distance)
const WAY = [[3, 5], [8, 5], [11.5, 5], [16, 5], [19, 4], [21.5, 4], [25, 4], [27, 6], [27, 11], [23.5, 11], [19, 11], [15.8, 11]];
function chaikin(pts, n) {
  for (let k = 0; k < n; k++) {
    const out = [pts[0]];
    for (let j = 0; j < pts.length - 1; j++) { const a = pts[j], b = pts[j + 1]; out.push([.75 * a[0] + .25 * b[0], .75 * a[1] + .25 * b[1]], [.25 * a[0] + .75 * b[0], .25 * a[1] + .75 * b[1]]); }
    out.push(pts[pts.length - 1]); pts = out;
  }
  return pts;
}
const PTS = chaikin(WAY, 3), CUM = [0];
for (let i = 1; i < PTS.length; i++) CUM.push(CUM[i - 1] + Math.hypot(PTS[i][0] - PTS[i - 1][0], PTS[i][1] - PTS[i - 1][1]));
const PLEN = CUM[CUM.length - 1];
function pathAt(s) {
  s = clamp(s, 0, PLEN); let lo = 0, hi = CUM.length - 1;
  while (hi - lo > 1) { const m = (lo + hi) >> 1; CUM[m] <= s ? lo = m : hi = m; }
  const u = (s - CUM[lo]) / Math.max(1e-9, CUM[hi] - CUM[lo]);
  return [lerp(PTS[lo][0], PTS[hi][0], u), lerp(PTS[lo][1], PTS[hi][1], u)];
}
function headingAt(s) {
  s = clamp(s, .8, PLEN - .8);
  const a = pathAt(s - .8), b = pathAt(s + .8); return Math.atan2(b[1] - a[1], b[0] - a[0]);
}

// ---------------------------------------------------------------- how fast we walk: stroll, then run
const T_STOP = 33.4;
function speedProfile(t) {
  if (t < 3) return 0;
  if (t < 4.5) return smooth((t - 3) / 1.5);
  if (t < 26) return 1;
  if (t < 27.5) return 1 + 1.7 * smooth((t - 26) / 1.5);
  if (t < 32.8) return 2.7;
  if (t < T_STOP) return 2.7 * (1 - smooth((t - 32.8) / .6));
  return 0;
}
const TAB_DT = 1 / 240, TAB = [0];
for (let i = 1; i <= Math.ceil(DUR / TAB_DT); i++) TAB.push(TAB[i - 1] + speedProfile((i - .5) * TAB_DT) * TAB_DT);
const TAB_TOTAL = TAB[Math.ceil(T_STOP / TAB_DT)];
function distAt(t) { const f = clamp(t, 0, DUR) / TAB_DT, i = Math.floor(f); return Math.min(PLEN, PLEN * lerp(TAB[i], TAB[Math.min(TAB.length - 1, i + 1)], f - i) / TAB_TOTAL); }
const speedAt = t => PLEN * speedProfile(t) / TAB_TOTAL;      // cells per second

const STRIDE = .6;                                            // cells per footstep
const STEPS = [];
for (let k = 1; k * STRIDE < PLEN; k++) { let lo = 0, hi = T_STOP; for (let i = 0; i < 30; i++) { const m = (lo + hi) / 2; distAt(m) < k * STRIDE ? lo = m : hi = m; } STEPS.push({ t: hi, k, run: speedAt(hi) > 1.8 }); }

// ---------------------------------------------------------------- looking back: something is standing behind you
const GLANCES = [{ t: 14.2, d: 9, hold: .9 }, { t: 18.0, d: 7, hold: .9 }, { t: 21.6, d: 5, hold: .9 }, { t: 24.6, d: 3.6, hold: .8 }, { t: 29.3, d: 2.6, hold: .45 }];
const TURN = .32, FINAL_TURN = [34.0, 1.0];
function lookBack(t) {
  let v = 0;
  for (const g of GLANCES) v += smooth((t - g.t) / TURN) - smooth((t - (g.t + TURN + g.hold)) / TURN);
  v += smooth((t - FINAL_TURN[0]) / FINAL_TURN[1]);
  return clamp(v);
}
// the figure: tall and dark until the lights come back on
const T_BLACKOUT = [34.8, 35.8];
function figureAt(t) {
  let d = null;
  for (const g of GLANCES) if (t >= g.t - .1 && t < g.t + TURN * 2 + g.hold + .2) d = g.d;
  if (t >= 33.9 && t < 35.8) d = 3.0;
  if (t >= 35.8 && t < 38.2) d = 2.4;
  if (d === null) return null;
  const s = distAt(t), p = pathAt(s - d), clawd = t >= 35.8;
  return { x: p[0], y: p[1], clawd, night: t >= T_BLACKOUT[0] && t < T_BLACKOUT[1] };
}

// ---------------------------------------------------------------- the lights
const FLICKS = [[.9, .3], [2.3, .5], [7.3, .4], [11.0, .5], [13.7, 1.1], [17.5, 1.1], [21.1, 1.1], [24.1, 1.1], [28.9, 1.0], [33.0, .5], [34.45, .35]];
function levelAt(t) {
  if (t >= T_BLACKOUT[0] && t < T_BLACKOUT[1]) return 0;
  let lv = 1;
  for (const [a, d] of FLICKS) if (t >= a && t < a + d) lv = (t - a > d * .45) ? 1 : (H(Math.floor((t - a) * 30) * 7.1 + a) < .55 ? .05 : 1);   // sputter first, then stay lit so you can see what is there
  return lv * (.97 + .03 * Math.sin(t * 37));
}
// individual ceiling panels: a few are bad bulbs
function panelOn(id, t) { return H(id * 3.7) < .12 ? (H(Math.floor(t * 9) + id) > .45 ? 1 : .15) : 1; }

// ---------------------------------------------------------------- the camera
function poseAt(t) {
  const s = distAt(t), v = speedAt(t), p = pathAt(s), ph = s / STRIDE, run = clamp((v - 1.1) / 1.6);
  const walk = clamp(v / 1.1, 0, 1.6);
  const bob = -Math.abs(Math.sin(Math.PI * ph)) * walk * (2.2 + 2.6 * run);
  const shake = (Math.sin(t * 2.1) * .012 + Math.sin(t * 5.3 + 1) * .007) * (1 + 2 * run) + (run > 0 ? Math.sin(t * 17) * .01 * run : 0);
  let yaw = headingAt(s) + Math.PI * lookBack(t) + shake + .05 * Math.sin(t * .8) * (1 - clamp(v));
  const roll = Math.sin(Math.PI * ph) * .012 * walk * (1 + run) + .006 * Math.sin(t * 1.3);
  const pitch = -3 + 5 * Math.sin(t * 1.1) * (1 - clamp(v)) - run * 6 * Math.abs(Math.sin(Math.PI * ph));
  return { x: p[0], y: p[1], yaw, horizonOff: bob + pitch, roll, lvl: levelAt(t), night: t >= T_BLACKOUT[0] && t < T_BLACKOUT[1], s, v };
}

// sanity check of the route against the map (printed in the console when a wall is closer than 0.3 cell)
(function checkRoute() {
  let worst = 9;
  for (let s = 0; s <= PLEN; s += .05) {
    const [x, y] = pathAt(s);
    for (let cy = Math.floor(y) - 1; cy <= Math.floor(y) + 1; cy++) for (let cx = Math.floor(x) - 1; cx <= Math.floor(x) + 1; cx++)
      if (isWall(cx, cy)) worst = Math.min(worst, Math.hypot(x - clamp(x, cx, cx + 1), y - clamp(y, cy, cy + 1)));
  }
  window.ROUTE_CLEARANCE = worst;
})();
