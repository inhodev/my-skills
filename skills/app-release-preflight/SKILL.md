---
name: app-release-preflight
description: Inspect an iOS, Android, Flutter, Expo, React Native, or web app immediately before release. Use when preparing TestFlight, App Store, Play Store, OTA, or production deployment and checking tracked secrets, environment separation, version/build identity, force update, remote config, deep links, session expiry, privacy documents, crash reporting, and rollback readiness.
---

# App Release Preflight

Return a release decision backed by repository evidence. Do not upload, deploy, publish, rotate keys, or change portal state unless the user separately authorizes it.

## Workflow

1. Resolve the exact app and release target.
2. Run:

   ```bash
   bash scripts/release_preflight.sh /absolute/project/path
   ```

3. Read [references/checklist.md](references/checklist.md).
4. Inspect only the files needed to settle reported `BLOCK` and `WARN` items.
5. Distinguish:
   - `PASS`: repository evidence confirms the item.
   - `BLOCK`: release must stop.
   - `WARN`: evidence is missing or requires attention.
   - `MANUAL`: portal, backend, device, or product behavior must be checked by a person.
6. Do not print secret values. Report only key names, filenames, line numbers, lengths, or status.
7. Return one decision:
   - `GO`: no blocks, manual checks completed.
   - `CONDITIONAL GO`: no blocks, named manual checks remain.
   - `BLOCK`: at least one release-blocking issue remains.

## Required output

```markdown
# Release preflight: <app> <version/build>

Decision: GO | CONDITIONAL GO | BLOCK

## Blocking
- <evidence and owner>

## Warnings
- <evidence and next action>

## Manual checks
- <check, owner, completion evidence>

## Release identity
- Bundle/package ID:
- Marketing version:
- Build number:
- Target channel:

## Next action
- <one exact action>
```

Treat build success, upload success, store processing, and public availability as separate states.
