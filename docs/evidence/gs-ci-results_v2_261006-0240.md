# GitHub Actions 테스트·HUD 확인 결과 (v2, 병합 후)

기록: 2026-10-06 02:40 KST. 환경: GitHub 러너 `ubuntu-latest`, Playwright Chromium, SwiftShader. 각 1회 실행. `gs-ci-results_v1_261005-2359.md`의 후속이며 v1은 수정하지 않는다.

## 테스트 25개 (PR #3 `tests/`)

| 대상 | `index.html` md5 | 결과 | 실행 |
|---|---|---|---|
| PR #10 헤드 `bb329b8` (HUD A+B) | `8c6fcd507f42bd00a7f89f015ba8e8de` | 25/25 통과 | https://github.com/Bananamlik/GS/actions/runs/37344363440 |
| PR #11 헤드 `8e5f367` (HUD C+D) | `2323f3ce044c950810763c3f6317b3f1` | 25/25 통과 | https://github.com/Bananamlik/GS/actions/runs/37346642500 |
| PR #11 헤드 `1d9139c` (위협 알약·체력 영역 수정 포함) | `5c7263984c75c6c44346abee821b4b88` | 25/25 통과 | https://github.com/Bananamlik/GS/actions/runs/37347396462 |
| `main` `a503a7e` (전체 병합 후, `workflow_dispatch`) | `5c7263984c75c6c44346abee821b4b88` | 25/25 통과 | https://github.com/Bananamlik/GS/actions/runs/37348683004 |

## HUD 화면 캡처 (3개 화면 × 10장면, 눈으로 확인)

캡처 브랜치(PR·병합 대상 아님): 수정 전 `claude/probe-hud-capture`, A+B 후 `claude/probe-hud-capture-after`, C+D 후 `claude/probe-hud-capture-cd`, 위협 알약 수정 후 `claude/probe-hud-capture-cd2`. 화면은 데스크톱 1280×720, 폰 가로 915×412, 폰 세로 412×915. 배율 1배. 모든 실행에서 페이지 오류 0건.

확인된 개선: 위협 알약이 스킬 바·터치 버튼·왼쪽 체력 영역을 피함, 터치 버튼에 쿨다운 숫자와 궁극 %, 스킬 이름 줄바꿈 개선, 가로 폰 스킬 줄 확대, 이동 스틱 안내 점선 원, 가로 폰 보상 창 스크롤 안내, 조준점 외곽선, 적 이름·체력바 확대, 저체력 붉은 가장자리 맥동(체력 가득이면 없음).

## `명중` 칩과 보상 창 진단 (`claude/probe-chip`, 6회)

세로 폰에서 `명중` 칩이 보상 창 글자 위에 보인 캡처가 한 번 있었다. 6회 반복에서 보상 창이 열린 직후 계산된 투명도가 1인 경우가 1회 있었으나 500ms 뒤에는 모두 0이었고, 이 시점의 스크린샷에서 칩은 보이지 않았다. 칩은 페이드(0.16초) 중이었던 것으로 추정한다. 지속되는 결함은 재현되지 않았다. 원인 확정은 아님.

## 한계

- SwiftShader. 실제 GPU, 폰 터치 느낌, 소리, 발열은 UNVERIFIED.
- 각 1회 실행. 반복 측정 아님.
