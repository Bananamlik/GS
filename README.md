# GS

GS Action 전투 및 VFX 시험장입니다.

## 실행

`GS_Action_v14_261003-0447.html`이 실행 파일입니다. 저장소 폴더에서 로컬 서버를 실행한 뒤 브라우저로 열어 주세요.

```sh
python3 -m http.server 8000
```

주소: `http://localhost:8000/GS_Action_v14_261003-0447.html`

Three.js는 jsDelivr에서 불러오므로 실행에는 해당 CDN 연결이 필요합니다. GitHub의 파일 보기 화면에서는 게임이 실행되지 않습니다.

## 검수 및 수정

[적대적 검수 수정 결과](gs-v14-fix-report_261003.md)에 기둥 차단·연쇄·투사체 피해·소리 보정 수정과 검증 범위를 기록했습니다. [기존 v14 작업 보고서](gs-v14-report_v1_261003-0447.md)는 최초 업로드 당시의 기록입니다.

## 회귀 테스트

```sh
node audit/regression.cjs
python3 audit/audio_regression.py
```

전투 테스트는 Node.js만 사용합니다. 오디오 테스트에는 Python Playwright와 `/usr/bin/chromium`이 필요합니다. 테스트는 실행 HTML에서 직접 코드를 추출하고 외부 CDN 연결 없이 수행합니다. 전체 화면·GPU 성능·실기기 및 실제 스킬 소리 청취 검증은 별도로 필요합니다.
