---
name: ux-feedback-report-builder
description: Build the client-facing PDF "사용자 피드백 보고서" (user feedback report, 20p/30p, A4) from per-participant usability-test analysis markdown, screen recordings and extracted frames. Use after video-ux-observer (or any per-tester analysis) when the user asks to write, assemble, redesign, fix, extend, or QA a Korean UX feedback report / 피드백 보고서 / 사용자 테스트 리포트 / 크몽 납품 보고서: page structure, evidence screenshots with red-box marks, crop rules per device, anti-AI-tone writing rules, density targets, HTML→PDF rendering and pre-delivery QA.
---

# UX Feedback Report Builder

## 이 스킬이 하는 일

테스터별 분석 문서(영상 관찰 md, 전사, 프레임)를 받아 **클라이언트에게 납품하는 A4 PDF 보고서**를 끝까지 만든다.
결과물은 "AI가 쓴 티가 나지 않고, 모든 지적에 실제 발언과 화면 캡처가 붙어 있으며, 페이지가 꽉 찬" 보고서다.

이 문서는 여러 프로젝트를 납품하며 클라이언트/운영자에게 실제로 지적받은 내용을 누적한 것이다.
여기 적힌 규칙은 취향이 아니라 **한 번씩 지적받고 고친 이력**이다. `references/lessons-log.md`에 날짜별 원문이 있다.
규칙이 왜 있는지 모르겠으면 그 로그를 먼저 읽는다. 임의로 완화하지 않는다.

## 읽기 순서 (작업 전 반드시)

1. 이 파일 전체
2. `references/report-structure.md` : 페이지 구성 명세
3. `references/writing-style.md` : 글쓰기 규칙과 AI티 금지표
4. `references/screenshots.md` : 캡처 추출·크롭·크기·정렬·빨간 네모
5. `references/design-tokens.md` : CSS 토큰·표지
6. `references/qa-checklist.md` : 납품 전 체크
7. `assets/template/report.html` : 페이지 타입별 스켈레톤 (이걸 복사해서 시작)
8. 이전 프로젝트의 `report_source/`가 있으면 그것이 최신 템플릿이다. 스킬의 스켈레톤보다 우선한다.

## 입력

- 테스터별 분석 md (사용자리서치종합, UX상세분석, 관찰 리포트 등). **전부 읽고 종합**한다. 일부만 읽고 쓰지 않는다.
- 원본 영상(MP4)과 추출 프레임 폴더. 프레임이 없으면 영상에서 직접 뽑는다.
- 서비스 이름, 플랫폼 구성, 테스트 일정, 브랜드 색(없으면 서비스 화면에서 추출).
- 이전 납품 보고서 PDF·소스가 있으면 구조와 톤의 기준으로 삼는다.

없는 정보는 `확인 필요`로 두고 사용자에게 한 번에 묻는다. 지어내지 않는다.

## 절차

### 0. 작업 환경

- 작업 폴더는 `report_source/` 하나에 자기완결적으로 둔다: `report.html`, `img/`, `fonts/`, `raw/`(크롭 전 원본 프레임), `marks.json`.
- 폰트: Noto Serif KR(제목), Noto Sans KR(본문). TTF를 `fonts/`에 두고 `@font-face`로 로컬 참조한다. 시스템 설치에 의존하지 않는다.
- 디스크: Chrome headless는 렌더할 때마다 임시 프로필을 만든다. `scripts/render_pdf.sh`를 쓰면 청소까지 한다. 본체 디스크가 부족하면 `--tmp`로 외장 경로를 지정한다.
- 원본 영상·프레임이 외장에 있으면 경로를 절대경로로 고정해 두고, 이동했다면 인수인계 문서(`AI_AGENT_HANDOFF.md` 등)를 갱신한다.

### 1. 종합

- 테스터별 md를 모두 읽고 **주제별 표**를 만든다: 주제 × 참가자 → (관찰 / 발언 원문 / 근거 프레임 후보).
- 우선순위는 **겪은 인원수**로만 정한다. High/Medium 라벨, 점수(60/100), 전환 가능성 % 금지.
- 참가자는 A, B, C… 로만 부른다. 실명·연령·성별·기기 모델을 문서에 남기지 않는다.
- 분량: 5명 = 20p, 8명 = 30p. 참가자 1인당 1페이지 + 주제 페이지 + 앞 3장(표지·방법·요약) + 뒤 3장(반복 반응·먼저 고칠 5가지·결론).

