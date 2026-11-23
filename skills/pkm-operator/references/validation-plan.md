# Validation Plan

Validate leaf skills independently first, then validate combined flows.

## Target vault validation

- Invoke each skill directly as well as through the operator; all target paths must resolve from `PKM_VALUT_DIR`.
- Unset, empty, relative, missing, and non-directory values stop before vault operations; the workspace never becomes the fallback vault.
- From an unrelated working directory, use a target path containing spaces. Verify note paths, templates, vault rules, and QuickAdd calls use that target.
- QuickAdd examples pass the selected root through `--vault-root`; any Obsidian vault identifier must match it. Preserve the configured choices and `quickadd:check` / `quickadd:run` order.
- The capture, link, and review helpers require the variable; `--vault` can only confirm it. Check parent-path and symlink escapes as well as ordinary operations.
- Run `python3 -B -m unittest discover -s tests -p 'test_*.py'` from the skill source repository, not the vault. Set `PKM_TEST_WRAPPER` to the current vault’s absolute `scripts/pkm_quickadd.py` to enable disposable-vault integration tests. Documented example tests use a stub wrapper; real Obsidian QuickAdd actions need separate integration validation.
- Run the vault’s existing `scripts/test_pkm_tasks.py` tests from the vault using `python3 -B -m unittest discover -s scripts -p 'test_pkm_tasks.py'`; they use temporary vaults.

## Leaf Validation

`pkm-capture`:

- Creates a note in the expected directory.
- Preserves raw context and prompt, renders the current vault AI template locally when needed, and never invents task placeholders.
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

- Uses the local wrapper for MOC/Project/Daily appends; a link in another section must not suppress the requested target section. Duplicate adds within the target section must be no-ops.
- Preserves existing note content.
- Updates Daily and MOC only when appropriate.

`pkm-review`:

- Lists unprocessed notes with concrete recommendations; skips protected files and processed notes. An empty To Verify heading is not an outstanding claim. Clearly scope the helper to ai/inbox.
- Does not mutate files unless explicitly asked.

## Whole-Flow Validation

For an AI conversation workflow:

1. Raw conversation exists in `00_inbox/AI Conversations/`.
2. Distilled resource exists in `03 Resources/` or is explicitly proposed.
3. Resource links back to raw conversation.
4. Project actions exist only in Project Next Actions; Daily contains progress links, or unassigned same-day temporary actions. Decisions and verification items are preserved.
5. MOC is updated when the resource is worth indexing.
