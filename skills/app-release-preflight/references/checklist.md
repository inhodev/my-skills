# App release checklist

## Automatic repository checks

1. **Secrets and ENV**
   - No real `.env`, signing key, service account JSON, certificate, provisioning profile, or keystore is tracked.
   - No recognizable production token is embedded in tracked source.
   - `.env.example` contains key names only.

2. **Environment separation**
   - Development, staging, and production endpoints cannot be confused at build time.
   - Bundle/package IDs and backend projects match the target channel.

3. **Release identity**
   - Marketing version and build number are explicit.
   - The new identity is higher than the latest submitted identity.
   - Version/build increments are automated when the stack supports it.

4. **Deep links**
   - Scheme, associated domains, universal/app links, and Android intent filters match.
   - A real installed build opens at least one representative link.

## Manual product and service checks

5. **Force update**
   - A severe incompatible release can require a minimum version.
   - The screen has a working store URL and does not trap users during an outage.

6. **OTA update**
   - OTA is enabled only for compatible code/data changes.
   - Native changes still use a store release.
   - A rollback path and currently served update identity are known.

7. **Remote config**
   - Risky features have a server-controlled kill switch when justified.
   - Safe defaults exist if config fetch fails.

8. **Authentication expiry**
   - Expired access and refresh tokens end in one predictable state.
   - Logout clears protected local data and repeated login loops are tested.

9. **Privacy and store policy**
   - Privacy policy, terms, support URL, account deletion, data collection declarations, tracking permission, and platform privacy manifests match actual behavior.

10. **Observability**
    - Production crashes and startup failures can be identified by version/build.
    - Sensitive user data is not sent to logs or analytics.

11. **Data safety**
    - Production migrations are backward compatible with the previous app version.
    - Backup, rollback, and irreversible migration decisions are written down.

12. **Release surface**
    - The exact archive/bundle is tested on a real device or production-like environment.
    - Upload acceptance is not reported as store availability.

## Release-blocking defaults

Block by default for a tracked secret, wrong production endpoint, duplicate/lower store build identity, missing required privacy disclosure, destructive migration without recovery, or an app that cannot start/sign in on the release surface.
