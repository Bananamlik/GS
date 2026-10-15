// usage: THREE_WORK=<dir> [CHROMIUM=<path>] [PLAYWRIGHT_PKG=<path>] node parity_run.mjs <html> <r128|r186> <outDir> [keys,comma|all] [--shots]
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)(process.env.PLAYWRIGHT_PKG || 'playwright');
import fs from 'fs';
import path from 'path';

const [html, ver, outDir, keysArg = 'all', ...flags] = process.argv.slice(2);
const shots = flags.includes('--shots');
/* W/node_modules/three = 0.186.1, W/r128/node_modules/three = 0.128.0 (npm i). */
const W = process.env.THREE_WORK || '.';
fs.mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({
  executablePath: process.env.CHROMIUM || undefined,
  args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'],
});
const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 }, deviceScaleFactor: 1 });
const page = await ctx.newPage();
const logs = [];
page.on('console', (m) => { if (['error', 'warning'].includes(m.type())) logs.push(m.type() + ': ' + m.text().slice(0, 400)); });
page.on('pageerror', (e) => logs.push('pageerror: ' + String(e.message).slice(0, 400)));

const CORS = { 'access-control-allow-origin': '*' };
await page.route('**/*', async (route) => {
  const u = route.request().url();
  if (u.startsWith('file://') || u.startsWith('data:') || u.startsWith('blob:')) return route.continue();
  if (/three\.min\.js/.test(u)) {
    let b = fs.readFileSync(`${W}/r128/node_modules/three/build/three.min.js`, 'utf8');
    const o = 'function ct(){const t=4294967295*Math.random()|0,e=4294967295*Math.random()|0,n=4294967295*Math.random()|0,i=4294967295*Math.random()|0;';
    if (!b.includes(o)) throw new Error('r128 uuid anchor');
    b = b.replace(o, 'let __u=0;function ct(){const t=++__u*2654435761|0,e=__u*40503|0,n=__u*69069|0,i=__u*1103515245|0;');
    return route.fulfill({ body: b, headers: { ...CORS, 'content-type': 'application/javascript' } });
  }
  let m = u.match(/three@0\.186\.\d\/build\/(three\.(?:module|core)\.js)/);
  if (m) {
    let b = fs.readFileSync(`${W}/node_modules/three/build/${m[1]}`, 'utf8');
    if (m[1] === 'three.core.js') {
      const o = ['const d0 = Math.random() * 0xffffffff | 0;','const d1 = Math.random() * 0xffffffff | 0;','const d2 = Math.random() * 0xffffffff | 0;','const d3 = Math.random() * 0xffffffff | 0;'];
      for (const x of o) if (!b.includes(x)) throw new Error('r186 uuid anchor');
      b = b.replace(o[0], 'globalThis.__u=(globalThis.__u||0)+1;const d0 = globalThis.__u*2654435761|0;').replace(o[1], 'const d1 = globalThis.__u*40503|0;').replace(o[2], 'const d2 = globalThis.__u*69069|0;').replace(o[3], 'const d3 = globalThis.__u*1103515245|0;');
    }
    return route.fulfill({ body: b, headers: { ...CORS, 'content-type': 'application/javascript' } });
  }
  return route.abort();
});

await page.addInitScript(() => {
  let q = [], t = 1000, s = 12345;
  window.requestAnimationFrame = (cb) => { q.push(cb); return q.length; };
  performance.now = () => t;
  Math.random = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
  window.__seed = (n) => { s = n >>> 0; };
  window.__step = (n, ms = 50) => { for (let i = 0; i < n; i++) { t += ms; const c = q; q = []; for (const f of c) f(t); } };
});

await page.goto('file://' + path.resolve(html));
await page.waitForFunction(() => typeof HEAD_KEYS !== 'undefined' && typeof select === 'function' && !!head, null, { timeout: 60000, polling: 100 }).catch((e) => { logs.push('WAIT FAIL ' + e.message.slice(0, 200)); });

const info = await page.evaluate(() => ({ rev: THREE.REVISION, keys: HEAD_KEYS.slice() })).catch(() => null);
console.log('three rev', info && info.rev, 'heads', info && info.keys.length);
if (!info) { console.log(logs.join('\n')); await browser.close(); process.exit(2); }

const keys = keysArg === 'all' ? info.keys : keysArg.split(',');
const result = {};
for (const k of keys) {
  const L0 = logs.length;
  const r = await page.evaluate((k) => {
    __seed(777); camFollow = true; camAuto = false; select(k);
    const out = { k, fireFrame: -1, peak: 0, peakTri: 0, rendErr: null };
    renderer.info.autoReset = false;
    for (let f = 0; f < 600; f++) {
      renderer.info.reset();
      __step(1);
      if (fired && out.fireFrame < 0) out.fireFrame = f;
      if (out.fireFrame >= 0) {
        const c = renderer.info.render.calls, tr = renderer.info.render.triangles;
        if (c > out.peak) out.peak = c;
        if (tr > out.peakTri) out.peakTri = tr;
        if (f - out.fireFrame >= 20) break;
      }
    }
    return out;
  }, k).catch((e) => ({ k, rendErr: e.message.slice(0, 200) }));
  result[k] = r;
  r.logIdx = [L0, null];
  if (shots) {
    // replay deterministic to capture frames
    const marks = [14, null, 3, 8, 16];
    await page.evaluate((k) => { __seed(777); camFollow = true; camAuto = false; select(k); window.__cf = -1; window.__ff = -1; }, k);
    const plan = [['fly', 15], ['i0', 3], ['i1', 8], ['i2', 16]];
    let ff = -1, f = 0;
    const want = { fly: 15 };
    const cap = async (tag) => { for (let a = 0; a < 3; a++) { try { return await page.screenshot({ path: `${outDir}/${k}_${tag}.png`, timeout: 120000 }); } catch (e) { logs.push('SHOTFAIL ' + k + ' ' + tag + ' try' + a); } } };
    // fly frame 15
    await page.evaluate(() => __step(15));
    await cap('fly');
    // advance to fire
    let fireF = await page.evaluate(() => { let n = 0; while (!fired && n < 600) { __step(1); n++; } return n; });
    for (const [tag, off] of [['i3', 3], ['i8', 8], ['i16', 16]]) {
      const prev = tag === 'i3' ? 3 : tag === 'i8' ? 5 : 8;
      await page.evaluate((p) => __step(p), prev);
      await cap(tag);
    }
  }
  r.logIdx[1] = logs.length;
  if (!(Object.keys(result).length % 8)) process.stdout.write('.');
}
console.log();
fs.writeFileSync(`${outDir}/_result.json`, JSON.stringify({ rev: info.rev, result, logs }, null, 1));
const uniq = [...new Set(logs)];
console.log('log lines', logs.length, 'unique', uniq.length);
console.log(uniq.slice(0, 25).join('\n'));
await browser.close();
