---
name: pkm-review
description: Leaf skill for reviewing PKM inboxes, unprocessed AI conversations, stale projects, and weakly linked notes. Use only when explicitly invoked by $pkm-review or selected by $pkm-operator. Produces concrete recommendations and does not mutate files unless explicitly asked.
---

# PKM Review

## Target vault

`PKM_VALUT_DIR` is required and is the sole filesystem target-vault selector. Before any vault read or write, require a nonempty absolute path to an existing directory. If it is unset, empty, relative, missing, or not a directory, stop and report the configuration error. Never fall back to the current workspace or a fixed home-directory path.

Resolve note paths, templates, and the vault's `AGENTS.md` from this directory. Keep vault-relative paths inside the resolved root, including through symlinks. Follow `$PKM_VALUT_DIR/AGENTS.md` for vault operations. Skill-local `references/` and bundled `scripts/` resolve from this skill's installed directory, independently of the target vault and current working directory.

## Role

Review the vault and recommend next actions. Default to reporting, not editing.

## Workflow

1. Determine review scope:
   - AI conversation inbox
   - general inbox
   - projects
   - resources
   - whole vault
2. Use this skill's bundled `scripts/review_inbox.py` for inbox and AI conversation reviews; resolve its absolute path from this `SKILL.md`.
3. For projects/resources/whole-vault review, read the requested local Markdown notes separately; the helper only covers ai/inbox. Respect the vault’s exclusions before reading. Use `check-tasks` for requested task-structure checks, without implicitly invoking manual-only `$pkm-todo`.
4. Treat helper output as initial recommendations, not proof of note quality or completion. It skips known processed statuses and raw notes with Resource associations; verify unresolved facts separately. Group findings by recommended action:
   - distill
   - triage
   - link
   - verify
   - archive
   - delete candidate
5. Provide concrete file paths and reasons. Never infer task completion from age or prose alone.
6. Review is read-only unless the user requested changes. Existing authorization to apply specific changes is sufficient; do not ask again. Deletion, archiving, and renaming require the user’s explicit request under the vault rules.

## Inbox review helper

For the default Codex installation:

```bash
python3 "$HOME/.agents/skills/pkm-review/scripts/review_inbox.py" --scope ai --json
```

The helper requires `PKM_VALUT_DIR`. Its optional `--vault` can only confirm the same resolved target.

## Output

```markdown
## Review Result

### Distill
- file: reason

### Triage
- file: reason

### Link
- file: reason

### Verify
- file: reason

### Archive
- file: reason

### Delete Candidates
- file: reason
```
