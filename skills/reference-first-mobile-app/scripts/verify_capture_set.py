#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

from inspect_reference_packet import IMAGE_SUFFIXES, image_size

SOURCE_SUFFIXES = {".swift", ".dart", ".json", ".arb", ".strings", ".xcstrings", ".yaml"}


def newest_source(root: Path) -> tuple[float, Path | None]:
    candidates = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES and ".build" not in path.parts and "build" not in path.parts
    ]
    if not candidates:
        return 0.0, None
    newest = max(candidates, key=lambda path: path.stat().st_mtime)
    return newest.stat().st_mtime, newest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--expected", type=int, default=10)
    parser.add_argument("--locale", required=True)
    args = parser.parse_args()

    images = sorted(
        path for path in args.directory.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    if len(images) != args.expected:
        raise SystemExit(f"expected {args.expected} captures, found {len(images)}")
    newest_time, newest_path = newest_source(args.source_root)
    seen: set[str] = set()
    sizes: set[tuple[int, int]] = set()
    for path in images:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in seen:
            raise SystemExit(f"duplicate capture content: {path}")
        seen.add(digest)
        sizes.add(image_size(path))
        if path.stat().st_mtime < newest_time:
            raise SystemExit(f"stale capture {path}; newer source is {newest_path}")
    if len(sizes) != 1:
        raise SystemExit(f"capture viewport mismatch: {sorted(sizes)}")
    print(f"PASS locale={args.locale} count={len(images)} viewport={next(iter(sizes))}")


if __name__ == "__main__":
    main()
