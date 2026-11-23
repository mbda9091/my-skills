# Validation Plan

Validate leaf skills independently first, then validate combined flows.

## Target Vault Validation

- Test every leaf directly as well as through the operator: `PKM_VALUT_DIR` must select the same target.
- Unset, empty, relative, missing, and non-directory values stop before vault reads or writes.
- From an unrelated working directory, use a target path containing spaces. Reads, writes, templates, and vault-local scripts must stay anchored to that target.
- Resolve vault-relative paths inside the target; reject parent-path and symlink escapes. Skill-local references and helpers still resolve from the installed skill.
- Internal operations read the target vault's `AGENTS.md`; `pkm-ingress` must not read it or accept a target-vault override in its payload.
- The bundled capture, link, and review helpers require the environment variable. `--vault` can only confirm the same resolved directory.
- In this repository, run `python3 -m unittest discover -s tests -p 'test_*.py'` for helper behavior and documented command examples. Example tests use stub vault wrappers; separately verify the real target vault's wrapper interfaces before production writes.

## Leaf Validation

`pkm-capture`:

- Creates a note in the expected directory.
- Preserves raw context.
- Refuses to overwrite existing files unless explicitly allowed.

`pkm-ingress`:

- Creates only an External Drop under `00_inbox/External Drops/`.
- Does not read `AGENTS.md` or perform PARA triage.
- Returns an existing drop for duplicate `source_app + external_id`.

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

`pkm-ingest`:

- Validates an External Drop before writing formal notes.
- Runs dry-run before write when processing a drop.
- Updates drop `status` and `outputs` after writing.

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
