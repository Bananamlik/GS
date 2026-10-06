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

    def test_run_shop_buy_and_leave(self):
        node = self.page.evaluate('''() => {const R=GA_RUN;for(let s=1;s<400;s++){const r=R.createRun('bolt',s);const n=r.map.a1.find(x=>x.kind==='shop'&&x.floor===1);
          if(!n)continue;r.nodeId=r.map.a1.find(x=>x.floor===0&&x.next.includes(n.id)).id;r.floor=1;r.gold=100;r.hero.hp=100;if(!R.saveRun(r).ok)throw Error('save');return n.id;}throw Error('no shop');}''')
        self.assertTrue(self.page.evaluate('GS_ACTION.run.continue()'))
        self.page.locator(f'#gaRunFloors .ga-run-node[data-id="{node}"]').click()
        state = self.page.evaluate('GS_ACTION.run.state')
        self.assertEqual(state['stop']['kind'], 'shop')
        heal = next(i for i, o in enumerate(state['stop']['options']) if 'hp' in o['fx'])
        self.page.locator(f'#gaRunFloors .ga-run-node[data-option="{heal}"]').click()
        state = self.page.evaluate('GS_ACTION.run.state')
        self.assertEqual(state['gold'], 70)
        self.assertGreater(state['hero']['hp'], 100)
        self.assertTrue(self.page.locator(f'#gaRunFloors .ga-run-node[data-option="{heal}"]').is_disabled())
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), 390)
        self.page.locator('#gaRunLeave').click()
        state = self.page.evaluate('GS_ACTION.run.state')
        self.assertIsNone(state['stop'])
        self.assertEqual((state['nodeId'], state['floor']), (node, 2))
        self.assertEqual(self.page.evaluate('JSON.parse(localStorage.getItem("gs-run-1")).floor'), 2)

    def test_unlock_screen_buys_a_hero(self):
        self.page.evaluate('''() => {const m=GA_RUN.createMeta();m.shards=70;m.maxDifficulty=1;GA_RUN.saveMeta(m);}''')
        self.assertTrue(self.page.evaluate('GS_ACTION.run.unlocks()'))
        self.assertEqual(self.page.locator('#gaRunFloors [data-diff]').count(), 2)
        self.assertTrue(self.page.locator('#gaRunFloors [data-unlock="hero:stone"]').is_disabled())
        self.page.locator('#gaRunFloors [data-unlock="hero:flame"]').click()
        meta = self.page.evaluate('GA_RUN.loadMeta().value')
        self.assertIn('flame', meta['unlocked']['heroes'])
        self.assertEqual(meta['shards'], 10)
        self.assertTrue(self.page.locator('#gaRunFloors [data-unlock="hero:flame"]').is_disabled())
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), 390)
