# VFX 위치 점검 판정표 (v2)

작성: 2026-10-08 18:11 KST. 대상: 평점 3 이상 243개 효과. 인계 문서 §7-1, P6·P7. v1(`gs-vfx-anchor-audit_v1_261008-1745.md`)을 대체한다.

## 1. 요약

- 243개 중 **정상 219개, 의심 24개**. (v1은 정상 194, 의심 49)
- 의심 분류(중복 있음): 과대 10, 허공 9, 하늘 6, 안 보임 2, 치우침 1, 방향 1.
- v1에서 의심이던 49개 중 25개는 재촬영 결과 정상으로 바뀌었다. 이유는 둘이다.
  - **촬영 시점**: 낙하·비행·생성 도중에 찍힌 것(13개).
  - **크기 배율**: v1 캡처는 스킬의 `fxScale`을 넣지 않고 원본 크기로 시전했다. 실제 게임은 `fxScale`(0.35~2.5)로 줄이거나 키운다. 게임 배율로 다시 찍으니 과대·높이·안 보임 문제가 사라진 것(12개).
- 확정된 코드 결함 1건: `D:PROJ:lance`가 시전마다 무작위 방향으로 나감 → 수정 PR #34.
- 나머지 23개는 '공중에 뜸'·'너무 큼' 계열이다. 원본 연출 의도일 수 있어 **사용자 판단이 필요**하다(§5).
- 실제 GPU·실기기 화면은 **UNVERIFIED**. 전부 SwiftShader(CPU 렌더) 캡처다.

## 2. 자료

| 캡처 | 브랜치·커밋 | 내용 | 장수 |
|---|---|---|---|
| v2 | `claude/probe-vfx-anchor` `ac45664` (run 37485389695) | 243개 × 측면·상단, 효과당 1시점(`firstHit+0.15초`), **원본 크기** | 498 |
| v3 | `claude/probe-vfx-anchor-v3` `b6c4892` (run 37752249366) | v1 의심 49개 × 6시점(0.3~약 7초), 원본 크기. 자광 단층 5시점, 관통 빔 조준 3방향, Lab 빔 2개 | 616 |
| v4 | `claude/probe-vfx-anchor-v4` `6bc455b` (run 37753531802) | 평점 3 이상 중 `fxScale`이 있는 78개 × 3시점, **게임 배율** | 468 |

- 세 실행 모두 성공, pageerrors 0, 시전 실패 0.
- v3·v4 대상 빌드는 main `b5f89cc`(md5 `0eaa8b73a1a4ef38a48e9809a52d5bd8`). v2 대상 빌드는 md5 `b6f3b177…`이며 효과 배치 코드(`poseFor`·`fx`·`__FX_ADJ` 등)는 main과 같다(`diff` 확인).
- 시전 조건: 영웅 (0,0), 조준점 (0,-25), `GS_ACTION.fx({caster:'test'})`. 카메라 측면 (34,14,-12)→(0,6,-12), 상단 (0,46,20)→(0,0,-12), 960×540.
- 판정: 조준점·영웅 발밑에 십자를 그린 묶음 시트를 전부 눈으로 확인. 보조로 배경 차이 픽셀의 높이·거리를 계산(작은 효과에서는 부정확).
- `fxScale`이 없는 165개는 게임에서도 원본 크기(배율 1)라 v2 판정이 그대로 유효하다.

## 3. 한계

- 조준 방향은 -z 1방향(관통 빔만 3방향). 좌우·대각 조준은 확인하지 않았다.
- 조준 거리 25 고정. 방사형(radial) 스킬은 실제로는 시전자 중심인데 여기서는 조준점에 놓였다.
- 스크린샷이 느려 v3·v4의 실제 촬영 시각은 계획보다 늦다(표의 시각은 실제 값).
- v4는 기본 변형의 `fxScale`만 썼다. 다른 변형(M·L·XL)은 확인하지 않았다.
- '허공'·'과대'는 눈 판정이다. 원본 의도 여부는 코드로 판별할 수 없다.

## 4. #26 수정 확인과 Lab

| 장면 | 결과 | 근거 |
|---|---|---|
| 비상 날개(`D:ULT:ascend`) | 영웅을 +10 옮긴 뒤에도 날개가 영웅 등에 있음 → 추적 확인 | v2 B |
| 실드(`ARC-04`) | 영웅 이동 후에도 돔이 영웅 중심 → 추적 확인 | v2 B |
| 지열 균열(`D:PROJ:fissure`) | 발밑에서 시작해 바닥을 따라 조준점까지 감 | v2 B |
| 자광 단층(`VA:violet_fault`) | 약 3.9초에 발밑~조준점 바닥을 따라 선이 그려지고 약 6초에 조준점에서 폭발 → 바닥 고정 확인. 시전 후 2초 넘게 거의 안 보임 | v3 |
| Lab 빔 길이(`CH:tidal`, `CH:storm`) | 안내 창을 닫고 재촬영. 빔이 화면을 가로질러 끝까지 그려짐, `labBeamHalf` = 27.5 | v3 |

인계 문서 P6 후보 대조: `ARC-08` 하늘(의심 유지), `AC-02` 머리 위 대형 → 게임 배율에서는 작아지지만 돔 바닥이 가슴 높이(의심 유지), `ARC-07` 정상.

## 5. 의심 24개와 처리 제안

