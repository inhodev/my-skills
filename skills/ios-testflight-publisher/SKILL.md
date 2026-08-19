---
name: ios-testflight-publisher
description: Publish, re-upload, prepare, register, or verify Swift/Xcode and Flutter iOS apps for TestFlight. Prefer the local App Studio fast release engine for already registered projects, including automatic project matching, preflight, live App Store Connect build-number selection, archive, IPA export, API-key upload, and processing polling. Fall back to explicit five-candidate identity approval, Apple Developer/App Store Connect registration, and the bundled standalone runner only for new, mismatched, or unsupported projects.
---

# iOS TestFlight Publisher

Use App Studio as the primary execution engine. Do not rebuild the TestFlight workflow from scratch when the project is already registered and its identity matches.

## Non-negotiable rules

- Archive, upload, or tester distribution only when the current user request explicitly authorizes it. Merely invoking this skill or asking to inspect/prepare does not authorize upload.
- Distinguish `BUILT`, `ARCHIVED`, `EXPORTED`, `UPLOADED`, `PROCESSING`, `PROCESSED`, and `TESTABLE`.
- Never expose or copy Apple passwords, 2FA codes, session cookies, `.p8` contents, Issuer ID values, Key ID values, or credential file paths into logs or replies.
- Never run `xcodebuild clean`, delete DerivedData, or reinstall dependencies as a first step. The fast path depends on warm Xcode/SPM/CocoaPods caches.
- Treat Bundle ID as the iOS package identifier. Never guess it from memory.
- Never boot a simulator for archive/upload. If separate app QA is explicitly required, run headless checks first and use only the existing iPhone 17 Pro without taking it from another task.
- Never accept agreements, change account settings, expire builds, stop testing, or remove tester groups without explicit authorization.

## Route first

From the target project root, run the bundled router. Its default is read-only plus App Studio dry-run; it cannot upload without `--upload`.

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/ios-testflight-publisher/scripts/fast_testflight.py" \
  --root .
```

The router must:

1. Match the canonical project path against App Studio inventory.
2. Require an iOS-capable, existing record with no stack mismatch.
3. Inspect source project Bundle IDs and require the App Studio Bundle ID to match.
4. Run App Studio `release --dry-run`, which performs preflight and reads live App Store Connect state without building or uploading.
5. Return `FAST_PATH_READY` only after those gates pass.

If the user explicitly requested TestFlight upload in the current message, run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/ios-testflight-publisher/scripts/fast_testflight.py" \
  --root . --upload
```

Add `--no-wait` only when the user wants upload acceptance without waiting for Apple processing. Add `--verbose` only to diagnose failure output.

## Fast path behavior

Use the fast path for an existing App Studio record whose canonical path and source Bundle ID agree. Do not present five new identity candidates in this case. The registered identity is operational state, not a new identity decision.

App Studio performs:

```text
app lock
→ release preflight
→ live ASC build lookup
→ max(live, TestFlight, local) + 1
→ build-number update
→ xcodebuild archive
→ xcodebuild -exportArchive
→ xcrun altool with ASC .p8 reference
→ exact build-number processing poll
```

The speed does not come from an Apple archive API. Archive and export are local Xcode operations. App Store Connect REST API supplies app/build state; `altool` transfers the IPA. App Studio is faster than a generic agent because it has already fixed scheme discovery, Team detection, ExportOptions generation, build-number selection, credential references, failure hints, and output paths.

Read [references/app_studio_fast_path.md](references/app_studio_fast_path.md) before diagnosing fast-path routing, performance, credentials, or App Studio failures.

## Fallback path

Use the fallback only when the router reports one of these:

- project absent from App Studio inventory;
- path is ambiguous or missing;
- App Studio record and source Bundle ID disagree;
- new app identity or capability registration is requested;
- manual signing, extension profile mapping, or another build shape is unsupported by App Studio;
- App Studio itself is unavailable.

### Inspect

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/ios-testflight-publisher/scripts/inspect_ios_project.py" \
  --root . --pretty
```

Inspect framework, workspace/project, shared scheme, main and extension Bundle IDs, display name, marketing/build version, team, entitlements, and capabilities.

### Identity approval for new or mismatched apps

Only on the fallback identity path, present exactly five `display name + main Bundle ID` candidates. Include the user-supplied pair first or the detected current pair as `현재 감지된 값`. Project files and Apple records are evidence, not approval for a new identity.

Do not register, archive, export, or upload until the user selects one exact pair. After selection, show derived extension/widget identifiers and proven capabilities before external registration.

### Apple registration

Use the visible logged-in Chrome session for:

1. Apple Developer App ID registration;
2. App Store Connect app record creation or exact Bundle ID reuse.

Search by exact Bundle ID, avoid duplicates, enable only entitlements-backed capabilities, and pause for login, 2FA, agreements, team ambiguity, or certificate/private-key decisions. Read [references/apple_workflow.md](references/apple_workflow.md) before browser registration or signing remediation.

### Standalone runner

Use the old runner only when App Studio cannot handle the project shape. Default to dry-run:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/ios-testflight-publisher/scripts/build_testflight.py" \
  --root . --build-number <next-number> --dry-run
```

Actual upload still requires explicit current-turn authorization and `--upload`:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/ios-testflight-publisher/scripts/build_testflight.py" \
  --root . --build-number <next-number> --upload
```

Use `--provisioning-profile` or repeated `--provisioning-profile-map BUNDLE_ID=PROFILE_NAME` only for a proven manual-signing requirement. Never apply manual signing globally to Swift Package targets.

## Verification contract

After any real upload, report each reached state separately:

| State | Evidence |
|---|---|
| `ARCHIVED` | `.xcarchive` exists and archive command exited 0 |
| `EXPORTED` | IPA exists and metadata/signature match |
| `UPLOADED` | Apple upload command accepted the package |
| `PROCESSING` | exact version/build row is visible but not valid yet |
| `PROCESSED` | exact build reached a valid processed state |
| `TESTABLE` | non-expired build is attached to a tester group in `Testing`; external review, territories, and agreements are clear when applicable |

Do not call the release done at archive success or upload acceptance. If the user only authorized upload, stop at the strongest verified state without silently changing tester distribution.

## Failure routing

- App Studio Bundle ID mismatch: do not upload; inspect source and inventory, then use the identity fallback.
- `No profiles for ...`: inspect Team, target capabilities, App ID, and Xcode account; do not change signing blindly.
- `Missing or invalid signature`: inspect the exported profile, embedded extensions, deep signature, and executable name.
- redundant build number: query live ASC, choose a strictly higher number, and rebuild once.
- Flutter `PathNotFoundException` after `destination=upload`: check ASC first; upload may already have succeeded.
- Apple processing failure: report the exact Apple message and inspect the uploaded artifact before rebuilding.
- browser login/2FA/permission block: request the exact visible user action and resume from that step.
- fast path is slow: preserve caches, inspect per-step `ms`, and separate archive, export, upload acceptance, processing, and testable time.

## Bundled resources

- `scripts/fast_testflight.py`: App Studio path/identity router; dry-run by default, `--upload` required for mutation.
- `scripts/inspect_ios_project.py`: standalone read-only project inspector.
- `scripts/build_testflight.py`: fallback archive/export/upload runner.
- `references/app_studio_fast_path.md`: engine location, commands, API/key boundaries, cache and timing contract.
- `references/apple_workflow.md`: new identity, capabilities, signing, and browser fallback details.
