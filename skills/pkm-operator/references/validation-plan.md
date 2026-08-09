# Validation Plan

Validate leaf skills independently first, then validate combined flows.

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
