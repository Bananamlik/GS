# 평점 3 이상 스킬 효과·피해·상태이상 점검

기록: 2026-10-06 21:47 KST. 대상: `GA_SKILL_LIB` 중 평점 3 이상 243개 (기본 항목 값. 크기 변형은 같은 상태이상을 가짐). 기준 main `7bcf549`(md5 `a1129562…`). 적용 코드 PR #21 (`window.GA_SKILL_THEME`).

## 요약

| 항목 | 결과 |
|---|---|
| 형태·사거리·쿨·준비 | 243/243 정의됨 |
| 피해 | 225/243. 피해 없는 18개는 실드·방벽·관문(설계상) |
| 피해 값 | 등급·크기별 공식(예: 기술 68/75/83, 궁극 240~260). 스킬 고유 차등 없음 |
| 상태이상 (점검 전) | 있음 107개, 없음 136개. stun/root/silence는 기본 규칙(`STATUS_RULES.forSkill`) 4개뿐 |
| 이번 추가 (PR #21) | 21개 (상태 없던 19개 + 기존 상태에 CC·burn 덧붙인 2개: ARC-21, D:ULT:agwisasal). 이름·시각이 상태를 뜻하는 것만. 기존 값은 바꾸지 않음 |
| 속성(원소) 체계 | 없음. 이번 범위 아님 |
| 승인 | `approved:true` 43개(설치물), 나머지 200개 제안값 |

## 매핑 규칙

| 주제 | 상태 | 수치 근거 |
|---|---|---|
| 불·잿불·태양·용암 | burn 3 (0.25초마다 2, 약 24) | 기존 burn 스킬과 같은 값 |
| 얼음·시간 | slow 3 (이동 ×0.65) | 기존 slow 값 |
| 번개·전자기 | expose 3 (받는 피해 ×1.25) | 기존 expose 값 |
| 감옥·그물·올가미·사슬·실 | root 0.5~0.8 | FX-30 root 0.7 기준 |
| 봉인·묵언 | silence 0.8~1.2 | ARC-01 silence 1.2 기준 |
| 궤도 낙하 충격 | stun 0.4 | ARC-21 stun 0.4 기준 |
| 독·저주 | curse 2 (만료 시 90) | 기존 curse 값 |

CC는 기존 규칙을 따른다: 정예 ×0.7, 보스 ×0.4, 8초 안 연속 CC 감쇠, 같은 시전은 대상별 1회.

## 검증 (PR #21)

- Node vm으로 `GA_VFX_QA`·`GA_SIM`·`GA_DATA`·`GA_SKILL_LIB` 블록 실행, 767 변형 전후 비교: 바뀐 것은 21개(44 객체)뿐, 나머지 756 변형 시험 피해 동일.
- 바뀐 변형 모두 `validateSkill`·`validSkill` 통과, 시전 수락, 2회 결정적, 적에게 상태 적용 확인.
- 시험장 피해(6초, 미니언 3): NV-07:M 75→105, CH:dokkaebi 68→90, CH:mycelium 68→158, D:STRUCT:altar 243→333, D:STRUCT:pylon 110→132.
- 실제 플레이 밸런스·상태 아이콘·청감은 **UNVERIFIED**.

## 남은 결정

1. 오로라 계열 burn(CH:aurora, GS-aurora, GS-aurora9, AS-04) 유지 여부.
2. CSV `gs-skill-lib_v7`의 `상태이상` 열은 갱신 안 함 → 21개 런타임과 다름. 새 버전 CSV(v8)로 갱신할지.
3. 스킬별 피해 차등, 속성 체계.

## 전체 목록 (평점 3 이상 243개)

| id | 이름 | 평점 | 등급 | 형태 | 피해 | 반경 | 쿨 | 상태이상(점검 전) | 조치 |
|---|---|---|---|---|---|---|---|---|---|
| `FX-06` | 플랑크톤 해류 | 4 | ult | zone | 45 | 15 | 0 | — |  |
| `FX-13` | 발광 포자 | 4 | skill | zone | 20 | 8 | 9 | — |  |
| `FX-18` | 마나 토네이도 | 3 | skill | zone | 20 | 8 | 9 | knock 10 |  |
| `FX-29` | 무지개 비눗방울 | 3 | skill | circle | 75 | 8 | 6 | — |  |
| `FX-30` | 액체 지형 · 조석 분지 | 3 | skill | zone | 20 | 11 | 9 | slow 2, root 0.7 |  |
| `FX-12` | 솔라 스트라이크 · 항성 단두대 | 3 | skill | circle | 83 | 11 | 8 | burn 3 |  |
| `FX-25` | CMYK 파쇄 | 3 | skill | circle | 75 | 8 | 6 | — |  |
| `FX-10` | 데이터 코어 · 숫자 수렴형 | 4 | skill | circle | 83 | 11 | 8 | — |  |
| `FX-17` | 육각 파동 지형 | 4 | ult | zone | 45 | 15 | 0 | knock 10 |  |
| `FX-08` | 여섯 봉인 · 나선 압박 | 4 | skill | circle | 75 | 8 | 6 | — | **추가** silence 1 |
| `FX-09` | 크로마 보이드 | 3 | skill | zone | 20 | 11 | 9 | — |  |
| `SC-01` | 절대영점 붕괴 | 3 | skill | circle | 83 | 11 | 8 | slow 3 |  |
| `SC-04` | 천벌 운석군 | 3 | skill | circle | 83 | 11 | 8 | — |  |
| `AS-02` | 빙정 관통 | 3 | basic | circle | 40 | 5 | 1.4 | slow 3 |  |
| `AS-10` | 공명 결정군 | 3 | skill | circle | 83 | 11 | 8 | — |  |
| `ARC-04` | 심연 조수 보호막 | 3 | guard | shield | — | — | 10 | shield 120 |  |
| `ARC-09` | 삼위 공명 · 프리즘 합창 | 3 | skill | radial | 83 | 11 | 8 | — |  |
| `FX-14` | 신성기하 결계 | 4 | skill | zone | 20 | 11 | 9 | — |  |
| `FX-21` | 보이드 티어 · 접힌 밤의 경계 | 3 | skill | zone | 20 | 8 | 9 | — |  |
| `FX-22` | 블랙홀 · 기울어진 강착관 | 3 | skill | zone | 20 | 11 | 9 | knock 12 |  |
| `FX-34` | 자수정 낙뢰 · 수정맥의 역류 | 3 | skill | circle | 83 | 11 | 8 | expose 3 |  |
| `ARC-02` | 크림슨 이중나선 | 3 | skill | radial | 75 | 8 | 6 | — |  |
| `ARC-07` | 화염-서리 융합 · 극광의 충돌 | 4 | skill | circle | 75 | 8 | 6 | burn 3 |  |
| `ARC-08` | 블러드플레임 · 적월 절단 | 3 | skill | circle | 75 | 8 | 6 | burn 3 |  |
| `MC-01` | 디바인 네뷸라 | 4 | ult | radial | 245 | 15 | 0 | — |  |
| `MC-02` | 에너지 실드 | 3 | guard | shield | — | — | 10 | shield 120 |  |
| `MC-04` | 아케인 코덱스 | 5 | skill | circle | 75 | 8 | 6 | — |  |
| `AC-01` | 퀀텀 프랙처 · 명계의 압축함 | 4 | skill | circle | 68 | 5 | 6 | expose 3 |  |
| `AC-02` | 이지스 래티스 | 3 | guard | shield | — | — | 10 | shield 120 |  |
| `AS-03` | 흑조의 와류 · 침강하는 해류 | 4 | ult | zone | 45 | 15 | 0 | slow 2 |  |
| `AS-04` | 성운의 축복 · 내려앉는 빛 | 4 | ult | radial | 245 | 15 | 0 | burn 3 | 검토 후보: 성운 축복인데 burn |
| `AS-06` | 파이어스톰 · 잿불 용승 | 3 | skill | zone | 20 | 11 | 9 | burn 3 |  |
| `INT-01` | 양자 오버라이드 | 3 | skill | zone | 20 | 11 | 9 | — |  |
| `INT-02` | 애비설 레저넌스 | 3 | skill | circle | 83 | 11 | 8 | — |  |
| `INT-03` | 슈퍼노바 · 외피 파열형 | 3 | basic | circle | 40 | 5 | 1.4 | burn 3 |  |
| `INT-04` | 에테리얼 팔랑크스 | 3 | skill | zone | 20 | 11 | 9 | — |  |
| `INT-05` | 비스커스 이클립스 | 3 | skill | zone | 20 | 11 | 9 | knock 12 |  |
| `INT-08` | 디컨스트럭션 · 큐브 격자형 | 5 | skill | circle | 83 | 11 | 8 | — |  |
| `INT-10` | 앱솔루트 제로 프랙처 | 3 | skill | circle | 83 | 11 | 8 | slow 3 |  |
| `SC-03` | 광자 집중 · 일점 폭축 | 4 | skill | circle | 75 | 8 | 6 | — |  |
| `SC-02` | 검기 폭풍 · 일곱 섬광 | 3 | skill | circle | 68 | 5 | 6 | — |  |
| `NV-03` | 독성 미아즈마 | 4 | skill | zone | 20 | 11 | 9 | — | **추가** curse 2 |
| `NV-06` | 에테리얼 연꽃 · 월광 개화 | 4 | skill | circle | 83 | 11 | 8 | — |  |
| `NV-07` | 운석 잿불 폭풍 | 3 | skill | circle | 83 | 11 | 8 | — | **추가** burn 3 |
| `V5-06` | 사이매틱스 · 공명의 정원 | 4 | ult | zone | 45 | 15 | 0 | knock 10 |  |
| `V5-03` | 메타볼 유기 분열 | 3 | skill | circle | 75 | 8 | 6 | — |  |
| `V5-05` | BZ 반응-확산 매질 | 3 | skill | zone | 20 | 11 | 9 | — |  |
| `INT-08-P` | 디컨스트럭션 · 패널 산란형 | 3 | skill | circle | 83 | 11 | 8 | — |  |
| `FX-10-C` | 데이터 코어 · 큐브 수렴 결합형 | 5 | skill | circle | 83 | 11 | 8 | — |  |
| `FX-10-O` | 데이터 코어 · 원본 바이너리 큐브 | 3 | skill | circle | 83 | 11 | 8 | — |  |
| `INT-08-O` | 디컨스트럭션 · 최초 3D 패널 | 3 | skill | zone | 20 | 11 | 9 | — |  |
| `ARC-21` | 지각융기·용암균열 | 4 | ult | circle | 245 | 15 | 0 | knock 12, stun 0.4 | **추가** burn 3 |
| `FX-101` | 진홍 장미 폭렬 | 3 | skill | circle | 83 | 11 | 8 | — |  |
| `FX-146` | 프리즘 나비 산란 | 4 | skill | circle | 75 | 8 | 6 | — |  |
| `FX-140` | 신성 연꽃 강타 | 4 | skill | circle | 75 | 8 | 6 | — |  |
| `FX-150` | 궤도 십자 폭격 | 4 | skill | circle | 83 | 11 | 8 | — |  |
| `FX-125` | 황금비 프랙탈 폭발 | 4 | ult | circle | 245 | 15 | 0 | — |  |
| `FX-141` | 잠식하는 공허핵 | 4 | skill | zone | 20 | 8 | 9 | — |  |
| `NX-05` | 빙백 연화 파쇄 | 4 | skill | circle | 75 | 8 | 6 | slow 3 |  |
| `FX-126` | 시간 역행의 와류 | 3 | skill | zone | 20 | 11 | 9 | slow 3 |  |
| `FX-142` | 점화 초승달 와류 | 3 | skill | radial | 75 | 8 | 6 | burn 3 |  |
| `FX-152` | 시공 단절 와류 | 4 | skill | zone | 20 | 8 | 9 | — | **추가** slow 3 |
| `FX-155` | 나비 탄막 | 3 | skill | circle | 75 | 8 | 6 | — |  |
| `FX-157` | 프리즘 나선 에너지파 | 4 | skill | radial | 83 | 11 | 8 | — |  |
| `NX-08` | 육각 빙결 성문 | 3 | skill | zone | 20 | 8 | 9 | slow 3 |  |
| `NX-10` | 심연 와류 | 3 | skill | zone | 20 | 11 | 9 | — |  |
| `ARC-22` | 차원 균열 | 3 | skill | zone | 20 | 8 | 9 | — |  |
| `ARC-24` | 심연 연꽃 포식 | 3 | skill | zone | 20 | 5 | 9 | — |  |
| `ARC-27` | 용암 개화 | 3 | skill | zone | 20 | 5 | 9 | burn 3 |  |
| `FX-130` | 침묵의 핵폭·버섯구름 | 3 | skill | circle | 83 | 11 | 8 | burn 3 |  |
| `ARC-25` | 사건의 지평선 낫 | 3 | skill | zone | 20 | 11 | 9 | knock 12 |  |
| `FX-108` | 마법공학 봉인 참격 | 3 | skill | circle | 75 | 8 | 6 | — | **추가** silence 0.8 |
| `WTR-1` | 워터 볼텍스 | 4 | skill | zone | 20 | 8 | 9 | slow 2 |  |
| `ARC-32` | 차원 거울 파쇄 | 3 | skill | circle | 83 | 11 | 8 | — |  |
| `MYTH-01` | 청연 · 언령신룡 강림 | 5 | ult | circle | 245 | 15 | 0 | — |  |
| `FX-121` | 디지털 글리치 · 양자 붕괴 | 4 | skill | circle | 75 | 8 | 6 | — |  |
| `CURSE-01` | 무간 · 흑왕의 장송 | 4 | skill | circle | 83 | 11 | 8 | curse 2 |  |
| `GS-aurora9` | 극광폭발 | 3 | skill | radial | 80 | 10 | 8 | burn 3 | 검토 후보: 오로라인데 burn |
| `GS-vortexring` | 와류환 | 4 | skill | circle | 70 | 6 | 6 | knock 10 |  |
| `GS-sedov` | 공중 가스폭연 | 4 | skill | circle | 78 | 9 | 6 | burn 3 |  |
| `GS-miura` | 미우라전개 | 3 | guard | shield | — | — | 10 | shield 90 |  |
| `GS-requiem` | 천구장송 | 5 | skill | circle | 70 | 6 | 6 | — |  |
| `GS-nuke` | 최후통첩 | 4 | ult | circle | 240 | 9 | 0 | burn 3 |  |
| `GS-sonic` | 음속파단 | 4 | skill | circle | 78 | 9 | 6 | knock 10 |  |
| `GS-helix` | 오행천파 | 4 | skill | circle | 75 | 8 | 6 | — |  |
| `GS-vacuum` | 진공파열 | 3 | skill | circle | 80 | 8 | 8 | burn 3 |  |
| `GS-thermo` | 항성점화 | 4 | ult | circle | 255 | 9 | 0 | burn 3 |  |
| `GS-mirv` | 묵시의비 | 4 | ult | circle | 255 | 6 | 0 | — |  |
| `GS-aegis` | 천개방벽 | 4 | guard | shield | — | — | 10 | shield 90 |  |
| `GS-rod` | 천주강림 | 4 | skill | circle | 80 | 5 | 8 | — | **추가** stun 0.4 |
| `GS-cannon` | 철갑작렬 | 3 | skill | circle | 68 | 5 | 6 | — |  |
| `GS-dynamite` | 도화선 | 3 | skill | circle | 75 | 8 | 6 | burn 3 |  |
| `GS-shuriken` | 수리검연격 | 3 | skill | circle | 68 | 5 | 6 | — |  |
| `GS-talisman` | 부적봉인 | 4 | skill | circle | 75 | 8 | 6 | — | **추가** silence 1 |
| `GS-bell` | 범종파문 | 4 | ult | circle | 250 | 6 | 0 | knock 10 |  |
| `GS-fan` | 선풍참 | 4 | skill | circle | 73 | 7 | 6 | knock 10 |  |
| `GS-frost` | 빙결탄 | 3 | skill | circle | 75 | 8 | 6 | slow 3 |  |
| `GS-arsenal` | 기갑전개 | 4 | skill | circle | 75 | 8 | 6 | — |  |
| `GS-railgun` | 전자기포 | 3 | skill | circle | 70 | 6 | 6 | — | **추가** expose 3 |
| `GS-nanite` | 나노해체 | 4 | skill | circle | 85 | 12 | 8 | — |  |
| `GS-tokamak` | 핵융합로 | 4 | skill | circle | 83 | 11 | 8 | burn 3 |  |
| `GS-web` | 결계망 | 3 | skill | circle | 68 | 5 | 6 | — | **추가** root 0.6 |
| `GS-lance` | 관통포 | 4 | skill | circle | 75 | 8 | 6 | — |  |
| `GS-hammer` | 뇌추 | 3 | skill | circle | 73 | 7 | 6 | expose 3 |  |
| `GS-meteor` | 유성우 | 4 | skill | circle | 73 | 7 | 6 | — |  |
| `GS-tsunami` | 해일 | 4 | ult | circle | 260 | 18 | 0 | slow 2 |  |
| `GS-horizon` | 사건지평 | 4 | skill | circle | 70 | 6 | 6 | knock 12 |  |
| `GS-ferro` | 자성첨탑 | 3 | skill | circle | 73 | 7 | 6 | knock 12 |  |
| `GS-murmur` | 군무 | 3 | skill | circle | 68 | 5 | 6 | — |  |
| `GS-bloom` | 몽화만개 | 5 | ult | radial | 245 | 11 | 0 | — |  |
| `GS-aurora` | 극광강림 | 4 | skill | radial | 78 | 9 | 6 | burn 3 | 검토 후보: 오로라인데 burn |
| `GS-fractal` | 무한전개 | 4 | skill | circle | 73 | 7 | 6 | — |  |
| `GS-abyss` | 심해명멸 | 4 | skill | circle | 73 | 7 | 6 | — |  |
| `GS-dune` | 사구성음 | 4 | skill | circle | 75 | 8 | 6 | knock 12 |  |
| `GS-chrono` | 시간층리 | 3 | skill | circle | 70 | 6 | 6 | slow 3 |  |
| `GS-mycel` | 포자군락 | 3 | skill | circle | 75 | 8 | 6 | — |  |
| `GS-tempest` | 뇌옥강림 | 4 | skill | circle | 80 | 10 | 8 | expose 3 |  |
| `GS-silk` | 천잠사 | 3 | skill | circle | 73 | 7 | 6 | — | **추가** root 0.5 |
| `GS-rift` | 분열지각 | 5 | ult | radial | 240 | 14 | 0 | knock 12 |  |
| `GS-judge` | 뇌정극형 | 4 | skill | circle | 85 | 12 | 8 | expose 3 |  |
| `GS-digital` | 연산붕괴 | 4 | skill | circle | 80 | 10 | 8 | — |  |
| `GS-polytope` | 다면압궤 | 5 | skill | circle | 73 | 7 | 6 | — |  |
| `CH:prism` | 프리즘 헬릭스 | 5 | skill | beam | 61 | — | 6 | — |  |
| `CH:rupture` | 럽처 드라이브 | 5 | skill | beam | 65 | — | 6 | expose 3 |  |
| `CH:void` | 보이드 오키드 | 4 | skill | beam | 64 | — | 6 | knock 12 |  |
| `CH:glacier` | 글레이셔 랜스 | 4 | skill | beam | 68 | — | 6 | slow 3 |  |
| `CH:solar` | 솔라 포지 | 4 | skill | beam | 60 | — | 6 | burn 3 |  |
| `CH:aurora` | 오로라 타이드 | 4 | skill | beam | 60 | — | 6 | burn 3 | 검토 후보: 오로라인데 burn |
| `CH:storm` | 스톰 필라멘트 | 4 | skill | beam | 61 | — | 6 | expose 3 |  |
| `CH:kintsugi` | 킨츠기 리프트 | 4 | skill | beam | 68 | — | 6 | knock 12 |  |
| `CH:coral` | 코랄 코러스 | 4 | skill | beam | 60 | — | 6 | — |  |
| `CH:tidal` | 타이달 크라운 | 5 | skill | beam | 61 | — | 6 | slow 2 |  |
| `CH:glitch` | 크로매틱 에러 | 4 | skill | beam | 60 | — | 6 | — |  |
| `CH:collapse` | 널 캐스케이드 | 4 | skill | beam | 60 | — | 6 | — |  |
| `CH:comic` | 패널 브레이커 | 4 | skill | beam | 60 | — | 6 | — |  |
| `CH:jade` | 비취 묵광 | 4 | skill | beam | 60 | — | 6 | — |  |
| `CH:dokkaebi` | 도깨비불 | 3 | skill | beam | 68 | — | 6 | — | **추가** burn 3 |
| `CH:matrix` | 매트릭스 캐스케이드 | 4 | skill | circle | 68 | 5 | 6 | — |  |
| `CH:cathedral` | 성당의 창 | 3 | skill | beam | 61 | — | 6 | — |  |
| `CH:ferro` | 자성 송곳니 | 4 | skill | circle | 68 | 5 | 6 | knock 12 |  |
| `CH:seraph` | 세라프 강림 | 3 | skill | beam | 63 | — | 6 | — |  |
| `CH:mycelium` | 균사 저주 | 3 | skill | circle | 68 | 5 | 6 | — | **추가** curse 2 |
| `CH:chronos` | 시간의 전단 | 3 | skill | beam | 60 | — | 6 | slow 3 |  |
| `CH:loom` | 중력 직조 | 4 | skill | beam | 60 | — | 6 | knock 12 |  |
| `CH:leviathan` | 레비아탄의 항적 | 4 | skill | circle | 68 | 5 | 6 | — |  |
| `CH:requiem` | 크림슨 레퀴엠 | 3 | skill | circle | 65 | 4 | 6 | — |  |
| `CH:prominence` | 태양 홍염 | 3 | skill | circle | 68 | 5 | 6 | burn 3 |  |
| `CH:manta` | 심해의 망토 | 4 | skill | circle | 68 | 5 | 6 | — |  |
| `CH:ssitgim` | 씻김 길가르기 | 3 | skill | circle | 68 | 5 | 6 | — |  |
| `CH:obang` | 오방 먹 분리 | 4 | skill | circle | 68 | 5 | 6 | — |  |
| `CH:chladni` | 클라드니 구 | 4 | skill | circle | 70 | 6 | 6 | knock 10 |  |
| `CH:emille` | 에밀레 맥놀이 | 4 | skill | circle | 68 | 5 | 6 | knock 10 |  |
| `CH:tomo` | 단층 촬영 | 4 | skill | circle | 68 | 5 | 6 | — |  |
| `CH:lazy` | 팬터그래프 케이지 | 3 | skill | circle | 65 | 4 | 6 | — | **추가** root 0.6 |
| `CH:brimstone` | 인페르노 헬파이어 | 4 | skill | circle | 70 | 6 | 6 | burn 3 |  |
| `CH:voltspear` | 블루썬더볼트 | 3 | skill | beam | 68 | — | 6 | expose 3 |  |
| `CH:crane` | 종이학 편대 | 4 | skill | circle | 65 | 4 | 6 | — |  |
| `CH:relay` | 거울 릴레이 | 3 | skill | beam | 65 | — | 6 | — |  |
| `CH:bubble` | 비눗방울 올가미 | 3 | skill | circle | 65 | 4 | 6 | — | **추가** root 0.6 |
| `CH:spiral` | 와류 진주 | 5 | skill | circle | 75 | 5 | 6 | knock 10 |  |
| `CH:galaxy` | 나선 성운 | 4 | skill | circle | 70 | 6 | 6 | — |  |
| `CH:twin` | 쌍나선 합일 | 4 | skill | circle | 68 | 5 | 6 | — |  |
| `CH:opal` | 오팔 박막 | 4 | skill | circle | 73 | 7 | 6 | — |  |
| `CH:marey` | 마레 잔상 | 4 | skill | circle | 65 | 4 | 6 | slow 3 |  |
| `CH:gaze` | 명부의 응시 | 4 | skill | circle | 68 | 5 | 6 | curse 2 |  |
| `FX-04` | 액체 화염 · 용융 초승달 | 3 | skill | circle | 83 | 11 | 8 | burn 3 |  |
| `V5-01` | 타이포 임팩트 | 3 | guard | shield | — | — | 12 | haste 5, shield 50 |  |
| `INT-03-G` | 슈퍼노바 · 금빛 잔재형 | 3 | skill | circle | 83 | 11 | 8 | burn 3 |  |
| `FX-158` | 나선 에너지 랜스 | 3 | skill | beam | 70 | — | 6 | — |  |
| `FX-88` | 진홍 핵 절단 | 3 | skill | circle | 83 | 11 | 8 | burn 3 |  |
| `C:FB_STRUCT:myco` | 발광 균사 결계 | 3 | skill | deploy | 9 | 12 | 14 | — |  |
| `D:STRUCT:obelisk` | 오벨리스크 | 3 | skill | deploy | 9 | 10 | 14 | — |  |
| `D:STRUCT:fountain` | 마나 분수 | 3 | skill | deploy | 9 | 10 | 14 | — |  |
| `D:STRUCT:ward` | 룬 결계 | 3 | skill | deploy | 9 | 12 | 14 | — |  |
| `D:STRUCT:tree` | 달빛 나무 | 3 | skill | deploy | 9 | 8 | 14 | — |  |
| `D:STRUCT:belfry` | 공명 종루 | 3 | skill | deploy | 9 | 12 | 14 | — |  |
| `D:STRUCT:altar` | 태양 제단 | 3 | skill | deploy | 9 | 12 | 14 | — | **추가** burn 3 |
| `D:STRUCT:lunar` | 월륜 첨탑 | 3 | skill | deploy | 9 | 12 | 14 | — |  |
| `D:STRUCT:sanctum` | 암흑 성소 | 3 | skill | deploy | 9 | 12 | 14 | — |  |
| `D:STRUCT:spire` | 수정 첨탑 | 3 | skill | deploy | 22 | 22 | 16 | — |  |
| `D:STRUCT:pylon` | 뇌전 첨주 | 3 | skill | deploy | 22 | 22 | 16 | — | **추가** expose 3 |
| `D:STRUCT:portal` | 포탈 | 3 | skill | deploy | 0 | 9 | 12 | haste 3 |  |
| `D:PROJ:lance` | 수평 관통 빔 | 3 | skill | circle | 65 | 4 | 6 | — |  |
| `D:ULT:inkfall` | 먹빛 강림 | 3 | skill | circle | 83 | 11 | 8 | — |  |
| `D:ULT:issen` | 일섬 | 3 | skill | circle | 68 | 5 | 6 | — |  |
| `D:ULT:crystalcage` | 수정뇌옥 | 3 | skill | circle | 70 | 6 | 6 | — | **추가** root 0.8 |
| `D:ULT:waltz` | 선회 무곡 | 3 | guard | shield | — | — | 12 | haste 5, shield 50 |  |
| `D:ULT:agwisasal` | 아귀사슬 | 4 | skill | circle | 70 | 6 | 6 | curse 2 | **추가** root 0.6 |
| `D:ULT:mugeonbu` | 묵언부 | 3 | skill | circle | 70 | 6 | 6 | — | **추가** silence 1.2 |
| `C:F_PROJ:dat` | 사이버 | 3 | basic | projectile | 40 | 6 | 1.4 | — |  |
| `C:F_PROJ:irn` | 쇠창 | 3 | basic | projectile | 40 | 6 | 1.4 | knock 12 |  |
| `C:F_PROJ:mtx` | 매트릭스 | 3 | basic | projectile | 40 | 6 | 1.4 | — |  |
| `C:F_PROJ:gho` | 유령 | 3 | basic | projectile | 40 | 6 | 1.4 | — |  |
| `C:F_PROJ:qnt` | 양자 | 3 | basic | projectile | 40 | 6 | 1.4 | — |  |
| `C:F_PROJ:lqm` | 리퀴드메탈 | 3 | basic | projectile | 40 | 6 | 1.4 | knock 12 |  |
| `C:F_PROJ:sing` | 특이점 블랙홀 | 3 | basic | projectile | 40 | 4 | 1.4 | knock 12 |  |
| `C:F_PROJ:memo` | 메멘토 에코 | 3 | basic | projectile | 40 | 4 | 1.4 | slow 3 |  |
| `C:F_PROJ:frost` | 서리 심장 | 3 | basic | projectile | 40 | 4 | 1.4 | slow 3 |  |
| `C:F_PROJ:meteor` | 유성탄 | 3 | basic | projectile | 40 | 4 | 1.4 | — |  |
| `C:SF_PROJ:prs` | 크로마 프리즘 | 3 | skill | projectile | 73 | 7 | 6 | — |  |
| `C:SF_PROJ:eco` | 크로노 에코 | 3 | skill | projectile | 73 | 7 | 6 | slow 3 |  |
| `C:SF_PROJ:mtr` | 유성 파쇄체 | 3 | skill | projectile | 73 | 7 | 6 | — |  |
| `C:FB_PROJ:ori` | 종이학(오리가미) | 4 | skill | projectile | 75 | 8 | 6 | — |  |
| `C:FB_PROJ:bel` | 공명 범종 | 3 | skill | projectile | 75 | 8 | 6 | knock 10 |  |
| `C:F_STRUCT:bismuth` | 비스무트 결정 | 4 | skill | deploy | 9 | 6 | 14 | — |  |
| `C:F_STRUCT:tectonic` | 지각 융기(그을음) · C | 4 | ult | circle | 240 | 14 | 0 | knock 12 |  |
| `C:F_STRUCT:talisman` | 음양 부적 관문 | 4 | skill | deploy | 0 | 9 | 12 | haste 3 |  |
| `C:F_STRUCT:chain` | 진홍 사슬 결계 | 3 | skill | deploy | 0 | 10 | 14 | shield 60 |  |
| `C:F_STRUCT:gateway` | 양자 게이트웨이 | 3 | skill | deploy | 0 | 9 | 12 | haste 3 |  |
| `C:F_STRUCT:icewall` | 극저온 빙벽 | 3 | skill | deploy | 0 | 9 | 14 | shield 60 |  |
| `C:F_STRUCT:turret` | 이지스 포탑 | 4 | skill | deploy | 22 | 22 | 16 | — |  |
| `C:F_STRUCT:siphon` | 특이점 사이폰 | 4 | skill | deploy | 9 | 8 | 14 | — |  |
| `C:SF_STRUCT:pct` | 플라즈마 격리로 | 4 | skill | deploy | 9 | 11 | 14 | burn 3 |  |
| `C:SF_STRUCT:chr` | 시간 조절 장치 | 3 | skill | deploy | 9 | 9 | 14 | slow 3 |  |
| `C:SF_STRUCT:nfn` | 나노 조립 노드 | 3 | skill | deploy | 9 | 9 | 14 | — |  |
| `C:SF_STRUCT:snt` | 자율 감시 포탑 | 3 | skill | deploy | 22 | 22 | 16 | — |  |
| `C:SF_STRUCT:hcb` | 홀로그램 지휘 비콘 | 4 | skill | deploy | 9 | 10 | 14 | — |  |
| `C:SF_STRUCT:ora` | 궤도 중계 첨탑 | 3 | skill | deploy | 9 | 8 | 14 | — |  |
| `C:SF_STRUCT:shd` | 위상 방어막 | 4 | skill | deploy | 0 | 11 | 14 | shield 60 |  |
| `C:SF_STRUCT:tsl` | 테슬라 아크 파일런 | 4 | skill | deploy | 9 | 10 | 14 | expose 3 |  |
| `C:SF_STRUCT:obl` | 궤도 타격 비콘 | 3 | skill | deploy | 9 | 7 | 14 | — |  |
| `C:SF_STRUCT:msd` | 매스 드라이버 | 4 | skill | deploy | 22 | 22 | 16 | — |  |
| `C:SF_STRUCT:hlx` | 헬륨-3 채굴기 | 4 | skill | deploy | 9 | 11 | 14 | — |  |
| `C:FB_STRUCT:pagoda` | 천공 석탑 | 3 | skill | deploy | 9 | 12 | 14 | — |  |
| `C:FB_STRUCT:astro` | 천구의 | 3 | skill | deploy | 9 | 10 | 14 | — |  |
| `C:FB_STRUCT:loom` | 운명의 베틀 | 4 | skill | deploy | 0 | 8 | 14 | shield 60 |  |
| `C:FB_STRUCT:organ` | 수정 공명 오르간 | 3 | skill | deploy | 9 | 8 | 14 | — |  |
| `C:EXT_STRUCT:reactor` | 플라스마 발전소 | 4 | skill | deploy | 9 | 12 | 14 | burn 3 |  |
| `C:EXT_STRUCT:graphene` | 그래핀 방벽 | 5 | skill | deploy | 0 | 12 | 14 | shield 60 |  |
| `C:EXT_STRUCT:hologram` | 홀로그램 송출기 | 4 | skill | deploy | 9 | 10 | 14 | — |  |
| `C:EXT_STRUCT:chiral` | 카이랄 결정군 | 4 | skill | deploy | 9 | 12 | 14 | — |  |
| `C:EXT_STRUCT:anchor` | 중력 앵커 | 3 | skill | deploy | 9 | 12 | 14 | — |  |
| `C:EXT_STRUCT:rift` | 시공 균열 | 3 | skill | deploy | 0 | 9 | 12 | haste 3 |  |
| `C:EXT_STRUCT:bio` | 바이오 콜로니 | 3 | skill | deploy | 9 | 12 | 14 | — |  |
| `C:EXT_STRUCT:beacon` | 펄서 비콘 | 3 | skill | deploy | 9 | 12 | 14 | burn 3 |  |
| `C:EXT_STRUCT:auroraCurtain` | 오로라 커튼 | 4 | guard | shield | — | — | 12 | haste 5, shield 50 |  |
| `C:EXT_STRUCT:auroraAltar` | 오로라 제단 | 5 | guard | shield | — | — | 12 | haste 5, shield 50 |  |
| `C:EXT_STRUCT:organ` | 공명 오르간 | 3 | skill | deploy | 9 | 12 | 14 | — |  |
| `D:PROJ:chain` | 연쇄 뇌창 | 4 | basic | chain | 40 | — | 1.2 | — | **추가** expose 3 |
| `C:FB_PROJ:koi` | 유수 잉어 | 4 | basic | projectile | 45 | 8 | 1.8 | — |  |
| `D:ULT:zenith` | 백일염천 | 4 | ult | circle | 260 | 14 | 0 | burn 5 |  |
| `D:PROJ:fissure` | 지열 균열 | 3 | basic | beam | 55 | — | 1.4 | knock 6 |  |
| `D:ULT:upheaval` | 대지 융기 | 5 | ult | circle | 200 | 12 | 0 | knock 12, slow 3, stun 0.75 |  |
