# STATUS

갱신: 2026-10-06 12:45 KST. 근거: `docs/evidence/`. 검증하지 못한 항목은 UNVERIFIED.

## 1. 코드 상태

| 항목 | 값 |
|---|---|
| main | `b43914e`. `index.html` = `GS_Action_v34_runtime.html`, md5 `8558fefd4fe5ee410fed3f4a8e1be54f` (v35 + HUD 개선 + HUD 위계 + 랩 모바일 + SFX 음량 정규화) |
| v35 파일 | `GS_Action_v35_261005-2000.html`, md5 `f7d2ab883d7bc78fc05d9b046e45bf47` = PR #3 최종본. HUD 개선 이전 빌드. 수정하지 않음. |
| 랩 모바일까지(#15 시점) | main `a8df602`의 `index.html`, md5 `f239381cb8f1ab9107ac1325db821e24` |
| HUD 개선만(#11 시점) | main `a503a7e`의 `index.html`, md5 `5c7263984c75c6c44346abee821b4b88` |
| 이전 v34 | main `76ddfb4`의 `index.html`, md5 `d8cb70f2d1876a0386740b73b2d6ecb9` |

### 병합 이력 (2026-10-06, 모두 merge commit)

| PR | 내용 | 병합 커밋 |
|---|---|---|
| [#8](https://github.com/Bananamlik/GS/pull/8) | 문서, 증거 | `dc61a71` |
| [#5](https://github.com/Bananamlik/GS/pull/5) A | 경과 시간 pacing, 출력 패스 생략, 렌더 크기 중복 설정 생략, 모듈 준비 취소 | `23b0b01` |
| [#6](https://github.com/Bananamlik/GS/pull/6) BC | 벤치 보정·추적, 4개씩 예열 큐, 실행 준비, context 손실 복구 | `744f093` |
| [#7](https://github.com/Bananamlik/GS/pull/7) D | CH:storm 분절 인스턴싱, 투명도 0 표면 생략 | `74b7b6a` |
| [#9](https://github.com/Bananamlik/GS/pull/9) | `tests/`, `scripts/`, GitHub Actions(25개) | `b07b275` |
| [#10](https://github.com/Bananamlik/GS/pull/10) HUD A+B | 위협 알약 겹침, 피드백 칩, 터치 쿨다운 숫자, 스킬 이름 줄바꿈, 이동 안내 | `38aed51` |
| [#11](https://github.com/Bananamlik/GS/pull/11) HUD C+D | 보상 창 스크롤 안내, 조준점 외곽선, 적 이름·체력바 확대, 저체력 경고, 위협 알약·체력 영역 수정 | `a503a7e` |
| [#14](https://github.com/Bananamlik/GS/pull/14) | 스킬 SFX 음량 측정 문서·원자료·보정안 CSV (코드 변경 없음) | `7d22d4c` |
| [#13](https://github.com/Bananamlik/GS/pull/13) | 게임 HUD 위계: 터치 성능 표시 좌하단 이동, 상단 스킬 줄 터치 기본 숨김(설정 `스킬 이름 줄`), 목표 칩 완료·실패 후 페이드 | `4729a7d` |
| [#15](https://github.com/Bananamlik/GS/pull/15) | 랩 모바일: 압축 미리보기 바, 하단 시트(peek 30dvh / tall 80dvh), 카메라 뷰를 남은 영역 중앙으로 이동, 가로 모드 배치 | `a8df602` |
| [#17](https://github.com/Bananamlik/GS/pull/17) | SFX 음량 정규화: 효과별 보정(±12 dB, 495개), 공통 음량 슬라이더(랩 `#vSfxVol`, 게임 설정 `#gaSfxVol`), 리미터 | `b43914e` |

- 닫음: [#4](https://github.com/Bananamlik/GS/pull/4) (권한 확인용).
- 열려 있음: [#3](https://github.com/Bananamlik/GS/pull/3) (분할 전 원본. 내용이 `main`에 들어가 중복 상태. 닫을지는 사용자 결정), [#1](https://github.com/Bananamlik/GS/pull/1) (v14, 별개).
- 결과 수집용 브랜치(PR·병합 대상 아님, 삭제해도 됨): `claude/ci-probe-a`, `claude/ci-probe-bc`, `claude/probe-hud-capture`, `claude/probe-hud-capture-after`, `claude/probe-hud-capture-cd`, `claude/probe-hud-capture-cd2`, `claude/probe-chip`.

## 2. 검증 상태

| 항목 | 결과 | 환경 |
|---|---|---|
| `main` md5, `cmp index.html GS_Action_v34_runtime.html` | 두 파일 `8558fefd…`, 동일 | 클라우드 세션 |
| `node --check` `<script>` 247개 (importmap JSON 제외) | 병합 단계마다 0 실패 | 클라우드 세션 |
| 브라우저 테스트 25개, PR #17 헤드 `9117e99` (병합 전) | **통과** (run 15) | GitHub 러너, SwiftShader, 1회 |
| 브라우저 테스트 25개, `main` `a8df602` (`workflow_dispatch`, run 13) | **통과** (워크플로 conclusion success) | GitHub 러너, SwiftShader, 1회 |
| 브라우저 테스트 25개, `main` `a503a7e` | 25/25 통과 | GitHub 러너, SwiftShader, 1회 |
| 브라우저 테스트 25개, 단계별 | A 11/25, BC 24/25는 예상된 실패(BC·D 기능 요구). D 25/25. HUD A+B, C+D 헤드 모두 25/25. | GitHub 러너. `docs/evidence/gs-ci-results_v1_261005-2359.md`, `v2_261006-0240.md` |
| 랩 뷰 면적 (`viewVisiblePct`, 16×24 격자 중 캔버스 비율) | 세로 21→46%, 17→50%, 가로 12→33%, 데스크톱 변화 없음 | SwiftShader 캡처 |
| HUD 화면 확인 | 3개 화면 × 10장면 캡처를 눈으로 확인. 개선 항목 확인됨. | SwiftShader, 배율 1배 |
| `명중` 칩과 보상 창 | 6회 반복에서 지속 결함 재현 안 됨(페이드 중 캡처로 추정) | SwiftShader |
| 클라우드 세션 브라우저 실행 | **UNVERIFIED** (`cdn.jsdelivr.net` 차단) | 클라우드 세션 |
| SFX 음량 편차 | 측정함(p5–p95 26.1 dB, 400ms 순간 음량 비가중). 실제 스피커 청감은 **UNVERIFIED**. `docs/evidence/gs-sfx-loudness_v1_261006-1230.md` | SwiftShader, 오디오 탭 |
| 실제 GPU / Galaxy S25+ 터치 느낌 / 소리 / 발열 / 랩 시트 핸들 조작 | 아래 §3 외 **UNVERIFIED**. HUD 개선은 GPU 측정 이후 변경. | |

## 3. 실제 GPU 측정 (사용자 PC 1대, HUD 개선 이전 빌드)

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
- 빌드는 PR #3 계열(v35)로 보이나 측정에 쓴 파일의 해시는 미확인. main v34와 비교 측정 없음.
- draw call이 병목으로 안 보여 D 우선순위 낮음(추정, 직접 증명 아님).

## 4. 병합 경위와 위험

- BC와 D는 이전 권고(main v34 비교 3회, 실제 GPU 프레임 시간 개선 확인)를 거치지 않고 사용자 지시로 병합했다. 이득은 입증되지 않음. 문제가 있으면 병합 커밋 `744f093`(BC), `74b7b6a`(D)를 되돌릴 수 있다.
- D의 프레임당 메모리 할당(`barriers`, `{z,order,group}`, `Map`, `filter/map/sort`, 임시 배열)은 그대로다.

## 5. 결정 대기

1. 예산 기준: 설정 60 vs pacing 목표 72.5. 현재 72.5.
2. 밸런스 승인: 설치물 46종만 승인, 나머지 379종은 제안값(`gs-cloud-handoff`).
3. PR #3 닫기, 결과 수집용 브랜치 삭제.

## 6. 남은 작업

1. 같은 PC·같은 조건으로 main v34(`76ddfb4`)와 현재 `main`을 3회씩 측정 (보류 중).
2. 현재 빌드 60초 측정 후 결과 JSON(`phaseTotals`, `phaseSpans`, `longTasks`)을 `docs/evidence/`에 저장. 끊김 원인 좁히기. 품질 `낮음` 1회.
3. D 프레임당 할당 줄이기 (코드 변경, GPU 확인 후).
4. HUD 미착수: 색약 대응, 패널 색 통일. 메뉴 제목이 아직 `GS ACTION · v34`.
   SFX 음량 정규화는 #17로 적용됨. 정규화 후 재측정(`claude/probe-sfx-after`)과 실기기 청취는 UNVERIFIED.
5. 조작감 후보 미착수: 터치 보조 조준, 스틱 데드존·반경, 마우스·터치 감도 분리, 진동 피드백.
6. Galaxy S25+ 화면·소리·터치·발열, HUD 터치 느낌 (사용자 직접).
7. 장시간·메모리·복구 재검증 (GPU 환경).
