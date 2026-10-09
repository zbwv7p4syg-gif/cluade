// audio.js — the soundtrack, synthesized from the same timeline with Web Audio (no recordings, no samples):
// the fluorescent hum (which sags and sputters with the lights), damp-carpet footsteps from the distance
// walked, breathing while running, the stings, and a music box for the very end.

const mtof = m => 440 * Math.pow(2, (m - 69) / 12);
function xorshift(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }

async function renderSoundtrack(sr = 44100) {
  const ac = new OfflineAudioContext(2, Math.ceil(sr * DUR), sr), rnd = xorshift(1996);
  const noise = ac.createBuffer(1, sr * 4, sr);
  { const d = noise.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = rnd() * 2 - 1; }
  const master = ac.createGain(); master.gain.value = .85;
  const comp = ac.createDynamicsCompressor(); comp.threshold.value = -20; comp.ratio.value = 3.5; master.connect(comp).connect(ac.destination);
  const verb = ac.createConvolver();
  { const len = sr * 1.2, ir = ac.createBuffer(2, len, sr); for (let c = 0; c < 2; c++) { const d = ir.getChannelData(c); for (let i = 0; i < len; i++) d[i] = (rnd() * 2 - 1) * Math.pow(1 - i / len, 2.6); } verb.buffer = ir; }
  const vg = ac.createGain(); vg.gain.value = .22; verb.connect(vg).connect(master);
  const out = (node, pan = 0, rev = 0) => { const p = ac.createStereoPanner(); p.pan.value = pan; node.connect(p).connect(master); if (rev) { const r = ac.createGain(); r.gain.value = rev; p.connect(r).connect(verb); } };
  const nsrc = (t, d, loop = false) => { const s = ac.createBufferSource(); s.buffer = noise; s.loop = loop; s.start(t, rnd() * 2, loop ? undefined : d); if (loop) s.stop(t + d); return s; };
  const burst = (t, d, type, f, q, vol, pan = 0, rev = 0) => { const s = nsrc(t, d + .02), fl = ac.createBiquadFilter(), g = ac.createGain(); fl.type = type; fl.frequency.value = f; fl.Q.value = q;
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(vol, t + Math.min(.01, d / 3)); g.gain.exponentialRampToValueAtTime(.0005, t + d); s.connect(fl).connect(g); out(g, pan, rev); };
  const tone = (t, f0, f1, d, type, vol, pan = 0, rev = 0) => { const o = ac.createOscillator(), g = ac.createGain(); o.type = type; o.frequency.setValueAtTime(f0, t); o.frequency.exponentialRampToValueAtTime(f1, t + d);
    g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(vol, t + .008); g.gain.exponentialRampToValueAtTime(.0005, t + d); o.connect(g); out(g, pan, rev); o.start(t); o.stop(t + d + .02); };

  // ---- the fluorescent hum follows the light level
  const hum = ac.createGain(), humLp = ac.createBiquadFilter(); humLp.frequency.value = 900; hum.gain.value = 0;
  for (const [f, a, ty] of [[60, .5, 'sine'], [120, 1, 'sawtooth'], [240, .45, 'square'], [360, .2, 'sawtooth']]) { const o = ac.createOscillator(), g = ac.createGain(); o.type = ty; o.frequency.value = f; o.detune.value = (f * 7) % 9 - 4; g.gain.value = a * .028; o.connect(g).connect(humLp); o.start(0); o.stop(DUR); }
  humLp.connect(hum); out(hum, 0, .2);
  const buzz = ac.createGain(), bz = nsrc(0, DUR, true), bf = ac.createBiquadFilter(); bf.type = 'bandpass'; bf.frequency.value = 3200; bf.Q.value = 4; buzz.gain.value = 0; bz.connect(bf).connect(buzz); out(buzz, .1);
  let prev = 1;
  for (let t = 0; t < DUR; t += 1 / 120) {
    const lv = levelAt(t); hum.gain.setValueAtTime(lv > .5 ? lv : lv * .4, t); buzz.gain.setValueAtTime(lv > .5 ? .012 : 0, t);
    if ((lv > .5) !== (prev > .5)) { lv > .5 ? (burst(t, .03, 'highpass', 3500, .7, .14, .1), tone(t, 2600, 900, .02, 'square', .05)) : (burst(t, .025, 'highpass', 2500, .7, .1, .1), tone(t, 160, 70, .06, 'sine', .12)); }
    prev = lv;
  }
  // ---- room tone, tape hiss, and the slow dread under the chase
  { const s = nsrc(0, DUR, true), fl = ac.createBiquadFilter(), g = ac.createGain(); fl.type = 'lowpass'; fl.frequency.value = 170; g.gain.value = .13; s.connect(fl).connect(g); out(g); }
  { const s = nsrc(0, 38, true), fl = ac.createBiquadFilter(), g = ac.createGain(); fl.type = 'highpass'; fl.frequency.value = 5500; g.gain.value = .012; s.connect(fl).connect(g); out(g); }
  { const o = ac.createOscillator(), g = ac.createGain(); o.frequency.value = 46; g.gain.setValueAtTime(0, 0); g.gain.setValueAtTime(.005, 12); g.gain.linearRampToValueAtTime(.05, 34.6); g.gain.setValueAtTime(0, 34.8); g.gain.setValueAtTime(.02, 35.9); g.gain.linearRampToValueAtTime(0, 37.6); o.connect(g); out(g); o.start(0); o.stop(DUR); }
  tone(.5, 1760, 1760, .1, 'sine', .04);                       // camcorder beep
  tone(37.9, 1500, 1500, .12, 'sine', .05);

  // ---- footsteps on damp carpet (from the distance walked) and breathing when running
  STEPS.forEach((s, i) => {
    const run = s.run, pan = (i % 2 ? .18 : -.18), v = run ? .34 : .22, j = 1 + (rnd() - .5) * .12;
    tone(s.t, 95 * j, 48, .09, 'sine', v, pan);
    burst(s.t, .08, 'lowpass', 520 * j, .8, v * .55, pan, .1); burst(s.t + .01, .05, 'bandpass', 2400, 1.2, v * .08, pan);
  });
  for (let t = 26.6; t < 33.2; t += .62) { burst(t, .26, 'bandpass', 760, 1.1, .06, 0, .1); burst(t + .3, .24, 'bandpass', 620, 1.1, .05, 0, .1); }
  for (let t = 33.5; t < 34.7; t += 1.2) { burst(t, .5, 'bandpass', 700, 1.1, .05, 0, .2); burst(t + .55, .5, 'bandpass', 600, 1.1, .045, 0, .2); }

  // ---- stings: whenever you look back, and the long one before the lights die
  for (const g of GLANCES) { tone(g.t, 62, 34, .6, 'sine', .38, 0, .3); burst(g.t, .12, 'lowpass', 400, .8, .2); tone(g.t, 760, 1250, .38, 'sawtooth', .012, -.2, .4); tone(g.t, 790, 1300, .38, 'sawtooth', .012, .2, .4); }
  { const g = ac.createGain(), a = ac.createOscillator(), b = ac.createOscillator(), c2 = ac.createOscillator();
    for (const [o, f0, f1] of [[a, 520, 1500], [b, 553, 1620], [c2, 780, 2300]]) { o.type = 'sawtooth'; o.frequency.setValueAtTime(f0, 33.7); o.frequency.exponentialRampToValueAtTime(f1, 34.78); o.connect(g); o.start(33.7); o.stop(34.8); }
    const fl = ac.createBiquadFilter(); fl.type = 'lowpass'; fl.frequency.value = 3200; g.gain.setValueAtTime(0, 33.7); g.gain.linearRampToValueAtTime(.05, 34.7); g.gain.setValueAtTime(0, 34.8); g.connect(fl); out(fl, 0, .3); }
  tone(34.8, 900, 35, .5, 'sine', .3, 0, .3);                  // the power dying
  // silence in the dark: just a heartbeat
  for (const t of [34.98, 35.2, 35.5, 35.72]) { tone(t, 62, 42, .14, 'sine', .3); }

  // ---- lights on, a little "hmph", and a music box
  tone(35.8, 38, 150, .5, 'sine', .45, 0, .2); burst(35.8, .25, 'lowpass', 1500, .6, .25, 0, .3); tone(35.8, 60, 60, 1.2, 'triangle', .05);
  tone(36.02, 420, 300, .14, 'triangle', .13, 0, .1); tone(36.2, 360, 240, .18, 'triangle', .13, 0, .1);
  tone(36.9, 523, 523, .2, 'triangle', .1, 0, .15); tone(37.1, 392, 392, .3, 'triangle', .09, 0, .15);
  [[38.4, 77], [38.85, 81], [39.3, 84], [39.75, 81], [40.2, 89]].forEach(([t, m], i) => {
    for (const [h, a] of [[1, 1], [3.01, .25], [5.4, .08]]) tone(t, mtof(m) * h, mtof(m) * h, 1.3, 'sine', .045 * a, (i % 2 - .5) * .3, .5);
  });
  master.gain.setValueAtTime(.85, DUR - 1.2); master.gain.linearRampToValueAtTime(0, DUR - .02);
  return ac.startRendering();
}
