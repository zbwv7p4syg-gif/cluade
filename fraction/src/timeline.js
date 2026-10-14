// timeline.js — when everything happens in 几分之几 · 像素 MV. Shots cut on the sung lines that analyze.py
// measured (BEATMAP.lines); drum-driven details use BEATMAP.kicks and the 144 BPM grid.
// The subtitles are original lines, one per sung line, timed to the singing. No lyrics are stored here.

const DUR = BEATMAP.duration;
const LINE = i => BEATMAP.lines[i];

const SHOTS = [
  { t0: 0.00, name: 'title' },        // dawn over the plain, the title
  { t0: 16.28, name: 'field' },       // a hot summer day; a friend waves goodbye at the bus stop
  { t0: 29.18, name: 'clouds' },      // on the hill, watching clouds; a breath before the drums
  { t0: 42.06, name: 'meet' },        // golden hour: she walks by in white sneakers; the world rushes on
  { t0: 56.02, name: 'sure' },        // close-ups: his heart thumps on the kick, she turns round
  { t0: 68.51, name: 'ride' },        // chorus: riding along the southern coast; the pie starts to fill
  { t0: 82.22, name: 'night' },       // eyes closed on the night beach, then ice lollies by the sea
  { t0: 97.71, name: 'rain' },        // lost at a rainy crossroads, she waits under the street lamp
  { t0: 104.28, name: 'roof' },       // stars over the rooftop
  { t0: 117.00, name: 'fireworks' },  // fireworks on every kick, building into the chorus
  { t0: 123.04, name: 'pieces' },     // he is made of eight pieces, and more and more of them are hers
  { t0: 150.22, name: 'station' },    // she leaves on the train; one piece stays with him
  { t0: 163.44, name: 'apart' },      // the bus stop in the rain, then two windows drifting apart
  { t0: 186.42, name: 'seasons' },    // the same bench, summer to autumn to winter; he grows old
  { t0: 214.08, name: 'end' },        // sunset over the plain, the title again
];
SHOTS.forEach((s, i) => s.t1 = i + 1 < SHOTS.length ? SHOTS[i + 1].t0 : DUR);
const shotIndex = t => { let i = 0; while (i + 1 < SHOTS.length && t >= SHOTS[i + 1].t0) i++; return i; };

// one original subtitle per sung line (same order as BEATMAP.lines)
const SUBS = [
  '那年夏天，阳光铺满了整片田野',
  '风吹过来，有人偷偷擦了擦眼睛',
  '那时候的一切，都好得不像真的',
  '你逆着光走来，鞋子白得发亮',
  '世界照常转动，只有我停了下来',
  '就是这一刻',
  '我认出你了',
  '从那天起，我的故事多了一个人',
  '你一点一点，变成了我的一部分',
  '就算不看，我也知道你在哪',
  '一起去南方吹海风',
  '走错了路，你就在路口等我',
  '停下来的时候，头顶有满天星星',
  '你什么都不问，就站在我这边',
  '如果把我拆开来数一数',
  '有好几块，都是你给的',
  '我变得比以前更完整',
  '因为有你',
  '后来，你去了很远的地方',
  '可你给我的那几块，还留在这里',
  '我还记得你靠过来时的温度',
  '可那段路，已经走不回去了',
  '我的这一块，永远是你的形状',
  '这一次，你真的走远了',
  '日子一年一年过去，我的头发白了',
  '但我一直记得那个夏天',
];

// the pie in the corner: one more eighth of him becomes hers at each of these moments
const SLICES = [68.51, 75.04, 91.92, 110.86, 130.04];
const slicesAt = t => SLICES.filter(x => t >= x).length;

// beat helpers on the fitted grid
const beatPos = t => (t - BEATMAP.phase) / BEATMAP.beat;
const beatPhase = t => { const p = beatPos(t) % 1; return p < 0 ? p + 1 : p; };
const lastKick = t => { let k = -1e9; for (const x of BEATMAP.kicks) { if (x > t) break; k = x; } return k; };
const kicksIn = (a, b) => BEATMAP.kicks.filter(x => x >= a && x < b);
const envAt = (band, t) => { const e = BEATMAP.env[band], i = Math.max(0, Math.min(e.length - 1, t * 30)), j = Math.floor(i), f = i - j; return e[j] * (1 - f) + (e[Math.min(e.length - 1, j + 1)] ?? 0) * f; };
