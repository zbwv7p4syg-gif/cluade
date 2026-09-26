// score.js — the one timeline. The synthesizer (audio.js) plays these events and the
// picture (visuals.js) reacts to the very same events, so every jump lands on its kick.
//
// 128 BPM, F minor, 32 bars = 60 s.
//   bars  0–3   突破前  muffled kick through a wall; Claude Code terminal cracks on the beat
//   bars  4–7   突破    the wall shatters — full house groove
//   bars  8–11  平静    drums out: pads, piano, phone lights
//   bars 12–15  蓄力    snare roll accelerates, riser, 3-2-1, one beat of silence
//   bars 16–23  燃 1    the drop: everyone jumps on every beat
//   bars 24–29  燃 2    bigger: flames, Clawd crowd-surfs
//   bars 30–31  终      last hit, title

const BPM = 128;
const BEAT = 60 / BPM;          // 0.46875 s
const STEP = BEAT / 4;
const BAR = BEAT * 4;           // 1.875 s
const DUR = 60;
const bt = (bar, beat = 0, step = 0) => +(((bar * 4 + beat) * BEAT) + step * STEP).toFixed(6);

const PROG = ['Fm', 'Db', 'Ab', 'Eb'];
const chordAt = b => PROG[b % 4];
const CHORD = { Fm: [65, 68, 72], Db: [61, 65, 68], Ab: [60, 63, 68], Eb: [58, 63, 67] };
const ROOT = { Fm: 41, Db: 37, Ab: 44, Eb: 39 };
// drop hook in 16ths: [step, midi, length in 16ths]
const HOOK = {
  Fm: [[0, 72, 2], [3, 75, 2], [6, 77, 2], [8, 80, 2], [10, 77, 2], [12, 75, 2], [14, 72, 2]],
  Db: [[0, 73, 2], [3, 77, 2], [6, 80, 2], [8, 82, 2], [10, 80, 2], [12, 77, 2], [14, 73, 2]],
  Ab: [[0, 72, 2], [3, 75, 2], [6, 80, 2], [8, 84, 2], [10, 80, 2], [12, 75, 2], [14, 72, 2]],
  Eb: [[0, 70, 2], [3, 74, 2], [6, 79, 2], [8, 82, 2], [10, 79, 2], [12, 75, 2], [14, 74, 2]],
};

// ---------------------------------------------------------------- the terminal (bars 0–3)
const PROMPT = { text: '开一场电音派对，我来当 DJ', t0: bt(0, 0), step: STEP };   // one character per 16th
const TERM_LINES = [
  { t: bt(1, 0), text: '✻ 好的！正在准备派对……', color: '#e8825c' },
  { t: bt(1, 1), text: '  ✓ 音响  就绪', color: '#7ee787' },
  { t: bt(1, 2), text: '  ✓ 灯光  就绪', color: '#7ee787' },
  { t: bt(1, 3), text: '  ✓ 人群  就绪', color: '#7ee787' },
  { t: bt(2, 0), text: '  ⚠ 墙太厚了，音乐传不出去', color: '#f2cc60' },
  { t: bt(2, 2), text: '  → 正在突破……', color: '#e8825c' },
];
const CRACKS = [bt(2, 2), bt(3, 0), bt(3, 2), bt(3, 3)];
const COUNTDOWN = [[bt(15, 0), '3'], [bt(15, 1), '2'], [bt(15, 2), '1']];
const SHOUTS = [[bt(4, 0), bt(5, 0), '突破！'], [bt(16, 0), bt(17, 0), '跳！！'], [bt(24, 0), bt(25, 0), '全场一起！']];
const SURF = { up: bt(25, 3), start: bt(26, 0), end: bt(28, 0) - BEAT, back: bt(28, 0) };

