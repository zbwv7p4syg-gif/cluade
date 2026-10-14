// scenes.js — one function per shot, (g, t, lt, s): t is song time, lt time since the shot began, s the shot.
// drawFrame picks the shot, dissolves into it from the previous one, then adds tags and subtitles on top.

const SCENES = {};

function drawFrame(g, t) {
  g.imageSmoothingEnabled = false;
  if (t < 0) return t > -10 ? testSheet(g, -t) : testDogs(g, -t);
  const i = shotIndex(t), s = SHOTS[i], lt = t - s.t0;
  const draw = (gg, k, tt) => renderShot(gg, k, tt);
  const x = s.x || 0;
  if (i > 0 && x > 0 && lt < x) {
    const p = lt / x;
    if (s.xc) {                                   // through a colour: out to it, then in from it
      if (p < .5) { draw(g, i - 1, t); fadeTo(g, s.xc, p * 2); }
      else { draw(g, i, t); fadeTo(g, s.xc, 2 - p * 2); }
    } else {
      const a = scratch('mixA'), b = scratch('mixB');
      draw(a.getContext('2d'), i - 1, t); draw(b.getContext('2d'), i, t);
      ditherMix(g, a, b, eio(p));
    }
  } else draw(g, i, t);
  for (const [text, t0, t1] of TAGS) boneTag(g, text, t, t0, t1);
  subtitle(g, t);
}

// draw shot k at song time tt into a context
function renderShot(gg, k, tt) {
  const sh = SHOTS[k], fn = SCENES[sh.name] || placeholder;
  gg.fillStyle = '#000'; gg.fillRect(0, 0, PW, PH);
  gg.save(); const cam = fn(gg, tt, tt - sh.t0, sh); gg.restore();
  // a scene may ask for a 2× camera: the 192×108 box at (cam.x, cam.y) is blown up to the whole frame
  if (cam && cam.zoom === 2) {
    const src = scratch('zoomSrc'); src.getContext('2d').drawImage(gg.canvas, 0, 0);
    gg.imageSmoothingEnabled = false; gg.drawImage(src, R(clamp(cam.x, 0, PW / 2)), R(clamp(cam.y, 0, PH / 2)), PW / 2, PH / 2, 0, 0, PW, PH);
  }
}
const shotByName = name => SHOTS.findIndex(s => s.name === name);

function placeholder(g, t, lt, s) {
  grad(g, ['#2A2440', '#4A3F6A']);
  ptext(g, s.name, PW / 2, PH / 2 - 6, { col: '#FFF3D6', outline: INK });
  ptext(g, lt.toFixed(1), PW / 2, PH / 2 + 10, { col: '#FFCB45', outline: INK });
}

// t < 0: a sheet of every character pose, for checking the sprites
function testSheet(g, T) {
  rect(g, 0, 0, PW, PH, '#9CC9A8');
  rect(g, 0, 70, PW, 1, '#7FAE8C'); rect(g, 0, 140, PW, 1, '#7FAE8C'); rect(g, 0, 210, PW, 1, '#7FAE8C');
  const poses = ['stand', 'walk', 'walk', 'walk', 'walk', 'run', 'sit', 'squat', 'sitFloor'];
  ['kid', 'teen', 'man'].forEach((age, row) => {
    poses.forEach((pose, i) => human(g, 16 + i * 26, 70 * row + 66, { age, pose, phase: i / 4, eyes: i === 6 ? 'happy' : 'open', mouth: i === 0 ? 'smile' : null, blush: i === 0, hat: age === 'kid' && i === 8 ? 'straw' : null }, T));
    human(g, 250, 70 * row + 66, { age, look: 'front', mouth: 'smile', blush: true }, T);
    human(g, 275, 70 * row + 66, { age, look: 'front', armN: 'cover', armF: 'cover' }, T);
    human(g, 300, 70 * row + 66, { age, armN: 'hold', armF: 'hold', eyes: 'closed' }, T);
    human(g, 345, 70 * row + 46, { age, pose: 'lie', eyes: 'closed' }, T);
  });
}
function testDogs(g, T) {
  rect(g, 0, 0, PW, PH, '#9CC9A8');
  const dp = ['stand', 'walk', 'walk', 'run', 'run', 'sit', 'lie', 'sleep', 'beg', 'jump'];
  dp.forEach((pose, i) => dog(g, 20 + i * 36, 60, { pose, phase: i / 4, collar: i % 2 === 0, tongue: i === 3, wag: 1 }, T + .1));
  dp.forEach((pose, i) => dog(g, 20 + i * 36, 130, { size: 'pup', pose, phase: i / 4, tongue: i === 0, wag: 1 }, T + .1));
  dp.forEach((pose, i) => dog(g, 20 + i * 36, 200, { pose, phase: i / 4, old: true, collar: true }, T + .1));
}
