"""Probe v4: effects with fxScale cast at in-game scale, 3 frames each (SwiftShader, not a real GPU). Not for merge.

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


FX = '''([id,kind,ox,oz,tx,tz,scale])=>GS_ACTION.fx({id,kind,caster:'test',origin:{x:ox,z:oz},target:{x:tx,z:tz},...(scale?{scale}:{})})'''
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

    def series(tag, fid, kind, aim, times, scale=None):
        fn = tag.replace(':', '_').replace('/', '_')
        page.evaluate(home)
        page.wait_for_timeout(200)
        res = step(f'{tag} cast', lambda: page.evaluate(FX, [fid, kind, 0, 0, aim[0], aim[1], scale]))
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

    # S. every rating>=3 effect whose default skill carries fxScale, cast at that in-game scale
    rows = page.evaluate("""()=>Object.values(GA_SKILL_LIB).filter(L=>['FX-146'].includes(L.id)).map(L=>({id:L.id,kind:L.skill.kind,first:L.native?.firstHit||0,scale:L.skill.fxScale||null,radius:L.skill.radius||null,nat:L.native?.radius||null}))""")
    note(f'series {len(rows)} scaled effects')
    for i, r in enumerate(rows):
        f = min(3.4, max(0.5, (r['first'] or 0.6) + 0.15))
        tag = f"S{i:03d}-{r['id']}"
        series(tag, r['id'], r['kind'], (0, -25), [0.3, 0.9, f, f + 0.8, f + 1.8, f + 3.0], scale=r['scale'])
        results[tag].update(r)
    note(f'pageerrors {len(errors)} {errors[:5]}')
    b.close()

(OUT / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=1))
(OUT / 'capture.log').write_text('\n'.join(log))
