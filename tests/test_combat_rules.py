"""Combat design C4: a dodge cancels a wind-up (cost kept), an ultimate cannot be cancelled. Node only, no browser."""
import unittest

import test_run_state as state


class CombatRules(unittest.TestCase):
    def test_dodge_cancels_a_wind_up_but_not_an_ultimate(self):
        result = state.node("""
        const make=()=>GA_SIM.create(GA_DATA,'bolt',5),aim={x:0,z:-25};
        const slot=[1,3,5].find(i=>{const w=make();return w.cast(i,aim)&&w.hero.state==='windup'&&w.pending.some(p=>p.type==='release');});
        assert.ok(slot!==undefined,'no skill with a wind-up');
        const w=make();assert.ok(w.cast(slot,aim));const cd=w.hero.cds[slot];assert.ok(cd>0);w.events.splice(0);
        assert.equal(w.dodge(1,0),true);
        assert.equal(w.hero.state,'dodge');assert.ok(!w.pending.some(p=>p.type==='release'),'release still pending');
        assert.equal(w.hero.cds[slot],cd,'cooldown refunded');assert.ok(w.hero.cds[2]>0);
        const cancel=w.events.find(e=>e.type==='cast:cancel');assert.ok(cancel,'no cast:cancel event');assert.equal(cancel.slot,slot);assert.equal(cancel.reason,'dodge');
        assert.ok(w.combatLog.some(r=>r.type==='cast:cancel'&&/회피으로 준비 중 시전 취소/.test(r.policy)),'no combat log row');
        for(let i=0;i<90;i++)w.step({});assert.ok(['idle','move','recover'].includes(w.hero.state)||w.hero.state!=='windup');

        const u=make();u.hero.ult=100;assert.ok(u.cast(4,aim),'ultimate did not cast');
        if(u.hero.state==='windup'){assert.equal(u.dodge(1,0),false);assert.ok(u.pending.some(p=>p.type==='release'));assert.equal(u.hero.state,'windup');}

        const run=()=>{const s=make();s.cast(slot,aim);s.dodge(0,1);for(let i=0;i<240;i++)s.step({mx:i%60<30?1:-1,mz:0});return JSON.stringify([s.hero.x,s.hero.z,s.hero.hp,s.t,s.enemies.map(e=>[e.x,e.z,e.hp])]);};
        assert.equal(run(),run());
        console.log(JSON.stringify({slot,ultWindup:u.hero.state}));
        """)
        self.assertEqual(result.returncode, 0, result.stderr[-1500:])
        self.assertIn('"slot"', result.stdout)
