"""Render every library variant at small resolution; capture shader/contact evidence.

This checks rendering and adapter contracts, not human visual/audio approval.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

parser=argparse.ArgumentParser()
parser.add_argument('--url',default='http://127.0.0.1:8000/')
parser.add_argument('--output',type=Path,required=True)
parser.add_argument('--limit',type=int,default=0)
args=parser.parse_args()
args.output.parent.mkdir(parents=True,exist_ok=True)
result={'rows':[],'errors':[],'manualVisualApproved':False,'audioApproved':False}
with sync_playwright() as p:
    options=dict(executable_path=os.environ.get('GS_CHROMIUM','/usr/bin/chromium'),headless=True,
        args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
    if os.environ.get('HTTPS_PROXY'):
        options['proxy']={'server':os.environ['HTTPS_PROXY'],'bypass':'localhost,127.0.0.1'}
    browser=p.chromium.launch(**options)
    page=None
    def open_page():
        global page
        if page:page.context.close()
        page=browser.new_page(viewport={'width':390,'height':844})
        page.on('pageerror',lambda e:result['errors'].append(str(e)))
        expected_404={args.url.rsplit('/',1)[0]+'/favicon.ico',args.url.rsplit('/',1)[0]+'/models/white_order_mech_opt.glb'}
        page.on('console',lambda m:result['errors'].append(m.text) if m.type=='error' and not ('404' in m.text and m.location.get('url') in expected_404) else None)
        response=page.goto(args.url,wait_until='networkidle',timeout=60000)
        assert response and response.status==200,'Runtime did not load'
        digest=hashlib.sha256(response.body()).hexdigest()
        if 'sourceSha256' in result:assert result['sourceSha256']==digest,'Source changed during audit'
        result['sourceSha256']=digest
        page.wait_for_function('window.GS_ACTION && window.GS_STUDIO',timeout=60000)
        page.evaluate('''() => {
          window.__GS_BENCH_CALIBRATING=true;window.sfxMuted=true;
          const R=STAGE3D.env.renderer,C=STAGE3D.host.composer,c=STAGE3D.env.camera;
          R.info.autoReset=false;R.setDrawingBufferSize(64,64,1);C.setPixelRatio(1);C.setSize(64,64);
          c.aspect=1;c.position.set(0,22,65);c.lookAt(0,3,-15);c.updateProjectionMatrix();c.updateMatrixWorld();
        }''')
    open_page()
    ids=page.evaluate('Object.keys(GA_SKILL_LIB)')
    result['catalogSkills']=len(ids)
    result['buildId']=page.evaluate('GS_ACTION.buildId')
    if args.limit:ids=ids[:args.limit]
    result['selectedSkills']=len(ids)
    result['scope']='full-library' if len(ids)==result['catalogSkills'] else 'subset'
    result['timeline']='Controlled 0.05-second effect steps; not a performance measurement'
    for index,id in enumerate(ids):
        if index and index%10==0:open_page()
        rows=page.evaluate('''async id => {
          const L=GA_SKILL_LIB[id],mod=STAGE3D.getEffect(id),R=STAGE3D.env.renderer,
            C=STAGE3D.host.composer,gl=R.getContext(),rows=[];
          await STAGE3D.prepare(id);
          for(const [size,v] of (L.variants?Object.entries(L.variants):[['',L]])){
            VFX_COMBAT.stopAll();const sk=v.skill;C.render(0);
            const baseline=new Uint8Array(64*64*4);gl.readPixels(0,0,64,64,gl.RGBA,gl.UNSIGNED_BYTE,baseline);
            const cast=VFX_COMBAT.cast({id,origin:{x:-10,y:3,z:-15},target:{x:10,y:0,z:-15},
              direction:{x:1,y:0,z:0},playAudio:false,scale:sk.fxScale||1,startAt:sk.fxStart||0,
              flightTime:.5,chainPoints:[{x:-5,y:0,z:-15},{x:0,y:0,z:-15},{x:10,y:0,z:-15}],
              structureAnchors:[{x:0,z:-15}]});
            const frames=[];let time=0;
            const nativeContact=cast.contactTime??L.native?.firstHit??.5;
            const times=[.25,Math.max(.3,Math.min(5,nativeContact-(sk.fxStart||0))),5.5].sort((a,b)=>a-b);
            for(const t of times){for(let dt=t-time;dt>1e-9;){const step=Math.min(.05,dt);mod.update(step);dt-=step;}
              time=t;STAGE3D.syncLights();R.info.reset();C.render(0);
              const pixels=new Uint8Array(64*64*4);gl.readPixels(0,0,64,64,gl.RGBA,gl.UNSIGNED_BYTE,pixels);
              let energy=0,changedPixels=0;for(let i=0;i<pixels.length;i+=4){energy+=pixels[i]+pixels[i+1]+pixels[i+2];
                if(pixels[i]!==baseline[i]||pixels[i+1]!==baseline[i+1]||pixels[i+2]!==baseline[i+2])changedPixels++;}
              frames.push({t,changedPixels,calls:R.info.render.calls,energy,glError:gl.getError()});
            }
            let nonFinite=0;for(const root of mod.__gsRoots||[])root.traverse(o=>{
              if(o.matrixWorld.elements.some(x=>!Number.isFinite(x)))nonFinite++;
              const a=o.geometry?.attributes.position;if(a&&!a.isInterleavedBufferAttribute)
                for(const x of a.array)if(!Number.isFinite(x)){nonFinite++;break;}
            });
            rows.push({id,size,accepted:cast.ok,reason:cast.reason||null,contactTime:cast.contactTime,
              impactTimes:cast.impactTimes,pixelsChanged:frames.some(f=>f.changedPixels>0),nativeFirstHit:L.native?.firstHit,frames,nonFinite,
              passed:!!cast.ok&&!nonFinite&&frames.every(f=>f.glError===0)});
            VFX_COMBAT.stop(id);
          }
          return rows;
        }''',id)
        result['rows'].extend(rows)
        args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2))
        if (index+1)%10==0 or index+1==len(ids):
            print(json.dumps({'skills':index+1,'variants':len(result['rows']),
                'failures':sum(not r['passed'] for r in result['rows']),'errors':len(result['errors'])}),flush=True)
    result['completion']='completed'
    result['passed']=all(r['passed'] for r in result['rows']) and not result['errors']
    args.output.write_text(json.dumps(result,ensure_ascii=False,indent=2))
    browser.close()
    assert result['passed'],'See audit result for rendering failures'
