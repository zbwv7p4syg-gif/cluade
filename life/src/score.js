// score.js — the single source of truth for timing.
// Both the synthesizer (audio.js) and the picture (visuals.js) read these event lists,
// so every flash, word and step lands on exactly the sample where its sound starts.
//
// 100 BPM: one beat = 0.6 s = exactly 18 frames at 30 fps; one bar = 2.4 s; 25 bars = 60 s.

const BPM = 100;
const BEAT = 60 / BPM;          // 0.6 s
const STEP = BEAT / 4;          // 16th note, 0.15 s
const BAR = BEAT * 4;           // 2.4 s
const DUR = 60;
const bt = (bar, beat = 0, step = 0) => +(((bar * 4 + beat) * BEAT) + step * STEP).toFixed(6);

// Sections (bars): 问 → 童年 → 青春 → 低谷 → 答案 → 传承 → 尾声
const SECTIONS = [
  { name: 'question', bar: 0 }, { name: 'childhood', bar: 4 }, { name: 'youth', bar: 8 },
  { name: 'valley', bar: 12 }, { name: 'answer', bar: 16 }, { name: 'legacy', bar: 20 }, { name: 'outro', bar: 24 },
];

const CHORD = {
  Am: [57, 60, 64], F: [53, 57, 60], C: [48, 52, 55, 60], G: [55, 59, 62], Em: [52, 55, 59], Dm: [50, 53, 57], E: [52, 56, 59],
};
const ROOT = { Am: 33, F: 29, C: 36, G: 31, Em: 28, Dm: 38, E: 28 };
const BARS = ['Am', 'F', 'C', 'G', 'C', 'G', 'Am', 'F', 'F', 'G', 'Em', 'Am', 'Dm', 'Am', 'F', 'E', 'F', 'G', 'Em', 'Am', 'F', 'G', 'C', 'C', 'C'];
// lead hook, in 8th notes: [eighth, midi, length in 8ths]
const HOOK = {
  F: [[0, 69, 2], [2, 72, 2], [4, 77, 3], [7, 76, 1]],
  G: [[0, 74, 2], [2, 71, 2], [4, 74, 2], [6, 79, 2]],
  Em: [[0, 76, 3], [3, 74, 1], [4, 71, 2], [6, 67, 2]],
  Am: [[0, 69, 4], [4, 72, 2], [6, 71, 2]],
};
const PENTA = [81, 84, 86, 88, 91, 93, 96];

// ---------------------------------------------------------------- words
// Each entry: time, text, style. Visuals draw them; the matching note is in the score below.
const WORDS = {
  // 问：人 生 的 意 义 — one character per beat
  title: [['人', bt(0, 2)], ['生', bt(0, 3)], ['的', bt(1, 0)], ['意', bt(1, 1)], ['义', bt(1, 2)]],
  titleQ: bt(2, 0),                                   // 是什么？
  birthLine: { text: '从一次心跳开始', t0: bt(3, 0), step: BEAT / 2 },
  childhood: [[bt(4, 0), '第一次', bt(4, 2), '睁开眼'], [bt(5, 0), '第一次', bt(5, 2), '叫出妈妈'],
              [bt(6, 0), '第一次', bt(6, 2), '摔倒'], [bt(7, 0), '然后', bt(7, 2), '站起来']],
  youth: ['奔跑', '追风', '去爱', '去闯', '熬过的夜', '走过的路', '唱过的歌', '流过的汗',
          '我们', '都曾', '那样', '热烈', '用力地', '活着', '像', '火焰'].map((w, i) => [bt(8, i), w]),
  valley: [[bt(12, 0), '也会迷路'], [bt(13, 0), '也会失去'], [bt(14, 0), '意义……'], [bt(14, 2), '在哪里？']],
  valleyTurn: { text: '直到有一天', t0: bt(15, 0), step: BEAT / 2 },
  answer: ['意义，是你爱过的人', '是你认真做过的事', '是你熬过的黑夜', '和你留下的光'].map((s, i) => ({ text: s, t0: bt(16 + i, 0), step: BEAT / 2 })),
  legacy: [{ text: '意义不是被找到的，', t0: bt(20, 0), step: BEAT / 2 }, { text: '而是被活出来的。', t0: bt(22, 0), step: BEAT / 2 }],
  outro: { title: bt(24, 1), sub: bt(24, 2) },
};
// times of each character of a typed line (one per 8th note)
const charTimes = l => [...l.text].map((c, i) => +(l.t0 + i * l.step).toFixed(6));

