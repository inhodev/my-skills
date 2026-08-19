#!/usr/bin/env bash
# HTML → PDF (Chrome headless). 임시 프로필을 지정 위치에 만들고 끝나면 청소한다.
#
# 사용:
#   render_pdf.sh --html report_source/report.html --out report.pdf [--tmp /Volumes/외장/tmp] [--budget 25000]
#
# --tmp   : Chrome 임시 프로필/캐시 위치. 본체 디스크가 부족하면 외장 경로를 준다. 기본은 out 파일 옆 .chrome_tmp
# --budget: virtual-time-budget(ms). 폰트·이미지 로딩 대기. 기본 25000
set -euo pipefail

html=""; out=""; tmp=""; budget=25000
while [[ $# -gt 0 ]]; do
  case "$1" in
    --html) html="$2"; shift 2;;
    --out) out="$2"; shift 2;;
    --tmp) tmp="$2"; shift 2;;
    --budget) budget="$2"; shift 2;;
    -h|--help) sed -n '2,9p' "$0"; exit 0;;
    *) echo "알 수 없는 인수: $1" >&2; exit 2;;
  esac
done
[[ -z "$html" || -z "$out" ]] && { echo "--html 과 --out 은 필수" >&2; exit 2; }
[[ -f "$html" ]] || { echo "HTML 없음: $html" >&2; exit 1; }

chrome=""
for c in \
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  "/Applications/Chromium.app/Contents/MacOS/Chromium" \
  "$(command -v google-chrome || true)" \
  "$(command -v chromium || true)" \
  "$(command -v chromium-browser || true)"; do
  [[ -n "$c" && -x "$c" ]] && { chrome="$c"; break; }
done
[[ -n "$chrome" ]] || { echo "Chrome/Chromium 실행 파일을 찾지 못함" >&2; exit 1; }

html_abs="$(cd "$(dirname "$html")" && pwd)/$(basename "$html")"
out_abs="$(cd "$(dirname "$out")" 2>/dev/null && pwd || pwd)/$(basename "$out")"
[[ -z "$tmp" ]] && tmp="$(dirname "$out_abs")/.chrome_tmp"
mkdir -p "$tmp/profile" "$tmp/tmpdir"

# 디스크 여유 경고 (200MB 미만이면 Chrome이 조용히 멈추는 경우가 있다)
avail_kb="$(df -k "$tmp" | awk 'NR==2{print $4}')"
if (( avail_kb < 204800 )); then
  echo "경고: 임시 경로 디스크 여유가 $((avail_kb/1024))MB 뿐입니다. --tmp 로 다른 볼륨을 지정하세요." >&2
fi

cleanup() {
  rm -rf "$tmp/profile" "$tmp/tmpdir" 2>/dev/null || true
  rmdir "$tmp" 2>/dev/null || true
  # 이전 실행이 남긴 시스템 임시 프로필도 정리 (zsh 글롭 실패를 피하려고 find 사용)
  find /tmp /private/tmp -maxdepth 1 -name '.org.chromium.*' -exec rm -rf {} + 2>/dev/null || true
}
trap cleanup EXIT

TMPDIR="$tmp/tmpdir" "$chrome" \
  --headless --disable-gpu --no-sandbox --disable-crash-reporter --disable-extensions \
  --no-pdf-header-footer --virtual-time-budget="$budget" \
  --user-data-dir="$tmp/profile" \
  --print-to-pdf="$out_abs" "file://$html_abs" >/dev/null 2>&1 || true

if [[ ! -s "$out_abs" ]]; then
  echo "PDF 생성 실패: $out_abs" >&2
  exit 1
fi

pages="$(python3 - "$out_abs" <<'PY' 2>/dev/null || echo '?'
import sys
try:
    import pypdfium2 as p
    print(len(p.PdfDocument(sys.argv[1])))
except Exception:
    print('?')
PY
)"
echo "생성: $out_abs ($(du -h "$out_abs" | cut -f1), ${pages}p)"
