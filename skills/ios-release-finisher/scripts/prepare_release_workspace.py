#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import plistlib
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


SKIP_DIRS = {
    ".git",
    ".dart_tool",
    ".idea",
    ".swiftpm",
    ".build",
    "Pods",
    "DerivedData",
    "build",
    "node_modules",
    "vendor",
    ".launcher-build",
    ".ios-release-finisher",
}
USAGE_KEY = re.compile(r"<key>(NS[A-Za-z]+UsageDescription)</key>")
BUNDLE_ID = re.compile(r"PRODUCT_BUNDLE_IDENTIFIER\s*=\s*([^;\s]+)")
TEAM_ID = re.compile(r"DEVELOPMENT_TEAM\s*=\s*([^;\s]+)")


def skill_root() -> Path:
    override = os.environ.get("IOS_RELEASE_FINISHER_SKILL_ROOT")
    if override:
        return Path(override).resolve()
    return Path(__file__).resolve().parent.parent


def iter_files(root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in SKIP_DIRS]
        base = Path(current)
        for name in files:
            yield base / name


def relative(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def detect_stack(root: Path) -> str:
    if (root / "pubspec.yaml").is_file() and (root / "ios").is_dir():
        return "flutter"
    if (root / "app.json").is_file() and (root / "ios").is_dir():
        return "react-native-or-expo"
    files = list(iter_files(root))
    if any(path.name == "project.pbxproj" for path in files):
        return "native-xcode"
    if any(path.suffix == ".xcworkspacedata" for path in files):
        return "native-xcode"
    return "unknown"


def flutter_version(root: Path) -> tuple[str | None, str | None]:
    pubspec = root / "pubspec.yaml"
    if not pubspec.is_file():
        return None, None
    match = re.search(r"^version:\s*([^\s+#]+)(?:\+([^\s#]+))?", read_text(pubspec), re.M)
    if not match:
        return None, None
    return match.group(1), match.group(2)


def plist_values(path: Path) -> dict[str, Any]:
    try:
        with path.open("rb") as handle:
            value = plistlib.load(handle)
        return value if isinstance(value, dict) else {}
    except (OSError, plistlib.InvalidFileException):
        return {}


def inspect_project(root: Path) -> dict[str, Any]:
    root = root.resolve()
    files = list(iter_files(root))
    stack = detect_stack(root)
    pbxproj_files = sorted(path for path in files if path.name == "project.pbxproj")
    plist_files = sorted(path for path in files if path.suffix == ".plist")

    bundle_ids: set[str] = set()
    team_ids: set[str] = set()
    for path in pbxproj_files:
        text = read_text(path)
        bundle_ids.update(value.strip('"') for value in BUNDLE_ID.findall(text))
        team_ids.update(value.strip('"') for value in TEAM_ID.findall(text))

    marketing_version, build_number = flutter_version(root)
    display_names: set[str] = set()
    usage_descriptions: set[str] = set()
    for path in plist_files:
        text = read_text(path)
        usage_descriptions.update(USAGE_KEY.findall(text))
        values = plist_values(path)
        for key in ("CFBundleDisplayName", "CFBundleName"):
            value = values.get(key)
            if isinstance(value, str) and "$" not in value:
                display_names.add(value)
        if marketing_version is None:
            value = values.get("CFBundleShortVersionString")
            if isinstance(value, str) and "$" not in value:
                marketing_version = value
        if build_number is None:
            value = values.get("CFBundleVersion")
            if isinstance(value, str) and "$" not in value:
                build_number = value

    privacy_manifests = sorted(
        relative(path, root) for path in files if path.name == "PrivacyInfo.xcprivacy"
    )
    entitlements = sorted(relative(path, root) for path in files if path.suffix == ".entitlements")
    dependency_files = sorted(
        relative(path, root)
        for path in files
        if path.name in {"Podfile.lock", "Package.resolved", "pubspec.lock", "package-lock.json"}
    )

    release_blocks: list[dict[str, str]] = []
    if stack == "unknown":
        release_blocks.append(
            {
                "id": "ios_project_not_found",
                "reason": "No iOS Xcode surface was found under the supplied project root.",
            }
        )

    findings: list[dict[str, str]] = []
    if stack != "unknown" and not bundle_ids:
        findings.append({"status": "WARN", "id": "bundle_id_unresolved", "detail": "Resolve from build settings."})
    if stack != "unknown" and not privacy_manifests:
        findings.append({"status": "WARN", "id": "privacy_manifest_not_found", "detail": "Audit app and SDK required-reason APIs."})
    if stack != "unknown" and not usage_descriptions:
        findings.append({"status": "CHECK", "id": "usage_descriptions_not_found", "detail": "Confirm that the app requests no protected resources."})

    deferred_inputs = [
        {"id": "privacy_contact", "reason": "Human or legal-entity contact data cannot be inferred safely."},
        {"id": "support_and_review_contact", "reason": "Public support and private review contacts require owner confirmation."},
        {"id": "pricing_and_territories", "reason": "Price, base territory, storefronts, and distribution method are business decisions."},
        {"id": "age_rating_approval", "reason": "The owner must approve semantic answers and irreversible Kids-category choices."},
        {"id": "legal_entity_and_regional_status", "reason": "Trader, Korean business, tax, banking, and permit facts require account-holder evidence."},
        {"id": "review_demo_credentials", "reason": "Create or provide only if the app requires sign-in for review."},
    ]

    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workflow_state": "LOCAL_PREPARATION_IN_PROGRESS",
        "project": {
            "root": str(root),
            "stack": stack,
            "display_names": sorted(display_names),
            "bundle_ids": sorted(bundle_ids),
            "team_ids_present": bool(team_ids),
            "marketing_version": marketing_version,
            "build_number": build_number,
        },
        "evidence": {
            "xcode_projects": sorted(relative(path.parent, root) for path in pbxproj_files),
            "privacy_manifest_files": privacy_manifests,
            "entitlement_files": entitlements,
            "dependency_files": dependency_files,
            "usage_descriptions": sorted(usage_descriptions),
        },
        "findings": findings,
        "deferred_inputs": deferred_inputs,
        "external_blocks": [],
        "release_blocks": release_blocks,
    }


