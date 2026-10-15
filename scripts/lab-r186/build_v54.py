import sys,hashlib
src,dst=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
def rep(old,new,n=1):
    global s
    c=s.count(old)
    assert c==n,(old[:60],c)
    s=s.replace(old,new)

# 1) r128 UMD -> r186.1 ESM (importmap) + classic main script kept sloppy-mode global
rep('''<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"
  onerror="document.body.innerHTML='<div style=&quot;padding:40px;font:14px monospace;color:#e88&quot;>three.js CDN 로드 실패 — 네트워크 확인 후 새로고침</div>'"></script>
<script>
''','''<script type="importmap">
{ "imports": { "three": "https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js" } }
</script>
<script type="module">
/* v54: three r128 UMD → r186.1 ESM. 본문은 sloppy 전역 스크립트(const/function 전역 · 외부 접근 유지)라
   모듈로 바꾸지 않고, THREE 를 window 에 얹은 뒤 아래 gsMain 을 클래식 스크립트로 주입해 실행한다. */
try {
  const THREE = await import("three");
  /* r128 색 경로 유지(대조 기준): 입력 색 변환 끔 + 출력 Linear. 본문 셰이더가 enc() 로 직접 sRGB 인코딩한다. */
  THREE.ColorManagement.enabled = false;
  window.THREE = THREE;
  const s = document.createElement("script");
  s.textContent = document.getElementById("gsMain").textContent;
  document.body.appendChild(s);
} catch (e) {
  console.error(e);
  document.body.innerHTML = '<div style="padding:40px;font:14px monospace;color:#e88">three.js CDN 로드 실패 — 네트워크 확인 후 새로고침</div>';
}
</script>
<script type="text/plain" id="gsMain">
''')

# 2) encoding -> colorSpace (3 sites)
rep('envTex.encoding = THREE.sRGBEncoding;','envTex.colorSpace = THREE.SRGBColorSpace;')
rep('t.encoding = THREE.sRGBEncoding;','t.colorSpace = THREE.SRGBColorSpace;')
rep('①' ' texture.colorSpace = THREE.SRGBColorSpace  →  .encoding = THREE.sRGBEncoding','①' ' texture.colorSpace = THREE.SRGBColorSpace  (v54: r186 = 원본 그대로. 이전 v53 은 r128 .encoding = sRGBEncoding)')

# 3) renderer output Linear (r128 기본과 동일)
rep('renderer.setPixelRatio(Math.min(devicePixelRatio, 2));\nGS_RUPTURE.init(renderer);',
    'renderer.setPixelRatio(Math.min(devicePixelRatio, 2));\nrenderer.outputColorSpace = THREE.LinearSRGBColorSpace; /* v54: r128 LinearEncoding 출력 유지 */\nGS_RUPTURE.init(renderer);')

# 4) light units: r128 legacy lights = intensity*PI. r155+ physical -> *PI
rep('new THREE.HemisphereLight(0x8a9ab8, 0x2a3040, 1.15)','new THREE.HemisphereLight(0x8a9ab8, 0x2a3040, 1.15 * Math.PI)')
rep('new THREE.DirectionalLight(0xffffff, 1.7)','new THREE.DirectionalLight(0xffffff, 1.7 * Math.PI)')
rep('new THREE.DirectionalLight(0xa8c4ff, 0.65)','new THREE.DirectionalLight(0xa8c4ff, 0.65 * Math.PI)')
rep('new THREE.DirectionalLight(0xffe0c0, 0.35)','new THREE.DirectionalLight(0xffe0c0, 0.35 * Math.PI)')

# 4b) v53 pre-existing bug: FAE_VS / FAERG_VS call gsCurve() without _SAG_GLSL -> vertex shader compile fail (fae)
rep('const FAE_VS =\n  _NOISE_GLSL +\n  _FBM_GLSL +\n','const FAE_VS =\n  _NOISE_GLSL +\n  _FBM_GLSL +\n  _SAG_GLSL +\n')
rep('const FAERG_VS =\n  _NOISE_GLSL +\n','const FAERG_VS =\n  _NOISE_GLSL +\n  _SAG_GLSL +\n')

# 5) labels
rep('<title>GlobeStriker · MIL ProjHead 랩 v53 (64종 · 비용절감 · SFX 정리)</title>','<title>GlobeStriker · MIL ProjHead 랩 v54 (64종 · three r186)</title>')
rep('GlobeStriker · MIL ProjHead Lab v53</div>','GlobeStriker · MIL ProjHead Lab v54</div>')
rep('<div class="splice">v53 · 정적 부품','<div class="splice">v54 · three r186.1 · 정적 부품')
rep('k.textContent = "GlobeStriker · ProjHead Lab v53";','k.textContent = "GlobeStriker · ProjHead Lab v54";')
rep('"v53 · 정적 부품 병합(draw −59%)','"v54 · three r186.1 · 정적 부품 병합(draw −59%)')
rep('document.title = "GlobeStriker · ProjHead 랩 v53 ("','document.title = "GlobeStriker · ProjHead 랩 v54 ("')
open(dst,'w',encoding='utf-8').write(s)
print(hashlib.md5(s.encode('utf-8')).hexdigest())
