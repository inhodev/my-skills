#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from factory_store import (
    ACTIVE_PHASES,
    READY_PHASES,
    TRANSITIONS,
    active_count,
    app_for,
    atomic_text,
    mark_ready,
    mutate,
    read_locked,
    record,
    require_session,
    timestamp,
)


def command_init(args: argparse.Namespace) -> None:
    if args.state.exists():
        raise SystemExit(f"refusing to overwrite existing state: {args.state}")
    parsed: list[tuple[str, str]] = []
    for value in args.app:
        if "=" not in value:
            raise SystemExit(f"app must be ID=NAME: {value}")
        app_id, name = value.split("=", 1)
        parsed.append((app_id.strip(), name.strip()))
    if not parsed or len({app_id for app_id, _ in parsed}) != len(parsed):
        raise SystemExit("apps must be non-empty with unique IDs")
    state = {
        "version": 1,
        "revision": 0,
        "max_active": args.max_active,
        "max_observed_active": 0,
        "ready_sequence": 0,
        "created_at": timestamp(),
        "apps": [
            {
                "id": app_id,
                "name": name,
                "order": index,
                "phase": "QUEUED",
                "thread_id": None,
                "ready_sequence": None,
                "reservation": None,
                "last_note": "queued",
                "history": [],
            }
            for index, (app_id, name) in enumerate(parsed, start=1)
        ],
    }
    atomic_text(args.state, json.dumps(state, ensure_ascii=False, indent=2) + "\n")
    print(args.state.resolve())


def command_bind(args: argparse.Namespace) -> None:
    def action(state: dict[str, Any]) -> None:
        app = app_for(state, args.app_id)
        if app["thread_id"] and app["thread_id"] != args.thread:
            raise SystemExit(f"app already bound to {app['thread_id']}")
        app["thread_id"] = args.thread
        record(state, app, "BOUND", args.note)
    mutate(args.state, action)


def command_transition(args: argparse.Namespace) -> None:
    def action(state: dict[str, Any]) -> None:
        app = app_for(state, args.app_id)
        allowed = TRANSITIONS.get(app["phase"], set())
        if args.to not in allowed:
            raise SystemExit(f"invalid transition {app['phase']} -> {args.to}")
        if args.to in READY_PHASES:
            mark_ready(state, app, args.to)
        else:
            app["phase"] = args.to
        record(state, app, f"PHASE_{args.to}", args.note)
    mutate(args.state, action)


def command_reserve(args: argparse.Namespace) -> None:
    def action(state: dict[str, Any]) -> None:
        app = app_for(state, args.app_id)
        require_session(app, args.thread)
        if app["phase"] not in READY_PHASES:
            raise SystemExit(f"app is not ready: {app['phase']}")
        if active_count(state) >= state["max_active"]:
            raise SystemExit("no maker slot available")
        eligible = sorted(
            (item for item in state["apps"] if item["phase"] in READY_PHASES),
            key=lambda item: (item["ready_sequence"], item["order"]),
        )
        if not eligible or eligible[0]["id"] != app["id"]:
            raise SystemExit(f"FIFO head is {eligible[0]['id']}")
        previous = app["phase"]
        app["phase"] = "BUILD" if previous == "BUILD_READY" else "CORRECTION"
        app["reservation"] = {"thread_id": args.thread, "reserved_at": timestamp(), "heartbeat_at": timestamp()}
        state["max_observed_active"] = max(state["max_observed_active"], active_count(state))
        record(state, app, f"RESERVED_{app['phase']}", args.note)
    mutate(args.state, action)


def command_advance(args: argparse.Namespace) -> None:
    allowed = {"BUILD": "HEADLESS_QA", "CORRECTION": "HEADLESS_QA", "HEADLESS_QA": "VISUAL_QA"}

    def action(state: dict[str, Any]) -> None:
        app = app_for(state, args.app_id)
        require_session(app, args.thread)
        if not app["reservation"] or allowed.get(app["phase"]) != args.to:
            raise SystemExit(f"invalid active transition {app['phase']} -> {args.to}")
        app["phase"] = args.to
        app["reservation"]["heartbeat_at"] = timestamp()
        record(state, app, f"PHASE_{args.to}", args.note)

    mutate(args.state, action)


