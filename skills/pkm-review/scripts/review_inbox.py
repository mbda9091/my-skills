#!/usr/bin/env python3
"""Review inbox notes and suggest PKM workflow actions."""

from __future__ import annotations

import argparse
import json
import os
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
    parser.add_argument("--vault", help="Optional confirmation of PKM_VALUT_DIR; cannot select a different vault.")
    parser.add_argument("--scope", choices=["ai", "inbox"], default="ai")
    parser.add_argument("--json", action="store_true")
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
    root = (vault / ("00_inbox/AI Conversations" if args.scope == "ai" else "00_inbox")).resolve()
    if not root.is_relative_to(vault):
        raise SystemExit("Review root must be inside PKM_VALUT_DIR.")
    if not root.exists():
        raise SystemExit(f"Review root does not exist: {root}")

    groups: dict[str, list[dict[str, str]]] = {"distill": [], "triage": [], "link": []}
    for path in sorted(root.rglob("*.md")):
        if not path.resolve().is_relative_to(vault):
            raise SystemExit(f"Review file must be inside PKM_VALUT_DIR: {path}")
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
