// Renders 人死后会去哪 to build/afterlife.mp4 (1920×1080, 30 fps, H.264 + AAC).
// The page synthesizes the soundtrack (voices, music, effects) from score.js; frames are drawn from the same score.
//   node render.mjs                 full render
//   node render.mjs --stills 1,3.2  JPEG stills in build/stills/
import { createServer } from 'node:http';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { spawn, execSync } from 'node:child_process';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
let chromium;
try { ({ chromium } = require('playwright')); }
catch { ({ chromium } = require(execSync('npm root -g').toString().trim() + '/playwright')); }
const ROOT = path.dirname(new URL(import.meta.url).pathname), BUILD = path.join(ROOT, 'build'), FPS = 30, SR = 44100;
const ffmpeg = process.env.FFMPEG || execSync(`python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"`).toString().trim();
const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.woff2': 'font/woff2', '.ttf': 'font/ttf' };
const server = createServer(async (req, res) => {
  try { const p = path.join(ROOT, decodeURIComponent(req.url.split('?')[0])); res.writeHead(200, { 'content-type': TYPES[path.extname(p)] || 'application/octet-stream' }); res.end(await readFile(p)); }
  catch { res.writeHead(404); res.end(); }
}).listen(0);
await mkdir(BUILD, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('pageerror', e => console.error('page error:', e.message));
await page.goto(`http://localhost:${server.address().port}/index.html?render`);
await page.evaluate(() => window.ready);
const DUR = await page.evaluate(() => DUR);
const grab = q => page.evaluate(q => document.getElementById('c').toDataURL('image/jpeg', q), q);
function wav(pcm) { const h = Buffer.alloc(44); h.write('RIFF', 0); h.writeUInt32LE(36 + pcm.length, 4); h.write('WAVE', 8); h.write('fmt ', 12); h.writeUInt32LE(16, 16); h.writeUInt16LE(1, 20); h.writeUInt16LE(2, 22); h.writeUInt32LE(SR, 24); h.writeUInt32LE(SR * 4, 28); h.writeUInt16LE(4, 32); h.writeUInt16LE(16, 34); h.write('data', 36); h.writeUInt32LE(pcm.length, 40); return Buffer.concat([h, pcm]); }

if (process.argv[2] === '--stills') {
  await mkdir(path.join(BUILD, 'stills'), { recursive: true });
  for (const s of process.argv[3].split(',')) { await page.evaluate(t => window.renderFrame(t), +s); await writeFile(path.join(BUILD, `stills/t${(+s).toFixed(2)}.jpg`), Buffer.from((await grab(.9)).split(',')[1], 'base64')); }
} else {
  const wavPath = path.join(BUILD, 'audio.wav');
  await writeFile(wavPath, wav(Buffer.from(await page.evaluate(() => window.renderAudioBase64()), 'base64')));
  const out = path.join(BUILD, 'afterlife.mp4');
  const ff = spawn(ffmpeg, ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-i', wavPath, '-map', '0:v', '-map', '1:a',
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-maxrate', '4M', '-bufsize', '8M', '-pix_fmt', 'yuv420p', '-r', String(FPS), '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const total = Math.round(DUR * FPS);
  for (let i = 0; i < total; i++) {
    await page.evaluate(t => window.renderFrame(t), i / FPS);
    if (!ff.stdin.write(Buffer.from((await grab(.95)).split(',')[1], 'base64'))) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise((r, j) => ff.on('close', c => c === 0 ? r() : j(new Error('ffmpeg ' + c))));
  console.log('wrote', out);
}
await browser.close(); server.close();
