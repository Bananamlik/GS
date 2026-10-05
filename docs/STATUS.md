# STATUS

갱신: 2026-10-06 KST. 근거: `docs/evidence/`. 검증하지 못한 항목은 UNVERIFIED.

## 1. 코드 상태

| 항목 | 값 |
|---|---|
| main | `d4af9c4` = v34(`76ddfb47a0adb04bc614b5812dce72db1ab9a043`, PR #2 병합) + `GS_Action_v35_261005-2000.html` 업로드 한 커밋. `index.html`은 v34 그대로(md5 `d8cb70f2d1876a0386740b73b2d6ecb9`). |
| v35 파일 | `GS_Action_v35_261005-2000.html`. md5 `f7d2ab883d7bc78fc05d9b046e45bf47` = PR #3 `index.html` = PR #7(D) `index.html`. diff 0줄 확인. 파일 안의 이름은 아직 `GS_Action v34`, buildId `v34-runtime-8`. |
| PR #3 `codex/cloud-runtime-hardening` | `953dd120d4d5cc7172e20a845249ebeb1431048d`. 병합 안 됨. 분할 원본. |
| 실행본 | `index.html` = `GS_Action_v34_runtime.html` (항상 동일해야 함) |

### 분할 PR (draft, 쌓인 구조, 병합 안 됨)

| 단계 | PR | base | 내용 | `index.html` md5 |
|---|---|---|---|---|
| A | [#5](https://github.com/Bananamlik/GS/pull/5) | `main` | 경과 시간 pacing, 출력 패스 생략, 렌더 크기 중복 설정 생략, 모듈 준비 취소 | `f0b0d3491881b4c714f2a8b3d0f77642` |
| BC | [#6](https://github.com/Bananamlik/GS/pull/6) | `claude/split-a-runtime` | 벤치 보정·추적, 4개씩 예열 큐, 실행 준비, context 손실 복구 | `01c26f278a86e646f7cb2c6b9348e3cb` |
| D | [#7](https://github.com/Bananamlik/GS/pull/7) | `claude/split-bc-warmup` | CH:storm 분절 인스턴싱, 투명도 0 표면 생략 | `f7d2ab883d7bc78fc05d9b046e45bf47` (= PR #3) |

B와 C는 같은 함수를 함께 다뤄 한 PR로 묶음.

| 부가 | PR | 내용 |
|---|---|---|
| 문서 | [#8](https://github.com/Bananamlik/GS/pull/8) | 이 문서, `CLAUDE.md`, `docs/evidence/` (docs-only, base `main`) |
| CI | [#9](https://github.com/Bananamlik/GS/pull/9) | PR #3의 `tests/`·`scripts/` + GitHub Actions (base: #7 브랜치) |
| 닫음 | [#4](https://github.com/Bananamlik/GS/pull/4) | 권한 확인용. 닫힘. |

probe 브랜치 `claude/ci-probe-a`, `claude/ci-probe-bc`는 단계별 테스트 결과 수집용이며 PR·병합 대상이 아님. 필요 없으면 삭제해도 됨.

## 2. 검증 상태

| 항목 | 결과 | 환경 |
|---|---|---|
| 패치 적용 후 md5 (A, BC, D) | 기대값과 일치 | 클라우드 세션 |
| `cmp index.html GS_Action_v34_runtime.html` | 3단계 모두 동일 | 클라우드 세션 |
| `node --check` `<script>` 247개 (importmap JSON 제외) | 3단계 모두 0 실패 | 클라우드 세션 |
| PR #3 node 전용 `SourceTests` 3개 | 3단계 모두 통과 | 클라우드 세션 |
| 브라우저 테스트 25개, 클라우드 세션 | **UNVERIFIED** (`cdn.jsdelivr.net` 차단, playwright 미설치). 대신 GitHub Actions 결과 아래 행 참고. | 클라우드 세션 |
| 브라우저 테스트 25개, GitHub Actions | D(= PR #3 코드) **25/25 통과**. BC 24/25(실패 1: D 기능 테스트, 예상). A 11/25(실패 14: BC·D 기능을 요구, 예상). 각 1회. | GitHub 러너, SwiftShader. `docs/evidence/gs-ci-results_v1_261005-2359.md` |
| 브라우저 테스트 25개, 다른 환경(SwiftShader) | PR #3 24/25, A 단독 11/14 실패, BC 24/25. 위 GitHub Actions 결과와 A·BC는 일치. | `gs-split-verification_v2` 기준. |
| 실제 GPU / Galaxy S25+ / 소리 / 발열 | 아래 §3 외 **UNVERIFIED** | |

## 3. 실제 GPU 측정 (사용자 PC 1대)

AMD Radeon 내장, ANGLE/D3D11, Chrome 154, 1920×922, 품질 auto, 설정 60 → pacing 목표 72.5 FPS (145Hz ÷ 2).

| 항목 | 60초 #1 | 60초 #2 | 600초 |
|---|---|---|---|
| 평균 FPS | 65.9 | 66.0 | 63.7 |
| p95 / p99 (ms) | 21 / 27.9 | 21 / 28 | 22.3 / 41.5 |
| 최대 (ms) | 565.4 | 182.8 | 636.7 |
| 100ms 초과 | 5 | 4 | 39 |
| 최대 draw call | 292 | 281 | 439 |

- 평균은 설정 60 초과. 내부 예산(72.5 기준)은 평균·p95·최대에서 미달.
- 문제는 꼬리 지연(100ms 초과 끊김). 원인 미확인.
- 열 저하는 이 측정에서 안 보임(추정, 1회).
- 빌드는 PR #3 계열(v35)로 보이나 측정에 쓴 파일의 해시는 미확인. repo의 v35 파일은 PR #3와 byte 동일. main v34와 비교 측정 없음 → BC 병합 이득 판단 불가.
- draw call이 병목으로 안 보여 D 우선순위 낮음(추정, 직접 증명 아님).

## 4. 병합 권장 (병합은 사용자 결정)

- **A**: 동작 보존형. 브라우저 회귀 확인 후 병합 가능. 실제 GPU 확인은 없음.
- **BC**: 실제 GPU에서 시작 준비 시간·첫 사용 끊김을 변경 전/후 3회씩 측정한 뒤. 같은 PC에서 main v34 3회 비교 필요.
- **D**: 실제 GPU에서 프레임 시간 개선이 확인될 때만. 병합 전 프레임당 할당 제거(`barriers`, `{z,order,group}`, `Map`, `filter/map/sort`, 임시 배열).

## 5. 결정 대기

1. 예산 기준: 설정 60 vs pacing 목표 72.5. 현재 72.5.
2. 밸런스 승인: 설치물 46종만 승인, 나머지 379종은 제안값(`gs-cloud-handoff`).

## 6. 남은 작업

1. 같은 PC·같은 조건으로 main v34 3회 측정.
2. PR #3 계열 60초 측정 후 결과 JSON(`phaseTotals`, `phaseSpans`, `longTasks`)을 `docs/evidence/`에 저장. 끊김 원인 좁히기.
3. 품질 `낮음` 1회 측정(GPU 병목 vs CPU 병목 구분).
4. CI: [#9](https://github.com/Bananamlik/GS/pull/9)에서 25/25 통과 확인. 병합 여부는 사용자 결정. #9는 #7 위에 쌓여 있어 #5~#7이 먼저 병합되어야 base가 정리됨.
5. Galaxy S25+ 화면·소리·터치·발열 (사용자 직접).
6. 장시간·메모리·복구 재검증 (GPU 환경).

## 7. 병합 권장 순서 (병합은 사용자 결정, 현재 모두 미병합)

현재 `main`(`d4af9c4`) 대비 #5, #6, #7, #8, #9 브랜치 모두 충돌 없음(`git merge-tree` 확인).

1. [#8](https://github.com/Bananamlik/GS/pull/8) 문서.
2. [#5](https://github.com/Bananamlik/GS/pull/5) A. 이후 [#6](https://github.com/Bananamlik/GS/pull/6)의 base를 `main`으로 갱신.
3. [#9](https://github.com/Bananamlik/GS/pull/9) CI. 병합 전에 base를 정리해야 함(#9는 #7 위에 쌓여 있어 #7 변경이 함께 들어옴). 따로 병합하려면 #9에서 `tests/`, `scripts/`, `.github/`만 남기는 정리 필요.
4. #6 BC: 같은 PC에서 main v34와 비교 측정 후.
5. #7 D: 실제 GPU에서 프레임 시간 개선이 확인될 때만.

v35 파일은 이미 `main`에 있고 D 단계와 byte 동일하므로, BC·D를 병합하지 않으면 `main`에는 v35 파일만 있고 `index.html`은 v34인 상태가 됨.
