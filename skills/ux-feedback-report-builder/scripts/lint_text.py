#!/usr/bin/env python3
"""보고서 HTML 본문의 'AI티'를 기계적으로 검출한다. writing-style.md 금지표의 자동화 가능한 부분.

사용:
  lint_text.py report_source/report.html [--strict] [--allow-words 파일]

검출 항목:
  - 대시(— – ―)와 문장 구분용 하이픈(" - ")   ※ 날짜 표기 "2026.08.11 - 14" 는 허용
  - 영문 대문자 라벨 (EXECUTIVE SUMMARY, KEY FINDINGS, INSIGHT 등)
  - 심각도 라벨 (High/Medium/Low, 높음/중간/낮음 + 심각도)
  - 점수/퍼센트 판정 (60/100, 전환 가능성 72%)
  - 타임스탬프 (03:12, [12:40], 12분 30초)
  - 녹화 시간 수치 (62분 12초, 총 녹화, 평균 N분)
  - 자료 인벤토리 나열 (영상 N본, 전사 N건, 프레임 N장)
  - 격언·비유 자주 쓰는 단어 (관문, 무기, 여정, 진정한, 궁극적으로 …) → 경고
  - 명사형 종결 리스트 항목 (li 가 "설정", "수집", "확인" 등으로 끝남) → 경고
  - 말줄임표(…, ...) 로 자른 인용 → 경고
  - 실명 의심: 인용 표기가 "참가자 X" 형식이 아닌 것 → 경고

--strict 는 경고도 실패로 취급.
"""
import argparse, html as htmllib, re, sys
from pathlib import Path

DASH = re.compile(r"[—–―]|(?<=\S) - (?=\S)")
DATE_RANGE = re.compile(r"\d{4}\.\d{2}\.\d{2}\s*[-–]\s*\d{2}")
ENG_LABEL = re.compile(r"\b(EXECUTIVE SUMMARY|KEY FINDINGS?|INSIGHTS?|OVERVIEW|METHODOLOGY|RECOMMENDATIONS?|USER FEEDBACK REPORT|SUMMARY|FINDINGS|NEXT STEPS)\b")
SEVERITY = re.compile(r"\b(High|Medium|Low|Critical)\b|심각도\s*[:：]?\s*(높음|중간|낮음)|\((높음|중간|낮음)\)")
SCORE = re.compile(r"\d{1,3}\s*/\s*100|전환\s*가능성\s*\d{1,3}\s*%|점수\s*\d")
TIMESTAMP = re.compile(r"\[?\b\d{1,2}:\d{2}(?::\d{2})?\b\]?")
REC_TIME = re.compile(r"\d+\s*분\s*\d+\s*초|총\s*녹화|녹화\s*(분량|시간)|평균\s*\d+\s*분")
INVENTORY = re.compile(r"(영상|전사|프레임|캡처)\s*\d[\d,]*\s*(본|건|장)\s*[,·]")
CLICHE = re.compile(r"관문|무기|여정|진정한|궁극적|패러다임|시너지|혁신적|게임\s*체인저|핵심\s*가치를\s*재정의|한마디로")
ELLIPSIS = re.compile(r"…|\.\.\.")
NOUN_END = re.compile(r"(설정|수집|확인|검증|분석|정리|점검|입력|등록|저장|탐색|이동|선택|완료|시도|테스트)\s*$")
QUOTE_TAG = re.compile(r'<span class="w">([^<]+)</span>')
PARTICIPANT = re.compile(r"^참가자\s+[A-Z](\s*[·:]|$|\s*(가|는|이|의)\s)")  # "참가자 B", "참가자 B · 상황 설명" 허용


def strip_tags(s: str) -> str:
    s = re.sub(r"<style.*?</style>", "", s, flags=re.S)
    s = re.sub(r"<[^>]+>", "", s)
    return htmllib.unescape(s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--strict", action="store_true")
    a = ap.parse_args()
    raw = Path(a.html).read_text(encoding="utf-8")

    # 페이지 단위로 나눠 위치를 보고
    pages = re.split(r'<div class="page', raw)[1:]
    errors, warns = [], []

    for i, pg in enumerate(pages, 1):
        text = strip_tags(pg)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        joined = "\n".join(lines)

        for m in DASH.finditer(joined):
            ctx = joined[max(0, m.start() - 25): m.end() + 25].replace("\n", " ")
            if DATE_RANGE.search(ctx):
                continue
            errors.append((i, "대시", ctx))
        for m in ENG_LABEL.finditer(joined):
            errors.append((i, "영문 라벨", m.group(0)))
        for m in SEVERITY.finditer(joined):
            errors.append((i, "심각도 라벨", joined[max(0, m.start()-15): m.end()+15].replace("\n", " ")))
        for m in SCORE.finditer(joined):
            errors.append((i, "점수/퍼센트 판정", m.group(0)))
        for m in TIMESTAMP.finditer(joined):
            ctx = joined[max(0, m.start()-12): m.end()+12].replace("\n", " ")
            # 시각 표기(예: 오후 3:00)는 UX 관찰일 수 있어 경고로
            warns.append((i, "타임스탬프", ctx))
        for m in REC_TIME.finditer(joined):
            errors.append((i, "녹화 시간", joined[max(0, m.start()-15): m.end()+15].replace("\n", " ")))
        for m in INVENTORY.finditer(joined):
            errors.append((i, "자료 인벤토리", joined[max(0, m.start()-15): m.end()+25].replace("\n", " ")))
        for m in CLICHE.finditer(joined):
            warns.append((i, "격언/비유 어휘", joined[max(0, m.start()-20): m.end()+20].replace("\n", " ")))
        for m in ELLIPSIS.finditer(joined):
            warns.append((i, "말줄임표", joined[max(0, m.start()-25): m.end()+5].replace("\n", " ")))
        for li in re.findall(r"<li[^>]*>(.*?)</li>", pg, flags=re.S):
            t = strip_tags(li).strip()
            if NOUN_END.search(t) and len(t) < 40:
                warns.append((i, "명사형 종결 li", t))
        for m in QUOTE_TAG.finditer(pg):
            w = strip_tags(m.group(1)).strip()
            if not PARTICIPANT.match(w):
                warns.append((i, "인용 표기", w))

    def show(kind, items):
        if not items:
            return
        print(f"\n[{kind}] {len(items)}건")
        for p, k, ctx in items:
            print(f"  p{p:02d} {k}: {ctx}")

    show("실패", errors)
    show("경고", warns)
    if not errors and not warns:
        print("통과: 검출 0건")
    print(f"\n요약: 실패 {len(errors)} / 경고 {len(warns)} / 페이지 {len(pages)}")
    print("참고: 격언조·비유·복붙 문장은 기계로 못 잡는다. 최종본은 처음부터 끝까지 사람이 읽는다.")
    sys.exit(1 if errors or (a.strict and warns) else 0)


if __name__ == "__main__":
    main()
