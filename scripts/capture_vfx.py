"""Probe v3: time series for the 49 suspect effects of the VFX anchor audit (SwiftShader, not a real GPU). Not for merge.

Usage: python3 scripts/capture_vfx.py OUTDIR  (serve the repo on 127.0.0.1:8000 first)
A: Lab beam preview with the welcome dialog closed.  B: violet fault over time.  D: lance at two aims.
S: every suspect at fixed times, side and top view, plus effect root positions.
Every step is best effort and logged.
"""
import json, os, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else 'vfx-captures')
(OUT / 'series').mkdir(parents=True, exist_ok=True)
URL = os.environ.get('GS_TEST_BASE_URL', 'http://127.0.0.1:8000/')
SUSPECTS = json.loads((Path(__file__).parent / 'vfx_suspects.json').read_text())
TIMES = [0.3, 0.8, 1.4, 2.2, 3.2, 4.5]
log, results = [], {}


def note(m):
    line = f'{time.strftime("%H:%M:%S")} {m}'
    print(line, flush=True)
    log.append(line)


def step(label, fn):
    try:
        r = fn()
        note(f'ok   {label}')
        return r
    except Exception as e:
        note(f'FAIL {label}: {str(e).splitlines()[0][:200]}')
        return None


FX = '''([id,kind,ox,oz,tx,tz])=>GS_ACTION.fx({id,kind,caster:'test',origin:{x:ox,z:oz},target:{x:tx,z:tz}})'''
ROOTS = '''id=>{try{const m=STAGE3D.getEffect(STAGE3D.resolveId?.(id)||id);const r=m?.__gsRoots||[];
  return {live:!!m?.__gsLive,n:r.length,roots:r.slice(0,12).map(o=>({v:o.visible,p:[o.position.x,o.position.y,o.position.z].map(x=>+x.toFixed(2)),
    pp:o.parent?[o.parent.position.x,o.parent.position.y,o.parent.position.z].map(x=>+x.toFixed(2)):null,pn:o.parent?.name||''}))};}catch(e){return {err:String(e).slice(0,120)};}}'''

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('GS_CHROMIUM') or None, headless=True,
                          args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    ctx = b.new_context(viewport={'width': 960, 'height': 540}, device_scale_factor=1)
    page = ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)[:200]))
    page.goto(URL, wait_until='networkidle', timeout=90000)
    page.wait_for_function('window.GS_ACTION && window.GS_STUDIO', timeout=90000)
    shot = lambda name, q=60: step(f'shot {name}', lambda: page.screenshot(path=str(OUT / f'{name}.jpg'), type='jpeg', quality=q))

    # A. Lab beam length, welcome dialog closed
    step('lab welcome close', lambda: page.evaluate("document.getElementById('gaLabWelcome').style.display='none'"))
    for bid in ['CH:tidal', 'CH:storm']:
        step(f'lab play {bid}', lambda: page.evaluate('id=>GS_STUDIO.select(id,{play:true})', bid))
        step('lab welcome close', lambda: page.evaluate("document.getElementById('gaLabWelcome').style.display='none'"))
        for i, w in enumerate([1200, 800, 800]):
            page.wait_for_timeout(w)
            shot(f'A-lab-{bid.replace(":", "_")}-{i}')
        results['A-' + bid] = step(f'lab half {bid}', lambda: page.evaluate('id=>({half:typeof labBeamHalf==="function"?labBeamHalf(id):null})', bid))
        step(f'lab stop {bid}', lambda: page.evaluate('id=>VFX_COMBAT.stop(id)', bid))
        page.wait_for_timeout(300)

    # Trial
    step('trial', lambda: page.evaluate("GS_ACTION.startTrial('bolt')"))
    step('start', lambda: page.locator('#gaStart').evaluate('e=>e.click()'))
    step('unpaused', lambda: page.wait_for_function('!GS_ACTION.status.paused', timeout=90000))
    step('warm', lambda: page.wait_for_function('GS_ACTION.vfxWarmStatus?.ids && GS_ACTION.warmStatus.queued===0', timeout=120000))
    step('invuln', lambda: page.evaluate("GS_ACTION.sim.hero.invuln=1e9;GS_ACTION.sim.enemies.forEach(e=>{e.cd=1e9})"))
    home = "GS_ACTION.sim.hero.x=0;GS_ACTION.sim.hero.z=0;"
    step('hide ui', lambda: page.add_style_tag(content='#gaTrialBar,#gaSkills,#gaHint,#gaInputHint,#ga .top,#gaMenuOpen,#gaExit,#gaTouch,#gaEnemyBars,#gaThreats{display:none!important}'))
    CAM = {'side': ([34, 14, -12], [0, 6, -12]), 'top': ([0, 46, 20], [0, 0, -12])}
    step('camera override', lambda: page.evaluate("""()=>{const H=STAGE3D.host,cam=H.controls.object,orig=H.composer.render;
      H.composer.render=function(...a){const c=window.__probeCam;if(c){cam.position.set(...c.p);cam.lookAt(...c.t);cam.updateMatrixWorld();}return orig.apply(this,a);};}"""))

    def cam(name):
        pp, t = CAM[name]
        page.evaluate('([p,t])=>{window.__probeCam={p,t}}', [pp, t])
        page.wait_for_timeout(110)

    def series(tag, fid, kind, aim, times):
        fn = tag.replace(':', '_').replace('/', '_')
        page.evaluate(home)
        page.wait_for_timeout(200)
        res = step(f'{tag} cast', lambda: page.evaluate(FX, [fid, kind, 0, 0, aim[0], aim[1]]))
        t0 = time.time()
        frames = []
        for k, t in enumerate(times):
            left = t - (time.time() - t0)
            if left > 0:
                page.wait_for_timeout(int(left * 1000))
            at = round(time.time() - t0, 2)
            roots = step(f'{tag} roots {k}', lambda: page.evaluate(ROOTS, fid))
            cam('side')
            step(f'{tag} side {k}', lambda: page.screenshot(path=str(OUT / 'series' / f'{fn}__t{k}__side.jpg'), type='jpeg', quality=50))
            cam('top')
            step(f'{tag} top {k}', lambda: page.screenshot(path=str(OUT / 'series' / f'{fn}__t{k}__top.jpg'), type='jpeg', quality=50))
            frames.append({'k': k, 't': t, 'at': at, 'roots': roots})
        results[tag] = {'cast': res, 'id': fid, 'kind': kind, 'aim': aim, 'frames': frames}
        step(f'{tag} stop', lambda: page.evaluate('id=>{VFX_COMBAT.stop(id)}', fid))
        page.wait_for_timeout(250)

    # B. violet fault over time
    series('B-violet', 'VA:violet_fault', 'beam', (0, -30), [0.9, 1.4, 2.0, 2.8, 3.6])
    # D. lance direction: same effect, two aims
    series('D-lance-fwd', 'D:PROJ:lance', 'circle', (0, -25), [0.5, 1.0])
    series('D-lance-diag', 'D:PROJ:lance', 'circle', (-20, -15), [0.5, 1.0])
    series('D-lance-side', 'D:PROJ:lance', 'circle', (22, 0), [0.5, 1.0])
    # S. suspects
    note(f'series {len(SUSPECTS)} suspects')
    for s in SUSPECTS:
        series(f"S{s['i']:03d}-{s['id']}", s['id'], s['kind'], (0, -25), TIMES)
    note(f'pageerrors {len(errors)} {errors[:5]}')
    b.close()

(OUT / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=1))
(OUT / 'capture.log').write_text('\n'.join(log))
