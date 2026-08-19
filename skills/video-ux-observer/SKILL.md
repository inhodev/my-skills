---
name: video-ux-observer
description: User-test video UX observation and user research synthesis workflow for screen recordings with optional voice audio. Use when the user asks to analyze usability test videos, app/web feedback recordings, UX screen recordings, participant videos, or batches of videos; extract audio, frames, transcripts, screen timelines, UX issues, positive moments, quote candidates, a grounded UX observation report, and a separate research-users synthesis report with personas, segments, and journey map hypotheses.
---

# Video UX Observer

## Overview

Produce grounded UX observation notes from user-test videos. Treat the primary output as research source material first: exact-ish speech, visible screen changes, hesitation, task flow, UX issues, positive points, and report-ready quotes.

Also produce a second, independent user-research synthesis report using the `research-users` skill whenever the input is a user-test/feedback video unless the user explicitly asks for only the observation report.

Do not invent emotions, hidden intent, technical causes, or unseen features. Mark uncertainty explicitly.

## Workflow

1. Confirm or infer input metadata:
   - service name, platform, test date, participant ID, participant info, service description, target user, core validation question.
   - If not provided and not visible, write `확인 필요`.
2. Prepare durable artifacts:
   - Keep artifacts after the run; this workflow is meant for repeated video analysis.
   - Prefer external storage when local disk is tight or the user asks.
   - Use `scripts/prepare_video_analysis.sh` for extraction when available.
3. Inspect both modalities:
   - Audio: extract WAV and transcribe with `whisper-cli` when available.
   - Video: extract 5-second frames, scene-change frames, and contact sheets.
   - Never rely on transcript alone. Match claims to visible screen flow.
4. Handle transcript quality:
   - Use transcript text as a draft, not truth.
   - If STT repeats implausible phrases, hallucinates screen text, or conflicts with the screen, label the section `음성 불명확 / 자동전사 신뢰 낮음`.
   - Preserve filler words and hesitation when audible.
5. Write the UX observation report using `references/report-format.md`.
6. Write the user-research synthesis report:
   - Read the installed `research-users` skill's `SKILL.md` before writing this second output. If it is unavailable, state that the synthesis step could not use that companion skill.
   - Use the completed UX observation report, transcript, and visible-screen notes as the research input.
   - Keep it independent from the UX observation report: do not duplicate the full transcript or screen timeline.
   - Frame personas, segments, and journey maps as evidence-based hypotheses when analyzing a single participant or small sample.
   - Never infer demographics, market size, willingness to pay, or segment prevalence beyond the available evidence. Use `확인 필요`, `근거 부족`, or `가설` where appropriate.
   - Save it as `reports/<participant-slug>_user_research_synthesis.md`.
   - Use `references/user-research-synthesis-format.md`.
7. Verify:
   - Confirm original video location.
   - Confirm audio, frames/contact sheets, transcript files, and report exist.
   - Confirm both markdown reports exist unless the user requested only one report.
   - State any gaps, especially unclear audio or unreadable screen text.

## Artifact Layout

Use a per-video folder under a stable workspace:

```text
video_analysis_workspace/<participant-slug>/
├── audio/audio.wav
├── frames_5s/frame_0001.jpg
├── scene_frames/scene_0001.jpg
├── contact_sheets/sheet_1_30.jpg
├── transcripts/transcript.{txt,srt,json}
└── reports/
    ├── <participant-slug>_feedback_analysis.md
    └── <participant-slug>_user_research_synthesis.md
```

For batch work, process videos in the user's requested order. Complete one participant's extraction, screen review, transcript review, and report before moving to the next unless the user explicitly asks for only preprocessing.

## Preparation Script

Run:

```bash
bash "${CODEX_HOME:-$HOME/.codex}/skills/video-ux-observer/scripts/prepare_video_analysis.sh" \
  --video "/path/to/video.mp4" \
  --workspace "/path/to/project" \
  --slug "participant_slug" \
  --model "/path/to/ggml-medium.bin"
```

Useful flags:

- `--move`: move the source video into `<workspace>/incoming_videos/` before processing.
- `--no-transcript`: skip Whisper transcription.
- `--keep-existing`: do not overwrite existing artifacts.

If the script fails, continue manually with `ffprobe`, `ffmpeg`, `magick montage`, and `whisper-cli`.

## Report Rules

- Use Korean if the user is working in Korean or the video is Korean.
- Quote only actual audible speech. If uncertain, write `[음성 불명확]` or `[전사 확인 필요]`.
- For UX problems, distinguish:
  - observed behavior
  - actual user speech
  - screen-visible cause
  - interpretation
- Severity must be justified by observed impact.
- For screen-only evidence, write "화면 기준" and avoid claiming the user's feeling.

Read `references/report-format.md` before writing the final report.

Read `references/user-research-synthesis-format.md` before writing the second user-research synthesis report.
