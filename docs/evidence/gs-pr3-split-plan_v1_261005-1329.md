# PR #3 분할 계획 (코드 분할은 아직 하지 않음)

작성: 2026-10-05 · 기준: main `76ddfb4` ← `codex/cloud-runtime-hardening` `953dd12`
실행본 변경: 2개 파일(동일 내용), diff 약 +330줄, 28개 hunk, 바뀐 script 블록 3개.

## 왜 코드를 아직 안 쪼갰나

변경들이 같은 함수를 공유해 hunk 단위로 떼면 중간 상태가 깨진다. 예: `prepareWave`는 벤치 계측(`benchPhaseStart/End`), 예열 큐, 4개씩 분할, 폭풍 훅(`H.syncStormBatches?.()`)을 한 함수 안에서 모두 쓴다. 쪼갠 branch는 브라우저 회귀 테스트(`tests/`)와 three.js CDN 접근이 있는 환경에서 만들고 검증해야 한다. 검증 없는 혼합본은 만들지 않았다.

## 묶음 (A→D 순서로 PR 권장)

| 묶음 | 내용 | 대표 위치 (branch 파일) | 의존 |
|---|---|---|---|
| A. 독립·저위험 | 출력 패스 생략(`outputPass`, `syncOutputPass`), 렌더 크기/픽셀비 중복 설정 생략(`applyRenderQuality`), 복원 안내의 준비 완료 확인 | 호스트 블록 `composer.addPass(OutputPass)` 근처, `applyRenderQuality`, tick의 `syncOutputPass()` | 없음 |
| A'. 프레임 제한 | `GS_PERFORMANCE_POLICY.createPacer`, tick의 경과 시간 기준 pacing(`framePacer.allow`) | `#gsPerformancePolicy` 스크립트, `tick()` | `target()` 변경(`Math.max(fpsCap>0?fpsCap:20,…)`)은 B의 보정과 결합 |
| A''. 모듈 준비 취소 | `shaderContextEpoch`, `ownEffect().prepare()`의 취소/세대 | 호스트 블록 `ownEffect` 앞뒤 | 없음 (WebGL 이벤트 리스너만 추가) |
| B. 측정 계측 | `benchPhaseStart/End`, `calibrateBenchPacing`, `runBench`/`finishBench` 변경, `__GS_BENCH_CALIBRATING`, `__GS_TRACE_END` | `// @V10 benchmark` 구역 | A' 선행 권장 |
| C. 예열·복구 | `warmBatch` 큐/`runWarmBatch`, 4개씩 분할, `prepareRun`/`runAlreadyPrepared`, `beginReady` 복구, `cancelWarmFor`, 예열 루트 숨김, `gpuSweep`의 `warmRoots` 보호 | `prepareWave`, `warmBatch`, `fx`, `stopPool`, `start`, `beginReady`, 컨텍스트 이벤트 | B 필요(`benchPhase*` 호출), D는 선택(`H.syncStormBatches?.()`) |
| D. 폭풍 배칭 | `createStormBatches`, `syncStormBatches`, `composer.render` 오버라이드, `skipZeroStormSurfaces`, CH:storm 훅 | 호스트 블록 `stormBatches…` ~ CH 프리셋 등록 | 없음(C의 훅은 선택 호출). **GPU 증거 전 병합 보류 권장** |

## 병합 게이트

- A·A'·A'': 회귀 테스트 통과 + 문법 검사. 실기기 증거 불필요(동작 보존 변경).
- B: 실제 GPU에서 보정 결과(`calibration.usable`, 관측 Hz)가 합리적인지 1회 확인.
- C: 실제 GPU에서 시작 준비 시간과 첫 사용 끊김 비교(변경 전/후 각 3회).
- D: 실제 GPU에서 프레임 시간 개선이 있을 때만. 개선 없으면 닫음. 병합 전 프레임당 할당 제거(`barriers`, `{z,order,group}`, `Map`, `filter/map/sort`, 임시 배열 재사용).

## 실제 GPU 측정 (도구 설치 불필요)

게임 안에 성능 측정 버튼이 있다. 사용자 PC의 Chrome으로 게임을 열고 `성능 측정`(60초) 또는 열 측정(600초)을 실행하면 결과 텍스트에 `GPU:` 줄이 나온다. 이 줄이 SwiftShader가 아닌 실제 GPU 이름이어야 유효하다. 30/60FPS 제한과 품질(자동/낮음/높음)별로 각 3회 이상, 결과 텍스트와 JSON을 `docs/evidence/`에 저장한다.

## 이 분석의 한계

- hunk 분류는 diff를 읽고 한 것이며 빌드·실행으로 확인하지 않았다.
- `tests/` 두 파일이 어떤 묶음을 각각 덮는지는 세부 매핑하지 않았다.
- 이 계획 작성 환경은 jsdelivr/unpkg 접근이 막혀 브라우저 테스트를 실행하지 못했다.
