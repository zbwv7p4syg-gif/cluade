// audio.js — the soundtrack, synthesized from SCORE with Web Audio (no recordings, no samples):
// ukulele-ish plucks, a music box, a whistled tune, soft bass and brushes, a glockenspiel,
// and paper sounds — pencil scratches, folds, whooshes and pops.

const mtof = m => 440 * Math.pow(2, (m - 69) / 12);
function xorshift(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }

async function renderSoundtrack(sr = 44100) {
  const ac = new OfflineAudioContext(2, Math.ceil(sr * DUR), sr);
  const rnd = xorshift(2026);
  const noise = ac.createBuffer(1, sr * 3, sr);
  { const d = noise.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = rnd() * 2 - 1; }
  const master = ac.createGain(); master.gain.value = .8;
  const comp = ac.createDynamicsCompressor(); comp.threshold.value = -16; comp.ratio.value = 3;
  master.connect(comp).connect(ac.destination);
  const verb = ac.createConvolver();
  { const len = sr * 2.4, ir = ac.createBuffer(2, len, sr); for (let c = 0; c < 2; c++) { const d = ir.getChannelData(c); for (let i = 0; i < len; i++) d[i] = (rnd() * 2 - 1) * Math.pow(1 - i / len, 3.2); } verb.buffer = ir; }
  const vg = ac.createGain(); vg.gain.value = .3; verb.connect(vg).connect(master);
  const out = (node, pan = 0, rev = 0) => { const p = ac.createStereoPanner(); p.pan.value = pan; node.connect(p).connect(master); if (rev) { const r = ac.createGain(); r.gain.value = rev; p.connect(r).connect(verb); } };
  const noiseSrc = (t, d) => { const s = ac.createBufferSource(); s.buffer = noise; s.start(t, rnd() * 2, d); return s; };
  const env = (g, t, a, peak, dec) => { g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(peak, t + a); g.gain.setTargetAtTime(0, t + a, dec); };

  // ---- instruments
  function pluckNote(t, m, amp, pan) {
    const f = mtof(m), g = ac.createGain(), lp = ac.createBiquadFilter();
    lp.frequency.setValueAtTime(f * 7, t); lp.frequency.exponentialRampToValueAtTime(f * 1.5, t + .35);
    [['triangle', 1, 1], ['sawtooth', 1.002, .25], ['sine', 2, .2]].forEach(([ty, h, a]) => { const o = ac.createOscillator(), og = ac.createGain(); o.type = ty; o.frequency.value = f * h; og.gain.value = a; o.connect(og).connect(lp); o.start(t); o.stop(t + 1.2); });
    lp.connect(g); env(g, t, .004, amp, .22); out(g, pan, .25);
  }
  function pluck(e) { e.notes.forEach((m, i) => pluckNote(e.t + i * .012, m + 12, .05 * e.g, -.2 + i * .12)); }
  function box(e) {
    const t = e.t, f = mtof(e.m), g = ac.createGain();
    [[1, 1], [3.01, .3], [5.4, .1]].forEach(([h, a]) => { const o = ac.createOscillator(), og = ac.createGain(); o.frequency.value = f * h; og.gain.value = a; o.connect(og).connect(g); o.start(t); o.stop(t + 1.4); });
    env(g, t, .003, .035 * e.g, .35); out(g, (e.m % 5 - 2) / 6, .55);
  }
  function glock(e) {
    const t = e.t, f = mtof(e.m), g = ac.createGain();
    [[1, 1], [2.76, .35], [5.4, .1]].forEach(([h, a]) => { const o = ac.createOscillator(), og = ac.createGain(); o.frequency.value = f * h; og.gain.value = a; o.connect(og).connect(g); o.start(t); o.stop(t + 2); });
    env(g, t, .002, .07, .5); out(g, .15, .55);
  }
  function pad(e) {
    const g = ac.createGain(), lp = ac.createBiquadFilter(); lp.frequency.value = 900;
    for (const m of e.notes) for (const det of [-6, 6]) { const o = ac.createOscillator(); o.type = 'triangle'; o.frequency.value = mtof(m); o.detune.value = det; o.connect(lp); o.start(e.t); o.stop(e.end + .9); }
    lp.connect(g);
    const pk = e.bar >= 11 && e.bar < 15 ? .03 : .04;
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(pk, e.t + .35); g.gain.setValueAtTime(pk, e.end); g.gain.linearRampToValueAtTime(0, e.end + .7);
    out(g, 0, .45);
  }
  function bass(e) {
    const o = ac.createOscillator(), g = ac.createGain(); o.type = 'sine'; o.frequency.value = mtof(e.m);
    const o2 = ac.createOscillator(), g2 = ac.createGain(); o2.type = 'triangle'; o2.frequency.value = mtof(e.m) * 2; g2.gain.value = .15; o2.connect(g2).connect(g);
    o.connect(g); g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(.2, e.t + .01); g.gain.setTargetAtTime(0, e.t + e.d * .6, .08);
    out(g, 0); for (const x of [o, o2]) { x.start(e.t); x.stop(e.t + e.d + .5); }
  }
  function mel(e) {   // a soft whistle: sine with breath and vibrato that grows
    const t = e.t, d = e.d, o = ac.createOscillator(), g = ac.createGain(), f = mtof(e.m + 12);
    o.frequency.setValueAtTime(f * .985, t); o.frequency.exponentialRampToValueAtTime(f, t + .05);
    const v = ac.createOscillator(), vg = ac.createGain(); v.frequency.value = 5.5; vg.gain.setValueAtTime(0, t); vg.gain.linearRampToValueAtTime(14, t + d); v.connect(vg).connect(o.detune);
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(.075, t + .04); g.gain.setValueAtTime(.065, t + d - .08); g.gain.linearRampToValueAtTime(0, t + d);
    o.connect(g); out(g, -.1, .4);
    const n = noiseSrc(t, d), nf = ac.createBiquadFilter(), ng = ac.createGain(); nf.type = 'bandpass'; nf.frequency.value = f; nf.Q.value = 8;
    ng.gain.setValueAtTime(0, t); ng.gain.linearRampToValueAtTime(.05, t + .03); ng.gain.linearRampToValueAtTime(0, t + d); n.connect(nf).connect(ng); out(ng, -.1, .4);
    for (const x of [o, v]) { x.start(t); x.stop(t + d + .05); }
  }
  function kick(e) {
    const o = ac.createOscillator(), g = ac.createGain(); o.frequency.setValueAtTime(130, e.t); o.frequency.exponentialRampToValueAtTime(48, e.t + .12);
    g.gain.setValueAtTime(.45, e.t); g.gain.exponentialRampToValueAtTime(.001, e.t + .28); o.connect(g); out(g); o.start(e.t); o.stop(e.t + .3);
  }
  function snap(e) {   // finger snap / brush
    const n = noiseSrc(e.t, .15), f = ac.createBiquadFilter(), g = ac.createGain(); f.type = 'bandpass'; f.frequency.value = 2400; f.Q.value = 1.4;
    g.gain.setValueAtTime(.22, e.t); g.gain.exponentialRampToValueAtTime(.001, e.t + .12); n.connect(f).connect(g); out(g, .15, .3);
  }
  function shake(e) {
    const n = noiseSrc(e.t, .08), f = ac.createBiquadFilter(), g = ac.createGain(); f.type = 'highpass'; f.frequency.value = 7000;
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(.05, e.t + .02); g.gain.exponentialRampToValueAtTime(.001, e.t + .07); n.connect(f).connect(g); out(g, -.3);
  }
  // ---- paper sounds
  function pencil(e) {   // a scratchy stroke or two per character
    const strokes = e.who === 'scribble' ? 2 : 3;
    for (let k = 0; k < strokes; k++) {
      const t = e.t + k * e.dur / strokes, d = e.dur / strokes * .8;
      const n = noiseSrc(t, d), f = ac.createBiquadFilter(), g = ac.createGain(); f.type = 'bandpass'; f.frequency.value = 3500 + rnd() * 1500; f.Q.value = 1.2;
      const am = ac.createOscillator(), amg = ac.createGain(); am.frequency.value = 35 + rnd() * 20; amg.gain.value = .02; am.connect(amg).connect(g.gain);
      g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(.05, t + .015); g.gain.linearRampToValueAtTime(0, t + d);
      n.connect(f).connect(g); out(g, .25); am.start(t); am.stop(t + d);
    }
  }
  function fold(e) {
    for (let k = 0; k < 2; k++) {
      const t = e.t + k * .07, n = noiseSrc(t, .18), f = ac.createBiquadFilter(), g = ac.createGain(); f.type = 'bandpass'; f.frequency.setValueAtTime(1200, t); f.frequency.exponentialRampToValueAtTime(3500, t + .15); f.Q.value = .8;
      g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(.16, t + .01); g.gain.exponentialRampToValueAtTime(.001, t + .16); n.connect(f).connect(g); out(g, k ? .2 : -.2);
    }
  }
  function whoosh(e) {
    const n = noiseSrc(e.t, e.d), f = ac.createBiquadFilter(), g = ac.createGain(), p = ac.createStereoPanner(); f.type = 'bandpass'; f.Q.value = 2.5;
    f.frequency.setValueAtTime(500, e.t); f.frequency.exponentialRampToValueAtTime(2600, e.t + e.d * .4); f.frequency.exponentialRampToValueAtTime(700, e.t + e.d);
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(.12, e.t + e.d * .35); g.gain.linearRampToValueAtTime(0, e.t + e.d);
    p.pan.setValueAtTime(-.6, e.t); p.pan.linearRampToValueAtTime(.6, e.t + e.d);
    n.connect(f).connect(g).connect(p).connect(master); const r = ac.createGain(); r.gain.value = .3; p.connect(r).connect(verb);
  }
  function pop(e) {
    const o = ac.createOscillator(), g = ac.createGain(); o.frequency.setValueAtTime(420, e.t); o.frequency.exponentialRampToValueAtTime(1100, e.t + .06);
    g.gain.setValueAtTime(.18, e.t); g.gain.exponentialRampToValueAtTime(.001, e.t + .14); o.connect(g); out(g, 0, .2); o.start(e.t); o.stop(e.t + .16);
  }
  function ding(e) { [84, 91, 96].forEach((m, i) => glock({ t: e.t + i * .05, m })); pop(e); }
  function tick(e) {   // a paper "flip" on every cut of the montage
    const n = noiseSrc(e.t, .06), f = ac.createBiquadFilter(), g = ac.createGain(); f.type = 'highpass'; f.frequency.value = 2500;
    g.gain.setValueAtTime(.14, e.t); g.gain.exponentialRampToValueAtTime(.001, e.t + .06); n.connect(f).connect(g); out(g, (e.i % 2 ? .3 : -.3));
    pluckNote(e.t, [84, 81, 79, 77, 79, 81, 84, 89][e.i], .05, e.i % 2 ? .4 : -.4);
  }
  function twinkle(e) { for (let k = 0; k < 6; k++) glock({ t: e.t + k * .07, m: [96, 100, 103, 108, 103, 100][k] }); }

  const PLAY = { chord: pad, pluck, box, bass, mel, kick, snap, shake, glock, pencil, fold, whoosh, pop, ding, tick, twinkle };
  for (const k in PLAY) for (const e of SCORE[k]) PLAY[k](e);
  master.gain.setValueAtTime(.8, DUR - 1.6); master.gain.linearRampToValueAtTime(0, DUR - .02);
  return ac.startRendering();
}
