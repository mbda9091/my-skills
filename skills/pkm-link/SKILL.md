---
name: pkm-link
description: Leaf skill for connecting PKM notes after capture or distillation. Use only when explicitly invoked by $pkm-link or selected by $pkm-operator. Updates Daily notes, MOCs, backlinks, Related sections, Raw links, and project/resource references while preserving existing content and avoiding duplicate links.
---

# PKM Link

## Target vault

`PKM_VALUT_DIR` is required and is the sole target-vault selector. Before any vault read or write, require a nonempty absolute path to an existing directory. If it is unset, empty, relative, missing, or not a directory, stop and report the configuration error. Never fall back to the current workspace, the skill repository, or a fixed home-directory path.

Resolve all note paths, templates, and vault-local scripts from this directory. Reject vault-relative paths that escape the resolved root, including through symlinks. Run vault-local wrappers with this directory as their working directory; if a wrapper accepts `--vault-root`, pass the same directory. A wrapper that selects another vault must be corrected before use. Skill-local `references/` and `scripts/` remain relative to this skill, not the vault.

Follow the target vault's `AGENTS.md` for internal vault operations. Keep each run bound to the same resolved directory.

## Role

Connect notes so work remains traceable. Add the smallest useful set of links; do not reorganize content beyond the requested connection.

## Workflow

1. Identify the source note, target note, and link purpose.
2. Read existing files before editing.
3. Use `scripts/pkm_ops.py append-daily` when appending to Daily notes.
4. Use `scripts/pkm_ops.py append-moc-link` for MOC links and `scripts/pkm_ops.py append-project-resource` for Project resource links.
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
  python3 scripts/pkm_ops.py append-daily --payload-json '{"date":"YYYY-MM-DD","section":"Links","content":"- [[03 Resources/example]]"}'
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

## MOC and Project Scripts

```bash
(
  [[ "${PKM_VALUT_DIR:?Set PKM_VALUT_DIR}" = /* && -d "$PKM_VALUT_DIR" ]] || { echo "PKM_VALUT_DIR must be an existing absolute directory" >&2; exit 1; }
  cd -- "$PKM_VALUT_DIR" || exit
  python3 scripts/pkm_ops.py append-moc-link --payload-json '{"link":"[[03 Resources/example]]"}'
  python3 scripts/pkm_ops.py append-project-resource --payload-json '{"project":"01 Projects/example.md","resource":"[[03 Resources/example]]"}'
)
```
