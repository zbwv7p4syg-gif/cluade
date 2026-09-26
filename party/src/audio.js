// audio.js — synthesizes the whole track from SCORE with the Web Audio API (no samples, no files).
// renderSoundtrack(sr, sc, dur): sc/dur let the renderer synthesize tiny calibration scores
// with exactly the same instruments.

const mtof = m => 440 * Math.pow(2, (m - 69) / 12);
function xorshift(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }

async function renderSoundtrack(sr = 44100, sc = SCORE, dur = DUR) {
  const ac = new OfflineAudioContext(2, Math.ceil(sr * dur), sr);
  const rnd = xorshift(128);
  const full = dur === DUR;
  const noise = ac.createBuffer(1, sr * 3, sr);
  { const d = noise.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = rnd() * 2 - 1; }

  // ---- buses
  const master = ac.createGain(); master.gain.value = 0.7;
  const comp = ac.createDynamicsCompressor();
  comp.threshold.value = -12; comp.ratio.value = 4; comp.attack.value = 0.005; comp.release.value = 0.15; comp.knee.value = 6;
  master.connect(comp).connect(ac.destination);
  const verb = ac.createConvolver();
  { const len = Math.floor(sr * 2.4), ir = ac.createBuffer(2, len, sr);
    for (let c = 0; c < 2; c++) { const d = ir.getChannelData(c); for (let i = 0; i < len; i++) d[i] = (rnd() * 2 - 1) * Math.pow(1 - i / len, 3.5); }
    verb.buffer = ir; }
  const verbOut = ac.createGain(); verbOut.gain.value = 0.28; verb.connect(verbOut).connect(master);
  // "through the wall": drums and bass pass a low-pass that bursts open at the breakthrough (bar 4)
  const wall = ac.createBiquadFilter(); wall.type = 'lowpass'; wall.Q.value = 0.9;
  if (full) {
    wall.frequency.setValueAtTime(280, 0); wall.frequency.setValueAtTime(280, bt(3));
    wall.frequency.exponentialRampToValueAtTime(900, bt(4) - 0.01); wall.frequency.setValueAtTime(20000, bt(4));
  } else wall.frequency.value = 20000;
  wall.connect(master);
  // sidechain bus: pumps on every kick (hard in the drop)
  const side = ac.createGain(); side.connect(master);
  side.gain.setValueAtTime(1, 0);
  for (const k of sc.kick || []) {
    const depth = k.style === 'drop' ? 0.78 : k.style === 'house' ? 0.45 : 0.3;
    side.gain.setValueAtTime(1 - depth, k.t); side.gain.linearRampToValueAtTime(1, k.t + BEAT * 0.42);
  }
  // 3/16 echo for the lead
  const dly = ac.createDelay(1); dly.delayTime.value = STEP * 3;
  const fb = ac.createGain(); fb.gain.value = 0.32; const dlyLP = ac.createBiquadFilter(); dlyLP.frequency.value = 3000;
  const dlyOut = ac.createGain(); dlyOut.gain.value = 0.3;
  dly.connect(dlyLP).connect(fb).connect(dly); dlyLP.connect(dlyOut).connect(master);

  const out = (node, dest = master, pan = 0, rev = 0) => {
    const p = ac.createStereoPanner(); p.pan.value = pan; node.connect(p); p.connect(dest);
    if (rev) { const r = ac.createGain(); r.gain.value = rev; p.connect(r); r.connect(verb); }
    return p;
  };
  const noiseSrc = (t, d) => { const s = ac.createBufferSource(); s.buffer = noise; s.start(t, rnd() * 2, d); return s; };
  const dist = (() => { const ws = ac.createWaveShaper(), c = new Float32Array(1024); for (let i = 0; i < 1024; i++) { const x = i / 511.5 - 1; c[i] = Math.tanh(x * 2.2); } ws.curve = c; return ws; });

  // ---------------------------------------------------------------- instruments
  function kick(e) {
    const drop = e.style === 'drop', o = ac.createOscillator(), g = ac.createGain();
    o.frequency.setValueAtTime(drop ? 210 : 160, e.t); o.frequency.exponentialRampToValueAtTime(drop ? 46 : 50, e.t + (drop ? 0.08 : 0.1));
    g.gain.setValueAtTime(e.g, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + (drop ? 0.5 : e.style === 'build' ? 0.2 : 0.35));
    if (drop) { const d = dist(), post = ac.createGain(); post.gain.value = 0.8; o.connect(d).connect(g); g.connect(post); out(post, e.style === 'house' ? wall : master); }
    else { o.connect(g); out(g, e.style === 'house' ? wall : master); }
    o.start(e.t); o.stop(e.t + 0.55);
    const n = noiseSrc(e.t, 0.02), f = ac.createBiquadFilter(), ng = ac.createGain();
    f.type = 'highpass'; f.frequency.value = 2500; ng.gain.setValueAtTime(0.3 * e.g, e.t); ng.gain.exponentialRampToValueAtTime(0.001, e.t + 0.012);
    n.connect(f).connect(ng); out(ng, e.style === 'house' ? wall : master);
  }
  function clap(e) {
    const n = noiseSrc(e.t, 0.4), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'bandpass'; f.frequency.value = 1400; f.Q.value = 0.8;
    g.gain.setValueAtTime(0, e.t);
    for (const d of [0, 0.01, 0.02]) { g.gain.setValueAtTime(0.8 * e.g, e.t + d); g.gain.exponentialRampToValueAtTime(0.1 * e.g, e.t + d + 0.009); }
    g.gain.setValueAtTime(0.6 * e.g, e.t + 0.03); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.25);
    n.connect(f).connect(g); out(g, master, 0.05, 0.3);
  }
  function hat(e, open) {
    const n = noiseSrc(e.t, open ? 0.3 : 0.05), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'highpass'; f.frequency.value = open ? 7000 : 9000;
    g.gain.setValueAtTime(0.3 * e.g, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + (open ? 0.22 : 0.04));
    n.connect(f).connect(g); out(g, wall, open ? -0.2 : 0.3);
  }
  function bass(e) {
    const o = ac.createOscillator(), s = ac.createOscillator(), f = ac.createBiquadFilter(), g = ac.createGain();
    o.type = 'sawtooth'; o.frequency.value = mtof(e.m); s.frequency.value = mtof(e.m);
    f.frequency.setValueAtTime(e.sub ? 200 : 1400, e.t); f.frequency.exponentialRampToValueAtTime(e.sub ? 150 : 250, e.t + e.dur);
    const sg = ac.createGain(); sg.gain.value = 1;
    o.connect(f); s.connect(sg); f.connect(g); sg.connect(g);
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(0.3 * e.g, e.t + (e.sub ? 0.2 : 0.004));
    g.gain.setValueAtTime(0.3 * e.g, e.t + e.dur); g.gain.linearRampToValueAtTime(0, e.t + e.dur + 0.05);
    out(g, e.sub ? master : wall); o.start(e.t); s.start(e.t); o.stop(e.t + e.dur + 0.1); s.stop(e.t + e.dur + 0.1);
  }
  function reese(e) {
    const g = ac.createGain(), f = ac.createBiquadFilter(); f.frequency.setValueAtTime(1600, e.t); f.frequency.exponentialRampToValueAtTime(350, e.t + e.dur); f.Q.value = 2;
    for (const det of [-14, 14]) { const o = ac.createOscillator(); o.type = 'sawtooth'; o.frequency.value = mtof(e.m); o.detune.value = det; o.connect(f); o.start(e.t); o.stop(e.t + e.dur + 0.05); }
    const s = ac.createOscillator(), sg = ac.createGain(); s.frequency.value = mtof(e.m); sg.gain.value = 1.2; s.connect(sg).connect(g); s.start(e.t); s.stop(e.t + e.dur + 0.05);
    f.connect(g);
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(0.22 * e.g, e.t + 0.004); g.gain.setValueAtTime(0.22 * e.g, e.t + e.dur); g.gain.linearRampToValueAtTime(0, e.t + e.dur + 0.04);
    out(g, side);
  }
  function saw(e) {   // supersaw chord, pumped by the sidechain
    const g = ac.createGain(), f = ac.createBiquadFilter(); f.type = 'lowpass'; f.Q.value = 0.5;
    f.frequency.setValueAtTime(e.ring ? 9000 : 6500, e.t); f.frequency.exponentialRampToValueAtTime(e.ring ? 900 : 3800, e.t + e.dur);
    for (const m of e.notes) for (const det of [-32, -19, -7, 0, 7, 19, 32]) {
      const o = ac.createOscillator(); o.type = 'sawtooth'; o.frequency.value = mtof(m); o.detune.value = det + (rnd() - 0.5) * 3;
      const p = ac.createStereoPanner(); p.pan.value = det / 40; o.connect(p).connect(f); o.start(e.t); o.stop(e.t + e.dur + (e.ring ? 2 : 0.2));
    }
    f.connect(g);
    const peak = 0.06 * e.g / Math.sqrt(e.notes.length);
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(peak, e.t + 0.01);
    if (e.ring) g.gain.setTargetAtTime(0, e.t + 0.2, 0.9);
    else { g.gain.setValueAtTime(peak, e.t + e.dur - 0.02); g.gain.linearRampToValueAtTime(0, e.t + e.dur + 0.03); }
    out(g, e.ring ? master : side, 0, 0.25);
  }
  function lead(e) {
    const o = ac.createOscillator(), o2 = ac.createOscillator(), f = ac.createBiquadFilter(), g = ac.createGain();
    o.type = 'sawtooth'; o2.type = 'square'; o.frequency.value = o2.frequency.value = mtof(e.m); o2.detune.value = 8;
    f.frequency.setValueAtTime(6000, e.t); f.frequency.exponentialRampToValueAtTime(1300, e.t + 0.2); f.Q.value = 3;
    const mix = ac.createGain(); mix.gain.value = 0.5; o.connect(mix); o2.connect(mix); mix.connect(f).connect(g);
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(0.13 * e.g, e.t + 0.003); g.gain.setTargetAtTime(0, e.t + 0.003, 0.12);
    const p = out(g, master, 0.1, 0.2); p.connect(dly);
    o.start(e.t); o2.start(e.t); o.stop(e.t + e.dur + 0.5); o2.stop(e.t + e.dur + 0.5);
  }
  function pluck(e) {
    const o = ac.createOscillator(), f = ac.createBiquadFilter(), g = ac.createGain();
    o.type = 'sawtooth'; o.frequency.value = mtof(e.m);
    f.frequency.setValueAtTime(e.soft ? 2200 : 4000, e.t); f.frequency.exponentialRampToValueAtTime(400, e.t + 0.25);
    o.connect(f).connect(g);
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(0.1 * e.g, e.t + 0.003); g.gain.setTargetAtTime(0, e.t + 0.003, 0.09);
    out(g, e.soft ? master : side, (e.m % 7 - 3) / 6, 0.45); o.start(e.t); o.stop(e.t + 0.6);
  }
  function pad(e) {
    const g = ac.createGain(), f = ac.createBiquadFilter(); f.frequency.value = 1300;
    for (const m of e.notes) for (const det of [-10, 10]) { const o = ac.createOscillator(); o.type = 'sawtooth'; o.frequency.value = mtof(m - 12); o.detune.value = det; o.connect(f); o.start(e.t); o.stop(e.t + e.dur + 1); }
    f.connect(g);
    const peak = 0.045 * e.g;
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(peak, e.t + 0.35); g.gain.setValueAtTime(peak, e.t + e.dur); g.gain.linearRampToValueAtTime(0, e.t + e.dur + 0.6);
    out(g, side, 0, 0.5);
  }
  function piano(e) {
    for (const m of e.notes) {
      const g = ac.createGain(), lp = ac.createBiquadFilter(); lp.frequency.value = 3500;
      [[1, 'sine', 1], [2, 'triangle', 0.3], [3, 'sine', 0.1]].forEach(([h, type, amp]) => {
        const o = ac.createOscillator(), og = ac.createGain(); o.type = type; o.frequency.value = mtof(m) * h; og.gain.value = amp; o.connect(og).connect(lp); o.start(e.t); o.stop(e.t + e.dur + 1.5);
      });
      lp.connect(g);
      g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(0.15 * e.g, e.t + 0.004); g.gain.setTargetAtTime(0.05 * e.g, e.t + 0.004, 0.3); g.gain.setTargetAtTime(0, e.t + e.dur, 0.3);
      out(g, master, 0, 0.5);
    }
  }
  function roll(e) {
    const n = noiseSrc(e.t, 0.12), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'bandpass'; f.frequency.value = 2200; f.Q.value = 0.8;
    g.gain.setValueAtTime(0.7 * e.g, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.09);
    n.connect(f).connect(g); out(g, master, 0, 0.3);
    const o = ac.createOscillator(), og = ac.createGain(); o.type = 'triangle'; o.frequency.value = 200;
    og.gain.setValueAtTime(0.25 * e.g, e.t); og.gain.exponentialRampToValueAtTime(0.001, e.t + 0.05); o.connect(og); out(og); o.start(e.t); o.stop(e.t + 0.06);
  }
  function riser(e) {
    const n = noiseSrc(e.t, e.dur), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'bandpass'; f.Q.value = 1.5; f.frequency.setValueAtTime(300, e.t); f.frequency.exponentialRampToValueAtTime(11000, e.t + e.dur);
    g.gain.setValueAtTime(0.001, e.t); g.gain.exponentialRampToValueAtTime(0.4 * e.g, e.t + e.dur - 0.005); g.gain.linearRampToValueAtTime(0, e.t + e.dur);
    n.connect(f).connect(g); out(g, master, 0, 0.3);
  }
  function pitch(e) {
    const o = ac.createOscillator(), o2 = ac.createOscillator(), f = ac.createBiquadFilter(), g = ac.createGain();
    o.type = o2.type = 'sawtooth'; o2.detune.value = 12;
    for (const x of [o, o2]) { x.frequency.setValueAtTime(110, e.t); x.frequency.exponentialRampToValueAtTime(1760, e.t + e.dur); }
    f.frequency.value = 4000; o.connect(f); o2.connect(f); f.connect(g);
    g.gain.setValueAtTime(0.001, e.t); g.gain.exponentialRampToValueAtTime(0.06 * e.g, e.t + e.dur - 0.005); g.gain.linearRampToValueAtTime(0, e.t + e.dur);
    out(g, master, 0, 0.3); o.start(e.t); o2.start(e.t); o.stop(e.t + e.dur); o2.stop(e.t + e.dur);
  }
  function crash(e) {
    const n = noiseSrc(e.t, 2.6), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'highpass'; f.frequency.value = 4000;
    g.gain.setValueAtTime(0.4 * e.g, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 2.5);
    n.connect(f).connect(g); out(g, master, 0, 0.4);
  }
  function impact(e) {
    const o = ac.createOscillator(), g = ac.createGain();
    o.frequency.setValueAtTime(90, e.t); o.frequency.exponentialRampToValueAtTime(28, e.t + 1.2);
    g.gain.setValueAtTime(0.9 * e.g, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 1.6);
    o.connect(g); out(g, master, 0, 0.3); o.start(e.t); o.stop(e.t + 1.7);
    const n = noiseSrc(e.t, 0.6), f = ac.createBiquadFilter(), ng = ac.createGain();
    f.frequency.value = 900; ng.gain.setValueAtTime(0.5 * e.g, e.t); ng.gain.exponentialRampToValueAtTime(0.001, e.t + 0.5);
    n.connect(f).connect(ng); out(ng, master, 0, 0.5);
  }
  function shatter(e) {
    const n = noiseSrc(e.t, 0.6), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'highpass'; f.frequency.value = 2500; g.gain.setValueAtTime(0.6, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.5);
    n.connect(f).connect(g); out(g, master, 0, 0.4);
    for (let k = 0; k < 40; k++) {
      const tp = e.t + 0.02 + Math.pow(rnd(), 2) * 1.1, o = ac.createOscillator(), og = ac.createGain();
      o.frequency.value = 2500 + rnd() * 6000; og.gain.setValueAtTime(0.05, tp); og.gain.exponentialRampToValueAtTime(0.0005, tp + 0.08);
      o.connect(og); out(og, master, rnd() * 2 - 1, 0.5); o.start(tp); o.stop(tp + 0.1);
    }
  }
  function crack(e) {
    const n = noiseSrc(e.t, 0.15), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'bandpass'; f.frequency.value = 2500; f.Q.value = 0.6; g.gain.setValueAtTime(0.7, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.12);
    n.connect(f).connect(g); out(g, master, 0, 0.4);
    const o = ac.createOscillator(), og = ac.createGain(); o.frequency.setValueAtTime(120, e.t); o.frequency.exponentialRampToValueAtTime(50, e.t + 0.15);
    og.gain.setValueAtTime(0.5, e.t); og.gain.exponentialRampToValueAtTime(0.001, e.t + 0.2); o.connect(og); out(og); o.start(e.t); o.stop(e.t + 0.22);
  }
  function type(e) {
    const n = noiseSrc(e.t, 0.015), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'highpass'; f.frequency.value = 3500; g.gain.setValueAtTime(0.25, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.012);
    n.connect(f).connect(g); out(g, master, 0.2);
  }
  function blip(e) {
    const o = ac.createOscillator(), g = ac.createGain(); o.type = 'square'; o.frequency.value = mtof(e.m);
    const f = ac.createBiquadFilter(); f.frequency.value = 3000;
    g.gain.setValueAtTime(0.07 * e.g, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.12);
    o.connect(f).connect(g); out(g, master, 0, 0.3); o.start(e.t); o.stop(e.t + 0.15);
  }
  function down(e) {
    const n = noiseSrc(e.t, e.dur), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'bandpass'; f.frequency.setValueAtTime(9000, e.t); f.frequency.exponentialRampToValueAtTime(300, e.t + e.dur);
    g.gain.setValueAtTime(0.35 * e.g, e.t); g.gain.linearRampToValueAtTime(0, e.t + e.dur);
    n.connect(f).connect(g); out(g, master, 0, 0.4);
  }
  function roar(e) {   // a crowd: band-passed noise with slow random swells
    for (let v = 0; v < 3; v++) {
      const n = noiseSrc(e.t, e.dur + 0.5), f = ac.createBiquadFilter(), g = ac.createGain();
      f.type = 'bandpass'; f.frequency.value = 600 + v * 700; f.Q.value = 1.2;
      g.gain.setValueAtTime(0.001, e.t);
      if (e.rise) g.gain.exponentialRampToValueAtTime(0.12 * e.g, e.t + e.dur);
      else { g.gain.linearRampToValueAtTime(0.14 * e.g, e.t + 0.15); for (let k = 1; k < 6; k++) g.gain.linearRampToValueAtTime((0.07 + rnd() * 0.07) * e.g, e.t + k * e.dur / 6); }
      g.gain.linearRampToValueAtTime(0, e.t + e.dur + 0.4);
      n.connect(f).connect(g); out(g, master, v - 1, 0.6);
    }
  }
  function hiss(e) {
    const n = noiseSrc(e.t, e.dur), f = ac.createBiquadFilter(), g = ac.createGain();
    f.type = 'highpass'; f.frequency.value = 1800; g.gain.setValueAtTime(0.25 * e.g, e.t); g.gain.linearRampToValueAtTime(0, e.t + e.dur);
    n.connect(f).connect(g); out(g, master, 0, 0.3);
  }
  function pyro(e) {
    const n = noiseSrc(e.t, 0.8), f = ac.createBiquadFilter(), g = ac.createGain();
    f.frequency.setValueAtTime(300, e.t); f.frequency.exponentialRampToValueAtTime(2000, e.t + 0.15); f.frequency.exponentialRampToValueAtTime(200, e.t + 0.7);
    g.gain.setValueAtTime(0.45, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.75);
    n.connect(f).connect(g); out(g, master, 0, 0.3);
  }

  const PLAY = { kick, clap, hat: e => hat(e, false), ohat: e => hat(e, true), bass, reese, saw, lead, pluck, pad, piano, roll, riser, pitch,
                 crash, impact, shatter, crack, type, blip, down, roar, hiss, pyro };
  for (const k in PLAY) for (const e of sc[k] || []) PLAY[k](e);
  if (full) { master.gain.setValueAtTime(0.7, DUR - 1.5); master.gain.linearRampToValueAtTime(0, DUR - 0.05); }
  return ac.startRendering();
}