function buildScore() {
  const S = { kick: [], clap: [], hat: [], ohat: [], bass: [], reese: [], saw: [], lead: [], pad: [], piano: [], pluck: [], roll: [], riser: [], pitch: [],
              crash: [], impact: [], shatter: [], crack: [], type: [], blip: [], down: [], roar: [], hiss: [], pyro: [], confetti: [] };
  const add = (k, e) => S[k].push(e);

  for (let b = 0; b < 32; b++) {
    const ch = chordAt(b), notes = CHORD[ch], root = ROOT[ch], t0 = bt(b);
    const intro = b < 4, groove = b >= 4 && b < 8, calm = b >= 8 && b < 12, build = b >= 12 && b < 16;
    const drop = b >= 16 && b < 30, drop2 = b >= 24 && b < 30;

    // ---- kicks
    if (intro || groove) for (let k = 0; k < 4; k++) add('kick', { t: bt(b, k), g: intro ? 0.9 : 0.95, style: 'house' });
    if (b === 13 || b === 14) for (let k = 0; k < 4; k++) add('kick', { t: bt(b, k), g: 0.6 + (b - 13) * 0.15, style: 'build' });
    if (b === 15) for (let k = 0; k < 3; k++) add('kick', { t: bt(b, k), g: 0.85, style: 'build' });
    if (drop) for (let k = 0; k < 4; k++) add('kick', { t: bt(b, k), g: 1, style: 'drop' });
    if (b === 30) add('kick', { t: t0, g: 1, style: 'drop' });

    // ---- claps and hats
    if (groove || drop) for (const k of [1, 3]) add('clap', { t: bt(b, k), g: drop ? 1 : 0.8 });
    if (b >= 2 && b < 8 || drop) for (let s = 0; s < 16; s++) {
      if (s % 4 === 2) add('ohat', { t: bt(b, 0, s), g: drop ? 0.8 : 0.6 });
      else if (b >= 4) add('hat', { t: bt(b, 0, s), g: s % 2 ? 0.3 : 0.18 });
    }
    // ---- bass: house offbeat bass, then a sidechained reese in the drop
    if (b >= 2 && b < 8) for (const s of [2, 6, 10, 14]) add('bass', { t: bt(b, 0, s), m: root, dur: STEP * 1.6, g: 0.9 });
    if (drop) for (let s = 0; s < 16; s += 2) add('reese', { t: bt(b, 0, s), m: root - 12 + (s % 4 === 2 ? 12 : 0), dur: STEP * 1.8, g: 0.9 });
    if (calm || build) add('bass', { t: t0, m: root - 12, dur: BAR * 0.95, g: 0.5, sub: true });

    // ---- harmony
    if (groove) for (let s = 0; s < 16; s += 2) add('pluck', { t: bt(b, 0, s), m: notes[[0, 1, 2, 1][(s / 2) % 4]] + 12, g: 0.4 });
    if (b >= 4 && b < 16) add('pad', { t: t0, notes, dur: BAR, g: calm ? 0.9 : 0.55 });
    if (calm || build) {
      add('piano', { t: t0, notes: notes.map(n => n - 12), dur: BAR, g: 0.7 });
      for (let s = 0; s < 16; s++) add('pluck', { t: bt(b, 0, s), m: notes[s % 3] + 12 + (s >= 8 ? 12 : 0), g: calm ? 0.16 : 0.22, soft: true });
    }
    if (drop) {
      add('saw', { t: t0, notes: [...notes, notes[0] + 12], dur: BAR, g: 1 });
      for (const [s, m, l] of HOOK[ch]) add('lead', { t: bt(b, 0, s), m: m + (drop2 ? 12 : 0), dur: l * STEP * 0.9, g: drop2 ? 0.8 : 0.9 });
    }
    // ---- the build
    if (build) {
      const per = b === 12 ? 4 : b === 13 ? 8 : b === 14 ? 16 : 32;
      const n = b === 15 ? 24 : per;           // bar 15: 32nds for three beats, then silence
      for (let k = 0; k < n; k++) add('roll', { t: +(t0 + k * BAR / per).toFixed(6), g: 0.25 + 0.6 * ((b - 12) * 4 + k * 4 / per) / 16 });
    }
    // ---- drop decorations
    if (drop && b % 4 === 0) { add('crash', { t: t0, g: 1 }); add('hiss', { t: t0, dur: BEAT * 2, g: 0.6 }); add('confetti', { t: t0 }); }
    if (drop2 && b % 2 === 0) add('pyro', { t: t0 });
  }
  // ---- intro story
  [...PROMPT.text].forEach((c, i) => add('type', { t: bt(0, 0, i) }));
  TERM_LINES.forEach((l, i) => add('blip', { t: l.t, m: i === 4 ? 70 : 84 + i * 2, g: 0.5 }));
  CRACKS.forEach(t => add('crack', { t }));
  add('riser', { t: bt(2, 0), dur: BAR * 2, g: 0.7 });
  for (let k = 0; k < 8; k++) add('roll', { t: bt(3, 2, k / 2), g: 0.3 + k * 0.08 });  // 32nds into the break
  // the breakthrough
  add('shatter', { t: bt(4) }); add('impact', { t: bt(4), g: 0.9 }); add('crash', { t: bt(4), g: 0.9 }); add('roar', { t: bt(4), dur: BAR * 2, g: 0.5 });
  // into the calm
  add('down', { t: bt(7, 2), dur: BEAT * 2, g: 0.6 }); add('impact', { t: bt(8), g: 0.5 }); add('crash', { t: bt(8), g: 0.5 });
  // the build: noise riser + pitch riser, countdown blips, one beat of nothing
  add('riser', { t: bt(12), dur: BAR * 4 - BEAT, g: 1 });
  add('pitch', { t: bt(14), dur: BAR * 2 - BEAT, g: 0.7 });
  add('roar', { t: bt(14), dur: BAR * 2 - BEAT, g: 0.35, rise: true });
  COUNTDOWN.forEach(([t], i) => add('blip', { t, m: 84 + i * 5, g: 0.8 }));
  // the drops
  for (const b of [16, 24]) { add('impact', { t: bt(b), g: 1 }); add('roar', { t: bt(b), dur: BAR * 2, g: 0.6 }); }
  for (let s = 12; s < 16; s++) add('roll', { t: bt(23, 0, s), g: 0.8 });   // fill into drop 2
  // the end
  add('impact', { t: bt(30), g: 1 }); add('crash', { t: bt(30), g: 1 }); add('confetti', { t: bt(30) }); add('pyro', { t: bt(30) });
  add('saw', { t: bt(30), notes: [53, 60, 65, 68, 72, 77], dur: BAR * 1.2, g: 1, ring: true });
  add('roar', { t: bt(30), dur: BAR * 1.8, g: 0.55 });
  for (const k in S) S[k].sort((a, b) => a.t - b.t);
  return S;
}
const SCORE = buildScore();
