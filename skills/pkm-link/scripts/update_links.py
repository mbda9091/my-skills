#!/usr/bin/env python3
"""Append a link through the target vault's canonical wrapper."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", help="Optional confirmation of PKM_VALUT_DIR; cannot select a different vault.")
    parser.add_argument("--file", required=True, help="Markdown file path relative to vault.")
    parser.add_argument("--heading", required=True, help="Heading text without leading ##.")
    parser.add_argument("--entry", required=True)
    parser.add_argument("--check-only", action="store_true")
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
    relative = Path(args.file)
    if relative.is_absolute() or ".." in relative.parts:
        raise SystemExit("Target file must be relative to PKM_VALUT_DIR without parent traversal.")
    target = (vault / relative).resolve()
    if not target.is_relative_to(vault):
        raise SystemExit("Target file must be inside the vault.")
    relative = target.relative_to(vault)
    actions = {"MOCs": "append-moc-link", "01 Projects": "append-project-resource"}
    action = actions.get(relative.parts[0] if relative.parts else "")
    if action is None:
        raise SystemExit("Use this helper only for MOCs or Project resource links; use append-daily for Daily.")
    wrapper = (vault / "scripts/pkm_quickadd.py").resolve()
    if not wrapper.is_relative_to(vault) or not wrapper.is_file():
        raise SystemExit("The vault-local scripts/pkm_quickadd.py must exist inside PKM_VALUT_DIR.")
    payload = {"file": relative.as_posix(), "heading": args.heading, "entry": args.entry}
    command = [sys.executable, str(wrapper), action, "--vault-root", str(vault),
               "--payload-json", json.dumps(payload, ensure_ascii=False)]
    if args.check_only:
        command.append("--check-only")
    return subprocess.run(command, cwd=vault, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
