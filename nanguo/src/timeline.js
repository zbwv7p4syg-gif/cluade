// timeline.js — when everything happens in 我不难过 · 像素 MV. One shot per sung line, cut on the line times of the
// user's .lrc (the words themselves are only read at render time, from build/lyrics.js, and never stored here).
// v is the palette of the retelling: 0 the rainy night, 1 dusk (the second verse, remembered), 2 before dawn.

const DUR = BEATMAP.duration;

const SHOTS = [
  { t0: 0.00, name: 'title' },                 // a rainy night street; she walks to his door with her umbrella
  { t0: 21.0, name: 'door' },                  // she knocks; the door opens
  { t0: 24.2, name: 'silence' },               // the two of them, and nothing but "…"
  { t0: 27.0, name: 'wait' },                  // waiting under the lamp while the moon crosses the sky and windows go dark
  { t0: 31.1, name: 'clock' },                 // a clock that won't stop; she sits on the step
  { t0: 36.1, name: 'tell', v: 0 },            // he finally speaks
  { t0: 39.6, name: 'gentle', v: 0 },          // the girl he talks about, soft and glowing
  { t0: 42.3, name: 'hands', v: 0 },           // he still holds her hand
  { t0: 46.2, name: 'heart', v: 0 },           // inside his heart there is someone else now
  { t0: 51.3, name: 'understand', v: 0 },      // in her room by the rainy window, a photo of them; she nods
  { t0: 58.4, name: 'notthere', v: 0 },        // alone in a spotlight, an outline where he used to stand
  { t0: 61.3, name: 'lonely', v: 0 },          // split screen: him alone with his phone, her far away
  { t0: 66.9, name: 'dontlook', v: 0 },        // he looks at her; she turns away
  { t0: 69.1, name: 'loved', v: 0, full: 1 },  // his bubble: a heart with a plaster; she raises her hand
  { t0: 73.1, name: 'fine', v: 0 },            // a big bright smile
  { t0: 76.6, name: 'tears', v: 0 },           // close-up: the smile stays, the tears come anyway
  { t0: 79.5, name: 'why', v: 0 },             // question marks
  { t0: 80.7, name: 'leave', v: 0 },           // she walks away down the street
  { t0: 85.4, name: 'free', v: 0 },            // the wind takes her umbrella, the clouds open
  { t0: 88.4, name: 'memories', v: 0 },        // polaroids float around her
  { t0: 91.3, name: 'shadow', v: 0 },          // her days, and his shadow in every one of them
  { t0: 96.8, name: 'strong', v: 0 },          // standing firm in the wind
  { t0: 101.7, name: 'alone', v: 0 },          // a tiny figure under a huge sky
  { t0: 103.1, name: 'lantern', v: 0 },        // she lets a heart-shaped lantern go
  { t0: 110.2, name: 'interlude' },            // her window: days pass; she picks up the photo and we fall into it
  { t0: 125.5, name: 'tell', v: 1 },
  { t0: 128.4, name: 'gentle', v: 1 },
  { t0: 131.3, name: 'hands', v: 1 },
  { t0: 135.0, name: 'heart', v: 1 },
  { t0: 139.4, name: 'understand', v: 1 },
  { t0: 146.8, name: 'notthere', v: 1 },
  { t0: 151.4, name: 'lonely', v: 1 },
  { t0: 155.3, name: 'dontlook', v: 1, bubbleAt: 2.4 },
  { t0: 160.2, name: 'loved', v: 1 },
  { t0: 161.4, name: 'fine', v: 1 },
  { t0: 165.0, name: 'tears', v: 1 },
  { t0: 167.9, name: 'why', v: 1 },
  { t0: 169.2, name: 'leave', v: 1 },
  { t0: 173.7, name: 'free', v: 1 },
  { t0: 176.9, name: 'memories', v: 1 },
  { t0: 179.9, name: 'shadow', v: 1 },
  { t0: 185.2, name: 'strong', v: 1 },
  { t0: 190.2, name: 'alone', v: 1 },
  { t0: 191.7, name: 'lantern', v: 1, release: 3.6 },
  { t0: 199.9, name: 'hug' },                  // bridge: a warm memory of holding each other
  { t0: 203.4, name: 'touched' },              // the glow between them
  { t0: 205.0, name: 'chest' },                // she keeps it close to her heart
  { t0: 207.4, name: 'notyourfault' },         // he hangs his head; she shakes hers
  { t0: 211.1, name: 'roadend' },              // the road ends at the sea
  { t0: 212.5, name: 'wind' },                 // right and wrong blow away on the wind
  { t0: 214.9, name: 'happy' },                // a bright day on her bicycle
  { t0: 222.9, name: 'understand', v: 2 },
  { t0: 229.8, name: 'notthere', v: 2 },
  { t0: 234.5, name: 'lonely', v: 2 },
  { t0: 238.2, name: 'dontlook', v: 2, bubbleAt: 2.5 },
  { t0: 243.2, name: 'loved', v: 2 },
  { t0: 244.8, name: 'fine', v: 2 },
  { t0: 248.2, name: 'tears', v: 2 },
  { t0: 250.9, name: 'why', v: 2 },
  { t0: 252.4, name: 'shh' },                  // he starts to say "maybe…"; she puts a finger to her lips
  { t0: 256.1, name: 'fork' },                 // a fork in the road at dawn
  { t0: 259.7, name: 'split' },                // they walk apart; the red thread snaps
  { t0: 262.8, name: 'blessing' },             // she sees him with the other girl, and smiles
  { t0: 265.0, name: 'drag' },                 // calendar pages and clock hands, round and round, until she stops them
  { t0: 268.4, name: 'letgo' },                // the hands let go; she steps away
  { t0: 273.1, name: 'forward' },              // she walks on toward the brightening sky
  { t0: 278.2, name: 'release' },              // sunrise: her scarf flies off with the birds
  { t0: 282.6, name: 'end' },                  // morning; she walks into the distance; the title again
];
SHOTS.forEach((s, i) => { s.t1 = i + 1 < SHOTS.length ? SHOTS[i + 1].t0 : DUR; s.v = s.v || 0; });
const shotIndex = t => { let i = 0; while (i + 1 < SHOTS.length && t >= SHOTS[i + 1].t0) i++; return i; };

// beat helpers on the fitted grid (the analysis finds 128 BPM, i.e. the ballad's 64 BPM in half-beats)
const beatPos = t => (t - BEATMAP.phase) / BEATMAP.beat;
const beatPhase = t => { const p = (beatPos(t) / 2) % 1; return p < 0 ? p + 1 : p; };
const lastKick = t => { let k = -1e9; for (const x of BEATMAP.kicks) { if (x > t) break; k = x; } return k; };
const kickPulse = (t, k = 6) => Math.exp(-Math.max(0, t - lastKick(t)) * k);
const envAt = (band, t) => { const e = BEATMAP.env[band], i = Math.max(0, Math.min(e.length - 1, t * 30)), j = Math.floor(i), f = i - j; return e[j] * (1 - f) + (e[Math.min(e.length - 1, j + 1)] ?? 0) * f; };
// is a syllable being sung right now? (used to move a speaking mouth)
const singing = t => { const w = BEATMAP.words; let lo = 0, hi = w.length - 1, k = -1; while (lo <= hi) { const m = (lo + hi) >> 1; if (w[m] <= t) { k = m; lo = m + 1; } else hi = m - 1; } return k >= 0 && t - w[k] < .16; };