| # | id | 이름 | 종류/형태 | 게임 배율 | 분류 | 메모 | 근거 |
|---|---|---|---|---|---|---|---|
| 0 | `FX-06` | 플랑크톤 해류 | zone/zone | 0.94 | 허공·치우침 | 띠가 표적 위 공중과 표적 뒤쪽에 계속 있음 | v2·v3·v4 |
| 6 | `FX-25` | CMYK 파쇄 | circle/point | 0.89 | 허공 | 파편이 넓게 흩어진 뒤 큰 구체가 표적 위(높이 약 8)에 뜸 | v2·v3·v4 |
| 14 | `AS-10` | 공명 결정군 | circle/point | 1.1 | 허공 | 결정 조각이 표적 위(높이 약 5~10)에 계속 떠 있음 | v2·v3·v4 |
| 16 | `ARC-09` | 삼위 공명 · 프리즘 합창 | radial/point | 0.79 | 허공 | 소용돌이 3개가 공중에 떠서 표적 위에서 합쳐짐. 방사형(시전자 중심) 스킬 | v2·v3·v4 |
| 18 | `FX-21` | 보이드 티어 · 접힌 밤의 경계 | zone/zone | 1(없음) | 과대·하늘 | 어두운 큰 형체가 표적에서 하늘까지 뻗음(판정 반경 8) | v2·v3 |
| 23 | `ARC-08` | 블러드플레임 · 적월 절단 | circle/point | 1.14 | 하늘·안 보임 | 원반이 높이 약 15~17에서 옆으로 지나감(원본 좌표가 그 높이). 표적 높이에 닿지 않음 | v2·v3·v4 |
| 24 | `MC-01` | 디바인 네뷸라 | radial/point | 1.07 | 하늘 | 날개 형상이 표적 뒤 하늘에 계속 있음. 방사형 궁극기 | v2·v3·v4 |
| 26 | `MC-04` | 아케인 코덱스 | circle/point | 1.14 | 허공 | 책이 표적 위(높이 약 10)에 계속 떠 있음(의도일 수 있음) | v2·v3·v4 |
| 28 | `AC-02` | 이지스 래티스 | shield/self | 0.35 | 허공 | 게임 배율에서 돔 바닥 고리가 시전자 가슴 높이(약 4). 원본 중심 높이 +12 | v2·v3·v4 |
| 30 | `AS-04` | 성운의 축복 · 내려앉는 빛 | radial/point | 0.94 | 하늘 | 빛 입자가 표적 뒤 하늘에 약 2초 뒤부터 나타남. 방사형 궁극기(의도일 수 있음) | v2·v3·v4 |
| 34 | `INT-03` | 슈퍼노바 · 외피 파열형 | circle/point | 0.83 | 과대 | 판정 반경 5인데 약 3초에 외피가 반경 15 이상으로 퍼짐 | v2·v3·v4 |
| 40 | `SC-02` | 검기 폭풍 · 일곱 섬광 | circle/point | 1(없음) | 하늘·안 보임 | 하늘 쪽 가는 선만 1초가량 보임 | v2·v3 |
| 47 | `INT-08-P` | 디컨스트럭션 · 패널 산란형 | circle/point | 0.92 | 과대 | 패널이 넓고 높은 벽으로 조립됨(의도일 수 있음) | v2·v3·v4 |
| 48 | `FX-10-C` | 데이터 코어 · 큐브 수렴 결합형 | circle/point | 0.92 | 과대·허공 | 큐브가 표적 위에 몰린 뒤 경기장 전체로 흩어짐 | v2·v3·v4 |
| 49 | `FX-10-O` | 데이터 코어 · 원본 바이너리 큐브 | circle/point | 0.55 | 허공 | 게임 배율에서도 흰 구체가 표적 위(높이 약 8)에 뜸. 원본 높이 +16 | v2·v3·v4 |
| 53 | `FX-146` | 프리즘 나비 산란 | circle/point | 1.14 | 하늘 | 빛 덩어리가 표적 위(높이 약 10)에서 커짐 | v2·v3·v4 |
| 70 | `ARC-25` | 사건의 지평선 낫 | zone/zone | 0.73 | 허공 | 원반이 표적 위(높이 약 8)에 계속 떠 있음 | v2·v3·v4 |
| 120 | `GS-digital` | 연산붕괴 | circle/point | 1(없음) | 과대 | 약 3초부터 판정 반경(10) 전체가 흰색으로 꽉 차 적이 가려짐 | v2·v3 |
| 151 | `CH:emille` | 에밀레 맥놀이 | circle/beam | 1(없음) | 과대 | 큰 종 형상이 시전자를 계속 덮음(의도일 수 있음) | v2·v3 |
| 182 | `D:PROJ:lance` | 수평 관통 빔 | circle/point | 1(없음) | 방향 | 조준 3방향 모두 조준선과 어긋남. 원인: 시전마다 무작위 방향. 수정 PR #34 | v2·v3 |
| 195 | `C:F_PROJ:sing` | 특이점 블랙홀 | projectile/flight | 1(없음) | 과대 | 착탄 때 반경 12 이상의 큰 고리가 한 번 퍼짐 | v2·v3 |
| 199 | `C:SF_PROJ:prs` | 크로마 프리즘 | projectile/flight | 1(없음) | 과대 | 착탄 때 반경 12 이상의 큰 고리가 한 번 퍼짐 | v2·v3 |
| 200 | `C:SF_PROJ:eco` | 크로노 에코 | projectile/flight | 1(없음) | 과대 | 착탄 때 반경 12 이상의 큰 고리가 한 번 퍼짐 | v2·v3 |
| 201 | `C:SF_PROJ:mtr` | 유성 파쇄체 | projectile/flight | 1(없음) | 과대 | 착탄 때 반경 12 이상의 큰 고리가 한 번 퍼짐 | v2·v3 |

처리 제안:

| 묶음 | 대상 | 제안 | 상태 |
|---|---|---|---|
| A. 확정 결함 | `D:PROJ:lance` | 조준 방향 사용, 시전자에서 시작 | PR #34 |
| B. 높이 보정(기존 `__FX_ADJ.lift` 방식) | `AC-02`, `ARC-08`, `FX-10-O`, `FX-25`, `FX-146`, `ARC-25`, `AS-10`, `SC-02` | 본체를 표적 몸 높이로 내림. 원본 높이가 코드에 있는 것: `AC-02` +12, `FX-10-O` +16, `FX-25` +10, `ARC-08` 약 +15.5. 나머지는 수치 확인 필요 | **사용자 결정 대기** |
| C. 의도일 수 있는 공중 연출 | `MC-04`(책), `MC-01`·`AS-04`·`ARC-09`(방사형), `FX-06` | 그대로 둘지 내릴지 | **사용자 결정 대기** |
| D. 크기·가림 | `FX-21`, `INT-03`, `INT-08-P`, `FX-10-C`, `GS-digital`, `CH:emille`, 투사체 고리 4종 | 줄일지 그대로 둘지 | **사용자 결정 대기** |

