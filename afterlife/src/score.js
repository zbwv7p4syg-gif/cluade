// score.js — the one timeline. 100 BPM, one beat = 0.6 s = 18 frames, one bar = 2.4 s.
// Shots cut on bar lines; every pencil stroke, paper fold, pop and ding below is both a sound
// (audio.js) and a moment on screen (visuals.js).

const BPM = 100, BEAT = 60 / BPM, BAR = BEAT * 4;
const b = n => +(n * BEAT).toFixed(4);           // beat -> seconds
const DUR = b(88);                               // 22 bars = 52.8 s

const QUESTION = '人死后，会去哪里？';
const ANSWER = ['会去所有', '还记得他们的地方。'];

// the montage: eight answers, two beats each
const ANSWERS = [
  { key: 'star',   text: '变成天上的星星', bg: '#8DB6E6' },
  { key: 'sea',    text: '回到大海',       bg: '#EE9DB9' },
  { key: 'tree',   text: '长成一棵大树',   bg: '#F4D36B' },
  { key: 'book',   text: '住进故事里',     bg: '#F2C24B' },
  { key: 'song',   text: '留在歌里',       bg: '#7FCCB0' },
  { key: 'food',   text: '藏在饺子的味道里', bg: '#F1D9A0' },
  { key: 'wind',   text: '变成一阵风',     bg: '#B8A5E2' },
  { key: 'heart',  text: '住在你心里',     bg: '#F7B9C8' },
];

const SHOTS = [
  { t0: b(0),  t1: b(8),  name: 'town' },      // night town, a lit window, the spark in the sky
  { t0: b(8),  t1: b(16), name: 'photo' },     // she looks at grandma's photo, then up at the sky
  { t0: b(16), t1: b(24), name: 'write' },     // writes the question
  { t0: b(24), t1: b(28), name: 'fold' },      // folds it into a paper plane
  { t0: b(28), t1: b(32), name: 'throw' },     // throws it out of the window
  { t0: b(32), t1: b(36), name: 'fly' },       // the plane crosses the night sky
  { t0: b(36), t1: b(44), name: 'catch' },     // the spark catches it, reads, thinks … !
  ...ANSWERS.map((a, i) => ({ t0: b(44 + 2 * i), t1: b(46 + 2 * i), name: 'ans', ans: a, i })),
  { t0: b(60), t1: b(64), name: 'reply' },     // the spark writes back
  { t0: b(64), t1: b(68), name: 'back' },      // the plane glides down to her window
  { t0: b(68), t1: b(72), name: 'got' },       // she catches it
  { t0: b(72), t1: b(80), name: 'read' },      // the answer
  { t0: b(80), t1: DUR,   name: 'end' },       // a new star next to the moon
];
const shotAt = t => SHOTS.find(s => t >= s.t0 && t < s.t1) || SHOTS[SHOTS.length - 1];

// chords, one or two per bar
const CHORDS = { F: [53, 57, 60, 65], C: [48, 55, 60, 64], Dm: [50, 57, 62, 65], Bb: [46, 53, 58, 62], Gm: [43, 55, 58, 62], Am: [45, 57, 60, 64], Csus: [48, 55, 60, 65] };
const PROG = ['F', 'C', 'Dm', 'Bb', 'F', 'C', 'Bb', 'Csus', 'F', 'Dm', 'Bb', 'F', 'C', 'Dm', 'Bb', 'Gm', 'C', 'Dm', 'Bb', 'C', 'F', 'F'];

function buildScore() {
  const S = { chord: [], pluck: [], box: [], bass: [], mel: [], kick: [], snap: [], shake: [], glock: [],
              pencil: [], fold: [], whoosh: [], pop: [], ding: [], twinkle: [], tick: [] };
  PROG.forEach((c, bar) => {
    const t = b(bar * 4), end = b(bar * 4 + 4), n = CHORDS[c];
    S.chord.push({ t, end, notes: n, name: c, bar });
    // ukulele-ish strum: down on 1, then a lilting 8th pattern
    const lively = bar >= 11 && bar < 15;
    const pat = bar < 2 ? [0, 2] : bar >= 20 ? [0] : lively ? [0, 1, 1.5, 2, 3, 3.5] : [0, 1.5, 2, 3];
    for (const p of pat) S.pluck.push({ t: b(bar * 4 + p), notes: n, g: lively ? 1 : bar >= 20 ? .7 : .75 });
    // music box arpeggio in the quiet parts
    if (bar < 11 || bar >= 15) for (let k = 0; k < 8; k++) if (bar < 20 || k < 4) S.box.push({ t: b(bar * 4 + k / 2), m: n[[1, 2, 3, 2][k % 4]] + 12, g: bar < 2 ? .5 : .8 });
    if (bar >= 9 && bar < 20) { S.bass.push({ t: b(bar * 4), m: n[0] - 12, d: BEAT * 1.8 }); S.bass.push({ t: b(bar * 4 + 2), m: n[0] - 12 + (lively ? 7 : 0), d: BEAT * 1.8 }); }
    if (lively) for (let k = 0; k < 4; k++) {
      if (k % 2 === 0) S.kick.push({ t: b(bar * 4 + k) }); else S.snap.push({ t: b(bar * 4 + k) });
      S.shake.push({ t: b(bar * 4 + k) }, { t: b(bar * 4 + k + .5) });
    }
  });
  // whistled tune over the montage
  [[72, 74, 72, 69], [67, 69, 67, 64], [65, 67, 69, 72], [70, 69, 67, 65]].forEach((bar, i) =>
    bar.forEach((m, k) => S.mel.push({ t: b(44 + i * 4 + k), m, d: BEAT * .9 })));
  // a gentle echo of it on the glockenspiel for the answer
  [[72, 0], [69, 1], [67, 2], [65, 3], [72, 4.5], [74, 5], [72, 6]].forEach(([m, k]) => S.glock.push({ t: b(72 + k), m }));
  [[77, 0], [76, 1], [72, 2], [69, 4], [72, 5], [77, 6]].forEach(([m, k]) => S.glock.push({ t: b(80 + k), m }));

  // ---- actions
  // she writes the question: one character per half-beat, starting on beat 17
  [...QUESTION].forEach((ch, i) => S.pencil.push({ t: b(17 + i * .66), ch, i, dur: BEAT * .5, who: 'girl' }));
  // the spark's reply appears in the reading shot
  [...ANSWER.join('')].forEach((ch, i) => S.pencil.push({ t: b(73 + i * .45), ch, i, dur: BEAT * .35, who: 'spark' }));
  // scribbling the reply (back of the note)
  for (let k = 0; k < 6; k++) S.pencil.push({ t: b(60.5 + k * .45), dur: BEAT * .35, who: 'scribble' });
  S.fold.push({ t: b(24.5) }, { t: b(25.5) }, { t: b(26.5) }, { t: b(62.5) });
  S.whoosh.push({ t: b(29.8), d: 1.2 }, { t: b(32), d: 2.2 }, { t: b(64), d: 2.3 });
  S.pop.push({ t: b(37.2) }, { t: b(68.6) });
  S.ding.push({ t: b(42.5) });
  ANSWERS.forEach((a, i) => S.tick.push({ t: b(44 + 2 * i), i }));
  S.twinkle.push({ t: b(82) }, { t: b(84) });
  S.glock.push({ t: b(82), m: 84 }, { t: b(82.25), m: 88 }, { t: b(82.5), m: 91 }, { t: b(82.75), m: 96 });
  for (const k in S) S[k].sort((a, c) => a.t - c.t);
  return S;
}
const SCORE = buildScore();
