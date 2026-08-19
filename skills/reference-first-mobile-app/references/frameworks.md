# Framework Execution Notes

## SwiftUI

- Prefer an app feature/core split only when the existing project already benefits from it; do not over-architect.
- Keep `WindowGroup` or the shipping root as the source of truth. Headless capture may inject deterministic model fixtures into that same root.
- Use Swift localization resources or String Catalog with Korean as the development/default language and complete English parity.
- Run warnings-as-errors build and tests from the package or Xcode project directory specified by the project.
- For macOS-compatible SwiftUI, an `NSHostingView` renderer can create deterministic PNG evidence without a simulator. Reject blank/solid captures and verify dimensions/signature.
- iOS-only frameworks, permissions, StoreKit, HealthKit, CoreLocation, MapKit tiles and speech require honest seams and explicit surface boundaries.

## Flutter

- Capture the same widget tree used by `MaterialApp`/`CupertinoApp`, with deterministic repositories/providers injected at app boundaries.
- Use ARB/gen-l10n or the existing localization stack. Test Korean/English key parity and rendered expansion.
- Run `flutter analyze`, unit tests, widget/component tests, then the project’s build or headless render command.
- Golden tests can protect layout, but they do not replace direct inspection or interaction tests.
- Check the build symlink target and disk capacity before diagnosing missing-path or ENOSPC failures as code defects.

## Both

- Preserve the existing architecture and dirty work.
- Model loading, empty, error, populated and edge states only where the product can actually enter them.
- Visible actions need real callbacks and assertions against observable state, not source-string tests.
- Do not weaken or delete stale tests; migrate them to equivalent behavior.
- Keep capture fixtures deterministic, realistic and clearly separated from fabricated production claims.
