# Session and Artifact Contract

## Ownership

One app has one owner session and one isolated project path. Record the session ID before work begins. Reuse that session for discovery, design, implementation, correction and QA so decisions and evidence remain connected.

The coordinator alone mutates queue state and grants maker reservations. A worker must not start implementation, compile/test, render or correction work until its reservation is confirmed. It may perform assigned lightweight research or contract preparation without a slot when resource policy permits.

## Worker Checkpoints

Workers report durable checkpoints, not prose-only status:

| Checkpoint | Required evidence |
|---|---|
| Discovery | market enhancement document with sources and no go/no-go filter |
| Design | product spec, interaction contract, design system, ten-screen map |
| Build ready | exact framework commands and isolated allowed paths |
| Build | real app root, model/action implementation, localization resources |
| Headless QA | analysis/build/test/smoke logs with exit status |
| Visual QA | reference, Korean and English captures plus direct-review report |
| User QA | remaining device/provider/permission/billing checks only |

## Monitoring

Use compact session wait snapshots and stored cursors. A cursor says which events the coordinator already processed; it is not user read state. On every meaningful checkpoint, inspect the actual file or command result before changing phase.

Session final text may trigger inspection but never completion. A quiet session may still be compiling. A user-unread session may be completely finished. Never infer either direction.

## Corrections

Send review defects back to the same app session with exact evidence and pass conditions. Settle the current maker round to `CORRECTION_READY` first so another ready app can use the freed slot. When the corrected app returns to FIFO head, reserve it and continue.

## Boundaries

Do not manipulate a simulator, connected device, TestFlight or external account unless the current user request authorizes it. When simulator QA is authorized, obey project instructions and use only an available iPhone 17 Pro. Report build, archive, upload, Apple processing and installability as separate states.
