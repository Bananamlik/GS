"""Run and meta state (S1 of docs/design/gs-run-skeleton_v1_261006-2213.md). Node only, no browser."""
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


def runtime_blocks():
    source = (ROOT / 'index.html').read_text()
    blocks = [code for attrs, code in re.findall(r'<script\b([^>]*)>(.*?)</script>', source, re.S) if 'module' not in attrs]
    pick = lambda marker: next(code for code in blocks if marker in code)
    run = re.search(r'<script id="gaRunState">(.*?)</script>', source, re.S)[1]
    # Each block runs in its own scope; module is hidden so the QA contract registers on window as in the page.
    wrap = lambda code: '(function(module){' + code + '\n})(undefined);'
    return '\n'.join(wrap(code) for code in [pick('GS VFX validation contract'), pick('window.GA_SIM='), pick('window.GA_DATA='), pick('window.GA_SKILL_LIB='), run])


def node(body):
    script = ("global.window=global;\nconst __store=new Map();global.localStorage={getItem:k=>__store.has(k)?__store.get(k):null,"
              "setItem:(k,v)=>__store.set(k,String(v)),removeItem:k=>__store.delete(k)};\n"
              + runtime_blocks() + "\nconst assert=require('node:assert/strict'),R=GA_RUN;\n" + body)
    return subprocess.run(['node'], input=script, capture_output=True, text=True)


class RunStateTests(unittest.TestCase):
    def test_create_validate_save_and_load_round_trip(self):
        result = node("""
        const meta=R.createMeta();assert.ok(R.validateMeta(meta));
        const run=R.createRun('bolt',927,{meta});assert.ok(R.validateRun(run));
        assert.equal(run.hero.hp,GA_DATA.heroes.bolt.hp);assert.equal(run.kit.length,GA_DATA.heroes.bolt.skills.length);
        assert.throws(()=>R.createRun('flame',1,{meta}),/locked/);assert.throws(()=>R.createRun('nobody',1),/Unknown/);
        run.kit[3]={src:'lib',id:'GS-web',size:''};run.gold=40;run.hero.hp=120;run.passives.push({id:'dmg',stacks:1});
        assert.ok(R.validateRun(run));assert.deepEqual(R.saveRun(run),{ok:true});
        const back=R.loadRun();assert.equal(back.reason,null);assert.deepEqual(back.value,run);
        assert.deepEqual(R.saveMeta(meta),{ok:true});assert.deepEqual(R.loadMeta().value,meta);
        assert.ok(R.clearRun());assert.equal(R.loadRun().reason,'empty');
        localStorage.setItem(R.RUN_KEY,'{bad json');assert.equal(R.loadRun().reason,'invalid');
        """)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_invalid_runs_are_rejected(self):
        result = node("""
        const ok=R.createRun('rain',5);assert.ok(R.validateRun(ok));
        const bad=f=>{const r=JSON.parse(JSON.stringify(ok));f(r);return R.validateRun(r);};
        assert.equal(bad(r=>r.contract='gs-wave-boundary-1'),false);
        assert.equal(bad(r=>r.hero.hp=r.hero.hpMax+1),false);
        assert.equal(bad(r=>r.hero.hp=0),false);
        assert.equal(bad(r=>{r.hero.hp=0;r.status='lost';}),true);
        assert.equal(bad(r=>r.hero.hpMax=1),false);
        assert.equal(bad(r=>r.act=4),false);
        assert.equal(bad(r=>r.gold=-1),false);
        assert.equal(bad(r=>r.gold=1.5),false);
        assert.equal(bad(r=>r.kit.pop()),false);
        assert.equal(bad(r=>r.kit[0]={src:'hero',slot:1}),false);
        assert.equal(bad(r=>r.kit[0]={src:'lib',id:'no-such-skill',size:''}),false);
        assert.equal(bad(r=>r.kit[0]={src:'lib',id:'FX-06',size:''}),false);
        assert.equal(bad(r=>r.kit[0]={src:'lib',id:'FX-06',size:'M'}),true);
        assert.equal(bad(r=>r.stats.damage=NaN),false);
        assert.equal(bad(r=>r.status='paused'),false);
        assert.equal(R.saveRun({}).ok,false);
        const m=R.createMeta();assert.equal(R.validateMeta({...m,unlocked:{...m.unlocked,heroes:['ghost']}}),false);
        assert.equal(R.validateMeta({...m,wins:1}),false);
        """)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_seeds_are_deterministic_and_kit_resolves_for_combat(self):
        result = node("""
        const a=R.createRun('bolt',42),b=R.createRun('bolt',42);
        assert.equal(R.encounterSeed(a,'a1-n2'),R.encounterSeed(b,'a1-n2'));
        assert.notEqual(R.encounterSeed(a,'a1-n2'),R.encounterSeed(a,'a1-n3'));
        const x=R.rng(7),y=R.rng(7);for(let i=0;i<20;i++)assert.equal(x(),y());
        a.kit[3]={src:'lib',id:'FX-06',size:'M'};
        const kit=R.resolveKit(a);assert.equal(kit.length,6);
        assert.deepEqual(kit[0],GA_DATA.heroes.bolt.skills[0]);
        assert.equal(kit[3].id,'FX-06');assert.equal(kit[3].key,GA_DATA.heroes.bolt.skills[3].key);
        assert.equal(kit[3].damage,GA_SKILL_LIB['FX-06'].variants.M.skill.damage);
        assert.ok(GA_VFX_QA.validateSkill(kit[3]).ok);
        kit[3].damage=1;assert.notEqual(GA_SKILL_LIB['FX-06'].variants.M.skill.damage,1);
        """)
        self.assertEqual(result.returncode, 0, result.stderr)


