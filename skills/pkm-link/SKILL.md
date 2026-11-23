---
name: pkm-link
description: Leaf skill for connecting PKM notes after capture or distillation. Use only when explicitly invoked by $pkm-link or selected by $pkm-operator. Updates Daily notes, MOCs, backlinks, Related sections, Raw links, and project/resource references while preserving existing content and avoiding duplicate links.
---

# PKM Link

## Target vault

`PKM_VALUT_DIR` is required and is the sole filesystem target-vault selector. Before any vault read or write, require a nonempty absolute path to an existing directory. If it is unset, empty, relative, missing, or not a directory, stop and report the configuration error. Never fall back to the current workspace or a fixed home-directory path.

Resolve note paths, templates, and the vault's `AGENTS.md` from this directory. Keep vault-relative paths inside the resolved root, including through symlinks. Follow `$PKM_VALUT_DIR/AGENTS.md` for vault operations. Skill-local `references/` and bundled `scripts/` resolve from this skill's installed directory, independently of the target vault and current working directory.

The QuickAdd wrapper is `$PKM_VALUT_DIR/scripts/pkm_quickadd.py`. Run it with `--vault-root "$PKM_VALUT_DIR"` in the configured vault directory. For Obsidian-backed actions, verify that the wrapper's `--vault` identifier points to the same vault before writing; pass the matching identifier when its default does not match.

## Role

Connect notes so work remains traceable. Add the smallest useful set of links; do not reorganize content beyond the requested connection.

## Workflow

1. Identify the source note, target note, and link purpose.
2. Read existing files before editing.
3. Use `scripts/pkm_quickadd.py append-daily` when appending to Daily notes.
4. Use `scripts/update_links.py` for MOCs or project/resource files when that script is available; otherwise use minimal direct Markdown edits.
5. Avoid duplicate entries.
6. Validate by reading the changed section.

## Common Links

- Raw AI capture -> Resource: add raw link in the Resource `Related` section.
- Resource -> Daily: append the resource link under `## Links` or `## Notes`.
- Resource -> MOC: append under the relevant index heading.
- Project -> Resource: add resource link under `## Resources`.

## Daily Script

```bash
(
  [[ "${PKM_VALUT_DIR:?Set PKM_VALUT_DIR}" = /* && -d "$PKM_VALUT_DIR" ]] || { echo "PKM_VALUT_DIR must be an existing absolute directory" >&2; exit 1; }
  cd -- "$PKM_VALUT_DIR" || exit
  python3 scripts/pkm_quickadd.py append-daily --vault-root "$PKM_VALUT_DIR" --payload /tmp/pkm-daily.json
)
```

Payload:

```json
{
  "date": "YYYY-MM-DD",
  "section": "Links",
  "content": "- [[03 Resources/example]]",
  "create_if_missing": "true",
  "allow_duplicate": "false"
}
```

Use `Links` for references, `Tasks` for dated actions, `Notes` for short logs, and `Ideas` for fleeting ideas. Entries under `Tasks` must follow the vault Tasks syntax.

## Generic Link Script

The bundled helper below uses the default Codex installation path. If this skill is installed elsewhere, resolve the helper's absolute path from this `SKILL.md`. Its optional `--vault` must match `PKM_VALUT_DIR` and cannot select a different target.

```bash
python3 "$HOME/.agents/skills/pkm-link/scripts/update_links.py" \
  --vault "$PKM_VALUT_DIR" \
  --file "MOCs/AI 对话沉淀.md" \
  --heading "已沉淀资源" \
  --entry "- [[03 Resources/example]]"
```
