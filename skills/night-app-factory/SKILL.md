---
name: night-app-factory
description: Use when several mobile-app ideas must be turned into separate app projects through a durable queue, separate Codex sessions, unattended monitoring, and at most two concurrent maker jobs.
---

# Night App Factory

## Outcome

Operate a recoverable multi-app factory while the user is away. Build every supplied idea; market research strengthens each product and never decides which ideas deserve implementation.

Each app has one owning session and durable artifacts. The coordinator owns queue state, concurrency, monitoring, recovery, and the morning report. A session being unread, quiet, or final is never a state signal by itself.

## Route and Limits

Use this skill for multiple apps, queues, overnight work, session creation, monitoring, or concurrency. For one app with ten references, use `reference-first-mobile-app` instead.

Default to at most two active maker jobs, and obey any lower user limit. A maker slot covers resource-heavy implementation, compile/test, rendering, and correction work for one app. Research and brief writing may run outside maker slots only when they do not create equivalent CPU/memory pressure. Never exceed the user’s global subagent/session limit.

## Durable Control Plane

Read [references/state-machine.md](references/state-machine.md) and [references/session-contract.md](references/session-contract.md) before dispatch.

Create a factory directory containing:

- `factory-state.json`, managed only through `scripts/factory_queue.py`;
- one isolated project directory per app;
- `MORNING_REPORT.md` generated from current state plus verified artifact links;
- event and command logs under each app’s evidence directory.

Initialize the queue before creating worker sessions. The script refuses a third active maker and enforces FIFO among ready or correction-ready jobs.

## Intake

Normalize every idea without ranking it out of the queue. Preserve user order, app name, description, target framework, reference paths, language requirements, constraints, and acceptance criteria.

For every app create these durable outputs:

1. `00_IDEA.md`
2. `01_MARKET_ENHANCEMENT.md`
3. `02_PRODUCT_SPEC.md`
4. `03_DESIGN_SYSTEM.md`
5. `04_BUILD.md`
6. `05_HEADLESS_QA.md`
7. Korean and English capture directories
8. `USER_QA.md`

Research competitors, current demand, community language, hooks, and feature opportunities to improve the supplied concept. Do not return a go/no-go verdict and do not silently replace the idea.

If a coherent ten-screen packet is supplied, bind it to the app. If absent, create the product flow and a coherent ten-screen visual packet using the available image-generation/design skills before maker work. Do not fall back to generic UI merely because the user is asleep.

## Dispatch

Create or reuse one user-visible Codex session per app only when the user authorized session creation, as invoking this factory normally does. Record the exact thread/task ID with `factory_queue.py bind`.

Send each worker a self-contained contract containing:

- app ID, idea and absolute project path;
- artifact checklist and current queue phase;
- reference packet and required framework;
- Korean default plus complete English localization;
- forbidden paths and simulator/device/TestFlight boundaries;
- exact maker-slot rule and verification commands;
- instruction that it is not alone in the workspace and must preserve others’ edits.

The same app session owns discovery, design, maker work, corrections, and QA. Do not create a fresh session for every phase. When its ten-screen packet is ready, require that same worker session to use **REQUIRED SUB-SKILL:** `reference-first-mobile-app`.

## Scheduler Loop

Repeat until every app is `USER_QA`, `COMPLETE`, or `ATTENTION`:

1. Inspect `factory-state.json` and actual session status.
2. Advance lightweight discovery/design work in user order.
3. Mark a job `BUILD_READY` only when its product and visual contracts exist.
4. Reserve the next FIFO maker slot with `factory_queue.py reserve` before telling a worker to implement or run resource-heavy commands.
5. Monitor the recorded thread/task ID using cursors or compact wait snapshots, not read/unread state.
6. Validate worker claims against project artifacts, logs, captures, and exit codes.
7. Advance the active job through `BUILD` or `CORRECTION`, `HEADLESS_QA`, and `VISUAL_QA` in the same session.
8. Settle it to `USER_QA`, `COMPLETE`, `CORRECTION_READY`, or `ATTENTION`; settlement releases the slot atomically.
9. Immediately admit the next eligible job.

Heartbeat only while a maker session is actually active. After coordinator restart, reload state, inspect every recorded session and artifact, then reconcile reservations. Never free a slot merely because a heartbeat is old; confirm the process/session is no longer active first.

## Failure and Correction Policy

A failure belongs to one app. Do not block the entire queue because one app has a build failure, missing key, repeated design defect, or user-only decision.

- Recoverable defect: settle to `CORRECTION_READY`, append it to the fair queue, continue other apps, then reacquire a maker slot.
- External authority or unavailable state: settle only that app to `ATTENTION`, record exact evidence and the next safe action, continue others.
- Worker final message without evidence: keep its state unchanged and request correction in the same session.
- Worker asks a harmless question while the user sleeps: choose the safest reversible assumption, record it, and continue.

Do not mark an app complete from a title, final message, build alone, or existing PNG alone. `USER_QA` means the working local app passed permitted automated/headless/visual gates and only explicitly listed user/device surfaces remain.

## Morning Report

Generate the state portion with `factory_queue.py report`, then enrich it with verified absolute links. Report in user order:

- app name, current phase, owning session ID, and last verified event;
- implemented product and exact project path;
- market/spec/design/build/QA/capture links;
- analysis, test, build, smoke and visual verdicts;
- provider, permission, purchase, simulator/device and TestFlight boundaries;
- correction attempts or attention reason;
- next user action.

Also report observed maximum active maker count. Never claim that eight hours elapsed, a session was watched, or an app completed unless the durable timeline and artifacts support it.

## Red Flags

- Creating many implementation sessions before slots exist
- Using user read/unread status as coordination
- Treating a worker’s final response as completion evidence
- Starting a correction while two maker slots are occupied
- Recreating a session for every phase and losing context
- Letting one blocked app stop unrelated jobs
- Calling build success visual, simulator, device, or TestFlight proof
- Producing generic code when a ten-screen visual packet is missing
