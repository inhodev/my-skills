#!/usr/bin/env bash

set -u

project_dir="${1:-}"

if [[ -z "$project_dir" || ! -d "$project_dir" ]]; then
  echo "Usage: bash release_preflight.sh /absolute/project/path" >&2
  exit 2
fi

project_dir="$(cd "$project_dir" && pwd)"
block_count=0
warn_count=0

pass() {
  printf 'PASS  %s\n' "$1"
}

warn() {
  warn_count=$((warn_count + 1))
  printf 'WARN  %s\n' "$1"
}

block() {
  block_count=$((block_count + 1))
  printf 'BLOCK %s\n' "$1"
}

manual() {
  printf 'MANUAL %s\n' "$1"
}

printf '# App release preflight\n'
printf 'Project: %s\n\n' "$project_dir"

if git -C "$project_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  pass "Git repository detected"

  tracked_sensitive="$(
    git -C "$project_dir" ls-files |
      awk '
        /(^|\/)\.env($|\.)/ && $0 !~ /\.env\.(example|sample|template)$/ { print }
        /(^|\/)(GoogleService-Info\.plist|google-services\.json|service-account.*\.json)$/ { print }
        /\.(p8|p12|pem|jks|keystore|mobileprovision)$/ { print }
      '
  )"

  if [[ -n "$tracked_sensitive" ]]; then
    block "Sensitive release files are tracked: $(printf '%s' "$tracked_sensitive" | tr '\n' ' ')"
  else
    pass "No known secret or signing files are tracked"
  fi

  leaked_files="$(
    git -C "$project_dir" grep -IlE \
      '(sk-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|gh[pousr]_[A-Za-z0-9]{30,})' \
      -- ':!*.lock' ':!package-lock.json' ':!Podfile.lock' 2>/dev/null || true
  )"

  if [[ -n "$leaked_files" ]]; then
    block "Possible embedded production credential in tracked files: $(printf '%s' "$leaked_files" | tr '\n' ' ')"
  else
    pass "No common production-token signature found in tracked source"
  fi
else
  warn "No Git repository; tracked-secret checks were not available"
fi

env_template="$(
  find "$project_dir" -maxdepth 2 \
    \( -name '.env.example' -o -name '.env.sample' -o -name '.env.template' \) \
    -print -quit
)"

if [[ -n "$env_template" ]]; then
  template_keys="$(
    awk -F= '/^[A-Za-z_][A-Za-z0-9_]*=/{ print $1 }' "$env_template" |
      sort -u
  )"
  if [[ -n "$template_keys" ]]; then
    pass "Environment key template exists and declares keys"
  else
    warn "Environment template exists but declares no keys"
  fi

  if [[ -f "$project_dir/.env" ]]; then
    local_env_keys="$(
      awk -F= '/^[A-Za-z_][A-Za-z0-9_]*=/{ print $1 }' "$project_dir/.env" |
        sort -u
    )"
    missing_template_keys="$(
      comm -23 \
        <(printf '%s\n' "$local_env_keys") \
        <(printf '%s\n' "$template_keys")
    )"
    if [[ -n "$missing_template_keys" ]]; then
      warn "Local environment keys missing from template: $(printf '%s' "$missing_template_keys" | tr '\n' ' ')"
    else
      pass "Local environment key names are represented in the template"
    fi
  fi
else
  warn "No .env.example, .env.sample, or .env.template found"
fi

release_identity=""

if [[ -f "$project_dir/pubspec.yaml" ]]; then
  release_identity="$(awk '/^version:[[:space:]]*/ { print $2; exit }' "$project_dir/pubspec.yaml")"
  [[ -n "$release_identity" ]] && pass "Flutter version/build: $release_identity" || warn "Flutter version/build not found"

  if [[ -n "$release_identity" ]]; then
    release_version="${release_identity%%+*}"
    stale_version_lines="$(
      git -C "$project_dir" grep -nEi \
        '(currentVersion|versionLabel|현재[[:space:]]*버전).*[0-9]+\.[0-9]+\.[0-9]+' \
        -- 'lib/**' 2>/dev/null |
        grep -Fv "$release_version" || true
    )"
    if [[ -n "$stale_version_lines" ]]; then
      warn "Possible stale app-visible version label: $(printf '%s' "$stale_version_lines" | tr '\n' ' ')"
    else
      pass "No conflicting hard-coded current-version label found"
    fi
  fi

  if grep -Eq '^[[:space:]]+(firebase_crashlytics|sentry_flutter):' "$project_dir/pubspec.yaml"; then
    pass "Flutter crash-reporting dependency found"
  else
    warn "No Flutter crash-reporting dependency found"
  fi

  if git -C "$project_dir" grep -Eqi \
    '(minimum.?version|force.?update|in_app_update|upgrader)' \
    -- 'lib/**' 'pubspec.yaml' 2>/dev/null; then
    pass "Minimum-version or force-update evidence found"
  else
    warn "No minimum-version or force-update evidence found"
  fi

  if git -C "$project_dir" grep -Eqi \
    '(remote.?config|kill.?switch)' \
    -- 'lib/**' 'pubspec.yaml' 2>/dev/null; then
    pass "Remote-config or kill-switch evidence found"
  else
    warn "No remote-config or kill-switch evidence found"
  fi
elif [[ -f "$project_dir/app.json" || -f "$project_dir/app.config.js" || -f "$project_dir/app.config.ts" ]]; then
  release_identity="$(grep -Eh '(^|[[:space:]])"version"[[:space:]]*:' "$project_dir/app.json" 2>/dev/null | head -1 | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')"
  [[ -n "$release_identity" ]] && pass "Expo/app version: $release_identity" || warn "Expo/app release version needs confirmation"
elif [[ -f "$project_dir/package.json" ]]; then
  release_identity="$(grep -E '"version"[[:space:]]*:' "$project_dir/package.json" | head -1 | sed -E 's/.*"version"[[:space:]]*:[[:space:]]*"([^"]+)".*/\1/')"
  [[ -n "$release_identity" ]] && pass "Package version: $release_identity" || warn "Package version not found"
else
  warn "Release identity was not detected automatically"
fi

if find "$project_dir" -maxdepth 5 \( -name '*.entitlements' -o -name 'AndroidManifest.xml' -o -name 'app.json' \) -type f -print0 |
  xargs -0 grep -Eil 'associated-domains|intent-filter|"scheme"|CFBundleURLTypes' 2>/dev/null |
  grep -q .; then
  pass "Deep-link configuration evidence found"
else
  warn "No deep-link configuration evidence found"
fi

manual "Confirm minimum-version or force-update behavior"
manual "Confirm OTA compatibility and rollback identity"
manual "Confirm remote-config kill switches and safe defaults"
manual "Test token expiry, refresh failure, logout, and login recovery"
manual "Verify privacy policy, terms, support, deletion, and store declarations"
manual "Verify crash reporting identifies the exact version/build"
manual "Verify production migration backup and rollback"
manual "Test the exact release artifact on a real device or production-like surface"

printf '\nSummary: %d BLOCK, %d WARN\n' "$block_count" "$warn_count"

if (( block_count > 0 )); then
  printf 'Decision: BLOCK\n'
  exit 1
fi

printf 'Decision: CONDITIONAL GO pending manual checks\n'
