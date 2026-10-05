# CLAUDE.md

GS Action: 단일 HTML 게임/VFX 스튜디오. 현재 상태는 `docs/STATUS.md`, 증거는 `docs/evidence/`.

## 파일

- `index.html` = `GS_Action_v34_runtime.html`. 항상 byte 동일. 한쪽만 바꾸지 않는다.
- `gs-skill-lib_v7_261003-0344.csv`: 스킬 라이브러리.
- `GS_Action_v14_261003-0447.html`, `gs-v14-report_v1_261003-0447.md`: 이전 버전·보고서.
- `docs/`: 상태·증거. `tests/`, `scripts/`, `.github/workflows/`는 PR #3 계열과 CI PR(#9)에만 있음.

## 규칙

- `index.html` 수정 전: md5 기록, 수정 후 md5 출력. 기대값과 다르면 중단하고 보고. 강제 패치 금지.
- 큰 블록 교체 전 백업(`.bak`). 패치는 앵커 기준 최소 줄 변경. 셰이더·uniform·config 블록 전체 교체 금지.
- 병합은 사용자가 지시할 때만. main 직접 push 금지.
- 코드 변경 PR과 docs-only PR을 섞지 않는다.
- 검증하지 못한 것은 "UNVERIFIED"로 쓴다. 통과로 쓰지 않는다. SwiftShader 수치는 GPU 성능이 아니다.

## 검증

1. 두 실행본 동일: `cmp index.html GS_Action_v34_runtime.html`
2. 문법: `<script>` 블록 추출 → `node --check` (importmap JSON은 `json.loads`만). `<script>` 247개 기준.
3. uniform: JS 선언 / GLSL 선언 / 런타임 set 일치. 새 mesh/material/RT는 참조 해제 확인. 프레임 루프 내 new/할당 0.
4. 브라우저 테스트(`tests/`): Python Playwright + Chromium + three.js CDN(`cdn.jsdelivr.net`) 필요.
   ```bash
   python3 -m http.server 8000 --bind 127.0.0.1 &
   python3 -m unittest discover -s tests -v
   ```
   CDN이 막히면 실패 이유만 보고하고 멈춘다.
5. 셰이더 컴파일·WebGL 실행·실기기는 로컬 샌드박스에서 확인 불가 → UNVERIFIED.

## PR 구조

분할 PR은 쌓인 구조: A(#5) → BC(#6) → D(#7). 각각 draft. 앞 PR이 병합되면 다음 PR base를 갱신한다.
