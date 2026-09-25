// Renders index.html frame-by-frame in headless Chromium and muxes it with
// build/music.wav into build/opus55_capcut.mp4 (1920×1080, 30 fps, H.264 + AAC).
//
//   node render.mjs                 -> full video
//   node render.mjs --stills 0,5,12 -> PNG stills in build/stills/ for checking
import { createServer } from 'node:http';
import { readFile, mkdir } from 'node:fs/promises';
import { spawn, execSync } from 'node:child_process';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(execSync('npm root -g').toString().trim() + '/playwright')); }

const ROOT = path.dirname(new URL(import.meta.url).pathname);
const FPS = 30, DUR = 30;
const TYPES = { '.html': 'text/html', '.ttf': 'font/ttf', '.wav': 'audio/wav', '.js': 'text/javascript' };

const server = createServer(async (req, res) => {
  try {
    const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0]));
    res.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' });
    res.end(await readFile(p));
  } catch { res.writeHead(404); res.end(); }
}).listen(0);
const port = server.address().port;

const ffmpeg = process.env.FFMPEG || execSync(`python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`).toString().trim();
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
await page.goto(`http://localhost:${port}/index.html?render`);
await page.evaluate(() => window.ready);
const grab = q => page.evaluate(q => document.getElementById('c').toDataURL(q ? 'image/jpeg' : 'image/png', q || undefined), q);

const stillsArg = process.argv.indexOf('--stills');
if (stillsArg > 0) {
  await mkdir(path.join(ROOT, 'build/stills'), { recursive: true });
  const { writeFile } = await import('node:fs/promises');
  for (const s of process.argv[stillsArg + 1].split(',')) {
    await page.evaluate(t => window.renderFrame(t), +s);
    const url = await grab(0.9);
    await writeFile(path.join(ROOT, `build/stills/t${(+s).toFixed(2)}.jpg`), Buffer.from(url.split(',')[1], 'base64'));
  }
} else {
  const out = path.join(ROOT, 'build/opus55_capcut.mp4');
  const ff = spawn(ffmpeg, ['-y', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-i', path.join(ROOT, 'build/music.wav'),
    '-map', '0:v', '-map', '1:a',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', String(FPS),
    '-c:a', 'aac', '-b:a', '192k', '-ar', '44100', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = FPS * DUR;
  for (let i = 0; i < total; i++) {
    await page.evaluate(t => window.renderFrame(t), i / FPS);
    const url = await grab(0.95);
    if (!ff.stdin.write(Buffer.from(url.split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 90 === 0) process.stdout.write(`frame ${i}/${total}\n`);
  }
  ff.stdin.end();
  await new Promise((r, j) => ff.on('close', c => c === 0 ? r() : j(new Error('ffmpeg exit ' + c))));
  console.log('wrote', out);
}
await browser.close();
server.close();
