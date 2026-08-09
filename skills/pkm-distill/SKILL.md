---
name: pkm-distill
description: Leaf skill for turning raw PKM captures into durable knowledge. Use only when explicitly invoked by $pkm-distill or selected by $pkm-operator. Extracts summaries, methods, judgment criteria, decisions, actions, verification items, and Resource notes from AI conversations or other raw notes.
---

# PKM Distill

## Role

Convert raw material into reusable knowledge. Preserve traceability to the raw source, but do not dump transcripts into Resource notes.

## Workflow

1. Read the raw note or user-provided content.
2. Identify the reusable unit:
   - method
   - checklist
   - framework
   - decision record
   - implementation plan
   - reference summary
3. Extract:
   - Summary
   - Key Points
   - Decisions
   - Actions
   - To Verify
   - Related Project/Area/Raw links
4. If writing a Resource note in vault `~/Documents/PKM_AI`, prefer the wrapper action `create-resource`.
5. If writing directly, use `03 Resources/` unless triage indicates Project or Area.
6. Route link updates to `$pkm-link`.

## Resource Shape

Use `references/distillation-patterns.md` for output patterns. Prefer dense, reusable notes over long summaries.

## QuickAdd Wrapper

Generate Markdown-ready values and write them to a payload JSON file:

```json
{
  "title": "durable resource title",
  "source_type": "ai",
  "summary": "- Durable takeaway.",
  "key_points": "- Reusable point.",
  "to_verify": "- Unstable claim to verify, or leave blank.",
  "raw_link": "[[00_inbox/AI Conversations/YYYY-MM-DD-title]]",
  "related_project": "[[01 Projects/PKM工作流搭建]]"
}
```

Then call the wrapper from the vault root:

```bash
python3 scripts/pkm_quickadd.py create-resource --payload /private/tmp/pkm-resource.json
```

The wrapper uses choice id `f50ab515-88cb-4878-9d0c-449278ef94b2`, runs `quickadd:check` before `quickadd:run`, and returns the created target path. If check reports missing fields, provide explicit empty strings for intentionally blank optional values. Do not copy the full Resource template into the skill when the wrapper path is available.

Use raw Obsidian QuickAdd CLI or direct Markdown writes only when the wrapper is unavailable, the Obsidian CLI is unavailable, the QuickAdd choice is missing, or the user explicitly asks for direct file edits.

## External Facts

If the source contains facts that may change, keep them under `To Verify` until verified. Do not convert unstable claims into durable knowledge without sources.
