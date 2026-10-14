// Renders 几分之几 · 像素 MV over the user's own copy of the song. Frames are drawn at 480×270 and
// scaled up 4× with nearest-neighbour by ffmpeg, so every art pixel is a crisp 4×4 block in the 1920×1080 video.
//   node render.mjs <song.mp3>               decode the song to build/bgm.wav, render build/fraction.mp4, check alignment
//   node render.mjs <song.mp3> --lyrics a.lrc  same, but the subtitles show the lines of your own .lrc file
//   node render.mjs --stills 20,70.5         PNG stills (1920×1080) in build/stills/
// The song and any lyrics file are the user's: they stay in build/ (git-ignored) and are never committed.
import { createServer } from 'node:http';
import { readFile, writeFile, mkdir, rm } from 'node:fs/promises';
import { spawn, execSync, execFileSync } from 'node:child_process';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(execSync('npm root -g').toString().trim() + '/playwright')); }
const ROOT = path.dirname(new URL(import.meta.url).pathname), BUILD = path.join(ROOT, 'build'), FPS = 30, SR = 44100;
const ffmpeg = process.env.FFMPEG || execSync(`python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`).toString().trim();
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2', '.wav': 'audio/wav' };
const args = process.argv.slice(2), opt = n => { const i = args.indexOf(n); return i >= 0 ? args.splice(i, 2)[1] : null; };
const stills = opt('--stills'), lrc = opt('--lyrics'), song = args[0];
await mkdir(BUILD, { recursive: true });

// an .lrc file ("[01:08.50]text" per line) becomes build/lyrics.js; without one, the original subtitles are used
if (lrc) {
  const lines = (await readFile(lrc, 'utf8')).split(/\r?\n/).flatMap(l => {
    const tags = [...l.matchAll(/\[(\d+):(\d+(?:\.\d+)?)\]/g)], text = l.replace(/\[[^\]]*\]/g, '').trim();
    return tags.map(m => ({ t: +m[1] * 60 + +m[2], text }));
  }).sort((a, b) => a.t - b.t);
  await writeFile(path.join(BUILD, 'lyrics.js'), 'const USER_LYRICS = ' + JSON.stringify(lines) + ';\n');
  console.log(`subtitles: ${lines.length} lines from ${lrc}`);
} else if (!stills) await rm(path.join(BUILD, 'lyrics.js'), { force: true });

const server = createServer(async (req, res) => {
  try { const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0])), body = await readFile(p); res.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' }); res.end(body); }
  catch { res.writeHead(404); res.end(); }
}).listen(0);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 960, height: 540 } });
page.on('pageerror', e => console.error('page error:', e.message));
await page.goto(`http://localhost:${server.address().port}/index.html?render`);
await page.evaluate(() => window.ready);
const DUR = await page.evaluate(() => DUR);
const grab = () => page.evaluate(() => document.getElementById('c').toDataURL('image/png'));
const pcm = f => { const r = execFileSync(ffmpeg, ['-v', 'error', '-i', f, '-ac', '1', '-ar', String(SR), '-f', 's16le', '-'], { maxBuffer: 1 << 30 }); const x = new Float32Array(r.length / 2); for (let i = 0; i < x.length; i++) x[i] = r.readInt16LE(i * 2) / 32768; return x; };

if (stills) {
  await mkdir(path.join(BUILD, 'stills'), { recursive: true });
  for (const s of stills.split(',')) {
    await page.evaluate(t => window.renderFrame(t), +s);
    const small = path.join(BUILD, 'stills/_frame.png');
    await writeFile(small, Buffer.from((await grab()).split(',')[1], 'base64'));
    execFileSync(ffmpeg, ['-y', '-v', 'error', '-i', small, '-vf', 'scale=1920:1080:flags=neighbor', path.join(BUILD, `stills/t${(+s).toFixed(2)}.png`)]);
  }
} else {
  const wav = path.join(BUILD, 'bgm.wav');
  if (song) execFileSync(ffmpeg, ['-y', '-v', 'error', '-i', song, '-vn', '-ac', '2', '-ar', String(SR), '-c:a', 'pcm_s16le', wav]);
  const out = path.join(BUILD, 'fraction.mp4');
  const ff = spawn(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-', '-i', wav, '-map', '0:v', '-map', '1:a',
    '-vf', 'scale=1920:1080:flags=neighbor', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-tune', 'animation', '-maxrate', '6M', '-bufsize', '12M', '-pix_fmt', 'yuv420p', '-r', String(FPS),
    '-c:a', 'aac', '-b:a', '192k', '-t', String(DUR), '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.round(DUR * FPS);
  for (let i = 0; i < total; i++) {
    await page.evaluate(t => window.renderFrame(t), i / FPS);
    if (!ff.stdin.write(Buffer.from((await grab()).split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 600 === 0) console.log(`frame ${i}/${total}`);
  }
  ff.stdin.end(); await new Promise((r, j) => ff.on('close', c => c === 0 ? r() : j(new Error('ffmpeg ' + c))));
  // alignment: cross-correlate the MP4's audio with the song
  const a = pcm(wav), b = pcm(out), n = Math.min(a.length, b.length, SR * 60); let best = -Infinity, lag = 0;
  for (let L = -2000; L <= 2000; L++) { let s = 0; for (let i = SR * 20; i < n - 3000; i += 12) s += a[i] * b[i + L]; if (s > best) { best = s; lag = L; } }
  console.log('wrote', out, `\nalignment: soundtrack offset ${lag} samples (${(lag / SR * 1000).toFixed(2)} ms) from the song`);
}
await browser.close(); server.close();
