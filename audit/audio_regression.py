from playwright.sync_api import sync_playwright
from pathlib import Path
import json, re
root = Path(__file__).resolve().parent.parent
html = (root / 'GS_Action_v14_261003-0447.html').read_text()
patch = re.search(r'<script\b[^>]*>(.*?)</script>', html, re.S).group(1)
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    page = browser.new_page()
    page.goto('about:blank')
    page.add_script_tag(content=patch)
    result = page.evaluate('''async()=>{
      async function render({name,shift=0,start=.7,stop=.8,loop=false,offset=0,duration,oscillator=false}){
        const c=new OfflineAudioContext(1,44100,44100),s=oscillator?c.createOscillator():c.createBufferSource();
        if(!oscillator){const buf=c.createBuffer(1,4410,44100);buf.getChannelData(0).fill(1);s.buffer=buf;s.loop=loop;}
        s.connect(c.destination);window.__GS_ASHIFT=shift;
        if(oscillator)s.start(start);else if(duration===undefined)s.start(start,offset);else s.start(start,offset,duration);
        if(stop!==null)s.stop(stop);window.__GS_ASHIFT=0;
        const rendered=await c.startRendering(),a=rendered.getChannelData(0);let first=-1,last=-1,n=0;
        for(let i=0;i<a.length;i++)if(Math.abs(a[i])>.01){if(first<0)first=i;last=i;n++;}
        return {name,first:first<0?null:first/44100,last:last<0?null:last/44100,nonzeroSamples:n};
      }
      const fixtures=[{name:'control'},{name:'shifted',shift:.5},{name:'loop',shift:.5,loop:true},{name:'offset',shift:.5,offset:.05,stop:null},{name:'oscillator',shift:.5,oscillator:true},{name:'expired',shift:.5,start:.1,stop:.2},{name:'expired-duration',shift:.5,start:.1,stop:null,duration:.05},{name:'preroll-tail',shift:.05,start:0,stop:.1}];
      const results=[];for(const f of fixtures)results.push(await render(f));return results;
    }''')
    for row in result:
        name = row['name']
        if name.startswith('expired'):
            assert row['nonzeroSamples'] == 0, row
        else:
            expected = .7 if name == 'control' else 0 if name == 'preroll-tail' else .2
            assert row['first'] is not None and abs(row['first'] - expected) < 2 / 44100, row
            assert row['nonzeroSamples'] > 0, row
        if name in ('shifted', 'loop', 'oscillator'):
            assert abs(row['last'] - .3) < 2 / 44100, row
        if name == 'offset':
            assert abs(row['last'] - .25) < 2 / 44100, row
    print(json.dumps({'audioCases': len(result), 'result': 'PASS', 'cases': result}, indent=2))
    (root / 'audit/audio-fixed-result.json').write_text(json.dumps(result, indent=2))
    browser.close()
