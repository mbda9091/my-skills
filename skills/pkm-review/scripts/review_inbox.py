#!/usr/bin/env python3
"""Review inbox notes and suggest PKM workflow actions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def note_title(text: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+)$", text, re.M)
    return match.group(1).strip() if match else fallback


def classify(path: Path, text: str) -> str:
    lowered = text.lower()
    if "## extracted value" in lowered and re.search(r"## Extracted Value\s*\n-\s*$", text, re.M):
        return "distill"
    if "to verify" in lowered:
        return "distill"
    if "related\n- project:\n- area:\n- resource:" in lowered:
        return "link"
    if "type: inbox" in lowered:
        return "triage"
    if "ai_conversation" in lowered:
        return "distill"
    return "triage"


def reason(action: str) -> str:
    return {
        "distill": "raw material likely contains reusable knowledge or verification items",
        "triage": "capture still needs PARA destination",
        "link": "note appears weakly connected to project, area, or resource",
    }.get(action, "needs review")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", default=".")
    parser.add_argument("--scope", choices=["ai", "inbox"], default="ai")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    vault = Path(args.vault).expanduser().resolve()
    root = vault / ("00_inbox/AI Conversations" if args.scope == "ai" else "00_inbox")
    if not root.exists():
        raise SystemExit(f"Review root does not exist: {root}")

    groups: dict[str, list[dict[str, str]]] = {"distill": [], "triage": [], "link": []}
    for path in sorted(root.rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        action = classify(path, text)
        groups.setdefault(action, []).append(
            {
                "file": str(path.relative_to(vault)),
                "title": note_title(text, path.stem),
                "reason": reason(action),
            }
        )

    if args.json:
        print(json.dumps(groups, ensure_ascii=False, indent=2))
        return 0

    print("## Review Result")
    for heading, items in groups.items():
        print(f"\n### {heading.title()}")
        if not items:
            print("- None")
            continue
        for item in items:
            print(f"- {item['file']}: {item['reason']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
