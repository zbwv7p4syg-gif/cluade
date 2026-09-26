// audio.js — synthesizes the whole soundtrack from SCORE with the Web Audio API.
// No samples and no audio files: oscillators, seeded noise and filters only.
// renderSoundtrack() uses an OfflineAudioContext, so the result is sample-exact and repeatable.

const mtof = m => 440 * Math.pow(2, (m - 69) / 12);

function xorshift(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }

// sc / dur let the renderer synthesize a tiny calibration score with the very same instruments.
async function renderSoundtrack(sr = 44100, sc = SCORE, dur = DUR) {
  const ac = new OfflineAudioContext(2, Math.ceil(sr * dur), sr);
  const rnd = xorshift(2024);

  const noise = ac.createBuffer(1, sr * 3, sr);
  { const d = noise.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = rnd() * 2 - 1; }

  // ---- buses: instruments -> (side: ducked by the kick) -> master -> compressor -> out, plus a reverb send
  const master = ac.createGain(); master.gain.value = 0.75;
  const comp = ac.createDynamicsCompressor();
  comp.threshold.value = -16; comp.ratio.value = 3; comp.attack.value = 0.008; comp.release.value = 0.2; comp.knee.value = 8;
  master.connect(comp).connect(ac.destination);
  const verb = ac.createConvolver();
  {
    const len = Math.floor(sr * 2.8), ir = ac.createBuffer(2, len, sr);
    for (let c = 0; c < 2; c++) { const d = ir.getChannelData(c); for (let i = 0; i < len; i++) d[i] = (rnd() * 2 - 1) * Math.pow(1 - i / len, 3.4); }
    verb.buffer = ir;
  }
  const verbOut = ac.createGain(); verbOut.gain.value = 0.32; verb.connect(verbOut).connect(master);
  const side = ac.createGain(); side.connect(master);
  // sidechain pump: every loud kick dips the harmonic bus, recovering over ~a quarter of a beat
  side.gain.setValueAtTime(1, 0);
  for (const k of sc.kick || []) if (!k.soft) { side.gain.setValueAtTime(1 - 0.45 * k.g, k.t); side.gain.linearRampToValueAtTime(1, k.t + 0.2); }
  // dotted-8th echo for the lead
  const dly = ac.createDelay(1); dly.delayTime.value = BEAT * 0.75;
  const fb = ac.createGain(); fb.gain.value = 0.3; const dlyOut = ac.createGain(); dlyOut.gain.value = 0.35;
  const dlyLP = ac.createBiquadFilter(); dlyLP.frequency.value = 2500;
  dly.connect(dlyLP).connect(fb).connect(dly); dlyLP.connect(dlyOut); dlyOut.connect(master); dlyOut.connect(verb);

  const out = (node, dest = master, pan = 0, rev = 0) => {
    const p = ac.createStereoPanner(); p.pan.value = pan; node.connect(p); p.connect(dest);
    if (rev) { const r = ac.createGain(); r.gain.value = rev; p.connect(r); r.connect(verb); }
    return p;
  };
  const env = (g, t, a, peak, tau, hold = 0) => { g.setValueAtTime(0, t); g.linearRampToValueAtTime(peak, t + a); g.setTargetAtTime(0, t + a + hold, tau); };
  const noiseSrc = (t, dur) => { const s = ac.createBufferSource(); s.buffer = noise; s.start(t, rnd() * 2, dur); return s; };

  // ---------------------------------------------------------------- instruments
  function kick(e) {
    const o = ac.createOscillator(), g = ac.createGain();
    o.frequency.setValueAtTime(e.soft ? 110 : 150, e.t); o.frequency.exponentialRampToValueAtTime(45, e.t + 0.12);
    g.gain.setValueAtTime(e.g * (e.soft ? 0.7 : 1), e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + (e.soft ? 0.25 : 0.42));
    o.connect(g); out(g); o.start(e.t); o.stop(e.t + 0.45);
    if (!e.soft) { const n = noiseSrc(e.t, 0.02), f = ac.createBiquadFilter(), ng = ac.createGain(); f.type = 'highpass'; f.frequency.value = 3000; ng.gain.setValueAtTime(0.25 * e.g, e.t); ng.gain.exponentialRampToValueAtTime(0.001, e.t + 0.015); n.connect(f).connect(ng); out(ng); }
  }
  function heart(e) {   // lub-dub: a muffled, round thump
    const o = ac.createOscillator(), g = ac.createGain(), f = ac.createBiquadFilter();
    f.frequency.value = 180;
    o.frequency.setValueAtTime(e.strong ? 95 : 80, e.t); o.frequency.exponentialRampToValueAtTime(38, e.t + 0.1);
    g.gain.setValueAtTime(e.strong ? 1.2 : 0.7, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.3);
    o.connect(f).connect(g); out(g, master, 0, 0.15); o.start(e.t); o.stop(e.t + 0.32);
  }
  function snare(e) {
    const n = noiseSrc(e.t, 0.3), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'bandpass'; f.frequency.value = e.roll ? 2500 : 1800; f.Q.value = 0.7;
    g.gain.setValueAtTime(0.9 * e.g, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + (e.roll ? 0.1 : 0.22));
    n.connect(f).connect(g); out(g, master, 0.05, 0.25);
    const o = ac.createOscillator(), og = ac.createGain(); o.type = 'triangle'; o.frequency.value = 190;
    og.gain.setValueAtTime(0.35 * e.g, e.t); og.gain.exponentialRampToValueAtTime(0.001, e.t + 0.08); o.connect(og); out(og); o.start(e.t); o.stop(e.t + 0.1);
  }
  function hat(e, open) {
    const n = noiseSrc(e.t, open ? 0.35 : 0.06), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'highpass'; f.frequency.value = 7500;
    g.gain.setValueAtTime(0.35 * e.g, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + (open ? 0.3 : 0.05));
    n.connect(f).connect(g); out(g, master, open ? -0.25 : 0.3);
  }
  function crash(e) {
    const n = noiseSrc(e.t, 2.5), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'highpass'; f.frequency.value = 4500;
    g.gain.setValueAtTime(0.4 * e.g, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 2.4);
    n.connect(f).connect(g); out(g, master, 0, 0.4);
  }
  function bass(e) {
    const o = ac.createOscillator(), s = ac.createOscillator(), f = ac.createBiquadFilter(), g = ac.createGain();
    o.type = 'sawtooth'; o.frequency.value = mtof(e.m); s.frequency.value = mtof(e.m);
    f.frequency.setValueAtTime(900, e.t); f.frequency.exponentialRampToValueAtTime(300, e.t + e.dur);
    const sg = ac.createGain(); sg.gain.value = 0.9;
    o.connect(f); s.connect(sg); f.connect(g); sg.connect(g);
    env(g.gain, e.t, 0.005, 0.32 * e.g, e.dur * 0.6);
    out(g, side); o.start(e.t); s.start(e.t); o.stop(e.t + e.dur + 0.5); s.stop(e.t + e.dur + 0.5);
  }
  function piano(e) {
    for (const m of e.notes) {
      const f0 = mtof(m), g = ac.createGain(), lp = ac.createBiquadFilter(); lp.frequency.value = 3800;
      [[1, 'sine', 1], [2, 'triangle', 0.3], [3, 'sine', 0.12], [4.01, 'sine', 0.05]].forEach(([h, type, amp]) => {
        const o = ac.createOscillator(), og = ac.createGain(); o.type = type; o.frequency.value = f0 * h; o.detune.value = (rnd() - 0.5) * 6;
        og.gain.value = amp; o.connect(og).connect(lp); o.start(e.t); o.stop(e.t + e.dur + 1.5);
      });
      lp.connect(g);
      g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(0.16 * e.g, e.t + 0.004);
      g.gain.setTargetAtTime(0.07 * e.g, e.t + 0.004, 0.25); g.gain.setTargetAtTime(0, e.t + e.dur, 0.25);
      out(g, side, (m % 12 - 6) / 14, 0.35);
    }
  }
  function pad(e) {
    const g = ac.createGain(), lp = ac.createBiquadFilter(); lp.frequency.value = 1100; lp.Q.value = 0.3;
    for (const m of e.notes) for (const det of [-8, 8]) {
      const o = ac.createOscillator(); o.type = 'sawtooth'; o.frequency.value = mtof(m); o.detune.value = det;
      o.connect(lp); o.start(e.t); o.stop(e.t + e.dur + 1.2);
    }
    lp.connect(g);
    const peak = 0.05 * e.g / Math.sqrt(e.notes.length);
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(peak, e.t + 0.5); g.gain.setValueAtTime(peak, e.t + e.dur); g.gain.linearRampToValueAtTime(0, e.t + e.dur + 0.8);
    out(g, side, 0, 0.5);
  }
  function lead(e) {
    const o = ac.createOscillator(), o2 = ac.createOscillator(), lp = ac.createBiquadFilter(), g = ac.createGain();
    o.type = 'square'; o2.type = 'sawtooth'; o.frequency.value = o2.frequency.value = mtof(e.m); o2.detune.value = 7;
    const lfo = ac.createOscillator(), lg = ac.createGain(); lfo.frequency.value = 5.5; lg.gain.value = 6;
    lfo.connect(lg); lg.connect(o.detune); lg.connect(o2.detune);
    lp.frequency.value = 2600;
    const mix = ac.createGain(); mix.gain.value = 0.5; o.connect(mix); o2.connect(mix); mix.connect(lp).connect(g);
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(0.12 * e.g, e.t + 0.01); g.gain.setTargetAtTime(0.08 * e.g, e.t + 0.01, 0.1);
    g.gain.setValueAtTime(0.08 * e.g, e.t + e.dur); g.gain.linearRampToValueAtTime(0, e.t + e.dur + 0.06);
    const p = out(g, master, 0.1, 0.25); p.connect(dly);
    for (const n of [o, o2, lfo]) { n.start(e.t); n.stop(e.t + e.dur + 0.1); }
  }
  function bell(e) {
    const g = ac.createGain();
    [[1, 1], [2.76, 0.4], [5.4, 0.15]].forEach(([h, a]) => { const o = ac.createOscillator(), og = ac.createGain(); o.frequency.value = mtof(e.m) * h; og.gain.value = a; o.connect(og).connect(g); o.start(e.t); o.stop(e.t + 2.5); });
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(0.14 * e.g, e.t + 0.003); g.gain.setTargetAtTime(0, e.t + 0.003, 0.5);
    out(g, master, 0, 0.5);
  }
  function drip(e) {
    const o = ac.createOscillator(), g = ac.createGain(), f = mtof(e.m);
    o.frequency.setValueAtTime(f, e.t); o.frequency.exponentialRampToValueAtTime(f * 0.55, e.t + 0.09);
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(0.18 * e.g, e.t + 0.002); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.25);
    o.connect(g); out(g, master, (e.x - 0.5) * 1.2, 0.6); o.start(e.t); o.stop(e.t + 0.3);
  }
  function riser(e) {
    const n = noiseSrc(e.t, e.dur), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'bandpass'; f.Q.value = 1.2; f.frequency.setValueAtTime(300, e.t); f.frequency.exponentialRampToValueAtTime(9000, e.t + e.dur);
    g.gain.setValueAtTime(0.001, e.t); g.gain.exponentialRampToValueAtTime(0.35 * e.g, e.t + e.dur - 0.01); g.gain.linearRampToValueAtTime(0, e.t + e.dur);
    n.connect(f).connect(g); out(g, master, 0, 0.3);
  }
  function boom(e) {   // firework: low thud + burst + crackle
    const o = ac.createOscillator(), g = ac.createGain();
    o.frequency.setValueAtTime(70, e.t); o.frequency.exponentialRampToValueAtTime(35, e.t + 0.6);
    g.gain.setValueAtTime(0.5, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.9);
    o.connect(g); out(g, master, (e.x - 0.5), 0.3); o.start(e.t); o.stop(e.t + 1);
    for (let k = 0; k < 10; k++) {
      const tc = e.t + 0.18 + rnd() * 0.6, n = noiseSrc(tc, 0.02), f = ac.createBiquadFilter(), cg = ac.createGain();
      f.type = 'highpass'; f.frequency.value = 3000; cg.gain.setValueAtTime(0.12, tc); cg.gain.exponentialRampToValueAtTime(0.001, tc + 0.02);
      n.connect(f).connect(cg); out(cg, master, (rnd() - 0.5) * 1.6, 0.4);
    }
  }

  const PLAY = { kick, heart, snare, hat: e => hat(e, false), ohat: e => hat(e, true), bass, piano, pad, lead, bell, crash, drip, riser, boom };
  for (const k in PLAY) for (const e of sc[k] || []) PLAY[k](e);

  // fade the tail
  if (dur === DUR) { master.gain.setValueAtTime(0.75, DUR - 1.2); master.gain.linearRampToValueAtTime(0, DUR - 0.05); }
  return ac.startRendering();
}
