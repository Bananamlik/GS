"""Catalog and user workflow regression checks on the current runtime."""
import csv
from pathlib import Path
import test_performance_measurement as performance


class CloudWorkflows(performance.BrowserSession):
    # Do not inherit the benchmark cases: this suite adds only workflow checks.
    def test_library_variants_and_seeded_simulation(self):
        result = self.page.evaluate('''() => {
          const rows=[],missing=[];
          for(const [id,L] of Object.entries(GA_SKILL_LIB)){
            if(!STAGE3D.meta.registry[STAGE3D.resolveId(id)])missing.push(id);
            const variants=L.variants?Object.entries(L.variants):[['',L]];
            for(const [size,v] of variants){const skill={...v.skill,id},qa=GA_VFX_QA.validateSkill(skill);
              const run=()=>{const w=GA_SIM.create(GA_DATA,'bolt',927,927);w.startTrial();
                const accepted=w.castLib(skill,{x:0,z:-25});
                for(let i=0;i<360;i++)w.step();
                return {accepted,damage:w.stats.damage,log:w.combatLog,stats:w.stats};};
              const a=run(),b=run();rows.push({id,size,valid:qa.ok,errors:qa.errors,
                skill,accepted:a.accepted,deterministic:JSON.stringify(a)===JSON.stringify(b),finite:Number.isFinite(a.damage)});
            }
          }
          return {skills:Object.keys(GA_SKILL_LIB).length,rows,missing,audit:GA_STATUS_AUDIT.run()};
        }''')
        self.assertEqual(result['skills'],425)
        self.assertEqual(len(result['rows']),767)
        self.assertEqual(result['missing'],[])
        self.assertTrue(result['audit']['passed'])
        self.assertTrue(all(r['valid'] and r['deterministic'] and r['finite'] and r['accepted'] for r in result['rows']),
                        [r for r in result['rows'] if not all(r[k] for k in ['valid','deterministic','finite','accepted'])])
        root=Path(__file__).resolve().parents[1]
        with next(root.glob('gs-skill*.csv')).open(encoding='utf-8-sig') as f:
            csv_rows=list(csv.DictReader(f))
        self.assertEqual(len(csv_rows),767)
        sizes={'소':'S','중':'M','대':'L','특대':'XL','':''}
        by_key={(r['id'],r['size']):r['skill'] for r in result['rows']}
        self.assertEqual({(r['id'],sizes[r['크기']]) for r in csv_rows},set(by_key))
        for row in csv_rows:
            skill=by_key[(row['id'],sizes[row['크기']])]
            self.assertEqual(row['형태'],skill['kind'])
            for label,field in [('피해','damage'),('준비s','windup'),('판정s','hitT'),('사거리','range')]:
                if row[label]:
                    self.assertEqual(float(row[label]),skill.get(field,0),(row['id'],label))

    def test_mobile_and_desktop_library_review_panels(self):
        for width in [320,390,1280]:
            self.page.set_viewport_size({'width':width,'height':844})
            self.page.evaluate("GS_STUDIO.open();GS_STUDIO.select('CH:storm',{play:false});GS_STUDIO.showInformation()")
            self.assertEqual(self.page.evaluate('GS_STUDIO.selection'),'CH:storm')
            self.assertTrue(self.page.locator('#panel').evaluate("e=>e.classList.contains('open')"))
            self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),width)
            self.page.evaluate('GS_STUDIO.openReview()')
            self.assertTrue(self.page.locator('#reviewDrawer').evaluate("e=>e.classList.contains('open')"))
            self.page.locator('#reviewClose').click(force=True)
            self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'),width)

    def test_checkpoint_resume_and_real_context_recovery(self):
        self.page.evaluate('GS_ACTION.start()')
        before=self.page.evaluate('GS_ACTION.checkpoint.saved')
        self.assertIsNotNone(before)
        self.assertTrue(self.page.evaluate('GS_ACTION.checkpoint.resume()'))
        self.assertEqual(self.page.evaluate('GS_ACTION.sim.wave'),before['wave'])
        self.page.evaluate("window.recoveryExt=STAGE3D.env.renderer.getContext().getExtension('WEBGL_lose_context');recoveryExt.loseContext()")
        self.page.wait_for_timeout(200)
        self.assertTrue(self.page.evaluate('GS_ACTION.status.paused'))
        self.page.locator('#gaStart').evaluate('e=>e.click()')
        self.assertTrue(self.page.evaluate('GS_ACTION.status.paused'))
        self.page.evaluate('recoveryExt.restoreContext()')
        self.page.wait_for_timeout(1000)
        self.page.locator('#gaStart').evaluate('e=>e.click()')
        self.page.wait_for_function('!GS_ACTION.status.paused',timeout=60000)
        self.assertEqual(self.page.evaluate('GS_ACTION.sim.wave'),before['wave'])
        self.page.evaluate('GS_ACTION.leaveToLab()')
        self.assertFalse(self.page.evaluate('GS_ACTION.status.active'))

    def test_representative_casts_deliver_damage_control_and_visual(self):
        self.page.evaluate('''() => {
          window.castTrace=[];const native=VFX_COMBAT;
          window.VFX_COMBAT=Object.freeze({...native,cast(...args){const r=native.cast(...args);
            castTrace.push({id:args[0].id,ok:r.ok});return r;}});
        }''')
        for hero,slot,status in [('bolt',5,'silence'),('rain',5,'root'),('stone',5,'stun'),('stone',4,'stun')]:
            self.page.evaluate('(hero)=>GS_ACTION.startTrial(hero)',hero)
            self.page.wait_for_function('!GS_ACTION.warmStatus.active && GS_ACTION.warmStatus.queued===0',timeout=60000)
            expected=self.page.evaluate('''([hero,slot]) => {
              const setup=w=>{const e=w.enemies[0];Object.assign(e,{x:0,z:-25,hp:10000,hpMax:10000,cd:1e9});
                for(const o of w.enemies.slice(1))Object.assign(o,{x:400,z:400,cd:1e9});w.hero.ult=100;};
              const b=GA_SIM.create(GA_DATA,hero,927,927);b.startTrial();setup(b);
              const accepted=b.cast(slot,{x:0,z:-25});for(let i=0;i<180;i++)b.step();
              setup(GS_ACTION.sim);castTrace.length=0;
              return {accepted:accepted&&GS_ACTION.sim.cast(slot,{x:0,z:-25}),id:GS_ACTION.sim.skills[slot].id,
                damage:b.stats.damage,controls:b.combatLog.filter(r=>r.type==='status:control'),until:GS_ACTION.sim.t+3};
            }''',[hero,slot])
            self.assertTrue(expected['accepted'])
            self.page.wait_for_function('(until)=>GS_ACTION.sim.t>=until',arg=expected['until'],timeout=60000)
            actual=self.page.evaluate('''() => ({damage:GS_ACTION.sim.stats.damage,
              controls:GS_ACTION.sim.combatLog.filter(r=>r.type==='status:control'),visual:castTrace})''')
            self.assertEqual(actual['damage'],expected['damage'])
            self.assertGreater(actual['damage'],0)
            self.assertEqual([(r['statusId'],r['duration']) for r in actual['controls']],
                             [(r['statusId'],r['duration']) for r in expected['controls']])
            self.assertTrue(any(r['statusId']==status for r in actual['controls']))
            self.assertTrue(any(r['id']==expected['id'] and r['ok'] for r in actual['visual']))

    def test_repeat_compare_cancel_and_json_export(self):
        self.page.evaluate("GS_ACTION.startTrial('bolt');GS_CONTEXT_PANELS.switchTrial('verify')")
        self.page.select_option('#gaTrialFx','ARC-01',force=True)
        self.page.select_option('#gsReviewB','FX-30',force=True)
        for button,mode,count in [('gsReviewRepeat','repeat',3),('gsReviewCompare','compare',2)]:
            self.page.locator('#'+button).evaluate('e=>e.click()')
            self.page.wait_for_function("document.body.classList.contains('gs-review-running')")
            self.page.wait_for_function("!document.body.classList.contains('gs-review-running')",timeout=180000)
            result=self.page.evaluate("JSON.parse(localStorage.getItem('gs-review-bench-v1'))")
            self.assertEqual(result['mode'],mode)
            self.assertEqual(result['completion'],'completed',result)
            self.assertEqual(len(result['runs']),count)
            self.assertFalse(result['releaseApproved'])
        with self.page.expect_download() as download:
            self.page.locator('#gsReviewExport').evaluate('e=>e.click()')
        import json
        exported=json.loads(Path(download.value.path()).read_text())
        self.assertEqual(exported['mode'],'compare')
        self.page.locator('#gsReviewRepeat').evaluate('e=>e.click()')
        self.page.wait_for_function("document.body.classList.contains('gs-review-running')")
        self.page.locator('#gsReviewCancel').evaluate('e=>e.click()')
        self.page.wait_for_function("!document.body.classList.contains('gs-review-running')",timeout=30000)
        self.assertEqual(self.page.evaluate("JSON.parse(localStorage.getItem('gs-review-bench-v1')).completion"),'interrupted')

    def test_equipment_change_prepares_and_restores_kit(self):
        self.page.evaluate("GS_ACTION.startTrial('bolt')")
        before=self.page.evaluate('GS_ACTION.sim.skills[1].id')
        self.assertEqual(self.page.evaluate("GS_ACTION.equipSkill('bolt',1,'FX-30')"),'')
        self.page.wait_for_function("!GS_ACTION.warmStatus.active && GS_ACTION.warmStatus.queued===0 && GS_ACTION.sim.skills[1].id==='FX-30'",timeout=60000)
        self.assertEqual(self.page.evaluate("GS_ACTION.equipSkill('bolt',1,'missing-id')"),'스킬 라이브러리에 없는 효과')
        self.page.evaluate("GS_ACTION.resetKit('bolt')")
        self.assertEqual(self.page.evaluate('GS_ACTION.sim.skills[1].id'),before)

    def test_second_context_loss_cancels_pending_recovery_compile(self):
        self.page.evaluate("GS_ACTION.startTrial('bolt')")
        self.page.wait_for_function('GS_ACTION.vfxWarmStatus && GS_ACTION.warmStatus.queued===0 && !GS_ACTION.warmStatus.active',timeout=60000)
        self.page.locator('#gaMenuOpen').evaluate('e=>e.click()')
        self.page.evaluate('''() => {
          const R=STAGE3D.env.renderer,c=R.domElement;window.nativeCompile=R.compileAsync;
          c.dispatchEvent(new Event('webglcontextlost'));c.dispatchEvent(new Event('webglcontextrestored'));
          window.recoveryCalls=0;R.compileAsync=()=>{recoveryCalls++;return new Promise(()=>{});};
        }''')
        self.page.locator('#gaStart').evaluate('e=>e.click()')
        self.page.wait_for_function('recoveryCalls===1')
        self.page.evaluate('''() => {
          const R=STAGE3D.env.renderer;R.domElement.dispatchEvent(new Event('webglcontextlost'));
          R.compileAsync=nativeCompile;R.domElement.dispatchEvent(new Event('webglcontextrestored'));
        }''')
        self.page.wait_for_timeout(100)
        self.assertTrue(self.page.evaluate('GS_ACTION.status.paused'))
        self.page.locator('#gaStart').evaluate('e=>e.click()')
        self.page.wait_for_function('!GS_ACTION.status.paused',timeout=60000)

    def test_touch_cast_root_restriction_and_pause(self):
        self.page.evaluate("GS_ACTION.startTrial('bolt')")
        self.page.wait_for_function('GS_ACTION.vfxWarmStatus && GS_ACTION.warmStatus.queued===0 && !GS_ACTION.warmStatus.active',timeout=60000)
        self.page.evaluate('''() => {
          window.touchAccepted=[];const w=GS_ACTION.sim,native=w.cast;
          w.cast=function(...args){const ok=native.apply(this,args);if(ok)touchAccepted.push(args[0]);return ok;};
        }''')
        self.page.locator('#gaTBtns button[data-slot="0"]').tap()
        self.assertTrue(self.page.evaluate('touchAccepted.includes(0)'))
        self.page.wait_for_function("GS_ACTION.sim.hero.state!=='windup' && GS_ACTION.sim.hero.state!=='dodge'")
        applied=self.page.evaluate("GS_ACTION.setTrialDamage(true);GS_ACTION.sim.applyStatus('hero','root',5)")
        self.assertTrue(applied['applied'],applied)
        self.assertEqual(self.page.evaluate('GS_ACTION.sim.actionAvailability(2).controlReason'),'속박')
        self.page.wait_for_function("document.querySelector('#gaTBtns button[data-slot=\"2\"]').getAttribute('aria-disabled')==='true'")
        self.page.locator('#gaTBtns button[data-slot="2"]').tap(force=True)
        self.assertNotEqual(self.page.evaluate('GS_ACTION.sim.hero.state'),'dodge')
        self.assertTrue(self.page.evaluate("GS_ACTION.sim.combatLog.some(r=>r.type==='action:blocked')"))
        self.page.locator('#gaTTop button[data-act="pause"]').tap()
        self.assertTrue(self.page.evaluate('GS_ACTION.status.paused'))

    def test_wave_reward_changes_checkpoint_and_restores_lab_kit(self):
        self.page.evaluate('GS_ACTION.start()')
        original=self.page.evaluate('GS_ACTION.sim.skills.map(s=>s.id)')
        self.page.locator('#gaStart').evaluate('e=>e.click()')
        self.page.evaluate('GS_ACTION.sim.enemies.forEach(e=>{e.hp=0;e.state="dead"})')
        self.page.wait_for_function('GS_ACTION.draft.open',timeout=30000)
        offer=self.page.evaluate('GS_ACTION.draft.offers[0]')
        slot={'basic':0,'skill':1,'ult':4}[offer['cls']]
        self.assertEqual(self.page.evaluate('([slot])=>GS_ACTION.draft.pick(0,slot)',[slot]),'')
        self.page.wait_for_function('GS_ACTION.sim.wave===2',timeout=30000)
        saved=self.page.evaluate('GS_ACTION.checkpoint.saved')
        self.assertEqual(saved['wave'],2)
        self.assertEqual(saved['skills'][slot]['id'],offer['id'])
        self.page.evaluate('GS_ACTION.leaveToLab();GS_ACTION.startTrial()')
        self.assertEqual(self.page.evaluate('GS_ACTION.sim.skills.map(s=>s.id)'),original)
