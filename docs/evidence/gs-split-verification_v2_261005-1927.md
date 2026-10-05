# GS PR #3 분할 — 전체 묶음 구성·검증 결과 (v2)

작성: 2026-10-05 19:27 KST · v1(`gs-split-verification_v1_261005-1401.md`)은 묶음 A만 다뤘고, 이 문서가 A+BC+D 전체를 대체합니다.
작업 위치: 샌드박스의 로컬 복제본. GitHub에는 push하지 않았습니다(쓰기 권한 없음).

## 1. 결과 요약

PR #3(`codex/cloud-runtime-hardening` @ `953dd12`)의 실행본 변경을 **3개 패치**로 나눴고, 순서대로 적용하면 PR #3의 실행본과 byte 단위로 같은 파일이 만들어집니다.

| 순서 | 패치 | 내용 | 실행본 md5 (적용 후) |
|---|---|---|---|
| 0 | main `76ddfb4` | 기준 (v34) | `c9e4da56…` (sha256) |
| 1 | `gs-split-a-runtime_v1_261005-1401.patch` | **A** 경과 시간 프레임 제한, 출력 패스 생략, 렌더 크기 중복 설정 생략, 모듈 준비 취소 | `f0b0d3491881b4c714f2a8b3d0f77642` |
| 2 | `gs-split-bc-warmup_v1_261005-1927.patch` | **B+C** 벤치 보정·추적, 4개씩 예열 큐, 실행 준비, context 손실 복구 | `01c26f278a86e646f7cb2c6b9348e3cb` |
| 3 | `gs-split-d-storm_v1_261005-1927.patch` | **D** CH:storm 분절 인스턴싱, 투명도 0 표면 생략 | `f7d2ab883d7bc78fc05d9b046e45bf47` (= PR #3와 동일) |

패치 md5: A `8fe42d7af23e051c60ff08c60cd1a3d2` · BC `f771bc88a23f9dfd544ce9eff4b7ba36` · D `dfa8f9f0b6464f2fe8fa4514bb8e8e10`.

적용(깨끗한 main에서 확인함):

```bash
git checkout -b split/a 76ddfb47a0adb04bc614b5812dce72db1ab9a043
git am gs-split-a-runtime_v1_261005-1401.patch
git am gs-split-bc-warmup_v1_261005-1927.patch   # 별도 PR로 낼 때는 branch를 나눠 적용
git am gs-split-d-storm_v1_261005-1927.patch
```

각 패치는 앞 단계 위에 쌓이는 구조입니다(BC는 A 위, D는 BC 위). 각각 별도 PR로 올리려면 단계마다 branch를 만들고 이전 branch를 base로 지정합니다.

## 2. 왜 B와 C를 합쳤나

계획서에서는 B(벤치 계측)와 C(예열·복구)를 따로 두었으나, 실제 코드에서 `prepareWave`·`fx`·`ensurePool`·`gpuSweep` 등이 두 가지를 한 함수 안에서 함께 다뤄 줄 단위로 분리하면 중간 상태가 깨집니다. 억지로 쪼개 검증 안 된 조각을 만들기보다 B+C를 한 PR로 묶었습니다. D는 독립적으로 분리됩니다(BC 쪽에 `H.syncStormBatches?.()` 선택 호출 1곳이 남아 있으며, `?.`이라 D가 없어도 안전).

## 3. 검증 (이 샌드박스: 2 vCPU, SwiftShader)

검증 환경: three@0.186.0을 npm으로 받아 로컬 HTTPS 서버로 `cdn.jsdelivr.net`을 대체. 테스트는 PR #3의 `tests/` 25개를 그대로 사용했고 repo는 수정하지 않았습니다.

| 대상 | 통과 | 실패 | 비고 |
|---|---|---|---|
| PR #3 head (D까지 전부) | 24 | 1 | 실패는 `test_fixed_target_and_real_phase_records`(3초 창에서 프레임 0). 같은 환경에서 BC 실행 때는 통과함 → 속도에 민감한 불안정 테스트 |
| A | 11 | 14 | 실패 14개는 B·C·D 기능을 요구하는 테스트. 그중 3개는 대기 조건만 임시 변경한 사본에서 통과 |
| BC | 24 | 1 | 실패는 `test_storm_segmented_batches_…`(D 기능이라 예상) |
| 체인 A→BC→D | — | — | 최종 파일 md5가 PR #3와 일치함을 확인(위 표) |

`script` 247개 문법 검사(`node --check`)는 모든 단계에서 통과했습니다(248번째는 importmap JSON이라 대상 아님).

## 4. 병합 권장 (이전 평가 유지)

- **A**: 동작 보존형 수정. 테스트 통과, 먼저 병합해도 안전하다고 판단합니다. 단 실제 GPU 확인은 없습니다.
- **BC**: 시작 준비 시간을 줄이고 context 손실 복구를 보강하나 FPS 이득은 입증되지 않았습니다. 실제 GPU에서 시작 준비 시간·첫 사용 끊김을 변경 전/후 3회씩 측정한 뒤 병합을 권장합니다.
- **D**: 실제 GPU에서 프레임 시간 개선이 확인될 때만. 병합 전에 프레임당 할당(`barriers`, `{z,order,group}`, `Map`, `filter/map/sort`, 임시 배열)을 줄일 것.

## 5. 못 한 것 (UNVERIFIED)

- 실제 GPU / Galaxy S25+ / 소리 / 발열. 모든 수치는 SwiftShader.
- A만 적용했을 때와 BC까지 적용했을 때의 장시간(10분) 안정성.
- 14개 실패 테스트 각각의 코드를 읽어 원인을 개별 확인하지는 않았음(오류 메시지와 테스트 이름 기준).
- 이 문서의 단계별 테스트는 모두 1회 실행 결과이며 반복 측정이 아님.
