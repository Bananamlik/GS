"""Probe C1: gameplay camera screenshots (SwiftShader). Not for merge."""
import json, os, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT = Path(sys.argv[1] if len(sys.argv) > 1 else 'vfx-captures'); OUT.mkdir(parents=True, exist_ok=True)
URL = os.environ.get('GS_TEST_BASE_URL', 'http://127.0.0.1:8000/')
log = []
def note(m):
    print(m, flush=True); log.append(m)
FX = '''([id,kind,tx,tz,scale])=>{const h=GS_ACTION.sim.hero;return GS_ACTION.fx({id,kind,caster:'test',origin:{x:h.x,z:h.z},target:{x:tx,z:tz},...(scale?{scale}:{})});}'''
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=os.environ.get('GS_CHROMIUM') or None, headless=True, args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
    for name, vp, mobile in (('pc', {'width': 1280, 'height': 720}, False), ('portrait', {'width': 412, 'height': 915}, True), ('landscape', {'width': 915, 'height': 412}, True)):
        ctx = b.new_context(viewport=vp, device_scale_factor=1, is_mobile=mobile, has_touch=mobile)
        page = ctx.new_page(); errs = []
        page.on('pageerror', lambda e: errs.append(str(e)[:200]))
        page.goto(URL, wait_until='networkidle', timeout=90000)
        page.wait_for_function('window.GS_ACTION && window.GS_STUDIO', timeout=90000)
        page.evaluate("GS_ACTION.startTrial('bolt')")
        page.locator('#gaStart').evaluate('e=>e.click()')
        page.wait_for_function('!GS_ACTION.status.paused', timeout=90000)
        try: page.wait_for_function('GS_ACTION.vfxWarmStatus?.ids && GS_ACTION.warmStatus.queued===0', timeout=120000)
        except Exception as e: note(f'{name} warm timeout')
        page.evaluate("GS_ACTION.sim.hero.invuln=1e9;GS_ACTION.sim.hero.x=0;GS_ACTION.sim.hero.z=0;GS_ACTION.sim.enemies.forEach(e=>{e.cd=1e9})")
        for dist in (None, 8, 16):
            if dist:
                page.evaluate("d=>{const e=document.getElementById('gaCameraDist');if(e){e.value=String(d);e.dispatchEvent(new Event('input'));}}", dist)
            page.wait_for_timeout(1800)
            tag = f'{name}-d{dist or "default"}'
            page.screenshot(path=str(OUT / f'{tag}-idle.jpg'), type='jpeg', quality=70)
            for fid, kind, sc, w in (('NV-03', 'zone', None, 900), ('FX-34', 'circle', .69, 1700), ('CH:tidal', 'beam', None, 1500)):
                r = page.evaluate(FX, [fid, kind, 0, -25, sc]); page.wait_for_timeout(w)
                page.screenshot(path=str(OUT / f'{tag}-{fid.replace(":", "_")}.jpg'), type='jpeg', quality=70)
                page.evaluate('id=>VFX_COMBAT.stop(id)', fid); page.wait_for_timeout(300)
                note(f'{tag} {fid} {json.dumps(r)}')
            cam = page.evaluate("(()=>{const c=STAGE3D.host.controls.object,h=GS_ACTION.sim.hero;return {dx:+(c.position.x-h.x).toFixed(2),y:+c.position.y.toFixed(2),dz:+(c.position.z-h.z).toFixed(2),fov:c.fov};})()")
            note(f'{tag} cam {json.dumps(cam)}')
        note(f'{name} pageerrors {len(errs)} {errs[:3]}')
        ctx.close()
    b.close()
(OUT / 'capture.log').write_text('\n'.join(log))
