---
name: pkm-capture
description: Leaf skill for capturing raw inputs into the user's Obsidian/PKM vault. Use only when explicitly invoked by $pkm-capture or selected by $pkm-operator. Captures AI conversations, fleeting notes, source excerpts, and unprocessed material into the correct inbox or Daily location without overwriting existing notes.
---

# PKM Capture

## Target vault

`PKM_VALUT_DIR` is required and is the sole target-vault selector. Before any vault read or write, require a nonempty absolute path to an existing directory. If it is unset, empty, relative, missing, or not a directory, stop and report the configuration error. Never fall back to the current workspace, the skill repository, or a fixed home-directory path.

Resolve all note paths, templates, and vault-local scripts from this directory. Reject vault-relative paths that escape the resolved root, including through symlinks. Run vault-local wrappers with this directory as their working directory; if a wrapper accepts `--vault-root`, pass the same directory. A wrapper that selects another vault must be corrected before use. Skill-local `references/` and `scripts/` remain relative to this skill, not the vault.

Follow the target vault's `AGENTS.md` for internal vault operations. Keep each run bound to the same resolved directory.

## Role

Capture raw material with enough context to process later. Do not over-distill. Do not decide final PARA placement unless the user explicitly asks.

## Workflow

1. Identify the capture type:
   - AI conversation: `00_inbox/AI Conversations/`
   - fleeting note or unclear material: `00_inbox/`
   - same-day action or quick log: `Daily/YYYY-MM-DD.md`
2. Preserve the user's request, source context, and raw answer/content.
3. For AI conversation captures, prefer `scripts/pkm_ops.py create-ai-conversation`.
4. For same-day Daily captures, prefer `scripts/pkm_ops.py append-daily`.
5. Use QuickAdd only as an explicit legacy/manual fallback.
6. If writing to Daily, preserve existing sections and append under the most relevant heading.
7. Validate by reading the created or updated file.

## AI Conversation Capture

Use the vault-native script `scripts/pkm_ops.py create-ai-conversation`. Generate a payload JSON object:

```json
{
  "title": "topic",
  "date": "YYYY-MM-DD",
  "context": "why this conversation happened",
  "prompt": "core user request",
  "raw_answer": "raw or lightly compressed answer"
}
```

Then call the wrapper in the configured target vault:

```bash
(
  [[ "${PKM_VALUT_DIR:?Set PKM_VALUT_DIR}" = /* && -d "$PKM_VALUT_DIR" ]] || { echo "PKM_VALUT_DIR must be an existing absolute directory" >&2; exit 1; }
  cd -- "$PKM_VALUT_DIR" || exit
  python3 scripts/pkm_ops.py create-ai-conversation --payload-json '{"title":"topic","date":"YYYY-MM-DD","context":"...","prompt":"...","raw_answer":"..."}'
)
```

A captured conversation should include:

- context
- prompt/request
- raw answer or summarized transcript
- initial actions, if obvious
- related project/area/resource placeholders

Do not create a Resource note in this skill. Route to `$pkm-distill` after capture if reusable knowledge is needed.

Use the raw template in `references/capture-templates.md` only as the fallback shape when `scripts/pkm_ops.py` is unavailable or direct Markdown drafting is explicitly requested.

## Daily Capture

Use `scripts/pkm_ops.py append-daily` for short logs, ideas, links, and tasks. Generate a payload JSON object:

```json
{
  "date": "YYYY-MM-DD",
  "section": "Notes",
  "content": "- Short daily note.",
  "create_if_missing": "true",
  "allow_duplicate": "false"
}
```

Then call the wrapper in the configured target vault:

```bash
(
  [[ "${PKM_VALUT_DIR:?Set PKM_VALUT_DIR}" = /* && -d "$PKM_VALUT_DIR" ]] || { echo "PKM_VALUT_DIR must be an existing absolute directory" >&2; exit 1; }
  cd -- "$PKM_VALUT_DIR" || exit
  python3 scripts/pkm_ops.py append-daily --payload-json '{"date":"YYYY-MM-DD","section":"Notes","content":"- Short daily note."}'
)
```

Use these section conventions:

- `Tasks`: dated actions using Tasks plugin syntax.
- `Notes`: short factual logs.
- `Ideas`: fleeting ideas.
- `Links`: wiki links or source links.

The wrapper appends under the matching `##` heading, creates a basic Daily note if allowed and missing, skips exact duplicates by default, and returns the target Daily path.

`scripts/pkm_quickadd.py` remains available only when the user explicitly requests QuickAdd behavior.
