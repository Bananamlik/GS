# GitHub Actions 테스트 결과 (PR #3 `tests/` 25개)

기록: 2026-10-05 23:59 KST. 환경: GitHub 러너 `ubuntu-latest`, Playwright Chromium 1243, SwiftShader. 각 단계 1회 실행. 워크플로: `.github/workflows/tests.yml` (PR #9). `tests/`, `scripts/`는 PR #3(`953dd12`)와 byte 동일.

| 단계 | 대상 | `index.html` md5 | 결과 | 실행 |
|---|---|---|---|---|
| D (= PR #3 코드) | PR #9 `claude/ci-tests` @ `9d6d3c9` | `f7d2ab883d7bc78fc05d9b046e45bf47` | **25/25 통과** | https://github.com/Bananamlik/GS/actions/runs/37325992150 |
| BC | probe `claude/ci-probe-bc` @ `aec5f31` | `01c26f278a86e646f7cb2c6b9348e3cb` | **24/25** (실패 1) | https://github.com/Bananamlik/GS/actions/runs/37328126489 |
| A | probe `claude/ci-probe-a` @ `3df0c5b` | `f0b0d3491881b4c714f2a8b3d0f77642` | **11/25** (실패 14: failures 5, errors 11) | https://github.com/Bananamlik/GS/actions/runs/37328122287 |

## 세부

- **BC 실패 1개**: `test_storm_segmented_batches_preserve_alpha_order_and_visibility`. D의 기능(폭풍 묶음 렌더링)을 검사하는 테스트라 예상된 실패. 오류: `AssertionError: 0 not greater than 200`.
- **A 통과 11개**: `library_variants_and_seeded_simulation`, `mobile_and_desktop_library_review_panels`, `repeat_compare_cancel_and_json_export`, `wave_reward_changes_checkpoint_and_restores_lab_kit`, `module_preparation_cancels_and_rebuilds_after_context_loss`, `output_copy_elision_preserves_pixels_and_conversion_fallback`, `preparation_failure_cannot_pass`, `quality_changes_resize_once_and_skip_identical_settings`, `SourceTests` 3개.
- **A 실패 14개**: 오류가 `GS_ACTION.warmStatus`, `GS_ACTION.warmFx`, `__GS_TRACE_START`, `targetBasis` 등 BC·D에 있는 기능이 없다는 내용(`undefined`, `not defined`, `KeyError`). 테스트 코드를 개별로 읽어 원인을 확인하지는 않았고 오류 메시지 기준임.
- 위 결과는 `gs-split-verification_v2`의 SwiftShader 결과(PR #3 24/25, A 11/14 실패, BC 24/25)와 A·BC는 같고, PR #3(D)는 이번에 25/25로 달랐음(이전 문서의 1개 실패 `test_fixed_target_and_real_phase_records`는 속도 민감 테스트로 이번엔 통과).

## 한계

- 각 1회 실행. 반복 측정 아님.
- GPU가 아닌 SwiftShader. 성능 근거로 쓰지 않음.
- probe 브랜치는 결과 수집용이며 PR이 없고 병합 대상이 아님.
