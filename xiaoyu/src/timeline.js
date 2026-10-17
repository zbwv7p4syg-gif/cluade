// timeline.js — when everything happens in 小宇 · 像素 MV. One shot per sung line, cut on the line times of the
// user's .lrc (the words themselves are only read at render time, from build/lyrics.js, and never stored here).

const DUR = BEATMAP.duration;

const SHOTS = [
  { t0: 0.00, name: 'title' },          // a seaside town in the morning; the title; he walks along the sea
  { t0: 10.3, name: 'surprise' },       // a gust carries a sun hat right onto his head
  { t0: 15.7, name: 'meet' },           // she runs after her hat; they meet and time slows down
  { t0: 20.9, name: 'eyes' },           // close-up: her clear eyes, with the sky and him reflected in them
  { t0: 27.3, name: 'dream' },          // he sleeps; she is in his dream
  { t0: 31.5, name: 'becloud' },        // on a hill he turns into a little cloud and floats up
  { t0: 36.9, name: 'drift' },          // over her garden the wind won't let the cloud stay
  { t0: 42.5, name: 'drizzle' },        // the cloud tries hard and a gentle rain begins
  { t0: 48.3, name: 'bloom' },          // rain on the heart-shaped field in her heart; it turns green and flowers
  { t0: 53.3, name: 'future' },         // a horizon of foggy question marks; they shrug and laugh
  { t0: 58.7, name: 'fun' },            // ice cream and a beach ball by the waves
  { t0: 63.9, name: 'ending' },         // a big picture book of their story; the last page is blank
  { t0: 69.5, name: 'missing' },        // alone at night, the stars join up into her
  { t0: 74.7, name: 'game' },           // an arcade game with hearts for lives; he pulls the plug
  { t0: 80.3, name: 'sincere' },        // he holds out a real, beating heart
  { t0: 85.3, name: 'unsaid' },         // a speech bubble with a padlock; he zips his lips
  { t0: 90.5, name: 'quiz' },           // the fear: she falls into a giant multiple-choice question
  { t0: 95.7, name: 'selfish' },        // his dark shadow reaches for her; he holds it back
  { t0: 102.3, name: 'hide' },          // night falls and swallows the shadow
  { t0: 106.5, name: 'beboat' },        // he becomes a little boat with a heart on its sail
  { t0: 111.9, name: 'lake' },          // her heart-shaped lake from above: every pier is closed
  { t0: 117.3, name: 'search' },        // a telescope; far away a lighthouse and a harbour
  { t0: 123.3, name: 'harbor' },        // he sails for the harbour lights, hoping
  { t0: 128.25, name: 'interlude' },    // sunset guitar on the beach, lanterns, then fireworks
  { t0: 149.5, name: 'ride' },          // riding one bicycle along the coast road at night
  { t0: 154.9, name: 'wheel' },         // the Ferris wheel
  { t0: 159.7, name: 'cinema' },        // a beach cinema says END; they look at each other instead
  { t0: 165.7, name: 'plane' },         // a paper plane with a heart flies from his window to hers
  { t0: 170.3, name: 'onward' },        // a windy morning; he walks on, whistling
  { t0: 176.3, name: 'everyday' },      // Monday to Sunday at her door, a different gift each day
  { t0: 181.1, name: 'closebook' },     // he shuts the picture book and takes her hand
  { t0: 186.7, name: 'together' },      // sunset on the pier, hand in hand
  { t0: 191.9, name: 'doubt' },         // she lets go and steps back; his hand stays in the air
  { t0: 200.1, name: 'leave' },         // he smiles, waves, and rows away quietly
  { t0: 207.35, name: 'end' },          // night sea: a tiny lantern on the horizon; the title again
];
SHOTS.forEach((s, i) => { s.t1 = i + 1 < SHOTS.length ? SHOTS[i + 1].t0 : DUR; });
const shotIndex = t => { let i = 0; while (i + 1 < SHOTS.length && t >= SHOTS[i + 1].t0) i++; return i; };

// beat helpers on the fitted grid
const beatPos = t => (t - BEATMAP.phase) / BEATMAP.beat;
const beatPhase = t => { const p = beatPos(t) % 1; return p < 0 ? p + 1 : p; };
const lastKick = t => { let k = -1e9; for (const x of BEATMAP.kicks) { if (x > t) break; k = x; } return k; };
const kicksIn = (a, b) => BEATMAP.kicks.filter(x => x >= a && x < b);
const kickPulse = (t, k = 6) => Math.exp(-Math.max(0, t - lastKick(t)) * k);
const envAt = (band, t) => { const e = BEATMAP.env[band], i = Math.max(0, Math.min(e.length - 1, t * 30)), j = Math.floor(i), f = i - j; return e[j] * (1 - f) + (e[Math.min(e.length - 1, j + 1)] ?? 0) * f; };
// is a syllable being sung right now? (used to move a speaking mouth)
const singing = t => { const w = BEATMAP.words; let lo = 0, hi = w.length - 1, k = -1; while (lo <= hi) { const m = (lo + hi) >> 1; if (w[m] <= t) { k = m; lo = m + 1; } else hi = m - 1; } return k >= 0 && t - w[k] < .16; };
