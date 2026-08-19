---
name: app-qa-gate
description: Run a resource-conscious QA gate for Flutter, Swift/Xcode, UIKit, SwiftUI, React Native, or Expo apps. Use when asked to validate an app, prepare it for manual QA, avoid simulator conflicts, decide whether simulator or physical-device testing is necessary, or verify an app up to the TestFlight boundary without uploading unless explicitly authorized.
---

# App QA Gate

Validate the cheapest reliable layer first, protect shared simulator and device state, and report exactly which QA surfaces have and have not passed.

## Workflow

1. Read the global and project `AGENTS.md` chain. Project-specific commands and stricter rules win.
2. Inspect the repository to identify the framework, app targets, documented commands, existing tests, and native integrations. Do not change code during a review-only request.
3. Inspect current resource state before native work:
   - available internal-disk space;
   - current memory pressure when relevant;
   - already booted simulators or connected devices;
   - whether another app or process appears to own the shared QA surface.
4. Run the repository's existing headless checks in the documented order. Do not invent a broad dependency update or add tests merely to satisfy this gate.
5. Decide the next QA surface using the matrix below.
6. Boot or operate a simulator only when the user requested it or the applicable project instructions require it. Preserve another task's running app and simulator state.
7. Treat TestFlight as a separate, explicit release action. If upload was not requested, stop at a readiness report. If upload was requested, invoke `ios-testflight-publisher` and obey its identity and approval gates.
8. Report evidence and remaining manual checks without upgrading an unverified state to complete.

## Headless checks

Prefer repository commands. When none are documented, select only applicable checks:

- Flutter: `flutter analyze`, `flutter test`, and a no-sign iOS build only when native compilation evidence is required.
- Swift Package: `swift test`.
- Xcode app: targeted Swift Testing/XCTest commands and a generic iOS build when the scheme supports it.
- React Native or Expo: repository lint, typecheck, unit tests, and documented non-interactive build checks.

Do not redirect Flutter tests through an external `TMPDIR`. Keep cache or derived-data relocation separate from the test process unless the repository already proves that setup.

## QA surface decision

| Change or risk | Minimum surface |
| --- | --- |
| Pure logic, parsing, copy, or data transformation | Headless tests |
| Ordinary layout, navigation, gestures, or animation | Headless checks, then simulator when interaction evidence is required |
| Native plugin or platform channel | Headless checks plus simulator; physical device when hardware or OS behavior matters |
| Permissions, push, camera, microphone, photos, deep links, StoreKit, keychain, background execution | Physical device or TestFlight |
| Launch time, memory, battery, thermal behavior | Release build on a physical device |
| Release candidate | Headless checks, focused simulator smoke test when authorized, then explicit TestFlight/device QA |

Flutter widget and unit tests do not prove native permission dialogs, notifications, platform views, or hardware behavior. Simulator results do not prove physical-device performance.

## Shared simulator rules

- Use only an existing `iPhone 17 Pro` unless the user explicitly names another device.
- Never create simulator clones or boot multiple simulators for parallel testing.
- Before booting, run a read-only booted-device check and inspect whether another relevant process is using it.
- Never shut down, erase, reset, uninstall, replace the running app, or change device state owned by another task or the user.
- If occupied, return `SIMULATOR DEFERRED` with the completed headless evidence and the exact pending scenario.
- After authorized QA, shut down only the simulator this task booted. Do not shut down a simulator that was already running.

## TestFlight boundary

- Do not archive, sign, upload, increment a build number, create an App Store Connect record, or change tester groups without an explicit request covering that action.
- Use `app-release-preflight` for a release-readiness audit.
- Use `ios-testflight-publisher` only after an explicit TestFlight request.
- Distinguish `build passed`, `archive created`, `upload accepted`, `processing`, `ready to test`, and `installed on device`.

## Output

Return one status per surface:

- `HEADLESS: PASS | FAIL | BLOCKED | NOT APPLICABLE`
- `SIMULATOR: PASS | FAIL | DEFERRED | NOT REQUESTED | NOT APPLICABLE`
- `DEVICE: PASS | FAIL | USER QA REQUIRED | NOT REQUESTED | NOT APPLICABLE`
- `TESTFLIGHT: READY FOR PREFLIGHT | NOT READY | UPLOAD NOT REQUESTED | <verified live state>`

List commands run, observable results, resource or ownership conflicts, and the smallest next manual scenario. Never say the app is fully QA-complete unless every required surface was observed during the current task.
