"""Run against a local HTTP server with Python Playwright and Chromium.

python3 -m http.server 8000 --bind 127.0.0.1 --directory /workspace/GS
python3 -m unittest discover -s tests -v
"""
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SourceTests(unittest.TestCase):
    def test_elapsed_pacing_keeps_slow_frames_and_limits_fast_refresh(self):
        source=(ROOT/'index.html').read_text()
        policy=re.search(r'<script id="gsPerformancePolicy">(.*?)</script>',source,re.S)[1]
        script="global.window=global;\n"+policy+"""
        const assert=require('node:assert/strict'),make=GS_PERFORMANCE_POLICY.createPacer;
        const p=make();assert.deepEqual([0,80,160,240].map(t=>p.allow(t,30)),[true,true,true,true]);
        p.reset();assert.deepEqual([0,16.6,33.2,49.8,66.4].map(t=>p.allow(t,30)),[true,false,true,false,true]);
        p.reset();let frames=0;for(let i=0;i<144;i++)frames+=p.allow(i*1000/144,72);
        assert.equal(frames,72);assert.equal(p.allow(999,0),true);
        assert.equal(p.allow(1000,30),true);assert.equal(p.allow(1001,30),false);
        p.reset();assert.equal(p.allow(1002,30),true);assert.equal(p.allow(NaN,30),false);
        """
        result=subprocess.run(['node'],input=script,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

    def test_runtime_files_match_and_scripts_parse(self):
        source = (ROOT / 'index.html').read_text()
        self.assertEqual(source, (ROOT / 'GS_Action_v34_runtime.html').read_text())
        blocks = re.findall(r'<script\b([^>]*)>(.*?)</script>', source, re.S)
        self.assertGreater(len(blocks), 200)
        with tempfile.TemporaryDirectory() as directory:
            for i, (attrs, code) in enumerate(blocks):
                if 'importmap' in attrs:
                    json.loads(code)
                    continue
                path = Path(directory) / f'{i}{".mjs" if "module" in attrs else ".js"}'
                path.write_text(code)
                result = subprocess.run(['node', '--check', str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_loaded_cadence_cannot_relax_requested_budget(self):
        source = (ROOT / 'index.html').read_text()
        policy = re.search(r'<script id="gsPerformancePolicy">(.*?)</script>', source, re.S)[1]
        script = "global.window=global;\n" + policy + """
        const assert=require('node:assert/strict'),p=GS_PERFORMANCE_POLICY;
        assert.equal(p.target({fpsCap:30,refreshHz:20,skipN:4}),30);
        assert.equal(p.target({fpsCap:60,refreshHz:20,skipN:1}),60);
        assert.equal(p.target({fpsCap:60,refreshHz:120,skipN:2}),60);
        assert.equal(p.target({fpsCap:60,refreshHz:144,skipN:2}),72);
        assert.equal(p.target({fpsCap:60,refreshHz:NaN,skipN:0}),60);
        const summary=p.summarize([50,50,50],60);
        assert.equal(p.checks(summary,p.budgets(60)).average,false);
        assert.equal(p.checks(p.summarize([],60),p.budgets(60)).samples,false);
        """
        result = subprocess.run(['node'], input=script, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


class BrowserSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.playwright = sync_playwright().start()
        options = dict(executable_path=os.environ.get('GS_CHROMIUM', '/usr/bin/chromium'),
                       headless=True, args=['--no-sandbox', '--use-angle=swiftshader',
                                           '--enable-unsafe-swiftshader'])
        if os.environ.get('HTTPS_PROXY'):
            options['proxy'] = {'server': os.environ['HTTPS_PROXY'], 'bypass': 'localhost,127.0.0.1'}
        cls.browser = cls.playwright.chromium.launch(**options)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 390, 'height': 844},
                                                is_mobile=True, has_touch=True)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda e: self.errors.append(str(e)))
        self.page.goto(os.environ.get('GS_TEST_BASE_URL', 'http://127.0.0.1:8000/'),
                       wait_until='networkidle', timeout=60000)
        self.page.wait_for_function('window.GS_ACTION && window.GS_STUDIO', timeout=60000)

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])


