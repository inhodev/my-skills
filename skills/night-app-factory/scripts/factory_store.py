from __future__ import annotations

import fcntl
import json
import os
import tempfile
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

READY_PHASES = {"BUILD_READY", "CORRECTION_READY"}
ACTIVE_PHASES = {"BUILD", "CORRECTION", "HEADLESS_QA", "VISUAL_QA"}
TRANSITIONS = {
    "QUEUED": {"DISCOVERY"},
    "DISCOVERY": {"DESIGN"},
    "DESIGN": {"BUILD_READY", "ATTENTION"},
    "ATTENTION": {"DISCOVERY"},
    "USER_QA": {"CORRECTION_READY", "COMPLETE"},
}


def timestamp() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temporary = Path(handle.name)
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def mutate(path: Path, action: Callable[[dict[str, Any]], Any]) -> Any:
    lock_path = path.with_name(f"{path.name}.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if not path.exists():
            raise SystemExit(f"state does not exist: {path}")
        state = load(path)
        result = action(state)
        atomic_text(path, json.dumps(state, ensure_ascii=False, indent=2) + "\n")
        return result


def read_locked(path: Path) -> dict[str, Any]:
    lock_path = path.with_name(f"{path.name}.lock")
    with lock_path.open("a+", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        return load(path)


def app_for(state: dict[str, Any], app_id: str) -> dict[str, Any]:
    for app in state["apps"]:
        if app["id"] == app_id:
            return app
    raise SystemExit(f"unknown app: {app_id}")


def record(state: dict[str, Any], app: dict[str, Any], event: str, note: str) -> None:
    state["revision"] += 1
    app["last_note"] = note
    app["history"].append({"revision": state["revision"], "at": timestamp(), "event": event, "note": note})


def active_count(state: dict[str, Any]) -> int:
    return sum(app["reservation"] is not None for app in state["apps"])


def mark_ready(state: dict[str, Any], app: dict[str, Any], phase: str) -> None:
    state["ready_sequence"] += 1
    app["phase"] = phase
    app["ready_sequence"] = state["ready_sequence"]


def require_session(app: dict[str, Any], session: str) -> None:
    if app["thread_id"] != session:
        raise SystemExit(f"session mismatch for {app['id']}")
