# GS

Three.js 기반 GS Action / VFX LAB입니다. 빌드 단계 없이 HTTP로 실행합니다.

```bash
python3 -m http.server 8000 --bind 127.0.0.1
```

브라우저에서 `http://127.0.0.1:8000/`을 엽니다. `index.html`과
`GS_Action_v34_runtime.html`은 같은 실행본으로 유지합니다. Three.js와 모델의
CDN 접근이 필요합니다. 로컬 모델이 없으면 기존 CDN 모델을 사용합니다.

클라우드 회귀 검사에는 Node.js, Python Playwright, Chromium이 필요합니다.
Playwright는 `python3 -m pip install playwright`로 설치합니다. Chromium은
시스템 패키지를 사용하거나 `GS_CHROMIUM`으로 실행 경로를 지정합니다.
프록시 환경에서는 브라우저의 CA 신뢰를 구성하고 `HTTPS_PROXY`를 유지합니다.
TLS 검증을 비활성화하지 않습니다.

서버를 실행한 상태에서:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/benchmark_cloud.py --seconds 60 --cap 30 --output cloud-results/30.json
python3 scripts/benchmark_cloud.py --seconds 600 --cap 60 --loop --output cloud-results/600.json
```

`GS_TEST_BASE_URL`로 테스트 서버 주소를 바꿀 수 있습니다. 장시간 검사는 실제
10분을 사용합니다. 브라우저 성능 검사는 다른 브라우저 검사와 동시에 실행하지
않습니다. 원시 결과는 기본적으로 Git에서 제외합니다.

검사 범위와 남은 작업은 [클라우드 검증 기록](docs/cloud-validation.md)에 있습니다.
