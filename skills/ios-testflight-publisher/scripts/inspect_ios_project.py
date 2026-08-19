#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import plistlib
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any


CAPABILITY_KEYS = {
    "aps-environment": "Push Notifications",
    "com.apple.developer.applesignin": "Sign in with Apple",
    "com.apple.developer.associated-domains": "Associated Domains",
    "com.apple.developer.healthkit": "HealthKit",
    "com.apple.developer.icloud-container-identifiers": "iCloud",
    "com.apple.developer.in-app-payments": "Apple Pay",
    "com.apple.developer.game-center": "Game Center",
    "com.apple.developer.networking.wifi-info": "Access Wi-Fi Information",
    "com.apple.developer.devicecheck.appattest-environment": "App Attest",
}


def unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def run_version(command: list[str]) -> str | None:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=8)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    line = next((line.strip() for line in result.stdout.splitlines() if line.strip()), "")
    return line or None


def parse_pbxproj(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    bundles = [value.strip().strip('"') for value in unique(re.findall(r"PRODUCT_BUNDLE_IDENTIFIER\s*=\s*([^;]+);", text))]
    app_bundles = [
        value for value in bundles
        if not any(value.endswith(suffix) for suffix in (".tests", ".UITests", ".Tests", ".UITests"))
    ]
    names = [
        value.strip().strip('"')
        for value in unique(re.findall(r"PRODUCT_NAME\s*=\s*([^;]+);", text))
        if "$(" not in value
    ]
    versions = unique(re.findall(r"MARKETING_VERSION\s*=\s*([^;]+);", text))
    build_numbers = unique(re.findall(r"CURRENT_PROJECT_VERSION\s*=\s*([^;]+);", text))
    teams = [value.strip().strip('"') for value in unique(re.findall(r"DEVELOPMENT_TEAM\s*=\s*([^;]+);", text))]
    teams = [value for value in teams if value]
    return {
        "path": str(path),
        "bundle_ids": bundles,
        "app_bundle_ids": app_bundles,
        "product_names": names,
        "marketing_versions": versions,
        "build_numbers": build_numbers,
        "development_teams": teams,
    }


def parse_pubspec(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    version_match = re.search(r"^version:\s*([^\s#]+)", text, re.MULTILINE)
    version = version_match.group(1) if version_match else None
    marketing_version = None
    build_number = None
    if version and "+" in version:
        marketing_version, build_number = version.split("+", 1)
    elif version:
        marketing_version = version
    return {
        "path": str(path),
        "version": version,
        "marketing_version": marketing_version,
        "build_number": build_number,
    }


def parse_entitlements(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.entitlements")):
        try:
            data = plistlib.loads(path.read_bytes())
        except (OSError, plistlib.InvalidFileException, ValueError):
            continue
        keys = [str(key) for key in data]
        capabilities = unique([CAPABILITY_KEYS[key] for key in keys if key in CAPABILITY_KEYS])
        findings.append({"path": str(path), "keys": keys, "capabilities": capabilities})
    return findings


def find_workspace(root: Path) -> Path | None:
    candidates = sorted(root.rglob("*.xcworkspace"), key=lambda path: ("Pods" in path.parts, len(path.parts), str(path)))
    return candidates[0] if candidates else None


def find_project(root: Path) -> Path | None:
    candidates = sorted(root.rglob("*.xcodeproj/project.pbxproj"), key=lambda path: ("Pods" in path.parts, len(path.parts), str(path)))
    return candidates[0] if candidates else None


def find_schemes(root: Path) -> list[dict[str, str]]:
    schemes: list[dict[str, str]] = []
    for path in sorted(root.rglob("*.xcscheme")):
        if "Pods" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        buildable = re.search(r'BuildableName\s*=\s*"([^"]+)"', text)
        blueprint = re.search(r'BlueprintName\s*=\s*"([^"]+)"', text)
        schemes.append({
            "name": path.stem,
            "path": str(path),
            "buildable_name": buildable.group(1) if buildable else "",
            "blueprint_name": blueprint.group(1) if blueprint else "",
        })
    return schemes


def parse_info_plists(root: Path) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path in sorted(root.rglob("Info.plist")):
        try:
            data = plistlib.loads(path.read_bytes())
        except (OSError, plistlib.InvalidFileException, ValueError):
            continue
        values: dict[str, str] = {"path": str(path)}
        for key in ("CFBundleDisplayName", "CFBundleName", "CFBundleIdentifier", "CFBundleShortVersionString", "CFBundleVersion"):
            value = data.get(key)
            if isinstance(value, str):
                values[key] = value
        findings.append(values)
    return findings


def inspect(root: Path) -> dict[str, Any]:
    root = root.resolve()
    pubspec = root / "pubspec.yaml"
    project_path = find_project(root)
    workspace_path = find_workspace(root)
    xcode = parse_pbxproj(project_path) if project_path else {}
    flutter = parse_pubspec(pubspec) if pubspec.is_file() else None
    swift_files = list(root.rglob("*.swift"))
    is_flutter = flutter is not None and (root / "ios").is_dir()
    is_xcode = project_path is not None
    if is_flutter and is_xcode:
        framework = "flutter"
    elif is_xcode or swift_files:
        framework = "swift/xcode"
    elif flutter is not None:
        framework = "flutter"
    else:
        framework = "unknown"

    info_plists = parse_info_plists(root)
    entitlements = parse_entitlements(root)
    app_bundle_ids = xcode.get("app_bundle_ids", [])
    bundles = app_bundle_ids or xcode.get("bundle_ids", [])
    app_name_candidates = unique(
        xcode.get("product_names", [])
        + [item.get("CFBundleDisplayName", "") for item in info_plists]
        + [item.get("CFBundleName", "") for item in info_plists]
    )
    tools = {name: shutil.which(name) for name in ("xcodebuild", "xcrun", "flutter", "security", "osascript")}
    warnings: list[str] = []
    if not bundles:
        warnings.append("No application Bundle ID was found in Xcode settings or Info.plist.")
    if not xcode.get("development_teams"):
        warnings.append("No DEVELOPMENT_TEAM is set; signing team selection is still required.")
    if framework == "unknown":
        warnings.append("The root does not look like a Swift/Xcode or Flutter iOS project.")
    if not tools.get("xcodebuild"):
        warnings.append("xcodebuild is not available on PATH.")

    return {
        "root": str(root),
        "framework": framework,
        "xcode": xcode,
        "workspace": str(workspace_path) if workspace_path else None,
        "project": str(project_path.parent) if project_path else None,
        "schemes": find_schemes(root),
        "flutter": flutter,
        "bundle_ids": bundles,
        "app_name_candidates": app_name_candidates,
        "info_plists": info_plists,
        "entitlements": entitlements,
        "capability_candidates": unique([cap for item in entitlements for cap in item["capabilities"]]),
        "tools": tools,
        "tool_versions": {
            "xcodebuild": run_version(["xcodebuild", "-version"]) if tools.get("xcodebuild") else None,
            "flutter": run_version(["flutter", "--version", "--machine"]) if tools.get("flutter") else None,
        },
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".", help="Project root to inspect")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON")
    args = parser.parse_args()
    try:
        data = inspect(Path(args.root))
    except OSError as exc:
        print(f"inspect_ios_project.py: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(data, ensure_ascii=False, indent=2 if args.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
