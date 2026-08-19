# Apple release workflow reference

## Identity surfaces

Apple Developer and App Store Connect are different records:

- Apple Developer `Identifiers` contains the App ID (explicit Bundle ID) and its capabilities.
- App Store Connect `My Apps` contains the app record, store metadata, TestFlight builds, and tester groups.
- A new App Store Connect iOS app normally selects an already-registered App ID. Registering only the App Store Connect record does not replace App ID registration.

Always use the exact approved Bundle ID in both surfaces. Search by Bundle ID before searching by name because names can collide and can be localized.

## Capability mapping

Use entitlements as evidence, not as a checklist to enable blindly:

| Entitlement evidence | Developer capability |
|---|---|
| `aps-environment` | Push Notifications |
| `com.apple.developer.applesignin` | Sign in with Apple |
| `com.apple.developer.associated-domains` | Associated Domains |
| `com.apple.developer.healthkit` | HealthKit |
| `com.apple.developer.icloud-container-identifiers` | iCloud |
| `com.apple.developer.in-app-payments` | Apple Pay |
| `com.apple.developer.game-center` | Game Center |
| `com.apple.developer.devicecheck.appattest-environment` | App Attest |

Some project behavior, such as StoreKit subscriptions, does not mean a separate App ID capability must be enabled. Match the project's entitlements and Apple's current portal labels.

## Signing and upload choices

Preferred order:

1. Existing Xcode account with automatic signing for a local interactive workflow.
2. App Store Connect API key for repeatable CI/local command-line uploads. Keep the `.p8` outside the repository and pass its path only at invocation time.
3. Manual certificates/profiles only when the project already requires them.

`xcodebuild -allowProvisioningUpdates` can create/update profiles, App IDs, and certificates when an Xcode account or App Store Connect authentication key is available. It does not replace the explicit user approval gate for choosing the app identity.

Never put `APPLE_ID`, passwords, 2FA codes, or `.p8` contents in source files or output logs. Environment variable names are acceptable in instructions; values must remain outside logs.

## Export compliance

For an app whose cryptographic behavior matches the App Store Connect no-non-exempt-encryption answer, declare the answer in the app's built `Info.plist` with:

```xml
<key>ITSAppUsesNonExemptEncryption</key>
<false/>
```

For generated Xcode plists, the equivalent build setting is `INFOPLIST_KEY_ITSAppUsesNonExemptEncryption = NO`. The bundled build runner applies this declaration automatically and updates a Flutter `ios/Runner/Info.plist` when that source file exists. If the app uses non-exempt or externally implemented encryption, do not reuse this declaration; stop for the appropriate Apple documentation and export-compliance decision.

## Versioning

`CFBundleShortVersionString` is the marketing version and `CFBundleVersion` is the build number. App Store Connect rejects a build number that has already been used, including numbers associated with failed or rejected uploads in some workflows. Check the current App Store Connect build list and choose a strictly higher integer before archiving.

For Flutter, the version is usually in `pubspec.yaml` as `version: marketing.build`. Prefer `flutter build ipa --build-name ... --build-number ...` for a one-off release so unrelated source files are not rewritten.

## Browser handoff

If Chrome is not logged in, tell the user to complete Apple ID login and 2FA in the visible browser. After every navigation or click, re-read the current page state because browser references are short-lived. Do not type credentials into shell commands. Do not accept legal agreements or change account settings on the user's behalf.

After a successful upload, App Store Connect may show `Processing` before the build is available to testers. Report that state explicitly and refresh only while the user expects a live verification.
