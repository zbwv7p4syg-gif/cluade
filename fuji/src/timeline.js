// timeline.js — when everything happens, measured from the uploaded clip (see analyze.py):
// the vocal enters at 22.25 s and each sung line starts ~4.3 s after the last (one phrase per bar
// at ~56 BPM). Shots cut on those phrase starts; the intro is split on the same 4.28 s grid.
// No lyrics are stored here — the captions are original lines.

const DUR = 54.13;
const PHRASE = 4.28;                       // one sung line ≈ one bar
const LINE_ONSETS = [22.25, 26.53, 30.75, 35.90, 40.48, 44.76, 49.60];
const SHOTS = [
  { t0: 0.00, name: 'fuji' },              // Mount Fuji at night, the title
  { t0: 5.13, name: 'tilt' },              // the camera comes down to a rainy street
  { t0: 9.41, name: 'alone' },             // 她, alone under a street lamp
  { t0: 13.69, name: 'car' },              // headlights: 他 drives up
  { t0: 17.97, name: 'walk' },             // 他 gets out and walks over
  { t0: 22.25, name: 'snowrain' },         // rain that falls like snow; she is crying
  { t0: 26.53, name: 'coat' },             // 他 puts his worn coat over her shoulders
  { t0: 30.75, name: 'memory' },           // he moved away for work, but still can't let go
  { t0: 35.90, name: 'drive' },            // he drives her home
  { t0: 40.48, name: 'flowers' },          // the flowers he no longer gives; a heart on the misted glass
  { t0: 44.76, name: 'petals' },           // petals turn into snow; Fuji at the end of the road
  { t0: 49.60, name: 'home' },             // she goes inside; he lets go
];
SHOTS.forEach((s, i) => s.t1 = i + 1 < SHOTS.length ? SHOTS[i + 1].t0 : DUR);
const shotIndex = t => { let i = 0; while (i + 1 < SHOTS.length && t >= SHOTS[i + 1].t0) i++; return i; };

// one quiet "beat" inside each phrase (wipers, light pulses): a quarter of a phrase
const pulseBeat = t => { const p = ((t - LINE_ONSETS[0]) / (PHRASE / 4)) % 1; return p < 0 ? p + 1 : p; };

const CAPTIONS = [
  [22.45, 26.30, '那天的雨，下得像雪'],
  [26.70, 30.55, '把穿旧的外套，披在你身上'],
  [30.95, 35.60, '走得再远，还是会想起你'],
  [36.10, 40.25, '今天，再送你回家一次'],
  [40.65, 42.55, '原谅我，不再送花了'],
  [42.75, 44.55, '伤口，总会慢慢结痂'],
  [44.95, 49.35, '心里的花，就让它安静落下'],
  [49.80, 53.40, '爱过，就好好说再见'],
];
