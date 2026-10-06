"""Measure how loud every Lab effect's SFX is (diagnostic, SwiftShader, headless Chromium).

Every connection to an AudioDestinationNode is redirected through a tap that records block peak and block power.
Each effect is played through the Lab preview for PLAY_S seconds; the meter is read after each one.
Env: SHARD, SHARDS, LIMIT, PLAY_S. Output: OUT/sfx-shard{SHARD}.json
Levels are digital full-scale values of the SFX bus (unweighted RMS and peak), not calibrated loudness (LUFS).
"""
import json
import math
import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(sys.argv[1] if len(sys.argv) > 1 else 'sfx-out')
OUT.mkdir(parents=True, exist_ok=True)
URL = os.environ.get('GS_TEST_BASE_URL', 'http://127.0.0.1:8000/')
SHARD = int(os.environ.get('SHARD', '0'))
SHARDS = int(os.environ.get('SHARDS', '1'))
LIMIT = int(os.environ.get('LIMIT', '0'))
PLAY_S = float(os.environ.get('PLAY_S', '4.0'))

INIT = '''() => {
  const orig=AudioNode.prototype.connect;
  window.__SFX_M={blocks:[],peak:0,count:0};
  AudioNode.prototype.connect=function(dest,...a){
    if(typeof AudioDestinationNode!=='undefined'&&dest instanceof AudioDestinationNode){
      const ctx=dest.context;
      if(!ctx.__tap){
        const tap=ctx.createGain();const sp=ctx.createScriptProcessor(2048,2,2);
        sp.onaudioprocess=e=>{const L=e.inputBuffer.getChannelData(0),R=e.inputBuffer.numberOfChannels>1?e.inputBuffer.getChannelData(1):L;
          let pk=0,ss=0;for(let i=0;i<L.length;i++){const l=L[i],r=R[i],m=Math.max(Math.abs(l),Math.abs(r));if(m>pk)pk=m;ss+=(l*l+r*r)*.5;}
          const M=window.__SFX_M;M.count++;if(pk>M.peak)M.peak=pk;M.blocks.push([pk,ss/L.length,ctx.sampleRate]);};
        orig.call(tap,sp);orig.call(sp,dest);ctx.__tap=tap;
        (window.__SFX_CTXS=window.__SFX_CTXS||[]).push(ctx);
      }
      return orig.call(this,ctx.__tap,...a);
    }
    return orig.call(this,dest,...a);
  };
}'''


def db(x):
    return -120.0 if x <= 1e-6 else 20 * math.log10(x)


def summarize(blocks):
    if not blocks:
        return dict(peakDb=-120, rmsDb=-120, momentaryDb=-120, activeBlocks=0)
    sr = blocks[0][2]
    bl = 2048 / sr
    peak = max(b[0] for b in blocks)
    pw = [b[1] for b in blocks]
    active = [p for p in pw if p > 1e-9]
    rms_active = math.sqrt(sum(active) / len(active)) if active else 0
    win = max(1, int(round(0.4 / bl)))
    mom = 0
    for i in range(0, max(1, len(pw) - win + 1)):
        w = pw[i:i + win]
        mom = max(mom, sum(w) / len(w))
    return dict(peakDb=round(db(peak), 1), rmsDb=round(db(rms_active), 1), momentaryDb=round(db(math.sqrt(mom)), 1), activeBlocks=len(active))


rows = []
with sync_playwright() as p:
    options = dict(headless=True, args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'])
    if os.environ.get('GS_CHROMIUM'):
        options['executable_path'] = os.environ['GS_CHROMIUM']
    browser = p.chromium.launch(**options)
    ctx = browser.new_context(viewport={'width': 412, 'height': 676}, is_mobile=False, has_touch=False)
    ctx.add_init_script('(' + INIT + ')()')
    page = ctx.new_page()
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)[:200]))
    page.goto(URL, wait_until='networkidle', timeout=90000)
    page.wait_for_function('window.GS_ACTION && window.GS_STUDIO', timeout=90000)
    page.wait_for_timeout(1500)
    page.evaluate('window.sfxMuted=false')
    page.evaluate('GS_STUDIO.open()')
    ids = page.evaluate('GS_STUDIO.filteredIds()')
    sel = [x for i, x in enumerate(ids) if i % SHARDS == SHARD]
    if LIMIT:
        sel = sel[:LIMIT]
    print(f'total ids {len(ids)}, this shard {len(sel)}', flush=True)
    for n, eid in enumerate(sel):
        row = {'id': eid}
        try:
            page.evaluate('()=>{const M=window.__SFX_M;M.blocks=[];M.peak=0;M.count=0;}')
            page.evaluate('(id)=>{GS_STUDIO.select(id,{play:true});}', eid)
            page.wait_for_timeout(int(PLAY_S * 1000))
            m = page.evaluate('()=>({blocks:window.__SFX_M.blocks,ctxs:(window.__SFX_CTXS||[]).length,states:(window.__SFX_CTXS||[]).map(c=>c.state)})')
            row.update(summarize(m['blocks']))
            row['ctxs'] = m['ctxs']
            row['states'] = m['states']
        except Exception as e:
            row['error'] = str(e).splitlines()[0][:160]
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    browser.close()
(OUT / f'sfx-shard{SHARD}.json').write_text(json.dumps({'play_s': PLAY_S, 'rows': rows, 'pageerrors': errors}, ensure_ascii=False, indent=1), encoding='utf-8')
