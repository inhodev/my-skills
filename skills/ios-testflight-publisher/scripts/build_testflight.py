#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import plistlib
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from pathlib import PurePosixPath
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
INSPECTOR = SCRIPT_DIR / "inspect_ios_project.py"
EXPORT_COMPLIANCE_KEY = "ITSAppUsesNonExemptEncryption"


def command_text(command: list[str]) -> str:
    return " ".join(shlex_quote(item) for item in command)


def shlex_quote(value: str) -> str:
    if value and all(char.isalnum() or char in "._/-=" for char in value):
        return value
    return "'" + value.replace("'", "'\\''") + "'"


def run(command: list[str], cwd: Path, *, dry_run: bool) -> None:
    print(f"$ {command_text(command)}")
    if dry_run:
        return
    completed = subprocess.run(command, cwd=cwd)
    if completed.returncode:
        raise RuntimeError(f"command failed with exit code {completed.returncode}: {command_text(command)}")


def inspect(root: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(INSPECTOR), "--root", str(root)],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip() or "project inspection failed")
    return json.loads(completed.stdout)


def first_nonempty(values: list[str]) -> str | None:
    return next((value for value in values if value), None)


def source_info_plists(root: Path, data: dict[str, Any], framework: str) -> list[Path]:
    ignored_parts = {".testflight", "Pods", "Tests", "SourcePackages", "DerivedData", "build"}
    if framework == "flutter":
        runner_plist = root / "ios" / "Runner" / "Info.plist"
        return [runner_plist] if runner_plist.is_file() else []
    candidates = []
    for item in data.get("info_plists", []):
        path = Path(item.get("path", ""))
        if path.is_file() and root in path.parents and not ignored_parts.intersection(path.parts):
            candidates.append(path)
    if len(candidates) == 1:
        return candidates
    app_candidates = [path for path in candidates if path.parent.name not in {"Tests", "Test", "Resources"}]
    return app_candidates if len(app_candidates) == 1 else []


def ensure_export_compliance_metadata(
    root: Path,
    data: dict[str, Any],
    framework: str,
    *,
    dry_run: bool,
) -> list[str]:
    updated: list[str] = []
    for path in source_info_plists(root, data, framework):
        try:
            plist = plistlib.loads(path.read_bytes())
        except (OSError, plistlib.InvalidFileException, ValueError) as exc:
            raise ValueError(f"could not read source Info.plist {path}: {exc}") from exc
        if plist.get(EXPORT_COMPLIANCE_KEY) is False:
            continue
        updated.append(str(path))
        if dry_run:
            print(f"would set {EXPORT_COMPLIANCE_KEY}=NO in {path}")
            continue
        plist[EXPORT_COMPLIANCE_KEY] = False
        path.write_bytes(plistlib.dumps(plist, fmt=plistlib.FMT_XML, sort_keys=False))
        print(f"set {EXPORT_COMPLIANCE_KEY}=NO in {path}")
    return updated


def write_export_options(
    path: Path,
    *,
    destination: str,
    provisioning_profiles: dict[str, str],
) -> None:
    options = {
        "destination": destination,
        "method": "app-store-connect",
        "signingStyle": "manual" if provisioning_profiles else "automatic",
        "manageAppVersionAndBuildNumber": False,
        "uploadSymbols": True,
        "uploadBitcode": False,
    }
    if provisioning_profiles:
        options["provisioningProfiles"] = provisioning_profiles
    path.write_bytes(plistlib.dumps(options, fmt=plistlib.FMT_XML, sort_keys=False))


def parse_provisioning_profile_maps(values: list[str]) -> dict[str, str]:
    profiles: dict[str, str] = {}
    for value in values:
        bundle_id, separator, profile = value.partition("=")
        if not separator or not bundle_id.strip() or not profile.strip():
            raise ValueError(
                "--provisioning-profile-map must use BUNDLE_ID=PROFILE_NAME"
            )
        bundle_id = bundle_id.strip()
        if bundle_id in profiles:
            raise ValueError(f"duplicate provisioning profile mapping for {bundle_id}")
        profiles[bundle_id] = profile.strip()
    return profiles


