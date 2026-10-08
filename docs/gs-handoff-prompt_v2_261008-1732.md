# GS Action 인계 프롬프트 (v2)

작성: 2026-10-08 01:53 KST (v2 갱신: 2026-10-08 17:32 KST, PR #31 병합 반영). 대상: 새 Claude Code 세션. 저장소 `Bananamlik/GS`.
이 문서 하나로 현재 상태를 이해하고 잔여 작업을 이어갈 수 있게 썼다. 검증하지 못한 것은 **UNVERIFIED**로 표기.

---

## 0. 새 세션에 주는 지시 (이 블록을 그대로 프롬프트로 사용)

> 너는 `Bananamlik/GS`(GS Action: 단일 HTML 액션 게임 + VFX 스튜디오)를 이어서 개발한다.
> 시작 전에 반드시 읽어라: `CLAUDE.md`, `docs/STATUS.md`, `docs/design/gs-run-skeleton_v1_261006-2213.md`, `docs/evidence/gs-session-wrapup_v1_261007-0016.md`, 이 문서.
> 시작 시 `md5sum index.html GS_Action_v34_runtime.html`을 출력하고 `0eaa8b73a1a4ef38a48e9809a52d5bd8`과 다르면 멈추고 보고해라.
> 작업 순서는 §7 계획을 따른다. 각 단계는 `main`에서 새 브랜치 → 코드 PR(초안) → CI 43개(+추가분) 통과 → 사용자 병합 지시 대기.
> 병합은 사용자가 지시할 때만. main 직접 push 금지. 코드 PR과 docs PR 섞지 않기.
> 모호하면 시작 전에 질문해라. 추측 작업 금지.

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|---|---|
| 정체 | 브라우저 단일 HTML(약 62,800줄). three.js(CDN `cdn.jsdelivr.net`) 기반 3D 액션 게임 + VFX 랩(Lab) |
| 실행본 | `index.html` = `GS_Action_v34_runtime.html`. **항상 byte 동일**. 둘 다 같이 수정 |
| 현재 md5 | `0eaa8b73a1a4ef38a48e9809a52d5bd8` (코드 기준 `3fc9c6e`, 문서 병합 후 main `6d933ae`) |
| `<script>` | JS 249개 + importmap 1개. `node --check` 0 실패 |
| 스킬 라이브러리 | `GA_SKILL_LIB` 425개(동결), 평점 3 이상 243개. 원본 CSV `gs-skill-lib_v7_261003-0344.csv` |
| 전투 코어 | `GA_SIM` (60 Hz 결정적 시뮬레이션). `GA_DATA`(영웅 4·적 6·보스 1·웨이브 6) |
| 대상 기기 | PC 브라우저 + Galaxy S25+ (터치) |
| 수정 금지 | `GS_Action_v35_261005-2000.html` (PR #3 최종본, md5 `f7d2ab88…`) |

## 2. 목표

1. **게임 뼈대**: 1판짜리 웨이브 게임 → 로그라이트 런(3지역 × 6층 지도, 노드 보상, 상점·이벤트·휴식, 계정 해금). 설계 S1~S8.
2. **VFX 품질**: 평점 3 이상 243개 효과가 위치·크기·방향이 맞게 나오고, 효과·피해·상태이상이 이름/시각과 일치.
3. **성능**: 실제 GPU에서 끊김(100ms 초과 프레임) 원인 파악·감소. SwiftShader 수치는 GPU 성능 아님.
4. **HUD/SFX**: 모바일 가독성, 효과음 음량 균일화(완료), 실기기 확인.

## 3. 현재 상태 요약

| 영역 | 상태 |
|---|---|
| 병합 | 코드 PR #20~#30 **전부 main 병합**. 문서 PR #31(세션 정리)도 **병합됨** (`6d933ae`, 2026-10-08) |
| 런 뼈대 | S1·S2·S3·S4·S5·S7 완료. **S6·S8 남음** |
| VFX 위치 | 자기형(실드·비상 날개) 추적, 지면 균열 바닥 고정, Lab 빔 길이 = 사거리 (#26). 243개 전수 점검 **미완** |
| 스킬 상태이상 | 주제 기반 21개 추가 (#21). 밸런스 체감 UNVERIFIED |
| SFX | 음량 정규화(#17) + 겹침 규칙(#20). 청감 UNVERIFIED |
| 테스트 | 43개 (브라우저 29 + Node만 14). 워크플로가 개수까지 검사(43) |
| 실기기·GPU | 대부분 UNVERIFIED (§6) |

## 4. 작업 경과 (이번 세션, 2026-10-06 ~ 10-08)

| 순서 | PR | 내용 | 병합 커밋 |
|---|---|---|---|
| 1 | #19 docs | STATUS 정정, 랩·HUD 증거 이관, 현황 보고서 | `b995c2a` |
| 2 | #20 | SFX 겹침 규칙 (큰 효과 뒤 조용한 효과 과감쇠 수정, 거절 시전 무시) | `7bcf549` |
| 3 | #21 | 평점 3 이상 21개 스킬 주제 상태이상 (`window.GA_SKILL_THEME`) | `a64f39f` |
| 4 | #24 | S1 런·계정 저장 (`GA_RUN`, 키 `gs-run-1`·`gs-meta-1`) | `68422bc` |
| 5 | #22 docs | 평점 3 이상 243개 점검표 | `9b41e92` |
| 6 | #23 docs | 로그라이트 런 설계 (S1~S8) | `22881a6` |
| 7 | #25 | S2 노드 전투 실행기 (전투 1개 = `GA_SIM` 1회, 체력 이월, 지역 배율) | `8a362f9` |
| 8 | #26 | VFX 위치 (추적·지면·Lab 빔 길이) | `553d6ae` |
| 9 | #27 | S3 지도 생성 + 지도 화면 + 게임 화면 런 전투 | `ea16598` |
| 10 | #28 | S4 노드 보상 (골드·스킬 드래프트·패시브 12종), 일반 드래프트 평점 필터 버그 수정 | `60b3b8a` |
| 11 | #29 | S5 상점·이벤트 5종·휴식 | `7cbf508` |
| 12 | #30 | S7 조각·해금(영웅 2·특성 3)·난이도 단계·최고 기록 | `3fc9c6e` |
| 13 | #31 docs | STATUS·CLAUDE.md 갱신, 세션 정리 문서 | `6d933ae` |

### 고친 버그

| 버그 | 수정 |
|---|---|
| SFX: 큰 효과 직후 조용한 효과가 -12 dB 보정을 같이 받음 | #20 |
| SFX: 거절된(busy) 시전이 공통 보정을 바꿈 (Codex 리뷰 지적) | #20 |
| 비상 날개·실드가 시전 자리에 남음 | #26 |
| 자광 단층·지열 균열이 손 높이 허공에 그려짐 | #26 |
| Lab 빔 길이 12 고정 vs 게임 55~80 → 모양 차이 | #26 |
| 일반 드래프트가 평점 3 미만·미평가 182개 제시 | #28 |
| `validNode`/`validMap` data 인자 없으면 예외 | #27 |
| Lab에서 런 시작 시 지도 안 보임 (`#ga`는 `body.ga-on`에서만 표시) | #27 (`runEnterView()`) |

## 5. 코드 지도 (main `3fc9c6e`, `index.html` 줄 번호는 근사)

| 기능 | 위치 |
|---|---|
| SFX 음량 정규화·겹침 규칙 | `<script id="gsSfxLevel">` 57줄, `note()` |
| D: storm 분절 인스턴싱 (프레임당 할당 남음) | `syncStormBatches` 1367줄 |
| 경기장 충돌 기둥 | `setSolids` 13047줄 |
| 지면/추적 효과 목록 | `window.__FX_GROUND`, `window.__FX_FOLLOW` 13429줄 |
| 주제 상태이상 표 | `window.GA_SKILL_THEME` 13458줄 |
| 런·계정 상태 전부 | `<script id="gaRunState">` 13487줄~ (`GA_RUN`) |
| └ 설정값 | `CONFIG` 13491줄 (acts 3, floors 6, startHeroes bolt/rain, deathShardKeep 0.5, actScale hp [1,1.6,2.4] dmg [1,1.3,1.6], difficultyStep 0.15) |
| └ S2 전투 | `encounterData`, `enemyScale`, `startEncounter`, `finishEncounter` |
| └ S3 지도 | `generateMap`, `WAVE_TABLE`, `availableNodes`, `advance`, `visitNode` |
| └ S4 보상 | `RUN_SLOTS`, `PASSIVES`(12), `GOLD`, `makeReward`, `takeReward` |
| └ S5 정지점 | `EVENTS`(5), `makeStop`, `chooseStop`, `applyFx` |
| └ S7 계정 | `UNLOCKS`, `shardsFor`, `settleRun` 13673줄, `unlock`, `applyTraits` |
| 효과 배치 | `poseFor`, `castVfx` 14027줄 부근, `followFx` 14077줄 |
| Lab 빔 길이 | `labBeamHalf` 14327줄 |
| 일반 드래프트 | `draftOffers` 14459줄 |
| 런 뷰 | `curWaves` 14840줄, `runStart` 14845줄, `openUnlocks` 14887줄, `runBattleEnd` 14908줄. API `GS_ACTION.run` |
| 메뉴·결과 DOM | `#gaMenu`(12958줄, 제목 `GS ACTION · v34`), `#gaResult`(`#gaRetry` "다시 시작") |

### 테스트

| 파일 | 개수 | 실행 |
|---|---|---|
| `tests/test_cloud_workflows.py`, `tests/test_performance_measurement.py` | 25 | GitHub Actions (브라우저) |
| `tests/test_vfx_anchoring.py` | 1 | Actions |
| `tests/test_run_state.py` (Node만, `<script>` 추출) | 14 | 로컬·Actions |
| `tests/test_run_ui.py` (런 흐름·상점·해금) | 3 | Actions |

- 클라우드 세션은 `cdn.jsdelivr.net` 차단 → 브라우저 테스트는 **CI에서만**. 로컬은 Node 테스트 + `node --check`.
- 테스트를 추가하면 `.github/workflows/tests.yml`의 개수(현재 43)도 같이 바꾼다. 병렬 PR이면 병합 순서대로 합산.

## 6. 문제점·위험·UNVERIFIED

| # | 항목 | 상태 | 확인 방법 |
|---|---|---|---|
| P1 | 런 모드 실제 체감·난이도 (자동 테스트는 무적 영웅) | UNVERIFIED | 실기기 1~2회 완주 |
| P2 | 신규 수치 전부 초안 (골드, 상점 가격 45~60/50/30, 조각 공식, 해금 비용 40~100, 난이도 +15%/단계) | UNVERIFIED | 플레이 후 조정 |
| P3 | 새 화면(지도·보상·상점·해금) 모바일 모양 | UNVERIFIED | 실기기 / probe 캡처 |
| P4 | 런 종료 후 결과 화면 "다시 시작"(`#gaRetry`)이 런이 아닌 일반 6웨이브로 감 | 알려진 결함 | S8에서 수정 |
| P5 | 지역 차이 없음: 3지역 모두 같은 경기장·같은 보스 계열 | 미구현 | S6 |
| P6 | VFX 위치 243개 전수 점검 미완. 1차 캡처 추정 후보: ARC-07·ARC-08(하늘 쪽), AC-02(머리 위 대형) | 추정 | probe v2 판정 (§7-1) |
| P7 | 비상 날개가 "등에 붙은" 느낌인지, 균열 모양, Lab 빔 55가 화면에 들어오는지 | UNVERIFIED | 화면 확인 |
| P8 | D(storm) 프레임당 할당(`barriers`, `Map`, `filter/map/sort`)과 `geometry/material.clone()` 해제 누락 가능성 | 코드 판독 추정 | 수정 PR + 메모리 측정 |
| P9 | 실제 GPU 꼬리 지연 (600초 100ms 초과 39회, 최대 636ms). 원인 미상 | 측정 1대 1회 | 사용자 PC 재측정 |
| P10 | SFX 겹침 청감, Galaxy S25+ 소리·터치·발열 | UNVERIFIED | 사용자 직접 |
| P11 | 메뉴 제목이 아직 `GS ACTION · v34` | 미착수 | 문자열 1곳 |
| P12 | 오래된 열린 PR #3(분할 전 원본, 중복), #1(v14) / probe·병합된 헤드 브랜치 다수 | 사용자 결정 | 닫기·삭제 여부 질문 |
| P13 | Codex 리뷰 봇은 사용량 한도 도달 상태 (리뷰 안 달림) | 참고 | — |

## 7. 계획 (권장 순서, 단계별 완료 기준)

### 7-0. 시작 정리
- PR #31은 병합 완료(`6d933ae`). 확인 불필요.
- md5 확인. `python3 -m unittest tests.test_run_state -v`로 Node 테스트 14개 로컬 통과 확인.

### 7-1. VFX 위치 점검 마무리 (P6, P7)
- 자료: 브랜치 `claude/probe-vfx-anchor` (PR·병합 대상 아님). probe v2 실행 run `37485389695` **성공**, 커밋 `ac45664`에 `vfx-captures/` 이미지 498장 + `results.json` + `capture.log`(pageerrors 0). **아직 판정 안 함.**
  - A: Lab 캡처, B: 수정 확인용(wings/shield/violet/fissure), C: 평점 3 이상 243개 측면·상단 시점(`C <번호> <id>`).
- 할 일: 이미지 판정 → 하늘/허공/과대/방향 오류 목록(`docs/evidence/gs-vfx-anchor-audit_v1_*.md`, docs PR) → `__FX_GROUND`/`__FX_FOLLOW`/`poseFor` 보정 코드 PR.
- 완료 기준: 판정표 243행, 오류 효과 수정 후 재캡처 비교, `test_vfx_anchoring.py` 대상 추가.

### 7-2. S6 지역 구성 (P5)
- 설계 §7: 지역1 해안 폐허(기둥 8개 현행), 지역2 저주받은 숲(역귀·술사·잡귀, 기둥 배치 변경), 지역3 심연(전 종류 혼합 + 엘리트, 기둥 축소).
- 지역 보스: 1 = 엘리트 잡귀 강화형(체력 ×3, 보스 페이즈 차용), 2 = 술사 강화형(`GA_ENEMY_LIB.mage` 다중 시전), 3 = 두억시니(현 보스).
- 구현 포인트: `encounterData`에 act별 경기장(`setSolids` 행)·보스 정의 주입. `GA_SIM` 내부 규칙은 바꾸지 않는다(결정성 유지).
- 완료 기준: 3지역 자동 완주 테스트, 지역별 기둥 수 다름, 같은 시드 2회 동일 결과.

### 7-3. S8 타이틀·결과·튜토리얼 (P4, P11)
- 타이틀 화면(시작·이어하기·해금·설정) 정리, 런 결과 화면 전용화(도달 지역·처치·조각·해금 가능 표시).
- `#gaRetry`가 런 종료 후엔 새 런(또는 지도)으로 가도록 분기.
- 튜토리얼 런: 지역 1 축소판(노드 3개), 첫 실행 자동 안내.
- 메뉴 제목 `v34` 갱신.
- 완료 기준: 첫 실행 → 런 완주/사망 → 결과 → 해금 → 새 런까지 막힘 없음(브라우저 테스트).

### 7-4. 성능 (P8, P9)
- D 프레임당 할당 제거, clone 해제 (`syncStormBatches` 부근). 코드 PR.
- 사용자 PC에서 main v34(`76ddfb4`) vs 현재 main 3회씩 측정 → `docs/evidence/`에 JSON 저장. 사용자 작업 필요.

### 7-5. 밸런스·실기기 (P1~P3, P10)
- 사용자가 실기기로 런 1~2회 플레이 → 수치 조정 PR. 그 전까지 수치 변경 금지.

### 7-6. 정리 (P12)
- PR #3·#1 닫기, probe 브랜치 삭제는 사용자 결정. 묻고 진행.

## 8. 규칙 (요약, 원문은 `CLAUDE.md`)

- `index.html` 수정 전 md5 기록, 수정 후 md5 출력. 기대값과 다르면 중단·보고. 강제 패치 금지.
- 두 실행본 byte 동일 (`cmp`).
- 큰 블록 교체 전 `.bak`. 앵커 기준 최소 줄 변경. 셰이더·uniform·config 블록 전체 교체 금지.
- 새 mesh/material/RT는 해제 확인, 프레임 루프 안 new/할당 0.
- 코드 PR ↔ docs PR 분리. 병합은 사용자 지시 시만. main 직접 push 금지.
- 화면 확인은 `claude/probe-*` 별도 브랜치에 캡처 워크플로를 얹어 실행. main에 넣지 않음.
- 셰이더 컴파일·WebGL·실기기·GPU 성능은 로컬에서 확인 불가 → UNVERIFIED.
- 파일명 `{slug}_v{N}_{YYMMDD-HHMM}.ext`(KST). 덮어쓰기·삭제 금지, 폐기본은 `_deprecated/`.

## 9. 알려진 함정 (이번 세션 경험)

- GitHub MCP 병합은 40자 전체 SHA 필요 (`git rev-parse`).
- Lab 스크립트의 `labPlay`는 모듈 스코프 → 외부에서는 `GS_STUDIO.select(id,{play:true})`.
- 브라우저 테스트에서 `sim.cast`로 실드 시전 시 타임아웃 → `GS_ACTION.fx({caster:'test'})` 사용.
- 런 화면은 게임 모드(`body.ga-on`)에서만 보임 → Lab에서 진입 시 `runEnterView()` 필요.
- 병렬 PR이 각각 테스트 개수를 바꾸면 병합 때 `tests.yml` 개수 충돌 → main 병합 후 합산값으로.
- 스택형 PR(base가 다른 PR 브랜치)은 앞 PR 병합 후 base를 main으로 바꾸고 병합.
