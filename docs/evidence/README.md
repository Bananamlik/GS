# docs/evidence

원본 보고서·측정 요약을 그대로 보존한 폴더. 파일은 수정하지 않는다. 새 증거는 새 파일명(`slug_vN_YYMMDD-HHMM.ext`)으로 추가한다.

| 파일 | md5 | 내용 | 주의 |
|---|---|---|---|
| `gs-cloud-handoff_v1_261005-1258.md` | `8536a79e6175a6f340b0ef8439c2b56c` | Codex 클라우드 작업 취합·인계 (PR #3) | 문서 수치. 재측정 안 함. 테스트 25개 통과는 Codex 보고. |
| `gs-evidence-runtime8_v1_261005-1329.json` | `2a670eedb7ed829ee62a78964e887a83` | `docs/cloud-runtime-8.md` 수치 요약 (SwiftShader) | 원시 로그는 repo에 없음. `reportedInConversationOnly` 항목은 미검증. |
| `gs-pr3-split-plan_v1_261005-1329.md` | `5589372a4723a1dd29d64d5368591d2b` | PR #3 분할 계획 (A/B/C/D 묶음, 병합 게이트) | 코드 분할 전에 쓴 계획. 실제 분할은 BC를 합쳐 3개 PR로 함. |
| `gs-split-verification_v2_261005-1927.md` | `2c86942246182e1f613e08c5b7b3fc7d` | 3개 패치 구성·검증 (A, BC, D) | SwiftShader 결과. 1회 실행. |
| `gs-gpu-measurement_v1_261005-2028.md` | `00631745408de10569c080c264b1e918` | 사용자 PC 실제 GPU 측정 해석 | 빌드 파일 해시 미확인. main v34 비교 없음. 1대·1회. |
| `gs-ci-results_v1_261005-2359.md` | `45ac8eca41a81cd1168ac5fa202ef937` | GitHub Actions 테스트 25개 결과 (D 25/25, BC 24/25, A 11/25) | 각 1회, SwiftShader. 예상된 실패 포함. |
| `gs-ci-results_v2_261006-0240.md` | `7a02c090453b514a596a390237f95e10` | 병합 후 테스트 25개 결과(main 포함), HUD 캡처 요약, `명중` 칩 진단 | 각 1회, SwiftShader. 칩 원인은 추정. |
| `gs-sfx-loudness_v1_261006-1230.md` | `d5423987972e4b00afeefc3468e99ced` | SFX 음량 측정 분석(효과 501개)과 정규화 제안 | 순간 음량은 가중치 없는 RMS. LUFS 아님. Lab 미리보기 1회. |
| `gs-sfx-loudness-raw_v1_261006-1230.json` | `c7c0ba5850b701272593e05ce30fba86` | SFX 음량 측정 원자료(효과별 피크·RMS·순간 음량) | 위 문서와 같은 한계. |
| `gs-sfx-gain-proposal_v1_261006-1230.csv` | `6699370b75accbb52ead37b99643ea7d` | 효과별 보정 게인 초안(목표 중앙값, ±12 dB, 피크 -3 dBFS) | 제안값. 적용 전 재측정·청취 필요. |
| `gs-sfx-loudness-after_v1_261006-1305.md` | `2e26290bfedbf4726f817658704c7501` | 정규화(#17) 후 재측정: 폭 26.3→9.0 dB, 최대 피크 -0.6 dBFS | 전과 같은 방법·한계. Lab 단일 효과 1회. 청감·겹침 UNVERIFIED. |
| `gs-sfx-loudness-after-raw_v1_261006-1305.json` | `e7025a2206bcacd42ad33e40041e4886` | 정규화 후 측정 원자료 | 위 문서와 같은 한계. |
| `gs-status-report_v1_261006-2015.md` | `a6801aaf1bcaebcbc13bbc1ca5d9dce9` | 전체 현황 분석(상태, 목표 달성도, UNVERIFIED 목록, 리스크, 다음 작업) | 읽기·분석만. 리스크 R4·R5는 코드 판독, 런타임 확인 안 함. |
| `gs-lab-hud-capture_v1_261006-2107.md` | `c4768b12e8ebda6c63aa9110a301c211` | 랩 모바일(#15) 면적·HUD 위계(#13) 캡처 결과를 probe 브랜치에서 이관 | SwiftShader 1회. 랩 후 측정은 최종 헤드 1커밋 전. `07-play` 측정 안 됨. |
| `gs-lab-metrics-before-raw_v1_261006-2107.json` | `895925313b010483804e1db8bc3e217a` | 랩 면적 원자료(전, `claude/probe-lab-before`) | 위 문서와 같은 한계. |
| `gs-lab-metrics-after-raw_v1_261006-2107.json` | `9845839d63f0ca4dc4987d64b530e8cb` | 랩 면적 원자료(후, `claude/probe-lab-after`) | 위 문서와 같은 한계. |
| `gs-hud-hier-capture-log_v1_261006-2107.txt` | `d46f8fd818d9e0b45a0fd8a4dc2ec7d8` | HUD 위계 캡처 로그(`claude/probe-hud-hier`) | 이미지는 브랜치에만 있음. |

## 한계

- SwiftShader(CPU 렌더) 수치는 GPU 성능이 아니다. 최적화 효과 판단에 쓰지 않는다.
- 실제 GPU 측정은 사용자 PC 1대(AMD Radeon 내장, Chrome 154)뿐이다.
- Galaxy S25+ 화면·소리·터치·발열은 UNVERIFIED.
