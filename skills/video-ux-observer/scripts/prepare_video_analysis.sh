#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
prepare_video_analysis.sh --video PATH --workspace DIR --slug NAME [--model PATH] [--move] [--no-transcript] [--keep-existing]

Creates durable artifacts for UX video observation:
  audio WAV, 5-second frames, scene frames, contact sheets, optional Whisper transcript.
USAGE
}

video=""
workspace=""
slug=""
model=""
move_source=0
make_transcript=1
overwrite=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --video) video="$2"; shift 2 ;;
    --workspace) workspace="$2"; shift 2 ;;
    --slug) slug="$2"; shift 2 ;;
    --model) model="$2"; shift 2 ;;
    --move) move_source=1; shift ;;
    --no-transcript) make_transcript=0; shift ;;
    --keep-existing) overwrite=0; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
done

if [[ -z "$video" || -z "$workspace" || -z "$slug" ]]; then
  usage >&2
  exit 2
fi

if [[ ! -f "$video" ]]; then
  echo "Video not found: $video" >&2
  exit 1
fi

command -v ffprobe >/dev/null || { echo "ffprobe not found" >&2; exit 1; }
command -v ffmpeg >/dev/null || { echo "ffmpeg not found" >&2; exit 1; }

mkdir -p "$workspace/incoming_videos"
if [[ "$move_source" -eq 1 ]]; then
  target="$workspace/incoming_videos/$(basename "$video")"
  if [[ "$video" != "$target" ]]; then
    mv "$video" "$target"
    video="$target"
  fi
fi

base="$workspace/video_analysis_workspace/$slug"
audio_dir="$base/audio"
frames_dir="$base/frames_5s"
scene_dir="$base/scene_frames"
sheets_dir="$base/contact_sheets"
transcript_dir="$base/transcripts"
report_dir="$base/reports"

mkdir -p "$audio_dir" "$frames_dir" "$scene_dir" "$sheets_dir" "$transcript_dir" "$report_dir"

ffmpeg_y="-y"
if [[ "$overwrite" -eq 0 ]]; then
  ffmpeg_y="-n"
fi

echo "[metadata] $video"
ffprobe -hide_banner -i "$video" 2>&1 | tee "$base/metadata.txt"

echo "[audio] extracting WAV"
ffmpeg "$ffmpeg_y" -i "$video" -vn -ac 1 -ar 16000 "$audio_dir/audio.wav"

echo "[frames] extracting 5-second frames"
ffmpeg "$ffmpeg_y" -i "$video" -vf "fps=1/5,scale=540:-1" "$frames_dir/frame_%04d.jpg"

echo "[frames] extracting scene-change frames"
scene_log="$scene_dir/scene_extract.log"
if ! ffmpeg "$ffmpeg_y" -i "$video" -vf "select='gt(scene,0.25)',scale=540:-1" -fps_mode vfr "$scene_dir/scene_%04d.jpg" > "$scene_log" 2>&1; then
  echo "[frames] no scene-change frames extracted; details: $scene_log"
fi

if command -v magick >/dev/null; then
  echo "[contact-sheets] creating contact sheets"
  shopt -s nullglob
  frame_count=("$frames_dir"/frame_*.jpg)
  total=${#frame_count[@]}
  start=1
  while [[ "$start" -le "$total" ]]; do
    end=$((start + 29))
    args=()
    for n in $(seq "$start" "$end"); do
      f=$(printf "%s/frame_%04d.jpg" "$frames_dir" "$n")
      [[ -f "$f" ]] && args+=("$f")
    done
    if [[ ${#args[@]} -gt 0 ]]; then
      magick montage "${args[@]}" -tile 5x6 -geometry 180x400+8+8 -background white -font /System/Library/Fonts/Helvetica.ttc "$sheets_dir/sheet_${start}_${end}.jpg" || \
      magick montage "${args[@]}" -tile 5x6 -geometry 180x400+8+8 -background white "$sheets_dir/sheet_${start}_${end}.jpg"
    fi
    start=$((start + 30))
  done
else
  echo "[contact-sheets] magick not found; skipped"
fi

if [[ "$make_transcript" -eq 1 ]]; then
  if command -v whisper-cli >/dev/null && [[ -n "$model" && -f "$model" ]]; then
    echo "[transcript] running whisper-cli"
    whisper-cli -m "$model" -l ko \
      --prompt "사용자 테스트 피드백, UX 피드백, 앱 사용성, ChatGPT, Gemini, AI, 프리미엄, 결제, 피벗, 관계 분석, 시그널, 사이 점검, 프로그램" \
      -osrt -oj -otxt \
      -of "$transcript_dir/transcript" \
      "$audio_dir/audio.wav"
  else
    echo "[transcript] skipped; whisper-cli or model missing"
  fi
fi

echo "[done] $base"
