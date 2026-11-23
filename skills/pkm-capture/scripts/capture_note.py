#!/usr/bin/env python3
"""Create a raw capture note in an Obsidian/PKM vault."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import date, datetime, timedelta, timezone
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


def frontmatter(stamp: str) -> str:
    return f"""---
type: inbox
status: inbox
created: {stamp}
updated: {stamp}
tags:
  - inbox
---"""


def inbox_body(title: str, content: str, context: str) -> str:
    return f"""# {title}

## Capture
{content}

## Context
{context}
"""


def render_ai(vault: Path, values: dict[str, str], stamp: str) -> str:
    template = (vault / "Templates/QuickAdd-PKM-AI-Conversation.md").resolve()
    if not template.is_relative_to(vault) or not template.is_file():
        raise SystemExit("AI fallback requires the vault's Templates/QuickAdd-PKM-AI-Conversation.md.")
    text = template.read_text(encoding="utf-8")

    def replace(match: re.Match[str]) -> str:
        token = match.group(1)
        if token == "DATE:YYYY-MM-DD HH:mm":
            return stamp
        if token.startswith("value:"):
            key = token[6:].split("|", 1)[0]
            if key in values:
                return values[key]
        raise SystemExit(f"Unsupported template token: {{{{{token}}}}}; render it explicitly before writing.")

    return re.sub(r"\{\{([^{}]+)\}\}", replace, text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", help="Optional confirmation of PKM_VALUT_DIR; cannot select a different vault.")
    parser.add_argument("--kind", choices=sorted(KIND_DIR), required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--content")
    parser.add_argument("--content-file")
    parser.add_argument("--prompt", default="")
    parser.add_argument("--context", default="")
    parser.add_argument("--context-file", help="UTF-8 context file, mutually exclusive with --context.")
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

    now = datetime.now(timezone(timedelta(hours=8), "Asia/Shanghai"))
    stamp = now.strftime("%Y-%m-%d %H:%M")
    date_str = args.date or now.strftime("%Y-%m-%d")
    try:
        if date.fromisoformat(date_str).isoformat() != date_str:
            raise ValueError
    except ValueError:
        raise SystemExit("--date must be a valid YYYY-MM-DD date.")
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
    if args.context and args.context_file:
        raise SystemExit("Provide only one of --context or --context-file.")
    context = Path(args.context_file).read_text(encoding="utf-8").strip() if args.context_file else args.context
    if args.kind == "ai_conversation":
        note = render_ai(vault, {"title": title, "date": date_str, "context": context,
                                "prompt": args.prompt, "raw_answer": content}, stamp)
    else:
        note = frontmatter(stamp) + "\n\n" + inbox_body(title, content, context)
    target_dir.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as output:
        output.write(note.rstrip() + "\n")
    print(json.dumps({"created": str(target), "relative_path": str(target.relative_to(vault))}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