기존 `__FX_ADJ` 보정이 있는 것의 현재 상태: `INT-03`(-14) 본체 높이는 정상, 외피 크기만 의심. `SC-03`(-7)·`FX-22`(-6)·`ARC-07`(-10) 정상.

## 6. 전체 판정표 (243행)

근거: v2 = 1시점·원본 크기, v3 = 6시점, v4 = 게임 배율 3시점.

| # | id | 이름 | 종류/형태 | 평점 | 판정 | 분류 | 메모 | 근거 |
|---|---|---|---|---|---|---|---|---|
| 0 | `FX-06` | 플랑크톤 해류 | zone/zone | 4 | 의심 | 허공·치우침 | 띠가 표적 위 공중과 표적 뒤쪽에 계속 있음 | v2·v3·v4 |
| 1 | `FX-13` | 발광 포자 | zone/zone | 4 | 정상 |  |  | v2·v4 |
| 2 | `FX-18` | 마나 토네이도 | zone/zone | 3 | 정상 |  |  | v2·v4 |
| 3 | `FX-29` | 무지개 비눗방울 | circle/point | 3 | 정상 |  |  | v2 |
| 4 | `FX-30` | 액체 지형 · 조석 분지 | zone/zone | 3 | 정상 |  | 영역이 시전자 발밑까지 닿음(영역 크기) | v2·v4 |
| 5 | `FX-12` | 솔라 스트라이크 · 항성 단두대 | circle/point | 3 | 정상 |  | 낙하 후 표적에 착탄(약 2~3초) | v2·v3·v4 |
| 6 | `FX-25` | CMYK 파쇄 | circle/point | 3 | 의심 | 허공 | 파편이 넓게 흩어진 뒤 큰 구체가 표적 위(높이 약 8)에 뜸 | v2·v3·v4 |
| 7 | `FX-10` | 데이터 코어 · 숫자 수렴형 | circle/point | 4 | 정상 |  |  | v2·v4 |
| 8 | `FX-17` | 육각 파동 지형 | zone/zone | 4 | 정상 |  |  | v2·v4 |
| 9 | `FX-08` | 여섯 봉인 · 나선 압박 | circle/point | 4 | 정상 |  |  | v2·v4 |
| 10 | `FX-09` | 크로마 보이드 | zone/zone | 3 | 정상 |  |  | v2·v4 |
| 11 | `SC-01` | 절대영점 붕괴 | circle/point | 3 | 정상 |  | 게임 배율에서 반경 약 8, 표적 중심 | v2·v3·v4 |
| 12 | `SC-04` | 천벌 운석군 | circle/point | 3 | 정상 |  |  | v2·v4 |
| 13 | `AS-02` | 빙정 관통 | circle/point | 3 | 정상 |  |  | v2 |
| 14 | `AS-10` | 공명 결정군 | circle/point | 3 | 의심 | 허공 | 결정 조각이 표적 위(높이 약 5~10)에 계속 떠 있음 | v2·v3·v4 |
| 15 | `ARC-04` | 심연 조수 보호막 | shield/self | 3 | 정상 |  |  | v2·v4 |
| 16 | `ARC-09` | 삼위 공명 · 프리즘 합창 | radial/point | 3 | 의심 | 허공 | 소용돌이 3개가 공중에 떠서 표적 위에서 합쳐짐. 방사형(시전자 중심) 스킬 | v2·v3·v4 |
| 17 | `FX-14` | 신성기하 결계 | zone/zone | 4 | 정상 |  |  | v2·v4 |
| 18 | `FX-21` | 보이드 티어 · 접힌 밤의 경계 | zone/zone | 3 | 의심 | 과대·하늘 | 어두운 큰 형체가 표적에서 하늘까지 뻗음(판정 반경 8) | v2·v3 |
| 19 | `FX-22` | 블랙홀 · 기울어진 강착관 | zone/zone | 3 | 정상 |  | 게임 배율에서 표적 머리 높이의 작은 원반 | v2·v3·v4 |
| 20 | `FX-34` | 자수정 낙뢰 · 수정맥의 역류 | circle/point | 3 | 정상 |  | 게임 배율에서 판정 반경과 비슷한 크기 | v2·v3·v4 |
| 21 | `ARC-02` | 크림슨 이중나선 | radial/point | 3 | 정상 |  |  | v2·v4 |
| 22 | `ARC-07` | 화염-서리 융합 · 극광의 충돌 | circle/point | 4 | 정상 |  | 꼬리가 위로 뻗지만 본체는 표적 몸 높이 | v2·v4 |
| 23 | `ARC-08` | 블러드플레임 · 적월 절단 | circle/point | 3 | 의심 | 하늘·안 보임 | 원반이 높이 약 15~17에서 옆으로 지나감(원본 좌표가 그 높이). 표적 높이에 닿지 않음 | v2·v3·v4 |
| 24 | `MC-01` | 디바인 네뷸라 | radial/point | 4 | 의심 | 하늘 | 날개 형상이 표적 뒤 하늘에 계속 있음. 방사형 궁극기 | v2·v3·v4 |
| 25 | `MC-02` | 에너지 실드 | shield/self | 3 | 정상 |  |  | v2·v4 |
| 26 | `MC-04` | 아케인 코덱스 | circle/point | 5 | 의심 | 허공 | 책이 표적 위(높이 약 10)에 계속 떠 있음(의도일 수 있음) | v2·v3·v4 |
| 27 | `AC-01` | 퀀텀 프랙처 · 명계의 압축함 | circle/point | 4 | 정상 |  |  | v2 |
| 28 | `AC-02` | 이지스 래티스 | shield/self | 3 | 의심 | 허공 | 게임 배율에서 돔 바닥 고리가 시전자 가슴 높이(약 4). 원본 중심 높이 +12 | v2·v3·v4 |
| 29 | `AS-03` | 흑조의 와류 · 침강하는 해류 | zone/zone | 4 | 정상 |  |  | v2·v4 |
| 30 | `AS-04` | 성운의 축복 · 내려앉는 빛 | radial/point | 4 | 의심 | 하늘 | 빛 입자가 표적 뒤 하늘에 약 2초 뒤부터 나타남. 방사형 궁극기(의도일 수 있음) | v2·v3·v4 |
| 31 | `AS-06` | 파이어스톰 · 잿불 용승 | zone/zone | 3 | 정상 |  |  | v2·v4 |
| 32 | `INT-01` | 양자 오버라이드 | zone/zone | 3 | 정상 |  |  | v2·v4 |
| 33 | `INT-02` | 애비설 레저넌스 | circle/point | 3 | 정상 |  | 게임 배율에서 구체가 표적 위에 얹힘(높이 약 4~14) | v2·v3·v4 |
| 34 | `INT-03` | 슈퍼노바 · 외피 파열형 | circle/point | 3 | 의심 | 과대 | 판정 반경 5인데 약 3초에 외피가 반경 15 이상으로 퍼짐 | v2·v3·v4 |
| 35 | `INT-04` | 에테리얼 팔랑크스 | zone/zone | 3 | 정상 |  |  | v2·v4 |
| 36 | `INT-05` | 비스커스 이클립스 | zone/zone | 3 | 정상 |  |  | v2·v4 |
| 37 | `INT-08` | 디컨스트럭션 · 큐브 격자형 | circle/point | 5 | 정상 |  |  | v2·v4 |
| 38 | `INT-10` | 앱솔루트 제로 프랙처 | circle/point | 3 | 정상 |  |  | v2·v4 |
| 39 | `SC-03` | 광자 집중 · 일점 폭축 | circle/point | 4 | 정상 |  | 흩어진 베기 뒤 표적에서 수렴(약 2.8초) | v2·v3·v4 |
| 40 | `SC-02` | 검기 폭풍 · 일곱 섬광 | circle/point | 3 | 의심 | 하늘·안 보임 | 하늘 쪽 가는 선만 1초가량 보임 | v2·v3 |
| 41 | `NV-03` | 독성 미아즈마 | zone/zone | 4 | 정상 |  |  | v2 |
| 42 | `NV-06` | 에테리얼 연꽃 · 월광 개화 | circle/point | 4 | 정상 |  | 꽃봉오리가 내려와 바닥에서 개화(약 3초) | v2·v3 |
| 43 | `NV-07` | 운석 잿불 폭풍 | circle/point | 3 | 정상 |  | 운석 낙하 중 | v2 |
| 44 | `V5-06` | 사이매틱스 · 공명의 정원 | zone/zone | 4 | 정상 |  | 영역이 시전자 발밑까지 닿음(영역 크기) | v2·v4 |
| 45 | `V5-03` | 메타볼 유기 분열 | circle/point | 3 | 정상 |  |  | v2 |
| 46 | `V5-05` | BZ 반응-확산 매질 | zone/zone | 3 | 정상 |  | 게임 배율에서 반경 약 5 | v2·v3·v4 |
| 47 | `INT-08-P` | 디컨스트럭션 · 패널 산란형 | circle/point | 3 | 의심 | 과대 | 패널이 넓고 높은 벽으로 조립됨(의도일 수 있음) | v2·v3·v4 |
| 48 | `FX-10-C` | 데이터 코어 · 큐브 수렴 결합형 | circle/point | 5 | 의심 | 과대·허공 | 큐브가 표적 위에 몰린 뒤 경기장 전체로 흩어짐 | v2·v3·v4 |
| 49 | `FX-10-O` | 데이터 코어 · 원본 바이너리 큐브 | circle/point | 3 | 의심 | 허공 | 게임 배율에서도 흰 구체가 표적 위(높이 약 8)에 뜸. 원본 높이 +16 | v2·v3·v4 |
| 50 | `INT-08-O` | 디컨스트럭션 · 최초 3D 패널 | zone/zone | 3 | 정상 |  |  | v2·v4 |
| 51 | `ARC-21` | 지각융기·용암균열 | circle/point | 4 | 정상 |  | 궁극기 판정 반경 15와 같은 크기 | v2·v3·v4 |
| 52 | `FX-101` | 진홍 장미 폭렬 | circle/point | 3 | 정상 |  |  | v2·v4 |
| 53 | `FX-146` | 프리즘 나비 산란 | circle/point | 4 | 의심 | 하늘 | 빛 덩어리가 표적 위(높이 약 10)에서 커짐 | v2·v3·v4 |
| 54 | `FX-140` | 신성 연꽃 강타 | circle/point | 4 | 정상 |  |  | v2·v4 |
| 55 | `FX-150` | 궤도 십자 폭격 | circle/point | 4 | 정상 |  |  | v2 |
| 56 | `FX-125` | 황금비 프랙탈 폭발 | circle/point | 4 | 정상 |  | 표적 위에서 시작해 판정 반경 15 전체로 폭발(궁극기) | v2·v3·v4 |
| 57 | `FX-141` | 잠식하는 공허핵 | zone/zone | 4 | 정상 |  |  | v2·v4 |
| 58 | `NX-05` | 빙백 연화 파쇄 | circle/point | 4 | 정상 |  |  | v2·v4 |
| 59 | `FX-126` | 시간 역행의 와류 | zone/zone | 3 | 정상 |  |  | v2·v4 |
| 60 | `FX-142` | 점화 초승달 와류 | radial/point | 3 | 정상 |  |  | v2·v4 |
| 61 | `FX-152` | 시공 단절 와류 | zone/zone | 4 | 정상 |  |  | v2·v4 |
| 62 | `FX-155` | 나비 탄막 | circle/point | 3 | 정상 |  |  | v2·v4 |
| 63 | `FX-157` | 프리즘 나선 에너지파 | radial/point | 4 | 정상 |  |  | v2·v4 |
| 64 | `NX-08` | 육각 빙결 성문 | zone/zone | 3 | 정상 |  |  | v2 |
| 65 | `NX-10` | 심연 와류 | zone/zone | 3 | 정상 |  |  | v2·v4 |
| 66 | `ARC-22` | 차원 균열 | zone/zone | 3 | 정상 |  |  | v2 |
| 67 | `ARC-24` | 심연 연꽃 포식 | zone/zone | 3 | 정상 |  |  | v2 |
| 68 | `ARC-27` | 용암 개화 | zone/zone | 3 | 정상 |  |  | v2·v4 |
| 69 | `FX-130` | 침묵의 핵폭·버섯구름 | circle/point | 3 | 정상 |  |  | v2·v4 |
| 70 | `ARC-25` | 사건의 지평선 낫 | zone/zone | 3 | 의심 | 허공 | 원반이 표적 위(높이 약 8)에 계속 떠 있음 | v2·v3·v4 |
| 71 | `FX-108` | 마법공학 봉인 참격 | circle/point | 3 | 정상 |  |  | v2·v4 |
| 72 | `WTR-1` | 워터 볼텍스 | zone/zone | 4 | 정상 |  |  | v2·v4 |
| 73 | `ARC-32` | 차원 거울 파쇄 | circle/point | 3 | 정상 |  |  | v2·v4 |
| 74 | `MYTH-01` | 청연 · 언령신룡 강림 | circle/point | 5 | 정상 |  | 용이 약 6초에 표적에 내려앉음(판정 5.25초) | v2·v3·v4 |
| 75 | `FX-121` | 디지털 글리치 · 양자 붕괴 | circle/point | 4 | 정상 |  |  | v2 |
| 76 | `CURSE-01` | 무간 · 흑왕의 장송 | circle/point | 4 | 정상 |  |  | v2·v4 |
| 77 | `GS-aurora9` | 극광폭발 | radial/point | 3 | 정상 |  | 희미함 | v2 |
| 78 | `GS-vortexring` | 와류환 | circle/point | 4 | 정상 |  | 고리가 표적 바닥에서 위로 올라감. 희미함 | v2·v3 |
| 79 | `GS-sedov` | 공중 가스폭연 | circle/point | 4 | 정상 |  |  | v2 |
| 80 | `GS-miura` | 미우라전개 | shield/self | 3 | 정상 |  |  | v2 |
| 81 | `GS-requiem` | 천구장송 | circle/point | 5 | 정상 |  |  | v2 |
| 82 | `GS-nuke` | 최후통첩 | circle/point | 4 | 정상 |  | 낙하 후 표적 착탄(약 1.7~2.9초) | v2·v3 |
| 83 | `GS-sonic` | 음속파단 | circle/point | 4 | 정상 |  |  | v2 |
| 84 | `GS-helix` | 오행천파 | circle/point | 4 | 정상 |  | 낙하 후 표적 착탄(약 5초) | v2·v3 |
| 85 | `GS-vacuum` | 진공파열 | circle/point | 3 | 정상 |  |  | v2 |
| 86 | `GS-thermo` | 항성점화 | circle/point | 4 | 정상 |  |  | v2 |
| 87 | `GS-mirv` | 묵시의비 | circle/point | 4 | 정상 |  | 낙하 후 표적 착탄(약 5초) | v2·v3 |
| 88 | `GS-aegis` | 천개방벽 | shield/self | 4 | 정상 |  |  | v2 |
| 89 | `GS-rod` | 천주강림 | circle/point | 4 | 정상 |  |  | v2 |
| 90 | `GS-cannon` | 철갑작렬 | circle/point | 3 | 정상 |  |  | v2 |
| 91 | `GS-dynamite` | 도화선 | circle/point | 3 | 정상 |  | 약 2.1초에 표적에서 폭발 | v2·v3 |
| 92 | `GS-shuriken` | 수리검연격 | circle/point | 3 | 정상 |  | 비행 중 | v2 |
| 93 | `GS-talisman` | 부적봉인 | circle/point | 4 | 정상 |  |  | v2 |
| 94 | `GS-bell` | 범종파문 | circle/point | 4 | 정상 |  |  | v2 |
| 95 | `GS-fan` | 선풍참 | circle/point | 4 | 정상 |  |  | v2 |
| 96 | `GS-frost` | 빙결탄 | circle/point | 3 | 정상 |  | 측면 시점에서는 희미함 | v2 |
| 97 | `GS-arsenal` | 기갑전개 | circle/point | 4 | 정상 |  |  | v2 |
| 98 | `GS-railgun` | 전자기포 | circle/point | 3 | 정상 |  |  | v2 |
| 99 | `GS-nanite` | 나노해체 | circle/point | 4 | 정상 |  |  | v2 |
| 100 | `GS-tokamak` | 핵융합로 | circle/point | 4 | 정상 |  |  | v2 |
| 101 | `GS-web` | 결계망 | circle/point | 3 | 정상 |  |  | v2 |
| 102 | `GS-lance` | 관통포 | circle/point | 4 | 정상 |  |  | v2 |
| 103 | `GS-hammer` | 뇌추 | circle/point | 3 | 정상 |  |  | v2 |
| 104 | `GS-meteor` | 유성우 | circle/point | 4 | 정상 |  |  | v2 |
| 105 | `GS-tsunami` | 해일 | circle/point | 4 | 정상 |  |  | v2 |
| 106 | `GS-horizon` | 사건지평 | circle/point | 4 | 정상 |  |  | v2 |
| 107 | `GS-ferro` | 자성첨탑 | circle/point | 3 | 정상 |  |  | v2 |
| 108 | `GS-murmur` | 군무 | circle/point | 3 | 정상 |  |  | v2 |
| 109 | `GS-bloom` | 몽화만개 | radial/point | 5 | 정상 |  |  | v2 |
| 110 | `GS-aurora` | 극광강림 | radial/point | 4 | 정상 |  |  | v2 |
| 111 | `GS-fractal` | 무한전개 | circle/point | 4 | 정상 |  | 덩어리가 표적 머리 위, 바닥 고리는 표적 위치 | v2 |
| 112 | `GS-abyss` | 심해명멸 | circle/point | 4 | 정상 |  |  | v2 |
| 113 | `GS-dune` | 사구성음 | circle/point | 4 | 정상 |  |  | v2 |
| 114 | `GS-chrono` | 시간층리 | circle/point | 3 | 정상 |  |  | v2 |
| 115 | `GS-mycel` | 포자군락 | circle/point | 3 | 정상 |  |  | v2 |
| 116 | `GS-tempest` | 뇌옥강림 | circle/point | 4 | 정상 |  |  | v2 |
| 117 | `GS-silk` | 천잠사 | circle/point | 3 | 정상 |  |  | v2 |
| 118 | `GS-rift` | 분열지각 | radial/point | 5 | 정상 |  |  | v2 |
| 119 | `GS-judge` | 뇌정극형 | circle/point | 4 | 정상 |  |  | v2 |
| 120 | `GS-digital` | 연산붕괴 | circle/point | 4 | 의심 | 과대 | 약 3초부터 판정 반경(10) 전체가 흰색으로 꽉 차 적이 가려짐 | v2·v3 |
| 121 | `GS-polytope` | 다면압궤 | circle/point | 5 | 정상 |  | 구체가 큼 | v2 |
| 122 | `CH:prism` | 프리즘 헬릭스 | beam/beam | 5 | 정상 |  |  | v2 |
| 123 | `CH:rupture` | 럽처 드라이브 | beam/beam | 5 | 정상 |  |  | v2 |
| 124 | `CH:void` | 보이드 오키드 | beam/beam | 4 | 정상 |  |  | v2 |
| 125 | `CH:glacier` | 글레이셔 랜스 | beam/beam | 4 | 정상 |  |  | v2 |
| 126 | `CH:solar` | 솔라 포지 | beam/beam | 4 | 정상 |  |  | v2 |
| 127 | `CH:aurora` | 오로라 타이드 | beam/beam | 4 | 정상 |  |  | v2 |
| 128 | `CH:storm` | 스톰 필라멘트 | beam/beam | 4 | 정상 |  |  | v2 |
| 129 | `CH:kintsugi` | 킨츠기 리프트 | beam/beam | 4 | 정상 |  |  | v2 |
| 130 | `CH:coral` | 코랄 코러스 | beam/beam | 4 | 정상 |  |  | v2 |
| 131 | `CH:tidal` | 타이달 크라운 | beam/beam | 5 | 정상 |  |  | v2 |
| 132 | `CH:glitch` | 크로매틱 에러 | beam/beam | 4 | 정상 |  | 측면 시점에서는 빔이 진행 중 | v2 |
| 133 | `CH:collapse` | 널 캐스케이드 | beam/beam | 4 | 정상 |  | 측면 시점에서는 빔이 진행 중 | v2 |
| 134 | `CH:comic` | 패널 브레이커 | beam/beam | 4 | 정상 |  |  | v2 |
| 135 | `CH:jade` | 비취 묵광 | beam/beam | 4 | 정상 |  |  | v2 |
| 136 | `CH:dokkaebi` | 도깨비불 | beam/beam | 3 | 정상 |  |  | v2 |
| 137 | `CH:matrix` | 매트릭스 캐스케이드 | circle/beam | 4 | 정상 |  | 끝 구체가 표적을 조금 지나침 | v2 |
| 138 | `CH:cathedral` | 성당의 창 | beam/beam | 3 | 정상 |  | 측면 시점에서는 빔이 진행 중 | v2 |
| 139 | `CH:ferro` | 자성 송곳니 | circle/beam | 4 | 정상 |  | 측면 시점에서는 빔이 진행 중 | v2 |
| 140 | `CH:seraph` | 세라프 강림 | beam/beam | 3 | 정상 |  | 측면 시점에서는 빔이 진행 중 | v2 |
| 141 | `CH:mycelium` | 균사 저주 | circle/beam | 3 | 정상 |  | 측면 시점에서는 빔이 진행 중 | v2 |
| 142 | `CH:chronos` | 시간의 전단 | beam/beam | 3 | 정상 |  | 측면 시점에서는 빔이 진행 중 | v2 |
| 143 | `CH:loom` | 중력 직조 | beam/beam | 4 | 정상 |  | 측면 시점에서는 빔이 진행 중 | v2 |
| 144 | `CH:leviathan` | 레비아탄의 항적 | circle/beam | 4 | 정상 |  | 진행 중 | v2 |
| 145 | `CH:requiem` | 크림슨 레퀴엠 | circle/beam | 3 | 정상 |  | 진행 중 | v2 |
| 146 | `CH:prominence` | 태양 홍염 | circle/beam | 3 | 정상 |  | 진행 중 | v2 |
| 147 | `CH:manta` | 심해의 망토 | circle/beam | 4 | 정상 |  | 진행 중 | v2 |
| 148 | `CH:ssitgim` | 씻김 길가르기 | circle/beam | 3 | 정상 |  |  | v2 |
| 149 | `CH:obang` | 오방 먹 분리 | circle/beam | 4 | 정상 |  | 시전자에서 출발해 약 4.5초에 표적 도달. 희미함 | v2·v3 |
| 150 | `CH:chladni` | 클라드니 구 | circle/beam | 4 | 정상 |  |  | v2 |
| 151 | `CH:emille` | 에밀레 맥놀이 | circle/beam | 4 | 의심 | 과대 | 큰 종 형상이 시전자를 계속 덮음(의도일 수 있음) | v2·v3 |
| 152 | `CH:tomo` | 단층 촬영 | circle/beam | 4 | 정상 |  | 고리가 시전자에서 표적으로 이동(약 4.5초 도달) | v2·v3 |
| 153 | `CH:lazy` | 팬터그래프 케이지 | circle/beam | 3 | 정상 |  |  | v2 |
| 154 | `CH:brimstone` | 인페르노 헬파이어 | circle/beam | 4 | 정상 |  | 진행 중 | v2 |
| 155 | `CH:voltspear` | 블루썬더볼트 | beam/beam | 3 | 정상 |  |  | v2 |
| 156 | `CH:crane` | 종이학 편대 | circle/beam | 4 | 정상 |  |  | v2 |
| 157 | `CH:relay` | 거울 릴레이 | beam/beam | 3 | 정상 |  |  | v2 |
| 158 | `CH:bubble` | 비눗방울 올가미 | circle/beam | 3 | 정상 |  |  | v2 |
| 159 | `CH:spiral` | 와류 진주 | circle/beam | 5 | 정상 |  | 진행 중 | v2 |
| 160 | `CH:galaxy` | 나선 성운 | circle/beam | 4 | 정상 |  |  | v2 |
| 161 | `CH:twin` | 쌍나선 합일 | circle/beam | 4 | 정상 |  |  | v2 |
| 162 | `CH:opal` | 오팔 박막 | circle/beam | 4 | 정상 |  |  | v2 |
| 163 | `CH:marey` | 마레 잔상 | circle/beam | 4 | 정상 |  |  | v2 |
| 164 | `CH:gaze` | 명부의 응시 | circle/beam | 4 | 정상 |  |  | v2 |
| 165 | `FX-04` | 액체 화염 · 용융 초승달 | circle/point | 3 | 정상 |  | 게임 배율에서 표적 근처의 작은 초승달 | v2·v3·v4 |
| 166 | `V5-01` | 타이포 임팩트 | shield/self | 3 | 정상 |  | 글자 효과, 작음 | v2 |
| 167 | `INT-03-G` | 슈퍼노바 · 금빛 잔재형 | circle/point | 3 | 정상 |  | 게임 배율에서 반경 약 10. 희미함 | v2·v3·v4 |
| 168 | `FX-158` | 나선 에너지 랜스 | beam/beam | 3 | 정상 |  |  | v2 |
| 169 | `FX-88` | 진홍 핵 절단 | circle/point | 3 | 정상 |  |  | v2·v4 |
| 170 | `C:FB_STRUCT:myco` | 발광 균사 결계 | deploy/structure | 3 | 정상 |  |  | v2 |
| 171 | `D:STRUCT:obelisk` | 오벨리스크 | deploy/structure | 3 | 정상 |  | 게임 배율(×2.5)에서 표적 위치에 구조물 확인 | v2·v3·v4 |
| 172 | `D:STRUCT:fountain` | 마나 분수 | deploy/structure | 3 | 정상 |  |  | v2·v4 |
| 173 | `D:STRUCT:ward` | 룬 결계 | deploy/structure | 3 | 정상 |  |  | v2·v4 |
| 174 | `D:STRUCT:tree` | 달빛 나무 | deploy/structure | 3 | 정상 |  | 게임 배율(×2.5)에서 표적 위치에 구조물 확인 | v2·v3·v4 |
| 175 | `D:STRUCT:belfry` | 공명 종루 | deploy/structure | 3 | 정상 |  |  | v2·v4 |
| 176 | `D:STRUCT:altar` | 태양 제단 | deploy/structure | 3 | 정상 |  |  | v2·v4 |
| 177 | `D:STRUCT:lunar` | 월륜 첨탑 | deploy/structure | 3 | 정상 |  | 게임 배율(×2.5)에서 표적 위치에 구조물 확인 | v2·v3·v4 |
| 178 | `D:STRUCT:sanctum` | 암흑 성소 | deploy/structure | 3 | 정상 |  |  | v2·v4 |
| 179 | `D:STRUCT:spire` | 수정 첨탑 | deploy/structure | 3 | 정상 |  |  | v2·v4 |
| 180 | `D:STRUCT:pylon` | 뇌전 첨주 | deploy/structure | 3 | 정상 |  | 게임 배율(×2.5)에서 표적 위치에 구조물 확인 | v2·v3·v4 |
| 181 | `D:STRUCT:portal` | 포탈 | deploy/structure | 3 | 정상 |  |  | v2·v4 |
| 182 | `D:PROJ:lance` | 수평 관통 빔 | circle/point | 3 | 의심 | 방향 | 조준 3방향 모두 조준선과 어긋남. 원인: 시전마다 무작위 방향. 수정 PR #34 | v2·v3 |
| 183 | `D:ULT:inkfall` | 먹빛 강림 | circle/point | 3 | 정상 |  | 약 4.6초에 표적에서 발광(판정 4.4초). 그 전에는 하늘의 작은 점만 보임 | v2·v3·v4 |
| 184 | `D:ULT:issen` | 일섬 | circle/point | 3 | 정상 |  |  | v2 |
| 185 | `D:ULT:crystalcage` | 수정뇌옥 | circle/point | 3 | 정상 |  |  | v2 |
| 186 | `D:ULT:waltz` | 선회 무곡 | shield/self | 3 | 정상 |  |  | v2 |
| 187 | `D:ULT:agwisasal` | 아귀사슬 | circle/point | 4 | 정상 |  |  | v2 |
| 188 | `D:ULT:mugeonbu` | 묵언부 | circle/point | 3 | 정상 |  |  | v2 |
| 189 | `C:F_PROJ:dat` | 사이버 | projectile/flight | 3 | 정상 |  |  | v2 |
| 190 | `C:F_PROJ:irn` | 쇠창 | projectile/flight | 3 | 정상 |  |  | v2 |
| 191 | `C:F_PROJ:mtx` | 매트릭스 | projectile/flight | 3 | 정상 |  |  | v2 |
| 192 | `C:F_PROJ:gho` | 유령 | projectile/flight | 3 | 정상 |  | 비행 중 | v2 |
| 193 | `C:F_PROJ:qnt` | 양자 | projectile/flight | 3 | 정상 |  | 비행 중 | v2 |
| 194 | `C:F_PROJ:lqm` | 리퀴드메탈 | projectile/flight | 3 | 정상 |  | 비행 중 | v2 |
| 195 | `C:F_PROJ:sing` | 특이점 블랙홀 | projectile/flight | 3 | 의심 | 과대 | 착탄 때 반경 12 이상의 큰 고리가 한 번 퍼짐 | v2·v3 |
| 196 | `C:F_PROJ:memo` | 메멘토 에코 | projectile/flight | 3 | 정상 |  | 비행 중 | v2 |
| 197 | `C:F_PROJ:frost` | 서리 심장 | projectile/flight | 3 | 정상 |  | 비행 중 | v2 |
| 198 | `C:F_PROJ:meteor` | 유성탄 | projectile/flight | 3 | 정상 |  | 비행 중 | v2 |
| 199 | `C:SF_PROJ:prs` | 크로마 프리즘 | projectile/flight | 3 | 의심 | 과대 | 착탄 때 반경 12 이상의 큰 고리가 한 번 퍼짐 | v2·v3 |
| 200 | `C:SF_PROJ:eco` | 크로노 에코 | projectile/flight | 3 | 의심 | 과대 | 착탄 때 반경 12 이상의 큰 고리가 한 번 퍼짐 | v2·v3 |
| 201 | `C:SF_PROJ:mtr` | 유성 파쇄체 | projectile/flight | 3 | 의심 | 과대 | 착탄 때 반경 12 이상의 큰 고리가 한 번 퍼짐 | v2·v3 |
| 202 | `C:FB_PROJ:ori` | 종이학(오리가미) | projectile/flight | 4 | 정상 |  | 비행 중 | v2 |
| 203 | `C:FB_PROJ:bel` | 공명 범종 | projectile/flight | 3 | 정상 |  | 비행 중 | v2 |
| 204 | `C:F_STRUCT:bismuth` | 비스무트 결정 | deploy/structure | 4 | 정상 |  |  | v2 |
| 205 | `C:F_STRUCT:tectonic` | 지각 융기(그을음) · C | circle/point | 4 | 정상 |  |  | v2 |
| 206 | `C:F_STRUCT:talisman` | 음양 부적 관문 | deploy/structure | 4 | 정상 |  |  | v2 |
| 207 | `C:F_STRUCT:chain` | 진홍 사슬 결계 | deploy/zone | 3 | 정상 |  |  | v2 |
| 208 | `C:F_STRUCT:gateway` | 양자 게이트웨이 | deploy/structure | 3 | 정상 |  |  | v2 |
| 209 | `C:F_STRUCT:icewall` | 극저온 빙벽 | deploy/structure | 3 | 정상 |  |  | v2 |
| 210 | `C:F_STRUCT:turret` | 이지스 포탑 | deploy/structure | 4 | 정상 |  |  | v2 |
| 211 | `C:F_STRUCT:siphon` | 특이점 사이폰 | deploy/structure | 4 | 정상 |  |  | v2 |
| 212 | `C:SF_STRUCT:pct` | 플라즈마 격리로 | deploy/structure | 4 | 정상 |  |  | v2 |
| 213 | `C:SF_STRUCT:chr` | 시간 조절 장치 | deploy/structure | 3 | 정상 |  |  | v2 |
| 214 | `C:SF_STRUCT:nfn` | 나노 조립 노드 | deploy/structure | 3 | 정상 |  |  | v2 |
| 215 | `C:SF_STRUCT:snt` | 자율 감시 포탑 | deploy/structure | 3 | 정상 |  |  | v2 |
| 216 | `C:SF_STRUCT:hcb` | 홀로그램 지휘 비콘 | deploy/structure | 4 | 정상 |  | 구조물이 높음 | v2 |
| 217 | `C:SF_STRUCT:ora` | 궤도 중계 첨탑 | deploy/structure | 3 | 정상 |  | 탑이 화면 위로 벗어날 만큼 높음 | v2 |
| 218 | `C:SF_STRUCT:shd` | 위상 방어막 | deploy/structure | 4 | 정상 |  |  | v2 |
| 219 | `C:SF_STRUCT:tsl` | 테슬라 아크 파일런 | deploy/structure | 4 | 정상 |  |  | v2 |
| 220 | `C:SF_STRUCT:obl` | 궤도 타격 비콘 | deploy/structure | 3 | 정상 |  |  | v2 |
| 221 | `C:SF_STRUCT:msd` | 매스 드라이버 | deploy/structure | 4 | 정상 |  |  | v2 |
| 222 | `C:SF_STRUCT:hlx` | 헬륨-3 채굴기 | deploy/structure | 4 | 정상 |  |  | v2 |
| 223 | `C:FB_STRUCT:pagoda` | 천공 석탑 | deploy/structure | 3 | 정상 |  |  | v2 |
| 224 | `C:FB_STRUCT:astro` | 천구의 | deploy/structure | 3 | 정상 |  |  | v2 |
| 225 | `C:FB_STRUCT:loom` | 운명의 베틀 | deploy/structure | 4 | 정상 |  |  | v2 |
| 226 | `C:FB_STRUCT:organ` | 수정 공명 오르간 | deploy/structure | 3 | 정상 |  |  | v2 |
| 227 | `C:EXT_STRUCT:reactor` | 플라스마 발전소 | deploy/structure | 4 | 정상 |  |  | v2 |
| 228 | `C:EXT_STRUCT:graphene` | 그래핀 방벽 | deploy/structure | 5 | 정상 |  |  | v2 |
| 229 | `C:EXT_STRUCT:hologram` | 홀로그램 송출기 | deploy/structure | 4 | 정상 |  |  | v2 |
| 230 | `C:EXT_STRUCT:chiral` | 카이랄 결정군 | deploy/structure | 4 | 정상 |  |  | v2 |
| 231 | `C:EXT_STRUCT:anchor` | 중력 앵커 | deploy/structure | 3 | 정상 |  |  | v2 |
| 232 | `C:EXT_STRUCT:rift` | 시공 균열 | deploy/structure | 3 | 정상 |  |  | v2 |
| 233 | `C:EXT_STRUCT:bio` | 바이오 콜로니 | deploy/structure | 3 | 정상 |  |  | v2 |
| 234 | `C:EXT_STRUCT:beacon` | 펄서 비콘 | deploy/structure | 3 | 정상 |  |  | v2 |
| 235 | `C:EXT_STRUCT:auroraCurtain` | 오로라 커튼 | shield/self | 4 | 정상 |  |  | v2 |
| 236 | `C:EXT_STRUCT:auroraAltar` | 오로라 제단 | shield/self | 5 | 정상 |  |  | v2 |
| 237 | `C:EXT_STRUCT:organ` | 공명 오르간 | deploy/structure | 3 | 정상 |  |  | v2 |
| 238 | `D:PROJ:chain` | 연쇄 뇌창 | chain/flight | 4 | 정상 |  | 연쇄가 옆 적 쪽으로 이동 | v2 |
| 239 | `C:FB_PROJ:koi` | 유수 잉어 | projectile/flight | 4 | 정상 |  | 비행 중 | v2 |
| 240 | `D:ULT:zenith` | 백일염천 | circle/point | 4 | 정상 |  |  | v2 |
| 241 | `D:PROJ:fissure` | 지열 균열 | beam/beam | 3 | 정상 |  |  | v2 |
| 242 | `D:ULT:upheaval` | 대지 융기 | circle/point | 5 | 정상 |  |  | v2 |
