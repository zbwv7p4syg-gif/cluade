// score.js — the one timeline for the remake. Shots, dialogue (split into syllables), footsteps,
// tears, the hug, the music. audio.js voices every syllable; visuals.js opens the mouths on the
// very same syllables and shows the matching subtitle.

const DUR = 16.0;

// the five shots of the original, cut at the same moments
const SHOTS = [
  { t0: 0.00, t1: 2.07, name: 'wide' },       // 噜妹儿 on the bed, 噜噜 cooking in the kitchen
  { t0: 2.07, t1: 4.13, name: 'sisCU' },      // close-up: 噜妹儿 cries
  { t0: 4.13, t1: 5.47, name: 'broMS' },      // 噜噜 turns round: 嗯？
  { t0: 5.47, t1: 9.07, name: 'walk' },       // wipes his hands, walks over: 怎么了
  { t0: 9.07, t1: 15.07, name: 'hug' },       // 我想你了 / 哈哈哈我也想你呀
  { t0: 15.07, t1: DUR, name: 'end' },
];
const shotAt = t => SHOTS.find(s => t >= s.t0 && t < s.t1) || SHOTS[SHOTS.length - 1];

const LINES = [
  { who: 'sis', text: '噜噜噜噜噜噜', t0: 0.35, t1: 1.95, mood: 'whine' },
  { who: 'sis', text: '噜噜噜噜噜噜', t0: 2.25, t1: 4.00, mood: 'cry' },
  { who: 'bro', text: '嗯？', t0: 4.55, t1: 5.20, mood: 'ask' },
  { who: 'bro', text: '怎么了', t0: 7.85, t1: 8.75, mood: 'gentle' },
  { who: 'sis', text: '我想你了', t0: 10.0, t1: 11.2, mood: 'shy' },
  { who: 'bro', text: '哈哈哈我也想你呀', t0: 12.0, t1: 14.6, mood: 'laugh' },
];
const VOWEL = { '噜': 'u', '哈': 'a', '嗯': 'n', '我': 'o', '想': 'a', '你': 'i', '了': 'e', '也': 'e', '呀': 'a', '怎': 'e', '么': 'e' };

function buildScore() {
  const S = { syl: [], step: [], tear: [], hug: [], hop: [], turn: [], chord: [], box: [], glock: [] };
  // ---- dialogue -> syllables (evenly spread, with a little rhythm per mood)
  for (const L of LINES) {
    const ch = [...L.text].filter(c => VOWEL[c]), n = ch.length, span = L.t1 - L.t0;
    ch.forEach((c, i) => {
      let t = L.t0 + span * i / n, dur = Math.min(0.24, span / n * 0.85);
      if (L.mood === 'laugh' && i < 3) { t = L.t0 + i * 0.2; dur = 0.13; }                 // ha-ha-ha, quick
      if (L.mood === 'laugh' && i >= 3) { t = L.t0 + 0.75 + (span - 0.75) * (i - 3) / (n - 3); dur = Math.min(0.24, (span - 0.75) / (n - 3) * 0.85); }
      const base = L.who === 'sis' ? 540 : 300;
      let f0 = base, f1 = base;
      if (L.mood === 'whine') { f0 = base * (1.05 + 0.08 * Math.sin(i * 1.3)); f1 = f0 * 0.9; }
      if (L.mood === 'cry') { f0 = base * (1.12 - i * 0.03); f1 = f0 * 0.82; }
      if (L.mood === 'ask') { f0 = base * 0.95; f1 = base * 1.45; dur = 0.45; }
      if (L.mood === 'gentle') { f0 = base * (1.05 - i * 0.04); f1 = f0 * (i === n - 1 ? 1.15 : 0.97); }
      if (L.mood === 'shy') { f0 = base * (1.0 + (i === 1 ? 0.12 : 0)); f1 = f0 * (i === n - 1 ? 0.85 : 1.0); }
      if (L.mood === 'laugh') { f0 = base * (i < 3 ? 1.35 - i * 0.05 : 1.1 + 0.1 * Math.sin(i)); f1 = f0 * (i === n - 1 ? 1.2 : 0.95); }
      S.syl.push({ t: +t.toFixed(4), dur: +dur.toFixed(4), who: L.who, v: VOWEL[c], f0, f1, cry: L.mood === 'cry' || L.mood === 'whine', line: L });
    });
  }
  // ---- action
  S.turn.push({ t: 4.35 });                                         // 噜噜 turns from the stove
  S.hop.push({ t: 5.75, who: 'bro' });                              // hops off his stool
  for (let t = 6.25; t < 8.45; t += 0.28) S.step.push({ t: +t.toFixed(3) });
  S.tear.push({ t: 2.85 }, { t: 3.55 });
  S.hop.push({ t: 10.55, who: 'sis' });                             // jumps into his arms
  S.hug.push({ t: 11.0 });
  // ---- music: chords change on the cuts, like a film score
  const CH = [[0, 'Dm'], [2.07, 'Bb'], [4.13, 'Gm'], [5.47, 'C'], [7.27, 'F'], [9.07, 'F'], [11.0, 'Bb'], [12.9, 'C'], [14.2, 'F']];
  const NOTES = { Dm: [62, 65, 69], Bb: [58, 62, 65], Gm: [55, 58, 62], C: [60, 64, 67], F: [60, 65, 69] };
  CH.forEach(([t, c], i) => {
    const end = i + 1 < CH.length ? CH[i + 1][0] : DUR;
    S.chord.push({ t, end, notes: NOTES[c], name: c });
    for (let k = 0; t + k / 3 < end - 0.05; k++) S.box.push({ t: +(t + k / 3).toFixed(4), m: NOTES[c][[0, 1, 2, 1][k % 4]] + 12, g: t >= 9.07 ? 0.9 : 0.6 });
  });
  // a little glockenspiel tune while they laugh
  [[12.0, 81], [12.2, 79], [12.4, 77], [12.75, 81], [13.1, 84], [13.45, 81], [13.8, 79], [14.2, 77], [14.5, 81]].forEach(([t, m]) => S.glock.push({ t, m }));
  for (const k in S) S[k].sort((a, b) => a.t - b.t);
  return S;
}
const SCORE = buildScore();
// the syllable one character is voicing at time t (for mouth shapes)
function speaking(who, t) {
  for (const s of SCORE.syl) if (s.who === who && t >= s.t && t < s.t + s.dur) return { s, k: Math.sin(Math.PI * (t - s.t) / s.dur) };
  return null;
}
