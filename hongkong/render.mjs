// Renders scene.html (640x360 pixel frames) and upscales x3 with nearest neighbour to 1920x1080.
//   node render.mjs --stills=0,5.4,14        -> build/stills/t05.40.png ... (640x360, for checking)
//   node render.mjs --preview                -> build/preview.mp4  (1 sample per frame, 15 fps, fast)
//   node render.mjs                          -> build/hongkong_night.mp4 (2 jittered samples per frame, 30 fps, with build/music.wav)
// Options: --from=0 --to=50 --fps=30 --k=4 --out=path --audio=path|none --workers=2
import { createRequire } from "node:module"; import http from "node:http"; import fs from "node:fs"; import path from "node:path"; import { spawn } from "node:child_process";
const { chromium } = createRequire(import.meta.url)("playwright");
const args = process.argv.slice(2), has = (k) => args.includes(`--${k}`), opt = (k, d) => { const a = args.find((x) => x.startsWith(`--${k}=`)); return a ? a.slice(a.indexOf("=") + 1) : d; };
const DIR = path.dirname(new URL(import.meta.url).pathname), PREVIEW = has("preview"), STILLS = opt("stills", null);
const FPS = +opt("fps", PREVIEW ? 15 : 30), FROM = +opt("from", 0), TO = +opt("to", 50), K = +opt("k", PREVIEW ? 1 : 2), WORKERS = +opt("workers", 2), SHUT = +opt("shutter", .35);
const OUT = opt("out", path.join(DIR, "build", PREVIEW ? "preview.mp4" : "hongkong_night.mp4")), AUDIO = opt("audio", path.join(DIR, "build", "music.wav"));
const JIT = [[-.375, -.125], [.125, -.375], [.375, .125], [-.125, .375]];
const ctype = (f) => f.endsWith(".html") ? "text/html" : /\.m?js$/.test(f) ? "text/javascript" : f.endsWith(".css") ? "text/css" : f.endsWith(".woff2") ? "font/woff2" : f.endsWith(".woff") ? "font/woff" : "application/octet-stream";
const srv = http.createServer((q, r) => { const f = path.join(DIR, decodeURIComponent(q.url.split("?")[0])); fs.readFile(f, (e, b) => { if (e) { r.writeHead(404); r.end(); } else { r.writeHead(200, { "content-type": ctype(f) }); r.end(b); } }); }).listen(0);
const URL_ = `http://localhost:${srv.address().port}/scene.html${opt("query", "")}`;
const browser = await chromium.launch({ args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
async function openPage() { const p = await browser.newPage({ viewport: { width: 640, height: 360 } });
  p.on("pageerror", (e) => { console.error("[page]", e.message); process.exitCode = 1; }); p.on("console", (m) => { if (m.type() === "error") console.error("[console]", m.text()); });
  await p.goto(URL_); await p.waitForFunction(() => window.READY === true, null, { timeout: 900000 }); return p; }
const frameAt = async (p, ms, k) => { const dt = 1000 / FPS, list = [];
  for (let j = 0; j < k; j++) list.push([k === 1 ? ms : ms + ((j + .5) / k - .5) * dt * SHUT, k === 1 ? 0 : JIT[j % 4][0], k === 1 ? 0 : JIT[j % 4][1]]);
  await p.evaluate((l) => window.renderMany(l), list); return (await p.$("#frame")).screenshot({ type: "png" }); };
fs.mkdirSync(path.join(DIR, "build", "stills"), { recursive: true });
const T0 = Date.now();
if (STILLS) {
  const p = await openPage(); console.log("loaded in", ((Date.now() - T0) / 1000).toFixed(1), "s", await p.evaluate(() => window.__info()));
  for (const s of STILLS.split(",").map(Number)) { const f = path.join(DIR, "build", "stills", `t${s.toFixed(2).padStart(5, "0")}.png`); fs.writeFileSync(f, await frameAt(p, s * 1000, +opt("k", 2))); console.log("still", f); }
} else {
  const n = Math.round((TO - FROM) * FPS), frames = new Array(n);
  const tmp = path.join(DIR, "build", "frames"); fs.rmSync(tmp, { recursive: true, force: true }); fs.mkdirSync(tmp, { recursive: true });
  let next = 0, done = 0;
  const work = async (w) => { const p = await openPage(); while (true) { const i = next++; if (i >= n) break; const buf = await frameAt(p, FROM * 1000 + i * 1000 / FPS, K);
      fs.writeFileSync(path.join(tmp, `f${String(i).padStart(5, "0")}.png`), buf); done++;
      if (done % 30 === 0) console.log(`frame ${done}/${n}  ${((Date.now() - T0) / 60000).toFixed(1)} min`); } };
  await Promise.all(Array.from({ length: WORKERS }, (_, w) => work(w)));
  const useAudio = AUDIO !== "none" && fs.existsSync(AUDIO);
  const ff = ["-y", "-loglevel", "error", "-framerate", String(FPS), "-i", path.join(tmp, "f%05d.png"), ...(useAudio ? ["-ss", String(FROM), "-t", String(TO - FROM), "-i", AUDIO] : []),
    "-vf", "scale=1920:1080:flags=neighbor", "-c:v", "libx264", "-preset", PREVIEW ? "veryfast" : "slow", "-crf", opt("crf", PREVIEW ? "22" : "27"), "-tune", "animation", "-pix_fmt", "yuv420p",
    ...(useAudio ? ["-c:a", "aac", "-b:a", "192k", "-shortest"] : []), "-movflags", "+faststart", OUT];
  await new Promise((res, rej) => spawn("ffmpeg", ff, { stdio: "inherit" }).on("close", (c) => c ? rej(new Error("ffmpeg " + c)) : res()));
  if (!has("keep")) fs.rmSync(tmp, { recursive: true, force: true });
  console.log("done", OUT, ((Date.now() - T0) / 60000).toFixed(1), "min");
}
await browser.close(); srv.close();
