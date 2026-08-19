---
name: mobile-app-studio
description: Use when a mobile-app request may mean either building one reference-driven app or orchestrating several app ideas, sessions, queues, or overnight jobs.
---

# Mobile App Studio

## Overview

Route the request once, then hand ownership to the matching execution skill. Do not duplicate either execution workflow here.

## Route

| Request signal | Action |
|---|---|
| One app, one product, one ten-screen reference packet | **REQUIRED SUB-SKILL:** Use `reference-first-mobile-app` immediately. |
| Several ideas/apps, overnight work, queue, session creation, monitoring, or concurrency | **REQUIRED SUB-SKILL:** Use `night-app-factory` immediately. |
| Both paths are plausible and scope is genuinely unclear | Ask the single routing question below, then use the selected sub-skill. |

Do not ask when the user already named a path or supplied enough scope to infer it.

## Routing Question

Ask only:

> 이번 요청은 어느 쪽으로 진행할까요? ① 시안 10장으로 앱 하나를 완성 ② 여러 앱을 큐·세션으로 순차 제작

Accept a plain-language answer; do not require the user to repeat a skill name.

## Composition Rule

When `night-app-factory` dispatches a job containing a ten-screen reference packet, require that worker session to use `reference-first-mobile-app`. The factory owns queue state; the single-app skill owns implementation quality.

Keep active build work at or below the user's limit; default to two when no lower limit is given.

## Red Flags

- Asking despite explicit single-app scope
- Treating several ideas as one app
- Running both workflows simultaneously
- Implementing work in the router instead of handing off
- Counting lightweight planning as build concurrency without evidence of equivalent resource use