def validate_exported_ipa(
    export_path: Path,
    *,
    expected_bundle_ids: set[str],
    marketing_version: str,
    build_number: int,
) -> Path:
    ipa_files = sorted(export_path.glob("*.ipa"))
    if len(ipa_files) != 1:
        raise ValueError(f"expected exactly one exported IPA in {export_path}, found {len(ipa_files)}")
    ipa_path = ipa_files[0]
    bundle_plists: dict[str, dict[str, Any]] = {}
    main_plist: dict[str, Any] | None = None
    with zipfile.ZipFile(ipa_path) as archive:
        for name in archive.namelist():
            parts = PurePosixPath(name).parts
            if not parts or parts[-1] != "Info.plist":
                continue
            bundle_part = next((part for part in reversed(parts[:-1]) if part.endswith((".app", ".appex"))), None)
            if bundle_part is None:
                continue
            plist = plistlib.loads(archive.read(name))
            bundle_identifier = plist.get("CFBundleIdentifier")
            if bundle_identifier:
                bundle_plists[str(bundle_identifier)] = plist
            if len(parts) == 3 and parts[0] == "Payload" and parts[1].endswith(".app"):
                main_plist = plist
    if main_plist is None:
        raise ValueError(f"could not find the main app Info.plist in {ipa_path}")
    missing_bundle_ids = sorted(expected_bundle_ids.difference(bundle_plists))
    if missing_bundle_ids:
        raise ValueError(f"IPA is missing expected signed bundles: {', '.join(missing_bundle_ids)}")
    if str(main_plist.get("CFBundleShortVersionString")) != marketing_version:
        raise ValueError("IPA marketing version does not match the requested version")
    if str(main_plist.get("CFBundleVersion")) != str(build_number):
        raise ValueError("IPA build number does not match the requested build number")
    if main_plist.get(EXPORT_COMPLIANCE_KEY) is not False:
        raise ValueError(f"IPA main Info.plist must contain {EXPORT_COMPLIANCE_KEY}=NO")
    print(json.dumps({
        "validated_ipa": str(ipa_path),
        "bundle_ids": sorted(bundle_plists),
        "marketing_version": marketing_version,
        "build_number": build_number,
        "export_compliance": False,
    }, ensure_ascii=False, indent=2))
    return ipa_path


def add_authentication_flags(command: list[str], args: argparse.Namespace) -> None:
    provided = [args.authentication_key_path, args.authentication_key_id, args.authentication_key_issuer_id]
    if any(provided) and not all(provided):
        raise ValueError("authentication key path, key id, and issuer id must be provided together")
    if all(provided):
        command.extend([
            "-authenticationKeyPath", str(Path(args.authentication_key_path).expanduser()),
            "-authenticationKeyID", args.authentication_key_id,
            "-authenticationKeyIssuerID", args.authentication_key_issuer_id,
        ])


def resolve_scheme(data: dict[str, Any], requested: str | None) -> str:
    if requested:
        return requested
    schemes = data.get("schemes", [])
    if len(schemes) == 1:
        return schemes[0]["name"]
    candidates = [item["name"] for item in schemes if item.get("name") not in {"Pods", "RunnerTests"}]
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError("multiple or zero schemes found; pass --scheme explicitly")


def resolve_version(data: dict[str, Any], requested: str | None) -> str | None:
    if requested:
        return requested
    flutter = data.get("flutter") or {}
    if flutter.get("marketing_version"):
        return flutter["marketing_version"]
    return first_nonempty(data.get("xcode", {}).get("marketing_versions", []))


