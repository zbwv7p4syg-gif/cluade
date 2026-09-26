// Renders index.html at 60 fps and muxes it with build/bgm.wav into build/claude_song.mp4.
// Afterwards the audio is decoded back out of the MP4 and cross-correlated with bgm.wav,
// so we know the soundtrack sits exactly where the beat map expects it.
//
//   node render.mjs                  full render + alignment check
//   node render.mjs --stills 1,7.2   JPEG stills in build/stills/
import { createServer } from 'node:http';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { spawn, execSync, execFileSync } from 'node:child_process';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(execSync('npm root -g').toString().trim() + '/playwright')); }

const ROOT = path.dirname(new URL(import.meta.url).pathname), BUILD = path.join(ROOT, 'build');
const FPS = 60, SR = 44100;
const ffmpeg = process.env.FFMPEG || execSync(`python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`).toString().trim();
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.wav': 'audio/wav' };
const server = createServer(async (req, res) => {
  try { const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0])); res.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' }); res.end(await readFile(p)); }
  catch { res.writeHead(404); res.end(); }
}).listen(0);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('pageerror', e => console.error('page error:', e.message));
await page.goto(`http://localhost:${server.address().port}/index.html?render`);
await page.evaluate(() => window.ready);
const DUR = await page.evaluate(() => BEATMAP.duration);
const grab = q => page.evaluate(q => document.getElementById('c').toDataURL('image/jpeg', q), q);

const pcm = file => { const r = execFileSync(ffmpeg, ['-v', 'error', '-i', file, '-ac', '1', '-ar', String(SR), '-f', 's16le', '-'], { maxBuffer: 1 << 30 }); const x = new Float32Array(r.length / 2); for (let i = 0; i < x.length; i++) x[i] = r.readInt16LE(i * 2) / 32768; return x; };
function alignment(mp4) {
  const a = pcm(path.join(BUILD, 'bgm.wav')), b = pcm(mp4), n = Math.min(a.length, b.length, SR * 6);
  let best = -Infinity, lag = 0;
  for (let L = -2000; L <= 2000; L++) { let s = 0; for (let i = 3000; i < n - 3000; i += 4) s += a[i] * b[i + L]; if (s > best) { best = s; lag = L; } }
  return `alignment: the MP4's audio is offset by ${lag} samples (${(lag / SR * 1000).toFixed(2)} ms) from the analysed track`;
}

if (process.argv[2] === '--stills') {
  await mkdir(path.join(BUILD, 'stills'), { recursive: true });
  for (const s of process.argv[3].split(',')) { await page.evaluate(t => window.renderFrame(t), +s); await writeFile(path.join(BUILD, `stills/t${(+s).toFixed(2)}.jpg`), Buffer.from((await grab(.9)).split(',')[1], 'base64')); }
} else {
  const out = path.join(BUILD, 'claude_song.mp4');
  const ff = spawn(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-i', path.join(BUILD, 'bgm.wav'),
    '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-maxrate', '8M', '-bufsize', '16M', '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.floor(DUR * FPS);
  for (let i = 0; i < total; i++) {
    await page.evaluate(t => window.renderFrame(t), i / FPS);
    if (!ff.stdin.write(Buffer.from((await grab(.95)).split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 240 === 0) console.log(`frame ${i}/${total}`);
  }
  ff.stdin.end();
  await new Promise((r, j) => ff.on('close', c => c === 0 ? r() : j(new Error('ffmpeg ' + c))));
  console.log('wrote', out);
  console.log(alignment(out));
}
await browser.close(); server.close();
