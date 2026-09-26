// Renders the Claude Code 电音派对 to build/party.mp4 (1920×1080, 30 fps, H.264 + AAC) — all from JavaScript:
//   1. the page synthesizes the soundtrack from score.js with an OfflineAudioContext -> build/music.wav
//   2. every frame is drawn from the same score and piped to ffmpeg
//   3. the audio is decoded back out of the finished MP4 and every kick onset is
//      measured against its scheduled time, so "on the beat" is checked, not assumed.
//
//   node render.mjs                  full render + sync report
//   node render.mjs --stills 1,12.5  PNG/JPEG stills in build/stills/ (no video)
//   node render.mjs --check          only re-run the sync report on build/party.mp4
import { createServer } from 'node:http';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { spawn, execSync, execFileSync } from 'node:child_process';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(execSync('npm root -g').toString().trim() + '/playwright')); }

const ROOT = path.dirname(new URL(import.meta.url).pathname);
const BUILD = path.join(ROOT, 'build');
const FPS = 30, DUR = 60, SR = 44100, BPM = 128;
const ffmpeg = process.env.FFMPEG || execSync(`python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`).toString().trim();
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2', '.ttf': 'font/ttf' };
await mkdir(BUILD, { recursive: true });

const server = createServer(async (req, res) => {
  try { const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0])); res.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' }); res.end(await readFile(p)); }
  catch { res.writeHead(404); res.end(); }
}).listen(0);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('pageerror', e => console.error('page error:', e.message));
await page.goto(`http://localhost:${server.address().port}/index.html?render`);
await page.evaluate(() => window.ready);
const score = await page.evaluate(() => window.scoreTimes());
const grab = q => page.evaluate(q => document.getElementById('c').toDataURL('image/jpeg', q), q);

function wavHeader(bytes) {
  const h = Buffer.alloc(44);
  h.write('RIFF', 0); h.writeUInt32LE(36 + bytes, 4); h.write('WAVE', 8); h.write('fmt ', 12);
  h.writeUInt32LE(16, 16); h.writeUInt16LE(1, 20); h.writeUInt16LE(2, 22); h.writeUInt32LE(SR, 24);
  h.writeUInt32LE(SR * 4, 28); h.writeUInt16LE(4, 32); h.writeUInt16LE(16, 34); h.write('data', 36); h.writeUInt32LE(bytes, 40);
  return h;
}

// ---- sync check: onsets in the low band vs. the score
// envelope: 2-pole low-pass (~150 Hz), rectified, 1 ms release
function envelope(x) {
  const a = Math.exp(-2 * Math.PI * 150 / SR), b = Math.exp(-1 / (0.001 * SR)), env = new Float32Array(x.length);
  let y1 = 0, y2 = 0, e = 0;
  for (let i = 0; i < x.length; i++) { y1 = (1 - a) * x[i] + a * y1; y2 = (1 - a) * y1 + a * y2; e = Math.max(Math.abs(y2), b * e); env[i] = e; }
  return env;
}
// onset = first 20% crossing between the level just before t and the peak that follows (ms, relative to t)
function onset(env, t) {
  const ia = Math.round((t - 0.04) * SR), ib = Math.round((t - 0.004) * SR), ic = Math.round((t + 0.08) * SR);
  let base = 0; for (let i = ia; i < ib; i++) base += env[i]; base /= (ib - ia);
  let peak = 0, ip = ib; for (let i = ib; i < ic; i++) if (env[i] > peak) { peak = env[i]; ip = i; }
  const thr = base + 0.2 * (peak - base);
  for (let i = ib; i <= ip; i++) if (env[i] >= thr) return (i / SR - t) * 1000;
  return (ip / SR - t) * 1000;
}
const pcmToFloat = raw => { const x = new Float32Array(raw.length / 2); for (let i = 0; i < x.length; i++) x[i] = raw.readInt16LE(i * 2) / 32768; return x; };
// detector latency, measured on isolated hits rendered by the real instruments at exactly t = 0.2 s
const LATENCY = {};
for (const style of ['house', 'build', 'drop'])
  LATENCY[style] = onset(envelope(pcmToFloat(Buffer.from(await page.evaluate(k => window.renderReference(k), style), 'base64'))), 0.2);

