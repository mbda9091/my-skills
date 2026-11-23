---
name: pkm-triage
description: Leaf skill for deciding where PKM material belongs by PARA action distance. Use only when explicitly invoked by $pkm-triage or selected by $pkm-operator. Classifies content into Daily, 00_inbox, 01 Projects, 02 Areas, 03 Resources, 04 Archive, or deletion candidates with rationale and next action.
---

# PKM Triage

## Target vault

`PKM_VALUT_DIR` is required and is the sole filesystem target-vault selector. Before any vault read or write, require a nonempty absolute path to an existing directory. If it is unset, empty, relative, missing, or not a directory, stop and report the configuration error. Never fall back to the current workspace or a fixed home-directory path.

Resolve note paths, templates, and the vault's `AGENTS.md` from this directory. Keep vault-relative paths inside the resolved root, including through symlinks. Follow `$PKM_VALUT_DIR/AGENTS.md` for vault operations. Skill-local `references/` and bundled `scripts/` resolve from this skill's installed directory, independently of the target vault and current working directory.

## Role

Decide where a note or idea belongs. Produce a destination, rationale, and next action. Do not rewrite the content unless the user asks.

## Decision Tree

1. Does an action belong to a known project, or have an outcome, finish condition, or ongoing progress value?
   - Yes: `01 Projects/<project>.md`, under `## Next Actions`, even for a single small step.
2. Is it unassigned same-day temporary work or a dated log?
   - Yes: `Daily/` Tasks for temporary actions, Notes/Links for progress context. A date alone does not override project ownership.
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

Use `references/para-rules.md` for edge cases. Classification alone does not authorize moves, deletion, archiving, or task status changes. If asked to apply task ownership changes, use `update-task` with the user’s reason, preserving the whole task block. Never duplicate a Project checkbox in Daily. Unresolved ownership remains ordinary text under Actions; ask only when a write needs that decision.