### 2. 캡처 (references/screenshots.md 필수)

- **원본 MP4에서 ffmpeg로 직접 추출**한다. 기존 `frames_5s`, `evidence_frames`는 절반 해상도인 경우가 흔하다. 각 파일 해상도를 `ffprobe`의 원본 해상도와 대조한다.
- 프레임 번호로 고르지 않는다. 시트를 만들어 눈으로 고른다. 핵심 요소(오류 배너 등)는 `scripts/find_color_band.py`로 **픽셀 색으로 존재를 검증**한다. 시트 오독으로 배너 없는 프레임을 넣은 적이 있다.
- 크롭: 모바일 웹은 상태바·주소창·브라우저 하단 컨트롤을 잘라내고 **앱 자체 하단 탭바는 남긴다**. 데스크톱은 브라우저 탭·북마크·작업표시줄을 잘라낸다(개인정보). `scripts/crop_frames.py` 프리셋 사용.
- 개인정보 프레임 금지: 사진첩, 실명, 이메일, 계정, 브라우저 북마크의 학교·회사명.
- 크기: 한 행 1장=62mm / 2장=54mm / 3장=46mm 폭. 더 작으면 "너무 작다"는 지적을 받는다. 캡처가 많으면 폭을 줄이지 말고 **캡처 전용 행**으로 분리한다.
- 정렬: 행마다 `--ih`(이미지 세로)를 고정하고 `img{height:var(--ih);width:auto}`. 테스터마다 화면비가 달라 폭 기준으로는 상·하단이 안 맞는다.
- 행 폭 합계가 본문 폭(180mm)을 넘으면 Chrome이 **모든 페이지를 일괄 축소**한다(전 페이지 흰 테두리 증상). 가로형 캡처는 폭 = ih ÷ (세로/가로) 로 계산해 행을 짠다.

### 3. 빨간 네모 (references/screenshots.md §5 필수)

- **테두리만** 그린다. 화면 위에 글자·라벨·화살표를 얹지 않는다. 설명은 캡션에, 강조는 캡션 안 빨간 글씨로.
- 좌표는 **눈대중 % 금지**. 색 있는 대상은 `find_color_band.py`로 자동 산출, 나머지는 `mark_review_sheet.py`로 실제 그린 시트를 보고 전수 보정한다.
- 크롭을 바꾸면 모든 좌표가 무효화된다. **크롭 확정 → 마크 산출** 순서.
- 대상이 크롭 경계에 잘려 있으면 마크를 늘리지 말고 **크롭을 넓힌다**.
- 마크 남발 금지: 캡션의 빨간 강조가 이미 설명하는 장면(빈 화면, 잘린 차트 전체)은 네모를 생략한다. 네모는 대상 요소만 감싸고 무관한 탭·안내문까지 넓히지 않는다.

### 4. 작성 (references/writing-style.md 필수)

- 페이지 제목은 질문형("~했을까?"). 각 주제 페이지: 서술 문단 → 카드 2개(잘 된 것/걸린 것) → 캡처 행 → 인용.
- 인용은 **참가자 발언 원문 그대로**. 문법이 어색해도 다듬지 않는다. 타임스탬프를 붙이지 않는다.
- 대시(—) 금지 → 콜론(:) 또는 괄호. 영문 라벨 금지. 격언조 금지. 자료 인벤토리 나열 금지. 명사형 종결 리스트 금지. 녹화 시간 수치 금지.
- 결론부는 비유("관문을 넓히고 무기를 꺼낸다") 대신 "먼저 ~하고, 다음으로 ~하고, 마지막으로 ~한다"로 직설.
- "이 리포트의 한계"는 부정문("~는 드러나지 않았다") 대신 "첫 사용의 기록으로 읽어 달라, 장기 경험은 다음 테스트에서"처럼 **다음 의뢰로 잇는 문장**으로.
- 인원 표기: 표지·개요는 클라이언트가 원하는 숫자(모집 인원)로 쓰되, 개요에서 "테스트 참가 10명, 기록 상세 분석 8명(A~H)"처럼 본문 참가자 수와 모순 없이 잇는다.
- 없는 말을 만들지 않는다. 여백을 채울 때도 분석 md의 실제 관찰·인용·미사용 캡처로만 채운다.

