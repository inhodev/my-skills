# App Studio TestFlight fast path

## Contents

1. Engine location
2. Why it is fast
3. Authentication and APIs
4. Exact command path
5. Cache and environment contract
6. Timing and state contract
7. Routing failures

## 1. Engine location

Set an App Studio checkout explicitly for the fast path:

```text
APP_STUDIO_ROOT="/path/to/AppStudio"
```

The router defaults to `~/AppStudio` when this environment variable is absent.

```bash
APP_STUDIO_ROOT="<new-root>" python3 scripts/fast_testflight.py --root <project>
```

Source-of-truth files:

```text
src/cli/index.ts
src/cli/commands/release.ts
src/core/release/pipeline.ts
src/core/release/upload.ts
src/core/release/version.ts
src/core/build/plans.ts
src/core/build/runner.ts
src/core/store/asc.ts
studio.config.yaml
apps/<app-id>/studio.yaml
```

Do not copy credential values from `studio.config.yaml` into a prompt or report.

## 2. Why it is fast

The engine eliminates repeated agent discovery. It already knows the registered project path, stack, platform, Bundle ID, Team lookup, archive/export locations, credential references, App Store state calls, build-number policy, and failure hints.

It intentionally avoids:

- Xcode GUI and Organizer;
- browser navigation for an existing app;
- Apple ID password and 2FA uploads;
- hand-written ExportOptions;
- a full fastlane lane for iOS binary upload;
- automatic clean or DerivedData deletion;
- re-asking identity for an aligned registered app.

Apple does not provide an API that creates the archive. Local Xcode creates it.

## 3. Authentication and APIs

| Purpose | Mechanism |
|---|---|
| app/build lookup and processing | App Store Connect REST API v1 |
| ASC authentication | 20-minute ES256 JWT from Issuer ID, Key ID, external App Store Connect API `.p8` |
| IPA transfer | `xcrun altool --upload-app` with `API_PRIVATE_KEYS_DIR` |
| code signing | Xcode account, Team, certificates, provisioning profiles |

The ASC `.p8` is not an APNs key and is not a code-signing certificate. The App Studio config stores references, not key contents. Never echo those values.

## 4. Exact command path

The router runs this dry-run first:

```bash
./bin/studio release <app-id> --platform ios --dry-run
```

With explicit upload authorization it then runs:

```bash
./bin/studio release <app-id> --platform ios
```

Optional flags:

```text
--no-wait   stop after Apple accepts upload; do not claim PROCESSED
--verbose   show Xcode/altool lines for diagnosis
```

For several registered app IDs, App Studio serializes CPU-heavy build/upload work and overlaps Apple processing polling with the next build.

## 5. Cache and environment contract

| Resource | Rule |
|---|---|
| Xcode DerivedData | Preserve the existing DerivedData cache; do not clean for routine release |
| SPM/CocoaPods caches | Preserve lockfiles and warmed downloads |
| project `build/` | Do not erase before evidence points to stale output |
| TMPDIR | Set `APP_STUDIO_TMPDIR` to an ASCII-only temporary path when Swift tools have path-encoding problems |
| Xcode account | Keep Team/cert/profile available for automatic signing |
| ASC key | Keep outside repo; App Studio config references it |

Warm caches can materially reduce repeated builds. They do not guarantee a fixed duration.

## 6. Timing and state contract

Preserved local event logs showed:

| Sample | archive | IPA export | build + export |
|---|---:|---:|---:|
| Sandtimer A | 46.1s | 25.5s | 71.5s |
| Mulmeong | 58.4s | 26.3s | 84.7s |
| Sandtimer B | 86.8s | 22.7s | 109.5s |

The observed 20-second range belongs to IPA export, not archive. Record separately:

```text
archive_ms
export_ms
upload_accept_ms
apple_processing_ms
testable_ms
```

`uploaded.ms` covers build start through upload command completion; it excludes Apple processing.

## 7. Routing failures

Return to the SKILL fallback path when:

- no exact canonical project-path match exists;
- more than one record matches;
- record path disappeared or stack changed;
- iOS is not registered for the record;
- source Bundle IDs do not contain the record Bundle ID;
- App Studio dry-run fails;
- manual profile maps or an unsupported target structure are required.

Do not force the fast path by editing identity merely to make the router pass.
