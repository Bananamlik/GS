"""Run S6: a stage bundles act names, wave tables and the act boss (an existing enemy strengthened for the boss node only). Node only."""
import unittest

import test_run_state as state


class RunStage(unittest.TestCase):
    def test_stage_names_and_act_bosses(self):
        result = state.node("""
        const D=GA_DATA,run=R.createRun('bolt',4242);
        assert.deepEqual(R.STAGES.coast.acts.map(a=>a.name),['해안 폐허','저주받은 숲','심연']);
        assert.equal(R.stageOf(run).id,'coast');assert.equal(R.actInfo(run).name,'해안 폐허');
        const boss=a=>run.map['a'+a].find(n=>n.kind==='boss');
        // act 1: one strengthened elite in the last wave only
        const b1=boss(1);assert.equal(b1.waves.at(-1).elite,1);assert.ok(!b1.waves[0].elite);
        const B1=R.bossOf(run,b1);assert.equal(B1.key,'elite');
        const k=R.enemyScale(run),d1=R.encounterData(run,b1);
        assert.equal(d1.enemies.elite.name,B1.name);assert.equal(d1.enemies.elite.hp,Math.round(Math.round(D.enemies.elite.hp*k.hp)*B1.hp));
        assert.ok(d1.enemies.elite.radius>D.enemies.elite.radius&&d1.enemies.elite.cd<D.enemies.elite.cd);
        assert.equal(d1.enemies.minion.hp,Math.round(D.enemies.minion.hp*k.hp));assert.equal(d1.enemies.minion.name,D.enemies.minion.name);
        assert.equal(D.enemies.elite.name,'엘리트 잡귀','base data must stay untouched');
        // a plain battle keeps normal elites
        const plain=run.map.a1.find(n=>n.kind==='battle');assert.equal(R.bossOf(run,plain),null);
        assert.equal(R.encounterData(run,plain).enemies.elite.hp,Math.round(D.enemies.elite.hp*k.hp));
        // a boss node saved before S6 (two elites) is left as it was
        const old={...b1,waves:[{minion:4,archer:1},{elite:2,minion:2}]};assert.equal(R.bossOf(run,old),null);
        assert.equal(R.encounterData(run,old).enemies.elite.name,'엘리트 잡귀');
        // act 2: strengthened mage; act 3: the real boss, no override
        const r2={...run,act:2,nodeId:null,floor:0},b2=boss(2),B2=R.bossOf(r2,b2);assert.equal(B2.key,'mage');assert.equal(b2.waves.at(-1).mage,1);
        assert.equal(R.actInfo(r2).name,'저주받은 숲');assert.equal(R.encounterData(r2,b2).enemies.mage.name,B2.name);
        const r3={...run,act:3,nodeId:null,floor:0},b3=boss(3);assert.equal(R.bossOf(r3,b3),null);assert.equal(b3.waves.at(-1).boss,1);
        // the act boss fight is winnable and deterministic
        const fight=()=>{const w=R.startEncounter({...run,nodeId:run.map.a1.find(n=>n.next.includes(b1.id)).id,floor:5},b1);w.hero.invuln=1e9;let n=0;
          while(!w.over&&n++<60*400){const t=w.enemies.find(e=>e.hp>0);if(t){for(const s of [0,1,3,5])w.cast(s,{x:t.x,z:t.z});}w.step({});}
          return [w.over,w.won,n,w.enemies.filter(e=>e.kind==='elite').map(e=>e.hpMax)];};
        const a=fight(),b=fight();assert.deepEqual(a,b);assert.equal(a[1],true,'act 1 boss not beaten: '+JSON.stringify(a));
        assert.deepEqual(a[3],[d1.enemies.elite.hp]);
        console.log(JSON.stringify({steps:a[2],hp:a[3]}));
        """)
        self.assertEqual(result.returncode, 0, result.stderr[-1800:])
        self.assertIn('"steps"', result.stdout)
