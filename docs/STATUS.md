# STATUS

갱신: 2026-10-08 20:50 KST. 근거: `docs/evidence/`. 검증하지 못한 항목은 UNVERIFIED.

## 1. 코드 상태

| 항목 | 값 |
|---|---|
| main | `bcf0ef7` (#47 병합). `index.html` = `GS_Action_v34_runtime.html`, md5 `8f6c5e60e32206cdfb3c53421a78379d` (위 + 런 S6 무대 묶음·지역 보스 + 전투 C5 예고 채움·피격 방향) |
| #45 시점 | main `1dd0d44`의 `index.html`, md5 `e05d67187d3869a3f638d9399621150e` |
| #41 시점 | main `44cb13e`의 `index.html`, md5 `7ebf35e6745424f0f8f2b0b653e85355` |
| 높이 보정까지(#35 시점) | main `886d728`의 `index.html`, md5 `10ef9fe87f56b0c0a9c13b92e86ff77e` |
| 런 S7까지(#30 시점) | main `3fc9c6e`의 `index.html`, md5 `0eaa8b73a1a4ef38a48e9809a52d5bd8` |
| SFX 겹침 규칙까지(#20 시점) | main `7bcf549`의 `index.html`, md5 `a1129562470585674331ed97ce640a6e` |
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
| [#16](https://github.com/Bananamlik/GS/pull/16) | 문서: md5·병합 이력 갱신 | `a7df8f0` |
| [#18](https://github.com/Bananamlik/GS/pull/18) | 문서: SFX 정규화 후 재측정 | `9c0f648` |
| [#19](https://github.com/Bananamlik/GS/pull/19) | 문서: STATUS 정정, 랩·HUD 증거 이관, 현황 보고서 | `b995c2a` |
| [#20](https://github.com/Bananamlik/GS/pull/20) | SFX 겹침 규칙: 다른 효과가 겹치면 마지막 효과 보정(감쇠만), 거절된 시전은 보정 안 바꿈 | `7bcf549` |
| [#21](https://github.com/Bananamlik/GS/pull/21) | 평점 3 이상 21개 스킬 주제 상태이상(`GA_SKILL_THEME`) | `a64f39f` |
| [#24](https://github.com/Bananamlik/GS/pull/24) | 런 S1: 런·계정 저장 구조(`GA_RUN`, `gs-run-1`·`gs-meta-1`) | `68422bc` |
| [#22](https://github.com/Bananamlik/GS/pull/22) | 문서: 평점 3 이상 243개 점검표 | `9b41e92` |
| [#23](https://github.com/Bananamlik/GS/pull/23) | 문서: 로그라이트 런 뼈대 설계(S1~S8) | `22881a6` |
| [#25](https://github.com/Bananamlik/GS/pull/25) | 런 S2: 노드 전투 실행기(체력 이월, 적 배율) | `8a362f9` |
| [#26](https://github.com/Bananamlik/GS/pull/26) | VFX 위치: 자기형 효과 시전자 추적, 지면 균열 바닥 고정, Lab 빔 길이 = 사거리 | `553d6ae` |
| [#27](https://github.com/Bananamlik/GS/pull/27) | 런 S3: 지도(3지역×6층), 지도 화면, 게임 화면 런 전투 | `ea16598` |
| [#28](https://github.com/Bananamlik/GS/pull/28) | 런 S4: 노드 보상(골드·스킬·패시브 12종), 일반 드래프트 평점 필터 수정 | `60b3b8a` |
| [#29](https://github.com/Bananamlik/GS/pull/29) | 런 S5: 상점·이벤트 5종·휴식 | `7cbf508` |
| [#30](https://github.com/Bananamlik/GS/pull/30) | 런 S7: 조각·해금(영웅 2·특성 3)·난이도 단계·최고 기록 | `3fc9c6e` |
| [#31](https://github.com/Bananamlik/GS/pull/31) | 문서: 세션 정리(10-07) | `6d933ae` |
| [#32](https://github.com/Bananamlik/GS/pull/32) | 문서: 인계 프롬프트 v2 | `b5f89cc` |
| [#33](https://github.com/Bananamlik/GS/pull/33) | 문서: VFX 위치 판정표 v1·v2 (243행, 정상 219·의심 24) | `f5403bd` |
| [#34](https://github.com/Bananamlik/GS/pull/34) | 수평 관통 빔(`D:PROJ:lance`): 무작위 방향 → 시전자에서 표적 방향 | `3ad36a8` |
| [#35](https://github.com/Bananamlik/GS/pull/35) | VFX 높이 보정 7개(`AC-02`·`ARC-08`·`SC-02`·`FX-10-O`·`FX-25`·`FX-146`·`AS-10`) | `886d728` |
| [#36](https://github.com/Bananamlik/GS/pull/36) | 문서: 상태 갱신 | `4ffcfcf` |
| [#37](https://github.com/Bananamlik/GS/pull/37) | 문서: 전투 설계 v1 (카메라·조준·이동·가독성·빌드 축, 결정 D1~D9 권장안 확정) | `2f799f2` |
| [#38](https://github.com/Bananamlik/GS/pull/38) | CI: 실패한 테스트 이름·오류 첫 줄을 주석으로 남김 | `7285c9a` |
| [#39](https://github.com/Bananamlik/GS/pull/39) | 전투 C1: 3인칭 카메라 거리 11(설정 8~16)·높이 +3.5·어깨 1.6·시작 시선 아래 16°·세로 화면 시야각 72° | `e0ca241` |
| [#40](https://github.com/Bananamlik/GS/pull/40) | 런 결과 화면의 버튼이 새 런 시작(P4), 메뉴 제목 v34 제거(P11) | `590d3c4` |
| [#41](https://github.com/Bananamlik/GS/pull/41) | 전투 C4: 준비 동작 중 회피로 취소(궁극기 제외). 위치 테스트 대기 시간 연장 | `44cb13e` |
| [#44](https://github.com/Bananamlik/GS/pull/44) | 테스트: 예열 대기를 결과 모양(`ids`)이 아니라 대기열 상태로 판정(6곳) | `c28467f` |
| [#45](https://github.com/Bananamlik/GS/pull/45) | 런 S6: 무대 묶음 `STAGES`(지역 이름·웨이브 표·지역 보스), 1·2지역 보스 = 강화된 적 1기(그 노드 한정), 지도·전투 준비에 지역·보스 이름. 저장 형식 불변 | `1dd0d44` |
| [#47](https://github.com/Bananamlik/GS/pull/47) | 전투 C5: 적 예고 안쪽 채움(판정 순간 가득), 예고를 내 효과 뒤에 그림(renderOrder 40~43), 피격 방향 호 0.45초 | `bcf0ef7` |
| [#48](https://github.com/Bananamlik/GS/pull/48) | 문서: 게임 기둥 v1 `docs/design/gs-game-pillars_v1_261009-1126.md` (읽고 피하고 꽂기 / 재미 3층 / 목표) | `2ae2ad3` |

- 닫음: [#4](https://github.com/Bananamlik/GS/pull/4) (권한 확인용).
- 열려 있음: [#49](https://github.com/Bananamlik/GS/pull/49) (빌드 축 B1 형태 조합, 초안. 조합 구성·수치 결정 대기), [#43](https://github.com/Bananamlik/GS/pull/43) (서사 뼈대 초안, 결정 N1~N8 대기), [#3](https://github.com/Bananamlik/GS/pull/3) (분할 전 원본. 내용이 `main`에 들어가 중복 상태. 닫을지는 사용자 결정), [#1](https://github.com/Bananamlik/GS/pull/1) (v14, 별개).
- 결과 수집용 브랜치(PR·병합 대상 아님, 삭제해도 됨) 12개: `claude/ci-probe-a`, `claude/ci-probe-bc`, `claude/probe-hud-capture`, `claude/probe-hud-capture-after`, `claude/probe-hud-capture-cd`, `claude/probe-hud-capture-cd2`, `claude/probe-chip`, `claude/probe-hud-hier`, `claude/probe-lab-before`, `claude/probe-lab-after`, `claude/probe-sfx`, `claude/probe-sfx-after`. 랩·HUD 위계 수치는 `docs/evidence/`로 옮김(`gs-lab-hud-capture_v1_261006-2107.md`). 캡처 JPG는 브랜치에만 있음.
- 병합 끝난 PR 헤드 브랜치 15개와 `codex/gs-v25…v34-*` 10개도 남아 있음. 삭제는 사용자 결정.

## 2. 검증 상태

| 항목 | 결과 | 환경 |
|---|---|---|
| `main` md5, `cmp index.html GS_Action_v34_runtime.html` | 두 파일 `8f6c5e60…`, 동일 (`bcf0ef7`) | 클라우드 세션 |
| `node --check` `<script>` JS 249개 + importmap 1개 (`bcf0ef7`) | 0 실패 | 클라우드 세션 |
| 테스트 51개 (브라우저 35 + Node만 16), PR #47 헤드 `10ab554` | **통과** | GitHub 러너, SwiftShader, 1회 |
| CI 간헐 실패 | #35·#36·#41에서 각 1회. #41에서 이름 확인: `test_poses_follow_ground_lab_length_and_shield_follows_hero`의 60초 대기 초과. 대기를 120~150초로 늘림(#41). 이후 판독으로 찾은 원인: 테스트가 `vfxWarmStatus.ids`를 기다리는데 개별 예열 결과에는 `ids`가 없음 → 대기열 상태로 판정하도록 수정(#44). 재현은 못 함, 원인 확정은 **UNVERIFIED** | 주석(annotation)으로 확인 |
| 런 모드 실제 플레이 체감·난이도·신규 수치·새 화면 모양 | **UNVERIFIED** (자동 테스트는 무적 영웅) | |
| VFX 위치 수정(#26) 화면 확인, 243개 전수 위치 점검 | **확인** (SwiftShader 캡처, `gs-vfx-anchor-audit_v2_261008-1811.md`). 정상 219·의심 24, 그중 8개는 #34·#35로 수정. 실제 GPU·실기기 화면은 UNVERIFIED | SwiftShader, 조준 1방향·거리 25 |
| 브라우저 테스트 25개, PR #20 헤드 `4e474ef` | **통과** | GitHub 러너, SwiftShader, 1회 |
| `node --check` `<script>` JS 248개 (importmap JSON 1개 별도 `json.loads`) | 0 실패 (`9c0f648`, 2026-10-06 21:00 재확인). 이전 기록의 247은 #17 이전 값 | 클라우드 세션 |
| 브라우저 테스트 25개, `main` `a7df8f0` (#17 코드 포함, `workflow_dispatch`, run 17) | **통과** (conclusion success) | GitHub 러너, SwiftShader, 1회 |
| 브라우저 테스트 25개, PR #17 헤드 `9117e99` (병합 전) | **통과** (run 15) | GitHub 러너, SwiftShader, 1회 |
| 브라우저 테스트 25개, `main` `a8df602` (`workflow_dispatch`, run 13) | **통과** (워크플로 conclusion success) | GitHub 러너, SwiftShader, 1회 |
| 브라우저 테스트 25개, `main` `a503a7e` | 25/25 통과 | GitHub 러너, SwiftShader, 1회 |
| 브라우저 테스트 25개, 단계별 | A 11/25, BC 24/25는 예상된 실패(BC·D 기능 요구). D 25/25. HUD A+B, C+D 헤드 모두 25/25. | GitHub 러너. `docs/evidence/gs-ci-results_v1_261005-2359.md`, `v2_261006-0240.md` |
| 랩 뷰 면적 (`viewVisiblePct`, 16×24 격자 중 캔버스 비율) | 세로 21→46%, 17→50%, 가로 12→33%, 데스크톱 변화 없음. 후 측정은 #15 최종 헤드 1커밋 전(`e491d02`). `07-play` 상태는 이동 실패로 측정 안 됨. `gs-lab-hud-capture_v1_261006-2107.md` | SwiftShader 캡처 |
| HUD 화면 확인 | 3개 화면 × 10장면 캡처를 눈으로 확인. 개선 항목 확인됨. | SwiftShader, 배율 1배 |
| `명중` 칩과 보상 창 | 6회 반복에서 지속 결함 재현 안 됨(페이드 중 캡처로 추정) | SwiftShader |
| 클라우드 세션 브라우저 실행 | **UNVERIFIED** (`cdn.jsdelivr.net` 차단) | 클라우드 세션 |
| SFX 음량 편차 | 정규화 전 p5–p95 26.1 dB → 후 9.0 dB (400ms 순간 음량 비가중). 실제 스피커 청감은 **UNVERIFIED**. `docs/evidence/gs-sfx-loudness_v1_261006-1230.md`, `gs-sfx-loudness-after_v1_261006-1305.md` | SwiftShader, 오디오 탭 |
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
- D의 프레임당 메모리 할당(`barriers`, `{z,order,group}`, `Map`, `filter/map/sort`, 임시 배열)은 그대로다 (`index.html` `syncStormBatches`, 1366줄 부근).
- D 해제 누락 가능성: storm 배치 `dispose()`가 `b.mesh.dispose()`만 부른다. `geometry.clone()`·`material.clone()` 해제가 안 보인다 (1381–1408줄 부근). 런타임 확인 안 함 → 추정.
- SFX 보정은 효과별이 아니라 AudioContext 공통 `trim`이다. #20 전: 최근 2.5초 효과 중 최소 보정 → 큰 효과 뒤 조용한 효과가 같이 깎임. #20 후: 같은 효과만 있으면 그 보정, 다른 효과가 겹치면 마지막 효과 보정을 0 dB 이하로(감쇠만), 거절된(busy) 시전은 보정을 바꾸지 않음. 겹칠 때 앞 효과 꼬리는 감쇠가 풀릴 수 있음(리미터 -4 dBFS가 피크 보호). 청감 UNVERIFIED.

## 5. 결정 대기

1. 예산 기준: 설정 60 vs pacing 목표 72.5. 현재 72.5.
2. 밸런스 승인: 설치물 46종만 승인, 나머지 379종은 제안값(`gs-cloud-handoff`).
3. PR #3 닫기, 결과 수집용 브랜치 삭제.
4. SFX 효과별 보정 구조: 겹침 규칙만 조정하기로 함(#20 적용). 공통 trim 구조는 유지. 겹침 청감 UNVERIFIED.
5. 평점 3 이상 스킬 상태이상: 주제 기반 21개 추가(#21 병합). 오로라 계열 burn 유지 여부, CSV v8 갱신, 피해 차등·속성 체계는 미결 (`gs-skill-theme_v1_261006-2147.md`).

## 6. 남은 작업

0. 게임 뼈대: 로그라이트 런(`docs/design/gs-run-skeleton_v1_261006-2213.md`). S1~S7 병합(S6은 #45: 무대 묶음·지역 보스. 지역별 기둥 배치는 `GA_SIM` 상수·뷰 메시를 함께 바꿔야 해서 새 맵 도입 시로 보류, 보스 이름 `잡귀 대장`·`대술사`와 수치 hp×3/×6은 임시). 새 맵(도시 `gs_g1`, 사이버펑크)은 `STAGES`에 묶음을 추가하는 방식. 남음: S8 타이틀·런 결과·튜토리얼(런 종료 후 "다시 시작"이 일반 6웨이브로 감). 모든 신규 수치는 초안, 플레이 후 조정. 세션 정리 `docs/evidence/gs-session-wrapup_v1_261007-0016.md`.
0-1. VFX 위치: 판정·1차 수정 완료(#33·#34·#35). 남음 16개 = 높이 보정이 안 듣는 `ARC-25`, 의도일 수 있는 공중 연출 5개(그대로 두기로 함), 크기·가림 10개(실기기에서 보고 결정). 평점 2 이하·폐기 효과는 작업 보류(사용자 방침, 평점 3 이상만 사용).
0-2. 전투 설계(`docs/design/gs-combat-design_v1_261008-1914.md`) 구현: C1 카메라(#39)·C4 회피 취소(#41)·C5 가독성(#47, 화면에서의 보임 정도는 UNVERIFIED) 완료. 상위 방향은 `docs/design/gs-game-pillars_v1_261009-1126.md`(작업 순서: 빌드 축 → 적 패턴 → C6 → S8 → C3). C2(범위 스킬 지점·준비 중 범위 표시)는 코드에 이미 있음(`w.cast`의 사거리 제한, `showPreview`) → 추가 작업 없음. 남음: 빌드 축 B1(#49 초안), 적 패턴 점검, C3 터치 조준 보조, C6 화면 가림 한도, S8 타이틀·결과·튜토리얼(결과 버튼만 #40으로 처리). 빌드 축(§8.3)은 새 VFX 목록 반입 후.
0-3. 수치(카메라 거리 11, 시작 시선 0.28 등)는 초안. 실제 조작감·실기기 UNVERIFIED. GPU·발열 검증은 보류(사용자 방침).

1. 같은 PC·같은 조건으로 main v34(`76ddfb4`)와 현재 `main`을 3회씩 측정 (보류 중).
2. 현재 빌드 60초 측정 후 결과 JSON(`phaseTotals`, `phaseSpans`, `longTasks`)을 `docs/evidence/`에 저장. 끊김 원인 좁히기. 품질 `낮음` 1회.
3. D 프레임당 할당 줄이기 (코드 변경, GPU 확인 후).
4. HUD 미착수: 색약 대응, 패널 색 통일. 메뉴 제목이 아직 `GS ACTION · v34`.
   SFX 음량 정규화는 #17로 적용됨. Lab 재측정: 폭 26.3→9.0 dB, 최대 피크 +0.4→-0.6 dBFS (`gs-sfx-loudness-after_v1_261006-1305.md`). 실기기 청취, 전투 겹침은 UNVERIFIED.
5. 조작감 후보 미착수: 터치 보조 조준, 스틱 데드존·반경, 마우스·터치 감도 분리, 진동 피드백.
6. Galaxy S25+ 화면·소리·터치·발열, HUD 터치 느낌 (사용자 직접).
7. 장시간·메모리·복구 재검증 (GPU 환경).
