# Mobile App Studio 묶음

`mobile-app-studio`는 단독 실행기가 아니라 모바일 앱 제작 요청을 올바른 실행
스킬로 보내는 라우터입니다. 따라서 다음 일곱 스킬을 함께 설치해야 합니다.

1. `mobile-app-studio`: 단일 앱 제작과 여러 앱 공장 중 실행 경로 선택
2. `reference-first-mobile-app`: 앱 설명과 통일된 시안 10장으로 앱 하나 완성
3. `night-app-factory`: 여러 아이디어를 세션과 큐로 관리하며 순차 제작
4. `app-qa-gate`: 헤드리스·시뮬레이터·실기기 QA 경계를 정직하게 판정
5. `app-release-preflight`: 앱 배포 전 시크릿, 환경, 버전, 딥링크, 개인정보, 롤백 점검
6. `ios-release-finisher`: App Store 메타데이터, 법무·개인정보, 스크린샷, 심사 준비
7. `ios-testflight-publisher`: iOS·Flutter TestFlight 등록, 빌드, 업로드, 처리 상태 확인

설치:

```bash
./scripts/install.sh mobile-app-studio
```

단일 앱 요청에서는 `reference-first-mobile-app`이 시안 10장을 디자인 계약으로
사용합니다. 여러 앱 요청에서는 `night-app-factory`가 큐와 세션을 관리하고,
시안 10장이 준비된 개별 앱 작업은 다시 `reference-first-mobile-app`으로
넘깁니다.

`product-design:image-to-code`, `omo:visual-qa`, `ios-simulator-skill`처럼 다른
플러그인이나 하네스가 제공하는 보조 스킬은 이 저장소에 포함하지 않습니다.
해당 기능이 없는 환경에서는 설치된 스킬의 절차를 읽고 동등한 도구로 수행하거나
관련 검증 경계를 명시해야 합니다.
