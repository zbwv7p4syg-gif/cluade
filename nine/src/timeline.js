// timeline.js — when everything happens in 九分之九 · 像素 MV. Shots cut on the sung lines (the user's .lrc and the
// four later lines it does not cover), the drum entry at 42.06 s and the 144 BPM grid.
//
// The story: 我 is nine and doing his 九九乘法表 homework when the yellow puppy with four white paws plants a paw on
// "九九八十一", so the puppy is called 九九. The nine-pane window of his room keeps count: on each "九分之九" it
// lights up pane by pane. Time is told in dog years on a bone-shaped tag.

const DUR = BEATMAP.duration;

const SHOTS = [
  { t0: 0.00, name: 'window' },       // dawn in the nine-pane window, the title; the middle pane opens onto the past
  { t0: 16.00, name: 'plains' },      // the sun pressing on the plain; dad's scooter along the straight road, wind in the rice
  { t0: 29.30, name: 'litter', x: .6 },  // a box of puppies under the banyan; one waddles over; no words needed
  { t0: 42.06, name: 'paws' },        // drums in: golden profile, then four white paws beside two white sneakers
  { t0: 49.40, name: 'homework', x: .5 }, // the fan turns, the clock ticks, mum cooks: the world keeps working, he does his homework
  { t0: 55.70, name: 'paper', x: .3 },    // 九九乘法表, one line per half beat; a white paw lands on 九九八十一
  { t0: 62.40, name: 'collar', x: .4 },  // a red collar and a tag that says 九九; the bell rings on the beat
  { t0: 68.50, name: 'door', x: .3, xc: '#FFFFFF' }, // chorus: the puppy walks in through the door and the house fills with colour
  { t0: 75.10, name: 'panes', x: .5 },   // boy and puppy under the nine-pane window; the panes light one by one
  { t0: 84.60, name: 'hide', x: .5 },    // hide-and-seek: eyes covered, he walks straight to the tail behind the water jar
  { t0: 91.60, name: 'grain', x: .5 },   // a clear southern day: rice drying in the courtyard, paw prints through the grain
  { t0: 97.40, name: 'busstop', x: .5 }, // he leaves on the bus; 九九 waits at the stop while days and nights race by
  { t0: 104.20, name: 'paddies', x: .6 },  // night: flooded paddies mirror the stars, the two of them on the ridge
  { t0: 110.70, name: 'doorstep', x: .5 }, // head down on the step; a chin on his knee, then her favourite slipper
  { t0: 123.40, name: 'movein', x: .4, xc: '#FFFFFF' }, // chorus 2: the city flat, 九九 walks in again
  { t0: 130.00, name: 'birthday', x: .4 }, // 九九 turns nine: nine candles, lit one per beat
  { t0: 140.00, name: 'puzzle', x: .6 },   // a nine-piece puzzle, one piece missing, 九九 brings it in her mouth
  { t0: 150.10, name: 'leave', x: .6 },    // night: old 九九 walks into a door of light and runs off into the plain, young again
  { t0: 156.70, name: 'rainwin', x: .8 },  // rain on the window, the empty bed, the collar on the latch
  { t0: 166.50, name: 'breath', x: .8 },   // a dream at first light: a warm nose, breath on his face
  { t0: 173.00, name: 'dawn', x: .6 },     // he wakes; nine squares of light lie on the floor where she used to sleep
  { t0: 180.60, name: 'grid', x: .4, xc: '#FFF3D6' }, // the nine squares become nine memories
  { t0: 193.00, name: 'walk', x: .5 },     // walking through the years together, until he walks on alone
  { t0: 205.40, name: 'sunset', x: .8 },   // the plain again, a dog-shaped cloud
  { t0: 214.08, name: 'end', x: 1.2 },     // the window at dusk, the title, the credit
];
SHOTS.forEach((s, i) => s.t1 = i + 1 < SHOTS.length ? SHOTS[i + 1].t0 : DUR);
const shotIndex = t => { let i = 0; while (i + 1 < SHOTS.length && t >= SHOTS[i + 1].t0) i++; return i; };

// dog-year tags: [text, from, to]
const TAGS = [
  ['九九 · 两个月', 30.4, 37.0],
  ['九九 · 2岁', 85.0, 90.8],
  ['九九 · 5岁', 92.0, 97.0],
  ['九九 · 6岁', 97.8, 103.8],
  ['九九 · 8岁', 104.6, 110.2],
  ['九九 · 9岁', 123.8, 129.6],
  ['九九 · 12岁', 140.4, 146.0],
  ['九九 · 15岁', 150.5, 156.2],
];

// sung-syllable onsets of the three "九分之九" lines (Whisper word timestamps of this recording, measured by
// fraction/analyze.py; times only). Nine onsets each, so something lights (or goes out) on every one.
const NINE_A = [75.04, 75.98, 76.68, 77.04, 77.56, 78.04, 78.96, 79.52, 79.96], NINE_A_END = 81.72;
const NINE_B = [130.04, 130.94, 131.6, 132.12, 132.54, 132.94, 134.06, 134.5, 134.94];
const NINE_C = [156.66, 157.64, 158.22, 158.72, 159.14, 159.48, 160.34, 161.24, 161.62];
const countIn = (list, t) => list.filter(x => t >= x).length;

// beat helpers on the fitted grid
const BEAT = BEATMAP.beat;
const beatPos = t => (t - BEATMAP.phase) / BEAT;
const beatPhase = t => { const p = beatPos(t) % 1; return p < 0 ? p + 1 : p; };
const beatAt = t => Math.floor(beatPos(t));
const lastKick = t => { let k = -1e9; for (const x of BEATMAP.kicks) { if (x > t) break; k = x; } return k; };
