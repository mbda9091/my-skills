---
name: pkm-triage
description: Leaf skill for deciding where PKM material belongs by PARA action distance. Use only when explicitly invoked by $pkm-triage or selected by $pkm-operator. Classifies content into Daily, 00_inbox, 01 Projects, 02 Areas, 03 Resources, 04 Archive, or deletion candidates with rationale and next action.
---

# PKM Triage

## Target vault

`PKM_VALUT_DIR` is required and is the sole target-vault selector. Before any vault read or write, require a nonempty absolute path to an existing directory. If it is unset, empty, relative, missing, or not a directory, stop and report the configuration error. Never fall back to the current workspace, the skill repository, or a fixed home-directory path.

Resolve all note paths, templates, and vault-local scripts from this directory. Reject vault-relative paths that escape the resolved root, including through symlinks. Run vault-local wrappers with this directory as their working directory; if a wrapper accepts `--vault-root`, pass the same directory. A wrapper that selects another vault must be corrected before use. Skill-local `references/` and `scripts/` remain relative to this skill, not the vault.

Follow the target vault's `AGENTS.md` for internal vault operations. Keep each run bound to the same resolved directory.

## Role

Decide where a note or idea belongs. Produce a destination, rationale, and next action. Do not rewrite the content unless the user asks.

## Decision Tree

1. Does it require action today or this week?
   - Yes: `Daily/` if small, `01 Projects/` if it has an outcome and multiple steps.
2. Does it have a clear outcome, deadline, or finish condition?
   - Yes: `01 Projects/`.
3. Is it an ongoing responsibility, standard, habit, or maintained domain?
   - Yes: `02 Areas/`.
4. Is it reusable knowledge, a method, reference, template, or judgment framework?
   - Yes: `03 Resources/`.
5. Is it unprocessed but may be useful?
   - Yes: `00_inbox/`.
6. Is it completed, inactive, obsolete, or no longer useful?
   - Yes: `04 Archive/` or deletion candidate.

## Output Format

```markdown
## Triage Result
- Destination:
- Rationale:
- Confidence: high|medium|low
- Next Action:
- Links to update:
```

Use `references/para-rules.md` for edge cases.
