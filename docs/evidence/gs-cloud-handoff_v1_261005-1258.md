# GS Action — 중단 작업 취합·인계 보고

작성: 2026-10-05 12:58 KST · 대상 repo: `Bananamlik/GS` (공개)

## 1. 한 줄 요약

Codex 클라우드 작업은 날아가지 않았다. 결과물은 GitHub `codex/cloud-runtime-hardening` branch(PR #3)에 커밋 2개로 push되어 있다. 코드·문서는 완결 상태이고, 빠진 것은 원시 측정 로그와 **실제 GPU 성능 증거**다. FPS 목표(60)는 미달이다.

## 2. 제출물 위치

| 항목 | 값 |
|---|---|
| repo | https://github.com/Bananamlik/GS |
| 작업 branch | `codex/cloud-runtime-hardening` @ `953dd12` |
| PR | #3 (`refs/pull/3/head` = 953dd12). 병합 안 됨 |
| 기준 | main @ `76ddfb4` (PR #2, v34 병합) |
| 커밋 1 | `aeda957` VFX 준비 보강, 폭풍 조각 배칭, 클라우드 회귀 검사 |
| 커밋 2 | `953dd12` 셰이더 예열 4개씩 분할, 부하 중 프레임 제한 수정, 425스킬·767변형 전수 렌더 |
| 실행본 | `index.html` = `GS_Action_v34_runtime.html`, md5 `f7d2ab883d7bc78fc05d9b046e45bf47`, sha256 `c4a1555b8dce092b6d950f49f462b9cad655b1267b6ec80f81e64faf74e2f19b` |
| 이전 v34 (main) | sha256 `c9e4da5639a1bd14ff2f636d22d9b476ad8d403a9f6f1e173f57b5dfa453614f`. 업로드 zip·v34 보고서와 일치 확인 |
| 변경 파일 (10) | index.html, GS_Action_v34_runtime.html, README.md, .gitignore, docs/cloud-validation.md, docs/cloud-runtime-8.md, scripts/audit_vfx_cloud.py, scripts/benchmark_cloud.py, tests/test_cloud_workflows.py, tests/test_performance_measurement.py |

branch 내 설명 문서: `docs/cloud-runtime-8.md`(최종), `docs/cloud-validation.md`(runtime-6 기록).

## 3. 이번 작업에서 한 것 (branch 기준)

1. 측정 신뢰성: 전투 전 유휴 RAF에서 FPS 목표 고정(부하로 목표가 20FPS로 잘못 산정되던 문제 수정), 단계별 시간·느린 작업 스택·렌더 호출 기록.
2. 프레임 제한: RAF 건너뛰기 방식에서 경과 시간 기준으로 변경. 느린 프레임을 추가로 건너뛰지 않음.
3. 셰이더 예열: 선택 효과를 시작 전에 4개씩 생성·컴파일·예열. 취소·소유권 반환·렌더 타깃 복원·15초 타임아웃. 병렬 컴파일 미지원 경로 포함.
4. WebGL context 손실: 미완료 준비 취소, 준비 캐시 세대 교체, 복구 후 재준비.
5. 렌더 비용: 출력 패스(항등 복사) 생략, CH:storm 투명도 0 표면 생략, 폭풍 원뿔 파편 깊이 구간별 인스턴스 묶음. 렌더 호출 최대 496 → 222.
6. 전수 렌더 검사: 425스킬·767변형 모두 픽셀 변화 있음, 시전 거절·셰이더/GL 오류 0. 네이티브 접촉 신호 172건(없는 효과는 추정값 승인 안 함).
7. 장시간: 10분 6웨이브 3회 완주, 오류 0 (이전 단계 기록). 최종 240초 측정에서 JS 힙 35~93MB, GPU 지오메트리·텍스처 회수 확인.

전투 수치(GA_SIM·GA_SKILLS)는 main과 byte 단위로 동일함을 이번에 재확인했다(바뀐 script 블록은 VFX 호스트, GS Action 뷰, 작은 설정 블록 3개).

## 4. 검증 상태

| 항목 | 상태 |
|---|---|
| script 247개 `node --check` (main·branch 모두) | 통과 (248번째는 importmap JSON) |
| 문서상 회귀 테스트 | 25개 통과 (Codex 보고). 이 세션에서 재실행 안 함 |
| 폭풍 배칭 화면 비교 | 카메라 3방향×시각 5개, 채널 차 최대 1/255 이내 (Codex 보고) |
| 성능 | 미달. 60초 측정: 변경 전 평균 15.4 → 예열 분할안 13.8 → 최종(60FPS 제한) 12.2 FPS. 30FPS 제한 7.8 FPS. 시작 준비 9.68초 → 약 7.3초 |
| 실제 GPU / Galaxy S25+ / 청취 / 밸런스 | **UNVERIFIED** |
| 셰이더 컴파일·WebGL 실행 (이 세션) | **UNVERIFIED** (읽기 검토만) |

측정은 모두 Chromium + SwiftShader(CPU 소프트웨어 렌더)다. 이 환경의 FPS는 실기기 성능이 아니며 draw call·필레이트 개선이 FPS에 거의 반영되지 않는다. ∴ "최적화 효과 없음"으로도 "있음"으로도 결론 낼 수 없다.

## 5. 검토에서 나온 위험

1. **성능 이득 미입증.** 코드 약 +330줄(복잡도 증가) 대비 FPS 개선 증거 없음. 개선은 시작 준비 시간뿐.
2. **폭풍 배칭 프레임당 할당.** `syncStormBatches`가 storm 활성 시 매 프레임 `scene.traverseVisible`, 배열·객체·`Map`·`filter/map/sort`를 새로 만든다. 루프 내 할당 0 원칙 위반. 모바일 GC 끊김 위험. 화면 정확도는 위 1/255 비교로 어느 정도 방어되나 검증 조건(카메라 3, 시각 5)은 제한적.
3. **원시 로그 미보존.** `runtime-8-tests.log`, `audit-all.json`, `final-repeat.json` 등은 Codex 환경 `/workspace/gs-onboarding/remaining/`에만 있음. `.gitignore`가 `cloud-results` 제외. 환경 소멸 시 증거 상실.
4. **v34 자체 한계(main):** 배칭은 가짜 fixture로만 확인, 실제 게임 draw call 감소 미측정, 프레임 예산 기준은 내부 기준, `physicalDeviceApproved=false`.
5. **GitHub 접근:** 이 세션은 공개 repo 읽기만 됨(쓰기 권한·토큰 없음). push·PR 수정은 별도 연결 필요.

## 6. 남은 계획 (우선순위)

| # | 작업 | 완료 기준 | 난이도 / 권장 |
|---|---|---|---|
| 1 | 증거 보존: 요약 JSON·로그를 `docs/evidence/`에 커밋 | 재현 명령 + 수치 파일이 branch에 존재 | 쉬움 |
| 2 | PR #3 분할: 안전한 수정(경과 시간 pacer, context 손실 취소, 렌더 버퍼 중복 설정 생략, 출력 패스 생략)을 먼저, 폭풍 배칭·4개 예열은 별도 PR | PR 2개, 각각 회귀 통과 | 중간 |
| 3 | 실제 GPU 측정: 사용자 PC(Chrome)에서 `benchmark_cloud.py` 동등 측정. 30/60FPS, 평균·p95·p99, 시작 준비 | SwiftShader가 아닌 GPU 수치 3회 이상 | 중간 (환경 의존) |
| 4 | 폭풍 배칭 재설계 또는 보류: 프레임 할당 제거(배열 재사용), GPU 측정에서 이득 확인 시에만 병합 | 루프 내 신규 할당 0, GPU에서 이득 입증 | 어려움 |
| 5 | 시작 준비 7.3초 단축, 프레임 지연 원인 분석(2~3초 멈춤 추적) | GPU 기준 프로파일에서 병목 1개 확정 후 수정 | 어려움 |
| 6 | 장시간·메모리, 장비/보상/체크포인트/context 복구 재검증 (GPU 환경) | 10분 3회, 오류 0, 자원 회수 | 중간 |
| 7 | Galaxy S25+ 화면·소리·터치·발열 | 사용자 실기기 확인 | 사용자 직접 |
| 8 | 밸런스 승인(설치물 46종만 승인, 나머지 379종 제안값), 폭발 파편 벽 넘김, 제외 53종 보정 | 사용자 결정 | 사용자 결정 |

기능 범위 밖(별도 설계): 공포·도발·실명·띄우기 규칙.

## 7. 모델 선택 의견

이 판단은 작업 성격에 대한 의견이다. Opus 5.5의 성능·가격 수치는 이 세션에서 확인하지 못했다.

- **Sonnet 5.5 높음으로 충분한 일:** 1(증거 보존), 2(PR 분할은 diff 재배치 위주), 문서·체크리스트 정리, 테스트 재실행.
- **상위 모델이 이득일 가능성이 큰 일:** 4·5 — 렌더 파이프라인(투명 정렬, 컴파일 타이밍, 비동기 취소 경합)을 읽고 원인을 가설→측정으로 좁히는 작업. 이 부분은 거대한 단일 파일(스크립트 1.36MB 블록) 안에서 상태 상호작용을 추적해야 해서 실수 비용이 크다.
- **모델보다 먼저 필요한 것:** 3번(실제 GPU 측정). 측정 환경이 SwiftShader이면 어떤 모델이 작업해도 최적화 근거가 생기지 않는다. 순서 권장: 1·2를 현재 모델로 → 3 확보 → 수치를 근거로 4·5를 상위 모델에 위임.
- 위임 시 전달물: 이 보고서, `docs/cloud-runtime-8.md`, GPU 측정 JSON.
