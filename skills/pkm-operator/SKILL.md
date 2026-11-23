---
name: pkm-operator
description: Main entrypoint for the user's Obsidian/PKM workflow. Use when the user explicitly invokes $pkm-operator or asks Codex to capture, triage, distill, link, or review knowledge in the PKM vault according to the user's PARA and AI-conversation workflow. This skill routes the goal to explicit leaf skills and coordinates end-to-end validation.
---

# PKM Operator

## Role

Act as the PKM workflow router, not as a monolithic writer. Understand the user's goal, select the smallest necessary workflow stage, explicitly load the matching leaf skill, and coordinate validation.

The vault workflow is:

```text
ingress -> capture -> triage -> distill -> link -> ingest -> review
```

## Routing

Read `references/routing-table.md` before choosing a leaf skill unless the user already named one.

Use these leaf skills:

| Goal | Leaf skill |
| --- | --- |
| Save raw input, AI chat, webpage excerpt, or fleeting idea | `$pkm-capture` |
| Decide whether content belongs in Daily, Project, Area, Resource, Inbox, or Archive | `$pkm-triage` |
| Extract reusable knowledge, decisions, actions, or verification items | `$pkm-distill` |
| Add backlinks, Daily links, MOC entries, or related project/resource references | `$pkm-link` |
| Process files under `00_inbox/External Drops/` into formal vault notes | `$pkm-ingest` |
| Review inbox, stale projects, unprocessed AI conversations, or weakly linked notes | `$pkm-review` |

After selecting a leaf, read that leaf skill's `SKILL.md` from the sibling skill directory, for example `../pkm-capture/SKILL.md`. Do not execute a leaf workflow from memory.

## End-To-End AI Conversation Flow

Use this as the first complete vertical slice:

1. `$pkm-capture`: Save the raw conversation into `00_inbox/AI Conversations/YYYY-MM-DD-title.md`.
2. `$pkm-distill`: Create or propose a `03 Resources/` note containing durable knowledge, decisions, actions, and items to verify.
3. `$pkm-link`: Link the resource back to the raw conversation, append the output to the Daily note, and update `MOCs/AI 对话沉淀.md` when appropriate.
4. Validate by reading the changed files and checking that raw context, distilled knowledge, and action links are all traceable.

## PKM Ops Wrapper

For vault-local automation, prefer the vault-native wrapper:

```bash
python3 scripts/pkm_ops.py create-ai-conversation --payload-json '{"title":"topic","date":"YYYY-MM-DD"}'
python3 scripts/pkm_ops.py create-resource --payload-json '{"title":"resource","source_type":"ai"}'
python3 scripts/pkm_ops.py append-daily --payload-json '{"date":"YYYY-MM-DD","section":"Notes","content":"- note"}'
```

Run these commands from the vault root. The operator and leaf skills should generate structured payloads and call `scripts/pkm_ops.py`; use `--payload-json` for short payloads and `--payload -` or `--payload <path>` for longer content.

Primary actions:

- `create-ai-conversation`
- `create-resource`
- `append-daily`
- `append-moc-link`
- `append-project-resource`
- `add-task`
- `create-external-drop`
- `validate-drops`
- `ingest-drop`
- `validate-templates`

Payload for `capture-ai`:

```json
{
  "title": "topic",
  "date": "YYYY-MM-DD",
  "context": "why this conversation happened",
  "prompt": "core user request",
  "raw_answer": "raw or lightly compressed answer"
}
```

Payload for `create-resource`:

```json
{
  "title": "durable resource title",
  "source_type": "ai",
  "summary": "- Durable takeaway.",
  "key_points": "- Reusable point.",
  "to_verify": "- Unstable claim to verify, or leave blank.",
  "raw_link": "[[00_inbox/AI Conversations/YYYY-MM-DD-title]]",
  "related_area": "[[02 Areas/related area]]",
  "related_project": "[[01 Projects/related project]]"
}
```

Resolve `related_area` and `related_project` from the actual note ownership. Use an empty string when either relation does not apply; never default new resources to a completed project.

Payload for `append-daily`:

```json
{
  "date": "YYYY-MM-DD",
  "section": "Notes",
  "content": "- Short daily note.",
  "create_if_missing": "true",
  "allow_duplicate": "false"
}
```

Use `Tasks`, `Notes`, `Ideas`, or `Links` for common Daily sections. Entries under `Tasks` must follow the vault Tasks syntax, for example `- [ ] Task content 📅 YYYY-MM-DD`.

Markdown values may contain lists and multiline text. When preparing JSON by hand, encode newlines as JSON newlines (`\n`), not as literal backslash-n text.

`scripts/pkm_quickadd.py` is a legacy adapter for explicit QuickAdd/manual Obsidian workflows. Do not use it as the default automation backend.

## Operating Rules

- Before PKM vault writes, read `~/Documents/PKM_AI/AGENTS.md`; use `references/workflow.md` only as skill-local routing context.
- Ask for clarification only when routing is genuinely ambiguous and a wrong write would be costly.
- Preserve user-authored content. Never overwrite notes unless explicitly requested.
- For facts that may change over time, require verification before turning them into durable knowledge.
- For each run, state the selected route before making file edits.
- For multi-stage work, validate each stage before moving to the next.

## Validation

Use `references/validation-plan.md` for independent leaf validation and whole-flow validation.
