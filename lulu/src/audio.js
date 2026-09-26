// audio.js — synthesizes the soundtrack from SCORE with the Web Audio API (no recordings, no samples):
// a formant "babble" voice for each character, a music box, glockenspiel, pad, and sound effects.

const mtof = m => 440 * Math.pow(2, (m - 69) / 12);
function xorshift(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }
// child-like vowel formants (Hz)
const FORMANTS = { u: [380, 850], o: [520, 950], a: [900, 1450], e: [560, 2050], i: [360, 2600], n: [300, 1200] };

async function renderSoundtrack(sr = 44100) {
  const ac = new OfflineAudioContext(2, Math.ceil(sr * DUR), sr);
  const rnd = xorshift(77);
  const noise = ac.createBuffer(1, sr * 3, sr);
  { const d = noise.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = rnd() * 2 - 1; }
  const master = ac.createGain(); master.gain.value = 0.8;
  const comp = ac.createDynamicsCompressor(); comp.threshold.value = -18; comp.ratio.value = 3;
  master.connect(comp).connect(ac.destination);
  const verb = ac.createConvolver();
  { const len = sr * 2, ir = ac.createBuffer(2, len, sr); for (let c = 0; c < 2; c++) { const d = ir.getChannelData(c); for (let i = 0; i < len; i++) d[i] = (rnd() * 2 - 1) * Math.pow(1 - i / len, 3); } verb.buffer = ir; }
  const vg = ac.createGain(); vg.gain.value = 0.25; verb.connect(vg).connect(master);
  const out = (node, pan = 0, rev = 0, dest = master) => { const p = ac.createStereoPanner(); p.pan.value = pan; node.connect(p).connect(dest); if (rev) { const r = ac.createGain(); r.gain.value = rev; p.connect(r).connect(verb); } };
  const noiseSrc = (t, d) => { const s = ac.createBufferSource(); s.buffer = noise; s.start(t, rnd() * 2, d); return s; };
  // music bus: ducks under the voices
  const music = ac.createGain(); music.connect(master); music.gain.setValueAtTime(1, 0);
  for (const s of SCORE.syl) { music.gain.setTargetAtTime(s.who === 'bro' ? 0.35 : 0.5, s.t - 0.02, 0.03); music.gain.setTargetAtTime(1, s.t + s.dur + 0.05, 0.15); }

  // ---- the voices
  function voice(e) {
    const sis = e.who === 'sis', t = e.t, d = e.dur;
    const src = ac.createOscillator(); src.type = 'sawtooth';
    src.frequency.setValueAtTime(e.f0, t); src.frequency.exponentialRampToValueAtTime(e.f1, t + d);
    const vib = ac.createOscillator(), vd = ac.createGain(); vib.frequency.value = e.cry ? 7.5 : 5.5; vd.gain.value = e.cry ? 38 : 12; vib.connect(vd).connect(src.detune);
    const [F1, F2] = FORMANTS[e.v].map(f => f * (sis ? 1.18 : 1));
    const b1 = ac.createBiquadFilter(), b2 = ac.createBiquadFilter(), lp = ac.createBiquadFilter();
    b1.type = b2.type = 'bandpass'; b1.frequency.value = F1; b1.Q.value = 6; b2.frequency.value = F2; b2.Q.value = 9; lp.frequency.value = e.v === 'n' ? 700 : 4200;
    const g2 = ac.createGain(); g2.gain.value = e.v === 'n' ? 0.1 : 0.55;
    src.connect(b1); src.connect(b2); b1.connect(lp); b2.connect(g2).connect(lp);
    const g = ac.createGain(), peak = sis ? 0.55 : 1.05;
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(peak, t + 0.025);
    if (e.cry) { const tr = ac.createOscillator(), tg = ac.createGain(); tr.frequency.value = 9; tg.gain.value = peak * 0.35; tr.connect(tg).connect(g.gain); tr.start(t); tr.stop(t + d + 0.1); }
    g.gain.setValueAtTime(peak, t + Math.max(0.03, d - 0.06)); g.gain.linearRampToValueAtTime(0, t + d + 0.02);
    lp.connect(g); out(g, sis ? -0.25 : 0.25, 0.25);
    // a breathy edge
    const n = noiseSrc(t, d + 0.05), nf = ac.createBiquadFilter(), ng = ac.createGain(); nf.type = 'bandpass'; nf.frequency.value = F2; nf.Q.value = 2;
    ng.gain.setValueAtTime(0, t); ng.gain.linearRampToValueAtTime(e.cry ? 0.05 : 0.02, t + 0.02); ng.gain.linearRampToValueAtTime(0, t + d);
    n.connect(nf).connect(ng); out(ng, sis ? -0.25 : 0.25);
    for (const o of [src, vib]) { o.start(t); o.stop(t + d + 0.1); }
  }
  // ---- music
  function musicbox(e) {
    const t = e.t, f = mtof(e.m), g = ac.createGain();
    [[1, 1], [3.01, .3], [5.4, .12]].forEach(([h, a]) => { const o = ac.createOscillator(), og = ac.createGain(); o.frequency.value = f * h; og.gain.value = a; o.connect(og).connect(g); o.start(t); o.stop(t + 1.3); });
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(0.045 * e.g, t + 0.003); g.gain.setTargetAtTime(0, t + 0.003, 0.35);
    out(g, (e.m % 5 - 2) / 5, 0.5, music);
  }
  function glock(e) {
    const t = e.t, f = mtof(e.m), g = ac.createGain();
    [[1, 1], [2.76, .35], [5.4, .1]].forEach(([h, a]) => { const o = ac.createOscillator(), og = ac.createGain(); o.frequency.value = f * h; og.gain.value = a; o.connect(og).connect(g); o.start(t); o.stop(t + 1.6); });
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(0.07, t + 0.002); g.gain.setTargetAtTime(0, t + 0.002, 0.45);
    out(g, 0.1, 0.5, music);
  }
  function pad(e) {
    const g = ac.createGain(), lp = ac.createBiquadFilter(); lp.frequency.value = 1100;
    for (const m of e.notes) for (const det of [-7, 7]) { const o = ac.createOscillator(); o.type = 'triangle'; o.frequency.value = mtof(m - 12); o.detune.value = det; o.connect(lp); o.start(e.t); o.stop(e.end + 0.8); }
    lp.connect(g);
    const pk = e.t >= 9.07 ? 0.05 : 0.035;
    g.gain.setValueAtTime(0, e.t); g.gain.linearRampToValueAtTime(pk, e.t + 0.3); g.gain.setValueAtTime(pk, e.end); g.gain.linearRampToValueAtTime(0, e.end + 0.6);
    out(g, 0, 0.4, music);
  }
  // ---- sound effects
  function sizzle() {   // the pot, louder when the kitchen is on screen
    const n = ac.createBufferSource(); n.buffer = noise; n.loop = true;
    const f = ac.createBiquadFilter(); f.type = 'bandpass'; f.frequency.value = 5000; f.Q.value = .6;
    const g = ac.createGain(); g.gain.setValueAtTime(0, 0);
    [[0, .05], [2.07, .015], [4.13, .09], [5.47, .045], [9.07, .012], [10, 0]].forEach(([t, v]) => g.gain.linearRampToValueAtTime(v, t + 0.05));
    const am = ac.createOscillator(), amg = ac.createGain(); am.frequency.value = 13; amg.gain.value = 0.015; am.connect(amg).connect(g.gain);
    n.connect(f).connect(g); out(g, 0.4); n.start(0); n.stop(10.5); am.start(0); am.stop(10.5);
  }
  function step(e) {
    const o = ac.createOscillator(), g = ac.createGain(); o.frequency.setValueAtTime(180, e.t); o.frequency.exponentialRampToValueAtTime(90, e.t + 0.06);
    g.gain.setValueAtTime(0.18, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.09); o.connect(g); out(g, 0.3 - (e.t - 6.2) * 0.25); o.start(e.t); o.stop(e.t + 0.1);
  }
  function tear(e) {
    const o = ac.createOscillator(), g = ac.createGain(); o.frequency.setValueAtTime(1600, e.t); o.frequency.exponentialRampToValueAtTime(900, e.t + 0.08);
    g.gain.setValueAtTime(0.06, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.25); o.connect(g); out(g, -0.2, 0.6); o.start(e.t); o.stop(e.t + 0.3);
  }
  function hop(e) {
    const o = ac.createOscillator(), g = ac.createGain(); o.frequency.setValueAtTime(300, e.t); o.frequency.exponentialRampToValueAtTime(900, e.t + 0.18);
    g.gain.setValueAtTime(0.08, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.22); o.connect(g); out(g, 0, 0.3); o.start(e.t); o.stop(e.t + 0.25);
  }
  function turn(e) {
    const n = noiseSrc(e.t, 0.2), f = ac.createBiquadFilter(), g = ac.createGain(); f.type = 'bandpass'; f.frequency.setValueAtTime(800, e.t); f.frequency.exponentialRampToValueAtTime(3000, e.t + 0.15);
    g.gain.setValueAtTime(0.1, e.t); g.gain.linearRampToValueAtTime(0, e.t + 0.18); n.connect(f).connect(g); out(g, 0.3);
  }
  function hug(e) {
    const o = ac.createOscillator(), g = ac.createGain(); o.frequency.setValueAtTime(220, e.t); o.frequency.exponentialRampToValueAtTime(90, e.t + 0.12);
    g.gain.setValueAtTime(0.35, e.t); g.gain.exponentialRampToValueAtTime(0.001, e.t + 0.25); o.connect(g); out(g); o.start(e.t); o.stop(e.t + 0.3);
    [84, 88, 91, 96].forEach((m, i) => glock({ t: e.t + 0.05 + i * 0.07, m }));
  }

  sizzle();
  const PLAY = { syl: voice, box: musicbox, glock, chord: pad, step, tear, hop, turn, hug };
  for (const k in PLAY) for (const e of SCORE[k]) PLAY[k](e);
  master.gain.setValueAtTime(0.8, DUR - 0.8); master.gain.linearRampToValueAtTime(0, DUR - 0.02);
  return ac.startRendering();
}
