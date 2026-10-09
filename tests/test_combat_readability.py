"""Combat design C5: an enemy warning fills as its time runs out and draws after the hero's effects; a hit shows which side it came from."""
import test_performance_measurement as performance

THREAT = '''()=>{let r=GS_ACTION.stageRoot;while(r.parent)r=r.parent;let o=null;r.traverse(x=>{if(x.name==='GS_ENEMY_THREAT')o=x;});
  if(!o)return null;const f=o.userData.fill;return {fill:f.scale.x,fillY:f.scale.y,name:f.name,order:[o.renderOrder,f.renderOrder],children:o.children.length};}'''
HIT = '''([x,z])=>{const w=GS_ACTION.sim,e=w.enemies[0];e.x=x;e.z=z;w.emit('hit',{src:e.id,dst:'hero',dmg:1,shield:0,heavy:false,x:w.hero.x,z:w.hero.z});}'''
DIR = '''()=>{const n=document.getElementById('gaHitDir');return {deg:+n.dataset.deg,opacity:+n.style.opacity};}'''


class CombatReadability(performance.BrowserSession):
    def start(self):
        self.page.evaluate("GS_ACTION.startTrial('bolt')")
        self.page.locator('#gaStart').evaluate('e=>e.click()')
        self.page.wait_for_function('!GS_ACTION.status.paused', timeout=60000)
        self.page.evaluate("GS_ACTION.sim.hero.x=0;GS_ACTION.sim.hero.z=0")
        self.page.wait_for_timeout(1500)

    def test_warning_fills_with_time_and_draws_last(self):
        self.start()
        self.assertIsNone(self.page.evaluate(THREAT))
        self.page.evaluate("GS_ACTION.sim.emit('telegraph:start',{id:'c5',kind:'mage',x:0,z:-30,target:{x:0,z:-12},dir:{x:0,z:1},shape:'zone',radius:6,duration:8})")
        self.page.wait_for_function('(%s)()' % THREAT, timeout=20000)
        self.page.wait_for_timeout(1200)
        early = self.page.evaluate(THREAT)
        self.page.wait_for_timeout(1800)
        late = self.page.evaluate(THREAT)
        self.assertEqual((early['name'], early['order'], early['children']), ('GS_ENEMY_THREAT_FILL', [40, 41], 3), early)
        self.assertTrue(0 < early['fill'] < late['fill'] <= 1, (early, late))
        self.assertAlmostEqual(late['fill'], late['fillY'], places=6, msg=str(late))
        self.page.evaluate("GS_ACTION.sim.emit('telegraph:end',{id:'c5'})")
        self.page.wait_for_function('(%s)()===null' % THREAT, timeout=20000)

    def test_hit_shows_the_side_it_came_from(self):
        self.start()
        self.assertEqual(self.page.evaluate(DIR)['opacity'], 0)
        for at, want in (([0, -30], 0), ([40, 11], 90), ([0, 50], 180), ([-40, 11], -90)):
            self.page.evaluate(HIT, at)
            self.page.wait_for_function("+document.getElementById('gaHitDir').style.opacity>0", timeout=20000)
            got = self.page.evaluate(DIR)
            off = abs((got['deg'] - want + 180) % 360 - 180)
            self.assertLess(off, 12, (at, want, got))
            self.page.wait_for_function("+document.getElementById('gaHitDir').style.opacity===0", timeout=20000)
