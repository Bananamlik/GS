"""Diagnostic: does the combat-feedback chip ever stay visible while the draft window is open?

Runs the real game on a portrait phone viewport N times; every time the wave is cleared it records the chip
state once the draft is open. Not part of the regular tests.
"""
import json
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else 'chip-probe')
OUT.mkdir(parents=True, exist_ok=True)
URL = os.environ.get('GS_TEST_BASE_URL', 'http://127.0.0.1:8000/')
RUNS = int(os.environ.get('CHIP_RUNS', '6'))
rows = []

STATE = '''() => {const chips=[...document.querySelectorAll('#gaCombatFeedback')];const c=chips[0];
  const r=c?c.getBoundingClientRect():null;
  return {draftOpen:GS_ACTION.draft.open,count:chips.length,opacity:c?getComputedStyle(c).opacity:null,inline:c?c.style.opacity:null,
    text:c?c.textContent:null,top:r?Math.round(r.top):null,clock:GS_ACTION.sim.t}}'''

with sync_playwright() as p:
    options = dict(headless=True, args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    if os.environ.get('GS_CHROMIUM'):
        options['executable_path'] = os.environ['GS_CHROMIUM']
    browser = p.chromium.launch(**options)
    ctx = browser.new_context(viewport={'width': 412, 'height': 915}, is_mobile=True, has_touch=True, device_scale_factor=1)
    page = ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)[:200]))
    page.goto(URL, wait_until='networkidle', timeout=90000)
    page.wait_for_function('window.GS_ACTION && window.GS_STUDIO', timeout=90000)
    for i in range(RUNS):
        row = {'run': i}
        try:
            page.evaluate('GS_ACTION.start()')
            page.wait_for_timeout(1200)
            page.wait_for_function('GS_ACTION.warmStatus && !GS_ACTION.warmStatus.active && GS_ACTION.warmStatus.queued===0', timeout=90000)
            page.locator('#gaStart').evaluate('e=>e.click()')
            page.wait_for_timeout(2500)
            page.evaluate('''() => {const s=GS_ACTION.sim,h=s.hero;s.enemies.forEach((e,i)=>{if(e.hp>0){e.x=h.x+(i%3-1)*3.5;e.z=h.z-6-Math.floor(i/3)*3;}});}''')
            page.wait_for_timeout(1500)
            page.evaluate('''() => {const s=GS_ACTION.sim,e=s.enemies.find(x=>x.hp>0);if(e)[0,1,3,5].map(k=>s.cast(k,{x:e.x,z:e.z}));}''')
            page.wait_for_timeout(300 * (i % 3))
            row['before'] = page.evaluate(STATE)
            page.evaluate('GS_ACTION.sim.enemies.forEach(e=>{e.hp=0;e.state="dead"})')
            page.wait_for_function('GS_ACTION.draft.open', timeout=30000)
            row['at_open'] = page.evaluate(STATE)
            page.wait_for_timeout(500)
            row['after500'] = page.evaluate(STATE)
            page.screenshot(path=str(OUT / f'run{i}.jpg'), type='jpeg', quality=80)
            page.evaluate('GS_ACTION.leaveToLab()')
        except Exception as e:
            row['error'] = str(e).splitlines()[0][:200]
        rows.append(row)
        print(json.dumps(row), flush=True)
    (OUT / 'chip-probe.json').write_text(json.dumps({'rows': rows, 'pageerrors': errors}, indent=1), encoding='utf-8')
    browser.close()
