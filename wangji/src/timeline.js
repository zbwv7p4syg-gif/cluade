// timeline.js — when everything happens in 给我一个理由忘记 · 铅笔 MV. One shot per sung line, cut on the line times of the
// user's .lrc (the words themselves are only read at render time, from build/lyrics.js, and never stored here).
// v is the setting of the retelling: 0 the city at night, 1 winter, 2 after the storm.

const DUR = BEATMAP.duration;

const SHOTS = [
  { t0: 0.00, name: 'title' },             // rain running down a window; city lights blurred behind it; the title is written
  { t0: 14.0, name: 'cityrain' },          // the whole city in pencil, in the rain
  { t0: 28.0, name: 'crossing' },          // umbrellas hurry past her at a crossing; she stands still
  { t0: 39.0, name: 'stopping' },          // the rain thins out; she lowers her umbrella
  { t0: 47.15, name: 'graysky' },          // she looks up into a sky shaded grey; the last drop falls into a puddle
  { t0: 54.05, name: 'smiley' },           // memory, in colour: he draws a smiley face on a misted café window
  { t0: 61.35, name: 'footsteps' },        // an empty street at midnight; every step rings out
  { t0: 66.75, name: 'lonely' },           // she holds herself in a lot of empty paper
  { t0: 68.65, name: 'lightsoff' },        // the city glows in colour; she pulls the cord and her window goes dark
  { t0: 74.45, name: 'crowd', v: 0 },      // people rush past on both sides of her
  { t0: 78.15, name: 'alone', v: 0 },      // and are rubbed out, until only she is left
  { t0: 81.35, name: 'smile' },            // at a table of friends she smiles
  { t0: 83.15, name: 'heartcry', v: 0 },   // inside her, a pencil heart full of rain
  { t0: 87.85, name: 'erase', v: 0 },      // she rubs out his portrait; it draws itself again
  { t0: 92.25, name: 'coatwrap', v: 0 },   // memory: he wraps his red coat round her in the snow
  { t0: 94.95, name: 'delete', v: 0 },     // her thumb hovers over "delete" under his photo
  { t0: 99.25, name: 'decision', v: 0 },   // that night: two umbrellas walk away from each other
  { t0: 102.05, name: 'thread', v: 0 },    // she pulls a red thread out of her heart; it only gets longer
  { t0: 104.65, name: 'clearer', v: 0 },   // his faint outline sharpens and fills with colour
  { t0: 106.45, name: 'distance', v: 0 },  // the two of them at the two edges of the page, a ruler between
  { t0: 109.15, name: 'empty', v: 0 },     // the other half of the bench, a dotted outline
  { t0: 111.85, name: 'inheart', v: 0 },   // hand on her chest: inside, in colour, him
  { t0: 120.2, name: 'seasons' },          // outside her window the leaves fall and the first snow comes
  { t0: 133.15, name: 'places' },          // the places they went, each with the two of them still there in colour
  { t0: 140.05, name: 'laugh' },           // his laugh, carefree, spinning in the snow; she turns round
  { t0: 147.15, name: 'home' },            // the door of a one-room flat; one cup, one chair
  { t0: 152.75, name: 'afraid' },          // she stops in the doorway, eyes wide
  { t0: 154.55, name: 'coat' },            // the red winter coat on its hook, the only colour in the room
  { t0: 160.25, name: 'crowd', v: 1 },
  { t0: 164.15, name: 'alone', v: 1 },
  { t0: 167.35, name: 'smilecry' },        // the smile, then the heart full of rain
  { t0: 173.75, name: 'erase', v: 1 },
  { t0: 178.15, name: 'coatwrap', v: 1 },
  { t0: 180.85, name: 'delete', v: 1 },
  { t0: 185.35, name: 'decision', v: 1 },
  { t0: 187.95, name: 'thread', v: 1 },
  { t0: 190.55, name: 'clearer', v: 1 },
  { t0: 192.45, name: 'distempty', v: 1 },
  { t0: 197.85, name: 'inheart', v: 1 },
  { t0: 206.6, name: 'storm' },            // the storm comes back: rain, lightning
  { t0: 223.95, name: 'noerase' },         // she puts the eraser down; the portrait fills with colour
  { t0: 228.35, name: 'farewell' },        // that night again: he walks away into the downpour in his red coat
  { t0: 231.05, name: 'keep' },            // she holds the phone to her heart; the bin fades away
  { t0: 235.45, name: 'wait' },            // she waits at the bus stop while the seasons go round her
  { t0: 238.05, name: 'thread', v: 2 },
  { t0: 240.85, name: 'clearer', v: 2 },
  { t0: 242.65, name: 'distance', v: 2 },
  { t0: 245.35, name: 'empty', v: 2 },
  { t0: 247.95, name: 'inheart', v: 2 },   // and this time the colour spreads over the whole page
  { t0: 263.85, name: 'missyou' },         // she draws a heart on the misted window
  { t0: 269.0, name: 'end' },              // morning; colour comes into the drawing of the city; the title again
];
SHOTS.forEach((s, i) => { s.t1 = i + 1 < SHOTS.length ? SHOTS[i + 1].t0 : DUR; s.v = s.v || 0; });
const shotIndex = t => { let i = 0; while (i + 1 < SHOTS.length && t >= SHOTS[i + 1].t0) i++; return i; };

// beat helpers on the fitted grid
const beatPos = t => (t - BEATMAP.phase) / BEATMAP.beat;
const beatPhase = t => { const p = beatPos(t) % 1; return p < 0 ? p + 1 : p; };
const lastKick = t => { let k = -1e9; for (const x of BEATMAP.kicks) { if (x > t) break; k = x; } return k; };
const kickPulse = (t, k = 6) => Math.exp(-Math.max(0, t - lastKick(t)) * k);
const envAt = (band, t) => { const e = BEATMAP.env[band], i = Math.max(0, Math.min(e.length - 1, t * 30)), j = Math.floor(i), f = i - j; return e[j] * (1 - f) + (e[Math.min(e.length - 1, j + 1)] ?? 0) * f; };
