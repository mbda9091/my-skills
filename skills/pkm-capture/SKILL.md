---
name: pkm-capture
description: Leaf skill for capturing raw inputs into the user's Obsidian/PKM vault. Use only when explicitly invoked by $pkm-capture or selected by $pkm-operator. Captures AI conversations, fleeting notes, source excerpts, and unprocessed material into the correct inbox or Daily location without overwriting existing notes.
---

# PKM Capture

## Target vault

`PKM_VALUT_DIR` is required and is the sole filesystem target-vault selector. Before any vault read or write, require a nonempty absolute path to an existing directory. If it is unset, empty, relative, missing, or not a directory, stop and report the configuration error. Never fall back to the current workspace or a fixed home-directory path.

Resolve note paths, templates, and the vault's `AGENTS.md` from this directory. Keep vault-relative paths inside the resolved root, including through symlinks. Follow `$PKM_VALUT_DIR/AGENTS.md` for vault operations. Skill-local `references/` and bundled `scripts/` resolve from this skill's installed directory, independently of the target vault and current working directory.

The QuickAdd wrapper is `$PKM_VALUT_DIR/scripts/pkm_quickadd.py`. Run it with `--vault-root "$PKM_VALUT_DIR"` in the configured vault directory. For Obsidian-backed actions, verify that the wrapper's `--vault` identifier points to the same vault before writing; pass the matching identifier when its default does not match.

## Role

Capture raw material with enough context to process later. Do not over-distill. Do not decide final PARA placement unless the user explicitly asks.

## Workflow

1. Identify the capture type:
   - AI conversation: `00_inbox/AI Conversations/`
   - fleeting note or unclear material: `00_inbox/`
   - same-day unassigned temporary task or quick log: `Daily/YYYY-MM-DD.md`; project actions go to that project’s `Next Actions`, even if small
2. Preserve the user's request, source context, and raw answer/content.
3. For AI conversation captures in the vault selected by `PKM_VALUT_DIR`, prefer the wrapper action `capture-ai`.
4. For same-day Daily captures, prefer the wrapper action `append-daily`.
5. For AI/inbox creation, use the current vault template and local Markdown fallback if the wrapper, Obsidian CLI, or QuickAdd choice is unavailable. Daily and task actions remain on the local wrapper; they do not depend on Obsidian. Do not fall back to manual task/date/history edits.
6. If writing to Daily, preserve existing sections and append under the most relevant heading.
7. Validate by reading the created or updated file.

## AI Conversation Capture

Use the QuickAdd template `Templates/QuickAdd-PKM-AI-Conversation.md` through `scripts/pkm_quickadd.py` when available. Prefer `--payload-json` for short payloads; use a UTF-8 file or stdin for long content:

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
  python3 scripts/pkm_quickadd.py capture-ai --vault-root "$PKM_VALUT_DIR" --payload-json '{"title":"topic","date":"YYYY-MM-DD","context":"Conversation context","prompt":"User request","raw_answer":"Raw answer"}'
)
```

The wrapper uses choice id `b0f3c0d6-89a5-4d86-bb7b-9f8f2f61c101`, runs `quickadd:check` before `quickadd:run`, and returns the created target path. If check reports missing fields, fix the payload rather than allowing interactive prompts.

A captured conversation should include:

- context
- prompt/request
- raw answer or summarized transcript
- initial actions, if obvious
- related project/area/resource placeholders

Do not create a Resource note in this skill. Route to `$pkm-distill` after capture if reusable knowledge is needed.

Read `references/capture-templates.md` for fallback handling. The vault’s current templates are authoritative; do not substitute an old skill-local template. Capture explicit decisions and verification candidates from the input without inventing actions or duplicate checkboxes.

## Daily Capture

Use `scripts/pkm_quickadd.py append-daily` for short logs, ideas, and links. Use `add-task` for new tasks with structured fields; do not hand-compose task metadata. Prefer `--payload-json` for short payloads and a file or stdin for long content:

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
  python3 scripts/pkm_quickadd.py append-daily --vault-root "$PKM_VALUT_DIR" --payload-json '{"date":"YYYY-MM-DD","section":"Notes","content":"- 今日推进 [[01 Projects/project]]","create_if_missing":"true","allow_duplicate":"false"}'
)
```

Use these section conventions:

- `Tasks`: only unassigned same-day temporary tasks, added through `add-task`; due date is optional and creation date is generated in Asia/Shanghai.
- `Notes`: short factual logs.
- `Ideas`: fleeting ideas.
- `Links`: wiki links or source links.

The wrapper appends under the matching `##` heading, creates a basic Daily note if allowed and missing, skips duplicate content by default (task deduplication compares task text and due date), and returns the target Daily path.

## Script

The bundled helper below uses the default Codex installation path. If this skill is installed elsewhere, resolve the helper's absolute path from this `SKILL.md`. Its optional `--vault` must match `PKM_VALUT_DIR` and cannot select a different target.

```bash
python3 "$HOME/.agents/skills/pkm-capture/scripts/capture_note.py" \
  --vault "$PKM_VALUT_DIR" \
  --kind ai_conversation \
  --title "topic" \
  --content-file /path/to/content.md \
  --context-file /path/to/context.md \
  --unique
```

This helper is only for inbox/AI creation, not Daily or task updates. AI capture renders `Templates/QuickAdd-PKM-AI-Conversation.md` from the target vault and fails if it cannot render a token. Supply context and prompt explicitly; never silently drop available context. It does not generate task placeholders. The script prints JSON containing the created path.