def template_values(state: dict[str, Any]) -> dict[str, str]:
    project = state["project"]
    bundles = ", ".join(project["bundle_ids"]) or "미확정"
    names = ", ".join(project["display_names"]) or "미확정"
    identity = (
        f"- 프로젝트: `{project['root']}`\n"
        f"- 스택: `{project['stack']}`\n"
        f"- 앱 이름: {names}\n"
        f"- Bundle ID: `{bundles}`\n"
        f"- 버전/빌드: `{project['marketing_version'] or '미확정'}` / `{project['build_number'] or '미확정'}`\n"
    )
    deferred = "\n".join(
        f"- [ ] `{item['id']}`: {item['reason']}" for item in state["deferred_inputs"]
    )
    evidence = state["evidence"]
    usage = ", ".join(evidence["usage_descriptions"]) or "감지되지 않음"
    manifests = "\n".join(f"- `{path}`" for path in evidence["privacy_manifest_files"]) or "- 감지되지 않음"
    return {
        "IDENTITY": identity,
        "DEFERRED_INPUTS": deferred,
        "FINDINGS_JSON": json.dumps(state["findings"], ensure_ascii=False, indent=2),
        "PRIVACY_MANIFESTS": manifests,
        "USAGE_DESCRIPTIONS": usage,
    }


def render_template(path: Path, values: dict[str, str]) -> str:
    content = read_text(path)
    for key, value in values.items():
        content = content.replace("{{" + key + "}}", value)
    unresolved = re.findall(r"\{\{[A-Z_]+\}\}", content)
    if unresolved:
        raise ValueError(f"unresolved template values in {path.name}: {unresolved}")
    return content


def packet_documents(state: dict[str, Any]) -> dict[str, str]:
    values = template_values(state)
    template_dir = skill_root() / "assets" / "packet-templates"
    return {
        path.name.removesuffix(".template"): render_template(path, values)
        for path in sorted(template_dir.glob("*.template"))
    }


def prepare_workspace(root: Path, output: Path) -> list[Path]:
    state = inspect_project(root)
    output.mkdir(parents=True, exist_ok=True)
    documents = packet_documents(state)
    created: list[Path] = []
    for name, content in documents.items():
        target = output / name
        if not target.exists():
            target.write_text(content, encoding="utf-8")
        created.append(target)
    state_path = output / "RELEASE_STATE.json"
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    created.append(state_path)
    return created


def main() -> int:
    parser = argparse.ArgumentParser(description="Create an iOS release-preparation packet from repository evidence.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="iOS project root")
    parser.add_argument("--output", type=Path, help="packet directory; defaults to <root>/.ios-release-finisher")
    parser.add_argument("--inspect", action="store_true", help="print JSON only and create no files")
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        parser.error(f"project root does not exist: {root}")
    if args.inspect:
        print(json.dumps(inspect_project(root), ensure_ascii=False, indent=2))
        return 0

    output = (args.output or root / ".ios-release-finisher").resolve()
    for path in prepare_workspace(root, output):
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