# Simple deterministic auto-player: nearest enemy, first ready attack, close in when far.
AUTOPLAY = """
const play=(run,node,maxSteps=60*240,idle=false)=>{const w=R.startEncounter(run,node);let i=0;
 for(;i<maxSteps&&!w.over;i++){const h=w.hero,alive=w.enemies.filter(e=>e.hp>0);
  if(alive.length&&!idle){alive.sort((a,b)=>Math.hypot(a.x-h.x,a.z-h.z)-Math.hypot(b.x-h.x,b.z-h.z));const t=alive[0];
   for(const slot of [4,3,5,1,0])if(w.cast(slot,{x:t.x,z:t.z}))break;
   const dx=t.x-h.x,dz=t.z-h.z,d=Math.hypot(dx,dz)||1;w.step(d>30?{mx:dx/d,mz:dz/d}:{});}else w.step({});}
 return w;};
const NODE={id:'a1-n0',kind:'battle',waves:[{minion:3},{minion:2,archer:1}]};
"""


class EncounterTests(unittest.TestCase):
    def test_encounter_is_deterministic_and_carries_hp_and_stats(self):
        result = node(AUTOPLAY + """
        const run=R.createRun('bolt',11);
        const a=play(run,NODE),b=play(run,NODE);
        assert.ok(a.over&&a.won);assert.equal(a.wave,2);
        assert.equal(JSON.stringify(a.stats),JSON.stringify(b.stats));assert.equal(a.hero.hp,b.hero.hp);assert.equal(a.t,b.t);
        const next=R.finishEncounter(run,a,NODE);assert.ok(R.validateRun(next));
        assert.equal(next.status,'active');assert.equal(next.hero.hp,a.hero.hp);assert.equal(next.stats.kills,6);assert.equal(next.stats.nodes,1);
        assert.deepEqual(next.history,[{nodeId:'a1-n0',kind:'battle',result:'won'}]);assert.equal(run.stats.nodes,0);
        run.hero.hp=50;assert.equal(R.startEncounter(run,NODE).hero.hp,50);
        assert.throws(()=>R.finishEncounter(run,R.startEncounter(run,NODE),NODE),/not over/);
        """)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_loss_ends_the_run(self):
        result = node(AUTOPLAY + """
        const run=R.createRun('rain',3);run.hero.hp=1;
        const w=play(run,{id:'a1-n1',kind:'elite',waves:[{elite:2,archer:2}]},60*120,true);
        assert.ok(w.over);assert.equal(w.won,false);
        const next=R.finishEncounter(run,w,{id:'a1-n1',kind:'elite',waves:[{elite:2,archer:2}]});
        assert.equal(next.status,'lost');assert.equal(next.hero.hp,0);assert.ok(R.validateRun(next));
        assert.throws(()=>R.startEncounter(next,NODE),/not active/);
        """)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_enemy_scaling_kit_and_node_validation(self):
        result = node("""
        const run=R.createRun('bolt',9),node={id:'n',kind:'battle',waves:[{minion:1}]};
        const d1=R.encounterData(run,node);assert.equal(d1.enemies.minion.hp,GA_DATA.enemies.minion.hp);assert.deepEqual(d1.waves,[{minion:1}]);
        run.act=3;run.difficulty=2;const d3=R.encounterData(run,node);
        assert.equal(d3.enemies.minion.hp,Math.round(GA_DATA.enemies.minion.hp*2.4*1.3));
        assert.equal(d3.enemies.boss.attacks.gaze.damage,Math.round(GA_DATA.enemies.boss.attacks.gaze.damage*1.6*1.3*10)/10);
        assert.equal(GA_DATA.enemies.minion.hp,60);
        run.kit[3]={src:'lib',id:'GS-web',size:''};assert.equal(R.encounterData(run,node).heroes.bolt.skills[3].id,'GS-web');
        for(const bad of [{id:'',kind:'battle',waves:[{minion:1}]},{id:'x',kind:'shop',waves:[{minion:1}]},{id:'x',kind:'battle',waves:[]},
          {id:'x',kind:'battle',waves:[{ghost:1}]},{id:'x',kind:'battle',waves:[{minion:0}]},{id:'x',kind:'battle',waves:[{minion:1},{minion:1},{minion:1},{minion:1}]}])
          assert.throws(()=>R.encounterData(run,bad),/Invalid node/);
        """)
        self.assertEqual(result.returncode, 0, result.stderr)