def command_heartbeat(args: argparse.Namespace) -> None:
    def action(state: dict[str, Any]) -> None:
        app = app_for(state, args.app_id)
        require_session(app, args.thread)
        if app["phase"] not in ACTIVE_PHASES or not app["reservation"]:
            raise SystemExit(f"app has no active reservation: {app['phase']}")
        app["reservation"]["heartbeat_at"] = timestamp()
        record(state, app, "HEARTBEAT", args.note)

    mutate(args.state, action)


def command_settle(args: argparse.Namespace) -> None:
    outcomes = {
        "user_qa": "USER_QA",
        "complete": "COMPLETE",
        "correction": "CORRECTION_READY",
        "attention": "ATTENTION",
    }

    def action(state: dict[str, Any]) -> None:
        app = app_for(state, args.app_id)
        require_session(app, args.thread)
        if app["phase"] not in ACTIVE_PHASES or not app["reservation"]:
            raise SystemExit(f"app has no active reservation: {app['phase']}")
        target = outcomes[args.outcome]
        app["reservation"] = None
        if target == "CORRECTION_READY":
            mark_ready(state, app, target)
        else:
            app["phase"] = target
            app["ready_sequence"] = None
        record(state, app, f"SETTLED_{target}", args.note)

    mutate(args.state, action)


def command_inspect(args: argparse.Namespace) -> None:
    state = read_locked(args.state)
    payload = {
        "revision": state["revision"],
        "active": active_count(state),
        "max_active": state["max_active"],
        "max_observed_active": state["max_observed_active"],
        "apps": [
            {key: app[key] for key in ("id", "name", "phase", "thread_id", "ready_sequence", "last_note")}
            for app in state["apps"]
        ],
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def command_report(args: argparse.Namespace) -> None:
    state = read_locked(args.state)
    lines = [
        "# Morning Report",
        "",
        f"Active maker jobs: {active_count(state)} / {state['max_active']}",
        f"Observed maximum active maker jobs: {state['max_observed_active']}",
        "",
    ]
    for app in sorted(state["apps"], key=lambda item: item["order"]):
        lines.extend(
            [
                f"## {app['id']} · {app['name']}",
                "",
                f"- Phase: `{app['phase']}`",
                f"- Session: `{app['thread_id'] or 'UNBOUND'}`",
                f"- Last verified event: {app['last_note']}",
                "",
            ]
        )
    atomic_text(args.output, "\n".join(lines))
    print(args.output.resolve())


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser()
    commands = root.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init")
    init.add_argument("state", type=Path)
    init.add_argument("--max-active", type=int, default=2, choices=(1, 2))
    init.add_argument("--app", action="append", required=True)
    init.set_defaults(run=command_init)
    for name, handler in (("bind", command_bind), ("transition", command_transition)):
        command = commands.add_parser(name)
        command.add_argument("state", type=Path)
        command.add_argument("--app", dest="app_id", required=True)
        command.add_argument("--note", required=True)
        if name == "bind":
            command.add_argument("--thread", required=True)
        else:
            command.add_argument("--to", required=True)
        command.set_defaults(run=handler)
    for name, handler in (("reserve", command_reserve), ("advance", command_advance), ("heartbeat", command_heartbeat)):
        command = commands.add_parser(name)
        command.add_argument("state", type=Path)
        command.add_argument("--app", dest="app_id", required=True)
        command.add_argument("--thread", required=True)
        command.add_argument("--note", required=True)
        if name == "advance":
            command.add_argument("--to", choices=("HEADLESS_QA", "VISUAL_QA"), required=True)
        command.set_defaults(run=handler)
    settle = commands.add_parser("settle")
    settle.add_argument("state", type=Path)
    settle.add_argument("--app", dest="app_id", required=True)
    settle.add_argument("--thread", required=True)
    settle.add_argument("--outcome", choices=("user_qa", "complete", "correction", "attention"), required=True)
    settle.add_argument("--note", required=True)
    settle.set_defaults(run=command_settle)
    inspect = commands.add_parser("inspect")
    inspect.add_argument("state", type=Path)
    inspect.set_defaults(run=command_inspect)
    report = commands.add_parser("report")
    report.add_argument("state", type=Path)
    report.add_argument("--output", type=Path, required=True)
    report.set_defaults(run=command_report)
    return root


def main() -> None:
    args = parser().parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
