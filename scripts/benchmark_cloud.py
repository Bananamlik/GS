"""Real-clock cloud benchmark; keep raw results separate from device approval."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8000/')
parser.add_argument('--seconds', type=int, default=60)
parser.add_argument('--cap', type=int, choices=[30, 60], default=60)
parser.add_argument('--loop', action='store_true')
parser.add_argument('--quality', choices=['auto','low','high'], default='auto')
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
if not 3 <= args.seconds <= 600:
    parser.error('--seconds must be between 3 and 600')
args.output.parent.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    options = dict(executable_path=os.environ.get('GS_CHROMIUM', '/usr/bin/chromium'),
                   headless=True, args=['--no-sandbox', '--use-angle=swiftshader',
                                        '--enable-unsafe-swiftshader'])
    if os.environ.get('HTTPS_PROXY'):
        options['proxy'] = {'server': os.environ['HTTPS_PROXY'], 'bypass': 'localhost,127.0.0.1'}
    browser = p.chromium.launch(**options)
    page = browser.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    response = page.goto(args.url, wait_until='networkidle', timeout=60000)
    assert response and response.status == 200, 'Runtime did not load successfully'
    source_hash = hashlib.sha256(response.body()).hexdigest()
    page.wait_for_function('window.GS_ACTION && window.GS_STUDIO', timeout=60000)
    page.select_option('#gaFpsCap', str(args.cap), force=True)
    page.select_option('#gaQuality', args.quality, force=True)
    cdp = page.context.new_cdp_session(page)
    cdp.send('Performance.enable')
    start = time.perf_counter()
    page.evaluate('([seconds,loop]) => GS_ACTION.runBench(seconds,{warmupSeconds:5,thermal:loop})',
                  [args.seconds, args.loop])
    preparation = time.perf_counter() - start
    samples = []
    deadline = time.perf_counter() + args.seconds + 90
    while page.evaluate('GS_ACTION.benchOn'):
        if time.perf_counter() > deadline:
            raise TimeoutError('Benchmark exceeded real-clock deadline')
        page.wait_for_timeout(10000)
        sample = page.evaluate('''() => ({wall:performance.now(),wave:GS_ACTION.sim.wave,
          loops:GS_ACTION.sim.benchmarkLoops||0,time:GS_ACTION.sim.t,gpu:GS_ACTION.gpu,
          roots:STAGE3D.env.scene.children.length,
          segments:(()=>{let n=0;STAGE3D.env.scene.traverse(o=>{if(o.userData.gsStormBatch)n++});return n})()})''')
        metrics = {m['name']:m['value'] for m in cdp.send('Performance.getMetrics')['metrics']}
        sample['jsHeapUsedBytes'] = metrics.get('JSHeapUsedSize')
        sample['jsHeapTotalBytes'] = metrics.get('JSHeapTotalSize')
        samples.append(sample)
        print(json.dumps(sample), flush=True)
    result = page.evaluate('GS_ACTION.benchResult')
    result.update(validationSourceSha256=source_hash,
                  startupWallSeconds=preparation, stabilitySamples=samples, pageErrors=errors,
                  pacingMethod=page.evaluate("window.__GS_PACING_METHOD || 'refresh-divisor'"),
                  validationNote='Cloud SwiftShader, real RAF; physical performance, thermal and release approval remain separate')
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    assert result['completion'] == 'completed' and result['frames'] > 0, result['completion']
    assert result['targetFps'] >= args.cap and not errors, errors
    print(json.dumps({k:result.get(k) for k in ['completion','fpsAvg','p95','p99','max','wave','loops','maxDrawCalls','metricsPassed']}), flush=True)
    browser.close()
