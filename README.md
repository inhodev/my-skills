# my-skills

반복해서 사용하는 AI 에이전트 워크플로우를 스킬 형태로 정리한 저장소입니다.

단순한 프롬프트 모음이 아니라, 에이전트가 실제 작업을 끝까지 수행하기 위한
절차, 검증 기준, 참고 문서와 자동화 스크립트를 함께 제공합니다. 기본 설명은
한국어로 작성하고, 각 스킬의 `SKILL.md`는 Codex와 호환되는 구조를 따릅니다.

## 빠른 설치

다른 컴퓨터에서 다음 명령을 실행하면 이 저장소의 모든 스킬을 설치할 수 있습니다.

```bash
git clone https://github.com/inhodev/my-skills.git
cd my-skills
./scripts/install.sh all
```

기본 설치 위치는 `~/.codex/skills`입니다. `CODEX_HOME`이 설정되어 있으면
`$CODEX_HOME/skills`를 사용합니다.

이미 같은 이름의 스킬이 있지만 내용이 다르면 기존 폴더를
`~/.codex/skill-backups/<날짜-시간>/`에 먼저 옮긴 뒤 새 버전을 설치합니다.

설치 후에는 새 Codex 작업을 시작하거나 Codex 앱을 다시 열어 스킬 목록을
갱신하세요.

## 포함된 스킬

| 스킬 | 하는 일 | 호출 예시 |
| --- | --- | --- |
| `mobile-app-studio` | 단일 앱 제작과 여러 앱 공장 중 올바른 실행 경로 선택 | `$mobile-app-studio 앱 아이디어와 시안 10장으로 만들어줘` |
| `reference-first-mobile-app` | 앱 설명과 통일된 시안 10장으로 실제 동작하는 앱 완성 | `$reference-first-mobile-app 이 시안 10장대로 SwiftUI 앱을 만들어줘` |
| `night-app-factory` | 여러 앱을 세션·큐로 관리하고 동시 제작 수를 제한 | `$night-app-factory 이 아이디어들을 밤새 순차 제작해줘` |
| `app-qa-gate` | Flutter/Swift/React Native/Expo 헤드리스 QA, 시뮬레이터 점유 보호 | `$app-qa-gate 이 앱의 현재 QA 상태를 확인해줘` |
| `app-release-preflight` | [출시 걸림돌 체크] 앱 배포 전 시크릿, 환경, 버전, 딥링크, 개인정보, 롤백 점검 | `$app-release-preflight 이 앱의 출시 걸림돌을 점검해줘` |
| `ios-release-finisher` | [출시직전 appstore connect올리는 용] App Store 메타데이터, 법무·개인정보, 스크린샷, 심사 준비 | `$ios-release-finisher 이 앱의 출시 준비를 끝까지 진행해줘` |
| `ios-testflight-publisher` | [testflight 올리는 용] iOS·Flutter TestFlight 등록, 빌드, 업로드, 처리 상태 확인 | `$ios-testflight-publisher 이 앱을 TestFlight에 올려줘` |
| `video-ux-observer` | [크몽 피드백에서 사용] 사용성 테스트 영상에서 UX 문제·긍정 순간·사용자 연구 추출 | `$video-ux-observer 이 사용자 테스트 영상을 분석해줘` |
| `app-review-miner` | [앱스토어 리뷰 수집 스킬] 앱스토어 리뷰를 수집·정규화하고 불만·기능 요청·MVP 기회 추출 | `$app-review-miner 이 앱 리뷰에서 MVP 기회를 찾아줘` |
| `git-organize-history` | [깃허브 올릴때 기능별로 한글 커밋메세지] 누적 변경을 기능별 커밋으로 나누고 상세 한국어 커밋 작성 | `$git-organize-history 변경을 기능별로 커밋하고 푸시해줘` |

## Mobile App Studio

`mobile-app-studio`는 모바일 앱 요청을 두 실행 경로 중 하나로 연결합니다.

### 앱 하나를 만드는 경우

앱 설명과 하나의 콘셉트로 통일된 시안 10장을 받으면
`reference-first-mobile-app`을 사용합니다.

