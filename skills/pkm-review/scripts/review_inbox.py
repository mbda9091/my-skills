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


EXCLUDED_DIRS = {".git", ".obsidian", ".agents", ".codex", ".stversions", ".stfolder",
                 "test", "tests", "backup", "backups", ".backup", ".backups"}
PROCESSED_STATUSES = {"processed", "completed", "archived", "cancelled", "distilled"}


def ignored(path: Path) -> bool:
    return (path.name in {"Welcome.md", "Untitled.md"}
            or any(part.lower() in EXCLUDED_DIRS for part in path.parts)
            or ("03 Resources" in path.parts and path.name.startswith("Untitled")))


def metadata(text: str, key: str) -> str:
    """Read only the simple scalar fields used by inbox templates."""
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", text, re.S)
    if not match:
        return ""
    field = re.search(rf"^{re.escape(key)}:[ \t]*([^\r\n]*)$", match.group(1), re.M)
    return field.group(1).split(" #", 1)[0].strip().strip("\"'").lower() if field else ""


def sections(text: str) -> dict[str, str]:
    """Ignore fenced examples so quoted headings do not become note sections."""
    visible = []
    fence = ""
    length = 0
    for line in text.splitlines():
        marker = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line)
        if marker:
            token = marker.group(1)
            if not fence:
                fence, length = token[0], len(token)
            elif token[0] == fence and len(token) >= length and not marker.group(2).strip():
                fence = ""
            continue
        if not fence:
            visible.append(line)
    result = {}
    current = ""
    for line in visible:
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current = heading.group(1).lower()
            result.setdefault(current, [])
        elif current:
            result[current].append(line)
    return {name: "\n".join(lines) for name, lines in result.items()}


def has_content(text: str) -> bool:
    empty = {"", "无", "无。", "暂无", "暂无。", "none", "none.", "n/a", "待补充", "待补充。"}
    for line in text.splitlines():
        value = re.sub(r"^\s*(?:[-*+]\s*)?(?:\[[ xX-]\]\s*)?", "", line).strip()
        if value and value.lower() not in empty:
            return True
    return False


def classify(path: Path, text: str) -> str | None:
    if ignored(path) or metadata(text, "status") in PROCESSED_STATUSES:
        return None
    parts = sections(text)
    if has_content(parts.get("to verify", "")):
        return "verify"
    related = parts.get("related", "")
    if re.search(r"^\s*-\s*Resource:\s*\[\[.+?\]\]", related, re.I | re.M):
        return None
    is_ai = metadata(text, "type") == "ai_conversation" or "AI Conversations" in path.parts
    if is_ai:
        if re.search(r"\[\[03 Resources/[^\]]+\]\]", parts.get("extracted value", "")):
            return "link"
        return "distill"
    return "triage"


def reason(action: str) -> str:
    return {
        "distill": "raw material likely contains reusable knowledge or verification items",
        "triage": "capture still needs PARA destination",
        "link": "note appears weakly connected to project, area, or resource",
        "verify": "To Verify contains claims requiring source verification",
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

    groups: dict[str, list[dict[str, str]]] = {"distill": [], "triage": [], "link": [], "verify": []}
    for path in sorted(root.rglob("*.md")):
        if ignored(path.relative_to(vault)):
            continue
        if not path.resolve().is_relative_to(vault):
            raise SystemExit(f"Review file must be inside PKM_VALUT_DIR: {path}")
        text = path.read_text(encoding="utf-8")
        action = classify(path.relative_to(vault), text)
        if action is None:
            continue
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
