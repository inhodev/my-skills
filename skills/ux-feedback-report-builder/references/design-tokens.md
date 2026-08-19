# 디자인 토큰과 표지

디자인은 새로 발명하지 않는다. `assets/template/report.html`의 CSS를 그대로 쓰고 **`:root` 색 변수만** 바꾼다.

## 1. 색

```css
:root{
  --bg:#FCFBFE;        /* 페이지 배경: 브랜드색을 아주 옅게 섞은 흰색 */
  --card:#FFFFFF;      /* 카드 */
  --ink:#191726;       /* 본문 글자 */
  --gray:#8E8B9A;      /* 보조 글자, 캡션 */
  --line:#E5E1F0;      /* 카드 테두리, 구분선 (브랜드색 10% 정도) */
  --accent:#5B3FD4;    /* 브랜드색: 제목 바, 박스 제목, 통계 숫자, 인용 따옴표 */
  --tint:#F3F0FC;      /* 인용·강조 박스 배경 (브랜드색 5%) */
  --tint-line:#DCD4F4; /* tint 박스 테두리 */
  --red:#C0392B;       /* 빨간 네모, 캡션 강조. 브랜드와 무관하게 고정 */
}
```

- 브랜드색은 서비스 화면에서 추출한다(주 버튼 색). 채도가 너무 높으면 제목에 쓰기 부담스러우니 살짝 어둡게.
- 예시 팔레트: 보라 서비스 `#5B3FD4`, 노랑·크림 서비스는 accent `#B8860B` 계열(노랑 원색은 글자에 못 쓴다), 초록 `#2E7D5B`.
- `--red`는 바꾸지 않는다. 마크와 강조는 항상 같은 빨강.

## 2. 타이포

- 제목(`h1`, `.bt`, `.st .n`, 표지): `NSerif` = Noto Serif KR Bold. `@font-face`로 `fonts/NotoSerifKR-Bold.ttf`, `-Regular.ttf` 로컬 참조.
- 본문: Noto Sans KR (시스템에 있으면 사용, 없으면 sans-serif 폴백. 정확히 맞추려면 TTF를 fonts/에 같이 둔다).
- 크기: h1 20.5px / intro 9.4px / box p 9.2px / li 9.1px / 인용 9.4px / 캡션 7.9px / 머리말 11.5px / 꼬리말 7.6px. 이 크기가 30p 밀도의 기준이다. 키우면 페이지가 넘친다.
- 폰트 파일은 저장소에 넣지 않는다(용량). Google Fonts에서 Noto Serif KR을 받아 `fonts/`에 넣는다.

## 3. 컴포넌트

| 클래스 | 용도 |
|---|---|
| `.page` | 210×297mm, padding 14mm 15mm 16mm, overflow hidden |
| `.hd` `.hdline` | 머리말 "앱이름 \| 사용자 피드백 보고서" |
| `h1` | 질문형 제목, 왼쪽 브랜드색 세로 바(::before) |
| `p.intro` | 페이지 서술 문단 |
| `.box` `.box.tint` | 흰 카드 / 연한 브랜드색 카드 |
| `.box .bt` | 카드 제목 (세리프, 브랜드색) |
| `.g2` `.g3` | 2열·3열 그리드 |
| `ul.li` | 점선 구분 리스트 |
| `.q` `.qs` | 인용 박스(큰따옴표 장식) / 인용 세로 묶음 |
| `.st` `.sts` | "N명 중 M명" 통계 행 |
| `.shots` `.shots.only` | 캡처 행 / 캡처 전용 행(가운데) |
| `.cap` `.iw` `.mk` `.cp` | 캡처 카드 / 이미지 래퍼 / 빨간 네모 / 캡션 |
| `.side` | 캡처 옆 flex:1 영역 |
| `.num .c .t .h .d` | 번호 원 + 제목 + 설명 (먼저 고칠 5가지) |
| `.sp` `.sp-s` | 9px / 6px 세로 간격 |
| `.ft` | 꼬리말 |

금지: 다크 네이비 박스, 배너, 폰 목업 프레임, 자체 브랜딩 로고, 아이콘 남발, 그라디언트 카드(표지 제외).

## 4. 표지 (표준: 시네마틱 다크)

```html
<div class="page cover" style="background:linear-gradient(180deg,#1D1145 0%,#120A2E 55%,#0A0520 100%);">
  <div style="position:absolute;inset:0;background:radial-gradient(ellipse 120% 90% at 50% 38%, transparent 45%, rgba(0,0,0,.55));"></div>
  <div style="position:absolute;left:0;right:0;top:43%;transform:translateY(-50%);text-align:center;">
    <div style="font-family:'NSerif';font-weight:700;font-size:82px;color:#F4EFFF;letter-spacing:-.02em;text-shadow:0 4mm 12mm rgba(0,0,0,.5);">앱이름</div>
    <div style="font-family:'NSerif';margin-top:7mm;font-size:13.5px;color:#CBB9FF;letter-spacing:.1em;">사용자 피드백 보고서</div>
  </div>
</div>
```

- 배경 세 색은 브랜드색을 아주 어둡게 내린 것(명도 10~25%). 보라 서비스면 위 값 그대로, 다른 색이면 같은 명도로 색상만 돌린다.
- 로고 글자색은 거의 흰색에 브랜드색 아주 약간, 부제는 브랜드색 파스텔.
- **표지에는 이 두 줄만.** 인원·플랫폼·일정 카드, 서비스 한 줄 소개, 리드 카피는 넣지 않는다(클라이언트가 전부 빼달라고 함). 그 정보는 2p 조사 개요로.
- 표지에는 머리말·꼬리말 없음.

### 표지 시안이 필요할 때

클라이언트가 고르게 하려면 같은 배경색 계열로 5종을 한 PDF로 뽑는다(각 페이지 우하단에 작게 "시안 N"):
1. 시네마 미니멀: 로고 아래 금색 얇은 선, 하단 3열 크레딧
2. 스포트라이트: 로고 뒤 원형 글로우 + 상단 빛줄기
3. 초대형 타이포: 왼쪽 밖으로 잘려나가는 126px 로고, 좌상단 영문 라벨, 하단 라인 위 3열
4. 골드 프레임: 이중 금색 테두리, 로고 아래 ◆
5. 필름 크레딧: 상단 리드 카피, 하단 빌링 블록

주의: `background-clip:text` 그라디언트 글자는 Chrome PDF에서 깨진다(보라 띠). 단색으로.
경험상 클라이언트는 5번을 고른 뒤 문구를 다 빼달라고 했다 → 그것이 지금의 표준.

## 5. 페이지 밀도 수치

- 하단 여백 평균 29% 이하, 40% 초과 0개. `qa_pages.py`가 측정한다.
- 채우는 순서: 미사용 캡처 → 참가자별 실제 관찰 항목 → 인용. 창작 금지.
- 넘치는 페이지는 인용 1개 제거 → 캡처 ih 4mm 축소 → 리스트 항목 병합 순으로 줄인다. 글자 크기는 건드리지 않는다.
