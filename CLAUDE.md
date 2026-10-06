# CLAUDE.md

GS Action: 단일 HTML 게임/VFX 스튜디오. 현재 상태는 `docs/STATUS.md`, 증거는 `docs/evidence/`.

## 파일

- `index.html` = `GS_Action_v34_runtime.html`. 항상 byte 동일. 한쪽만 바꾸지 않는다. 현재 md5 `8558fefd4fe5ee410fed3f4a8e1be54f` (v35 + HUD 개선 + HUD 위계 + 랩 모바일 + SFX 음량 정규화).
- `GS_Action_v35_261005-2000.html`: PR #3 최종본과 byte 동일(md5 `f7d2ab883d7bc78fc05d9b046e45bf47`), HUD 개선 이전 빌드. 수정하지 않는다.
- `gs-skill-lib_v7_261003-0344.csv`: 스킬 라이브러리.
- `GS_Action_v14_261003-0447.html`, `gs-v14-report_v1_261003-0447.md`: 이전 버전·보고서.
- `docs/`: 상태·증거. `tests/`(25개), `scripts/`, `.github/workflows/tests.yml`은 `main`에 있고 PR마다 자동 실행됨(`workflow_dispatch`로 수동 실행도 가능).

## 규칙

- `index.html` 수정 전: md5 기록, 수정 후 md5 출력. 기대값과 다르면 중단하고 보고. 강제 패치 금지.
- 큰 블록 교체 전 백업(`.bak`). 패치는 앵커 기준 최소 줄 변경. 셰이더·uniform·config 블록 전체 교체 금지.
- 병합은 사용자가 지시할 때만. main 직접 push 금지.
- 코드 변경 PR과 docs-only PR을 섞지 않는다.
- 검증하지 못한 것은 "UNVERIFIED"로 쓴다. 통과로 쓰지 않는다. SwiftShader 수치는 GPU 성능이 아니다.

## 검증

1. 두 실행본 동일: `cmp index.html GS_Action_v34_runtime.html`
2. 문법: `<script>` 블록 추출 → `node --check` (importmap JSON은 `json.loads`만). `<script>` 248개 기준.
3. uniform: JS 선언 / GLSL 선언 / 런타임 set 일치. 새 mesh/material/RT는 참조 해제 확인. 프레임 루프 내 new/할당 0.
4. 브라우저 테스트(`tests/`): Python Playwright + Chromium + three.js CDN(`cdn.jsdelivr.net`) 필요.
   ```bash
   python3 -m http.server 8000 --bind 127.0.0.1 &
   python3 -m unittest discover -s tests -v
   ```
   CDN이 막히면 실패 이유만 보고하고 멈춘다.
5. 셰이더 컴파일·WebGL 실행·실기기는 로컬 샌드박스에서 확인 불가 → UNVERIFIED.

## PR 구조

- 분할 PR #5~#7, CI #9, HUD #10·#11·#13, 랩 모바일 #15, SFX 측정 문서 #14, SFX 음량 정규화 #17, 문서 #16·#18은 모두 `main`에 병합됨(상세는 `docs/STATUS.md`).
- 새 변경은 `main`에서 브랜치를 만든다. 코드 PR은 `index.html`과 `GS_Action_v34_runtime.html`을 함께 바꾸고 25개 테스트 통과를 확인한다.
- 화면 확인이 필요하면 결과 수집용 브랜치(`claude/probe-*`)처럼 캡처 워크플로를 별도 브랜치에 얹어 실행한다. `main`에 넣지 않는다.
