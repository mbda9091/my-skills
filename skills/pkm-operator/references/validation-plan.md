# Validation Plan

Validate leaf skills independently first, then validate combined flows.

## Target vault validation

- Invoke each skill directly as well as through the operator; all target paths must resolve from `PKM_VALUT_DIR`.
- Unset, empty, relative, missing, and non-directory values stop before vault operations; the workspace never becomes the fallback vault.
- From an unrelated working directory, use a target path containing spaces. Verify note paths, templates, vault rules, and QuickAdd calls use that target.
- QuickAdd examples pass the selected root through `--vault-root`; any Obsidian vault identifier must match it. Preserve the configured choices and `quickadd:check` / `quickadd:run` order.
- The capture, link, and review helpers require the variable; `--vault` can only confirm it. Check parent-path and symlink escapes as well as ordinary operations.
- Run `python3 -m unittest discover -s tests -p 'test_*.py'` in this repository. Documented command tests use a stub wrapper; real Obsidian QuickAdd actions need separate integration validation.

## Leaf Validation

`pkm-capture`:

- Creates a note in the expected directory.
- Preserves raw context.
- Refuses to overwrite existing files unless explicitly allowed.

`pkm-triage`:

- Produces a PARA destination and rationale.
- Distinguishes action from reference value.
- Surfaces uncertainty instead of guessing silently.

`pkm-distill`:

- Produces reusable knowledge, not just a transcript summary.
- Extracts decisions, actions, and verification items.
- Keeps a traceable raw/source link.

`pkm-link`:

- Adds links without duplicating existing entries.
- Preserves existing note content.
- Updates Daily and MOC only when appropriate.

`pkm-review`:

- Lists unprocessed notes with concrete recommendations.
- Does not mutate files unless explicitly asked.

## Whole-Flow Validation

For an AI conversation workflow:

1. Raw conversation exists in `00_inbox/AI Conversations/`.
2. Distilled resource exists in `03 Resources/` or is explicitly proposed.
3. Resource links back to raw conversation.
4. Daily note contains the action or link if action is required.
5. MOC is updated when the resource is worth indexing.