function syncReport(file) {
  const raw = execFileSync(ffmpeg, ['-v', 'error', '-i', file, '-ac', '1', '-ar', String(SR), '-f', 's16le', '-'], { maxBuffer: 1 << 30 });
  const env = envelope(pcmToFloat(raw));
  // (the kick at t = 0 is skipped: its 'level before' window would start before the file)
  const events = score.kick.filter(k => k.t >= 0.05).map(k => ({ t: k.t, kind: k.style }));
  const offs = events.map(ev => onset(env, ev.t) - LATENCY[ev.kind]);
  if (process.env.DETAIL) events.forEach((ev, i) => { if (Math.abs(offs[i]) > 5) console.log(`    bar ${Math.floor(ev.t / (240 / BPM))} beat ${Math.round(ev.t / (60 / BPM)) % 4} (${ev.kind}, t=${ev.t.toFixed(3)}): ${offs[i].toFixed(1)} ms`); });
  const abs = offs.map(Math.abs).sort((p, q) => p - q), sorted = [...offs].sort((p, q) => p - q);
  return [
    `sync check on ${path.basename(file)}: ${offs.length} scheduled kicks`,
    `  detector latency (isolated kicks): house ${LATENCY.house.toFixed(1)} ms, build ${LATENCY.build.toFixed(1)} ms, drop ${LATENCY.drop.toFixed(1)} ms`,
    `  error after removing it: median ${sorted[offs.length >> 1].toFixed(1)} ms, 95th pct |err| ${abs[Math.floor(abs.length * .95)].toFixed(1)} ms, max |err| ${abs[abs.length - 1].toFixed(1)} ms`,
    `  within ±5 ms: ${offs.filter(o => Math.abs(o) <= 5).length}/${offs.length}, within ±10 ms: ${offs.filter(o => Math.abs(o) <= 10).length}/${offs.length}`,
    `  video: ${BPM} BPM = ${(60 / BPM * FPS).toFixed(3)} frames per beat at ${FPS} fps; each hit is drawn on the nearest frame (≤ ${(500 / FPS).toFixed(1)} ms)`,
  ].join('\n');
}

const arg = process.argv[2];
if (arg === '--stills') {
  await mkdir(path.join(BUILD, 'stills'), { recursive: true });
  for (const s of process.argv[3].split(',')) {
    await page.evaluate(t => window.renderFrame(t), +s);
    await writeFile(path.join(BUILD, `stills/t${(+s).toFixed(2)}.jpg`), Buffer.from((await grab(0.9)).split(',')[1], 'base64'));
  }
} else if (arg === '--check') {
  console.log(syncReport(path.join(BUILD, 'music.wav')));
  console.log(syncReport(path.join(BUILD, 'party.mp4')));
} else {
  const pcm = Buffer.from(await page.evaluate(() => window.renderAudioBase64()), 'base64');
  const wav = path.join(BUILD, 'music.wav');
  await writeFile(wav, Buffer.concat([wavHeader(pcm.length), pcm]));
  console.log('wrote', wav);
  const out = path.join(BUILD, 'party.mp4');
  const ff = spawn(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-i', wav,
    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-maxrate', '3.6M', '-bufsize', '7.2M', '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < FPS * DUR; i++) {
    await page.evaluate(t => window.renderFrame(t), i / FPS);
    if (!ff.stdin.write(Buffer.from((await grab(0.95)).split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 300 === 0) console.log(`frame ${i}/${FPS * DUR}`);
  }
  ff.stdin.end();
  await new Promise((r, j) => ff.on('close', c => c === 0 ? r() : j(new Error('ffmpeg ' + c))));
  console.log('wrote', out);
  console.log(syncReport(out));
}
await browser.close();
server.close();
