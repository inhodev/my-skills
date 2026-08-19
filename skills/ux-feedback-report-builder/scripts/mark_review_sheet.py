#!/usr/bin/env python3
"""marks.json 의 빨간 네모를 실제 이미지에 그려 검수 시트를 만든다. HTML 에 좌표를 써넣을 수도 있다.

"대부분 뒤틀려 있어" 지적 이후 규칙: 마크는 반드시 그려서 눈으로 확인한 뒤 납품한다.

marks.json 형식 (단위 %, 이미지 파일명에서 확장자를 뺀 키):
  {"m_p2_fail": [[4, 32.6, 92, 6.7]], "d_p7_wide": [[1,3,25,94],[74,3,25,94]]}

사용:
  mark_review_sheet.py --img img/ --marks marks.json --sheet marks_review.png
  mark_review_sheet.py --img img/ --marks marks.json --sheet marks_review.png --only m_p2_fail,d_p7_cal
  mark_review_sheet.py --img img/ --marks marks.json --apply report_source/report.html   # HTML .mk 인라인 좌표 동기화
  mark_review_sheet.py --html report_source/report.html --img img/ --sheet marks_review.png   # HTML 에 박힌 좌표를 그대로 그려서 검수

--apply 는 <img src="img/NAME.jpg"> 바로 다음에 오는 .mk div 들을 marks.json 값으로 교체한다.
  (이미지 하나에 여러 mk 가 있으면 개수도 맞춘다. marks 에 없는 이미지는 건드리지 않는다.)

필요: Pillow
"""
import argparse, json, re, sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("pip install pillow", file=sys.stderr); sys.exit(2)

MK_RE = re.compile(r'<div class="mk" style="left:([\d.]+)%;top:([\d.]+)%;width:([\d.]+)%;height:([\d.]+)%;"></div>')
IMG_RE = re.compile(r'<img src="img/([^"]+?)\.(?:jpg|jpeg|png)">')


def marks_from_html(html: str):
    """이미지 태그 뒤(같은 .iw 안)에 나오는 mk 들을 수집."""
    out = {}
    for m in IMG_RE.finditer(html):
        name = m.group(1)
        # 다음 </div> (iw 닫힘) 전까지의 구간에서 mk 검색
        seg_end = html.find("</div>", m.end())
        # .iw 안에 mk div 가 있으면 첫 </div> 는 mk 의 닫힘이므로, 연속된 mk 를 모두 읽는다
        seg = html[m.end(): m.end() + 800]
        boxes = []
        for mk in MK_RE.finditer(seg):
            # mk 는 img 와 같은 iw 안에서만 인정: 사이에 '<div class="cp"' 나 '<div class="cap"' 가 있으면 중단
            between = seg[: mk.start()]
            if 'class="cp"' in between or 'class="cap"' in between:
                break
            boxes.append([float(v) for v in mk.groups()])
        if boxes:
            out[name] = boxes
    return out


def apply_to_html(html: str, marks: dict):
    changed = 0
    def repl(m):
        nonlocal changed
        name = m.group(1)
        if name not in marks:
            return m.group(0)
        return m.group(0)  # placeholder (실제 치환은 아래 루프)
    # 이미지별로 위치를 찾아 그 뒤의 mk 블록을 교체
    pos = 0
    out = []
    for m in IMG_RE.finditer(html):
        name = m.group(1)
        out.append(html[pos:m.end()]); pos = m.end()
        if name not in marks:
            continue
        # 기존 mk 들 (같은 iw 안) 제거
        seg = html[pos: pos + 800]
        cut = 0
        for mk in MK_RE.finditer(seg):
            between = seg[:mk.start()]
            if 'class="cp"' in between or 'class="cap"' in between:
                break
            cut = mk.end()
        # 기존 mk 앞의 공백/개행 유지
        prefix = seg[:cut]
        lead = re.match(r'\s*', prefix).group(0) if cut else "\n        "
        new = "".join(f'{lead}<div class="mk" style="left:{b[0]}%;top:{b[1]}%;width:{b[2]}%;height:{b[3]}%;"></div>' for b in marks[name])
        out.append(new)
        pos += cut
        changed += 1
    out.append(html[pos:])
    return "".join(out), changed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--img", required=True, help="이미지 폴더")
    ap.add_argument("--marks", help="marks.json")
    ap.add_argument("--html", help="HTML 에서 마크를 읽어 그린다 (marks 대신)")
    ap.add_argument("--sheet", help="검수 시트 PNG")
    ap.add_argument("--only", help="쉼표로 구분한 이미지 키")
    ap.add_argument("--apply", help="marks.json 을 이 HTML 의 .mk 인라인에 써넣는다")
    ap.add_argument("--thumb-w", type=int, default=360)
    ap.add_argument("--cols", type=int, default=5)
    a = ap.parse_args()

    if a.marks:
        marks = json.loads(Path(a.marks).read_text())
    elif a.html:
        marks = marks_from_html(Path(a.html).read_text())
    else:
        ap.error("--marks 또는 --html 필요")
    if a.only:
        keep = set(a.only.split(","))
        marks = {k: v for k, v in marks.items() if k in keep}

    if a.apply:
        p = Path(a.apply)
        html = p.read_text()
        new, changed = apply_to_html(html, marks)
        p.write_text(new)
        print(f"HTML 갱신: {changed}개 이미지의 마크 동기화 → {p}")

    if a.sheet:
        img_dir = Path(a.img)
        tiles = []
        for name, boxes in marks.items():
            src = None
            for ext in (".jpg", ".jpeg", ".png"):
                if (img_dir / f"{name}{ext}").exists():
                    src = img_dir / f"{name}{ext}"; break
            if not src:
                print(f"  경고: 이미지 없음 {name}"); continue
            im = Image.open(src).convert("RGB")
            W, H = im.size
            d = ImageDraw.Draw(im)
            lw = max(3, W // 250)
            for b in boxes:
                x, y, w, h = b
                d.rectangle([W * x / 100, H * y / 100, W * (x + w) / 100, H * (y + h) / 100], outline=(220, 40, 30), width=lw)
            s = a.thumb_w / W
            im = im.resize((a.thumb_w, int(H * s)), Image.LANCZOS)
            tiles.append((name, im, boxes))
        if not tiles:
            print("그릴 마크 없음"); sys.exit(1)
        cols = a.cols
        maxh = max(t[1].height for t in tiles)
        rows = (len(tiles) + cols - 1) // cols
        pad, lab = 10, 30
        sheet = Image.new("RGB", (cols * (a.thumb_w + pad) + pad, rows * (maxh + pad + lab) + pad), "#EEE")
        d = ImageDraw.Draw(sheet)
        for i, (name, im, boxes) in enumerate(tiles):
            r, c = divmod(i, cols)
            x = pad + c * (a.thumb_w + pad); y = pad + r * (maxh + pad + lab)
            sheet.paste(im, (x, y))
            d.text((x + 2, y + im.height + 3), f"{name}  {boxes}", fill="#111")
        sheet.save(a.sheet)
        print(f"검수 시트: {a.sheet} ({len(tiles)}장). 눈으로 확인: 대상이 다 들어왔는가 / 여백 과하지 않은가 / 경계에 잘리지 않았는가")


if __name__ == "__main__":
    main()
