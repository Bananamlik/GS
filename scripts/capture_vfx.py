"""Probe: VFX placement captures (SwiftShader, not a real GPU). Not for merge.

Usage: python3 scripts/capture_vfx.py OUTDIR  (serve the repo on 127.0.0.1:8000 first)
A: Lab beam preview length (CH:tidal, CH:storm).  B: anchoring scenes (wings, shield follow, ground fissures).
C: contact sheet, every library effect rated >= 3 cast from the hero at a fixed aim, shot near first contact.
Every step is best effort and logged.
"""
import json, os, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else 'vfx-captures')
(OUT / 'sheet').mkdir(parents=True, exist_ok=True)
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


FX = '''([id,kind,ox,oz,tx,tz])=>GS_ACTION.fx({id,kind,caster:'test',origin:{x:ox,z:oz},target:{x:tx,z:tz}})'''

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('GS_CHROMIUM') or None, headless=True,
                          args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    ctx = b.new_context(viewport={'width': 960, 'height': 540}, device_scale_factor=1)
    page = ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)[:200]))
    page.goto(URL, wait_until='networkidle', timeout=90000)
    page.wait_for_function('window.GS_ACTION && window.GS_STUDIO', timeout=90000)
    shot = lambda name, q=70: step(f'shot {name}', lambda: page.screenshot(path=str(OUT / f'{name}.jpg'), type='jpeg', quality=q))

    # A. Lab beam length
    for bid in ['CH:tidal', 'CH:storm']:
        step(f'lab play {bid}', lambda: page.evaluate('id=>labPlay(id)', bid))
        page.wait_for_timeout(1600)
        shot('A-lab-' + bid.replace(':', '_'))
        step(f'lab stop {bid}', lambda: page.evaluate('id=>VFX_COMBAT.stop(id)', bid))
        page.wait_for_timeout(300)

    # Trial
    step('trial', lambda: page.evaluate("GS_ACTION.startTrial('bolt')"))
    step('start', lambda: page.locator('#gaStart').evaluate('e=>e.click()'))
    step('unpaused', lambda: page.wait_for_function('!GS_ACTION.status.paused', timeout=90000))
    step('warm', lambda: page.wait_for_function('GS_ACTION.vfxWarmStatus?.ids && GS_ACTION.warmStatus.queued===0', timeout=120000))
    step('invuln', lambda: page.evaluate("GS_ACTION.sim.hero.invuln=1e9;GS_ACTION.sim.enemies.forEach(e=>{e.cd=1e9})"))
    home = "GS_ACTION.sim.hero.x=0;GS_ACTION.sim.hero.z=0;"

    # B. Anchoring scenes
    def scene(tag, fid, kind, aim, waits, move=None):
        step(f'{tag} home', lambda: page.evaluate(home))
        page.wait_for_timeout(300)
        r = step(f'{tag} cast', lambda: page.evaluate(FX, [fid, kind, 0, 0, aim[0], aim[1]]))
        results['B-' + tag] = r
        for i, w in enumerate(waits):
            page.wait_for_timeout(w)
            if move and i == 1:
                step(f'{tag} move', lambda: page.evaluate(move))
                page.wait_for_timeout(400)
            shot(f'B-{tag}-{i}')
        step(f'{tag} stop', lambda: page.evaluate('id=>VFX_COMBAT.stop(id)', fid))
    scene('wings', 'D:ULT:ascend', 'dash', (0, -25), [700, 500, 600], move='GS_ACTION.sim.hero.x+=10')
    scene('shield', 'ARC-04', 'shield', (0, -20), [600, 400, 600], move='GS_ACTION.sim.hero.x+=10')
    scene('violet', 'VA:violet_fault', 'beam', (0, -30), [900, 500])
    scene('fissure', 'D:PROJ:fissure', 'beam', (0, -30), [500, 400])

    # C. Contact sheet
    rows = page.evaluate('''()=>Object.values(GA_SKILL_LIB).filter(L=>(L.rating||0)>=3).map(L=>({id:L.id,name:L.name,kind:L.skill.kind,first:L.native?.firstHit||0,rating:L.rating}))''')
    note(f'sheet {len(rows)} effects')
    for i, r in enumerate(rows):
        fid = r['id']
        page.evaluate(home)
        res = step(f'C {i} {fid} cast', lambda: page.evaluate(FX, [fid, r['kind'], 0, 0, 0, -25]))
        wait = min(3.2, max(0.5, (r['first'] or 0.6) + 0.15))
        page.wait_for_timeout(int(wait * 1000))
        fn = fid.replace(':', '_').replace('/', '_')
        step(f'C {i} shot', lambda: page.screenshot(path=str(OUT / 'sheet' / f'{fn}.jpg'), type='jpeg', quality=55))
        results[fid] = {'cast': res, 'wait': wait, **r}
        step(f'C {i} stop', lambda: page.evaluate('id=>{VFX_COMBAT.stop(id)}', fid))
        page.wait_for_timeout(150)
    note(f'pageerrors {len(errors)} {errors[:5]}')
    b.close()

(OUT / 'results.json').write_text(json.dumps(results, ensure_ascii=False, indent=1))
(OUT / 'capture.log').write_text('\n'.join(log))