### 5. 배치와 밀도

- 하단 여백 **평균 29% 이하, 40% 초과 페이지 0개**. 클라이언트는 꽉 찬 보고서를 좋아한다. `scripts/qa_pages.py`로 측정한다.
- 이미지를 페이지 가운데 홀로 띄우지 않는다. 단독 이미지는 왼쪽 + 오른쪽 관찰 정리 박스로 짝을 맞춘다.
- 관찰 박스는 내용만큼만(height:100% 금지). 텍스트 아래 빈 공간이 생기면 지적받는다.
- 캡처 행이 본문 오른쪽 끝까지 꽉 차게(플러시) 두지 않는다. 이미지를 줄여 중앙 정렬하거나 여유를 남긴다.
- 좌우로 나눈 인용 박스는 같은 줄끼리 높이를 맞춘다(`.qs .q{flex:1}`).

### 6. 표지

- **시네마틱 다크 표지가 표준**: 브랜드색을 아주 어둡게 깐 세로 그라디언트 + 가장자리 비네트, 중앙에 세리프 로고(80px 안팎)와 "사용자 피드백 보고서"(13~14px)만.
- 인원·플랫폼·일정 카드, 서비스 한 줄 소개는 표지에 넣지 않고 2p 조사 개요로 보낸다.
- 표지 시안이 필요하면 5종(미니멀·스포트라이트·초대형 타이포·골드 프레임·필름 크레딧)을 한 PDF로 뽑아 번호로 고르게 한다. `design-tokens.md` 참고.

### 7. 렌더와 QA

```bash
bash "${CODEX_HOME:-$HOME/.codex}/skills/ux-feedback-report-builder/scripts/render_pdf.sh" \
  --html "report_source/report.html" --out "report.pdf" [--tmp /Volumes/외장/tmp]
python3 "${CODEX_HOME:-$HOME/.codex}/skills/ux-feedback-report-builder/scripts/qa_pages.py" report.pdf --sheet qa_sheet.png
python3 "${CODEX_HOME:-$HOME/.codex}/skills/ux-feedback-report-builder/scripts/lint_text.py" report_source/report.html
```

- `qa_pages.py`: 페이지 수, 페이지별 하단 여백률, 평균/최대, 축소 증상(전 페이지 흰 테두리) 감지, 시트 PNG.
- `lint_text.py`: 대시, 영문 라벨, 심각도 라벨, 점수, 타임스탬프, 녹화 시간, 인벤토리 나열, 금지어.
- 시트를 **눈으로** 본다. 잘림, 겹침, 마크 위치, 캡션 오탈자, 검정 띠(크롭이 이미지보다 큼).
- `references/qa-checklist.md`를 하나씩 확인하고, 사용자에게 보고할 때 미확인 항목은 미확인이라고 쓴다.

## 완료 조건

- PDF 페이지 수가 약속한 분량(20 또는 30)과 정확히 일치
- 모든 캡처가 원본 해상도, 크롭 규칙 준수, 개인정보 0건
- 모든 빨간 네모가 검수 시트로 확인됨
- `lint_text.py` 통과, 여백률 기준 통과
- 참가자 발언 원문 유지 확인
- 마지막 페이지에 "수정 완료 확인 방법"(재검증 시나리오) 포함
- 표준 문서(프로젝트 폴더의 `보고서_작성_표준.md` 등)가 있으면 이번에 새로 확정된 규칙을 거기에도 통합

## 금지

- 심각도 라벨, 점수, 전환 가능성 %
- 화면 위 텍스트 주석, 눈대중 마크 좌표
- 다크 박스·배너·폰 목업·자체 브랜딩·영문 eyebrow 라벨(본문)
- 참가자 발언 다듬기, 타임스탬프
- 지어낸 관찰·인용
- 사용자에게 확인 없이 분량·구조 변경

## 새 규칙이 생겼을 때

클라이언트나 운영자가 새로 지적하면 (1) 그 프로젝트의 표준 문서에 반영하고 (2) 이 스킬의 해당 `references/` 파일과 `lessons-log.md`에 날짜와 함께 추가하고 (3) 저장소에 커밋한다. 이 스킬은 살아 있는 문서다.
