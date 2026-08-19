#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unicodedata


SKILL_DIR = Path(__file__).resolve().parent.parent
INSPECTOR = SKILL_DIR / "scripts" / "inspect_ios_project.py"
DEFAULT_STUDIO_ROOT = Path.home() / "AppStudio"
DEFAULT_TMPDIR = Path(tempfile.gettempdir()) / "app-studio-tmp"
FALLBACK_EXIT = 20


def canonical(path: str | Path) -> str:
    return unicodedata.normalize("NFC", str(Path(path).expanduser().resolve()))


def capture_json(command: list[str], cwd: Path) -> dict:
    proc = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        detail = proc.stderr.strip() or proc.stdout.strip() or f"exit {proc.returncode}"
        raise RuntimeError(f"JSON command failed: {' '.join(command)}\n{detail}") from exc


def source_bundle_ids(report: dict) -> set[str]:
    values: list[str] = []
    xcode = report.get("xcode")
    if isinstance(xcode, dict):
        for key in ("app_bundle_ids", "bundle_ids"):
            item = xcode.get(key)
            if isinstance(item, list):
                values.extend(value for value in item if isinstance(value, str))

    flutter = report.get("flutter") or {}
    if isinstance(flutter, dict):
        for key in ("bundle_ids", "app_bundle_ids"):
            item = flutter.get(key)
            if isinstance(item, list):
                values.extend(value for value in item if isinstance(value, str))

    if not values:
        item = report.get("bundle_ids")
        if isinstance(item, list):
            values.extend(value for value in item if isinstance(value, str))
    return set(values)


def fallback(message: str) -> int:
    print("ROUTE=FALLBACK")
    print(f"REASON={message}")
    print(
        "NEXT=Run inspect_ios_project.py, resolve identity, and use the SKILL fallback path."
    )
    return FALLBACK_EXIT


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Use App Studio for an aligned registered iOS project; dry-run by default."
    )
    parser.add_argument("--root", default=".", help="iOS/Flutter project root")
    parser.add_argument("--app-id", help="require this App Studio app id")
    parser.add_argument(
        "--studio-root",
        default=os.environ.get("APP_STUDIO_ROOT", str(DEFAULT_STUDIO_ROOT)),
        help="App Studio checkout (or set APP_STUDIO_ROOT)",
    )
    parser.add_argument(
        "--upload", action="store_true", help="actually archive, export, and upload"
    )
    parser.add_argument("--no-wait", action="store_true", help="skip Apple processing wait")
    parser.add_argument("--verbose", action="store_true", help="show full build/upload output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    project_root = Path(args.root).expanduser().resolve()
    studio_root = Path(args.studio_root).expanduser().resolve()
    studio_entry = studio_root / "src" / "cli" / "index.ts"

    if not project_root.is_dir():
        return fallback(f"project root does not exist: {project_root}")
    if not studio_entry.is_file():
        return fallback(f"App Studio engine not found: {studio_entry}")
    if not INSPECTOR.is_file():
        return fallback(f"bundled inspector not found: {INSPECTOR}")

    try:
        inventory = capture_json(
            ["node", str(studio_entry), "status", "--json"], cwd=studio_root
        )
    except RuntimeError as exc:
        return fallback(str(exc))

    wanted_path = canonical(project_root)
    apps = inventory.get("apps") or []
    matches = [
        app
        for app in apps
        if isinstance(app, dict)
        and canonical(app.get("path", "")) == wanted_path
        and (not args.app_id or app.get("id") == args.app_id)
    ]
    if len(matches) != 1:
        return fallback(f"expected one App Studio path match, found {len(matches)}")

    app = matches[0]
    app_id = app.get("id")
    if not app_id:
        return fallback("matched record has no app id")
    if not app.get("exists", False):
        return fallback("matched App Studio path is marked missing")
    if app.get("stackMismatch", False):
        return fallback("registered and detected stacks disagree")
    if "ios" not in (app.get("platforms") or []):
        return fallback("matched record is not iOS-capable")

    record_bundle = (((app.get("store") or {}).get("ios") or {}).get("bundle_id"))
    if not record_bundle:
        return fallback("App Studio record has no iOS Bundle ID")

    try:
        report = capture_json(
            [sys.executable, str(INSPECTOR), "--root", str(project_root)], cwd=project_root
        )
    except RuntimeError as exc:
        return fallback(str(exc))

    bundles = source_bundle_ids(report)
    if record_bundle not in bundles:
        return fallback(
            "App Studio Bundle ID does not match source project Bundle IDs; refusing release"
        )

    env = os.environ.copy()
    tmpdir = Path(env.get("APP_STUDIO_TMPDIR", str(DEFAULT_TMPDIR)))
    tmpdir.mkdir(parents=True, exist_ok=True, mode=0o700)
    env["TMPDIR"] = str(tmpdir)

    base = ["node", str(studio_entry), "release", str(app_id), "--platform", "ios"]
    dry_run = subprocess.run(base + ["--dry-run"], cwd=studio_root, env=env, check=False)
    if dry_run.returncode != 0:
        return fallback(f"App Studio release dry-run failed with exit {dry_run.returncode}")

    print("ROUTE=FAST_PATH")
    print(f"APP_ID={app_id}")
    print(f"PROJECT_ROOT={project_root}")
    print("IDENTITY=matched")
    print("MODE=upload" if args.upload else "MODE=dry-run")

    if not args.upload:
        print("FAST_PATH_READY")
        print("NEXT=Re-run with --upload only when the current user explicitly authorizes upload.")
        return 0

    command = list(base)
    if args.no_wait:
        command.append("--no-wait")
    if args.verbose:
        command.append("--verbose")
    return subprocess.run(command, cwd=studio_root, env=env, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
