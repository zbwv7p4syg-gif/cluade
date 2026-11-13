// timeline.js — when everything happens in 平凡的一天 · 像素 MV. One shot per sung line, cut on the line times of the
// user's .lrc (the words themselves are only read at render time, from build/lyrics.js, and never stored here).
// v is the time of day a repeated chorus is retold in: 0 late afternoon, 1 night, 2 the next golden morning.

const DUR = BEATMAP.duration;

const SHOTS = [
  { t0: 0.00, name: 'dawn' },              // night turns to dawn over the little town: hills, river, roofs, a train, a cat; the title
  { t0: 8.2, name: 'bedroom' },            // his room: the sunbeam creeps across the floor, the clock ticks towards half past seven
  { t0: 15.7, name: 'wake' },              // he wakes by himself at 7:30 and stretches; so does the cat
  { t0: 23.3, name: 'chime' },             // the wind chime rings; he opens the window on a sky of light clouds
  { t0: 31.0, name: 'laundry' },           // the washing dries on the roof; he buries his face in a sunny shirt
  { t0: 38.6, name: 'soft' },              // tea steaming, the cat asleep in the sun, dust floating in the light
  { t0: 46.2, name: 'flowers' },           // down the street, flowers open at every corner as he passes
  { t0: 53.8, name: 'lovesong' },          // a record shop: notes and hearts float out of the gramophone
  { t0: 61.4, name: 'nearby' },            // the map of the town: home to the bakery is only a short dotted line
  { t0: 69.1, name: 'kindness' },          // the busy square: every neighbour has a smile for someone
  { t0: 75.3, name: 'ordinary', v: 0 },    // an ordinary afternoon in the square: pigeons, the fountain, the clock tower
  { t0: 80.1, name: 'askyou', v: 0 },      // he turns to us and waves
  { t0: 83.8, name: 'slowhome', v: 0 },    // others run for the bus; he strolls home, overtaken only by a snail
  { t0: 90.0, name: 'idle', v: 0 },        // lying in the grass by the river, watching the clouds go by
  { t0: 99.1, name: 'breeze', v: 0 },      // on the bridge, the evening wind in his hair
  { t0: 104.0, name: 'ride' },             // interlude: cycling along the river through the golden afternoon
  { t0: 122.5, name: 'sunset' },           // the sun melts into the river
  { t0: 130.1, name: 'market' },           // the dusk market, lanterns and stalls; a bag full of shopping
  { t0: 137.7, name: 'call' },             // the phone rings: his friend is waiting at the gate
  { t0: 145.3, name: 'chat' },             // they meet and the talk never stops
  { t0: 153.0, name: 'courtyard' },        // a table laid in a courtyard full of flowers, lights strung overhead
  { t0: 160.5, name: 'cheers' },           // a little tipsy: glasses, a guitar, songs and laughter
  { t0: 168.1, name: 'notomorrow' },       // tomorrow's map blows away; he leans back and looks at the stars
  { t0: 175.8, name: 'nightwind' },        // the warm night wind: lanterns sway, fireflies drift
  { t0: 181.9, name: 'ordinary', v: 1 },
  { t0: 186.8, name: 'askyou', v: 1 },
  { t0: 190.5, name: 'slowhome', v: 1 },
  { t0: 196.8, name: 'idle', v: 1 },
  { t0: 205.7, name: 'breeze', v: 1 },
  { t0: 212.6, name: 'perfect' },          // the whole day pinned up in photographs, sparkling
  { t0: 217.2, name: 'offer' },            // he holds a flower out to us
  { t0: 221.1, name: 'simple' },           // a scribble of knots and worries untangles into one straight line
  { t0: 227.2, name: 'idle', v: 2 },
  { t0: 236.2, name: 'breeze', v: 2 },
  { t0: 243.3, name: 'horizon' },          // he and his friend walk up the hill towards a shining little town far away
  { t0: 250.7, name: 'goodnight' },        // night again: the lights go out one by one, the cat curls up; the title
];
SHOTS.forEach((s, i) => { s.t1 = i + 1 < SHOTS.length ? SHOTS[i + 1].t0 : DUR; s.v = s.v || 0; });
const shotIndex = t => { let i = 0; while (i + 1 < SHOTS.length && t >= SHOTS[i + 1].t0) i++; return i; };

// beat helpers on the fitted grid
const beatPos = t => (t - BEATMAP.phase) / BEATMAP.beat;
const beatPhase = t => { const p = beatPos(t) % 1; return p < 0 ? p + 1 : p; };
const lastKick = t => { let k = -1e9; for (const x of BEATMAP.kicks) { if (x > t) break; k = x; } return k; };
const kickPulse = (t, k = 6) => Math.exp(-Math.max(0, t - lastKick(t)) * k);
const envAt = (band, t) => { const e = BEATMAP.env[band], i = Math.max(0, Math.min(e.length - 1, t * 30)), j = Math.floor(i), f = i - j; return e[j] * (1 - f) + (e[Math.min(e.length - 1, j + 1)] ?? 0) * f; };
// is a syllable being sung right now? (used to move a speaking mouth)
const singing = t => { const w = BEATMAP.words; let lo = 0, hi = w.length - 1, k = -1; while (lo <= hi) { const m = (lo + hi) >> 1; if (w[m] <= t) { k = m; lo = m + 1; } else hi = m - 1; } return k >= 0 && t - w[k] < .16; };