- 시안 10장을 화면 이미지가 아닌 디자인 계약으로 사용
- 색상·글꼴·간격·컴포넌트를 하나의 디자인 시스템으로 추출
- 전체 스크린샷을 붙이지 않고 실제 SwiftUI 또는 Flutter 요소로 구현
- 모든 주요 버튼과 화면 전환을 실제 상태에 연결
- 한국어를 기본 언어로 제공하고 자연스러운 영어 화면도 구현
- 한국어 10장과 영어 10장을 다시 캡처해 원본과 직접 비교
- 빌드 성공과 실제 시각·동작 검증을 분리해 보고

### 여러 앱을 만드는 경우

아이디어가 여러 개이거나 야간 제작, 큐, 세션 생성과 감시가 필요하면
`night-app-factory`를 사용합니다.

- 앱마다 별도 프로젝트와 소유 세션 유지
- 내구성 있는 상태 파일과 FIFO 큐 사용
- 무거운 동시 제작은 기본 두 개 이하로 제한
- 한 앱의 실패가 다른 앱의 진행을 막지 않도록 격리
- 시안 10장이 준비된 개별 앱은 `reference-first-mobile-app`으로 제작
- 다음 날 실제 결과물·로그·캡처 링크가 있는 보고서 생성

출시와 배포까지 같이 쓸 때는 `app-release-preflight`, `ios-release-finisher`,
`ios-testflight-publisher`도 이 묶음에 함께 설치됩니다.

모바일 앱 묶음만 설치하려면 다음 명령을 사용합니다.

```bash
./scripts/install.sh mobile-app-studio
```

자세한 구성은 [`bundles/mobile-app-studio.md`](bundles/mobile-app-studio.md)를
참고하세요.

## 설치 명령

```bash
# 설치할 수 있는 스킬 보기
./scripts/install.sh list

# 실제 변경 없이 설치 대상 확인
./scripts/install.sh --dry-run all

# 저장소의 모든 스킬 설치 또는 업데이트
./scripts/install.sh all

# 스킬 하나만 설치
./scripts/install.sh git-organize-history
```

저장소를 업데이트한 뒤 같은 설치 명령을 다시 실행하면 됩니다.

```bash
git pull
./scripts/install.sh all
```

## 다른 에이전트·하네스에서 사용

Codex 스킬 탐색을 지원하지 않는 에이전트에는 다음과 같이 지시하세요.

> 사용할 스킬 폴더의 `SKILL.md`를 먼저 전부 읽고, 그 파일이 요구하는
> `references/` 문서도 읽어라. 반복 검증은 제공된 `scripts/`를 사용하고,
> 완료 조건과 금지 사항을 생략하지 말고 작업하라.

하네스에 따라 도구 이름은 다를 수 있습니다. 도구 이름을 그대로 흉내 내기보다
스킬이 요구하는 검증 목적과 안전 경계를 동등한 도구로 충족해야 합니다.

`product-design:image-to-code`, `omo:visual-qa`, `ios-simulator-skill`처럼 외부
플러그인이 제공하는 보조 스킬은 이 저장소에 포함하지 않습니다. 해당 스킬이 없는
환경에서는 관련 단계를 생략했다고 숨기지 말고, 미검증 경계로 명확히 보고해야
합니다.

## 저장소 구조

```text
my-skills/
├── README.md
├── LICENSE
├── bundles/
├── scripts/
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── references/      # 필요한 경우
        └── scripts/         # 필요한 경우
```

사람을 위한 설치·사용 설명은 저장소 최상위 README에 둡니다. 에이전트가 실행할
핵심 절차는 각 `SKILL.md`, 상세 지식은 `references/`, 반복 가능한 검증은
`scripts/`에 둡니다.

## 저장소 검증

```bash
./scripts/doctor.sh
```

검증기는 다음을 확인합니다.

- 폴더명과 `SKILL.md`의 `name` 일치
- `agents/openai.yaml`과 기본 호출 예시 존재
- Python 캐시 파일 미포함
- 개인 컴퓨터 절대경로와 일반적인 비밀정보 패턴 미포함

## 라이선스와 출처

이 저장소에 포함된 파일은 별도 표시가 없는 한 MIT License로 배포합니다.

외부에서 가져오거나 수정한 스킬은 원본 라이선스와 출처를 확인한 뒤 별도로
표시해야 합니다. 출처나 재배포 조건이 확인되지 않은 스킬은 이 저장소에 넣지
않습니다.
