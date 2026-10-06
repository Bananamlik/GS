# GS Action 전체 현황 분석 보고서

작성: 2026-10-06 20:15 KST · 범위: 읽기·분석만 (코드·브랜치·PR 변경 없음) · 기준: `origin/main` `9c0f648`
표기: **[사실]** 파일·명령으로 확인 / **[추정]** 확인 못 함 / **UNVERIFIED** 검증 안 됨. SwiftShader 수치는 GPU 성능이 아님.

---

## 1. 현재 상태

### 1.1 main 코드 (이 세션에서 직접 확인)

| 항목 | 값 | 출처 |
|---|---|---|
| main HEAD | `9c0f648` (PR #18 병합) | `git log origin/main` |
| `index.html` md5 | `8558fefd4fe5ee410fed3f4a8e1be54f` | `md5sum` |
| `GS_Action_v34_runtime.html` | 동일 (`cmp` 통과) | `cmp` |
| `GS_Action_v35_261005-2000.html` | `f7d2ab88…` = PR #3 최종본 | `md5sum`, `gs-split-verification_v2` |
| 크기 | 62,473줄, 5.47MB, 최대 script 블록 1,336KB | 파이썬 집계 |
| `<script>` | 249개 = JS 248 + importmap 1. `node --check` 248개 0 실패, importmap `json.loads` 통과 | 이 세션 실행 |
| CI on 현재 코드 | run 17(`a7df8f0`, #17 코드 포함, `workflow_dispatch`) success, run 18(#18 헤드) success. `9c0f648`은 docs만 추가 → 코드 동일 | GitHub Actions 목록 |
| 브라우저 테스트(로컬) | UNVERIFIED (이 세션에서 실행 안 함) | — |

### 1.2 병합된 작업

| PR | 분류 | 내용 | 병합 |
|---|---|---|---|
| #2 | 코드 | v34 통합 | `76ddfb4` |
| #5 A / #6 BC / #7 D | 코드 | PR #3 분할: pacing·출력 패스 생략 / 예열 큐·벤치·복구 / storm 인스턴싱 | `23b0b01` / `744f093` / `74b7b6a` |
| #8, #12, #16, #18 | docs | STATUS·증거·md5 갱신, SFX 재측정 | — |
| #9 | CI | `tests/` 25개 + `tests.yml` | `b07b275` |
| #10, #11, #13 | 코드 | HUD A+B, C+D, 위계 | `38aed51`, `a503a7e`, `4729a7d` |
| #14 | docs | SFX 측정·보정안 | `7d22d4c` |
| #15 | 코드 | 랩 모바일 | `a8df602` |
| #17 | 코드 | SFX 정규화 | `b43914e` |

참고: GitHub API는 `merged:false`로 응답하나 `merged_at`이 있고 main에 merge commit이 있으므로 병합으로 판단 **[사실]**.

### 1.3 열린 PR

| PR | 상태 | 판단 |
|---|---|---|
| **#18** | **이미 병합됨** (2026-10-06 10:43Z, `9c0f648`). 요청서의 "열린 PR"과 다름 | 조치 없음 |
| #3 | draft, open. 내용은 A+BC+D로 main에 반영 | 닫기 후보. 사용자 결정 (`STATUS §5-3`) |
| #1 | open. v14 결함 5건 수정, 현행과 별개 계통 | 닫기 또는 보존 결정 필요. 현 main 반영 여부 **[추정: 미반영]** |

### 1.4 정리할 브랜치 (원격 41개 중 main 제외 40개)

| 종류 | 브랜치 | 개수 | 판단 |
|---|---|---|---|
| 결과 수집용 probe | `ci-probe-a/-bc`, `probe-chip`, `probe-hud-capture{,-after,-cd,-cd2}`, `probe-hud-hier`, `probe-lab-before/-after`, `probe-sfx/-after` | 12 | 삭제 가능. 단 캡처·`metrics.json`·SFX shard 로그가 이 브랜치에만 있음 → 필요분을 먼저 `docs/evidence/`로 옮길지 결정 |
| 병합 끝난 PR 헤드 | `split-a/-bc/-d`, `ci-tests`, `hud-a-b/-c-d`, `hud-hierarchy`, `lab-mobile`, `sfx-normalize`, `docs-status-evidence/-after-merge/-md5-update/-sfx-loudness/-sfx-after`, `access-check`(#4 닫힘) | 15 | 삭제 가능 |
| Codex 이력 | `codex/gs-v25 … v34-*`(10), `codex/cloud-runtime-hardening`(#3) | 11 | v34는 #2로 병합. v25~v33은 상위 버전에 흡수 **[추정]**. #3 닫은 뒤 삭제 |
| v14 | `fix/v14-adversarial-review`(#1) | 1 | #1 결정 따름 |

STATUS의 probe 목록은 7개만 기재 → 5개(`probe-hud-hier`, `probe-lab-*`, `probe-sfx*`) 누락.

### 1.5 문서 불일치 (docs-only 수정 대상)

| 위치 | 현재 기재 | 실제 |
|---|---|---|
| `STATUS.md §1` main | `b43914e` | `9c0f648` (코드 md5는 동일) |
| `STATUS.md §2` script 수 | 247 | JS 248 (+importmap 1). CLAUDE.md의 248과 일치 |
| `STATUS.md` 병합 표 | #16, #18, #2 없음 | 추가 필요 |
| `STATUS.md` probe 목록 | 7개 | 12개 |
| 메뉴 제목 | `GS ACTION · v34` (2곳) | 빌드는 v35+ (`STATUS §6-4`에 이미 기재) |

---

## 2. 목표와 달성도

### (a) 성능·끊김 개선 — **달성도: 낮음 (근거 부족)**

| 하위 목표 | 근거 | 수치 (출처) | 판단 |
|---|---|---|---|
| A 동작 보존 수정 | CI 11/25(예상 실패), D 단계 25/25 | `gs-ci-results_v1` | 회귀 없음 확인. 성능 이득 측정 없음 |
| BC 시작 준비 단축 | SwiftShader만 | 준비 9.68s → 7.31s (`gs-evidence-runtime8`) | SwiftShader 수치. GPU 근거 없음 |
| BC 첫 사용 끊김 | **근거 없음** | — | 병합 게이트(GPU 전/후 3회) 미이행 (`gs-pr3-split-plan`) |
| D draw call 감소 | SwiftShader만 | 최대 496 → 222 (`gs-cloud-handoff §3-5`) | GPU 프레임 시간 개선 **근거 없음** |
| 실제 GPU 프레임 | 사용자 PC 1대, v35 추정 빌드 | 평균 65.9/66.0/63.7 FPS, p95 21/21/22.3ms, 100ms 초과 5/4/39회, 최대 565/183/637ms (`gs-gpu-measurement_v1`) | 설정 60 대비 평균 달성. 72.5 기준 미달. 꼬리 지연 원인 미확인 |
| v34 대비 개선 | **근거 없음** | main v34 비교 측정 0회 | 판단 불가 |
| 현재 main GPU 측정 | **근거 없음** | HUD·SFX 변경 후 0회 | 판단 불가 |

### (b) 모바일 HUD·랩 사용성 — **달성도: 화면상 달성, 실기기 UNVERIFIED**

| PR | 근거 | 수치·관찰 (출처) | 판단 |
|---|---|---|---|
| #10, #11 | 3화면×10장면 캡처 육안 확인, CI 25/25 | 위협 알약 겹침 해소, 쿨다운 숫자, 저체력 맥동 등 (`gs-ci-results_v2`) | SwiftShader·배율 1배 화면 확인. 정량 지표 없음 |
| #13 | probe `probe-hud-hier` 캡처(md5 `690f2f57…` = #13 헤드), CI 25/25 | 증거 문서 없음. STATUS 서술만 | `docs/evidence/`에 근거 파일 **없음** |
| #15 | `probe-lab-before/-after` `metrics.json` | `viewVisiblePct` 미리보기 중: 412×676 21→46, 360×640 17→50, 915×360 12→33, 1280×720 53→53. 시트 tall 상태 13% (설계상) | 개선 확인. 단 after 측정 빌드 md5 `e1270f43…` ≠ #15 최종 헤드 `25c3eba6…`(`e491d02`, 핸들 글자 가운데 정렬 1커밋 전) **[사실]**. 최종본 재측정 없음 |
| `명중` 칩 겹침 | 6회 반복 | 지속 결함 재현 안 됨 (`gs-ci-results_v2`) | 원인 추정(페이드 중) |
| 터치 느낌·시트 핸들 조작 | **근거 없음** | — | UNVERIFIED |
| 회귀 테스트 | `tests/`에 HUD·랩 모바일·SFX 전용 테스트 없음 (#9 이후 `tests/` 변경 0) | — | 회귀 보호 없음 |

### (c) SFX 음량 편차 보정 — **달성도: Lab 단일 재생 기준 달성, 실전 UNVERIFIED**

| 지표 | 전 | 후 | 출처 |
|---|---|---|---|
| 순간 음량 p5~p95 폭 | 26.3 dB (이전 문서 26.1) | **9.0 dB** (시뮬레이션 예상 6.1) | `gs-sfx-loudness-after_v1` |
| 최대 피크 | +0.4 dBFS | -0.6 dBFS | 동 |
| 피크 -1 dBFS 초과 | 9개 | 8개 | 동 |
| 중앙값 ±6 dB 안 | 282/499 | 462/500 | 동 |
| 묶음 내 폭 잔존 | — | `D:ULT:` 25.8, 그 외 30.6, `D:PROJ:` 18.7, `GS-` 18.2 dB | 동 |
| 측정 실패 효과 | 2개 | 1개(`C:F_PROJ:nbl`) | 동 |
| 청감·겹침 재생·슬라이더 | **근거 없음** | — | UNVERIFIED |

측정은 가중치 없는 400ms RMS, LUFS 아님, SwiftShader 러너, 효과당 1회.

---

## 3. UNVERIFIED 항목

| # | 항목 | 검증 방법 | 담당 |
|---|---|---|---|
| U1 | 현재 main 실제 GPU 프레임 시간 | 게임 내 `성능 측정` 60초×3, 결과 텍스트+JSON 저장, `GPU:` 줄 확인 | 사용자 실기기(PC) |
| U2 | v34(`76ddfb4`) 대비 BC·D 이득 | 같은 PC·조건으로 v34/현재 각 3회, 시작 준비·p95·100ms 초과 비교 | 사용자 실기기 |
| U3 | 끊김(100ms 초과) 원인 | 60초 JSON의 `phaseTotals`·`phaseSpans`·`longTasks` 분석, 품질 `낮음` 1회 | 사용자 측정 → 분석은 세션 |
| U4 | GPU 측정 빌드 해시 | 측정 시 파일 md5 기록 | 사용자 |
| U5 | Galaxy S25+ 화면·터치·발열·소리 | 실기기 플레이 10분, 체크리스트 | 사용자 실기기 |
| U6 | HUD 터치 느낌, 랩 시트 핸들(peek/tall) 조작 | 실기기 조작 | 사용자 실기기 |
| U7 | #15 최종 헤드 랩 면적 | `probe-lab-after` 워크플로를 현재 main에 재실행 | GitHub Actions |
| U8 | #13 HUD 위계 증거 문서화 | `probe-hud-hier` 결과를 evidence로 기록 | GitHub Actions(완료분) + docs |
| U9 | SFX 겹침 재생 음량·trim 상호작용 | 전투 시나리오 2~3개 동시 시전, 측정기로 효과별 출력 기록 | GitHub Actions (오디오 탭) |
| U10 | SFX 청감·스피커/이어폰 | 실청취, 조용한 12개·큰 12개 목록 확인 | 사용자 실기기 |
| U11 | 셰이더 컴파일·WebGL 실행 (클라우드 세션) | 불가 (`cdn.jsdelivr.net` 차단) → Actions로 대체 | 세션 불가 / Actions |
| U12 | 장시간(10분)·메모리·context 복구 (현재 main) | GPU 환경 10분×3, 힙·지오메트리 회수 | 사용자 실기기 |
| U13 | storm 배치 GPU 자원 회수 | 반복 시전 후 `renderer.info.memory` 추이 | GitHub Actions(SwiftShader로 개수만) |
| U14 | 열 저하 없음 (1회 관측) | 600초 측정 반복 | 사용자 실기기 |

---

## 4. 리스크

| # | 리스크 | 근거 | 심각도 | 비고 |
|---|---|---|---|---|
| R1 | BC·D 근거 없이 병합 | 병합 게이트(GPU 전/후 3회) 미이행. `STATUS §4` 명시 | 높음 | 되돌리기 커밋 `744f093`, `74b7b6a`. 이후 HUD·SFX가 위에 쌓여 revert 충돌 가능성 증가 **[추정]** |
| R2 | 실제 GPU 측정 1대·1회 계열, 빌드 해시 미확인, 현재 main 미측정 | `gs-gpu-measurement_v1 §4` | 높음 | 모든 성능 판단의 기준선 부재 |
| R3 | D 프레임당 할당 | `index.html:1366-1407` `syncStormBatches`: 매 프레임 `barriers=[]`, `{z,order,group}`, `mats` 배열, `some`, `filter/map/sort`, `new Map`, 세그먼트 배열, `[[attr,count]…]` 리터럴, `composer.render(...args)` | 중간 | 프레임 루프 할당 0 규칙 위반 **[사실]**. 모바일 GC 끊김 기여 여부 **[추정]** |
| R4 | D 자원 해제 누락 가능성 | `dispose()`가 `b.mesh.dispose()`만 호출. `geometry.clone()`·`material.clone()` 해제 코드 안 보임 (`index.html:1381-1408`) | 중간 | 반복 시전 시 GPU 메모리 누수 가능 **[추정, 런타임 미확인]** |
| R5 | **SFX trim이 효과별이 아니라 AudioContext 전체에 걸림** | `index.html:62-98`: `note(id)`가 최근 2.5초 효과 중 **최소** trim을 `trimDb`로 잡아 컨텍스트 공통 `trim` 노드에 적용 | 높음 | 겹침 시: 큰 효과(-10 dB)가 조용한 효과(+12 dB)와 2.5초 내 겹치면 둘 다 -10 dB → 조용한 효과가 더 묻힘. 단독 +12 dB 효과 재생 중 잔향·다른 소리도 같이 +12 dB. 게인 전환(20ms) 펌핑. Lab 측정은 단일 재생이라 이 동작이 드러나지 않음 **[코드 판독 사실, 청감 영향 추정]** |
| R6 | SFX 엔진 다중 압축기 + 공통 리미터 | `DynamicsCompressor` 20곳 이상, 공통 리미터 threshold -4 / ratio 20 | 중간 | 예상 6.1 vs 실측 9.0 dB 차이 원인 미분리. 겹침 시 리미터 상시 동작 → 펌핑 **[추정]** |
| R7 | 단일 62k줄 HTML | 5.47MB, 최대 script 1.34MB, 두 실행본 byte 동일 유지 필요 | 높음 | 리뷰·diff·충돌 비용 큼. 앵커 패치 실수 시 탐지 어려움 |
| R8 | CSS 층층 덧씌움 | v35→main: `<style>` 14→18, `@media` 28→37, `!important` 139→144, CSS 78→84KB. #15 커밋 "override generic panel button style" | 중간 | 뒤 블록이 앞 블록을 덮는 구조. 선택자 우선순위 추적 어려움, 화면 회귀 위험 |
| R9 | HUD·랩·SFX 회귀 테스트 없음 | `tests/`는 #9 이후 변경 0, 25개 모두 PR #3 범위 | 중간 | CI 녹색 ≠ HUD·SFX 정상 |
| R10 | 증거가 probe 브랜치에만 존재 | 랩 `metrics.json`, HUD 캡처, SFX shard 로그 | 낮음 | 브랜치 삭제 시 상실 |
| R11 | 테스트 1회 실행·속도 민감 테스트 | `test_fixed_target_and_real_phase_records` 1회 실패 이력 (`gs-split-verification_v2`) | 낮음 | 플레이크 가능성 |

---

## 5. 다음 작업 제안

### 5.1 코드 변경 PR (각각 별도, main에서 분기, 두 실행본 동시 수정, 25개 테스트 통과)

| 순위 | 작업 | 크기(추정) | 성공 기준 |
|---|---|---|---|
| C1 | **SFX trim을 효과별로** (R5): 효과 출력 앞 개별 GainNode, 컨텍스트 공통 trim 제거. 리미터 유지 | 소~중 (30~60줄) | ① Lab 재측정 p5–p95 ≤ 9.0 dB 유지 ② 겹침 시나리오(큰+조용 동시)에서 조용한 효과 출력이 단독 대비 ±1.5 dB 이내 ③ 최대 피크 ≤ -0.5 dBFS ④ 25/25 |
| C2 | **D 프레임당 할당 제거 + dispose 보강** (R3, R4): `barriers`·cuts·segments 재사용 배열, 객체 풀, geometry/material 해제 | 중 (50~100줄) | ① storm 활성 프레임에서 `syncStormBatches` 신규 할당 0 (코드 판독 + 힙 스냅샷) ② 반복 시전 50회 후 `renderer.info.memory.geometries` 기준선 복귀 ③ 화면 차 ≤ 1/255 ④ 25/25 |
| C3 | 조건부 **BC/D revert 또는 유지** | 소 (revert 커밋) | U2 측정 결과로 결정. 유지 기준: 시작 준비 또는 p95가 v34 대비 개선, 악화 없음 |
| C4 | 메뉴 제목 `v34` 수정 | 극소 | 2곳 갱신, 25/25 |
| C5 | HUD·랩·SFX 회귀 테스트 추가 (tests 변경 → 기대 개수 갱신) | 중 | `viewVisiblePct` 하한, 위협 알약 겹침 0, SFX 슬라이더 저장·피크 상한 자동 검사 |
| C6 | 끊김 원인 수정 | 미정 | U3 결과로 병목 1개 확정 후 착수. GPU에서 100ms 초과 횟수 감소 |
| C7 | CSS 정리 (모바일 덮어쓰기 블록 통합) | 대 | 화면 캡처 전/후 픽셀 동일, `!important` 감소. 측정 기반 확보(C5) 뒤 착수 |

### 5.2 docs-only PR

| 순위 | 작업 | 크기 | 성공 기준 |
|---|---|---|---|
| D1 | STATUS 정정: main `9c0f648`, script 248, #2·#16·#18 병합 표, probe 12개, #18 상태 | 소 | §1.5 표 불일치 0 |
| D2 | #13·#15 증거 문서화: `probe-hud-hier`, `probe-lab-*` `metrics.json` 요약을 `docs/evidence/` 새 파일로 | 소 | 수치 + 빌드 md5 + 측정 빌드≠최종 헤드 명시 |
| D3 | SFX 겹침 리스크(R5)·D 자원 해제(R4)를 STATUS §4에 기록 | 극소 | 코드 위치 줄 번호 포함 |
| D4 | GPU 측정 결과 수집 (사용자 측정 후) | 소 | 결과 텍스트+JSON+빌드 md5, v34·현재 각 3회 |

### 5.3 사용자 결정·작업

| 순위 | 항목 |
|---|---|
| P1 | U1·U2·U3 GPU 측정 (C3·C6의 전제). 빌드 md5 기록 |
| P2 | PR #3 닫기, PR #1 처리, 브랜치 정리(필요 증거 이관 후) |
| P3 | 예산 기준 60 vs 72.5 결정 (`STATUS §5-1`) |
| P4 | S25+ 실기기·청취 확인 (U5, U6, U10) |

권장 순서: D1·D3 → C1 → (P1 측정) → C3 판정 → C2 → C5 → C6 → C7.

---

## 부록: 이 세션 검증 기록

| 검사 | 결과 |
|---|---|
| `cmp index.html GS_Action_v34_runtime.html` | 동일 |
| md5 | `8558fefd4fe5ee410fed3f4a8e1be54f` (양쪽) |
| `node --check` JS 248개 | 0 실패 |
| importmap `json.loads` | 통과 |
| `docs/evidence` md5 | README 기재값과 12개 모두 일치 |
| 브라우저 테스트 25개 | 이 세션 미실행 (CI run 17·18 success로 대체 인용) |
| uniform 삼중 일치·orphan·hot pass | 전체 검사 안 함. `syncStormBatches`만 판독 (R3, R4) |
