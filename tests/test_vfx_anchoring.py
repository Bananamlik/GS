"""VFX anchoring: self effects follow the caster, ground fissures sit on the floor, Lab beams use the library range."""
import test_performance_measurement as performance


class VfxAnchoring(performance.BrowserSession):
    def test_poses_follow_ground_lab_length_and_shield_follows_hero(self):
        poses = self.page.evaluate('''() => {
          const P=e=>GS_ACTION.poseFor({caster:'hero',origin:{x:3,z:4},target:{x:30,z:4},...e});
          return {fault:P({id:'VA:violet_fault',kind:'beam'}),fissure:P({id:'D:PROJ:fissure',kind:'beam'}),
            wings:P({id:'D:ULT:ascend',kind:'dash'}),shield:P({id:'ARC-04',kind:'shield'}),
            enemyShield:GS_ACTION.poseFor({id:'ARC-04',kind:'shield',caster:'e1',origin:{x:3,z:4},target:{x:3,z:4}}),
            storm:P({id:'CH:storm',kind:'beam'}),
            labTidal:labBeamHalf('CH:tidal'),labCircle:labBeamHalf('FX-06')};
        }''')
        for key in ['fault', 'fissure']:
            self.assertEqual((poses[key]['origin']['y'], poses[key]['target']['y']), (0, 0), key)
            self.assertEqual((poses[key]['origin']['x'], poses[key]['target']['x']), (3, 30), key)
        self.assertEqual(poses['wings']['form'], 'self')
        self.assertTrue(poses['wings']['follow'])
        self.assertEqual(poses['wings']['target']['x'], 3)
        self.assertTrue(poses['shield']['follow'])
        self.assertFalse(poses['enemyShield'].get('follow'))
        self.assertGreater(poses['storm']['origin']['y'], 1)
        self.assertEqual(poses['labTidal'], 27.5)
        self.assertEqual(poses['labCircle'], 6)

        self.page.evaluate("GS_ACTION.startTrial('rain')")
        self.page.locator('#gaStart').evaluate('e=>e.click()')
        self.page.wait_for_function('!GS_ACTION.status.paused', timeout=120000)
        self.page.wait_for_function('GS_ACTION.vfxWarmStatus?.ids && GS_ACTION.warmStatus.queued===0', timeout=150000)
        cast = self.page.evaluate("(()=>{const h=GS_ACTION.sim.hero;return GS_ACTION.fx({id:'ARC-04',kind:'shield',caster:'test',origin:{x:h.x,z:h.z},target:{x:h.x,z:h.z-20}});})()")
        self.assertTrue(cast['ok'], cast)
        self.assertEqual(cast['form'], 'self')
        self.page.wait_for_function("STAGE3D.getEffect('ARC-04').__gsLive", timeout=20000)
        self.page.wait_for_timeout(200)
        before = self.page.evaluate("STAGE3D.getEffect('ARC-04').__gsRoots.map(r=>r.position.x)")
        self.assertTrue(before)
        self.page.evaluate("GS_ACTION.sim.hero.x+=12")
        self.page.wait_for_timeout(500)
        after = self.page.evaluate("STAGE3D.getEffect('ARC-04').__gsRoots.map(r=>r.position.x)")
        moved = max(a - b for a, b in zip(after, before))
        self.assertGreater(moved, 8, (before, after))

    def test_lance_beam_follows_the_aim_and_starts_at_the_caster(self):
        self.page.evaluate("GS_ACTION.startTrial('bolt')")
        self.page.locator('#gaStart').evaluate('e=>e.click()')
        self.page.wait_for_function('!GS_ACTION.status.paused', timeout=120000)
        self.page.wait_for_function('GS_ACTION.vfxWarmStatus?.ids && GS_ACTION.warmStatus.queued===0', timeout=150000)
        probe = '''([tx,tz])=>new Promise(done=>{
          const h=GS_ACTION.sim.hero;h.x=0;h.z=0;h.invuln=1e9;
          const r=GS_ACTION.fx({id:'D:PROJ:lance',kind:'circle',caster:'test',origin:{x:0,z:0},target:{x:tx,z:tz}});
          const t0=performance.now();
          (function look(){
            let top=(STAGE3D.getEffect(r.id)?.__gsRoots||[])[0];while(top?.parent)top=top.parent;
            let hit=null;top?.traverse(o=>{if(!hit&&o.isMesh&&o.geometry?.type==='CylinderGeometry'&&o.geometry.parameters.height>40&&o.material?.uniforms?.uOp)hit=o;});
            if(hit){hit.updateWorldMatrix(true,false);const e=hit.matrixWorld.elements,l=Math.hypot(e[4],e[5],e[6])||1;
              return done({cast:r,axis:[e[4]/l,e[5]/l,e[6]/l],mid:[e[12],e[13],e[14]],len:hit.geometry.parameters.height});}
            if(performance.now()-t0>8000)return done({cast:r,axis:null});
            requestAnimationFrame(look);})();})'''
        for aim, axis in (((0, -25), 2), ((20, 0), 0)):
            got = self.page.evaluate(probe, list(aim))
            self.assertTrue(got['cast']['ok'], got)
            self.assertIsNotNone(got['axis'], got)
            reach = (aim[0] ** 2 + aim[1] ** 2) ** .5
            self.assertGreater(abs(got['axis'][axis]), .98, (aim, got))
            self.assertAlmostEqual(got['len'], reach + 62, delta=1.5, msg=str((aim, got)))
            for k, unit in ((0, aim[0] / reach), (2, aim[1] / reach)):
                self.assertAlmostEqual(got['mid'][k], unit * (reach + 62) / 2, delta=1.5, msg=str((aim, got)))
            self.page.evaluate("VFX_COMBAT.stop('D:PROJ:lance')")
            self.page.wait_for_timeout(1500)

    def test_audit_lifts_lower_floating_effects(self):
        lifts = {'AC-02': -12, 'ARC-08': -12, 'SC-02': -11, 'FX-10-O': -8, 'FX-25': -4, 'FX-146': -10, 'AS-10': -3}
        self.assertEqual(self.page.evaluate('ids=>ids.map(i=>window.__FX_ADJ[i]?.lift)', list(lifts)), list(lifts.values()))
        self.assertTrue(self.page.evaluate('ids=>ids.every(i=>window.__FX_SCALABLE.has(i))', list(lifts)))
        self.page.evaluate("GS_ACTION.startTrial('bolt')")
        self.page.locator('#gaStart').evaluate('e=>e.click()')
        self.page.wait_for_function('!GS_ACTION.status.paused', timeout=120000)
        self.page.wait_for_function('GS_ACTION.vfxWarmStatus?.ids && GS_ACTION.warmStatus.queued===0', timeout=150000)
        got = self.page.evaluate('''()=>{const h=GS_ACTION.sim.hero;h.x=0;h.z=0;h.invuln=1e9;
          const r=GS_ACTION.fx({id:'FX-25',kind:'circle',caster:'test',origin:{x:0,z:0},target:{x:0,z:-25},scale:.5});
          const root=(STAGE3D.getEffect(r.id)?.__gsRoots||[])[0];
          return {cast:r,parent:root?.parent?.name,y:root?.parent?.position.y,k:root?.parent?.scale.x};}''')
        self.assertTrue(got['cast']['ok'], got)
        self.assertEqual(got['parent'], 'GS_FX_SCALER', got)
        self.assertAlmostEqual(got['k'], .5, places=3, msg=str(got))
        self.assertAlmostEqual(got['y'], -4 * .5, places=3, msg=str(got))
