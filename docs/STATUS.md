# STATUS

갱신: 2026-10-05 KST. 근거: `docs/evidence/`. 검증하지 못한 항목은 UNVERIFIED.

## 1. 코드 상태

| 항목 | 값 |
|---|---|
| main | `76ddfb47a0adb04bc614b5812dce72db1ab9a043` (v34, PR #2 병합) |
| PR #3 `codex/cloud-runtime-hardening` | `953dd120d4d5cc7172e20a845249ebeb1431048d`. 병합 안 됨. 분할 원본. |
| 실행본 | `index.html` = `GS_Action_v34_runtime.html` (항상 동일해야 함) |

### 분할 PR (draft, 쌓인 구조, 병합 안 됨)

| 단계 | PR | base | 내용 | `index.html` md5 |
|---|---|---|---|---|
| A | [#5](https://github.com/Bananamlik/GS/pull/5) | `main` | 경과 시간 pacing, 출력 패스 생략, 렌더 크기 중복 설정 생략, 모듈 준비 취소 | `f0b0d3491881b4c714f2a8b3d0f77642` |
| BC | [#6](https://github.com/Bananamlik/GS/pull/6) | `claude/split-a-runtime` | 벤치 보정·추적, 4개씩 예열 큐, 실행 준비, context 손실 복구 | `01c26f278a86e646f7cb2c6b9348e3cb` |
| D | [#7](https://github.com/Bananamlik/GS/pull/7) | `claude/split-bc-warmup` | CH:storm 분절 인스턴싱, 투명도 0 표면 생략 | `f7d2ab883d7bc78fc05d9b046e45bf47` (= PR #3) |

B와 C는 같은 함수를 함께 다뤄 한 PR로 묶음.

## 2. 검증 상태

| 항목 | 결과 | 환경 |
|---|---|---|
| 패치 적용 후 md5 (A, BC, D) | 기대값과 일치 | 클라우드 세션 |
| `cmp index.html GS_Action_v34_runtime.html` | 3단계 모두 동일 | 클라우드 세션 |
| `node --check` `<script>` 247개 (importmap JSON 제외) | 3단계 모두 0 실패 | 클라우드 세션 |
| PR #3 node 전용 `SourceTests` 3개 | 3단계 모두 통과 | 클라우드 세션 |
| 브라우저 테스트 25개, 클라우드 세션 | **UNVERIFIED** (`cdn.jsdelivr.net` 차단, playwright 미설치) | 클라우드 세션 |
| 브라우저 테스트 25개, SwiftShader | PR #3 24/25 통과(실패 1: `test_fixed_target_and_real_phase_records`, 속도 민감). A 단독 11/14 실패(B·C·D 기능 요구). BC 24/25(실패 1: D 기능 테스트). 1회 실행. | 다른 환경, `gs-split-verification_v2` 기준. 이 repo에서 재현 안 함. |
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
- 빌드는 PR #3 계열로 보이나 파일 해시 미확인. main v34와 비교 측정 없음 → BC 병합 이득 판단 불가.
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
4. CI: `tests/`·`scripts/`를 #7 위에 쌓아 GitHub Actions로 25개 실행 (별도 PR).
5. Galaxy S25+ 화면·소리·터치·발열 (사용자 직접).
6. 장시간·메모리·복구 재검증 (GPU 환경).
