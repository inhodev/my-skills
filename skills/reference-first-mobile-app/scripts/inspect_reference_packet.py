#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def image_size(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"\xff\xd8"):
        index = 2
        while index + 9 < len(data):
            if data[index] != 0xFF:
                index += 1
                continue
            marker = data[index + 1]
            index += 2
            if marker in {0xD8, 0xD9}:
                continue
            if index + 2 > len(data):
                break
            length = int.from_bytes(data[index : index + 2], "big")
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                return (
                    int.from_bytes(data[index + 5 : index + 7], "big"),
                    int.from_bytes(data[index + 3 : index + 5], "big"),
                )
            index += length
    raise ValueError(f"unsupported or corrupt image: {path}")


def inspect(directory: Path, expected: int) -> list[dict[str, object]]:
    images = sorted(
        path for path in directory.iterdir() if path.is_file() and path.suffix.lower() in IMAGE_SUFFIXES
    )
    if len(images) != expected:
        raise ValueError(f"expected {expected} images, found {len(images)} in {directory}")
    records: list[dict[str, object]] = []
    hashes: set[str] = set()
    for index, path in enumerate(images, start=1):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in hashes:
            raise ValueError(f"duplicate image content: {path}")
        hashes.add(digest)
        width, height = image_size(path)
        records.append(
            {
                "id": f"{index:02d}",
                "reference": str(path.resolve()),
                "width": width,
                "height": height,
                "sha256": digest,
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--expected", type=int, default=10)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    records = inspect(args.directory, args.expected)
    payload = {"count": len(records), "references": records}
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
