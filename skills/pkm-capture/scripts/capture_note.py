#!/usr/bin/env python3
"""Create a raw capture note in an Obsidian/PKM vault."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path


KIND_DIR = {
    "ai_conversation": Path("00_inbox/AI Conversations"),
    "inbox": Path("00_inbox"),
}


def clean_filename(title: str) -> str:
    name = re.sub(r'[\\/:*?"<>|#^\[\]]+', "-", title.strip())
    name = re.sub(r"\s+", " ", name).strip(" .-")
    return name or "Untitled"


def read_content(args: argparse.Namespace) -> str:
    if args.content_file:
        return Path(args.content_file).read_text(encoding="utf-8").strip()
    return (args.content or "").strip()


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    for index in range(2, 1000):
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise SystemExit(f"Could not find unique path for {path}")


def frontmatter(kind: str, stamp: str) -> str:
    if kind == "ai_conversation":
        return f"""---
type: ai_conversation
source_type: ai
status: inbox
created: {stamp}
updated: {stamp}
model:
platform:
related_project:
related_area:
tags:
  - ai/conversation
---"""
    return f"""---
type: inbox
status: inbox
created: {stamp}
updated: {stamp}
tags:
  - inbox
---"""


def body(kind: str, title: str, date_str: str, content: str, prompt: str) -> str:
    if kind == "ai_conversation":
        return f"""# {date_str} {title}

## Context
- 

## Prompt
> {prompt}

## Raw Answer
{content}

## Extracted Value
- 

## Decisions
- 

## To Verify
- 

## Actions
- [ ] 

## Related
- Project:
- Area:
- Resource:
"""
    return f"""# {title}

## Capture
{content}

## Context

## Next
- [ ] Triage this note.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", help="Optional confirmation of PKM_VALUT_DIR; cannot select a different vault.")
    parser.add_argument("--kind", choices=sorted(KIND_DIR), required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--content")
    parser.add_argument("--content-file")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--date", help="YYYY-MM-DD. Defaults to today.")
    parser.add_argument("--unique", action="store_true")
    args = parser.parse_args()

    configured_vault = os.environ.get("PKM_VALUT_DIR")
    if not configured_vault or not configured_vault.strip():
        raise SystemExit("PKM_VALUT_DIR must be set to the absolute target vault directory.")
    vault = Path(configured_vault)
    if not vault.is_absolute():
        raise SystemExit("PKM_VALUT_DIR must be an absolute path.")
    if not vault.is_dir():
        raise SystemExit(f"PKM_VALUT_DIR must name an existing directory: {vault}")
    vault = vault.resolve()
    if args.vault is not None and Path(args.vault).expanduser().resolve() != vault:
        raise SystemExit("--vault must match PKM_VALUT_DIR; it cannot select another vault.")

    now = datetime.now()
    stamp = now.strftime("%Y-%m-%d %H:%M")
    date_str = args.date or now.strftime("%Y-%m-%d")
    title = args.title.strip()
    filename = clean_filename(title)
    if args.kind == "ai_conversation":
        filename = f"{date_str}-{filename}"

    target_dir = (vault / KIND_DIR[args.kind]).resolve()
    if not target_dir.is_relative_to(vault):
        raise SystemExit("Capture directory must be inside PKM_VALUT_DIR.")
    target = target_dir / f"{filename}.md"
    if target.exists():
        if args.unique:
            target = unique_path(target)
        else:
            raise SystemExit(f"Refusing to overwrite existing note: {target}")

    if not target.resolve().is_relative_to(vault):
        raise SystemExit("Capture file must be inside PKM_VALUT_DIR.")

    content = read_content(args)
    note = frontmatter(args.kind, stamp) + "\n\n" + body(args.kind, title, date_str, content, args.prompt)
    target_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(note.rstrip() + "\n", encoding="utf-8")
    print(json.dumps({"created": str(target), "relative_path": str(target.relative_to(vault))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
