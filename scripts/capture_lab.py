"""Capture the Lab (library / preview / list) at phone viewports and measure how much of the 3D view stays uncovered.

Usage: python3 scripts/capture_lab.py OUTDIR  (serve the repo on 127.0.0.1:8000 first). SwiftShader, not a real GPU.
Viewports are CSS pixels. 412x676 is a 412-wide phone with the browser toolbars showing.
"""
import json
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else 'lab-captures')
OUT.mkdir(parents=True, exist_ok=True)
URL = os.environ.get('GS_TEST_BASE_URL', 'http://127.0.0.1:8000/')
VIEWPORTS = [
    ('p412x676', dict(viewport={'width': 412, 'height': 676}, is_mobile=True, has_touch=True)),
    ('l915x360', dict(viewport={'width': 915, 'height': 360}, is_mobile=True, has_touch=True)),
    ('p360x640', dict(viewport={'width': 360, 'height': 640}, is_mobile=True, has_touch=True)),
    ('d1280x720', dict(viewport={'width': 1280, 'height': 720}, is_mobile=False, has_touch=False)),
]
log = []
metrics = []

PROBE = '''() => {
  const W=innerWidth,H=innerHeight,cols=16,rows=24;let hit=0,total=0;
  for(let i=0;i<cols;i++)for(let j=0;j<rows;j++){const x=(i+.5)*W/cols,y=(j+.5)*H/rows;const e=document.elementFromPoint(x,y);total++;if(e&&e.tagName==='CANVAS')hit++;}
  const boxes=[];
  for(const e of document.querySelectorAll('body *')){const cs=getComputedStyle(e);if(cs.display==='none'||cs.visibility==='hidden')continue;
    if(cs.position!=='fixed'&&cs.position!=='sticky')continue;const r=e.getBoundingClientRect();if(r.width<80||r.height<30)continue;if(r.bottom<=0||r.top>=H)continue;
    boxes.push({id:e.id||'',cls:(e.className&&e.className.toString().slice(0,40))||'',tag:e.tagName,x:Math.round(r.left),y:Math.round(r.top),w:Math.round(r.width),h:Math.round(r.height),pe:cs.pointerEvents,z:cs.zIndex});}
  return {W,H,viewVisiblePct:Math.round(100*hit/total),boxes};
}'''


def note(msg):
    line = f'{time.strftime("%H:%M:%S")} {msg}'
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


def run_viewport(browser, name, opts):
    ctx = browser.new_context(device_scale_factor=1, **opts)
    page = ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)[:200]))

    def shot(tag):
        step(f'{name} shot {tag}', lambda: page.screenshot(path=str(OUT / f'{name}__{tag}.jpg'), type='jpeg', quality=82))
        m = step(f'{name} measure {tag}', lambda: page.evaluate(PROBE))
        if m:
            m['state'] = f'{name}:{tag}'
            metrics.append(m)

    page.goto(URL, wait_until='networkidle', timeout=90000)
    page.wait_for_function('window.GS_ACTION && window.GS_STUDIO', timeout=90000)
    page.wait_for_timeout(1500)
    shot('01-load')
    step(f'{name} open browse', lambda: page.evaluate('GS_STUDIO.open()'))
    page.wait_for_timeout(1200)
    shot('02-browse')
    ids = step(f'{name} ids', lambda: page.evaluate('GS_STUDIO.filteredIds().slice(0,40)')) or []
    pick = 'GS-requiem' if 'GS-requiem' in ids else (ids[0] if ids else None)
    if pick:
        step(f'{name} select {pick}', lambda: page.evaluate('(id)=>{GS_STUDIO.select(id,{play:true});}', pick))
        page.wait_for_timeout(2500)
        shot('03-preview-playing')
    step(f'{name} collapse list', lambda: page.get_by_text('목록 접기').first.click(timeout=4000))
    page.wait_for_timeout(800)
    shot('04-list-collapsed')
    step(f'{name} info', lambda: page.evaluate('GS_STUDIO.showInformation()'))
    page.wait_for_timeout(800)
    shot('05-info')
    for label, tag in (('시험장', '06-trial'), ('플레이', '07-play')):
        step(f'{name} nav {label}', lambda: page.locator('#gsStudioNav button', has_text=label).first.click(timeout=4000))
        page.wait_for_timeout(2500)
        shot(tag)
    note(f'{name} pageerrors {len(errors)} {errors[:3]}')
    ctx.close()


with sync_playwright() as p:
    options = dict(headless=True, args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    if os.environ.get('GS_CHROMIUM'):
        options['executable_path'] = os.environ['GS_CHROMIUM']
    browser = p.chromium.launch(**options)
    for name, opts in VIEWPORTS:
        step(f'viewport {name}', lambda: run_viewport(browser, name, opts))
    browser.close()
(OUT / 'capture.log').write_text('\n'.join(log), encoding='utf-8')
(OUT / 'metrics.json').write_text(json.dumps(metrics, ensure_ascii=False, indent=1), encoding='utf-8')