class MapTests(unittest.TestCase):
    def test_map_is_deterministic_and_well_formed(self):
        result = node("""
        const a=R.createRun('bolt',77),b=R.createRun('bolt',77),c=R.createRun('bolt',78);
        assert.deepEqual(a.map,b.map);assert.notDeepEqual(a.map,c.map);assert.ok(R.validMap(a.map));
        for(let act=1;act<=3;act++){const nodes=a.map['a'+act];
          assert.equal(nodes.filter(n=>n.kind==='boss').length,1);assert.equal(nodes.find(n=>n.kind==='boss').floor,5);
          for(let f=0;f<5;f++){const row=nodes.filter(n=>n.floor===f);assert.ok(row.length>=2&&row.length<=3);
            const next=new Set(row.flatMap(n=>n.next));assert.equal(next.size,nodes.filter(n=>n.floor===f+1).length,'every next-floor node reachable');}
          assert.ok(nodes.filter(n=>n.floor===0).every(n=>n.kind==='battle'));
          assert.ok(nodes.filter(n=>n.floor===1).every(n=>n.kind!=='elite'));
          for(const n of nodes)if(n.waves)assert.ok(R.validNode(n));}
        assert.equal(a.map.a3.find(n=>n.kind==='boss').waves.at(-1).boss,1);
        const bad=JSON.parse(JSON.stringify(a));bad.map.a1[0].next=['a1-f3-n0'];assert.equal(R.validateRun(bad),false);
        const bad2=JSON.parse(JSON.stringify(a));bad2.nodeId='a1-f9-n9';assert.equal(R.validateRun(bad2),false);
        """)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_reachability_and_non_combat_visit(self):
        result = node("""
        const run=R.createRun('rain',5);
        assert.deepEqual(R.availableNodes(run).map(n=>n.floor),R.availableNodes(run).map(()=>0));
        const f0=R.availableNodes(run)[0],far=run.map.a1.find(n=>n.floor===2);
        assert.throws(()=>R.startEncounter(run,far),/not reachable/);
        assert.throws(()=>R.visitNode(run,f0.id),/needs an encounter/);
        const r1=JSON.parse(JSON.stringify(run));r1.nodeId=f0.id;r1.floor=1;assert.ok(R.validateRun(r1));
        const quiet=R.availableNodes(r1).find(n=>!['battle','elite','boss'].includes(n.kind));
        if(quiet){const r2=R.visitNode(r1,quiet.id);assert.equal(r2.nodeId,quiet.id);assert.equal(r2.floor,2);assert.equal(r2.history.at(-1).result,'visited');assert.ok(R.validateRun(r2));}
        """)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_full_run_through_three_acts(self):
        result = node("""
        let run=R.createRun('stone',2024);let steps=0,battles=0;
        while(run.status==='active'&&steps++<60){const opts=R.availableNodes(run);assert.ok(opts.length>0,'dead end at '+run.act+'/'+run.floor);const n=opts[0];
          if(['battle','elite','boss'].includes(n.kind)){const w=R.startEncounter(run,n);w.hero.invuln=1e9;
            for(let i=0;i<60*600&&!w.over;i++){const h=w.hero,alive=w.enemies.filter(e=>e.hp>0);
              if(alive.length){alive.sort((a,b)=>Math.hypot(a.x-h.x,a.z-h.z)-Math.hypot(b.x-h.x,b.z-h.z));const t=alive[0];
                for(const slot of [4,5,1,0])if(w.cast(slot,{x:t.x,z:t.z}))break;const dx=t.x-h.x,dz=t.z-h.z,d=Math.hypot(dx,dz)||1;w.step(d>25?{mx:dx/d,mz:dz/d}:{});}else w.step({});}
            assert.ok(w.over&&w.won,'battle '+n.id+' not won');run=R.finishEncounter(run,w,n);battles++;}
          else run=R.visitNode(run,n.id);
          assert.ok(R.validateRun(run),'invalid after '+n.id);}
        assert.equal(run.status,'won');assert.equal(run.act,3);assert.equal(run.history.length,18);
        assert.ok(battles>=6);assert.ok(run.history.filter(h=>h.kind==='boss').length===3);
        """)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
