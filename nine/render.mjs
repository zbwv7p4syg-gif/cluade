// Renders 九分之九 · 像素 MV over the user's own copy of the song. Frames are drawn at 384×216 by several headless
// Chromium pages in parallel, then ffmpeg scales them 5× with nearest-neighbour (every art pixel becomes a crisp
// 5×5 block in the 1920×1080 video) and muxes the song.
//   node render.mjs <song.mp3> --lyrics a.lrc   decode the song to build/bgm.wav, render build/nine.mp4 with your subtitles
//   node render.mjs --stills 20,70.5           PNG stills (1920×1080) in build/stills/
//   node render.mjs --sheet 20,30,40           one contact sheet of 384×216 frames, build/stills/sheet.png
// The song and the lyrics file are the user's: they stay in build/ (git-ignored) and are never committed.
import { createServer } from 'node:http';
import { readFile, writeFile, mkdir, rm } from 'node:fs/promises';
import { spawn, execSync, execFileSync } from 'node:child_process';
import os from 'node:os';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(execSync('npm root -g').toString().trim() + '/playwright')); }
const ROOT = path.dirname(new URL(import.meta.url).pathname), BUILD = path.join(ROOT, 'build'), FPS = 30, SR = 44100, SCALE = 5;
const which = b => { try { return execSync(`command -v ${b}`).toString().trim(); } catch { return null; } };
const ffmpeg = process.env.FFMPEG || which('ffmpeg') || execSync(`python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`).toString().trim();
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2', '.wav': 'audio/wav' };
const args = process.argv.slice(2), opt = n => { const i = args.indexOf(n); return i >= 0 ? args.splice(i, 2)[1] : null; };
const stills = opt('--stills'), sheet = opt('--sheet'), lrc = opt('--lyrics'), workers = +(opt('--workers') || Math.max(1, Math.min(6, os.cpus().length)));
const range = (opt('--range') || '').split(',').filter(Boolean).map(Number), song = args[0];
await mkdir(BUILD, { recursive: true });

// an .lrc file ("[01:08.50]text" per line; an empty line ends the subtitle) becomes build/lyrics.js
if (lrc) {
  const lines = (await readFile(lrc, 'utf8')).split(/\r?\n/).flatMap(l => {
    const tags = [...l.matchAll(/\[(\d+):(\d+(?:\.\d+)?)\]/g)], text = l.replace(/\[[^\]]*\]/g, '').trim();
    return tags.map(m => ({ t: +m[1] * 60 + +m[2], text }));
  }).sort((a, b) => a.t - b.t);
  await writeFile(path.join(BUILD, 'lyrics.js'), 'const USER_LYRICS = ' + JSON.stringify(lines) + ';\n');
  console.log(`subtitles: ${lines.filter(l => l.text).length} lines from ${lrc}`);
}

const server = createServer(async (req, res) => {
  try { const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0])), body = await readFile(p); res.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' }); res.end(body); }
  catch { res.writeHead(404); res.end(); }
}).listen(0);
const browser = await chromium.launch();
const openPage = async () => {
  const page = await browser.newPage({ viewport: { width: 400, height: 240 } });
  page.on('pageerror', e => console.error('page error:', e.message));
  page.on('console', m => { if (m.type() === 'error') console.error('console:', m.text()); });
  await page.goto(`http://localhost:${server.address().port}/index.html?render`);
  await page.evaluate(() => window.ready);
  return page;
};
const grab = (page, t) => page.evaluate(t => { window.renderFrame(t); return document.getElementById('c').toDataURL('image/png'); }, t);
const png = url => Buffer.from(url.split(',')[1], 'base64');
const pcm = f => { const r = execFileSync(ffmpeg, ['-v', 'error', '-i', f, '-ac', '1', '-ar', String(SR), '-f', 's16le', '-'], { maxBuffer: 1 << 30 }); const x = new Float32Array(r.length / 2); for (let i = 0; i < x.length; i++) x[i] = r.readInt16LE(i * 2) / 32768; return x; };