class BrowserTests(BrowserSession):
    def test_slow_render_is_not_skipped_again_at_30_fps(self):
        self.page.evaluate("GS_ACTION.startTrial('bolt')")
        self.page.wait_for_function('GS_ACTION.vfxWarmStatus?.ids && GS_ACTION.warmStatus.queued===0',timeout=60000)
        self.page.select_option('#gaFpsCap','30',force=True)
        self.page.evaluate('''() => {
          window.pacedFrames=[];const C=STAGE3D.host.composer;
          window.pacedRender=C.render;
          C.render=()=>{pacedFrames.push(performance.now());const end=performance.now()+80;
            while(performance.now()<end){};};
        }''')
        self.page.wait_for_function('pacedFrames.length>=10',timeout=15000)
        result=self.page.evaluate('''() => {
          STAGE3D.host.composer.render=pacedRender;
          const times=pacedFrames.slice(2),intervals=times.slice(1).map((t,i)=>t-times[i]);
          return {intervals,mean:intervals.reduce((a,b)=>a+b,0)/intervals.length,method:__GS_PACING_METHOD};
        }''')
        self.assertEqual(result['method'],'elapsed-time')
        self.assertLess(result['mean'],95,result)

    def test_module_preparation_cancels_and_rebuilds_after_context_loss(self):
        self.page.evaluate('''() => {
          window.__GS_BENCH_CALIBRATING=true;const R=STAGE3D.env.renderer;
          window.epochFixture={calls:0,cancelled:false,native:R.compileAsync};
          R.compileAsync=()=>{epochFixture.calls++;return epochFixture.calls===1?new Promise(()=>{}):Promise.resolve();};
          window.epochId=Object.keys(GA_SKILL_LIB).find(id=>!STAGE3D.getEffect(id).__instantiated);
          STAGE3D.prepare(epochId).catch(()=>{epochFixture.cancelled=true;});
        }''')
        self.page.wait_for_function('epochFixture.calls===1')
        self.page.evaluate("STAGE3D.env.renderer.domElement.dispatchEvent(new Event('webglcontextlost'))")
        self.page.wait_for_function('epochFixture.cancelled')
        self.page.evaluate("STAGE3D.env.renderer.domElement.dispatchEvent(new Event('webglcontextrestored'))")
        self.page.evaluate('STAGE3D.prepare(epochId)')
        self.assertEqual(self.page.evaluate('epochFixture.calls'),2)
        self.page.evaluate('() => {STAGE3D.env.renderer.compileAsync=epochFixture.native}')

    def test_quality_changes_resize_once_and_skip_identical_settings(self):
        self.page.set_viewport_size({'width':800,'height':1600})
        self.page.wait_for_function('STAGE3D.env.camera.aspect===0.5')
        self.page.evaluate('''() => {
          GS_ACTION.enterGameSelect();const R=STAGE3D.env.renderer,C=STAGE3D.host.composer;
          window.resizeTrace={buffer:0,legacy:0,composer:0};
          const b=R.setDrawingBufferSize,s=R.setSize,c=C.setPixelRatio;
          R.setDrawingBufferSize=function(...a){resizeTrace.buffer++;return b.apply(this,a);};
          R.setSize=function(...a){resizeTrace.legacy++;return s.apply(this,a);};
          C.setPixelRatio=function(...a){resizeTrace.composer++;return c.apply(this,a);};
        }''')
        self.page.select_option('#gaQuality','low',force=True)
        first=self.page.evaluate('({...resizeTrace,width:STAGE3D.env.renderer.domElement.width,height:STAGE3D.env.renderer.domElement.height})')
        self.assertEqual(first['buffer'],1)
        self.assertEqual(first['legacy'],0)
        self.assertEqual(first['composer'],1)
        self.assertLessEqual(first['height'],960)
        self.page.select_option('#gaQuality','low',force=True)
        self.assertEqual(self.page.evaluate('resizeTrace'),{k:first[k] for k in ['buffer','legacy','composer']})
        self.page.select_option('#gaQuality','high',force=True)
        self.assertEqual(self.page.evaluate('STAGE3D.env.renderer.domElement.height'),1600)

    def start_bench(self, cap=60):
        self.page.select_option('#gaFpsCap', str(cap), force=True)
        self.page.evaluate('GS_ACTION.runBench(3, {warmupSeconds:0.3})')
        self.page.wait_for_function('GS_ACTION.benchOn', timeout=60000)

    def finish_bench(self):
        self.page.wait_for_function('!GS_ACTION.benchOn && GS_ACTION.benchResult', timeout=30000)
        return self.page.evaluate('GS_ACTION.benchResult')

    def test_fixed_target_and_real_phase_records(self):
        self.start_bench()
        self.page.evaluate('window.__GS_HZ=20;window.__GS_SKIP_N=1')
        result = self.finish_bench()
        self.assertEqual(result['completion'], 'completed')
        self.assertGreaterEqual(result['frames'], 2)
        self.assertGreaterEqual(result['targetFps'], 60)
        self.assertEqual(result['targetBasis']['requestedCap'], 60)
        self.assertGreaterEqual(result['calibration']['samples'], 24)
        if not self.page.evaluate('GS_ACTION.warmStatus.parallel'):
            self.assertEqual(result['preparation']['throughWave'], 6)
            self.assertGreaterEqual(result['preparation']['ids'], 7)
        self.assertIn('wave.prepare', result['phaseTotals'])
        self.assertEqual(result['phaseTotals']['wave.prepare']['kind'], 'async-wall')
        self.assertTrue({'warm.compile','warm.compile.wait'} & result['phaseTotals'].keys())
        self.assertIn('warm.render', result['phaseTotals'])
        self.assertIn('render.submit', result['phaseTotals'])
        self.assertLessEqual(len(result['phaseSpans']), 120)
        self.assertFalse(self.page.evaluate('!!window.__GS_BENCH_CALIBRATING'))
        audit = self.page.evaluate('GA_STATUS_AUDIT.run()')
        self.assertEqual((audit['passed'], audit['passedCount'], audit['total']), (True, 10, 10))

    def test_cancel_during_calibration_restores_active_trial(self):
        result = self.page.evaluate('''async () => {
          GS_ACTION.startTrial();const before=GS_ACTION.status;
          const pending=GS_ACTION.runBench(3);GS_ACTION.stopBench();await pending;
          return {before,after:GS_ACTION.status,calibrating:!!window.__GS_BENCH_CALIBRATING};
        }''')
        self.assertEqual(result['before']['paused'], result['after']['paused'])
        self.assertEqual(result['after']['mode'], 'trial')
        self.assertFalse(result['calibrating'])
        self.assertFalse(self.page.evaluate('GS_ACTION.benchOn'))

    def test_trace_capacity_stack_and_setting_change(self):
        self.start_bench(30)
        # Deterministic trace-storage fault injection, not a performance measurement.
        self.page.evaluate('''() => {
          const original=performance.now;let time=100000;
          performance.now=()=>time;
          try {
            const worst=__GS_TRACE_START();time+=1000;__GS_TRACE_END('test.worst',worst);
            for(let i=0;i<131;i++){
            const started=__GS_TRACE_START();time+=60;
            __GS_TRACE_END('test.trace',started,{test:true});
          }} finally {performance.now=original;}
          document.getElementById('gaFpsCap').value='60';
          document.getElementById('gaFpsCap').dispatchEvent(new Event('change'));
        }''')
        result = self.finish_bench()
        self.assertEqual(result['completion'], 'configuration-changed')
        self.assertFalse(result['metricsPassed'])
        self.assertEqual(result['targetFps'], 30)
        self.assertEqual(result['phaseTotals']['test.trace']['count'], 131)
        self.assertLessEqual(len(result['phaseSpans']), 120)
        self.assertGreaterEqual(result['phaseSpansDropped'], 11)
        self.assertTrue(any(s['phase']=='test.trace' and s['stack'] for s in result['phaseSpans']))
        self.assertTrue(any(s['phase']=='test.worst' and s['durationMs']==1000 for s in result['phaseSpans']))
        self.assertEqual(result['phaseSpansRetention'], 'largest-duration')

    def test_preparation_failure_cannot_pass(self):
        self.page.evaluate("() => {STAGE3D.prepare=async()=>{throw Error('Injected prepare failure')};}")
        self.start_bench(30)
        result = self.finish_bench()
        self.assertEqual(result['completion'], 'completed')
        self.assertGreater(result['preparation']['failed'], 0)
        self.assertGreaterEqual(result['frames'], 2)
        self.assertFalse(result['metricsPassed'])

    def test_output_copy_elision_preserves_pixels_and_conversion_fallback(self):
        result=self.page.evaluate("""() => {
          window.__GS_BENCH_CALIBRATING=true;
          const T=THREE,R=STAGE3D.env.renderer,H=STAGE3D.host,C=H.composer;
          R.setDrawingBufferSize(64,64,1);C.setPixelRatio(1);C.setSize(64,64);
          const scene=new T.Scene(),camera=new T.OrthographicCamera(-2,2,2,-2,.1,10);
          camera.position.z=2;scene.background=new T.Color(.01,.05,.2);
          for(let i=0;i<4;i++){
            const mat=new T.MeshBasicMaterial({color:new T.Color(i===0?4:.1,i===1?2:.2,i===2?3:.05),toneMapped:false});
            const mesh=new T.Mesh(new T.PlaneGeometry(.85,3),mat);mesh.position.x=i-1.5;scene.add(mesh);
          }
          C.passes[0].scene=scene;C.passes[0].camera=camera;
          H.classicBloom.uBloomAmt=.7;H.classicBloom.uKnee=.25;
          R.info.autoReset=false;
          const gl=R.getContext(),capture=enabled=>{
            H.outputPass.enabled=enabled;R.info.reset();C.render(0);
            const pixels=new Uint8Array(64*64*4);gl.readPixels(0,0,64,64,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
            return {pixels,calls:R.info.render.calls};
          };
          const results=[];
          for(const [space,tone] of [[T.LinearSRGBColorSpace,T.NoToneMapping],[T.SRGBColorSpace,T.NoToneMapping],[T.LinearSRGBColorSpace,T.ACESFilmicToneMapping]]){
            R.outputColorSpace=space;R.toneMapping=tone;
            const reference=capture(true),enabled=H.syncOutputPass(),actual=capture(enabled);
            let maxDelta=0,changed=0;
            for(let i=0;i<actual.pixels.length;i++){
              const delta=Math.abs(actual.pixels[i]-reference.pixels[i]);maxDelta=Math.max(maxDelta,delta);if(delta)changed++;
            }
            results.push({enabled,maxDelta,changed,referenceCalls:reference.calls,actualCalls:actual.calls});
          }
          return results;
        }""")
        self.assertEqual([r['enabled'] for r in result],[False,True,True])
        self.assertLessEqual(result[0]['maxDelta'],1)
        self.assertEqual(result[0]['actualCalls'],result[0]['referenceCalls']-1)
        self.assertTrue(all(r['maxDelta']==0 and r['actualCalls']==r['referenceCalls'] for r in result[1:]))

    def test_storm_segmented_batches_preserve_alpha_order_and_visibility(self):
        result=self.page.evaluate("""() => {
          window.__GS_BENCH_CALIBRATING=true;
          const T=THREE,R=STAGE3D.env.renderer,H=STAGE3D.host,C=H.composer,camera=STAGE3D.env.camera;
          R.setDrawingBufferSize(128,96,1);C.setPixelRatio(1);C.setSize(128,96);
          camera.aspect=128/96;camera.updateProjectionMatrix();R.info.autoReset=false;
          const mod=STAGE3D.getEffect('CH:storm'),gl=R.getContext(),rows=[];
          const trigger=()=>VFX_COMBAT.cast({id:'CH:storm',origin:{x:-10,y:3,z:0},target:{x:10,y:3,z:0},playAudio:false});
          trigger();const all=new Set();for(const root of mod.__gsRoots)root.traverse(o=>{if(o.material&&!Array.isArray(o.material))all.add(o.material);});
          const eligible=[...all].filter(m=>m.isMeshBasicMaterial&&m.transparent&&m.blending===T.AdditiveBlending&&!m.depthWrite&&m.side===T.DoubleSide);
          const normal=[...all].filter(m=>m.isMeshBasicMaterial&&m.blending===T.NormalBlending);
          const normalUntouched=normal.every(m=>!m.forceSinglePass);
          for(const [x,z] of [[-7,2],[0,-2],[7,3]]){
            const overlay=new T.Mesh(new T.PlaneGeometry(5,8),new T.MeshBasicMaterial({color:0x506080,transparent:true,opacity:.45,depthWrite:false,side:T.DoubleSide}));
            overlay.position.set(x,3,z);STAGE3D.env.scene.add(overlay);
          }
          const capture=skip=>{for(const root of mod.__gsRoots)root.traverse(o=>{if(o.userData.gsStormSegmented)o.userData.gsStormBatchDisabled=!skip;if(o.userData.gsStormZeroHidden)o.visible=!skip;});
            STAGE3D.syncLights();R.info.reset();C.render(0);
            const pixels=new Uint8Array(128*96*4);gl.readPixels(0,0,128,96,gl.RGBA,gl.UNSIGNED_BYTE,pixels);return {pixels,calls:R.info.render.calls};};
          for(const position of [[0,6,35],[0,6,-35],[25,15,25]]){
            camera.position.set(...position);camera.lookAt(0,3,0);camera.updateMatrixWorld(true);
            for(const time of [.35,1.2,1.6,2.8,4.2]){
              mod.stop();trigger();mod.update(time);
              const before=capture(false),after=capture(true);let maxDelta=0,totalDelta=0;
              for(let i=0;i<after.pixels.length;i++){const d=Math.abs(after.pixels[i]-before.pixels[i]);maxDelta=Math.max(maxDelta,d);totalDelta+=d;}
              rows.push({time,position,maxDelta,meanDelta:totalDelta/after.pixels.length,before:before.calls,after:after.calls});
            }
          }

          return {normalUntouched,eligible:eligible.length,normal:normal.length,rows};
        }""")
        self.assertTrue(result['normalUntouched'],result)
        self.assertGreater(result['eligible'],180)
        self.assertGreater(result['normal'],0)
        self.assertTrue(all(r['maxDelta']<=1 for r in result['rows']),result)
        self.assertTrue(all(r['after']<=r['before'] for r in result['rows']),result)
        self.assertGreater(max(r['before']-r['after'] for r in result['rows']),200)

    def install_warm_fixture(self, parallel=True, reject=False):
        self.page.evaluate('''({parallel,reject}) => {
          GS_ACTION.enterGameSelect();window.__GS_BENCH_CALIBRATING=true;
          const R=STAGE3D.env.renderer,has=R.extensions.has.bind(R.extensions);
          R.extensions.has=name=>name==='KHR_parallel_shader_compile'?parallel:has(name);
          window.warmFixture={calls:[],renders:0,waiters:[],completed:[],originalRender:R.render};
          R.compile=(view,camera,target)=>{warmFixture.calls.push({kind:'sync',ids:view.children.map(x=>x.uuid),parents:view.children.map(x=>x.parent?.uuid),target:R.getRenderTarget()?.uuid||null});};
          R.compileAsync=(view,camera,target)=>{
            warmFixture.calls.push({kind:'async',ids:view.children.map(x=>x.uuid),parents:view.children.map(x=>x.parent?.uuid),target:R.getRenderTarget()?.uuid||null});
            if(reject)return Promise.reject(Error('Injected compile failure'));
            return new Promise(resolve=>warmFixture.waiters.push(resolve));
          };
          R.render=view=>{warmFixture.renders++;
            warmFixture.renderViews=warmFixture.renderViews||[];
            warmFixture.renderViews.push({ids:view.children.map(x=>x.uuid),
              lights:view.children.filter(x=>x.isLight).length,
              unrelated:view.children.some(x=>!x.isLight&&!warmFixture.calls.some(c=>c.ids.includes(x.uuid)))});
          };
        }''', {'parallel':parallel,'reject':reject})

    def release_warm_pass(self):
        self.page.wait_for_function('warmFixture.waiters.length > 0')
        self.page.evaluate('warmFixture.waiters.shift()()')

    def test_async_warm_serializes_hides_and_restores_latest_target(self):
        self.install_warm_fixture()
        self.page.evaluate("() => {GS_ACTION.warmFx('FX-30').then(r=>warmFixture.completed.push(r));GS_ACTION.warmFx('ARC-01').then(r=>warmFixture.completed.push(r));}")
        self.page.wait_for_function('warmFixture.calls.length === 1')
        state = self.page.evaluate('''() => {
          const R=STAGE3D.env.renderer,mod=STAGE3D.getEffect('FX-30');
          window.warmTarget=new THREE.WebGLRenderTarget(8,8);R.setRenderTarget(warmTarget);
          return {queued:GS_ACTION.warmStatus.queued,hidden:mod.__gsRoots.every(x=>!x.visible),
            frozen:__GS_IS_WARM_MOD(mod),parents:mod.__gsRoots.map(x=>x.parent?.uuid),
            recorded: warmFixture.calls[0].parents};
        }''')
        self.assertEqual(state['queued'],2)
        self.assertTrue(state['hidden'] and state['frozen'])
        self.assertEqual(state['parents'],state['recorded'])
        for _ in range(4):
            self.release_warm_pass()
        self.page.wait_for_function('warmFixture.completed.length === 2 && GS_ACTION.warmStatus.queued === 0')
        result = self.page.evaluate('''() => ({results:warmFixture.completed,calls:warmFixture.calls,
          renders:warmFixture.renders,views:warmFixture.renderViews,status:GS_ACTION.warmStatus,
          target:STAGE3D.env.renderer.getRenderTarget()===warmTarget,checks:STAGE3D.env.renderer.debug.checkShaderErrors})''')
        self.assertTrue(all(r['warmed'] and r['parallel'] for r in result['results']))
        self.assertEqual(result['renders'],2)
        self.assertTrue(all(v['lights'] > 0 and not v['unrelated'] for v in result['views']))
        self.assertEqual(len(result['calls']),4)
        self.assertEqual(result['calls'][0]['ids'],result['calls'][1]['ids'])
        self.assertTrue(result['target'] and result['checks'])
        self.assertEqual(result['status']['maskedRoots'],0)

    def test_real_cast_cancels_warm_without_stopping_new_visual(self):
        self.install_warm_fixture()
        self.page.evaluate("() => {GS_ACTION.warmFx('FX-30').then(r=>warmFixture.completed.push(r));}")
        self.page.wait_for_function('warmFixture.waiters.length > 0')
        result = self.page.evaluate("GS_ACTION.fx({id:'FX-30',caster:'test',origin:{x:0,z:0},target:{x:0,z:-25}})")
        self.assertTrue(result['ok'])
        self.page.wait_for_function('warmFixture.completed.length === 1')
        self.release_warm_pass()
        state = self.page.evaluate("({cancelled:warmFixture.completed[0].cancelled,live:STAGE3D.getEffect('FX-30').__gsLive,masked:GS_ACTION.warmStatus.maskedRoots,renders:warmFixture.renders})")
        self.assertTrue(state['cancelled'] and state['live'])
        self.assertEqual((state['masked'],state['renders']),(0,0))

    def test_compile_failure_and_context_loss_release_warm_ownership(self):
        self.install_warm_fixture(reject=True)
        result=self.page.evaluate("GS_ACTION.warmFx('FX-30')")
        self.assertFalse(result['warmed'])
        self.assertGreater(result['failed'],0)
        self.assertEqual(self.page.evaluate('GS_ACTION.warmStatus.maskedRoots'),0)
        self.install_warm_fixture()
        self.page.evaluate("() => {GS_ACTION.warmFx('FX-30').then(r=>warmFixture.completed.push(r));}")
        self.page.wait_for_function('warmFixture.waiters.length > 0')
        self.page.evaluate("STAGE3D.env.renderer.domElement.dispatchEvent(new Event('webglcontextlost',{cancelable:true}))")
        self.page.wait_for_function('warmFixture.completed.length === 1')
        self.assertTrue(self.page.evaluate('warmFixture.completed[0].cancelled'))
        self.assertEqual(self.page.evaluate('GS_ACTION.warmStatus.maskedRoots'),0)
        self.release_warm_pass()

    def test_extension_fallback_is_explicit_and_yields(self):
        self.install_warm_fixture(parallel=False)
        result=self.page.evaluate("GS_ACTION.warmFx('FX-30')")
        self.assertTrue(result['warmed'])
        self.assertFalse(result['parallel'])
        self.assertEqual(self.page.evaluate("warmFixture.calls.map(x=>x.kind)"),['sync','sync'])
        self.assertEqual(self.page.evaluate('GS_ACTION.warmStatus.maskedRoots'),0)


if __name__ == '__main__':
    unittest.main()
