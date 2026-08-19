# App Store Connect 자동화 경계

## API와 전송 수단

App Store Connect REST API는 JWT로 인증한다. API key, Key ID, Issuer ID, `.p8` 내용과 경로는 출력하지 않는다. 바이너리는 REST API로 직접 업로드하지 않고 Xcode, Transporter 또는 Apple이 지원하는 업로드 도구를 사용한다.

## API 자동화 가능

- 기존 앱과 버전 조회
- 새 App Store 버전 생성
- App Info와 version localization
- 설명, 키워드, 프로모션 문구, URL
- 스크린샷, 미리보기, 심사 첨부파일
- 연령 등급 declaration
- 콘텐츠 권리, 일부 앱 정보와 카테고리
- 사용자 지정 EULA
- 암호화 declaration과 문서
- 심사 연락처, 데모 계정, 심사 메모
- 가격 schedule과 availability 리소스
- 접근성 declaration
- 앱 태그
- IAP와 구독 메타데이터
- review submission 리소스

지원 여부는 실행 시 최신 공식 OpenAPI 명세에서 다시 확인한다. API는 production 데이터를 변경하므로 write 전에 변경 미리보기를 남긴다.

## 포털 또는 사람 전용으로 취급

- 새 앱 레코드 최초 생성
- App Privacy 데이터 유형 응답과 Publish
- Apple 계약과 Paid Apps Agreement 동의
- 세금, 은행, 신원, 법인 확인
- EU DSA trader 인증
- 한국 개발자 식별정보 인증
- 국가별 허가 문서의 의미 확인
- 첫 IAP를 앱 버전과 함께 제출하는 일부 흐름

웹 자동화가 기술적으로 가능해도 법적 동의와 계정 소유자 진술을 에이전트가 대신 확정하지 않는다.

## 사람 승인 후 API 입력

- 연령 등급의 의미 답변
- Made for Kids
- 콘텐츠 권리 선언
- 가격과 출시 국가
- 공개·비공개 유통
- 수출규정 사실 답변
- 실제 심사 제출과 출시 방식

## 상태 증거

| 상태 | 요구 증거 |
|---|---|
| `METADATA_SAVED` | exact app/version API 재조회 또는 포털 값 |
| `ARCHIVED` | xcarchive 존재와 명령 성공 |
| `EXPORTED` | IPA 존재와 서명·식별자 확인 |
| `UPLOADED` | Apple 전송 수락 응답 |
| `PROCESSING` | exact version/build가 처리 중으로 보임 |
| `PROCESSED` | exact build가 유효한 처리 완료 상태 |
| `SUBMITTED` | review submission이 제출 상태 |
| `APPROVED` | App Review 승인 상태 |
| `LIVE` | 대상 storefront의 실제 제품 페이지 또는 availability |

앞 상태를 뒤 상태로 과장하지 않는다.
