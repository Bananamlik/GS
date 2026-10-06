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
        self.page.wait_for_function('!GS_ACTION.status.paused', timeout=60000)
        self.page.wait_for_function('GS_ACTION.vfxWarmStatus?.ids && GS_ACTION.warmStatus.queued===0', timeout=60000)
        self.assertTrue(self.page.evaluate("GS_ACTION.sim.cast(3,{x:GS_ACTION.sim.hero.x,z:GS_ACTION.sim.hero.z-20})"))
        self.page.wait_for_function("STAGE3D.getEffect('ARC-04').__gsLive", timeout=20000)
        self.page.wait_for_timeout(200)
        before = self.page.evaluate("STAGE3D.getEffect('ARC-04').__gsRoots.map(r=>r.position.x)")
        self.assertTrue(before)
        self.page.evaluate("GS_ACTION.sim.hero.x+=12")
        self.page.wait_for_timeout(500)
        after = self.page.evaluate("STAGE3D.getEffect('ARC-04').__gsRoots.map(r=>r.position.x)")
        moved = max(a - b for a, b in zip(after, before))
        self.assertGreater(moved, 8, (before, after))
