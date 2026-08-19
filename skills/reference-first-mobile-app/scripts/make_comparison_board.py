#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from inspect_reference_packet import IMAGE_SUFFIXES


def images(directory: Path) -> list[Path]:
    return sorted(path.resolve() for path in directory.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--ko", type=Path, required=True)
    parser.add_argument("--en", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    references = json.loads(args.manifest.read_text(encoding="utf-8"))["references"]
    ko_images = images(args.ko)
    en_images = images(args.en)
    if not (len(references) == len(ko_images) == len(en_images) == 10):
        raise SystemExit("comparison board requires exactly ten reference, Korean, and English images")

    lines = ["# Reference / Korean / English", "", "Open every image individually; this board is supplementary.", ""]
    for record, ko_path, en_path in zip(references, ko_images, en_images, strict=True):
        screen_id = record["id"]
        lines.extend(
            [
                f"## Screen {screen_id}",
                "",
                "| Reference | Korean | English |",
                "|---|---|---|",
                f"| ![reference {screen_id}]({record['reference']}) | ![Korean {screen_id}]({ko_path}) | ![English {screen_id}]({en_path}) |",
                "",
            ]
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
