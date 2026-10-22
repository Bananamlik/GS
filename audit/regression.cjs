const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict'),cp=require('node:child_process');
const html=fs.readFileSync(path.join(__dirname,'../GS_Action_v14_261003-0447.html'),'utf8');
const scripts=[...html.matchAll(/<script\b([^>]*)>([\s\S]*?)<\/script>/g)];
global.window={};
for(const marker of ['window.GA_SIM=(function','const GA_SKILLS=','window.GA_SKILL_LIB=Object.freeze'])vm.runInThisContext(scripts.find(s=>s[2].includes(marker))[2]);
let checked=0;
for(const [i,s] of scripts.entries()){
 if(s[1].includes('importmap')||!s[2].trim())continue;
 const r=cp.spawnSync(process.execPath,['--check','--input-type='+ (s[1].includes('module')?'module':'commonjs')],{input:s[2],encoding:'utf8'});
 assert.equal(r.status,0,`script ${i}: ${r.stderr}`);checked++;
}
const S=window.GA_SIM,D=window.GA_DATA,p=S.pillars[0],u=S.norm(p.x,p.z),at=n=>({x:p.x+u.x*n,z:p.z+u.z*n});
function world(){const w=S.create(D);w.startTrial();w.enemies=w.enemies.slice(0,1);Object.assign(w.hero,at(-15));Object.assign(w.enemies[0],at(6));return w;}
function advance(w,n=180){for(let i=0;i<n;i++)w.step({});}
function close(a,b){assert.ok(Math.abs(a-b)<1e-8,`${a} != ${b}`);}
let cases=0;
{const w=world(),hp=w.enemies[0].hp;assert.ok(w.cast(0,at(20)));advance(w);assert.ok(S.blocked(w.hero,w.enemies[0]));assert.equal(w.enemies[0].hp,hp);assert.equal(w.events.find(e=>e.type==='fx:cast').chainPoints.length,0);cases++;}
{const w=world(),hp=w.enemies[0].hp;w.castLib({...window.GA_SKILL_LIB['C:FB_PROJ:koi'].skill,id:'C:FB_PROJ:koi'},at(20));advance(w);assert.equal(w.enemies[0].hp,hp);cases++;}
{const w=world();w.castTrialBeam('CH:prism',at(20));const fx=w.events.find(e=>e.type==='fx:cast');close(S.dist(fx.origin,fx.target),S.rayPillar(w.hero,u,35));assert.equal(S.blocked(fx.origin,fx.target),false);cases++;}
{const w=world();Object.assign(w.hero,at(-7.2));w.cast(1,at(20));const fx=w.events.find(e=>e.type==='fx:cast');advance(w);for(const e of w.events.filter(e=>e.type==='windup'))close(e.range,S.dist(fx.origin,fx.target));cases++;}
// Clear-path hits still land and chains retain their three-target damage pattern.
{const w=S.create(D);w.startTrial();w.enemies[0].x=0;w.enemies[0].z=-25;w.enemies[1].x=5;w.enemies[1].z=-25;w.enemies[2].x=10;w.enemies[2].z=-25;w.cast(0,{x:0,z:-25});advance(w);assert.deepEqual(w.events.filter(e=>e.type==='hit').map(e=>e.dmg),[40,24,24]);cases++;}
{const w=S.create(D);w.startTrial();w.enemies=w.enemies.slice(0,1);w.castLib({...window.GA_SKILL_LIB['C:FB_PROJ:koi'].skill,id:'C:FB_PROJ:koi'},{x:0,z:-25});advance(w);assert.equal(w.stats.damage,45);cases++;}
// A visible primary cannot chain to the enemy behind the same pillar.
{const w=world();w.spawn('minion');Object.assign(w.enemies[1],at(-6),{hp:1200,hpMax:1200});w.cast(0,at(-6));advance(w);assert.equal(w.enemies[0].hp,1200);assert.equal(w.events.find(e=>e.type==='fx:cast').chainPoints.length,1);cases++;}
// Recheck visibility at impact when a selected primary moves behind cover.
{const w=world(),v={x:-u.z,z:u.x},base=at(6),a={x:base.x+v.x*6,z:base.z+v.z*6},b={x:base.x+v.x*2,z:base.z+v.z*2};Object.assign(w.enemies[0],a);assert.equal(S.blocked(w.hero,a),false);w.cast(0,a);advance(w,8);assert.equal(w.pending.filter(p=>p.type==='chainHit').length,1);Object.assign(w.enemies[0],b);assert.ok(S.inCircle(w.enemies[0],a,4.5));assert.ok(S.blocked(w.hero,b));advance(w);assert.equal(w.stats.damage,0);cases++;}
// Ground effects can still be placed and deal damage behind pillars.
{const w=world();w.castLib({...window.GA_SKILL_LIB['FX-11'].skill,id:'FX-11'},at(6));advance(w);assert.ok(w.stats.damage>0);cases++;}
{const w=world(),profile=Object.values(window.GA_FX_TRIAL).find(p=>p.id.startsWith('GS-')&&p.kind==='circle');assert.ok(profile);assert.ok(w.castTrialBeam(profile.id,at(6)));const fx=w.events.find(e=>e.type==='fx:cast');close(S.dist(w.hero,fx.target),21);cases++;}
// Test the actual rendering adapter too: it must not expand a short combat endpoint.
{const source=html.slice(html.indexOf('function poseFor(entry)'),html.indexOf('\nfunction fx(entry)'));
 const ctx={V:{rigs:new Map(),world:{skills:[]}},formOf:()=> 'beam',muzzleOf:()=>({x:0,y:6,z:0,f:{x:1,y:0,z:0}}),alongLook:()=>{throw Error('combat target must not be extended')},lookBasis:()=>({r:{x:1,z:0}})};
 vm.createContext(ctx);vm.runInContext(source,ctx);const pose=ctx.poseFor({id:'D:PROJ:fissure',kind:'beam',caster:'hero',origin:{x:0,z:0},target:{x:3.9,z:0}});close(pose.target.x,3.9);cases++;}
// Smoke every size tier in the real library through release, impact and sustained effects.
let variants=0;
for(const L of Object.values(window.GA_SKILL_LIB))for(const tier of L.variants?Object.values(L.variants):[{skill:L.skill}]){
 const w=S.create(D);w.startTrial();const sk={...tier.skill,id:L.id};assert.ok(w.castLib(sk,{x:0,z:-25}),L.id);advance(w,1200);
 assert.ok(Number.isFinite(w.stats.damage)&&Number.isFinite(w.hero.hp),L.id);
 assert.ok(w.events.some(e=>e.type==='impact'),L.id+' no impact');variants++;
}
console.log(JSON.stringify({syntaxScripts:checked,regressionCases:cases,libraryVariants:variants,result:'PASS'},null,2));
