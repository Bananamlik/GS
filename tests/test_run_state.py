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
    return '\n'.join(wrap(code) for code in [pick('GS VFX validation contract'), pick('window.GA_DATA='), pick('window.GA_SKILL_LIB='), run])


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


if __name__ == '__main__':
    unittest.main()
