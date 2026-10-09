"""Build axis B1: a skill's form comes from its kind; two different forms picked during a run switch a combo on. Node only."""
import unittest

import test_run_state as state


class RunBuild(unittest.TestCase):
    def test_forms_combos_and_reward_preview(self):
        result = state.node("""
        const lib=GA_SKILL_LIB,D=GA_DATA;
        assert.deepEqual(['projectile','chain','beam','circle','radial','zone','deploy','shield','dash','dodge'].map(R.formOfKind),['flight','flight','beam','point','point','zone','install','self','','']);
        // every usable library skill has a form
        const usable=Object.values(lib).filter(L=>(L.rating||0)>=3);assert.equal(usable.length,243);
        for(const L of usable)assert.ok(R.FORMS[R.formOfKind(L.skill.kind)],L.id+' '+L.skill.kind);
        // a fresh run has no combo for any hero: hero skills do not count
        for(const h of Object.keys(D.heroes)){const run=R.createRun(h,7);assert.deepEqual(R.activeCombos(R.resolveKit(run)),[],h);}
        const pick=(kind,cls)=>{for(const L of usable){if(L.variants){for(const [size,v] of Object.entries(L.variants))if(v.skill.kind===kind&&v.cls===cls)return {id:L.id,size};}else if(L.skill.kind===kind&&L.cls===cls)return {id:L.id,size:''};}throw Error('no '+kind+' '+cls);};
        const zone=pick('zone','skill'),point=pick('circle','skill');
        let run=R.createRun('bolt',7);const base=R.encounterData(run,{id:'n',kind:'battle',waves:[{minion:1}]}).heroes.bolt.skills;
        // one form alone: nothing; preview says the second form switches the combo on
        run.kit[3]={src:'lib',...zone};assert.ok(R.validateRun(run));assert.deepEqual(R.activeCombos(R.resolveKit(run)),[]);
        assert.deepEqual(R.comboChange(run,{...point},4),{gain:['bind'],lose:[]});
        assert.deepEqual(R.comboChange(run,{...point},3),{gain:[],lose:[]},'replacing the zone gives no pair');
        run.kit[4]={src:'lib',...point};assert.deepEqual(R.activeCombos(R.resolveKit(run)).map(c=>c.id),['bind']);
        assert.deepEqual(R.comboChange(run,{...point},3),{gain:[],lose:['bind']});
        // the combo raises point damage by 20% for the whole kit, before passives, and leaves other forms alone
        const raw=R.resolveKit(run),kit=R.encounterData(run,{id:'n',kind:'battle',waves:[{minion:1}]}).heroes.bolt.skills;
        raw.forEach((s,i)=>{const f=R.formOfKind(s.kind);assert.equal(kit[i].damage,f==='point'&&s.damage>0?Math.round(s.damage*1.2):s.damage,i+' '+s.kind);assert.equal(kit[i].cd,s.cd);});
        assert.equal(kit[5].damage,Math.round(base[5].damage*1.2),'hero point skill also gains');
        run.passives=[{id:'dmg',stacks:1}];const both=R.encounterData(run,{id:'n',kind:'battle',waves:[{minion:1}]}).heroes.bolt.skills;
        assert.equal(both[4].damage,Math.round(Math.round(raw[4].damage*1.2)*1.1));
        // combos are data: unique ids, two different known forms each
        assert.equal(new Set(R.COMBOS.map(c=>c.id)).size,R.COMBOS.length);
        for(const c of R.COMBOS){assert.equal(c.need.length,2);assert.notEqual(c.need[0],c.need[1]);for(const f of c.need)assert.ok(R.FORMS[f]);assert.ok(c.name&&c.text);}
        // the fight still runs with a combo kit, deterministically
        const fight=()=>{const w=R.startEncounter(run,{id:'n',kind:'battle',waves:[{minion:3}]});w.hero.invuln=1e9;let n=0;while(!w.over&&n++<60*200){const t=w.enemies.find(e=>e.hp>0);if(t)for(const s of [0,1,3,4,5])w.cast(s,{x:t.x,z:t.z});w.step({});}return [w.won,n,w.stats.damage];};
        const a=fight();assert.deepEqual(a,fight());assert.equal(a[0],true);
        console.log(JSON.stringify({zone,point,steps:a[1]}));
        """)
        self.assertEqual(result.returncode, 0, result.stderr[-1800:])
        self.assertIn('"steps"', result.stdout)
