"""Combat design C1: third-person camera sits farther back, higher and over the right shoulder; distance is a saved setting."""
import test_performance_measurement as performance

READ = '''()=>{const c=STAGE3D.host.controls.object,h=GS_ACTION.sim.hero;
  return {dx:c.position.x-(h.rx??h.x),y:c.position.y,dz:c.position.z-(h.rz??h.z),fov:c.fov,
    saved:JSON.parse(localStorage.getItem('ga-play-settings-v1')||'{}').cameraDist,slider:+document.getElementById('gaCameraDist').value,
    label:document.getElementById('gaCameraDistVal').textContent};}'''


class CombatCamera(performance.BrowserSession):
    def test_third_person_camera_distance_height_shoulder_and_setting(self):
        self.page.evaluate("GS_ACTION.startTrial('bolt')")
        self.page.locator('#gaStart').evaluate('e=>e.click()')
        self.page.wait_for_function('!GS_ACTION.status.paused', timeout=60000)
        self.page.evaluate("GS_ACTION.sim.hero.invuln=1e9;GS_ACTION.sim.hero.x=0;GS_ACTION.sim.hero.z=0")
        self.page.wait_for_timeout(1800)
        got = self.page.evaluate(READ)
        self.assertEqual(got['slider'], 11, got)
        self.assertEqual(got['fov'], 72, got)  # the test viewport is portrait
        self.assertAlmostEqual(got['dz'], 11, delta=.35, msg=str(got))
        self.assertAlmostEqual(got['dx'], 1.6, delta=.2, msg=str(got))
        self.assertAlmostEqual(got['y'], 1.65 / .2 + 3.5, delta=.2, msg=str(got))

        self.page.evaluate("(()=>{const e=document.getElementById('gaCameraDist');e.value='16';e.dispatchEvent(new Event('input'));})()")
        self.page.wait_for_timeout(1800)
        far = self.page.evaluate(READ)
        self.assertEqual((far['saved'], far['label']), (16, '16'), far)
        self.assertAlmostEqual(far['dz'], 16, delta=.4, msg=str(far))
        self.assertAlmostEqual(far['dx'], 1.6, delta=.2, msg=str(far))