// ---------------------------------------------------------------- the score
function buildScore() {
  const S = { kick: [], heart: [], snare: [], hat: [], ohat: [], bass: [], piano: [], pad: [], lead: [], bell: [], crash: [], drip: [], riser: [], boom: [], node: [] };
  const add = (k, e) => S[k].push(e);
  let seed = 7; const rnd = () => (seed = (seed * 16807) % 2147483647) / 2147483647;

  for (let b = 0; b < 25; b++) {
    const ch = BARS[b], notes = CHORD[ch], root = ROOT[ch], t0 = bt(b);
    const sec = b < 4 ? 0 : b < 8 ? 1 : b < 12 ? 2 : b < 16 ? 3 : b < 20 ? 4 : b < 24 ? 5 : 6;

    // pad: the air under everything (none in the blackout beat before the answer)
    if (b < 24) add('pad', { t: t0, dur: sec === 3 && b === 15 ? BEAT * 3 : BAR, notes, g: [0.5, 0.35, 0.3, 0.45, 0.4, 0.5][sec] });

    // ---- 问 (bars 0–3): a heartbeat on beats 1 and 3, soft piano
    if (sec === 0) {
      for (const beat of [0, 2]) { add('heart', { t: bt(b, beat), strong: true }); add('heart', { t: bt(b, beat, 1), strong: false }); }
      if (b >= 1) add('piano', { t: t0, notes: notes.map(n => n + 12), dur: 2.2, g: 0.45 });
    }
    // ---- 童年 (bars 4–7): a soft footstep kick on every beat, shaker 8ths, music-box arpeggio
    if (sec === 1) {
      for (let beat = 0; beat < 4; beat++) add('kick', { t: bt(b, beat), g: 0.55, soft: true });
      for (const beat of [1, 3]) add('snare', { t: bt(b, beat), g: 0.35 });
      for (let e = 0; e < 8; e++) add('hat', { t: bt(b, 0, e * 2), g: e % 2 ? 0.35 : 0.2 });
      for (let e = 0; e < 8; e++) add('piano', { t: bt(b, 0, e * 2), notes: [notes[[0, 1, 2, 1][e % 4]] + 24], dur: 0.8, g: 0.3 });
      add('bass', { t: t0, m: root + 12, dur: BEAT * 1.8, g: 0.6 }); add('bass', { t: bt(b, 2), m: root + 12, dur: BEAT * 1.8, g: 0.6 });
    }
    // ---- 青春 (bars 8–11): four-on-the-floor, a word on every kick
    if (sec === 2) {
      if (b === 8) add('crash', { t: t0, g: 0.9 });
      for (let beat = 0; beat < 4; beat++) add('kick', { t: bt(b, beat), g: 1 });
      for (const beat of [1, 3]) add('snare', { t: bt(b, beat), g: 0.85 });
      for (let s = 0; s < 16; s++) (s % 4 === 2 ? add('ohat', { t: bt(b, 0, s), g: 0.6 }) : add('hat', { t: bt(b, 0, s), g: s % 2 ? 0.28 : 0.18 }));
      for (let e = 0; e < 8; e++) add('bass', { t: bt(b, 0, e * 2), m: root + (e % 2 ? 24 : 12), dur: STEP * 1.7, g: 0.8 });
      for (const [e, m, l] of HOOK[ch]) add('lead', { t: bt(b, 0, e * 2), m, dur: l * STEP * 2 * 0.92, g: 0.9 });
      for (const beat of [0.5, 1.5, 2.5, 3.5]) add('piano', { t: bt(b, beat), notes: notes.map(n => n + 12), dur: 0.25, g: 0.35 });
    }
    // ---- 低谷 (bars 12–15): half-time, raindrops on 8ths, a build, then one beat of silence
    if (sec === 3) {
      if (b < 15) { add('kick', { t: t0, g: 0.8 }); add('snare', { t: bt(b, 2), g: 0.55 }); }
      if (b === 14) add('kick', { t: bt(b, 2, 2), g: 0.6 });
      if (b < 15) add('piano', { t: t0, notes: notes.map(n => n + 12), dur: 2.3, g: 0.4 });
      add('bass', { t: t0, m: root + 12, dur: b === 15 ? BEAT * 2.8 : BAR * 0.95, g: 0.55 });
      const drips = b === 15 ? 6 : 8;                 // drips stop before the silent last beat
      for (let e = 0; e < drips; e++) if (b >= 14 || e % 2 === 0 || rnd() > 0.4)
        add('drip', { t: bt(b, 0, e * 2), m: PENTA[Math.floor(rnd() * PENTA.length)], x: rnd(), g: 0.5 });
      if (b === 15) {
        for (let s = 0; s < 12; s++) add('snare', { t: bt(b, 0, s), g: 0.2 + s * 0.05, roll: true });   // snare roll, 16ths
        add('riser', { t: bt(14), dur: BAR + BEAT * 3, g: 0.8 });
      }
      for (const w of WORDS.valley) if (w[0] >= t0 && w[0] < t0 + BAR) add('bell', { t: w[0], m: 76, g: 0.35 });
    }
    // ---- 答案 (bars 16–19): the full chorus, fireworks on beats 1 and 3
    if (sec === 4) {
      add('crash', { t: t0, g: 1 });
      for (let beat = 0; beat < 4; beat++) add('kick', { t: bt(b, beat), g: 1 });
      for (const beat of [0, 2]) add('boom', { t: bt(b, beat), x: rnd(), y: rnd(), hue: rnd() });
      for (const beat of [1, 3]) add('snare', { t: bt(b, beat), g: 0.9 });
      for (let s = 0; s < 16; s++) (s % 4 === 2 ? add('ohat', { t: bt(b, 0, s), g: 0.55 }) : add('hat', { t: bt(b, 0, s), g: 0.22 }));
      for (let e = 0; e < 8; e++) add('bass', { t: bt(b, 0, e * 2), m: root + (e % 2 ? 24 : 12), dur: STEP * 1.7, g: 0.85 });
      for (const [e, m, l] of HOOK[ch]) add('lead', { t: bt(b, 0, e * 2), m: m + 12, dur: l * STEP * 2 * 0.92, g: 0.8 });
      // piano arpeggio on 8ths = the rhythm the words are typed in
      for (let e = 0; e < 8; e++) add('piano', { t: bt(b, 0, e * 2), notes: [notes[[0, 1, 2, 1][e % 4]] + 24], dur: 0.6, g: 0.3 });
    }
    // ---- 传承 (bars 20–23): drums fall away; a new light (and a bell) on every beat
    if (sec === 5) {
      if (b < 22) { add('kick', { t: t0, g: 0.6 }); add('kick', { t: bt(b, 2), g: 0.5 }); }
      add('piano', { t: t0, notes: notes.map(n => n + 12), dur: 2.3, g: 0.45 });
      for (let e = 0; e < 8; e++) add('piano', { t: bt(b, 0, e * 2), notes: [notes[[0, 1, 2, 1][e % 4]] + 24], dur: 0.7, g: 0.22 });
      add('bass', { t: t0, m: root + 12, dur: BAR * 0.95, g: 0.5 });
      for (let beat = 0; beat < 4; beat++) { const i = (b - 20) * 4 + beat; add('node', { t: bt(b, beat), i }); add('bell', { t: bt(b, beat), m: PENTA[i % 7] - 12 + (i >= 7 ? 12 : 0), g: 0.3 }); }
    }
    // ---- 尾声 (bar 24): one last heartbeat, then the title
    if (sec === 6) {
      add('heart', { t: t0, strong: true }); add('heart', { t: bt(b, 0, 1), strong: false });
      add('piano', { t: t0, notes: [48, 55, 60, 64, 67, 72], dur: 3.2, g: 0.5 });
      add('pad', { t: t0, dur: 2.2, notes: [48, 55, 60, 64], g: 0.4 });
      add('bell', { t: WORDS.outro.title, m: 84, g: 0.4 }); add('bell', { t: WORDS.outro.sub, m: 88, g: 0.3 });
    }
  }
  // word bells for 问 and 童年
  WORDS.title.forEach(([c, t], i) => add('bell', { t, m: [69, 72, 76, 81, 84][i], g: 0.45 }));
  add('piano', { t: WORDS.titleQ, notes: [45, 57, 64], dur: 2, g: 0.5 });
  WORDS.childhood.forEach(([ta, a, tb, b]) => { add('bell', { t: ta, m: 84, g: 0.25 }); add('bell', { t: tb, m: 88, g: 0.4 }); });
  for (const k in S) S[k].sort((a, b) => a.t - b.t);
  return S;
}
const SCORE = buildScore();
