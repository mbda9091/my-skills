---
name: pkm-review
description: Leaf skill for reviewing PKM inboxes, unprocessed AI conversations, stale projects, and weakly linked notes. Use only when explicitly invoked by $pkm-review or selected by $pkm-operator. Produces concrete recommendations and does not mutate files unless explicitly asked.
---

# PKM Review

## Target vault

`PKM_VALUT_DIR` is required and is the sole target-vault selector. Before any vault read or write, require a nonempty absolute path to an existing directory. If it is unset, empty, relative, missing, or not a directory, stop and report the configuration error. Never fall back to the current workspace, the skill repository, or a fixed home-directory path.

Resolve all note paths, templates, and vault-local scripts from this directory. Reject vault-relative paths that escape the resolved root, including through symlinks. Run vault-local wrappers with this directory as their working directory; if a wrapper accepts `--vault-root`, pass the same directory. A wrapper that selects another vault must be corrected before use. Skill-local `references/` and `scripts/` remain relative to this skill, not the vault.

Follow the target vault's `AGENTS.md` for internal vault operations. Keep each run bound to the same resolved directory.

## Role

Review the vault and recommend next actions. Default to reporting, not editing.

## Workflow

1. Determine review scope:
   - AI conversation inbox
   - general inbox
   - projects
   - resources
   - whole vault
2. Use `scripts/pkm_ops.py validate-drops` for External Drop review.
3. Use direct Markdown reads/searches for AI conversation inbox, general inbox, projects, and resources when no dedicated script exists.
4. Group findings by recommended action:
   - distill
   - triage
   - link
   - archive
   - delete candidate
5. Provide concrete file paths and reasons.
6. Only edit files after the user approves the proposed changes.

## Output

```markdown
## Review Result

### Distill
- file: reason

### Triage
- file: reason

### Link
- file: reason

### Archive
- file: reason

### Delete Candidates
- file: reason
```