if (stills || sheet) {
  const page = await openPage(), dir = path.join(BUILD, 'stills');
  await mkdir(dir, { recursive: true });
  const ts = (stills || sheet).split(',').map(Number);
  const files = [];
  for (const s of ts) {
    const small = path.join(dir, `s${s.toFixed(2)}.png`);
    await writeFile(small, png(await grab(page, s)));
    files.push(small);
    if (stills) execFileSync(ffmpeg, ['-y', '-v', 'error', '-i', small, '-vf', `scale=${384 * SCALE}:${216 * SCALE}:flags=neighbor`, path.join(dir, `t${s.toFixed(2)}.png`)]);
  }
  if (sheet) {
    const cols = Math.min(3, files.length), rows = Math.ceil(files.length / cols);
    const inputs = files.flatMap(f => ['-i', f]);
    while (files.length < cols * rows) { inputs.push('-f', 'lavfi', '-i', 'color=c=black:s=384x216'); files.push(null); }
    const layout = files.map((_, i) => `${(i % cols) * 388}_${Math.floor(i / cols) * 220}`).join('|');
    execFileSync(ffmpeg, ['-y', '-v', 'error', ...inputs, '-filter_complex', `xstack=inputs=${files.length}:layout=${layout}:fill=gray,scale=iw*2:ih*2:flags=neighbor`, '-frames:v', '1', path.join(dir, 'sheet.png')]);
    console.log('wrote', path.join(dir, 'sheet.png'));
  }
} else {
  const wav = path.join(BUILD, 'bgm.wav');
  if (song) execFileSync(ffmpeg, ['-y', '-v', 'error', '-i', song, '-vn', '-ac', '2', '-ar', String(SR), '-c:a', 'pcm_s16le', wav]);
  const frames = path.join(BUILD, 'frames');
  const probe = await openPage(), DUR = await probe.evaluate(() => DUR); await probe.close();
  const total = Math.round(DUR * FPS), [f0, f1] = range.length ? [Math.round(range[0] * FPS), Math.round(range[1] * FPS)] : [0, total];
  if (!range.length) await rm(frames, { recursive: true, force: true });
  await mkdir(frames, { recursive: true });
  let done = 0; const t0 = Date.now();
  await Promise.all(Array.from({ length: workers }, async (_, w) => {
    const page = await openPage();
    for (let i = f0 + w; i < f1; i += workers) {
      await writeFile(path.join(frames, `${String(i).padStart(5, '0')}.png`), png(await grab(page, i / FPS)));
      if (++done % 600 === 0) console.log(`frame ${done}/${f1 - f0} (${((Date.now() - t0) / 1000).toFixed(0)} s)`);
    }
    await page.close();
  }));
  if (!range.length) {
    const out = path.join(BUILD, 'nine.mp4');
    execFileSync(ffmpeg, ['-y', '-v', 'error', '-framerate', String(FPS), '-i', path.join(frames, '%05d.png'), '-i', wav, '-map', '0:v', '-map', '1:a',
      '-vf', `scale=${384 * SCALE}:${216 * SCALE}:flags=neighbor`, '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-tune', 'animation', '-maxrate', '8M', '-bufsize', '16M',
      '-pix_fmt', 'yuv420p', '-r', String(FPS), '-c:a', 'aac', '-b:a', '192k', '-t', String(DUR), '-movflags', '+faststart', out], { stdio: 'inherit' });
    // alignment: cross-correlate the MP4's audio with the song
    const a = pcm(wav), b = pcm(out), n = Math.min(a.length, b.length, SR * 60); let best = -Infinity, lag = 0;
    for (let L = -2000; L <= 2000; L++) { let s = 0; for (let i = SR * 20; i < n - 3000; i += 12) s += a[i] * b[i + L]; if (s > best) { best = s; lag = L; } }
    console.log('wrote', out, `\nalignment: soundtrack offset ${lag} samples (${(lag / SR * 1000).toFixed(2)} ms) from the song`);
  }
}
await browser.close(); server.close();
