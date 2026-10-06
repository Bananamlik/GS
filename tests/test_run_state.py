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
    return '\n'.join(wrap(code) for code in [pick('GS VFX validation contract'), pick('window.GA_DRAFT_POLICY='), pick('window.GA_SIM='), pick('window.GA_DATA='), pick('window.GA_SKILL_LIB='), run])


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
        if(quiet){const r2=R.visitNode(r1,quiet.id);assert.equal(r2.stop.nodeId,quiet.id);assert.deepEqual(R.availableNodes(r2),[]);assert.ok(R.validateRun(r2));
          const r3=quiet.kind==='shop'?R.chooseStop(r2,null):R.chooseStop(r2,0,undefined);assert.equal(r3.nodeId,quiet.id);assert.equal(r3.floor,2);assert.equal(r3.stop,null);assert.ok(R.validateRun(r3));}
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
            assert.ok(w.over&&w.won,'battle '+n.id+' not won');run=R.finishEncounter(run,w,n);battles++;
            if(run.reward){const o=run.reward.offers[0];run=R.takeReward(run,o?{index:0,slot:o.slots?.[0]}:null);}}
          else{run=R.visitNode(run,n.id);run=R.chooseStop(run,run.stop.kind==='shop'?null:run.stop.kind==='rest'?0:run.stop.options.length-1);}
          assert.ok(R.validateRun(run),'invalid after '+n.id);}
        assert.equal(run.status,'won');assert.equal(run.act,3);assert.equal(run.history.length,18);
        assert.ok(battles>=6);assert.ok(run.history.filter(h=>h.kind==='boss').length===3);assert.ok(run.gold>0);assert.equal(run.reward,null);
        """)
        self.assertEqual(result.returncode, 0, result.stderr)


WIN = """
const win=(run,n)=>{const w=R.startEncounter(run,n);w.hero.invuln=1e9;for(let i=0;i<60*600&&!w.over;i++){for(const e of w.enemies)if(e.hp>0){e.hp=0;e.state='dead';}w.step({});}assert.ok(w.won);return R.finishEncounter(run,w,n);};
"""


class RewardTests(unittest.TestCase):
    def test_battle_reward_offers_and_skill_swap(self):
        result = node(WIN + """
        const run=R.createRun('bolt',31),n=R.availableNodes(run)[0];const a=win(run,n),b=win(run,n);
        assert.deepEqual(a.reward,b.reward);assert.ok(a.reward.gold>=15&&a.reward.gold<=25);assert.equal(a.reward.offers.length,3);
        assert.deepEqual(R.availableNodes(a),[]);assert.throws(()=>R.startEncounter(a,R.mapNode(a,a.map.a1.find(x=>x.floor===1).id)),/not reachable/);
        const kitIds=new Set(R.resolveKit(a).map(s=>s.id));
        for(const o of a.reward.offers){assert.equal(o.type,'skill');assert.ok(GA_SKILL_LIB[o.id].rating>=3);assert.ok(!kitIds.has(o.id));assert.ok(o.slots.length>0);}
        assert.deepEqual(a.reward.offers.map(o=>o.cls).map(c=>c==='guard'?'skill':c),['basic','skill','skill']);
        const o=a.reward.offers[1];assert.throws(()=>R.takeReward(a,{index:1,slot:2}),/Invalid slot/);
        const t=R.takeReward(a,{index:1,slot:o.slots[0]});assert.equal(t.gold,a.reward.gold);assert.equal(t.reward,null);assert.ok(R.validateRun(t));
        assert.deepEqual(t.kit[o.slots[0]],{src:'lib',id:o.id,size:o.size});assert.ok(R.availableNodes(t).length>0);
        const next=R.availableNodes(t).find(x=>['battle','elite'].includes(x.kind));if(next)assert.equal(R.encounterData(t,next).heroes.bolt.skills[o.slots[0]].id,o.id);
        const skip=R.takeReward(a,null);assert.equal(skip.gold,a.reward.gold);assert.deepEqual(skip.kit,a.kit);
        const bad=JSON.parse(JSON.stringify(a));bad.reward.offers[0].id='nope';assert.equal(R.validateRun(bad),false);
        """)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_passives_change_only_combat_copies(self):
        result = node("""
        const run=R.createRun('bolt',8);run.reward={nodeId:'x',kind:'elite',gold:40,offers:[{type:'passive',id:'dmg',name:'',text:''},{type:'passive',id:'cd',name:'',text:''}]};
        assert.ok(R.validateRun(run));let t=R.takeReward(run,{index:0});assert.deepEqual(t.passives,[{id:'dmg',stacks:1}]);
        t.reward=run.reward;t=R.takeReward(t,{index:0});assert.deepEqual(t.passives,[{id:'dmg',stacks:2}]);
        t.reward=run.reward;t=R.takeReward(t,{index:1});assert.equal(t.passives.length,2);
        const node={id:'n',kind:'battle',waves:[{minion:1}]},base=GA_DATA.heroes.bolt.skills,kit=R.encounterData(t,node).heroes.bolt.skills;
        assert.equal(kit[3].damage,Math.round(base[3].damage*1.2));assert.equal(kit[3].cd,+(base[3].cd*0.92).toFixed(2));
        assert.equal(base[3].damage,90);assert.ok(kit.every(s=>GA_VFX_QA.validateSkill({...s}).ok));
        const bad=JSON.parse(JSON.stringify(t));bad.passives.push({id:'ghost',stacks:1});assert.equal(R.validateRun(bad),false);
        const dup=JSON.parse(JSON.stringify(t));dup.passives.push({id:'dmg',stacks:1});assert.equal(R.validateRun(dup),false);
        """)
        self.assertEqual(result.returncode, 0, result.stderr)


STOP = """
const stopAt=(kind,seed=1)=>{for(let s=seed;s<seed+400;s++){const r=R.createRun('bolt',s);for(const n of r.map.a1)if(n.kind===kind&&n.floor===1){const f0=r.map.a1.find(x=>x.floor===0&&x.next.includes(n.id));r.nodeId=f0.id;r.floor=1;return {r,n};}}throw Error('no '+kind);};
"""


class StopTests(unittest.TestCase):
    def test_shop_buy_and_leave(self):
        result = node(STOP + """
        const {r,n}=stopAt('shop');r.gold=100;const a=R.visitNode(r,n.id),b=R.visitNode(r,n.id);assert.deepEqual(a.stop,b.stop);assert.equal(a.stop.kind,'shop');
        assert.ok(R.validateRun(a));const heal=a.stop.options.findIndex(o=>o.fx.hp);a.hero.hp=100;
        let t=R.chooseStop(a,heal);assert.equal(t.gold,70);assert.equal(t.hero.hp,100+Math.round(.3*t.hero.hpMax));assert.ok(t.stop.options[heal].sold);
        assert.throws(()=>R.chooseStop(t,heal),/Sold out/);
        const sk=t.stop.options.findIndex(o=>o.fx.skill);const o=t.stop.options[sk];t.gold=o.price-1;assert.throws(()=>R.chooseStop(t,sk,o.fx.skill.slots[0]),/Not enough gold/);
        t.gold=200;assert.throws(()=>R.chooseStop(t,sk,2),/Invalid slot/);t=R.chooseStop(t,sk,o.fx.skill.slots[0]);assert.equal(t.kit[o.fx.skill.slots[0]].id,o.fx.skill.id);assert.equal(t.gold,200-o.price);
        assert.deepEqual(R.availableNodes(t),[]);const out=R.chooseStop(t,null);assert.equal(out.stop,null);assert.equal(out.nodeId,n.id);assert.equal(out.floor,2);assert.ok(R.validateRun(out));
        assert.ok(R.availableNodes(out).length>0);
        """)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_event_and_rest(self):
        result = node(STOP + """
        const e=stopAt('event');e.r.gold=0;const ev=R.visitNode(e.r,e.n.id);assert.equal(ev.stop.kind,'event');assert.ok(R.EVENTS.some(x=>x.title===ev.stop.title));
        assert.throws(()=>R.chooseStop(ev,null),/Choose/);
        const pay=ev.stop.options.findIndex(o=>o.fx.gold<0);if(pay>=0)assert.throws(()=>R.chooseStop(ev,pay),/Not enough gold/);
        const done=R.chooseStop(ev,ev.stop.options.length-1);assert.equal(done.stop,null);assert.equal(done.floor,2);assert.equal(done.history.at(-1).result,ev.stop.options.at(-1).label);assert.ok(R.validateRun(done));
        const z=stopAt('rest');z.r.kit[3]={src:'lib',id:'FX-06',size:'M'};z.r.hero.hp=1;const rs=R.visitNode(z.r,z.n.id);
        const up=rs.stop.options.findIndex(o=>o.fx.upgrade?.slot===3);assert.ok(up>0);assert.equal(rs.stop.options[up].fx.upgrade.size,'L');
        const u=R.chooseStop(rs,up);assert.equal(u.kit[3].size,'L');assert.equal(u.hero.hp,1);const nn={id:'q',kind:'battle',waves:[{minion:1}]};
        assert.equal(R.encounterData(u,nn).heroes.bolt.skills[3].radius,GA_SKILL_LIB['FX-06'].variants.L.skill.radius);
        const h=R.chooseStop(rs,0);assert.equal(h.hero.hp,1+Math.round(.3*h.hero.hpMax));
        const bad=JSON.parse(JSON.stringify(rs));bad.stop.options[0].fx={hp:5};assert.equal(R.validateRun(bad),false);
        const bad2=JSON.parse(JSON.stringify(rs));bad2.stop.options[0].fx={teleport:1};assert.equal(R.validateRun(bad2),false);
        """)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
