"""Run mode in the game view (S3, S4): map overlay, a battle node through GA_RUN, reward choice, back on the map with the result saved."""
import test_performance_measurement as performance


class RunUi(performance.BrowserSession):
    def test_run_map_battle_and_return(self):
        self.page.evaluate('localStorage.removeItem("gs-run-1")')
        self.assertTrue(self.page.evaluate('GS_ACTION.run.start()'))
        self.assertTrue(self.page.evaluate('GS_ACTION.run.mapOpen'))
        first = self.page.evaluate('''() => {const s=GS_ACTION.run.state,open=[...document.querySelectorAll('#gaRunFloors .ga-run-node[data-state="open"]')].map(b=>b.dataset.id);
          return {open,floor0:s.map.a1.filter(n=>n.floor===0).map(n=>n.id),width:document.documentElement.scrollWidth}}''')
        self.assertEqual(sorted(first['open']), sorted(first['floor0']))
        self.assertLessEqual(first['width'], 390)
        node = first['open'][0]
        self.page.locator(f'#gaRunFloors .ga-run-node[data-id="{node}"]').click()
        self.page.wait_for_function("GS_ACTION.run.node && GS_ACTION.status.ready && !document.getElementById('gaStart').disabled", timeout=90000)
        self.assertFalse(self.page.evaluate('GS_ACTION.run.mapOpen'))
        self.assertEqual(self.page.evaluate('GS_ACTION.sim.waveTotal'), self.page.evaluate('GS_ACTION.run.node.waves.length'))
        self.page.locator('#gaStart').evaluate('e=>e.click()')
        self.page.wait_for_function('!GS_ACTION.status.paused', timeout=60000)
        self.page.evaluate('GS_ACTION.sim.hero.invuln=1e9')
        self.page.wait_for_function('''() => {const w=GS_ACTION.sim;if(w)for(const e of w.enemies)if(e.hp>0){e.hp=0;e.state='dead';}return GS_ACTION.run.mapOpen;}''',
                                    timeout=60000, polling=250)
        state = self.page.evaluate('GS_ACTION.run.state')
        self.assertIsNotNone(state['reward'])
        self.assertEqual(self.page.locator('#gaRunFloors .ga-run-offer').count(), len(state['reward']['offers']))
        offer = state['reward']['offers'][0]
        self.page.locator(f'#gaRunFloors .ga-run-node[data-offer="0"][data-slot="{offer["slots"][0]}"]').click()
        state = self.page.evaluate('GS_ACTION.run.state')
        self.assertIsNone(state['reward'])
        self.assertEqual(state['kit'][offer['slots'][0]]['id'], offer['id'])
        self.assertGreater(state['gold'], 0)
        self.assertEqual(state['nodeId'], node)
        self.assertEqual(state['floor'], 1)
        self.assertEqual(state['history'][-1]['result'], 'won')
        self.assertIsNone(self.page.evaluate('GS_ACTION.run.node'))
        saved = self.page.evaluate('JSON.parse(localStorage.getItem("gs-run-1"))')
        self.assertEqual(saved['nodeId'], node)
        reachable = self.page.evaluate('''() => [...document.querySelectorAll('#gaRunFloors .ga-run-node[data-state="open"]')].map(b=>b.dataset.id)''')
        self.assertEqual(sorted(reachable), sorted(next(n for n in state['map']['a1'] if n['id'] == node)['next']))
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), 390)
