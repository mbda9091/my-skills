#!/usr/bin/env python3
"""Append a de-duplicated entry under a Markdown heading."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def append_under_heading(text: str, heading: str, entry: str) -> tuple[str, bool]:
    entry = entry.strip()
    if entry in text:
        return text, False

    heading_line = f"## {heading}"
    if heading_line not in text:
        updated = text.rstrip() + f"\n\n{heading_line}\n{entry}\n"
        return updated, True

    pattern = re.compile(rf"(^## {re.escape(heading)}\s*$)(.*?)(?=^##\s|\Z)", re.M | re.S)
    match = pattern.search(text)
    if not match:
        updated = text.rstrip() + f"\n\n{heading_line}\n{entry}\n"
        return updated, True

    section = match.group(2).rstrip()
    replacement = match.group(1) + "\n" + section + ("\n" if section else "") + entry + "\n"
    return text[: match.start()] + replacement + text[match.end() :], True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", default=".")
    parser.add_argument("--file", required=True, help="Markdown file path relative to vault.")
    parser.add_argument("--heading", required=True, help="Heading text without leading ##.")
    parser.add_argument("--entry", required=True)
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    target = (vault / args.file).resolve()
    if not str(target).startswith(str(vault)):
        raise SystemExit("Target file must be inside the vault.")
    if target.exists():
        text = target.read_text(encoding="utf-8")
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        text = f"# {target.stem}\n"

    updated, changed = append_under_heading(text, args.heading, args.entry)
    if changed:
        target.write_text(updated.rstrip() + "\n", encoding="utf-8")

    print(json.dumps({"file": str(target), "changed": changed}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
