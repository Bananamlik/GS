# docs/evidence

원본 보고서·측정 요약을 그대로 보존한 폴더. 파일은 수정하지 않는다. 새 증거는 새 파일명(`slug_vN_YYMMDD-HHMM.ext`)으로 추가한다.

| 파일 | md5 | 내용 | 주의 |
|---|---|---|---|
| `gs-cloud-handoff_v1_261005-1258.md` | `8536a79e6175a6f340b0ef8439c2b56c` | Codex 클라우드 작업 취합·인계 (PR #3) | 문서 수치. 재측정 안 함. 테스트 25개 통과는 Codex 보고. |
| `gs-evidence-runtime8_v1_261005-1329.json` | `2a670eedb7ed829ee62a78964e887a83` | `docs/cloud-runtime-8.md` 수치 요약 (SwiftShader) | 원시 로그는 repo에 없음. `reportedInConversationOnly` 항목은 미검증. |
| `gs-pr3-split-plan_v1_261005-1329.md` | `5589372a4723a1dd29d64d5368591d2b` | PR #3 분할 계획 (A/B/C/D 묶음, 병합 게이트) | 코드 분할 전에 쓴 계획. 실제 분할은 BC를 합쳐 3개 PR로 함. |
| `gs-split-verification_v2_261005-1927.md` | `2c86942246182e1f613e08c5b7b3fc7d` | 3개 패치 구성·검증 (A, BC, D) | SwiftShader 결과. 1회 실행. |
| `gs-gpu-measurement_v1_261005-2028.md` | `00631745408de10569c080c264b1e918` | 사용자 PC 실제 GPU 측정 해석 | 빌드 파일 해시 미확인. main v34 비교 없음. 1대·1회. |

## 한계

- SwiftShader(CPU 렌더) 수치는 GPU 성능이 아니다. 최적화 효과 판단에 쓰지 않는다.
- 실제 GPU 측정은 사용자 PC 1대(AMD Radeon 내장, Chrome 154)뿐이다.
- Galaxy S25+ 화면·소리·터치·발열은 UNVERIFIED.