def resolve_current_build(data: dict[str, Any]) -> int | None:
    flutter = data.get("flutter") or {}
    raw = flutter.get("build_number") or first_nonempty(data.get("xcode", {}).get("build_numbers", []))
    try:
        return int(str(raw)) if raw is not None else None
    except ValueError:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--scheme")
    parser.add_argument("--configuration", default="Release")
    parser.add_argument("--build-number", type=int)
    parser.add_argument("--marketing-version")
    parser.add_argument("--output-dir", default=".testflight")
    parser.add_argument("--workspace", help="Explicit .xcworkspace or .xcodeproj path")
    parser.add_argument("--upload", action="store_true", help="Actually upload to App Store Connect")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing them")
    parser.add_argument("--authentication-key-path")
    parser.add_argument("--authentication-key-id")
    parser.add_argument("--authentication-key-issuer-id")
    parser.add_argument("--provisioning-profile")
    parser.add_argument(
        "--provisioning-profile-map",
        action="append",
        default=[],
        metavar="BUNDLE_ID=PROFILE_NAME",
        help="Repeat for the app and every embedded extension",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output_dir = (root / args.output_dir).resolve()
    dry_run = args.dry_run or not args.upload
    try:
        data = inspect(root)
        framework = data.get("framework")
        if framework not in {"swift/xcode", "flutter"}:
            raise ValueError(f"unsupported project type: {framework}")
        if (args.provisioning_profile or args.provisioning_profile_map) and framework != "swift/xcode":
            raise ValueError("manual provisioning profiles are supported only for Swift/Xcode projects")
        if args.upload and args.build_number is None:
            raise ValueError("--build-number is required with --upload; read the latest App Store Connect build first")
        build_number = args.build_number
        if build_number is None:
            current = resolve_current_build(data)
            if current is None:
                raise ValueError("pass --build-number because the current build number could not be determined")
            build_number = current + 1
        if build_number <= 0:
            raise ValueError("--build-number must be a positive integer")
        marketing_version = args.marketing_version or resolve_version(data, None)
        if not marketing_version:
            raise ValueError("pass --marketing-version because the marketing version could not be determined")
        bundle_id = first_nonempty(data.get("bundle_ids", [])) or ""
        provisioning_profiles = parse_provisioning_profile_maps(args.provisioning_profile_map)
        if args.provisioning_profile and not bundle_id:
            raise ValueError("--provisioning-profile requires an application Bundle ID")
        if args.provisioning_profile:
            if bundle_id in provisioning_profiles:
                raise ValueError(f"duplicate provisioning profile mapping for {bundle_id}")
            provisioning_profiles[bundle_id] = args.provisioning_profile
        if args.upload and not args.authentication_key_path:
            print("warning: no App Store Connect API key supplied; Xcode must have a signed-in account", file=sys.stderr)

        compliance_plists = ensure_export_compliance_metadata(root, data, framework, dry_run=dry_run)

        print(json.dumps({
            "root": str(root),
            "framework": framework,
            "bundle_ids": data.get("bundle_ids", []),
            "scheme": args.scheme,
            "marketing_version": marketing_version,
            "build_number": build_number,
            "upload_requested": args.upload,
            "dry_run": dry_run,
            "output_dir": str(output_dir),
            "export_compliance": {
                "key": EXPORT_COMPLIANCE_KEY,
                "value": False,
                "source_plists": compliance_plists,
            },
        }, ensure_ascii=False, indent=2))

        if not dry_run:
            output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        if framework == "flutter":
            export_options = output_dir / f"export-options-{timestamp}.plist"
            if dry_run:
                print(f"would write export options: {export_options}")
            else:
                write_export_options(
                    export_options,
                    destination="export",
                    provisioning_profiles=provisioning_profiles,
                )
            command = [
                "flutter", "build", "ipa", "--release",
                "--build-number", str(build_number),
                "--build-name", marketing_version,
                "--export-options-plist", str(export_options),
            ]
            run(command, root, dry_run=dry_run)
            # `flutter build ipa` reads back build/ios/ipa after exporting. A
            # destination=upload export writes no local IPA, so the tool crashes
            # on a successful upload and reports failure. Always export locally,
            # then upload the archive in a separate xcodebuild step.
            ipa_dir = root / "build" / "ios" / "ipa"
            archive_path = root / "build" / "ios" / "archive" / "Runner.xcarchive"
            print(f"artifact directory: {ipa_dir}")
            if args.upload:
                if dry_run:
                    print(f"would validate exported IPA in {ipa_dir}")
                else:
                    validate_exported_ipa(
                        ipa_dir,
                        expected_bundle_ids={bundle_id},
                        marketing_version=marketing_version,
                        build_number=build_number,
                    )
                upload_options = output_dir / f"upload-options-{timestamp}.plist"
                if dry_run:
                    print(f"would write upload options: {upload_options}")
                else:
                    write_export_options(
                        upload_options,
                        destination="upload",
                        provisioning_profiles=provisioning_profiles,
                    )
                upload = [
                    "xcodebuild", "-exportArchive",
                    "-archivePath", str(archive_path),
                    "-exportPath", str(output_dir / f"upload-{marketing_version}-{build_number}"),
                    "-exportOptionsPlist", str(upload_options),
                ]
                add_authentication_flags(upload, args)
                run(upload, root, dry_run=dry_run)
            return 0

        scheme = resolve_scheme(data, args.scheme)
        project_or_workspace = Path(args.workspace).expanduser().resolve() if args.workspace else None
        if project_or_workspace is None:
            project_or_workspace = Path(data["workspace"] or data["project"])
        archive_path = output_dir / f"{scheme}-{marketing_version}-{build_number}.xcarchive"
        export_path = output_dir / f"export-{marketing_version}-{build_number}"
        export_options = output_dir / f"export-options-{timestamp}.plist"
        if dry_run:
            print(f"would write export options: {export_options}")
        else:
            write_export_options(
                export_options,
                destination="export",
                provisioning_profiles=provisioning_profiles,
            )

        base = ["xcodebuild"]
        if project_or_workspace.suffix == ".xcworkspace":
            base.extend(["-workspace", str(project_or_workspace)])
        else:
            base.extend(["-project", str(project_or_workspace)])
        archive = base + [
            "-scheme", scheme,
            "-configuration", args.configuration,
            "-destination", "generic/platform=iOS",
            "-archivePath", str(archive_path),
            "-allowProvisioningUpdates",
            "MARKETING_VERSION=" + marketing_version,
            "CURRENT_PROJECT_VERSION=" + str(build_number),
            "INFOPLIST_KEY_" + EXPORT_COMPLIANCE_KEY + "=NO",
        ]
        add_authentication_flags(archive, args)
        archive.append("archive")
        run(archive, root, dry_run=dry_run)

        export = [
            "xcodebuild", "-exportArchive",
            "-archivePath", str(archive_path),
            "-exportPath", str(export_path),
            "-exportOptionsPlist", str(export_options),
        ]
        add_authentication_flags(export, args)
        run(export, root, dry_run=dry_run)
        print(f"artifact directory: {export_path}")
        if args.upload:
            if dry_run:
                print(f"would validate exported IPA in {export_path}")
            else:
                validate_exported_ipa(
                    export_path,
                    expected_bundle_ids=set(provisioning_profiles) or {bundle_id},
                    marketing_version=marketing_version,
                    build_number=build_number,
                )
            upload_options = output_dir / f"upload-options-{timestamp}.plist"
            if dry_run:
                print(f"would write upload options: {upload_options}")
            else:
                write_export_options(
                    upload_options,
                    destination="upload",
                    provisioning_profiles=provisioning_profiles,
                )
            upload = [
                "xcodebuild", "-exportArchive",
                "-archivePath", str(archive_path),
                "-exportPath", str(output_dir / f"upload-{marketing_version}-{build_number}"),
                "-exportOptionsPlist", str(upload_options),
            ]
            add_authentication_flags(upload, args)
            run(upload, root, dry_run=dry_run)
        return 0
    except (OSError, RuntimeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"build_testflight.py: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
