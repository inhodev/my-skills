#!/usr/bin/env python3
"""색 감지로 빨간 네모 좌표를 자동 산출한다 (눈대중 금지 규칙의 도구).

오류 배너, 브랜드색 버튼, 분홍/빨강 경고처럼 색이 뚜렷한 대상의 위치를 픽셀 스캔으로 찾아
[x%, y%, w%, h%] 를 출력한다. 그대로 marks.json 과 HTML .mk 인라인 스타일에 쓴다.
"존재 검증"에도 쓴다: 시트 축소본에서 배너가 있는 줄 알았는데 없던 적이 있다.

사용:
  find_color_band.py img/m_p2_fail.jpg --preset pink
  find_color_band.py img/x.jpg --rgb 91,63,212 --tol 40 --axis both
  find_color_band.py img/x.jpg --preset pink --min-run 0.6 --pad 1.5
  find_color_band.py img/x.jpg --preset red --roi 0,50,100,100     # 이미지 하단 절반에서만 찾기

옵션:
  --preset pink|red|purple|yellow|green   자주 쓰는 색 판별식
  --rgb R,G,B --tol N                     목표색 ± 허용오차(맨해튼 거리)
  --axis rows|both                        rows: 세로 방향 띠(배너)만 찾아 x는 전폭 / both: 가로세로 모두 감지
  --min-run 0.5                           한 행에서 색 픽셀 비율이 이 이상이어야 '띠'로 인정 (rows 모드)
  --min-frac 0.002                        both 모드에서 색 픽셀이 전체의 이 비율 미만이면 '없음'
  --roi x0,y0,x1,y1 (%)                   탐색 영역 제한
  --pad 1.0                               결과 박스에 더할 여백(%)
  --json                                  JSON 한 줄로 출력

출력이 '없음' 이면 그 프레임에 대상이 없다는 뜻이다. 다른 프레임을 고른다.

필요: Pillow, numpy
"""
import argparse, json, sys

try:
    from PIL import Image
    import numpy as np
except ImportError:
    print("pip install pillow numpy", file=sys.stderr); sys.exit(2)


def preset_mask(a, name):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if name == "pink":    # 연분홍 오류 배너 (실측: R−B>7 & R>225, G 낮음)
        return (r > 225) & ((r - b) > 7) & ((r - g) > 12)
    if name == "red":
        return (r > 170) & (g < 110) & (b < 110)
    if name == "purple":  # 보라 브랜드 버튼
        return (b > 150) & (r > 60) & (g < 120) & ((b - g) > 60)
    if name == "yellow":
        return (r > 200) & (g > 170) & (b < 120)
    if name == "green":
        return (g > 140) & (r < 120) & (b < 140) & ((g - r) > 40)
    raise ValueError(name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("--preset", choices=["pink", "red", "purple", "yellow", "green"])
    ap.add_argument("--rgb"); ap.add_argument("--tol", type=int, default=40)
    ap.add_argument("--axis", choices=["rows", "both"], default="rows")
    ap.add_argument("--min-run", type=float, default=0.5)
    ap.add_argument("--min-frac", type=float, default=0.002)
    ap.add_argument("--roi", default=None)
    ap.add_argument("--pad", type=float, default=1.0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    im = Image.open(a.image).convert("RGB")
    arr = np.asarray(im).astype(int)
    H, W, _ = arr.shape

    if a.rgb:
        t = np.array([int(x) for x in a.rgb.split(",")])
        mask = np.abs(arr - t).sum(axis=2) <= a.tol
    elif a.preset:
        mask = preset_mask(arr, a.preset)
    else:
        ap.error("--preset 또는 --rgb 필요")

    x0 = y0 = 0; x1, y1 = W, H
    if a.roi:
        rx0, ry0, rx1, ry1 = [float(v) for v in a.roi.split(",")]
        x0, x1 = int(W * rx0 / 100), int(W * rx1 / 100)
        y0, y1 = int(H * ry0 / 100), int(H * ry1 / 100)
    sub = mask[y0:y1, x0:x1]

    if a.axis == "rows":
        row_frac = sub.mean(axis=1)
        rows = np.where(row_frac >= a.min_run)[0]
        if len(rows) == 0:
            # 약한 기준으로 재시도해 힌트 제공
            hint = np.where(row_frac >= a.min_run / 3)[0]
            msg = {"found": False, "hint_rows_pct": [round(100 * (y0 + hint.min()) / H, 1), round(100 * (y0 + hint.max()) / H, 1)] if len(hint) else None}
            print(json.dumps(msg) if a.json else f"없음 (min-run {a.min_run} 기준). 약한 힌트: {msg['hint_rows_pct']}")
            sys.exit(1)
        # 가장 긴 연속 구간 선택
        groups = np.split(rows, np.where(np.diff(rows) > 3)[0] + 1)
        g = max(groups, key=len)
        top, bot = y0 + g.min(), y0 + g.max()
        cols = np.where(sub[g.min():g.max() + 1].any(axis=0))[0]
        left, right = x0 + cols.min(), x0 + cols.max()
    else:
        ys, xs = np.where(sub)
        if len(ys) < a.min_frac * sub.size:
            print(json.dumps({"found": False}) if a.json else f"없음 (색 픽셀 {len(ys)}개, 기준 {int(a.min_frac*sub.size)})")
            sys.exit(1)
        top, bot = y0 + ys.min(), y0 + ys.max()
        left, right = x0 + xs.min(), x0 + xs.max()

    px = a.pad
    x_pct = max(0.0, 100 * left / W - px)
    y_pct = max(0.0, 100 * top / H - px)
    w_pct = min(100 - x_pct, 100 * (right - left + 1) / W + 2 * px)
    h_pct = min(100 - y_pct, 100 * (bot - top + 1) / H + 2 * px)
    box = [round(x_pct, 1), round(y_pct, 1), round(w_pct, 1), round(h_pct, 1)]
    if a.json:
        print(json.dumps({"found": True, "box_pct": box, "px": [int(left), int(top), int(right), int(bot)], "size": [W, H]}))
    else:
        print(f"[{box[0]}, {box[1]}, {box[2]}, {box[3]}]   px=({left},{top})-({right},{bot})  img={W}x{H}")
        print(f'HTML: <div class="mk" style="left:{box[0]}%;top:{box[1]}%;width:{box[2]}%;height:{box[3]}%;"></div>')


if __name__ == "__main__":
    main()
