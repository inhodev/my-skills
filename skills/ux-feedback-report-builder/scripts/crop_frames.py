#!/usr/bin/env python3
"""기기 프리셋으로 프레임을 크롭한다. 원본 해상도 경고, 경계 미리보기(--probe) 포함.

사용:
  crop_frames.py --preset ios_safari raw/m_p2_fail.jpg -o img/m_p2_fail.jpg
  crop_frames.py --box 0,145,1920,1026 raw/d_p7_cal.jpg -o img/d_p7_cal.jpg
  crop_frames.py --preset android_chrome raw/*.jpg --outdir img/
  crop_frames.py --preset ios_safari raw/m_p2_fail.jpg --probe probe.jpg   # 크롭선만 그려서 확인
  crop_frames.py --list

프리셋은 실측값이다. 새 프로젝트에서는 한 프레임을 --probe 로 먼저 확인하고, 다르면 --box 로 직접 준다.
크롭 규칙: 상태바·주소창·브라우저 하단 컨트롤은 제거, 앱 자체 하단 탭바는 유지, 데스크톱은 브라우저 탭/북마크/작업표시줄 제거.

필요: Pillow
"""
import argparse, sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("pip install pillow", file=sys.stderr); sys.exit(2)

# name: (expected_w, expected_h, left, top, right, bottom)  — right/bottom 은 None 이면 이미지 끝
PRESETS = {
    "ios_safari":        (884, 1920, 0, 120, None, 1755),   # 880~884 폭
    "ios_top_address":   (1290, 2796, 0, 255, None, 2565),
    "android_chrome":    (1080, 2400, 0, 215, None, 2272),
    "desktop_chrome":    (1920, 1080, 0, 145, None, 1026),  # 브라우저 UI·작업표시줄 제거
    "desktop_chrome_wide": (2560, 1440, 0, 190, None, 1370),
}


def crop_one(src: Path, box, dst: Path = None, probe: Path = None, expect=None):
    im = Image.open(src)
    w, h = im.size
    l, t, r, b = box
    r = w if r is None else r
    b = h if b is None else b
    warn = []
    if expect and (abs(w - expect[0]) > 8 or abs(h - expect[1]) > 8):
        warn.append(f"해상도 {w}x{h} ≠ 프리셋 기대 {expect[0]}x{expect[1]} (절반 해상도 파일이거나 다른 기기)")
    if r > w or b > h or l < 0 or t < 0:
        warn.append(f"크롭 박스 {box}가 이미지({w}x{h})를 벗어남 → 검정 패딩 생김. 원본 해상도 확인")
        r, b = min(r, w), min(b, h)
    if probe:
        pv = im.convert("RGB").copy()
        d = ImageDraw.Draw(pv)
        d.rectangle([l, t, r - 1, b - 1], outline=(255, 0, 0), width=max(3, w // 300))
        pv.save(probe)
        print(f"probe: {probe}  box=({l},{t},{r},{b})  원본 {w}x{h}")
    if dst:
        out = im.crop((l, t, r, b))
        dst.parent.mkdir(parents=True, exist_ok=True)
        out.save(dst, quality=94)
        print(f"crop: {src.name} {w}x{h} → {dst} {out.size[0]}x{out.size[1]}  ratio {out.size[1]/out.size[0]:.3f}")
    for x in warn:
        print(f"  경고: {x}")
    return warn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="*")
    ap.add_argument("--preset", choices=sorted(PRESETS))
    ap.add_argument("--box", help="left,top,right,bottom (px)")
    ap.add_argument("-o", "--out")
    ap.add_argument("--outdir")
    ap.add_argument("--probe", help="크롭선을 그린 미리보기 저장 경로 (단일 입력)")
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()

    if a.list:
        for k, v in PRESETS.items():
            print(f"{k:22s} 기대 {v[0]}x{v[1]}  box=({v[2]},{v[3]},{v[4] or 'W'},{v[5]})")
        return
    if not a.inputs:
        ap.error("입력 파일 필요")
    if a.box:
        box = tuple(int(x) if x.strip() else None for x in a.box.split(","))
        expect = None
    elif a.preset:
        p = PRESETS[a.preset]; box = p[2:]; expect = p[:2]
    else:
        ap.error("--preset 또는 --box 필요")

    total_warn = 0
    for s in a.inputs:
        src = Path(s)
        if a.probe:
            crop_one(src, box, None, Path(a.probe), expect); continue
        if a.out:
            dst = Path(a.out)
        elif a.outdir:
            dst = Path(a.outdir) / src.name
        else:
            ap.error("-o 또는 --outdir 필요")
        total_warn += len(crop_one(src, box, dst, None, expect))
    sys.exit(1 if total_warn else 0)


if __name__ == "__main__":
    main()
