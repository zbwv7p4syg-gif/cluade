// Renders 富士山下 · Claude Code 版 at 30 fps over the user's own copy of the song.
//   node render.mjs <song.mp3>        decode the song to build/bgm.wav, render build/fuji.mp4, check alignment
//   node render.mjs --stills 3,25.1   JPEG stills in build/stills/ (needs build/bgm.wav only for playback, not stills)
// The song is the user's file: it stays in build/ (git-ignored) and is never committed.
import { createServer } from 'node:http';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { spawn, execSync, execFileSync } from 'node:child_process';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(execSync('npm root -g').toString().trim() + '/playwright')); }
const ROOT = path.dirname(new URL(import.meta.url).pathname), BUILD = path.join(ROOT, 'build'), FPS = 30, SR = 44100;
const ffmpeg = process.env.FFMPEG || execSync(`python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`).toString().trim();
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2', '.ttf': 'font/ttf', '.wav': 'audio/wav' };
await mkdir(BUILD, { recursive: true });
const server = createServer(async (req, res) => {
  try { const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0])), body = await readFile(p); res.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' }); res.end(body); }
  catch { res.writeHead(404); res.end(); }
}).listen(0);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('pageerror', e => console.error('page error:', e.message));
await page.goto(`http://localhost:${server.address().port}/index.html?render`);
await page.evaluate(() => window.ready);
const DUR = await page.evaluate(() => DUR);
const grab = q => page.evaluate(q => document.getElementById('c').toDataURL('image/jpeg', q), q);
const pcm = f => { const r = execFileSync(ffmpeg, ['-v', 'error', '-i', f, '-ac', '1', '-ar', String(SR), '-f', 's16le', '-'], { maxBuffer: 1 << 30 }); const x = new Float32Array(r.length / 2); for (let i = 0; i < x.length; i++) x[i] = r.readInt16LE(i * 2) / 32768; return x; };

if (process.argv[2] === '--stills') {
  await mkdir(path.join(BUILD, 'stills'), { recursive: true });
  for (const s of process.argv[3].split(',')) { await page.evaluate(t => window.renderFrame(t), +s); await writeFile(path.join(BUILD, `stills/t${(+s).toFixed(2)}.jpg`), Buffer.from((await grab(.9)).split(',')[1], 'base64')); }
} else {
  const wav = path.join(BUILD, 'bgm.wav');
  if (process.argv[2]) execFileSync(ffmpeg, ['-y', '-v', 'error', '-i', process.argv[2], '-vn', '-ac', '2', '-ar', String(SR), '-c:a', 'pcm_s16le', wav]);
  const out = path.join(BUILD, 'fuji.mp4');
  const ff = spawn(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-i', wav, '-map', '0:v', '-map', '1:a',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-maxrate', '3.5M', '-bufsize', '7M', '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-af', `afade=t=out:st=${(DUR - 0.9).toFixed(2)}:d=0.85`, '-c:a', 'aac', '-b:a', '192k', '-t', String(DUR), '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.round(DUR * FPS);
  for (let i = 0; i < total; i++) {
    await page.evaluate(t => window.renderFrame(t), i / FPS);
    if (!ff.stdin.write(Buffer.from((await grab(.93)).split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 300 === 0) console.log(`frame ${i}/${total}`);
  }
  ff.stdin.end(); await new Promise((r, j) => ff.on('close', c => c === 0 ? r() : j(new Error('ffmpeg ' + c))));
  // alignment: cross-correlate the MP4's audio with the song (before the fade-out)
  const a = pcm(wav), b = pcm(out), n = Math.min(a.length, b.length, SR * 20); let best = -Infinity, lag = 0;
  for (let L = -2000; L <= 2000; L++) { let s = 0; for (let i = SR * 3; i < n - 3000; i += 6) s += a[i] * b[i + L]; if (s > best) { best = s; lag = L; } }
  console.log('wrote', out, `\nalignment: soundtrack offset ${lag} samples (${(lag / SR * 1000).toFixed(2)} ms) from the song`);
}
await browser.close(); server.close();
