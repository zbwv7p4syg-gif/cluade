// timeline.js — when everything happens. Shot boundaries sit on the sung phrase starts that analyze.py
// measured (BEATMAP.phrases); the drum-driven details use BEATMAP.kicks and the 139.94 BPM beat grid.
// No lyrics are stored here: the captions are original narration lines.

const DUR = BEATMAP.duration;
const SHOTS = [
  { t0: 0.00, name: 'river' },      // a soul with a suitcase heavier than itself sinks to a riverbed
  { t0: 6.00, name: 'storm' },      // lightning through the water, then rings of light ahead
  { t0: 14.86, name: 'light' },     // inside the light: figures waiting, scissors cut the suitcase loose
  { t0: 23.52, name: 'closing' },   // it looks back; the way in closes behind it
  { t0: 28.16, name: 'voice' },     // a newborn hears a humming voice in the dark
  { t0: 41.98, name: 'babble' },    // so much to say, only babble comes out
  { t0: 51.02, name: 'window' },    // by the window; it closes its eyes and remembers (build into the chorus)
  { t0: 55.66, name: 'grove' },     // chorus: long ago, a forest, then the hillside
  { t0: 60.84, name: 'jujube' },    // knocking ripe jujubes off the tree, one per kick
  { t0: 64.64, name: 'pockets' },   // pockets stuffed, walking home at sunset
  { t0: 69.48, name: 'lane' },      // an old lane: back then it was the grown-up and she was the kid
  { t0: 78.44, name: 'coins' },     // a copper coin for each beat, a smile for each coin
  { t0: 82.10, name: 'now' },       // now it is her turn to hold it
];
SHOTS.forEach((s, i) => s.t1 = i + 1 < SHOTS.length ? SHOTS[i + 1].t0 : DUR);
const shotIndex = t => { let i = 0; while (i + 1 < SHOTS.length && t >= SHOTS[i + 1].t0) i++; return i; };

const CAPTIONS = [
  [1.40, 5.70, '上辈子的事，都装进了箱子里'],
  [6.20, 9.40, '沉到很深、很深的地方'],
  [9.80, 14.40, '前面亮着光。要过去吗？'],
  [15.05, 19.40, '光的那一边，有人在等我'],
  [19.80, 23.30, '箱子，就留在这儿吧'],
  [23.70, 27.40, '回头看，来时的路已经没了'],
  [28.40, 33.60, '黑暗里，有人在轻轻哼歌'],
  [34.10, 36.90, '这个声音……是你'],
  [37.30, 41.60, '你笑着看我，好像我们第一次见面'],
  [42.20, 46.60, '我有好多好多话，想告诉你'],
  [47.60, 50.80, '可一开口，只有咿咿呀呀'],
  [51.20, 55.30, '没关系。闭上眼，我还能看见'],
  [56.10, 60.50, '很久很久以前'],
  [61.00, 64.40, '一竿子打下去，枣子哗啦啦地掉'],
  [64.85, 69.20, '兜里鼓鼓的，一路笑着回家'],
  [69.70, 74.20, '那时候，我是大人，你是小孩'],
  [74.70, 78.20, '小小的你，一路小跑跟着我'],
  [78.60, 81.90, '叮当，一枚铜钱，换一个笑脸'],
  [82.40, 85.60, '这一次，换你抱着我'],
];

// beat helpers on the fitted grid
const beatPos = t => (t - BEATMAP.phase) / BEATMAP.beat;              // beats since the first beat
const beatPhase = t => { const p = beatPos(t) % 1; return p < 0 ? p + 1 : p; };
const lastKick = t => { let k = -1e9; for (const x of BEATMAP.kicks) { if (x > t) break; k = x; } return k; };
const kicksIn = (a, b) => BEATMAP.kicks.filter(x => x >= a && x < b);
const envAt = (band, t) => { const e = BEATMAP.env[band], i = Math.max(0, Math.min(e.length - 1, t * 30)), j = Math.floor(i), f = i - j; return e[j] * (1 - f) + (e[Math.min(e.length - 1, j + 1)] ?? 0) * f; };
