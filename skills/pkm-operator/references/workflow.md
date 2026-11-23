# PKM Workflow

`PKM_VALUT_DIR` is the sole target selector and must be an existing absolute directory. Resolve its symlinks and follow its `AGENTS.md`. Skill helpers and references resolve from the installed skill; templates and wrappers resolve from the vault.

```text
Capture -> Triage -> Distill -> Link -> Review
```

| Directory | Purpose |
| --- | --- |
| `Daily/` | Dated logs/links and unassigned same-day temporary tasks |
| `00_inbox/` | Unprocessed captures |
| `00_inbox/AI Conversations/` | Raw AI records |
| `01 Projects/` | Outcomes/finish conditions/continued progress; tasks under Next Actions |
| `02 Areas/` | Ongoing responsibilities and standards |
| `03 Resources/` | Reusable methods, knowledge, and references |
| `04 Archive/` | Inactive content, only moved on explicit request |
| `MOCs/` | Curated indexes |

## Task ownership and lifecycle

Check project ownership before task size or date. A small action in a known project stays in its Next Actions. Daily Notes/Links records progress, not a duplicate Project checkbox. Unresolved actions stay as ordinary text pending triage.

Use `add-task` for new structured text plus optional due date. The wrapper generates the creation date in Asia/Shanghai. Use `set-task-status` for completion/cancellation/reopening and `update-task` for text/due/ownership or sourced creation-date backfill. Combined requests require separate calls. Content edits and cancellation need the user’s real reason; completion needs no reason and an optional conclusion only when available. Preserve task blocks and history during moves; do not reset dates or duplicate checkboxes. Never infer task completion or backfill original dates from filenames.

The manual-only `$pkm-todo` is not an implicit operator leaf. Authorized PKM workflows may call the vault task wrapper directly while following `AGENTS.md`.

## Creation and linking

AI records use `00_inbox/AI Conversations/YYYY-MM-DD-title.md`; Resources use `source_type: ai` and a Raw link. Record decisions explicitly in supported fields and route actions to their owner. Link raw Related/Resource back to the output. Log progress in Daily Notes/Links and index worthwhile outputs in MOCs.

Use `append-daily`, `append-moc-link`, and `append-project-resource` for local appends. They do not require Obsidian. Preserve current templates, fields, wiki-link syntax, task syntax, and Dashboard dependencies. A missing local wrapper is an error, not permission to hand-edit task history or protected append paths.

For capture/resource creation, prefer QuickAdd with explicit `--vault-root` and a matching Obsidian vault identifier. Preserve `quickadd:check` before `quickadd:run`. When unavailable, create local Markdown from the current vault template; this exception does not apply to tasks or MOC/Project/Daily appends. Prefer short `--payload-json`; use stdin or a UTF-8 file for long content.

Read the current note before modifying it. Preserve personal content, exclusions, sync metadata, agent metadata, and plugin configuration. Never delete/archive/rename without explicit instruction. Keep external claims in To Verify until verified.
