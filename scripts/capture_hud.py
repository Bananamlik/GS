"""Capture HUD screenshots of the current runtime at several viewports (SwiftShader, not a real GPU).

Usage: python3 scripts/capture_hud.py OUTDIR  (serve the repo on 127.0.0.1:8000 first)
Every step is best-effort and logged; a failed step never stops the run.
"""
import json
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else 'hud-captures')
OUT.mkdir(parents=True, exist_ok=True)
URL = os.environ.get('GS_TEST_BASE_URL', 'http://127.0.0.1:8000/')
VIEWPORTS = [
    ('desktop-1280x720', dict(viewport={'width': 1280, 'height': 720}, is_mobile=False, has_touch=False)),
    ('phone-landscape-915x412', dict(viewport={'width': 915, 'height': 412}, is_mobile=True, has_touch=True)),
    ('phone-portrait-412x915', dict(viewport={'width': 412, 'height': 915}, is_mobile=True, has_touch=True)),
]
log = []


def note(msg):
    line = f'{time.strftime("%H:%M:%S")} {msg}'
    print(line, flush=True)
    log.append(line)


def step(label, fn):
    try:
        r = fn()
        note(f'ok   {label}')
        return r
    except Exception as e:  # best effort
        note(f'FAIL {label}: {str(e).splitlines()[0][:200]}')
        return None


def run_viewport(browser, name, opts):
    ctx = browser.new_context(device_scale_factor=1, **opts)
    page = ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)[:200]))
    shot = lambda tag: step(f'{name} shot {tag}', lambda: page.screenshot(path=str(OUT / f'{name}__{tag}.jpg'), type='jpeg', quality=82))
    ev = lambda js, *a: page.evaluate(js, *a)

    page.goto(URL, wait_until='networkidle', timeout=90000)
    page.wait_for_function('window.GS_ACTION && window.GS_STUDIO', timeout=90000)
    shot('01-lab')

    # real game: menu overlay, then fight
    step(f'{name} GS_ACTION.start', lambda: ev('GS_ACTION.start()'))
    step(f'{name} perf overlay on', lambda: ev("()=>{const c=document.getElementById('gaShowPerf');if(c&&!c.checked)c.click();return !!c;}"))
    page.wait_for_timeout(1500)
    shot('02-game-menu')
    step(f'{name} warm wait', lambda: page.wait_for_function('GS_ACTION.warmStatus && !GS_ACTION.warmStatus.active && GS_ACTION.warmStatus.queued===0', timeout=90000))
    step(f'{name} click #gaStart', lambda: page.locator('#gaStart').evaluate('e=>e.click()'))
    page.wait_for_timeout(3000)
    shot('03-game-early')
    step(f'{name} enemies close', lambda: ev('''() => {const s=GS_ACTION.sim;const h=s.hero;
      s.enemies.forEach((e,i)=>{if(e.hp>0){e.x=h.x+(i%3-1)*3.5;e.z=h.z-6-Math.floor(i/3)*3;}});
      return s.enemies.length;}'''))
    page.wait_for_timeout(2500)
    shot('04-game-enemies')
    step(f'{name} cast skills', lambda: ev('''() => {const s=GS_ACTION.sim,e=s.enemies.find(x=>x.hp>0);if(!e)return 'no enemy';
      return [0,1,3,5].map(k=>s.cast(k,{x:e.x,z:e.z}));}'''))
    page.wait_for_timeout(450)
    shot('05-game-cast-a')
    page.wait_for_timeout(500)
    shot('06-game-cast-b')
    shot('06b-game-perf-on')
    step(f'{name} skill row on', lambda: ev("()=>{const c=document.getElementById('gaSkillRow');if(c&&!c.checked)c.click();return !!c;}"))
    page.wait_for_timeout(500)
    shot('06c-game-skillrow-on')
    step(f'{name} skill row off', lambda: ev("()=>{const c=document.getElementById('gaSkillRow');if(c&&c.checked)c.click();return !!c;}"))
    step(f'{name} low hp', lambda: ev('''() => {const h=GS_ACTION.sim.hero;if(h.hpMax){h.hp=Math.max(1,h.hpMax*0.22);}return h.hp;}'''))
    page.wait_for_timeout(700)
    shot('07-game-low-hp')
    step(f'{name} clear wave -> draft', lambda: ev('GS_ACTION.sim.enemies.forEach(e=>{e.hp=0;e.state="dead"})'))
    step(f'{name} draft open', lambda: page.wait_for_function('GS_ACTION.draft.open', timeout=30000))
    page.wait_for_timeout(500)
    shot('08-draft')
    step(f'{name} leave', lambda: ev('GS_ACTION.leaveToLab()'))

    # trial mode (lab stage with HUD)
    step(f'{name} startTrial', lambda: ev("GS_ACTION.startTrial('bolt')"))
    step(f'{name} trial warm', lambda: page.wait_for_function('GS_ACTION.warmStatus && !GS_ACTION.warmStatus.active && GS_ACTION.warmStatus.queued===0', timeout=90000))
    page.wait_for_timeout(1500)
    shot('09-trial')
    step(f'{name} trial cast ult', lambda: ev('''() => {const s=GS_ACTION.sim;const e=s.enemies[0];if(e){Object.assign(e,{x:0,z:-25,hp:10000,hpMax:10000,cd:1e9});}s.hero.ult=100;return s.cast(5,{x:0,z:-25});}'''))
    page.wait_for_timeout(600)
    shot('10-trial-cast')
    info = step(f'{name} dom info', lambda: ev('''() => {const r=id=>{const e=document.getElementById(id);if(!e)return null;const b=e.getBoundingClientRect();return [Math.round(b.left),Math.round(b.top),Math.round(b.width),Math.round(b.height)];};
      return {vw:innerWidth,vh:innerHeight,dpr:devicePixelRatio,reticle:r('gaReticle'),skills:r('gaSkills'),vitals:document.querySelector('.vitals')?.getBoundingClientRect().toJSON?.(),top:document.querySelector('#ga .top')?.getBoundingClientRect().toJSON?.(),objective:r('gaObjective'),hint:r('gaHint'),feedback:r('gaCombatFeedback')};}'''))
    note(f'{name} info {json.dumps(info)}')
    note(f'{name} pageerrors {len(errors)} {errors[:3]}')
    ctx.close()


with sync_playwright() as p:
    options = dict(executable_path=os.environ.get('GS_CHROMIUM') or None, headless=True,
                   args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    if not options['executable_path']:
        del options['executable_path']
    browser = p.chromium.launch(**options)
    for name, opts in VIEWPORTS:
        step(f'viewport {name}', lambda: run_viewport(browser, name, opts))
    browser.close()
(OUT / 'capture.log').write_text('\n'.join(log), encoding='utf-8')
