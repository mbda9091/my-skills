---
name: pkm-ingress
description: Controlled external entry point for the user's PKM vault. Use when external systems, bots, browser tools, another agent, or the user explicitly ask to submit outside content into the vault without reading AGENTS.md or performing PARA triage. Creates External Drops only.
---

# PKM Ingress

## Role

Accept external content through the smallest contract and create an External Drop. Do not summarize, triage, classify, link, create Resources, add Tasks, or read the vault `AGENTS.md`.

External Ingress is the boundary before the vault workflow:

```text
external caller -> $pkm-ingress -> scripts/pkm_ops.py create-external-drop -> External Drop
```

The output is always a pending note under `00_inbox/External Drops/`.

## Contract

Required fields:

- `source_app`: single-line external entry identifier, such as `feishu-bot`, `qq-bot`, `browser-extension`, `cli`, or `another-agent`.
- `content`: raw external content.

Optional fields:

- `source_ref`: external locator, such as a URL, message id, thread id, or external file id.
- `source_created_at`: timestamp from the source system.
- `external_id`: source-system idempotency key. Reusing the same `source_app + external_id` returns the existing drop.
- `title_hint`: weak human title hint.
- `intent_hint`: one of `capture`, `distill`, `task`, `unknown`.
- `content_format`: one of `plain_text`, `markdown`.
- `attachments`: list of external attachment references. Do not pass local absolute paths.

Unknown fields are invalid. External callers must not pass PARA placement, Dashboard fields, MOC targets, or Tasks plugin syntax.

## Workflow

1. Build the smallest payload from the external request.
2. Run from the vault root:

```bash
python3 scripts/pkm_ops.py create-external-drop --payload-json '{"source_app":"cli","content":"raw text","intent_hint":"unknown"}'
```

3. Read the returned `target_path` if validation is needed.
4. Return only the drop path, wiki link, duplicate flag, and pending status to the caller.

## Guardrails

- Do not read `AGENTS.md`; External Ingress should not import the vault's internal workflow into the external context.
- Do not convert `intent_hint: task` into a checkbox. Task ownership is decided during internal ingest.
- Do not copy or localize attachments in this skill. Preserve external references only.
- Do not call `ingest-drop`. Use `$pkm-ingest` or `$pkm-operator` after the drop exists.
