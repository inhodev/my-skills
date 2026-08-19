#!/usr/bin/env python3
"""PDF 납품 전 QA: 페이지 수, 페이지별 하단 여백률, 전 페이지 축소 증상, 검수 시트.

사용:
  qa_pages.py report.pdf [--sheet qa_sheet.png] [--expect 30] [--avg-max 29] [--page-max 40]
             [--cols 6] [--scale 0.45] [--skip-first] [--json out.json]

여백률 정의:
  페이지를 렌더한 뒤, .page 패딩 안쪽 본문 영역(상 14mm ~ 하 16mm 안쪽, 꼬리말 제외)에서 배경색과 다른
  마지막 픽셀 행을 찾고, 그 아래부터 본문 하단 경계까지의 비율(%). 표지(1p)와 어두운 페이지는 제외.
  기준: 평균 29% 이하, 40% 초과 페이지 0개.

축소 증상:
  캡처 행 폭 합계가 본문 폭을 넘으면 Chrome이 모든 페이지를 일괄 축소한다. 증상은 전 페이지 가장자리에
  동일한 흰 테두리. 각 페이지의 4변에서 배경색과 다른 첫 픽셀까지의 거리가 모두 같은 값(>2px)이면 경고.

필요: pypdfium2, Pillow, numpy
"""
import argparse, json, sys
from pathlib import Path

try:
    import pypdfium2 as pdfium
    from PIL import Image, ImageDraw
    import numpy as np
except ImportError as e:
    print(f"필요 패키지 없음: {e}. pip install pypdfium2 pillow numpy", file=sys.stderr)
    sys.exit(2)


def page_metrics(img: Image.Image, footer_frac=0.054, top_frac=0.047):
    # 기본값은 .page 패딩(상 14mm, 하 16mm)의 안쪽 = 본문 영역. 꼬리말(bottom 8mm)은 영역 밖.
    a = np.asarray(img.convert("RGB")).astype(int)
    h, w, _ = a.shape
    # 배경색: 페이지 네 모서리 안쪽(패딩 영역) 픽셀의 최빈값
    corners = np.concatenate([a[2:8, 2:8].reshape(-1, 3), a[2:8, -8:-2].reshape(-1, 3),
                              a[-8:-2, 2:8].reshape(-1, 3), a[-8:-2, -8:-2].reshape(-1, 3)])
    vals, counts = np.unique(corners, axis=0, return_counts=True)
    bg = vals[counts.argmax()]
    diff = (np.abs(a - bg).sum(axis=2) > 24)  # 배경과 다른 픽셀

    # 본문 영역: 상단 머리말 아래 ~ 꼬리말 위
    y0 = int(h * top_frac)
    y1 = int(h * (1 - footer_frac))
    body = diff[y0:y1]
    rows = np.where(body.any(axis=1))[0]
    if len(rows) == 0:
        blank_ratio = 100.0
    else:
        last = rows.max()
        blank_ratio = 100.0 * (body.shape[0] - 1 - last) / body.shape[0]

    # 축소 증상: 4변에서 첫 non-bg까지 거리
    def first_edge(mask_1d):
        idx = np.where(mask_1d)[0]
        return int(idx.min()) if len(idx) else -1
    col_any = diff.any(axis=0); row_any = diff.any(axis=1)
    left = first_edge(col_any); right = first_edge(col_any[::-1])
    top = first_edge(row_any); bottom = first_edge(row_any[::-1])
    return {
        "bg": [int(x) for x in bg],
        "blank_pct": round(blank_ratio, 1),
        "edges": [left, top, right, bottom],
        "dark_page": bool(bg.sum() < 200),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--sheet", default=None, help="검수 시트 PNG 경로")
    ap.add_argument("--expect", type=int, default=None, help="기대 페이지 수")
    ap.add_argument("--avg-max", type=float, default=29.0)
    ap.add_argument("--page-max", type=float, default=40.0)
    ap.add_argument("--cols", type=int, default=6)
    ap.add_argument("--scale", type=float, default=0.45)
    ap.add_argument("--skip-first", action="store_true", default=True)
    ap.add_argument("--include-first", dest="skip_first", action="store_false")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    pdf = pdfium.PdfDocument(args.pdf)
    n = len(pdf)
    print(f"페이지 수: {n}" + (f" (기대 {args.expect})" if args.expect else ""))
    fail = 0
    if args.expect and n != args.expect:
        print(f"  실패: 페이지 수 불일치"); fail += 1

    imgs, metrics = [], []
    for i in range(n):
        im = pdf[i].render(scale=1.0).to_pil()
        m = page_metrics(im)
        m["page"] = i + 1
        metrics.append(m)
        imgs.append(im.resize((int(im.width * args.scale), int(im.height * args.scale)), Image.LANCZOS))

    body = [m for m in metrics if not (args.skip_first and m["page"] == 1) and not m["dark_page"]]
    if body:
        avg = sum(m["blank_pct"] for m in body) / len(body)
        worst = max(body, key=lambda m: m["blank_pct"])
        over = [m["page"] for m in body if m["blank_pct"] > args.page_max]
        print(f"하단 여백률: 평균 {avg:.1f}% (기준 ≤{args.avg_max}), 최대 {worst['blank_pct']}% (p{worst['page']}), "
              f"{args.page_max}% 초과: {over if over else '없음'}")
        if avg > args.avg_max: print("  실패: 평균 여백 초과"); fail += 1
        if over: print("  실패: 페이지 여백 초과"); fail += 1
        print("  페이지별: " + ", ".join(f"p{m['page']}:{m['blank_pct']}" for m in body))

    # 축소 증상
    edges = [tuple(m["edges"]) for m in metrics if not m["dark_page"]]
    if edges:
        common = set(edges)
        if len(common) == 1 and min(edges[0]) > 2:
            print(f"  경고: 전 페이지 가장자리에 동일한 여백 {edges[0]}px → 행 폭 초과로 일괄 축소됐을 가능성. 캡처 행 폭 합계(≤180mm)를 확인.")
            fail += 1
        else:
            print("축소 증상: 없음")

    if args.sheet:
        cols = args.cols
        rows = (n + cols - 1) // cols
        w, h = imgs[0].size
        pad, label_h = 6, 16
        sheet = Image.new("RGB", (cols * (w + pad) + pad, rows * (h + pad + label_h) + pad), "#DDD")
        d = ImageDraw.Draw(sheet)
        for i, im in enumerate(imgs):
            r, c = divmod(i, cols)
            x = pad + c * (w + pad); y = pad + r * (h + pad + label_h)
            sheet.paste(im, (x, y))
            m = metrics[i]
            lab = f"p{i+1}  blank {m['blank_pct']}%"
            col = "#B00" if (m["blank_pct"] > args.page_max and not m["dark_page"] and i > 0) else "#222"
            d.text((x + 2, y + h + 2), lab, fill=col)
        sheet.save(args.sheet)
        print(f"시트: {args.sheet}")

    if args.json:
        Path(args.json).write_text(json.dumps(metrics, ensure_ascii=False, indent=1))

    sys.exit(1 if fail else 0)


if __name__ == "__main__":
    main()
