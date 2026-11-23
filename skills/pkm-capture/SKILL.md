---
name: pkm-capture
description: Leaf skill for capturing raw inputs into the user's Obsidian/PKM vault. Use only when explicitly invoked by $pkm-capture or selected by $pkm-operator. Captures AI conversations, fleeting notes, source excerpts, and unprocessed material into the correct inbox or Daily location without overwriting existing notes.
---

# PKM Capture

## Role

Capture raw material with enough context to process later. Do not over-distill. Do not decide final PARA placement unless the user explicitly asks.

## Workflow

1. Identify the capture type:
   - AI conversation: `00_inbox/AI Conversations/`
   - fleeting note or unclear material: `00_inbox/`
   - same-day action or quick log: `Daily/YYYY-MM-DD.md`
2. Preserve the user's request, source context, and raw answer/content.
3. For AI conversation captures in vault `~/Documents/PKM_AI`, prefer the wrapper action `capture-ai`.
4. For same-day Daily captures, prefer the wrapper action `append-daily`.
5. Use raw Obsidian QuickAdd CLI or direct Markdown edits only when the wrapper, Obsidian CLI, or QuickAdd choice is unavailable.
6. If writing to Daily, preserve existing sections and append under the most relevant heading.
7. Validate by reading the created or updated file.

## AI Conversation Capture

Use the QuickAdd template `Templates/QuickAdd-PKM-AI-Conversation.md` through `scripts/pkm_quickadd.py` when available. Generate a payload JSON file:

```json
{
  "title": "topic",
  "date": "YYYY-MM-DD",
  "context": "why this conversation happened",
  "prompt": "core user request",
  "raw_answer": "raw or lightly compressed answer"
}
```

Then call the wrapper from the vault root:

```bash
python3 scripts/pkm_quickadd.py capture-ai --payload /private/tmp/pkm-capture.json
```

The wrapper uses choice id `b0f3c0d6-89a5-4d86-bb7b-9f8f2f61c101`, runs `quickadd:check` before `quickadd:run`, and returns the created target path. If check reports missing fields, fix the payload rather than allowing interactive prompts.

A captured conversation should include:

- context
- prompt/request
- raw answer or summarized transcript
- initial actions, if obvious
- related project/area/resource placeholders

Do not create a Resource note in this skill. Route to `$pkm-distill` after capture if reusable knowledge is needed.

Use the raw template in `references/capture-templates.md` only as the fallback shape when the wrapper and QuickAdd path are unavailable.

## Daily Capture

Use `scripts/pkm_quickadd.py append-daily` for short logs, ideas, links, and tasks. Generate a payload JSON file:

```json
{
  "date": "YYYY-MM-DD",
  "section": "Notes",
  "content": "- Short daily note.",
  "create_if_missing": "true",
  "allow_duplicate": "false"
}
```

Then call the wrapper from the vault root:

```bash
python3 scripts/pkm_quickadd.py append-daily --payload /private/tmp/pkm-daily.json
```

Use these section conventions:

- `Tasks`: dated actions using Tasks plugin syntax.
- `Notes`: short factual logs.
- `Ideas`: fleeting ideas.
- `Links`: wiki links or source links.

The wrapper appends under the matching `##` heading, creates a basic Daily note if allowed and missing, skips exact duplicates by default, and returns the target Daily path.

## Script

```bash
python3 scripts/capture_note.py \
  --vault /path/to/vault \
  --kind ai_conversation \
  --title "topic" \
  --content-file /path/to/content.md \
  --unique
```

The script prints JSON containing the created path.
